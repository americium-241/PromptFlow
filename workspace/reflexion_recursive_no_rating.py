# workspace/test.py
from core_system import CoreSystem

config = {
    'plugin_directory': ["data/actions", "base_plugin_lib"],
    'template_dir': "data/templates/",
    'string_dir': "data/strings/",
    'debug': True
}

core = CoreSystem(config)

# List all registered actions
try:
    actions = core.execute('list_actions')
    print(f"Registered actions: {actions}\n")
except Exception as e:
    print(f"Error listing actions: {e}")

# Set up the model and problem
core.execute('container_set', key='model', value='llama3')
core.execute('container_set', key='problem', value='Design a scalable web application architecture.')

# Set maximum limits for depth and breadth
MAX_DEPTH_LIMIT = 3   # Maximum depth allowed
MAX_BREADTH_LIMIT = 3 # Maximum breadth allowed

# Step 1: Estimate Complexity
try:
    # Use the complexity estimator plugin
    core.execute('complexity_estimator_agent')

    # Retrieve the complexity estimate
    complexity_estimate = core.execute('container_get', 'complexity_estimate')
    print("\nComplexity Estimate:")
    print(complexity_estimate)

    # Extract depth and breadth values
    depth = None
    breadth = None
    for item_dict in complexity_estimate:
        for key, value in item_dict.items():
            if key == 'depth':
                try:
                    depth = int(value)
                except ValueError:
                    depth = None
            elif key == 'breadth':
                try:
                    breadth = int(value)
                except ValueError:
                    breadth = None

    if depth is None or breadth is None:
        print("Failed to retrieve valid depth and breadth values.")
        # Set default values or handle the error
        depth = 1
        breadth = 1

    print(f"Estimated Depth: {depth}, Estimated Breadth: {breadth}")

except Exception as e:
    print(f"Error estimating complexity: {e}")
    # Set default values in case of error
    depth = 1
    breadth = 1

# Apply maximum limits
MAX_DEPTH = min(depth, MAX_DEPTH_LIMIT)
MAX_BREADTH = min(breadth, MAX_BREADTH_LIMIT)
print(f"Using Depth: {MAX_DEPTH}, Breadth: {MAX_BREADTH}")

# Recursive exploration function
def explore_concepts(concept, current_depth):
    if current_depth > MAX_DEPTH:
        return None

    indent = '  ' * (current_depth - 1)
    print(f"\n{indent}Exploring at depth {current_depth}: {concept}")

    # Set the current concept in the container
    core.execute('container_set', key='concept', value=concept)

    # Generate sub-concepts
    core.execute('list_subconcepts_agent')

    # Retrieve the sub-concepts
    subconcepts = core.execute('container_get', 'subconcepts')

    # Check if subconcepts were retrieved
    if not subconcepts:
        print(f"{indent}  No further concepts found.")
        return None

    # Flatten the subconcepts and limit to MAX_BREADTH
    flattened_subconcepts = []
    for item_dict in subconcepts:
        for item_key, item_value in item_dict.items():
            flattened_subconcepts.append((item_key, item_value))

    # Limit to MAX_BREADTH
    flattened_subconcepts = flattened_subconcepts[:MAX_BREADTH]

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

# Start the exploration from the main problem
try:
    concept = core.execute('container_get', 'problem')
    print('___________________________________________')
    print(concept)
    concept_hierarchy = explore_concepts(concept, current_depth=1)
except Exception as e:
    print(f"Error executing recursive exploration: {e}")

# Print the final concept hierarchy
import pprint
pp = pprint.PrettyPrinter(indent=2)
print('\nFinal Concept Hierarchy:')
pp.pprint(concept_hierarchy)
