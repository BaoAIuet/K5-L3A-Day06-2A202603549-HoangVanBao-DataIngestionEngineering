import csv, shutil

PATH = "results/audit_grounding_dev_v2_b1000.csv"

# 45 điểm theo thứ tự #1..#45, mỗi câu 3 số (A, B, C).
# SỬA số nào bạn không đồng ý TRƯỚC khi chạy. Đây phải là nhãn của bạn.
SCORES = [
    2, 2, 2,   # q01
    2, 0, 0,   # q02
    2, 2, 2,   # q03
    2, 2, 2,   # q04
    2, 2, 2,   # q05
    2, 2, 2,   # q06
    2, 0, 0,   # q07
    2, 0, 0,   # q08
    2, 2, 2,   # q09
    2, 2, 2,   # q10
    2, 2, 2,   # q14
    2, 2, 2,   # q18
    2, 0, 0,   # q19
    2, 2, 2,   # q20
    2, 2, 2,   # q21
]

NOTES = {
    5: "top-3 không có đoạn nêu các yếu tố đặt nguyên liệu; chunk đúng nằm ngoài top-3",
    6: "giống #5 (C dùng chunk của B, câu không có filter)",
    20: "top-3 là các đoạn định nghĩa lãnh đạo chung (tr. 376, 378); chunk chứa 'emergent leaders' nằm ngoài top-3",
    21: "giống #20",
    23: "top-3 nói về follower và giới tính (tr. 379, 389); không có đoạn về đặc điểm khiến người ta không đi theo",
    24: "giống #23",
    38: "top-3 nói về bias 'similar to me' và bảng tóm tắt; không có đoạn nêu cách giảm bias",
    39: "giống #38",
}

shutil.copy(PATH, PATH + ".bak")
rows = list(csv.DictReader(open(PATH, encoding="utf-8-sig", newline="")))
fields = list(rows[0].keys())
assert len(rows) == 45 and len(SCORES) == 45, (len(rows), len(SCORES))

for i, (r, s) in enumerate(zip(rows, SCORES), 1):
    assert s in (0, 1, 2), (i, s)
    r["grounding_0_2"] = str(s)
    if i in NOTES:
        r["note"] = NOTES[i]

with open(PATH, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

for s in ("A", "B", "C"):
    v = [int(r["grounding_0_2"]) for r in rows if r["strategy"] == s]
    dist = {k: v.count(k) for k in (0, 1, 2)}
    print(s, "mean =", round(sum(v) / len(v), 2), "n =", len(v), "phân bố 0/1/2 =", dist)