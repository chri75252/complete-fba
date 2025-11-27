import json
import os

base_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
cache_path = os.path.join(base_path, "OUTPUTS", "cached_products", "poundwholesale-co-uk_products_cache.json")
state_path = os.path.join(base_path, "OUTPUTS", "enhanced_category_tracking.json")

def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return f"Error reading {path}: {e}"

print("--- CACHE ANALYSIS ---")
cache_data = read_json(cache_path)
if isinstance(cache_data, list):
    print(f"Cache is a LIST. Length: {len(cache_data)}")
    if len(cache_data) > 0:
        print(f"First item keys: {list(cache_data[0].keys())}")
        # Check if items have a 'category' field
        cats = set()
        for p in cache_data:
            if isinstance(p, dict):
                cats.add(p.get('category', 'UNKNOWN'))
        print(f"Categories found in list: {cats}")
elif isinstance(cache_data, dict):
    print(f"Cache is a DICT. Keys: {list(cache_data.keys())}")
else:
    print(f"Cache type: {type(cache_data)}")

print("\n--- STATE ANALYSIS ---")
state_data = read_json(state_path)
if isinstance(state_data, dict):
    print("State loaded successfully.")
    # Print frozen denominators if present
    print(f"Frozen Denominators: {state_data.get('frozen_denominators', 'Not Found')}")
else:
    print(f"State data error/type: {state_data}")
