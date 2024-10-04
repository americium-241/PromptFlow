# data/actions/complexity_estimator_agent.py
from plugin_base import PluginBase
import ollama
import logging

class ComplexityEstimatorAgentPlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing ComplexityEstimatorAgentPlugin")
        self.register_action('complexity_estimator_agent', self.complexity_estimator_agent)
        self.logger.debug("Registered action complexity_estimator_agent")

    def complexity_estimator_agent(self, *args, **kwargs):
        problem = self.execute('container_get', 'problem')
        model = self.execute('container_get', 'model')

        # Render the prompt for estimating complexity
        prompt = self.execute('render_template', 'render_template', 'complexity_estimator_template.j2', problem=problem)
        if self.debug:
            print("Prompt for estimating complexity:")
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
        complexity_estimate = self.execute('container_get', 'json_objects')

        # Store the complexity estimate
        self.execute('container_set', key='complexity_estimate', value=complexity_estimate)
        return complexity_estimate
