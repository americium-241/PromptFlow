# action_manager.py
import os
import importlib.util
import uuid
import inspect
from file_manager import FileManager
from typing import Any, Callable, Dict
from logger import LoggerFactory

class ActionManager:
    def __init__(
        self,
        debug: bool = False,
        directory: str = "data/actions",
        mapping_file: str = "action_mapping.json",
        execution_id: str = None
    ):
        self.debug = debug
        self.execution_id = execution_id
        self.logger = LoggerFactory.create_logger(
            self.__class__.__name__, self.debug, self.execution_id
        )
        self.file_manager = FileManager()
        self.directory = directory
        self.mapping_file = os.path.join(directory, mapping_file)
        os.makedirs(directory, exist_ok=True)
        self.actions_mapping: Dict[str, Dict[str, str]] = self._load_action_mapping()
        self.module_cache: Dict[str, Any] = {}
        self.actions: Dict[str, Callable] = {
            'add_action': self.add_action,
            'execute_action': self.execute_action,
            'list_actions': self.list_actions,
            'remove_action': self.remove_action,
        }

    def has_action(self, action_name: str) -> bool:
        return action_name in self.actions or action_name in self.actions_mapping

    def list_actions(self):
        return list(self.actions.keys()) + list(self.actions_mapping.keys())

    def add_action(self, action_name, func, func_name=None):
        filename = f"{uuid.uuid4()}.py"
        filepath = os.path.join(self.directory, filename)

        if not func_name:
            func_name = action_name

        try:
            source = inspect.getsource(func)
        except TypeError:
            raise ValueError("Function source code could not be determined. Please provide the function as a string.")

        if func.__name__ != func_name:
            source = source.replace(f"def {func.__name__}", f"def {func_name}", 1)

        with open(filepath, 'w') as file:
            file.write(source)

        self.actions_mapping[action_name] = {"filename": filename, "func_name": func_name}
        self._save_action_mapping()
        self.logger.debug(f"Added action: {action_name} with file: {filename}")

    def execute_action(self, action_name, *args, **kwargs):
        self.logger.debug(f"Executing action: {action_name}")
        if action_name in self.actions:
            return self.actions[action_name](*args, **kwargs)
        elif action_name in self.actions_mapping:
            action_info = self.actions_mapping[action_name]
            filename = action_info["filename"]
            func_name = action_info["func_name"]
            filepath = os.path.join(self.directory, filename)

            if action_name in self.module_cache:
                module = self.module_cache[action_name]
            else:
                spec = importlib.util.spec_from_file_location("module_" + action_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.module_cache[action_name] = module

            action_func = getattr(module, func_name)
            return action_func(*args, **kwargs)
        else:
            raise ValueError(f"No action defined for '{action_name}'.")

    def _load_action_mapping(self):
        return self.file_manager.read_json(self.mapping_file) or {}

    def _save_action_mapping(self):
        self.file_manager.write_json(self.mapping_file, self.actions_mapping)

    def remove_action(self, action_name):
        if action_name in self.actions_mapping:
            filename = self.actions_mapping[action_name]["filename"]
            filepath = os.path.join(self.directory, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.actions_mapping[action_name]
            self._save_action_mapping()
            self.logger.debug(f"Removed action: {action_name}")
        else:
            self.logger.debug(f"Action '{action_name}' not found.")
