from plugin_base import PluginBase
import ollama
import logging
import json

class RatingAgentPlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing RatingAgentPlugin")
        self.register_action('rating_agent', self.rating_agent)
        self.logger.debug("Registered action rating_agent")
    
    def rating_agent(self, *args, **kwargs):
        problem = self.execute('container_get', 'problem')
        model = self.execute('container_get', 'model')
        items = self.execute('container_get', 'items_to_rate')  # Should be set before calling this agent
        item_type = self.execute('container_get', 'item_type')  # 'areas' or 'considerations'
        
        # Prepare the items_list as a JSON string
        # Flatten the items into a list
        flat_items = []
        for item_dict in items:
            for key, value in item_dict.items():
                flat_items.append(value)
        
        # Create a new items_list in the format {"item_0": "text", ...}
        items_list_dict = {f'item_{i}': text for i, text in enumerate(flat_items)}
        items_list_json = json.dumps(items_list_dict, indent=4)
        
        # Render the prompt for rating
        prompt = self.execute('render_template', 'render_template', 'rating_template.j2', problem=problem, items_list=items_list_json)
        print(f"Prompt for rating {item_type}:")
        print(prompt)
        
        # Get response from the language model
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        answer = response['message']['content']
        self.execute('container_set', key='answer', value=answer)
        self.execute('extract_json_objects')
        rated_items = self.execute('container_get', 'json_objects')
        
        print(f"Rated {item_type.capitalize()}: {rated_items}")
        # Store the rated items
        self.execute('container_set', key=f'rated_{item_type}', value=rated_items)
        return rated_items
