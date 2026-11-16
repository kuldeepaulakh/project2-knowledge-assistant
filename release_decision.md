# Day 3–4 release recommendation

## Conditional go for evaluation/demo; no-go for production policy use

The frozen validator is valid, all 12 baseline and 12 candidate first-pass outputs were human-reviewed, and the full 32-attempt raw run set is present. The configured retrieval value is `k=5`; both releases hit at least one applicable passage in 10/12 cases (83.3%). Candidate decision matching is 11/12 with one explicit citation-integrity error.

Candidate improvements are real: C04 now answers the security-training question, C06 now provides substantive content instead of a citation-only response, and C11 now explains its clarification. The candidate also preserves bounded abstention for unknown C07/C08.

The release is not production-ready. C05 still converts a weekly Support Operations rule into a guaranteed four-day April total, and C10 is rejected because the model supplied no verifiable citation. Several otherwise grounded answers still omit material conditions such as approval, receipt, alcohol, or carryover rules.

Decision: use the candidate for classroom demonstration and continued investigation, but do not use it for employee policy decisions until the C05 generation/grounding issue and C10 citation-recovery path are fixed and re-reviewed.

Evidence: `eval/raw_runs.jsonl`, `eval/analysis.json`, `eval/human_review.csv`, and findings F01–F03. The app uses only fictional passages and the API key remains local in ignored `.env`.
