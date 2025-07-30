import streamlit as st
import pandas as pd

def discount_settings(pricing_engine):
    """
    Component for configuring discount brackets.
    
    Args:
        pricing_engine: Instance of PricingEngine to manage discount settings
    """
    st.subheader("Discount Settings")
    
    # Get current discount settings
    discounts = pricing_engine.discounts
    
    # Create a table of discount brackets
    brackets_data = []
    for bracket in discounts.get("brackets", []):
        try:
            # Ensure all values are valid
            min_qty = bracket.get("min", 1)
            max_qty = bracket.get("max", 24)
            discount_val = bracket.get("discount", 0)
            
            # Convert to proper types and validate
            if pd.notna(min_qty) and pd.notna(max_qty) and pd.notna(discount_val):
                brackets_data.append({
                    "min_qty": int(min_qty),
                    "max_qty": int(max_qty),
                    "discount": float(discount_val)
                })
        except (ValueError, TypeError) as e:
            st.error(f"Error loading discount bracket: {e}")
            continue
    
    # If no valid data, provide default
    if not brackets_data:
        brackets_data = [
            {"min_qty": 1, "max_qty": 24, "discount": 0.0},
            {"min_qty": 25, "max_qty": 49, "discount": 5.0},
            {"min_qty": 50, "max_qty": 99, "discount": 10.0},
            {"min_qty": 100, "max_qty": 10000, "discount": 15.0}
        ]
    
    brackets_df = pd.DataFrame(brackets_data)
    
    # Display editable table for discount brackets
    edited_df = st.data_editor(
        brackets_df,
        column_config={
            "min_qty": st.column_config.NumberColumn(
                "Min Quantity",
                min_value=1,
                step=1,
            ),
            "max_qty": st.column_config.NumberColumn(
                "Max Quantity",
                min_value=1,
                step=1,
            ),
            "discount": st.column_config.NumberColumn(
                "Discount %",
                min_value=0,
                max_value=100,
                step=1,
                format="%.1f",
            ),
        },
        hide_index=True,
        num_rows="dynamic",
        key="discount_brackets_editor"
    )
    
    # Save button
    if st.button("Save Discount Settings"):
        # Prepare new discount brackets
        new_brackets = []
        for _, row in edited_df.iterrows():
            try:
                # Skip rows with empty/invalid values
                if pd.isna(row["min_qty"]) or pd.isna(row["max_qty"]) or pd.isna(row["discount"]):
                    continue
                    
                min_qty = int(row["min_qty"])
                max_qty = int(row["max_qty"]) 
                discount = float(row["discount"])
                
                # Validate values
                if min_qty < 1 or max_qty < min_qty or discount < 0:
                    st.error(f"Invalid discount bracket: min={min_qty}, max={max_qty}, discount={discount}")
                    continue
                    
                new_brackets.append({
                    "min": min_qty,
                    "max": max_qty,
                    "discount": discount
                })
            except (ValueError, TypeError) as e:
                st.error(f"Error processing discount bracket: {e}")
                continue
        
        # Sort brackets by min quantity
        new_brackets.sort(key=lambda x: x["min"])
        
        # Prepare new discount settings
        new_discounts = {
            "brackets": new_brackets
        }
        
        # Save the new settings
        success, message = pricing_engine.save_discounts(new_discounts)
        
        if success:
            st.success(message)
        else:
            st.error(message) 