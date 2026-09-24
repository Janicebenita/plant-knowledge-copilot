from dataclasses import dataclass
import hashlib
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from .chunking import chunk_sections
from .extract import extract_document


@dataclass(frozen=True)
class SearchHit:
    text: str
    source: str
    page: int | None
    score: float
    chunk_id: str


class KnowledgeBase:
    def __init__(self, path: str, collection: str, embedding_model: str, embedding_function: Any = None):
        self.embedding_model = embedding_model
        self.client = chromadb.PersistentClient(path=path)
        metadata = {"hnsw:space": "cosine", "embedding_model": embedding_model, "schema_version": "1"}
        self.collection = self.client.get_or_create_collection(
            name=collection,
            metadata=metadata,
            embedding_function=embedding_function or SentenceTransformerEmbeddingFunction(model_name=embedding_model),
        )
        actual = self.collection.metadata or {}
        if actual.get("embedding_model") != embedding_model or actual.get("hnsw:space") != "cosine":
            raise RuntimeError("Collection embedding model or distance metric is incompatible. Use a new collection name or rebuild it.")

    def ingest(self, filename: str, data: bytes, size: int, overlap: int) -> dict[str, Any]:
        digest = hashlib.sha256(data).hexdigest()
        existing = self.collection.get(where={"source": filename}, include=["metadatas"])
        if existing["ids"] and all(m.get("document_hash") == digest for m in existing["metadatas"]):
            return {"status": "unchanged", "chunks": len(existing["ids"]), "sha256": digest}
        sections = extract_document(filename, data)
        chunks = chunk_sections(sections, filename, size, overlap)
        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])
        ids = [f"{hashlib.sha256(filename.encode()).hexdigest()[:16]}:{digest[:16]}:{c.index}" for c in chunks]
        metadatas = [{"source": c.source, "page": c.page or 0, "chunk_index": c.index, "document_hash": digest, "embedding_model": self.embedding_model} for c in chunks]
        self.collection.add(ids=ids, documents=[c.text for c in chunks], metadatas=metadatas)
        return {"status": "replaced" if existing["ids"] else "indexed", "chunks": len(chunks), "sha256": digest}

    def search(self, query: str, top_k: int, threshold: float) -> list[SearchHit]:
        if not query.strip() or self.collection.count() == 0:
            return []
        result = self.collection.query(query_texts=[query], n_results=min(top_k, self.collection.count()), include=["documents", "metadatas", "distances"])
        hits: list[SearchHit] = []
        for chunk_id, text, meta, distance in zip(result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]):
            score = 1.0 - float(distance)
            if score >= threshold:
                hits.append(SearchHit(text, meta["source"], meta.get("page") or None, score, chunk_id))
        return hits

