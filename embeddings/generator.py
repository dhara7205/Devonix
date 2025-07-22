import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from logger.log_config import setup_logger

logger = setup_logger("embedding")

# Load MiniLM model (384-dim embeddings)
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    return model.encode([text])[0]

def load_chunks(data_dir="data"):
    chunks = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".parsed.json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                parsed = json.load(f)
                chunks.extend(parsed)
                logger.info(f"Loaded {len(parsed)} chunks from {filename}")
    return chunks

def build_embedding_dataset(chunks, output_path="data/embeddings.json"):
    embedded_data = []
    for chunk in chunks:
        text = chunk.get("docstring", "") + "\n" + chunk.get("code", "")
        vector = embed_text(text)

        entry = {
            "vector": vector,
            **chunk  # include all metadata (rel_path, language, etc.)
        }
        embedded_data.append(entry)
        logger.debug(f"Embedded: {chunk['qualified_name']}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, indent=2)

    logger.info(f"Saved {len(embedded_data)} embeddings to {output_path}")

if __name__ == "__main__":
    logger.info("🔁 Starting embedding pipeline")
    chunks = load_chunks()
    build_embedding_dataset(chunks)
    logger.info("✅ Embedding pipeline complete.")
