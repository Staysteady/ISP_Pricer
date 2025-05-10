-- Create a function to check if a column exists in a table
CREATE OR REPLACE FUNCTION check_column_exists(table_name TEXT, column_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    column_exists BOOLEAN;
BEGIN
    -- Check if the column exists in the table
    SELECT COUNT(*) > 0 INTO column_exists
    FROM information_schema.columns
    WHERE table_name = check_column_exists.table_name
    AND column_name = check_column_exists.column_name
    AND table_schema = 'public';
    
    RETURN column_exists;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 