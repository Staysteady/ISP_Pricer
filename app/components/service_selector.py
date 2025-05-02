import streamlit as st
from app.utils.session_state import add_line_item, delete_line_item

def service_selector(service_loader, pricing_engine):
    """
    Component for selecting printing and embroidery services.
    
    Args:
        service_loader: Instance of ServiceLoader to fetch services data
        pricing_engine: Instance of PricingEngine to calculate prices with discounts
    
    Returns:
        dict: Selected service data if a service is selected and quantity entered
    """
    st.subheader("Printing & Embroidery Services")
    
    # Create tabs for different service types
    tab1, tab2 = st.tabs(["Printing Services", "Embroidery Services"])
    
    with tab1:
        selected_service = select_printing_service(service_loader, pricing_engine)
        if selected_service:
            return selected_service
    
    with tab2:
        selected_service = select_embroidery_service(service_loader, pricing_engine)
        if selected_service:
            return selected_service
    
    return None

def select_printing_service(service_loader, pricing_engine):
    """Select a printing service and add it to the quote."""
    # Get all printing services
    printing_services = service_loader.get_printing_services()
    
    if not printing_services:
        st.info("No printing services defined yet. Add some in the settings.")
        return None
    
    # Create a mapping of service names to IDs for the dropdown
    service_options = {service["name"]: service["id"] for service in printing_services}
    
    # Add a blank option
    service_options = {"": ""} | service_options
    
    # Service selection dropdown
    selected_service_name = st.selectbox(
        "Select Printing Service", 
        options=list(service_options.keys()),
        key="printing_service_select"
    )
    
    # If a service is selected, show details and quantity input
    if selected_service_name:
        selected_service_id = service_options[selected_service_name]
        service, _ = service_loader.get_service_by_id(selected_service_id)
        
        if service:
            # Display service details
            st.markdown(f"**Service:** {service['name']}")
            st.markdown(f"**Price:** £{service['price']:.2f}")
            
            # Quantity input
            quantity_key = f"printing_quantity_{service['id']}"
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=quantity_key)
            
            # Calculate price with discounts but no markup
            price_data = service_loader.calculate_service_price(service['id'], quantity, pricing_engine)
            
            # Display calculated price
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Unit Price", f"£{price_data['unit_price']:.2f}")
            
            with col2:
                st.metric("Discount", f"{price_data['discount_percent']}%")
            
            with col3:
                st.metric("Total Price", f"£{price_data['total_price']:.2f}")
            
            # Add buttons in a row - one to add and one to remove
            col1, col2 = st.columns(2)
            
            with col1:
                # Add to quote button
                if st.button("Add to Quote", key=f"add_printing_{service['id']}"):
                    # Prepare line item data
                    item_data = {
                        "supplier": "InkStitchPress",  # Your company as the supplier
                        "product_group": "Printing",    # Category
                        "style_no": service['id'],      # Use service ID as style number
                        "colours": "N/A",               # Not applicable for services
                        "sizes": "N/A",                 # Not applicable for services
                        "base_price": service['price'],  # Original price
                        "unit_price": price_data['unit_price'],  # Price with no markup
                        "quantity": quantity,
                        "discount_percent": price_data['discount_percent'],
                        "total_price": price_data['total_price'],
                        "markup_percent": 0,  # No markup for printing services
                        "is_service": True,   # Flag to indicate this is a service
                        "service_type": "printing",
                        "service_name": service['name']
                    }
                    
                    # Add the item to the session state
                    add_line_item(item_data)
                    
                    # Success message
                    st.success(f"Added {service['name']} to quote!", icon="✅")
                    # Use JavaScript to auto-clear the success message after 2 seconds
                    st.markdown("""
                        <script>
                            setTimeout(function() {
                                document.querySelector('.stSuccess').style.display = 'none';
                            }, 2000);
                        </script>
                        """, unsafe_allow_html=True)
                    
                    return item_data
            
            with col2:
                # Check if this service exists in the line items
                service_exists = False
                service_item_id = None
                
                if 'line_items' in st.session_state:
                    for item in st.session_state.line_items:
                        if (item.get('is_service', False) and 
                            item.get('service_type') == 'printing' and 
                            item.get('style_no') == service['id']):
                            service_exists = True
                            service_item_id = item.get('id')
                            break
                
                # Show remove button if the service exists
                if service_exists and service_item_id:
                    if st.button("Remove from Quote", key=f"remove_printing_{service['id']}"):
                        success = delete_line_item(service_item_id)
                        if success:
                            st.success(f"Removed {service['name']} from quote!", icon="✅")
                            # Use JavaScript to auto-clear the success message after 2 seconds
                            st.markdown("""
                                <script>
                                    setTimeout(function() {
                                        document.querySelector('.stSuccess').style.display = 'none';
                                    }, 2000);
                                </script>
                                """, unsafe_allow_html=True)
                            st.rerun()
    
    return None

