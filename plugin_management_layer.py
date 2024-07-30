# plugin_management_layer.py
import logging
from typing import Any, List
from plugin_loader import PluginLoader
from plugin_registry import PluginRegistry
from logger import LoggerFactory
from custom_exceptions import PluginManagementError

class PluginManagementLayer:
    def __init__(self, plugin_directories: list, container: Any, debug: bool = False):
        self.container = container
        self.debug = debug
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, self.debug)
        self.logger.debug("Initializing PluginManagementLayer")

        self.loader = PluginLoader(plugin_directories, debug)
        self.registry = PluginRegistry(debug)

    def load_plugins(self) -> None:
        self.logger.debug("Loading plugins")
        try:
            plugins = self.loader.load_plugins()
            for plugin_class in plugins.values():
                self.logger.debug(f"Instantiating plugin class: {plugin_class}")
                plugin_instance = plugin_class(self.container, self.debug)
                self.logger.debug(f"Loading plugin instance: {plugin_instance}")
                plugin_instance.load()
                self.registry.register_plugin(plugin_instance)
                self.logger.debug(f"Loaded and registered plugin: {plugin_instance.__class__.__name__}")
        except Exception as e:
            self.logger.error(f"Failed to load plugins: {str(e)}")
            raise PluginManagementError(f"Failed to load plugins: {str(e)}")

    def register_action(self, action_name: str, plugin_instance: Any) -> None:
        self.logger.debug(f"Registering action {action_name} from plugin {plugin_instance.__class__.__name__}")
        self.registry.register_action(action_name, plugin_instance)

    def execute_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing action: {action_name}")
        return self.registry.execute_action(action_name, *args, **kwargs)

    def list_actions(self) -> List[str]:
        return self.registry.get_actions()
