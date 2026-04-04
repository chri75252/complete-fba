"""
FBA Financial Calculator - Amazon Cache Processor
Processes ALL Amazon cache files and matches with supplier prices to generate
a complete financial report (like the system workflow does).
"""
import os
import json
import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMAZON_SCRAPE_DIR = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS", "amazon_cache")
OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS")

def get_supplier_specific_paths(supplier_name):
    """Generate supplier-specific paths per authoritative path tracker"""
    normalized_supplier_name = supplier_name.replace('.', '-')
    return {
        'supplier_cache': os.path.join(BASE_DIR, "OUTPUTS", "cached_products", f"{normalized_supplier_name}_products_cache.json"),
        'financial_reports_dir': os.path.join(OUTPUT_DIR, "financial_reports", normalized_supplier_name),
        'linking_map': os.path.join(OUTPUT_DIR, "linking_maps", supplier_name, "linking_map.json"),
    }

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

_config = load_system_config()

# Parameters from config with fallbacks
VAT_RATE = _config.get("amazon", {}).get("vat_rate", 0.2)
PREP_COST = _config.get("amazon", {}).get("fba_fees", {}).get("prep_house_fixed_fee", 0.55)
SHIP_COST = 0.0
SUPPLIER_PRICES_INCLUDE_VAT = _config.get("supplier", {}).get("prices_include_vat", True)

# Fee defaults from config
FBA_FEES_CFG = _config.get("amazon", {}).get("fba_fees", {})
REFERRAL_FEE_RATE_DEFAULT = FBA_FEES_CFG.get("referral_fee_rate", 0.15)
FBA_FEE_DEFAULT = FBA_FEES_CFG.get("fulfillment_fee_minimum", 2.8)

def extract_keepa_fees(product_details):
    """Extract referral and FBA fees from Keepa product details."""
    ref, fba = None, None
    if not product_details:
        return None, None
    for k, v in product_details.items():
        k_lower = k.lower()
        v_str = str(v).strip()

        if 'referral' in k_lower and 'fee' in k_lower:
            try:
                if '%' in v_str:
                    continue
                ref = float(v_str.replace('\u00A3','').replace('$','').replace('\u20AC','').replace(',','').strip())
            except (ValueError, TypeError):
                continue

        if ('fba' in k_lower or 'fulfillment' in k_lower or 'pick&pack' in k_lower) and 'fee' in k_lower:
            try:
                if '%' in v_str:
                    continue
                fba = float(v_str.replace('\u00A3','').replace('$','').replace('\u20AC','').replace(',','').strip())
            except (ValueError, TypeError):
                continue
    return ref, fba

def extract_enhanced_metrics(amazon_data):
    """Extract enhanced metrics from Amazon data."""
    enhanced_metrics = {
        'bought_in_past_month': None,
        'fba_seller_count': None,
        'fbm_seller_count': None,
        'total_offer_count': None
    }

    if amazon_data.get('amazon_monthly_sales_badge'):
        enhanced_metrics['bought_in_past_month'] = amazon_data['amazon_monthly_sales_badge']

    keepa_data = amazon_data.get('keepa', {})
    if keepa_data:
        product_details = keepa_data.get('product_details_tab_data', {})
        if product_details:
            if 'Total Offer Count' in product_details:
                try:
                    enhanced_metrics['total_offer_count'] = int(str(product_details['Total Offer Count']).replace(',', ''))
                except (ValueError, TypeError):
                    pass

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

            if enhanced_metrics['fba_seller_count'] is None and 'Lowest FBA Seller' in product_details:
                enhanced_metrics['fba_seller_count'] = 'Available (see Keepa data)'
            if enhanced_metrics['fbm_seller_count'] is None and 'Lowest FBM Seller' in product_details:
                enhanced_metrics['fbm_seller_count'] = 'Available (see Keepa data)'

    return enhanced_metrics

