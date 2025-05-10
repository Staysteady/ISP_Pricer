-- Create business_costs table for ISP_Pricer app
CREATE TABLE IF NOT EXISTS business_costs (
  id SERIAL PRIMARY KEY,
  category_id INTEGER,
  name TEXT,
  description TEXT,
  cost_value NUMERIC(10,2),
  cost_type TEXT,
  date_incurred DATE,
  recurring_period TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_business_costs_category ON business_costs (category_id);
CREATE INDEX IF NOT EXISTS idx_business_costs_date ON business_costs (date_incurred);

-- Enable Row Level Security
ALTER TABLE business_costs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (will be secured by Supabase API keys)
CREATE POLICY "Enable all operations for authenticated users" ON business_costs
  FOR ALL USING (true); 