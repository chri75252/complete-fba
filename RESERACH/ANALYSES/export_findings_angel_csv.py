
import csv
import re
import os
from difflib import SequenceMatcher

# Input and Output Paths
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251210_064939.csv"
OUTPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\angel_findings_final.csv"

def normalize(text):
    if not text: return ""
    return str(text).lower().strip()

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def extract_pack_size(title):
    match = re.search(r'pack\s+of\s+(\d+)', title)
    if match: return int(match.group(1))
    
    match = re.search(r'(\d+)\s*pack', title)
    if match: return int(match.group(1))
    
    match = re.search(r'(\d+)\s*pcs', title)
    if match: return int(match.group(1))
    
    return 1

def calculate_title_score(supplier_title, amazon_title):
    st = normalize(supplier_title)
    at = normalize(amazon_title)
    
    if not st or not at:
        return 0
        
    sim = get_similarity(st, at)
    score = sim * 100
    
    sp = extract_pack_size(st)
    ap = extract_pack_size(at)
    
    if sp != ap:
        if sp > 1 and ap > 1:
            score -= 40
        elif (sp > 1 or ap > 1):
             score -= 30
    
    return max(0, min(100, score))

def clean_ean(val):
    if not val: return ""
    s = str(val).strip()
    if not s: return ""
    if 'e' in s.lower():
        try:
            s = str(int(float(s)))
        except:
            pass
    if '.' in s:
        try:
            s = str(int(float(s)))
        except:
            pass
    return s

def main():
    results = []
    
    print(f"Reading from: {INPUT_FILE}")
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            # Normalize field names
            fieldnames = [x.strip() for x in reader.fieldnames]
            reader.fieldnames = fieldnames
            
            for row in reader:
                ean = clean_ean(row.get('EAN'))
                ean_on_page = clean_ean(row.get('EAN_OnPage'))
                
                s_title = row.get('SupplierTitle', '')
                a_title = row.get('AmazonTitle', '')
                
                # Net Profit Calculation
                net_profit_str = row.get('NetProfit', '')
                if not net_profit_str:
                    try:
                        proceeds = float(row.get('NetProceeds', 0))
                        cost = float(row.get('SupplierPrice_exVAT', 0))
                        net_profit = proceeds - cost
                    except:
                        net_profit = -9999.0
                else:
                    try:
                        net_profit = float(net_profit_str)
                    except:
                        net_profit = -9999.0
                        
                # Filter: NetProfit > 1
                if net_profit <= 1:
                    continue
                    
                match_type = "no_match"
                match_score = 0
                
                # Matching Logic
                if ean and ean_on_page and ean == ean_on_page:
                    match_type = "ean_match"
                    match_score = 100
                else:
                    score = calculate_title_score(s_title, a_title)
                    if score >= 60:
                        match_type = "title_match"
                        match_score = score
                
                if match_type == "no_match":
                    continue
                
                # Prepare Result Row
                item = {
                    'EAN': ean,
                    'EAN_OnPage': ean_on_page,
                    'ASIN': row.get('ASIN', ''),
                    'SupplierTitle': s_title,
                    'AmazonTitle': a_title,
                    'SupplierPrice_incVAT': row.get('SupplierPrice_incVAT', ''),
                    'SupplierPrice_exVAT': row.get('SupplierPrice_exVAT', ''),
                    'SellingPrice_incVAT': row.get('SellingPrice_incVAT', ''),
                    'NetProceeds': row.get('NetProceeds', ''),
                    'NetProfit': net_profit,
                    'ROI': row.get('ROI', ''),
                    'bought_in_past_month': row.get('bought_in_past_month', '') or row.get('sales_per_month', ''),
                    'ProfitMargin': row.get('ProfitMargin', ''),
                    'match_type': match_type,
                    'matching_score': int(match_score)
                }
                results.append(item)

    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Sort: EAN matches first, then Title matches by score desc
    def sort_key(x):
        type_rank = 0 if x['match_type'] == 'ean_match' else 1
        return (type_rank, -x['matching_score'])
        
    results.sort(key=sort_key)
    
    # Write to CSV
    output_columns = [
        "EAN", "EAN_OnPage", "ASIN", "SupplierTitle", "AmazonTitle", 
        "SupplierPrice_incVAT", "SupplierPrice_exVAT", "SellingPrice_incVAT", 
        "NetProceeds", "NetProfit", "ROI", "bought_in_past_month", "ProfitMargin", 
        "match_type", "matching_score"
    ]
    
    print(f"Writing {len(results)} findings to: {OUTPUT_FILE}")
    
    try:
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=output_columns)
            writer.writeheader()
            for r in results:
                # Format floats for cleaner CSV
                row_to_write = r.copy()
                try:
                    row_to_write['NetProfit'] = f"{r['NetProfit']:.2f}"
                except:
                    pass
                writer.writerow(row_to_write)
        print("Done.")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()
