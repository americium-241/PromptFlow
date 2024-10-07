# data/actions/list_subconcepts_agent.py
from plugin_base import PluginBase
import ollama
import logging

class ListSubconceptsAgentPlugin(PluginBase):
    def __init__(self, context, debug=False):
        super().__init__(context, debug)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing ListSubconceptsAgentPlugin")
        self.register_action('list_subconcepts_agent', self.list_subconcepts_agent)

    def list_subconcepts_agent(self, *args, **kwargs):
        concept = self.di_layer.get('concept')
        self.logger.debug(f"Concept: {concept}")
        model = self.di_layer.get('model')
        parent_trace_id = self.di_layer.get('current_trace_id')

        # Render the prompt for listing subconcepts
        prompt = self.core_execute_action(
            'render_template',
            template_name='subconcepts_template.j2',
            test=concept,
            parent_trace_id=parent_trace_id  # Pass parent_trace_id here
        )

        self.logger.debug(f"Prompt for subconcepts of '{concept}':\n{prompt}")

        # Get response from the language model
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        answer = response['message']['content']
        self.di_layer.set('answer', answer)

        # Execute 'extract_json_objects' action
        self.core_execute_action('extract_json_objects', parent_trace_id=parent_trace_id)

        subconcepts = self.di_layer.get('json_objects')

        # Store the subconcepts for later use
        self.di_layer.set('subconcepts', subconcepts)
        return subconcepts