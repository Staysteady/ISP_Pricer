import pandas as pd
import os
import streamlit as st
from supabase import create_client, Client

class CloudDataLoader:
    def __init__(self):
        """Initialize the cloud data loader with Supabase connection."""
        self.supabase_url = st.secrets.get("SUPABASE_URL", "")
        self.supabase_key = st.secrets.get("SUPABASE_KEY", "")
        self.supabase = None
        
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
    
    def load_excel_to_db(self, excel_file, sheet_name='Ralawise Price List 2025', skiprows=1):
        """Load the Excel pricing data into Supabase database."""
        try:
            if not self.supabase:
                return False, "Supabase connection not initialized"
                
            # Read Excel file
            print(f"Reading Excel file, sheet: {sheet_name}, skiprows: {skiprows}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=skiprows)
            
            # Clean column names
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            
            # Print column names to help with debugging
            print(f"Columns in Excel file: {df.columns.tolist()}")
            
            # Print a sample of the data
            print("Sample data from Excel file:")
            print(df.head(3))
            
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
            print(f"Error getting unique values for {column}: {str(e)}")
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
                query = query.or_(f"Colours.eq.{colours},Colours.like.%All%,Colours.eq.All")
            
            if sizes and sizes != "All":
                query = query.or_(f"Sizes.eq.{sizes},Sizes.like.%All%,Sizes.eq.All,Sizes.like.%-%-")
            
            response = query.execute()
            
            if hasattr(response, 'data'):
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting filtered products: {str(e)}")
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
            print(f"Error checking if DB is initialized: {str(e)}")
            return False 