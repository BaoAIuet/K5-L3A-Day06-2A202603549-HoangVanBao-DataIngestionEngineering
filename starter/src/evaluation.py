"""Retrieval evaluation with per-query traces."""
from collections import defaultdict
from typing import Any


def _sq(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    gold_pages, ev = set(question["gold_page"]), _sq(question["evidence_quote"])
    top = []
    for rank, h in enumerate(hits, 1):
        page_ok = h["document_id"] == question["gold_source_id"] and h["page"] in gold_pages
        top.append({"rank": rank, "chunk_id": h["chunk_id"], "page": h["page"], "score": h["score"],
                    "page_hit": page_ok, "evidence_hit": page_ok and ev in _sq(h["text"]),
                    "text": h["text"]})
    first = next((t["rank"] for t in top if t["evidence_hit"]), None)
    return {"id": question["id"], "split": question["split"], "type": question["type"],
            "filter": question["filter"], "question": question["question"],
            "hit_at_1": bool(top and top[0]["evidence_hit"]),
            "hit_at_3": first is not None,
            "page_hit_at_3": any(t["page_hit"] for t in top),
            "first_evidence_rank": first, "top3": top}


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    g = defaultdict(list)
    for t in traces:
        g[f'{t["strategy"]}|{t["split"]}'].append(t)
    out = {}
    for key, ts in sorted(g.items()):
        n = len(ts)
        out[key] = {"n": n,
                    "hit@1": round(sum(t["hit_at_1"] for t in ts) / n, 3),
                    "evidence_hit@3": round(sum(t["hit_at_3"] for t in ts) / n, 3),
                    "page_hit@3": round(sum(t["page_hit_at_3"] for t in ts) / n, 3),
                    "mrr": round(sum(1 / t["first_evidence_rank"] for t in ts
                                     if t["first_evidence_rank"]) / n, 3)}
    return out