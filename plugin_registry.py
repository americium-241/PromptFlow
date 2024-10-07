# plugin_registry.py
from typing import Dict, Any, List
from logger import LoggerFactory
from custom_exceptions import PluginRegistryError

class PluginRegistry:
    def __init__(self, debug: bool = False, execution_id: str = None):
        self.debug = debug
        self.execution_id = execution_id
        self.logger = LoggerFactory.create_logger(
            self.__class__.__name__, self.debug, self.execution_id
        )
        self.plugins: Dict[str, Any] = {}
        self.actions: Dict[str, Any] = {}

    def register_plugin(self, plugin_instance: Any) -> None:
        self.plugins[plugin_instance.__class__.__name__] = plugin_instance
        self._register_actions(plugin_instance)

    def _register_actions(self, plugin_instance: Any) -> None:
        for action_name in plugin_instance.get_actions():
            self.register_action(action_name, plugin_instance)

    def register_action(self, action_name: str, plugin_instance: Any) -> None:
        self.logger.debug(f"Registering action {action_name} from plugin {plugin_instance.__class__.__name__}")
        if action_name in self.actions:
            self.logger.warning(f"Action {action_name} is already registered. Overwriting with new plugin.")
        self.actions[action_name] = plugin_instance

    def execute_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing action: {action_name}")
        try:
            if action_name in self.actions:
                plugin_instance = self.actions[action_name]
                return plugin_instance.execute_action(action_name, *args, **kwargs)
            else:
                self.logger.error(f"No action defined for '{action_name}'")
                raise PluginRegistryError(f"No action defined for '{action_name}'.")
        except PluginRegistryError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error executing action '{action_name}': {e}")
            raise PluginRegistryError(f"Error executing action '{action_name}'.") from e

    def has_action(self, action_name: str) -> bool:
        return action_name in self.actions

    def get_actions(self) -> List[str]:
        return list(self.actions.keys())
