# PRD 04 v1.1: Conversational Chat + Product‑List Amazon Refresh (Sandboxed)

**Version**: 1.1  
**Date**: 2026-01-30  
**Status**: Draft (Aligned to current implementation; gaps noted)  
**Author**: Sisyphus (OhMyOpenCode)

---

## 0. Positioning vs PRD_03

This document is **PRD_04 v1.1**, covering:

1) **All PRD_03 chat UX requirements** (prose-first, deterministic tool selection, confirmation gating, JSON expanders)
2) A **new domain capability**: **Product‑List Amazon Refresh** (accept a list of supplier products in cached-products entry format, refresh Amazon metrics, write linking map entries, generate financial report)

PRD_04 is separate from PRD_03 because it adds a new tool + job type + runner.

---

## 1. Executive Summary

### 1.1 Problem

- Chat UI historically behaved like a tool console.
- The system lacked a first-class workflow to refresh Amazon data for a curated product list and re-run financials.

### 1.2 Solution

- Chat becomes a conversational control plane UI (PRD_03 UX).
- Introduce `enqueue_product_list_refresh` to queue a sandboxed job that:
  - writes a sandbox supplier cached-products file
  - searches Amazon (EAN-first, title fallback)
  - overwrites canonical Amazon cache files for freshness
  - writes a sandbox linking map
  - runs `tools.FBA_Financial_calculator.run_calculations(...)`

### 1.3 Hard Constraints (must hold)

- Do not modify core workflow engine (`tools/`, especially `tools/passive_extraction_workflow_latest.py`) unless explicitly approved.
- Sandboxing must prevent contamination of production supplier artifacts.
- Write tools must be UI-confirmed before enqueue.

---

## 2. Glossary

- **Sandboxed Category Analysis**: a sandboxed run of the existing workflow runner (`run_custom_*.py`) scoped to user-provided category URL(s).
- **Lookup / Read-only**: reading existing artifacts (linking map, cached products, etc.) without enqueueing a job.

- **Control Plane**: `control_plane/` job system that queues and runs work.
- **Sandbox Supplier**: unique supplier identity for isolation.
- **Canonical Amazon Cache File**: `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN_SAFE}.json`.

---

## 3. Current Implementation (Ground Truth)

This PRD is intentionally file-grounded and matches the current implementation.

### 3.1 Tool: enqueue_product_list_refresh

- **Tool name**: `enqueue_product_list_refresh`
- **Implementation**: `control_plane/tools/product_list_refresh.py`

**Request model** (`ProductListRefreshRequest`):
- `supplier_domain` (required)
- `products` (optional, list[dict])
- `products_path` (optional)
- `run_id` (optional)
- `notes` (optional)
- `dry_run` (optional)

**Behavior**:
- Creates `run_id` (uuid if not provided)
- Computes sandbox supplier:
  - `sandbox_supplier = f"{supplier_domain}__sandbox__{run_id[:8]}"`
- If `products` is provided inline:
  - writes `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/products_subset.json`
  - sets `products_path` to that file
- Writes job JSON to:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`
- Job payload uses:
  - `job_type = "run_product_list_refresh"`
  - `supplier_domain = sandbox_supplier` (note: it is not the raw supplier domain)
  - `source_supplier_domain = supplier_domain`

### 3.2 Worker Support

- Job type constant: `control_plane/job_types.py`
  - `JOB_TYPE_RUN_PRODUCT_LIST_REFRESH = "run_product_list_refresh"`

- Worker runner mapping: `control_plane/worker.py`
  - When `job_type == run_product_list_refresh`:
    - sets env var `CONTROL_PLANE_JOB_PATH=<running job json>`
    - runs `python -m control_plane.run_product_list_refresh`
    - default timeout: `refresh.timeout_seconds` or `7200`

### 3.3 Runner: control_plane.run_product_list_refresh

- Reads job via `CONTROL_PLANE_JOB_PATH`.
- Loads `products_subset.json` and (optionally) corrects `sandbox_supplier` from file.
- Writes sandbox cached-products file:
  - `OUTPUTS/cached_products/{sandbox_supplier_normalized}_products_cache.json`
  - where `sandbox_supplier_normalized = sandbox_supplier.replace(".", "-")`
- For each product:
  - determines query: `ean` (digits-only) else `title`
  - searches: `https://www.amazon.co.uk/s?k={query}`
  - selects first ASIN based on `data-asin="[A-Z0-9]{10}"`
  - visits PDP: `https://www.amazon.co.uk/dp/{asin}?th=1&psc=1`
  - extracts:
    - title: regex on `id="productTitle"`
    - price: regex for first `a-offscreen` value
  - if price is found and not `dry_run`:
    - writes canonical amazon cache file:
      - `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{asin}_{ean_safe}.json`
      - where `ean_safe` is digits-only supplier ean else `"N"`
    - backs up overwritten cache files:
      - `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/amazon_cache_backups/`
  - appends a linking row into a list (written at end)

