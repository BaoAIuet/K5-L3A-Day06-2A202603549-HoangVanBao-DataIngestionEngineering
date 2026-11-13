"""Chroma persistent vector store (one collection per strategy, cosine distance)."""
from typing import Any
import chromadb
from .models import Chunk

ALLOWED_FILTERS = {"chapter", "page", "document_id", "section"}


class ChromaStore:
    def __init__(self, path: str, dimensions: int) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be > 0")
        self.dim = dimensions
        self.client = chromadb.PersistentClient(path=path)

    def create_schema(self) -> None:
        """Collections are created lazily; this just verifies the client works."""
        self.client.heartbeat()

    def _col(self, strategy: str):
        return self.client.get_or_create_collection(
            name=f"chunks_{strategy}", metadata={"hnsw:space": "cosine"})

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors differ in length")
        if any(len(v) != self.dim for v in vectors):
            raise ValueError(f"vector dimension != {self.dim}")
        col = self._col(strategy)
        ids, docs, metas = [], [], []
        for c in chunks:
            m = {k: v for k, v in c.metadata.items()
                 if isinstance(v, (str, int, float, bool))}   # Chroma rejects None/dict
            m.update(document_id=c.document_id, source=c.source, page=c.page)
            ids.append(c.chunk_id)
            docs.append(c.text)
            metas.append(m)
        for i in range(0, len(ids), 500):
            col.upsert(ids=ids[i:i + 500], embeddings=vectors[i:i + 500],
                       documents=docs[i:i + 500], metadatas=metas[i:i + 500])
        # remove obsolete chunks of re-ingested documents
        keep = set(ids)
        for doc in {c.document_id for c in chunks}:
            existing = col.get(where={"document_id": doc}, include=[])["ids"]
            stale = [x for x in existing if x not in keep]
            if stale:
                col.delete(ids=stale)

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        conds = []
        for k, v in (filters or {}).items():
            if k not in ALLOWED_FILTERS:
                raise ValueError(f"filter not allowed: {k}")
            conds.append({k: v})
        where = None if not conds else (conds[0] if len(conds) == 1 else {"$and": conds})
        res = self._col(strategy).query(query_embeddings=[query_vector], n_results=top_k,
                                        where=where, include=["documents", "metadatas", "distances"])
        out = []
        for cid, text, meta, dist in zip(res["ids"][0], res["documents"][0],
                                         res["metadatas"][0], res["distances"][0]):
            out.append(dict(chunk_id=cid, text=text, score=1.0 - float(dist),
                            document_id=meta.get("document_id"), source=meta.get("source"),
                            page=meta.get("page"), chapter=meta.get("chapter"),
                            section=meta.get("section"), metadata=meta))
        return out