import os
import google.generativeai as genai
from sql_tool import run_select
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

Constraints:
- Output only a single SQL SELECT statement (no explanation).
- Use table names exactly as above: transactions_income, transactions_expense
- Do not use INSERT/UPDATE/DELETE/DROP/ALTER.
- If date ranges are mentioned, use the `date` column.
- Limit returned rows to 1000 if unsure.
- For income queries, use transactions_income table
- For expense queries, use transactions_expense table
- For combined financial analysis, consider UNION or separate queries

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

def ai_query_agent(question: str):
    # 1) Ask LLM to produce SQL
    prompt = SQL_PROMPT_TEMPLATE.format(question=question)
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
