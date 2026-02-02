# Plan: Sandboxed Output Grouping + Product List Refresh Test

## TL;DR

- Confirm the last run was **headed** based on CDP + Keepa extraction evidence.
- Implement a **per-area sandbox grouping** so sandbox runs land under a predictable per-supplier folder tree.
- Run a **product list refresh** test using a file-based `products_subset.json` containing 6 products (2 each from 3 categories).

---

## 1) Headed vs Headless Explanation (Evidence-backed)

### Claim
Run `9a250a20-35a4-4c3b-88b7-203f06175dd8` was not headless (i.e., used a headed Chrome session with extensions).

### Why Keepa implies headed (with caveats)
- In many setups, browser **extensions do not run in headless Chromium**, so Keepa/SellerAmp-style extension UI generally implies headed execution.
- However, the strongest proof here is **CDP attachment to an existing Chrome instance** (not Playwright launching a new headless browser).

### Sources of truth (2–3)
- **CDP connection to existing Chrome**:
  - `logs/debug/run_custom_angelwholesale-co-uk__sandbox__9a250a20_20260201_013612.log` shows `Connecting to existing Chrome debug instance on port 9222` and successful connection.
- **Merged config explicitly headless=false**:
  - `OUTPUTS/CONTROL_PLANE/overrides/9a250a20-35a4-4c3b-88b7-203f06175dd8/system_config.merged.json` contains `chrome.headless: false` and `chrome.debug_port: 9222`.
- **Keepa extension DOM/iframe interaction**:
  - `OUTPUTS/CONTROL_PLANE/logs/9a250a20-35a4-4c3b-88b7-203f06175dd8.log` includes Keepa iframe detection/parsing and Keepa AG Grid parsing steps.

### Why you might not see the browser move
- The BrowserManager logs show it reused an existing context with multiple pages and reused an existing page; if the run navigates a background tab, you may not notice visually.
  - Evidence: `logs/debug/run_custom_angelwholesale-co-uk__sandbox__9a250a20_20260201_013612.log` contains `Using existing context with 4 pages` and `Reusing existing page in persistent context.`

### Hard requirement: “prove extensions + adblock active”
Add explicit runtime checks + log markers:
- Detect Keepa iframe present and log `EXT_KEEPA_OK`.
- Detect SellerAmp elements (if enabled) and log `EXT_SELLERAMP_OK`.
- Detect adblock effectiveness by counting sponsored results before/after filtering (or logging “sponsored filtered count”).

---

## 2) Implement per-supplier sandbox output grouping (Per-area grouping)

### Goal
Instead of flat dirs like:
- `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__9a250a20/...`

Create per-area sandbox grouping like:
- `OUTPUTS/FBA_ANALYSIS/linking_maps/sandboxes/angelwholesale.co.uk/9a250a20/linking_map.json`
- `OUTPUTS/FBA_ANALYSIS/financial_reports/sandboxes/angelwholesale.co.uk/9a250a20/...`
- `OUTPUTS/CACHE/processing_states/sandboxes/angelwholesale.co.uk/9a250a20/processing_state.json`
- `OUTPUTS/cached_products/sandboxes/angelwholesale.co.uk/9a250a20/products_cache.json`

### Constraints
- Must remain backward compatible with current paths.
- Dashboard and Control Plane Run Monitor must resolve the new paths.

### Implementation Tasks

1. **Add sandbox path helpers**
   - Update path resolution logic (likely `utils/path_manager.py` and/or dedicated helpers in workflow modules) to support a new optional “sandbox layout”.

2. **Update workflow output writers**
   - Ensure linking map writer and processing state writer can target the new sandbox directories.
   - Ensure financial report output directory uses the new sandbox directory.

3. **Update Control Plane `enqueue_run` sandbox naming**
   - Keep `sandbox_supplier` string for logical identity, but pass a `sandbox_run_id` (or `sandbox_dir_hint`) into overrides so workflows can compute the new grouped folder.
   - Primary reference: `control_plane/chat_orchestrator.py` `enqueue_run` tool handler.

4. **Update dashboard path resolution**
   - Extend `dashboard/metrics_core.py:resolve_paths()` to check sandbox grouped directories.
   - Current resolver only checks canonical names and misses sandbox state files.

