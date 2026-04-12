
import pandas as pd

CSV_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\deep_analysis_part1.csv"

def extract_candidates():
    df = pd.read_csv(CSV_PATH)
    
    # Filter for HIGH LIKELIHOOD (Non-Exact EAN) that passed initial filters
    # Sales > 0, NetProfit > 0
    candidates = df[
        (df['category'] == 'HIGH_LIKELIHOOD') & 
        (df['is_exact_ean'] == False) &
        (df['sales'] > 0) &
        (df['NetProfit'] > 0)
    ].copy()
    
    candidates = candidates.sort_values(by='sales', ascending=False)
    
    print(f"Found {len(candidates)} High Likelihood candidates for manual review.\n")
    
    for idx, row in candidates.head(40).iterrows():
        print(f"ID: {idx}")
        print(f"S_Ti: {row['SupplierTitle']}")
        print(f"A_Ti: {row['AmazonTitle']}")
        print(f"ASIN: {row['ASIN']}")
        print(f"S_EAN: {row['EAN']}")
        print(f"Price: {row['SupplierPrice_incVAT']} -> {row['SellingPrice_incVAT']}")
        print(f"Profit: {row['NetProfit']}")
        print(f"PackRatio: {row['Qty_Ratio']}")
        print("-" * 50)

if __name__ == "__main__":
    extract_candidates()
