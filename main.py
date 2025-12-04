import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent import ai_query_agent
from pydantic import BaseModel

app = FastAPI(title="AI Supabase Agent")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskIn(BaseModel):
    question: str

@app.post('/ask')
def ask(payload: AskIn):
    question = payload.question
    result = ai_query_agent(question)
    return result

@app.get('/')
def health():
    return {"status": "ok"}
