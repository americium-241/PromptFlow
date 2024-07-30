# dependency_injection_layer.py
import logging
from typing import Any, Optional, Dict
from logger import LoggerFactory
from custom_exceptions import DependencyInjectionError

class DependencyInjectionLayer:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, self.debug)
        self.data: Dict[str, Any] = {}
        self.actions = {
            'container_set': self.set,
            'container_get': self.get
        }

    def set(self, key: str, value: Any, expected_type: Optional[type] = None) -> None:
        if expected_type and not isinstance(value, expected_type):
            raise DependencyInjectionError(f"Value for {key} must be of type {expected_type}")
        self.data[key] = value
        self.logger.debug(f"Set {key} to {value}")

    def get(self, key: str, expected_type: Optional[type] = None) -> Any:
        value = self.data.get(key)
        if expected_type and not isinstance(value, expected_type):
            raise DependencyInjectionError(f"Value for {key} is not of the expected type {expected_type}")
        self.logger.debug(f"Retrieved {key}: {value}")
        return value

    def execute(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        if action_name in self.actions:
            return self.actions[action_name](*args, **kwargs)
        plugin_manager = self.get('plugin_manager')
        return plugin_manager.execute_action(action_name, *args, **kwargs)

    def register_with_plugin_manager(self, plugin_manager: Any) -> None:
        for action_name in self.actions:
            plugin_manager.register_action(action_name, self)
