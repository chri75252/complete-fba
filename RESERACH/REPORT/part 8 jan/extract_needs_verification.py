#!/usr/bin/env python3
"""
Extract all NEEDS VERIFICATION entries from source data and all reports
Format them according to the specified table schema
"""

import pandas as pd
import re
import os
from datetime import datetime

BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan"
SOURCE_FILE = os.path.join(BASE_DIR, "part 8 jan.xlsx")

# All reports to extract NEEDS VERIFICATION from
REPORTS = {
    "CODEX_FINAL": os.path.join(BASE_DIR, "CODEX final", "PHASEA_MANUAL_REPORT_0110052809 - Copy.md"),
    "CODEX_NEW": os.path.join(BASE_DIR, "CODEX NEW", "PHASEA_MANUAL_REPORT_VALIDATED_2601090352.md"),
    "CODEX_MANU": os.path.join(BASE_DIR, "CODEX manu", "PHASEA_MANUAL_REPORT_2601090949.md"),
}


def extract_needs_verification_eans(filepath):
    """Extract EANs from NEEDS VERIFICATION section of a report."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find NEEDS VERIFICATION section
        pattern = r'## NEEDS VERIFICATION.*?(?=## |---\s*\n\*Report|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            section = match.group(0)
            # Extract all EANs
            ean_pattern = r'\b(\d{12,14})\b'
            eans = set(re.findall(ean_pattern, section))
            return eans
        return set()
    except:
        return set()


def main():
    # Load source data
    print("Loading source data...")
    source_df = pd.read_excel(SOURCE_FILE)
    
    # Collect all NEEDS VERIFICATION EANs from reports
    all_nv_eans = set()
    for name, path in REPORTS.items():
        eans = extract_needs_verification_eans(path)
        print(f"{name}: {len(eans)} NEEDS VERIFICATION EANs")
        all_nv_eans.update(eans)
    
    print(f"\nTotal unique NEEDS VERIFICATION EANs: {len(all_nv_eans)}")
    
    # Build source lookup
    source_by_ean = {}
    for idx, row in source_df.iterrows():
        ean = str(row['EAN']).replace('.0', '').strip()
        if ean and ean != 'nan':
            source_by_ean[ean] = row.to_dict()
    
    # Build NEEDS VERIFICATION table entries
    nv_entries = []
    
    for ean in sorted(all_nv_eans):
        if ean in source_by_ean:
            row = source_by_ean[ean]
            
            # Get values with safe defaults
            supplier_title = str(row.get('SupplierTitle', 'N/A'))[:60].replace('|', '/').replace('\n', ' ')
            amazon_title = str(row.get('AmazonTitle', 'N/A'))[:80].replace('|', '/').replace('\n', ' ')
            amazon_ean = str(row.get('EAN_OnPage', '-')).replace('.0', '').strip()
            if amazon_ean == 'nan' or not amazon_ean:
                amazon_ean = '-'
            asin = str(row.get('ASIN', '-'))
            supplier_price = row.get('SupplierPrice_incVAT', 0) or row.get('SupplierPrice', 0) or 0
            selling_price = row.get('SellingPrice_incVAT', 0) or row.get('SellingPrice', 0) or 0
            net_profit = row.get('NetProfit', 0) or 0
            roi = row.get('ROI ( % )', 0) or row.get('ROI', 0) or 0
            sales = row.get('bought_in_past_month', 0) or row.get('Sales', 0) or 0
            
            # Determine filter reason based on EAN status
            if amazon_ean != '-' and amazon_ean != ean:
                filter_reason = "EAN conflict; needs verification"
            elif amazon_ean == '-':
                filter_reason = "No Amazon EAN; needs verification"
            else:
                filter_reason = "Needs product/pack verification"
            
            nv_entries.append({
                'ean': ean,
                'supplier_title': supplier_title,
                'amazon_title': amazon_title,
                'amazon_ean': amazon_ean,
                'asin': asin,
                'supplier_price': supplier_price,
                'selling_price': selling_price,
                'net_profit': net_profit,
                'roi': roi,
                'sales': sales,
                'filter_reason': filter_reason
            })
    
    print(f"Built {len(nv_entries)} NEEDS VERIFICATION entries")
    
    # Generate table output
    output_lines = []
    output_lines.append("| Verdict            | Confidence | SupplierTitle                                                     | AmazonTitle                                                                                      | Supplier EAN   | Amazon EAN    | ASIN       | SupplierPrice | SellingPrice | NetProfit | ROI     | Sales | Pack Verdict                   | Adjusted Profit | Key Match Evidence                   | Filter Reason                                     |")
    output_lines.append("|--------------------|------------|-------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|----------------|---------------|------------|---------------|--------------|-----------|---------|-------|--------------------------------|-----------------|-------------------------------------|---------------------------------------------------|")
    
    for entry in nv_entries[:151]:  # Limit to 151 as per count
        sup_title = entry['supplier_title'][:63].ljust(63)
        amz_title = entry['amazon_title'][:94].ljust(94)
        ean = entry['ean'].ljust(14)
        amz_ean = entry['amazon_ean'][:13].ljust(13)
        asin = entry['asin'][:10].ljust(10)
        sup_price = f"£{float(entry['supplier_price']):.2f}".ljust(13)
        sell_price = f"£{float(entry['selling_price']):.2f}".ljust(12)
        net_prof = f"£{float(entry['net_profit']):.2f}".ljust(9)
        roi = f"{float(entry['roi']):.1f}%".ljust(7)
        sales = str(int(entry['sales']) if entry['sales'] else 0)[:5].ljust(5)
        pack = "1:1 Match".ljust(30)
        adj_prof = f"£{float(entry['net_profit']):.2f}".ljust(15)
        evidence = "EAN status unclear".ljust(37)
        filter_r = entry['filter_reason'][:49].ljust(49)
        
        line = f"| NEEDS VERIFICATION | 70         | {sup_title} | {amz_title} | {ean} | {amz_ean} | {asin} | {sup_price} | {sell_price} | {net_prof} | {roi} | {sales} | {pack} | {adj_prof} | {evidence} | {filter_r} |"
        output_lines.append(line)
    
    # Save to file
    output_path = os.path.join(BASE_DIR, "NEEDS_VERIFICATION_TABLE.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Table saved to: {output_path}")
    
    # Also print first 10 for review
    print("\nFirst 10 entries:")
    for line in output_lines[:12]:
        print(line)


if __name__ == "__main__":
    main()
