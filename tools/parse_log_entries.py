"""
Parse ALL missing EANs from log - simplified approach
"""

import os
import json
import re
from datetime import datetime

BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

MERGED_MAP = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "efghousewares.co.uk", "linking_map_MERGED_FIXED.json")
LOG_FILE = os.path.join(BASE_DIR, "logs", "debug", "run_custom_poundwholesale_20260104_090928.log")
OUTPUT = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "efghousewares.co.uk", "linking_map_COMPLETE_FINAL.json")

START_LINE = 737426
END_LINE = 761466

# Load merged map
print(f"Loading merged map...")
with open(MERGED_MAP, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"Loaded {len(data)} entries")

# Index existing EANs
existing_eans = set()
for e in data:
    ean = e.get("supplier_ean")
    if ean:
        existing_eans.add(str(ean).strip())
print(f"Existing unique EANs: {len(existing_eans)}")

# Patterns - capture EAN, ASIN, Price, Title in one pass
# Format: PRICE FOUND: EAN=5000101510632, ASIN=None, Price=£1.1 (from current_price)
# or: NO PRICE DATA: EAN=6923456819870, ASIN=None
price_found_pattern = re.compile(r"PRICE FOUND: EAN=(\d+), ASIN=([A-Z0-9]+|None), Price=£([\d.]+)")
no_price_pattern = re.compile(r"NO PRICE DATA: EAN=(\d+), ASIN=([A-Z0-9]+|None)")
title_pattern = re.compile(r"Title: (.+)")

print(f"Parsing log lines {START_LINE} to {END_LINE}...")

# First pass: collect all EANs with their data
log_entries = {}  # EAN -> entry data

with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
    current_ean = None
    
    for i, line in enumerate(f, 1):
        if i < START_LINE:
            continue
        if i > END_LINE:
            break
        
        # PRICE FOUND
        match = price_found_pattern.search(line)
        if match:
            ean = match.group(1)
            asin = match.group(2) if match.group(2) != "None" else None
            price = float(match.group(3))
            
            if ean not in existing_eans and ean not in log_entries:
                log_entries[ean] = {
                    "supplier_ean": ean,
                    "amazon_asin": asin,
                    "supplier_title": "",
                    "amazon_title": None,
                    "supplier_price": 0.0,
                    "amazon_price": price,
                    "match_method": "log_price_found",
                    "confidence": "medium",
                    "created_at": datetime.now().isoformat(),
                    "supplier_url": ""
                }
                current_ean = ean
            continue
        
        # NO PRICE DATA
        match = no_price_pattern.search(line)
        if match:
            ean = match.group(1)
            asin = match.group(2) if match.group(2) != "None" else None
            
            if ean not in existing_eans and ean not in log_entries:
                log_entries[ean] = {
                    "supplier_ean": ean,
                    "amazon_asin": asin,
                    "supplier_title": "",
                    "amazon_title": None,
                    "supplier_price": 0.0,
                    "amazon_price": None,
                    "match_method": "log_no_price",
                    "confidence": "low",
                    "created_at": datetime.now().isoformat(),
                    "supplier_url": "",
                    "no_match_reason": "NO PRICE DATA"
                }
                current_ean = ean
            continue
        
        # Title - update last entry
        match = title_pattern.search(line)
        if match and current_ean and current_ean in log_entries:
            log_entries[current_ean]["supplier_title"] = match.group(1).strip()

print(f"Found {len(log_entries)} new entries from log")

# Add to data
for entry in log_entries.values():
    data.append(entry)

print(f"Total entries: {len(data)}")

# Save
print(f"Saving to: {OUTPUT}")
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Done.")
