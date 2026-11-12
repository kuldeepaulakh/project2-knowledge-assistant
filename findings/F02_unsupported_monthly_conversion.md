# F02 — Unsupported monthly conversion

- Layer: generation/grounding
- Evidence: baseline C05 traces `b4f6a260188443f2a7f7e092802fd84f`, plus repeat trials.
- Expected: one day per week for Support Operations, manager approval; do not guarantee a monthly total.
- Actual: model answered four remote days in April and omitted manager approval.
- Impact: material scope and condition error.
- Candidate change: added explicit prompt constraint not to convert weekly limits into monthly totals and to preserve all material conditions.
- Retest: candidate C05 still produced a four-day monthly derivation in the recorded run; this remains an open limitation.
