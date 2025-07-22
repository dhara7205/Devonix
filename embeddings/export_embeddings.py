import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from logger.log_config import setup_logger

logger = setup_logger("embedding")


def generate_and_save_embeddings(data_dir, output_path, model_name):
    chunks = load_chunks(data_dir)
    embeddings = embed_chunks(chunks, model_name)
    save_faiss_index(np.array(embeddings).astype("float32"), chunks, output_path)


def load_chunks(data_dir):
    chunks = []
    for file in Path(data_dir).glob("*.parsed.json"):
        with open(file, "r", encoding="utf-8") as f:
            chunks.extend(json.load(f))
    logger.info(f"Loaded {len(chunks)} code chunks from {data_dir}")
    return chunks

def embed_chunks(chunks, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    texts = [chunk["code"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    logger.info(f"Generated embeddings for {len(embeddings)} chunks")
    return embeddings

def save_faiss_index(embeddings, chunks, output_dir="vector_store", index_name="faiss_index"):
    os.makedirs(output_dir, exist_ok=True)

    index_path = os.path.join(output_dir, f"{index_name}.index")
    metadata_path = os.path.join(output_dir, f"{index_name}.meta.json")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, index_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    logger.info(f"FAISS index saved to: {index_path}")
    logger.info(f"Metadata saved to: {metadata_path}")

def main():
    data_dir = "data"
    output_path = "faiss_index"
    model_name = "all-MiniLM-L6-v2"

    chunks = load_chunks(data_dir)
    embeddings = embed_chunks(chunks, model_name)
    save_faiss_index(np.array(embeddings).astype("float32"), chunks, output_path)

if __name__ == "__main__":
    main()
