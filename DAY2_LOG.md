# Day 2 log — 12 November 2026

## Status

- [Done] Read `START_HERE.md` and `SOURCE_RULES.md`; created this project folder.
- [Blocked with exact cause] Groq connectivity proof: requires the student's own local `GROQ_API_KEY` in `.env`; no secret was supplied or stored here. Run `connectivity_check.py` locally and record the response below.
- [Done] Ten synthetic policy documents and manifest created and source-checked.
- [Done] FastAPI baseline with BM25 retrieval, `/api/health`, `/api/ask`, server-side model call, citations, trace JSONL, and bounded no-key response.
- [Done] Tests added for health and manifest passage resolution.
- [Pending] Six manual smoke responses and screenshot require running the app with the local key.

## Connectivity proof

- Provider: Groq
- Exact model ID: value of local `GROQ_MODEL` (default `openai/gpt-oss-20b`)
- Result: pending local run; key is intentionally not recorded.

## Known failures and next action

The model call cannot be proved from this environment without a user-owned API key. Copy `.env.example` to `.env`, add the key locally, run `connectivity_check.py`, start Uvicorn, and save the six raw JSON responses under `smoke_results/`. Do not replace a failed response with a fabricated pass.

