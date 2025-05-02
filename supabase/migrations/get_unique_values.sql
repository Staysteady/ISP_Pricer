-- Function to get unique values from a specific column
CREATE OR REPLACE FUNCTION get_unique_values(column_name text)
RETURNS TABLE(value text) AS $$
BEGIN
  RETURN QUERY EXECUTE format('
    SELECT DISTINCT %I::text AS value 
    FROM products 
    WHERE %I IS NOT NULL 
    ORDER BY %I::text
  ', column_name, column_name, column_name);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 