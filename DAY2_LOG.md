# Day 2 log — 12 November 2026

## Status

- [Done] Read `START_HERE.md` and `SOURCE_RULES.md`; created this project folder.
- [Done] Groq connectivity proof completed server-side with the local `.env`; the key was not printed or stored in the repository.
- [Done] Ten synthetic policy documents and manifest created and source-checked.
- [Done] FastAPI baseline with BM25 retrieval, `/api/health`, `/api/ask`, server-side model call, citations, trace JSONL, and bounded no-key response.
- [Done] Tests added for health and manifest passage resolution.
- [Pending] Six manual smoke responses and screenshot require running the app with the local key.

## Connectivity proof

- Provider: Groq
- Exact model ID: `openai/gpt-oss-20b`
- Status: successful
- Response: `READY`

## Known failures and next action

The model call cannot be proved from this environment without a user-owned API key. Copy `.env.example` to `.env`, add the key locally, run `connectivity_check.py`, start Uvicorn, and save the six raw JSON responses under `smoke_results/`. Do not replace a failed response with a fabricated pass.

