import json, random

SEED = 20261113
path = "data/benchmark.json"
items = json.load(open(path, encoding="utf-8"))

# Ứng viên: câu đang ở test và KHÔNG dùng filter, nhóm theo trang gold
groups = {}
for it in items:
    if it["split"] == "test" and it["filter"] is None:
        groups.setdefault(it["gold_page"][0], []).append(it)

print("Ứng viên theo trang:", {p: [x["id"] for x in v] for p, v in groups.items()})
assert set(groups) == {57, 394}, "Nhóm trang khác dự kiến, dừng lại để kiểm tra"

random.seed(SEED)
for page in (57, 394):
    chosen = random.choice(groups[page])
    chosen["split"] = "dev"
    print(f"Chuyển {chosen['id']} (trang {page}) sang dev")

json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)