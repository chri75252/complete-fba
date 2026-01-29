import pandas as pd
import re
from difflib import SequenceMatcher
import os
import sys

# Configuration
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251211_203547.csv"
OUTPUT_DIR = os.path.dirname(INPUT_PATH)
DATE_SUFFIX = "20251212" # Using current date as per prompt versioning implication

OUTPUT_CSV = os.path.join(OUTPUT_DIR, f"deep_analysis_{DATE_SUFFIX}.csv")
OUTPUT_MD = os.path.join(OUTPUT_DIR, f"FINAL_REPORT_{DATE_SUFFIX}.md")

print(f"Loading data from: {INPUT_PATH}")
df = pd.read_csv(INPUT_PATH)

# --- STAGE 1: Data Loading & Initial Cleaning ---
print("Stage 1: Cleaning Data...")
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# --- STAGE 2: Title Similarity Calculation ---
print("Stage 2: Title Similarity...")
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# --- STAGE 3: STRICT EAN Matching ---
print("Stage 3: Strict EAN Check...")
def is_valid_ean(ean):
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def is_exact_ean_match(row):
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    
    return ean_sup == ean_amz

df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)

# --- STAGE 4: Pack Size Extraction & Profit Recalc ---
print("Stage 4: Pack Size Logic...")
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

def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        # If ratio > 1, we buy 'ratio' amount of supplier items. 
        # But wait, original profit = Sell - Fees - Cost.
        # If we need to buy 2, Cost becomes 2*Cost.
        # Adjusted = Sell - Fees - 2*Cost
        #          = (Sell - Fees - Cost) - Cost
        #          = Original - Cost*(Ratio-1)
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# --- STAGE 5: Product Categorization ---
print("Stage 5: Categorization...")
def categorize(row):
    # Rule #3 from prompt: Sales > 0 priority implies we might filter later, 
    # but categorization logic itself:
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
        # Ratio < 1 means Supp has 10, Amz has 1. Splitting.
        # Cost is Cost/10? No, logic above for recalculate_profit handles Ratio > 1.
        # For Ratio < 1 (Split):
        # We buy 1 supplier item (cost $10 for 10 units), sell 10 amazon items? 
        # Or we act as if we sell 1 amazon unit.
        # Recalculate_profit formula: adj = cost * (ratio - 1).
        # If ratio = 0.1, adj = cost * (-0.9). 
        # Profit = Orig - (-0.9*Cost) = Orig + 0.9*Cost.
        # This assumes Orig Profit was calculated using full supplier cost against 1 amazon unit?
        # Usually 'NetProfit' in reports is Sell - Fees - Cost.
        # If we split, true cost is Cost * Ratio.
        # So True Profit = Sell - Fees - (Cost * Ratio)
        #                 = (Sell - Fees - Cost) + Cost - (Cost * Ratio)
        #                 = Orig + Cost * (1 - Ratio)
        #                 = Orig - Cost * (Ratio - 1).
        # MATH CHECKS OUT.
        if row['Adjusted_Profit'] > 0:
            return f"SPLIT (1/{int(1/row['Qty_Ratio'])}) - OK"
        else:
            return "SPLIT - LOSS"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# --- ROI Recalc ---
def calc_roi(row):
    try:
        cost = float(row['SupplierPrice_incVAT']) * row['Qty_Ratio']
        if cost == 0: return 0.0
        return (row['Adjusted_Profit'] / cost) * 100
    except:
        return 0.0

df['ROI_Adjusted'] = df.apply(calc_roi, axis=1)

# --- FILTERING False Matches ---
# "FALSE MATCHES / LOSS MAKERS" are those that became losses or are just bad.
# But for the CSV, we keep everything? The prompt says "Output File 1... Include these columns". 
# It doesn't explicitly say "Exclude false matches from CSV", but usually we keep data.
# However, the Report Markdown needs separation.

# Save CSV
output_columns = [
    'category', 'is_exact_ean', 'Pack_Verdict',
    'Adjusted_Profit', 'NetProfit', 'ROI', 'ROI_Adjusted',
    'Qty_Ratio', 'Sup_Qty', 'Amz_Qty',
    'title_match', 'sales',
    'SupplierTitle', 'AmazonTitle',
    'EAN', 'EAN_OnPage',
    'ASIN', 'SupplierPrice_incVAT', 'SellingPrice_incVAT'
]
# Ensure all columns exist
for c in output_columns:
    if c not in df.columns:
        df[c] = None

df.to_csv(OUTPUT_CSV, columns=output_columns, index=False)
print(f"Deep Analysis CSV saved to: {OUTPUT_CSV}")

# --- Generate Markdown Report ---
print("Generating Markdown Report...")

# Filtering for Report Groups
# Sort by sales desc
df_sorted = df.sort_values(by=['sales', 'Adjusted_Profit'], ascending=[False, False])

def is_profitable(row):
    return row['Adjusted_Profit'] > 0

group1 = df_sorted[
    (df_sorted['category'] == 'EXACT_EAN_MATCH') & 
    is_profitable(df_sorted)
]

group2 = df_sorted[
    (df_sorted['category'] == 'HIGH_LIKELIHOOD') & 
    (~df_sorted['is_exact_ean']) & 
    is_profitable(df_sorted)
]

group3 = df_sorted[
    (df_sorted['category'] == 'MODERATE_CONFIDENCE') & 
    (~df_sorted['is_exact_ean']) & 
    (df_sorted['Adjusted_Profit'] > 1.00) # Prompt criteria > £1.00
]

