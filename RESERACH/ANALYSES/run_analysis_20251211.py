"""
FBA Product Deep Analysis Script - v5 (EAN Strict Mode)
Date: 2025-12-11
Focus: STRICT EAN matching for TIER 1 + Both EAN columns visible
"""

import pandas as pd
import re
from difflib import SequenceMatcher

# ============== CONFIGURATION ==============
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251211_012758.csv"
OUTPUT_REPORT = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\FINAL_REPORT_20251211.md"
OUTPUT_CSV = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\deep_analysis_20251211.csv"

print("="*80)
print("FBA DEEP ANALYSIS v5 - STRICT EAN MODE")
print("="*80)

# ============== LOAD DATA ==============
df = pd.read_csv(INPUT_PATH)
total_rows = len(df)
print(f"Loaded {total_rows} total rows.")

# Clean EAN columns
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# ============== TITLE SIMILARITY ==============
def title_similarity(t1, t2):
    if pd.isna(t1) or pd.isna(t2):
        return 0.0
    return SequenceMatcher(None, str(t1).lower(), str(t2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# ============== PACK SIZE EXTRACTION ==============
def extract_quantity(title):
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'\bx\s*(\d+)\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'\b(\d+)\s*piece\b',
    ]
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

# ============== PROFIT RECALCULATION ==============
def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# ============== STRICT EAN MATCHING ==============
def is_valid_ean(ean):
    """Check if EAN is valid (not nan, empty, None, etc.)"""
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def is_exact_ean_match(row):
    """Returns True only if BOTH EANs are valid AND they match exactly"""
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    
    return ean_sup == ean_amz

df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)

def categorize(row):
    if row['is_exact_ean']:
        return 'EXACT_EAN_MATCH'
    elif row['title_match'] >= 0.50:
        return 'HIGH_LIKELIHOOD'
    elif row['title_match'] >= 0.30:
        return 'MODERATE_CONFIDENCE'
    else:
        return 'UNCERTAIN'

df['category'] = df.apply(categorize, axis=1)

def pack_verdict(row):
    if row['Qty_Ratio'] == 1.0:
        return "1:1 Match"
    elif row['Qty_Ratio'] > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"BUNDLE ({int(row['Qty_Ratio'])}x) - OK"
        else:
            return f"BUNDLE ({int(row['Qty_Ratio'])}x) - LOSS"
    else:
        if row['Adjusted_Profit'] > 0:
            return f"SPLIT (1/{int(1/row['Qty_Ratio'])}) - OK"
        else:
            return "SPLIT - LOSS"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# ============== KEY FILTERS ==============
profitable_df = df[df['Adjusted_Profit'] > 0].copy()
with_sales = profitable_df[profitable_df['sales'] > 0].copy()

print(f"\nTotal profitable: {len(profitable_df)}")
print(f"With sales > 0: {len(with_sales)}")

# ============== GROUP 1: EXACT EAN MATCHES (Strict) ==============
# ONLY products where both EANs exist AND match exactly
group1_exact_ean = with_sales[
    (with_sales['is_exact_ean'] == True) &
    (with_sales['Adjusted_Profit'] > 0.10) &
    (~with_sales['Pack_Verdict'].str.contains('LOSS'))
].sort_values(['sales', 'Adjusted_Profit'], ascending=[False, False])

print(f"GROUP 1 (Exact EAN with Sales): {len(group1_exact_ean)} products")

# ============== GROUP 2: HIGH LIKELIHOOD (Title Match >= 50%, No EAN Match) ==============
# Good title match but EANs don't match or are missing
group2_high_likelihood = with_sales[
    (with_sales['is_exact_ean'] == False) &
    (with_sales['title_match'] >= 0.50) &
    (with_sales['Adjusted_Profit'] > 0.50) &
    (~with_sales['Pack_Verdict'].str.contains('LOSS'))
].sort_values(['sales', 'Adjusted_Profit'], ascending=[False, False]).head(30)

print(f"GROUP 2 (High Likelihood): {len(group2_high_likelihood)} products")

# ============== GROUP 3: MODERATE CONFIDENCE ==============
group3_moderate = with_sales[
    (with_sales['category'] == 'MODERATE_CONFIDENCE') &
    (with_sales['Adjusted_Profit'] > 1.0)
].sort_values(['sales', 'Adjusted_Profit'], ascending=[False, False]).head(20)

print(f"GROUP 3 (Moderate): {len(group3_moderate)} products")

