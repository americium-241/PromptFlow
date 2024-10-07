# should_explore_agent.py
from plugin_base import PluginBase
import ollama
import logging
# should_explore_agent.py

class ShouldExploreAgentPlugin(PluginBase):
    def __init__(self, context, debug=False):
        super().__init__(context, debug)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing ShouldExploreAgentPlugin")
        self.register_action('should_explore_agent', self.should_explore_agent)

    def should_explore_agent(self, *args, **kwargs):
        problem = self.di_layer.get('problem')
        concept = self.di_layer.get('concept')
        model = self.di_layer.get('model')

        # Get parent_trace_id from DI layer
        parent_trace_id = self.di_layer.get('current_trace_id')

        # Use self.core_execute_action to call core system actions
        prompt = self.core_execute_action(
            'render_template',
            template_name='should_explore_template.j2',
            problem=problem,
            concept=concept,
            parent_trace_id=parent_trace_id
        )


        if self.debug:
            print(f"Prompt for deciding whether to explore '{concept}':")
            print(prompt)

        # Get response from the language model
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        answer = response['message']['content']

        # Parse the response (expecting 'Yes' or 'No')
        decision = 'yes' in answer.lower()

        # Store the decision
        self.di_layer.set('should_explore', decision)

        return decision

