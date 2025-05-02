import streamlit as st
import pandas as pd
from app.utils.session_state import delete_line_item

def quote_summary(pricing_engine, cost_tracker=None):
    """
    Component for displaying and managing the current quote.
    
    Args:
        pricing_engine: Instance of PricingEngine to calculate totals
        cost_tracker: Optional instance of CostTracker to show profitability
    """
    st.subheader("Quote Summary")
    
    # Display current markup setting
    markup_percent = pricing_engine.get_markup_percentage()
    if markup_percent > 0:
        st.info(f"Current Markup: {markup_percent:.1f}%")
    
    # Check if there are any line items
    if 'line_items' not in st.session_state or not st.session_state.line_items:
        st.info("No items added to the quote yet.")
        return
    
    # Create a DataFrame from line items
    line_items = st.session_state.line_items
    
    # Get profitability data if cost_tracker is provided
    profit_data = None
    if cost_tracker:
        quote_data = {'line_items': line_items}
        profit_data = cost_tracker.calculate_quote_costs_and_profit(quote_data)
    
    # Create a display DataFrame with selected columns
    display_data = []
    for i, item in enumerate(line_items):
        # Check if this is a service item
        is_service = item.get("is_service", False)
        
        # Get profit data for this line item if available
        item_profit = None
        if profit_data and i < len(profit_data['line_items']):
            item_profit = profit_data['line_items'][i]
        
        if is_service:
            # For standalone service items (legacy format)
            service_type = item.get("service_type", "")
            service_name = item.get("service_name", "Unknown Service")
            display_row = {
                "id": item["id"],
                "Supplier": "InkStitchPress",
                "Product": f"{service_type.capitalize()}: {service_name}",
                "Style No": "N/A",
                "Colour": "N/A",
                "Size": "N/A",
                "Unit Price": f"£{item['unit_price']:.2f}",
                "Quantity": item["quantity"],
                "Discount": f"{item['discount_percent']}%",
                "Total": f"£{item['total_price']:.2f}"
            }
            
            # Add profit data if available
            if item_profit:
                display_row["Cost"] = f"£{item_profit['costs']['total_cost']:.2f}"
                display_row["Profit"] = f"£{item_profit['profit']:.2f}"
                display_row["Margin"] = f"{item_profit['profit_margin']:.1f}%"
                
            display_data.append(display_row)
        else:
            # Product items with optional printing/embroidery
            has_printing = item.get("has_printing", False)
            has_embroidery = item.get("has_embroidery", False)
            
            # Calculate description showing printing/embroidery included
            product_desc = item["product_group"]
            if has_printing or has_embroidery:
                decorations = []
                if has_printing:
                    decorations.append(f"{item.get('printing_service_name', 'Printing')}")
                if has_embroidery:
                    decorations.append(f"{item.get('embroidery_service_name', 'Embroidery')}")
                
                if decorations:
                    product_desc += f" + {' & '.join(decorations)}"
            
            # Add item to display data
            display_row = {
                "id": item["id"],
                "Supplier": item["supplier"],
                "Product": product_desc,
                "Style No": item["style_no"],
                "Colour": item["colours"],
                "Size": item["sizes"],
                "Unit Price": f"£{item['unit_price']:.2f}",
                "Quantity": item["quantity"],
                "Discount": f"{item['discount_percent']}%",
                "Total": f"£{item['total_price']:.2f}"
            }
            
            # Add profit data if available
            if item_profit:
                display_row["Cost"] = f"£{item_profit['costs']['total_cost']:.2f}"
                display_row["Profit"] = f"£{item_profit['profit']:.2f}"
                display_row["Margin"] = f"{item_profit['profit_margin']:.1f}%"
            
            display_data.append(display_row)
    
    df = pd.DataFrame(display_data)
    
    # Show profit toggle if cost_tracker is available
    show_profit = False
    if cost_tracker:
        show_profit = st.toggle("Show Profitability Analysis", value=False)
    
    # Create column configuration
    column_config = {
        "id": None,  # Hide ID column
        "Supplier": st.column_config.TextColumn("Supplier"),
        "Product": st.column_config.TextColumn("Product"),
        "Style No": st.column_config.TextColumn("Style No"),
        "Colour": st.column_config.TextColumn("Colour"),
        "Size": st.column_config.TextColumn("Size"),
        "Unit Price": st.column_config.TextColumn("Unit Price"),
        "Quantity": st.column_config.NumberColumn("Quantity"),
        "Discount": st.column_config.TextColumn("Discount"),
        "Total": st.column_config.TextColumn("Total"),
    }
    
    # Add profit columns if showing profit analysis
    if show_profit and "Cost" in df.columns:
        column_config.update({
            "Cost": st.column_config.TextColumn("Cost"),
            "Profit": st.column_config.TextColumn("Profit"),
            "Margin": st.column_config.TextColumn("Margin")
        })
    
    # Add delete column
    column_config["Delete"] = st.column_config.CheckboxColumn("Delete")
    
    # Display the line items with delete buttons
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        disabled=list(column_config.keys())  # Disable all columns except Delete
    )
    
    # Show line item details on selection
    if "selected_rows" in edited_df:
        for idx, row in edited_df.iterrows():
            if row.get("selected_rows", False):
                show_line_item_details(row["id"], cost_tracker, show_profit)
    
    # Calculate order total and item counts
    line_item_count = len(line_items)
    total_physical_items = sum(item["quantity"] for item in line_items)
    total_price = sum(item.get("total_price", 0) for item in line_items)
    
    # Create metrics columns
    if show_profit and profit_data:
        # Six columns with profit data
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Line Items", line_item_count)
        
        with col2:
            st.metric("Total Items", total_physical_items)
        
        with col3:
            st.metric("Revenue", f"£{profit_data['total_revenue']:.2f}")
        
        with col4:
            st.metric("Cost", f"£{profit_data['total_cost']:.2f}")
        
        with col5:
            st.metric("Profit", f"£{profit_data['total_profit']:.2f}")
        
        with col6:
            st.metric("Margin", f"{profit_data['profit_margin']:.1f}%")
            
        # Add a visual for the profit breakdown
        profit_breakdown = pd.DataFrame({
            'Category': ['Revenue', 'Cost', 'Profit'],
            'Value': [profit_data['total_revenue'], profit_data['total_cost'], profit_data['total_profit']]
        })
        
        # Add a unique key to the bar chart
        st.bar_chart(profit_breakdown, x='Category', y='Value', key="quote_summary_profit_chart")
    else:
        # Original three columns without profit data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Line Items", line_item_count)
        
        with col2:
            st.metric("Total Items", total_physical_items)
        
        with col3:
            st.metric("Order Total", f"£{total_price:.2f}")
    
    # Delete selected items
    if st.button("Delete Selected Items"):
        delete_count = 0
        
        # Get IDs to delete
        if "Delete" in edited_df.columns:
            for idx, row in edited_df.iterrows():
                if row.get("Delete", False):
                    if delete_line_item(row["id"]):
                        delete_count += 1
        
        if delete_count > 0:
            st.success(f"Deleted {delete_count} item(s).")
            st.rerun()
        else:
            st.info("No items selected for deletion.")
    
    # Button to clear all items
    if st.button("Clear All Items"):
        st.session_state.line_items = []
        st.success("All items cleared.")
        st.rerun()

