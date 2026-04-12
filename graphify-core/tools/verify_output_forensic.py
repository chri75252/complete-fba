import pandas as pd

INPUT_CSV = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\deep_analysis_20251212_ANTIGRAVITY_PROTECTED.csv"

df = pd.read_csv(INPUT_CSV)

print("=" * 60)
print("FORENSIC VERIFICATION OF GENERATED REPORT")
print("=" * 60)

# 1. Exact EAN Matches - Profitable Only
exact_matches = df[(df['category'] == 'EXACT_EAN_MATCH') & (df['Adjusted_Profit'] > 0)]
print(f"\n[1] EXACT EAN MATCHES (Profitable): {len(exact_matches)}")

# 2. Check for suspicious ROI (>500%)
suspicious_roi = exact_matches[exact_matches['ROI_Adjusted'] > 500]
print(f"[2] Suspicious ROI (>500%): {len(suspicious_roi)}")

# 3. Check for pack mismatches within exact EAN
pack_issues = exact_matches[exact_matches['Qty_Ratio'] != 1.0]
print(f"[3] Pack Ratio Issues (Qty_Ratio != 1): {len(pack_issues)}")

# 4. Sample verification - check if EANs ACTUALLY match
print("\n--- SAMPLE EXACT MATCH VERIFICATION (First 10) ---")
for idx, row in exact_matches.head(10).iterrows():
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    match_status = "✓ MATCH" if ean_sup == ean_amz else "✗ MISMATCH"
    print(f"{match_status}: {ean_sup} vs {ean_amz}")
    print(f"   Supplier: {str(row['SupplierTitle'])[:60]}")
    print(f"   Amazon:   {str(row['AmazonTitle'])[:60]}")
    print(f"   Qty Ratio: {row['Qty_Ratio']:.1f} | Profit: £{row['Adjusted_Profit']:.2f} | ROI: {row['ROI_Adjusted']:.0f}%")
    print()

# 5. Suspicious ROI deep dive
if len(suspicious_roi) > 0:
    print("\n--- SUSPICIOUS ROI (>500%) - LIKELY FALSE POSITIVES ---")
    for idx, row in suspicious_roi.head(10).iterrows():
        print(f"EAN: {row['EAN']}")
        print(f"   Supplier: {str(row['SupplierTitle'])[:60]}")
        print(f"   Amazon:   {str(row['AmazonTitle'])[:60]}")
        print(f"   ** ROI: {row['ROI_Adjusted']:.0f}% ** Profit: £{row['Adjusted_Profit']:.2f}")
        print(f"   Qty Ratio: {row['Qty_Ratio']:.1f} (Sup: {row['Sup_Qty']}, Amz: {row['Amz_Qty']})")
        print()

# 6. HIGH LIKELIHOOD - Title mismatch check
high_likelihood = df[(df['category'] == 'HIGH_LIKELIHOOD') & (df['Adjusted_Profit'] > 0)]
print(f"\n[6] HIGH LIKELIHOOD MATCHES: {len(high_likelihood)}")
print("--- SAMPLE TITLE COMPARISON (First 5) ---")
for idx, row in high_likelihood.head(5).iterrows():
    print(f"Title Match: {row['title_match']:.2f}")
    print(f"   Supplier: {str(row['SupplierTitle'])[:70]}")
    print(f"   Amazon:   {str(row['AmazonTitle'])[:70]}")
    print(f"   Profit: £{row['Adjusted_Profit']:.2f} | ROI: {row['ROI_Adjusted']:.0f}%")
    print()

print("=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