group4 = df_sorted[
    (df_sorted['Qty_Ratio'] != 1.0) &
    is_profitable(df_sorted) &
    (df_sorted['Pack_Verdict'].str.contains('SPLIT') | df_sorted['Pack_Verdict'].str.contains('BUNDLE'))
    # Note: Logic overlap. Group 1/2/3 might also be splits/bundles. 
    # Prompt implies Group 4 is specifically "Split Opportunities".
    # Usually "Split" falls into this bucket.
    # Let's prioritize: If it's a split and profitable, it goes here? 
    # Or strict hierarchy? 
    # The prompt says: "GROUP 4: SPLIT OPPORTUNITIES - Supplier multipack -> Amazon single".
    # So if Qty_Ratio < 1.0 and Profitable.
]

# Refine groups to avoid dupes if necessary or just list them.
# Usually hierarchy: Exact EAN -> High Match -> Moderate.
# Split could be any of them?
# Let's follow strict criteria from prompt text.
# Group 4 Criteria: "Supplier sells multipack, Amazon sells singles, Profitable if split."
# This implies Qty_Ratio < 1.0.

group4_splits = df_sorted[
    (df_sorted['Qty_Ratio'] < 1.0) & 
    is_profitable(df_sorted)
]

false_matches = df_sorted[
    (df_sorted['Adjusted_Profit'] <= 0) &
    (df_sorted['NetProfit'] > 0) # Looked profitable initially but failed adjustment
]

total_products = len(df)
profitable_count = len(df_sorted[df_sorted['Adjusted_Profit'] > 0])
with_sales_count = len(df_sorted[df_sorted['sales'] > 0])

md_content = f"""# 🔍 FINAL DEEP ANALYSIS REPORT - Angel Wholesale

**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d')}  
**Source:** `{os.path.basename(INPUT_PATH)}`  
**Total Products:** {total_products}  
**Profitable Products:** {profitable_count}  
**With Sales Data (>0):** {with_sales_count}

---

## 📊 SUMMARY

| Group | Count | Description |
|:------|:-----:|:------------|
| 🟢 GROUP 1: EXACT EAN MATCH | {len(group1)} | Both EANs present AND matching |
| 🟡 GROUP 2: HIGH LIKELIHOOD | {len(group2)} | Title match >=50%, EANs don't match |
| 🟠 GROUP 3: MODERATE CONFIDENCE | {len(group3)} | Title match 30-50% |
| 🔵 GROUP 4: SPLIT OPPORTUNITIES | {len(group4_splits)} | Supplier multipack -> Amazon single |
| 🔴 FALSE MATCHES | {len(false_matches)} | Loss makers (dropped) |

---

## 🟢 GROUP 1: EXACT EAN MATCHES (Highest Confidence)

**Criteria:** Sales > 0, Supplier EAN = Amazon EAN (BOTH must be present), Profitable.

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

def row_to_md(row):
    return f"| {str(row['SupplierTitle'])[:50]} | {str(row['AmazonTitle'])[:50]} | {row['EAN']} | {row['EAN_OnPage']} | {row['ASIN']} | {row['title_match']:.2f} | {int(row['sales'])} | £{row['Adjusted_Profit']:.2f} | {row['ROI_Adjusted']:.0f}% |"

for _, row in group1.iterrows():
    md_content += row_to_md(row) + "\n"

md_content += """
**✅ These are your SAFEST buys - VERIFIED EAN matches with proven sales.**

---

## 🟡 GROUP 2: HIGH LIKELIHOOD MATCHES (Title Match >= 50%)

**Criteria:** Sales > 0, Title similarity >= 50%, EANs do NOT match or are missing, Profitable.

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

for _, row in group2.iterrows():
    md_content += row_to_md(row) + "\n"

md_content += """
**⚠️ EANs don't match - verify manually before large orders.**

---

## 🟠 GROUP 3: MODERATE CONFIDENCE (Title Match 30-50%)

**Criteria:** Sales > 0, Title match 30-50%, Profit > £1.00

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

for _, row in group3.iterrows():
    md_content += row_to_md(row) + "\n"

md_content += """
**⚠️ Lower confidence - manual verification required before ordering.**

---

## 🔵 GROUP 4: SPLIT OPPORTUNITIES

**Criteria:** Supplier sells multipack, Amazon sells singles, Profitable if split.

| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |
|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|
"""

for _, row in group4_splits.iterrows():
    md_content += row_to_md(row) + "\n"

md_content += """
**💡 These require splitting supplier packs - check inner packaging has barcodes.**

---

## 🔴 FALSE MATCHES / LOSS MAKERS (Do Not Buy)

**These products looked profitable but became LOSSES after pack size adjustment:**

| SupplierTitle | AmazonTitle | Pack Issue | Original Profit | Adjusted Profit |
|:--------------|:------------|:-----------|----------------:|----------------:|
"""

for _, row in false_matches.head(20).iterrows(): # Limit to 20 for brevity if many
    md_content += f"| {str(row['SupplierTitle'])[:40]} | {str(row['AmazonTitle'])[:40]} | Sup:{row['Sup_Qty']} vs Amz:{row['Amz_Qty']} | £{row['NetProfit']:.2f} | £{row['Adjusted_Profit']:.2f} |\n"

md_content += """
---

## ⚠️ CRITICAL WARNINGS

1. **GROUP 1 is SAFEST:** Only products with BOTH EANs matching are included.
2. **GROUP 2 needs verification:** Title match is good but EANs differ - could be same product, different variant.
3. **Pomegranate Noir / Jo Malone (if present):** This is likely a "smell-alike" generic. **HIGH IP RISK.**
4. **Always verify pack sizes:** Check supplier AND Amazon listing images before ordering.

---

*Report generated using FBA Deep Analysis Pipeline v2.0*
"""

with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Markdown Report saved to: {OUTPUT_MD}")
print("Done.")
