# Product Cache Save Fix - Design Document

## Overview

**Goal (now):** Make the prefiltered path save supplier products to the cache at the configured cadence by invoking the existing workflow progress callback after each successful extraction.

**Secondary (future-proof, zero-risk):** Enrich the **callback payload** (inside `product` dict only), and add minimal, parseable logs so the next phase can reconstruct state/resume points deterministically—without changing signatures, control flow, or introducing new persistence.

This design implements a surgical fix with future-proofing metadata that enables better state reconstruction and resume capabilities without any architectural changes.

## Architecture

The current system architecture remains unchanged. The fix operates within the existing callback-driven cache save mechanism:

```
PassiveExtractionWorkflow
├── Creates progress callback (_create_product_progress_callback)
├── Sets callback on scraper (set_progress_callback)
├── Calls scraper method
└── Progress callback handles periodic cache saves

ConfigurableSupplierScraper
├── scrape_products_from_url ✅ (calls progress callback)
└── scrape_products_from_prefiltered_urls ❌ (missing progress callback)
```

**Design Principle:** Maintain the existing separation of concerns where the workflow controls cache save logic and the scraper only triggers it via callbacks.

## Components and Interfaces

### Modified Component: ConfigurableSupplierScraper

**File:** `tools/configurable_supplier_scraper.py`
**Method:** `scrape_products_from_prefiltered_urls`

**Current Interface (unchanged):**
```python
async def scrape_products_from_prefiltered_urls(
    self, 
    filtered_urls: List[str], 
    category_url: str = None, 
    product_accumulator: List = None
) -> List[Dict]
```

**Internal Behavior Change:**
- Add progress callback invocation after successful product extraction
- Use identical signature to `scrape_products_from_url` for consistency
- Include error handling to prevent callback failures from breaking extraction

### Unchanged Components

**PassiveExtractionWorkflow:**
- No code changes required
- Existing `_create_product_progress_callback` handles cache save logic
- Existing `set_progress_callback` wires the callback to the scraper

**Progress Callback Interface:**
```python
progress_callback(
    operation_type: str,      # 'supplier_extraction'
    product_index: int,       # 1-based index (i+1)
    total_products: int,      # len(filtered_urls)
    product_url: str,         # Current product URL
    product_data: dict        # Extracted product data
)
```

## Data Models

No data model changes required. The fix operates within existing data structures:

- `product_accumulator` (List[Dict]) - Shared list for real-time product collection
- `filtered_urls` (List[str]) - Pre-filtered URLs for extraction
- `product` (Dict) - Individual product data structure

## Error Handling

**Progress Callback Error Handling:**
```python
if self.progress_callback:
    try:
        self.progress_callback(...)
    except Exception as cb_err:
        log.debug(f"⚠️ progress_callback failed at {i+1}: {cb_err}")
```

**Design Rationale:**
- Non-fatal error handling ensures extraction continues even if callback fails
- Debug-level logging prevents log spam while maintaining visibility
- Exception isolation prevents callback issues from breaking the main extraction loop

**Error Recovery:**
- If callback fails on product N, extraction continues to product N+1
- Next successful callback will trigger cache save with accumulated products
- No data loss occurs due to callback failures

## Testing Strategy

#### Tests (Today)

**Test 1: N=1 (Save Every Product)**
- Configure `update_frequency_products=1`
- Expect "CACHE CHECK …" logs and atomic save after each product
- Verify cache file grows with each extraction

**Test 2: N=2 (Save Every 2nd Product)**  
- Configure `update_frequency_products=2`
- Expect saves on products 2, 4, 6, … with callback logs on every product
- Verify callback fires for all products but saves occur at configured frequency

**Test 3: Callback Error Simulation**
- Raise exception inside callback on product 2 of 4
- Verify scraper continues to products 3 and 4
- Verify next product still triggers save
- Verify debug log shows callback failure

**Test 4: No Accumulator Edge Case**
- Call method with `product_accumulator=None`
- Expect one warning: "Prefiltered path: no product_accumulator; periodic saves may not trigger."
- Verify no periodic saves occur (documented behavior)

#### Future-Proofing Validation

**Metadata Enrichment:**
- Verify `product["__cb_meta"]` contains all required fields:
  - `phase`: "supplier_extraction"
  - `category_url`: Current category URL
  - `attempt_index`: 1-based index
  - `total_in_batch`: Length of filtered URLs
  - `accumulator_len`: Current accumulator size
  - `ts_epoch`: Timestamp for ordering

**URL Normalization:**
- Verify `product["normalized_url"]` field is added
- Test with various URL formats (www, trailing slashes, etc.)
- Verify normalization handles edge cases gracefully

**Parseable Logging:**
- Verify INFO log format: "🔄 REAL-TIME: appended=%s idx=%s/%s acc_len=%s url=%s"
- Verify log contains accurate accumulator length and index information

### Acceptance Testing

**Log Pattern Verification:**
```
🔍 CACHE CHECK: Product 1, frequency=1, enabled=True
💾 PERIODIC CACHE SAVE: Saved 1 products to cache (every 1 products)
🔍 CACHE CHECK: Product 2, frequency=1, enabled=True
💾 PERIODIC CACHE SAVE: Saved 2 products to cache (every 1 products)
```

