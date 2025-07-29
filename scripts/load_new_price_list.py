#!/usr/bin/env python3
"""
Script to load the new price list data into the database.
This script can be run directly from the command line.
"""

import os
import sys
import pandas as pd
import io
import sqlite3

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force using the local data loader to avoid Streamlit issues
print("Using local data loader...")
from app.utils.data_loader import DataLoader

def main():
    """Load the new price list data into the database."""
    print("Loading new price list data...")
    
    # Use internal JSON data instead of Excel file
    json_data_file = 'app/data/products_data.json'
    
    if not os.path.exists(json_data_file):
        print(f"Error: Internal product data file '{json_data_file}' not found.")
        return 1
    
    # Ensure the database directory exists
    db_path = 'app/data/pricer.db'
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Initialize the data loader
    data_loader = DataLoader(db_path)
    
    try:
        # Load directly from JSON to verify the file is readable
        print(f"Verifying JSON data file: {json_data_file}")
        import json
        with open(json_data_file, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data['products'])
        metadata = data.get('metadata', {})
        print(f"JSON data is valid. Found {len(df)} products")
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Load the data
        print("Loading data into database...")
        success, message = data_loader.load_excel_to_db()
        
        if success:
            print(f"Success: {message}")
            
            # Verify data was loaded
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            conn.close()
            
            print(f"Verified {count} products in database")
            return 0
        else:
            print(f"Error: {message}")
            return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 