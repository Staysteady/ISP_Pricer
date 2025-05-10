-- Create a function to get distinct values for a given column in the products table
-- This is used by the CloudDataLoader to populate dropdown options
CREATE OR REPLACE FUNCTION get_unique_values(column_name TEXT)
RETURNS TABLE(value TEXT) AS $$
BEGIN
    -- Validate input to prevent SQL injection
    IF column_name IS NULL OR column_name = '' THEN
        RAISE EXCEPTION 'Invalid column name';
    END IF;

    -- Try to get distinct values from the specified column
    RETURN QUERY EXECUTE format(
        'SELECT DISTINCT "%s"::TEXT as value FROM products WHERE "%s" IS NOT NULL ORDER BY "%s"',
        column_name, column_name, column_name
    );
    
    -- If there are no results, return an empty set
    IF NOT FOUND THEN
        RETURN;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 