import streamlit as st
import pandas as pd
from app.utils.session_state import add_line_item

def product_selector(data_loader, pricing_engine, service_loader=None):
    """
    Component for selecting products with cascading filters.
    
    Args:
        data_loader: Instance of DataLoader to fetch product data
        pricing_engine: Instance of PricingEngine to calculate prices
        service_loader: Instance of ServiceLoader to fetch service data
    
    Returns:
        dict: Selected product data if a product is selected and quantity entered
    """
    st.subheader("Product Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Supplier selection
        suppliers = data_loader.get_unique_values("Supplier")
        supplier = st.selectbox("Supplier", [""] + suppliers, key="supplier_select")
        
        # If supplier selected, show product groups for that supplier
        product_groups = []
        if supplier:
            # Get filtered products for this supplier
            filtered_df = data_loader.get_filtered_products(supplier=supplier)
            product_groups = sorted(filtered_df["Product Group"].unique().tolist())
            if "Product Group" in st.session_state and st.session_state["Product Group"] not in product_groups:
                st.session_state["Product Group"] = ""
        
        product_group = st.selectbox("Product Group", [""] + product_groups, key="Product Group")
    
    with col2:
        # If product group selected, show colors for that supplier and product group
        colours = []
        if supplier and product_group:
            # Get filtered products to extract available colors
            filtered_df = data_loader.get_filtered_products(supplier=supplier, product_group=product_group)
            colours = sorted(filtered_df["Colours"].unique().tolist())
            if "Colours" in st.session_state and st.session_state["Colours"] not in colours:
                st.session_state["Colours"] = ""
        
        colour = st.selectbox("Colours", [""] + colours, key="Colours")
        
        # If color selected, show sizes for that supplier, product group, and color
        sizes = []
        if supplier and product_group and colour:
            # Get filtered products to extract available sizes
            filtered_df = data_loader.get_filtered_products(
                supplier=supplier, 
                product_group=product_group,
                colours=colour
            )
            sizes = sorted(filtered_df["Sizes"].unique().tolist())
            if "Sizes" in st.session_state and st.session_state["Sizes"] not in sizes:
                st.session_state["Sizes"] = ""
        
        size = st.selectbox("Sizes", [""] + sizes, key="Sizes")
    
    # Get product details if all filters are selected
    selected_product = None
    if supplier and product_group and colour and size:
        filtered_df = data_loader.get_filtered_products(
            supplier=supplier,
            product_group=product_group,
            colours=colour,
            sizes=size
        )
        
        if not filtered_df.empty:
            selected_product = filtered_df.iloc[0]
            
            # Display product details
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Selected Product:** {product_group}")
                st.markdown(f"**Supplier:** {supplier}")
                st.markdown(f"**Style No:** {selected_product['Style No']}")
            
            with col2:
                st.markdown(f"**Colour:** {colour}")
                st.markdown(f"**Size:** {size}")
                # Check which column to use for price and handle potential missing columns
                if 'Price (£).2' in selected_product:
                    price_col = 'Price (£).2'
                elif 'Price (£)' in selected_product:
                    price_col = 'Price (£)'
                else:
                    # Try to find a column with 'Price' in its name
                    price_cols = [col for col in selected_product.index if 'Price' in str(col)]
                    price_col = price_cols[-1] if price_cols else None
                
                if price_col:
                    base_price = selected_product[price_col]
                    # Apply markup to the base price
                    markup_percent = pricing_engine.get_markup_percentage()
                    markup_factor = 1 + (markup_percent / 100)
                    marked_up_price = base_price * markup_factor
                    st.markdown(f"**Price:** £{marked_up_price:.2f}")
                else:
                    st.error("Price column not found in the data")
                    return None
    
    # Quantity input and price calculation
    if selected_product is not None:
        st.divider()
        
        # Generate a unique key for the quantity input
        quantity_key = f"quantity_input_{selected_product['Style No']}_{colour}_{size}"
        
        # Check if we need to reset the quantity (after adding an item)
        if "reset_quantity" in st.session_state and st.session_state.reset_quantity == quantity_key:
            # Clear the reset flag
            st.session_state.reset_quantity = None
            # Initialize a new widget (this avoids the double assignment warning)
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=quantity_key)
        else:
            # Normal case - just display the input
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=quantity_key)
        
        # Determine which price column to use (same logic as above)
        if 'Price (£).2' in selected_product:
            price_col = 'Price (£).2'
        elif 'Price (£)' in selected_product:
            price_col = 'Price (£)'
        else:
            price_cols = [col for col in selected_product.index if 'Price' in str(col)]
            price_col = price_cols[-1] if price_cols else None
        
        if not price_col:
            st.error("Price column not found in the data")
            return None
            
        base_price = selected_product[price_col]  # Using the single garment price as requested
        
        # Add Printing and Embroidery options if service_loader is provided
        selected_printing_service = None
        selected_embroidery_service = None
        printing_price_data = None
        embroidery_price_data = None
        
        if service_loader:
            st.divider()
            st.subheader("Decoration Options")
            
            # Create tabs for different decoration types
            tab1, tab2 = st.tabs(["Printing", "Embroidery"])
            
            with tab1:
                # Get all printing services
                printing_services = service_loader.get_printing_services()
                
                if printing_services:
                    # Create a mapping of service names to IDs for the dropdown
                    printing_options = {service["name"]: service["id"] for service in printing_services}
                    
                    # Add a blank option
                    printing_options = {"None": ""} | printing_options
                    
                    # Service selection dropdown
                    selected_printing_name = st.selectbox(
                        "Select Printing Option", 
                        options=list(printing_options.keys()),
                        key=f"printing_select_{quantity_key}"
                    )
                    
                    # If a service is selected, get the service details
                    if selected_printing_name and selected_printing_name != "None":
                        selected_printing_id = printing_options[selected_printing_name]
                        selected_printing_service, _ = service_loader.get_service_by_id(selected_printing_id)
                        
                        if selected_printing_service:
                            st.markdown(f"**Selected Printing:** {selected_printing_service['name']}")
                            st.markdown(f"**Price per item:** £{selected_printing_service['price']:.2f}")
                            
                            # Calculate printing price with discounts but no markup
                            printing_price_data = service_loader.calculate_service_price(
                                selected_printing_id, 
                                quantity, 
                                pricing_engine,
                                supplier=supplier,
                                product_group=product_group,
                                line_items=st.session_state.get('line_items', [])
                            )
                else:
                    st.info("No printing services defined yet. Add some in the settings.")
            
            with tab2:
                # Get all embroidery services
                embroidery_services = service_loader.get_embroidery_services()
                
                if embroidery_services:
                    # Create a mapping of service names to IDs for the dropdown
                    embroidery_options = {service["name"]: service["id"] for service in embroidery_services}
                    
                    # Add a blank option
                    embroidery_options = {"None": ""} | embroidery_options
                    
                    # Service selection dropdown
                    selected_embroidery_name = st.selectbox(
                        "Select Embroidery Option", 
                        options=list(embroidery_options.keys()),
                        key=f"embroidery_select_{quantity_key}"
                    )
                    
                    # If a service is selected, get the service details
                    if selected_embroidery_name and selected_embroidery_name != "None":
                        selected_embroidery_id = embroidery_options[selected_embroidery_name]
                        selected_embroidery_service, _ = service_loader.get_service_by_id(selected_embroidery_id)
                        
                        if selected_embroidery_service:
                            st.markdown(f"**Selected Embroidery:** {selected_embroidery_service['name']}")
                            st.markdown(f"**Price per item:** £{selected_embroidery_service['price']:.2f}")
                            
                            # Calculate embroidery price with discounts but no markup
                            embroidery_price_data = service_loader.calculate_service_price(
                                selected_embroidery_id, 
                                quantity, 
                                pricing_engine,
                                supplier=supplier,
                                product_group=product_group,
                                line_items=st.session_state.get('line_items', [])
                            )
                else:
                    st.info("No embroidery services defined yet. Add some in the settings.")
        
        # Get existing line items
        line_items = st.session_state.get('line_items', [])
        
        # Calculate garment price with markup and bulk quantity discounts for same supplier/product group
        product_price_data = pricing_engine.calculate_price(
            base_price, 
            quantity,
            supplier=supplier,
            product_group=product_group,
            line_items=line_items
        )
        
        # Calculate total price including printing and embroidery if selected
        total_price = product_price_data['total_price']
        unit_price = product_price_data['unit_price']
        
        printing_unit_price = 0
        printing_total_price = 0
        embroidery_unit_price = 0
        embroidery_total_price = 0
        
        if printing_price_data:
            printing_unit_price = printing_price_data['unit_price']
            printing_total_price = printing_price_data['total_price']
            total_price += printing_total_price
            
        if embroidery_price_data:
            embroidery_unit_price = embroidery_price_data['unit_price']
            embroidery_total_price = embroidery_price_data['total_price']
            total_price += embroidery_total_price
        
        # Display calculated price breakdown
        st.divider()
        st.subheader("Price Breakdown")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Garment Unit Price", f"£{unit_price:.2f}")
            if printing_unit_price > 0:
                st.metric("Printing Unit Price", f"£{printing_unit_price:.2f}")
            if embroidery_unit_price > 0:
                st.metric("Embroidery Unit Price", f"£{embroidery_unit_price:.2f}")
        
        with col2:
            st.metric("Quantity", quantity)
            st.metric("Discount", f"{product_price_data['discount_percent']}%")
            
            # Calculate and show the total quantity for this supplier and product group
            total_group_quantity = pricing_engine.get_supplier_product_group_quantity(
                supplier, product_group, line_items) + quantity
            if total_group_quantity > quantity:
                st.metric("Total Group Quantity", total_group_quantity)
        
        with col3:
            st.metric("Garment Total", f"£{product_price_data['total_price']:.2f}")
            if printing_total_price > 0:
                st.metric("Printing Total", f"£{printing_total_price:.2f}")
            if embroidery_total_price > 0:
                st.metric("Embroidery Total", f"£{embroidery_total_price:.2f}")
            st.metric("Total Price", f"£{total_price:.2f}", delta=f"{total_price - product_price_data['total_price']:.2f}")
        
        # Add to quote button
        if st.button("Add to Quote"):
            # Prepare line item data
            item_data = {
                "supplier": supplier,
                "product_group": product_group,
                "style_no": selected_product['Style No'],
                "colours": colour,
                "sizes": size,
                "base_price": base_price,                  # Store base price but don't display
                "unit_price": product_price_data['unit_price'],    # This is the marked-up price
                "quantity": quantity,
                "discount_percent": product_price_data['discount_percent'],
                "product_total_price": product_price_data['total_price'],
                "markup_percent": product_price_data['markup_percent'],
                # Add printing details if selected
                "has_printing": selected_printing_service is not None,
                "printing_service_id": selected_printing_service['id'] if selected_printing_service else None,
                "printing_service_name": selected_printing_service['name'] if selected_printing_service else None,
                "printing_unit_price": printing_unit_price,
                "printing_total_price": printing_total_price,
                # Add embroidery details if selected
                "has_embroidery": selected_embroidery_service is not None,
                "embroidery_service_id": selected_embroidery_service['id'] if selected_embroidery_service else None,
                "embroidery_service_name": selected_embroidery_service['name'] if selected_embroidery_service else None,
                "embroidery_unit_price": embroidery_unit_price,
                "embroidery_total_price": embroidery_total_price,
                # Total price including all services
                "total_price": total_price
            }
            
            # Add the item to the session state using the add_line_item function
            add_line_item(item_data)
            
            # After adding item, recalculate discounts for all items based on the new bulk quantities
            updated_items = pricing_engine.recalculate_discounts(st.session_state.line_items)
            st.session_state.line_items = updated_items
            
            # Set a flag to reset the quantity on next render instead of directly setting the session state
            st.session_state.reset_quantity = quantity_key
            
            # Use st.success with auto-clear
            st.success(f"Added {product_group} to quote!", icon="✅")
            # Use JavaScript to auto-clear the success message after 2 seconds
            st.markdown("""
                <script>
                    setTimeout(function() {
                        document.querySelector('.stSuccess').style.display = 'none';
                    }, 2000);
                </script>
                """, unsafe_allow_html=True)
            
            return item_data
    
    return None 