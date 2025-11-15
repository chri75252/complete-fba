# AngelWholesale Complete Investigation - Root Causes Identified
**Date**: 2025-11-13  
**Status**: ALL ROOT CAUSES CONFIRMED

## 🎯 INVESTIGATION SUMMARY

Conducted thorough investigation as requested to identify why:
1. System only records 1 product (deduplication issue)
2. System shows 40 products instead of 61 (pagination issue)

## 🔍 ROOT CAUSE #1: EAN Pattern Matching Bug (DEDUPLICATION TRIGGER)

### Problem
**ALL products extract the same EAN "00059884" via pattern matching**, causing every product to have identical deduplication keys.

### Evidence

**Product 1**: Dinosaur Assorted (toy07636)
- Correct EAN (from specs table): `5012866016618` ✅
- Pattern match (FIRST extraction): `00059884` ❌
- Deduplication key: `ean:00059884`

**Product 2**: Wooden Shape Sorter (toy021747)
- Correct EAN (from specs table): `5012866625599` ✅
- Pattern match (FIRST extraction): `00059884` ❌
- Deduplication key: `ean:00059884`

**Cache Entry**: London Taxi & Bus (toy021688)
- Cached EAN: `00059884`
- Deduplication key: `ean:00059884`

### Deduplication Logic Analysis

**File**: `tools/passive_extraction_workflow_latest.py:4408`
```python
k = stable_key(normalize_url(p.get("url")), self._valid_ean_for_key(p.get("ean")))
```

**File**: `utils/normalization.py:25-30`
```python
def stable_key(url: str|None, ean: str|None) -> str:
    ne = normalize_ean(ean)
    if ne:  # **EAN-first authority**
        return f"ean:{ne}"
    nu = normalize_url(url)
    return f"url:{nu}" if nu else "anon:__missing__"
```

**CRITICAL**: EAN takes **priority** over URL. If any EAN exists, the key becomes `ean:{ean}`, completely ignoring the product URL.

### EAN Extraction Priority

**File**: `tools/configurable_supplier_scraper.py:3243-3300`

**Extraction Order:**
1. **FIRST**: HTML pattern matching (lines 3246-3266) 🚨 PROBLEMATIC
2. **SECOND**: CSS selectors from config (lines 3268-3300)

**Pattern Matching Code:**
```python
# FIRST: Try HTML pattern search for 8-14 digit codes (MOST RELIABLE)
html_content = str(product_page_soup)
ean_patterns = [
    r"Product Barcode/ASIN/EAN:\s*([0-9]{8,14})",
    r"barcode[^>]*[>:]?\s*([0-9]{8,14})",
    r"ean[^>]*[>:]?\s*([0-9]{8,14})",
    ...
]

for pattern in ean_patterns:
    matches = re.finditer(pattern, html_content, re.IGNORECASE)
    for match in matches:
        code = match.group(1).strip()
        if len(code) >= 8 and code.isdigit():
            log.info(f"🎯 EAN found via pattern search: {code}")
            return code  # RETURNS IMMEDIATELY
```

**The Bug**: Pattern matching finds `00059884` in ALL product pages (likely from a common element like advertisement, tracking code, or related products section), and returns it BEFORE trying the correct CSS selector.

### Why Deduplication Triggers

**Workflow**:
1. Cache has 1 product with EAN `00059884`
2. Scraper extracts 39 new products, ALL get EAN `00059884` via pattern matching
3. Deduplication generates keys:
   - Cached product: `ean:00059884`
   - New product 1: `ean:00059884` → DUPLICATE ❌
   - New product 2: `ean:00059884` → DUPLICATE ❌
   - New product 3: `ean:00059884` → DUPLICATE ❌
   - ... (all 39 marked as duplicates)
4. Result: 0 new products saved, "DEDUP SUMMARY: 0 new; dedup scan skipped"

### Configuration Review

