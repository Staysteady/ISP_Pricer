import json
import os

class PricingEngine:
    def __init__(self, discount_file='app/data/discounts.json', markup_file='app/data/markup.json'):
        """Initialize the pricing engine with the discount settings file."""
        self.discount_file = discount_file
        self.markup_file = markup_file
        self.discounts = self._load_discounts()
        self.markup = self._load_markup()
        
    def _load_discounts(self):
        """Load discount settings from JSON file or create default."""
        if os.path.exists(self.discount_file):
            try:
                with open(self.discount_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading discounts: {str(e)}")
        
        # Default discount brackets
        default_discounts = {
            "brackets": [
                {"min": 1, "max": 9, "discount": 0},
                {"min": 10, "max": 24, "discount": 5},
                {"min": 25, "max": 49, "discount": 10},
                {"min": 50, "max": 99, "discount": 15},
                {"min": 100, "max": 249, "discount": 20},
                {"min": 250, "max": 10000, "discount": 25}
            ]
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.discount_file), exist_ok=True)
        
        # Save default discounts
        with open(self.discount_file, 'w') as f:
            json.dump(default_discounts, f, indent=4)
        
        return default_discounts
    
    def _load_markup(self):
        """Load markup setting from JSON file or create default."""
        if os.path.exists(self.markup_file):
            try:
                with open(self.markup_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading markup: {str(e)}")
        
        # Default markup setting
        default_markup = {
            "percentage": 0
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.markup_file), exist_ok=True)
        
        # Save default markup
        with open(self.markup_file, 'w') as f:
            json.dump(default_markup, f, indent=4)
        
        return default_markup
    
    def save_discounts(self, new_discounts):
        """Save updated discount settings."""
        try:
            with open(self.discount_file, 'w') as f:
                json.dump(new_discounts, f, indent=4)
            self.discounts = new_discounts
            return True, "Discounts saved successfully"
        except Exception as e:
            return False, f"Error saving discounts: {str(e)}"
    
    def save_markup(self, new_markup):
        """Save updated markup setting."""
        try:
            with open(self.markup_file, 'w') as f:
                json.dump(new_markup, f, indent=4)
            self.markup = new_markup
            return True, "Markup saved successfully"
        except Exception as e:
            return False, f"Error saving markup: {str(e)}"
    
    def get_discount_for_quantity(self, quantity):
        """Get the appropriate discount percentage based on quantity."""
        # Find applicable bracket
        for bracket in self.discounts.get("brackets", []):
            if bracket["min"] <= quantity <= bracket["max"]:
                return bracket["discount"]
        
        # Default to no discount if no bracket matches
        return 0
    
    def get_markup_percentage(self):
        """Get the current markup percentage."""
        return self.markup.get("percentage", 0)
    
    def calculate_price(self, base_price, quantity):
        """Calculate final price with applicable discount and markup."""
        # Apply markup to base price
        markup_percent = self.get_markup_percentage()
        markup_factor = 1 + (markup_percent / 100)
        marked_up_price = base_price * markup_factor
        
        # Apply quantity discount
        discount_percent = self.get_discount_for_quantity(quantity)
        discount_factor = 1 - (discount_percent / 100)
        total_price = marked_up_price * quantity * discount_factor
        
        return {
            "unit_price": round(marked_up_price, 2),
            "base_price": base_price,
            "markup_percent": markup_percent,
            "quantity": quantity,
            "discount_percent": discount_percent,
            "total_price": round(total_price, 2)
        }
    
    def calculate_order_total(self, line_items):
        """Calculate the total for an entire order with multiple line items."""
        total = sum(item["total_price"] for item in line_items)
        return round(total, 2) 