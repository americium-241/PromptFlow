from plugin_base import PluginBase
import re

class ExtractMarkdownPythonCodeBlocksPlugin(PluginBase):
    def __init__(self, di_container, debug=False):
        super().__init__(di_container, debug)
        self.register_action('extract_markdown_python_code_blocks', self.extract_markdown_python_code_blocks)

    def extract_markdown_python_code_blocks(self, *args, **kwargs):
        if self.debug:
            print("ExtractMarkdownPythonCodeBlocksPlugin: Executing extract_markdown_python_code_blocks")

        text = self.execute('container_get', 'answer')
        
        if self.debug:
            print(f"ExtractMarkdownPythonCodeBlocksPlugin: Retrieved answer text: {text[:100]}...")  # Print first 100 chars

        # Updated pattern to match both ``` and ''' delimiters, and to capture the content
        pattern = r"(?:```|''')python\s*(.*?)(?:```|''')"
        code_blocks = re.findall(pattern, text, re.DOTALL)
        
        if self.debug:
            print(f"ExtractMarkdownPythonCodeBlocksPlugin: Found {len(code_blocks)} code blocks")
            for i, block in enumerate(code_blocks):
                print(f"Code block {i+1}:\n{block}")

        # Wrap each code block in a tuple to match the expected format
        code_blocks = [(block,) for block in code_blocks]

        self.execute('container_set', key='snippets', value=code_blocks)
        return code_blocks