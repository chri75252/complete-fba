import pandas as pd

# Load the confirmed entries
confirmed_ean = pd.read_csv('confirmed_exact_ean.csv')
confirmed_non_ean = pd.read_csv('confirmed_non_ean.csv')

print("="*100)
print("COMPLETE LIST OF CONFIRMED PRODUCT MATCHES")
print("="*100)
print()

print("-"*100)
print("SECTION A: CONFIRMED VIA EXACT EAN MATCH (14 products)")
print("-"*100)
print()

for idx, row in confirmed_ean.iterrows():
    print(f"{idx+1}. ASIN: {row['ASIN']}")
    print(f"   EAN: {row['EAN']}")
    print(f"   Supplier: {row['SupplierTitle']}")
    print(f"   Amazon: {row['AmazonTitle'][:100]}...")
    print(f"   NetProfit: {row['NetProfit']:.2f} | Sales: {row['Sales']}")
    print(f"   Verdict: {row['PackVerdict']}")
    print()

print()
print("-"*100)
print(f"SECTION B: CONFIRMED VIA TITLE ANALYSIS ({len(confirmed_non_ean)} products)")
print("-"*100)
print()

# Sort by sales and profit
confirmed_non_ean_sorted = confirmed_non_ean.sort_values(['Sales', 'NetProfit'], ascending=[False, False])

for idx, (_, row) in enumerate(confirmed_non_ean_sorted.iterrows()):
    print(f"{idx+1}. ASIN: {row['ASIN']}")
    if pd.notna(row.get('EAN')):
        print(f"   EAN: {row['EAN']}")
    print(f"   Supplier: {row['SupplierTitle']}")
    amz_title = str(row['AmazonTitle'])[:100] if pd.notna(row.get('AmazonTitle')) else 'N/A'
    print(f"   Amazon: {amz_title}...")
    print(f"   Similarity: {row['TitleSimilarity']:.2f} | Tokens: {row.get('TokenOverlap', 'N/A')}")
    print(f"   NetProfit: {row['NetProfit']:.2f} | Sales: {row['Sales']}")
    print(f"   Reason: {row.get('Reason', 'N/A')}")
    print()

print("="*100)
print(f"TOTAL CONFIRMED: {len(confirmed_ean) + len(confirmed_non_ean)}")
print("="*100)

# Create a combined CSV
all_confirmed = pd.concat([
    confirmed_ean[['ASIN', 'EAN', 'SupplierTitle', 'AmazonTitle', 'NetProfit', 'Sales', 'PackVerdict']].assign(MatchType='Exact EAN'),
    confirmed_non_ean[['ASIN', 'EAN', 'SupplierTitle', 'AmazonTitle', 'NetProfit', 'Sales']].assign(PackVerdict='Confirmed (Title)', MatchType='Title Analysis')
])
all_confirmed.to_csv('ALL_CONFIRMED_PRODUCTS.csv', index=False)
print("\nSaved to: ALL_CONFIRMED_PRODUCTS.csv")
