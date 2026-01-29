import pandas as pd
import os

# Target CSV
csv_path = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_ALL_linking_map_20260108_005810.csv"
output_xlsx = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\valentines_filtered_report.xlsx"

# List of products to find
products_to_find = [
    "BALLOON SURPRISE IN A BOX",
    "CUTE ANIMALS WITH HEART 15CM",
    "MOTHERS DAY FAUX FUR HEART SHAPED POM POM KEYCHAIN",
    "FOOD STUFF WITH LOVE HEART 25CM ASSORTED",
    "GLITTER HEART TEALIGHT CANDLES 8 PACK",
    "VALENTINES HANGING HEART DECORATION 2 PIECES",
    "VALENTINES HANGING DECORATION HEART 3 PIECES",
    "HANGING HONEYCOMB HEART 9INCH",
    "HEART BATH CONFETTI",
    "HEART GARLAND 3M",
    "HEART KEYRING ASSORTED",
    "HEART PLUSH KEYRING",
    "HEART SHAPED CHOCOLATE MOULDS 4 PACK",
    "HEART SHAPED TEA LIGHTS PK2",
    "HEART STICKY NOTES PK3",
    "I LOVE YOU BALLOON 40CM",
    "I LOVE YOU BEAR WITH HOODY 5 INCH ASSORTED",
    "JUMBO HEART SHAPED CHOCOLATE MOULDS 2 PACK",
    "VALENTINES LED WIRE HEART LIGHTS",
    "LOVE DACHSHUND SAUSAGE DOG 30CM",
    "LOVE HEART SHAPE RESIN CHARM ASSORTED",
    "LOVE PHOTO FRAME 6 X 4 INCH",
    "MOTHERS DAY PLUSH LOVE HEART CLIP-ON 12CM ASSORTED",
    "PLUSH TEDDY WITH ROSE 27CM",
    "PVC LOVE DUCK ASSORTED",
    "VALENTINES RED HEART GARLAND",
    "RED PETALS IN ORGANZA BAG",
    "RING MY BELL NOVELTY HANDBELL IN WINDOW GIFT BOX ASSORTED",
    "SCENTED ROSE CANDLE IN GLASS PK12",
    "SEAL WITH HEART 14INCH",
    "MOTHERS DAY SEQUIN HEART PENS ASSORTED",
    "VALENTINE STICKY NOTES 5 PACK",
    "VALENTINES 100 DATES CHALLENGE POSTER",
    "VALENTINES 4 IN A ROW LOVE GAME",
    "VALENTINES ACRYLIC HEART DECORATIONS 75G",
    "VALENTINES ARTIFICIAL FLOWERS GIFT BOX 22CMX19.5CM",
    "VALENTINES BALLOON DISPLAY PACK",
    "VALENTINES BEAR PLUSH 8\" INCH",
    "VALENTINES BEAR WITH HEART 20CM",
    "VALENTINES BILLY CREAM BEAR WITH I LOVE YOU HEART 60CM",
    "VALENTINES CUSTOMISABLE MINI FOIL BALLOONS PACK 6",
    "VALENTINES CUTE BEAR BAG LARGE PACK 12",
    "VALENTINES CUTE BEAR BAG MEDIUM PACK 12",
    "VALENTINES DAY SILVER HEART NECKLACE ASSORTED",
    "VALENTINES DECORATION HEART 35X25CM",
    "VALENTINES DOUBLE HEART LIGHT 7CM PACK 12",
    "VALENTINES FALLING HEARTS LARGE BAG PK12",
    "VALENTINES FALLING HEARTS MEDIUM BAG PK12",
    "VALENTINES FOAM ROSE BEAR 25CM",
    "VALENTINES GIFT BOX RED SOAP ROSES",
    "VALENTINES HANGING HEART DECORATIONS 5PK",
    "VALENTINES HEADBAND WITH PROP HEARTS",
    "VALENTINES HEART SHAPE CONFETTI 20G",
    "VALENTINES HEART BALLOON BUNDLE WITH STREAMERS PACK 12",
    "VALENTINES HEART PLUSH",
    "VALENTINES HEART PRINTED BALLOONS PACK 10",
    "VALENTINES HEART SHAPE TEALIGHTS PACK 8",
    "VALENTINES I LOVE YOU GREY HEART BEAR 11INCH",
    "VALENTINES I LOVE YOU HEART BEAR 6INCH",
    "VALENTINES I LOVE YOU SITTING BEAR CREAM WITH HEART 17 INCH",
    "VALENTINES LED ROSE CLOCHE 19CM",
    "VALENTINES LOVE DECAL PUZZLE SET OF 2 9CM",
    "VALENTINES MINI LOVE COMMITMENT GLASS BOTTLE",
    "VALENTINES MOVIE NIGHT AT HOME KIT",
    "VALENTINES MOVIE NIGHT KIT",
    "VALENTINES PLASTIC HEART FLUTES PACK 2",
    "VALENTINES RED HEART PLASTIC PLATE",
    "VALENTINES RED PLASTIC HEART SERVING BOWL",
    "MOTHERS DAY RED ROSE PETALS IN ACETATE BOX",
    "VALENTINES RING IN A BOX",
    "VALENTINES ROOM DECORATION KIT",
    "VALENTINES ROSE SCENTED HEART CUBE CANDLE PK12",
    "VALENTINES SCENTED ROSE BEAR AND HEART CANDLES IN GLASS PK12",
    "VALENTINES SINGLE RED ROSE",
    "VALENTINES SOAP ROSE",
    "VALENTINES SOAP ROSE 40CM",
    "VALENTINES SOAP ROSES 3 PIECE",
    "VALENTINES TWO OF A KIND GAME",
    "VALENTINES WINE GLASS WITH GLITTER BASE LOVE",
    "VALENTINES ZIPEMALS PLUSH COIN PURSE 12CM",
]