def select_embroidery_service(service_loader, pricing_engine):
    """Select an embroidery service and add it to the quote."""
    # Get all embroidery services
    embroidery_services = service_loader.get_embroidery_services()
    
    if not embroidery_services:
        st.info("No embroidery services defined yet. Add some in the settings.")
        return None
    
    # Create a mapping of service names to IDs for the dropdown
    service_options = {service["name"]: service["id"] for service in embroidery_services}
    
    # Add a blank option
    service_options = {"": ""} | service_options
    
    # Service selection dropdown
    selected_service_name = st.selectbox(
        "Select Embroidery Service", 
        options=list(service_options.keys()),
        key="embroidery_service_select"
    )
    
    # If a service is selected, show details and quantity input
    if selected_service_name:
        selected_service_id = service_options[selected_service_name]
        service, _ = service_loader.get_service_by_id(selected_service_id)
        
        if service:
            # Display service details
            st.markdown(f"**Service:** {service['name']}")
            st.markdown(f"**Price:** £{service['price']:.2f}")
            
            # Quantity input
            quantity_key = f"embroidery_quantity_{service['id']}"
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=quantity_key)
            
            # Calculate price with discounts but no markup
            price_data = service_loader.calculate_service_price(service['id'], quantity, pricing_engine)
            
            # Display calculated price
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Unit Price", f"£{price_data['unit_price']:.2f}")
            
            with col2:
                st.metric("Discount", f"{price_data['discount_percent']}%")
            
            with col3:
                st.metric("Total Price", f"£{price_data['total_price']:.2f}")
            
            # Add buttons in a row - one to add and one to remove
            col1, col2 = st.columns(2)
            
            with col1:
                # Add to quote button
                if st.button("Add to Quote", key=f"add_embroidery_{service['id']}"):
                    # Prepare line item data
                    item_data = {
                        "supplier": "InkStitchPress",  # Your company as the supplier
                        "product_group": "Embroidery",  # Category
                        "style_no": service['id'],      # Use service ID as style number
                        "colours": "N/A",               # Not applicable for services
                        "sizes": "N/A",                 # Not applicable for services
                        "base_price": service['price'],  # Original price
                        "unit_price": price_data['unit_price'],  # Price with no markup
                        "quantity": quantity,
                        "discount_percent": price_data['discount_percent'],
                        "total_price": price_data['total_price'],
                        "markup_percent": 0,  # No markup for embroidery services
                        "is_service": True,   # Flag to indicate this is a service
                        "service_type": "embroidery",
                        "service_name": service['name']
                    }
                    
                    # Add the item to the session state
                    add_line_item(item_data)
                    
                    # Success message
                    st.success(f"Added {service['name']} to quote!", icon="✅")
                    # Use JavaScript to auto-clear the success message after 2 seconds
                    st.markdown("""
                        <script>
                            setTimeout(function() {
                                document.querySelector('.stSuccess').style.display = 'none';
                            }, 2000);
                        </script>
                        """, unsafe_allow_html=True)
                    
                    return item_data
            
            with col2:
                # Check if this service exists in the line items
                service_exists = False
                service_item_id = None
                
                if 'line_items' in st.session_state:
                    for item in st.session_state.line_items:
                        if (item.get('is_service', False) and 
                            item.get('service_type') == 'embroidery' and 
                            item.get('style_no') == service['id']):
                            service_exists = True
                            service_item_id = item.get('id')
                            break
                
                # Show remove button if the service exists
                if service_exists and service_item_id:
                    if st.button("Remove from Quote", key=f"remove_embroidery_{service['id']}"):
                        success = delete_line_item(service_item_id)
                        if success:
                            st.success(f"Removed {service['name']} from quote!", icon="✅")
                            # Use JavaScript to auto-clear the success message after 2 seconds
                            st.markdown("""
                                <script>
                                    setTimeout(function() {
                                        document.querySelector('.stSuccess').style.display = 'none';
                                    }, 2000);
                                </script>
                                """, unsafe_allow_html=True)
                            st.rerun()
    
    return None 