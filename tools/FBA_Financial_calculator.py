"""
FBA Financial Calculator
========================
Calculates ROI, net‑profit, breakeven price and profit margin by combining
supplier data (from OUTPUTS/FBA_ANALYSIS/cache) with Amazon scrape data
(from OUTPUTS/AMAZON_SCRAPE).

* VAT rate hard‑coded to 20 % (UK seller).
* Supplier prices are treated as EXCLUSIVE of VAT (config: supplier.prices_include_vat = false).
* Calculator automatically adds 20% VAT to supplier prices for accurate cost calculations.
* Prep cost (ex‑VAT) default 0.55 £ / unit.
* Shipping cost (ex‑VAT) default 0.00 £ / unit.
* If FBA and Referral fees are missing in Keepa product details, you can supply fallback values.
* Results are saved to the financial reports directory in OUTPUTS/FBA_ANALYSIS/financial_reports
"""

import os
import json
import pandas as pd
from datetime import datetime
import logging
import numpy as np

# Set up logging
log = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMAZON_SCRAPE_DIR = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "amazon_cache")
OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS")

def get_supplier_specific_paths(supplier_name):
    """Generate supplier-specific paths per authoritative path tracker"""
    # CRITICAL FIX: Normalize supplier name to match other components (dots → hyphens)
    normalized_supplier_name = supplier_name.replace('.', '-')
    return {
        'supplier_cache': os.path.join(BASE_DIR, "OUTPUTS", "cached_products", f"{normalized_supplier_name}_products_cache.json"),
        'financial_reports_dir': os.path.join(OUTPUT_DIR, "financial_reports", normalized_supplier_name),
        'linking_map': os.path.join(OUTPUT_DIR, "linking_maps", supplier_name, "linking_map.json"),  # Keep original subdirectory structure
        'ai_categories': os.path.join(OUTPUT_DIR, "ai_category_cache", f"{normalized_supplier_name}_ai_categories.json")
    }

# Ensure base directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AMAZON_SCRAPE_DIR, exist_ok=True)

# Load configuration from system_config.json
def load_system_config():
    """Load system configuration including VAT and fee settings."""
    try:
        config_path = os.path.join(BASE_DIR, "config", "system_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        log.warning(f"Failed to load system config: {e}, using defaults")
        return {}

# Load configuration
_config = load_system_config()

# Parameters from config with fallbacks
VAT_RATE = _config.get("amazon", {}).get("vat_rate", 0.2)
PREP_COST = _config.get("amazon", {}).get("fba_fees", {}).get("prep_house_fixed_fee", 0.55)  # Updated default to 0.55
SHIP_COST = 0.0
SUPPLIER_PRICES_INCLUDE_VAT = _config.get("supplier", {}).get("prices_include_vat", False)
FINANCIAL_REPORT_BATCH_SIZE = _config.get("system", {}).get("financial_report_batch_size", 50)

# Debug log the configuration values
print(f"🔧 CONFIG DEBUG: financial_report_batch_size = {FINANCIAL_REPORT_BATCH_SIZE}")
print(f"🧮 CONFIG DEBUG: supplier_prices_include_vat = {SUPPLIER_PRICES_INCLUDE_VAT}")
if SUPPLIER_PRICES_INCLUDE_VAT:
    print("   📝 Supplier prices are treated as INCLUSIVE of VAT")
else:
    print("   📝 Supplier prices are treated as EXCLUSIVE of VAT (will add 20% VAT)")

# Global variable to cache the linking map
_linking_map = None

def load_linking_map(supplier_name=None, latest_n=None):
    """
    Load the persistent linking map file for enhanced product matching.

    Args:
        supplier_name: Supplier identifier for supplier-specific paths
        latest_n: If provided, return only the N most recent entries by created_at timestamp
    """
    global _linking_map
    if _linking_map is not None:
        linking_map = _linking_map
    else:
        # Use supplier-specific linking map if supplier_name provided
        if supplier_name:
            supplier_paths = get_supplier_specific_paths(supplier_name)
            linking_map_path = supplier_paths['linking_map']
            if os.path.exists(linking_map_path):
                try:
                    with open(linking_map_path, 'r', encoding='utf-8') as f:
                        linking_map = json.load(f)
                    print(f"Loaded supplier-specific linking map with {len(linking_map)} entries")
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Error reading supplier-specific linking map: {e}")
                    return []
            else:
                print(f"Supplier-specific linking map not found: {linking_map_path}")
                return []
        else:
            # Fallback: try generic linking map
            generic_linking_map_path = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "linking_map.json")
            if os.path.exists(generic_linking_map_path):
                try:
                    with open(generic_linking_map_path, 'r', encoding='utf-8') as f:
                        linking_map = json.load(f)
                    print(f"Loaded generic linking map with {len(linking_map)} entries")
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Error reading generic linking map: {e}")
                    return []
            else:
                # Fallback: Look for linking map files in the output directory (legacy)
                linking_files = []

                if os.path.exists(OUTPUT_DIR):
                    for fname in os.listdir(OUTPUT_DIR):
                        if fname.startswith("linking_map_") and fname.endswith(".json"):
                            linking_files.append(os.path.join(OUTPUT_DIR, fname))

                if not linking_files:
                    print("No linking map found - using fallback lookup methods")
                    return []

                # Use the most recent linking map
                latest_map = max(linking_files, key=os.path.getmtime)
                try:
                    with open(latest_map, 'r', encoding='utf-8') as f:
                        linking_map = json.load(f)
                    print(f"Loaded legacy linking map: {latest_map} with {len(linking_map)} entries")
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Error reading legacy linking map {latest_map}: {e}")
                    return []

        # Cache the full linking map
        _linking_map = linking_map

    # Apply latest_n filtering if requested
    if latest_n and isinstance(latest_n, int) and latest_n > 0:
        # Sort by created_at timestamp (most recent first)
        try:
            sorted_map = sorted(linking_map,
                              key=lambda x: x.get('created_at', ''),
                              reverse=True)
            filtered_map = sorted_map[:latest_n]
            print(f"Filtered to latest {latest_n} entries (from {len(linking_map)} total)")
            return filtered_map
        except (KeyError, TypeError) as e:
            print(f"Warning: Could not sort by created_at timestamp: {e}. Using original order.")
            return linking_map[:latest_n]

    return linking_map

