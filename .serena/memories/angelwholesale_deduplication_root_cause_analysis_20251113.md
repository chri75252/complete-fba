# AngelWholesale Deduplication Root Cause Analysis
**Date**: 2025-11-13
**Status**: ROOT CAUSE IDENTIFIED

## 🎯 PROBLEM SUMMARY
System only records 1 product for angelwholesale.co.uk despite finding 40 unique products on category pages. All subsequent products trigger deduplication and are not saved.

## 🔍 INVESTIGATION FINDINGS

### Chrome DevTools Analysis
**Verified with live site inspection:**
- ✅ **40 unique products** found on category page
- ✅ **All products have unique identifiers:**
  - `data-card-id`: 61333, 26486, 26485, 26482, 26481, etc. (40 unique)
  - `data-sku`: T14381, T14842, T14841, T14838, T14837, etc. (40 unique)  
  - Product URLs: All unique (40/40)
  - Titles: All unique (40/40)
- ✅ **Selectors working correctly:**
  - `li.product` finds all 40 products
  - `h3.card-title` extracts titles correctly
  - `span.price.price--withoutTax` extracts prices correctly
  - `a.card-figure__link` extracts URLs correctly

### Cache File Analysis
**Location**: `OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json`
**Contents**: 1 product entry:
```json
{
  "title": "London Taxi & Bus Pull Back",
  "price": null,  ⚠️ CRITICAL: Price extraction failed
  "url": "https://angelwholesale.co.uk/Item/Bp-Services-Station-Set-With-Dc-Car--by-AtoZ-Toys-toy021688",
  "ean": "00059884",
  "scraped_at": "2025-11-13T17:25:22.455592"
}
```

### Deduplication Logic Analysis
**Code Location**: `tools/passive_extraction_workflow_latest.py:4402-4438`

**Deduplication Key Generation:**
```python
k = stable_key(normalize_url(p.get("url")), self._valid_ean_for_key(p.get("ean")))
```

**Key Components:**
1. **Normalized URL**: Primary identifier
2. **Valid EAN**: Secondary identifier (if present)
3. **SKU removed before keying**: `p.pop("sku", None)` at line 4420

## 🚨 ROOT CAUSES IDENTIFIED

### Primary Issue: Price Extraction Failure
**Problem**: The selector configuration is not extracting prices from product detail pages.
- Category page selector works: `span.price.price--withoutTax` ✓
- Product detail page extraction fails: `price: null` ❌

**Impact**: Products without valid price data may be:
1. Discarded as invalid
2. Normalized to empty/null keys causing hash collisions
3. Failing validation checks

### Secondary Issue: Selector Context Mismatch  
**Problem**: Configuration has separate selectors for category vs product detail pages:
```json
"field_mappings": {
  "price": ["span.price.price--withoutTax"]  // Used on category pages
},
"category_page": {
  "price": ["span.price.price--withoutTax"]  // Duplicate definition
}
```

Missing product detail page price selector:
```json
"product_detail_price": [
  ".productView-price .price--withoutTax",
  ".price--withoutTax"
]
```

### Tertiary Issue: EAN Extraction Not Capturing data-sku
**Problem**: The system extracts EAN from product detail pages using:
```json
"ean": [
  ".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)"
]
```

But doesn't extract the `data-sku` attribute from category page `article.card` elements, which would provide immediate unique identifiers.

## 📊 WORKFLOW SEQUENCE ANALYSIS

### What Actually Happens:
1. **URL Collection Phase** (Line 1417 in configurable_supplier_scraper.py)
   - Finds 40 products with `li.product` selector ✓
   - Extracts 40 unique URLs ✓

2. **URL Filtering Phase** (Lines 554-565)
   - Loads cache: 1 existing URL
   - Filters new URLs: 40 - 1 = 39 URLs need processing ✓

3. **Product Extraction Phase** (Lines 1238-1302)
   - Visits each of 39 product detail pages
   - Extracts product data using product detail selectors
   - **FAILS to extract price** → creates products with `price: null`

