# plugin_base.py
from plugin_interface import Plugin
from typing import Any, Callable, Dict
from logger import LoggerFactory
from custom_exceptions import PluginManagementError

class PluginBase(Plugin):
    def __init__(self, context: Any, debug: bool = False):
        super().__init__(context, debug)  # This calls Plugin.__init__(context, debug)
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, debug)
        self.context = context
        self.di_layer = context.di_layer
        self.core_execute_action = context.execute_action
        self.actions: Dict[str, Callable] = {}
        self.load()

    def register_action(self, action_name: str, func: Callable) -> None:
        self.logger.debug(f"Registering action: {action_name}")
        self.actions[action_name] = func
        self.context.plugin_manager.register_action(action_name, self)
        self.logger.debug(f"Registered action: {action_name}")

    def load(self) -> None:
        self.logger.debug(f"Loading plugin: {self.__class__.__name__}")
        self.logger.debug(f"Actions registered for plugin: {self.__class__.__name__}")

    def unload(self) -> None:
        pass  # Implement if needed

    def execute_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        # Implement the abstract method by calling the plugin-specific action executor
        return self._execute_plugin_action(action_name, *args, **kwargs)

    def _execute_plugin_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing plugin action in {self.__class__.__name__}: {action_name}")
        if action_name in self.actions:
            return self.actions[action_name](*args, **kwargs)
        else:
            raise PluginManagementError(
                f"No action defined for '{action_name}' in {self.__class__.__name__}."
            )

    def get_actions(self) -> list:
        return list(self.actions.keys())
