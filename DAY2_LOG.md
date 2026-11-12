# Day 2 log — 12 November 2026

## Status

- [Done] Read `START_HERE.md` and `SOURCE_RULES.md`; created this project folder.
- [Done] Groq connectivity proof completed server-side with the local `.env`; the key was not printed or stored in the repository.
- [Done] Ten synthetic policy documents and manifest created and source-checked.
- [Done] FastAPI baseline with BM25 retrieval, `/api/health`, `/api/ask`, server-side model call, citations, trace JSONL, and bounded no-key response.
- [Done] Tests added for health and manifest passage resolution.
- [Done with QA evidence] Six manual smoke questions were run against `http://127.0.0.1:8000`; raw records are in `traces/requests.jsonl`. S1, S2, S3, and S5 answered; S4 clarified; S6 abstained. S3's raw answer omitted the manager-approval condition, so it remains recorded as a known model-quality failure.

## Connectivity proof

- Provider: Groq
- Exact model ID: `openai/gpt-oss-20b`
- Status: successful
- Response: `READY`

## Known failures and next action

The baseline is runnable and the live Groq call succeeded. S3 needs prompt/model-quality follow-up to consistently include the manager-approval condition; the raw response was not edited away. The API key must remain only in ignored `.env`; `.env.example` contains a placeholder. Do not replace a failed response with a fabricated pass.

