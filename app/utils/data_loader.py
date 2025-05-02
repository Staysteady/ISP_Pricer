import pandas as pd
import os
import sqlite3
from pathlib import Path

class DataLoader:
    def __init__(self, db_path='app/data/pricer.db'):
        """Initialize the data loader with the database path."""
        self.db_path = db_path
        self._ensure_db_directory()
        
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def load_excel_to_db(self, excel_path, sheet_name='Ralawise Price List 2025', skiprows=1):
        """Load the Excel pricing data into SQLite database."""
        try:
            # Read Excel file
            print(f"Reading Excel file: {excel_path}, sheet: {sheet_name}, skiprows: {skiprows}")
            df = pd.read_excel(excel_path, sheet_name=sheet_name, skiprows=skiprows)
            
            # Clean column names
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            
            # Print column names to help with debugging
            print(f"Columns in Excel file: {df.columns.tolist()}")
            
            # Print a sample of the data
            print("Sample data from Excel file:")
            print(df.head(3))
            
            # Create SQLite connection
            conn = sqlite3.connect(self.db_path)
            
            # Save data to SQLite
            df.to_sql('products', conn, if_exists='replace', index=False)
            
            # Create indices for faster queries
            c = conn.cursor()
            c.execute('CREATE INDEX IF NOT EXISTS idx_supplier ON products (Supplier)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_product_group ON products ("Product Group")')
            c.execute('CREATE INDEX IF NOT EXISTS idx_colours ON products (Colours)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_sizes ON products (Sizes)')
            conn.commit()
            conn.close()
            
            return True, f"Successfully loaded {len(df)} products from {excel_path}"
        except Exception as e:
            return False, f"Error loading data: {str(e)}"
    
    def get_unique_values(self, column):
        """Get unique values for a specific column from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            query = f'SELECT DISTINCT "{column}" FROM products WHERE "{column}" IS NOT NULL ORDER BY "{column}"'
            values = pd.read_sql_query(query, conn).iloc[:, 0].tolist()
            conn.close()
            return values
        except Exception as e:
            print(f"Error getting unique values for {column}: {str(e)}")
            return []
    
    def get_filtered_products(self, supplier=None, product_group=None, colours=None, sizes=None):
        """Get products filtered by the selected criteria."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = 'SELECT * FROM products WHERE 1=1'
            params = []
            
            if supplier:
                query += ' AND Supplier = ?'
                params.append(supplier)
            
            if product_group:
                query += ' AND "Product Group" = ?'
                params.append(product_group)
            
            if colours:
                # Allow for 'All' or exact match
                query += ' AND (Colours = ? OR Colours = "All" OR Colours LIKE "%All%" OR ? = "All")'
                params.append(colours)
                params.append(colours)
            
            if sizes:
                # Allow for 'All' or exact match or ranges that might include the size
                query += ' AND (Sizes = ? OR Sizes = "All" OR Sizes LIKE "%All%" OR ? = "All" OR Sizes LIKE "%-%")'
                params.append(sizes)
                params.append(sizes)
            
            print(f"SQL Query: {query}")
            print(f"Parameters: {params}")
            
            df = pd.read_sql_query(query, conn, params=params)
            print(f"Query returned {len(df)} rows")
            
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting filtered products: {str(e)}")
            return pd.DataFrame()
    
    def is_db_initialized(self):
        """Check if the database has been initialized with product data."""
        if not os.path.exists(self.db_path):
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='products'")
            result = cursor.fetchone()[0]
            
            if result > 0:
                # Also check if there are any products
                cursor.execute("SELECT count(*) FROM products")
                product_count = cursor.fetchone()[0]
                conn.close()
                return product_count > 0
            
            conn.close()
            return False
        except Exception as e:
            print(f"Error checking if DB is initialized: {str(e)}")
            return False 