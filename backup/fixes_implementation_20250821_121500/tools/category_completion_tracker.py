#!/usr/bin/env python3
"""
Category Completion Tracker - Integration Module
===============================================

Simple integration module for getting category completion status.
Can be imported into other scripts for real-time completion tracking.

Usage:
    from tools.category_completion_tracker import get_completion_metrics
    
    metrics = get_completion_metrics()
    print(f"Total categories: {metrics['total_categories']}")
    print(f"Next URL: {metrics['last_analyze_url']}")
"""

import json
import os
from typing import Dict, Optional
from collections import defaultdict


def get_completion_metrics(base_path: str = None) -> Dict:
    """
    Get category completion metrics for system integration
    
    Args:
        base_path: Base path to the project directory
        
    Returns:
        Dict containing:
        - total_categories: Total number of categories (185)
        - category_completion_status: Complete status for all categories
        - last_analyze_url: Next category to process (lowest completion)
    """
    
    if base_path is None:
        # Auto-detect base path from current script location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(current_dir)  # Go up one level from tools/
    
    try:
        # Load categories
        config_path = os.path.join(base_path, "config", "poundwholesale_categories.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            categories = json.load(f)['category_urls']
        
        # Load product cache
        cache_path = os.path.join(base_path, "OUTPUTS", "cached_products", "poundwholesale-co-uk_products_cache.json")
        with open(cache_path, 'r', encoding='utf-8') as f:
            product_cache = json.load(f)
        
        # Load linking map
        linking_path = os.path.join(base_path, "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "poundwholesale.co.uk", "linking_map.json")
        with open(linking_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
        
        # Calculate totals per category
        category_totals = defaultdict(int)
        for product in product_cache:
            source_url = product.get('source_url')
            if source_url and source_url in categories:
                category_totals[source_url] += 1
        
        # Calculate processed per category
        category_processed = defaultdict(int)
        url_to_category = {}
        for product in product_cache:
            product_url = product.get('url')
            source_url = product.get('source_url')
            if product_url and source_url and source_url in categories:
                url_to_category[product_url] = source_url
        
        for link_entry in linking_map:
            supplier_url = link_entry.get('supplier_url')
            if supplier_url and supplier_url in url_to_category:
                category = url_to_category[supplier_url]
                category_processed[category] += 1
        
        # Build completion status
        category_completion_status = {}
        for category in categories:
            total = category_totals.get(category, 0)
            processed = category_processed.get(category, 0)
            percentage = round((processed / total) * 100, 2) if total > 0 else 0.0
            
            category_completion_status[category] = {
                'total_products': total,
                'processed_products': processed,
                'completion_percentage': percentage,
                'remaining_products': total - processed
            }
        
        # Find next category to analyze
        incomplete_categories = {
            cat: data for cat, data in category_completion_status.items()
            if data['total_products'] > 0 and data['completion_percentage'] < 100
        }
        
        last_analyze_url = None
        if incomplete_categories:
            last_analyze_url = min(
                incomplete_categories.items(),
                key=lambda x: (x[1]['completion_percentage'], -x[1]['remaining_products'])
            )[0]
        
        return {
            'total_categories': len(categories),
            'category_completion_status': category_completion_status,
            'last_analyze_url': last_analyze_url
        }
        
    except Exception as e:
        print(f"❌ Error calculating completion metrics: {e}")
        return {
            'total_categories': 0,
            'category_completion_status': {},
            'last_analyze_url': None
        }


def get_quick_stats(base_path: str = None) -> Dict:
    """
    Get quick statistics without full completion status
    
    Returns:
        Dict with summary statistics only
    """
    metrics = get_completion_metrics(base_path)
    
    if not metrics['category_completion_status']:
        return {'error': 'Unable to calculate statistics'}
    
    active_categories = sum(1 for status in metrics['category_completion_status'].values() if status['total_products'] > 0)
    completed_categories = sum(1 for status in metrics['category_completion_status'].values() if status['completion_percentage'] == 100)
    total_products = sum(status['total_products'] for status in metrics['category_completion_status'].values())
    total_processed = sum(status['processed_products'] for status in metrics['category_completion_status'].values())
    overall_completion = round((total_processed / total_products * 100), 2) if total_products > 0 else 0
    
    return {
        'total_categories': metrics['total_categories'],
        'active_categories': active_categories,
        'completed_categories': completed_categories,
        'never_scraped': metrics['total_categories'] - active_categories,
        'total_products': total_products,
        'total_processed': total_processed,
        'overall_completion_percentage': overall_completion,
        'next_category_url': metrics['last_analyze_url']
    }


if __name__ == "__main__":
    # Test the integration module
    print("🧪 Testing Category Completion Tracker")
    
    stats = get_quick_stats()
    print(f"✅ Quick Stats: {stats}")
    
    full_metrics = get_completion_metrics()
    print(f"✅ Full Metrics: total_categories={full_metrics['total_categories']}, completion_entries={len(full_metrics['category_completion_status'])}")