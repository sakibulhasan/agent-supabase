# AI Supabase Agent

A FastAPI backend service that converts natural language questions into SQL queries, executes them against a Supabase database, and returns AI-generated insights.

## Overview

This intelligent agent bridges the gap between business users and databases by allowing anyone to ask questions in plain English and get instant answers with actionable insights. Perfect for financial analysis, reporting, and data exploration without writing SQL.

### Key Features

- 🤖 **Natural Language to SQL**: Ask questions in plain English, get precise SQL queries
- 🧠 **AI-Powered**: Uses Google Gemini 2.0 Flash for query generation and result summarization
- 📊 **Context-Aware**: Dynamically fetches available categories and payment methods from your database
- 🔒 **Safe Execution**: Only SELECT queries allowed, prevents data modification
- 📈 **Insightful Analysis**: Automatically generates 2-6 key insights from query results
- 🚀 **Production Ready**: CORS-enabled, auto-deploys via Render.com
- ⚡ **Fast**: Efficient batch processing and connection pooling

---

## 🏗️ Architecture & Functional Flow

```
User Question (Natural Language)
        ↓
[1] Fetch Schema Metadata
    - Available categories
    - Payment methods
    - Dynamic context
        ↓
[2] AI Query Generation (Gemini)
    - Convert question to SQL
    - Use exact database values
    - Apply safety checks
        ↓
[3] SQL Execution (Supabase)
    - Execute via RPC function
    - Return structured data
        ↓
[4] AI Summarization (Gemini)
    - Generate human-readable summary
    - Extract 2-3 key insights
        ↓
JSON Response
{
  "question": "...",
  "sql": "SELECT ...",
  "rows": [...],
  "summary": "..."
}
```

### Database Schema

The agent works with two main transaction tables:

**`transactions_income`**
- Vehicle Sales, Service Revenue, Parts Sales
- Tracks: item, category, customer, service_provider, payment_method, total_price

**`transactions_expense`**
- Operating expenses and purchases
- Tracks: item, category, vendor, payment_method, total_price

---

## 🚀 Quick Start - Local Development

### Prerequisites
- Python 3.11+
- Supabase account with database
- Google Gemini API key

### 1. Clone and Setup

```bash
git clone https://github.com/sakibulhasan/agent-supabase.git
cd agent-supabase
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

**Where to get credentials:**
- **Supabase URL & Key**: Supabase Dashboard → Settings → API
- **Gemini API Key**: https://makersuite.google.com/app/apikey

### 3. Setup Database Function

Run `supabase_setup.sql` in your Supabase SQL Editor:

```bash
# Copy contents of supabase_setup.sql and execute in:
# Supabase Dashboard → SQL Editor → New Query
```

This creates the `execute_sql()` function that the agent uses to run queries safely.

### 4. Generate Sample Data (Optional)

```bash
python data/generate_avondale_data.py
```

This will populate your database with ~4,700 sample transactions (income & expenses).

### 5. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Server starts at: **http://localhost:8080**

### 6. Test the API

```bash
# Health check
curl http://localhost:8080/

# Ask a question
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total revenue in 2024?"}'
```

---

## 🌐 Deploy to Render.com (with Auto CI/CD)

### Prerequisites
- GitHub account
- Render.com account (free signup at https://render.com)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Connect Render to GitHub

1. Go to https://render.com
2. Click **"Get Started"** → **"Sign up with GitHub"**
3. Authorize Render to access your repositories

### Step 3: Create Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Find and click **"Connect"** on `agent-supabase` repository
3. Render auto-detects settings from `render.yaml` ✨

### Step 4: Add Environment Variables

In the Render dashboard, add these environment variables:

| Key | Value |
|-----|-------|
| `SUPABASE_URL` | `https://your-project.supabase.co` |
| `SUPABASE_ANON_KEY` | Your Supabase anonymous key |
| `GEMINI_API_KEY` | Your Google Gemini API key |

### Step 5: Deploy!

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. Your API will be live at: `https://your-app-name.onrender.com`

### 🔄 Automatic Deployments (CI/CD)

