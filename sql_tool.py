import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Very small helper to run only safe SELECT queries
ALLOWED_PREFIX = ('select',)

def run_select(sql: str):
    """
    Execute a SELECT query using Supabase RPC function.
    The SQL is executed via a Supabase database function for safety.
    """
    sql = sql.strip()
    if not sql.lower().startswith(ALLOWED_PREFIX):
        raise Exception('Only SELECT queries are allowed')
    
    # Use Supabase RPC to execute raw SQL
    # Note: This requires a database function named 'execute_sql' to be created
    try:
        response = supabase.rpc('execute_sql', {'query': sql}).execute()
        return response.data
    except Exception as e:
        # If RPC function doesn't exist, try using PostgREST query
        error_msg = str(e)
        if 'function' in error_msg.lower() and 'does not exist' in error_msg.lower():
            raise Exception(
                "Database function 'execute_sql' not found. "
                "Please create it in your Supabase database or use direct table queries."
            )
        raise Exception(f"Query execution failed: {error_msg}")
