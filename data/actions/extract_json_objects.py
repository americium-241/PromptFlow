from plugin_base import PluginBase
import json

class ExtractJsonObjectsPlugin(PluginBase):
    def __init__(self, di_container, debug=False):
        super().__init__(di_container, debug)
        self.register_action('extract_json_objects', self.extract_json_objects)
    
    def extract_json_objects(self, *args, **kwargs):
        if self.debug:
            print("ExtractJsonObjectsPlugin: Executing extract_json_objects")
    
        text = self.execute('container_get', 'answer')
    
        if self.debug:
            print(f"ExtractJsonObjectsPlugin: Retrieved answer text: {text[:100]}...")
    
        # Find the first '{' and last '}' in the text
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            if self.debug:
                print(f"Extracted JSON string: {json_str[:100]}...")
            try:
                json_obj = json.loads(json_str)
                json_objects = [json_obj]
            except json.JSONDecodeError as e:
                if self.debug:
                    print(f"Error parsing JSON string: {e}")
                json_objects = []
        else:
            if self.debug:
                print("No JSON object found in the text.")
            json_objects = []
    
        self.execute('container_set', key='json_objects', value=json_objects)
        return json_objects
