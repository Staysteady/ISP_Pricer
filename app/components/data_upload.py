import streamlit as st
import os
import tempfile
import pandas as pd

def data_upload(data_loader):
    """
    Component for uploading and processing a new price list.
    
    Args:
        data_loader: Instance of DataLoader to process the uploaded file
    """
    st.subheader("Update Price List")
    
    # Check if we're in cloud mode
    is_cloud = 'STREAMLIT_SHARING' in os.environ or 'DEPLOYED' in os.environ or st.secrets.get('DEPLOYED', False)
    
    # Upload file
    uploaded_file = st.file_uploader(
        "Upload new price list Excel file", 
        type=["xlsx", "xls"],
        help="Upload a new price list to replace the current one."
    )
    
    if uploaded_file is not None:
        # For local mode, save to temp file
        if not is_cloud:
            # Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # For preview, use the temp file path
            preview_file = tmp_file_path
        else:
            # For cloud mode, use the uploaded file directly
            preview_file = uploaded_file
            
        # Show Excel file info
        with st.expander("Excel File Information", expanded=True):
            try:
                # List sheets in the Excel file
                excel = pd.ExcelFile(preview_file)
                st.write("Sheets in the Excel file:")
                for i, sheet in enumerate(excel.sheet_names):
                    st.write(f"{i+1}. {sheet}")
                
                # Allow user to select sheet to preview
                preview_sheet = st.selectbox(
                    "Select a sheet to preview", 
                    excel.sheet_names,
                    index=0
                )
                
                # Show preview of selected sheet
                preview_rows = st.slider("Number of preview rows", 3, 10, 5)
                df_preview = pd.read_excel(preview_file, sheet_name=preview_sheet, nrows=preview_rows)
                st.write(f"Preview of '{preview_sheet}' sheet:")
                st.dataframe(df_preview)
                
                # Show column names
                st.write("Column names in the selected sheet:")
                st.write(df_preview.columns.tolist())
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")
        
        # Options for sheet selection and header rows
        st.write("Please configure the import settings:")
        
        col1, col2 = st.columns(2)
        with col1:
            sheet_name = st.text_input("Sheet Name", "Ralawise Price List 2025")
        
        with col2:
            skip_rows = st.number_input("Header Rows to Skip", min_value=0, value=1)
        
        # Process the file when button is clicked
        if st.button("Process Price List"):
            with st.spinner("Processing price list..."):
                if is_cloud:
                    # For cloud mode, pass the file directly
                    success, message = data_loader.load_excel_to_db(
                        uploaded_file, 
                        sheet_name=sheet_name,
                        skiprows=skip_rows
                    )
                else:
                    # For local mode, use the file path
                    success, message = data_loader.load_excel_to_db(
                        tmp_file_path, 
                        sheet_name=sheet_name,
                        skiprows=skip_rows
                    )
                    
                    # Clean up the temporary file
                    try:
                        os.unlink(tmp_file_path)
                    except Exception:
                        pass
                
                if success:
                    st.success(message)
                    
                    # Display found data categories
                    with st.expander("Data Categories Found", expanded=True):
                        st.write("Suppliers:", len(data_loader.get_unique_values("Supplier")))
                        st.write("Product Groups:", len(data_loader.get_unique_values("Product Group")))
                        st.write("Colors:", len(data_loader.get_unique_values("Colours")))
                        st.write("Sizes:", len(data_loader.get_unique_values("Sizes")))
                    
                    st.session_state.initialized_db = True
                else:
                    st.error(message) 