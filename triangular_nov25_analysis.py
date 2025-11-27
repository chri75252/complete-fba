"""
Triangular Protocol Analysis: Nov 25 Logs (401 vs 397 discrepancy)
Focus: Unchanged cache/linking_map between runs
"""
import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent

def extract_log_metrics(log_path, search_phrase="All-Baby-and-child"):
    """Extract key metrics from log file"""
    metrics = {
        'denominators': [],
        'resume_pointers': [],
        'cache_counts': [],
        'skip_counts': [],
        'amazon_extractions': []
    }

    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if search_phrase not in line:
                    continue

                # Extract denominators from various log patterns
                if 'total=' in line:
                    match = re.search(r'total=(\d+)', line)
                    if match:
                        metrics['denominators'].append(int(match.group(1)))

                # Extract resume pointers
                if 'ptr=' in line or 'product:' in line:
                    match = re.search(r'(?:ptr=|product:\s*)(\d+)', line)
                    if match:
                        metrics['resume_pointers'].append(int(match.group(1)))

                # Extract cache counts
                if 'cached=' in line:
                    match = re.search(r'cached=(\d+)', line)
                    if match:
                        metrics['cache_counts'].append(int(match.group(1)))

                # Extract skip counts
                if 'skip=' in line:
                    match = re.search(r'skip=(\d+)', line)
                    if match:
                        metrics['skip_counts'].append(int(match.group(1)))

                # Detect Amazon extraction events
                if 'Extracting Amazon' in line or 'AMAZON EXTRACT' in line:
                    metrics['amazon_extractions'].append(line.strip())

    except Exception as e:
        print(f"Error reading {log_path}: {e}")

    return metrics

def count_cache_products(category_url):
    """Count products in cache for specific category"""
    cache_path = BASE_DIR / "OUTPUTS" / "cached_products" / "angelwholesale-co-uk_products_cache.json"

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Cache is a list of products
        matching = [p for p in cache_data if p.get('source_url') == category_url]

        return len(cache_data), len(matching), [p.get('url') for p in matching[:5]]
    except Exception as e:
        return 0, 0, [f"Error: {e}"]

def count_linking_map_entries(category_url):
    """Count linking map entries for category"""
    linking_map_path = BASE_DIR / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / "angelwholesale.co.uk" / "linking_map.json"
    manifest_path = BASE_DIR / "OUTPUTS" / "manifests" / "angelwholesale.co.uk" / "angelwholesale.co.uk_Category_All-Baby-and-child_manifest.json"

    try:
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # Get manifest URLs
        manifest_urls = set(manifest.get('product_urls', []))

        # Count linking map entries that match manifest
        matched = sum(1 for entry in linking_map if entry.get('supplier_url') in manifest_urls)

        return len(linking_map), matched, len(manifest_urls)
    except Exception as e:
        return 0, 0, 0

def check_reprocessing(log1_path, log2_path):
    """Check if same ASINs were extracted in both logs"""
    def extract_asins(log_path):
        asins = set()
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Look for ASIN patterns
                    matches = re.findall(r'(?:asin|ASIN)[:\s]+([A-Z0-9]{10})', line)
                    asins.update(matches)
        except:
            pass
        return asins

    asins1 = extract_asins(log1_path)
    asins2 = extract_asins(log2_path)

    duplicates = asins1 & asins2

    return len(asins1), len(asins2), len(duplicates), list(duplicates)[:10]