def financials(supplier_price_inc_vat, amazon):
    """Calculate financial metrics for a product."""
    amazon_price = None
    if 'current_price' in amazon:
        amazon_price = amazon['current_price']
    elif 'price' in amazon:
        amazon_price = amazon['price']
    else:
        return {}

    referral_fee = REFERRAL_FEE_RATE_DEFAULT * (amazon_price / (1 + VAT_RATE))
    fba_fee = FBA_FEE_DEFAULT

    if 'keepa' in amazon and amazon['keepa']:
        keepa_data = amazon['keepa']
        if 'product_details_tab_data' in keepa_data and keepa_data['product_details_tab_data']:
            ref, fba = extract_keepa_fees(keepa_data['product_details_tab_data'])
            if ref: referral_fee = ref
            if fba: fba_fee = fba
        elif 'keepa_product_details' in amazon and amazon['keepa_product_details']:
            ref, fba = extract_keepa_fees(amazon['keepa_product_details'])
            if ref: referral_fee = ref
            if fba: fba_fee = fba

    selling_price_inc_vat = amazon_price

    if SUPPLIER_PRICES_INCLUDE_VAT:
        supplier_price_ex_vat = supplier_price_inc_vat / (1 + VAT_RATE)
        input_vat = supplier_price_inc_vat * VAT_RATE / (1 + VAT_RATE)
    else:
        supplier_price_ex_vat = supplier_price_inc_vat
        input_vat = supplier_price_ex_vat * VAT_RATE
        supplier_price_inc_vat = supplier_price_ex_vat + input_vat

    amazon_price_ex_vat = selling_price_inc_vat / (1 + VAT_RATE)
    output_vat = selling_price_inc_vat - amazon_price_ex_vat
    input_vat_supplier = supplier_price_inc_vat - supplier_price_ex_vat
    input_vat_fees_prep_ship = VAT_RATE * (referral_fee + fba_fee + PREP_COST + SHIP_COST)
    input_vat = input_vat_supplier + input_vat_fees_prep_ship
    hmrc = -input_vat

    net_proceeds = amazon_price_ex_vat - referral_fee - fba_fee - supplier_price_ex_vat
    net_profit = net_proceeds - PREP_COST - SHIP_COST

    total_cost_ex_vat = supplier_price_ex_vat + PREP_COST + SHIP_COST
    roi = (net_profit / total_cost_ex_vat) * 100 if total_cost_ex_vat > 0 else 0

    breakeven = (1 + VAT_RATE) * (
        supplier_price_ex_vat + referral_fee + fba_fee + PREP_COST + SHIP_COST
    )

    profit_margin = (net_profit / amazon_price_ex_vat) * 100 if amazon_price_ex_vat > 0 else 0
    return {
        'SupplierPrice_incVAT': supplier_price_inc_vat,
        'SupplierPrice_exVAT': supplier_price_ex_vat,
        'SellingPrice_incVAT': selling_price_inc_vat,
        'ReferralFee': referral_fee,
        'FBAFee': fba_fee,
        'PrepHouseFee': PREP_COST,
        'OutputVAT': output_vat,
        'InputVAT': input_vat,
        'NetProceeds': net_proceeds,
        'HMRC': hmrc,
        'NetProfit': net_profit,
        'ROI': roi,
        'Breakeven': breakeven,
        'ProfitMargin': profit_margin,
    }

