import json
import sys
gold = {q["id"]: q["gold_page"] for q in json.load(open("data/benchmark.json", encoding="utf-8"))}
rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "results/traces_dev.jsonl", encoding="utf-8")]
for strat in ("A", "B"):
    print("=" * 20, strat)
    for r in rows:
        if r["strategy"] != strat or r["hit_at_1"]:
            continue
        print(f'{r["id"]} [{r["type"]}] gold_page={gold[r["id"]]} first_evidence_rank={r["first_evidence_rank"]}')
        print("  Q:", r["question"])
        for t in r["top3"]:
            print(f'   #{t["rank"]} p{t["page"]} score={t["score"]:.3f} ev={t["evidence_hit"]} :: {t["text"][:90]!r}')