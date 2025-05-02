import streamlit as st
from datetime import datetime, timedelta
import uuid
from app.utils.session_state import update_quote_details

def quote_details():
    """
    Component for managing quote details like customer name, reference, etc.
    """
    st.subheader("Quote Details")
    
    # Get current quote details from session state
    details = st.session_state.get('quote_details', {
        'customer_name': '',
        'quote_date': datetime.now().strftime('%Y-%m-%d'),
        'quote_reference': f'QU-{datetime.now().strftime("%Y%m%d")}-{str(uuid.uuid4())[:8]}',
        'expiry_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'notes': ''
    })
    
    # Create a form for quote details
    with st.form(key="quote_details_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Customer Name", value=details.get('customer_name', ''))
            quote_date = st.date_input("Quote Date", 
                                      value=datetime.strptime(details.get('quote_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'))
            quote_reference = st.text_input("Quote Reference", value=details.get('quote_reference', ''))
        
        with col2:
            expiry_date = st.date_input("Expiry Date", 
                                       value=datetime.strptime(details.get('expiry_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')), '%Y-%m-%d'))
            vat_registered = st.checkbox("VAT Registered", value=details.get('vat_registered', False))
            vat_rate = st.number_input("VAT Rate (%)", min_value=0.0, max_value=100.0, value=details.get('vat_rate', 20.0), step=0.1) if vat_registered else 0.0
        
        # Notes and terms
        st.subheader("Notes & Terms")
        notes = st.text_area("Notes", value=details.get('notes', ''), height=100)
        
        terms_options = [
            "Please note that due to current supply price changes, we can only guarantee our quotations for 30 days from the above-mentioned date, after this, our quote may change.",
            "The client acknowledges that the seller cannot be held responsible for replacing or repairing items supplied by the client that may be damaged during the embroidery or print process."
        ]
        
        selected_terms = st.multiselect(
            "Select Terms & Conditions",
            options=terms_options,
            default=details.get('terms', terms_options)
        )
        
        # Company details
        st.subheader("Company Details")
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", value=details.get('company_name', 'Ink Stitch Press Ltd'))
            company_address_line1 = st.text_input("Address Line 1", value=details.get('company_address_line1', 'Unit C8, Seedbed'))
            company_address_line2 = st.text_input("Address Line 2", value=details.get('company_address_line2', 'Business Centre'))
        
        with col2:
            company_address_line3 = st.text_input("Address Line 3", value=details.get('company_address_line3', 'Vanguard Way'))
            company_address_line4 = st.text_input("Address Line 4", value=details.get('company_address_line4', 'Shoeburyness'))
            company_postcode = st.text_input("Postcode", value=details.get('company_postcode', 'SS3 9QY'))
        
        company_registration = st.text_input("Company Registration", 
                                           value=details.get('company_registration', 'Company Registration No: 13154821. Registered Office: Attention: Ink Stitch Press Limited, Clarence Street Chambers, 32 Clarence Street, Southend on Sea, Essex, SS1 1BD, United Kingdom.'))
        
        # Submit button
        submitted = st.form_submit_button("Save Quote Details")
        
        if submitted:
            # Prepare updated details
            updated_details = {
                'customer_name': customer_name,
                'quote_date': quote_date.strftime('%Y-%m-%d'),
                'quote_reference': quote_reference,
                'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                'vat_registered': vat_registered,
                'vat_rate': vat_rate if vat_registered else 0.0,
                'notes': notes,
                'terms': selected_terms,
                'company_name': company_name,
                'company_address_line1': company_address_line1,
                'company_address_line2': company_address_line2,
                'company_address_line3': company_address_line3,
                'company_address_line4': company_address_line4,
                'company_postcode': company_postcode,
                'company_registration': company_registration
            }
            
            # Update session state
            update_quote_details(updated_details)
            
            st.success("Quote details saved successfully!")
    
    return details 