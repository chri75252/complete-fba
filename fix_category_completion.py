#!/usr/bin/env python3
"""
Fix Category Completion Tracking
Rebuilds missing cache entries from linking map to restore category tracking
"""

import os
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re

def extract_category_from_url(product_url):
    """Extract likely category URL from product URL"""
    try:
        # Parse the URL
        parsed = urlparse(product_url)
        path_parts = parsed.path.strip('/').split('/')
        
        # For poundwholesale.co.uk, category is usually first 2-3 path segments
        if len(path_parts) >= 2:
            # Try 2-level category first (most common)
            category_path = '/'.join(path_parts[:2])
            category_url = f"{parsed.scheme}://{parsed.netloc}/{category_path}"
            return category_url
        
        return None
    except Exception as e:
        print(f"Error extracting category from {product_url}: {e}")
        return None

def load_category_config():
    """Load category URLs from config file"""
    config_path = "config/poundwholesale_categories.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('category_urls', [])
    else:
        print(f"⚠️ Category config not found at {config_path}")
        return []

def find_best_category_match(product_url, category_urls):
    """Find the best matching category URL for a product"""
    extracted_category = extract_category_from_url(product_url)
    
    if not extracted_category:
        return None
    
    # Direct match
    if extracted_category in category_urls:
        return extracted_category
    
    # Fuzzy match - find most similar category
    best_match = None
    best_score = 0
    
    for category_url in category_urls:
        # Calculate similarity score
        if extracted_category in category_url or category_url in extracted_category:
            # Count common path segments
            extracted_parts = extracted_category.split('/')
            category_parts = category_url.split('/')
            
            common_parts = 0
            for i in range(min(len(extracted_parts), len(category_parts))):
                if extracted_parts[i] == category_parts[i]:
                    common_parts += 1
                else:
                    break
            
            score = common_parts / max(len(extracted_parts), len(category_parts))
            if score > best_score:
                best_score = score
                best_match = category_url
    
    return best_match if best_score > 0.5 else None

