# workspace/reflexion_dynamic_recursive.py
from core_system import CoreSystem

config = {
    'plugin_directory': ["data/actions"],
    'template_dir': "data/templates/",
    'string_dir': "data/strings/",
    'debug': True
}

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
MAX_DEPTH_LIMIT = 3   # Maximum depth allowed
MAX_BREADTH_LIMIT = 3 # Maximum breadth allowed

# Assume default depth and breadth
depth = MAX_DEPTH_LIMIT
breadth = MAX_BREADTH_LIMIT
print(f"Using Depth: {depth}, Breadth: {breadth}")

def explore_concepts(concept, current_depth):
    if current_depth > depth:
        return None

    indent = '  ' * (current_depth - 1)
    print(f"\n{indent}Exploring at depth {current_depth}: {concept}")

    # Decide whether to explore this concept further
    core.set('concept', concept)
    should_explore = core.execute_action('should_explore_agent')

    if not should_explore:
        print(f"{indent}Decided not to explore '{concept}' further.")
        return None

    # Generate sub-concepts
    core.execute_action('list_subconcepts_agent')

    # Retrieve the sub-concepts
    subconcepts = core.get('subconcepts')

    # Check if subconcepts were retrieved
    if not subconcepts:
        print(f"{indent}No further concepts found for '{concept}'.")
        return None

    # Flatten the subconcepts and limit to breadth
    flattened_subconcepts = []
    for item_dict in subconcepts:
        for item_key, item_value in item_dict.items():
            flattened_subconcepts.append((item_key, item_value))

    # Limit to breadth
    flattened_subconcepts = flattened_subconcepts[:breadth]

    # Collect concepts and recurse
    concept_tree = {}
    for item_key, item_value in flattened_subconcepts:
        if isinstance(item_value, str):
            sub_text = item_value.strip()
            print(f"{indent}- {sub_text}")
            # Recurse into the sub-concept
            sub_tree = explore_concepts(sub_text, current_depth + 1)
            concept_tree[sub_text] = sub_tree
        elif isinstance(item_value, dict):
            sub_text = item_key.strip()
            print(f"{indent}- {sub_text}")
            # Recurse into the sub-concept with item_value
            sub_tree = explore_concepts(item_value, current_depth + 1)
            concept_tree[sub_text] = sub_tree
        else:
            # Handle other types if necessary
            pass

    return concept_tree

try:
    concept = core.get('problem')
    concept_hierarchy = explore_concepts(concept, current_depth=1)
except Exception as e:
    print(f"Error executing recursive exploration: {e}")

# Print the final concept hierarchy
import pprint
pp = pprint.PrettyPrinter(indent=2)
print('\nFinal Concept Hierarchy:')
pp.pprint(concept_hierarchy)
