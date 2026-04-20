"""
Rerun pack-extraction audit with extended regex (v2). Pull 50 samples per
bucket per supplier for large-pool manual review. Compare against v1.
"""
from __future__ import annotations
import csv, json, sys, io
from pathlib import Path
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "FINAL STALE/agent analyses/initial_probabilistic_implementation_package"))
from probabilistic_matcher_prototype import extract_pack as extract_pack_v1  # noqa
from pack_extraction_v2 import extract_pack_v2  # noqa

PREV = REPO / "temp/tier_preview_approach2"
FILES = [
    ("EFG",            PREV / "efg__tier_preview.csv"),
    ("POUNDWHOLESALE", PREV / "poundwholesale__tier_preview.csv"),
    ("ANGEL",          PREV / "angelwholesale__tier_preview.csv"),
]

def bucket(p_sup, p_amz):
    if p_sup is not None and p_amz is not None:
        return "BOTH_EQUAL" if p_sup == p_amz else "BOTH_DIFFERENT"
    if p_sup is not None: return "ONLY_SUP"
    if p_amz is not None: return "ONLY_AMZ"
    return "NEITHER"

def main():
    per_supplier_v1 = {}; per_supplier_v2 = {}
    overall_v1 = Counter(); overall_v2 = Counter()
    samples_v2 = {b:[] for b in ("BOTH_EQUAL","BOTH_DIFFERENT","ONLY_SUP","ONLY_AMZ","NEITHER")}
    # Special sample: rows changed status from v1 -> v2 (what v2 unlocked)
    newly_extracted = []
    newly_disagreed = []   # rows that were BOTH_EQUAL in v1 but BOTH_DIFFERENT in v2 (regression risk)
    for label, path in FILES:
        rows = list(csv.DictReader(open(path, "r", encoding="utf-8-sig")))
        ean_rows = [r for r in rows if str(r.get("ean_exact_match","")).lower() in ("true","1")]
        c1, c2 = Counter(), Counter()
        for r in ean_rows:
            st, at = r["SupplierTitle"], r["AmazonTitle"]
            p1s, p1a = extract_pack_v1(st), extract_pack_v1(at)
            p2s, p2a = extract_pack_v2(st), extract_pack_v2(at)
            b1, b2 = bucket(p1s, p1a), bucket(p2s, p2a)
            c1[b1] += 1; c2[b2] += 1
            overall_v1[b1] += 1; overall_v2[b2] += 1
            if len(samples_v2[b2]) < 60:
                samples_v2[b2].append({
                    "supplier": label,
                    "sup_title": st[:120],
                    "amz_title": at[:120],
                    "v1_sup": p1s, "v1_amz": p1a, "v1_bucket": b1,
                    "v2_sup": p2s, "v2_amz": p2a, "v2_bucket": b2,
                    "ean": r.get("EAN","")[:16],
                })
            if b1 != b2:
                rec = {"supplier":label,"sup":st[:120],"amz":at[:120],
                       "v1":(p1s,p1a,b1),"v2":(p2s,p2a,b2)}
                if b2 in ("BOTH_EQUAL","BOTH_DIFFERENT") and b1 not in ("BOTH_EQUAL","BOTH_DIFFERENT"):
                    newly_extracted.append(rec)
                if b1 == "BOTH_EQUAL" and b2 == "BOTH_DIFFERENT":
                    newly_disagreed.append(rec)
        per_supplier_v1[label] = {"total": len(ean_rows), "buckets": dict(c1)}
        per_supplier_v2[label] = {"total": len(ean_rows), "buckets": dict(c2)}
        print(f"\n=== {label} — {len(ean_rows)} EAN-matched rows ===")
        print(f"  bucket             v1        v2       delta")
        for b in ("BOTH_EQUAL","BOTH_DIFFERENT","ONLY_SUP","ONLY_AMZ","NEITHER"):
            delta = c2[b] - c1[b]
            print(f"  {b:16s}  {c1[b]:6d}   {c2[b]:6d}   {delta:+6d}")

    total = sum(overall_v2.values())
    print(f"\n=== OVERALL (total EAN-matched rows: {total}) ===")
    print(f"  bucket             v1        v2       delta        v1%      v2%")
    for b in ("BOTH_EQUAL","BOTH_DIFFERENT","ONLY_SUP","ONLY_AMZ","NEITHER"):
        p1 = overall_v1[b]/total*100; p2 = overall_v2[b]/total*100
        print(f"  {b:16s}  {overall_v1[b]:6d}   {overall_v2[b]:6d}  {overall_v2[b]-overall_v1[b]:+6d}   {p1:6.1f}%  {p2:6.1f}%")
    confident = overall_v2["BOTH_EQUAL"] + overall_v2["BOTH_DIFFERENT"]
    print(f"\n  CONFIDENT buckets (BOTH_EQUAL + BOTH_DIFFERENT): v2 = {confident} ({confident/total*100:.1f}%)")
    print(f"                                                 v1 = {overall_v1['BOTH_EQUAL']+overall_v1['BOTH_DIFFERENT']} ({(overall_v1['BOTH_EQUAL']+overall_v1['BOTH_DIFFERENT'])/total*100:.1f}%)")

    print(f"\n\n===== ROWS NEWLY MOVED INTO CONFIDENT BUCKETS BY V2 =====")
    print(f"Total: {len(newly_extracted)}")
    for rec in newly_extracted[:40]:
        print(f"  [{rec['supplier']}] v1={rec['v1']} -> v2={rec['v2']}")
        print(f"    SUP: {rec['sup']}")
        print(f"    AMZ: {rec['amz']}")

    print(f"\n\n===== POTENTIAL REGRESSIONS: BOTH_EQUAL -> BOTH_DIFFERENT =====")
    print(f"Total: {len(newly_disagreed)}")
    for rec in newly_disagreed[:30]:
        print(f"  [{rec['supplier']}] v1={rec['v1']} -> v2={rec['v2']}")
        print(f"    SUP: {rec['sup']}")
        print(f"    AMZ: {rec['amz']}")

    out = REPO / "TIER_CLASSIFICATION_RESEARCH/rerun/pack_audit_v2.json"
    out.write_text(json.dumps({
        "v1": {"per_supplier": per_supplier_v1, "overall": dict(overall_v1)},
        "v2": {"per_supplier": per_supplier_v2, "overall": dict(overall_v2)},
        "samples_v2": samples_v2,
        "newly_extracted": newly_extracted,
        "newly_disagreed": newly_disagreed,
    }, indent=2))
    print(f"\nWrote detailed JSON: {out}")

if __name__ == "__main__":
    main()
