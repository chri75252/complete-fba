# Analysis Report: Multi-Category Product Discrepancy & Workflow Logic

**Date:** 2025-11-28
**Status:** Analysis Complete
**Triangulation Protocol:** Applied (Logs + Code + Data)

## 1. User Hypothesis Verification
**Hypothesis:** The system skips supplier extraction because products are already in the cache from *other* categories (multi-category overlap).
**Verdict:** ✅ **CONFIRMED**

### Evidence (Triangulation)
1.  **Logs (Symptom):**
    *   `Skipping: ... 26 in cache`
    *   `Products to process: 0` (Supplier Extraction)
    *   This confirms the system believes 26 products are already cached.
2.  **Data (State):**
    *   User verified the cache file only contains **2 products** with `source_url = Baby-Socks-and-Booties`.
    *   **Conclusion:** The other **24 products** exist in the cache but are associated with *different* categories (e.g., `All-Shop-by-age`).
3.  **Code (Logic):**
    *   **File:** `utils/url_filter.py`
    *   **Function:** `filter_urls`
    *   **Logic:** `cached_urls = {normalize_url(p.get("url")) for p in cached_products}`
    *   **Observation:** The filter checks if the **normalized URL** exists in the *entire* cache. It does **not** check the category.
    *   **Result:** A product scraped in Category A is correctly identified as "cached" when encountered in Category B. This is intended behavior to prevent re-scraping the same product.

## 2. Critical Bug Identified: The "2 vs 26" Discrepancy
**Issue:** The user observed that while 26 products were skipped (identified as cached), only **2** were actually processed in the Amazon Analysis phase.

### Root Cause Analysis
There is a **logic mismatch** between the *Filtering* step and the *Retrieval* step in `passive_extraction_workflow_latest.py`.

**Step 1: Filtering (Correct)**
*   Uses `normalize_url`.
*   Identifies 26 matches.
*   Adds 26 URLs to `needs_amazon_only`.

**Step 2: Retrieval (Broken)**
*   **Location:** `tools/passive_extraction_workflow_latest.py` (Line ~7091)
*   **Code:** `prod = next((p for p in cached_products if p.get('url') == url), None)`
*   **Defect:** This uses an **EXACT STRING MATCH** (`==`).
*   **Scenario:**
    *   Scraper returns: `https://.../productA`
    *   Cache contains: `https://.../productA?sid=123` (or similar variation)
    *   `normalize_url` says: **MATCH** (Filter passes 26).
    *   `==` says: **NO MATCH** (Retrieval fails for 24).
    *   **Result:** 24 products are silently dropped from the Amazon queue. Only the 2 that happen to match exactly are processed.

## 3. Proposed Remediation Plan

### Step 1: Fix Retrieval Logic
Update the retrieval loop in `passive_extraction_workflow_latest.py` to use `normalize_url` for matching, ensuring it aligns with the filter logic.

```python
# Current (Broken)
prod = next((p for p in cached_products if p.get('url') == url), None)

# Proposed (Fixed)
target_norm = normalize_url(url)
prod = next((p for p in cached_products if normalize_url(p.get('url')) == target_norm), None)
```

### Step 2: Re-Apply Crash Fix
The `NameError: name 'absolute_cat_index' is not defined` is a genuine bug that **will** crash the script if not fixed. I must re-apply the fix to use `category_index`.

### Step 3: Verify Pagination
Ensure the pagination fix (IIFE in `angelwholesale.co.uk.json`) remains in place to ensure full product discovery.

## 4. Execution
I await your approval to proceed with these code changes.
