import json

def chapter(p):
    return 2 if 35 <= p <= 58 else 13 if 375 <= p <= 399 else None

rows = [json.loads(l) for l in open("results/traces_test.jsonl", encoding="utf-8")]

print("== Câu miss Hit@3")
for r in rows:
    if not r["hit_at_3"]:
        print(r["strategy"], r["id"], r["type"], "| Q:", r["question"])
        for t in r["top3"]:
            print(f'   #{t["rank"]} p{t["page"]} ev={t["evidence_hit"]} :: {t["text"][:90]!r}')

print("\n== Từng câu: Hit@1 và hạng của evidence đầu tiên")
for qid in sorted({r["id"] for r in rows}):
    parts = []
    for s in "ABC":
        r = next(x for x in rows if x["id"] == qid and x["strategy"] == s)
        parts.append(f'{s}: hit@1={int(r["hit_at_1"])} rank={r["first_evidence_rank"]}')
    print(qid, " | ".join(parts))

print("\n== Tuân thủ filter: chapter của top-3 ở các câu có filter")
for r in rows:
    if r["filter"]:
        print(r["strategy"], r["id"], r["filter"], [chapter(t["page"]) for t in r["top3"]])
        