**File System Verification:**
- Cache file exists and grows with each save
- File size increases appropriately
- JSON structure remains valid

## Implementation Details

### Constraints

* Do **not** change the workflow's callback signature or ownership of save cadence.
* Do **not** write any new state files or modify the processing-state schema yet.
* Keep all additions backward-compatible and optional.

### Required Changes

#### 1. Add Progress Callback Call in Prefiltered Path

**File:** `tools/configurable_supplier_scraper.py`
**Method:** `scrape_products_from_prefiltered_urls(...)`
**Insertion point:** Immediately **after** `product_accumulator.append(product)` in the `if product:` block.

```python
# Ensure we didn't silently run without a shared accumulator
if product_accumulator is None:
    log.warning("Prefiltered path: no product_accumulator; periodic saves may not trigger.")

# Attach future-proof metadata INSIDE the product dict (no signature change)
# This will help the next step (state/resume) without altering current behavior.
meta = product.setdefault("__cb_meta", {})
meta.update({
    "phase": "supplier_extraction",
    "category_url": category_url,
    "attempt_index": i + 1,                       # 1-based attempt index
    "total_in_batch": len(filtered_urls),
    "accumulator_len": len(product_accumulator) if product_accumulator is not None else None,
    "ts_epoch": __import__("time").time(),        # monotonic-ish stamp for ordering
})

# Trigger workflow-controlled cache save path
if getattr(self, "progress_callback", None) and callable(self.progress_callback):
    try:
        self.progress_callback(
            "supplier_extraction",
            i + 1,
            len(filtered_urls),
            product_url,
            product,
        )
    except Exception as cb_err:
        log.debug(f"⚠️ progress_callback failed at {i+1}: {cb_err}")
```

#### 2. (Optional, Safe) Normalize URL Field for Dedupe Parity

*Keep it local; don't import new modules beyond stdlib. If a normalized field already exists, skip.*

```python
def _normalize_url_for_cache(u: str) -> str:
    try:
        from urllib.parse import urlsplit, urlunsplit
        sp = urlsplit(u.strip())
        netloc = sp.netloc.lower().removeprefix("www.")
        path = sp.path or "/"
        return urlunsplit((sp.scheme.lower(), netloc, path.rstrip("/"), "", ""))
    except Exception:
        return u

product.setdefault("normalized_url", _normalize_url_for_cache(product_url))
```

#### 3. Emit Parseable INFO Line Per Product

Add this right before/after the callback to aid later timeline/state reconstruction (no behavior change):

```python
log.info(
    "🔄 REAL-TIME: appended=%s idx=%s/%s acc_len=%s url=%s",
    bool(product_accumulator is not None),
    i + 1, len(filtered_urls),
    len(product_accumulator) if product_accumulator is not None else None,
    product.get("normalized_url", product_url),
)
```

### Consistency with Existing Implementation

The callback invocation matches the pattern used in `scrape_products_from_url`:

**Existing Pattern:**
```python
self.progress_callback('supplier_extraction', i+1, len(all_product_urls), product_url, product)
```

**New Pattern:**
```python
self.progress_callback('supplier_extraction', i+1, len(filtered_urls), product_url, product)
```

**Key Consistency Points:**
- Same operation type: `'supplier_extraction'`
- Same 1-based indexing: `i+1`
- Same total calculation: `len(url_list)`
- Same parameter order and types

## Performance Considerations

**Minimal Performance Impact:**
- Single function call per product (microseconds)
- No additional I/O operations in scraper
- Cache save frequency controlled by existing configuration

**Memory Impact:**
- No additional memory allocation
- Reuses existing product data structures
- No change to memory management patterns

**I/O Impact:**
- Cache saves controlled by `update_frequency_products` setting
- No change to existing I/O patterns
- Atomic saves prevent corruption (existing mechanism)

## Security Considerations

**No Security Impact:**
- No new external interfaces
- No changes to data validation
- No changes to file permissions or paths
- Uses existing atomic save mechanism

## Deployment Considerations

**Zero-Downtime Deployment:**
- Backward compatible change
- No configuration changes required
- No database migrations needed
- Can be deployed during active runs (will take effect on next extraction)

**Rollback Strategy:**
- Simple code revert if issues arise
- No data migration required for rollback
- Existing cache files remain valid

**Monitoring:**
- Existing log patterns will show cache save activity
- No new monitoring requirements
- Existing error handling patterns apply

## Future-Proofing Benefits

### Why These Refinements Help the Next Phase (Tomorrow)

* `product["__cb_meta"]` gives you **phase**, **attempt index**, **batch size**, **category context**, and **timestamps**—all without touching the state file. That's enough to:
  * Reconstruct accurate **progress** and **resume hints** from logs+cache alone.
  * Cross-check for **drift** between cache events and state updates when you harden the state manager.

* `normalized_url` aligns supplier cache entries with the duplicate filter's worldview, reducing ambiguity when you add **resume-point validation** and **URL-based dedupe**.

### Acceptance (Today)

* No signature changes anywhere.
* Prefiltered path now produces the same save behavior and log patterns as the URL path.
* New metadata/logs appear but do not change control flow or persistence schema.