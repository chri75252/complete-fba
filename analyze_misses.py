
import pandas as pd
import json

ledger_path = r'runs_phase3_test\20260109_010428\coverage_ledger.csv'
df = pd.read_csv(ledger_path)

print(f"Total Rows: {len(df)}")
# Handle string/float mismatch in bucket column just in case
df['bucket'] = df['bucket'].astype(str)
filtered = df[df['bucket'] == 'FILTERED_OUT']
print(f"Filtered Out: {len(filtered)}")

# Filter for High Similarity Matches that were Filtered
# These are potential "Highly Likely" candidates killed by Brand Gate
missed_text_matches = df[
    (df['bucket'] == 'FILTERED_OUT') & 
    (df['supplier_ean'] != df['amazon_ean']) &
    (df['confidence'] > 70)  # Using confidence as proxy for similarity if similarity col not in CSV
]

# Note: CSV might not have 'similarity' column. Let's check columns first.
# If 'similarity' exists, use it.
if 'similarity' in df.columns:
     missed_text_matches = df[
        (df['bucket'] == 'FILTERED_OUT') & 
        (df['supplier_ean'] != df['amazon_ean']) &
        (df['similarity'] > 0.3)
    ]

print(f"Potential Missed Text Matches: {len(missed_text_matches)}")
print('\n--- MISSED TEXT MATCH EXAMPLES ---')

count = 0
for _, row in missed_text_matches.iterrows():
    if count >= 20: break
    
    # Skip if filtered for profit (unless we want to verify profit calculation)
    # We care about BRAND/MATCHING filters
    if "profit" in str(row.get('filter_reason', '')).lower():
        continue

    print(f"RowID: {row.get('row_id')}")
    print(f"Titles: {str(row.get('supplier_title', ''))[:40]}... VS {str(row.get('amazon_title', ''))[:40]}...")
    print(f"Reason: {row.get('filter_reason')}")
    print(f"Evidence: {row.get('key_match_evidence')}")
    print('--------------------------------------------------')
    count += 1

