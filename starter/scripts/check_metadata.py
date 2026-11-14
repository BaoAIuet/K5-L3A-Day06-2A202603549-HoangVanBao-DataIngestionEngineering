import chromadb

CH = {2: (35, 58), 13: (375, 399)}
REQ = ["document_id", "source", "page", "chapter", "chunk_index", "strategy"]
client = chromadb.PersistentClient(path="data/chroma_v2_b1000")

for label in ("A", "B"):
    col = client.get_collection(f"chunks_{label}")
    res = col.get(include=["metadatas", "documents"])
    n = len(res["ids"])
    full = right = 0
    for cid, m, d in zip(res["ids"], res["metadatas"], res["documents"]):
        has_all = all(m.get(k) not in (None, "") for k in REQ) and bool(d.strip())
        full += has_all
        if has_all:
            lo, hi = CH.get(m["chapter"], (0, -1))
            ok = (lo <= m["page"] <= hi
                  and m["document_id"] == "principles-management"
                  and f"-p{m['page']:03d}-" in cid)
            right += ok
    print(f"{label}: đủ trường {full}/{n}; nhất quán (trang thuộc đúng chương, chunk_id khớp trang) {right}/{n}")