def run_calculations_from_amazon_cache(supplier_name):
    """
    Process ALL Amazon cache files and match with supplier prices
    (like the system workflow does).

    Args:
        supplier_name: Supplier identifier for supplier-specific paths (REQUIRED)

    Returns:
        dict: Results containing DataFrame, statistics, and file path
    """
    if not supplier_name:
        raise ValueError("supplier_name is required")

    supplier_paths = get_supplier_specific_paths(supplier_name)

    # Paths
    supplier_cache_path = supplier_paths['supplier_cache']
    linking_map_path = supplier_paths['linking_map']
    out_dir = supplier_paths['financial_reports_dir']

    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading supplier cache from: {supplier_cache_path}")
    print(f"Loading linking map from: {linking_map_path}")
    print(f"Using Amazon data from: {AMAZON_SCRAPE_DIR}")
    print(f"Output will be saved to: {out_dir}")

    # Load supplier cache for price lookup
    try:
        with open(supplier_cache_path, 'r', encoding='utf-8') as f:
            supplier_products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Error reading supplier cache: {e}")

    # Create maps for quick lookup
    supplier_products_map = {}  # EAN -> supplier product
    supplier_url_map = {}  # URL -> supplier product
    for sp in supplier_products:
        if 'ean' in sp:
            supplier_products_map[sp['ean']] = sp
        if 'normalized_url' in sp:
            supplier_url_map[sp['normalized_url']] = sp
        elif 'url' in sp:
            supplier_url_map[sp['url']] = sp

    print(f"Loaded {len(supplier_products_map)} products from supplier cache (EAN map)")
    print(f"Loaded {len(supplier_url_map)} URLs from supplier cache (URL map)")

    # Load linking map for EAN->ASIN lookups
    try:
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load linking map: {e}")
        linking_map = []

    # Create linking map lookups
    ean_to_asin = {}  # EAN -> ASIN
    url_to_asin = {}  # supplier URL -> ASIN
    for link in linking_map:
        if link.get('supplier_ean') and link.get('amazon_asin'):
            ean_to_asin[link['supplier_ean']] = link['amazon_asin']
        if link.get('supplier_url') and link.get('amazon_asin'):
            url_to_asin[link['supplier_url']] = link['amazon_asin']

    print(f"Loaded {len(ean_to_asin)} EAN->ASIN mappings from linking map")
    print(f"Loaded {len(url_to_asin)} URL->ASIN mappings from linking map")

    # Get all Amazon cache files
    amazon_files = [f for f in os.listdir(AMAZON_SCRAPE_DIR) if f.endswith('.json')]
    print(f"Processing {len(amazon_files):,} Amazon cache files...")

    records = []
    processed = 0
    found_matches = 0
    no_supplier_match = 0
    no_price = 0

    for amazon_filename in amazon_files:
        try:
            with open(os.path.join(AMAZON_SCRAPE_DIR, amazon_filename), 'r', encoding='utf-8') as f:
                amazon = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log.error(f"Error reading {amazon_filename}: {e}")
            continue

        processed += 1

        # Extract EAN from Amazon data
        amazon_ean = amazon.get('ean_on_page')
        asin = amazon.get('asin_queried') or amazon.get('asin')

        if not asin:
            continue

        # Try to find supplier price via EAN
        supplier_product = None
        supplier_price = None
        match_method = None

        # Method 1: Match by EAN
        if amazon_ean and amazon_ean in supplier_products_map:
            supplier_product = supplier_products_map[amazon_ean]
            supplier_price = float(supplier_product['price']) if supplier_product.get('price') else 0
            match_method = 'EAN'

        # Method 2: Match via linking map EAN->ASIN
        if not supplier_product and amazon_ean and amazon_ean in ean_to_asin:
            linked_ean = amazon_ean
            if linked_ean in supplier_products_map:
                supplier_product = supplier_products_map[linked_ean]
                supplier_price = float(supplier_product['price']) if supplier_product.get('price') else 0
                match_method = 'LinkingMap_EAN'

        # Method 3: Match via linking map URL->ASIN
        if not supplier_product:
            for supplier_url, linked_asin in url_to_asin.items():
                if linked_asin == asin and supplier_url in supplier_url_map:
                    supplier_product = supplier_url_map[supplier_url]
                    supplier_price = float(supplier_product['price']) if supplier_product.get('price') else 0
                    match_method = 'LinkingMap_URL'
                    break

        if not supplier_product or supplier_price is None or supplier_price == 0:
            no_supplier_match += 1
            continue

        # Extract price from Amazon data
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

        if not price or price <= 0:
            no_price += 1
            continue

        found_matches += 1

        # Build URLs
        amazon_url = amazon.get('url')
        if not amazon_url:
            amazon_url = f"https://www.amazon.co.uk/dp/{asin}"

        amazon_title = amazon.get('title', amazon.get('product_title', 'N/A'))

        row = {
            'EAN': amazon_ean,
            'EAN_OnPage': amazon_ean,
            'ASIN': asin,
            'SupplierTitle': supplier_product.get('title', 'N/A'),
            'AmazonTitle': amazon_title,
            'SupplierURL': supplier_product.get('url'),
            'AmazonURL': amazon_url
        }

        # Add enhanced metrics
        enhanced_metrics = extract_enhanced_metrics(amazon)
        row.update(enhanced_metrics)

        # Calculate financials
        financial_data = financials(supplier_price, amazon)
        if financial_data:
            row.update(financial_data)
            records.append(row)

        if found_matches % 1000 == 0:
            print(f"Found {found_matches:,} matches so far...")

    print(f"\nProcessing complete:")
    print(f"  Amazon files processed: {processed:,}")
    print(f"  Found supplier matches: {found_matches:,}")
    print(f"  No supplier match: {no_supplier_match:,}")
    print(f"  No price data: {no_price:,}")

    if not records:
        raise Exception("No matching records found.")

    df = pd.DataFrame(records)

    if 'ROI' in df.columns:
        df = df.sort_values(by='ROI', ascending=False)

    dt = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(out_dir, f'fba_financial_report_{dt}.csv')
    df.to_csv(out_path, index=False)

    stats = {
        'processed': processed,
        'found_matches': found_matches,
        'generated_calculations': len(records),
        'output_file': out_path,
        'no_supplier_match': no_supplier_match,
        'no_price': no_price
    }

    if 'ROI' in df.columns:
        min_roi_cfg = _config.get("analysis", {}).get("min_roi_percent", 30.0)
        profitable_threshold = float(min_roi_cfg)
        stats['profitable_count'] = df[df['ROI'] > profitable_threshold].shape[0]
        stats['marginal_count'] = df[(df['ROI'] <= profitable_threshold) & (df['ROI'] > 0)].shape[0]
        stats['unprofitable_count'] = df[df['ROI'] <= 0].shape[0]
        stats['top_5_by_roi'] = df.head(5)[['ASIN', 'EAN', 'SupplierTitle', 'ROI', 'NetProfit', 'SellingPrice_incVAT', 'SupplierPrice_incVAT']].to_dict('records')

    return {
        'dataframe': df,
        'statistics': stats,
        'records': records
    }

