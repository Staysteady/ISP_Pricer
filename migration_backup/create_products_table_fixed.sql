-- Create products table for ISP_Pricer app with columns matching the CSV
CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  "Supplier" TEXT,
  "Style No" TEXT,
  "Product Group" TEXT,
  "Colours" TEXT,
  "Sizes" TEXT,
  "Qty" INTEGER,
  "Price (£)" NUMERIC(10,2),
  "Qty.1" INTEGER,
  "Price (£).1" NUMERIC(10,2),
  "Price (£).2" NUMERIC(10,2)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_supplier ON products ("Supplier");
CREATE INDEX IF NOT EXISTS idx_product_group ON products ("Product Group");
CREATE INDEX IF NOT EXISTS idx_colours ON products ("Colours");
CREATE INDEX IF NOT EXISTS idx_sizes ON products ("Sizes");

-- Enable Row Level Security
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (will be secured by Supabase API keys)
CREATE POLICY "Enable all operations for authenticated users" ON products
  FOR ALL USING (true); 