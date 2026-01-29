import pandas as pd
import re

# Load the data
df = pd.read_excel('part 4 jan.xlsx')

print("=== COLUMN NAMES ===")
for c in df.columns:
    print(f"  '{c}'")

print(f"\n=== DATA SUMMARY ===")
print(f"Total rows: {len(df)}")

# Find ROI column (may have different formatting)
roi_col = None
for c in df.columns:
    if 'roi' in c.lower():
        roi_col = c
        break

# Filter for profitable rows with sales
profit_col = 'NetProfit'
sales_col = 'bought_in_past_month'

profitable = df[df[profit_col] > 0]
print(f"Rows with NetProfit > 0: {len(profitable)}")

with_sales = df[df[sales_col] > 0]
print(f"Rows with bought_in_past_month > 0: {len(with_sales)}")

viable = df[(df[profit_col] > 0) & (df[sales_col] > 0)]
print(f"Rows with BOTH NetProfit > 0 AND Sales > 0: {len(viable)}")

# Show sample of viable rows
print("\n=== SAMPLE VIABLE ROWS (first 20) ===")
key_cols = ['EAN', 'EAN_OnPage', 'ASIN', 'SupplierTitle', 'AmazonTitle', 
            'SupplierPrice_incVAT', 'SellingPrice_incVAT', profit_col, roi_col, sales_col]
print(viable[key_cols].head(20).to_string())

# Save viable rows to CSV for detailed analysis
viable.to_csv('viable_products.csv', index=False)
print(f"\nSaved {len(viable)} viable rows to viable_products.csv")
