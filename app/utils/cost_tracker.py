import os
import json
import sqlite3
import pandas as pd
from datetime import datetime

class CostTracker:
    def __init__(self, db_path='app/data/pricer.db', costs_file='app/data/business_costs.json'):
        """Initialize the cost tracker with the database and costs file."""
        self.db_path = db_path
        self.costs_file = costs_file
        self.services_file = 'app/data/printing_embroidery.json'
        self._initialize_db()
        self._load_default_costs()
        self.business_costs = self._load_business_costs()
        
    def _initialize_db(self):
        """Initialize the cost tracking tables in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create cost categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cost_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create costs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            cost_value REAL NOT NULL,
            cost_type TEXT DEFAULT 'fixed',  -- fixed, variable, per_unit, etc.
            date_incurred DATE,
            recurring_period TEXT,  -- monthly, quarterly, annually, one-time
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES cost_categories(id)
        )
        ''')
        
        # Create electricity usage table based on image data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS electricity_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_type TEXT NOT NULL,  -- print, embroidery
            process_name TEXT NOT NULL,  -- e.g., "Print 1 Logo", "Embroidery Small Logo"
            avg_time_min REAL,
            cost_per_unit_kwh REAL,
            machine_watts REAL,
            usage_w REAL,
            cost_per_run REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create materials cost table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS material_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_type TEXT NOT NULL,  -- film, ink, powder, backing, etc.
            material_name TEXT NOT NULL,
            cost_per_unit REAL,
            unit_measurement TEXT,  -- length, weight, piece, etc.
            unit_value REAL,  -- length in m, weight in g, etc.
            logo_size TEXT,  -- small, large
            cost_per_logo REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_default_costs(self):
        """Load default costs from JSON file or create default if not exists."""
        if os.path.exists(self.costs_file):
            return
        
        # Default business costs
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
                {"category_id": 2, "name": "Electricity", "description": "Monthly electricity bill", "cost_value": 0.4, "cost_type": "per_unit", "recurring_period": "monthly"},
                {"category_id": 5, "name": "Workshop Rent", "description": "Monthly workshop rent", "cost_value": 1000, "cost_type": "fixed", "recurring_period": "monthly"}
            ]
        }
        
        # Create the default costs file
        os.makedirs(os.path.dirname(self.costs_file), exist_ok=True)
        with open(self.costs_file, 'w') as f:
            json.dump(default_costs, f, indent=4)
        
        # Import the default costs to the database
        self._import_default_costs(default_costs)
    
    def _import_default_costs(self, default_costs):
        """Import default costs to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add default categories
        for category in default_costs["categories"]:
            cursor.execute('''
            INSERT OR IGNORE INTO cost_categories (id, name, description)
            VALUES (?, ?, ?)
            ''', (category["id"], category["name"], category["description"]))
        
        # Add default costs
        today = datetime.now().strftime("%Y-%m-%d")
        for cost in default_costs["costs"]:
            cursor.execute('''
            INSERT OR IGNORE INTO business_costs 
            (category_id, name, description, cost_value, cost_type, date_incurred, recurring_period)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                cost["category_id"], 
                cost["name"], 
                cost["description"], 
                cost["cost_value"],
                cost["cost_type"],
                today,
                cost["recurring_period"]
            ))
        
        conn.commit()
        conn.close()
    
    def import_electricity_costs_from_image(self, electricity_data):
        """Import electricity costs from the image data provided."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in electricity_data:
            cursor.execute('''
            INSERT INTO electricity_costs 
            (process_type, process_name, avg_time_min, cost_per_unit_kwh, machine_watts, usage_w, cost_per_run)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item["process_type"],
                item["process_name"],
                item["avg_time_min"],
                item["cost_per_unit_kwh"],
                item["machine_watts"],
                item["usage_w"],
                item["cost_per_run"]
            ))
        
        conn.commit()
        conn.close()
        return True
    
    def import_material_costs_from_image(self, material_data):
        """Import material costs from the image data provided."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in material_data:
            cursor.execute('''
            INSERT INTO material_costs 
            (material_type, material_name, cost_per_unit, unit_measurement, unit_value, logo_size, cost_per_logo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item["material_type"],
                item["material_name"],
                item["cost_per_unit"],
                item["unit_measurement"],
                item["unit_value"],
                item["logo_size"],
                item["cost_per_logo"]
            ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_all_cost_categories(self):
        """Get all cost categories."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM cost_categories ORDER BY name", conn)
        conn.close()
        return df
    
    def get_costs_by_category(self, category_id=None):
        """Get costs filtered by category."""
        conn = sqlite3.connect(self.db_path)
        
        if category_id:
            query = "SELECT * FROM business_costs WHERE category_id = ? ORDER BY name"
            df = pd.read_sql_query(query, conn, params=(category_id,))
        else:
            query = """
            SELECT bc.*, cc.name as category_name 
            FROM business_costs bc
            JOIN cost_categories cc ON bc.category_id = cc.id
            ORDER BY cc.name, bc.name
            """
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def add_cost_category(self, name, description=""):
        """Add a new cost category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO cost_categories (name, description)
            VALUES (?, ?)
            ''', (name, description))
            conn.commit()
            success = True
            message = "Category added successfully"
        except sqlite3.IntegrityError:
            success = False
            message = "Category already exists"
        except Exception as e:
            success = False
            message = f"Error adding category: {str(e)}"
        
        conn.close()
        return success, message
    
    def add_business_cost(self, data):
        """Add a new business cost."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO business_costs 
            (category_id, name, description, cost_value, cost_type, date_incurred, recurring_period)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data["category_id"], 
                data["name"], 
                data["description"], 
                data["cost_value"],
                data["cost_type"],
                data["date_incurred"],
                data["recurring_period"]
            ))
            conn.commit()
            success = True
            message = "Cost added successfully"
        except Exception as e:
            success = False
            message = f"Error adding cost: {str(e)}"
        
        conn.close()
        return success, message
    
    def update_business_cost(self, cost_id, data):
        """Update an existing business cost."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE business_costs 
            SET category_id = ?, name = ?, description = ?, cost_value = ?,
                cost_type = ?, date_incurred = ?, recurring_period = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (
                data["category_id"], 
                data["name"], 
                data["description"], 
                data["cost_value"],
                data["cost_type"],
                data["date_incurred"],
                data["recurring_period"],
                cost_id
            ))
            conn.commit()
            success = True
            message = "Cost updated successfully"
        except Exception as e:
            success = False
            message = f"Error updating cost: {str(e)}"
        
        conn.close()
        return success, message
    
    def delete_business_cost(self, cost_id):
        """Delete a business cost."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM business_costs WHERE id = ?", (cost_id,))
            conn.commit()
            success = True
            message = "Cost deleted successfully"
        except Exception as e:
            success = False
            message = f"Error deleting cost: {str(e)}"
        
        conn.close()
        return success, message
    
    def get_all_electricity_costs(self):
        """Get all electricity costs."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM electricity_costs ORDER BY process_type, process_name", conn)
        conn.close()
        return df
    
    def get_all_material_costs(self):
        """Get all material costs."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM material_costs ORDER BY material_type, material_name", conn)
        conn.close()
        return df
    
    def get_profit_analysis(self, quote_data):
        """Calculate profit based on quote data and costs."""
        # TODO: Implement profit analysis logic
        # Will need to calculate actual costs of items in quotes based on costs in the database
        # and return the difference between quote price and actual costs
        pass 
    
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
        """Calculate printing costs including electricity, materials, etc."""
        total_cost = 0
        
        # Get electricity costs from database
        conn = sqlite3.connect(self.db_path)
        
        # Map service_id to relevant process names
        # Update process names to match what's used in the electricity_costs table
        # These should be consistent with the process names in manual entry
        process_mapping = {
            "print_1_small": ["DTF Printer", "Oven", "Heat Press"],
            "print_2_small": ["DTF Printer", "Oven", "Heat Press", "Heat Press (2nd logo)", 
                              "DTF Printer (2nd small logo)", "Oven (2nd small logo)", 
                              "Heat Press (2nd small logo)", "Heat Press (2nd small logo, 2nd pass)"],
            "print_half_back_front": ["DTF Printer", "Oven", "Heat Press"],
            "print_large_back_front": ["DTF Printer", "Oven", "Heat Press"]
        }
        
        # Get electricity costs for the relevant processes
        processes = process_mapping.get(service_id, [])
        
        for process in processes:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cost_per_run FROM electricity_costs 
                WHERE process_type = 'print' AND process_name = ?
            """, (process,))
            result = cursor.fetchone()
            
            if result:
                cost_per_run = result[0]
                total_cost += cost_per_run * quantity
        
        # Get material costs
        logo_size = "Small Logo" if "small" in service_id else "Large Logo"
        
        # Get film costs
        cursor.execute("""
            SELECT cost_per_logo FROM material_costs 
            WHERE material_type = 'Film' AND logo_size = ?
        """, (logo_size,))
        result = cursor.fetchone()
        if result:
            total_cost += result[0] * quantity
        
        # Get ink costs
        cursor.execute("""
            SELECT cost_per_logo FROM material_costs 
            WHERE material_type = 'Ink' AND logo_size = ?
        """, (logo_size,))
        result = cursor.fetchone()
        if result:
            total_cost += result[0] * quantity
        
        # Get powder costs
        cursor.execute("""
            SELECT cost_per_logo FROM material_costs 
            WHERE material_type = 'Powder' AND logo_size = ?
        """, (logo_size,))
        result = cursor.fetchone()
        if result:
            total_cost += result[0] * quantity
        
        conn.close()
        
        # Add estimated labor costs (can be adjusted based on actual data)
        labor_cost_per_item = 1.50  # Example value
        total_cost += labor_cost_per_item * quantity
        
        return round(total_cost, 2)
    
    def _calculate_embroidery_costs(self, service_id, quantity):
        """Calculate embroidery costs including electricity, materials, etc."""
        total_cost = 0
        
        # Get electricity costs from database
        conn = sqlite3.connect(self.db_path)
        
        # Map service_id to relevant process names
        # Update process names to match what's used in the electricity_costs table
        process_mapping = {
            "emb_1_small": ["Melco EMT16 Small Logo"],
            "emb_1_large": ["Melco EMT16 Large Logo"],
            "emb_front_back": ["Melco EMT16 Small Logo", "Melco EMT16 Large Logo"]
        }
        
        # Get electricity costs for the relevant processes
        processes = process_mapping.get(service_id, [])
        
        for process in processes:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cost_per_run FROM electricity_costs 
                WHERE process_type = 'embroidery' AND process_name = ?
            """, (process,))
            result = cursor.fetchone()
            
            if result:
                cost_per_run = result[0]
                total_cost += cost_per_run * quantity
        
        # Get material costs
        # For embroidery, we need backing and thread costs
        if service_id == "emb_1_small":
            logo_size = "Small Logo"
        elif service_id == "emb_1_large":
            logo_size = "Large Logo"
        else:  # front and back - both sizes
            # This is approximated by using both sizes
            cursor = conn.cursor()
            
            # Small backing costs
            cursor.execute("""
                SELECT cost_per_logo FROM material_costs 
                WHERE material_type = 'Backing' AND logo_size = 'Small Logo' LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                total_cost += result[0] * quantity
            
            # Large backing costs
            cursor.execute("""
                SELECT cost_per_logo FROM material_costs 
                WHERE material_type = 'Backing' AND logo_size = 'Large Logo' LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                total_cost += result[0] * quantity
                
            # Add thread costs (approximate)
            total_cost += 3.00 * quantity  # Combined thread costs from image
            
            conn.close()
            return round(total_cost, 2)
        
        # Get backing costs
        cursor.execute("""
            SELECT cost_per_logo FROM material_costs 
            WHERE material_type = 'Backing' AND logo_size = ? LIMIT 1
        """, (logo_size,))
        result = cursor.fetchone()
        if result:
            total_cost += result[0] * quantity
        
        # Add thread costs (approximate based on image)
        thread_cost = 1.25 if logo_size == "Small Logo" else 1.75  # From image
        total_cost += thread_cost * quantity
        
        conn.close()
        
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
    
    def delete_electricity_cost(self, cost_id):
        """Delete an electricity cost entry by ID."""
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if the cost exists
            cursor.execute("SELECT id FROM electricity_costs WHERE id = ?", (cost_id,))
            if not cursor.fetchone():
                print(f"Electricity cost with ID {cost_id} not found")
                conn.close()
                return False
            
            # Delete the cost
            cursor.execute("DELETE FROM electricity_costs WHERE id = ?", (cost_id,))
            
            # Commit the changes and close the connection
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error deleting electricity cost: {str(e)}")
            return False
    
    def delete_material_cost(self, cost_id):
        """Delete a material cost entry by ID."""
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if the cost exists
            cursor.execute("SELECT id FROM material_costs WHERE id = ?", (cost_id,))
            if not cursor.fetchone():
                print(f"Material cost with ID {cost_id} not found")
                conn.close()
                return False
            
            # Delete the cost
            cursor.execute("DELETE FROM material_costs WHERE id = ?", (cost_id,))
            
            # Commit the changes and close the connection
            conn.commit()
            conn.close()
            
            return True
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