import json
import os
import uuid
from datetime import datetime

class ServiceLoader:
    def __init__(self, services_file='app/data/printing_embroidery.json'):
        """Initialize the service loader with the services file."""
        self.services_file = services_file
        self.services = self._load_services()
        
    def _load_services(self):
        """Load services from JSON file or create default."""
        if os.path.exists(self.services_file):
            try:
                with open(self.services_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading services: {str(e)}")
                return self._create_default_services()
        else:
            return self._create_default_services()
    
    def _create_default_services(self):
        """Create default services structure if file doesn't exist."""
        default_services = {
            "printing_services": [],
            "embroidery_services": []
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.services_file), exist_ok=True)
        
        # Save default services
        with open(self.services_file, 'w') as f:
            json.dump(default_services, f, indent=4)
        
        return default_services
    
    def save_services(self):
        """Save the current services to the JSON file."""
        try:
            with open(self.services_file, 'w') as f:
                json.dump(self.services, f, indent=4)
            return True, "Services saved successfully"
        except Exception as e:
            return False, f"Error saving services: {str(e)}"
    
    def get_printing_services(self):
        """Get all printing services."""
        return self.services.get("printing_services", [])
    
    def get_embroidery_services(self):
        """Get all embroidery services."""
        return self.services.get("embroidery_services", [])
    
    def get_service_by_id(self, service_id):
        """Get a service by its ID."""
        # Check printing services
        for service in self.get_printing_services():
            if service["id"] == service_id:
                return service, "printing"
        
        # Check embroidery services
        for service in self.get_embroidery_services():
            if service["id"] == service_id:
                return service, "embroidery"
        
        return None, None
    
    def add_printing_service(self, service_data):
        """Add a new printing service."""
        if "id" not in service_data:
            service_data["id"] = f"print_{str(uuid.uuid4())[:8]}"
        
        self.services["printing_services"].append(service_data)
        success, message = self.save_services()
        return success, message, service_data["id"]
    
    def add_embroidery_service(self, service_data):
        """Add a new embroidery service."""
        if "id" not in service_data:
            service_data["id"] = f"emb_{str(uuid.uuid4())[:8]}"
        
        self.services["embroidery_services"].append(service_data)
        success, message = self.save_services()
        return success, message, service_data["id"]
    
    def update_service(self, service_id, updated_data):
        """Update an existing service by ID."""
        # Check and update printing services
        for i, service in enumerate(self.services["printing_services"]):
            if service["id"] == service_id:
                updated_data["id"] = service_id  # Ensure ID remains unchanged
                self.services["printing_services"][i] = updated_data
                success, message = self.save_services()
                return success, message, "printing"
        
        # Check and update embroidery services
        for i, service in enumerate(self.services["embroidery_services"]):
            if service["id"] == service_id:
                updated_data["id"] = service_id  # Ensure ID remains unchanged
                self.services["embroidery_services"][i] = updated_data
                success, message = self.save_services()
                return success, message, "embroidery"
        
        return False, f"Service with ID {service_id} not found", None
    
    def delete_service(self, service_id):
        """Delete a service by ID."""
        # Check and delete from printing services
        for i, service in enumerate(self.services["printing_services"]):
            if service["id"] == service_id:
                self.services["printing_services"].pop(i)
                success, message = self.save_services()
                return success, message
        
        # Check and delete from embroidery services
        for i, service in enumerate(self.services["embroidery_services"]):
            if service["id"] == service_id:
                self.services["embroidery_services"].pop(i)
                success, message = self.save_services()
                return success, message
        
        return False, f"Service with ID {service_id} not found"
    
    def calculate_service_price(self, service_id, quantity, pricing_engine):
        """Calculate final price for a service with quantity discount but no markup."""
        service, service_type = self.get_service_by_id(service_id)
        
        if not service:
            return None
        
        # Get base price from service
        base_price = service.get("price", 0)
        
        # Apply quantity discount but not markup
        discount_percent = pricing_engine.get_discount_for_quantity(quantity)
        discount_factor = 1 - (discount_percent / 100)
        total_price = base_price * quantity * discount_factor
        
        return {
            "service_id": service_id,
            "service_name": service.get("name", "Unknown Service"),
            "service_type": service_type,
            "unit_price": round(base_price, 2),
            "base_price": base_price,  # Same as unit price since no markup
            "markup_percent": 0,  # No markup for services
            "quantity": quantity,
            "discount_percent": discount_percent,
            "total_price": round(total_price, 2)
        } 