import json
from pathlib import Path
from urllib.parse import urlparse

def normalize_url(url):
    if not url: return ""
    if url.endswith("/"): url = url[:-1]
    return url.lower().strip()

def stable_key(url, ean):
    """
    Generate a stable key for deduplication, matching the logic in PassiveExtractionWorkflow.
    """
    if ean:
        return f"ean:{ean}"
    
    if not url:
        return "unknown"
        
    try:
        parsed = urlparse(url)
        # Remove query parameters and fragments for stability
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return f"url:{normalize_url(clean_url)}"
    except Exception:
        return f"url:{normalize_url(url)}"

cache_path = "OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json"
target_cat = "https://angelwholesale.co.uk/Category/All-Baby-and-child"
norm_target = normalize_url(target_cat)

print(f"Analyzing Cache File: {cache_path}")
print(f"Target Category: {target_cat}")
print(f"Normalized Target: {norm_target}")

try:
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"ERROR: Cache file not found at {cache_path}")
    exit(1)

# 1. Identify the 401 "Source" products (The Frozen Denominator)
source_products = []
for p in data:
    if isinstance(p, dict):
        src = p.get("source_url")
        # Check if this product belongs to the target category based on source_url
        if src and normalize_url(src) == norm_target:
            source_products.append(p)

print(f"\n--- STEP 1: SOURCE ANALYSIS ---")
print(f"Total Source Products (Denominator): {len(source_products)}")

# 2. Simulate _rebuild_category_amazon_queue logic
print(f"\n--- STEP 2: QUEUE REBUILD SIMULATION ---")
queue = []
rejected_mismatch = []
rejected_duplicate = []
seen_keys = set()

# Assuming _category_allowed_keys is NOT set (allowed_gate=off in logs)
# If it was on, we would need that set. Logs say "allowed_gate=off".

for p in source_products:
    # Logic from _rebuild_category_amazon_queue
    src = p.get("source_url") or p.get("category_url") or ""
    try:
        n_src = normalize_url(src) if src else ""
    except Exception:
        n_src = src
    
    # Filter 1: Category Mismatch (Should match because we pre-filtered, but let's verify exact logic)
    if norm_target and n_src != norm_target:
        rejected_mismatch.append(p['url'])
        continue
        
    # Filter 2: Duplicates (Implicit in some workflows, explicit in others. 
    # The provided code snippet for _rebuild_category_amazon_queue does NOT explicitly dedup 
    # unless 'allowed' set is passed. However, let's check if duplicates exist in source.)
    
    # Wait, the snippet provided earlier:
    # if allowed:
    #    k = stable_key(...)
    #    if k not in allowed: continue
    # 
    # It does NOT seem to have an internal 'seen' set for deduping itself if allowed is empty.
    # Let's check if the list itself has duplicates.
    
    queue.append(p)

print(f"Rebuilt Queue Size: {len(queue)}")
print(f"Missing Count: {len(source_products) - len(queue)}")

if len(source_products) != len(queue):
    print("Discrepancy found in simulation!")
    for r in rejected_mismatch:
        print(f"REJECTED (Mismatch): {r}")
else:
    print("No discrepancy found with simple logic. Checking for duplicates in source...")
    # Check for duplicates in source_products
    urls = [p.get('url') for p in source_products]
    unique_urls = set(urls)
    if len(urls) != len(unique_urls):
        print(f"Found {len(urls) - len(unique_urls)} duplicate URLs in source products!")
        from collections import Counter
        counts = Counter(urls)
        for url, count in counts.items():
            if count > 1:
                print(f"DUPLICATE: {url} (Count: {count})")
