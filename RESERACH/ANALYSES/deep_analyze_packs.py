import pandas as pd
import re

# Load the previously categorized data
input_path = r"RESERACH\categorized_products_20251207.csv"
output_path = r"RESERACH\deep_analysis_results.csv"

try:
    df = pd.read_csv(input_path)
except FileNotFoundError:
    # Fallback to absolute path if relative fails (based on user context)
    input_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\categorized_products_20251207.csv"
    df = pd.read_csv(input_path)

def extract_quantity(title):
    """
    Extracts pack quantity from a product title.
    Defaults to 1 if no clear quantity is found.
    """
    if pd.isna(title):
        return 1.0
    
    title = str(title).lower()
    
    # Common patterns
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack',
        r'\b(\d+)\s*pk',
        r'(\d+)\s*pcs',
        r'(\d+)\s*pieces?',  # piece or pieces
        r'(\d+)\s*pairs?',   # pair or pairs
        r'(\d+)\s*sets?',
        r'\bx(\d+)\b',
        r'\((?:pack of )?(\d+)\)'
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            try:
                qty = float(match.group(1))
                if qty > 1:
                    return qty
            except:
                continue
                
    return 1.0

# Apply extraction
df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)

# Calculate Ratio: How many Supplier Units make 1 Amazon Unit?
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    original_profit = row['NetProfit']
    supplier_price = row['SupplierPrice_incVAT']
    ratio = row['Qty_Ratio']
    
    try:
        p = float(original_profit)
        c = float(supplier_price)
    except:
        return 0.0
        
    adjustment = c * (ratio - 1)
    
    return p - adjustment

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

def analyze_outcome(row):
    if row['Qty_Ratio'] == 1.0:
        return "MATCH (1:1)"
    elif row['Qty_Ratio'] > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"PROFITABLE BUNDLE ({int(row['Qty_Ratio'])}x)"
        else:
            return f"LOSS MAKING BUNDLE ({int(row['Qty_Ratio'])}x)"
    else:
        if row['Adjusted_Profit'] > 0:
            return f"PROFITABLE SPLIT (1/{int(1/row['Qty_Ratio'])})"
        else:
            return "LOSS MAKING SPLIT"

df['Pack_Analysis_Verdict'] = df.apply(analyze_outcome, axis=1)

# Filter for meaningful results
# Filter out low match scores (> 0.4) to avoid "Balloon vs Heater" noise
mask_profitable = df['Adjusted_Profit'] > 0.50
mask_sales = df['sales_numeric'] > 0
mask_match = df['title_match'] > 0.4 

final_df = df[mask_profitable & mask_sales & mask_match].copy()

final_df = final_df.sort_values('Adjusted_Profit', ascending=False)

cols = ['category', 'Pack_Analysis_Verdict', 'Adjusted_Profit', 'Qty_Ratio', 'Sup_Qty', 'Amz_Qty', 'sales_numeric', 'SupplierTitle', 'AmazonTitle', 'EAN', 'ASIN']
final_df[cols].to_csv(output_path, index=False)

print("="*80)
print("DEEP PACK ANALYSIS REPORT (v2)")
print("="*80)

print(f"\nAnalyzed {len(df)} products.")
print(f"Found {len(final_df)} products that remain profitable after pack size adjustment AND logic filter (>40% match).")

print("\n--- EXACT EAN MATCHES (Status Check) ---")
exact = final_df[final_df['category'] == 'EXACT_EAN_MATCH']
if exact.empty:
    print("No profitable Exact Matches found? (Check logic)")
else:
    print(exact[['SupplierTitle', 'Pack_Analysis_Verdict', 'Adjusted_Profit', 'Sup_Qty', 'Amz_Qty']].to_string())

print("\n--- HIDDEN GEMS: Profitable Bundles/Splits ---")
gems = final_df[final_df['Pack_Analysis_Verdict'].str.contains("PROFITABLE")]
if gems.empty:
    print("No profitable bundles found.")
else:
    for _, row in gems.head(20).iterrows():
        print(f"\nVerdict: {row['Pack_Analysis_Verdict']}")
        print(f"Supplier: {str(row['SupplierTitle']).encode('ascii', 'ignore').decode()}")
        print(f"Amazon:   {str(row['AmazonTitle']).encode('ascii', 'ignore').decode()}")
        print(f"Qty: Sup {row['Sup_Qty']} | Amz {row['Amz_Qty']}")
        print(f"Real Profit: £{row['Adjusted_Profit']:.2f}")

print("\n--- FALSE POSITIVES DETECTED (Examples) ---")
losses = df[(df['Qty_Ratio'] > 1) & (df['Adjusted_Profit'] < 0) & (df['title_match'] > 0.4)].head(5)
for _, row in losses.iterrows():
    print(f"\nOriginal Profit: £{row['NetProfit']:.2f} -> Adjusted: £{row['Adjusted_Profit']:.2f}")
    print(f"Mismatch: {str(row['SupplierTitle']).encode('ascii', 'ignore').decode()} ({row['Sup_Qty']}) vs {str(row['AmazonTitle']).encode('ascii', 'ignore').decode()} ({row['Amz_Qty']})")
