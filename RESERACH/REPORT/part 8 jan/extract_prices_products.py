import pandas as pd
import os

# Target CSV
csv_path = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_ALL_linking_map_20260108_005810.csv"
output_xlsx = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\prices_filtered_report.xlsx"

# List of products to find
products_to_find = [
    "PRICES PILLAR CANDLE 6 INCH WHITE",
    "PRICES PILLAR CANDLE 6 INCH RED",
    "PRICES PILLAR CANDLE 6 INCH IVORY",
    "PRICES 50 CATERING DINNER CANDLES GREEN",
    "PRICES CANDLE JAR* ARGAN",
    "PRICES ALADINO TEALIGHTS 10 VANILLA PK10",
    "PRICES ALADINO TEALIGHTS 10 ROSE PK10",
    "PRICES ALADINO TEALIGHTS 10 MIXED BERRIE PK10",
    "PRICES ALADINO TEALIGHTS 10 LAVENDER PK10",
    "PRICES ALADINO TEALIGHTS 10 JASMINE PK10",
    "PRICES ALADINO TEALIGHTS 10 COTTONFLOWER PK10",
    "PRICES TEALIGHTS 4 HRS 50PCS",
    "PRICES TEALIGHTS PK30 (SP)",
    "PRICES 10 TEALIGHTS PK10",
    "PRICES DINNER CANDLE PK10 RED",
    "PRICES DINNER CANDLE PK10 WHITE",
    "PRICES DINNER CANDLE PK10 IVORY",
    "PRICE'S CHEFS TEALIGHTS 10 PACK - PK10",
    "PRICES 50 CATERING DINNER CANDLES WHITE (SP)",
    "PRICES 50 CATERING DINNER CANDLES IVORY",
    "PRICES BLACK CHERRY JAR LARGE",
    "PRICES ALADINO JASMINE JAR",
    "PRICES ALADINO MACARONS JAR",
    "PRICES ALADINO JAR COTTON FLOWERS",
    "PRICES ALADINO CHERRY JAR",
    "PRICES ALADINO CINNAMON JAR",
    "PRICES PILLAR CANDLE IVORY 10X8CM",
    "PRICES PILLAR CANDLE IVORY 15X8CM (SP)",
    "PRICES PILLAR CANDLE IVORY 20X8CM (SP)",
    "PRICES PILLAR CANDLE IVORY 25X8CM (SP)",
    "PRICES 50 CATERING DINNER CANDLES RED (SP)",
    "PRICES CITRONELLA TERRACOTTA POT REFILL",
    "PRICES PILLAR CANDLE 6 INCH GREEN",
    "PRICES PILLAR CANDLE 6 INCH METALLIC GOLD",
    "PRICES PILLAR CANDLE 6 INCH METALLIC SILVER",
    "PRICES TEALIGHTS ALADINO 25 VANILLA MACARONS",
    "PRICES TEALIGHTS ALADINO 25 FROSTED CHERRY",
    "PRICES TEALIGHTS ALADINO 25 APPLE SPICE",
    "PRICES 5 HOUSEHOLD CANDLE",
    "PRICES HOUSEHOLD 10 CANDLE PK6",
    "PRICES TEALIGHTS ALADINO 4 MAXI COTTON",
    "PRICES TEALIGHTS ALADINO 4 MAXI BERRIES",
    "PRICES TEALIGHTS ALADINO 4 MAXI JASMINE",
    "PRICES TEALIGHTS ALADINO 4 MAXI VANILLA",
    "PRICES TEALIGHTS ALADINO 4 MAXI LAVENDER",
    "PRICES TEALIGHT 12 MAXI",
    "PRICES CITRONELLA TEALIGHT 25PC",
    "PRICES CITRONELLA 10 TEALIGHTS PK10 (2020)",
    "PRICES CITRONELLA TIN UNLIDDED 9.7CM PK6",
    "PRICES CITRONELLA MAXI 4 TEALIGHT",
    "PRICES TEALIGHT SENTINEL 50 NIGHTLIGHTS",
    "PRICES TEALIGHT SENTINEL 25 NIGHTLIGHTS BAG",
    "PRICES TEALIGHTS ALADINO 25 CITRUS",
    "PRICES TEALIGHTS ALADINO 4 MAXI ROSE",
    "PRICES ALADINO CITRUS JAR",
    "PRICES ALADINO MIXED BERRIES JAR",
    "PRICES ALADINO VANILLA JAR",
    "PRICES ALADINO LAVENDER JAR",
    "PRICES ALADINO ROSE JAR",
    "PRICES TEALIGHTS ALADINO 25 COTTON FLOWER",
    "PRICES TEALIGHTS ALADINO 25 JASMINE",
    "PRICES TEALIGHTS ALADINO 25 ROSE",
    "PRICES TEALIGHTS ALADINO 25 MIXED BERRIES",
    "PRICES TEALIGHTS ALADINO 25 LAVENDER",
    "PRICES TEALIGHTS ALADINO 25 VANILLA",
    "PRICES TEALIGHTS ALADINO 25 CINNAMON",
]

