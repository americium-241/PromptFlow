# logger.py
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from datetime import datetime
from models import LogEntry, LogLevel
from database import SessionLocal

class DatabaseLogHandler(logging.Handler):
    def __init__(self, execution_id):
        super().__init__()
        self.execution_id = execution_id

    def emit(self, record):
        db_session = SessionLocal()
        try:
            log_entry = LogEntry(
                execution_id=self.execution_id,
                timestamp=datetime.utcfromtimestamp(record.created),
                component=record.name,
                level=LogLevel[record.levelname],
                message=record.getMessage(),
                data={'pathname': record.pathname, 'lineno': record.lineno}
            )
            db_session.add(log_entry)
            db_session.commit()
        except Exception as e:
            # Handle logging exceptions to avoid infinite recursion
            print(f"Logging error: {e}")
        finally:
            db_session.close()

class LoggerFactory:
    log_queue = Queue()
    listener = None

    @staticmethod
    def start_listener():
        if not LoggerFactory.listener:
            listener = QueueListener(LoggerFactory.log_queue)
            listener.start()
            LoggerFactory.listener = listener

    @staticmethod
    def create_logger(name: str, debug: bool = False, execution_id: str = None) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.DEBUG if debug else logging.INFO)

            # Set up queue handler
            queue_handler = QueueHandler(LoggerFactory.log_queue)
            logger.addHandler(queue_handler)

            # Set up database handler
            db_handler = DatabaseLogHandler(execution_id)
            listener = QueueListener(LoggerFactory.log_queue, db_handler)
            listener.start()

            # Optional: Also log to console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(console_handler)

        return logger
