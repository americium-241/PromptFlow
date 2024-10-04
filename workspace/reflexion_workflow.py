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
# # Execute the reflection workflow
try:
    # First, get the conceptual areas
    core.execute('list_areas_agent')
    
    # Retrieve the conceptual areas
    conceptual_areas = core.execute('container_get', 'conceptual_areas')
    
    # Prepare items for rating
    core.execute('container_set', key='items_to_rate', value=conceptual_areas)
    core.execute('container_set', key='item_type', value='areas')
    
    # Rate the conceptual areas
    core.execute('rating_agent')
  
    # Reorder and filter based on ratings
    N = 6  # Number of top areas to keep
    # After rating the areas
    rated_areas = core.execute('container_get', 'rated_areas')
    print("\nRated Areas:")
    for item_dict in rated_areas:
        for item_key, item_value in item_dict.items():
            if isinstance(item_value, dict):
                text = item_value.get('text', '')
                try:
                    rating = int(item_value.get('rating', 0))
                except ValueError:
                    rating = 0
            else:
                text = item_value
                rating = 0
            print(f"Area: {text}, Rating: {rating}")
    
    # Adjusted code to handle possible string values
    flattened_rated_areas = []
    for item_dict in rated_areas:
        for item_key, item_value in item_dict.items():
            if isinstance(item_value, dict):
                text = item_value.get('text', '')
                try:
                    rating = int(item_value.get('rating', 0))
                except ValueError:
                    rating = 0
            else:
                text = item_value
                rating = 0
            flattened_rated_areas.append({'text': text, 'rating': rating})

    # Sort based on rating
    sorted_areas = sorted(flattened_rated_areas, key=lambda x: x['rating'], reverse=True)
    # Keep top N
    filtered_areas = sorted_areas[:N]
    print("\nTop Conceptual Areas Based on Ratings:")
    for area in filtered_areas:
        print(f"Area: {area['text']}, Rating: {area['rating']}")
    M=10
    # Now, process considerations for each area

    all_considerations = {}
    for area in filtered_areas:
        conceptual_area = area['text'].strip()
        print(f"\nProcessing considerations for area: {conceptual_area}")
        
        # Set the current conceptual area in the container
        core.execute('container_set', key='conceptual_area', value=conceptual_area)
        
        # Generate considerations for the area
        core.execute('list_considerations_agent')
        
        # Retrieve the considerations
        considerations = core.execute('container_get', 'considerations')  # Updated to 'considerations'
        
        # Check if considerations were retrieved
        if not considerations:
            print(f"No considerations found for area: {conceptual_area}")
            continue
        
        # Prepare items for rating
        # Flatten considerations if necessary
        flattened_considerations = []
        for item_dict in considerations:
            for item_key, item_value in item_dict.items():
                text = item_value.strip()
                flattened_considerations.append({'text': text})
        # Limit to M considerations before rating
        flattened_considerations = flattened_considerations[:M]
        core.execute('container_set', key='items_to_rate', value=flattened_considerations)
        core.execute('container_set', key='item_type', value='considerations')
        
        # Rate the considerations
        core.execute('rating_agent')
        
        # Get the rated considerations
        rated_considerations = core.execute('container_get', 'rated_considerations')
        
        # Process rated considerations
        flattened_rated_considerations = []
        for item_dict in rated_considerations:
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
                flattened_rated_considerations.append({'text': text, 'rating': rating})
        
        # Since we limited before rating, no need to filter again
        filtered_considerations = flattened_rated_considerations
        
        print(f"\nTop Considerations for '{conceptual_area}' Based on Ratings:")
        for cons in filtered_considerations:
            print(f"- {cons['text']} (Rating: {cons['rating']})")
        
        # Store the filtered considerations
        all_considerations[conceptual_area] = filtered_considerations

except Exception as e:
    print(f"Error executing reflection workflow: {e}")


print ('_______________________________________________________')
print(all_considerations)
