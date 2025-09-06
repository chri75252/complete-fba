# Product Cache Save Fix - Requirements Document

## Introduction

The Amazon FBA system currently fails to update the supplier product cache file during supplier extraction when using the "prefiltered" path. Root cause:

- In `tools/configurable_supplier_scraper.py`, `scrape_products_from_prefiltered_urls(...)` does **not** call the progress callback after extracting each product, so the workflow's periodic cache-save logic never triggers. [EVID: configurable_supplier_scraper.py:scrape_products_from_prefiltered_urls (no callback after append)] 

- The URL-based path does call the callback, which is why product cache saves occur there. [EVID: configurable_supplier_scraper.py:scrape_products_from_url (callback present)]

- The workflow already creates and wires a per-product progress callback that drives per-product cache saves at `supplier_cache_control.update_frequency_products` cadence; we must ensure it's invoked from the prefiltered path. [EVID: passive_extraction_workflow_latest.py:_create_product_progress_callback and set_progress_callback()]

## Requirements

### R1: Progress Callback Integration (Prefiltered Path)

**User Story:** As an operator, I want the cache file to update every N products when using the prefiltered extraction path so I don't lose data on interruption.

**Acceptance Criteria**

1. In `scrape_products_from_prefiltered_urls(filtered_urls, ...)`, **after** a product is parsed and **after** it's appended to the shared `product_accumulator`, the scraper **MUST** call:

```python
self.progress_callback('supplier_extraction', i+1, len(filtered_urls), product_url, product)
```

(only if `self.progress_callback` is set).  

[EVID: configurable_supplier_scraper.py:scrape_products_from_prefiltered_urls (currently missing)]

2. The call site MUST use `total_products = len(filtered_urls)` for consistency with progress math.

3. On runs where `update_frequency_products=1`, cache saves MUST occur per product (see R3 logs).

### R2: Consistent Progress Tracking (All Scraper Paths)

**User Story:** I want the same telemetry across scraping methods so monitoring and recovery are reliable.

**Acceptance Criteria**

1. The prefiltered path MUST use the **same** progress callback signature used by the URL-based path:

```python
('supplier_extraction', product_index, total_products, product_url, product_data)
```

[EVID: configurable_supplier_scraper.py:scrape_products_from_url (signature)]

2. The workflow MUST remain the sole place that decides cache-save cadence; scraper does not implement its own save. (No change required.)

### R3: Cache Save Verification (Workflow-Driven)

**User Story:** I need explicit proof that the cache persisted.

**Acceptance Criteria**

1. When the progress callback fires and the modulo/frequency condition is met, the workflow MUST log its **per-product save check** lines (examples):

- `"🔍 CACHE CHECK: Product X, frequency=..., enabled=..."`  
- `"🔍 CACHE CHECK: List length=..., modulo=..."`

These confirm the callback path was reached. [EVID: passive_extraction_workflow_latest.py:_create_product_progress_callback 'CACHE CHECK' logs]

2. After the save operation, the run MUST show the atomic save log (e.g., WindowsSaveGuardian) with entry counts. (Existing behavior; no code change, but this is part of acceptance.)

3. On error, workflow MUST log a non-fatal error and continue.

### R4: Backward Compatibility

**User Story:** The fix must not break other flows.

**Acceptance Criteria**

1. No changes to the workflow's save logic—only ensure the prefiltered scraper path **invokes** it through the callback. [EVID: passive_extraction_workflow_latest.py:set_progress_callback() call before scraping]

2. `scrape_products_from_url(...)` remains unchanged and continues calling the callback as-is. [EVID: configurable_supplier_scraper.py:scrape_products_from_url]

3. Existing config keys (e.g., `supplier_cache_control.update_frequency_products`) continue to control behavior.

## Files to Modify

1. `tools/configurable_supplier_scraper.py`  
   - Inside `scrape_products_from_prefiltered_urls(...)`, **add** the progress-callback invocation immediately after appending to `product_accumulator`.

2. `tools/passive_extraction_workflow_latest.py`  
   - **No code changes expected.** Verify that `set_progress_callback(self._create_product_progress_callback(...))` occurs before scraper calls, and that the callback logs the "CACHE CHECK" lines and performs the save at the configured frequency.

## Concrete Code Anchor (DO apply)

**File:** `tools/configurable_supplier_scraper.py`  
**Method:** `scrape_products_from_prefiltered_urls(...)`  
**Insertion point:** Inside the `if product:` block, **right after** `product_accumulator.append(product)`.

```python
# NEW — trigger workflow's per-product cache-save path
if self.progress_callback:
    try:
        self.progress_callback(
            'supplier_extraction',
            i + 1,
            len(filtered_urls),
            product_url,
            product,
        )
    except Exception as cb_err:
        log.debug(f"⚠️ progress_callback failed at {i+1}: {cb_err}")
```

## Test & Acceptance (ONLY for product-cache saving)

**Scenario:** filtered list of 3 URLs, update_frequency_products=1.
**Expect:** For each product:
- Workflow logs CACHE CHECK ... (proof callback fired) and then an atomic save log with updated counts.
- Total saves ≥ extracted products.

**Scenario:** update_frequency_products=2.
**Expect:** Saves occur on products 2, 4, 6, …; callback logs on every product.

**Scenario:** Callback exception simulation.
**Expect:** Non-fatal ⚠️ progress_callback failed ... log; scraping continues; later saves still occur on next product.

## Evidence Pointers

- Workflow creates callback and performs modulo/frequency checks: [EVID: passive_extraction_workflow_latest.py:_create_product_progress_callback lines with CACHE CHECK]
- Workflow sets callback before scraping and passes all_products as accumulator: [EVID: passive_extraction_workflow_latest.py:set_progress_callback + call sequence]
- Prefiltered method currently lacks callback call: [EVID: configurable_supplier_scraper.py:scrape_products_from_prefiltered_urls (no callback)]
- URL-based method calls callback: [EVID: configurable_supplier_scraper.py:scrape_products_from_url (callback present)]