import json
import os

base_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
cache_path = os.path.join(base_path, "OUTPUTS", "cached_products", "poundwholesale-co-uk_products_cache.json")

def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return f"Error reading {path}: {e}"

print("--- CACHE ITEM INSPECTION ---")
cache_data = read_json(cache_path)
if isinstance(cache_data, list) and len(cache_data) > 0:
    first_item = cache_data[0]
    print(f"First item keys: {list(first_item.keys())}")
    print(f"Has 'source_url': {'source_url' in first_item}")
    if 'source_url' in first_item:
        print(f"Sample source_url: {first_item['source_url']}")
    
    # Count how many have source_url
    count = sum(1 for p in cache_data if 'source_url' in p)
    print(f"Items with source_url: {count}/{len(cache_data)}")
