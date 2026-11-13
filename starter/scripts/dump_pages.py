import os, unicodedata
from pypdf import PdfReader

reader = PdfReader("data/raw/principles-management.pdf")
os.makedirs("data/processed/pages", exist_ok=True)
for a, b in [(35, 58), (375, 399)]:
    for p in range(a, b + 1):
        text = unicodedata.normalize("NFC", reader.pages[p - 1].extract_text() or "")
        with open(f"data/processed/pages/page_{p:03d}.txt", "w", encoding="utf-8") as f:
            f.write(text)
print("Xong")