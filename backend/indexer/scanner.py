import os
from logger.log_config import setup_logger

logger = setup_logger(__name__)

VALID_EXTENSIONS = {'.py', '.js', '.java'}
EXCLUDE_DIRS = {'venv', 'build', '__pycache__', 'tests', '.git', 'node_modules'}

def is_valid_file(file_path):
    _, ext = os.path.splitext(file_path)
    return ext in VALID_EXTENSIONS

def should_exclude(path):
    return any(excluded in path.split(os.sep) for excluded in EXCLUDE_DIRS)

def scan_codebase(root_dir):
    collected_files = []

    logger.info(f"Scanning directory: {root_dir}")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        if should_exclude(dirpath):
            logger.debug(f"Skipping excluded directory: {dirpath}")
            continue

        for file in filenames:
            file_path = os.path.join(dirpath, file)
            if is_valid_file(file_path):
                collected_files.append(file_path)
                logger.debug(f"Collected: {file_path}")

    logger.info(f"Total files collected: {len(collected_files)}")
    return collected_files

if __name__ == "__main__":
    files = scan_codebase(".")
    for f in files:
        print(f)
