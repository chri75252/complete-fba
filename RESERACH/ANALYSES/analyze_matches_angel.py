
import csv
import sys
import re
from difflib import SequenceMatcher

FILE_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251210_064939.csv"

def normalize(text):
    if not text: return ""
    return str(text).lower().strip()

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def extract_pack_size(title):
    # Look for "pack of X", "X pack", "X pcs", "X set"
    # Prioritize "pack of X"
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
        
    # Base similarity
    sim = get_similarity(st, at)
    score = sim * 100
    
    # Pack size check
    sp = extract_pack_size(st)
    ap = extract_pack_size(at)
    
    # If one has a pack size > 1 and the other is 1 (or different), penalize
    # But be careful: "pack of 1" vs "1 pack" is same.
    if sp != ap:
        # If both are > 1 and different, heavy penalty
        if sp > 1 and ap > 1:
            score -= 40
        # If one is > 1 and other is 1, check if the title implies quantity otherwise
        elif (sp > 1 or ap > 1):
             score -= 30

    # Brand check (heuristic: first word)
    # This is risky if brand is "The" or "A". 
    # Let's skip strict brand check for now and rely on similarity + pack size.
    
    return max(0, min(100, score))

def clean_ean(val):
    if not val: return ""
    s = str(val).strip()
    if not s: return ""
    # Handle scientific notation
    if 'e' in s.lower():
        try:
            s = str(int(float(s)))
        except:
            pass
    # Remove decimals
    if '.' in s:
        try:
            s = str(int(float(s)))
        except:
            pass
    return s

def main():
    results_ean = []
    results_title = []
    
    total_rows = 0
    
    try:
        with open(FILE_PATH, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            # Normalize field names (strip whitespace)
            fieldnames = [x.strip() for x in reader.fieldnames]
            reader.fieldnames = fieldnames
            
            for row in reader:
                total_rows += 1
                
                # Extract Data
                ean = clean_ean(row.get('EAN'))
                ean_on_page = clean_ean(row.get('EAN_OnPage'))
                
                s_title = row.get('SupplierTitle', '')
                a_title = row.get('AmazonTitle', '')
                
                # Net Profit
                net_profit_str = row.get('NetProfit', '')
                if not net_profit_str:
                    # Try to calculate
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
                    
                # Match Logic
                match_type = "no_match"
                match_score = 0
                
                # 1. Exact EAN
                if ean and ean_on_page and ean == ean_on_page:
                    match_type = "ean_match"
                    match_score = 100
                else:
                    # 2. Title Match
                    score = calculate_title_score(s_title, a_title)
                    if score >= 60:
                        match_type = "title_match"
                        match_score = score
                
                # Store Result
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
                    'NetProfit': net_profit, # Store as float for sorting
                    'ROI': row.get('ROI', ''),
                    'bought_in_past_month': row.get('bought_in_past_month', '') or row.get('sales_per_month', ''),
                    'ProfitMargin': row.get('ProfitMargin', ''),
                    'match_type': match_type,
                    'matching_score': match_score
                }
                
                if match_type == 'ean_match':
                    results_ean.append(item)
                elif match_type == 'title_match':
                    results_title.append(item)

    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Sort Title Matches by Score Descending
    results_title.sort(key=lambda x: x['matching_score'], reverse=True)
    
    # Generate Markdown Output
    
    columns = [
        "EAN", "EAN_OnPage", "ASIN", "SupplierTitle", "AmazonTitle", 
        "SupplierPrice_incVAT", "SupplierPrice_exVAT", "SellingPrice_incVAT", 
        "NetProceeds", "NetProfit", "ROI", "bought_in_past_month", "ProfitMargin", 
        "match_type", "matching_score"
    ]
    
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    
    def print_row(item):
        row_vals = []
        for col in columns:
            val = item.get(col, '')
            if col in ['NetProfit', 'NetProceeds', 'SupplierPrice_incVAT', 'SupplierPrice_exVAT', 'SellingPrice_incVAT']:
                try:
                    val = f"{float(val):.2f}"
                except:
                    pass
            elif col == 'matching_score':
                try:
                    val = f"{int(val)}"
                except:
                    pass
            
            # Escape pipes in text
            val = str(val).replace("|", "\|").replace("\n", " ")
            row_vals.append(val)
        print("| " + " | ".join(row_vals) + " |")

    # Section 1: EAN Matches
    print("### 1. Exact matches by EAN (NetProfit > 1)")
    if not results_ean:
        print("No exact EAN matches found with NetProfit > 1.")
    else:
        print(header)
        print(separator)
        for i in results_ean:
            print_row(i)

    print("\n")
    
    # Section 2: Title Matches
    print("### 2. Title-based matches (NetProfit > 1)")
    if not results_title:
        print("No title-based matches found with NetProfit > 1.")
    else:
        print(header)
        print(separator)
        for i in results_title:
            print_row(i)

    print("\n")
    print("### Summary")
    print(f"- Processed {total_rows} rows.")
    print(f"- Found {len(results_ean)} exact EAN matches.")
    avg_score = sum(r['matching_score'] for r in results_title) / len(results_title) if results_title else 0
    print(f"- Found {len(results_title)} title-based matches (Avg Score: {avg_score:.1f}).")

if __name__ == "__main__":
    main()