def rebuild_missing_cache_entries():
    """Rebuild missing cache entries from linking map"""
    print("🔧 REBUILDING MISSING CACHE ENTRIES")
    print("=" * 50)
    
    # Load files
    cache_path = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
    linking_map_path = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
    
    try:
        # Load existing cache
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            print(f"✅ Loaded cache: {len(cache_data)} entries")
        else:
            print("❌ Cache file not found")
            return False
        
        # Load linking map
        if os.path.exists(linking_map_path):
            with open(linking_map_path, 'r', encoding='utf-8') as f:
                linking_map = json.load(f)
            print(f"✅ Loaded linking map: {len(linking_map)} entries")
        else:
            print("❌ Linking map file not found")
            return False
        
        # Load category URLs
        category_urls = load_category_config()
        print(f"✅ Loaded categories: {len(category_urls)} URLs")
        
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return False
    
    # Find missing products
    cache_urls = set(product.get('url', '') for product in cache_data)
    linking_urls = set(entry.get('supplier_url', '') for entry in linking_map if entry.get('supplier_url'))
    
    missing_urls = linking_urls - cache_urls
    print(f"🔍 Found {len(missing_urls)} products in linking map but not in cache")
    
    if not missing_urls:
        print("✅ No missing products found - cache is synchronized")
        return True
    
    # Rebuild missing entries
    rebuilt_products = []
    category_matches = {}
    
    for entry in linking_map:
        supplier_url = entry.get('supplier_url', '')
        
        if supplier_url in missing_urls:
            # Extract product data from linking map entry
            product_data = {
                "title": entry.get('supplier_title', ''),
                "price": entry.get('supplier_price', 0),
                "url": supplier_url,
                "ean": entry.get('supplier_ean', ''),
                "sku": "",  # Not available in linking map
                "availability": "Unknown",  # Not available in linking map
                "image_url": "",  # Not available in linking map
                "scraped_at": entry.get('created_at', datetime.now().isoformat())
            }
            
            # Find best matching category
            best_category = find_best_category_match(supplier_url, category_urls)
            if best_category:
                product_data["source_url"] = best_category
                category_matches[best_category] = category_matches.get(best_category, 0) + 1
            else:
                print(f"⚠️ No category match found for: {supplier_url}")
                # Use extracted category even if not in config
                extracted = extract_category_from_url(supplier_url)
                if extracted:
                    product_data["source_url"] = extracted
                    category_matches[extracted] = category_matches.get(extracted, 0) + 1
            
            rebuilt_products.append(product_data)
    
    print(f"🔧 Rebuilt {len(rebuilt_products)} missing products")
    
    # Show category distribution
    if category_matches:
        print(f"\n📊 REBUILT PRODUCTS BY CATEGORY:")
        for category, count in sorted(category_matches.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count:3d} products: {category}")
    
    # Add rebuilt products to cache
    updated_cache = cache_data + rebuilt_products
    print(f"\n💾 Updated cache: {len(cache_data)} + {len(rebuilt_products)} = {len(updated_cache)} total")
    
    # Create backup
    backup_path = cache_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup created: {backup_path}")
    except Exception as e:
        print(f"⚠️ Backup failed: {e}")
    
    # Save updated cache
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(updated_cache, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated cache saved: {len(updated_cache)} total products")
        return True
    except Exception as e:
        print(f"❌ Error saving updated cache: {e}")
        return False

def validate_category_tracking_fix():
    """Validate that category tracking now works correctly"""
    print(f"\n🔍 VALIDATING CATEGORY TRACKING FIX")
    print("-" * 40)
    
    # Load files
    cache_path = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
    linking_map_path = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
        
        category_urls = load_category_config()
        
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return False
    
    # Simulate category tracking calculation
    from collections import defaultdict
    
    processed_urls = set(entry.get('supplier_url', '') for entry in linking_map if entry.get('supplier_url'))
    
    category_totals = defaultdict(int)
    category_processed = defaultdict(int)
    
    for product in cache_data:
        source_url = product.get('source_url', '')
        product_url = product.get('url', '')
        
        if source_url:
            category_totals[source_url] += 1
            if product_url in processed_urls:
                category_processed[source_url] += 1
    
    # Count categories with processed products
    tracked_categories = {url: {"total": category_totals[url], "processed": category_processed[url]} 
                         for url in category_totals if category_processed[url] > 0}
    
    print(f"Categories in config: {len(category_urls)}")
    print(f"Categories with products: {len(category_totals)}")
    print(f"Categories with processed products: {len(tracked_categories)}")
    
    # Check specific missing category
    missing_category = "https://www.poundwholesale.co.uk/stationery/wholesale-pens-pencils-markers"
    
    if missing_category in tracked_categories:
        stats = tracked_categories[missing_category]
        percent = (stats["processed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"\n✅ MISSING CATEGORY NOW TRACKED:")
        print(f"   Category: {missing_category}")
        print(f"   Total products: {stats['total']}")
        print(f"   Processed products: {stats['processed']}")
        print(f"   Completion: {percent:.1f}%")
        return True
    else:
        print(f"\n❌ Missing category still not tracked: {missing_category}")
        return False

def generate_fixed_category_report():
    """Generate a report of fixed category tracking"""
    print(f"\n📊 GENERATING FIXED CATEGORY REPORT")
    print("-" * 40)
    
    try:
        # Load files
        cache_path = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
        linking_map_path = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
        
        category_urls = load_category_config()
        
        # Calculate comprehensive category status
        from collections import defaultdict
        
        processed_urls = set(entry.get('supplier_url', '') for entry in linking_map if entry.get('supplier_url'))
        
        category_totals = defaultdict(int)
        category_processed = defaultdict(int)
        
        for product in cache_data:
            source_url = product.get('source_url', '')
            product_url = product.get('url', '')
            
            if source_url:
                category_totals[source_url] += 1
                if product_url in processed_urls:
                    category_processed[source_url] += 1
        
        # Build comprehensive report
        results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_categories_in_config": len(category_urls),
                "categories_with_products": len(category_totals),
                "categories_with_processed_products": len([url for url in category_totals if category_processed[url] > 0]),
                "total_products_in_cache": len(cache_data),
                "total_processed_products": len(processed_urls)
            },
            "category_details": {}
        }
        
        # Add details for each category with activity
        for category_url in category_totals:
            total = category_totals[category_url]
            processed = category_processed[category_url]
            percent = (processed / total * 100) if total > 0 else 0
            
            results["category_details"][category_url] = {
                "total_products": total,
                "processed_products": processed,
                "completion_percent": round(percent, 1),
                "status": "completed" if percent == 100 else "in_progress" if processed > 0 else "not_started"
            }
        
        # Save results
        output_path = "OUTPUTS/FIXED_category_completion_status.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_path}")
        
        # Show summary
        print(f"\n📈 SUMMARY:")
        print(f"Total categories in config: {results['summary']['total_categories_in_config']}")
        print(f"Categories with products: {results['summary']['categories_with_products']}")
        print(f"Categories with processed products: {results['summary']['categories_with_processed_products']}")
        print(f"Total products in cache: {results['summary']['total_products_in_cache']:,}")
        print(f"Total processed products: {results['summary']['total_processed_products']:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

if __name__ == "__main__":
    print("🚀 FIXING CATEGORY COMPLETION TRACKING")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Rebuild missing cache entries
    rebuild_success = rebuild_missing_cache_entries()
    
    if rebuild_success:
        # Step 2: Validate the fix
        validation_success = validate_category_tracking_fix()
        
        # Step 3: Generate comprehensive report
        report_success = generate_fixed_category_report()
        
        if validation_success and report_success:
            print(f"\n🎉 CATEGORY TRACKING FIX COMPLETED SUCCESSFULLY!")
            print("✅ Missing cache entries rebuilt from linking map")
            print("✅ Category tracking now includes all processed categories")
            print("✅ Comprehensive report generated")
        else:
            print(f"\n⚠️ Fix completed but validation failed")
    else:
        print(f"\n❌ Fix failed - could not rebuild missing cache entries")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Review the generated report for category completion status")
    print("2. Run the system to verify category tracking works correctly")
    print("3. Monitor for any remaining missing categories")