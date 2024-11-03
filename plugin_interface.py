# plugin_interface.py
from abc import ABC, abstractmethod

class Plugin(ABC):
    def __init__(self, context, debug=False):
        # Remove the call to super().__init__()
        # super().__init__()  # This line can be omitted
        self.context = context
        self.debug = debug


    def load(self):
        pass


    def unload(self):
        pass

    @abstractmethod
    def execute_action(self, action_name, *args, **kwargs):
        pass

    @abstractmethod
    def get_actions(self):
        pass
