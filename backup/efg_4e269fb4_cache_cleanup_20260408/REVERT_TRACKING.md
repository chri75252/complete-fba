# REVERT TRACKING — efg_4e269fb4_cache_cleanup_20260408

**Date:** 2026-04-08
**File changed:** `OUTPUTS/cached_products/efghousewares-co-uk__sandbox__4e269fb4_products_cache.json`

## What was done

The supplier cache file contained 1776 entries — the full raw product list for the EFG sandbox run, written by the old startup behaviour (pre-Fix-1) which dumped all raw input products to the cache at start.

The cache was cleaned to 863 entries: only products whose identity key (EAN-based or URL-based) matches an entry in the sandbox linking map at:
`OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk__sandbox__4e269fb4/linking_map.json`

The 913 removed entries were raw-input products from categories not yet processed (light-bulbs, bathroom-cosmetics-beauty, candles-air-fresheners, glass-tableware, bin-bags, air-fresheners, home-baking).

## Why

Stale raw-input entries in the cache would cause Fix 3's STEP 2 (cached_keys) to classify unstarted categories as "amazon_only" on resume. The system would skip supplier scraping for those categories and go straight to Amazon analysis using incomplete raw data. Removing stale entries ensures unstarted categories go through full extraction (correct behaviour on resume).

## State after cleanup

- Linking map: 863 entries ✓
- Cache: 863 entries ✓
- All linking map entries present in cache ✓
- All cache entries match linking map ✓

## To revert

```
cp backup/efg_4e269fb4_cache_cleanup_20260408/efghousewares-co-uk__sandbox__4e269fb4_products_cache.json \
   OUTPUTS/cached_products/efghousewares-co-uk__sandbox__4e269fb4_products_cache.json
```
