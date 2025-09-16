# Batch 2 Deduplication Implementation Status - Multi-Batch Stabilization Plan

## Primary Goal/Purpose
Implementation of **Batch 2** of a multi-batch stabilization plan for the Amazon FBA Agent System. The high-level goal of this batch is to **make the 2-step deduplication filter strict and consistent from end-to-end.** This eliminates the count mismatches between pre-filter "full" count and atomic save "new" count (e.g., "need 9 / add 1" mismatches).

The solution creates a shared normalization utility and uses it at every stage: data ingress (scraper), pre-filtering, and final atomic save, ensuring consistent deduplication throughout the entire workflow.

## Background Context
**Previous Work**: Batch 1 successfully implemented 6 surgical patches for state management, resume logic, and data integrity including:
- Suppressed workflow-side PTR prints
- Added manifest hash tracking and lineage
- Implemented denominator immutability guards
- Added pointer validation and clamping
- Implemented single-writer proof with UUID tracking
- Enhanced Amazon phase commits and proofs

## Batch 2 Implementation Status

### ✅ COMPLETED Steps:

#### **Step 2.1: Created Shared Normalization Utility**
**File**: `utils/normalization.py`
**Status**: ✅ COMPLETED

**Implementation**:
```python
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
import unicodedata

_TRACKERS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"}

def _nfc(s: str|None) -> str:
    return unicodedata.normalize("NFC", (s or "").strip())

def normalize_url(u: str|None) -> str:
    if not u:
        return ""
    raw = _nfc(u)
    p = urlparse(raw)
    host = p.netloc.lower()
    path = p.path.rstrip("/")
    q = [(k,v) for (k,v) in parse_qsl(p.query, keep_blank_values=False)
         if k and k.lower() not in _TRACKERS]
    return urlunparse((p.scheme.lower(), host, path, "", urlencode(sorted(q)), ""))

def normalize_ean(e: str|None) -> str|None:
    if not e: return None
    s = "".join(ch for ch in _nfc(e) if ch.isdigit())
    return s or None

def stable_key(url: str|None, ean: str|None) -> str:
    ne = normalize_ean(ean)
    if ne:  # **EAN-first authority**
        return f"ean:{ne}"
    nu = normalize_url(url)
    return f"url:{nu}" if nu else "anon:__missing__"
```

**Key Features**:
- **EAN-first authority**: Products with EANs get `ean:` prefixed keys
- **URL normalization**: Removes tracking parameters, normalizes case, removes trailing slashes
- **Unicode normalization**: Consistent NFC normalization
- **Fallback handling**: Graceful handling of missing data

#### **Step 2.2A: Updated Configurable Supplier Scraper (Ingress Normalization)**
**File**: `tools/configurable_supplier_scraper.py`
**Status**: ✅ COMPLETED

**Changes Made**:
1. **Added import**:
```python
# Import normalization utilities for Batch 2 deduplication fixes
from utils.normalization import normalize_url, normalize_ean
```

2. **Updated all product dictionary creation locations** (3 locations):
```python
# BEFORE:
product = {
    "title": title,
    "price": price,
    "url": product_url,
    "ean": ean,
    "sku": sku,
    # ... other fields
}

# AFTER:
product = {
    "title": title,
    "price": price,
    "url": product_url,
    "normalized_url": normalize_url(product_url),
    "ean": normalize_ean(ean),
    "sku": sku,
    # ... other fields
}
```

**Locations Updated**:
- `scrape_products_from_url` method (2 identical locations)
- `_extract_product_data_from_soup` method

**Impact**: All scraped products now have normalized URLs and EANs at the point of ingress.

#### **Step 2.2B: Updated Pre-Filter Logic with stable_key**
**File**: `tools/passive_extraction_workflow_latest.py`
**Method**: `_filter_unprocessed_products_with_hash_lookup`
**Status**: ✅ COMPLETED

**Changes Made**:

1. **Added stable_key import** (3 locations):
```python
# BEFORE:
from utils.normalization import normalize_url

# AFTER: 
from utils.normalization import normalize_url, stable_key
```

2. **Replaced EAN/URL separate filtering with stable_key approach**:
```python
# BEFORE - Separate EAN and URL sets:
processed_eans = {
    entry.get("supplier_ean")
    for entry in linking_map_data
    if entry.get("supplier_ean")
}
processed_urls = {
    normalize_url(entry.get("supplier_url"))
    for entry in linking_map_data
    if entry.get("supplier_url")
}

# AFTER - Single stable_key set:
processed_keys = {
    stable_key(entry.get("supplier_url"), entry.get("supplier_ean"))
    for entry in linking_map_data
    if entry.get("supplier_url") or entry.get("supplier_ean")
}
```

3. **Updated cache index building**:
```python
# BEFORE - Separate EAN and URL indexes:
self.product_cache_ean_index = {}
self.product_cache_url_index = {}
for product in cached_products:
    product_ean = product.get("ean", "")
    product_url = product.get("url", "")
    if product_ean:
        self.product_cache_ean_index[product_ean] = True
    if product_url:
        normalized_product_url = normalize_url(product_url)
        self.product_cache_url_index[normalized_product_url] = True

# AFTER - Single stable_key index:
self.product_cache_key_index = {}
for product in cached_products:
    product_url = product.get("url", "")
    product_ean = product.get("ean", "")
    key = stable_key(product_url, product_ean)
    self.product_cache_key_index[key] = True
```

