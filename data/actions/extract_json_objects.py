# data/actions/extract_json_objects.py
from plugin_base import PluginBase
import json

class ExtractJsonObjectsPlugin(PluginBase):
    def __init__(self, context, debug=False):
        super().__init__(context, debug)  # Calls PluginBase.__init__(context, debug)
        self.logger.debug("Initializing ExtractJsonObjectsPlugin")
        self.register_action('extract_json_objects', self.extract_json_objects)
        
    def extract_json_objects(self, *args, **kwargs):
        self.logger.debug("Executing extract_json_objects action")

        # Retrieve the 'answer' text from the DI layer
        text = self.di_layer.get('answer')

        self.logger.debug(f"Retrieved answer text: {text[:100]}...")

        # Extract JSON objects from the text
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            self.logger.debug(f"Extracted JSON string: {json_str[:100]}...")
            try:
                json_obj = json.loads(json_str)
                json_objects = [json_obj]
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON string: {e}")
                json_objects = []
        else:
            self.logger.warning("No JSON object found in the text.")
            json_objects = []

        # Store the json_objects in the DI layer
        self.di_layer.set('json_objects', json_objects)
        return json_objects
