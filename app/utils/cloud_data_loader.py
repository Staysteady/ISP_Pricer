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
    
    def load_excel_to_db(self, excel_file, sheet_name='Ralawise Price List 2025', skiprows=1):
        """Load the Excel pricing data into Supabase database."""
        try:
            if not self.supabase:
                return False, "Supabase connection not initialized"
                
            # Read Excel file
            st.info(f"Reading Excel file, sheet: {sheet_name}, skiprows: {skiprows}")
            
            # Wrap bytes in BytesIO to avoid warning
            if isinstance(excel_file, bytes):
                excel_file = io.BytesIO(excel_file)
            
            df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=skiprows)
            
            # Clean column names
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            
            # Print column names to help with debugging
            st.write(f"Columns in Excel file: {df.columns.tolist()}")
            
            # Print a sample of the data
            st.write("Sample data from Excel file:")
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
                # We can't use 'or_' as it's not available in the cloud environment
                # Let's use two separate queries and combine the results
                try:
                    # First, get products that exactly match the colour
                    exact_match_query = self.supabase.table('products').select('*')
                    if supplier:
                        exact_match_query = exact_match_query.eq('Supplier', supplier)
                    if product_group:
                        exact_match_query = exact_match_query.eq('Product Group', product_group)
                    exact_match_query = exact_match_query.eq('Colours', colours)
                    
                    # Then, get products with 'All' colours
                    all_colours_query = self.supabase.table('products').select('*')
                    if supplier:
                        all_colours_query = all_colours_query.eq('Supplier', supplier)
                    if product_group:
                        all_colours_query = all_colours_query.eq('Product Group', product_group)
                    all_colours_query = all_colours_query.eq('Colours', 'All')
                    
                    # Execute both queries
                    exact_match_response = exact_match_query.execute()
                    all_colours_response = all_colours_query.execute()
                    
                    # Combine results
                    exact_match_df = pd.DataFrame(exact_match_response.data) if hasattr(exact_match_response, 'data') else pd.DataFrame()
                    all_colours_df = pd.DataFrame(all_colours_response.data) if hasattr(all_colours_response, 'data') else pd.DataFrame()
                    
                    combined_df = pd.concat([exact_match_df, all_colours_df], ignore_index=True)
                    
                    # Continue with size filtering if needed
                    if sizes and sizes != "All" and not combined_df.empty:
                        # Filter by size in Python
                        size_mask = (combined_df['Sizes'] == sizes) | (combined_df['Sizes'] == 'All')
                        return combined_df[size_mask]
                    
                    return combined_df
                except Exception as e:
                    st.error(f"Error in colour filtering: {str(e)}")
                    # Fall back to base query without colour filtering
                    pass
            
            # If we didn't handle colours with the special case above or if that failed, continue with the original query
            
            # Execute the query
            response = query.execute()
            results_df = pd.DataFrame()
            
            if hasattr(response, 'data'):
                results_df = pd.DataFrame(response.data)
                
                # If we need to filter by size and have results, do the filtering in Python
                if sizes and sizes != "All" and not results_df.empty:
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