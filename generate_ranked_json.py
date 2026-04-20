import csv
import json
import math
from datetime import datetime
import os

EXCL_FILE = r'OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk__sandbox__4e269fb4\fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_RECONCILED_20260410_001500.csv'
MASTER_FILE = r'OUTPUTS\PRODUCTS_LISTS\efghousewares_VALIDATED_master_20260413_023831.csv'
OUT_FILE = r'OUTPUTS\PRODUCTS_LISTS\efghousewares_validated_ranked_products_20260413.json'

def pf(v):
    try:
        f = float(v)
        return f if not math.isnan(f) else 0.0
    except:
        return 0.0

def process():
    # 1. Load exclusion list
    excluded_asins = set()
    excluded_titles = set()
    with open(EXCL_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get('ASIN'):
                excluded_asins.add(r['ASIN'].strip())
            if r.get('SupplierTitle'):
                excluded_titles.add(r['SupplierTitle'].strip())
                
    print(f"Loaded {len(excluded_asins)} exclusion ASINs and {len(excluded_titles)} exclusion Titles.")

    # 2. Load validated master list
    with open(MASTER_FILE, 'r', encoding='utf-8-sig') as f:
        master_rows = list(csv.DictReader(f))
        
    print(f"Loaded {len(master_rows)} rows from master list.")
    
    # 3. Filter out excluded products
    filtered_rows = []
    excluded_count = 0
    for r in master_rows:
        asin = r.get('ASIN', '').strip()
        title = r.get('Supplier_Title', '').strip()
        if asin in excluded_asins or title in excluded_titles:
            excluded_count += 1
            continue
        filtered_rows.append(r)
        
    print(f"Excluded {excluded_count} rows. {len(filtered_rows)} remain.")

    # 4. Rank from most likely to sell/profit down
    def rank_score(row):
        # primary: Bucket A = 0, Bucket B = 1, Bucket C = 2
        # secondary: Priority HIGH = 0, MEDIUM = 1, LOW = 2
        # tertiary: Confidence HIGH = 0, MEDIUM = 1, LOW = 2
        # quaternary: -(profit * min(sales, 1000)) if we have sales, else -profit
        
        bk = row.get('Bucket', 'Z')
        bk_score = 0 if bk == 'A' else 1 if bk == 'B' else 2
        
        pr = row.get('Priority', 'LOW')
        pr_score = 0 if pr == 'HIGH' else 1 if pr == 'MEDIUM' else 2
        
        cf = row.get('Confidence', 'LOW')
        cf_score = 0 if cf == 'HIGH' else 1 if cf == 'MEDIUM' else 2
        
        profit = pf(row.get('Net_Profit'))
        sales = row.get('Sales', '0')
        sales_val = pf(sales) if sales != 'Unknown' else 0.0
        
        # We want higher profit/sales to be smaller negative numbers to sort ascending
        if bk == 'A':
            score_val = -(profit * min(sales_val, 1000))
        elif bk == 'B':
            score_val = -profit
        else: # Bucket C
            score_val = -sales_val
            
        return (bk_score, pr_score, cf_score, score_val)

    filtered_rows.sort(key=rank_score)

    # 5. Format into required JSON structure
    products = []
    
    now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for r in filtered_rows:
        prod = {
            "title": r.get('Supplier_Title', ''),
            "amazon_title": r.get('Amazon_Title', ''),
            "price": pf(r.get('Supplier_Price')),
            "amazon_price": pf(r.get('Amazon_Price')),
            "url": r.get('Supplier_URL', ''),
            "normalized_url": r.get('Supplier_URL', ''),
            "amazon_url": r.get('Amazon_URL', ''),
            "ean": r.get('EAN', ''),
            "asin": r.get('ASIN', ''),
            "availability": "Unknown",
            "source_url": r.get('Supplier_URL', ''),
            "scraped_at": now_str,
            "net_profit": pf(r.get('Net_Profit')),
            "sales": r.get('Sales', '0'),
            "roi": pf(r.get('ROI')),
            "bucket": r.get('Bucket', ''),
            "priority": r.get('Priority', ''),
            "confidence": r.get('Confidence', ''),
            "unit_qty_flag": r.get('Unit_Qty_Flag', ''),
            "tier": r.get('Tier', '')
        }
        products.append(prod)

    out_json = {
        "supplier_domain": "efghousewares.co.uk",
        "generated_at": now_str,
        "source_cached_file": MASTER_FILE,
        "selection": {
            "mode": "ranked_validated",
            "sample_size": len(products),
            "category_count": 0,
            "selected_categories": []
        },
        "products": products
    }

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(out_json, f, indent=2, ensure_ascii=False)
        
    print(f"JSON generated successfully at: {OUT_FILE}")

if __name__ == '__main__':
    process()
