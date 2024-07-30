import os
import importlib.util
import uuid
import inspect
from file_manager import FileManager
from plugin_base import PluginBase
from typing import Any, Callable, Dict, List, Optional

class ActionManagerPlugin(PluginBase):
    def __init__(self, container: Any, debug: bool = False, directory: str = "data/actions", mapping_file: str = "action_mapping.json"):
        super().__init__(container, debug)
        self.file_manager = FileManager()
        self.directory = directory
        self.mapping_file = os.path.join(directory, mapping_file)
        os.makedirs(directory, exist_ok=True)
        self.actions_mapping: Dict[str, Dict[str, str]] = self._load_action_mapping()
        self.module_cache: Dict[str, Any] = {}
        self.register_action('add_action', self.add_action)
        self.register_action('execute_action', self.execute_action)
        self.register_action('list_actions', self.list_actions)
        self.register_action('remove_action', self.remove_action)

    def list_actions(self, *args, **kwargs):
        plugin_manager = self.container.get('plugin_manager')
        return plugin_manager.list_actions()

    def load(self):
        if not self.container.get('action_manager'):
            self.container.set('action_manager', self)
            if self.debug:
                print(f"ActionManagerPlugin: Registered self as 'action_manager'")

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
        print(f"Added action: {action_name} with file: {filename}")

    def execute_action(self, action_name, *args, **kwargs):
        print(f"Executing action in ActionManagerPlugin: {action_name} with args: {args} kwargs: {kwargs}")
        plugin_manager = self.container.get('plugin_manager')
        if action_name in plugin_manager.actions:
            return plugin_manager.execute_action(action_name, *args, **kwargs)
        elif action_name in self.actions_mapping:
            action_info = self.actions_mapping[action_name]
            filename = action_info["filename"]
            func_name = action_info["func_name"]
            filepath = os.path.join(self.directory, filename)

            spec = importlib.util.spec_from_file_location("module_" + action_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
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
            print(f"Removed action: {action_name}")
        else:
            print(f"Action '{action_name}' not found.")
