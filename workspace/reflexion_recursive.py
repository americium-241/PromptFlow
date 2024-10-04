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
        depth = 3
        breadth = 5

    print(f"Using Depth: {depth}, Breadth: {breadth}")

except Exception as e:
    print(f"Error estimating complexity: {e}")
    # Set default values in case of error
    depth = 3
    breadth = 5

# Now proceed with the recursive exploration using the estimated depth and breadth
MAX_DEPTH = depth   # Use the estimated depth
MAX_BREADTH = breadth # Use the estimated breadth

# Recursive exploration function
def explore_concepts(concept, current_depth):
    if current_depth > MAX_DEPTH:
        return None

    print(f"\n{'  ' * current_depth}Exploring at depth {current_depth}: {concept}")

    # Set the current concept in the container
    core.execute('container_set', key='concept', value=concept)

    # Generate sub-concepts
    core.execute('list_subconcepts_agent')

    # Retrieve the sub-concepts
    subconcepts = core.execute('container_get', 'subconcepts')

    # Check if subconcepts were retrieved
    if not subconcepts:
        print(f"{'  ' * current_depth}No further concepts found.")
        return None

    # Prepare items for rating
    core.execute('container_set', key='items_to_rate', value=subconcepts)
    core.execute('container_set', key='item_type', value='concepts')

    # Rate the subconcepts
    core.execute('rating_agent')

    # Get the rated subconcepts
    rated_subconcepts = core.execute('container_get', 'rated_concepts')

    # Process rated subconcepts
    flattened_rated_subconcepts = []
    for item_dict in rated_subconcepts:
        for item_key, item_value in item_dict.items():
            if isinstance(item_value, dict):
                text = item_value.get('text', '').strip()
                try:
                    rating = int(item_value.get('rating', 0))
                except ValueError:
                    rating = 0
            else:
                text = item_value.strip()
                rating = 0
            flattened_rated_subconcepts.append({'text': text, 'rating': rating})

    # Sort based on rating
    sorted_subconcepts = sorted(flattened_rated_subconcepts, key=lambda x: x['rating'], reverse=True)
    # Keep top MAX_BREADTH
    filtered_subconcepts = sorted_subconcepts[:MAX_BREADTH]

    # Collect concepts and recurse
    concept_tree = {}
    for sub in filtered_subconcepts:
        sub_text = sub['text']
        sub_rating = sub['rating']
        print(f"{'  ' * current_depth}- {sub_text} (Rating: {sub_rating})")
        # Recurse into the sub-concept
        sub_tree = explore_concepts(sub_text, current_depth + 1)
        concept_tree[sub_text] = {
            'rating': sub_rating,
            'subconcepts': sub_tree
        }

    return concept_tree

# Start the exploration from the main problem
try:
    concept =core.execute('container_get', 'problem')
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
