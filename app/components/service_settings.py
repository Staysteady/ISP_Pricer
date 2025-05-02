import streamlit as st
import pandas as pd

def service_settings(service_loader):
    """
    Component for managing printing and embroidery services.
    
    Args:
        service_loader: Instance of ServiceLoader to manage services data
    """
    st.subheader("Printing & Embroidery Services")
    
    # Create tabs for different service types
    tab1, tab2 = st.tabs(["Printing Services", "Embroidery Services"])
    
    with tab1:
        manage_printing_services(service_loader)
    
    with tab2:
        manage_embroidery_services(service_loader)

def manage_printing_services(service_loader):
    """Manage printing services."""
    # Get current printing services
    printing_services = service_loader.get_printing_services()
    
    # Display current services in a table
    if printing_services:
        # Create a DataFrame for display
        display_data = []
        for service in printing_services:
            display_data.append({
                "id": service["id"],
                "Name": service["name"],
                "Price": f"£{service['price']:.2f}",
                "Cost": f"£{service['total_cost']:.2f}",
                "Profit": f"£{service['price'] - service['total_cost']:.2f}"
            })
        
        df = pd.DataFrame(display_data)
        
        # Display the services in a table
        st.dataframe(
            df,
            column_config={
                "id": None,  # Hide ID column
                "Name": st.column_config.TextColumn("Service Name"),
                "Price": st.column_config.TextColumn("Price"),
                "Cost": st.column_config.TextColumn("Cost"),
                "Profit": st.column_config.TextColumn("Profit")
            },
            hide_index=True
        )
        
        # Add a section for editing and deleting services
        st.subheader("Edit or Delete Services")
        
        # Service selection for edit/delete
        service_options = {service["name"]: service["id"] for service in printing_services}
        selected_service_name = st.selectbox(
            "Select Printing Service",
            options=list(service_options.keys()),
            key="printing_service_edit_select"
        )
        
        if selected_service_name:
            selected_service_id = service_options[selected_service_name]
            
            # Use buttons without columns
            edit_button = st.button("Edit Service", key=f"edit_printing_{selected_service_id}")
            if edit_button:
                edit_printing_service(service_loader, selected_service_id)
            
            delete_button = st.button("Delete Service", key=f"delete_printing_{selected_service_id}", type="primary")
            if delete_button:
                success, message = service_loader.delete_service(selected_service_id)
                if success:
                    st.success(f"Successfully deleted '{selected_service_name}'")
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info("No printing services defined yet.")
    
    # Add new service
    st.divider()
    st.subheader("Add New Printing Service")
    
    # Form for adding new service
    with st.form(key="add_printing_service_form"):
        service_name = st.text_input("Service Name", placeholder="e.g., PRINTING 1 SMALL LOGO")
        service_price = st.number_input("Price (£)", min_value=0.0, value=0.0, step=0.01)
        
        # Cost breakdown
        st.subheader("Cost Breakdown")
        
        # Use sequential inputs instead of columns
        st.text("Electric and Power Costs")
        electric_to_print = st.number_input("Electric to Print (£)", min_value=0.0, value=0.0, step=0.01)
        electric_to_bake = st.number_input("Electric to Bake (£)", min_value=0.0, value=0.0, step=0.01)
        electric_to_press = st.number_input("Electric to Press (£)", min_value=0.0, value=0.0, step=0.01)
        
        st.text("Material Costs")
        film_and_ink_costs = st.number_input("Film & Ink Costs (£)", min_value=0.0, value=0.0, step=0.01)
        sanding_costs = st.number_input("Sanding Costs (£)", min_value=0.0, value=0.0, step=0.01)
        
        # Calculate total cost
        total_cost = electric_to_print + electric_to_bake + electric_to_press + film_and_ink_costs + sanding_costs
        st.metric("Total Cost", f"£{total_cost:.2f}")
        
        # Submit button
        submit_button = st.form_submit_button("Add Printing Service")
        
        if submit_button:
            if service_name and service_price > 0:
                # Prepare service data
                service_data = {
                    "name": service_name,
                    "price": service_price,
                    "costs": {
                        "electric_to_print": electric_to_print,
                        "electric_to_bake": electric_to_bake,
                        "electric_to_press": electric_to_press,
                        "film_and_ink_costs": film_and_ink_costs,
                        "sanding_costs": sanding_costs
                    },
                    "total_cost": total_cost
                }
                
                # Add the service
                success, message, _ = service_loader.add_printing_service(service_data)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter a service name and a price greater than 0.")