4. **Simplified filtering loop**:
```python
# BEFORE - Complex EAN/URL logic:
# Check linking map EAN-based skipping
if product_ean and product_ean in processed_eans:
    skipped_by_linking_map_ean += 1
    skip_product = True
elif product_url and normalize_url(product_url) in processed_urls:
    skipped_by_linking_map_url += 1  
    skip_product = True

# AFTER - Simple stable_key logic:
product_key = stable_key(product_url, product_ean)
if product_key in processed_keys:
    skipped_by_linking_map += 1
    continue
```

5. **Updated cache checking**:
```python
# BEFORE:
cached_supplier_data = sum(
    1 for product in unprocessed_products
    if (product.get("ean") and product.get("ean") in self.product_cache_ean_index)
    or (product.get("url") and normalize_url(product.get("url")) in self.product_cache_url_index)
)

# AFTER:
cached_supplier_data = sum(
    1 for product in unprocessed_products
    if stable_key(product.get("url"), product.get("ean")) in self.product_cache_key_index
)
```

**Impact**: Pre-filter now uses consistent stable_key logic with EAN-first authority, eliminating inconsistencies between EAN and URL based filtering.

### ⏳ PENDING Steps:

#### **Step 2.2C: Update Atomic Save Deduplication**
**Status**: 🔄 IN PROGRESS - **NOT YET LOCATED**

**Target Pattern** (from specification):
```python
# Need to find and update:
seen = { (p.get("ean") or p.get("url")) for p in existing }
# Inside loop:
k = (p.get("ean") or p.get("url"))

# Should become:
seen = { stable_key(p.get("url"), p.get("ean")) for p in existing }
# Inside loop:
k = stable_key(p.get("url"), p.get("ean"))
```

**Issue**: The atomic save deduplication section was not found in the expected location. The search results showed a different deduplication pattern using URL-only logic:
```python
seen_urls = set()
for product in price_filtered_products:
    product_url = product.get("url")
    if product_url and product_url not in seen_urls:
        seen_urls.add(product_url)
        deduplicated_products.append(product)
```

**Next Action Required**: Need to locate the correct atomic save section that matches the Batch 2 specification pattern and update it to use stable_key logic.

#### **Step 2.3: Add Observability Log**
**Status**: ⏳ PENDING
**Target**: Add log line showing normalized pre-filter results:
```python
self.log.info(f"🔗 PRE-FILTER (normalized): IN={len(collected_urls)} skip={len(skip)} amazon_only={len(amazon_only)} full={len(full)}")
```

**Issue**: Need to locate where `collected_urls`, `skip`, `amazon_only`, and `full` variables exist in the pre-filtering logic.

### 🔍 ARCHITECTURAL INSIGHTS DISCOVERED

#### **1. Existing Normalization Complexity**
The codebase already had sophisticated URL normalization in multiple places, but inconsistent approaches:
- `_filter_unprocessed_products_with_hash_lookup` used `normalize_url` for URLs
- Different normalization logic existed in other parts
- No centralized EAN normalization
- No unified stable_key approach

#### **2. EAN-First Authority Pattern**
The `stable_key` function implements EAN-first authority:
- If EAN exists: `"ean:{normalized_ean}"`
- If only URL exists: `"url:{normalized_url}"`
- If neither: `"anon:__missing__"`

This ensures products are consistently identified by EAN when available, preventing URL variations from creating duplicates of the same EAN-identified product.

#### **3. Performance Optimization Pattern**
The existing code used separate hash indexes for EAN and URL lookups. The stable_key approach consolidates this into a single index, potentially improving performance and definitely improving consistency.

## Next Steps for Implementation Continuation

### **Immediate Actions Required**:

1. **Locate Atomic Save Section**: 
   - Search for the exact pattern mentioned in Batch 2 spec: `seen = { (p.get("ean") or p.get("url")) for p in existing }`
   - May be in a different method or workflow path
   - Alternative: Look for any deduplication logic that combines EAN and URL

2. **Update Atomic Save Logic**:
   - Replace existing logic with stable_key approach
   - Ensure consistency with pre-filter and ingress normalization

3. **Add Observability Logging**:
   - Find the pre-filtering section with `collected_urls`, `skip`, `amazon_only`, `full` variables
   - Add the specified log line for monitoring

4. **Verify Acceptance Criteria**:
   - Test that pre-filter "full" count matches atomic save "new" count
   - Verify URLs differing only by tracking parameters are treated as duplicates
   - Confirm observability log appears

### **Testing Strategy**:
- Create test cases with URLs that differ only by tracking parameters
- Verify EAN-first authority works (same EAN with different URLs should be treated as single item)
- Check that count mismatches are eliminated

### **Risk Assessment**:
- **Low Risk**: Changes are additive and use defensive programming patterns
- **Rollback Strategy**: All changes can be individually reverted
- **Impact**: Should eliminate the "need 9 / add 1" type mismatches in production

## Integration Points with Batch 1

The Batch 2 changes build upon Batch 1's stable state management:
- Uses the same stable_key normalization for linking map entries that Batch 1 state manager expects
- Maintains compatibility with Batch 1's immutability guards and resume logic
- Leverages Batch 1's single-writer proof UUID system for safe concurrent operation

## Key Files Modified

1. **`utils/normalization.py`** - ✅ New shared utility
2. **`tools/configurable_supplier_scraper.py`** - ✅ Ingress normalization
3. **`tools/passive_extraction_workflow_latest.py`** - ✅ Pre-filter stable_key logic (partial - atomic save still pending)

## Technical Debt Addressed

- **Normalization Inconsistency**: Centralized all URL/EAN normalization logic
- **Deduplication Mismatches**: EAN-first authority prevents same-product-different-URL duplicates
- **Performance**: Single hash index instead of separate EAN/URL indexes
- **Maintainability**: All normalization logic in one place with clear authority hierarchy