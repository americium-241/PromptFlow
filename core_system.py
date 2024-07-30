# core_system.py
import logging
from typing import List, Any, Optional, Dict
from plugin_management_layer import PluginManagementLayer
from dependency_injection_layer import DependencyInjectionLayer
from logger import LoggerFactory
from custom_exceptions import CoreSystemError

class CoreSystem:
    def __init__(self, config: Dict[str, Any]):
        self.debug = config.get('debug', True)
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, self.debug)
        self.logger.debug(f"Initializing CoreSystem with config: {config}")

        self.di_layer = DependencyInjectionLayer(self.debug)
        self.plugin_layer = PluginManagementLayer(config.get('plugin_directory', []), self.di_layer, self.debug)
        
        self._initialize_dependencies()
        self._initialize_core_plugins(config.get('template_dir', ""), config.get('string_dir', ""))

    def _initialize_dependencies(self):
        self.logger.debug("Initializing dependencies")
        try:
            self.di_layer.set('core_system', self)
            self.di_layer.set('plugin_manager', self.plugin_layer)
            self.di_layer.register_with_plugin_manager(self.plugin_layer)
            self.plugin_layer.load_plugins()
        except Exception as e:
            self.logger.error(f"Failed to initialize dependencies: {str(e)}")
            raise CoreSystemError(f"Failed to initialize dependencies: {str(e)}")

    def _initialize_core_plugins(self, template_dir: str, string_dir: str) -> None:
        from base_plugin_lib.action_manager import ActionManagerPlugin
        from base_plugin_lib.string_manager import StringManagerPlugin

        self._initialize_plugin('action_manager', ActionManagerPlugin, template_dir, string_dir)
        self._initialize_plugin('string_manager', StringManagerPlugin, template_dir, string_dir)

    def _initialize_plugin(self, key: str, plugin_class: Any, *args: Any):
        if not self.di_layer.get(key):
            self.logger.debug(f"Initializing plugin: {key}")
            plugin = plugin_class(self.di_layer, self.debug, *args)
            plugin.load()
            self.di_layer.set(key, plugin)

    def execute(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        try:
            self.logger.debug(f"Executing action: {action_name}")
            result = self.di_layer.execute(action_name, *args, **kwargs)
            self.logger.debug(f"Action {action_name} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error executing action '{action_name}': {str(e)}")
            raise CoreSystemError(f"Error executing action '{action_name}': {str(e)}")

    def set(self, key: str, value: Any, expected_type: Optional[type] = None) -> None:
        self.di_layer.set(key, value, expected_type)

    def get(self, key: str, expected_type: Optional[type] = None) -> Any:
        return self.di_layer.get(key, expected_type)
