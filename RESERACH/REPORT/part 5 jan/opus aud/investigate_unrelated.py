import pandas as pd
import random

# Load source data
source_file = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\part 5 jan.xlsx"
df = pd.read_excel(source_file)

print("="*80)
print("UNRELATED ROWS INVESTIGATION")
print("="*80)
print(f"\nTotal rows in source: {len(df)}")
print(f"Categorized in report: 636")
print(f"UNRELATED (not shown): {len(df) - 636}")

# The report included:
# - 35 VERIFIED RECOMMENDED
# - 9 VERIFIED AUDITED OUT
# - 62 HIGHLY LIKELY RECOMMENDED
# - 0 HIGHLY LIKELY AUDITED OUT
# - 530 NEEDS VERIFICATION
#Total: 636 rows shown

# Extract RowIDs from categorized products
# Since the report shows only 636 products, we need to see which 2,153 were excluded

# Sample 50 random rows from the full dataset to check for potential misses
sample_size = min(50, len(df))
sample_indices = random.sample(range(len(df)), sample_size)

print(f"\n\nSampling {sample_size} random rows for manual inspection:")
print("="*80)

output_file = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\opus aud\SAMPLE_UNRELATED_ROWS.csv"

# Extract key columns for analysis
sample_df = df.iloc[sample_indices][['EAN', 'EAN_OnPage', 'SupplierTitle', 'AmazonTitle', 'NetProfit', 'bought_in_past_month']].copy()
sample_df['RowID'] = [i+2 for i in sample_indices]  # Excel row (1-indexed + header)
sample_df = sample_df[['RowID', 'EAN', 'EAN_OnPage', 'SupplierTitle', 'AmazonTitle', 'NetProfit', 'bought_in_past_month']]

# Save sample
sample_df.to_csv(output_file, index=False)
print(f"\nSample saved to: {output_file}")

# Print first 10 for immediate review
print("\nFirst 10 sampled rows:")
print("-"*80)
for idx, row in sample_df.head(10).iterrows():
    print(f"\nRow {row['RowID']}:")
    print(f"  EAN: {row['EAN']} | Amazon EAN: {row['EAN_OnPage']}")
    print(f"  Supplier: {str(row['SupplierTitle'])[:70]}...")
    print(f"  Amazon:   {str(row['AmazonTitle'])[:70]}...")
    print(f"  Profit: £{row['NetProfit']:.2f} | Sales: {row['bought_in_past_month']}")

# Check for exact EAN matches in sample
def clean_ean(ean):
    if pd.isna(ean):
        return ''
    return str(ean).replace('.0', '').strip()

sample_df['EAN_clean'] = sample_df['EAN'].apply(clean_ean)
sample_df['EAN_OnPage_clean'] = sample_df['EAN_OnPage'].apply(clean_ean)
sample_df['EAN_Match'] = (sample_df['EAN_clean'] == sample_df['EAN_OnPage_clean']) & (sample_df['EAN_clean'] != '') & (sample_df['EAN_OnPage_clean'] != '')

exact_ean_in_sample = sample_df[sample_df['EAN_Match'] == True]

print(f"\n\n⚠️ EXACT EAN MATCHES IN SAMPLE: {len(exact_ean_in_sample)}")
if len(exact_ean_in_sample) > 0:
    print("\n\n🚨 CRITICAL: Found exact EAN matches that were excluded!")
    print("="*80)
    for idx, row in exact_ean_in_sample.iterrows():
        print(f"\nRow {row['RowID']} - EXACT EAN MATCH MISSED:")
        print(f"  EAN: {row['EAN_clean']}")
        print(f"  Supplier: {row['SupplierTitle']}")
        print(f"  Amazon: {row['AmazonTitle']}")
        print(f"  Profit: £{row['NetProfit']:.2f}")
        print(f"  Sales: {row['bought_in_past_month']}")

# Check for brand matches
def extract_first_word(title):
    if pd.isna(title):
        return ''
    words = str(title).split()
    if words:
        return words[0].upper()
    return ''

sample_df['Sup_Brand'] = sample_df['SupplierTitle'].apply(extract_first_word)
sample_df['Amz_Brand'] = sample_df['AmazonTitle'].apply(lambda x: str(x).upper() if pd.notna(x) else '')

# Check if supplier brand appears anywhere in Amazon title
sample_df['Brand_Match'] = sample_df.apply(
    lambda row: row['Sup_Brand'] in row['Amz_Brand'] if row['Sup_Brand'] and len(row['Sup_Brand']) > 2 else False,
    axis=1
)

brand_matches_in_sample = sample_df[sample_df['Brand_Match'] == True]

print(f"\n\n⚠️ BRAND MATCHES IN SAMPLE: {len(brand_matches_in_sample)}")
if len(brand_matches_in_sample) > 0:
    print("\n\n🔍 Potential Brand Matches that were excluded:")
    print("="*80)
    for idx, row in brand_matches_in_sample.head(10).iterrows():
        print(f"\nRow {row['RowID']} - Brand: {row['Sup_Brand']}")
        print(f"  Supplier: {row['SupplierTitle'][:70]}...")
        print(f"  Amazon: {row['AmazonTitle'][:70]}...")
        print(f"  Profit: £{row['NetProfit']:.2f} | Sales: {row['bought_in_past_month']}")

print("\n\n" + "="*80)
print("INVESTIGATION COMPLETE")
print("="*80)
print(f"\nFull sample saved to: {output_file}")
print(f"Sample size: {len(sample_df)} rows")
print(f"Exact EAN matches found: {len(exact_ean_in_sample)}")
print(f"Potential brand matches found: {len(brand_matches_in_sample)}")
