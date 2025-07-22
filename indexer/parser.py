import ast
import os
import json
from pathlib import Path
from logger.log_config import setup_logger

logger = setup_logger("parser")

def parse_python_file(file_path, root_dir="."):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {e}")
        return []

    results = []
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    rel_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno
            end_line = max(getattr(node, 'end_lineno', node.lineno), node.body[-1].lineno if node.body else node.lineno)

            name = node.name
            node_type = "function" if isinstance(node, ast.FunctionDef) else "class"
            docstring = ast.get_docstring(node) or ""
            qualified_name = f"{module_name}.{name}"

            chunk = {
                "file": os.path.basename(file_path),
                "rel_path": rel_path,
                "repo": "codexpro",  # hardcoded project/repo ID; optional
                "language": "python",
                "type": node_type,
                "name": name,
                "qualified_name": qualified_name,
                "start_line": start_line,
                "end_line": end_line,
                "docstring": docstring.strip(),
                "code": "\n".join(source.splitlines()[start_line - 1:end_line])
            }
            results.append(chunk)

    logger.info(f"Parsed {len(results)} chunks from {file_path}")
    return results


def save_chunks_to_json(chunks, output_dir="data"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    file_chunks = {}
    for chunk in chunks:
        file_chunks.setdefault(chunk["file"], []).append(chunk)

    for filename, chunk_list in file_chunks.items():
        output_path = os.path.join(output_dir, f"{filename}.parsed.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunk_list, f, indent=2)

        logger.info(f"Saved {len(chunk_list)} chunks to {output_path}")


if __name__ == "__main__":
    import sys
    file_path = sys.argv[1]
    root_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    logger.info(f"Running standalone parser on {file_path}")
    chunks = parse_python_file(file_path, root_dir=root_dir)

    for chunk in chunks:
        print(chunk)

    save_chunks_to_json(chunks)
