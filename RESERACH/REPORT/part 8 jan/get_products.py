import pandas as pd
import json

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\tes.xlsx"

try:
    df = pd.read_excel(file_path)
    # clean columns
    df.columns = [c.strip() for c in df.columns]
    
    products = []
    for index, row in df.iterrows():
        products.append({
            "title": str(row.get('AmazonTitle', '')).strip(),
            "ean": str(row.get('Supplier EAN', '')).strip(),
            "listed_price": str(row.get('SupplierPrice', '')).strip()
        })
        
    print(json.dumps(products, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}))
