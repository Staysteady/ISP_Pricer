-- Create material_costs table for ISP_Pricer app
CREATE TABLE IF NOT EXISTS material_costs (
  id SERIAL PRIMARY KEY,
  material_type TEXT,
  material_name TEXT,
  cost_per_unit NUMERIC(10,4),
  unit_measurement TEXT,
  unit_value NUMERIC(10,2),
  logo_size TEXT,
  cost_per_logo NUMERIC(10,4),
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_material_costs_material_type ON material_costs (material_type);
CREATE INDEX IF NOT EXISTS idx_material_costs_material_name ON material_costs (material_name);

-- Enable Row Level Security
ALTER TABLE material_costs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (will be secured by Supabase API keys)
CREATE POLICY "Enable all operations for authenticated users" ON material_costs
  FOR ALL USING (true); 