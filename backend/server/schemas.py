from pydantic import BaseModel

class EmbedRequest(BaseModel):
    folder_path: str
    model_name: str = "all-MiniLM-L6-v2"
    output_dir: str = "faiss_index"
    data_dir: str = "data"

class AskRequest(BaseModel):
    question: str
