# reflexion_recursive.py

import uuid
from core_system import CoreSystem
from database import init_db
from logger import LoggerFactory

# Initialize the database
init_db()

# Generate execution_id
execution_id = str(uuid.uuid4())

config = {
    'plugin_directory': ["data/actions"],
    'template_dir': "data/templates/",
    'string_dir': "data/strings/",
    'debug': True,
    'execution_id': execution_id  # Include execution_id in config
}

# Initialize the CoreSystem with the provided execution_id
core = CoreSystem(config)

# List all registered plugin actions
try:
    actions = core.execute_action('list_actions')
    print(f"Registered plugin actions: {actions}\n")
except Exception as e:
    print(f"Error listing actions: {e}")

# Set up the model and problem
core.set('model', 'llama3')
core.set('problem', 'Design a scalable web application architecture.')

# Set maximum limits for depth and breadth
core.set('max_depth', 3)    # Maximum depth allowed
core.set('max_breadth', 5)  # Maximum breadth allowed

print(f"Using Depth: {core.get('max_depth')}, Breadth: {core.get('max_breadth')}")

# Execute the recursive planning agent
try:
    concept_hierarchy = core.execute_action('recursive_planning_agent')
    # Retrieve the concept hierarchy from the DI layer
    concept_hierarchy = core.get('concept_hierarchy')
except Exception as e:
    print(f"Error executing recursive planning agent: {e}")

# Print the final concept hierarchy
import pprint
pp = pprint.PrettyPrinter(indent=2)
print('\nFinal Concept Hierarchy:')
pp.pprint(concept_hierarchy)

# Ensure LoggerListener stops gracefully
import atexit

def stop_logger_listener():
    if LoggerFactory.listener:
        LoggerFactory.listener.stop()

atexit.register(stop_logger_listener)
