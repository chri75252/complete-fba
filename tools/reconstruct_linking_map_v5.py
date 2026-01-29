"""
Linking Map Reconstruction Script v5 - CORRECT SCHEMA
Uses Financial Report with PROPER column mapping.
Output format matches the original linking map schema exactly.
"""

import os
import json
import csv
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
LINKING_MAP_DIR = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "efghousewares.co.uk")

# Source Files - CORRECT FORMAT BACKUP
BACKUP_LINKING_MAP = os.path.join(LINKING_MAP_DIR, "linking_map (30.json")
LAST_GOOD_REPORT = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "financial_reports", "efghousewares-co-uk", "fba_financial_report_20260105_090250.csv")
LOG_FILE = os.path.join(BASE_DIR, "logs", "debug", "run_custom_poundwholesale_20260104_090928.log")

# Output
OUTPUT_FILE = os.path.join(LINKING_MAP_DIR, "linking_map_FINAL_CORRECT.json")

# Log range
LOG_START_LINE = 737426
LOG_END_LINE = 761466

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_json(path: str) -> List[Dict]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return []


def save_json(path: str, data: List[Dict]):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(data)} entries to {path}")
    except Exception as e:
        logger.error(f"Failed to save {path}: {e}")


def parse_price(val) -> float:
    """Safely parse price value."""
    if val is None:
        return 0.0
    try:
        cleaned = str(val).replace("£", "").replace(",", "").strip()
        if not cleaned:
            return 0.0
        return float(cleaned)
    except:
        return 0.0


def parse_financial_report(report_path: str) -> List[Dict]:
    """Parse financial report CSV into CORRECT linking map entry format."""
    entries = []
    if not os.path.exists(report_path):
        logger.warning(f"Report not found: {report_path}")
        return entries

    logger.info(f"Parsing financial report: {report_path}")
    
    try:
        with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            # Log available columns
            if reader.fieldnames:
                logger.info(f"CSV Columns: {reader.fieldnames[:10]}...")
            
            for row in reader:
                # Map CSV columns to CORRECT linking map schema
                # CSV columns: EAN, EAN_OnPage, ASIN, SupplierTitle, AmazonTitle, SupplierURL, SupplierPrice, AmazonPrice, etc.
                
                ean = row.get("EAN") or row.get("Supplier EAN")
                asin = row.get("ASIN") or row.get("Amazon ASIN")
                
                if not ean or not asin:
                    continue
                
                supplier_price = parse_price(row.get("SupplierPrice") or row.get("Supplier Price"))
                amazon_price = parse_price(row.get("AmazonPrice") or row.get("Amazon Price"))
                
                # Build entry in CORRECT format
                entry = {
                    "supplier_ean": str(ean).strip(),
                    "amazon_asin": str(asin).strip(),
                    "supplier_title": (row.get("SupplierTitle") or row.get("Supplier Title") or "").strip(),
                    "amazon_title": (row.get("AmazonTitle") or row.get("Amazon Title") or "").strip(),
                    "supplier_price": supplier_price,
                    "amazon_price": amazon_price,
                    "match_method": "report_reconstruction",
                    "confidence": "high",
                    "created_at": datetime.now().isoformat(),
                    "supplier_url": (row.get("SupplierURL") or row.get("Supplier URL") or "").strip()
                }
                entries.append(entry)
                
    except Exception as e:
        logger.error(f"Error parsing report: {e}")
        import traceback
        traceback.print_exc()

    logger.info(f"Extracted {len(entries)} entries from financial report.")
    return entries


def parse_log_for_entries(log_path: str, start_line: int, end_line: int) -> List[Dict]:
    """Parse log file for entries with EAN/ASIN info."""
    entries = []
    if not os.path.exists(log_path):
        logger.warning(f"Log file not found: {log_path}")
        return entries

    logger.info(f"Parsing log file lines {start_line}-{end_line}")
    
    ean_asin_pattern = re.compile(r"EAN=(\d+),\s*ASIN=([A-Z0-9]+)")
    title_pattern = re.compile(r"Title:\s*(.+)")
    
    current_ean = None
    current_asin = None
    current_title = None
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f, 1):
                if i < start_line:
                    continue
                if i > end_line:
                    break
                
                ean_match = ean_asin_pattern.search(line)
                if ean_match:
                    if current_ean and current_asin:
                        entry = {
                            "supplier_ean": current_ean,
                            "amazon_asin": current_asin,
                            "supplier_title": current_title or "",
                            "amazon_title": "",
                            "supplier_price": 0.0,
                            "amazon_price": 0.0,
                            "match_method": "log_reconstruction",
                            "confidence": "low",
                            "created_at": datetime.now().isoformat(),
                            "supplier_url": ""
                        }
                        entries.append(entry)
                    
                    current_ean = ean_match.group(1)
                    current_asin = ean_match.group(2)
                    current_title = None
                
                title_match = title_pattern.search(line)
                if title_match:
                    current_title = title_match.group(1).strip()
                    
    except Exception as e:
        logger.error(f"Error parsing log: {e}")

    logger.info(f"Extracted {len(entries)} entries from log.")
    return entries


def reconstruct():
    logger.info("=" * 60)
    logger.info("Linking Map Reconstruction v5 - CORRECT SCHEMA")
    logger.info("=" * 60)

    # 1. Load CORRECT FORMAT Backup
    logger.info(f"Loading backup: {BACKUP_LINKING_MAP}")
    baseline_map = load_json(BACKUP_LINKING_MAP)
    logger.info(f"Baseline entries: {len(baseline_map)}")

    # Verify format
    if baseline_map:
        sample = baseline_map[0]
        logger.info(f"Sample entry keys: {list(sample.keys())}")

    # Build index
    existing_eans = set()
    for entry in baseline_map:
        ean = entry.get("supplier_ean")
        if ean:
            existing_eans.add(str(ean).strip())

    # 2. Parse Financial Report
    report_entries = parse_financial_report(LAST_GOOD_REPORT)
    
    added_from_report = 0
    for entry in report_entries:
        ean = entry.get("supplier_ean")
        if ean and ean not in existing_eans:
            baseline_map.append(entry)
            existing_eans.add(ean)
            added_from_report += 1

    logger.info(f"Added {added_from_report} new entries from report.")

    # 3. Parse Log File
    log_entries = parse_log_for_entries(LOG_FILE, LOG_START_LINE, LOG_END_LINE)
    
    added_from_log = 0
    for entry in log_entries:
        ean = entry.get("supplier_ean")
        if ean and ean not in existing_eans:
            baseline_map.append(entry)
            existing_eans.add(ean)
            added_from_log += 1

    logger.info(f"Added {added_from_log} new entries from log.")

    # 4. Summary
    logger.info("=" * 60)
    logger.info(f"TOTAL ENTRIES: {len(baseline_map)}")
    logger.info(f"  - From Backup: {len(baseline_map) - added_from_report - added_from_log}")
    logger.info(f"  - From Report: {added_from_report}")
    logger.info(f"  - From Log: {added_from_log}")
    logger.info("=" * 60)
    
    save_json(OUTPUT_FILE, baseline_map)
    
    # Verify output format
    if baseline_map:
        logger.info(f"Output sample entry: {json.dumps(baseline_map[-1], indent=2)}")
    
    logger.info("Done.")


if __name__ == "__main__":
    reconstruct()
