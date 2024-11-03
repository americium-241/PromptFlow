# plugin_loader.py
import importlib.util
import os
import inspect
from typing import Dict, Any
from plugin_base import PluginBase
from logger import LoggerFactory
from custom_exceptions import PluginLoaderError
class PluginLoader:
    def __init__(self, directories, plugin_registry):
        self.directories = directories
        self.plugin_registry = plugin_registry
        self.loaded_plugins = set()
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)

    def load_plugins(self, context):
        for directory in self.directories:
            for filename in os.listdir(directory):
                if filename.endswith('.py') and filename != '__init__.py':
                    plugin_path = os.path.join(directory, filename)
                    if plugin_path in self.loaded_plugins:
                        self.logger.debug(f"Plugin {filename} already loaded. Skipping.")
                        continue
                    self.loaded_plugins.add(plugin_path)
                    self._load_plugin(plugin_path, context)

    def _load_plugin(self, plugin_path, context):
        spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if inspect.isclass(attribute) and issubclass(attribute, PluginBase) and attribute is not PluginBase:
                plugin_instance = attribute(context) # Pass context correctly
                self.plugin_registry.register_plugin(plugin_instance)
                self.logger.debug(f"Loaded and registered plugin: {attribute.__name__}")
    def _load_module(self, filepath: str) -> Any:
        spec = importlib.util.spec_from_file_location("plugin_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
