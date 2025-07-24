from fastapi import APIRouter
from server.schemas import EmbedRequest, AskRequest
from cli.main import run_embedding_pipeline
from cli.query import run_query_pipeline

router = APIRouter()

@router.post("/embed")
def embed_codebase(req: EmbedRequest):
    run_embedding_pipeline(
        root_dir=req.folder_path,
        model_name=req.model_name,
        output_dir=req.output_dir,
        data_dir=req.data_dir
    )
    return {"status": "success", "message": "Embedding completed"}

@router.post("/ask")
def ask_question(req: AskRequest):
    result = run_query_pipeline(req.question)
    return result
