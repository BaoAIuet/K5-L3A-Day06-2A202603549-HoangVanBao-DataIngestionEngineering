import sys, json, unicodedata
from pypdf import PdfReader

def norm(t):
    return unicodedata.normalize("NFC", t or "").strip()

path = sys.argv[1]
reader = PdfReader(path)
rows = []
for i, page in enumerate(reader.pages, start=1):
    text = norm(page.extract_text())
    rows.append({"page": i, "chars": len(text), "suspect": len(text) < 300})

print(f"Tổng trang vật lý: {len(rows)}")
print(f"Trang nghi ngờ (<300 ký tự): {[r['page'] for r in rows if r['suspect']]}")
with open(path + ".pages.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)