def main():
    print("="*80)
    print("TRIANGULAR PROTOCOL ANALYSIS: NOV 25 LOGS")
    print("="*80)
    print()

    # Configuration
    LOG1 = BASE_DIR / "logs" / "debug" / "run_custom_poundwholesale_20251125_154127.log"
    LOG2 = BASE_DIR / "logs" / "debug" / "run_custom_poundwholesale_20251125_155617.log"
    CATEGORY_URL = "https://angelwholesale.co.uk/Category/All-Baby-and-child"

    print("TARGET: All-Baby-and-child category")
    print(f"LOG 1 (First run): {LOG1.name}")
    print(f"LOG 2 (Resume run): {LOG2.name}")
    print()

    # SOURCE 1: Actual File Counts
    print("-"*80)
    print("SOURCE 1: ACTUAL FILE COUNTS (Ground Truth)")
    print("-"*80)

    total_cache, cat_cache, sample_cache = count_cache_products(CATEGORY_URL)
    total_links, matched_links, manifest_count = count_linking_map_entries(CATEGORY_URL)

    print(f"Cache file:")
    print(f"  Total products: {total_cache}")
    print(f"  For target category: {cat_cache}")
    print(f"  Sample URLs: {sample_cache[:3]}")
    print()

    print(f"Linking map:")
    print(f"  Total entries: {total_links}")
    print(f"  Matching manifest: {matched_links}")
    print()

    print(f"Manifest:")
    print(f"  Total URLs: {manifest_count}")
    print()

    print(f"INVARIANT CHECK:")
    expected_remaining = manifest_count - matched_links - cat_cache
    print(f"  {manifest_count} (manifest) = {matched_links} (skip) + {cat_cache} (cached) + {expected_remaining} (remaining)")
    print(f"  Sum: {matched_links + cat_cache + expected_remaining} == {manifest_count}? {matched_links + cat_cache + expected_remaining == manifest_count}")
    print()

    # SOURCE 2: First Run Log Claims
    print("-"*80)
    print("SOURCE 2: FIRST RUN LOG (154127)")
    print("-"*80)

    metrics1 = extract_log_metrics(LOG1)
    print(f"Denominators found: {metrics1['denominators']}")
    print(f"Resume pointers: {metrics1['resume_pointers']}")
    print(f"Cache counts: {metrics1['cache_counts']}")
    print(f"Skip counts: {metrics1['skip_counts']}")
    print(f"Amazon extractions: {len(metrics1['amazon_extractions'])}")
    print()

    # SOURCE 3: Resume Run Log Claims
    print("-"*80)
    print("SOURCE 3: RESUME RUN LOG (155617)")
    print("-"*80)

    metrics2 = extract_log_metrics(LOG2)
    print(f"Denominators found: {metrics2['denominators']}")
    print(f"Resume pointers: {metrics2['resume_pointers']}")
    print(f"Cache counts: {metrics2['cache_counts']}")
    print(f"Skip counts: {metrics2['skip_counts']}")
    print(f"Amazon extractions: {len(metrics2['amazon_extractions'])}")
    print()

    # CROSS-VERIFICATION
    print("="*80)
    print("CROSS-VERIFICATION: Claims vs Reality")
    print("="*80)
    print()

    # Check denominator discrepancy
    if metrics1['denominators'] and metrics2['denominators']:
        denom1 = metrics1['denominators'][-1]
        denom2 = metrics2['denominators'][-1]

        print(f"DENOMINATOR SHIFT:")
        print(f"  First run claimed: {denom1}")
        print(f"  Resume run claimed: {denom2}")
        print(f"  Actual manifest count: {manifest_count}")
        print(f"  Discrepancy: {abs(denom1 - denom2)} products")
        print()

        if denom1 != manifest_count:
            print(f"  WARNING: First run denominator {denom1} != manifest {manifest_count}")
        if denom2 != manifest_count:
            print(f"  ERROR: Resume run denominator {denom2} != manifest {manifest_count}")
            print(f"         This causes 4 products to be lost!")
        print()

    # Check cache count accuracy
    if metrics1['cache_counts'] and metrics2['cache_counts']:
        cache1 = metrics1['cache_counts'][-1]
        cache2 = metrics2['cache_counts'][-1]

        print(f"CACHE COUNT CLAIMS:")
        print(f"  First run claimed: {cache1}")
        print(f"  Resume run claimed: {cache2}")
        print(f"  Actual cache count: {cat_cache}")
        print()

        if cache1 != cat_cache:
            print(f"  ERROR: First run claimed {cache1} but actual is {cat_cache}")
        if cache2 != cat_cache:
            print(f"  ERROR: Resume run claimed {cache2} but actual is {cat_cache}")
        print()

    # Check for reprocessing
    print("-"*80)
    print("REPROCESSING DETECTION")
    print("-"*80)

    asins1, asins2, duplicates, sample_dups = check_reprocessing(LOG1, LOG2)

    print(f"ASINs extracted:")
    print(f"  First run: {asins1} unique ASINs")
    print(f"  Resume run: {asins2} unique ASINs")
    print(f"  Duplicates: {duplicates} ASINs")
    print()

    if duplicates > 0:
        print(f"  WARNING: {duplicates} ASINs were reprocessed!")
        print(f"  Sample duplicates: {sample_dups[:5]}")
        print()

    # ROOT CAUSE SUMMARY
    print("="*80)
    print("ROOT CAUSE ANALYSIS")
    print("="*80)
    print()

    print("ISSUE 1: Denominator Mismatch (401 -> 397)")
    print("  Observation: First run uses 401, resume uses 397")
    print("  Impact: 4 products are lost in transition")
    print("  Likely cause: Filtering logic differs between initial and resume")
    print()

    print("ISSUE 2: Cache Count Variation")
    if metrics1['cache_counts'] and metrics2['cache_counts']:
        print(f"  Observation: Cache count changes from {metrics1['cache_counts'][-1]} to {metrics2['cache_counts'][-1]}")
        print(f"  Actual cache: {cat_cache}")
        print("  Impact: Incorrect resume pointer calculation")
        print("  Likely cause: URL matching inconsistency")
    print()

    print("ISSUE 3: Amazon Reprocessing")
    if duplicates > 0:
        reprocess_pct = (duplicates / max(asins1, 1)) * 100
        print(f"  Observation: {duplicates} ASINs ({reprocess_pct:.1f}%) were extracted twice")
        print("  Impact: Wasted API calls and time")
        print("  Likely cause: Resume pointer doesn't align with processed products")
    print()

    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
