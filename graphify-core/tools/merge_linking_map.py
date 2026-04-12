"""
Simple Linking Map Gap Filler - FIXED COLUMN NAMES
"""

import os
import json
import csv
from datetime import datetime

BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

BACKUP = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "efghousewares.co.uk", "linking_map_DEC29.json")
REPORT = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "financial_reports", "efghousewares-co-uk", "fba_financial_report_20260105_090250.csv")
OUTPUT = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "efghousewares.co.uk", "linking_map_MERGED_FIXED.json")

def parse_float(val):
    try:
        return float(str(val).replace("£","").replace(",","").strip() or 0)
    except:
        return 0.0

# Load backup
print(f"Loading backup: {BACKUP}")
with open(BACKUP, 'r', encoding='utf-8') as f:
    backup_data = json.load(f)
print(f"Backup entries: {len(backup_data)}")

# Index existing EANs
existing_eans = set()
for e in backup_data:
    ean = e.get("supplier_ean")
    if ean:
        existing_eans.add(str(ean).strip())
print(f"Existing unique EANs: {len(existing_eans)}")

# Parse report
print(f"Parsing report: {REPORT}")
added = 0
with open(REPORT, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ean = row.get("EAN", "").strip()
        asin = row.get("ASIN", "").strip()
        
        if not ean or not asin:
            continue
        
        if ean in existing_eans:
            continue
        
        # CORRECT COLUMN NAMES from report
        entry = {
            "supplier_ean": ean,
            "amazon_asin": asin,
            "supplier_title": row.get("SupplierTitle", ""),
            "amazon_title": row.get("AmazonTitle", ""),
            "supplier_price": parse_float(row.get("SupplierPrice_incVAT")),
            "amazon_price": parse_float(row.get("SellingPrice_incVAT")),
            "match_method": "report_reconstruction",
            "confidence": "high",
            "created_at": datetime.now().isoformat(),
            "supplier_url": row.get("SupplierURL", "")
        }
        
        backup_data.append(entry)
        existing_eans.add(ean)
        added += 1

print(f"Added {added} new entries from report")
print(f"Total entries: {len(backup_data)}")

# Save
print(f"Saving to: {OUTPUT}")
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(backup_data, f, indent=2, ensure_ascii=False)

print("Done.")
