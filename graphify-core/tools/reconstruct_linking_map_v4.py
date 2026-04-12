"""
Linking Map Reconstruction Script v4 - Correct Schema
Uses Financial Reports and Log Files as the source of truth.
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

# Source Files
BACKUP_LINKING_MAP = os.path.join(LINKING_MAP_DIR, "linking_map (30.json")  # Dec 30 backup
LAST_GOOD_REPORT = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "financial_reports", "efghousewares-co-uk", "fba_financial_report_20260105_090250.csv")
LOG_FILE = os.path.join(BASE_DIR, "logs", "debug", "run_custom_poundwholesale_20260104_090928.log")

# Output
OUTPUT_FILE = os.path.join(LINKING_MAP_DIR, "linking_map_RECONSTRUCTED_V4.json")

# Log range for "no match" entries
LOG_START_LINE = 737426
LOG_END_LINE = 761466

# Setup logging
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


def normalize_ean(ean) -> Optional[str]:
    if not ean:
        return None
    return str(ean).strip().lstrip('0') if str(ean).strip() else None


def parse_financial_report(report_path: str) -> List[Dict]:
    """Parse financial report CSV into linking map entry format."""
    entries = []
    if not os.path.exists(report_path):
        logger.warning(f"Report not found: {report_path}")
        return entries

    logger.info(f"Parsing financial report: {report_path}")
    try:
        with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to linking map schema
                ean = row.get("Supplier EAN") or row.get("EAN") or row.get("supplier_ean")
                asin = row.get("Amazon ASIN") or row.get("ASIN") or row.get("amazon_asin")
                
                if not ean or not asin:
                    continue
                
                # Parse prices safely
                try:
                    supplier_price = float(str(row.get("Supplier Price", "") or row.get("supplier_price", "0")).replace("£", "").replace(",", "").strip() or 0)
                except:
                    supplier_price = 0.0
                    
                try:
                    amazon_price = float(str(row.get("Amazon Price", "") or row.get("amazon_price", "0")).replace("£", "").replace(",", "").strip() or 0)
                except:
                    amazon_price = 0.0

                entry = {
                    "supplier_ean": str(ean).strip(),
                    "amazon_asin": str(asin).strip(),
                    "supplier_title": row.get("Supplier Title") or row.get("supplier_title") or "",
                    "amazon_title": row.get("Amazon Title") or row.get("amazon_title") or "",
                    "supplier_price": supplier_price,
                    "amazon_price": amazon_price,
                    "match_method": row.get("Match Method") or row.get("match_method") or "report_reconstruction",
                    "confidence": row.get("Confidence") or row.get("confidence") or "high",
                    "created_at": datetime.now().isoformat(),
                    "supplier_url": row.get("Supplier URL") or row.get("supplier_url") or ""
                }
                entries.append(entry)
                
    except Exception as e:
        logger.error(f"Error parsing report: {e}")

    logger.info(f"Extracted {len(entries)} entries from financial report.")
    return entries


def parse_log_for_no_match_entries(log_path: str, start_line: int, end_line: int) -> List[Dict]:
    """Parse log file section for entries that failed to get price data."""
    entries = []
    if not os.path.exists(log_path):
        logger.warning(f"Log file not found: {log_path}")
        return entries

    logger.info(f"Parsing log file lines {start_line}-{end_line}: {log_path}")
    
    # Regex patterns
    ean_asin_pattern = re.compile(r"EAN=(\d+),\s*ASIN=([A-Z0-9]+|None)")
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
                
                # Look for EAN/ASIN pattern
                ean_match = ean_asin_pattern.search(line)
                if ean_match:
                    # Save previous entry if we have one
                    if current_ean and current_asin and current_asin != "None":
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
                
                # Look for Title pattern
                title_match = title_pattern.search(line)
                if title_match:
                    current_title = title_match.group(1).strip()
                    
    except Exception as e:
        logger.error(f"Error parsing log: {e}")

    logger.info(f"Extracted {len(entries)} entries from log file.")
    return entries


def reconstruct():
    logger.info("=" * 60)
    logger.info("Starting Linking Map Reconstruction v4...")
    logger.info("=" * 60)

    # 1. Load Backup Linking Map as baseline
    logger.info(f"Loading backup map: {BACKUP_LINKING_MAP}")
    baseline_map = load_json(BACKUP_LINKING_MAP)
    logger.info(f"Baseline entries: {len(baseline_map)}")

    # Build index of existing EANs
    existing_eans = set()
    for entry in baseline_map:
        ean = entry.get("supplier_ean") or entry.get("amazon_ean_on_page")
        if ean:
            existing_eans.add(str(ean).strip())

    # 2. Parse Financial Report (PRIMARY SOURCE)
    report_entries = parse_financial_report(LAST_GOOD_REPORT)
    
    # Add new entries from report
    added_from_report = 0
    for entry in report_entries:
        ean = entry.get("supplier_ean")
        if ean and ean not in existing_eans:
            baseline_map.append(entry)
            existing_eans.add(ean)
            added_from_report += 1

    logger.info(f"Added {added_from_report} new entries from financial report.")

    # 3. Parse Log File for No-Match entries (SECONDARY SOURCE)
    log_entries = parse_log_for_no_match_entries(LOG_FILE, LOG_START_LINE, LOG_END_LINE)
    
    # Add new entries from log
    added_from_log = 0
    for entry in log_entries:
        ean = entry.get("supplier_ean")
        if ean and ean not in existing_eans:
            baseline_map.append(entry)
            existing_eans.add(ean)
            added_from_log += 1

    logger.info(f"Added {added_from_log} new entries from log file.")

    # 4. Save Reconstructed Map
    logger.info("=" * 60)
    logger.info(f"TOTAL ENTRIES: {len(baseline_map)}")
    logger.info(f"  - Baseline: {len(baseline_map) - added_from_report - added_from_log}")
    logger.info(f"  - From Report: {added_from_report}")
    logger.info(f"  - From Log: {added_from_log}")
    logger.info("=" * 60)
    
    save_json(OUTPUT_FILE, baseline_map)
    logger.info("Reconstruction Complete.")


if __name__ == "__main__":
    reconstruct()
