import csv, json, os, sys

def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)

def save(path, fields, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def req(r):
    return str(r["in_required_5"]).strip().lower() == "true"

def to_int(x):
    try:
        return int(float(x))
    except Exception:
        return None

def label_grounding():
    path = "results/audit_grounding_test.csv"
    crit_path = "results/audit_test_criteria.json"
    criteria = json.load(open(crit_path, encoding="utf-8")) if os.path.exists(crit_path) else {}
    traces = {}
    for l in open("results/traces_test.jsonl", encoding="utf-8"):
        t = json.loads(l)
        traces[(t["id"], t["strategy"])] = t
    fields, rows = read(path)
    todo = sorted([r for r in rows if req(r) and r["score"].strip() == ""],
                  key=lambda r: (r["qid"], r["strategy"]))
    print(len(todo), "dòng grounding chưa chấm")
    for r in todo:
        t = traces[(r["qid"], r["strategy"])]
        print("\n" + "=" * 80)
        print(f"{r['qid']}  cấu hình {r['strategy']}  gold_page={r['gold_page']}")
        print("HỎI    :", r["question"])
        print("ĐÁP ÁN :", r["expected_answer"])
        if r["qid"] not in criteria:
            criteria[r["qid"]] = input("Ý CỐT LÕI bắt buộc của đáp án (1 dòng, dùng chung cho A/B/C): ").strip()
            json.dump(criteria, open(crit_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        else:
            print("Ý cốt lõi:", criteria[r["qid"]])
        for c in t["top3"]:
            print(f"--- [{c['rank']}] trang {c['page']}")
            print(c["text"])
        while True:
            s = input("Điểm 0/1/2 (q = lưu và thoát): ").strip()
            if s in ("0", "1", "2", "q"):
                break
        if s == "q":
            return
        r["score"] = s
        r["reason"] = input("Lý do (1 dòng, nêu chunk/trang/ý còn thiếu): ").strip()
        save(path, fields, rows)
    print("Xong grounding.")

def label_metadata():
    path = "results/audit_metadata_test.csv"
    fields, rows = read(path)
    todo = sorted([r for r in rows if req(r) and r["metadata_ok"].strip() == ""],
                  key=lambda r: (r["strategy"], r["qid"], int(r["rank"])))
    print(len(todo), "dòng metadata chưa chấm")
    for r in todo:
        pt, ps = to_int(r["page_in_trace"]), to_int(r["page_in_store"])
        cs, ce = to_int(r["chapter_in_store"]), to_int(r["chapter_expected_from_page"])
        have = ps is not None and cs is not None and r["source_in_store"].strip() != ""
        suggest = None
        if have:
            ok_source = "principles-management" in r["source_in_store"].strip()
            ok_page = (ps == pt)
            ok_chapter = (cs == ce)
            ok_chunk_id = (f"p{pt:03d}" in r["chunk_id"])
            suggest = "1" if (ok_source and ok_page and ok_chapter and ok_chunk_id) else "0"
        print("\n" + "-" * 80)
        print(f"{r['qid']} cấu hình {r['strategy']} hạng {r['rank']}  chunk_id={r['chunk_id']}")
        print(f"  trace: trang {pt} | store: source={r['source_in_store']} trang={ps} chương={cs} | "
              f"chương đúng theo trang={ce} | tự động tìm thấy trên trang: {r['text_found_on_page(auto)']}")
        print(f"  gợi ý của máy: {suggest}")
        while True:
            s = input("metadata_ok [Enter=gợi ý máy; 1/0; thêm p nếu đã mở PDF kiểm tra, vd 1p; q=thoát]: ").strip().lower()
            if s == "q":
                return
            if s == "" and suggest is not None:
                val, pdf = suggest, False
                break
            if s in ("1", "0", "1p", "0p"):
                val, pdf = s[0], s.endswith("p")
                break
        note = input("Ghi chú (Enter nếu không có): ").strip()
        r["metadata_ok"] = val
        r["note"] = (note + " " if note else "") + ("pdf_checked" if pdf else "")
        save(path, fields, rows)
    print("Xong metadata.")

mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode == "grounding":
    label_grounding()
elif mode == "metadata":
    label_metadata()
else:
    print("Dùng: python scripts\\label_test.py grounding | metadata")