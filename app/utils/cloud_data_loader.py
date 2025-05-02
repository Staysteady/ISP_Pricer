import pandas as pd
import os
import streamlit as st

# Try to import Supabase with error handling
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.error("Supabase library could not be imported. Please install with: pip install supabase==1.0.3 httpx==0.23.3")

class CloudDataLoader:
    def __init__(self):
        """Initialize the cloud data loader with Supabase connection."""
        if not SUPABASE_AVAILABLE:
            st.warning("Running in degraded mode: Supabase connection not available")
            self.supabase = None
            return
            
        self.supabase_url = st.secrets.get("SUPABASE_URL", "")
        self.supabase_key = st.secrets.get("SUPABASE_KEY", "")
        
        # Helpful debugging information
        if not self.supabase_url or not self.supabase_key:
            st.error("Missing Supabase credentials in secrets.toml")
            st.info("Go to the Streamlit Cloud dashboard, click on your app, select 'Settings', and verify your secrets.")
            self.supabase = None
            return
            
        # Check if the key looks like a valid Supabase key
        if not self.supabase_key.startswith("eyJ"):
            st.error("The Supabase key doesn't appear to be valid. It should start with 'eyJ'.")
            self.supabase = None
            return
        
        # Remove the role key check as it's causing false positives
        self.supabase = None
        
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            st.success("Connected to Supabase")
        except Exception as e:
            st.error(f"Failed to connect to Supabase: {str(e)}")
            st.info("Please check your Supabase URL and key in the Streamlit secrets.")
    
    def load_excel_to_db(self, excel_file, sheet_name='Ralawise Price List 2025', skiprows=1):
        """Load the Excel pricing data into Supabase database."""
        try:
            if not self.supabase:
                return False, "Supabase connection not initialized"
                
            # Read Excel file
            st.info(f"Reading Excel file, sheet: {sheet_name}, skiprows: {skiprows}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=skiprows)
            
            # Clean column names
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            
            # Print column names to help with debugging
            st.write(f"Columns in Excel file: {df.columns.tolist()}")
            
            # Print a sample of the data
            st.write("Sample data from Excel file:")
            st.write(df.head(3))
            
            # Delete all existing products
            self.supabase.table('products').delete().execute()
            
            # Convert DataFrame to dict and insert in batches
            records = df.to_dict('records')
            batch_size = 1000
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                self.supabase.table('products').insert(batch).execute()
            
            return True, f"Successfully loaded {len(df)} products from Excel file"
        except Exception as e:
            return False, f"Error loading data: {str(e)}"
    
    def get_unique_values(self, column):
        """Get unique values for a specific column from the database."""
        try:
            if not self.supabase:
                return []
                
            response = self.supabase.rpc(
                'get_unique_values', 
                {'column_name': column}
            ).execute()
            
            if hasattr(response, 'data') and response.data:
                return [item['value'] for item in response.data if item['value'] is not None]
            return []
        except Exception as e:
            st.error(f"Error getting unique values for {column}: {str(e)}")
            return []
    
    def get_filtered_products(self, supplier=None, product_group=None, colours=None, sizes=None):
        """Get products filtered by the selected criteria."""
        try:
            if not self.supabase:
                return pd.DataFrame()
                
            query = self.supabase.table('products').select('*')
            
            if supplier:
                query = query.eq('Supplier', supplier)
            
            if product_group:
                query = query.eq('Product Group', product_group)
            
            if colours and colours != "All":
                # We need to check for exact match or All values
                query = query.or_('Colours.eq.' + colours + ',Colours.eq.All')
                
            if sizes and sizes != "All":
                # Don't use the size value directly in the query to avoid PostgREST parsing issues
                # Instead, retrieve all products that match other criteria and filter in Python
                include_sizes = True
            else:
                include_sizes = False
            
            response = query.execute()
            results_df = pd.DataFrame()
            
            if hasattr(response, 'data'):
                results_df = pd.DataFrame(response.data)
                
                # If we need to filter by size and have results, do the filtering in Python
                if include_sizes and not results_df.empty:
                    # Keep products that have the exact size or "All" size
                    size_mask = (results_df['Sizes'] == sizes) | (results_df['Sizes'] == 'All')
                    results_df = results_df[size_mask]
            
            return results_df
        except Exception as e:
            st.error(f"Error getting filtered products: {str(e)}")
            return pd.DataFrame()
    
    def is_db_initialized(self):
        """Check if the database has been initialized with product data."""
        try:
            if not self.supabase:
                return False
                
            response = self.supabase.table('products').select('count', count='exact').limit(1).execute()
            
            if hasattr(response, 'count'):
                return response.count > 0
            return False
        except Exception as e:
            st.error(f"Error checking if DB is initialized: {str(e)}")
            return False 