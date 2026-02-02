# Product‑List Refresh Gaps Report + Implementation Agent Prompt

**Date**: 2026-01-30  
**Scope**: `control_plane` Product‑List Refresh workflow (PRD_04)  
**Audience**: Implementation agent who will improve extraction fidelity  

---

## 0. Executive Summary

PRD_04’s product-list refresh workflow exists end-to-end, but the current runner (`control_plane/run_product_list_refresh.py`) writes **minimal Amazon cache payloads** with **naive price extraction** and **no Keepa/SellerAmp parsing**. This means:

- Financial reports can be generated, but they are likely to be **fee-inaccurate** and sometimes **price-missing**, causing empty/incorrect ROI calculations.
- The new workflow is sandbox-safe (supplier cache + linking map + financial reports are sandboxed), but it intentionally **overwrites canonical Amazon cache files** (by design) and therefore must be correct.

This report enumerates the top gaps, explains root causes, and provides an executor-ready prompt.

---

## 1. Ground Truth: What’s Implemented Today

### 1.1 Product-list refresh runner
File: `control_plane/run_product_list_refresh.py`

Key behaviors:
- Amazon search: `https://www.amazon.co.uk/s?k={query}`
- ASIN selection: first match of `data-asin="([A-Z0-9]{10})"`
- PDP visit: `https://www.amazon.co.uk/dp/{asin}?th=1&psc=1`
- Title extraction: regex on `id="productTitle"`
- Price extraction: **first match** of `a-offscreen">\s*([^<]+)`
- Amazon cache writes:
  - Path: `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{asin}_{ean_safe}.json`
  - `ean_safe` is digits-only supplier EAN or `"N"`.
  - Writes only if price is not `None`.
- Linking map writes:
  - Path: `OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json`
- Financial report runs:
  - `tools.FBA_Financial_calculator.run_calculations(sandbox_supplier)`

### 1.2 Financial calculator expects richer data (fees)
File: `tools/FBA_Financial_calculator.py`

- If `amazon["keepa"]["product_details_tab_data"]` exists, it extracts:
  - referral fee
  - fba fee
- If Keepa block absent, it falls back to config defaults.

---

## 2. Gaps (Issues + Root Causes + Impact)

### Gap A — Price extraction is naive and frequently wrong

**Where**:
- `control_plane/run_product_list_refresh.py` `_extract_price()`

**Root cause**:
- It parses raw HTML and takes the **first** `a-offscreen` match.
- Amazon pages often contain multiple `a-offscreen` spans:
  - list price, deal price, subscription price, other offers, shipping, etc.

**Impact**:
- Wrong `current_price` → ROI and profit wrong.
- Missing `current_price` → the runner does not write the amazon cache file at all, so the financial calculator can’t find data (or falls back to stale cache).

### Gap B — No Keepa fee extraction

**Where**:
- `control_plane/run_product_list_refresh.py` writes `keepa: {}` in `_minimal_amazon_payload()`.

**Root cause**:
- Control-plane runner does not parse the Keepa extension DOM / iframe.

**Impact**:
- `tools/FBA_Financial_calculator.py` will default fees:
  - referral fee = configured percent of price ex-VAT
  - fba fee = configured minimum
- That is acceptable as fallback, but not good enough for “refresh Amazon metrics” expectations.

### Gap C — No EAN extraction from Amazon / Keepa

**Where**:
- `control_plane/run_product_list_refresh.py` only echoes supplier EAN into `ean_on_page`/`eans_on_page`.

**Root cause**:
- There is no parsing of EAN fields from Amazon page content or from Keepa extension.

**Impact**:
- For products missing/dirty supplier EAN:
  - canonical cache naming uses `"N"` (risk of collisions)
  - linking map has weaker join keys

### Gap D — Attempting to reuse the “core” amazon extractor is currently unsafe

