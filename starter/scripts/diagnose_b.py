import sys, json
sys.path.insert(0, ".")
from src.run import build_pages
from src.chunking import by_paragraph
from src.embeddings import MyEmbedder
from src.store import ChromaStore
from src.evaluation import _sq

bench = {q["id"]: q for q in json.load(open("data/benchmark.json", encoding="utf-8"))}
emb = MyEmbedder()
store = ChromaStore("data/chroma", emb.dimensions)
B = [c for p in build_pages() for c in by_paragraph(p, 1000)]
for qid in sys.argv[1:]:
    q = bench[qid]
    ev = _sq(q["evidence_quote"])
    gold = [c for c in B if c.page in q["gold_page"] and ev in _sq(c.text)]
    print("=" * 10, qid, q["question"])
    if not gold:
        print("  Không chunk B nào chứa trọn evidence (bị cắt qua ranh giới chunk)")
    hits = store.search("B", emb.embed_query(q["question"]), top_k=200)
    rank = {h["chunk_id"]: i + 1 for i, h in enumerate(hits)}
    for c in gold:
        print(f"  gold chunk {c.chunk_id} len={len(c.text)} rank={rank.get(c.chunk_id)}")
        print("   ", repr(c.text[:400]))