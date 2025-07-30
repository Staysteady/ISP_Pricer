import os
import json
import pandas as pd
from datetime import datetime

class CostTracker:
    def __init__(self, costs_file='app/data/business_costs.json'):
        """Initialize the cost tracker with JSON files."""
        self.costs_file = costs_file
        self.services_file = 'app/data/printing_embroidery.json'
        self.electricity_file = 'app/data/electricity_costs.json'
        self.material_file = 'app/data/material_costs.json'
        self.business_costs = self._load_business_costs()
        self.electricity_costs = self._load_electricity_costs()
        self.material_costs = self._load_material_costs()
        
    def _load_electricity_costs(self):
        """Load electricity costs from JSON file or create default."""
        if os.path.exists(self.electricity_file):
            try:
                with open(self.electricity_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading electricity costs: {str(e)}")
                return self._create_default_electricity_costs()
        else:
            return self._create_default_electricity_costs()
    
    def _load_material_costs(self):
        """Load material costs from JSON file or create default."""
        if os.path.exists(self.material_file):
            try:
                with open(self.material_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading material costs: {str(e)}")
                return self._create_default_material_costs()
        else:
            return self._create_default_material_costs()
    
    def _create_default_electricity_costs(self):
        """Create default electricity costs if file doesn't exist."""
        default_costs = {
            "print_electricity": [],
            "embroidery_electricity": []
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.electricity_file), exist_ok=True)
        
        # Save default costs
        with open(self.electricity_file, 'w') as f:
            json.dump(default_costs, f, indent=4)
        
        return default_costs
    
    def _create_default_material_costs(self):
        """Create default material costs if file doesn't exist."""
        default_costs = {
            "film_costs": [],
            "ink_costs": [],
            "powder_costs": [],
            "backing_costs": []
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.material_file), exist_ok=True)
        
        # Save default costs
        with open(self.material_file, 'w') as f:
            json.dump(default_costs, f, indent=4)
        
        return default_costs
    
    def save_electricity_costs(self, electricity_data):
        """Save electricity costs to JSON file."""
        try:
            with open(self.electricity_file, 'w') as f:
                json.dump(electricity_data, f, indent=4)
            self.electricity_costs = electricity_data
            return True, "Electricity costs saved successfully"
        except Exception as e:
            return False, f"Error saving electricity costs: {str(e)}"
    
    def save_material_costs(self, material_data):
        """Save material costs to JSON file."""
        try:
            with open(self.material_file, 'w') as f:
                json.dump(material_data, f, indent=4)
            self.material_costs = material_data
            return True, "Material costs saved successfully"
        except Exception as e:
            return False, f"Error saving material costs: {str(e)}"
    
    def save_business_costs(self, business_data):
        """Save business costs to JSON file."""
        try:
            with open(self.costs_file, 'w') as f:
                json.dump(business_data, f, indent=4)
            self.business_costs = business_data
            return True, "Business costs saved successfully"
        except Exception as e:
            return False, f"Error saving business costs: {str(e)}"
    
    
    
    def import_electricity_costs_from_image(self, electricity_data):
        """Import electricity costs from the image data provided."""
        try:
            # Load existing data
            current_data = self._load_electricity_costs()
            
            # Add new electricity data
            for item in electricity_data:
                if item["process_type"] == "print":
                    current_data["print_electricity"].append(item)
                elif item["process_type"] == "embroidery":
                    current_data["embroidery_electricity"].append(item)
            
            # Save updated data
            with open(self.electricity_file, 'w') as f:
                json.dump(current_data, f, indent=4)
            
            # Update instance data
            self.electricity_costs = current_data
            return True
        except Exception as e:
            print(f"Error importing electricity costs: {str(e)}")
            return False
    
    def import_material_costs_from_image(self, material_data):
        """Import material costs from the image data provided."""
        try:
            # Load existing data
            current_data = self._load_material_costs()
            
            # Add new material data to appropriate categories
            for item in material_data:
                material_type = item["material_type"].lower()
                if material_type == "film":
                    current_data["film_costs"].append(item)
                elif material_type == "ink":
                    current_data["ink_costs"].append(item)
                elif material_type == "powder":
                    current_data["powder_costs"].append(item)
                elif material_type == "backing":
                    current_data["backing_costs"].append(item)
            
            # Save updated data
            with open(self.material_file, 'w') as f:
                json.dump(current_data, f, indent=4)
            
            # Update instance data
            self.material_costs = current_data
            return True
        except Exception as e:
            print(f"Error importing material costs: {str(e)}")
            return False
    
    def get_all_cost_categories(self):
        """Get all cost categories from business costs JSON."""
        try:
            data = self._load_business_costs()
            categories = data.get("categories", [])
            if categories:
                df = pd.DataFrame(categories)
                return df.sort_values('name') if 'name' in df.columns else df
            else:
                return pd.DataFrame(columns=['id', 'name', 'description'])
        except Exception as e:
            print(f"Error getting cost categories: {str(e)}")
            return pd.DataFrame()
    
    def get_costs_by_category(self, category_id=None):
        """Get costs filtered by category from business costs JSON."""
        try:
            data = self._load_business_costs()
            costs = data.get("costs", [])
            categories = data.get("categories", [])
            
            # Create category lookup
            category_lookup = {cat['id']: cat['name'] for cat in categories}
            
            if category_id:
                # Filter by specific category
                filtered_costs = [cost for cost in costs if cost.get('category_id') == category_id]
            else:
                # Return all costs with category names
                filtered_costs = costs.copy()
                for cost in filtered_costs:
                    cost['category_name'] = category_lookup.get(cost.get('category_id'), 'Unknown')
            
            if filtered_costs:
                df = pd.DataFrame(filtered_costs)
                return df.sort_values('name') if 'name' in df.columns else df
            else:
                columns = ['category_id', 'name', 'description', 'cost_value', 'cost_type', 'date_incurred', 'recurring_period']
                if not category_id:
                    columns.append('category_name')
                return pd.DataFrame(columns=columns)
        except Exception as e:
            print(f"Error getting costs by category: {str(e)}")
            return pd.DataFrame()
    
    def add_cost_category(self, name, description=""):
        """Add a new cost category to business costs JSON."""
        try:
            data = self._load_business_costs()
            categories = data.get("categories", [])
            
            # Check if category already exists
            if any(cat['name'].lower() == name.lower() for cat in categories):
                return False, "Category already exists"
            
            # Find next available ID
            max_id = max([cat.get('id', 0) for cat in categories], default=0)
            new_id = max_id + 1
            
            # Add new category
            new_category = {
                "id": new_id,
                "name": name,
                "description": description
            }
            categories.append(new_category)
            
            # Save updated data
            data["categories"] = categories
            with open(self.costs_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            # Update instance data
            self.business_costs = data
            return True, "Category added successfully"
        except Exception as e:
            return False, f"Error adding category: {str(e)}"
    
    def add_business_cost(self, cost_data):
        """Add a new business cost to business costs JSON."""
        try:
            data = self._load_business_costs()
            costs = data.get("costs", [])
            
            # Add timestamp if not provided
            if 'date_incurred' not in cost_data:
                cost_data['date_incurred'] = datetime.now().strftime("%Y-%m-%d")
            
            # Add new cost
            costs.append(cost_data)
            
            # Save updated data
            data["costs"] = costs
            with open(self.costs_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            # Update instance data
            self.business_costs = data
            return True, "Cost added successfully"
        except Exception as e:
            return False, f"Error adding cost: {str(e)}"
    
    def update_business_cost(self, cost_index, cost_data):
        """Update an existing business cost in business costs JSON."""
        try:
            data = self._load_business_costs()
            costs = data.get("costs", [])
            
            if 0 <= cost_index < len(costs):
                # Update the cost at the specified index
                costs[cost_index] = cost_data
                
                # Save updated data
                data["costs"] = costs
                with open(self.costs_file, 'w') as f:
                    json.dump(data, f, indent=4)
                
                # Update instance data
                self.business_costs = data
                return True, "Cost updated successfully"
            else:
                return False, "Cost index out of range"
        except Exception as e:
            return False, f"Error updating cost: {str(e)}"
    
    def delete_business_cost(self, cost_index):
        """Delete a business cost from business costs JSON."""
        try:
            data = self._load_business_costs()
            costs = data.get("costs", [])
            
            if 0 <= cost_index < len(costs):
                # Remove the cost at the specified index
                removed_cost = costs.pop(cost_index)
                
                # Save updated data
                data["costs"] = costs
                with open(self.costs_file, 'w') as f:
                    json.dump(data, f, indent=4)
                
                # Update instance data
                self.business_costs = data
                return True, "Cost deleted successfully"
            else:
                return False, "Cost index out of range"
        except Exception as e:
            return False, f"Error deleting cost: {str(e)}"
    
    def get_all_electricity_costs(self):
        """Get all electricity costs as a DataFrame."""
        try:
            data = self._load_electricity_costs()
            
            # Combine all electricity costs into a single list
            all_costs = []
            for process_list in data.values():
                if isinstance(process_list, list):
                    all_costs.extend(process_list)
            
            # Convert to DataFrame
            if all_costs:
                df = pd.DataFrame(all_costs)
                # Sort by process_type and process_name if columns exist
                if 'process_type' in df.columns and 'process_name' in df.columns:
                    df = df.sort_values(['process_type', 'process_name'])
                return df
            else:
                # Return empty DataFrame with expected columns
                return pd.DataFrame(columns=['process_type', 'process_name', 'avg_time_min', 'cost_per_unit_kwh', 'machine_watts', 'usage_w', 'cost_per_run'])
        except Exception as e:
            print(f"Error getting electricity costs: {str(e)}")
            return pd.DataFrame()
    
    def get_all_material_costs(self):
        """Get all material costs as a DataFrame."""
        try:
            data = self._load_material_costs()
            
            # Combine all material costs into a single list
            all_costs = []
            for material_list in data.values():
                if isinstance(material_list, list):
                    all_costs.extend(material_list)
            
            # Convert to DataFrame
            if all_costs:
                df = pd.DataFrame(all_costs)
                # Sort by material_type and material_name if columns exist
                if 'material_type' in df.columns and 'material_name' in df.columns:
                    df = df.sort_values(['material_type', 'material_name'])
                return df
            else:
                # Return empty DataFrame with expected columns
                return pd.DataFrame(columns=['material_type', 'material_name', 'cost_per_unit', 'unit_measurement', 'unit_value', 'logo_size', 'cost_per_logo'])
        except Exception as e:
            print(f"Error getting material costs: {str(e)}")
            return pd.DataFrame()
    
    def get_profit_analysis(self, quote_data):
        """Calculate profit based on quote data and costs using JSON data."""
        # This method can be implemented later if needed
        # It would use the existing calculate_quote_costs_and_profit method
        return self.calculate_quote_costs_and_profit(quote_data) 
    
    def _get_service_cost_from_file(self, service_id):
        """Get the cost of a service from the services file."""
        if not os.path.exists(self.services_file):
            return None
        
        try:
            with open(self.services_file, 'r') as f:
                services_data = json.load(f)
                
            # Check printing services
            for service in services_data.get("printing_services", []):
                if service.get("id") == service_id:
                    return service.get("total_cost", 0)
                
            # Check embroidery services
            for service in services_data.get("embroidery_services", []):
                if service.get("id") == service_id:
                    return service.get("total_cost", 0)
                
        except Exception as e:
            print(f"Error reading services file: {str(e)}")
        
        return None
    
    def calculate_line_item_costs(self, line_item):
        """Calculate simple profit margin: supplier cost vs client revenue."""
        
        # Get basic data
        base_price = line_item.get("base_price", 0)
        quantity = line_item.get("quantity", 0)
        total_revenue = line_item.get("total_price", 0)
        
        # Calculate supplier costs only
        supplier_product_cost = base_price * quantity
        
        # Add service costs (these are also supplier costs)
        printing_service_cost = 0
        embroidery_service_cost = 0
        
        # Get printing service costs if present
        if line_item.get("has_printing", False):
            printing_service_id = line_item.get("printing_service_id")
            if printing_service_id:
                service_cost = self._get_service_cost_from_file(printing_service_id)
                if service_cost is not None:
                    printing_service_cost = service_cost * quantity
        
        # Get embroidery service costs if present
        if line_item.get("has_embroidery", False):
            embroidery_service_id = line_item.get("embroidery_service_id")
            if embroidery_service_id:
                service_cost = self._get_service_cost_from_file(embroidery_service_id)
                if service_cost is not None:
                    embroidery_service_cost = service_cost * quantity
        
        # Legacy service handling for backwards compatibility
        if not line_item.get("has_printing", False) and not line_item.get("has_embroidery", False):
            services = line_item.get("services", [])
            for service in services:
                service_id = service.get("id", "")
                if service_id.startswith("print_"):
                    service_cost = self._get_service_cost_from_file(service_id)
                    if service_cost is not None:
                        printing_service_cost += service_cost * quantity
                elif service_id.startswith("emb_"):
                    service_cost = self._get_service_cost_from_file(service_id)
                    if service_cost is not None:
                        embroidery_service_cost += service_cost * quantity
        
        # Total supplier cost
        total_supplier_cost = supplier_product_cost + printing_service_cost + embroidery_service_cost
        
        # Calculate profit and margin
        profit = total_revenue - total_supplier_cost
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Return simplified cost structure
        return {
            "product_cost": round(supplier_product_cost, 2),
            "printing_costs": round(printing_service_cost, 2),
            "embroidery_costs": round(embroidery_service_cost, 2),
            "material_costs": 0,
            "electricity_costs": 0,
            "labor_costs": 0,
            "waste_costs": 0,
            "depreciation_costs": 0,
            "total_cost": round(total_supplier_cost, 2),
            "revenue": total_revenue,
            "profit": round(profit, 2),
            "profit_margin": round(profit_margin, 2)
        }
    
    def _calculate_printing_costs(self, service_id, quantity):
        """Calculate printing costs including electricity, materials, etc. using JSON data."""
        total_cost = 0
        
        try:
            # Get electricity costs from JSON
            electricity_data = self._load_electricity_costs()
            print_electricity = electricity_data.get("print_electricity", [])
            
            # Map service_id to relevant process names
            process_mapping = {
                "print_1_small": ["Print", "Bake", "Press 1 Logo"],
                "print_2_small": ["Print", "Bake", "Press 1 Logo", "Press 2 Logo", 
                                  "Print (2nd small logo)", "Bake (2nd small logo)", 
                                  "Press 1 Logo (2nd small logo)", "Press 2 Logo (2nd small logo)"],
                "print_half_back_front": ["Print", "Bake", "Press 1 Logo"],
                "print_large_back_front": ["Print", "Bake", "Press 1 Logo"]
            }
            
            # Get electricity costs for the relevant processes
            processes = process_mapping.get(service_id, [])
            
            for process in processes:
                matching_process = next((item for item in print_electricity 
                                       if item.get('process_name') == process), None)
                if matching_process:
                    cost_per_run = matching_process.get('cost_per_run', 0)
                    total_cost += cost_per_run * quantity
            
            # Get material costs from JSON
            material_data = self._load_material_costs()
            logo_size = "Small Logo" if "small" in service_id else "Large Logo"
            
            # Get film costs
            film_costs = material_data.get("film_costs", [])
            matching_film = next((item for item in film_costs 
                                if item.get('logo_size') == logo_size), None)
            if matching_film:
                total_cost += matching_film.get('cost_per_logo', 0) * quantity
            
            # Get ink costs
            ink_costs = material_data.get("ink_costs", [])
            matching_ink = next((item for item in ink_costs 
                               if item.get('logo_size') == logo_size), None)
            if matching_ink:
                total_cost += matching_ink.get('cost_per_logo', 0) * quantity
            
            # Get powder costs
            powder_costs = material_data.get("powder_costs", [])
            matching_powder = next((item for item in powder_costs 
                                  if item.get('logo_size') == logo_size), None)
            if matching_powder:
                total_cost += matching_powder.get('cost_per_logo', 0) * quantity
                
        except Exception as e:
            print(f"Error calculating printing costs: {str(e)}")
        
        # Add estimated labor costs (can be adjusted based on actual data)
        labor_cost_per_item = 1.50  # Example value
        total_cost += labor_cost_per_item * quantity
        
        return round(total_cost, 2)
    
    def _calculate_embroidery_costs(self, service_id, quantity):
        """Calculate embroidery costs including electricity, materials, etc. using JSON data."""
        total_cost = 0
        
        try:
            # Get electricity costs from JSON
            electricity_data = self._load_electricity_costs()
            embroidery_electricity = electricity_data.get("embroidery_electricity", [])
            
            # Map service_id to relevant process names
            process_mapping = {
                "emb_1_small": ["Embroidery Small Logo"],
                "emb_1_large": ["Embroidery Large Logo"],
                "emb_front_back": ["Embroidery Small Logo", "Embroidery Large Logo"]
            }
            
            # Get electricity costs for the relevant processes
            processes = process_mapping.get(service_id, [])
            
            for process in processes:
                matching_process = next((item for item in embroidery_electricity 
                                       if item.get('process_name') == process), None)
                if matching_process:
                    cost_per_run = matching_process.get('cost_per_run', 0)
                    total_cost += cost_per_run * quantity
            
            # Get material costs from JSON
            material_data = self._load_material_costs()
            backing_costs = material_data.get("backing_costs", [])
            
            # For embroidery, we need backing and thread costs
            if service_id == "emb_1_small":
                logo_size = "Small Logo"
            elif service_id == "emb_1_large":
                logo_size = "Large Logo"
            else:  # front and back - both sizes
                # Small backing costs
                small_backing = next((item for item in backing_costs 
                                    if item.get('logo_size') == 'Small Logo'), None)
                if small_backing:
                    total_cost += small_backing.get('cost_per_logo', 0) * quantity
                
                # Large backing costs
                large_backing = next((item for item in backing_costs 
                                    if item.get('logo_size') == 'Large Logo'), None)
                if large_backing:
                    total_cost += large_backing.get('cost_per_logo', 0) * quantity
                    
                # Add thread costs (approximate)
                total_cost += 3.00 * quantity  # Combined thread costs
                
                # Add estimated labor costs
                labor_cost_per_item = 2.00  # Higher for embroidery
                total_cost += labor_cost_per_item * quantity
                
                return round(total_cost, 2)
            
            # Get backing costs for single logo size
            matching_backing = next((item for item in backing_costs 
                                   if item.get('logo_size') == logo_size), None)
            if matching_backing:
                total_cost += matching_backing.get('cost_per_logo', 0) * quantity
            
            # Add thread costs (approximate based on size)
            thread_cost = 1.25 if logo_size == "Small Logo" else 1.75
            total_cost += thread_cost * quantity
                
        except Exception as e:
            print(f"Error calculating embroidery costs: {str(e)}")
        
        # Add estimated labor costs (can be adjusted based on actual data)
        labor_cost_per_item = 2.00  # Example value, higher for embroidery
        total_cost += labor_cost_per_item * quantity
        
        return round(total_cost, 2)
    
    def calculate_quote_costs_and_profit(self, quote_data):
        """Calculate costs and profit for an entire quote."""
        line_items = quote_data.get('line_items', [])
        
        if not line_items:
            return {
                "total_revenue": 0,
                "total_cost": 0,
                "total_profit": 0,
                "profit_margin": 0,
                "line_items": []
            }
        
        total_revenue = 0
        total_cost = 0
        line_item_results = []
        
        # Calculate costs for each line item
        for item in line_items:
            item_costs = self.calculate_line_item_costs(item)
            
            # Add line item details to results
            line_item_data = {
                "id": item.get("id", ""),
                "style_no": item.get("style_no", ""),
                "product_name": item.get("product_name", ""),
                "quantity": item.get("quantity", 0),
                "services": [service.get("name", "") for service in item.get("services", [])],
                "revenue": item_costs["revenue"],
                "costs": item_costs,
                "profit": item_costs["profit"],
                "profit_margin": item_costs["profit_margin"]
            }
            
            line_item_results.append(line_item_data)
            
            # Add to totals
            total_revenue += item_costs["revenue"]
            total_cost += item_costs["total_cost"]
        
        # Calculate overall profit and margin
        total_profit = round(total_revenue - total_cost, 2)
        profit_margin = round((total_profit / total_revenue) * 100, 2) if total_revenue > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "profit_margin": profit_margin,
            "line_items": line_item_results
        }
    
    def delete_electricity_cost(self, process_name, process_type):
        """Delete an electricity cost entry by process name and type."""
        try:
            data = self._load_electricity_costs()
            
            # Find and remove the cost entry
            target_key = f"{process_type}_electricity"
            if target_key in data:
                original_length = len(data[target_key])
                data[target_key] = [item for item in data[target_key] 
                                   if not (item.get('process_name') == process_name and 
                                          item.get('process_type') == process_type)]
                
                # Check if anything was removed
                if len(data[target_key]) < original_length:
                    # Save updated data
                    with open(self.electricity_file, 'w') as f:
                        json.dump(data, f, indent=4)
                    
                    # Update instance data
                    self.electricity_costs = data
                    return True
                else:
                    print(f"Electricity cost with process name '{process_name}' and type '{process_type}' not found")
                    return False
            else:
                print(f"No electricity costs found for process type '{process_type}'")
                return False
        except Exception as e:
            print(f"Error deleting electricity cost: {str(e)}")
            return False
    
    def delete_material_cost(self, material_name, material_type):
        """Delete a material cost entry by material name and type."""
        try:
            data = self._load_material_costs()
            
            # Find and remove the cost entry
            target_key = f"{material_type.lower()}_costs"
            if target_key in data:
                original_length = len(data[target_key])
                data[target_key] = [item for item in data[target_key] 
                                   if not (item.get('material_name') == material_name and 
                                          item.get('material_type') == material_type)]
                
                # Check if anything was removed
                if len(data[target_key]) < original_length:
                    # Save updated data
                    with open(self.material_file, 'w') as f:
                        json.dump(data, f, indent=4)
                    
                    # Update instance data
                    self.material_costs = data
                    return True
                else:
                    print(f"Material cost with name '{material_name}' and type '{material_type}' not found")
                    return False
            else:
                print(f"No material costs found for material type '{material_type}'")
                return False
        except Exception as e:
            print(f"Error deleting material cost: {str(e)}")
            return False
    
    def _load_business_costs(self):
        """Load business costs from JSON file or create default."""
        if os.path.exists(self.costs_file):
            try:
                with open(self.costs_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading business costs: {str(e)}")
                return self._create_default_business_costs()
        else:
            return self._create_default_business_costs()

    def _create_default_business_costs(self):
        """Create default business costs if file doesn't exist."""
        default_costs = {
            "categories": [
                {"id": 1, "name": "Equipment", "description": "Costs related to equipment purchase and maintenance"},
                {"id": 2, "name": "Utilities", "description": "Utility costs including electricity, water, etc."},
                {"id": 3, "name": "Materials", "description": "Materials used in production process"},
                {"id": 4, "name": "Labor", "description": "Labor costs"},
                {"id": 5, "name": "Rent", "description": "Rent and property-related costs"},
                {"id": 6, "name": "Software", "description": "Software and digital services"},
                {"id": 7, "name": "Other", "description": "Miscellaneous business costs"}
            ],
            "costs": [
                {"category_id": 2, "name": "Electricity", "description": "Monthly electricity bill", "cost_value": 0.4, "cost_type": "per_unit", "date_incurred": datetime.now().strftime("%Y-%m-%d"), "recurring_period": "monthly"},
                {"category_id": 5, "name": "Workshop Rent", "description": "Monthly workshop rent", "cost_value": 1000, "cost_type": "fixed", "date_incurred": datetime.now().strftime("%Y-%m-%d"), "recurring_period": "monthly"}
            ],
            "electricity_rates": {
                "cost_per_kwh": 0.34
            },
            "labor_rates": {
                "printing": 10.50,
                "embroidery": 12.00
            }
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.costs_file), exist_ok=True)
        
        # Save default costs
        with open(self.costs_file, 'w') as f:
            json.dump(default_costs, f, indent=4)
        
        return default_costs
    
    def _calculate_labor_costs(self, line_item):
        """Calculate labor costs per line item - much more realistic rates."""
        quantity = line_item.get("quantity", 0)
        
        # Basic handling cost per item (very reasonable)
        base_labor_cost = 0.10  # £0.10 per item for basic handling
        
        # Setup costs for services (fixed cost divided across quantity)
        service_labor_per_item = 0
        if line_item.get("has_printing", False):
            # £20 setup cost divided across quantity, min £0.20 per item
            printing_setup = max(20.0 / quantity if quantity > 0 else 20.0, 0.20)
            service_labor_per_item += printing_setup
            
        if line_item.get("has_embroidery", False):
            # £15 setup cost divided across quantity, min £0.15 per item  
            embroidery_setup = max(15.0 / quantity if quantity > 0 else 15.0, 0.15)
            service_labor_per_item += embroidery_setup
        
        total_labor_per_item = base_labor_cost + service_labor_per_item
        total_labor = total_labor_per_item * quantity
        
        print(f"DEBUG: Labor costs - £{base_labor_cost:.2f} base + £{service_labor_per_item:.2f} services = £{total_labor_per_item:.2f} per item")
        
        return round(total_labor, 2)
    
    def _calculate_waste_costs(self, material_total):
        """Calculate waste costs based on material totals."""
        try:
            # Load machine settings to get waste factors
            machine_settings_file = 'app/data/machine_settings.json'
            if not os.path.exists(machine_settings_file):
                return material_total * 0.05  # Default 5% waste
            
            with open(machine_settings_file, 'r') as f:
                settings = json.load(f)
            
            waste_factors = settings.get('waste_factors', {})
            waste_percentage = waste_factors.get('material_waste_percentage', 5.0) / 100
            
            return round(material_total * waste_percentage, 2)
            
        except Exception as e:
            print(f"Error calculating waste costs: {str(e)}")
            return material_total * 0.05  # Default 5% waste
    
    def _calculate_depreciation_costs(self, line_item):
        """Calculate equipment depreciation costs per line item - simplified."""
        quantity = line_item.get("quantity", 0)
        
        # Simple per-item depreciation cost
        depreciation_per_item = 0.05  # £0.05 per item basic depreciation
        
        # Additional depreciation for services
        if line_item.get("has_printing", False):
            depreciation_per_item += 0.10  # £0.10 extra for DTF printer usage
            
        if line_item.get("has_embroidery", False):
            depreciation_per_item += 0.15  # £0.15 extra for embroidery machine usage
        
        total_depreciation = depreciation_per_item * quantity
        
        print(f"DEBUG: Depreciation - £{depreciation_per_item:.2f} per item × {quantity} = £{total_depreciation:.2f}")
        
        return round(total_depreciation, 2) 