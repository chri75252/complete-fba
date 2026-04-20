"""
Audit pack-size extraction accuracy on EAN-matched rows across three suppliers.
Measures how often pack is extractable from both sides, how often it agrees,
and surfaces a sample for manual review so we can judge reliability.
"""
from __future__ import annotations
import csv, json, sys, io
from pathlib import Path
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "FINAL STALE/agent analyses/initial_probabilistic_implementation_package"))
from probabilistic_matcher_prototype import extract_pack  # noqa

PREV = REPO / "temp/tier_preview_approach2"
FILES = [
    ("EFG",           PREV / "efg__tier_preview.csv"),
    ("POUNDWHOLESALE",PREV / "poundwholesale__tier_preview.csv"),
    ("ANGEL",         PREV / "angelwholesale__tier_preview.csv"),
]

def classify_pack(sup_title, amz_title):
    """Returns one of:
       BOTH_EQUAL, BOTH_DIFFERENT, ONLY_SUP, ONLY_AMZ, NEITHER
    """
    p_sup = extract_pack(sup_title)
    p_amz = extract_pack(amz_title)
    if p_sup is not None and p_amz is not None:
        return "BOTH_EQUAL" if p_sup == p_amz else "BOTH_DIFFERENT", p_sup, p_amz
    if p_sup is not None: return "ONLY_SUP", p_sup, None
    if p_amz is not None: return "ONLY_AMZ", None, p_amz
    return "NEITHER", None, None

def main():
    overall_counts = Counter()
    per_supplier = {}
    manual_review_samples = {"BOTH_EQUAL":[], "BOTH_DIFFERENT":[], "ONLY_SUP":[], "ONLY_AMZ":[], "NEITHER":[]}
    for label, path in FILES:
        rows = list(csv.DictReader(open(path, "r", encoding="utf-8-sig")))
        ean_match_rows = [r for r in rows if str(r.get("ean_exact_match","")).lower() in ("true","1")]
        counts = Counter()
        for r in ean_match_rows:
            cat, p_sup, p_amz = classify_pack(r["SupplierTitle"], r["AmazonTitle"])
            counts[cat] += 1
            overall_counts[cat] += 1
            if len(manual_review_samples[cat]) < 10:
                manual_review_samples[cat].append({
                    "supplier": label,
                    "sup_title": r["SupplierTitle"][:110],
                    "amz_title": r["AmazonTitle"][:110],
                    "extracted_sup_pack": p_sup,
                    "extracted_amz_pack": p_amz,
                    "ean": r.get("EAN","")[:15],
                })
        per_supplier[label] = {
            "total_ean_matched": len(ean_match_rows),
            "buckets": dict(counts),
        }
        print(f"\n=== {label} — {len(ean_match_rows)} EAN-matched rows ===")
        for b in ["BOTH_EQUAL","BOTH_DIFFERENT","ONLY_SUP","ONLY_AMZ","NEITHER"]:
            c = counts[b]; pct = (c/len(ean_match_rows)*100) if ean_match_rows else 0
            print(f"  {b:16s} {c:6d}  ({pct:5.1f}%)")

    print("\n\n=============  MANUAL SAMPLE (10 per bucket)  =============")
    for bucket in ["BOTH_EQUAL","BOTH_DIFFERENT","ONLY_SUP","ONLY_AMZ","NEITHER"]:
        print(f"\n--- {bucket} ---")
        for s in manual_review_samples[bucket][:10]:
            print(f"  [{s['supplier']}] sup_pack={s['extracted_sup_pack']}  amz_pack={s['extracted_amz_pack']}  ean={s['ean']}")
            print(f"    SUP: {s['sup_title']}")
            print(f"    AMZ: {s['amz_title']}")

    print("\n\n=============  OVERALL  =============")
    total = sum(overall_counts.values())
    for b in ["BOTH_EQUAL","BOTH_DIFFERENT","ONLY_SUP","ONLY_AMZ","NEITHER"]:
        c = overall_counts[b]; pct = c/total*100 if total else 0
        print(f"  {b:16s} {c:6d}  ({pct:5.1f}%)")
    print(f"  TOTAL            {total:6d}")

    out = REPO / "TIER_CLASSIFICATION_RESEARCH/rerun/pack_extraction_audit.json"
    out.write_text(json.dumps({
        "per_supplier": per_supplier,
        "overall": dict(overall_counts),
        "samples": manual_review_samples,
    }, indent=2))

if __name__ == "__main__":
    main()
