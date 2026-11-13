"""Pipeline: ingest -> chunk (A/B/C) -> embed -> store -> retrieve -> evaluate."""
import argparse, csv, json, os, random, time
from pathlib import Path
from dotenv import load_dotenv
from .chunking import by_paragraph, fixed_size
from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .ingestion import load_pdf, normalize_text
from .store import ChromaStore

DOC_ID = "principles-management"
SOURCE = "https://assets.openstax.org/oscms-prodcms/media/documents/principles-management_-_WEB.pdf"
PDF, BENCH, RESULTS = Path("data/raw/principles-management.pdf"), Path("data/benchmark.json"), Path("results")
CHAPTERS = {2: (35, 58), 13: (375, 399)}
A_SIZE, A_OVERLAP, TOP_K = 1000, 100, 3


def build_pages():
    nums = [p for a, b in CHAPTERS.values() for p in range(a, b + 1)]
    pages = load_pdf(PDF, DOC_ID, SOURCE, nums)
    for p in pages:
        p.metadata["chapter"] = next(c for c, (a, b) in CHAPTERS.items() if a <= p.page <= b)
        p.text = normalize_text(p.text)
    return pages


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "test"], default="dev")
    ap.add_argument("--b-max", type=int, default=1000)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    bmax, tag = args.b_max, args.tag
    load_dotenv()
    t0 = time.time()
    RESULTS.mkdir(exist_ok=True)

    pages = build_pages()
    content = [p for p in pages if not p.metadata["low_text"]]
    assert len(content) >= 30, f"only {len(content)} content pages"
    bench = [q for q in json.load(open(BENCH, encoding="utf-8")) if q["split"] == args.split]

    chunks = {"A": [c for p in pages for c in fixed_size(p, A_SIZE, A_OVERLAP)],
              "B": [c for p in pages for c in by_paragraph(p, bmax)]}
    print({k: len(v) for k, v in chunks.items()}, "chunks", flush=True)

    emb = MyEmbedder()
    # mỗi lần chạy dùng thư mục Chroma riêng để các cấu hình khác nhau không lẫn nhau
    store = ChromaStore(os.environ.get("CHROMA_PATH", f"data/chroma{tag}"), emb.dimensions)
    store.create_schema()

    t_embed = time.time()
    for s, cs in chunks.items():
        texts, vecs = [c.text for c in cs], []
        for i in range(0, len(texts), 64):
            vecs += emb.embed_documents(texts[i:i + 64])
            print(f"  embed {s}: {min(i + 64, len(texts))}/{len(texts)}", flush=True)
        store.upsert(s, cs, vecs)
    t_embed = time.time() - t_embed

    traces = []
    for q in bench:
        qv = emb.embed_query(q["question"])
        for label, table, flt in (("A", "A", None), ("B", "B", None), ("C", "B", q["filter"])):
            tr = evaluate_query(q, store.search(table, qv, TOP_K, flt))
            tr["strategy"] = label
            traces.append(tr)

    summary = summarize(traces)
    with open(RESULTS / f"traces_{args.split}{tag}.jsonl", "w", encoding="utf-8") as f:
        for t in traces:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    json.dump({"split": args.split, "summary": summary,
               "config": {"model": emb.model_name, "dims": emb.dimensions,
                          "A": {"size": A_SIZE, "overlap": A_OVERLAP}, "B": {"max_size": bmax},
                          "C": "B chunks + metadata filter (chapter) when the question has one",
                          "content_pages": len(content), "n_chunks": {k: len(v) for k, v in chunks.items()},
                          "embed_seconds": round(t_embed, 1), "total_seconds": round(time.time() - t0, 1)}},
              open(RESULTS / f"summary_{args.split}{tag}.json", "w", encoding="utf-8"), indent=2)

    # manual-audit sheets (fill the blank columns by hand)
    rnd = random.Random(42)
    with open(RESULTS / f"audit_coherence{tag}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["strategy", "chunk_id", "page", "text", "coherence_0_2", "note"])
        for s in ("A", "B"):
            for c in rnd.sample(chunks[s], min(20, len(chunks[s]))):
                w.writerow([s, c.chunk_id, c.page, c.text, "", ""])
    exp = {q["id"]: q["expected_answer"] for q in bench}
    with open(RESULTS / f"audit_grounding_{args.split}{tag}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["strategy", "id", "question", "expected_answer", "top3_pages", "top3_text",
                    "grounding_0_2", "note"])
        for t in traces:
            w.writerow([t["strategy"], t["id"], t["question"], exp[t["id"]],
                        [x["page"] for x in t["top3"]],
                        " || ".join(x["text"] for x in t["top3"]), "", ""])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()