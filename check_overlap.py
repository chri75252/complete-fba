"""
Check for overlap between cache and linking_map
This should NOT exist - products should be in ONE or the OTHER
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
CATEGORY_URL = "https://angelwholesale.co.uk/Category/All-Baby-and-child"

# Load cache
cache_path = BASE_DIR / "OUTPUTS" / "cached_products" / "angelwholesale-co-uk_products_cache.json"
with open(cache_path, 'r', encoding='utf-8') as f:
    cache_data = json.load(f)

# Load linking map
linking_map_path = BASE_DIR / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / "angelwholesale.co.uk" / "linking_map.json"
with open(linking_map_path, 'r', encoding='utf-8') as f:
    linking_map = json.load(f)

# Load manifest
manifest_path = BASE_DIR / "OUTPUTS" / "manifests" / "angelwholesale.co.uk" / "angelwholesale.co.uk_Category_All-Baby-and-child_manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

manifest_urls = set(manifest['product_urls'])

# Get cache URLs for target category
cache_urls = set(p['url'] for p in cache_data if p.get('source_url') == CATEGORY_URL)

# Get linking map URLs that match manifest
linking_urls = set(e['supplier_url'] for e in linking_map if e.get('supplier_url') in manifest_urls)

print("="*80)
print("OVERLAP DETECTION")
print("="*80)
print()

print(f"Manifest URLs: {len(manifest_urls)}")
print(f"Cache URLs (for category): {len(cache_urls)}")
print(f"Linking map URLs (matching manifest): {len(linking_urls)}")
print()

# Check for overlap
overlap = cache_urls & linking_urls

print(f"OVERLAP (products in BOTH cache and linking_map): {len(overlap)}")
print()

if len(overlap) > 0:
    print("CRITICAL ERROR: Products exist in both cache and linking_map!")
    print("This violates the invariant that products should be in ONE location.")
    print()
    print("Sample overlapping URLs:")
    for i, url in enumerate(list(overlap)[:10]):
        print(f"  {i+1}. {url}")
    print()

# Check coverage
cache_only = cache_urls - linking_urls
linking_only = linking_urls - cache_urls
neither = manifest_urls - cache_urls - linking_urls

print(f"CLASSIFICATION:")
print(f"  In cache ONLY: {len(cache_only)}")
print(f"  In linking_map ONLY: {len(linking_only)}")
print(f"  In BOTH (overlap): {len(overlap)}")
print(f"  In NEITHER: {len(neither)}")
print()

print(f"COVERAGE CHECK:")
total_covered = len(cache_only) + len(linking_only) + len(overlap)
print(f"  Total covered: {total_covered}")
print(f"  Manifest total: {len(manifest_urls)}")
print(f"  Missing: {len(neither)}")
print()

# Verify the correct calculation
print(f"CORRECT INVARIANT:")
print(f"  {len(manifest_urls)} = {len(linking_only)} (skip) + {len(cache_only)} (cached) + {len(neither)} (remaining)")
print(f"  {len(manifest_urls)} = {len(linking_only) + len(cache_only) + len(neither)}")
print(f"  Balanced: {len(manifest_urls) == len(linking_only) + len(cache_only) + len(neither)}")
print()

# Show what's in neither
if len(neither) > 0:
    print(f"URLs in NEITHER cache nor linking_map (should be processed next):")
    for i, url in enumerate(list(neither)[:10]):
        print(f"  {i+1}. {url}")
