# plugin_base.py
from plugin_interface import Plugin
from typing import Any, Callable, Dict
from logger import LoggerFactory
from custom_exceptions import PluginManagementError
from datetime import datetime
from models import ActionTrace, ActionStatus

class PluginBase(Plugin):
    def __init__(self, context: Any, debug: bool = False):
        super().__init__(context, debug)
        self.context = context
        self.di_layer = context.di_layer
        self.execute_action = context.execute_action
        self.plugin_manager = context.plugin_manager
        self.actions: Dict[str, Callable] = {}
        self.execution_id = self.di_layer.get('execution_id') if self.di_layer else None
        self.db_session = self.di_layer.get('db_session')
        self.debug = debug
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)

    def register_action(self, action_name: str, func: Callable) -> None:
        self.logger.debug(f"Registering action: {action_name}")
        self.actions[action_name] = func
        self.plugin_manager.register_action(action_name, self)
        self.logger.debug(f"Registered action: {action_name}")

    def execute_action(self, action_name: str, *args: Any, parent_trace_id: str = None, **kwargs: Any) -> Any:
        self.logger.debug(f"Executing action: {action_name}")

        # Get parent_trace_id from parameter or DI layer
        if parent_trace_id is None:
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



        # Store current trace_id in the DI layer using context manager
        with self.di_layer.trace_context(action_trace.trace_id):
            try:
                if action_name in self.actions:
                    result = self.actions[action_name](*args, **kwargs)
                else:
                    # Delegate to the plugin manager
                    result = self.plugin_manager.execute_action(action_name, *args, **kwargs)

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
                raise PluginManagementError(f"Error executing action '{action_name}'.") from e

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