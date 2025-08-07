#!/usr/bin/env python3
"""
Category Completion Status Calculator
=====================================

Surgical precision implementation for fixing category completion tracking.
This script generates the exact category_completion_status object needed by the system.

FIXES THESE ISSUES:
1. total_categories: 1 → 185 (correct count from poundwholesale_categories.json)
2. category_completion_status: {} → Complete object with real percentages
3. Determines "last analyze url" (category with least progress)

ALGORITHM:
1. Load product cache (2387 products) - source of truth for total products per category
2. Load linking map (2115 products) - tracks processed products per category  
3. Load category URLs (185 categories) - all available categories
4. Match products to categories using source_url from cache data
5. Calculate completion percentage: (processed/total) * 100 per category
6. Find category with lowest completion percentage for next processing
"""

import json
import os
from typing import Dict, Tuple, Optional
from collections import defaultdict


def load_data_sources(base_path: str) -> Tuple[list, list, list]:
    """Load all three data sources with error handling"""
    
    # Load categories
    config_path = os.path.join(base_path, "config", "poundwholesale_categories.json")
    with open(config_path, 'r') as f:
        categories_data = json.load(f)
        categories = categories_data['category_urls']
    
    # Load product cache
    cache_path = os.path.join(base_path, "OUTPUTS", "cached_products", "poundwholesale-co-uk_products_cache.json")
    with open(cache_path, 'r') as f:
        product_cache = json.load(f)
    
    # Load linking map
    linking_path = os.path.join(base_path, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "poundwholesale.co.uk", "linking_map.json")
    with open(linking_path, 'r') as f:
        linking_map = json.load(f)
    
    return categories, product_cache, linking_map


def map_cache_products_to_categories(product_cache: list, categories: list) -> Dict[str, int]:
    """Map products from cache to categories (total products per category)"""
    category_totals = defaultdict(int)
    
    for product in product_cache:
        source_url = product.get('source_url')
        if source_url and source_url in categories:
            category_totals[source_url] += 1
    
    return dict(category_totals)


def map_linking_products_to_categories(linking_map: list, product_cache: list, categories: list) -> Dict[str, int]:
    """Map products from linking map to categories (processed products per category)"""
    category_processed = defaultdict(int)
    
    # Create lookup map from product URL to category
    url_to_category = {}
    for product in product_cache:
        product_url = product.get('url')
        source_url = product.get('source_url')
        if product_url and source_url and source_url in categories:
            url_to_category[product_url] = source_url
    
    # Count processed products per category
    for link_entry in linking_map:
        supplier_url = link_entry.get('supplier_url')
        if supplier_url and supplier_url in url_to_category:
            category = url_to_category[supplier_url]
            category_processed[category] += 1
    
    return dict(category_processed)


def calculate_category_completion_status(categories: list, category_totals: Dict[str, int], category_processed: Dict[str, int]) -> Dict[str, Dict]:
    """Calculate completion status for all categories"""
    category_completion_status = {}
    
    for category in categories:
        total_products = category_totals.get(category, 0)
        processed_products = category_processed.get(category, 0)
        
        if total_products > 0:
            completion_percentage = round((processed_products / total_products) * 100, 2)
        else:
            completion_percentage = 0.0
        
        category_completion_status[category] = {
            'total_products': total_products,
            'processed_products': processed_products, 
            'completion_percentage': completion_percentage,
            'remaining_products': total_products - processed_products
        }
    
    return category_completion_status


def find_next_category_to_analyze(category_completion_status: Dict[str, Dict]) -> Optional[str]:
    """Find category with lowest completion percentage (next to analyze)"""
    
    # Filter to categories that have products and are not 100% complete
    incomplete_categories = {
        cat: data for cat, data in category_completion_status.items()
        if data['total_products'] > 0 and data['completion_percentage'] < 100
    }
    
    if not incomplete_categories:
        return None
    
    # Sort by completion percentage (ascending), then by remaining products (descending)
    # This prioritizes categories with 0% completion first, then those with most remaining work
    next_category = min(
        incomplete_categories.items(),
        key=lambda x: (x[1]['completion_percentage'], -x[1]['remaining_products'])
    )[0]
    
    return next_category


def get_category_completion_status(base_path: str = None) -> Dict:
    """
    Main function to generate category completion status
    
    Returns:
        Dict with exact format needed by the system:
        {
            'total_categories': int,
            'category_completion_status': dict,
            'last_analyze_url': str
        }
    """
    
    if base_path is None:
        base_path = "/mnt/c/Users/chris/Desktop/Amazon-FBA-Agent-System-v32 - latest good - Copy (3)"
    
    # Load all data sources
    categories, product_cache, linking_map = load_data_sources(base_path)
    
    # Map products to categories
    category_totals = map_cache_products_to_categories(product_cache, categories)
    category_processed = map_linking_products_to_categories(linking_map, product_cache, categories)
    
    # Calculate completion status
    category_completion_status = calculate_category_completion_status(
        categories, category_totals, category_processed
    )
    
    # Find next category to analyze
    last_analyze_url = find_next_category_to_analyze(category_completion_status)
    
    return {
        'total_categories': len(categories),
        'category_completion_status': category_completion_status,
        'last_analyze_url': last_analyze_url
    }


def print_summary(result: Dict):
    """Print a summary of the analysis results"""
    print("🎯 CATEGORY COMPLETION STATUS SUMMARY")
    print("="*50)
    print(f"Total Categories: {result['total_categories']}")
    print(f"Category Completion Status Entries: {len(result['category_completion_status'])}")
    print(f"Next Category to Analyze: {result['last_analyze_url']}")
    
    # Count categories by status
    active_categories = 0
    completed_categories = 0
    for category, status in result['category_completion_status'].items():
        if status['total_products'] > 0:
            active_categories += 1
            if status['completion_percentage'] == 100:
                completed_categories += 1
    
    print(f"Active Categories (with products): {active_categories}")
    print(f"Completed Categories: {completed_categories}")
    print(f"Categories Never Scraped: {result['total_categories'] - active_categories}")
    
    # Calculate overall completion
    total_products = sum(status['total_products'] for status in result['category_completion_status'].values())
    total_processed = sum(status['processed_products'] for status in result['category_completion_status'].values())
    overall_completion = round((total_processed / total_products * 100), 2) if total_products > 0 else 0
    
    print(f"Overall Completion: {overall_completion}% ({total_processed:,}/{total_products:,})")


if __name__ == "__main__":
    # Generate the results
    result = get_category_completion_status()
    
    # Print summary
    print_summary(result)
    
    # Save results for system integration
    output_path = "/mnt/c/Users/chris/Desktop/Amazon-FBA-Agent-System-v32 - latest good - Copy (3)/OUTPUTS/system_category_completion.json"
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_path}")
    print("\n✅ Category completion status calculation COMPLETE!")