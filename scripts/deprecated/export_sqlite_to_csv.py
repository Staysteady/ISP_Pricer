#!/usr/bin/env python3
"""
Utility script to export data from SQLite database to CSV files
for easy import into Supabase or other database systems.
"""

import os
import sqlite3
import pandas as pd
import argparse

def export_sqlite_to_csv(db_path, output_dir):
    """
    Export all tables from SQLite database to CSV files.
    
    Args:
        db_path (str): Path to SQLite database file
        output_dir (str): Directory to save CSV files
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    
    # Get list of tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables in database")
    
    # Export each table to CSV
    for table in tables:
        table_name = table[0]
        output_file = os.path.join(output_dir, f"{table_name}.csv")
        
        print(f"Exporting table '{table_name}' to {output_file}")
        
        # Read table data into DataFrame
        df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        print(f"Exported {len(df)} rows")
    
    conn.close()
    print("Export complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export SQLite database to CSV files")
    parser.add_argument("--db", default="app/data/pricer.db", help="Path to SQLite database file")
    parser.add_argument("--output", default="exports", help="Output directory for CSV files")
    
    args = parser.parse_args()
    
    export_sqlite_to_csv(args.db, args.output)
    
    print(f"""
Next steps for Supabase migration:
1. Go to your Supabase project: https://app.supabase.com/project/_/editor
2. Create the required tables using the SQL migrations
3. Import the CSV files using the Table Editor
""") 