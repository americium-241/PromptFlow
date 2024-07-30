# plugin_loader.py
import importlib.util
import os
import logging
import inspect
from typing import Dict, Any
from plugin_base import PluginBase
from logger import LoggerFactory
from custom_exceptions import PluginLoaderError

class PluginLoader:
    def __init__(self, directories: list[str], debug: bool = False):
        self.directories = directories
        self.debug = debug
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, self.debug)
        self.logger.debug(f"PluginLoader initialized with directories: {directories}")

    def load_plugins(self) -> Dict[str, Any]:
        plugins: Dict[str, Any] = {}
        for directory in self.directories:
            self.logger.debug(f"Loading plugins from directory: {directory}")
            if not os.path.exists(directory):
                self.logger.warning(f"Plugin directory does not exist: {directory}")
                continue
            plugins.update(self._load_plugins_from_directory(directory))
        return plugins

    def _load_plugins_from_directory(self, directory: str) -> Dict[str, Any]:
        plugins: Dict[str, Any] = {}
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                self.logger.debug(f"Loading plugin: {filename}")
                try:
                    module = self._load_module(os.path.join(directory, filename))
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                            plugins[obj.__name__] = obj
                            self.logger.debug(f"Loaded plugin class: {obj.__name__}")
                except Exception as e:
                    self.logger.error(f"Error loading plugin from {filename}: {str(e)}")
                    raise PluginLoaderError(f"Error loading plugin from {filename}: {str(e)}")
        return plugins

    def _load_module(self, filepath: str) -> Any:
        spec = importlib.util.spec_from_file_location("plugin_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
