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
    
    # Check if we're using old Size Range structure and show refresh option
    try:
        import sqlite3
        conn = sqlite3.connect(data_loader.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
        
        needs_update = False
        update_message = "⚠️ Database needs updating: "
        update_reasons = []
        
        if "Size Range" in columns and "Web Size" not in columns:
            needs_update = True
            update_reasons.append("Individual sizes (Web Size)")
            
        if "Colour Name" not in columns:
            needs_update = True
            update_reasons.append("Color information")
        
        if needs_update:
            st.warning(update_message + " & ".join(update_reasons))
            if st.button("🔄 Update Database (Web Size + Colors)", type="primary"):
                with st.spinner("Updating to individual sizes..."):
                    # Force clear the database first
                    try:
                        import os
                        if os.path.exists(data_loader.db_path):
                            os.remove(data_loader.db_path)
                    except Exception as e:
                        st.warning(f"Could not clear old database: {e}")
                    
                    success, message = data_loader.load_excel_to_db()
                    if success:
                        st.success("✅ Updated database with Web Size + Colors! Please refresh the page.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ " + message)
                return None
                        
    except Exception as e:
        pass  # Continue normally if database check fails
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Brand selection
        brands = data_loader.get_unique_values("Brand")
        brand = st.selectbox("Brand", [""] + brands, key="brand_select")
        
        # If brand selected, show product groups for that brand
        product_groups = []
        if brand:
            # Get filtered products for this brand
            filtered_df = data_loader.get_filtered_products(brand=brand)
            product_groups = sorted(filtered_df["Product Group"].unique().tolist())
            if "Product Group" in st.session_state and st.session_state["Product Group"] not in product_groups:
                st.session_state["Product Group"] = ""
        
        product_group = st.selectbox("Product Group", [""] + product_groups, key="Product Group")
    
    with col2:
        # If product group selected, show primary categories for that brand and product group
        primary_categories = []
        if brand and product_group:
            # Get filtered products to extract available primary categories
            filtered_df = data_loader.get_filtered_products(brand=brand, product_group=product_group)
            primary_categories = sorted(filtered_df["Primary Category"].unique().tolist())
            if "Primary Category" in st.session_state and st.session_state["Primary Category"] not in primary_categories:
                st.session_state["Primary Category"] = ""
        
        primary_category = st.selectbox("Primary Category", [""] + primary_categories, key="Primary Category")
        
        # Product name search field
        product_name_filter = st.text_input("Search Product Name (optional)", key="product_name_filter")
    
    # Second row for Web Size selection
    if brand and product_group:
        # Get available Web Sizes for the current selection
        filtered_df = data_loader.get_filtered_products(
            brand=brand, 
            product_group=product_group,
            primary_category=primary_category if primary_category else None,
            product_name=product_name_filter if product_name_filter else None
        )
        
        web_sizes = []
        if not filtered_df.empty:
            # Check if Web Size column exists, fallback to Size Range if not
            if "Web Size" in filtered_df.columns:
                web_sizes = sorted(filtered_df["Web Size"].unique().tolist())
                size_column = "Web Size"
            elif "Size Range" in filtered_df.columns:
                web_sizes = sorted(filtered_df["Size Range"].unique().tolist())
                size_column = "Size Range"
            else:
                web_sizes = []
                size_column = None
                
            if size_column and size_column in st.session_state and st.session_state[size_column] not in web_sizes:
                st.session_state[size_column] = ""
        
        # Use appropriate label based on available column  
        if not filtered_df.empty:
            size_label = "Web Size" if "Web Size" in filtered_df.columns else "Size Range"
        else:
            size_label = "Web Size"
        web_size = st.selectbox(size_label, [""] + web_sizes, key="Web Size")
    else:
        web_size = None
    
    # Third row for Color selection
    if brand and product_group and web_size:
        # Get available Colors for the current selection
        filtered_df = data_loader.get_filtered_products(
            brand=brand, 
            product_group=product_group,
            primary_category=primary_category if primary_category else None,
            product_name=product_name_filter if product_name_filter else None,
            web_size=web_size
        )
        
        colours = []
        if not filtered_df.empty:
            if "Colour Name" in filtered_df.columns:
                colours = sorted(filtered_df["Colour Name"].unique().tolist())
                print(f"DEBUG: Found {len(colours)} colors: {colours[:5]}")
                if "Colour Name" in st.session_state and st.session_state["Colour Name"] not in colours:
                    st.session_state["Colour Name"] = ""
            else:
                print("DEBUG: No Colour Name column in filtered data")
                st.info("💡 Color selection not available - database may need updating with color data")
        else:
            print("DEBUG: No products found for color filtering")
        
        colour_name = st.selectbox("Colour", [""] + colours, key="Colour Name")
    else:
        colour_name = None
    
    # Get product details if required filters are selected
    selected_product = None
    if brand and product_group:
        filtered_df = data_loader.get_filtered_products(
            brand=brand,
            product_group=product_group,
            primary_category=primary_category if primary_category else None,
            product_name=product_name_filter if product_name_filter else None,
            web_size=web_size if web_size else None,
            colour_name=colour_name if colour_name else None
        )
        
        if not filtered_df.empty:
            # Show a selectbox if multiple products match
            if len(filtered_df) > 1:
                product_options = {}
                for idx, row in filtered_df.iterrows():
                    # Use the appropriate size column for display
                    size_value = row.get('Web Size', row.get('Size Range', 'N/A'))
                    colour_value = row.get('Colour Name', 'N/A')
                    display_name = f"{row['Product Name']} - {size_value} - {colour_value}"
                    product_options[display_name] = idx
                
                selected_display_name = st.selectbox("Select Product", list(product_options.keys()), key="product_selection")
                selected_idx = product_options[selected_display_name]
                selected_product = filtered_df.loc[selected_idx]
            else:
                selected_product = filtered_df.iloc[0]
            
            # Display product details
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Selected Product:** {selected_product['Product Name']}")
                st.markdown(f"**Brand:** {brand}")
                st.markdown(f"**Product Group:** {product_group}")
            
            with col2:
                st.markdown(f"**Primary Category:** {selected_product['Primary Category']}")
                # Display the appropriate size column
                size_value = selected_product.get('Web Size', selected_product.get('Size Range', 'N/A'))
                size_label = 'Web Size' if 'Web Size' in selected_product else 'Size Range'
                st.markdown(f"**{size_label}:** {size_value}")
                # Display color information
                colour_value = selected_product.get('Colour Name', 'N/A')
                st.markdown(f"**Colour:** {colour_value}")
                
                # Use the 'Price' column (renamed from 'Cust Single Price')
                if 'Price' in selected_product:
                    base_price = selected_product['Price']
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
        # Use appropriate size column and color for the quantity key
        size_value = selected_product.get('Web Size', selected_product.get('Size Range', 'N/A'))
        colour_value = selected_product.get('Colour Name', 'N/A')
        quantity_key = f"quantity_input_{selected_product['Product Group']}_{selected_product['Product Name']}_{size_value}_{colour_value}"
        
        # Check if we need to reset the quantity (after adding an item)
        if "reset_quantity" in st.session_state and st.session_state.reset_quantity == quantity_key:
            # Clear the reset flag
            st.session_state.reset_quantity = None
            # Initialize a new widget (this avoids the double assignment warning)
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=quantity_key)
        else:
            # Normal case - just display the input
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=quantity_key)
        
        # Use the 'Price' column (renamed from 'Cust Single Price')
        if 'Price' not in selected_product:
            st.error("Price column not found in the data")
            return None
            
        base_price = selected_product['Price']  # Using the single garment price as requested
        
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
                                supplier=brand,
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
                                supplier=brand,
                                product_group=product_group,
                                line_items=st.session_state.get('line_items', [])
                            )
                else:
                    st.info("No embroidery services defined yet. Add some in the settings.")
        
        # Get existing line items
        line_items = st.session_state.get('line_items', [])
        
        # Calculate garment price with markup and bulk quantity discounts for same brand/product group
        product_price_data = pricing_engine.calculate_price(
            base_price, 
            quantity,
            supplier=brand,
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
            
            # Calculate and show the total quantity for this brand and product group
            total_group_quantity = pricing_engine.get_supplier_product_group_quantity(
                brand, product_group, line_items) + quantity
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
                "supplier": brand,
                "product_group": product_group,
                "product_name": selected_product['Product Name'],
                "primary_category": selected_product['Primary Category'],
                "web_size": selected_product.get('Web Size', selected_product.get('Size Range', 'N/A')),
                "colour_name": selected_product.get('Colour Name', 'N/A'),
                "colour_code": selected_product.get('Colour Code', 'N/A'),
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
            st.success(f"Added {selected_product['Product Name']} to quote!", icon="✅")
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