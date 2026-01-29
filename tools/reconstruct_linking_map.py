
import os
import json
import csv
import logging
from typing import Dict, List, Set

# Configuration
BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
LINKING_MAP_DIR = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "efghousewares.co.uk")
AMAZON_CACHE_DIR = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "amazon_cache")
FINANCIAL_REPORT_PATH = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "financial_reports", "efghousewares-co-uk", "fba_financial_report_20260105_231633.csv")

LINKING_MAP_FILE = os.path.join(LINKING_MAP_DIR, "linking_map.json")
OUTPUT_FILE = os.path.join(LINKING_MAP_DIR, "linking_map_COMPLETE.json")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return []

def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved {len(data)} entries to {path}")
    except Exception as e:
        logger.error(f"Failed to save {path}: {e}")

def normalize_ean(ean):
    if not ean:
        return None
    return str(ean).strip()

def reconstruct():
    logger.info("Starting Linking Map Reconstruction...")

    # 1. Load Baseline Linking Map
    logger.info(f"Loading baseline map from {LINKING_MAP_FILE}")
    current_map = load_json(LINKING_MAP_FILE)
    if isinstance(current_map, dict):
        # Convert dict to list format if necessary (though the restored file should be a list based on "linking_map (30.json")
        logger.info("Detected dictionary format, converting to list...")
        new_map = []
        for k, v in current_map.items():
             new_map.append({
                "supplier_product_identifier": f"EAN_{k}",
                "chosen_amazon_asin": v,
                 "match_method": "legacy_dict_conversion"
            })
        current_map = new_map
    
    logger.info(f"Baseline entries: {len(current_map)}")

    # Index existing entries to prevent duplicates
    # Key: EAN (stripped of 'EAN_' prefix if present) -> ASIN
    existing_index = {} 
    for entry in current_map:
        ident = entry.get("supplier_product_identifier", "")
        asin = entry.get("chosen_amazon_asin")
        
        # normalize ident to just the number if possible
        if ident.startswith("EAN_"):
            ean = ident.replace("EAN_", "")
        else:
            ean = ident
            
        if ean and asin:
            existing_index[ean] = asin

    # 2. Scan Amazon Cache
    logger.info(f"Scanning Amazon Cache at {AMAZON_CACHE_DIR}...")
    cache_added_count = 0
    
    try:
        cache_files = [f for f in os.listdir(AMAZON_CACHE_DIR) if f.endswith(".json")]
        logger.info(f"Found {len(cache_files)} cache files.")
        
        for i, filename in enumerate(cache_files):
            file_path = os.path.join(AMAZON_CACHE_DIR, filename)
            
            try:
                # We interpret the filename as amazon_{ASIN}.json usually, but let's rely on content
                data = load_json(file_path)
                if not data:
                    continue
                
                # Extract Info
                asin = data.get("asin") or data.get("asin_extracted_from_page")
                ean_on_page = data.get("ean_on_page")
                
                # Fallback: check if we can get EAN from 'eans_on_page' list
                if not ean_on_page and data.get("eans_on_page"):
                    ean_on_page = data.get("eans_on_page")[0]

                if asin and ean_on_page:
                    ean = normalize_ean(ean_on_page)
                    
                    # Check if already exists
                    if ean not in existing_index:
                        # Create new entry
                        new_entry = {
                            "supplier_product_identifier": f"EAN_{ean}",
                            "supplier_title_snippet": "Reconstructed from Cache",
                            "chosen_amazon_asin": asin,
                            "amazon_title_snippet": data.get("title", ""),
                            "amazon_ean_on_page": ean,
                            "match_method": "RECONSTRUCTED_FROM_CACHE"
                        }
                        current_map.append(new_entry)
                        existing_index[ean] = asin # Update index
                        cache_added_count += 1
            except Exception as e:
                logger.warning(f"Error processing {filename}: {e}")
                
            if i > 0 and i % 1000 == 0:
                logger.info(f"Processed {i} files...")
                
    except Exception as e:
        logger.error(f"Error scanning cache dir: {e}")

    logger.info(f"Added {cache_added_count} entries from Amazon Cache.")

    # 3. Scan Financial Report
    logger.info(f"Scanning Financial Report at {FINANCIAL_REPORT_PATH}...")
    report_added_count = 0
    if os.path.exists(FINANCIAL_REPORT_PATH):
        try:
            with open(FINANCIAL_REPORT_PATH, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ean = row.get("Supplier EAN") or row.get("EAN")
                    asin = row.get("Amazon ASIN") or row.get("ASIN")
                    
                    if ean and asin:
                        ean = normalize_ean(ean)
                        if ean not in existing_index:
                             new_entry = {
                                "supplier_product_identifier": f"EAN_{ean}",
                                "supplier_title_snippet": "Reconstructed from Report",
                                "chosen_amazon_asin": asin,
                                "amazon_title_snippet": row.get("Amazon Title", ""),
                                "amazon_ean_on_page": ean,
                                "match_method": "RECONSTRUCTED_FROM_REPORT"
                            }
                             current_map.append(new_entry)
                             existing_index[ean] = asin
                             report_added_count += 1

        except Exception as e:
            logger.error(f"Error reading financial report: {e}")
    else:
        logger.warning("Financial report not found.")

    logger.info(f"Added {report_added_count} entries from Financial Report.")
    
    # 4. Save COMPLETE Map
    logger.info(f"Saving constructed map to {OUTPUT_FILE}...")
    save_json(OUTPUT_FILE, current_map)
    logger.info("Reconstruction Complete.")

if __name__ == "__main__":
    reconstruct()
