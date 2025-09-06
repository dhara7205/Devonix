from fastapi import APIRouter, HTTPException
from server.schemas import EmbedRequest, AskRequest, QAPair, FeedbackRequest, ConfigRequest
from cli.main import run_embedding_pipeline
from cli.query import run_query_pipeline
from license.license_manager import LicenseManager
import json
import os
import tempfile
import threading
from typing import Optional
router = APIRouter()

@router.post("/embed")
def embed_codebase(req: EmbedRequest):
    license = LicenseManager()
    run_embedding_pipeline(
        root_dir=req.folder_path,
        model_name=req.model_name,
        output_dir=req.output_dir,
        data_dir=req.data_dir,
        license=license
    )
    return {"status": "success", "message": "Embedding completed"}

@router.post("/ask")
def ask_question(req: AskRequest):
    result = run_query_pipeline(req.question)
    return result

FIXED_FILENAME = "qa_store.json"
_file_lock = threading.Lock()

def _ensure_store_exists(path: str):
    # Create parent directory if needed and initialize file with []
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def _read_all(path: str):
    _ensure_store_exists(path)
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return []

def _atomic_write_list(path: str, data):
    dirpath = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix="qa_tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            json.dump(data, tmpf, ensure_ascii=False, indent=2)
            tmpf.flush()
            os.fsync(tmpf.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

def _resolve_store_path(request_store_dir: Optional[str], filename: str) -> str:
    """
    Resolve final path for a given filename.
    Priority:
      1) request_store_dir (if provided and non-empty)
      2) DEFAULT_STORE_DIR (configured via /qa/config)
      3) current working directory
    Ensures the directory exists and returns absolute file path.
    """
    # 1) request-specified dir (highest priority)
    if request_store_dir and str(request_store_dir).strip():
        chosen_dir = os.path.abspath(str(request_store_dir).strip())
    # 2) configured default store dir
    elif DEFAULT_STORE_DIR:
        chosen_dir = os.path.abspath(DEFAULT_STORE_DIR)
    # 3) fallback to cwd
    else:
        chosen_dir = os.getcwd()

    # ensure it exists
    os.makedirs(chosen_dir, exist_ok=True)
    return os.path.join(chosen_dir, filename)

@router.post("/qa/store", status_code=201)
def store_qa(pair: QAPair):
    """
    Accepts {"question": "...", "answer": "...", "store_dir": "/path/to/dir"}.
    Saves into <store_dir>/qa_store.json (or ./qa_store.json if store_dir omitted).
    Only stores question and answer (no metadata).
    """
    item = {"question": pair.question.strip(), "answer": pair.answer}
    if not item["question"]:
        raise HTTPException(status_code=400, detail="question must not be empty")

    # resolve path and write
    path = _resolve_store_path(pair.store_dir,FIXED_FILENAME)

    # single-process safe append
    with _file_lock:
        items = _read_all(path)
        items.append(item)
        _atomic_write_list(path, items)

    return {"stored": item, "path": path}

@router.get("/qa/all")
def get_all_qa(store_dir: Optional[str] = None):
    """
    Return all stored QA pairs from <store_dir>/qa_store.json (or ./qa_store.json if omitted).
    Query parameter: ?store_dir=/path/to/dir
    """
    path = _resolve_store_path(store_dir,FIXED_FILENAME)
    return _read_all(path)

@router.post("/feedback", status_code=201)
def receive_feedback(req: FeedbackRequest):
    """
    Accepts:
      { question, answer, prompt?, feedback }
    Stores into <store_dir>/feedback.json according to configured directory or request override.
    """
    item = {
        "question": req.question.strip(),
        "answer": req.answer,
        "prompt": req.prompt,
        "feedback": req.feedback
    }

    # use DEFAULT_STORE_DIR (or request override) to persist feedback
    feedback_path = _resolve_store_path(None, "feedback.json")

    with _file_lock:
        items = _read_all(feedback_path)
        items.append(item)
        _atomic_write_list(feedback_path, items)

    return {"received": item, "path": feedback_path}

CONFIG_FILE = os.path.join(os.getcwd(), "qa_service_config.json")

# in-memory config values (used by other routes)
EXTERNAL_API_ENDPOINT: Optional[str] = None
API_KEY: Optional[str] = None
DEFAULT_STORE_DIR: Optional[str] = None

# simple lock for config writes
_config_lock = threading.Lock()

def _load_config_from_disk():
    """Load config into memory if CONFIG_FILE exists. Silently ignore errors."""
    global EXTERNAL_API_ENDPOINT, API_KEY, DEFAULT_STORE_DIR
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f) or {}
            EXTERNAL_API_ENDPOINT = cfg.get("api_endpoint")
            API_KEY = cfg.get("api_key")
            DEFAULT_STORE_DIR = cfg.get("store_dir")
    except Exception:
        EXTERNAL_API_ENDPOINT = None
        API_KEY = None
        DEFAULT_STORE_DIR = None

def _save_config_to_disk():
    """Persist current in-memory config to disk (atomic-ish)."""
    global EXTERNAL_API_ENDPOINT, API_KEY, DEFAULT_STORE_DIR
    cfg = {
        "api_endpoint": EXTERNAL_API_ENDPOINT,
        "api_key": API_KEY,
        "store_dir": DEFAULT_STORE_DIR
    }
    tmp_path = CONFIG_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, CONFIG_FILE)

# load config at import/startup
_load_config_from_disk()

# ---------------- Config endpoints ----------------
@router.post("/qa/config", status_code=200)
def set_qa_config(cfg: ConfigRequest):
    """
    Set the required LLM config. This route is expected to be called by the UI once.
    Body: { api_key, api_endpoint, store_dir }
    """
    global EXTERNAL_API_ENDPOINT, API_KEY, DEFAULT_STORE_DIR

    # basic validation
    api_key = (cfg.api_key or "").strip()
    api_endpoint = (cfg.api_endpoint or "").strip()
    store_dir = (cfg.store_dir or "").strip()

    if not api_key:
        raise HTTPException(status_code=400, detail="api_key is required")
    if not api_endpoint or not (api_endpoint.startswith("http://") or api_endpoint.startswith("https://")):
        raise HTTPException(status_code=400, detail="api_endpoint must start with http:// or https://")
    if not store_dir:
        raise HTTPException(status_code=400, detail="store_dir is required")

    # normalize store_dir to absolute path and ensure writable
    try:
        resolved_dir = os.path.abspath(store_dir)
        os.makedirs(resolved_dir, exist_ok=True)
        # quick write permission check (attempt to create a tiny temp file)
        test_path = os.path.join(resolved_dir, ".qa_write_test")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"cannot create/use store_dir: {e}")

    # apply config in-memory and persist
    with _config_lock:
        API_KEY = api_key
        EXTERNAL_API_ENDPOINT = api_endpoint
        DEFAULT_STORE_DIR = resolved_dir
        try:
            _save_config_to_disk()
        except Exception as e:
            # rollback in-memory if save fails (optional)
            raise HTTPException(status_code=500, detail=f"failed to save config: {e}")

    return {"status": "success", "api_endpoint": EXTERNAL_API_ENDPOINT, "store_dir": DEFAULT_STORE_DIR}

@router.get("/qa/config", status_code=200)
def get_qa_config():
    """
    Return the currently saved configuration (if any).
    """
    # return the persisted config (don't return API key in plaintext? we include it for admin UI — if you want to hide it, omit)
    if not os.path.exists(CONFIG_FILE):
        raise HTTPException(status_code=404, detail="config not set")
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to read config: {e}")