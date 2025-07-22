import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from indexer.scanner import scan_codebase
from indexer.parser import parse_python_file, save_chunks_to_json
from embeddings.export_embeddings import generate_and_save_embeddings
from logger.log_config import setup_logger

def main():
    logger = setup_logger("cli")

    parser = argparse.ArgumentParser(description="Codebase Scanner CLI")
    parser.add_argument(
        "root_dir",
        type=str,
        help="Root directory of the codebase to scan (e.g., ./my_project)"
    )
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Generate embeddings and export FAISS index"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="SentenceTransformer model name for embeddings"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="faiss_index",
        help="Output path prefix for FAISS index and metadata"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory where parsed JSON chunks are saved"
    )

    args = parser.parse_args()

    logger.info(f"📂 Scanning codebase under: {args.root_dir}")

    # Step 1: Recursively collect relevant source files
    source_files = scan_codebase(args.root_dir)
    logger.info(f"✅ Found {len(source_files)} source files.")

    # Step 2: Parse each Python file
    all_chunks = []
    for file_path in source_files:
        if file_path.endswith(".py"):
            logger.info(f"🧠 Parsing: {file_path}")
            chunks = parse_python_file(file_path, root_dir=args.root_dir)
            all_chunks.extend(chunks)

    # Step 3: Store parsed chunks
    save_chunks_to_json(all_chunks, output_dir=args.data_dir)
    logger.info(f"📦 All parsed chunks saved in '{args.data_dir}/' directory.")

    # Step 4: Optionally generate embeddings and export FAISS index
    if args.embed:
        logger.info("🔎 Generating embeddings and exporting FAISS index...")
        generate_and_save_embeddings(
            data_dir=args.data_dir,
            output_path=args.output,
            model_name=args.model
        )

if __name__ == "__main__":
    main()