def clean_title(title):
    if not isinstance(title, str):
        return ""
    return title.strip().upper()

print(f"Loading CSV: {csv_path}")
df = pd.read_csv(csv_path)

# Normalize column names just in case
df.columns = [c.strip() for c in df.columns]

# We will check SupplierTitle primarily, as they look like supplier names.
# We'll use fuzzy matching or just check if the target string is IN the title.

matched_rows = []
remaining_products = [p.upper() for p in products_to_find]

# Strategy: For each product in the list, see if it matches any row.
# We'll check if the product name is a substring of SupplierTitle or vice versa, 
# or if it's an exact match after normalization.

# Track found products to avoid duplicates
found_product_indices = set()
filtered_df_list = []

for product in remaining_products:
    # Try exact match first
    mask = (df['SupplierTitle'].str.upper().str.strip() == product) | \
           (df['AmazonTitle'].str.upper().str.strip() == product)
    match = df[mask]
    
    if match.empty:
        # Try substring match
        mask = df['SupplierTitle'].str.upper().str.contains(product, regex=False, na=False) | \
               df['AmazonTitle'].str.upper().str.contains(product, regex=False, na=False)
        match = df[mask]
    
    # NEW: Fuzzy match if still empty
    if match.empty:
        # Split product name into words and see if we have a row that contains MANY of those words
        words = [w for w in product.split() if len(w) > 2] # ignore small words
        if words:
            # Create a mask that checks if MOST words are present
            # We'll use a threshold (e.g. 80% of words)
            def is_fuzzy_match(row_title, target_words):
                if not isinstance(row_title, str): return False
                row_title = row_title.upper()
                matches = sum(1 for w in target_words if w in row_title)
                return matches / len(target_words) >= 0.8
            
            mask = df['SupplierTitle'].apply(lambda x: is_fuzzy_match(x, words)) | \
                   df['AmazonTitle'].apply(lambda x: is_fuzzy_match(x, words))
            match = df[mask]

    if not match.empty:
        # Only add rows we haven't already included (for this specific product request)
        filtered_df_list.append(match)
    else:
        print(f"No match found for: {product}")

if filtered_df_list:
    final_df = pd.concat(filtered_df_list).drop_duplicates()
    final_df.to_excel(output_xlsx, index=False)
    print(f"\nSuccessfully saved {len(final_df)} rows to {output_xlsx}")
    
    found_count = len(final_df)
    total_requested = len(products_to_find)
    print(f"Matched {found_count} out of {total_requested} requested products.")
    
    # Also print a summary table
    print("\nSummary Table (First 10 matches):")
    cols = [c for c in ['SupplierTitle', 'ASIN', 'NetProfit', 'ROI'] if c in final_df.columns]
    print(final_df[cols].head(10).to_string())
else:
    print("No products matched any list.")
