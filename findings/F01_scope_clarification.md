# F01 — Over-broad remote context clarification

- Layer: scope handling
- Evidence: baseline C04 trace `19f37c1193a04562aa4abfa69116e74b`
- Expected: answer that security training is required before remote-work approval, citing `ONBOARD-2026-P1`.
- Actual: clarification asking for department/date.
- Impact: direct answer was incorrectly blocked.
- Candidate change: only candidate scope handling treats remote wording as ambiguous when the user asks for an allowance/count; security-training questions proceed to generation.
- Retest: candidate C04 answered with security training and cited `ONBOARD-2026-P1`.
