import json, re, unicodedata

def norm(s):
    s = unicodedata.normalize("NFC", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("\u00ad", "")
    s = re.sub(r"-\s+", "-", s)   # gộp "well- understood" thành "well-understood"
    return re.sub(r"\s+", " ", s).strip().casefold()

items = json.load(open("data/benchmark.json", encoding="utf-8"))
bad = 0
for q in items:
    pages = q["gold_page"] if isinstance(q["gold_page"], list) else [q["gold_page"]]
    text = " ".join(
        norm(open(f"data/processed/pages/page_{p:03d}.txt", encoding="utf-8").read())
        for p in pages
    )
    if norm(q["evidence_quote"]) not in text:
        bad += 1
        print("KHÔNG TÌM THẤY evidence:", q["id"], pages)
print(f"{len(items)} câu, {bad} câu lỗi. dev={sum(q['split']=='dev' for q in items)}, "
      f"test={sum(q['split']=='test' for q in items)}, "
      f"filter={sum(bool(q.get('filter')) for q in items)}")