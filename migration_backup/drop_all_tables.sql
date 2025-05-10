-- Drop all existing tables if they exist
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS business_costs CASCADE;
DROP TABLE IF EXISTS cost_categories CASCADE;
DROP TABLE IF EXISTS electricity_costs CASCADE;
DROP TABLE IF EXISTS material_costs CASCADE;

-- Drop functions if they exist
DROP FUNCTION IF EXISTS get_unique_values(text); 