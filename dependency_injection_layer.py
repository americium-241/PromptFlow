# dependency_injection_layer.py
from typing import Any, Optional, Dict
from logger import LoggerFactory
from custom_exceptions import DependencyInjectionError
from contextlib import contextmanager
class DependencyInjectionLayer:
    def __init__(self, initial_context=None):
        self.context = initial_context if initial_context is not None else {}
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)
        self.data: Dict[str, Any] = {}
        self._trace_stack = []

    def set(self, key: str, value: Any, expected_type: Optional[type] = None) -> None:
        if expected_type and not isinstance(value, expected_type):
            raise DependencyInjectionError(
                f"Value for {key} must be of type {expected_type}"
            )
        self.data[key] = value
        self.logger.debug(f"Set {key} to {value}")

    def get(self, key: str, default: Any = None, suppress_logging: bool = False) -> Any:
        value = self.data.get(key, default)  # Changed from self.context to self.data
        if not suppress_logging:
            self.logger.debug(f"Retrieved {key}: {value}")
        return value
    
    @contextmanager
    def trace_context(self, trace_id: Optional[str]):
        """
        Context manager to set and unset the current_trace_id.
        Supports nested contexts.
        """
        self._trace_stack.append(self.get('current_trace_id', suppress_logging=True))
        self.set('current_trace_id', trace_id)
        try:
            yield
        finally:
            previous_trace_id = self._trace_stack.pop()
            self.set('current_trace_id', previous_trace_id)