-- Create electricity_costs table for ISP_Pricer app
CREATE TABLE IF NOT EXISTS electricity_costs (
  id SERIAL PRIMARY KEY,
  process_type TEXT,
  process_name TEXT,
  avg_time_min NUMERIC(10,2),
  cost_per_unit_kwh NUMERIC(10,4),
  machine_watts INTEGER,
  usage_w NUMERIC(10,2),
  cost_per_run NUMERIC(10,4),
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_electricity_costs_process_type ON electricity_costs (process_type);
CREATE INDEX IF NOT EXISTS idx_electricity_costs_process_name ON electricity_costs (process_name);

-- Enable Row Level Security
ALTER TABLE electricity_costs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (will be secured by Supabase API keys)
CREATE POLICY "Enable all operations for authenticated users" ON electricity_costs
  FOR ALL USING (true); 