import re

def normalize_text(text):
    if not isinstance(text, str): return ""
    # Remove special chars, handle multiple spaces, convert to upper
    text = text.upper()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

print(f"Loading CSV: {csv_path}")
df = pd.read_csv(csv_path)
df.columns = [c.strip() for c in df.columns]

# Pre-normalize row titles for speed
df['Normalized_SupplierTitle'] = df['SupplierTitle'].apply(normalize_text)
df['Normalized_AmazonTitle'] = df['AmazonTitle'].apply(normalize_text)

remaining_products = [normalize_text(p) for p in products_to_find]
filtered_df_list = []

for product in remaining_products:
    if not product: continue
    
    # Try exact match on normalized text
    mask = (df['Normalized_SupplierTitle'] == product) | \
           (df['Normalized_AmazonTitle'] == product)
    match = df[mask]
    
    if match.empty:
        # Try substring match
        mask = df['Normalized_SupplierTitle'].str.contains(product, regex=False, na=False) | \
               df['Normalized_AmazonTitle'].str.contains(product, regex=False, na=False)
        match = df[mask]
    
    # Fuzzy match if still empty
    if match.empty:
        words = [w for w in product.split() if len(w) > 2] # ignore small words
        if words:
            def is_fuzzy_match(row_title, target_words):
                if not row_title: return False
                matches = sum(1 for w in target_words if w in row_title)
                # Lower the threshold slightly to 70% or at least 2 words if target has few words
                threshold = 0.7 if len(target_words) > 2 else 1.0
                return (matches / len(target_words)) >= threshold
            
            mask = df['Normalized_SupplierTitle'].apply(lambda x: is_fuzzy_match(x, words)) | \
                   df['Normalized_AmazonTitle'].apply(lambda x: is_fuzzy_match(x, words))
            match = df[mask]

    if not match.empty:
        filtered_df_list.append(match)
    else:
        print(f"FAILED TO FIND: {product}")

if filtered_df_list:
    # Cleanup before saving
    final_df = pd.concat(filtered_df_list).drop_duplicates()
    if 'Normalized_SupplierTitle' in final_df.columns:
        final_df = final_df.drop(columns=['Normalized_SupplierTitle', 'Normalized_AmazonTitle'])
        
    final_df.to_excel(output_xlsx, index=False)
    print(f"\nSuccessfully saved {len(final_df)} rows to {output_xlsx}")
    
    found_count = len(filtered_df_list)
    total_requested = len(products_to_find)
    print(f"Provided data for {found_count} out of {total_requested} requested products.")
else:
    print("No products matched any list.")
