from __future__ import annotations

import json
import os
import re
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .corpus import load_passages
from .retrieval import BM25, Passage

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
app = FastAPI(title="Fictional Policy Knowledge Assistant")
passages, manifest = load_passages()
retriever = BM25(passages)
TRACE_DIR = Path(__file__).resolve().parents[1] / "traces"
TRACE_DIR.mkdir(exist_ok=True)
PASSAGE_IDS = {passage.passage_id for passage in passages}
ID_PATTERN = re.compile(r"\[([A-Z0-9-]+)\]")
DECISION_PATTERN = re.compile(r"(?:DECISION\s*:\s*)(answer|clarify|abstain|conflict)", re.IGNORECASE)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    department: str | None = None
    as_of: date | None = None
    release: Literal["baseline", "candidate"] = "baseline"
    top_k: int = Field(default=5, ge=1, le=10)


def write_trace(record: dict[str, Any]) -> None:
    with (TRACE_DIR / "requests.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def model_error(exc: Exception) -> str:
    status = getattr(exc, "status_code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    category = f"HTTP {status}" if status else "request error"
    return f"Groq {category}: {str(exc)[:500]}"


def context_clarification(question: str, department: str | None, as_of: date | None, release: str = "baseline") -> str | None:
    lower = question.lower()
    remote_context_needed = release == "baseline" or any(term in lower for term in ("how many", "how much", "allowance", "days per week"))
    if remote_context_needed and any(term in lower for term in ("remote", "remotely", "work from home")) and not department and "support operations" not in lower:
        return "Which department should I apply, and what date should I use? Department exceptions can change the remote-work allowance."
    if "learning leave" in lower and not as_of and not re.search(r"\b20\d{2}\b", lower):
        return "What date or calendar year should I use? The learning-leave rule differs between 2025 and 2026."
    return None


def in_scope(passage: Passage, as_of: date | None) -> bool:
    if not as_of:
        return True
    metadata = passage.metadata
    start = date.fromisoformat(metadata["effective_start"])
    end_text = metadata.get("effective_end")
    end = date.fromisoformat(end_text) if end_text else None
    return start <= as_of and (end is None or as_of <= end)


def select_passages(question: str, department: str | None, as_of: date | None, top_k: int, release: str = "baseline") -> list[dict[str, Any]]:
    query = " ".join(part for part in (question, department or "", as_of.isoformat() if as_of else "") if part)
    candidates = retriever.search(query, 10)
    if release == "candidate":
        lower = f"{question} {department or ''}".lower()
        if "remote" in lower or "remotely" in lower or "work from home" in lower:
            if department and department.lower() == "support operations":
                candidates = [(p, s) for p, s in candidates if p.passage_id != "REMOTE-2026-P1"] + [(p, s) for p, s in candidates if p.passage_id == "REMOTE-2026-P1"]
        if "learning leave" in lower or "learning-leave" in lower:
            if as_of and as_of.year >= 2026:
                candidates = [(p, s) for p, s in candidates if p.passage_id != "LEAVE-2025-P1"]
            elif as_of and as_of.year == 2025:
                candidates = [(p, s) for p, s in candidates if p.passage_id != "LEAVE-2026-P1"]
        if "travel" in lower or "meal" in lower or "expense" in lower:
            candidates = [(p, s) for p, s in candidates if p.passage_id != "EXPENSE-FAQ-P1"] + [(p, s) for p, s in candidates if p.passage_id == "EXPENSE-FAQ-P1"]
        candidates = [(p, s) for p, s in candidates if p.passage_id != "WEBINAR-2026-P1"]
    selected: list[dict[str, Any]] = []
    for passage, score in candidates:
        if not in_scope(passage, as_of):
            continue
        selected.append({"id": passage.passage_id, "text": passage.text, "filename": passage.filename, "score": round(score, 4)})
        if len(selected) == top_k:
            break
    return selected


def answer_with_groq(question: str, department: str | None, as_of: date | None, selected: list[dict[str, Any]], release: str = "baseline") -> tuple[str, str, str | None]:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    if not api_key:
        return "", "abstain", "GROQ_API_KEY is not configured in the server .env."
    from groq import Groq

    context = "\n\n".join(f"[{item['id']}] {item['text']}" for item in selected)
    prompt = (
        "You are a cautious assistant for fictional policies. Use only the supplied passages. "
        "Return the first line exactly as DECISION: answer, DECISION: clarify, DECISION: abstain, or DECISION: conflict. "
        "Use clarify when the question lacks department/date context, abstain when the corpus does not establish the fact, "
        "and conflict only when applicable authoritative passages truly conflict. Cite only supplied passage IDs in square brackets. "
        "Never invent policy facts, dates, entitlements, or citation IDs. Quote or closely paraphrase all material conditions. "
        "Do not convert a weekly allowance into a monthly total unless the passage explicitly gives a monthly limit. "
        "Always provide a substantive answer before the citations.\n\n"
        f"Question: {question}\nDepartment: {department or '(not provided)'}\nAs of: {as_of.isoformat() if as_of else '(not provided)'}\n\nPassages:\n{context}"
    )
    try:
        response = Groq(api_key=api_key).chat.completions.create(model=model, temperature=0, messages=[{"role": "user", "content": prompt}])
        answer = response.choices[0].message.content or ""
        match = DECISION_PATTERN.search(answer)
        decision = match.group(1).lower() if match else "answer"
        answer = re.sub(r"^\s*DECISION\s*:\s*(?:answer|clarify|abstain|conflict)\s*\n?", "", answer, count=1, flags=re.IGNORECASE)
        return answer.strip(), decision, None
    except Exception as exc:
        return "", "abstain", model_error(exc)


def make_response(trace_id: str, started: float, request: AskRequest, decision: str, answer: str, citations: list[str], retrieved: list[dict[str, Any]], error: str | None, model: str) -> dict[str, Any]:
    return {"release": request.release, "decision": decision, "answer": answer, "citations": citations, "retrieved": retrieved, "model": model, "trace_id": trace_id, "elapsed_ms": round((time.perf_counter() - started) * 1000, 2), "error": error, "status": "ok" if not error else "error"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><title>Policy assistant</title><style>body{font:16px system-ui;max-width:760px;margin:40px auto;padding:0 18px;background:#e8f1f8;min-height:100vh}input,textarea{width:100%;box-sizing:border-box;margin:6px 0;padding:8px}textarea{height:100px}button{padding:10px 18px;margin-top:8px}pre{white-space:pre-wrap;background:#f3f3f3;padding:14px}</style></head><body><h1>Fictional policy assistant</h1><p>Only synthetic policy documents are used.</p><textarea id='q' placeholder='Ask a policy question'></textarea><input id='d' placeholder='Department (optional)'><input id='a' type='date' aria-label='As of date (optional)'><button onclick='ask()'>Ask</button><pre id='out'></pre><script>async function ask(){const body={question:q.value,release:'baseline'};if(d.value)body.department=d.value;if(a.value)body.as_of=a.value;const r=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});out.textContent=JSON.stringify(await r.json(),null,2)}</script></body></html>"""


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "corpus_documents": len(manifest["documents"]), "passages": len(passages), "model_configured": bool(os.getenv("GROQ_API_KEY"))}


@app.post("/api/ask")
def ask(request: AskRequest) -> dict[str, Any]:
    started = time.perf_counter()
    trace_id = uuid.uuid4().hex
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    retrieved = select_passages(request.question, request.department, request.as_of, request.top_k, request.release)
    clarification = context_clarification(request.question, request.department, request.as_of, request.release)
    error: str | None = None
    citations: list[str] = []
    if clarification:
        decision, answer = "clarify", clarification
    elif not retrieved:
        decision, answer = "abstain", "This question is not established in these documents."
    else:
        answer, decision, error = answer_with_groq(request.question, request.department, request.as_of, retrieved, request.release)
        cited_ids = ID_PATTERN.findall(answer)
        invalid = sorted(set(cited_ids) - {item["id"] for item in retrieved})
        if invalid:
            decision, error, answer = "conflict", f"Citation integrity failure: model cited IDs not in retrieved passages: {', '.join(invalid)}", "The model response was rejected because its citations could not be verified."
        else:
            citations = list(dict.fromkeys(cited_ids))
            substantive_answer = ID_PATTERN.sub("", answer).strip(" :\n")
            if decision == "answer" and (not citations or (request.release == "candidate" and not substantive_answer)):
                decision, error, answer = "conflict", "Citation integrity failure: answer contained no verifiable passage citation.", "The model response was rejected because it did not cite a retrieved passage."
            elif decision == "abstain" and not answer:
                answer = "This question is not established in these documents."
    result = make_response(trace_id, started, request, decision, answer, citations, retrieved, error, model)
    write_trace({"timestamp": datetime.now(timezone.utc).isoformat(), "question": request.question, "department": request.department, "as_of": request.as_of.isoformat() if request.as_of else None, "release": request.release, "retrieved": retrieved, "model_result": answer, "decision": decision, "citations": citations, "error": error, "trace_id": trace_id, "elapsed_ms": result["elapsed_ms"]})
    return result

