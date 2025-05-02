import json
import os
import sys
import sqlite3

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.utils.cost_tracker import CostTracker

def import_electricity_costs():
    """Import electricity costs from the JSON file."""
    print("Importing electricity costs...")
    
    # Load electricity costs from JSON
    with open('app/data/electricity_costs.json', 'r') as f:
        data = json.load(f)
    
    # Flatten the data for import
    electricity_costs = []
    for process_type in ['print_electricity', 'embroidery_electricity']:
        for item in data[process_type]:
            electricity_costs.append(item)
    
    # Create cost tracker and import data
    cost_tracker = CostTracker()
    if cost_tracker.import_electricity_costs_from_image(electricity_costs):
        print("Electricity costs imported successfully!")
    else:
        print("Error importing electricity costs")

def import_material_costs():
    """Import material costs from the JSON file."""
    print("Importing material costs...")
    
    # Load material costs from JSON
    with open('app/data/material_costs.json', 'r') as f:
        data = json.load(f)
    
    # Flatten the data for import
    material_costs = []
    for material_type in ['film_costs', 'ink_costs', 'powder_costs', 'backing_costs']:
        for item in data[material_type]:
            material_costs.append(item)
    
    # Create cost tracker and import data
    cost_tracker = CostTracker()
    if cost_tracker.import_material_costs_from_image(material_costs):
        print("Material costs imported successfully!")
    else:
        print("Error importing material costs")

def import_all_costs():
    """Import all default costs."""
    try:
        import_electricity_costs()
        import_material_costs()
        print("All default costs imported successfully!")
        return True
    except Exception as e:
        print(f"Error importing costs: {str(e)}")
        return False

if __name__ == "__main__":
    import_all_costs() 