5. **Migration strategy**
   - For each run, write outputs to *both*:
     - old flat layout (current)
     - new grouped layout
   - Once stable, optionally disable old layout (future decision).

### Acceptance Criteria
- Running a sandbox job produces files in the new grouped directories.
- Dashboard Run Monitor displays the sandbox paths (not canonical non-sandbox ones) for sandbox runs.
- No breaking changes to existing non-sandbox suppliers.

---

## 3) Product List Refresh Test (file-based)

### What the system supports
- Product list refresh is category-agnostic (can mix categories) because it consumes a list of product dicts.
  - References: `control_plane/tools/product_list_refresh.py` and `control_plane/run_product_list_refresh.py`.
- Chat currently supports **file-based** `products_path` only.
  - Reference: `control_plane/chat_orchestrator.py` tool schema for `enqueue_product_list_refresh`.

### Selected 6 products (2 each from 3 categories)

Source file: `OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json`

**Category 1:** `https://angelwholesale.co.uk/Category/A-To-Z-wholesale`
- 3pcs Mosaic Vehicles  by AtoZ Toys
  - url: `https://angelwholesale.co.uk/Item/3pcs-Mosaic-Vehicles--by-AtoZ-Toys-toy021614`
  - ean: `5012866069058`, price: `1.76`
- Abc Train Set Med  by AtoZ Toys
  - url: `https://angelwholesale.co.uk/Item/Wooden-Abacus--Med--by-AtoZ-Toys-toy021725`
  - ean: `5012866625032`, price: `1.18`

**Category 2:** `https://angelwholesale.co.uk/Category/All-Baby-and-child`
- Muslinz 6pk Green Quality Muslin Squares 100% Cotton
  - url: `https://angelwholesale.co.uk/Item/Muslinz-6pk-Blue-Quality-Muslin-Squares-Cotton-bac05399`
  - ean: `5055499001200`, price: `8.62`
- Silicone Teats Medium Flow 2 Pack by First Steps
  - url: `https://angelwholesale.co.uk/Item/Bottle-and-Teat-Brush-by-First-Steps-toy01231`
  - ean: `5015302105747`, price: `1.0`

**Category 3:** `https://angelwholesale.co.uk/Category/All-Bears`
- 15cm London Guardsman Bear Soft Plush By Keel Toys - Souvenir
  - url: `https://angelwholesale.co.uk/Item/25cm-London-Guardsman-Bear-Soft-Plush-By-Keel-Toys---Souvenir-toy08910`
  - ean: `5027148041455`, price: `10.07`
- Blue Star Baby Cot Blanket by Nursery Time 100x150cm
  - url: `https://angelwholesale.co.uk/Item/Nursery-Time-Sleepy-Bear-and-Polka-Dot-Baby-Blanket-in-a-Pink-Display-Box-bto01315`
  - ean: `5035320257174`, price: `11.36`

### How to run it (file-based)

1) Create a `products_subset.json` in an overrides folder (recommended):
- `OUTPUTS/CONTROL_PLANE/overrides/<new-run-id>/products_subset.json`

Use schema compatible with `control_plane/run_product_list_refresh.py`:
```json
{
  "schema_version": "1.0",
  "supplier_domain": "angelwholesale.co.uk",
  "sandbox_supplier": "angelwholesale.co.uk__sandbox__<runid8>",
  "products": [
    {"title":"...","url":"...","ean":"...","price":1.23},
    {"title":"...","url":"...","ean":"...","price":4.56}
  ],
  "notes": "6-product mixed-category test"
}
```

2) In chat UI, request a product list refresh using `enqueue_product_list_refresh` with `products_path`.

### Acceptance Criteria
- Worker runs `python -m control_plane.run_product_list_refresh` (see `control_plane/worker.py`).
- Outputs created:
  - Amazon cache JSONs written for products where a price is detected.
  - Linking map created at `OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json` (current behavior).
  - Financial report generated for sandbox supplier.

---

## 4) Next Actions

1. Implement explicit headed/extension/adblock verification logs.
2. Implement per-area sandbox grouping paths + dashboard resolver updates.
3. Run the product list refresh test using `products_subset.json`.

