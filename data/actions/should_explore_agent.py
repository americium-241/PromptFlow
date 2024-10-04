# should_explore_agent.py
from plugin_base import PluginBase
import ollama
import logging

class ShouldExploreAgentPlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.logger = logging.getLogger(__name__)
        self.register_action('should_explore_agent', self.should_explore_agent)

    def should_explore_agent(self, *args, **kwargs):
        problem = self.execute('container_get', 'problem')
        concept = self.execute('container_get', 'concept')
        model = self.execute('container_get', 'model')

        # Render the prompt
        prompt = self.execute(
            'render_template',
            'render_template',
            'should_explore_template.j2',
            problem=problem,
            concept=concept
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
        self.execute('container_set', key='should_explore', value=decision)

        return decision
