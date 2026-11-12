from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = Path(__file__).resolve().parent


def main() -> None:
    cases = {row["case_id"]: row for row in csv.DictReader((EVAL / "benchmark_v1.csv").open(encoding="utf-8", newline=""))}
    attempts = [json.loads(line) for line in (EVAL / "raw_runs.jsonl").read_text(encoding="utf-8").splitlines()]
    first_pass = [row for row in attempts if row["trial_id"] == 1]
    summary = {}
    for release in ("baseline", "candidate"):
        rows = [row for row in first_pass if row["release"] == release]
        errors = sum(bool(row["error"]) for row in rows)
        valid_citations = sum(set(row["citations"]) <= {p["id"] for p in row["retrieved"]} for row in rows)
        hits = sum(bool(set(cases[row["case_id"]]["applicable_passage_ids"].split(";") if cases[row["case_id"]]["applicable_passage_ids"] else []) & {p["id"] for p in row["retrieved"]}) for row in rows)
        expected_decisions = sum(row["decision"] == cases[row["case_id"]]["expected_decision"] for row in rows)
        summary[release] = {"first_pass_attempted": len(rows), "errors": errors, "valid_citation_records": valid_citations, "evidence_hit_at_5": hits, "expected_decision_matches": expected_decisions}
    diff = []
    baseline = {row["case_id"]: row for row in first_pass if row["release"] == "baseline"}
    candidate = {row["case_id"]: row for row in first_pass if row["release"] == "candidate"}
    for case_id in sorted(cases):
        if baseline[case_id]["answer"] != candidate[case_id]["answer"] or baseline[case_id]["decision"] != candidate[case_id]["decision"]:
            diff.append({"case_id": case_id, "baseline_decision": baseline[case_id]["decision"], "candidate_decision": candidate[case_id]["decision"], "baseline_answer": baseline[case_id]["answer"], "candidate_answer": candidate[case_id]["answer"]})
    result = {"attempts_total": len(attempts), "attempts_by_release": dict(Counter(row["release"] for row in attempts)), "first_pass": summary, "baseline_candidate_differences": diff}
    (EVAL / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
