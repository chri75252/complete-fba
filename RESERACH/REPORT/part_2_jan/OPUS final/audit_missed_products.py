"""
COMPREHENSIVE AUDIT: Check for Missed Products in Initial Analysis
This script identifies potential products that were missed or incorrectly excluded.
"""

import pandas as pd
import re

# Load original data
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\part_2_jan.xlsx"
df = pd.read_excel(INPUT_PATH)

print("=" * 80)
print("COMPREHENSIVE AUDIT: Checking for Missed Products")
print("=" * 80)
print(f"\nTotal rows in source file: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Check for required columns
print(f"\nData quality check:")
print(f"- Rows with SupplierTitle: {df['SupplierTitle'].notna().sum()}")
print(f"- Rows with AmazonTitle: {df['AmazonTitle'].notna().sum()}")
print(f"- Rows with ASIN: {df['ASIN'].notna().sum()}")
print(f"- Rows with positive NetProfit: {(df['NetProfit'] > 0).sum()}")

if 'bought_in_past_month' in df.columns:
    print(f"- Rows with Sales > 0: {(df['bought_in_past_month'] > 0).sum()}")

# EAN cleaning function
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return re.sub(r'\D', '', s)

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)

# ==============================================================================
# PART 1: FIND ALL EXACT EAN MATCHES
# ==============================================================================
print("\n" + "=" * 80)
print("PART 1: ALL EXACT EAN MATCHES IN SOURCE DATA")
print("=" * 80)

exact_ean_matches = df[
    (df['EAN_clean'].str.len() >= 8) & 
    (df['EAN_OnPage_clean'].str.len() >= 8) & 
    (df['EAN_clean'] == df['EAN_OnPage_clean'])
].copy()

print(f"\nTotal exact EAN matches (basic check): {len(exact_ean_matches)}")

# List ALL EAN matches
print("\nALL EAN Matches found in source data:")
print("-" * 80)
ean_match_list = []
for idx, row in exact_ean_matches.iterrows():
    ean_match_list.append({
        'RowID': idx + 1,
        'EAN': row['EAN_clean'],
        'SupplierTitle': str(row['SupplierTitle'])[:50],
        'AmazonTitle': str(row['AmazonTitle'])[:50],
        'NetProfit': row['NetProfit'],
        'Sales': row.get('bought_in_past_month', 0)
    })
    print(f"Row {idx+1}: EAN={row['EAN_clean']} | Profit=£{row['NetProfit']:.2f} | {str(row['SupplierTitle'])[:40]}")

# ==============================================================================
# PART 2: IDENTIFY KNOWN BRANDS IN SOURCE DATA
# ==============================================================================
print("\n" + "=" * 80)
print("PART 2: PRODUCTS WITH KNOWN BRAND MATCHES")
print("=" * 80)

KNOWN_BRANDS = [
    "BRIGHT & HOMELY", "CHEF AID", "MASON CASH", "PAN AROMA", "SCHOTT ZWIESEL",
    "PRICE & KENSINGTON", "BAKER & SALT", "BLUE CANYON", "KEEP IT HANDY",
    "SMART CHOICE", "WASTE SMART", "WORLD OF PETS", "EXTRA SELECT", "THE BIG CHEESE",
    "ELBOW GREASE", "PPS", "APOLLO", "DEKTON", "PRIMA", "SIL", "ASHLEY", "ADORN", 
    "RYSONS", "HOBBY", "FESTIVE", "AMTECH", "THL", "ROLSON", "BLACKSPUR", "KINGFISHER",
    "SMART", "MARKSMAN", "BETTINA", "JAUNTY", "EXTRASTAR", "PREMIER", "EUROWRAP",
    "RSW", "DLUX", "TALA", "OPAL", "MINKY", "PROKLEEN", "GIFTMAKER",
    "TIDYZ", "AIRWICK", "FAIRY", "DUNLOP", "PYREX", "KILROCK",
    "SOUDAL", "EVERBUILD", "STATUS", "SISTEMA", "LAV", "WHAM",
    "THERMOS", "ECO", "DRAPER", "FALCON", "ULTRATAPE", "PENDEFORD", 
    "BEAUFORT", "MASTERCLASS", "BACOFOIL", "MARIGOLD", "SWIRL", "DETTOL", 
    "MOKATE", "PASABAHCE", "CHUPA", "KILNER", "EVERREADY", "EVEREADY", 
    "ELLIOTT", "PRODEC", "ADDIS", "FORTHGLADE"
]

def extract_brand(title):
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand.upper() in title_upper:
            return brand
    return None

df['SupBrand'] = df['SupplierTitle'].apply(extract_brand)
df['AmzBrand'] = df['AmazonTitle'].apply(extract_brand)

# Count brand matches
brand_matches = df[(df['SupBrand'].notna()) & (df['AmzBrand'].notna()) & (df['SupBrand'] == df['AmzBrand'])]
print(f"\nProducts with matching brand in both titles: {len(brand_matches)}")

# Products with brand in supplier title only
sup_brand_only = df[(df['SupBrand'].notna()) & (df['NetProfit'] > 0)]
print(f"Products with brand detected in supplier title (positive profit): {len(sup_brand_only)}")

