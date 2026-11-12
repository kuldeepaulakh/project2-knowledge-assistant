from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .corpus import load_passages
from .retrieval import BM25

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
app = FastAPI(title="Fictional Policy Knowledge Assistant")
passages, manifest = load_passages()
retriever = BM25(passages)
TRACE_DIR = Path(__file__).resolve().parents[1] / "traces"
TRACE_DIR.mkdir(exist_ok=True)


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


def write_trace(record: dict) -> None:
    with (TRACE_DIR / "requests.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def answer_with_groq(question: str, selected: list[dict]) -> tuple[str, str]:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    if not api_key:
        return ("Model call is not configured. Add GROQ_API_KEY to the local server .env; no policy answer was produced.", "blocked")
    from groq import Groq

    context = "\n\n".join(f"[{p['id']}] {p['text']}" for p in selected)
    prompt = (
        "You are a cautious assistant for fictional policies. Use only the supplied passages. "
        "If the passages do not establish an answer, say exactly that it is not established in these documents. "
        "If department or date context is necessary, ask a concise clarification. Never invent facts or citations. "
        "Cite passage IDs in square brackets.\n\n"
        f"Question: {question}\n\nPassages:\n{context}"
    )
    response = Groq(api_key=api_key).chat.completions.create(
        model=model,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or "The model returned no answer.", "model"


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><title>Policy assistant</title>
    <style>body{font:16px system-ui;max-width:760px;margin:40px auto;padding:0 18px}textarea{width:100%;height:100px}button{padding:10px 18px;margin-top:10px}pre{white-space:pre-wrap;background:#f3f3f3;padding:14px}</style></head>
    <body><h1>Fictional policy assistant</h1><p>Ask about the synthetic policy corpus.</p>
    <textarea id='q' placeholder='Ask a policy question'></textarea><br><button onclick='ask()'>Ask</button><pre id='out'></pre>
    <script>async function ask(){const q=document.getElementById('q').value;const r=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}</script></body></html>"""


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "corpus_documents": len(manifest["documents"]), "passages": len(passages), "model_configured": bool(os.getenv("GROQ_API_KEY"))}


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    if not request.question.strip():
        return {"status": "clarification", "answer": "Please provide a policy question.", "citations": [], "retrieved": []}
    results = retriever.search(request.question, max(1, min(request.top_k, 10)))
    selected = [{"id": p.passage_id, "text": p.text, "filename": p.filename, "score": round(score, 4)} for p, score in results]
    if not selected:
        answer, mode = "This question is not established in these documents.", "abstention"
    else:
        answer, mode = answer_with_groq(request.question, selected)
    valid_ids = {p["id"] for p in selected}
    citations = [p_id for p_id in valid_ids if f"[{p_id}]" in answer]
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), "question": request.question, "response": answer, "mode": mode, "retrieved": selected, "citations": citations}
    write_trace(record)
    return {"status": "answered" if mode == "model" else mode, "answer": answer, "citations": citations, "retrieved": selected, "trace": {"mode": mode, "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")}}

