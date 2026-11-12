"""Small dependency-free BM25 retriever for the fictional corpus."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass(frozen=True)
class Passage:
    passage_id: str
    text: str
    filename: str
    metadata: dict


class BM25:
    def __init__(self, passages: list[Passage]) -> None:
        self.passages = passages
        self.docs = [tokens(p.text) for p in passages]
        self.lengths = [len(doc) for doc in self.docs]
        self.avgdl = sum(self.lengths) / max(len(self.lengths), 1)
        self.df = Counter(term for doc in self.docs for term in set(doc))

    def search(self, query: str, k: int = 5) -> list[tuple[Passage, float]]:
        query_terms = tokens(query)
        n = len(self.docs)
        scores: list[tuple[Passage, float]] = []
        for passage, doc, length in zip(self.passages, self.docs, self.lengths):
            counts = Counter(doc)
            score = 0.0
            for term in query_terms:
                if term not in counts:
                    continue
                idf = math.log(1 + (n - self.df[term] + 0.5) / (self.df[term] + 0.5))
                tf = counts[term]
                score += idf * (tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * length / self.avgdl))
            if score > 0:
                scores.append((passage, score))
        return sorted(scores, key=lambda item: item[1], reverse=True)[:k]