**Current Config** (`angelwholesale.co.uk.json`):
```json
"field_mappings": {
  "ean": [
    ".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)",
    ".specs-data:last-child"
  ]
}
```

**PROBLEM**: This selector uses `:has()` and `:contains()` pseudo-selectors which are **jQuery/Cheerio syntax**, NOT standard CSS. BeautifulSoup's `.select()` doesn't support these.

**What Actually Works**:
- Manual iteration through `.specs-row` elements
- Check `.specs-data` cells for "Barcode" label
- Extract second cell value

**Why Config Selector Fails**:
- BeautifulSoup can't parse `:has()` or `:contains()`
- Selector returns nothing
- Falls back to pattern matching
- Pattern matching extracts wrong EAN from common HTML element

---

## 🔍 ROOT CAUSE #2: Pagination Configuration (40 vs 61 PRODUCTS)

### Problem
System shows only 40 products when 61 exist on the category page.

### Evidence

**Chrome DevTools**:
- Products currently visible: 40
- Total products available: 61
- Missing products: 21
- Page status: "You've viewed 40 of 61 products"

**LOAD MORE Button**:
```html
<a class="btn-load-more button !rg-bg-violet-100 ... ">
  <span>Load More</span>
</a>
```
- ✅ Button EXISTS
- ✅ Button is VISIBLE
- ✅ Button is CLICKABLE
- ✅ Selector: `a.btn-load-more` or `.btn-load-more`

### Configuration Review

**Current Config** (`angelwholesale.co.uk.json`):
```json
"category_page": {
  "next_page_button_selector": [],  // ❌ EMPTY!
  "pagination_method": "scroll_and_wait",
  "infinite_scroll": true,
  "scroll_wait_time": 2.0,
  "max_scrolls": 10
}
```

**PROBLEM**: 
- `next_page_button_selector` is **EMPTY**
- System configured for infinite scroll, but button exists
- Button never gets clicked → only initial 40 products loaded

---

## 🔍 SCRAPER CONFIGURATION READING VERIFICATION

### Config Loading Path

**File**: `tools/configurable_supplier_scraper.py:1669-1775`

**Method**: `_get_selectors_for_domain()`

**Priority Order**:
1. Supplier package (`suppliers/angelwholesale-co-uk/config/product_selectors.json`)
2. Legacy config (`config/supplier_configs/angelwholesale.co.uk.json`) ✅ USED
3. Fallback filesystem search

**Confirmation**: System correctly loads from `config/supplier_configs/angelwholesale.co.uk.json`

### Field Mapping Verification

**EAN Extraction** (`extract_ean` method):
- Line 3272: `selectors_config = self._get_selectors_for_domain(domain)`
- Line 3273: `selectors = selectors_config.get("field_mappings", {}).get("ean", [])`
- ✅ **Correct variable names used**
- ✅ **Correct nested key access**: `field_mappings → ean`

**Price Extraction** (`extract_price` method):
- Line 2190: `selectors = self._get_selectors_for_domain(urlparse(context_url).netloc)`
- Line 2191: `price_selectors = selectors.get("field_mappings", {}).get("price", [])`
- ✅ **Correct variable names used**

**URL Extraction** (`extract_url` method):
- Line 2210: `selectors = self._get_selectors_for_domain(urlparse(context_url).netloc)`
- Line 2211: `url_selectors = selectors.get("field_mappings", {}).get("url", [])`
- ✅ **Correct variable names used**

**Pagination** (category page processing):
- System reads `category_page.next_page_button_selector`
- ✅ **Correct config key accessed**

---

## 🔍 OTHER SUPPLIER COMPARISON

### PoundWholesale Cache Analysis

**Sample Products**:
```json
{"title": "'Welcome' Wellies Door Mat", "price": 1.18, "ean": "5055056750510"}
{"title": "Congratulations Balloons", "price": 0.54, "ean": "5060082931130"}
{"title": "It's A Girl Pink Plaque", "price": 0.71, "ean": "5010792236995"}
```

