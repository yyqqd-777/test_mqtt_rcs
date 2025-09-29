import logging
from logging.handlers import RotatingFileHandler


class LogTool:
    log = None

    def __init__(self, name, log_file: str, level=logging.INFO):
        handler = RotatingFileHandler(log_file, maxBytes=int(1e8), backupCount=10)
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)06d %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.addHandler(handler)
        self.log = logger

    def get_logger(self):
        return self.log