# ============== GROUP 4: SPLIT OPPORTUNITIES ==============
group4_split = with_sales[
    (with_sales['Sup_Qty'] > 1) &
    (with_sales['Qty_Ratio'] < 1.0) &
    (with_sales['Adjusted_Profit'] > 0.50) &
    (with_sales['title_match'] > 0.35)
].sort_values('Adjusted_Profit', ascending=False).head(15)

print(f"GROUP 4 (Split): {len(group4_split)} products")

# ============== FALSE MATCHES ==============
false_matches = df[
    (df['Qty_Ratio'] > 1.5) &
    (df['Adjusted_Profit'] < 0) &
    (df['title_match'] > 0.30) &
    (df['sales'] > 0)
].sort_values('NetProfit', ascending=False).head(15)

print(f"FALSE MATCHES: {len(false_matches)} products")

# ============== GENERATE REPORT ==============
def calc_roi(row):
    try:
        cost = float(row['SupplierPrice_incVAT'])
        if cost > 0:
            return (float(row['Adjusted_Profit']) / cost) * 100
        return 0
    except:
        return 0

def truncate(text, length=40):
    text = str(text) if pd.notna(text) else ''
    return text[:length] + '...' if len(text) > length else text

def format_ean(ean):
    """Format EAN for display"""
    if pd.isna(ean):
        return '-'
    ean_str = str(ean).strip()
    if ean_str in ['nan', '', 'None', 'NaN', '0']:
        return '-'
    return ean_str

report = f"""# 🔍 FINAL DEEP ANALYSIS REPORT - Angel Wholesale

**Generated:** 2025-12-11  
**Source:** `fba_financial_report_20251211_012758.csv`  
**Total Products:** {total_rows}  
**Profitable Products:** {len(profitable_df)}  
**With Sales Data (>0):** {len(with_sales)}

---

## 📊 SUMMARY

| Group | Count | Description |
|:------|:-----:|:------------|
| 🟢 GROUP 1: EXACT EAN MATCH | {len(group1_exact_ean)} | Both EANs present AND matching |
| 🟡 GROUP 2: HIGH LIKELIHOOD | {len(group2_high_likelihood)} | Title match >=50%, EANs don't match |
| 🟠 GROUP 3: MODERATE CONFIDENCE | {len(group3_moderate)} | Title match 30-50% |
| 🔵 GROUP 4: SPLIT OPPORTUNITIES | {len(group4_split)} | Supplier multipack -> Amazon single |
| 🔴 FALSE MATCHES | {len(false_matches)} | Loss makers (dropped) |

---

## 🟢 GROUP 1: EXACT EAN MATCHES (Highest Confidence)

**Criteria:** Sales > 0, Supplier EAN = Amazon EAN (BOTH must be present), Profitable.

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

for _, row in group1_exact_ean.iterrows():
    roi = calc_roi(row)
    report += f"| {truncate(row['SupplierTitle'], 35)} | {truncate(row['AmazonTitle'], 35)} | {format_ean(row['EAN'])} | {format_ean(row['EAN_OnPage'])} | {row['ASIN']} | {row['title_match']*100:.0f}% | {int(row['sales'])} | £{row['Adjusted_Profit']:.2f} | {roi:.0f}% |\n"

if len(group1_exact_ean) == 0:
    report += "| *No exact EAN matches found with sales > 0* | - | - | - | - | - | - | - | - |\n"

report += f"""
**✅ These are your SAFEST buys - VERIFIED EAN matches with proven sales.**

---

## 🟡 GROUP 2: HIGH LIKELIHOOD MATCHES (Title Match >= 50%)

**Criteria:** Sales > 0, Title similarity >= 50%, EANs do NOT match or are missing, Profitable.

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

for _, row in group2_high_likelihood.iterrows():
    roi = calc_roi(row)
    report += f"| {truncate(row['SupplierTitle'], 35)} | {truncate(row['AmazonTitle'], 35)} | {format_ean(row['EAN'])} | {format_ean(row['EAN_OnPage'])} | {row['ASIN']} | {row['title_match']*100:.0f}% | {int(row['sales'])} | £{row['Adjusted_Profit']:.2f} | {roi:.0f}% |\n"

if len(group2_high_likelihood) == 0:
    report += "| *No high likelihood matches found* | - | - | - | - | - | - | - | - |\n"

