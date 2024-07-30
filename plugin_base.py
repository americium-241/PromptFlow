# plugin_base.py
from plugin_interface import Plugin
from typing import Any, Callable, Dict
import logging
from logger import LoggerFactory
from custom_exceptions import PluginManagementError

class PluginBase(Plugin):
    def __init__(self, container: Any, debug: bool = False):
        super().__init__(container, debug)
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, debug)
        self.container = container
        self.core_system = container.get('core_system', None)
        
        self.actions: Dict[str, Callable] = {}
        self.load()

    def execute(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing action: {action_name}")
        return self.container.get('core_system').execute(action_name, *args, **kwargs)

    def register_action(self, action_name: str, func: Callable) -> None:
        self.logger.debug(f"Registering action: {action_name}")
        self.actions[action_name] = func
        plugin_manager = self.container.get('plugin_manager')
        plugin_manager.register_action(action_name, self)
        self.logger.debug(f"Registered action: {action_name}")

    def load(self) -> None:
        self.logger.debug(f"Loading plugin: {self.__class__.__name__}")
        for action_name, action_func in self.actions.items():
            self.register_action(action_name, action_func)
        self.logger.debug(f"Actions registered for plugin: {self.__class__.__name__}")

    def unload(self) -> None:
        pass

    def execute_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing action in {self.__class__.__name__}: {action_name}")
        if action_name in self.actions:
            return self.actions[action_name](*args, **kwargs)
        else:
            raise PluginManagementError(f"No action defined for '{action_name}' in {self.__class__.__name__}.")

    def get_actions(self) -> list[str]:
        return list(self.actions.keys())
