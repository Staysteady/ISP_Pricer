-- Create products table for ISP_Pricer app
CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  "Supplier" TEXT,
  "Product Group" TEXT,
  "Style No" TEXT,
  "Colours" TEXT,
  "Sizes" TEXT,
  "Price (£)" NUMERIC(10,2),
  "Description" TEXT,
  "Type" TEXT,
  "Material" TEXT,
  "Weight (g)" NUMERIC(10,2),
  "Brand" TEXT,
  "Gender" TEXT,
  "Created At" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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