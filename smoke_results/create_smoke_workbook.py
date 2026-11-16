import json
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
TRACE_FILE = ROOT / "traces" / "requests.jsonl"
OUTPUT_FILE = Path(__file__).resolve().parent / "smoke_results.xlsx"

cases = [
    ("S1", "I am full-time, have worked eight months, and want learning leave in 2026. How many days?", "Current five-day rule; manager approval; current source.", "Answered"),
    ("S2", "What was the learning-leave allowance in 2025?", "Archived three-day rule, clearly limited to 2025.", "Answered"),
    ("S3", "I work in Support Operations. How many remote days can I take in April 2026?", "Current department exception: one day/week and manager approval.", "Answered with known quality failure"),
    ("S4", "How many remote days can I work?", "Ask for department/date if needed; do not assume the general allowance always applies.", "Clarified"),
    ("S5", "What is the meal limit on approved business travel?", "CAD 35/day with applicable conditions; cite current expenses policy.", "Answered"),
    ("S6", "How many days of parental leave do I get?", "Corpus does not establish this; no invented number.", "Abstained"),
]

records = []
for line in TRACE_FILE.read_text(encoding="utf-8").splitlines():
    if line.strip():
        records.append(json.loads(line))

selected = []
for case_id, question, check, expected_outcome in cases:
    matches = [
        record for record in records
        if record.get("question") == question and record.get("trace_id")
    ]
    if not matches:
        raise RuntimeError(f"No usable trace found for {case_id}: {question}")
    matches.sort(key=lambda record: record.get("timestamp", ""))
    record = matches[0]
    record["case_id"] = case_id
    record["qa_check"] = check
    record["expected_outcome"] = expected_outcome
    selected.append(record)

wb = Workbook()
summary = wb.active
summary.title = "Smoke Results"
headers = [
    "Case ID", "Question", "Expected QA Check", "Recorded Outcome", "Decision",
    "Answer / Model Result", "Citations", "Retrieved Passage IDs", "Error",
    "Trace ID", "Timestamp", "Elapsed (ms)", "Release", "Model",
]
summary.append(headers)

for record in selected:
    retrieved = record.get("retrieved") or []
    answer = record.get("model_result")
    if answer is None:
        answer = record.get("response", "")
    summary.append([
        record["case_id"],
        record["question"],
        record["qa_check"],
        record["expected_outcome"],
        record.get("decision") or record.get("mode", ""),
        answer or "",
        ", ".join(record.get("citations") or []),
        ", ".join(item.get("id", "") for item in retrieved),
        record.get("error") or "",
        record.get("trace_id") or "",
        record.get("timestamp") or "",
        record.get("elapsed_ms") or "",
        record.get("release") or "baseline",
        record.get("model") or "",
    ])

passages = wb.create_sheet("Retrieved Passages")
passages_headers = ["Case ID", "Passage ID", "Filename", "Score", "Passage Text"]
passages.append(passages_headers)
for record in selected:
    for item in record.get("retrieved") or []:
        passages.append([
            record["case_id"], item.get("id", ""), item.get("filename", ""),
            item.get("score", ""), item.get("text", ""),
        ])

header_fill = PatternFill("solid", fgColor="1F4E78")
for sheet in wb.worksheets:
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for column_cells in sheet.columns:
        column_letter = get_column_letter(column_cells[0].column)
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 60)
    sheet.row_dimensions[1].height = 30

summary.column_dimensions["B"].width = 55
summary.column_dimensions["C"].width = 55
summary.column_dimensions["F"].width = 65
passages.column_dimensions["E"].width = 90

wb.save(OUTPUT_FILE)
print(OUTPUT_FILE)
