import json
import os
import math

class CostCalculator:
    def __init__(self, settings_file='app/data/machine_settings.json'):
        """Initialize the cost calculator with machine settings."""
        self.settings_file = settings_file
        self.settings = self._load_settings()
        
    def _load_settings(self):
        """Load settings from JSON file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {str(e)}")
                return self._create_default_settings()
        else:
            return self._create_default_settings()
    
    def _create_default_settings(self):
        """Create default settings if file doesn't exist."""
        default_settings = {
            "print_machines": [
                {
                    "name": "DTF Printer",
                    "wattage": 400,
                    "description": "Direct to film printer for transfers"
                },
                {
                    "name": "Heat Press",
                    "wattage": 1800,
                    "description": "Heat press for applying transfers"
                },
                {
                    "name": "Oven",
                    "wattage": 1800,
                    "description": "Oven for curing prints"
                }
            ],
            "embroidery_machines": [
                {
                    "name": "Melco EMT16",
                    "wattage": 500,
                    "description": "Standard embroidery machine"
                }
            ],
            "electricity_rate": {
                "cost_per_kwh": 0.4,
                "last_updated": "2023-11-01"
            },
            "process_times": {
                "print": {
                    "standard_print": 10,
                    "standard_bake": 5,
                    "standard_press": 10,
                    "small_logo_print": 5,
                    "small_logo_bake": 2.5,
                    "small_logo_press": 5
                },
                "embroidery": {
                    "small_logo": 10,
                    "large_logo": 40
                }
            },
            "usage_factors": {
                "print": {
                    "printer_usage_factor": 0.17,
                    "bake_usage_factor": 0.08,
                    "press_usage_factor": 0.17
                },
                "embroidery": {
                    "embroidery_usage_factor": 0.17,
                    "melco_emt16_usage_factor": 0.17
                }
            }
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        
        # Save default settings
        with open(self.settings_file, 'w') as f:
            json.dump(default_settings, f, indent=4)
        
        return default_settings
    
    def save_settings(self, new_settings):
        """Save updated settings."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(new_settings, f, indent=4)
            self.settings = new_settings
            return True, "Settings saved successfully"
        except Exception as e:
            return False, f"Error saving settings: {str(e)}"
    
    def update_electricity_rate(self, cost_per_kwh):
        """Update the electricity cost per kWh."""
        if "electricity_rate" not in self.settings:
            self.settings["electricity_rate"] = {}
        
        from datetime import datetime
        self.settings["electricity_rate"]["cost_per_kwh"] = cost_per_kwh
        self.settings["electricity_rate"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        return self.save_settings(self.settings)
    
    def update_machine_wattage(self, machine_type, machine_name, new_wattage):
        """Update the wattage for a specific machine."""
        machine_key = f"{machine_type}_machines"
        
        if machine_key not in self.settings:
            return False, f"Machine type '{machine_type}' not found"
        
        for machine in self.settings[machine_key]:
            if machine["name"] == machine_name:
                machine["wattage"] = new_wattage
                return self.save_settings(self.settings)
        
        return False, f"Machine '{machine_name}' not found"
    
    def update_process_time(self, process_type, process_name, new_time):
        """Update the processing time for a specific process."""
        if "process_times" not in self.settings:
            self.settings["process_times"] = {}
        
        if process_type not in self.settings["process_times"]:
            self.settings["process_times"][process_type] = {}
        
        self.settings["process_times"][process_type][process_name] = new_time
        return self.save_settings(self.settings)
    
    def update_usage_factor(self, process_type, factor_name, new_factor):
        """Update the usage factor for a specific process."""
        if "usage_factors" not in self.settings:
            self.settings["usage_factors"] = {}
        
        if process_type not in self.settings["usage_factors"]:
            self.settings["usage_factors"][process_type] = {}
        
        self.settings["usage_factors"][process_type][factor_name] = new_factor
        return self.save_settings(self.settings)
    
    def get_electricity_rate(self):
        """Get the current electricity rate."""
        if "electricity_rate" in self.settings:
            return self.settings["electricity_rate"].get("cost_per_kwh", 0.4)
        return 0.4
    
    def get_machine_wattage(self, machine_type, machine_name):
        """Get the wattage for a specific machine."""
        machine_key = f"{machine_type}_machines"
        
        if machine_key not in self.settings:
            return 0
        
        for machine in self.settings[machine_key]:
            if machine["name"] == machine_name:
                return machine["wattage"]
        
        return 0
    
    def get_process_time(self, process_type, process_name):
        """Get the processing time for a specific process."""
        if "process_times" not in self.settings:
            return 0
        
        if process_type not in self.settings["process_times"]:
            return 0
        
        return self.settings["process_times"][process_type].get(process_name, 0)
    
    def get_usage_factor(self, process_type, factor_name):
        """Get the usage factor for a specific process."""
        if "usage_factors" not in self.settings:
            return 0
        
        if process_type not in self.settings["usage_factors"]:
            return 0
        
        return self.settings["usage_factors"][process_type].get(factor_name, 0)
    
    def calculate_electricity_cost(self, machine_type, machine_name, process_type, process_name):
        """Calculate the electricity cost for a specific machine and process."""
        wattage = self.get_machine_wattage(machine_type, machine_name)
        process_time_minutes = self.get_process_time(process_type, process_name)
        
        # Convert minutes to hours
        hours = process_time_minutes / 60
        
        # Calculate energy in kilowatt-hours: (watts × hours) ÷ 1000
        energy_kwh = (wattage * hours) / 1000
        
        # Get electricity rate per kWh
        electricity_rate = self.get_electricity_rate()
        
        # Calculate cost
        cost = energy_kwh * electricity_rate
        
        return {
            "process_type": process_type,
            "process_name": process_name,
            "machine_name": machine_name,
            "wattage": wattage,
            "process_time_min": process_time_minutes,
            "energy_kwh": energy_kwh,
            "cost_per_kwh": electricity_rate,
            "cost_per_run": round(cost, 3)  # Rounded to 3 decimal places
        }
    
    def calculate_material_cost(self, material_type, material_name, logo_size):
        """
        Calculate the material cost for a specific material and logo size.
        This is a placeholder method - in a real implementation, you would
        retrieve material costs from your database.
        """
        # Placeholder material costs based on your image
        material_costs = {
            "Film": {
                "Small Logo": 0.158,
                "Large Logo": 0.395
            },
            "Ink": {
                "Small Logo": 0.18,
                "Large Logo": 0.24
            },
            "Powder": {
                "Small Logo": 0.09,
                "Large Logo": 0.18
            },
            "Backing": {
                "Small Logo": 0.04,
                "Large Logo": 0.92
            }
        }
        
        if material_type in material_costs and logo_size in material_costs[material_type]:
            return material_costs[material_type][logo_size]
        return 0
    
    def calculate_print_cost(self, print_type, quantity=1):
        """Calculate the total cost for a printing job."""
        total_cost = 0
        cost_breakdown = {
            "electricity_costs": [],
            "material_costs": {},
            "total_electricity_cost": 0,
            "total_material_cost": 0,
            "labor_cost": 0,
            "total_cost": 0
        }
        
        # Get available machine names
        print_machines = {machine["name"]: machine for machine in self.settings.get("print_machines", [])}
        
        # Determine logo size and process details based on print type
        if print_type == "print_1_small":
            logo_size = "Small Logo"
            processes = []
            
            # Only add processes for machines that exist in settings
            if "DTF Printer" in print_machines:
                processes.append(("print", "DTF Printer", "print", "standard_print"))
            if "Oven" in print_machines:
                processes.append(("print", "Oven", "print", "standard_bake"))
            if "Heat Press" in print_machines:
                processes.append(("print", "Heat Press", "print", "standard_press"))
            
            labor_cost_per_item = 1.50
        elif print_type == "print_2_small":
            logo_size = "Small Logo"
            processes = []
            
            # First logo - only add processes for machines that exist
            if "DTF Printer" in print_machines:
                processes.append(("print", "DTF Printer", "print", "standard_print"))
            if "Oven" in print_machines:
                processes.append(("print", "Oven", "print", "standard_bake"))
            if "Heat Press" in print_machines:
                processes.append(("print", "Heat Press", "print", "standard_press"))
                processes.append(("print", "Heat Press", "print", "standard_press")) # Second logo press
            
            # Second small logo
            if "DTF Printer" in print_machines:
                processes.append(("print", "DTF Printer", "print", "small_logo_print"))
            if "Oven" in print_machines:
                processes.append(("print", "Oven", "print", "small_logo_bake"))
            if "Heat Press" in print_machines:
                processes.append(("print", "Heat Press", "print", "small_logo_press"))
                processes.append(("print", "Heat Press", "print", "small_logo_press")) # Second small logo press
            
            labor_cost_per_item = 2.25
        elif print_type == "print_large_back_front":
            logo_size = "Large Logo"
            processes = []
            
            # Only add processes for machines that exist
            if "DTF Printer" in print_machines:
                processes.append(("print", "DTF Printer", "print", "standard_print"))
            if "Oven" in print_machines:
                processes.append(("print", "Oven", "print", "standard_bake"))
            if "Heat Press" in print_machines:
                processes.append(("print", "Heat Press", "print", "standard_press"))
            
            labor_cost_per_item = 1.75
        else:  # Default for other print types
            logo_size = "Small Logo"
            processes = []
            
            # Only add processes for machines that exist
            if "DTF Printer" in print_machines:
                processes.append(("print", "DTF Printer", "print", "standard_print"))
            if "Oven" in print_machines:
                processes.append(("print", "Oven", "print", "standard_bake"))
            if "Heat Press" in print_machines:
                processes.append(("print", "Heat Press", "print", "standard_press"))
            
            labor_cost_per_item = 1.50
        
        # Calculate electricity costs
        for machine_type, machine_name, process_type, process_name in processes:
            cost_data = self.calculate_electricity_cost(machine_type, machine_name, process_type, process_name)
            cost_breakdown["electricity_costs"].append(cost_data)
            total_cost += cost_data["cost_per_run"] * quantity
            cost_breakdown["total_electricity_cost"] += cost_data["cost_per_run"] * quantity
        
        # Calculate material costs
        materials = ["Film", "Ink", "Powder"]
        cost_breakdown["material_costs"] = {}
        
        for material in materials:
            material_cost = self.calculate_material_cost(material, "", logo_size) * quantity
            cost_breakdown["material_costs"][material] = {
                "cost_per_logo": self.calculate_material_cost(material, "", logo_size),
                "total_cost": material_cost
            }
            total_cost += material_cost
            cost_breakdown["total_material_cost"] += material_cost
        
        # Add labor cost
        labor_cost = labor_cost_per_item * quantity
        cost_breakdown["labor_cost"] = labor_cost
        total_cost += labor_cost
        
        # Set the total cost
        cost_breakdown["total_cost"] = round(total_cost, 2)
        
        return cost_breakdown
    
    def calculate_embroidery_cost(self, embroidery_type, quantity=1):
        """Calculate the total cost for an embroidery job."""
        total_cost = 0
        cost_breakdown = {
            "electricity_costs": [],
            "material_costs": {},
            "total_electricity_cost": 0,
            "total_material_cost": 0,
            "labor_cost": 0,
            "total_cost": 0
        }
        
        # Get available machine names
        embroidery_machines = {machine["name"]: machine for machine in self.settings.get("embroidery_machines", [])}
        
        # Determine logo size and process details based on embroidery type
        if embroidery_type == "emb_1_small":
            logo_size = "Small Logo"
            processes = []
            
            # Only add processes for machines that exist
            for machine_name in embroidery_machines.keys():
                processes.append(("embroidery", machine_name, "embroidery", "small_logo"))
            
            labor_cost_per_item = 2.00
            thread_cost = 1.25
        elif embroidery_type == "emb_1_large":
            logo_size = "Large Logo"
            processes = []
            
            # Only add processes for machines that exist
            for machine_name in embroidery_machines.keys():
                processes.append(("embroidery", machine_name, "embroidery", "large_logo"))
            
            labor_cost_per_item = 2.50
            thread_cost = 1.75
        elif embroidery_type == "emb_front_back":
            # Combined small and large logo
            logo_size = "Large Logo"  # For material calculations we'll use the larger one
            processes = []
            
            # Only add processes for machines that exist
            for machine_name in embroidery_machines.keys():
                processes.append(("embroidery", machine_name, "embroidery", "small_logo"))
                processes.append(("embroidery", machine_name, "embroidery", "large_logo"))
                
            labor_cost_per_item = 4.00
            thread_cost = 3.00
        else:  # Default
            logo_size = "Small Logo"
            processes = []
            
            # Only add processes for machines that exist
            for machine_name in embroidery_machines.keys():
                processes.append(("embroidery", machine_name, "embroidery", "small_logo"))
                
            labor_cost_per_item = 2.00
            thread_cost = 1.25
        
        # Calculate electricity costs
        for machine_type, machine_name, process_type, process_name in processes:
            cost_data = self.calculate_electricity_cost(machine_type, machine_name, process_type, process_name)
            cost_breakdown["electricity_costs"].append(cost_data)
            total_cost += cost_data["cost_per_run"] * quantity
            cost_breakdown["total_electricity_cost"] += cost_data["cost_per_run"] * quantity
        
        # Calculate material costs - for embroidery we need backing and thread
        cost_breakdown["material_costs"] = {}
        
        # Backing cost
        backing_cost = self.calculate_material_cost("Backing", "", logo_size) * quantity
        cost_breakdown["material_costs"]["Backing"] = {
            "cost_per_logo": self.calculate_material_cost("Backing", "", logo_size),
            "total_cost": backing_cost
        }
        total_cost += backing_cost
        cost_breakdown["total_material_cost"] += backing_cost
        
        # Thread cost (approximated)
        cost_breakdown["material_costs"]["Thread"] = {
            "cost_per_logo": thread_cost,
            "total_cost": thread_cost * quantity
        }
        total_cost += thread_cost * quantity
        cost_breakdown["total_material_cost"] += thread_cost * quantity
        
        # Add labor cost
        labor_cost = labor_cost_per_item * quantity
        cost_breakdown["labor_cost"] = labor_cost
        total_cost += labor_cost
        
        # Set the total cost
        cost_breakdown["total_cost"] = round(total_cost, 2)
        
        return cost_breakdown 