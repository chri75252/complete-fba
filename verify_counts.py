import json
import os

def count_products(file_path, category_url=None):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if category_url:
            # This is for the main cache file, filter by category
            if isinstance(data, list):
                count = sum(1 for item in data if item.get('source_url') == category_url)
                return count
            else:
                return "Error: Expected a list of products."
        else:
            # This is for a manifest file
            if 'product_urls' in data and isinstance(data['product_urls'], list):
                return data.get('count', len(data['product_urls']))
            else:
                 return "Error: Manifest file in unexpected format."

    except json.JSONDecodeError:
        return f"Error: Invalid JSON in {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"

# Paths to check
manifest_path = "OUTPUTS/manifests/angelwholesale.co.uk/angelwholesale.co.uk_Category_All-Baby-and-child_manifest.json"
cache_path = "OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json"
category_to_check = "https://angelwholesale.co.uk/Category/All-Baby-and-child"

# Get counts
manifest_count = count_products(manifest_path)
cache_count_for_category = count_products(cache_path, category_url=category_to_check)

print(f"Manifest product count for '{category_to_check}': {manifest_count}")
print(f"Cached product count for '{category_to_check}': {cache_count_for_category}")
