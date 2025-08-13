#!/usr/bin/env python3
"""
Sync Linking Map URLs to Processed Products
===========================================

This script extracts all URLs from the linking map and adds them to processed_products
with appropriate status, making the system much more efficient at resume detection.

Usage: python sync_linking_map_to_processed.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

def normalize_url(url):
    """Normalize URL for consistent comparison."""
    if not url:
        return ""
    return url.lower().strip().rstrip('/')

def load_linking_map(supplier_name):
    """Load linking map for the supplier."""
    linking_map_path = f"OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/linking_map.json"
    
    if not os.path.exists(linking_map_path):
        print(f"❌ Linking map not found: {linking_map_path}")
        return []
    
    try:
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
        print(f"✅ Loaded linking map: {len(linking_map)} entries")
        return linking_map
    except Exception as e:
        print(f"❌ Error loading linking map: {e}")
        return []

def load_processing_state(supplier_name):
    """Load processing state file."""
    # Try different filename formats
    possible_paths = [
        f"OUTPUTS/CACHE/processing_states/{supplier_name.replace('.', '_')}_processing_state.json",
        f"OUTPUTS/CACHE/processing_states/processing_state_during_longrun.json",
        f"OUTPUTS/CACHE/processing_states/{supplier_name}_processing_state.json"
    ]
    
    state_path = None
    for path in possible_paths:
        if os.path.exists(path):
            state_path = path
            break
    
    if not state_path:
        print(f"❌ Processing state not found in any of these locations:")
        for path in possible_paths:
            print(f"   - {path}")
        return None, None
    
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        print(f"✅ Loaded processing state: {len(state_data.get('processed_products', {}))} processed products")
        return state_data, state_path
    except Exception as e:
        print(f"❌ Error loading processing state: {e}")
        return None, None

def sync_linking_map_to_processed(supplier_name="poundwholesale.co.uk"):
    """Sync all linking map URLs to processed_products."""
    
    print(f"🔄 Starting sync for supplier: {supplier_name}")
    
    # Load linking map
    linking_map = load_linking_map(supplier_name)
    if not linking_map:
        return False
    
    # Load processing state
    state_data, state_path = load_processing_state(supplier_name)
    if not state_data:
        return False
    
    # Get current processed products
    processed_products = state_data.setdefault("processed_products", {})
    initial_count = len(processed_products)
    
    # Extract URLs from linking map
    linking_map_urls = set()
    for entry in linking_map:
        url = entry.get("supplier_url") or entry.get("url")
        if url:
            linking_map_urls.add(url)
    
    print(f"📊 Found {len(linking_map_urls)} unique URLs in linking map")
    
    # Determine status based on linking map entry completeness
    added_count = 0
    updated_count = 0
    
    for entry in linking_map:
        url = entry.get("supplier_url") or entry.get("url")
        if not url:
            continue
        
        # Determine completion status
        has_amazon_data = bool(entry.get("amazon_asin") or entry.get("amazon_title"))
        has_financial_data = bool(entry.get("roi") or entry.get("profit"))
        
        if has_financial_data:
            # Complete with financial analysis
            if entry.get("roi", 0) > 0:
                status = "completed_profitable"
            else:
                status = "completed_not_profitable"
        elif has_amazon_data:
            # Amazon analysis done, but no financial data
            status = "amazon_extracted"
        else:
            # Only supplier data available
            status = "supplier_extracted"
        
        # Add or update in processed_products
        if url not in processed_products:
            processed_products[url] = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "source": "linking_map_sync",
                "original_url": url
            }
            added_count += 1
        else:
            # Update status if linking map has more complete data
            current_status = processed_products[url].get("status", "")
            if (status == "completed_profitable" or status == "completed_not_profitable") and \
               not current_status.startswith("completed_"):
                processed_products[url]["status"] = status
                processed_products[url]["updated_from_linking_map"] = True
                updated_count += 1
    
    # Update state data
    state_data["processed_products"] = processed_products
    state_data["last_updated"] = datetime.now().isoformat()
    
    # Add sync metadata
    state_data.setdefault("sync_metadata", {})["linking_map_sync"] = {
        "timestamp": datetime.now().isoformat(),
        "initial_processed_count": initial_count,
        "linking_map_count": len(linking_map_urls),
        "added_count": added_count,
        "updated_count": updated_count,
        "final_processed_count": len(processed_products)
    }
    
    # Create backup
    backup_path = state_path + ".backup_before_sync"
    if os.path.exists(state_path):
        import shutil
        shutil.copy2(state_path, backup_path)
        print(f"💾 Created backup: {backup_path}")
    
    # Save updated state
    try:
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sync completed successfully!")
        print(f"📊 Results:")
        print(f"   - Initial processed products: {initial_count}")
        print(f"   - Linking map URLs: {len(linking_map_urls)}")
        print(f"   - Added to processed: {added_count}")
        print(f"   - Updated statuses: {updated_count}")
        print(f"   - Final processed products: {len(processed_products)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving updated state: {e}")
        return False

if __name__ == "__main__":
    success = sync_linking_map_to_processed()
    if success:
        print("\n🎯 OPTIMIZATION COMPLETE!")
        print("The system will now:")
        print("✅ Skip all linking map products instantly")
        print("✅ Resume much faster (no category scanning needed)")
        print("✅ Avoid all Pattern Combination #2 issues")
        print("✅ Have unified state tracking")
    else:
        print("\n❌ Sync failed - check error messages above")