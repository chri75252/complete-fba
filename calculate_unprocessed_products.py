#!/usr/bin/env python3
"""
Calculate Unprocessed Products - Find the actual difference between supplier cache and linking map
This script will identify which products still need Amazon analysis
"""

import json
import os
from pathlib import Path

def load_supplier_cache():
    """Load the supplier product cache"""
    cache_patterns = [
        "OUTPUTS/FBA_ANALYSIS/supplier_cache/poundwholesale.co.uk/poundwholesale-co-uk_products_cache.json",
        "OUTPUTS/FBA_ANALYSIS/supplier_cache/poundwholesale_co_uk_products_cache.json",
        "OUTPUTS/FBA_ANALYSIS/poundwholesale_co_uk_products_cache.json"
    ]
    
    for pattern in cache_patterns:
        if os.path.exists(pattern):
            print(f"✅ Found supplier cache: {pattern}")
            with open(pattern, 'r', encoding='utf-8') as f:
                products = json.load(f)
            print(f"📊 Loaded {len(products)} products from supplier cache")
            return products
    
    print("❌ No supplier cache file found!")
    return []

def load_linking_map():
    """Load the current linking map"""
    linking_patterns = [
        "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json",
        "OUTPUTS/FBA_ANALYSIS/poundwholesale-co-uk_linking_map.json",
        "OUTPUTS/FBA_ANALYSIS/poundwholesale_co_uk_linking_map.json"
    ]
    
    for pattern in linking_patterns:
        if os.path.exists(pattern):
            print(f"✅ Found linking map: {pattern}")
            with open(pattern, 'r', encoding='utf-8') as f:
                linking_data = json.load(f)
            print(f"📊 Loaded {len(linking_data)} entries from linking map")
            return linking_data
    
    print("❌ No linking map file found!")
    return []

def create_processed_lookup(linking_map):
    """Create lookup sets for fast checking"""
    processed_eans = set()
    processed_urls = set()
    
    for entry in linking_map:
        # Add EAN if present
        ean = entry.get('supplier_ean') or entry.get('ean')
        if ean:
            processed_eans.add(ean)
        
        # Add URL if present
        url = entry.get('supplier_url') or entry.get('url')
        if url:
            processed_urls.add(url)
    
    print(f"📋 Created lookup: {len(processed_eans)} EANs, {len(processed_urls)} URLs")
    return processed_eans, processed_urls

def find_unprocessed_products(supplier_products, processed_eans, processed_urls):
    """Find products that haven't been processed yet"""
    unprocessed = []
    
    for i, product in enumerate(supplier_products):
        product_ean = product.get('ean') or product.get('EAN')
        product_url = product.get('url') or product.get('source_url')
        
        # Check if this product is already processed
        is_processed = False
        
        if product_ean and product_ean in processed_eans:
            is_processed = True
        elif product_url and product_url in processed_urls:
            is_processed = True
        
        if not is_processed:
            unprocessed.append({
                'index': i,
                'product': product,
                'ean': product_ean,
                'url': product_url,
                'title': product.get('title', 'Unknown')
            })
    
    return unprocessed

def main():
    print("🔍 CALCULATING UNPROCESSED PRODUCTS...")
    print("=" * 60)
    
    # Load data
    supplier_products = load_supplier_cache()
    linking_map = load_linking_map()
    
    if not supplier_products:
        print("❌ Cannot proceed without supplier cache")
        return
    
    # Create lookup for fast checking
    processed_eans, processed_urls = create_processed_lookup(linking_map)
    
    # Find unprocessed products
    unprocessed = find_unprocessed_products(supplier_products, processed_eans, processed_urls)
    
    print("\n📊 ANALYSIS RESULTS:")
    print("=" * 60)
    print(f"Total supplier products: {len(supplier_products)}")
    print(f"Total linking map entries: {len(linking_map)}")
    print(f"Unprocessed products: {len(unprocessed)}")
    print(f"Processing efficiency: {((len(supplier_products) - len(unprocessed)) / len(supplier_products) * 100):.1f}%")
    
    if unprocessed:
        print(f"\n🎯 UNPROCESSED PRODUCTS (showing first 10):")
        print("-" * 60)
        for i, item in enumerate(unprocessed[:10]):
            print(f"{i+1:3d}. Index {item['index']:4d}: {item['title'][:50]}...")
            print(f"     EAN: {item['ean'] or 'None'}")
            print(f"     URL: {item['url'][:80] if item['url'] else 'None'}...")
            print()
        
        if len(unprocessed) > 10:
            print(f"... and {len(unprocessed) - 10} more products")
    
    # Save unprocessed products for targeted processing
    if unprocessed:
        unprocessed_file = "unprocessed_products_for_analysis.json"
        unprocessed_data = [item['product'] for item in unprocessed]
        
        with open(unprocessed_file, 'w', encoding='utf-8') as f:
            json.dump(unprocessed_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(unprocessed_data)} unprocessed products to: {unprocessed_file}")
        
        # Also save the indices for reference
        indices_file = "unprocessed_product_indices.json"
        indices_data = {
            'total_products': len(supplier_products),
            'unprocessed_count': len(unprocessed),
            'unprocessed_indices': [item['index'] for item in unprocessed],
            'first_unprocessed_index': unprocessed[0]['index'] if unprocessed else None,
            'last_unprocessed_index': unprocessed[-1]['index'] if unprocessed else None
        }
        
        with open(indices_file, 'w', encoding='utf-8') as f:
            json.dump(indices_data, f, indent=2)
        
        print(f"💾 Saved indices information to: {indices_file}")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Use the unprocessed_products_for_analysis.json file for targeted processing")
        print("2. Set last_processed_index to start from the right position")
        print("3. Process only the unprocessed products to save time")
    else:
        print("\n✅ All products have been processed!")

if __name__ == "__main__":
    main()