# Database Migrations

This directory contains SQL scripts for setting up and maintaining the database schema for the InkStitchPress Pricer application.

## Directory Structure

- **schema/**: Contains current table definitions
  - `create_products_table_fixed.sql`: Product catalog table
  - `create_business_costs_table.sql`: Business costs tracking
  - `create_cost_categories_table.sql`: Cost categories
  - `create_electricity_costs_table.sql`: Electricity cost tracking
  - `create_material_costs_table.sql`: Material cost tracking

- **functions/**: Contains utility database functions
  - `create_check_column_exists_function.sql`: Helper function to check if a column exists
  - `get_unique_values.sql`: Function to extract unique values from a column

- **deprecated/**: Contains obsolete migration scripts (kept for reference)
  - `create_products_table.sql`: Original products table definition (superseded by fixed version)
  - `fix_single_price_column.sql`: One-time migration script
  - `update_products_table_for_single_prices.sql`: One-time migration script
  - `drop_all_tables.sql`: Emergency reset script (use with caution)

## Setup Instructions

To set up a fresh database:

1. Execute scripts in the schema directory to create the base tables
2. Execute scripts in the functions directory to add utility functions

Note: Scripts in the deprecated directory should not be run on new installations. 