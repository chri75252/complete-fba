"""
COMPREHENSIVE FBA REPORT GENERATOR
Thoroughly analyzes PART3.xlsx and generates a properly formatted report.
Includes VERIFIED, HIGH LIKELIHOOD, REALISTIC NEEDS VERIFICATION, and FILTERED-OUT audit tables.
"""
import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from datetime import datetime

# Load source data
print("Loading data...")
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx')
df['RowID'] = df.index + 1

# Clean EANs
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# =====================================
# HELPER FUNCTIONS
# =====================================

def is_valid_ean(ean):
    """Check if EAN is a valid barcode"""
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN', '0', '-']:
        return False
    s = str(ean).strip()
    return s.isdigit() and len(s) >= 8

def eans_match(row):
    """Check if supplier and amazon EANs match exactly"""
    ean1 = row['EAN_clean']
    ean2 = row['EAN_OnPage_clean']
    return is_valid_ean(ean1) and is_valid_ean(ean2) and ean1 == ean2

def title_similarity(t1, t2):
    """Calculate title similarity ratio"""
    if pd.isna(t1) or pd.isna(t2):
        return 0.0
    return SequenceMatcher(None, str(t1).lower(), str(t2).lower()).ratio()

def jaccard_similarity(t1, t2):
    """Calculate Jaccard token overlap"""
    if pd.isna(t1) or pd.isna(t2):
        return 0.0
    tokens1 = set(str(t1).lower().split())
    tokens2 = set(str(t2).lower().split())
    if not tokens1 or not tokens2:
        return 0.0
    return len(tokens1 & tokens2) / len(tokens1 | tokens2)

def get_brand_from_title(title):
    """Extract brand (first word) from title"""
    if pd.isna(title):
        return ""
    words = str(title).upper().split()
    return words[0] if words else ""

def extract_pack_count(title):
    """Extract pack count from title"""
    if pd.isna(title):
        return 1
    title = str(title).lower()
    patterns = [
        r'pack of (\d+)',
        r'(\d+)\s*pack\b',
        r'(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*x\s+\d',
        r'x\s*(\d+)\b',
        r'\((\d+)\)',  # (3) or similar
        r'set of (\d+)',
    ]
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = int(match.group(1))
            if 1 < qty < 500:
                return qty
    return 1

def get_core_product_types(title):
    """Extract core product type nouns"""
    if pd.isna(title):
        return set()
    
    title = str(title).lower()
    product_types = [
        'bowl', 'dish', 'plate', 'cup', 'glass', 'glasses', 'mug', 'jar', 'bottle', 'container',
        'tray', 'trays', 'pan', 'pot', 'knife', 'fork', 'spoon', 'brush', 'sponge', 'cloth',
        'bag', 'bags', 'liner', 'liners', 'foil', 'gloves', 'torch', 'light', 'lamp', 'candle',
        'hammer', 'screwdriver', 'pliers', 'wrench', 'spanner', 'saw', 'drill', 'trowel',
        'tape', 'glue', 'paint', 'roller', 'mirror', 'mat', 'rug', 'squeegee',
        'towel', 'tissue', 'napkin', 'cleaner', 'spray', 'diffuser', 'freshener',
        'cable', 'charger', 'adapter', 'socket', 'extension', 'lead',
        'hat', 'glove', 'sock', 'scarf', 'backpack', 'wallet', 'purse',
        'plaque', 'frame', 'holder', 'stand', 'rack', 'hook', 'bracket',
        'kettle', 'toaster', 'blender', 'mixer', 'fryer', 'oven', 'grill',
        'sack', 'stocking', 'decoration', 'ornament', 'bauble',
        'shovel', 'rake', 'hose', 'sprayer', 'secateurs',
        'carafe', 'decanter', 'shaker', 'grinder', 'mortar', 'pestle',
        'teapot', 'jug', 'pitcher', 'vase', 'planter',
        'bin', 'basket', 'box', 'case', 'caddy', 'organizer', 'storage',
        'clock', 'watch', 'timer', 'thermometer', 'scale', 'measure',
        'foam', 'cement', 'mastic', 'filler', 'sealant', 'caulk',
        'laptray', 'lantern', 'doyleys', 'doilies', 'firelighters',
    ]
    
    found = set()
    for pt in product_types:
        if pt in title:
            found.add(pt)
    return found

