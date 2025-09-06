from pydantic import BaseModel
from typing import Optional

class EmbedRequest(BaseModel):
    folder_path: str
    model_name: str = "all-MiniLM-L6-v2"
    output_dir: str = "faiss_index"
    data_dir: str = "data"

class AskRequest(BaseModel):
    question: str

class QAPair(BaseModel):
    question: str
    answer: str
    # If provided, backend will save to <store_dir>/qa_store.json
    store_dir: Optional[str] = None

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    prompt: Optional[str] = None
    feedback: str   # e.g. "up" or "down"

class ConfigRequest(BaseModel):
    api_key: str          # the user's LLM API key (required)
    api_endpoint: str     # the LLM endpoint URL (required, must start with http/https)
    store_dir: str        # directory path where qa_store.json and feedback.json will be stored