def main():
    """Main entry point."""
    supplier_name = "efghousewares.co.uk"

    try:
        results = run_calculations_from_amazon_cache(supplier_name)

        if not results:
            print("\nNo results generated.")
            return

        df = results['dataframe']
        stats = results['statistics']

        print(f"\n{'='*70}")
        print(f"Amazon Cache Financial Report Generated")
        print(f"{'='*70}")
        print(f"Amazon files processed: {stats['processed']:,}")
        print(f"Found supplier matches: {stats['found_matches']:,}")
        print(f"Generated calculations: {stats['generated_calculations']:,}")
        print(f"\nFinancial report saved to:")
        print(f"  {stats['output_file']}")

        if 'ROI' in df.columns:
            print(f"\n{'='*70}")
            print(f"Top 5 items by ROI:")
            print(f"{'='*70}")
            print(df.head(5)[['ASIN', 'EAN', 'SupplierTitle', 'ROI', 'NetProfit', 'SellingPrice_incVAT', 'SupplierPrice_incVAT']].to_string())

            print(f"\n{'='*70}")
            print(f"Profitability breakdown:")
            print(f"{'='*70}")
            print(f"  - Good ROI (>30%): {stats.get('profitable_count', 0):,} items")
            print(f"  - Marginal (0-30%): {stats.get('marginal_count', 0):,} items")
            print(f"  - Unprofitable: {stats.get('unprofitable_count', 0):,} items")
            print(f"{'='*70}\n")

    except Exception as e:
        log.error(f"Error in financial calculations: {e}", exc_info=True)
        print(f"Error: {e}")
        return

if __name__ == '__main__':
    main()