- Writes sandbox linking map:
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json`

- Runs financial calculator (unless `dry_run`):
  - `tools.FBA_Financial_calculator.run_calculations(sandbox_supplier)`

---

## 4. Functional Requirements

### 4.1 Chat UX (inherits PRD_03)

- Prose-first assistant messages.
- Tool outputs shown in JSON expanders (not dumped into chat).
- Local LLM planner returns schema-valid JSON tool call.
- Confirmation gating for write tools.

### 4.2 Sandboxed Category Analysis (Option A: Full Workflow Run)

**Intent**: When a user provides one or more supplier category URLs (e.g., `https://angelwholesale.co.uk/Category/...`), the system must enqueue a **sandboxed** run of the existing workflow runner (`run_custom_*.py`) scoped to those category URLs.

**Routing requirement (critical)**:
- Category URL input must not default to `find_linking_entries` (read-only lookup). That tool is only valid when the user explicitly asks to view existing linking-map data.
- When category URLs are detected, the system must prefer `enqueue_run` and must set `category_urls=[...]`.

**Sandboxing requirement**:
- The sandbox run must override `workflows[workflow_key].supplier_name` to a sandbox supplier name:
  - `<supplier_domain>__sandbox__<run_id[:8]>`
- This guarantees that linking maps, processing state, and financial reports are written under a new sandbox supplier identity.

**Cache/backfill semantics (clarified)**:
- The workflow may use cached products for progress/backfill.
- The “amazon-only backfill” safety-net adds cached products to the Amazon-analysis queue only if they are **missing from the linking map**.
- In a sandbox run, the linking map referenced by the workflow is the **sandbox linking map** for the sandbox supplier name, not the production linking map.

### 4.3 Product‑List Refresh

**FR-PROD-1 (Input)**
- Accept product list in “cached-products entry format” (minimum required fields for meaningful run):
  - `title`, `price`, `url`
- Optional:
  - `ean`, `sku`, `availability`, `image_url`, `scraped_at`, etc.

**FR-PROD-2 (Amazon refresh)**
- For each product:
  - If EAN present → search by EAN.
  - Else → search by title.

**FR-PROD-3 (Canonical overwrite)**
- Overwrite canonical amazon cache files for freshness.

**FR-PROD-4 (Sandbox linking map)**
- Write linking map under `linking_maps/<sandbox_supplier>/`.

**FR-PROD-5 (Financial report)**
- Execute `tools.FBA_Financial_calculator.run_calculations(sandbox_supplier)`.

---

## 5. Output Contracts (Minimal Schemas)

### 5.1 Linking Map Rows (as written today)

`control_plane/run_product_list_refresh.py` writes a JSON list of dicts. Each row currently contains (some fields optional by outcome):

- `supplier_ean` (string; digits-only; may be empty)
- `supplier_url` (string)
- `supplier_title` (string)
- `supplier_price` (as provided in input)
- `amazon_asin` (string or null)
- `amazon_title` (string or null)
- `amazon_price` (float or null)
- `match_method` ("EAN" | "title" | "captcha" | "no_results" | "missing_query")
- `confidence` (0 or 1)

