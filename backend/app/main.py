import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import research

load_dotenv()

app = FastAPI(
    title="Agentic AI Research Assistant",
    version="1.0.0",
    description="Research planning, web research and report synthesis API."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Agentic AI Research Assistant API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/research")
def run_research(request: ResearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Research query is required.")
    try:
        return research(request.query.strip())
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Research failed. Verify OPENAI_API_KEY and TAVILY_API_KEY in backend/.env.",
        )
