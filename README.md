# Project 2 Knowledge Assistant — Day 2 baseline

This is a local FastAPI knowledge assistant over ten fictional policy documents. It retrieves source passages with a small BM25 implementation, sends only retrieved fictional passages plus the question to Groq, and returns an answer, clarification, or bounded abstention with resolvable citation IDs.

## Run

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env locally; never commit or share it.
.\.venv\Scripts\python.exe connectivity_check.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Health is at `/api/health`; questions use `POST /api/ask` with `{"question":"..."}`.

## Model setup status

Provider: Groq. The exact model is read from `GROQ_MODEL` (default `openai/gpt-oss-20b`). Run `connectivity_check.py` after adding your own Free-plan key. No key is stored in this repository.

