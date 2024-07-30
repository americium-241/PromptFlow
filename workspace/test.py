# workspace/test.py
from core_system import CoreSystem

config = {
    'plugin_directory': ["action_plugins", "base_plugin_lib"],
    'template_dir': "data/templates/",
    'string_dir': "data/strings/",
    'debug': True
}

core = CoreSystem(config)

# List all registered actions
try:
    actions = core.execute('list_actions')
    print(f"Registered actions: {actions}")
except Exception as e:
    print(f"Error listing actions: {e}")

core.execute('container_set', key='model', value='llama3')
core.execute('container_set', key='task', value='list the current directory content')

try:
    core.execute('python_agent_exe')
except Exception as e:
    print(f"Error executing python_agent_exe: {e}")
