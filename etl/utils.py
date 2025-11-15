import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_FILE = os.path.join(LOG_DIR, "etl.log")


def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name="crypto_etl", level=logging.INFO):
    """
    Creates a logger that prints messages using your '=== message ===' style.
    Example log line:
    2025-11-15 12:01:33 [INFO] === Successfully Connected With Postgres ===
    """

    ensure_log_dir()

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # avoid adding multiple handlers in interactive runs

    logger.setLevel(level)

    # Formatter: timestamp and level. We keep the message content as-is and
    # will include the === ... === wrapper in each logged message (see usage).
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Rotating file handler
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Avoid duplicate propagation
    logger.propagate = False
    return logger
