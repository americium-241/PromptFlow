# logger.py
import logging

class LoggerFactory:
    @staticmethod
    def create_logger(name: str, debug: bool = False) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger
