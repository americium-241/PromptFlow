## Introduction

Welcome to the Prompt Framework! This framework provides a modular and reusable approach to building workflows. Its plugin-based architecture allows for easy extension and customization of functionalities. The framework focuses on essential features such as string management, recursive templates, and agnostic modular workflows. Being file-based, it allows for seamless versioning and easy integration with version control systems.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Extending the Framework](#extending-the-framework)
4. [Templates and Strings](#templates-and-strings)
5. [Available Plugins](#available-plugins)
6. [Usage Example](#usage-example)

## Installation

To install the Prompt Framework, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/prompt-framework.git
cd prompt-framework
pip install -r requirements.txt
```

## Configuration

Configure the framework using a dictionary that specifies various settings:

```python
config = {
    'plugin_directory': ["action_plugins", "base_plugin_lib"],
    'template_dir': "data/templates/",
    'string_dir': "data/strings/",
    'debug': True
}
```

## Extending the Framework

Extend the framework by creating new plugins:

```python
from plugin_base import PluginBase

class CustomPlugin(PluginBase):
    def __init__(self, di_container, debug=False):
        super().__init__(di_container, debug)
        self.register_action('custom_action', self.custom_action)

    def custom_action(self, *args, **kwargs):
        # Custom action logic
        pass
```

Register the new plugin in the configuration:

```python
config = {
    'plugin_directory': ["action_plugins", "base_plugin_lib", "custom_plugins"],
    'template_dir': "data/templates/",
    'string_dir': "data/strings/",
    'debug': True
}
```

## Templates and Strings

### Templates

The framework uses Jinja2 templates stored in the `data/templates/` directory:

- `python_dev_description.j2`:
  ```jinja
  {{ python_dev_intro }}
  {{ python_dev_intro_description }}
  ```

- `python_dev_markdown.j2`:
  ```jinja
  {{ function_format }}
  {{ example_format }}
  {{ additional_info }}
  ```

- `python_dev_final.j2`:
  ```jinja
  {% include 'python_dev_description.j2' %}
  task: {{ task }}
  {% include 'python_dev_markdown.j2' %}
  {{ your_code }}
  ```

### Strings

Strings are managed using JSON files in the `data/strings/` directory:

- `dev_strings.json`:
  ```json
  {
    "python_dev_intro": "context: You are an expert in Python development",
    "python_dev_intro_description": "description: you have to write a Python code snippet to resolve the given task",
    "function_format": "the code format should be in a markdown style",
    "example_format": "example_format: ```python\n# your code to complete the task\n```",
    "additional_info": "only the code you gave using this format will be read by the user",
    "your_code": "your_code:"
  }
  ```

## EXAMPLE Plugins

### PythonAgentExePlugin

This plugin uses the ollama library to chat with a language model and generate Python code based on a given task.

```python
# action_plugins/python_agent_exe.py
from plugin_base import PluginBase
import ollama
import logging

class PythonAgentExePlugin(PluginBase):
    def __init__(self, container, debug=False):
        super().__init__(container, debug)
        self.register_action('python_agent_exe', self.python_agent_exe)

    def python_agent_exe(self, *args, **kwargs):
        task = self.execute('container_get', 'task')
        model = self.execute('container_get', 'model')
        
        prompt = self.execute('render_template', 'render_template', 'python_dev_final.j2', task=task)
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
        
        return result
```

### ExtractMarkdownPythonCodeBlocksPlugin

This plugin extracts Python code blocks from a markdown-formatted string.

```python
# action_plugins/extract_markdown_python_code_blocks.py
from plugin_base import PluginBase
import re

class ExtractMarkdownPythonCodeBlocksPlugin(PluginBase):
    def __init__(self, di_container, debug=False):
        super().__init__(di_container, debug)
        self.register_action('extract_markdown_python_code_blocks', self.extract_markdown_python_code_blocks)

    def extract_markdown_python_code_blocks(self, *args, **kwargs):
        text = self.execute('container_get', 'answer')

        # Updated pattern to match both ``` and ''' delimiters, and to capture the content
        pattern = r"(?:```|''')python\s*(.*?)(?:```|''')"
        code_blocks = re.findall(pattern, text, re.DOTALL)

        # Wrap each code block in a tuple to match the expected format
        code_blocks = [(block,) for block in code_blocks]

        self.execute('container_set', key='snippets', value=code_blocks)
        return code_blocks
```

### ExecuteCodeSnippetsPlugin

This plugin executes Python code snippets, capturing the output and errors.

```python
# action_plugins/execute_code_snippets.py
from plugin_base import PluginBase
import io
from contextlib import redirect_stdout, redirect_stderr

class ExecuteCodeSnippetsPlugin(PluginBase):
    def __init__(self, di_container, debug=False):
        super().__init__(di_container, debug)
        self.register_action('execute_code_snippets', self.execute_code_snippets)

    def execute_code_snippets(self, *args, **kwargs):
        snippets = self.execute('container_get', 'snippets')

        results = []
        for snippet in snippets:
            local_env = {}
            global_env = {}
            try:
                output_capture = io.StringIO()
                error_capture = io.StringIO()
                with redirect_stdout(output_capture), redirect_stderr(error_capture):
                    exec(str(snippet[0]), global_env, local_env)
                output = output_capture.getvalue()
                error = error_capture.getvalue()
                result = {"output": output, "error": error, "env": local_env}
            except Exception as e:
                result = {"error": str(e), "env": local_env}
            
            results.append(result)

        return results
```

## Usage Example

Here's a step-by-step guide on how to use the framework:

1. Initialize Core System:

```python
from core_system import CoreSystem

config = {
    'plugin_directory': ["action_plugins", "base_plugin_lib"],
    'template_dir': "data/templates/",
    'string_dir': "data/strings/",
    'debug': True
}

core = CoreSystem(config)
```

2. Set Container Values:

```python
core.execute('container_set', key='model', value='llama3')
core.execute('container_set', key='task', value='list the current directory content')
```

3. Execute a Plugin Action:

```python
try:
    core.execute('python_agent_exe')
except Exception as e:
    print(f"Error executing python_agent_exe: {e}")
```


