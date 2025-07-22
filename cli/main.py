import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from indexer.scanner import scan_codebase
from indexer.parser import parse_python_file, save_chunks_to_json
from logger.log_config import setup_logger

def main():
    logger = setup_logger("cli")

    parser = argparse.ArgumentParser(description="Codebase Scanner CLI")
    parser.add_argument(
        "root_dir",
        type=str,
        help="Root directory of the codebase to scan (e.g., ./my_project)"
    )
    args = parser.parse_args()
    root_dir = args.root_dir

    logger.info(f"📂 Scanning codebase under: {root_dir}")

    # Step 1: Recursively collect relevant source files
    source_files = scan_codebase(root_dir)
    logger.info(f"✅ Found {len(source_files)} source files.")

    # Step 2: Parse each Python file
    all_chunks = []
    for file_path in source_files:
        if file_path.endswith(".py"):
            logger.info(f"🧠 Parsing: {file_path}")
            chunks = parse_python_file(file_path,root_dir=root_dir)
            all_chunks.extend(chunks)

    # Step 3: Store parsed chunks
    save_chunks_to_json(all_chunks)
    logger.info("📦 All parsed chunks saved in 'data/' directory.")

if __name__ == "__main__":
    main()