def show_line_item_details(item_id, cost_tracker=None, show_profit=False):
    """Show detailed breakdown of a line item with printing/embroidery options."""
    # Find the item with the given ID
    for item in st.session_state.get('line_items', []):
        if item.get("id") == item_id:
            # Skip if it's a service-only item (legacy format)
            if item.get("is_service", False):
                return
                
            # Show detailed price breakdown
            st.divider()
            st.subheader("Line Item Details")
            
            # Product info
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Product:** {item['product_group']}")
                st.markdown(f"**Style No:** {item['style_no']}")
                st.markdown(f"**Colour:** {item['colours']}")
                st.markdown(f"**Size:** {item['sizes']}")
            
            with col2:
                st.markdown(f"**Quantity:** {item['quantity']}")
                st.markdown(f"**Discount:** {item['discount_percent']}%")
                st.markdown(f"**Total Price:** £{item['total_price']:.2f}")
            
            # Price breakdown
            st.subheader("Price Breakdown")
            
            has_printing = item.get("has_printing", False)
            has_embroidery = item.get("has_embroidery", False)
            
            price_items = [
                {"Item": "Base Garment", "Unit Price": item["unit_price"], "Total": item.get("product_total_price", 0)}
            ]
            
            if has_printing:
                price_items.append({
                    "Item": item.get("printing_service_name", "Printing"),
                    "Unit Price": item.get("printing_unit_price", 0),
                    "Total": item.get("printing_total_price", 0)
                })
            
            if has_embroidery:
                price_items.append({
                    "Item": item.get("embroidery_service_name", "Embroidery"),
                    "Unit Price": item.get("embroidery_unit_price", 0),
                    "Total": item.get("embroidery_total_price", 0)
                })
            
            # Add Grand Total
            price_items.append({
                "Item": "TOTAL",
                "Unit Price": item["unit_price"], 
                "Total": item["total_price"]
            })
            
            # Display price breakdown
            price_df = pd.DataFrame(price_items)
            st.dataframe(
                price_df,
                column_config={
                    "Item": st.column_config.TextColumn("Item"),
                    "Unit Price": st.column_config.NumberColumn("Unit Price (£)", format="£%.2f"),
                    "Total": st.column_config.NumberColumn("Total (£)", format="£%.2f")
                },
                hide_index=True
            )
            
            # Cost and profit breakdown if requested
            if cost_tracker and show_profit:
                # Get profit data for just this item
                profit_data = cost_tracker.calculate_line_item_costs(item)
                
                st.subheader("Cost & Profit Analysis")
                
                # Cost metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Cost", f"£{profit_data['total_cost']:.2f}")
                
                with col2:
                    st.metric("Profit", f"£{profit_data['profit']:.2f}")
                
                with col3:
                    st.metric("Profit Margin", f"{profit_data['profit_margin']:.1f}%")
                
                # Cost breakdown
                cost_items = []
                for key, value in profit_data.items():
                    if key not in ['total_cost', 'revenue', 'profit', 'profit_margin'] and value > 0:
                        cost_items.append({
                            "Cost Item": key.replace('_', ' ').title(),
                            "Value": value
                        })
                
                if cost_items:
                    cost_df = pd.DataFrame(cost_items)
                    st.dataframe(
                        cost_df,
                        column_config={
                            "Cost Item": st.column_config.TextColumn("Cost Item"),
                            "Value": st.column_config.NumberColumn("Cost (£)", format="£%.2f")
                        },
                        hide_index=True
                    )
                    
                    # Show cost breakdown chart with a unique key
                    st.bar_chart(cost_df, x='Cost Item', y='Value', key=f"cost_bar_chart_{item_id}")
                    
                    # Per unit analysis
                    st.subheader("Per Unit Analysis")
                    
                    unit_data = {
                        "Item": ["Unit Selling Price", "Unit Cost", "Unit Profit"],
                        "Value": [
                            profit_data['revenue'] / item['quantity'] if item['quantity'] > 0 else 0,
                            profit_data['total_cost'] / item['quantity'] if item['quantity'] > 0 else 0,
                            profit_data['profit'] / item['quantity'] if item['quantity'] > 0 else 0
                        ]
                    }
                    
                    unit_df = pd.DataFrame(unit_data)
                    st.dataframe(
                        unit_df,
                        column_config={
                            "Item": st.column_config.TextColumn("Item"),
                            "Value": st.column_config.NumberColumn("Amount (£)", format="£%.2f")
                        },
                        hide_index=True
                    ) 