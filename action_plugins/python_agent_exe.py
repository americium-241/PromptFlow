# action_plugins/python_agent_exe.py
from plugin_base import PluginBase
import ollama
import logging
class PythonAgentExePlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.logger.debug("Initializing PythonAgentExePlugin")
        self.register_action('python_agent_exe', self.python_agent_exe)
        self.logger.debug("Registered action python_agent_exe")

    def python_agent_exe(self, *args, **kwargs):
        task = self.execute('container_get', 'task')
        model = self.execute('container_get', 'model')
        
        prompt = self.execute('render_template', 'render_template', 'python_dev_final.j2', task=task)
        print(prompt)
        
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        answer = response['message']['content']
        self.execute('container_set', key='answer', value=answer)
        self.execute('extract_markdown_python_code_blocks')
        result = self.execute('execute_code_snippets')
        
        print(f"Execution result: {result}")
        return result