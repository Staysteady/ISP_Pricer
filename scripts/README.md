# Utility Scripts

This directory contains utility scripts for the InkStitchPress Pricer application.

## Available Scripts

- **load_new_price_list.py**: Utility to load a new price list Excel file into the database
  - Usage: `python scripts/load_new_price_list.py`
  - Requires a properly formatted Excel file (see script for details)

## Deprecated Scripts

The `deprecated` directory contains scripts that were used for one-time operations or migrations and are kept for reference:

- **export_sqlite_to_csv.py**: Tool for exporting SQLite data to CSV files for migration to Supabase
  - Only needed if migrating from SQLite to Supabase 