# dependency_injection_layer.py
from typing import Any, Optional, Dict
from logger import LoggerFactory
from custom_exceptions import DependencyInjectionError

class DependencyInjectionLayer:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = LoggerFactory.create_logger(
            self.__class__.__name__, self.debug
        )
        self.data: Dict[str, Any] = {}

    def set(self, key: str, value: Any, expected_type: Optional[type] = None) -> None:
        if expected_type and not isinstance(value, expected_type):
            raise DependencyInjectionError(
                f"Value for {key} must be of type {expected_type}"
            )
        self.data[key] = value
        self.logger.debug(f"Set {key} to {value}")

    def get(
        self, key: str, default: Any = None, expected_type: Optional[type] = None
    ) -> Any:
        value = self.data.get(key, default)
        if expected_type and not isinstance(value, expected_type):
            raise DependencyInjectionError(
                f"Value for {key} is not of the expected type {expected_type}"
            )
        self.logger.debug(f"Retrieved {key}: {value}")
        return value
