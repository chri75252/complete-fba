import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re

def normalize_url(url):
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        # Normalize scheme and netloc
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.rstrip("/")
        
        # Sort query parameters
        qs = parse_qs(parsed.query)
        sorted_qs = urlencode(sorted(qs.items()), doseq=True)
        
        return urlunparse((scheme, netloc, path, parsed.params, sorted_qs, ""))
    except Exception:
        return url

def deep_analyze_logs_and_cache():
    base_dir = Path("c:/Users/chris/Desktop/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-")
    cache_path = base_dir / "OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json"
    linking_map_path = base_dir / "OUTPUTS/CACHE/amazon_data/angelwholesale.co.uk_linking_map.json"
    
    print(f"Loading cache from: {cache_path}")
    with open(cache_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
        
    print(f"Loading linking map from: {linking_map_path}")
    if linking_map_path.exists():
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            linking_map = json.load(f)
    else:
        linking_map = []
        print("Linking map not found.")

    # 1. Build Lookup Tables
    # Map Normalized URL -> List of Categories it appears in (from cache)
    url_to_categories = {}
    url_to_raw_urls = {}
    
    for p in products:
        raw_url = p.get('url')
        norm_url = normalize_url(raw_url)
        cat = p.get('source_url', 'Unknown')
        
        if norm_url not in url_to_categories:
            url_to_categories[norm_url] = set()
            url_to_raw_urls[norm_url] = set()
            
        url_to_categories[norm_url].add(cat)
        url_to_raw_urls[norm_url].add(raw_url)

    # 2. Analyze the "Baby-Socks-and-Booties" Discrepancy
    target_cat = "https://angelwholesale.co.uk/Category/Baby-Socks-and-Booties"
    print(f"\n--- Deep Analysis: {target_cat} ---")
    
    # We need to find products that *would* be in this category.
    # Since we don't have the scraper's live output, we look for products in the cache
    # that are associated with this category OR have keywords suggesting they belong.
    # BUT, the most reliable way is to check the products the user said were "skipped".
    # The user said "26 in cache". This means 26 URLs found by the scraper matched the cache.
    
    # Let's find ALL products in the cache that are associated with this category directly
    direct_products = [p for p in products if p.get('source_url') == target_cat]
    print(f"Products directly saved under '{target_cat}': {len(direct_products)}")
    
    # Now, let's find products that are NOT saved under this category, but might belong to it.
    # We can infer this if they share a URL with a product that IS in this category? No, that's circular.
    # We can infer this if they are in the linking map?
    
    # Let's look at the "26 in cache" claim.
    # If the scraper found 26 URLs, and the filter said they are in the cache,
    # then there must be 26 Normalized URLs in the cache that matched.
    # But only 2 have 'source_url' = target_cat.
    # So 24 must have 'source_url' = SOMETHING ELSE.
    
    # We can't know exactly WHICH 26 URLs the scraper found without the scraper logs.
    # BUT we can look for products that appear in MULTIPLE categories in the cache.
    
    multi_cat_products = {u: cats for u, cats in url_to_categories.items() if len(cats) > 1}
    print(f"Total products appearing in multiple categories in cache: {len(multi_cat_products)}")
    
    # Let's see if any products in the cache have 'Baby-Socks-and-Booties' as ONE of their categories
    # (This would imply we scraped it once, saved it, then scraped it again in another category and saved it again?
    #  Actually, the system prevents saving duplicates. So a product is usually only saved under the FIRST category it was found in.)
    
    # So, if a product is in 'Baby-Socks-and-Booties', it was likely found there FIRST.
    # If it's in 'All-Shop-by-age', it was found there FIRST.
    
    # The discrepancy is: Scraper visits 'Baby-Socks-and-Booties'. Finds Product X.
    # Product X is ALREADY in cache under 'All-Shop-by-age'.
    # Filter says: "It's in cache! Skip extraction."
    # Retrieval says: "Get me Product X from cache." -> FAILS due to string mismatch.
    
    # Let's prove the string mismatch.
    # We need to find a product where:
    # 1. It exists in the cache.
    # 2. Its Raw URL in the cache is DIFFERENT from what the scraper likely found.
    #    (Scraper usually finds canonical URLs or URLs with specific params).
    
    print("\n--- Checking for URL Variations (Potential Retrieval Failures) ---")
    variation_count = 0
    for norm_url, raw_urls in url_to_raw_urls.items():
        if len(raw_urls) > 1:
            variation_count += 1
            if variation_count <= 5:
                print(f"Normalized: {norm_url}")
                print(f"Variations: {raw_urls}")
                
    print(f"Total products with multiple raw URL variations in cache: {variation_count}")
    
    # 3. Verify "Only Reason" Hypothesis
    # Are there other reasons for skipping?
    # - Linking Map: "27 in linking map". These are skipped entirely.
    # - Cache: "26 in cache". These are "needs_amazon_only".
    
    # If the retrieval bug exists, then "needs_amazon_only" products are dropped.
    # If the linking map logic is correct, those 27 are safely ignored (already fully done).
    
    # Let's check if any of the "26 in cache" are ALSO in the linking map?
    # The filter logic separates them:
    # if in linking_map -> skip_entirely
    # elif in cache -> needs_amazon_only
    # So they are mutually exclusive in the filter's output.
    
    # Conclusion: The 26 products are in cache but NOT in linking map.
    # They represent products that have Supplier Data but NO Amazon Data (or failed Amazon analysis).
    # The system SHOULD process them.
    # The fact that it processed 0 (or 2) means the retrieval failed.

if __name__ == "__main__":
    deep_analyze_logs_and_cache()
