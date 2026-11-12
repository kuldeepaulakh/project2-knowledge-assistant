from fastapi.testclient import TestClient

from app.main import app, manifest, passages

client = TestClient(app)


def test_health_responds() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_corpus_manifest_resolves_all_passages() -> None:
    manifest_ids = {p["id"] for document in manifest["documents"] for p in __import__("json").loads((__import__("pathlib").Path("corpus") / document["filename"]).read_text())["passages"]}
    assert manifest_ids == {p.passage_id for p in passages}

