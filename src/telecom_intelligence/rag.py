 
from __future__ import annotations
 
import hashlib
import re
from pathlib import Path
from typing import Any
 
 
class HashEmbedder:
    """Deterministic local embedding model used when an embedding API is not needed."""
 
    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions
 
    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9_/-]+", text.lower())
        for token in tokens:
            index = int(hashlib.sha256(token.encode()).hexdigest(), 16) % self.dimensions
            vector[index] += 1.0
        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        return [value / norm for value in vector]
 
 
def read_chunks(documents_dir: Path) -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    for path in sorted(documents_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for index, chunk in enumerate(re.split(r"\n\s*\n", text)):
            cleaned = chunk.strip()
            if cleaned:
                chunks.append({"source": path.name, "chunk_id": str(index), "text": cleaned})
    return chunks
 
 
class RunbookRetriever:
    def __init__(self, documents_dir: Path):
        self.chunks = read_chunks(documents_dir)
        self.embedder = HashEmbedder()
        self.index = None
        try:
            import faiss
 
            import numpy as np
 
            matrix = np.array([self.embedder.embed(c["text"]) for c in self.chunks], dtype="float32")
            self.index = faiss.IndexFlatIP(self.embedder.dimensions)
            self.index.add(matrix)
        except (ImportError, Exception):
            self.index = None
 
    @property
    def backend(self) -> str:
        return "faiss" if self.index is not None else "lexical-fallback"
 
    def retrieve(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        if not self.chunks:
            return []
        if self.index is not None:
            import numpy as np
 
            scores, indices = self.index.search(
                np.array([self.embedder.embed(query)], dtype="float32"), limit
            )
            return [
                {**self.chunks[index], "score": round(float(score), 4)}
                for score, index in zip(scores[0], indices[0])
                if index >= 0
            ]
        query_tokens = set(re.findall(r"[a-z0-9_/-]+", query.lower()))
        ranked = []
        for chunk in self.chunks:
            tokens = set(re.findall(r"[a-z0-9_/-]+", chunk["text"].lower()))
            score = len(query_tokens & tokens) / max(len(query_tokens), 1)
            ranked.append(({**chunk, "score": round(score, 4)}))
        return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
 
 
 