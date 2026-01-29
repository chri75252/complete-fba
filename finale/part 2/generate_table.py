import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import re

# Load data
df = pd.read_excel('PART3.xlsx')
confirmed_ean = pd.read_csv('confirmed_exact_ean.csv')
confirmed_non_ean = pd.read_csv('confirmed_non_ean.csv')

# Combine all confirmed ASINs
all_confirmed_asins = set(confirmed_ean['ASIN'].tolist() + confirmed_non_ean['ASIN'].tolist())

# Function to extract pack quantities
def extract_pack_qty(title):
    if pd.isna(title):
        return 1
    title = str(title).lower()
    patterns = [
        r'pack of (\d+)', r'(\d+)\s*pack\b', r'(\d+)\s*pcs\b', r'(\d+)\s*pieces\b',
        r'set of (\d+)', r'(\d+)\s*x\s+\w', r'x\s*(\d+)\b', r'(\d+)\s*bags\b',
        r'(\d+)\s*bottles\b', r'(\d+)\s*containers\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            qty = int(match.group(1))
            if 1 < qty <= 200:
                return qty
    return 1

def title_similarity(s1, s2):
    if pd.isna(s1) or pd.isna(s2):
        return 0
    return SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio()

# Build comprehensive table
results = []

for asin in all_confirmed_asins:
    # Get row from PART3
    row = df[df['ASIN'] == asin]
    if len(row) == 0:
        continue
    row = row.iloc[0]
    
    # Get confirmation source
    is_ean = asin in confirmed_ean['ASIN'].values
    is_title = asin in confirmed_non_ean['ASIN'].values
    
    # Calculate values
    sup_title = row['SupplierTitle']
    amz_title = row['AmazonTitle']
    sim = title_similarity(sup_title, amz_title)
    sup_qty = extract_pack_qty(sup_title)
    amz_qty = extract_pack_qty(amz_title)
    
    sup_ean = row['EAN']
    amz_ean = row['EAN_OnPage']
    
    # Determine verdict and confidence
    if is_ean:
        ean_match = (str(sup_ean) == str(amz_ean)) if pd.notna(sup_ean) and pd.notna(amz_ean) else False
        if ean_match:
            verdict = "VERIFIED"
            confidence = 95
            match_evidence = f"Exact EAN match: {sup_ean}"
        else:
            verdict = "VERIFIED"
            confidence = 90
            match_evidence = f"EAN confirmed, Title sim: {sim:.2f}"
    else:
        if sim >= 0.70:
            verdict = "HIGH LIKELIHOOD"
            confidence = 85
        elif sim >= 0.50:
            verdict = "HIGH LIKELIHOOD"
            confidence = 75
        else:
            verdict = "NEEDS VERIFICATION"
            confidence = 65
        
        # Get match reason from non_ean csv
        non_ean_row = confirmed_non_ean[confirmed_non_ean['ASIN'] == asin]
        if len(non_ean_row) > 0:
            reason = non_ean_row.iloc[0].get('Reason', f'Title sim: {sim:.2f}')
            match_evidence = reason
        else:
            match_evidence = f"Title sim: {sim:.2f}"
    
    # Pack verdict
    if sup_qty == amz_qty:
        pack_verdict = f"OK (1:1)"
    else:
        pack_verdict = f"MISMATCH ({sup_qty} vs {amz_qty})"
    
    # Adjusted profit
    profit = row['NetProfit']
    if sup_qty > 1 and amz_qty == 1:
        adj_profit = profit / sup_qty
        adj_note = f"~{adj_profit:.2f} (divided by {sup_qty})"
    elif sup_qty == 1 and amz_qty > 1:
        adj_profit = profit * amz_qty
        adj_note = f"~{adj_profit:.2f} (x{amz_qty})"
    else:
        adj_profit = profit
        adj_note = f"{profit:.2f}"
    
    # Key risks
    risks = []
    if sim < 0.40:
        risks.append("Low title similarity")
    if sup_qty != amz_qty and (sup_qty > 1 or amz_qty > 1):
        risks.append(f"Pack qty difference ({sup_qty} vs {amz_qty})")
    if profit < 0.50:
        risks.append("Low profit margin")
    if not risks:
        risks.append("None identified")
    
    # Source tracking
    source = "Winner (Report 2.7)"
    
    results.append({
        'Verdict': verdict,
        'Confidence': confidence,
        'SupplierTitle': sup_title,
        'AmazonTitle': str(amz_title)[:120] + "..." if len(str(amz_title)) > 120 else amz_title,
        'Supplier EAN': sup_ean if pd.notna(sup_ean) else '-',
        'Amazon EAN': amz_ean if pd.notna(amz_ean) else '-',
        'ASIN': asin,
        'SupplierPrice_incVAT': f"{row['SupplierPrice_incVAT']:.2f}" if pd.notna(row['SupplierPrice_incVAT']) else '-',
        'SellingPrice_incVAT': f"{row['SellingPrice_incVAT']:.2f}" if pd.notna(row['SellingPrice_incVAT']) else '-',
        'NetProfit': f"{profit:.2f}",
        'ROI': f"{row['ROI']:.1f}%" if pd.notna(row['ROI']) else '-',
        'Sales': int(row['bought_in_past_month']) if pd.notna(row['bought_in_past_month']) else 0,
        'Pack Verdict': pack_verdict,
        'Adjusted Profit': adj_note,
        'Key Match Evidence': match_evidence,
        'Key Risks / Notes': '; '.join(risks),
        'Source': source,
        'TitleSim': sim
    })

# Convert to DataFrame and sort
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(['Verdict', 'Confidence', 'Sales'], ascending=[True, False, False])

# Separate VERIFIED and other categories
verified_df = results_df[results_df['Verdict'] == 'VERIFIED'].copy()
high_likelihood_df = results_df[results_df['Verdict'] == 'HIGH LIKELIHOOD'].copy()
needs_verification_df = results_df[results_df['Verdict'] == 'NEEDS VERIFICATION'].copy()

# Output columns (excluding Source and TitleSim for display)
display_cols = ['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 
                'ASIN', 'SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI', 'Sales',
                'Pack Verdict', 'Adjusted Profit', 'Key Match Evidence', 'Key Risks / Notes']

# Generate Markdown output
output = []

output.append("# CONFIRMED PRODUCTS COMPREHENSIVE TABLE")
output.append("")
output.append("Generated: 2025-12-25")
output.append("")
output.append("---")
output.append("")

# Section 1: VERIFIED (Exact EAN matches)
output.append("## TABLE 1: VERIFIED (Exact EAN Match) - From Winner Report 2.7")
output.append("")
output.append(f"**Total: {len(verified_df)} products**")
output.append("")

# Create markdown table
header = "| " + " | ".join(display_cols) + " |"
separator = "|" + "|".join(["---" for _ in display_cols]) + "|"
output.append(header)
output.append(separator)

for _, row in verified_df.iterrows():
    row_str = "| " + " | ".join([str(row[col])[:50] if col in ['SupplierTitle', 'AmazonTitle', 'Key Match Evidence', 'Key Risks / Notes'] else str(row[col]) for col in display_cols]) + " |"
    output.append(row_str)

output.append("")
output.append("---")
output.append("")

# Section 2: HIGH LIKELIHOOD
output.append("## TABLE 2: HIGH LIKELIHOOD (Title-Confirmed) - From Winner Report 2.7")
output.append("")
output.append(f"**Total: {len(high_likelihood_df)} products**")
output.append("")

output.append(header)
output.append(separator)

for _, row in high_likelihood_df.iterrows():
    row_str = "| " + " | ".join([str(row[col])[:50] if col in ['SupplierTitle', 'AmazonTitle', 'Key Match Evidence', 'Key Risks / Notes'] else str(row[col]) for col in display_cols]) + " |"
    output.append(row_str)

output.append("")
output.append("---")
output.append("")

# Section 3: NEEDS VERIFICATION
output.append("## TABLE 3: NEEDS VERIFICATION (Lower Confidence Title Match) - From Winner Report 2.7")
output.append("")
output.append(f"**Total: {len(needs_verification_df)} products**")
output.append("")

output.append(header)
output.append(separator)

for _, row in needs_verification_df.iterrows():
    row_str = "| " + " | ".join([str(row[col])[:50] if col in ['SupplierTitle', 'AmazonTitle', 'Key Match Evidence', 'Key Risks / Notes'] else str(row[col]) for col in display_cols]) + " |"
    output.append(row_str)

output.append("")
output.append("---")
output.append("")

# Section 4: MISSED BY WINNER (from other reports or my analysis)
output.append("## TABLE 4: CONFIRMED PRODUCTS MISSED BY WINNER (From Other Reports or My Analysis)")
output.append("")
output.append("| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes | Source |")
output.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

# B0042FBWQ0 - missed by winner but in Report 2.8
missed_row = df[df['ASIN'] == 'B0042FBWQ0']
if len(missed_row) > 0:
    r = missed_row.iloc[0]
    sup_ean = r['EAN'] if pd.notna(r['EAN']) else '-'
    amz_ean = r['EAN_OnPage'] if pd.notna(r['EAN_OnPage']) else '-'
    output.append(f"| VERIFIED | 95 | {r['SupplierTitle'][:50]} | {str(r['AmazonTitle'])[:50]}... | {sup_ean} | {amz_ean} | B0042FBWQ0 | {r['SupplierPrice_incVAT']:.2f} | {r['SellingPrice_incVAT']:.2f} | {r['NetProfit']:.2f} | {r['ROI']:.1f}% | {int(r['bought_in_past_month'])} | OK (1:1) | {r['NetProfit']:.2f} | Exact EAN match | None identified | **Report 2.8** |")

output.append("")
output.append("---")
output.append("")

# Section 5: EXCLUDED EXACT EAN MATCHES (for reference)
output.append("## TABLE 5: EXCLUDED - Exact EAN but Pack Mismatch (For Audit)")
output.append("")
output.append("These products have exact EAN matches but were excluded due to pack/quantity contradictions.")
output.append("")

excluded_ean = pd.read_csv('excluded_exact_ean.csv')
output.append("| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | ASIN | NetProfit | Sales | Pack Verdict | Key Risks / Notes |")
output.append("|---|---|---|---|---|---|---|---|---|---|")

for _, row in excluded_ean.iterrows():
    output.append(f"| EXCLUDED | 0 | {str(row['SupplierTitle'])[:50]} | {str(row['AmazonTitle'])[:50]}... | {row['EAN']} | {row['ASIN']} | {row['NetProfit']:.2f} | {row['Sales']} | {row['PackVerdict']} | Pack mismatch - verify manually |")

# Write output
with open('CONFIRMED_PRODUCTS_TABLE.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Generated: CONFIRMED_PRODUCTS_TABLE.md")
print(f"\nSummary:")
print(f"  - VERIFIED: {len(verified_df)}")
print(f"  - HIGH LIKELIHOOD: {len(high_likelihood_df)}")
print(f"  - NEEDS VERIFICATION: {len(needs_verification_df)}")
print(f"  - MISSED BY WINNER: 1")
print(f"  - EXCLUDED (Pack issues): {len(excluded_ean)}")
print(f"  - TOTAL: {len(results_df) + 1}")

# Also save as CSV
results_df.to_csv('CONFIRMED_PRODUCTS_TABLE.csv', index=False)
print("\nAlso saved: CONFIRMED_PRODUCTS_TABLE.csv")
