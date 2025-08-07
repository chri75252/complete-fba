#!/usr/bin/env python3
"""
Category Completion Analyzer
Diagnoses why certain categories are missing from progress tracking
"""

import os
import json
from collections import defaultdict
from urllib.parse import urlparse

def analyze_category_tracking_issue():
    """Analyze why categories are missing from progress tracking"""
    print("🔍 CATEGORY COMPLETION TRACKING ANALYSIS")
    print("=" * 60)
    
    # File paths
    product_cache_path = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
    linking_map_path = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
    config_path = "config/poundwholesale_categories.json"
    
    # Load files
    try:
        print("📂 Loading files...")
        
        # Load product cache
        if os.path.exists(product_cache_path):
            with open(product_cache_path, 'r', encoding='utf-8') as f:
                product_cache = json.load(f)
            print(f"✅ Product cache: {len(product_cache):,} entries")
        else:
            print("❌ Product cache file not found")
            return
        
        # Load linking map
        if os.path.exists(linking_map_path):
            with open(linking_map_path, 'r', encoding='utf-8') as f:
                linking_map = json.load(f)
            print(f"✅ Linking map: {len(linking_map):,} entries")
        else:
            print("❌ Linking map file not found")
            return
        
        # Load category config
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                category_config = json.load(f)
            category_urls = category_config.get('category_urls', [])
            print(f"✅ Category config: {len(category_urls):,} URLs")
        else:
            print("❌ Category config file not found")
            category_urls = []
        
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return
    
    # Analyze specific missing category
    missing_category = "https://www.poundwholesale.co.uk/stationery/wholesale-pens-pencils-markers"
    example_product = "https://www.poundwholesale.co.uk/4-permanant-markers-chisel-tip-b-c"
    
    print(f"\n🎯 ANALYZING MISSING CATEGORY:")
    print(f"Category: {missing_category}")
    print(f"Example Product: {example_product}")
    
    # Check if category is in config
    if missing_category in category_urls:
        print("✅ Category IS in config file")
    else:
        print("❌ Category NOT in config file")
        # Check for similar URLs
        similar_urls = [url for url in category_urls if "pens-pencils" in url or "stationery" in url]
        if similar_urls:
            print(f"🔍 Similar URLs found: {similar_urls}")
    
    # Check if example product exists in cache
    example_found = False
    example_product_data = None
    for product in product_cache:
        if product.get('url') == example_product:
            example_found = True
            example_product_data = product
            break
    
    if example_found:
        print("✅ Example product IS in product cache")
        print(f"   Product data: {json.dumps(example_product_data, indent=2)}")
        
        # Check source_url
        source_url = example_product_data.get('source_url', '')
        if source_url:
            print(f"✅ Product has source_url: {source_url}")
            if source_url == missing_category:
                print("✅ source_url matches expected category")
            else:
                print(f"⚠️ source_url MISMATCH: expected {missing_category}, got {source_url}")
        else:
            print("❌ Product has NO source_url field")
    else:
        print("❌ Example product NOT in product cache")
    
    # Check if product is in linking map
    example_in_linking = False
    for entry in linking_map:
        if entry.get('supplier_url') == example_product:
            example_in_linking = True
            print("✅ Example product IS in linking map")
            print(f"   Linking entry: {json.dumps(entry, indent=2)}")
            break
    
    if not example_in_linking:
        print("❌ Example product NOT in linking map")
    
    # Analyze source_url patterns in cache
    print(f"\n📊 SOURCE_URL ANALYSIS:")
    source_url_counts = defaultdict(int)
    missing_source_url = 0
    
    for product in product_cache:
        source_url = product.get('source_url', '')
        if source_url:
            source_url_counts[source_url] += 1
        else:
            missing_source_url += 1
    
    print(f"Products with source_url: {len(product_cache) - missing_source_url:,}")
    print(f"Products WITHOUT source_url: {missing_source_url:,}")
    
    if missing_source_url > 0:
        print(f"⚠️ {missing_source_url} products missing source_url - this causes tracking issues!")
    
    # Show top categories by product count
    print(f"\n📈 TOP CATEGORIES BY PRODUCT COUNT:")
    sorted_categories = sorted(source_url_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories[:10]):
        print(f"{i+1:2d}. {count:3d} products: {category}")
    
    # Check if missing category appears in source_urls
    if missing_category in source_url_counts:
        count = source_url_counts[missing_category]
        print(f"\n✅ Missing category FOUND in source_urls: {count} products")
    else:
        print(f"\n❌ Missing category NOT FOUND in source_urls")
        # Check for partial matches
        partial_matches = {url: count for url, count in source_url_counts.items() 
                          if "pens-pencils" in url or "stationery" in url}
        if partial_matches:
            print(f"🔍 Partial matches found:")
            for url, count in partial_matches.items():
                print(f"   {count} products: {url}")
    
    # Analyze linking map coverage
    print(f"\n🔗 LINKING MAP COVERAGE ANALYSIS:")
    processed_urls = set(entry.get('supplier_url', '') for entry in linking_map if entry.get('supplier_url'))
    
    category_totals = defaultdict(int)
    category_processed = defaultdict(int)
    
    for product in product_cache:
        source_url = product.get('source_url', '')
        product_url = product.get('url', '')
        
        if source_url:
            category_totals[source_url] += 1
            if product_url in processed_urls:
                category_processed[source_url] += 1
    
    # Show categories with processing status
    print(f"\nCATEGORIES WITH PROCESSED PRODUCTS:")
    processed_categories = {url: {"total": category_totals[url], "processed": category_processed[url]} 
                           for url in category_totals if category_processed[url] > 0}
    
    for category, stats in sorted(processed_categories.items(), key=lambda x: x[1]["processed"], reverse=True)[:10]:
        total = stats["total"]
        processed = stats["processed"]
        percent = (processed / total * 100) if total > 0 else 0
        print(f"{processed:3d}/{total:3d} ({percent:5.1f}%): {category}")
    
    # Check why missing category isn't showing
    if missing_category in category_totals:
        total = category_totals[missing_category]
        processed = category_processed[missing_category]
        percent = (processed / total * 100) if total > 0 else 0
        print(f"\n🎯 MISSING CATEGORY STATUS:")
        print(f"Total products: {total}")
        print(f"Processed products: {processed}")
        print(f"Completion: {percent:.1f}%")
        
        if processed == 0:
            print("❌ REASON: No products from this category have been processed yet")
            print("   This is why it doesn't appear in progress tracking")
        else:
            print("✅ Category should appear in progress tracking")
    else:
        print(f"\n❌ MISSING CATEGORY NOT FOUND in totals - source_url issue")

