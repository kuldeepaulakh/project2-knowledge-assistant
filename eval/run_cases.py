from __future__ import annotations

import csv
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
CASES = Path(__file__).with_name("benchmark_v1.csv")
OUTPUT = Path(__file__).with_name("raw_runs.jsonl")
URL = "http://127.0.0.1:8000/api/ask"
HIGH_RISK = {"C05", "C10"}


def run_release(release: str) -> None:
    rows = list(csv.DictReader(CASES.open(encoding="utf-8", newline="")))
    with OUTPUT.open("a", encoding="utf-8") as output:
        with httpx.Client(timeout=60) as client:
            for row in rows:
                trials = [1, 2, 3] if row["case_id"] in HIGH_RISK else [1]
                for trial_id in trials:
                    request = {"question": row["question"], "release": release}
                    if row["department"]:
                        request["department"] = row["department"]
                    if row["as_of"]:
                        request["as_of"] = row["as_of"]
                    started = time.perf_counter()
                    error = None
                    try:
                        response = client.post(URL, json=request)
                        response.raise_for_status()
                        payload = response.json()
                    except Exception as exc:
                        payload = {}
                        error = str(exc)
                    record = {"run_id": uuid.uuid4().hex, "timestamp": datetime.now(timezone.utc).isoformat(), "case_id": row["case_id"], "release": release, "trial_id": trial_id, "request": request, "response": payload, "retrieved": payload.get("retrieved", []), "answer": payload.get("answer", ""), "citations": payload.get("citations", []), "decision": payload.get("decision"), "model": payload.get("model"), "elapsed_ms": payload.get("elapsed_ms", round((time.perf_counter() - started) * 1000, 2)), "error": error or payload.get("error")}
                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                    output.flush()
                    print(json.dumps({"case_id": row["case_id"], "release": release, "trial_id": trial_id, "decision": record["decision"], "error": record["error"]}))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"baseline", "candidate"}:
        raise SystemExit("Usage: python eval/run_cases.py baseline|candidate")
    run_release(sys.argv[1])
