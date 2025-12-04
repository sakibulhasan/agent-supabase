-- Execute this SQL in your Supabase SQL Editor to enable raw SQL execution
-- This creates a function that the Python agent can call via RPC

CREATE OR REPLACE FUNCTION execute_sql(query text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result json;
BEGIN
    -- Only allow SELECT statements
    IF lower(trim(query)) NOT LIKE 'select%' THEN
        RAISE EXCEPTION 'Only SELECT queries are allowed';
    END IF;
    
    -- Execute the query and return results as JSON
    EXECUTE 'SELECT json_agg(row_to_json(t)) FROM (' || query || ') t'
    INTO result;
    
    -- Return empty array if no results
    IF result IS NULL THEN
        result := '[]'::json;
    END IF;
    
    RETURN result;
END;
$$;

-- Grant execute permission to anon and authenticated users
GRANT EXECUTE ON FUNCTION execute_sql(text) TO anon, authenticated;

-- Optional: Add comment for documentation
COMMENT ON FUNCTION execute_sql(text) IS 'Executes a SELECT query and returns results as JSON. Only SELECT statements are allowed for security.';
