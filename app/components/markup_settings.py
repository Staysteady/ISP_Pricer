import streamlit as st

def markup_settings(pricing_engine):
    """
    Component for configuring markup percentage.
    
    Args:
        pricing_engine: Instance of PricingEngine to manage markup settings
    """
    st.subheader("Markup Settings")
    
    # Get current markup percentage
    current_markup = pricing_engine.get_markup_percentage()
    
    # Display markup percentage input
    markup_percentage = st.number_input(
        "Markup Percentage",
        min_value=0.0,
        max_value=500.0,
        value=float(current_markup),
        step=1.0,
        format="%.1f",
        help="Enter the markup percentage to apply to base prices (e.g., 50 for 50% markup)"
    )
    
    st.text(f"This will add {markup_percentage}% to the base prices from your supplier")
    
    # Save button
    if st.button("Save Markup"):
        # Prepare new markup setting
        new_markup = {
            "percentage": markup_percentage
        }
        
        # Save the new setting
        success, message = pricing_engine.save_markup(new_markup)
        
        if success:
            st.success(message)
        else:
            st.error(message) 