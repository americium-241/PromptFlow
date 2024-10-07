# core_system.py
import logging
import uuid
from datetime import datetime
from typing import Any, Dict
from plugin_management_layer import PluginManagementLayer
from dependency_injection_layer import DependencyInjectionLayer
from logger import LoggerFactory
from custom_exceptions import CoreSystemError
from base_plugin_lib.action_manager import ActionManager
from base_plugin_lib.string_manager import StringManager
from database import SessionLocal
from models import ExecutionSession, ActionTrace, ActionStatus

class PluginContext:
    def __init__(self, di_layer, execute_action, plugin_manager):
        self.di_layer = di_layer
        self.execute_action = execute_action
        self.plugin_manager = plugin_manager

class CoreSystem:
    def __init__(self, config: Dict[str, Any]):
        self.debug = config.get('debug', True)
        self.di_layer = DependencyInjectionLayer(self.debug)

        # Generate or retrieve execution_id
        self.execution_id = self.di_layer.get('execution_id', default=str(uuid.uuid4()))
        self.di_layer.set('execution_id', self.execution_id)

        # Initialize database session
        self.db_session = SessionLocal()
        self.di_layer.set('db_session', self.db_session)

        # Create ExecutionSession entry
        self.execution_session = ExecutionSession(
            execution_id=self.execution_id,
            start_time=datetime.utcnow()
        )
        self.db_session.add(self.execution_session)
        self.db_session.commit()

        # Initialize logger with execution_id
        self.logger = LoggerFactory.create_logger(
            self.__class__.__name__, self.debug, self.execution_id
        )
        self.logger.debug(f"Initializing CoreSystem with config: {config}")

        # Initialize Plugin Management Layer
        self.plugin_layer = PluginManagementLayer(
            config.get('plugin_directory', []), self.debug, self.execution_id
        )

        # Initialize Core Services
        self.action_manager = ActionManager(
            self.debug,
            directory=config.get('action_directory', "data/actions"),
            execution_id=self.execution_id
        )
        self.string_manager = StringManager(
            self.debug,
            template_dir=config.get('template_dir', ""),
            string_dir=config.get('string_dir', ""),
            execution_id=self.execution_id
        )

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

    

    def execute_action(self, action_name: str, *args: Any, parent_trace_id: str = None, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing action: {action_name}")

        # Create ActionTrace entry
        action_trace = ActionTrace(
            execution_id=self.execution_id,
            action_name=action_name,
            component=self.__class__.__name__,
            start_time=datetime.utcnow(),
            status=ActionStatus.STARTED,
            input_data={'args': args, 'kwargs': kwargs},
            parent_trace_id=parent_trace_id
        )
        self.db_session.add(action_trace)
        self.db_session.commit()

        # Store current trace_id in the DI layer
        self.di_layer.set('current_trace_id', action_trace.trace_id)

        try:
            # Execute the action as before
            if self.action_manager.has_action(action_name):
                result = self.action_manager.execute_action(action_name, *args, **kwargs)
            elif hasattr(self.string_manager, action_name):
                action = getattr(self.string_manager, action_name)
                result = action(*args, **kwargs)
            elif self.plugin_layer.has_action(action_name):
                result = self.plugin_layer.execute_action(action_name, *args, **kwargs)
            else:
                raise CoreSystemError(f"No action named '{action_name}' found.")

            # Update ActionTrace
            action_trace.end_time = datetime.utcnow()
            action_trace.status = ActionStatus.COMPLETED
            action_trace.output_data = {'result': result}
            self.db_session.commit()
            return result

        except Exception as e:
            # Update ActionTrace
            action_trace.end_time = datetime.utcnow()
            action_trace.status = ActionStatus.FAILED
            action_trace.output_data = {'error': str(e)}
            self.db_session.commit()
            self.logger.error(f"Error executing action '{action_name}': {e}")
            raise CoreSystemError(f"Error executing action '{action_name}'.") from e
        finally:
            # Clear the current_trace_id from the DI layer
            self.di_layer.set('current_trace_id', None)

    def set(self, key: str, value: Any, expected_type: Any = None) -> None:
        self.di_layer.set(key, value, expected_type)

    def get(self, key: str, expected_type: Any = None) -> Any:
        return self.di_layer.get(key, expected_type)
