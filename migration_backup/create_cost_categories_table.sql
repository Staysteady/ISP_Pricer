-- Create cost_categories table for ISP_Pricer app
CREATE TABLE IF NOT EXISTS cost_categories (
  id SERIAL PRIMARY KEY,
  name TEXT,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cost_categories_name ON cost_categories (name);

-- Enable Row Level Security
ALTER TABLE cost_categories ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (will be secured by Supabase API keys)
CREATE POLICY "Enable all operations for authenticated users" ON cost_categories
  FOR ALL USING (true); 