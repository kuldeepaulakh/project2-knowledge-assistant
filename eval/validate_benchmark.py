from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = Path(__file__).with_name("benchmark_v1.csv")


def main() -> None:
    rows = list(csv.DictReader(BENCHMARK.open(encoding="utf-8", newline="")))
    manifest = json.loads((ROOT / "corpus" / "manifest.json").read_text(encoding="utf-8"))
    valid_ids = {passage_id for doc in manifest["documents"] for passage_id in doc["passage_ids"]}
    required = {"direct": 4, "conditional/multi-document": 2, "unknown": 2, "outdated/conflicting": 2, "ambiguous": 2}
    counts = {category: sum(row["primary_category"] == category for row in rows) for category in required}
    assert len(rows) == 12
    assert counts == required, counts
    assert sum(row["split"] == "development" for row in rows) == 8
    assert sum(row["split"] == "held-out" for row in rows) == 4
    assert len({row["case_id"] for row in rows}) == 12
    for row in rows:
        for passage_id in filter(None, row["applicable_passage_ids"].split(";")):
            assert passage_id in valid_ids, (row["case_id"], passage_id)
    print(json.dumps({"status": "valid", "version": "v1", "cases": len(rows), "category_counts": counts, "development": 8, "held_out": 4, "valid_manifest_ids": len(valid_ids)}))


if __name__ == "__main__":
    main()
