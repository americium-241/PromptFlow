import json
import os
from jinja2 import Environment, FileSystemLoader, Template
from plugin_base import PluginBase
from typing import Any, Dict

class StringManagerPlugin(PluginBase):
    def __init__(self, container: Any, debug: bool = False, template_dir: str = "data/templates", string_dir: str = "data/strings"):
        super().__init__(container, debug)
        self.template_dir = template_dir
        self.string_dir = string_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.strings: Dict[str, Any] = self._load_strings()
        self.register_action('render_template', self.render_template)

    def load(self):
        if not self.container.get('string_manager'):
            self.container.set('string_manager', self)
            if self.debug:
                print(f"StringManagerPlugin: Registered self as 'string_manager'")

    def _load_strings(self):
        strings = {}
        for filename in os.listdir(self.string_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.string_dir, filename), 'r') as f:
                    strings.update(json.load(f))
        return strings

    def render_template(self, action_name: str, template_name: str, **kwargs):
        print(f"____________________________render_template: {kwargs}")
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
        print('_________________________', rendered_output)
        return rendered_output
