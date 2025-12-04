import os
import google.generativeai as genai
from sql_tool import run_select, supabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Unset Google Cloud credentials to force API key usage
os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
os.environ.pop('GCLOUD_PROJECT', None)
os.environ.pop('GOOGLE_CLOUD_PROJECT', None)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

SQL_PROMPT_TEMPLATE = '''
You are an AI assistant that generates safe SQL SELECT queries for a Postgres database.

Tables:
- transactions_income(id, date, item, category, quantity, unit_price, list_price, total_price, customer, service_provider, payment_method, notes, created_at, updated_at)
  * id: uuid (primary key)
  * date: date (required)
  * item: varchar (required, the item/service sold)
  * category: varchar (required)
  * quantity: numeric (required, default 1, must be > 0)
  * unit_price: numeric (required, must be >= 0)
  * list_price: numeric (nullable, must be >= 0 if not null)
  * total_price: numeric (required, must be >= 0)
  * customer: varchar (required)
  * service_provider: varchar (nullable)
  * payment_method: text (nullable)
  * notes: text (nullable)
  * created_at, updated_at: timestamp with time zone

- transactions_expense(id, date, item, category, quantity, unit_price, list_price, total_price, vendor, payment_method, notes, created_at, updated_at)
  * id: uuid (primary key)
  * date: date (required)
  * item: varchar (required, the item/service purchased)
  * category: varchar (required)
  * quantity: numeric (required, default 1, must be > 0)
  * unit_price: numeric (required, must be >= 0)
  * list_price: numeric (required, default 0)
  * total_price: numeric (required, must be >= 0)
  * vendor: varchar (nullable)
  * payment_method: text (nullable)
  * notes: text (nullable)
  * created_at, updated_at: timestamp with time zone

Database Context (use these exact values when filtering by category or payment_method):
{metadata_context}

Constraints:
- Output only a single SQL SELECT statement (no explanation).
- Use table names exactly as above: transactions_income, transactions_expense
- Do not use INSERT/UPDATE/DELETE/DROP/ALTER.
- If date ranges are mentioned, use the `date` column.
- Limit returned rows to 1000 if unsure.
- For income queries, use transactions_income table
- For expense queries, use transactions_expense table
- For combined financial analysis, consider UNION or separate queries
- When filtering by category or payment_method, use the exact values from the Database Context above

User question: """{question}"""

Return just SQL.
'''

SUMMARY_PROMPT_TEMPLATE = '''
You are an assistant summarizing SQL results.
User question: "{question}"
SQL executed:
{sql}
Results (JSON):
{result}

Provide a concise summary in plain language (2-6 short sentences) and highlight up to 3 insights.
'''

def fetch_schema_metadata():
    """
    Fetch available categories and payment methods from the database
    to provide context to the AI for better query generation.
    """
    try:
        # Fetch distinct income categories
        income_categories_sql = "SELECT DISTINCT category FROM transactions_income WHERE category IS NOT NULL ORDER BY category"
        income_categories = run_select(income_categories_sql)
        income_cats = [row['category'] for row in income_categories] if income_categories else []
        
        # Fetch distinct expense categories
        expense_categories_sql = "SELECT DISTINCT category FROM transactions_expense WHERE category IS NOT NULL ORDER BY category"
        expense_categories = run_select(expense_categories_sql)
        expense_cats = [row['category'] for row in expense_categories] if expense_categories else []
        
        # Fetch distinct payment methods from both tables
        payment_methods_sql = """
        SELECT DISTINCT payment_method FROM (
            SELECT payment_method FROM transactions_income WHERE payment_method IS NOT NULL
            UNION
            SELECT payment_method FROM transactions_expense WHERE payment_method IS NOT NULL
        ) AS combined ORDER BY payment_method
        """
        payment_methods = run_select(payment_methods_sql)
        payment_method_list = [row['payment_method'] for row in payment_methods] if payment_methods else []
        
        return {
            "income_categories": income_cats,
            "expense_categories": expense_cats,
            "payment_methods": payment_method_list
        }
    except Exception as e:
        print(f"Warning: Could not fetch schema metadata: {e}")
        return {
            "income_categories": [],
            "expense_categories": [],
            "payment_methods": []
        }

def ai_query_agent(question: str):
    # 0) Fetch schema metadata
    metadata = fetch_schema_metadata()
    
    # Build dynamic context for the prompt
    metadata_context = ""
    if metadata["income_categories"]:
        metadata_context += f"\nIncome Categories: {', '.join(metadata['income_categories'])}"
    if metadata["expense_categories"]:
        metadata_context += f"\nExpense Categories: {', '.join(metadata['expense_categories'])}"
    if metadata["payment_methods"]:
        metadata_context += f"\nPayment Methods: {', '.join(metadata['payment_methods'])}"
    
    # 1) Ask LLM to produce SQL
    prompt = SQL_PROMPT_TEMPLATE.format(question=question, metadata_context=metadata_context)
    sql_resp = model.generate_content(prompt)
    sql = sql_resp.text.strip()
    
    # Remove markdown code blocks if present
    if sql.startswith('```'):
        lines = sql.split('\n')
        # Remove first line (```sql or ```)
        lines = lines[1:]
        # Remove last line (```)
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        sql = '\n'.join(lines).strip()

    # Safety: quick sanitization
    if not sql.lower().startswith('select'):
        return {"error": "LLM-generated SQL not allowed", "generated_sql": sql}

    if ';' in sql:
        # keep only first statement
        sql = sql.split(';')[0]

    # 2) Execute SQL
    try:
        rows = run_select(sql)
        # Convert rows to list of dicts if needed
        if rows and not isinstance(rows, list):
            rows = [rows] if isinstance(rows, dict) else list(rows)
    except Exception as e:
        return {"error": str(e), "generated_sql": sql}

    # 3) Summarize with LLM
    summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(question=question, sql=sql, result=rows)
    summary_resp = model.generate_content(summary_prompt)
    summary = summary_resp.text.strip()

    return {
        "question": question,
        "sql": sql,
        "rows": rows,
        "summary": summary
    }
