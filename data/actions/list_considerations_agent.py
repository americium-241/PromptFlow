# list_considerations_agent.py
from plugin_base import PluginBase
import ollama
import logging

class ListConsiderationsAgentPlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing ListConsiderationsAgentPlugin")
        self.register_action('list_considerations_agent', self.list_considerations_agent)
        self.logger.debug("Registered action list_considerations_agent")

    def list_considerations_agent(self, *args, **kwargs):
        problem = self.execute('container_get', 'problem')
        model = self.execute('container_get', 'model')
        conceptual_area = self.execute('container_get', 'conceptual_area')

        # Render the prompt for listing considerations
        prompt = self.execute('render_template', 'render_template', 'considerations_template.j2', problem=problem, conceptual_area=conceptual_area)
        print(f"Prompt for considerations of {conceptual_area}:")
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
        considerations = self.execute('container_get', 'json_objects')

        # Store the considerations for later use
        self.execute('container_set', key='considerations', value=considerations)
        return considerations
