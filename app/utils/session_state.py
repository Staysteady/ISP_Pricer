import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'line_items' not in st.session_state:
        st.session_state.line_items = []
    
    if 'quote_details' not in st.session_state:
        st.session_state.quote_details = {
            'customer_name': '',
            'quote_date': datetime.now().strftime('%Y-%m-%d'),
            'quote_reference': f'Q-{datetime.now().strftime("%Y%m%d")}-{str(uuid.uuid4())[:8]}',
            'notes': ''
        }
    
    if 'initialized_db' not in st.session_state:
        st.session_state.initialized_db = False

def add_line_item(item_data):
    """Add a new line item to the quote."""
    if 'line_items' not in st.session_state:
        st.session_state.line_items = []
    
    # Create a unique ID for the line item
    item_data['id'] = str(uuid.uuid4())
    
    # Add timestamp
    item_data['timestamp'] = datetime.now().isoformat()
    
    # Add to session state
    st.session_state.line_items.append(item_data)
    
    return item_data['id']

def update_line_item(item_id, updated_data):
    """Update an existing line item by ID."""
    if 'line_items' not in st.session_state:
        return False
    
    for i, item in enumerate(st.session_state.line_items):
        if item['id'] == item_id:
            # Update the item but preserve id and timestamp
            updated_data['id'] = item_id
            updated_data['timestamp'] = item.get('timestamp', datetime.now().isoformat())
            st.session_state.line_items[i] = updated_data
            return True
    
    return False

def delete_line_item(item_id):
    """Delete a line item by ID."""
    if 'line_items' not in st.session_state:
        return False
    
    for i, item in enumerate(st.session_state.line_items):
        if item['id'] == item_id:
            st.session_state.line_items.pop(i)
            return True
    
    return False

def get_line_items_as_dataframe():
    """Convert line items to a pandas DataFrame for display."""
    if 'line_items' not in st.session_state or not st.session_state.line_items:
        return pd.DataFrame()
    
    return pd.DataFrame(st.session_state.line_items)

def clear_line_items():
    """Clear all line items."""
    st.session_state.line_items = []

def update_quote_details(details):
    """Update the quote details."""
    if 'quote_details' not in st.session_state:
        st.session_state.quote_details = {}
    
    st.session_state.quote_details.update(details)

def get_full_quote_data():
    """Get the full quote data including details and line items."""
    return {
        'details': st.session_state.get('quote_details', {}),
        'line_items': st.session_state.get('line_items', [])
    } 