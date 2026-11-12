# Day 3 release recommendation

## Conditional go for candidate evaluation

The corpus, validator, app, tests, benchmark and 32 raw attempts are present. Baseline and candidate remain selectable through `release=baseline|candidate`. The candidate improved the false clarification in C04 and citation-only output in C06, while preserving bounded unknown handling.

This is not a production-ready release. C05 still converts a weekly Support Operations rule into a monthly total in the candidate run, and C10 exposed a citation-integrity rejection. Human review and Day 4 investigation are required before any stronger recommendation.

Evidence: `eval/raw_runs.jsonl`, `eval/analysis.json`, `eval/human_review.csv`, and findings F01–F03. The app uses only fictional passages and the API key remains local in ignored `.env`.