def edit_printing_service(service_loader, service_id):
    """Edit a printing service."""
    service, _ = service_loader.get_service_by_id(service_id)
    
    if not service:
        st.error(f"Service with ID {service_id} not found.")
        return
    
    st.subheader(f"Edit Printing Service: {service['name']}")
    
    # Form for editing service
    with st.form(key=f"edit_printing_service_form_{service_id}"):
        service_name = st.text_input("Service Name", value=service["name"])
        service_price = st.number_input("Price (£)", min_value=0.0, value=service["price"], step=0.01)
        
        # Cost breakdown
        st.subheader("Cost Breakdown")
        
        # Get cost values
        costs = service.get("costs", {})
        
        # Use sequential inputs instead of columns
        st.text("Electric and Power Costs")
        electric_to_print = st.number_input(
            "Electric to Print (£)", 
            min_value=0.0, 
            value=costs.get("electric_to_print", 0.0), 
            step=0.01
        )
        electric_to_bake = st.number_input(
            "Electric to Bake (£)", 
            min_value=0.0, 
            value=costs.get("electric_to_bake", 0.0), 
            step=0.01
        )
        electric_to_press = st.number_input(
            "Electric to Press (£)", 
            min_value=0.0, 
            value=costs.get("electric_to_press", 0.0), 
            step=0.01
        )
        
        st.text("Material Costs")
        film_and_ink_costs = st.number_input(
            "Film & Ink Costs (£)", 
            min_value=0.0, 
            value=costs.get("film_and_ink_costs", 0.0), 
            step=0.01
        )
        sanding_costs = st.number_input(
            "Sanding Costs (£)", 
            min_value=0.0, 
            value=costs.get("sanding_costs", 0.0), 
            step=0.01
        )
        
        # Calculate total cost
        total_cost = electric_to_print + electric_to_bake + electric_to_press + film_and_ink_costs + sanding_costs
        st.metric("Total Cost", f"£{total_cost:.2f}")
        
        # Submit button
        submit_button = st.form_submit_button("Update Printing Service")
        
        if submit_button:
            if service_name and service_price > 0:
                # Prepare updated service data
                updated_service_data = {
                    "id": service_id,  # Maintain original ID
                    "name": service_name,
                    "price": service_price,
                    "costs": {
                        "electric_to_print": electric_to_print,
                        "electric_to_bake": electric_to_bake,
                        "electric_to_press": electric_to_press,
                        "film_and_ink_costs": film_and_ink_costs,
                        "sanding_costs": sanding_costs
                    },
                    "total_cost": total_cost
                }
                
                # Update the service
                success, message, _ = service_loader.update_service(service_id, updated_service_data)
                
                if success:
                    st.success(f"Successfully updated '{service_name}'")
                    # Force a rerun to reload the updated data
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter a service name and a price greater than 0.")

