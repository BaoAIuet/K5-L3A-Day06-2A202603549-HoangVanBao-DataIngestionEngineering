import csv, shutil

PATH = "results/audit_coherence_v2_b1000.csv"

# Điểm nháp theo đúng thứ tự dòng: 20 dòng A rồi 20 dòng B.
# SỬA lại số nào bạn không đồng ý TRƯỚC khi chạy. Đây phải là nhãn của bạn.
SCORES = [
    1, 1, 1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 0, 1, 2, 1,   # A
    2, 1, 0, 2, 1, 1, 1, 2, 2, 0, 2, 2, 2, 1, 2, 2, 2, 1, 2, 0,   # B
]

NOTES = {
    "principles-management-p399-fx04": "bắt đầu giữa câu, kết thúc bằng tiêu đề MANAGERIAL LEADERSHIP",
    "principles-management-p037-fx00": "mở đầu là danh sách URL nguồn",
    "principles-management-p036-fx04": "ý liền mạch nhưng cuối là URL nguồn bị cắt",
    "principles-management-p041-fx00": "lẫn câu hỏi ôn tập và tiêu đề mục",
    "principles-management-p393-fx03": "cắt giữa câu ở đầu và cuối",
    "principles-management-p041-fx02": "cắt giữa câu ở đầu và cuối",
    "principles-management-p053-fx01": "cắt giữa câu ở đầu và cuối",
    "principles-management-p049-fx01": "cắt giữa câu ở đầu và cuối",
    "principles-management-p043-fx02": "cắt giữa câu ở đầu và cuối",
    "principles-management-p040-fx01": "cắt giữa câu ở đầu và cuối",
    "principles-management-p036-pg03": "một câu đơn lẻ mất ngữ cảnh",
    "principles-management-p058-pg01": "lẫn mảnh bảng và dòng Table 2.3 (Attribution)",
    "principles-management-p043-pg00": "lẫn câu hỏi ôn tập và tiêu đề mục kế tiếp",
    "principles-management-p385-pg01": "trọn ý nhưng cuối là dòng trích dẫn tham khảo",
    "principles-management-p045-pg00": "bắt đầu giữa đoạn",
    "principles-management-p391-pg03": "gộp cuối một mục và đầu mục tiếp theo",
    "principles-management-p388-pg02": "bullet không có câu dẫn",
    "principles-management-p049-pg04": "gộp hai mục",
    "principles-management-p393-pg05": "cắt giữa câu ở cuối",
}

shutil.copy(PATH, PATH + ".bak")
rows = list(csv.DictReader(open(PATH, encoding="utf-8-sig", newline="")))
fields = list(rows[0].keys())
assert len(rows) == 40 and len(SCORES) == 40, (len(rows), len(SCORES))

for r, s in zip(rows, SCORES):
    r["coherence_0_2"] = str(s)
    if r["chunk_id"] in NOTES:
        r["note"] = NOTES[r["chunk_id"]]

with open(PATH, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

for s in ("A", "B"):
    v = [int(r["coherence_0_2"]) for r in rows if r["strategy"] == s]
    print(s, "mean =", round(sum(v) / len(v), 2), "n =", len(v))