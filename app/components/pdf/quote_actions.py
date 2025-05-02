import streamlit as st
import os
from app.components.pdf.quote_generator import QuoteGenerator
from app.components.pdf.email_sender import EmailSender

def quote_actions(quote_data, line_items, pricing_engine):
    """
    Component for generating, viewing and emailing quotes.
    
    Args:
        quote_data: Dictionary containing quote details
        line_items: List of line items
        pricing_engine: Instance of PricingEngine to calculate totals
    """
    st.subheader("Quote Actions")
    
    if not line_items:
        st.warning("Please add items to your quote before generating a PDF.")
        return
    
    # Initialize quote generator and email sender
    quote_generator = QuoteGenerator()
    email_sender = EmailSender()
    
    # Check if there's a previously generated PDF for this quote
    quote_ref = quote_data.get('quote_reference', '')
    pdf_filename = f"{quote_ref}.pdf"
    pdf_path = os.path.join(quote_generator.output_dir, pdf_filename)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate or regenerate PDF button
        if st.button("Generate PDF Quote", key="generate_pdf_button"):
            with st.spinner("Generating PDF..."):
                pdf_path, pdf_content = quote_generator.generate_quote_pdf(quote_data, line_items, pricing_engine)
                
                # Store PDF content in session state for viewing
                st.session_state.current_pdf_content = pdf_content
                st.session_state.current_pdf_path = pdf_path
                
                st.success(f"PDF quote generated successfully")
                st.rerun()  # Rerun to display the PDF
    
    # Set PDF viewing and emailing options if PDF has been generated
    pdf_exists = os.path.exists(pdf_path)
    
    if pdf_exists or ('current_pdf_path' in st.session_state and os.path.exists(st.session_state.current_pdf_path)):
        # Use the session state path if available, otherwise use the default path
        if 'current_pdf_path' in st.session_state and os.path.exists(st.session_state.current_pdf_path):
            pdf_path = st.session_state.current_pdf_path
        
        with col2:
            # Download button for the PDF
            with open(pdf_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
                st.download_button(
                    label="Download PDF",
                    data=pdf_content,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )
        
        # PDF viewer
        st.subheader("PDF Preview")
        
        # Convert PDF content to base64 for embedded viewing
        if 'current_pdf_content' in st.session_state:
            pdf_base64 = quote_generator.get_quote_as_base64(st.session_state.current_pdf_content)
        else:
            # If PDF content not in session state but file exists, read it
            with open(pdf_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
                st.session_state.current_pdf_content = pdf_content
                pdf_base64 = quote_generator.get_quote_as_base64(pdf_content)
        
        # Display PDF in an iframe
        pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # Email section
        st.subheader("Email Quote")
        
        with st.form(key="email_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                recipient_email = st.text_input("Recipient Email")
                customer_name = st.text_input("Customer Name", value=quote_data.get('customer_name', ''))
            
            with col2:
                subject = st.text_input("Email Subject", 
                                       value=f"Quote {quote_data.get('quote_reference', '')} - Ink Stitch Press")
            
            # Generate default email body
            default_body = email_sender.generate_email_body(quote_data, customer_name)
            email_body = st.text_area("Email Body", value=default_body, height=200)
            
            # Send button
            send_button = st.form_submit_button("Compose Email")
            
            if send_button:
                if not recipient_email:
                    st.error("Please enter a recipient email address.")
                elif not customer_name:
                    st.error("Please enter a customer name.")
                else:
                    # Ensure we have the latest PDF file
                    if not os.path.exists(pdf_path):
                        st.error("PDF file not found. Please generate the quote first.")
                    else:
                        with st.spinner("Preparing email..."):
                            # Send email
                            success, message = email_sender.send_email_with_pdf(
                                recipient_email, 
                                subject, 
                                email_body, 
                                pdf_path,
                                customer_name
                            )
                            
                            if success:
                                st.success(message)
                            else:
                                st.error(message) 