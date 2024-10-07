# plugin_base.py
from plugin_interface import Plugin
from typing import Any, Callable, Dict
from logger import LoggerFactory
from custom_exceptions import PluginManagementError
from datetime import datetime
from models import ActionTrace, ActionStatus



class PluginBase(Plugin):
    def __init__(self, context: Any, debug: bool = False):
        self.context = context
        self.di_layer = context.di_layer
        self.core_execute_action = context.execute_action
        self.actions: Dict[str, Callable] = {}
        self.execution_id = self.di_layer.get('execution_id')
        self.db_session = self.di_layer.get('db_session')
        self.debug = debug  # Add this line to initialize self.debug

        # Initialize logger with execution_id
        self.logger = LoggerFactory.create_logger(
            self.__class__.__name__, debug, self.execution_id
        )

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
        # Get parent_trace_id from DI layer
        parent_trace_id = self.di_layer.get('current_trace_id')

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
            result = self._execute_plugin_action(action_name, *args, **kwargs)

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
            self.logger.error(f"Error executing plugin action '{action_name}': {e}")
            raise PluginManagementError(f"Error executing plugin action '{action_name}'.") from e
        finally:
            # Clear the current_trace_id from the DI layer
            self.di_layer.set('current_trace_id', None)


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