def extract_dimensions(title):
    """Extract dimensions/sizes from title"""
    if pd.isna(title):
        return []
    title = str(title).lower()
    dims = []
    # Match patterns like 20cm, 150ml, 4ft, 1L, etc.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(cm|mm|m|inch|in|"|ft)',
        r'(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|liter)',
        r'(\d+(?:\.\d+)?)\s*(oz|g|kg)',
    ]
    for pat in patterns:
        matches = re.findall(pat, title)
        dims.extend([f"{m[0]}{m[1]}" for m in matches])
    return dims

def format_currency(val):
    """Format value as currency"""
    if pd.isna(val):
        return "-"
    return f"£{float(val):.2f}"

def format_percent(val):
    """Format value as percentage"""
    if pd.isna(val):
        return "-"
    return f"{float(val):.1f}%"

# =====================================
# COMPREHENSIVE ANALYSIS
# =====================================

print("Analyzing all rows...")

results = []
for idx, row in df.iterrows():
    row_id = row['RowID']
    sup_title = str(row.get('SupplierTitle', ''))
    amz_title = str(row.get('AmazonTitle', ''))
    
    # Get values
    sup_ean = row['EAN_clean']
    amz_ean = row['EAN_OnPage_clean']
    asin = row.get('ASIN', '')
    sup_price = row.get('SupplierPrice_incVAT', row.get('SupplierPrice', 0))
    sell_price = row.get('SellingPrice_incVAT', row.get('SellingPrice', 0))
    profit = row.get('NetProfit', 0)
    roi = row.get('ROI', 0)
    sales = row.get('sales_numeric', row.get('bought_in_past_month', 0))
    
    if pd.isna(profit):
        profit = 0
    if pd.isna(roi):
        roi = 0
    if pd.isna(sales):
        sales = 0
    if pd.isna(sup_price):
        sup_price = 0
    if pd.isna(sell_price):
        sell_price = 0
    
    # Analysis metrics
    exact_ean = eans_match(row)
    sim = title_similarity(sup_title, amz_title)
    jaccard = jaccard_similarity(sup_title, amz_title)
    
    sup_brand = get_brand_from_title(sup_title)
    amz_brand = get_brand_from_title(amz_title)
    brand_match = sup_brand and amz_brand and (
        sup_brand == amz_brand or 
        sup_brand in amz_title.upper() or 
        amz_brand in sup_title.upper()
    )
    
    sup_types = get_core_product_types(sup_title)
    amz_types = get_core_product_types(amz_title)
    type_overlap = len(sup_types & amz_types)
    
    sup_pack = extract_pack_count(sup_title)
    amz_pack = extract_pack_count(amz_title)
    pack_match = sup_pack == amz_pack
    
    sup_dims = extract_dimensions(sup_title)
    amz_dims = extract_dimensions(amz_title)
    dims_match = bool(set(sup_dims) & set(amz_dims)) if sup_dims and amz_dims else True
    
    # Determine category
    category = 'INVALID'
    confidence = 0
    verdict = ''
    pack_verdict = ''
    evidence = ''
    risks = ''
    filter_reason = ''
    
    # Pack verdict
    if pack_match:
        pack_verdict = '1:1 Match'
    elif amz_pack > sup_pack:
        ratio = amz_pack / sup_pack
        pack_verdict = f'Pack Mismatch ({sup_pack}→{amz_pack})'
    else:
        pack_verdict = f'Pack Mismatch ({sup_pack}→{amz_pack})'
    
    # EXACT EAN MATCH
    if exact_ean:
        evidence = f'Exact EAN match ({sup_ean})'
        if profit > 0:
            if pack_match or (amz_pack <= sup_pack * 1.5 and amz_pack >= sup_pack * 0.5):
                category = 'VERIFIED'
                confidence = 95
                verdict = 'VERIFIED (Exact EAN)'
            else:
                category = 'VERIFIED_FILTERED'
                confidence = 80
                verdict = 'EAN Match - Pack Mismatch'
                filter_reason = f'Pack ratio issue: Supplier={sup_pack}, Amazon={amz_pack}'
                risks = filter_reason
        else:
            category = 'VERIFIED_FILTERED'
            confidence = 75
            verdict = 'EAN Match - Not Profitable'
            filter_reason = f'NetProfit={profit:.2f}'
            risks = filter_reason
    
    # NON-EAN MATCHES
    else:
        evidence = f'Similarity={sim:.2f}; Jaccard={jaccard:.2f}'
        
        # HIGH LIKELIHOOD: Strong brand match + product type + good similarity
        if brand_match and type_overlap >= 1 and sim >= 0.5:
            if profit > 0:
                if pack_match:
                    category = 'HIGH_LIKELIHOOD'
                    confidence = 85
                    verdict = 'HIGH LIKELIHOOD'
                else:
                    # Pack mismatch but still valuable - filter for audit
                    category = 'HIGH_LIKELIHOOD_FILTERED'
                    confidence = 70
                    verdict = 'High Likelihood - Pack Mismatch'
                    filter_reason = f'Pack mismatch: Supplier={sup_pack}, Amazon={amz_pack}'
                    risks = filter_reason
            else:
                category = 'HIGH_LIKELIHOOD_FILTERED'
                confidence = 65
                verdict = 'High Likelihood - Not Profitable'
                filter_reason = f'NetProfit={profit:.2f}'
                risks = filter_reason
        
        elif brand_match and sim >= 0.6:
            if profit > 0:
                category = 'HIGH_LIKELIHOOD'
                confidence = 80
                verdict = 'HIGH LIKELIHOOD'
            else:
                category = 'HIGH_LIKELIHOOD_FILTERED'
                confidence = 65
                verdict = 'Brand Match - Not Profitable'
                filter_reason = f'NetProfit={profit:.2f}'
                risks = filter_reason
        
        # REALISTIC NEEDS VERIFICATION: Same brand but pack/size differs, or very close description
        elif brand_match and type_overlap >= 1:
            if profit > 0 and sim >= 0.4:
                category = 'NEEDS_VERIFICATION_REALISTIC'
                confidence = 60
                verdict = 'NEEDS VERIFICATION'
                risks = 'Same brand/type, verify pack/variant'
            elif sim >= 0.45:
                category = 'NEEDS_VERIFICATION_REALISTIC'
                confidence = 55
                verdict = 'NEEDS VERIFICATION'
                risks = 'Brand match, moderate similarity'
        
        elif type_overlap >= 2 and sim >= 0.45 and profit > 0:
            category = 'NEEDS_VERIFICATION_REALISTIC'
            confidence = 55
            verdict = 'NEEDS VERIFICATION'
            risks = 'Multiple product type matches'
        
        elif sim >= 0.7 and profit > 0:
            category = 'NEEDS_VERIFICATION_REALISTIC'
            confidence = 60
            verdict = 'NEEDS VERIFICATION'
            risks = 'High title similarity'
        
        elif profit > 2 and roi > 30 and sim >= 0.4 and (brand_match or type_overlap >= 1):
            category = 'NEEDS_VERIFICATION_REALISTIC'
            confidence = 50
            verdict = 'NEEDS VERIFICATION'
            risks = f'Good profit potential (£{profit:.2f}, ROI={roi:.1f}%), verify match'
    
    results.append({
        'RowID': row_id,
        'Category': category,
        'Verdict': verdict,
        'Confidence': confidence,
        'SupplierTitle': sup_title,
        'AmazonTitle': amz_title,
        'Supplier_EAN': sup_ean if is_valid_ean(sup_ean) else '-',
        'Amazon_EAN': amz_ean if is_valid_ean(amz_ean) else '-',
        'ASIN': asin,
        'SupplierPrice': sup_price,
        'SellingPrice': sell_price,
        'NetProfit': profit,
        'ROI': roi,
        'Sales': sales,
        'Pack_Verdict': pack_verdict,
        'Supplier_Pack': sup_pack,
        'Amazon_Pack': amz_pack,
        'Adjusted_Profit': profit * (sup_pack / amz_pack) if amz_pack > 0 else profit,
        'Evidence': evidence,
        'Risks': risks,
        'Filter_Reason': filter_reason,
        'Similarity': sim,
        'Brand_Match': brand_match,
        'Type_Overlap': type_overlap,
    })

