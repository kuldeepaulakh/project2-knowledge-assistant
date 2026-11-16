# Project 2 Knowledge Assistant — Day 2 baseline

This is a local FastAPI knowledge assistant over ten fictional policy documents. It retrieves source passages with a small BM25 implementation, sends only retrieved fictional passages plus the question to Groq, and returns an answer, clarification, or bounded abstention with resolvable citation IDs.

## Run (Windows, actually executed)

```powershell
cd "C:\Users\jyoti\Downloads\Project2_Self_Build_Student_Pack\Project2_Self_Build_Student_Pack\project2-knowledge-assistant"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Create .env locally with GROQ_API_KEY and GROQ_MODEL; never commit or share it.
.\.venv\Scripts\python.exe connectivity_check.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Health is at `/api/health`; questions use `POST /api/ask` with `{"question":"...","department":"Support Operations","as_of":"2026-04-01","release":"baseline"}`. The response includes decision, retrieved passages, verified citations, trace ID, timing, model tag, and visible errors.

## Day 3 evaluation

The frozen versioned benchmark is `eval/benchmark_v1.csv`; its validator is run with:

```powershell
.\.venv\Scripts\python.exe eval\validate_benchmark.py
.\.venv\Scripts\python.exe eval\run_cases.py baseline
.\.venv\Scripts\python.exe eval\run_cases.py candidate
.\.venv\Scripts\python.exe eval\analyze.py
```

The runner writes the exact request/response, retrieved passage text and IDs, citations, decision, model, timing and error to `eval/raw_runs.jsonl`. It runs 12 first-pass cases plus repeat trials for preselected high-risk cases C05 and C10, producing 16 attempts per release. `release=baseline` preserves the original path; `release=candidate` enables the authority/scope/citation-validation changes.

## Model setup status

Provider: Groq. The exact model is read from `GROQ_MODEL` (default `openai/gpt-oss-20b`). Run `connectivity_check.py` after adding your own Free-plan key. No key is stored in this repository.

## Day 3–4 handover

Human review covers all 12 first-pass baseline and candidate outputs. With the runner's configured `k=5`, retrieval hit@5 is 10/12 (83.3%) for both releases. Candidate human review improves correctness from 3 fully-correct cases to 5 and decision correctness from 9/12 to 11/12, but C05 still makes an unsupported monthly conversion and C10 is rejected by citation-integrity validation. The recommendation is conditional go for classroom demonstration and no-go for production policy use. See `eval/human_review_summary.md`, `eval/human_review.csv`, `release_decision.md`, and `findings/`.

For the final demonstration, show an answerable question such as the 2026 learning-leave case, an unknown or ambiguous case such as parental leave or an unspecified remote-work allowance, one raw record from `eval/raw_runs.jsonl`, and a matched C05 or C06 baseline/candidate comparison.

