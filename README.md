# Agentic AI Research Assistant

Full-stack MVP: React + Vite frontend, FastAPI backend, planner/research/synthesis agent workflow, Tavily web search and OpenAI-compatible LLM.

## Requirements
- Python 3.11+
- Node.js 20+
- OpenAI API key
- Tavily API key

## Backend (Windows)
```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs

## Frontend
Open another terminal:
```bat
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally http://localhost:5173.

Never commit `.env` or API keys to GitHub.
