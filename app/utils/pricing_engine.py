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
    
    def get_supplier_product_group_quantity(self, supplier, product_group, line_items):
        """Calculate total quantity for a supplier and product group across all line items.
        
        Args:
            supplier (str): The supplier name
            product_group (str): The product group name
            line_items (list): List of line items from session state
            
        Returns:
            int: Total quantity for the given supplier and product group
        """
        total_quantity = 0
        for item in line_items:
            # Only consider items from the same supplier and product group
            if (item.get("supplier") == supplier and 
                item.get("product_group") == product_group):
                total_quantity += item.get("quantity", 0)
        
        return total_quantity
    
    def get_bulk_discount_for_item(self, supplier, product_group, line_items, item_quantity):
        """Get discount based on total quantity of the same supplier and product group.
        
        Args:
            supplier (str): The supplier name
            product_group (str): The product group name
            line_items (list): List of line items from session state
            item_quantity (int): Quantity of the current item
            
        Returns:
            float: Discount percentage to apply
        """
        # Get total quantity for this supplier and product group combination
        total_quantity = self.get_supplier_product_group_quantity(supplier, product_group, line_items)
        
        # Add current item quantity if it's a new item being added
        total_quantity += item_quantity
        
        # Get discount for the total quantity
        return self.get_discount_for_quantity(total_quantity)
    
    def get_markup_percentage(self):
        """Get the current markup percentage."""
        return self.markup.get("percentage", 0)
    
    def calculate_price(self, base_price, quantity, supplier=None, product_group=None, line_items=None):
        """Calculate final price with applicable discount and markup."""
        # Apply markup to base price
        markup_percent = self.get_markup_percentage()
        markup_factor = 1 + (markup_percent / 100)
        marked_up_price = base_price * markup_factor
        
        # Apply quantity discount, considering bulk purchases of same supplier/product group
        if supplier and product_group and line_items:
            # Use the bulk discount logic for matching supplier and product group
            discount_percent = self.get_bulk_discount_for_item(supplier, product_group, line_items, quantity)
        else:
            # Fallback to original per-item quantity discount
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
    
    def recalculate_discounts(self, line_items):
        """Recalculate discounts for all line items based on bulk quantities.
        
        Args:
            line_items (list): List of line items to recalculate
            
        Returns:
            list: Updated line items with recalculated discounts
        """
        # Create a copy of line items to avoid modifying the original
        updated_items = []
        
        # Group all items by supplier and product group
        for item in line_items:
            # Skip service-only items
            if item.get("is_service", False):
                updated_items.append(item)
                continue
                
            supplier = item.get("supplier")
            product_group = item.get("product_group")
            quantity = item.get("quantity", 0)
            base_price = item.get("base_price", 0)
            
            # Calculate the bulk discount for this item
            discount_percent = self.get_bulk_discount_for_item(supplier, product_group, line_items, 0)
            
            # Recalculate the total price with the new discount
            markup_percent = item.get("markup_percent", 0)
            marked_up_price = item.get("unit_price", 0)
            discount_factor = 1 - (discount_percent / 100)
            total_price = marked_up_price * quantity * discount_factor
            
            # Update the item with the new discount and total price
            updated_item = item.copy()
            updated_item["discount_percent"] = discount_percent
            updated_item["product_total_price"] = round(total_price, 2)
            
            # Recalculate the total price including any services
            updated_total = total_price
            if updated_item.get("has_printing", False):
                updated_total += updated_item.get("printing_total_price", 0)
            if updated_item.get("has_embroidery", False):
                updated_total += updated_item.get("embroidery_total_price", 0)
                
            updated_item["total_price"] = round(updated_total, 2)
            updated_items.append(updated_item)
            
        return updated_items 