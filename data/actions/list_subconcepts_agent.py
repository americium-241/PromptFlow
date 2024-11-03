# data/actions/list_subconcepts_agent.py
from plugin_base import PluginBase

class ListSubconceptsAgentPlugin(PluginBase):
    def __init__(self, context, debug=False):
        super().__init__(context, debug)
        self.register_action('list_subconcepts_agent', self.list_subconcepts_agent)

    def list_subconcepts_agent(self, *args, **kwargs):
        concept = self.di_layer.get('concept')
        parent_trace_id = self.di_layer.get('current_trace_id')

        # Render the prompt
        prompt = self.execute_action(
            'render_template',
            template_name='subconcepts_template.j2',
            test=concept,
            parent_trace_id=parent_trace_id
        )

        # Use the new 'ollama_chat' action
        answer = self.execute_action('ollama_chat', prompt=prompt, parent_trace_id=parent_trace_id)

        # Store the answer and extract JSON objects
        self.di_layer.set('answer', answer)
        self.execute_action('extract_json_objects', parent_trace_id=parent_trace_id)

        
        subconcepts = self.di_layer.get('json_objects')
        if not subconcepts:
            self.logger.warning("No subconcepts found.")
            return []
        self.di_layer.set('subconcepts', subconcepts)
        return subconcepts