### 5.2 Amazon Cache JSON (as written today)

`control_plane/run_product_list_refresh.py` writes a minimal payload via `_minimal_amazon_payload(...)`:

- `asin_queried` (string)
- `asin` (string)
- `url` (string; `https://www.amazon.co.uk/dp/{asin}`)
- `_search_method_used` ("EAN" | "title")
- `scraped_at` (ISO string)
- `selleramp` (object; currently `{ "status": "not_run" }`)
- `keepa` (object; currently `{}`)
- Optional when known:
  - `title` (string)
  - `current_price` (float)
  - `ean_on_page` (string)
  - `eans_on_page` (list[string])

### 5.3 Supplier Cache JSON (as written)

- Path: `OUTPUTS/cached_products/{sandbox_supplier_normalized}_products_cache.json`
- Contents: list of product dicts (passed through from `products_subset.json`).

---

## 6. Naming + Normalization Rules

These rules are critical for correctness because the financial calculator uses mixed normalization:

- **Supplier cache file name**:
  - dots are replaced with hyphens: `supplier.replace(".", "-")`
  - file: `OUTPUTS/cached_products/{normalized}_products_cache.json`

- **Linking map directory**:
  - uses the supplier domain string as-is (can contain dots and `__sandbox__...`):
  - dir: `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_domain}/linking_map.json`

- **Financial reports directory**:
  - uses dots replaced with hyphens (`supplier.replace(".", "-")`).

- **Amazon cache file**:
  - `amazon_{asin}_{ean_safe}.json` where `ean_safe` is digits-only else `"N"`.

**Known risk (documented; not fixed yet)**:
- No-EAN uses `"N"` and can collide if multiple runs produce `amazon_{asin}_N.json`.

---

## 7. Known Gaps / Not Implemented (v1.1)

These are intentionally called out so operators don’t assume parity with the core extractor:

1) **Price extraction is naive**
   - Uses the first regex match of `a-offscreen` on the PDP HTML.

2) **No Keepa extension parsing**
   - `keepa` block is `{}`; no `product_details_tab_data`, no fee extraction.

3) **No EAN extraction from Amazon/Keepa**
   - Only carries supplier EAN if provided.

4) **Captcha handling is detection-only**
   - Marks result as `captcha` but does not attempt resolution.

---

## 8. Acceptance Criteria

- Chat UX: prose-first, JSON expanders, confirmation gating for write tools.

- Category analysis (sandboxed full workflow run):
  - a sandbox run is enqueued via `enqueue_run` when a category URL is provided
  - job files written under `OUTPUTS/CONTROL_PLANE/jobs/pending/` and `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/`
  - outputs written under sandbox supplier identity:
    - linking map at `OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json`
    - processing state at `OUTPUTS/CACHE/processing_states/<sandbox_supplier>_processing_state.json`
    - financial reports under `OUTPUTS/FBA_ANALYSIS/financial_reports/<sandbox_supplier_normalized>/`

- Product-list refresh:
  - supplier cache written under sandbox supplier identity
  - linking map created under `OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json`
  - canonical amazon cache written for products with extracted price
  - financial report generated under `OUTPUTS/FBA_ANALYSIS/financial_reports/<sandbox_supplier_normalized>/`

---

## 9. Operator Cheat Sheet (avoid wrong tool routing)

**Sandboxed category analysis (full workflow)**
- "run sandboxed category analysis" + category URL(s)
- "enqueue sandbox run" + category URL(s)
- "run workflow for these category URLs" + URL(s)

**Sandboxed product list refresh**
- "run sandboxed product list refresh" + `products_subset.json` path
- "refresh Amazon for this product list" + file path

**Read-only**
- "show existing linking map" + supplier domain
- "find linking entries" + supplier domain + filters

## 10. Rollback

- Changes are confined to `control_plane/`, `dashboard/`, and PRD docs.
- Rollback = restore files from `backup/`.

---

**END PRD_04 v1.1**
