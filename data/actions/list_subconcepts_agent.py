# data/actions/list_subconcepts_agent.py
from plugin_base import PluginBase
import ollama
import logging

class ListSubconceptsAgentPlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing ListSubconceptsAgentPlugin")
        self.register_action('list_subconcepts_agent', self.list_subconcepts_agent)
        self.logger.debug("Registered action list_subconcepts_agent")

    def list_subconcepts_agent(self, *args, **kwargs):
        concept = self.execute('container_get', 'concept')
        print('___________________________________________ PLUGIN')
        print(concept)
        model = self.execute('container_get', 'model')

        # Render the prompt for listing subconcepts
        prompt = self.execute('render_template', 'render_template', 'subconcepts_template.j2', test=concept)
        print(f"Prompt for subconcepts of '{concept}':")
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
        subconcepts = self.execute('container_get', 'json_objects')

        # Store the subconcepts for later use
        self.execute('container_set', key='subconcepts', value=subconcepts)
        return subconcepts
