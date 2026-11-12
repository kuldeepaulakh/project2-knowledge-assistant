# F03 — Citation-only answer

- Layer: citation/answer validation
- Evidence: baseline C06 trace `d02dcca696ce446b98e9c920c23b1593`.
- Expected: answer the conditional meal question with CAD 35, approved travel, and receipt condition.
- Actual: response contained only `[EXPENSE-2026-P1]`.
- Impact: citation existed, but answer content was unusable.
- Candidate change: candidate rejects answer decisions whose substantive text is empty after citation removal.
- Retest: candidate C06 returned a substantive CAD 35/receipt answer citing `EXPENSE-2026-P1`.