# ==============================================================================
# PART 3: HIGH-VALUE PRODUCTS CHECK
# ==============================================================================
print("\n" + "=" * 80)
print("PART 3: HIGH-VALUE PRODUCTS (Potential Misses)")
print("=" * 80)

# High profit products
high_profit = df[df['NetProfit'] > 5]
print(f"\nProducts with NetProfit > £5: {len(high_profit)}")

# High profit + sales
if 'bought_in_past_month' in df.columns:
    high_value = df[(df['NetProfit'] > 3) & (df['bought_in_past_month'] >= 100)]
    print(f"Products with NetProfit > £3 AND Sales >= 100: {len(high_value)}")

# ==============================================================================
# PART 4: COMPARE WITH INITIAL REPORT
# ==============================================================================
print("\n" + "=" * 80)
print("PART 4: COMPARISON WITH INITIAL REPORT")
print("=" * 80)

# Read the initial report to extract row count
initial_report_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\OPUS final\PHASEA_MANUAL_REPORT_20260103_002701.md"

try:
    with open(initial_report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # Count entries in each section
    verified_count = report_content.count("| VERIFIED |") 
    filtered_count = report_content.count("| FILTERED |")
    highly_likely_count = report_content.count("| HIGHLY LIKELY |")
    needs_verif_count = report_content.count("| NEEDS VERIF |")
    
    print(f"\nCounts from initial report:")
    print(f"- VERIFIED entries: {verified_count}")
    print(f"- FILTERED entries: {filtered_count}")
    print(f"- HIGHLY LIKELY entries: {highly_likely_count}")
    print(f"- NEEDS VERIFICATION entries: {needs_verif_count}")
    print(f"- Total categorized: {verified_count + filtered_count + highly_likely_count + needs_verif_count}")
    
except Exception as e:
    print(f"Could not read initial report: {e}")

# ==============================================================================
# PART 5: ROOT CAUSE ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("PART 5: ROOT CAUSE ANALYSIS - Why Products Might Be Missed")
print("=" * 80)

# Check 1: Products excluded due to no valid EAN
no_ean_but_profitable = df[(df['EAN_clean'].str.len() < 8) & (df['NetProfit'] > 2)]
print(f"\n1. Products with invalid/missing EAN but NetProfit > £2: {len(no_ean_but_profitable)}")

# Check 2: Products with brand in title but not matched
brand_in_sup_not_amz = df[(df['SupBrand'].notna()) & (df['AmzBrand'].isna()) & (df['NetProfit'] > 0)]
print(f"2. Products with brand in supplier but not Amazon (positive profit): {len(brand_in_sup_not_amz)}")

# Check 3: Products with no brand detected at all
no_brand_high_profit = df[(df['SupBrand'].isna()) & (df['NetProfit'] > 3)]
print(f"3. Products with no brand detected but NetProfit > £3: {len(no_brand_high_profit)}")

# ==============================================================================
# PART 6: SPECIFIC MISSED PRODUCTS CHECK
# ==============================================================================
print("\n" + "=" * 80)
print("PART 6: SPECIFIC HIGH-VALUE PRODUCTS TO CHECK")
print("=" * 80)

# Find potentially missed high-value products
potential_misses = df[
    (df['NetProfit'] > 5) &  # High profit
    (df['EAN_clean'] != df['EAN_OnPage_clean']) &  # Not exact EAN match (so might be excluded)
    (df['SupBrand'].notna())  # Has brand
].copy()

print(f"\nHigh-value products (Profit>£5) with brand but no EAN match: {len(potential_misses)}")
print("\nTop 20 to manually verify:")
print("-" * 80)

for idx, row in potential_misses.head(20).iterrows():
    print(f"Row {idx+1}: Brand={row['SupBrand']}")
    print(f"  Supplier: {str(row['SupplierTitle'])[:60]}")
    print(f"  Amazon: {str(row['AmazonTitle'])[:60]}")
    print(f"  Profit: £{row['NetProfit']:.2f} | Sales: {row.get('bought_in_past_month', 'N/A')}")
    print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)

print(f"""
SOURCE DATA:
- Total rows in part_2_jan.xlsx: {len(df)}
- Rows with positive profit: {(df['NetProfit'] > 0).sum()}

EAN MATCH ANALYSIS:
- Exact EAN matches found: {len(exact_ean_matches)}
- Products with brand match (both titles): {len(brand_matches)}

POTENTIAL COVERAGE GAPS:
- Products with brand only in supplier title: {len(brand_in_sup_not_amz)}
- High-profit products without brand detected: {len(no_brand_high_profit)}
- High-value products that may need manual review: {len(potential_misses)}

If the initial report had:
- ~33 VERIFIED products (should match ~{len(exact_ean_matches)} EAN matches)
- ~132+ HIGHLY LIKELY products (from {len(brand_matches)} brand matches)
""")

# Save detailed list to CSV for manual review
output_csv = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\OPUS final\AUDIT_ALL_EAN_MATCHES.csv"
ean_df = pd.DataFrame(ean_match_list)
ean_df.to_csv(output_csv, index=False)
print(f"\nAll EAN matches saved to: {output_csv}")
