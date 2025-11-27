import json
import sys

def extract_manifest_urls():
    try:
        with open('OUTPUTS/manifests/angelwholesale.co.uk/angelwholesale.co.uk_Category_All-Baby-and-child_manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            return set(manifest['product_urls'])
    except Exception as e:
        print(f"Error reading manifest: {e}")
        return set()

def extract_cache_urls():
    try:
        with open('OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)

        # Filter for All-Baby-and-child category
        baby_cache = [p for p in cache if p.get('source_url', '').endswith('All-Baby-and-child')]
        return set(p.get('url', '') for p in baby_cache if p.get('url'))
    except Exception as e:
        print(f"Error reading cache: {e}")
        return set()

def main():
    manifest_urls = extract_manifest_urls()
    cache_urls = extract_cache_urls()

    print(f"Manifest URLs: {len(manifest_urls)}")
    print(f"Cache URLs: {len(cache_urls)}")

    # Find URLs in manifest but not in cache
    missing_urls = manifest_urls - cache_urls
    print(f"Missing URLs: {len(missing_urls)}")

    if missing_urls:
        print("Missing URLs:")
        for i, url in enumerate(sorted(missing_urls), 1):
            print(f"  {i}. {url}")

    # Find URLs in cache but not in manifest (for debugging)
    extra_urls = cache_urls - manifest_urls
    if extra_urls:
        print(f"Extra URLs in cache: {len(extra_urls)}")
        for i, url in enumerate(sorted(extra_urls)[:5], 1):
            print(f"  {i}. {url}")

if __name__ == "__main__":
    main()