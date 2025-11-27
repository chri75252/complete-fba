import json
import os
import re

# --- Normalization functions copied from the codebase for accuracy ---

def normalize_url_simple(url: str) -> str:
    """Basic normalization for comparison."""
    if not url:
        return ""
    return url.lower().rstrip('/').strip()

def investigate_reprocessing(linking_map_path, cache_path, category_url, resume_ptr):
    """
    Investigates why products might be reprocessed by simulating the 'is_processed' check.
    """
    # 1. Load all processed URLs from the linking map
    if not os.path.exists(linking_map_path):
        return {"error": f"Linking map not found: {linking_map_path}"}
    
    processed_urls = set()
    try:
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
        for entry in linking_map:
            if entry.get("supplier_url"):
                processed_urls.add(normalize_url_simple(entry["supplier_url"]))
    except Exception as e:
        return {"error": f"Could not load or parse linking map: {e}"}

    # 2. Load the specific category queue from the main cache file
    if not os.path.exists(cache_path):
        return {"error": f"Cache file not found: {cache_path}"}
        
    category_queue = []
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
        
        # Rebuild the queue exactly as the workflow does
        for p in all_products:
            source = p.get("source_url") or p.get("category_url") or ""
            if normalize_url_simple(source) == normalize_url_simple(category_url):
                category_queue.append(p)
        
        # Sort it deterministically
        category_queue.sort(key=lambda x: normalize_url_simple(x.get("url", "")))

    except Exception as e:
        return {"error": f"Could not load or parse cache file: {e}"}

    # 3. Simulate the check
    unrecognized_products = []
    # Check products that *should* have been processed (from 0 up to the resume pointer)
    if resume_ptr > len(category_queue):
        return {"error": f"Resume pointer {resume_ptr} is out of bounds for the queue of size {len(category_queue)}."}

    for i in range(resume_ptr):
        product = category_queue[i]
        product_url = product.get("url")
        if not product_url:
            continue
        
        normalized_product_url = normalize_url_simple(product_url)
        
        # This simulates `if normalized_url not in processed_urls_set:`
        if normalized_product_url not in processed_urls:
            unrecognized_products.append({
                "index": i,
                "url": product_url,
                "normalized_url": normalized_product_url,
                "title": product.get("title")
            })

    # 4. Report findings
    return {
        "total_processed_in_linking_map": len(processed_urls),
        "category_queue_size": len(category_queue),
        "products_checked_before_resume_ptr": resume_ptr,
        "unrecognized_product_count": len(unrecognized_products),
        "unrecognized_products_sample": unrecognized_products[:20] # Sample to keep output clean
    }

# --- Main Execution ---
if __name__ == "__main__":
    LINKING_MAP_PATH = "OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk/linking_map.json"
    CACHE_PATH = "OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json"
    CATEGORY_URL = "https://angelwholesale.co.uk/Category/All-Baby-and-child"
    RESUME_POINTER = 298 # From the log: ptr=298

    results = investigate_reprocessing(LINKING_MAP_PATH, CACHE_PATH, CATEGORY_URL, RESUME_POINTER)
    
    print(json.dumps(results, indent=2))

