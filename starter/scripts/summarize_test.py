import csv, json
from collections import defaultdict

def rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))

def required(r):
    return str(r["in_required_5"]).strip().lower() == "true"

# ---- Grounding (5 câu bắt buộc) ----
g = [r for r in rows("results/audit_grounding_test.csv") if required(r)]
print("=== GROUNDING test (5 câu: q11, q12, q13, q15, q16) ===")
for s in "ABC":
    rs = [r for r in g if r["strategy"] == s]
    done = [r for r in rs if r["score"].strip() != ""]
    dist = {k: sum(1 for r in done if r["score"].strip() == str(k)) for k in (0, 1, 2)}
    mean = round(sum(int(r["score"]) for r in done) / len(done), 2) if done else None
    print(f"{s}: n={len(done)}/{len(rs)} đã chấm, phân bố 0/1/2 = {dist}, trung bình = {mean}")
    miss = [r["qid"] for r in rs if r["score"].strip() == ""]
    if miss:
        print("   CHƯA CHẤM:", miss)
    for r in done:
        if r["reason"].strip() == "":
            print("   thiếu lý do:", r["qid"], s)

# ---- Metadata (5 câu x top-3) ----
m = [r for r in rows("results/audit_metadata_test.csv") if required(r)]
print("\n=== METADATA test (5 câu x top-3) ===")
for s in "ABC":
    rs = [r for r in m if r["strategy"] == s]
    done = [r for r in rs if r["metadata_ok"].strip() != ""]
    ok = sum(1 for r in done if r["metadata_ok"].strip() == "1")
    print(f"{s}: đủ và đúng {ok}/{len(done)} (tổng {len(rs)} bản ghi)")
    for r in done:
        if r["metadata_ok"].strip() != "1":
            print("   lỗi:", r["qid"], "rank", r["rank"], r["chunk_id"], "|", r["note"])
    if len(done) < len(rs):
        print(f"   CHƯA CHẤM {len(rs) - len(done)} bản ghi")

# ---- Tuân thủ filter ----
def chapter(p):
    return 2 if 35 <= p <= 58 else 13 if 375 <= p <= 399 else None

print("\n=== TUÂN THỦ FILTER (top-3 toàn thuộc đúng chương được lọc) ===")
allg = rows("results/audit_grounding_test.csv")
for s in "ABC":
    res = []
    for r in allg:
        if r["strategy"] != s or r["filter"].strip() in ("null", ""):
            continue
        want = json.loads(r["filter"])["chapter"]
        pages = json.loads(r["top3_pages"])
        res.append((r["qid"], all(chapter(p) == want for p in pages), required(r)))
    req = [x for x in res if x[2]]
    print(f"{s}: 5 câu bắt buộc: {sum(x[1] for x in req)}/{len(req)}; tất cả câu filter của test: {sum(x[1] for x in res)}/{len(res)}")
    print("   chi tiết:", [(q, ok) for q, ok, _ in res])