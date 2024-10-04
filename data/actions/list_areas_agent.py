from plugin_base import PluginBase
import ollama
import logging

class ListAreasAgentPlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing ListAreasAgentPlugin")
        self.register_action('list_areas_agent', self.list_areas_agent)
        self.logger.debug("Registered action list_areas_agent")

    def list_areas_agent(self, *args, **kwargs):
        problem = self.execute('container_get', 'problem')
        model = self.execute('container_get', 'model')

        # Render the prompt for listing areas
        prompt = self.execute('render_template', 'render_template', 'areas_template.j2', problem=problem)
        print("Prompt for conceptual areas:")
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
        conceptual_areas = self.execute('container_get', 'json_objects')

        print(f"Conceptual Areas: {conceptual_areas}")
        # Store the conceptual areas for later use
        self.execute('container_set', key='conceptual_areas', value=conceptual_areas)
        return conceptual_areas
