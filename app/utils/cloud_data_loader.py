import pandas as pd
import os
import streamlit as st
import io

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
    
    def load_excel_to_db(self, excel_file=None, sheet_name='Customer_Specific_Pricing_Stand', skiprows=0):
        """Load the Excel pricing data into Supabase database."""
        try:
            if not self.supabase:
                return False, "Supabase connection not initialized"
            
            # Use internal JSON file instead of Excel
            if excel_file is None:
                json_path = 'app/data/products_data.json'
                st.info(f"Loading product data from internal JSON: {json_path}")
                
                # Check if internal JSON file exists
                if not os.path.exists(json_path):
                    return False, f"Internal product data file not found: {json_path}"
                
                # Load data from JSON
                import json
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                # Convert to DataFrame
                df = pd.DataFrame(data['products'])
                
                # Print metadata info
                metadata = data.get('metadata', {})
                st.write(f"Data source: {metadata.get('source', 'Unknown')}")
                st.write(f"Total products: {metadata.get('total_products', len(df))}")
            else:
                # Handle uploaded Excel files (fallback)
                st.info(f"Reading uploaded Excel file, sheet: {sheet_name}")
                
                # Handle both file paths and bytes
                if isinstance(excel_file, str):
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1)
                else:
                    # Wrap bytes in BytesIO to avoid warning
                    if isinstance(excel_file, bytes):
                        excel_file = io.BytesIO(excel_file)
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1)
                
                # Select only the required columns
                required_columns = ['Product Group', 'Brand', 'Cust Single Price', 'Primary Category', 'Product Name', 'Size Range']
                
                # Check if all required columns exist
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return False, f"Missing required columns: {missing_columns}"
                
                # Select only the required columns
                df = df[required_columns].copy()
                
                # Rename 'Cust Single Price' to 'Price' for consistency
                df.rename(columns={'Cust Single Price': 'Price'}, inplace=True)
            
            # Ensure all required columns exist
            required_columns = ['Product Group', 'Brand', 'Price', 'Primary Category', 'Product Name', 'Size Range']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Missing required columns in data: {missing_columns}"
            
            # Clean column names
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            
            # Remove rows with missing price data
            df = df.dropna(subset=['Price'])
            
            # Print column names to help with debugging
            st.write(f"Columns in processed data: {df.columns.tolist()}")
            
            # Print a sample of the data
            st.write("Sample data:")
            st.write(df.head(3))
            
            # Delete all existing products
            try:
                # Use a WHERE clause that matches all records
                self.supabase.table('products').delete().eq('id', 'id').execute()
            except Exception as e:
                # If that fails, try with a different approach
                try:
                    self.supabase.table('products').delete().neq('id', 0).execute()
                except Exception as e2:
                    st.warning(f"Could not delete existing products: {str(e2)}")
            
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
    
    def get_filtered_products(self, brand=None, product_group=None, primary_category=None, product_name=None):
        """Get products filtered by the selected criteria."""
        try:
            if not self.supabase:
                return pd.DataFrame()
                
            query = self.supabase.table('products').select('*')
            
            if brand:
                query = query.eq('Brand', brand)
            
            if product_group:
                query = query.eq('Product Group', product_group)
            
            if primary_category:
                query = query.eq('Primary Category', primary_category)
            
            if product_name:
                query = query.ilike('Product Name', f'%{product_name}%')
            
            # Execute the query
            response = query.execute()
            results_df = pd.DataFrame()
            
            if hasattr(response, 'data'):
                results_df = pd.DataFrame(response.data)
            
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