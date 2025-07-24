import argparse
import faiss
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sentence_transformers import SentenceTransformer
import numpy as np
from logger.log_config import setup_logger
from llm.llm_client import get_answer
from dotenv import load_dotenv
load_dotenv()


logger = setup_logger("query")

# Configs
INDEX_DIR = "faiss_index"
INDEX_NAME = "faiss_index"
TOP_K = 15

# Load model once
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_faiss_index(index_dir, index_name):
    index_path = os.path.join(index_dir, f"{index_name}.index")
    meta_path = os.path.join(index_dir, f"{index_name}.meta.json")

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("FAISS index or metadata file not found.")

    index = faiss.read_index(index_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata

def embed_query(query):
    return embed_model.encode([query])[0]  # returns 1D array

def retrieve_top_chunks(query_vec, index, metadata, k=TOP_K):
    D, I = index.search(np.array([query_vec]), k)

    top_chunks = []
    for score, idx in zip(D[0], I[0]):
        if idx < len(metadata):
            chunk = metadata[idx]
            chunk["score"] = float(score)  # Lower score = more similar
            chunk["content"] = chunk.get("docstring", "") + "\n" + chunk.get("code", "")
            top_chunks.append(chunk)

    # Sort by ascending distance (i.e., higher semantic relevance)
    top_chunks.sort(key=lambda x: x["score"])

    # for i, chunk in enumerate(top_chunks):
    #     print(f"\n--- Chunk {i} (Score: {chunk['score']:.4f}) ---\n{chunk}")

    return top_chunks


def build_prompt(chunks, query):
    context_blocks = []
    for chunk in chunks:
        filename = chunk.get("rel_path", chunk.get("file", "unknown_file.py"))
        qualified_name = chunk.get("qualified_name", chunk.get("name", "unknown_function"))
        content = chunk.get("content", "").strip()

        context_block = f"[File: {filename} | Symbol: {qualified_name}]\n{content}"
        context_blocks.append(context_block)

    context = "\n---\n".join(context_blocks)

    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    print("=================================HERE IS THE PROMPT==================================")
    print(prompt)
    return prompt

def simulate_answer(prompt):
    # For now, just simulate answer
    print("\n📄 Generated Prompt Sent to Model:\n")
    print(prompt)
    print("\n🤖 Answer:")
    return "This is a simulated answer based on the retrieved context."



def main():
    parser = argparse.ArgumentParser(description="Ask a question to your codebase.")
    parser.add_argument("question", type=str, help="The natural language question to ask")
    args = parser.parse_args()

    logger.info("Embedding query...")
    query_vec = embed_query(args.question)

    logger.info("Loading index and metadata...")
    index, metadata = load_faiss_index(INDEX_DIR, INDEX_NAME)

    logger.info("Searching for top chunks...")
    top_chunks = retrieve_top_chunks(query_vec, index, metadata)

    logger.info(f"Retrieved {len(top_chunks)} chunks.")
    prompt = build_prompt(top_chunks, args.question)

    answer = get_answer(prompt)
    print(answer)

if __name__ == "__main__":
    main()
