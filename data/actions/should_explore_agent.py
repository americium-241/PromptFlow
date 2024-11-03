# data/actions/should_explore_agent.py
from plugin_base import PluginBase

# data/actions/should_explore_agent.py

class ShouldExploreAgentPlugin(PluginBase):
    def __init__(self, context, debug=False):
        super().__init__(context, debug)
        self.register_action('should_explore_agent', self.should_explore_agent)

    def should_explore_agent(self, *args, **kwargs):
        problem = self.di_layer.get('problem')
        concept = self.di_layer.get('concept')
        parent_trace_id = self.di_layer.get('current_trace_id')

        # Render the prompt
        prompt = self.execute_action(
            'render_template',
            template_name='should_explore_template.j2',
            problem=problem,
            concept=concept,
            parent_trace_id=parent_trace_id
        )
        # Use the new 'ollama_chat' action
        answer = self.execute_action('ollama_chat', prompt=prompt, parent_trace_id=parent_trace_id)

        # Parse the response
        decision = 'yes' in answer.lower()
        self.di_layer.set('should_explore', decision)
        return decision
