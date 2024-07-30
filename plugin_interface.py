from abc import ABC, abstractmethod

class Plugin(ABC):
    def __init__(self, container, debug=False):
        self.container = container
        self.debug = debug

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def unload(self):
        pass

    @abstractmethod
    def execute_action(self, action_name, *args, **kwargs):
        pass

    @abstractmethod
    def get_actions(self):
        pass