**It's already configured!** Every time you push to `main` branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
# → Render automatically detects and deploys! 🎉
```

No GitHub Actions needed - Render monitors your repository automatically.

---

## 📡 API Usage

### Endpoints

#### `GET /`
Health check endpoint
```bash
curl https://agent-supabase.onrender.com/
```
**Response:**
```json
{
  "status": "ok",
  "service": "AI Supabase Agent",
  "endpoints": {
    "health": "GET /",
    "ask": "POST /ask",
    "ask_info": "GET /ask"
  }
}
```

#### `POST /ask`
Submit a natural language question
```bash
curl -X POST https://agent-supabase.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top 5 customers by spending?"}'
```

**Response:**
```json
{
  "question": "What are the top 5 customers by spending?",
  "sql": "SELECT customer, SUM(total_price) AS total_spending FROM transactions_income GROUP BY customer ORDER BY total_spending DESC LIMIT 5",
  "rows": [
    {"customer": "Sophia Martinez", "total_spending": 40237616},
    {"customer": "James Anderson", "total_spending": 36101420}
  ],
  "summary": "The top 5 customers by total spending are...\n\n**Insights:**\n* Sophia Martinez leads with $40.2M\n* Top 5 customers represent significant revenue concentration"
}
```

#### `GET /ask`
Get API usage information
```bash
curl https://agent-supabase.onrender.com/ask
```

### Example Questions

**Financial Analysis:**
- "What is the total revenue in 2024?"
- "Compare income vs expenses for 2023"
- "Show monthly revenue trend for 2025"

**Category Analysis:**
- "What is revenue from vehicle sales vs service revenue?"
- "Show me all income categories with their totals"
- "What are the most common service items sold?"

**Customer Insights:**
- "Who are the top 5 customers by spending?"
- "Show me all transactions for Alice Johnson"

**Payment Analysis:**
- "What payment methods are used most frequently?"
- "Show credit card transactions over $100,000"

---

## 🛠️ Project Structure

```
agent-supabase/
├── main.py                  # FastAPI application
├── agent.py                 # AI agent logic & query generation
├── sql_tool.py             # Supabase connection & query execution
├── requirements.txt        # Python dependencies
├── render.yaml            # Render.com deployment config
├── supabase_setup.sql     # Database function setup
├── data/
│   └── generate_avondale_data.py  # Sample data generator
├── .env                   # Environment variables (local only)
└── README.md              # This file
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Supabase anonymous/public key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `PORT` | Server port (auto-set by Render) | No (default: 8080) |

### Render.com Configuration

The `render.yaml` file contains:
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Auto-deploy**: Enabled from `main` branch
- **Health check**: `GET /`

---

## 📊 Monitoring & Troubleshooting

### Render Dashboard
- View logs: Dashboard → Your Service → Logs
- Monitor deployments: Dashboard → Your Service → Events
- Check metrics: Dashboard → Your Service → Metrics

### Common Issues

**405 Error when accessing `/ask` in browser:**
- `/ask` requires POST method
- Use `GET /ask` for usage information
- Use API tools (curl, Postman) for POST requests

**Query execution fails:**
- Ensure `supabase_setup.sql` was executed
- Check that `execute_sql()` function exists in database
- Verify Supabase credentials in environment variables

**Slow first response on Render:**
- Free tier sleeps after 15 min inactivity
- First request takes ~30 seconds to wake up
- Upgrade to paid plan for always-on service

---

## 💰 Render.com Free Tier

- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ✅ Automatic deployments from GitHub
- ✅ Custom domains supported
- ⚠️ Service sleeps after 15 min inactivity
- ⚠️ ~30 sec cold start on first request

---

## 🔐 Security Best Practices

- ✅ Only SELECT queries allowed (enforced in code & database)
- ✅ SQL injection prevention via RPC function
- ✅ Environment variables never committed to Git
- ✅ CORS configured (adjust origins in `main.py` for production)
- ⚠️ Consider adding authentication for production use
- ⚠️ Rate limiting recommended for public APIs

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - feel free to use this project for your own purposes.

---

## 🆘 Support

- **Issues**: https://github.com/sakibulhasan/agent-supabase/issues
- **Deployed App**: https://agent-supabase.onrender.com
- **API Docs**: https://agent-supabase.onrender.com/docs (FastAPI auto-generated)
   - Validates syntax
   - Runs tests

2. **CD** (Continuous Deployment) - Runs after CI succeeds
   - Builds Docker image
   - Pushes to Google Container Registry
   - Deploys to Cloud Run
   - Sets environment variables

### Required GitHub Secrets

Set these in your GitHub repository (Settings → Secrets and variables → Actions):

| Secret | Description | Where to Get |
|--------|-------------|--------------|
| `GCP_SA_KEY` | Service account JSON key | Google Cloud Console → IAM & Admin → Service Accounts |
| `GCP_PROJECT` | GCP project ID | Top of GCP Console |
| `REGION` | Deployment region | e.g., `us-central1` |
| `SUPABASE_URL` | Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Supabase Dashboard → Settings → API |
| `GEMINI_API_KEY` | Google Gemini API key | https://makersuite.google.com/app/apikey |

### Setting up GCP Service Account

1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Create service account: `github-actions-sa`
3. Grant roles:
   - Cloud Run Admin
   - Storage Admin
   - Service Account User
   - Artifact Registry Writer
4. Create JSON key and add to GitHub Secrets as `GCP_SA_KEY`
5. Enable required APIs:
   - Cloud Run API
   - Container Registry API
   - Cloud Build API

### Manual Deployment

If needed, deploy manually:
```bash
# Build image
docker build -t gcr.io/PROJECT_ID/ai-supabase-agent:latest .

# Push to registry
docker push gcr.io/PROJECT_ID/ai-supabase-agent:latest

# Deploy to Cloud Run
gcloud run deploy ai-supabase-agent \
  --image gcr.io/PROJECT_ID/ai-supabase-agent:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=$SUPABASE_URL,SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY,GEMINI_API_KEY=$GEMINI_API_KEY
```

## Architecture

```
User Question → FastAPI → Gemini AI → SQL Query → Supabase → Results → AI Summary → Response
```

## Security Notes

- ✅ Only SELECT queries are allowed
- ✅ Environment variables for all credentials
- ✅ Never commit `.env` file
- ✅ Service account with minimal required permissions
- ✅ CORS configured for specific origins
