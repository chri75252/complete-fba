"""
FBA Product Validation - efghousewares-co-uk
Phases 0-1: Preflight + Load & Summarize
"""
import csv, json, os, sys, math
from collections import Counter

BASE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
ANALYSIS = os.path.join(BASE, r"FINAL STALE\19-04\fba_analysis_2026-04-18.csv")
FINREPORT = os.path.join(BASE, r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_efghousewares-co-uk_20260413_003445.csv")

def safe_float(v):
    if v is None or str(v).strip() in ('', 'nan', 'NaN', 'None', 'N/A'):
        return None
    s = str(v).strip().replace('£','').replace(',','')
    try:
        return float(s)
    except:
        return None

def load_csv(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

# Phase 0: Preflight
print("="*60)
print("PHASE 0: PRE-FLIGHT")
print("="*60)
print(f"Analysis CSV exists: {os.path.exists(ANALYSIS)} ({os.path.getsize(ANALYSIS)} bytes)")
print(f"Financial Report exists: {os.path.exists(FINREPORT)} ({os.path.getsize(FINREPORT)} bytes)")

rows = load_csv(ANALYSIS)
fin_rows = load_csv(FINREPORT)

# Column mapping
COLS_ANALYSIS = list(rows[0].keys())
COLS_FIN = list(fin_rows[0].keys())
print(f"\nAnalysis columns ({len(COLS_ANALYSIS)}): {COLS_ANALYSIS}")
print(f"\nFinancial report columns ({len(COLS_FIN)}): {COLS_FIN}")

# Normalize aliases - check which exist
alias_map = {
    'tier': ['tier', 'Tier'],
    'confidence_score': ['confidence_score', 'Confidence_Score'],
    'sales_value': ['sales_value', 'Sales', 'monthly_sales'],
    'NetProfit': ['NetProfit', 'Net_Profit'],
    'ROI': ['ROI', 'roi_percent'],
    'ean_exact_match': ['ean_exact_match', 'EAN_Exact_Match'],
}
print("\nColumn alias resolution:")
for canonical, aliases in alias_map.items():
    found = [a for a in aliases if a in COLS_ANALYSIS]
    print(f"  {canonical}: using '{found[0]}'" if found else f"  {canonical}: NOT FOUND")

# Phase 1: Summarize
print("\n" + "="*60)
print("PHASE 1: LOAD & SUMMARIZE")
print("="*60)
print(f"Total rows: {len(rows)}")

# Tier distribution
tiers = Counter(r.get('tier','?') for r in rows)
print(f"\nTier distribution:")
for t, c in sorted(tiers.items()):
    print(f"  {t}: {c}")

# Flags distribution
all_flags = []
for r in rows:
    f = r.get('flags', '')
    if f:
        for flag in f.split(','):
            flag = flag.strip()
            if flag:
                all_flags.append(flag)
flag_counts = Counter(all_flags).most_common(10)
print(f"\nTop 10 flags:")
for flag, count in flag_counts:
    print(f"  {flag}: {count}")

# Profitable count
profitable = 0
unprofitable = 0
profit_na = 0
for r in rows:
    p = safe_float(r.get('NetProfit'))
    if p is None:
        profit_na += 1
    elif p > 0:
        profitable += 1
    else:
        unprofitable += 1
print(f"\nProfitable (NetProfit > 0): {profitable}")
print(f"Unprofitable: {unprofitable}")
print(f"Profit N/A: {profit_na}")

# Sales data
has_sales = 0
zero_sales = 0
nan_sales = 0
for r in rows:
    s = safe_float(r.get('sales_value'))
    if s is None:
        nan_sales += 1
    elif s > 0:
        has_sales += 1
    else:
        zero_sales += 1
print(f"\nItems with sales > 0: {has_sales}")
print(f"Items with sales = 0: {zero_sales}")
print(f"Items with sales NaN/missing: {nan_sales}")

# Financial report summary
print(f"\nFinancial report rows: {len(fin_rows)}")
fin_tiers = Counter(r.get('tier','?') for r in fin_rows)
print(f"Financial report tier distribution:")
for t, c in sorted(fin_tiers.items()):
    print(f"  {t}: {c}")

# EAN exact match distribution
ean_exact = Counter(str(r.get('ean_exact_match','')).lower() for r in rows)
print(f"\nEAN exact match distribution: {dict(ean_exact)}")

# Save rows as JSON for next phase
with open(os.path.join(BASE, 'scratch', 'analysis_rows.json'), 'w') as f:
    json.dump(rows, f)
with open(os.path.join(BASE, 'scratch', 'fin_rows.json'), 'w') as f:
    json.dump(fin_rows, f)
print("\nPhase 0-1 complete. Data saved for Phase 2.")
