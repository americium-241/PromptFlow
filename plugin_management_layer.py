# plugin_management_layer.py
from plugin_loader import PluginLoader
from plugin_registry import PluginRegistry
from custom_exceptions import PluginRegistryError
from logger import LoggerFactory
from custom_exceptions import PluginManagementError
from typing import Any

class PluginManagementLayer:
    def __init__(self, plugin_directories: list, debug: bool = False, execution_id: str = None, core_system=None):
        self.debug = debug
        self.execution_id = execution_id
        self.core_system = core_system
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)
        self.registry = PluginRegistry(debug, execution_id)
        self.loader = PluginLoader(plugin_directories, self.registry)

    def load_plugins(self, context: Any) -> None:
        self.logger.debug("Loading plugins")
        try:
            self.loader.load_plugins(context)
        except Exception as e:
            self.logger.error(f"Failed to load plugins: {str(e)}")
            raise PluginManagementError(f"Failed to load plugins: {str(e)}")

    def register_action(self, action_name: str, plugin_instance: Any) -> None:
        self.logger.debug(f"Registering action {action_name} from plugin {plugin_instance.__class__.__name__}")
        self.registry.register_action(action_name, plugin_instance)

    def execute_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        try:
            return self.registry.execute_action(action_name, *args, **kwargs)
        except PluginRegistryError:
            # Delegate to core system
            if self.core_system and self.core_system.action_manager.has_action(action_name):
                return self.core_system.action_manager.execute_action(action_name, *args, **kwargs)
            else:
                raise PluginManagementError(f"No action defined for '{action_name}' in plugins or core system.")

    def has_action(self, action_name: str) -> bool:
        return self.registry.has_action(action_name)

    def list_actions(self) -> list:
        return self.registry.get_actions()
