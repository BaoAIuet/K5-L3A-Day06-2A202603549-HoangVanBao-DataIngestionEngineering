import csv
from collections import defaultdict

def avg(path, key_col, score_col):
    g = defaultdict(list)
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        v = r[score_col].strip()
        if v != "":
            g[r[key_col]].append(float(v))
    return {k: (round(sum(v) / len(v), 2), len(v)) for k, v in sorted(g.items())}

print("Coherence (mean 0-2, n):", avg("results/audit_coherence_v2_b1000.csv", "strategy", "coherence_0_2"))
print("Grounding dev (mean 0-2, n):", avg("results/audit_grounding_dev_v2_b1000.csv", "strategy", "grounding_0_2"))
try:
    print("Grounding test (mean 0-2, n):", avg("results/audit_grounding_test.csv", "strategy", "grounding_0_2"))
except FileNotFoundError:
    pass