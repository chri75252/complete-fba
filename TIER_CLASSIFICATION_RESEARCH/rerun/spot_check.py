"""
Print 6 sample rows for each of 4 transition buckets for each supplier,
so we can eyeball whether the new tiers are sensible.
"""
import csv, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = Path(__file__).resolve().parents[2]
PREV = REPO / "temp/tier_preview_approach2"

BUCKETS = [
    ("T4->T2 (big win)",       lambda r: r["tier_old"]=="TIER_4_REJECTED" and r["tier"]=="TIER_2_LIKELY"),
    ("T4->T3 (review rescue)", lambda r: r["tier_old"]=="TIER_4_REJECTED" and r["tier"]=="TIER_3_NEEDS_REVIEW"),
    ("T1->T3 (listing swap)",  lambda r: r["tier_old"]=="TIER_1_VERIFIED" and r["tier"]=="TIER_3_NEEDS_REVIEW"),
    ("T4->T4 (still bad)",     lambda r: r["tier_old"]=="TIER_4_REJECTED" and r["tier"]=="TIER_4_REJECTED"),
]

def truncate(s, n=80):
    s = (s or "")[:n]
    return s

for file_label, fname in [("EFG","efg__tier_preview.csv"),
                          ("POUNDWHOLESALE","poundwholesale__tier_preview.csv"),
                          ("ANGEL","angelwholesale__tier_preview.csv")]:
    rows = list(csv.DictReader(open(PREV/fname, "r", encoding="utf-8-sig")))
    print(f"\n========== {file_label} ({len(rows)} rows) ==========")
    for label, pred in BUCKETS:
        matches = [r for r in rows if pred(r)]
        print(f"\n-- {label} [{len(matches)} total] --")
        for r in matches[:4]:
            s = truncate(r["SupplierTitle"])
            a = truncate(r["AmazonTitle"])
            prob = r.get("posterior_match_probability","")
            sim = r.get("title_similarity","")
            shared = r.get("shared_tokens","")
            ean_sup = r.get("EAN","") or "-"
            ean_amz = r.get("EAN_OnPage","") or "-"
            ean_match = r.get("ean_exact_match","")
            flags = r.get("flags","")
            print(f"  SUP: {s}")
            print(f"  AMZ: {a}")
            print(f"  EAN: sup={ean_sup} amz={ean_amz} match={ean_match}")
            print(f"  prob={prob} sim={sim} shared={shared}")
            print(f"  flags={flags}")
            print()
