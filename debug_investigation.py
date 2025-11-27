import json
import os

base_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
cache_path = os.path.join(base_path, "OUTPUTS", "cached_products", "poundwholesale-co-uk_products_cache.json")
state_path = os.path.join(base_path, "OUTPUTS", "enhanced_category_tracking.json")
log_154127 = os.path.join(base_path, "logs", "debug", "run_custom_poundwholesale_20251125_154127.log")
log_155617 = os.path.join(base_path, "logs", "debug", "run_custom_poundwholesale_20251125_155617.log")

def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return f"Error reading {path}: {e}"

def read_log_tail(path, lines=20):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            return "".join(content[-lines:])
    except Exception as e:
        return f"Error reading {path}: {e}"

def read_log_head(path, lines=20):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            return "".join(content[:lines])
    except Exception as e:
        return f"Error reading {path}: {e}"

print("--- CACHE ANALYSIS ---")
cache_data = read_json(cache_path)
if isinstance(cache_data, dict):
    print(f"Cache Keys: {list(cache_data.keys())}")
    if "All-Baby-and-child" in cache_data:
        val = cache_data["All-Baby-and-child"]
        if isinstance(val, list):
            print(f"Count for 'All-Baby-and-child': {len(val)}")
        else:
            print(f"Type of 'All-Baby-and-child': {type(val)}")
    else:
        print("'All-Baby-and-child' NOT FOUND in cache")
else:
    print(f"Cache data is not a dict: {type(cache_data)}")

print("\n--- STATE ANALYSIS ---")
state_data = read_json(state_path)
print(f"State Data: {json.dumps(state_data, indent=2)[:500]}...")

print("\n--- LOG 154127 TAIL ---")
print(read_log_tail(log_154127))

print("\n--- LOG 155617 HEAD ---")
print(read_log_head(log_155617))
