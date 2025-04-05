import logging
import sys
import os

_loggers = {}

def get_logger(name: str = "crawler", debug: bool = False) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    # Define o nível com base no modo debug
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Arquivo de log
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/crawler.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger