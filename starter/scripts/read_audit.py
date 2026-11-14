import csv, sys

qids = sys.argv[1:]
out = open("results/read_audit_test.txt", "w", encoding="utf-8")
for qid in qids:
    for r in csv.DictReader(open("results/audit_grounding_test.csv", encoding="utf-8-sig")):
        if r["qid"] == qid:
            out.write("=" * 90 + "\n")
            out.write(f"{r['qid']}  cau hinh {r['strategy']}  filter={r['filter']}  gold_page={r['gold_page']}\n")
            out.write("HOI    : " + r["question"] + "\n")
            out.write("DAP AN : " + r["expected_answer"] + "\n")
            out.write(r["top3_text"] + "\n")
out.close()
print("Da ghi results/read_audit_test.txt")