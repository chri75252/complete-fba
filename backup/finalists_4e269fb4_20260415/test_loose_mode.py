import sys, csv
sys.path.insert(0, '.')
from tools.fba_report_filter import classify_row

csv_path = "FINAL STALE/fba_analysis_202 efg newst4 (1).csv"
strict_counts = {"TIER_1_VERIFIED": 0, "TIER_2_LIKELY": 0, "TIER_3_NEEDS_REVIEW": 0, "TIER_4_REJECTED": 0}
loose_counts = {"TIER_1_VERIFIED": 0, "TIER_2_LIKELY": 0, "TIER_3_NEEDS_REVIEW": 0, "TIER_4_REJECTED": 0}

with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        s = classify_row(row, loose_mode=False)
        l = classify_row(row, loose_mode=True)
        strict_counts[s["tier"]] += 1
        loose_counts[l["tier"]] += 1

total = sum(strict_counts.values())
print(f"Total rows: {total}")
print()
print(f"{'Tier':<25} {'Strict':>8} {'Strict%':>8} | {'Loose':>8} {'Loose%':>8}")
print("-" * 65)
for t in strict_counts:
    print(f"{t:<25} {strict_counts[t]:>8} {strict_counts[t]/total*100:>7.1f}% | {loose_counts[t]:>8} {loose_counts[t]/total*100:>7.1f}%")
print()
strict_ok = strict_counts["TIER_1_VERIFIED"] + strict_counts["TIER_2_LIKELY"] + strict_counts["TIER_3_NEEDS_REVIEW"]
loose_ok = loose_counts["TIER_1_VERIFIED"] + loose_counts["TIER_2_LIKELY"] + loose_counts["TIER_3_NEEDS_REVIEW"]
print(f"Non-rejected (T1+T2+T3):")
print(f"  Strict: {strict_ok} ({strict_ok/total*100:.1f}%)")
print(f"  Loose:  {loose_ok} ({loose_ok/total*100:.1f}%)")