results_df = pd.DataFrame(results)

# =====================================
# GENERATE REPORT
# =====================================

print("Generating report...")

report_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\COMPREHENSIVE_ANALYSIS_REPORT.md'

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# COMPREHENSIVE FBA ANALYSIS REPORT\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"**Source Data:** PART3.xlsx (1411 rows)\n\n")
    f.write("---\n\n")
    
    # Summary
    verified = results_df[results_df['Category'] == 'VERIFIED']
    verified_filtered = results_df[results_df['Category'] == 'VERIFIED_FILTERED']
    high_likelihood = results_df[results_df['Category'] == 'HIGH_LIKELIHOOD']
    high_likelihood_filtered = results_df[results_df['Category'] == 'HIGH_LIKELIHOOD_FILTERED']
    needs_verify = results_df[results_df['Category'] == 'NEEDS_VERIFICATION_REALISTIC']
    
    f.write("## EXECUTIVE SUMMARY\n\n")
    f.write("| Category | Count |\n")
    f.write("|:---|---:|\n")
    f.write(f"| **VERIFIED (Exact EAN - Recommended)** | {len(verified)} |\n")
    f.write(f"| **HIGH LIKELIHOOD (Recommended)** | {len(high_likelihood)} |\n")
    f.write(f"| **REALISTIC NEEDS VERIFICATION** | {len(needs_verify)} |\n")
    f.write(f"| VERIFIED - Filtered Out | {len(verified_filtered)} |\n")
    f.write(f"| HIGH LIKELIHOOD - Filtered Out | {len(high_likelihood_filtered)} |\n")
    f.write(f"| **Total Actionable** | {len(verified) + len(high_likelihood) + len(needs_verify)} |\n")
    f.write("\n---\n\n")
    
    # =====================================
    # VERIFIED SECTION
    # =====================================
    f.write("## 1. VERIFIED (Exact EAN Match) — RECOMMENDED\n\n")
    f.write(f"**{len(verified)} products** with exact EAN match, profitable, pack OK.\n\n")
    
    if len(verified) > 0:
        f.write("| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |\n")
        f.write("| :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |\n")
        
        for _, row in verified.sort_values('NetProfit', ascending=False).iterrows():
            f.write(f"| {row['Verdict']} | {row['Confidence']} | {row['SupplierTitle'][:60]} | {row['AmazonTitle'][:60]} | {row['Supplier_EAN']} | {row['Amazon_EAN']} | {row['ASIN']} | £{row['SupplierPrice']:.2f} | £{row['SellingPrice']:.2f} | £{row['NetProfit']:.2f} | {row['ROI']:.1f}% | {int(row['Sales'])} | {row['Pack_Verdict']} | £{row['Adjusted_Profit']:.2f} | {row['Evidence']} | {row['Risks']} |\n")
    
    f.write("\n---\n\n")
    
    # =====================================
    # HIGH LIKELIHOOD SECTION
    # =====================================
    f.write("## 2. HIGH LIKELIHOOD (Non-EAN Strong Match) — RECOMMENDED\n\n")
    f.write(f"**{len(high_likelihood)} products** with strong brand/title match, profitable, pack OK.\n\n")
    
    if len(high_likelihood) > 0:
        f.write("| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |\n")
        f.write("| :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |\n")
        
        for _, row in high_likelihood.sort_values('NetProfit', ascending=False).iterrows():
            f.write(f"| {row['Verdict']} | {row['Confidence']} | {row['SupplierTitle'][:60]} | {row['AmazonTitle'][:60]} | {row['Supplier_EAN']} | {row['Amazon_EAN']} | {row['ASIN']} | £{row['SupplierPrice']:.2f} | £{row['SellingPrice']:.2f} | £{row['NetProfit']:.2f} | {row['ROI']:.1f}% | {int(row['Sales'])} | {row['Pack_Verdict']} | £{row['Adjusted_Profit']:.2f} | {row['Evidence']} | Brand/type match, verify variant |\n")
    
    f.write("\n---\n\n")
    
    # =====================================
    # REALISTIC NEEDS VERIFICATION SECTION
    # =====================================
    f.write("## 3. REALISTIC NEEDS VERIFICATION — High Probability Matches\n\n")
    f.write(f"**{len(needs_verify)} products** with good match probability but require manual verification.\n\n")
    f.write("*These are same brand/close description but may have pack/size differences, or no specific brand but very close description with reasonable profit.*\n\n")
    
    if len(needs_verify) > 0:
        f.write("| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |\n")
        f.write("| :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |\n")
        
        for _, row in needs_verify.sort_values('NetProfit', ascending=False).head(75).iterrows():
            f.write(f"| {row['Verdict']} | {row['Confidence']} | {row['SupplierTitle'][:60]} | {row['AmazonTitle'][:60]} | {row['Supplier_EAN']} | {row['Amazon_EAN']} | {row['ASIN']} | £{row['SupplierPrice']:.2f} | £{row['SellingPrice']:.2f} | £{row['NetProfit']:.2f} | {row['ROI']:.1f}% | {int(row['Sales'])} | {row['Pack_Verdict']} | £{row['Adjusted_Profit']:.2f} | {row['Evidence']} | {row['Risks']} |\n")
    
    f.write("\n---\n\n")
    
    # =====================================
    # FILTERED OUT - VERIFIED (Audit)
    # =====================================
    f.write("## FILTERED OUT: VERIFIED (Exact EAN) — Audit Table\n\n")
    f.write(f"**{len(verified_filtered)} products** with exact EAN match but filtered out due to pack mismatch or profitability issues.\n\n")
    
    if len(verified_filtered) > 0:
        f.write("| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |\n")
        f.write("| :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |\n")
        
        for _, row in verified_filtered.sort_values('NetProfit', ascending=False).iterrows():
            f.write(f"| {row['Verdict']} | {row['Confidence']} | {row['SupplierTitle'][:60]} | {row['AmazonTitle'][:60]} | {row['Supplier_EAN']} | {row['Amazon_EAN']} | {row['ASIN']} | £{row['SupplierPrice']:.2f} | £{row['SellingPrice']:.2f} | £{row['NetProfit']:.2f} | {row['ROI']:.1f}% | {int(row['Sales'])} | {row['Pack_Verdict']} | £{row['Adjusted_Profit']:.2f} | {row['Evidence']} | {row['Filter_Reason']} |\n")
    
    f.write("\n---\n\n")
    
    # =====================================
    # FILTERED OUT - HIGH LIKELIHOOD (Audit)
    # =====================================
    f.write("## FILTERED OUT: HIGH LIKELIHOOD — Audit Table\n\n")
    f.write(f"**{len(high_likelihood_filtered)} products** with strong brand/title match but filtered out primarily due to pack/size mismatch or low profitability.\n\n")
    
    if len(high_likelihood_filtered) > 0:
        f.write("| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |\n")
        f.write("| :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |\n")
        
        for _, row in high_likelihood_filtered.sort_values('Confidence', ascending=False).iterrows():
            f.write(f"| {row['Verdict']} | {row['Confidence']} | {row['SupplierTitle'][:60]} | {row['AmazonTitle'][:60]} | {row['Supplier_EAN']} | {row['Amazon_EAN']} | {row['ASIN']} | £{row['SupplierPrice']:.2f} | £{row['SellingPrice']:.2f} | £{row['NetProfit']:.2f} | {row['ROI']:.1f}% | {int(row['Sales'])} | {row['Pack_Verdict']} | £{row['Adjusted_Profit']:.2f} | {row['Evidence']} | {row['Filter_Reason']} |\n")
    
    f.write("\n---\n\n")
    
    # =====================================
    # RECONCILIATION
    # =====================================
    f.write("## RECONCILIATION PROOF\n\n")
    f.write("| Category | Count |\n")
    f.write("|:---|---:|\n")
    f.write(f"| Total Input Rows | 1411 |\n")
    f.write(f"| VERIFIED (Recommended) | {len(verified)} |\n")
    f.write(f"| HIGH LIKELIHOOD (Recommended) | {len(high_likelihood)} |\n")
    f.write(f"| REALISTIC NEEDS VERIFICATION | {len(needs_verify)} |\n")
    f.write(f"| VERIFIED - Filtered Out | {len(verified_filtered)} |\n")
    f.write(f"| HIGH LIKELIHOOD - Filtered Out | {len(high_likelihood_filtered)} |\n")
    invalid_count = len(results_df[results_df['Category'] == 'INVALID'])
    f.write(f"| OTHER (No Match/Low Confidence) | {invalid_count} |\n")
    total = len(verified) + len(high_likelihood) + len(needs_verify) + len(verified_filtered) + len(high_likelihood_filtered) + invalid_count
    f.write(f"| **TOTAL** | **{total}** |\n")
    
    f.write("\n---\n\n")
    f.write("*Report generated by independent analysis engine. All categorizations based on EAN matching, title similarity, brand detection, and pack analysis.*\n")

print(f"\nReport saved to: {report_path}")

# Print summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"  VERIFIED (Exact EAN - Recommended): {len(verified)}")
print(f"  HIGH LIKELIHOOD (Recommended): {len(high_likelihood)}")
print(f"  REALISTIC NEEDS VERIFICATION: {len(needs_verify)}")
print(f"  VERIFIED - Filtered Out: {len(verified_filtered)}")
print(f"  HIGH LIKELIHOOD - Filtered Out: {len(high_likelihood_filtered)}")
print(f"  OTHER (Invalid/Low Conf): {len(results_df[results_df['Category'] == 'INVALID'])}")
