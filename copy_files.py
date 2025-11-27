import shutil
import os
import json

base_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
pkg_path = os.path.join(base_path, "LLM_ANALYSIS_PACKAGE")

files_to_copy = [
    ("tools/passive_extraction_workflow_latest.py", "scripts/passive_extraction_workflow_latest.py"),
    ("utils/fixed_enhanced_state_manager.py", "scripts/fixed_enhanced_state_manager.py"),
    ("OUTPUTS/CACHE/processing_states/angelwholesale_co_uk_processing_state.json", "state_files/angelwholesale_co_uk_processing_state.json"),
    ("OUTPUTS/enhanced_category_tracking.json", "state_files/enhanced_category_tracking.json"),
    ("OUTPUTS/manifests/angelwholesale.co.uk/angelwholesale.co.uk_Category_All-Baby-and-child_manifest.json", "output_files/manifest_All-Baby-and-child.json"),
    ("OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk/linking_map.json", "output_files/linking_map.json"),
    ("config/angelwholesale_categories.json", "output_files/angelwholesale_categories.json"),
]

print("Copying files to LLM_ANALYSIS_PACKAGE...")
for src_rel, dst_rel in files_to_copy:
    src = os.path.join(base_path, src_rel.replace("/", os.sep))
    dst = os.path.join(pkg_path, dst_rel.replace("/", os.sep))

    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"OK Copied: {src_rel}")
    else:
        print(f"SKIP: {src_rel} not found")

# Extract first 3343 products from cache (summary info only - EAN, title, source_url)
cache_file = os.path.join(base_path, "OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json")
if os.path.exists(cache_file):
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)

    # Create summary: just EAN, title, source_URL for each product
    cache_summary = []
    for p in cache_data:
        cache_summary.append({
            "ean": p.get("ean", ""),
            "title": p.get("title", ""),
            "source_url": p.get("source_url", "")
        })

    summary_file = os.path.join(pkg_path, "output_files/cache_summary_all_products.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_products": len(cache_summary),
            "products": cache_summary
        }, f, indent=2)
    print(f"OK Created cache summary: {len(cache_summary)} products")

    # Count products per category
    category_counts = {}
    for p in cache_data:
        url = p.get("source_url", "")
        if "/Category/" in url:
            cat = url.split("/Category/")[-1].split("?")[0]
            category_counts[cat] = category_counts.get(cat, 0) + 1

    cat_file = os.path.join(pkg_path, "output_files/cache_products_by_category.json")
    with open(cat_file, 'w', encoding='utf-8') as f:
        json.dump(category_counts, f, indent=2)
    print(f"OK Created category count file: {len(category_counts)} categories")

print("\nFile copying complete!")
