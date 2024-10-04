# string_manager.py
import json
import os
from jinja2 import Environment, FileSystemLoader, Template
from typing import Any, Dict
from logger import LoggerFactory

class StringManager:
    def __init__(self, debug: bool = False, template_dir: str = "data/templates", string_dir: str = "data/strings"):
        self.debug = debug
        self.logger = LoggerFactory.create_logger(self.__class__.__name__, self.debug)
        self.template_dir = template_dir
        self.string_dir = string_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.strings: Dict[str, Any] = self._load_strings()

    def _load_strings(self):
        strings = {}
        for filename in os.listdir(self.string_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.string_dir, filename), 'r') as f:
                    strings.update(json.load(f))
        return strings

    def render_template(self, template_name: str, **kwargs):
        self.logger.debug(f"Rendering template: {template_name} with context: {kwargs}")
        template = self.env.get_template(template_name)
        context = self.strings.copy()
        context.update(kwargs)
        
        # Render strings in context that may contain placeholders
        for key, value in context.items():
            if isinstance(value, str):
                # Use Jinja2 Template to render the string with the current context
                template_string = Template(value)
                context[key] = template_string.render(context)
        
        rendered_output = template.render(context)
        self.logger.debug(f"Rendered output: {rendered_output}")
        return rendered_output