import streamlit as st

# Set page config - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="InkStitchPress Pricer",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import pandas as pd
import base64

# Determine if we're in cloud deployment
is_cloud = 'STREAMLIT_SHARING' in os.environ or 'DEPLOYED' in os.environ or st.secrets.get('DEPLOYED', False)

# Import appropriate data loader
if is_cloud:
    # Import cloud version
    from app.utils.cloud_data_loader import CloudDataLoader as DataLoader
    st.write("🌥️ Running in cloud mode with Supabase database")
else:
    # Import local version
    from app.utils.data_loader import DataLoader
    st.write("💻 Running in local mode with SQLite database")

from app.utils.pricing_engine import PricingEngine
from app.utils.service_loader import ServiceLoader
from app.utils.cost_tracker import CostTracker
from app.utils.session_state import initialize_session_state, add_line_item, get_full_quote_data

from app.components.product_selector import product_selector
from app.components.quote_summary import quote_summary
from app.components.discount_settings import discount_settings
from app.components.markup_settings import markup_settings
from app.components.data_upload import data_upload
from app.components.quote_details import quote_details
from app.components.pdf.quote_actions import quote_actions
from app.components.service_settings import service_settings
from app.components.service_selector import service_selector
from app.components.cost_tracker import cost_tracker_main

# Function to load and display the logo
def display_logo():
    logo_path = "app/static/images/inkstitchpress_logo.png"
    if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
        # Display the logo image if it exists
        with open(logo_path, "rb") as f:
            logo_contents = f.read()
            logo_base64 = base64.b64encode(logo_contents).decode("utf-8")
            
        # Display logo with custom HTML
        st.markdown(
            f'<div style="display: flex; justify-content: center; margin-bottom: 20px;">'
            f'<img src="data:image/png;base64,{logo_base64}" style="max-width: 300px; max-height: 100px;">'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        # Fallback to text if logo isn't available
        st.title("InkStitchPress Pricer")

# Initialize session state
initialize_session_state()

# Initialize components
data_loader = DataLoader()
pricing_engine = PricingEngine()
service_loader = ServiceLoader()
cost_tracker = CostTracker()

# Display logo and title
display_logo()
st.markdown("Pricing tool for InkStitchPress printing and embroidery business")

# Create mode selector in sidebar
with st.sidebar:
    st.header("Mode Selection")
    app_mode = st.radio(
        "Select Mode",
        ["Quoting Tool", "Cost Tracker"],
        horizontal=True,
        help="Quoting Tool: Create quotes for customers. Cost Tracker: Track business costs and profitability."
    )

# Quoting tool mode
if app_mode == "Quoting Tool":
    # Sidebar for settings and data management
    with st.sidebar:
        st.header("Settings & Data")
        
        # Show quote stats if there are line items
        if 'line_items' in st.session_state and st.session_state.line_items:
            line_item_count = len(st.session_state.line_items)
            total_physical_items = sum(item["quantity"] for item in st.session_state.line_items)
            
            # Display compact stats
            st.caption(f"📋 Current Quote: {line_item_count} line items ({total_physical_items} items total)")
            st.divider()
        
        # First-time setup
        if not data_loader.is_db_initialized() and not st.session_state.get("initialized_db", False):
            st.warning("Please upload a price list Excel file to begin.")
            
            # Show data upload form
            data_upload(data_loader)
            
            # Check if we have the default file to auto-load
            default_file = "ralawise-price-list---uk---2025---6th-april-2025.xlsx"
            if os.path.exists(default_file) and st.button("Load Default Price List"):
                with st.spinner("Loading default price list..."):
                    if is_cloud:
                        # For cloud deployment, read the file and pass it directly
                        with open(default_file, "rb") as f:
                            excel_file = f.read()
                        success, message = data_loader.load_excel_to_db(excel_file)
                    else:
                        # For local deployment, pass the file path
                        success, message = data_loader.load_excel_to_db(default_file)
                        
                    if success:
                        st.success(message)
                        st.session_state.initialized_db = True
                        st.rerun()
                    else:
                        st.error(message)
        else:
            # Tabs for different settings
            tab1, tab2, tab3, tab4 = st.tabs(["Markup Settings", "Discount Settings", "Printing & Embroidery", "Update Price List"])
            
            with tab1:
                markup_settings(pricing_engine)
                
            with tab2:
                discount_settings(pricing_engine)
            
            with tab3:
                service_settings(service_loader)
            
            with tab4:
                data_upload(data_loader)

    # Main content layout
    if data_loader.is_db_initialized() or st.session_state.get("initialized_db", False):
        # Get line item count for tab display
        line_item_count = len(st.session_state.get('line_items', []))
        line_item_text = f"Quote Summary ({line_item_count})" if line_item_count > 0 else "Quote Summary"
        
        # Create tabs for product selection, quote summary, quote details and PDF actions
        tab1, tab2, tab3, tab4 = st.tabs(["Product Selection", line_item_text, "Quote Details", "Generate & Send"])
        
        with tab1:
            # Product selection form with service options integrated
            selected_item = product_selector(data_loader, pricing_engine, service_loader)
            
            if selected_item:
                # Refresh the page to show updated items in summary
                st.rerun()
        
        with tab2:
            # Display quote summary - pass cost_tracker to enable profitability analysis
            quote_summary(pricing_engine, cost_tracker)
        
        with tab3:
            # Quote details form
            details = quote_details()
        
        with tab4:
            # Get the full quote data
            quote_data = st.session_state.get('quote_details', {})
            line_items = st.session_state.get('line_items', [])
            
            # Quote actions (generate PDF, email)
            quote_actions(quote_data, line_items, pricing_engine)

    else:
        # Display placeholder instructions
        st.info("Please upload a price list file in the sidebar to get started.")

# Cost Tracker mode
else:
    # Display the cost tracker
    cost_tracker_main(cost_tracker) 