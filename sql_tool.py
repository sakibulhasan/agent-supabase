import os
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration (optional - for future use)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Initialize Supabase client if credentials are available
supabase = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")

# Very small helper to run only safe SELECT queries
ALLOWED_PREFIX = ('select',)

def run_select(sql: str):
    sql = sql.strip()
    if not sql.lower().startswith(ALLOWED_PREFIX):
        raise Exception('Only SELECT queries are allowed')

    # Use psycopg2 for raw SQL queries
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DB_URL = os.getenv('SUPABASE_DB_URL')
    if not DB_URL:
        raise ValueError("SUPABASE_DB_URL must be set for raw SQL queries")
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
