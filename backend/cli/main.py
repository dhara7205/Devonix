import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from logger.log_config import setup_logger
from license.license_manager import LicenseManager

logger = setup_logger("cli")


def run_embedding_pipeline(root_dir, model_name="all-MiniLM-L6-v2", output_dir="faiss_index", data_dir="data", license=None):
    # Lazy load heavy modules
    from indexer.scanner import scan_codebase
    from indexer.parser import parse_python_file, save_chunks_to_json
    from embeddings.export_embeddings import generate_and_save_embeddings

    logger.info(f"📂 Scanning codebase under: {root_dir}")
    source_files = scan_codebase(root_dir)
    logger.info(f"✅ Found {len(source_files)} source files.")

    # 📌 Enforce file limit for Community plan
    if not license.is_enterprise():
        MAX_FILES = 50
        if len(source_files) > MAX_FILES:
            logger.warning(f"⚠️ Community plan limit: processing only first {MAX_FILES} files.")
            source_files = source_files[:MAX_FILES]

    # Step 2: Parse each Python file
    all_chunks = []
    for file_path in source_files:
        if file_path.endswith(".py"):
            logger.info(f"🧠 Parsing: {file_path}")
            chunks = parse_python_file(file_path, root_dir=root_dir)
            all_chunks.extend(chunks)

            # 📌 Enforce chunk limit for Community plan
            if not license.is_enterprise() and len(all_chunks) >= 200:
                logger.warning("⚠️ Community plan limit: maximum 200 chunks reached.")
                all_chunks = all_chunks[:200]
                break

    # Step 3: Store parsed chunks
    save_chunks_to_json(all_chunks, output_dir=data_dir)
    logger.info(f"📦 All parsed chunks saved in '{data_dir}/' directory.")

    # Step 4: Generate embeddings and export FAISS index
    logger.info("🔎 Generating embeddings and exporting FAISS index...")
    generate_and_save_embeddings(
        data_dir=data_dir,
        output_path=output_dir,
        model_name=model_name
    )


def main():
    parser = argparse.ArgumentParser(description="Codebase Scanner CLI")
    parser.add_argument("root_dir", nargs="?", type=str, help="Root directory of the codebase to scan (e.g., ./my_project)")
    parser.add_argument("--embed", action="store_true", help="Generate embeddings and export FAISS index")
    parser.add_argument("--model", type=str, default="all-MiniLM-L6-v2", help="Model name for embeddings")
    parser.add_argument("--output", type=str, default="faiss_index", help="Output path prefix for FAISS index")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory to store parsed chunks")
    parser.add_argument("--license-info", action="store_true", help="Show license information and exit")

    args = parser.parse_args()

    license = LicenseManager()

    if args.license_info:
        print(license.get_summary())
        return

    if not license.is_valid():
        print("🚫 License invalid or expired. Please contact support.")
        return

    if not license.is_enterprise():
        print("⚠️ Community plan active — limits apply (max 50 files, 200 chunks).")

    if args.embed:
        if not args.root_dir:
            print("❗ Please provide a root directory for embedding.")
            return

        run_embedding_pipeline(
            root_dir=args.root_dir,
            model_name=args.model,
            output_dir=args.output,
            data_dir=args.data_dir,
            license=license
        )


if __name__ == "__main__":
    main()
