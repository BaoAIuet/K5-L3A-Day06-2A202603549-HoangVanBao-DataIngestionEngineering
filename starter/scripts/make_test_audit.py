import csv, json, os, re, unicodedata
from dotenv import load_dotenv

load_dotenv()
REQUIRED = ["q11", "q12", "q13", "q15", "q16"]  # quy tắc ghi trước: 5 id nhỏ nhất của test
TRACE = "results/traces_test.jsonl"
CHROMA = os.environ.get("CHROMA_PATH", "data/chroma")

def norm(s):
    s = unicodedata.normalize("NFC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("\u00ad", "")
    s = re.sub(r"-\s+", "-", s)
    return re.sub(r"\s+", " ", s).strip().casefold()

def chapter_of(p):
    return 2 if 35 <= p <= 58 else 13 if 375 <= p <= 399 else None

def page_text(p):
    path = f"data/processed/pages/page_{p:03d}.txt"
    return norm(open(path, encoding="utf-8").read()) if os.path.exists(path) else ""

def load_store_meta():
    metas = {}
    try:
        import chromadb
        client = chromadb.PersistentClient(CHROMA)
        for c in client.list_collections():
            col = client.get_collection(getattr(c, "name", c))
            data = col.get(include=["metadatas"])
            for i, m in zip(data["ids"], data["metadatas"]):
                metas.setdefault(i, []).append(m)
    except Exception as e:
        print("Không đọc được metadata từ Chroma:", e)
    return metas

bench = {q["id"]: q for q in json.load(open("data/benchmark.json", encoding="utf-8"))}
rows = [json.loads(l) for l in open(TRACE, encoding="utf-8")]
metas = load_store_meta()

def store_meta(cid):
    ms = metas.get(cid, [])
    if not ms:
        return {}
    return ms[0] if all(m == ms[0] for m in ms) else {"source": "AMBIGUOUS"}

def found_on_page(text, page):
    t, pt = norm(text), page_text(page)
    if not t or not pt:
        return "?"
    mid = len(t) // 2
    return "Y" if (t[:60] in pt or t[mid:mid + 60] in pt) else "N"

grounding, metadata = [], []
for r in sorted(rows, key=lambda r: (r["id"], r["strategy"])):
    b = bench[r["id"]]
    req = r["id"] in REQUIRED
    grounding.append({
        "qid": r["id"], "in_required_5": req, "strategy": r["strategy"],
        "filter": json.dumps(r["filter"]), "question": r["question"],
        "expected_answer": b["expected_answer"], "gold_page": b["gold_page"],
        "top3_pages": [c["page"] for c in r["top3"]],
        "top3_text": "\n---\n".join(f"[{c['rank']}] p{c['page']}: {c['text'][:900]}" for c in r["top3"]),
        "score": "", "reason": "",
    })
    for c in r["top3"]:
        m = store_meta(c["chunk_id"])
        metadata.append({
            "qid": r["id"], "in_required_5": req, "strategy": r["strategy"], "rank": c["rank"],
            "chunk_id": c["chunk_id"], "page_in_trace": c["page"],
            "source_in_store": m.get("source", ""), "chapter_in_store": m.get("chapter", ""),
            "page_in_store": m.get("page", ""),
            "chapter_expected_from_page": chapter_of(c["page"]),
            "filter": json.dumps(r["filter"]),
            "text_found_on_page(auto)": found_on_page(c["text"], c["page"]),
            "metadata_ok": "", "note": "",
        })

def write(path, data):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)
    print("Đã ghi", path, len(data), "dòng")

write("results/audit_grounding_test.csv", grounding)
write("results/audit_metadata_test.csv", metadata)