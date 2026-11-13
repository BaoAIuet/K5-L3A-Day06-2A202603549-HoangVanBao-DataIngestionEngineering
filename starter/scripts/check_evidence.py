import sys, json
sys.path.insert(0, ".")
from src.ingestion import normalize_text

def sq(s): return "".join(ch for ch in s.lower() if ch.isalnum())

items = json.load(open("data/benchmark.json", encoding="utf-8"))
bad = 0
for q in items:
    ok = False
    for p in q["gold_page"]:
        raw = open(f"data/processed/pages/page_{p:03d}.txt", encoding="utf-8").read()
        if sq(q["evidence_quote"]) in sq(normalize_text(raw)):
            ok = True
    if not ok:
        bad += 1
        print("KHÔNG KHỚP:", q["id"], q["gold_page"])
print(f"{len(items) - bad}/{len(items)} câu có evidence khớp sau normalize")