def check_source_url_integrity():
    """Check integrity of source_url fields in product cache"""
    print(f"\n🔍 SOURCE_URL INTEGRITY CHECK")
    print("-" * 40)
    
    product_cache_path = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
    
    if not os.path.exists(product_cache_path):
        print("❌ Product cache file not found")
        return
    
    with open(product_cache_path, 'r', encoding='utf-8') as f:
        product_cache = json.load(f)
    
    # Analyze source_url patterns
    issues = {
        "missing_source_url": [],
        "invalid_source_url": [],
        "mismatched_domain": []
    }
    
    for i, product in enumerate(product_cache):
        product_url = product.get('url', '')
        source_url = product.get('source_url', '')
        
        # Check for missing source_url
        if not source_url:
            issues["missing_source_url"].append({
                "index": i,
                "url": product_url,
                "title": product.get('title', '')[:50]
            })
            continue
        
        # Check for invalid source_url format
        if not source_url.startswith('http'):
            issues["invalid_source_url"].append({
                "index": i,
                "url": product_url,
                "source_url": source_url
            })
            continue
        
        # Check domain consistency
        try:
            product_domain = urlparse(product_url).netloc
            source_domain = urlparse(source_url).netloc
            
            if product_domain != source_domain:
                issues["mismatched_domain"].append({
                    "index": i,
                    "product_url": product_url,
                    "source_url": source_url,
                    "product_domain": product_domain,
                    "source_domain": source_domain
                })
        except Exception as e:
            issues["invalid_source_url"].append({
                "index": i,
                "url": product_url,
                "source_url": source_url,
                "error": str(e)
            })
    
    # Report issues
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    print(f"Total products analyzed: {len(product_cache):,}")
    print(f"Total issues found: {total_issues:,}")
    
    for issue_type, issue_list in issues.items():
        if issue_list:
            print(f"\n❌ {issue_type.upper()}: {len(issue_list)} products")
            # Show first 5 examples
            for issue in issue_list[:5]:
                if issue_type == "missing_source_url":
                    print(f"   [{issue['index']}] {issue['url']} - {issue['title']}")
                elif issue_type == "invalid_source_url":
                    print(f"   [{issue['index']}] {issue['url']} -> {issue['source_url']}")
                elif issue_type == "mismatched_domain":
                    print(f"   [{issue['index']}] {issue['product_domain']} vs {issue['source_domain']}")
            
            if len(issue_list) > 5:
                print(f"   ... and {len(issue_list) - 5} more")
    
    if total_issues == 0:
        print("✅ All source_url fields are valid")
    
    return issues

def save_analysis_results(analysis_data, output_path="category_analysis_results.json"):
    """Save analysis results to JSON file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"💾 Analysis saved to: {output_path}")
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")

if __name__ == "__main__":
    print("🚀 Starting Category Completion Analysis")
    print(f"Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run main analysis
    analyze_category_tracking_issue()
    
    # Check source_url integrity
    source_url_issues = check_source_url_integrity()
    
    # Final recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("1. Check if missing categories have products with correct source_url")
    print("2. Verify that products from missing categories have been processed (in linking map)")
    print("3. If source_url is missing/incorrect, this explains why categories don't appear")
    print("4. Categories only appear in progress tracking if they have processed products")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Fix any source_url integrity issues found above")
    print("2. Ensure products are properly tagged with their source category")
    print("3. Verify linking map entries have correct supplier_url values")
    print("4. Re-run system to see if missing categories now appear")