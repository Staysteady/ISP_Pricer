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
    
    def load_excel_to_db(self, excel_path=None, sheet_name=None, skiprows=0):
        """Load the product data from internal JSON file into SQLite database."""
        try:
            # Use internal JSON file instead of Excel
            json_path = 'app/data/products_data.json'
            
            print(f"Loading product data from internal JSON: {json_path}")
            
            # Check if internal JSON file exists
            if not os.path.exists(json_path):
                return False, f"Internal product data file not found: {json_path}"
            
            # Load data from JSON
            import json
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            df = pd.DataFrame(data['products'])
            
            # Ensure all required columns exist
            required_columns = ['Product Group', 'Brand', 'Price', 'Primary Category', 'Product Name', 'Web Size', 'Colour Name', 'Colour Code']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Missing required columns in internal data: {missing_columns}"
            
            # Remove rows with missing price data
            df = df.dropna(subset=['Price'])
            
            # Print column names to help with debugging
            print(f"Columns in internal data: {df.columns.tolist()}")
            
            # Print metadata info
            metadata = data.get('metadata', {})
            print(f"Data source: {metadata.get('source', 'Unknown')}")
            print(f"Total products: {metadata.get('total_products', len(df))}")
            
            # Print a sample of the data
            print("Sample data from internal JSON:")
            print(df.head(3))
            
            # Create SQLite connection
            conn = sqlite3.connect(self.db_path)
            
            # Clear existing products table and create fresh
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS products')
            conn.commit()
            
            # Save data to SQLite
            df.to_sql('products', conn, if_exists='replace', index=False)
            
            # Create indices for faster queries
            c = conn.cursor()
            c.execute('CREATE INDEX IF NOT EXISTS idx_brand ON products (Brand)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_product_group ON products ("Product Group")')
            c.execute('CREATE INDEX IF NOT EXISTS idx_primary_category ON products ("Primary Category")')
            c.execute('CREATE INDEX IF NOT EXISTS idx_product_name ON products ("Product Name")')
            c.execute('CREATE INDEX IF NOT EXISTS idx_web_size ON products ("Web Size")')
            c.execute('CREATE INDEX IF NOT EXISTS idx_colour_name ON products ("Colour Name")')
            conn.commit()
            conn.close()
            
            return True, f"Successfully loaded {len(df)} products from internal data"
        except Exception as e:
            return False, f"Error loading internal data: {str(e)}"
    
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
    
    def get_filtered_products(self, brand=None, product_group=None, primary_category=None, product_name=None, web_size=None, colour_name=None):
        """Get products filtered by the selected criteria."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = 'SELECT * FROM products WHERE 1=1'
            params = []
            
            if brand:
                query += ' AND Brand = ?'
                params.append(brand)
            
            if product_group:
                query += ' AND "Product Group" = ?'
                params.append(product_group)
            
            if primary_category:
                query += ' AND "Primary Category" = ?'
                params.append(primary_category)
            
            if product_name:
                query += ' AND "Product Name" LIKE ?'
                params.append(f'%{product_name}%')
            
            if web_size:
                # Check if Web Size column exists, fallback to Size Range
                conn_check = sqlite3.connect(self.db_path)
                cursor_check = conn_check.cursor()
                cursor_check.execute("PRAGMA table_info(products)")
                columns = [col[1] for col in cursor_check.fetchall()]
                conn_check.close()
                
                if "Web Size" in columns:
                    query += ' AND "Web Size" = ?'
                    params.append(web_size)
                elif "Size Range" in columns:
                    query += ' AND "Size Range" = ?'
                    params.append(web_size)
            
            if colour_name:
                # Check if Colour Name column exists
                conn_check = sqlite3.connect(self.db_path)
                cursor_check = conn_check.cursor()
                cursor_check.execute("PRAGMA table_info(products)")
                columns = [col[1] for col in cursor_check.fetchall()]
                conn_check.close()
                
                if "Colour Name" in columns:
                    query += ' AND "Colour Name" = ?'
                    params.append(colour_name)
            
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