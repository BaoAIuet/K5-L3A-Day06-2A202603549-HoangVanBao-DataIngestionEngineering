import sys
sys.path.insert(0, ".")
from src.normalize import clean_page

n = sys.argv[1]
raw = open(f"data/processed/pages/page_{int(n):03d}.txt", encoding="utf-8").read()
blocks, log = clean_page(raw)
for b in blocks:
    print(f"[{b['type']}] {b['text'][:110]}")
print("\nĐã loại/sửa:", log)
