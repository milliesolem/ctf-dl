import logging


def setup_logging(log_file: str = "ctfdl-debug.log"):
    logger = logging.getLogger("ctfdl")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