**Observations**:
- ✅ Each product has UNIQUE 13-digit EAN
- ✅ All products have valid prices
- ✅ No null EANs causing deduplication issues
- ✅ EAN extraction working correctly for PoundWholesale

**Why PoundWholesale Works**:
- Correct EAN selectors configured
- No conflicting pattern matches
- Each product generates unique key: `ean:5055056750510`, `ean:5060082931130`, etc.

---

## 📊 SOLUTIONS

### Solution 1: Fix EAN Extraction Priority (CRITICAL)

**Option A**: Skip pattern matching for angelwholesale.co.uk
**Option B**: Fix CSS selector to work with BeautifulSoup
**Option C**: Reverse priority (CSS selectors BEFORE pattern matching)

**Recommended**: **Option C** - Reverse Priority

**Implementation**:
```python
# Try CSS selectors FIRST
for selector in selectors:
    element = product_page_soup.select_one(selector)
    if element:
        return element.get_text(strip=True)

# THEN try pattern matching as fallback
for pattern in ean_patterns:
    matches = re.finditer(pattern, html_content, re.IGNORECASE)
    ...
```

### Solution 2: Fix EAN Selector for BeautifulSoup

**Current (doesn't work)**:
```json
".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)"
```

**Fixed for BeautifulSoup** (manual iteration):
Add to `extract_ean` method or use simpler selector:
```json
"ean": [
  ".specs-data"  // Get all, iterate to find Barcode row
]
```

Or implement custom logic:
```python
specs_rows = product_page_soup.select('.specs-row')
for row in specs_rows:
    cells = row.select('.specs-data')
    if len(cells) >= 2 and 'barcode' in cells[0].get_text(strip=True).lower():
        return cells[1].get_text(strip=True)
```

### Solution 3: Add Pagination Button Selector (IMMEDIATE)

**Update** `config/supplier_configs/angelwholesale.co.uk.json`:
```json
"category_page": {
  "next_page_button_selector": [
    "a.btn-load-more",
    ".btn-load-more"
  ],
  "pagination_method": "button",
  "infinite_scroll": false
}
```

### Solution 4: Clear Broken Cache (IMMEDIATE)

Delete cache file with incorrect EAN:
```bash
rm "OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json"
```

---

## 🎯 VERIFICATION CHECKLIST

Before implementing fixes:
- [x] Confirmed EAN pattern matching extracts same value for all products
- [x] Confirmed deduplication uses EAN-first priority
- [x] Confirmed CSS selector syntax incompatible with BeautifulSoup
- [x] Confirmed LOAD MORE button exists and is clickable
- [x] Confirmed pagination config has empty button selector
- [x] Verified scraper reads config correctly (variable names, keys)
- [x] Compared with working supplier (poundwholesale)

---

## 📋 IMPLEMENTATION PRIORITY

### Phase 1: Stop Deduplication (CRITICAL)
1. Delete broken cache file
2. Fix EAN extraction priority OR disable pattern matching for angelwholesale

### Phase 2: Enable Full Product Collection
1. Add LOAD MORE button selector to config
2. Change pagination_method from "scroll_and_wait" to "button"

### Phase 3: Improve EAN Extraction
1. Implement BeautifulSoup-compatible EAN extraction
2. Test on multiple products to ensure unique EANs

### Phase 4: Test & Validate
1. Run full extraction on first category
2. Verify all products have unique EANs
3. Verify all 61 products extracted (not just 40)
4. Verify no deduplication errors

---

## 🚨 CRITICAL NOTES

1. **DO NOT edit files yet** - investigation complete, awaiting user approval
2. **EAN pattern matching is the primary culprit** - all products get same EAN
3. **Pagination button exists but not configured** - 21 products missing
4. **Configuration reading is correct** - no variable name issues
5. **Other suppliers work fine** - issue is specific to angelwholesale EAN extraction