def manage_embroidery_services(service_loader):
    """Manage embroidery services."""
    # Get current embroidery services
    embroidery_services = service_loader.get_embroidery_services()
    
    # Display current services in a table
    if embroidery_services:
        # Create a DataFrame for display
        display_data = []
        for service in embroidery_services:
            display_data.append({
                "id": service["id"],
                "Name": service["name"],
                "Price": f"£{service['price']:.2f}",
                "Cost": f"£{service['total_cost']:.2f}",
                "Profit": f"£{service['price'] - service['total_cost']:.2f}"
            })
        
        df = pd.DataFrame(display_data)
        
        # Display the services in a table
        st.dataframe(
            df,
            column_config={
                "id": None,  # Hide ID column
                "Name": st.column_config.TextColumn("Service Name"),
                "Price": st.column_config.TextColumn("Price"),
                "Cost": st.column_config.TextColumn("Cost"),
                "Profit": st.column_config.TextColumn("Profit")
            },
            hide_index=True
        )
        
        # Add a section for editing and deleting services
        st.subheader("Edit or Delete Services")
        
        # Service selection for edit/delete
        service_options = {service["name"]: service["id"] for service in embroidery_services}
        selected_service_name = st.selectbox(
            "Select Embroidery Service",
            options=list(service_options.keys()),
            key="embroidery_service_edit_select"
        )
        
        if selected_service_name:
            selected_service_id = service_options[selected_service_name]
            
            # Use buttons without columns
            edit_button = st.button("Edit Service", key=f"edit_embroidery_{selected_service_id}")
            if edit_button:
                edit_embroidery_service(service_loader, selected_service_id)
            
            delete_button = st.button("Delete Service", key=f"delete_embroidery_{selected_service_id}", type="primary")
            if delete_button:
                success, message = service_loader.delete_service(selected_service_id)
                if success:
                    st.success(f"Successfully deleted '{selected_service_name}'")
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info("No embroidery services defined yet.")
    
    # Add new service
    st.divider()
    st.subheader("Add New Embroidery Service")
    
    # Form for adding new service
    with st.form(key="add_embroidery_service_form"):
        service_name = st.text_input("Service Name", placeholder="e.g., EMBROIDERY 1 SMALL LOGO")
        service_price = st.number_input("Price (£)", min_value=0.0, value=0.0, step=0.01)
        
        # Cost breakdown
        st.subheader("Cost Breakdown")
        
        # Use sequential inputs instead of columns
        st.text("Machine and Power Costs")
        electric = st.number_input("Electric (£)", min_value=0.0, value=0.0, step=0.01)
        threads = st.number_input("Threads (£)", min_value=0.0, value=0.0, step=0.01)
        bobbins = st.number_input("Bobbins (£)", min_value=0.0, value=0.0, step=0.01)
        
        st.text("Material Costs")
        front_film_costing = st.number_input("Front Film Costing (£)", min_value=0.0, value=0.0, step=0.01)
        backing = st.number_input("Backing (£)", min_value=0.0, value=0.0, step=0.01)
        
        # Calculate total cost
        total_cost = electric + threads + bobbins + front_film_costing + backing
        st.metric("Total Cost", f"£{total_cost:.2f}")
        
        # Submit button
        submit_button = st.form_submit_button("Add Embroidery Service")
        
        if submit_button:
            if service_name and service_price > 0:
                # Prepare service data
                service_data = {
                    "name": service_name,
                    "price": service_price,
                    "costs": {
                        "electric": electric,
                        "threads": threads,
                        "bobbins": bobbins,
                        "front_film_costing": front_film_costing,
                        "backing": backing
                    },
                    "total_cost": total_cost
                }
                
                # Add the service
                success, message, _ = service_loader.add_embroidery_service(service_data)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter a service name and a price greater than 0.")

def edit_embroidery_service(service_loader, service_id):
    """Edit an embroidery service."""
    service, _ = service_loader.get_service_by_id(service_id)
    
    if not service:
        st.error(f"Service with ID {service_id} not found.")
        return
    
    st.subheader(f"Edit Embroidery Service: {service['name']}")
    
    # Form for editing service
    with st.form(key=f"edit_embroidery_service_form_{service_id}"):
        service_name = st.text_input("Service Name", value=service["name"])
        service_price = st.number_input("Price (£)", min_value=0.0, value=service["price"], step=0.01)
        
        # Cost breakdown
        st.subheader("Cost Breakdown")
        
        # Get cost values
        costs = service.get("costs", {})
        
        # Use sequential inputs instead of columns
        st.text("Machine and Power Costs")
        electric = st.number_input(
            "Electric (£)", 
            min_value=0.0, 
            value=costs.get("electric", 0.0), 
            step=0.01
        )
        threads = st.number_input(
            "Threads (£)", 
            min_value=0.0, 
            value=costs.get("threads", 0.0), 
            step=0.01
        )
        bobbins = st.number_input(
            "Bobbins (£)", 
            min_value=0.0, 
            value=costs.get("bobbins", 0.0), 
            step=0.01
        )
        
        st.text("Material Costs")
        front_film_costing = st.number_input(
            "Front Film Costing (£)", 
            min_value=0.0, 
            value=costs.get("front_film_costing", 0.0), 
            step=0.01
        )
        backing = st.number_input(
            "Backing (£)", 
            min_value=0.0, 
            value=costs.get("backing", 0.0), 
            step=0.01
        )
        
        # Calculate total cost
        total_cost = electric + threads + bobbins + front_film_costing + backing
        st.metric("Total Cost", f"£{total_cost:.2f}")
        
        # Submit button
        submit_button = st.form_submit_button("Update Embroidery Service")
        
        if submit_button:
            if service_name and service_price > 0:
                # Prepare updated service data
                updated_service_data = {
                    "id": service_id,  # Maintain original ID
                    "name": service_name,
                    "price": service_price,
                    "costs": {
                        "electric": electric,
                        "threads": threads,
                        "bobbins": bobbins,
                        "front_film_costing": front_film_costing,
                        "backing": backing
                    },
                    "total_cost": total_cost
                }
                
                # Update the service
                success, message, _ = service_loader.update_service(service_id, updated_service_data)
                
                if success:
                    st.success(f"Successfully updated '{service_name}'")
                    # Force a rerun to reload the updated data
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter a service name and a price greater than 0.") 