# AI Supabase Agent

A FastAPI backend service that answers natural language questions against Supabase `income` and `expense` tables using AI.

## Features
- Natural-language questions -> SQL (Gemini AI) -> safe SELECT execution on Supabase
- LLM-based summarization of results
- RESTful API with CORS support
- CI/CD with GitHub Actions to build and deploy to Cloud Run

## Prerequisites
- Supabase project (Postgres) with `income` and `expense` tables
- Google Gemini API key
- Python 3.11+

## Setup

1. Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```bash
SUPABASE_DB_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET=your_jwt_secret_here_at_least_32_characters_long
```

3. Run the server
```bash
# Unset Google Cloud credentials to avoid conflicts
unset GOOGLE_APPLICATION_CREDENTIALS
unset GCLOUD_PROJECT

uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## API Usage

### Health Check
```bash
curl http://localhost:8080/
```

### Ask a Question
```bash
curl -X POST "http://localhost:8080/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total income last month?"}'
```

**Response:**
```json
{
  "question": "What is the total income last month?",
  "sql": "SELECT SUM(price) FROM income WHERE date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')...",
  "rows": [...],
  "summary": "The total income last month was $X,XXX..."
}
```

## Deploy to Cloud Run

1. Build and push Docker image
```bash
docker build -t gcr.io/PROJECT_ID/ai-supabase-agent:latest .
docker push gcr.io/PROJECT_ID/ai-supabase-agent:latest
```

2. Deploy to Cloud Run
```bash
gcloud run deploy ai-supabase-agent \
  --image gcr.io/PROJECT_ID/ai-supabase-agent:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_DB_URL=$SUPABASE_DB_URL,GEMINI_API_KEY=$GEMINI_API_KEY,JWT_SECRET=$JWT_SECRET
```

## GitHub Actions CI/CD

Required GitHub Secrets:
- `GCP_SA_KEY` - Service account JSON key
- `GCP_PROJECT` - Your GCP project ID
- `CLOUD_RUN_SERVICE` - Service name
- `REGION` - Deployment region

**NOTE: Never commit sensitive credentials to the repository. Use environment variables and GitHub Secrets.**
