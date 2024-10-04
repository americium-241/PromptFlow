# core_system.py
import logging
from typing import Any, Dict
from plugin_management_layer import PluginManagementLayer
from dependency_injection_layer import DependencyInjectionLayer
from logger import LoggerFactory
from custom_exceptions import CoreSystemError
from base_plugin_lib.action_manager import ActionManager
from base_plugin_lib.string_manager import StringManager

class PluginContext:
    def __init__(self, di_layer, execute_action, plugin_manager):
        self.di_layer = di_layer
        self.execute_action = execute_action
        self.plugin_manager = plugin_manager

class CoreSystem:
    def __init__(self, config: Dict[str, Any]):
        self.debug = config.get('debug', True)
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, self.debug)
        self.logger.debug(f"Initializing CoreSystem with config: {config}")

        # Initialize Dependency Injection Layer
        self.di_layer = DependencyInjectionLayer(self.debug)
        # Initialize Plugin Management Layer
        self.plugin_layer = PluginManagementLayer(config.get('plugin_directory', []), self.debug)
        
        # Initialize Core Services
        self.action_manager = ActionManager(self.debug, directory=config.get('action_directory', "data/actions"))
        self.string_manager = StringManager(self.debug, template_dir=config.get('template_dir', ""), string_dir=config.get('string_dir', ""))

        # Set up dependencies
        self._initialize_dependencies()

        # Set up context for plugins
        self.plugin_context = PluginContext(
            di_layer=self.di_layer,
            execute_action=self.execute_action,
            plugin_manager=self.plugin_layer
        )

        # Load plugins
        self.plugin_layer.load_plugins(self.plugin_context)

    def _initialize_dependencies(self):
        self.logger.debug("Initializing dependencies")
        try:
            self.di_layer.set('core_system', self)
            self.di_layer.set('action_manager', self.action_manager)
            self.di_layer.set('string_manager', self.string_manager)
            self.di_layer.set('plugin_manager', self.plugin_layer)
        except Exception as e:
            self.logger.error(f"Failed to initialize dependencies: {str(e)}")
            raise CoreSystemError(f"Failed to initialize dependencies: {str(e)}")

    def execute_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing action: {action_name}")
        try:
            # First check if action is in action_manager
            if self.action_manager.has_action(action_name):
                return self.action_manager.execute_action(action_name, *args, **kwargs)
            # Then check if action is in string_manager
            elif hasattr(self.string_manager, action_name):
                action = getattr(self.string_manager, action_name)
                return action(*args, **kwargs)
            # Then check plugin actions
            elif self.plugin_layer.has_action(action_name):
                return self.plugin_layer.execute_action(action_name, *args, **kwargs)
            else:
                raise CoreSystemError(f"No action named '{action_name}' found.")
        except CoreSystemError as e:
            raise e  # Re-raise without modification
        except Exception as e:
            self.logger.error(f"Error executing action '{action_name}': {e}")
            raise CoreSystemError(f"Error executing action '{action_name}'.") from e


    def set(self, key: str, value: Any, expected_type: Any = None) -> None:
        self.di_layer.set(key, value, expected_type)

    def get(self, key: str, expected_type: Any = None) -> Any:
        return self.di_layer.get(key, expected_type)
