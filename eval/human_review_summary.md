# Day 3 human review and matched comparison

Reviewed all 12 first-pass cases for both releases. The runner does not override `top_k`, so the configured retrieval value is the API default `top_k=5`. Retrieval hit@k uses the 12 first-pass cases as the denominator and counts a hit when at least one expected applicable passage ID appears in the top five retrieved passages.

## Machine and retrieval counts

| Release | Attempted | Valid citation records | Errors | Retrieval hit@5 | Decision matches |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 12 | 12 | 0 | 10/12 (83.3%) | 11/12 |
| Candidate | 12 | 12 | 1 | 10/12 (83.3%) | 11/12 |

“Valid citation record” means every cited ID is present in that record's retrieved passage IDs; empty citation lists are not treated as an error by the machine check. The candidate error is C10, where the citation-integrity guard rejected a response with no verifiable citation.

## Human review counts

| Release | Reviewed | Correctness 2 / 1 / 0 | Decision correct | Grounding average* | Citation average* |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 12 | 3 / 6 / 3 | 9/12 | 1.375 | 1.714 |
| Candidate | 12 | 5 / 6 / 1 | 11/12 | 1.625 | 1.625 |

\* Averages exclude `NA` rows. Candidate improves direct-answer correctness and decision selection, but citation quality is not uniformly improved because C10 is rejected and several answers omit material policy conditions.

## Matched baseline/candidate review

- C04 improved from an incorrect clarification to the correct security-training answer with `ONBOARD-2026-P1`.
- C06 improved from citation-only output to a substantive CAD 35/receipt answer, although alcohol exclusion remains omitted.
- C11 improved from an empty clarification body to an explanatory clarification with the two year-specific passages.
- C05 improved by retaining the weekly rule and manager approval, but still converts one day per week into a guaranteed four-day April total. This remains an unsupported claim.
- C10 regressed to a safe error: the candidate rejected the answer because no verifiable citation was present. This is preferable to accepting an uncited answer, but it is still a failed user-facing case.

Full row-level scores and trace IDs are in `human_review.csv`; raw evidence is in `raw_runs.jsonl`. Findings F01–F03 document the observed scope, generation, and citation-layer issues, including candidate retests.