def find_amazon_json_by_linking_map(ean, title, url, supplier_name=None, latest_n=None):
    """Use linking map to find Amazon data for supplier product."""
    linking_map = load_linking_map(supplier_name, latest_n)
    
    # Search linking map for matching supplier product using current structure
    for link_record in linking_map:
        # CRITICAL FIX: Use actual linking map field names instead of expected legacy format
        supplier_ean = link_record.get("supplier_ean", "")
        supplier_url = link_record.get("supplier_url", "")
        
        # Check if this record matches our supplier product by EAN or URL
        match_found = False
        if ean and supplier_ean and ean == supplier_ean:
            match_found = True
            match_method = "EAN"
        elif url and supplier_url and url == supplier_url:
            match_found = True
            match_method = "URL"
        
        if match_found:
            # CRITICAL FIX: Use actual linking map field name for ASIN
            asin = link_record.get("amazon_asin")
            if asin:
                # Try to find the Amazon data file for this ASIN
                amazon_data = find_amazon_json_by_asin(asin, supplier_ean)
                if amazon_data:
                    print(f"Found Amazon data via linking map ({match_method}): {ean or url} -> {asin}")
                    return amazon_data
    
    return None

def find_amazon_json_by_asin(asin, ean=None):
    """Find Amazon JSON data by ASIN, with optional EAN for enhanced filename matching."""
    if not asin:
        return None
    
    # Try EAN-enhanced filename first if EAN is available
    if ean:
        ean_filename = f"amazon_{asin}_{ean}.json"
        ean_path = os.path.join(AMAZON_SCRAPE_DIR, ean_filename)
        if os.path.exists(ean_path):
            try:
                with open(ean_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error reading {ean_filename}: {e}")
    
    # Fallback to standard ASIN filename
    standard_filename = f"amazon_{asin}.json"
    standard_path = os.path.join(AMAZON_SCRAPE_DIR, standard_filename)
    if os.path.exists(standard_path):
        try:
            with open(standard_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error reading {standard_filename}: {e}")
    
    # Final fallback: search for any file containing the ASIN
    for fname in os.listdir(AMAZON_SCRAPE_DIR):
        if asin in fname and fname.endswith('.json'):
            try:
                with open(os.path.join(AMAZON_SCRAPE_DIR, fname), 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error reading {fname}: {e}")
                continue
    
    return None

# Helper to find Amazon data file by ASIN, EAN, or fuzzy title

def find_amazon_json(ean, asin, title, url=None, supplier_name=None, latest_n=None):
    """
    Enhanced Amazon data lookup using linking map as primary method.
    Falls back to legacy methods if linking map fails.
    """
    # Method 1: Use linking map (primary method for Fix 2.6)
    amazon_data = find_amazon_json_by_linking_map(ean, title, url, supplier_name, latest_n)
    if amazon_data:
        return amazon_data
    
    # Method 2: Direct ASIN lookup (if ASIN is provided)
    if asin:
        amazon_data = find_amazon_json_by_asin(asin, ean)
        if amazon_data:
            return amazon_data
    
    # Method 3: Legacy fallback methods for backwards compatibility
    # First try exact match for amazon_{ASIN}.json format
    if asin:
        exact_match_filename = f"amazon_{asin}.json"
        exact_match_path = os.path.join(AMAZON_SCRAPE_DIR, exact_match_filename)
        if os.path.exists(exact_match_path):
            try:
                with open(exact_match_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error reading {exact_match_filename}: {e}")
    
    # Fallback 1: Try any other filename containing EAN or ASIN
    for fname in os.listdir(AMAZON_SCRAPE_DIR):
        if (asin and asin in fname) or (ean and ean in fname):
            try:
                with open(os.path.join(AMAZON_SCRAPE_DIR, fname), 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error reading {fname}: {e}")
                continue
    
    # Fallback 2: Try fuzzy title search
    if title:
        title_main = title.lower().replace(' ', '').replace('-', '').replace('&', '')
        for fname in os.listdir(AMAZON_SCRAPE_DIR):
            if all(tok in fname.lower() for tok in title_main.split()[:3]):
                try:
                    with open(os.path.join(AMAZON_SCRAPE_DIR, fname), 'r', encoding='utf-8') as f:
                        return json.load(f)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Error reading {fname}: {e}")
                    continue
    
    return None

def extract_keepa_fees(product_details):
    # Accepts Keepa "Product Details" dict as loaded from Amazon scrape JSON
    # Returns referral_fee, fba_fee (both in £)
    # Looks for 'Referral fee' and 'FBA fee' in the block
    ref, fba = None, None
    if not product_details:
        return None, None
    for k, v in product_details.items():
        k_lower = k.lower()
        v_str = str(v).strip()

        if 'referral' in k_lower and 'fee' in k_lower:
            try:
                # Skip percentage fields and look for actual fee values
                if '%' in v_str:
                    continue
                # Remove currency symbols and parse
                ref = float(v_str.replace('£','').replace('$','').replace('€','').replace(',','').strip())
            except (ValueError, TypeError):
                print(f"Could not parse referral fee value: {v_str}")
                continue
                
        if ('fba' in k_lower or 'fulfillment' in k_lower or 'pick&pack' in k_lower) and 'fee' in k_lower:
            try:
                # Skip percentage fields
                if '%' in v_str:
                    continue
                # Remove currency symbols and parse
                fba = float(v_str.replace('£','').replace('$','').replace('€','').replace(',','').strip())
            except (ValueError, TypeError):
                print(f"Could not parse FBA fee value: {v_str}")
                continue
                
    return ref, fba

def extract_enhanced_metrics(amazon_data):
    """
    Extract enhanced metrics from Amazon data including:
    - Bought in past month data
    - FBA/FBM seller counts from Keepa
    """
    enhanced_metrics = {
        'bought_in_past_month': None,
        'fba_seller_count': None,
        'fbm_seller_count': None,
        'total_offer_count': None
    }

    # Extract "Bought in past month" data
    if amazon_data.get('amazon_monthly_sales_badge'):
        enhanced_metrics['bought_in_past_month'] = amazon_data['amazon_monthly_sales_badge']

    # Extract seller counts from Keepa data
    keepa_data = amazon_data.get('keepa', {})
    if keepa_data:
        product_details = keepa_data.get('product_details_tab_data', {})
        if product_details:
            # Extract total offer count
            if 'Total Offer Count' in product_details:
                try:
                    enhanced_metrics['total_offer_count'] = int(str(product_details['Total Offer Count']).replace(',', ''))
                except (ValueError, TypeError):
                    pass

            # Look for FBA/FBM seller information
            # Check for specific seller count fields first
            for key, value in product_details.items():
                key_lower = key.lower()
                if 'fba seller count' in key_lower or 'fba count' in key_lower:
                    try:
                        enhanced_metrics['fba_seller_count'] = int(str(value).replace(',', ''))
                    except (ValueError, TypeError):
                        enhanced_metrics['fba_seller_count'] = value
                elif 'fbm seller count' in key_lower or 'fbm count' in key_lower:
                    try:
                        enhanced_metrics['fbm_seller_count'] = int(str(value).replace(',', ''))
                    except (ValueError, TypeError):
                        enhanced_metrics['fbm_seller_count'] = value

            # Fallback: Look for presence indicators if specific counts not found
            if enhanced_metrics['fba_seller_count'] is None and 'Lowest FBA Seller' in product_details:
                enhanced_metrics['fba_seller_count'] = 'Available (see Keepa data)'
            if enhanced_metrics['fbm_seller_count'] is None and 'Lowest FBM Seller' in product_details:
                enhanced_metrics['fbm_seller_count'] = 'Available (see Keepa data)'

    return enhanced_metrics

def _financials_internal(supplier, amazon, supplier_price_inc_vat):
    """
    Scenario 1 — UK-Established VAT-Registered (you account for output VAT)
    Returns values keyed the same way as the original script, but fixes VAT/flow math:
      - NetProceeds = Amazon payout NOW (gross − fees inc-VAT)
      - HMRC = Output VAT − Input VAT (input VAT includes supplier + fees + prep + shipping)
      - NetProfit = ex-VAT identity: (Selling/1.2) − (Supplier_ex + Fees_ex + Prep_ex + Ship_ex)
      - ROI kept on (Supplier_ex + Prep_ex + Ship_ex)
      - Breakeven (inc-VAT) = 1.2 × (Supplier_ex + Fees_ex + Prep_ex + Ship_ex)
      - ProfitMargin on ex-VAT revenue
    """
    # 1) Resolve Amazon price (inc-VAT) from multiple possible fields
    amazon_price = None
    if 'current_price' in amazon:
        amazon_price = amazon['current_price']
    elif 'price' in amazon:
        amazon_price = amazon['price']
    else:
        print(f"WARNING: No price found in Amazon data for {amazon.get('asin_queried', 'unknown ASIN')}")
        return {}

    # Normalize to float & set explicit alias used below
    selling_price_inc_vat = float(amazon_price)

    # 2) Defaults (fallbacks ONLY; prefer external/Keepa when available). All EX-VAT.
    #    If your pipeline provides ex/ inc VAT fee fields, they will override these below.
    referral_fee = 0.15 * (selling_price_inc_vat / (1 + VAT_RATE))  # EX-VAT fallback %
    fba_fee = 2.8  # EX-VAT fallback flat

    # 3) Pull fees from Keepa (already EX-VAT in your extractor). Keeps minimal structure you had.
    if 'keepa' in amazon and amazon['keepa']:
        keepa_data = amazon['keepa']
        if 'product_details_tab_data' in keepa_data and keepa_data['product_details_tab_data']:
            ref, fba = extract_keepa_fees(keepa_data['product_details_tab_data'])
            if ref is not None: referral_fee = float(ref)
            if fba is not None: fba_fee = float(fba)
        elif 'keepa_product_details' in amazon and amazon['keepa_product_details']:
            ref, fba = extract_keepa_fees(amazon['keepa_product_details'])
            if ref is not None: referral_fee = float(ref)
            if fba is not None: fba_fee = float(fba)

    # 4) Supplier price normalization (compute both ex-VAT and inc-VAT consistently)
    original_price = float(supplier_price_inc_vat)

    if SUPPLIER_PRICES_INCLUDE_VAT:
        supplier_price_ex_vat = original_price / (1 + VAT_RATE)
        supplier_price_inc_vat = original_price  # as provided
        print(f"🧮 VAT: Supplier price £{original_price:.2f} inc-VAT → £{supplier_price_ex_vat:.2f} ex-VAT (÷{1+VAT_RATE})")
    else:
        supplier_price_ex_vat = original_price   # provided ex-VAT
        supplier_price_inc_vat = original_price * (1 + VAT_RATE)
        print(f"🧮 VAT: Supplier price £{original_price:.2f} ex-VAT → £{supplier_price_inc_vat:.2f} inc-VAT (×{1+VAT_RATE})")

    # 5) Core VAT pieces
    amazon_price_ex_vat = selling_price_inc_vat / (1 + VAT_RATE)          # P_ex
    output_vat = selling_price_inc_vat * VAT_RATE / (1 + VAT_RATE)        # P/6

    # 6) Costs (EX-VAT)
    fees_ex_vat = (referral_fee or 0.0) + (fba_fee or 0.0)
    total_ex_vat_costs = supplier_price_ex_vat + fees_ex_vat + PREP_COST + SHIP_COST

    # 7) Amazon payout NOW (cash): gross − fees inc-VAT
    net_proceeds = selling_price_inc_vat - (fees_ex_vat * (1 + VAT_RATE))

    # 8) HMRC later: Output VAT − Input VAT (Input VAT includes supplier + fees + prep + shipping)
    input_vat = VAT_RATE * (supplier_price_ex_vat + fees_ex_vat + PREP_COST + SHIP_COST)
    hmrc = output_vat - input_vat  # +payable / −refund

    # 9) Eventual Net Profit (AFTER VAT return) — ex-VAT identity
    net_profit = amazon_price_ex_vat - total_ex_vat_costs
    # (Equivalently: (net_proceeds - supplier_price_inc_vat) - hmrc)

    # 10) ROI — keep your original convention (supplier_ex + prep + shipping)
    _roi_base = supplier_price_ex_vat + PREP_COST + SHIP_COST
    roi = (net_profit / _roi_base * 100) if _roi_base > 0 else 0.0

    # 11) Breakeven (inc-VAT) and Profit Margin (on ex-VAT revenue)
    breakeven = total_ex_vat_costs * (1 + VAT_RATE)
    profit_margin = (net_profit / amazon_price_ex_vat * 100) if amazon_price_ex_vat > 0 else 0.0

    # 12) Return keys unchanged
    return {
        'SupplierPrice_incVAT': supplier_price_inc_vat,
        'SupplierPrice_exVAT': supplier_price_ex_vat,
        'SellingPrice_incVAT': selling_price_inc_vat,
        'ReferralFee': referral_fee,               # EX-VAT
        'FBAFee': fba_fee,                         # EX-VAT
        'PrepHouseFee': PREP_COST,                 # EX-VAT
        'OutputVAT': output_vat,
        'InputVAT': input_vat,
        'NetProceeds': net_proceeds,               # Amazon payout (cash now)
        'HMRC': hmrc,                              # +payable / −refund later
        'NetProfit': net_profit,                   # AFTER VAT return
        'ROI': roi,                                # %
        'Breakeven': breakeven,                    # inc-VAT price
        'ProfitMargin': profit_margin,             # % on ex-VAT revenue
    }


def financials(supplier_price, amazon_price, amazon_sales_rank=None, amazon_rating=None, amazon_review_count=None):
    """
    Backward compatibility wrapper for the financials function.
    This maintains the original API that the workflow expects.

    Args:
        supplier_price: The supplier price (treated as exclusive of VAT based on config)
        amazon_price: The Amazon selling price (inclusive of VAT)
        amazon_sales_rank: Optional sales rank for enhanced metrics
        amazon_rating: Optional rating for enhanced metrics
        amazon_review_count: Optional review count for enhanced metrics

    Returns:
        dict: Financial calculations with proper VAT handling
    """
    # Create mock objects to match the expected function signature
    supplier_mock = {
        'price': supplier_price,
        'title': 'Unknown Product',
        'url': 'Unknown URL'
    }

    amazon_mock = {
        'current_price': amazon_price,
        'price': amazon_price,
        'sales_rank': amazon_sales_rank or 999999,
        'rating': amazon_rating or 0,
        'reviews': amazon_review_count or 0,
        'asin_queried': 'UNKNOWN_ASIN'
    }

    # Call the internal financials function with proper VAT handling
    return _financials_internal(supplier_mock, amazon_mock, supplier_price)


def run_calculations(supplier_name, supplier_cache_path=None, output_dir=None, amazon_scrape_dir=None,
                    latest_n=None, batch_size=None):
    """
    Core calculation function with batching support.

    Args:
        supplier_name: Supplier identifier for supplier-specific paths (REQUIRED)
        supplier_cache_path: Path to supplier cache JSON file
        output_dir: Directory to save financial reports
        amazon_scrape_dir: Directory containing Amazon scrape data
        latest_n: If provided, process only the N most recent linking map entries
        batch_size: Size of batches for CSV generation (uses config default if None)

    Returns:
        dict: Results containing DataFrames, statistics, and file paths
    """
    if not supplier_name:
        raise ValueError("supplier_name is required for supplier-specific path generation")

    # Use provided batch_size or config default
    if batch_size is None:
        batch_size = FINANCIAL_REPORT_BATCH_SIZE

    print(f"🔧 CONFIG: Using batch_size = {batch_size}")
    if latest_n:
        print(f"🔧 CONFIG: Processing latest_n = {latest_n} linking map entries")

    # Generate supplier-specific paths
    supplier_paths = get_supplier_specific_paths(supplier_name)

    # Use parameters or supplier-specific defaults
    cache_path = supplier_cache_path or supplier_paths['supplier_cache']
    out_dir = output_dir or supplier_paths['financial_reports_dir']
    amazon_dir = amazon_scrape_dir or AMAZON_SCRAPE_DIR

    # Ensure output directory exists - CRITICAL for supplier-specific paths
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.dirname(supplier_paths['supplier_cache']), exist_ok=True)
    os.makedirs(os.path.dirname(supplier_paths['linking_map']), exist_ok=True)
    os.makedirs(os.path.dirname(supplier_paths['ai_categories']), exist_ok=True)

    # === BEGIN ADDED DEBUG ===
    if not os.path.exists(amazon_dir):
        raise FileNotFoundError(f"CRITICAL FBA_Financial_calculator: amazon_dir does not exist: {amazon_dir}")
    if not os.path.isdir(amazon_dir):
        raise NotADirectoryError(f"CRITICAL FBA_Financial_calculator: amazon_dir is not a directory: {amazon_dir}")
    log.info(f"FBA_Financial_calculator: amazon_dir confirmed to exist and is a directory: {amazon_dir}")
    # === END ADDED DEBUG ===

    print(f"Loading supplier products from: {cache_path}")
    print(f"Using Amazon data from: {amazon_dir}")
    print(f"Output will be saved to: {out_dir}")

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            supplier_products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Error reading supplier cache: {e}")

    # Load linking map (with latest_n filtering if specified)
    linking_map = load_linking_map(supplier_name, latest_n)
    if not linking_map:
        raise Exception("No linking map entries found")

    print(f"Processing {len(linking_map)} linking map entries...")
    print(f"Supplier products cache has {len(supplier_products)} items")

    # Create a lookup dict for faster supplier product matching
    supplier_lookup = {}
    for sp in supplier_products:
        ean = sp.get('ean')
        url = sp.get('url')
        if ean:
            supplier_lookup[ean] = sp
        if url:
            supplier_lookup[url] = sp

    all_records = []
    batch_results = []
    processed = 0
    found_matches = 0
    batch_number = 1

    for link_record in linking_map:
        supplier_ean = link_record.get("supplier_ean", "")
        supplier_url = link_record.get("supplier_url", "")
        amazon_asin = link_record.get("amazon_asin")

        # Find matching supplier product
        supplier_product = None
        if supplier_ean and supplier_ean in supplier_lookup:
            supplier_product = supplier_lookup[supplier_ean]
        elif supplier_url and supplier_url in supplier_lookup:
            supplier_product = supplier_lookup[supplier_url]

        if not supplier_product:
            continue

        processed += 1

        # Get product details
        ean = supplier_product.get('ean')
        asin = amazon_asin  # Use ASIN from linking map
        title = supplier_product.get('title')
        url = supplier_product.get('url')

        supplier_price = float(supplier_product.get('price', 0))

        # Find Amazon data using linking map ASIN or fallback methods
        amazon = None
        if amazon_asin:
            amazon = find_amazon_json_by_asin(amazon_asin, ean)
        if not amazon:
            amazon = find_amazon_json(ean, asin, title, url, supplier_name, latest_n)

        if not amazon:
            if processed % 25 == 0:
                print(f"Processed {processed}/{len(linking_map)} - No Amazon data for: EAN={ean}, ASIN={asin}")
            continue

        found_matches += 1

        # Check for price data
        price_fields = ['current_price', 'price', 'original_price', 'amazon_price']
        price = None
        price_source = None

        for field in price_fields:
            if field in amazon and amazon[field] is not None:
                try:
                    price = float(amazon[field])
                    price_source = field
                    break
                except (ValueError, TypeError):
                    continue

        if not price:
            missing_fields = [f"{field}={amazon.get(field)}" for field in price_fields]
            logger = logging.getLogger(__name__)
            logger.warning(f"❌ NO PRICE DATA: EAN={ean}, ASIN={asin}, Available fields: {missing_fields}")
            continue
        else:
            logger = logging.getLogger(__name__)
            logger.info(f"✅ PRICE FOUND: EAN={ean}, ASIN={asin}, Price=£{price} (from {price_source})")

        # Get Amazon URL
        amazon_url = amazon.get('url')
        if not amazon_url and 'asin_queried' in amazon:
            amazon_url = f"https://www.amazon.co.uk/dp/{amazon['asin_queried']}"

        # Get Amazon title for the CSV
        amazon_title = amazon.get('title', amazon.get('product_title', 'N/A'))

        # Create the row data
        row = {
            'EAN': ean,
            'EAN_OnPage': amazon.get('ean_on_page'),
            'ASIN': asin if asin else amazon.get('asin_queried', amazon.get('asin_from_details')),
            'SupplierTitle': title,
            'AmazonTitle': amazon_title,
            'SupplierURL': url,
            'AmazonURL': amazon_url,
            'MatchMethod': link_record.get('match_method', ''),
            'Confidence': link_record.get('confidence', ''),
            'CreatedAt': link_record.get('created_at', '')
        }

        # Add enhanced metrics
        enhanced_metrics = extract_enhanced_metrics(amazon)
        row.update(enhanced_metrics)

        financial_data = _financials_internal(supplier_product, amazon, supplier_price)
        if financial_data:
            row.update(financial_data)
            all_records.append(row)

        # Check if we should generate a batch report based on linking map entries processed
        if processed % batch_size == 0 and processed > 0:
            # Generate batch report for this batch of linking map entries
            if all_records:  # Only generate if we have some successful calculations
                batch_df = pd.DataFrame(all_records)

                # Sort by ROI (highest first) for better analysis
                if 'ROI' in batch_df.columns:
                    batch_df = batch_df.sort_values(by='ROI', ascending=False)

                dt = datetime.now().strftime('%Y%m%d_%H%M%S')
                batch_out_path = os.path.join(out_dir, f'fba_financial_report_batch_{batch_number}_{dt}.csv')
                batch_df.to_csv(batch_out_path, index=False)

                print(f"📊 Generated batch {batch_number} CSV: {batch_out_path} ({len(all_records)} records from {batch_size} linking map entries)")

                # Store batch results
                batch_stats = {
                    'batch_number': batch_number,
                    'records_count': len(all_records),
                    'output_file': batch_out_path,
                    'linking_map_entries_processed': batch_size,
                    'successful_calculations': len(all_records)
                }

                if 'ROI' in batch_df.columns:
                    batch_stats['profitable_count'] = batch_df[batch_df['ROI'] > 0.3].shape[0]
                    batch_stats['marginal_count'] = batch_df[(batch_df['ROI'] <= 0.3) & (batch_df['ROI'] > 0)].shape[0]
                    batch_stats['unprofitable_count'] = batch_df[batch_df['ROI'] <= 0].shape[0]

                batch_results.append({
                    'dataframe': batch_df,
                    'statistics': batch_stats,
                    'records': all_records
                })

            # Reset accumulator for next batch
            all_records = []
            batch_number += 1

    # Process remaining records if any
    if all_records:
        batch_df = pd.DataFrame(all_records)

        # Sort by ROI (highest first) for better analysis
        if 'ROI' in batch_df.columns:
            batch_df = batch_df.sort_values(by='ROI', ascending=False)

        dt = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_out_path = os.path.join(out_dir, f'fba_financial_report_batch_{batch_number}_{dt}.csv')
        batch_df.to_csv(batch_out_path, index=False)

        print(f"📊 Generated final batch {batch_number} CSV: {batch_out_path} ({len(all_records)} records)")

        batch_stats = {
            'batch_number': batch_number,
            'records_count': len(all_records),
            'output_file': batch_out_path,
            'processed_in_batch': len(all_records)
        }

        if 'ROI' in batch_df.columns:
            batch_stats['profitable_count'] = batch_df[batch_df['ROI'] > 0.3].shape[0]
            batch_stats['marginal_count'] = batch_df[(batch_df['ROI'] <= 0.3) & (batch_df['ROI'] > 0)].shape[0]
            batch_stats['unprofitable_count'] = batch_df[batch_df['ROI'] <= 0].shape[0]

        batch_results.append({
            'dataframe': batch_df,
            'statistics': batch_stats,
            'records': all_records
        })

    # Calculate overall statistics
    total_processed = sum(batch['statistics']['records_count'] for batch in batch_results)

    overall_stats = {
        'total_batches': len(batch_results),
        'total_processed': processed,
        'total_found_matches': found_matches,
        'total_generated_calculations': total_processed,
        'linking_map_entries_processed': len(linking_map),
        'supplier_products_total': len(supplier_products),
        'batch_size_used': batch_size,
        'latest_n_used': latest_n,
        'output_files': [batch['statistics']['output_file'] for batch in batch_results]
    }

    # Add profitability summary across all batches
    all_profitable = sum(batch['statistics'].get('profitable_count', 0) for batch in batch_results)
    all_marginal = sum(batch['statistics'].get('marginal_count', 0) for batch in batch_results)
    all_unprofitable = sum(batch['statistics'].get('unprofitable_count', 0) for batch in batch_results)

    overall_stats.update({
        'total_profitable': all_profitable,
        'total_marginal': all_marginal,
        'total_unprofitable': all_unprofitable
    })

    if not batch_results:
        raise Exception("No matching records found. Check file paths and data consistency.")

    return {
        'batch_results': batch_results,
        'overall_statistics': overall_stats,
        'linking_map_size': len(linking_map)
    }

def main():
    """Main entry point that calls run_calculations and displays results."""
    try:
        # Default supplier name for backward compatibility - should be passed as parameter in production
        supplier_name = "poundwholesale.co.uk"  # Updated to match current usage

        # For testing batching - process latest 100 entries with batch size 10
        results = run_calculations(
            supplier_name,
            latest_n=100,  # Process only latest 100 linking map entries
            batch_size=10  # Generate CSV every 10 records
        )

        batch_results = results['batch_results']
        overall_stats = results['overall_statistics']

        print(f"\n🎯 BATCHING RESULTS SUMMARY:")
        print(f"Total batches generated: {overall_stats['total_batches']}")
        print(f"Total processed: {overall_stats['total_processed']}")
        print(f"Total found matches: {overall_stats['total_found_matches']}")
        print(f"Total calculations: {overall_stats['total_generated_calculations']}")
        print(f"Linking map entries processed: {overall_stats['linking_map_entries_processed']}")
        print(f"Batch size used: {overall_stats['batch_size_used']}")
        print(f"Latest N used: {overall_stats['latest_n_used']}")

        print(f"\n📁 Generated CSV files:")
        for i, file_path in enumerate(overall_stats['output_files'], 1):
            print(f"  Batch {i}: {file_path}")

        print(f"\n💰 Overall Profitability:")
        print(f"  - Good ROI (>30%): {overall_stats.get('total_profitable', 0)} items")
        print(f"  - Marginal (0-30%): {overall_stats.get('total_marginal', 0)} items")
        print(f"  - Unprofitable: {overall_stats.get('total_unprofitable', 0)} items")

        # Show details for first batch
        if batch_results:
            first_batch = batch_results[0]
            df = first_batch['dataframe']
            stats = first_batch['statistics']

            print(f"\n📊 First Batch Details (Batch {stats['batch_number']}):")
            print(f"Records in batch: {stats['records_count']}")
            print(f"Output file: {stats['output_file']}")

            if 'ROI' in df.columns and not df.empty:
                print(f"\nTop 3 items in first batch by ROI:")
                print(df.head(3)[['ASIN', 'EAN', 'SupplierTitle', 'ROI', 'NetProfit', 'SellingPrice_incVAT', 'SupplierPrice_incVAT']].to_string())

    except Exception as e:
        print(f"Error in financial calculations: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == '__main__':
    main()
