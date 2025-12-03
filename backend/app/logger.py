import logging
import sys
from logging.handlers import RotatingFileHandler

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level = f"{record.levelname:<5}"          # pad so INFO, WARN line up
        name = f"{record.name:<20}"              # pad module/service name
        msg = record.getMessage()
        return f"{timestamp} | {level} | {name} | {msg}"


def setup_logger():
    logger = logging.getLogger()       # root logger
    logger.setLevel(logging.INFO)
    formatter = StructuredFormatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)


    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=2_000_000,     # 2 MB per file
        backupCount=5,          # keep 5 backups
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)


    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