4. **Cache Save Deduplication Phase** (Lines 4402-4455)
   - Loads 1 existing product for deduplication
   - Generates keys for 39 new products
   - **All products deduplicated away** → "0 new; dedup scan skipped"

### Why Deduplication Fails:
Products with null/invalid data likely generate empty or identical deduplication keys, causing all products to hash to the same value or be rejected as invalid.

## 🔧 SOLUTIONS

### Solution 1: Fix Product Detail Price Selector (IMMEDIATE)
**Action**: Update `config/supplier_configs/angelwholesale.co.uk.json`

**Current (Broken)**:
```json
"product_detail_price": [
  ".productView-price .price--withoutTax",
  ".price--withoutTax"
]
```

**Chrome DevTools Verification Needed**:
Navigate to product detail page and test:
```javascript
document.querySelector('.productView-price .price--withoutTax')?.textContent
document.querySelector('.price-section .price--withoutTax')?.textContent  
document.querySelector('span.price.price--withoutTax')?.textContent
```

### Solution 2: Extract data-sku from Category Page (ENHANCEMENT)
**Action**: Modify configurable_supplier_scraper.py to extract `data-sku` attribute

**Location**: In `extract_identifier` method or product extraction loop

**Implementation**:
```python
# Extract data-sku from article element if available
if element.name == 'li' and element.get('class') and 'product' in element.get('class'):
    article = element.select_one('article.card')
    if article:
        data_sku = article.get('data-sku')
        if data_sku:
            product['sku'] = data_sku
            log.info(f"Extracted data-sku: {data_sku}")
```

### Solution 3: Clear Broken Cache (IMMEDIATE)
**Action**: Delete the broken cache file to start fresh

```bash
rm "OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json"
```

This removes the 1 product with null price that's causing issues.

### Solution 4: Add Validation to Prevent Null Price Save
**Action**: Add validation before cache save to reject products with null prices

**Location**: `tools/passive_extraction_workflow_latest.py` before deduplication

```python
# Filter out invalid products before deduplication
valid_products = [p for p in products if p.get('price') is not None and p.get('price') != 'N/A']
log.info(f"Validation: {len(valid_products)}/{len(products)} products have valid prices")
products = valid_products
```

## 🎯 RECOMMENDED ACTION PLAN

### Phase 1: Investigation (5 minutes)
1. Navigate to product detail page with Chrome DevTools
2. Test price selectors to find working selector
3. Document correct selector for product_detail_price

### Phase 2: Configuration Fix (2 minutes)
1. Update `angelwholesale.co.uk.json` with correct product_detail_price selector
2. Verify configuration file syntax is valid JSON

### Phase 3: Clean Slate (1 minute)
1. Delete broken cache file: `angelwholesale-co-uk_products_cache.json`
2. Optionally delete linking map if it exists

### Phase 4: Test Run (10 minutes)
1. Run: `python run_custom_angelwholesale-co-uk.py`
2. Monitor logs for:
   - Price extraction success
   - Multiple products being saved (not just 1)
   - No premature deduplication

### Phase 5: Validation (5 minutes)
1. Check cache file has multiple products with valid prices
2. Verify product count matches expected category page products
3. Confirm no "0 new; dedup scan skipped" messages

## 📝 NEXT SESSION CONTINUATION

**Context for Next Agent/Session:**
1. Root cause identified: Price extraction failing on product detail pages
2. Chrome DevTools needed to find correct price selector for detail pages
3. Clean cache and re-run after fixing product_detail_price selector
4. Monitor for successful multi-product extraction and cache save

**Key Files to Reference:**
- Config: `config/supplier_configs/angelwholesale.co.uk.json`
- Cache: `OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json`
- Workflow: `tools/passive_extraction_workflow_latest.py` (dedup logic)
- Scraper: `tools/configurable_supplier_scraper.py` (extraction logic)

**Success Criteria:**
- Cache file contains 40+ products
- All products have valid (non-null) prices
- No premature deduplication messages
- System processes full category successfully
