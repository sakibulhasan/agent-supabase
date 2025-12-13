# AI Supabase Agent

A FastAPI backend service that answers natural language questions against Supabase transaction tables using AI.

## Features
- Natural-language questions → SQL (Gemini AI) → safe SELECT execution on Supabase
- LLM-based summarization of query results with insights
- Context-aware query generation (fetches categories and payment methods from database)
- RESTful API with CORS support
- Automated deployments via Render.com

## 🚀 Quick Deploy to Render.com

**See [RENDER_QUICKSTART.md](RENDER_QUICKSTART.md) for 5-minute deployment guide!**

Or follow these steps:
1. Push this repo to GitHub
2. Sign up at https://render.com with GitHub
3. Create new Web Service from your repository
4. Add environment variables (see below)
5. Deploy! 🎉

**Automatic deployments**: Every push to `main` branch auto-deploys!

---

## Prerequisites
- Supabase project (Postgres) with transaction tables
- Google Gemini API key
- Python 3.11+
- Google Cloud Project (for deployment)

## Local Development Setup

1. **Create a virtual environment and install dependencies**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables**

Create a `.env` file in the project root:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
```

**Where to get credentials:**
- **Supabase**: Dashboard → Settings → API
- **Gemini API**: https://makersuite.google.com/app/apikey

3. **Run the server locally**
```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Server will start at: http://localhost:8080

## API Endpoints

### Health Check
```bash
curl https://ai-supabase-agent-b3l4e7s4eq-uc.a.run.app/
```
**Response:** `{"status":"ok"}`

### Ask a Question
```bash
curl -X POST "https://ai-supabase-agent-b3l4e7s4eq-uc.a.run.app/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the total expenses?"}'
```

**Response:**
```json
{
  "question": "What are the total expenses?",
  "sql": "SELECT SUM(total_price) FROM transactions_expense",
  "rows": [{"sum": 62267809}],
  "summary": "The total expenses amount to 62,267,809..."
}
```

**Example Questions:**
- "What are the total expenses?"
- "Show me the top 5 highest expenses"
- "What was spent on advertising this year?"
- "List all vendor payments over $100,000"

## CI/CD Pipeline

The project uses GitHub Actions for automated deployment to Google Cloud Run.

### Workflow
1. **CI** (Continuous Integration) - Runs on push to `main`
   - Lints Python code
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
