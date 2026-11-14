import json

def load(path):
    out = {}
    for l in open(path, encoding="utf-8"):
        r = json.loads(l)
        out[(r["id"], r["strategy"])] = r["first_evidence_rank"]
    return out

v1 = load("results/traces_dev.jsonl")
v2 = load("results/traces_dev_v2_b1000.jsonl")
ids = sorted({k[0] for k in v1})
f = lambda x: "-" if x is None else str(x)
print("hạng evidence đầu tiên (- = không có trong top-3)")
print("câu   | v1 A B C | v2 A B C")
for q in ids:
    a = " ".join(f(v1[(q, s)]) for s in "ABC")
    b = " ".join(f(v2[(q, s)]) for s in "ABC")
    print(f"{q:5} | {a:8} | {b}")
for name, d in (("v1", v1), ("v2", v2)):
    for s in "ABC":
        ranks = [d[(q, s)] for q in ids]
        print(name, s, "Hit@1:", sum(r == 1 for r in ranks), "Hit@3:", sum(r is not None for r in ranks))