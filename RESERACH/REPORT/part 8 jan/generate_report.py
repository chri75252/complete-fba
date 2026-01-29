import pandas as pd
import json
import os

# Input and Output Paths
input_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\products_list.json"
output_dir = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\SEARCH"
output_file = os.path.join(output_dir, "SOURCING_REPORT_JAN_COMPLETE.xlsx")

# Load Products
with open(input_path, "r") as f:
    products = json.load(f)

# Wholesaler Mapping Logic
CATEGORY_MAP = {
    "chemicals": ["Rayburn Trading", "Astro Imports", "Pricecheck", "Harrisons Direct"],
    "toiletries": ["Pharmazon", "Astro Imports", "Pricecheck", "Rayburn Trading", "Harrisons Direct"],
    "housewares": ["Stax Trade Centres", "Harrisons Direct", "DK Wholesale", "Rayburn Trading"],
    "catering": ["Catering24", "Stephensons", "Nisbets", "Booker"],
    "poundlines": ["Pound Wholesale", "MX Wholesale", "Clearance King", "Opatra"]
}

BRAND_MAP = {
    "Pan Aroma": ["Pound Wholesale", "MX Wholesale"],
    "Superior": ["Catering24", "Starlight Packaging", "Booker"],
    "Eveready": ["Astro Imports", "ElekDirect", "Rayburn Trading"],
    "Alberto Balsam": ["Pharmazon", "Astro Imports", "Pricecheck", "Rayburn Trading"],
    "Mason Cash": ["Rayware Group (Direct)", "Jones Wholesale", "Cooksmill"],
    "Chef Aid": ["Pound Wholesale", "Rayburn Trading", "Stax"],
    "Tala": ["George East (Tala Direct)", "Stax", "Harrisons"],
    "Apollo": ["Apollo Housewares (Direct)", "Stax"],
    "Lesser & Pavey": ["Lesser & Pavey (Direct - Leonardo)", "Pound Wholesale"],
    "Blue Canyon": ["Blue Canyon (Direct)", "Rayburn Trading"],
    "Elliott": ["Elliott (Direct)", "Stax", "Rayburn"],
    "Air Wick": ["Rayburn Trading", "Astro Imports", "Pricecheck"],
    "Adidas": ["Pricecheck", "Astro Imports"],
    "Fragrant Cloud": ["Perfume Wholesalers", "Pricecheck"],
    "The Big Cheese": ["STV International (Direct)", "Decco", "Stax"],
    "Fireglow": ["Pound Wholesale", "MX Wholesale"],
    "Alpina": ["Maston's?", "Discount Wholesalers"]
}

KEYWORD_MAP = {
    "foil": CATEGORY_MAP["catering"],
    "tray": CATEGORY_MAP["catering"],
    "candle": CATEGORY_MAP["poundlines"],
    "shampoo": CATEGORY_MAP["toiletries"],
    "deodorant": CATEGORY_MAP["toiletries"],
    "cleaner": CATEGORY_MAP["chemicals"],
    "plaque": ["Lesser & Pavey", "Pound Wholesale"],
    "mirror": CATEGORY_MAP["housewares"],
    "glass": CATEGORY_MAP["housewares"],
    "batteries": ["Astro Imports", "House of Batteries"],
    "bulb": ["Astro Imports", "Lyco"]
}

results = []

for p in products:
    title = p['title']
    ean = p['ean']
    listed_price = p['listed_price']
    
    # Infer Brand (Simple heuristic)
    title_words = title.split()
    brand_guess = title_words[0] if title_words else "Unknown"
    if title_words and len(title_words) > 1 and title_words[0].lower() in ["the", "pan", "chef", "blue", "air", "mason", "alberto"]:
         brand_guess = f"{title_words[0]} {title_words[1]}"
    
    # Clean Brand Guess
    brand_guess_clean = brand_guess.replace(",", "").strip()
    
    # Find Suppliers
    suppliers = []
    
    # 1. Check Exact Brand Map
    for k, v in BRAND_MAP.items():
        if k.lower() in title.lower():
            suppliers.extend(v)
            brand_guess_clean = k
            
    # 2. Check Keywords if no suppliers yet
    if not suppliers:
        for k, v in KEYWORD_MAP.items():
            if k in title.lower():
                 suppliers.extend(v)
    
    # 3. Default
    if not suppliers:
        suppliers = ["General Wholesaler Search Required"]

    # Deduplicate
    suppliers = list(set(suppliers))
    
    # Notes & formatting
    notes = "Login to view exact trade prices."
    found_price = "TBD (Login Req)"
    
    # Specific Overrides for the Research Samples
    if "Superior Large Foil" in title or ean == "5060357990114":
        found_price = "~3.50 - 4.00"
        notes = "Found at Catering24 / Starlight. Bulk discounts likely."
    elif "Eveready" in title and "Tube" in title:
        found_price = "~1.50 - 2.00"
        notes = "Astro Imports / Clearance King. Strong availability."
    elif "Pan Aroma" in title and "Candle" in title:
         found_price = "~0.75 - 0.95"
         notes = "Pound Wholesale is a primary distributor. High margin potential."
    elif "Alberto Balsam" in title:
         found_price = "~0.85 - 1.00"
         notes = "Pharmazon / Pricecheck. Standard toiletries line."
    elif "Mason Cash" in title:
         found_price = "Contact for Trade List"
         notes = "Rayware Group is the parent company. Check Jones Wholesale."

    results.append({
        "Product Name": title,
        "Brand": brand_guess_clean,
        "Supplier EAN": ean,
        "Listed Price": listed_price,
        "Target Wholesale Price": found_price,
        "Recommended Wholesalers": ", ".join(suppliers[:4]), # Top 4
        "Notes": notes
    })

# Create DataFrame
df_out = pd.DataFrame(results)

# Save
try:
    df_out.to_excel(output_file, index=False)
    print(f"Report generated at: {output_file}")
except Exception as e:
    print(f"Error saving report: {e}")
