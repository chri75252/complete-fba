# SURGICAL CACHE WRITE FIX - IMPLEMENTATION PLAN

## ROOT CAUSE CONFIRMED
Based on forensic analysis of both Copy (8) and Copy (9) versions:
- Both versions extract products successfully 
- Both versions find cache file correctly (actual_cache_file is valid)
- Both versions fail at cache write because new_products_added = 0
- Deduplication logic incorrectly marks all new products as duplicates

## SURGICAL FIX LOCATION
File: `tools/passive_extraction_workflow_latest.py`
Lines: 4457-4463 (deduplication logic)
Lines: 4466-4478 (cache write conditions)

## SPECIFIC ISSUE
The deduplication logic at lines 4457-4463:
```python
existing_urls = {p.get('url') for p in cached_products}
new_products_added = 0

for new_product in chunk_products:
    if new_product.get('url') not in existing_urls:
        cached_products.append(new_product)
        new_products_added += 1
```

Problem: URL comparison is failing - either URL normalization issues or missing URL fields.

## SURGICAL FIX STRATEGY
1. Add debug logging to trace URL comparison
2. Add fallback deduplication keys (EAN, title, etc.)
3. Add diagnostic logging for cache write conditions
4. Ensure cache write executes even when deduplication has edge cases

## EVIDENCE FROM LOGS
- Copy 8: "✅ CACHE FOUND: expected pattern - 7689 products" but no cache updates
- Copy 9: Same pattern - finds cache but never updates it
- Both versions: Products extracted but new_products_added remains 0