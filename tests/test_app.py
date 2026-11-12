from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import PASSAGE_IDS, app, manifest, passages

client = TestClient(app)


def test_health_responds() -> None:
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["corpus_documents"] == 10


def test_manifest_source_ids_are_valid() -> None:
    manifest_ids = set()
    for document in manifest["documents"]:
        data = json.loads((Path("corpus") / document["filename"]).read_text(encoding="utf-8"))
        manifest_ids.update(passage["id"] for passage in data["passages"])
    assert manifest_ids == {passage.passage_id for passage in passages} == PASSAGE_IDS


def test_ask_citations_are_retrieved_ids(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeCompletions:
        def create(self, **kwargs):
            message = type("Message", (), {"content": "DECISION: answer\nThe allowance is five days [LEAVE-2026-P1]."})()
            return type("Completion", (), {"choices": [type("Choice", (), {"message": message})()]})()

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("groq.Groq", FakeClient)
    body = client.post("/api/ask", json={"question": "How many learning leave days in 2026?", "as_of": "2026-06-01"}).json()
    retrieved_ids = {item["id"] for item in body["retrieved"]}
    assert body["decision"] == "answer"
    assert set(body["citations"]) <= retrieved_ids
    assert body["trace_id"]
    assert body["elapsed_ms"] >= 0


def test_missing_remote_context_clarifies() -> None:
    body = client.post("/api/ask", json={"question": "How many remote days can I work?"}).json()
    assert body["decision"] == "clarify"
    assert body["citations"] == []

