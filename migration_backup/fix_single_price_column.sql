-- Fix the products table schema for ISP_Pricer app
-- This script completely recreates the products table with the correct column names

-- Drop existing table if it exists
DROP TABLE IF EXISTS products;

-- Create products table with proper column definitions
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  "Supplier" TEXT,
  "Style No" TEXT,
  "Product Group" TEXT,
  "Colours" TEXT,
  "Sizes" TEXT,
  "Single Price (£)" NUMERIC(10,2),
  "Created At" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_supplier ON products ("Supplier");
CREATE INDEX idx_style_no ON products ("Style No");
CREATE INDEX idx_product_group ON products ("Product Group");
CREATE INDEX idx_colours ON products ("Colours");
CREATE INDEX idx_sizes ON products ("Sizes");
CREATE INDEX idx_single_price ON products ("Single Price (£)");

-- Enable Row Level Security
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (will be secured by Supabase API keys)
CREATE POLICY "Enable all operations for authenticated users" ON products
  FOR ALL USING (true); 