report += f"""
**⚠️ EANs don't match - verify manually before large orders.**

---

## 🟠 GROUP 3: MODERATE CONFIDENCE (Title Match 30-50%)

**Criteria:** Sales > 0, Title match 30-50%, Profit > £1.00

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

for _, row in group3_moderate.iterrows():
    roi = calc_roi(row)
    report += f"| {truncate(row['SupplierTitle'], 35)} | {truncate(row['AmazonTitle'], 35)} | {format_ean(row['EAN'])} | {format_ean(row['EAN_OnPage'])} | {row['ASIN']} | {row['title_match']*100:.0f}% | {int(row['sales'])} | £{row['Adjusted_Profit']:.2f} | {roi:.0f}% |\n"

if len(group3_moderate) == 0:
    report += "| *No moderate confidence matches found* | - | - | - | - | - | - | - | - |\n"

report += f"""
**⚠️ Lower confidence - manual verification required before ordering.**

---

## 🔵 GROUP 4: SPLIT OPPORTUNITIES

**Criteria:** Supplier sells multipack, Amazon sells singles, Profitable if split.

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

for _, row in group4_split.iterrows():
    roi = calc_roi(row)
    report += f"| {truncate(row['SupplierTitle'], 35)} | {truncate(row['AmazonTitle'], 35)} | {format_ean(row['EAN'])} | {format_ean(row['EAN_OnPage'])} | {row['ASIN']} | {row['title_match']*100:.0f}% | {int(row['sales'])} | £{row['Adjusted_Profit']:.2f} | {roi:.0f}% |\n"

if len(group4_split) == 0:
    report += "| *No split opportunities found with sales* | - | - | - | - | - | - | - | - |\n"

report += f"""
**💡 These require splitting supplier packs - check inner packaging has barcodes.**

---

## 🔴 FALSE MATCHES / LOSS MAKERS (Do Not Buy)

**These products looked profitable but became LOSSES after pack size adjustment:**

| SupplierTitle | AmazonTitle | Pack Issue | Original Profit | Adjusted Profit |
|:--------------|:------------|:-----------|----------------:|----------------:|
"""

for _, row in false_matches.iterrows():
    pack_issue = f"Sup: {int(row['Sup_Qty'])} vs Amz: {int(row['Amz_Qty'])}"
    report += f"| {truncate(row['SupplierTitle'], 35)} | {truncate(row['AmazonTitle'], 35)} | {pack_issue} | £{row['NetProfit']:.2f} | £{row['Adjusted_Profit']:.2f} |\n"

if len(false_matches) == 0:
    report += "| *No false matches with sales data found* | - | - | - | - |\n"

report += f"""
---

## ⚠️ CRITICAL WARNINGS

1. **GROUP 1 is SAFEST:** Only products with BOTH EANs matching are included.
2. **GROUP 2 needs verification:** Title match is good but EANs differ - could be same product, different variant.
3. **Pomegranate Noir / Jo Malone:** This is likely a "smell-alike" generic. **HIGH IP RISK.**
4. **Always verify pack sizes:** Check supplier AND Amazon listing before ordering.

---

## 🚀 ACTION PLAN

1. **Immediate Order:** GROUP 1 - VERIFIED EAN matches with sales.
2. **Test Orders:** GROUP 2 - order small quantities, verify manually.
3. **Manual Check:** GROUP 3 - verify title/product matches carefully.
4. **Split Prep:** GROUP 4 - verify inner packaging before splitting.
5. **Avoid:** All items in FALSE MATCHES section.

---

*Report generated using FBA Deep Analysis Pipeline v5.0 (Strict EAN Mode)*
*Analysis Date: 2025-12-11*
"""

# Save report
with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\nReport saved: {OUTPUT_REPORT}")

# Save CSV
cols = ['category', 'is_exact_ean', 'Pack_Verdict', 'Adjusted_Profit', 'NetProfit', 'ROI', 'Qty_Ratio', 
        'Sup_Qty', 'Amz_Qty', 'title_match', 'sales', 'SupplierTitle', 'AmazonTitle', 
        'EAN', 'EAN_OnPage', 'ASIN', 'SupplierPrice_incVAT', 'SellingPrice_incVAT']
available_cols = [c for c in cols if c in df.columns]
with_sales[available_cols].to_csv(OUTPUT_CSV, index=False)
print(f"CSV saved: {OUTPUT_CSV}")

# ============== FINAL SUMMARY ==============
print("\n" + "="*80)
print("TOP 10 EXACT EAN MATCHES (With Sales)")
print("="*80)
for i, (_, row) in enumerate(group1_exact_ean.head(10).iterrows(), 1):
    print(f"{i}. {str(row['SupplierTitle'])[:45]}")
    print(f"   EAN: {row['EAN']} = {row['EAN_OnPage']}")
    print(f"   Sales: {int(row['sales'])} | Profit: £{row['Adjusted_Profit']:.2f}")
    print()
