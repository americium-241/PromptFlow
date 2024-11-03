# logger.py
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from datetime import datetime
from models import LogEntry, LogLevel
from database import SessionLocal
from typing import Any

# logger.py

# logger.py

class CurrentTraceIDFilter(logging.Filter):
    def __init__(self, di_layer):
        super().__init__()
        self.di_layer = di_layer

    def filter(self, record):
        try:
            trace_id = None
            if self.di_layer is not None:
                trace_id = self.di_layer.get('current_trace_id', default=None, suppress_logging=True)
            if trace_id:
                # Set the action_trace_id attribute on the record
                record.action_trace_id = trace_id
                record.msg = f"[TRACE_ID: {trace_id}] {record.msg}"
        except AttributeError:
            # Handle the case where di_layer or context is not initialized yet
            pass
        return True


class SafeFormatter(logging.Formatter):
    def format(self, record):
        # Provide default values for missing attributes
        if not hasattr(record, 'trace_id'):
            record.trace_id = 'N/A'
        return super().format(record)
class DatabaseLogHandler(logging.Handler):
    def __init__(self, execution_id, di_layer=None, level=logging.NOTSET):
        super().__init__(level)
        self.execution_id = execution_id
        self.di_layer = di_layer

    def emit(self, record):
        db_session = SessionLocal()
        try:
            action_trace_id = getattr(record, 'action_trace_id', None)
            # Map log level safely
            level_name = record.levelname
            try:
                log_level = LogLevel[level_name]
            except KeyError:
                log_level = LogLevel.INFO  # Default to INFO if level not found

            log_entry = LogEntry(
                execution_id=self.execution_id,
                action_trace_id=action_trace_id,
                timestamp=datetime.utcfromtimestamp(record.created),
                component=record.name,
                level=log_level,
                message=record.getMessage(),
                data={'pathname': record.pathname, 'lineno': record.lineno}
            )
            db_session.add(log_entry)
            db_session.commit()
        except Exception as e:
            # Log the exception to console for debugging
            print(f"Logging error in DatabaseLogHandler.emit: {e}")
        finally:
            db_session.close()

class LoggerFactory:
    log_queue = Queue()
    listener = None

    @staticmethod
    def start_listener(handlers):
        if not LoggerFactory.listener:
            listener = QueueListener(LoggerFactory.log_queue, *handlers)
            listener.start()
            LoggerFactory.listener = listener

    @staticmethod
    def configure_root_logger(debug: bool = False, execution_id: str = None, di_layer: Any = None) -> None:
        root_logger = logging.getLogger()
        if not root_logger.handlers:
            root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

            # Set up queue handler
            queue_handler = QueueHandler(LoggerFactory.log_queue)
            root_logger.addHandler(queue_handler)

            # Set up database handler
            db_handler = DatabaseLogHandler(execution_id=execution_id, di_layer=di_layer)

            # Set up console handler
            console_handler = logging.StreamHandler()
            console_formatter = SafeFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - [TRACE_ID: %(trace_id)s] %(message)s'
            )
            console_handler.setFormatter(console_formatter)

            # Add filter to handlers
            if di_layer is not None:
                trace_filter = CurrentTraceIDFilter(di_layer)
                db_handler.addFilter(trace_filter)
                console_handler.addFilter(trace_filter)

            # Start listener with both handlers
            LoggerFactory.start_listener([db_handler, console_handler])
    @staticmethod
    def create_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
