import csv, sys

path = "results/audit_grounding_dev_v2_b1000.csv"
rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
hi = int(sys.argv[2]) if len(sys.argv) > 2 else min(lo + 2, len(rows))
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 700
for i in range(lo, hi + 1):
    r = rows[i - 1]
    print("=" * 80)
    print(f'#{i}  cấu hình {r["strategy"]}  câu {r["id"]}  trang top-3: {r["top3_pages"]}')
    print("HỎI    :", r["question"])
    print("ĐÁP ÁN :", r["expected_answer"])
    for k, t in enumerate(r["top3_text"].split(" || "), 1):
        print(f"  [{k}] {t[:limit]}")