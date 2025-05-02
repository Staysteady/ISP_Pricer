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
        brackets_data.append({
            "min_qty": bracket["min"],
            "max_qty": bracket["max"],
            "discount": bracket["discount"]
        })
    
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
            new_brackets.append({
                "min": int(row["min_qty"]),
                "max": int(row["max_qty"]),
                "discount": float(row["discount"])
            })
        
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