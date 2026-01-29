"""
Verify product matches by analyzing title similarity between Supplier and Amazon titles.
Classify matches as: TRUE MATCH, POSSIBLE MATCH, or FALSE MATCH
"""

import pandas as pd
from difflib import SequenceMatcher
import re

# Load the prioritized products
df = pd.read_csv(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\profitable_products_prioritized.csv")

# Get products with sales, sorted by priority
products_to_verify = df[df['sales_numeric'] > 0].sort_values('priority_score', ascending=False)

# Enhanced title matching
def analyze_match(supplier_title, amazon_title):
    if pd.isna(supplier_title) or pd.isna(amazon_title):
        return 0, "UNKNOWN", []
    
    supplier = str(supplier_title).lower().strip()
    amazon = str(amazon_title).lower().strip()
    
    # Basic similarity
    basic_score = SequenceMatcher(None, supplier, amazon).ratio()
    
    # Extract key product identifiers
    reasons = []
    
    # Check for brand name matches
    brands = ['booja-booja', 'zog', 'aurora', 'soft touch', 'peppa pig', 'disney', 
              'nursery time', 'watch me grow', 'just too cute', 'mumbles', 'suki']
    for brand in brands:
        if brand in supplier and brand in amazon:
            reasons.append(f"Brand match: {brand}")
    
    # Check for product type keywords
    product_types = {
        'bib': ['bib', 'bibs'],
        'sock': ['sock', 'socks'],
        'blanket': ['blanket', 'fleece', 'throw'],
        'balloon': ['balloon', 'balloons'],
        'toy': ['toy', 'plush', 'soft toy'],
        'chocolate': ['chocolate', 'truffles', 'cocoa'],
        'basket': ['basket', 'trug', 'hamper'],
        'flower': ['flower', 'rose', 'lily', 'bouquet'],
        'baby': ['baby', 'infant', 'newborn'],
    }
    
    for ptype, keywords in product_types.items():
        supplier_has = any(kw in supplier for kw in keywords)
        amazon_has = any(kw in amazon for kw in keywords)
        if supplier_has and amazon_has:
            reasons.append(f"Type match: {ptype}")
        elif supplier_has and not amazon_has:
            reasons.append(f"Type MISMATCH: supplier={ptype}, amazon=different")
    
    # Check for completely unrelated categories (FALSE MATCHES)
    false_match_indicators = [
        ('baby', ['lego', 'vr headset', 'car', 'laptop', 'phone', 'gaming', 'camera']),
        ('bib', ['electronics', 'headset', 'charger', 'cable']),
        ('balloon', ['furniture', 'appliance', 'machine']),
        ('flower', ['gun', 'tool', 'power', 'electric']),
    ]
    
    supplier_category = None
    for cat, _ in false_match_indicators:
        if cat in supplier:
            supplier_category = cat
            break
    
    if supplier_category:
        for cat, false_kws in false_match_indicators:
            if cat == supplier_category:
                for kw in false_kws:
                    if kw in amazon:
                        reasons.append(f"FALSE: {supplier_category} matched to {kw}")
    
    # Determine verdict
    if basic_score > 0.7:
        verdict = "[OK] TRUE MATCH"
    elif basic_score > 0.4 and len([r for r in reasons if 'match:' in r.lower()]) > 0:
        verdict = "[OK] TRUE MATCH"
    elif basic_score > 0.3:
        verdict = "[??] POSSIBLE MATCH"
    elif any('FALSE' in r for r in reasons):
        verdict = "[XX] FALSE MATCH"
    elif basic_score > 0.15:
        verdict = "[??] NEEDS VERIFICATION"
    else:
        verdict = "[XX] LIKELY FALSE"
    
    return basic_score, verdict, reasons

# Analyze all products with sales
results = []
for idx, row in products_to_verify.iterrows():
    score, verdict, reasons = analyze_match(row['SupplierTitle'], row['AmazonTitle'])
    results.append({
        'ASIN': row['ASIN'],
        'EAN': row['EAN'],
        'SupplierTitle': str(row['SupplierTitle'])[:60],
        'AmazonTitle': str(row['AmazonTitle'])[:60],
        'TitleMatch': score,
        'Verdict': verdict,
        'Reasons': '; '.join(reasons) if reasons else 'Similarity only',
        'Sales': row['sales_numeric'],
        'NetProfit': row['NetProfit'],
        'ROI': row['ROI']
    })

results_df = pd.DataFrame(results)

# Save full results
results_df.to_csv(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\verified_matches.csv", index=False)

# Print summary
print("=" * 100)
print("MATCH VERIFICATION SUMMARY")
print("=" * 100)

verdicts = results_df['Verdict'].value_counts()
print("\nVerdict Distribution:")
print(verdicts)

print("\n" + "=" * 100)
print("TRUE MATCHES (High Confidence - Ready to Buy)")
print("=" * 100)
true_matches = results_df[results_df['Verdict'] == '[OK] TRUE MATCH'].head(30)
for idx, row in true_matches.iterrows():
    print(f"\n[{row['ASIN']}] Sales: {row['Sales']:.0f} | Profit: £{row['NetProfit']:.2f}")
    print(f"  Supplier: {row['SupplierTitle']}...")
    print(f"  Amazon:   {row['AmazonTitle']}...")
    print(f"  Score: {row['TitleMatch']:.2f} | {row['Reasons']}")

print("\n" + "=" * 100)
print("FALSE MATCHES (Do NOT Buy - Wrong Products)")
print("=" * 100)
false_matches = results_df[results_df['Verdict'].str.contains('FALSE|LIKELY FALSE')].head(20)
for idx, row in false_matches.iterrows():
    print(f"\n[{row['ASIN']}] [XX] FALSE MATCH")
    print(f"  Supplier: {row['SupplierTitle']}...")
    print(f"  Amazon:   {row['AmazonTitle']}...")
    print(f"  Score: {row['TitleMatch']:.2f} | {row['Reasons']}")

print("\n" + "=" * 100)
print("NEEDS MANUAL VERIFICATION")
print("=" * 100)
needs_verify = results_df[results_df['Verdict'].str.contains('POSSIBLE|NEEDS')].head(20)
for idx, row in needs_verify.iterrows():
    print(f"\n[{row['ASIN']}] [??] VERIFY MANUALLY")
    print(f"  Supplier: {row['SupplierTitle']}...")
    print(f"  Amazon:   {row['AmazonTitle']}...")
    print(f"  Score: {row['TitleMatch']:.2f}")

print(f"\n\nTotal analyzed: {len(results_df)}")
print(f"True matches: {len(results_df[results_df['Verdict'] == '[OK] TRUE MATCH'])}")
print(f"False matches: {len(results_df[results_df['Verdict'].str.contains('FALSE|LIKELY')])}")
print(f"Need verification: {len(results_df[results_df['Verdict'].str.contains('POSSIBLE|NEEDS')])}")