**Where**:
- `tools/amazon_playwright_extractor.py` hard-exits if OpenAI key missing:
  - checks `OPENAI_API_KEY` env
  - `sys.exit(1)` if absent

**Root cause**:
- The file loads OpenAI config on import and terminates the process early.

**Impact**:
- If the control-plane refresh runner imports this module in an environment where OpenAI is intentionally not configured, the job will crash instantly.

---

## 3. Recommended Fix Strategy (Safe, Minimal Blast Radius)

### Recommendation: Keep improvements inside `control_plane/`

Do not modify core workflow (`tools/`) unless explicitly approved.

Implement improvements in `control_plane/run_product_list_refresh.py`:

1) **Robust price extraction** (highest ROI fix)
   - Replace regex-first strategy with multi-strategy extraction:
     - Playwright locator-based DOM extraction (preferred)
     - JSON-LD offers fallback
     - Then regex fallback
   - Return a structured status when price missing: `price_status: unavailable|captcha|not_found`.

2) **Optional Keepa extension parsing**
   - If extension UI is present, parse the Keepa “Product Details” tab and store:
     - `keepa.product_details_tab_data` (dict)
   - This immediately upgrades fee extraction for the financial calculator.

3) **EAN extraction and no-EAN collision policy**
   - If Keepa exposes EAN(s), fill:
     - `ean_on_page`
     - `eans_on_page`
   - Add a no-EAN naming rule:
     - either `amazon_{asin}_N_{hash}.json`
     - or write `amazon_{asin}_N.json` but also write a second file keyed by title hash and enhance the `read_amazon_cache_by_asin` search.

4) **Do not import `tools/amazon_playwright_extractor.py`**
   - Unless the OpenAI hard-exit is removed (separate explicitly approved change).

---

## 4. Implementation Agent Prompt (copy/paste)

### 1) TASK
Improve product-list refresh extraction fidelity (price, Keepa fees, EANs) while keeping sandbox guarantees.

### 2) EXPECTED OUTCOME
- Product-list refresh writes canonical amazon cache files with:
  - reliable `current_price`
  - optional `keepa.product_details_tab_data` when available
  - `ean_on_page` / `eans_on_page` when discoverable
- Financial reports reflect improved fee accuracy (when Keepa is available).

### 3) REQUIRED TOOLS
- Repo file reads/edits only.
- Python compilation check (`python -m py_compile ...`) for modified files.

### 4) MUST DO
- Keep changes confined to `control_plane/` (especially `control_plane/run_product_list_refresh.py`).
- Preserve sandbox behavior:
  - supplier cache written for sandbox supplier
  - linking map written under `linking_maps/<sandbox_supplier>/`
- Preserve canonical overwrite behavior (amazon cache refresh) but improve correctness.
- Add a deterministic no-EAN collision strategy.

### 5) MUST NOT DO
- Do not edit `tools/passive_extraction_workflow_latest.py`.
- Do not import or depend on `tools/amazon_playwright_extractor.py` (it can `sys.exit(1)` without OpenAI env).
- Do not add `as any` / `@ts-ignore` (not applicable here, but same rule: no type suppression patterns).
- Do not commit.

### 6) CONTEXT
Relevant code:
- `control_plane/run_product_list_refresh.py` (current implementation)
- `control_plane/tools/product_list_refresh.py` (tool enqueue)
- `control_plane/worker.py` and `control_plane/job_types.py` (job execution)
- `tools/FBA_Financial_calculator.py` (fee extraction reads Keepa product_details_tab_data)
- `tools/amazon_playwright_extractor.py` (Keepa logic exists but is unsafe due to OpenAI hard-exit)

---

## 5. Verification Checklist

- `python -m py_compile "control_plane/run_product_list_refresh.py"`
- Create a dry-run job and verify:
  - linking map written
  - sandbox supplier cache written
- Run a non-dry-run job and verify:
  - at least one `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_*.json` updated
  - financial report CSV generated for sandbox supplier

---

**END**
