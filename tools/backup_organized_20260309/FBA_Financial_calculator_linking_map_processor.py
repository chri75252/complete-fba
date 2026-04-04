"""
FBA Financial Calculator - Linking Map Processor
Processes the linking map directly (like the system workflow does) to generate
a complete financial report with all matched products.
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

def find_amazon_json_by_asin(asin, ean=None):
    """Find Amazon JSON data by ASIN, with optional EAN for enhanced filename matching."""
    if not asin:
        return None

    if ean:
        ean_filename = f"amazon_{asin}_{ean}.json"
        ean_path = os.path.join(AMAZON_SCRAPE_DIR, ean_filename)
        if os.path.exists(ean_path):
            try:
                with open(ean_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                log.error(f"Error reading {ean_filename}: {e}")

    standard_filename = f"amazon_{asin}.json"
    standard_path = os.path.join(AMAZON_SCRAPE_DIR, standard_filename)
    if os.path.exists(standard_path):
        try:
            with open(standard_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log.error(f"Error reading {standard_filename}: {e}")

    for fname in os.listdir(AMAZON_SCRAPE_DIR):
        if asin in fname and fname.endswith('.json'):
            try:
                with open(os.path.join(AMAZON_SCRAPE_DIR, fname), 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                log.error(f"Error reading {fname}: {e}")
                continue

    return None

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
        log.warning(f"WARNING: No price found in Amazon data for {amazon.get('asin_queried', 'unknown ASIN')}")
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

def run_calculations_from_linking_map(supplier_name):
    """
    Process the linking map directly (like the system workflow does).

    Args:
        supplier_name: Supplier identifier for supplier-specific paths (REQUIRED)

    Returns:
        dict: Results containing DataFrame, statistics, and file path
    """
    if not supplier_name:
        raise ValueError("supplier_name is required")

    supplier_paths = get_supplier_specific_paths(supplier_name)

    # Paths - FIX: supplier_cache no longer needed
    linking_map_path = supplier_paths['linking_map']
    out_dir = supplier_paths['financial_reports_dir']

    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading linking map from: {linking_map_path}")
    print(f"Using Amazon data from: {AMAZON_SCRAPE_DIR}")
    print(f"Output will be saved to: {out_dir}")

    # Load linking map
    try:
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Error reading linking map: {e}")

    print(f"Loaded {len(linking_map)} entries from linking map")

    # FIX: Removed supplier cache dependency - linking map entries already contain all supplier data
    # (supplier_ean, supplier_title, supplier_price, supplier_url)
    print(f"Using linking map as primary data source (no supplier cache required)")

    records = []
    processed = 0
    found_matches = 0

    print(f"Processing {len(linking_map)} entries from the linking map...")

    for link_entry in linking_map:
        ean = link_entry.get('supplier_ean')
        asin = link_entry.get('amazon_asin')

        if not ean or not asin:
            continue

        processed += 1

        # FIX: Get supplier data DIRECTLY from linking map entry (no cache lookup needed)
        supplier_price = 0
        if link_entry.get('supplier_price') is not None:
            try:
                supplier_price = float(link_entry['supplier_price'])
            except (ValueError, TypeError):
                pass
        
        supplier_title = link_entry.get('supplier_title', 'N/A')
        supplier_url = link_entry.get('supplier_url', '')

        # Find Amazon data
        amazon = find_amazon_json_by_asin(asin, ean)

        if not amazon:
            if processed % 100 == 0:
                print(f"Processed {processed}/{len(linking_map)} - No Amazon data for: EAN={ean}, ASIN={asin}")
            continue

        found_matches += 1

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

        if not price:
            log.warning(f"NO PRICE DATA: EAN={ean}, ASIN={asin}")
            continue

        # Build URL
        amazon_url = amazon.get('url')
        if not amazon_url and 'asin_queried' in amazon:
            amazon_url = f"https://www.amazon.co.uk/dp/{amazon['asin_queried']}"

        amazon_title = amazon.get('title', amazon.get('product_title', link_entry.get('amazon_title', 'N/A')))

        row = {
            'EAN': ean,
            'EAN_OnPage': amazon.get('ean_on_page'),
            'ASIN': asin,
            'SupplierTitle': supplier_title,
            'AmazonTitle': amazon_title,
            'SupplierURL': supplier_url,
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

        if found_matches % 500 == 0:
            print(f"Found {found_matches} matches so far...")

    if not records:
        raise Exception("No matching records found. Check file paths and data consistency.")

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
        'linking_map_total': len(linking_map)
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
        results = run_calculations_from_linking_map(supplier_name)

        if not results:
            print("\nNo results generated.")
            return

        df = results['dataframe']
        stats = results['statistics']

        print(f"\n{'='*60}")
        print(f"Linking Map Financial Report Generated")
        print(f"{'='*60}")
        print(f"Linking map entries: {stats['linking_map_total']}")
        print(f"Processed: {stats['processed']}")
        print(f"Found Amazon matches: {stats['found_matches']}")
        print(f"Generated calculations: {stats['generated_calculations']}")
        print(f"\nFinancial report saved to:")
        print(f"  {stats['output_file']}")

        if 'ROI' in df.columns:
            print(f"\n{'='*60}")
            print(f"Top 5 items by ROI:")
            print(f"{'='*60}")
            print(df.head(5)[['ASIN', 'EAN', 'SupplierTitle', 'ROI', 'NetProfit', 'SellingPrice_incVAT', 'SupplierPrice_incVAT']].to_string())

            print(f"\n{'='*60}")
            print(f"Profitability breakdown:")
            print(f"{'='*60}")
            print(f"  - Good ROI (>30%): {stats.get('profitable_count', 0)} items")
            print(f"  - Marginal (0-30%): {stats.get('marginal_count', 0)} items")
            print(f"  - Unprofitable: {stats.get('unprofitable_count', 0)} items")
            print(f"{'='*60}\n")

    except Exception as e:
        log.error(f"Error in financial calculations: {e}", exc_info=True)
        print(f"Error: {e}")
        return

if __name__ == '__main__':
    main()
