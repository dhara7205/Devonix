import logging
import os
import sys

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "scanner.log")

os.makedirs(LOG_DIR, exist_ok=True)

def remove_emojis(text):
    return text.encode('ascii', errors='ignore').decode()

class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            record.msg = remove_emojis(str(record.msg))
            super().emit(record)
        except Exception:
            pass

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # File handler (keeps emojis)
        fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Console handler (strips emojis)
        ch = SafeStreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
