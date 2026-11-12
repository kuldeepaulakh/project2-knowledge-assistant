from __future__ import annotations

import json
from pathlib import Path

from .retrieval import Passage

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
MANIFEST_PATH = CORPUS / "manifest.json"


def load_passages() -> tuple[list[Passage], dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    passages: list[Passage] = []
    for document in manifest["documents"]:
        data = json.loads((CORPUS / document["filename"]).read_text(encoding="utf-8"))
        for passage in data["passages"]:
            passages.append(Passage(passage["id"], passage["text"], document["filename"], document))
    return passages, manifest

