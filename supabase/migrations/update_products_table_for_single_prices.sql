-- Update products table for ISP_Pricer app to handle new single price format
ALTER TABLE products RENAME COLUMN "Price (£)" TO "Single Price (£)";

-- In case the table was created with the old schema but doesn't have data yet, modify the columns
ALTER TABLE products DROP COLUMN IF EXISTS "Description";
ALTER TABLE products DROP COLUMN IF EXISTS "Type";
ALTER TABLE products DROP COLUMN IF EXISTS "Material";
ALTER TABLE products DROP COLUMN IF EXISTS "Weight (g)";
ALTER TABLE products DROP COLUMN IF EXISTS "Brand";
ALTER TABLE products DROP COLUMN IF EXISTS "Gender";

-- Create an index for the new price column if it doesn't exist yet
CREATE INDEX IF NOT EXISTS idx_single_price ON products ("Single Price (£)");

-- Create index for style number for faster lookups
CREATE INDEX IF NOT EXISTS idx_style_no ON products ("Style No");

-- Keep row level security enabled
-- The policy for all operations should already exist 