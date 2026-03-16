# REVERT TRACKING — product_refresh_live_scrape_20260314

**Date:** 2026-03-14  
**Reason:** Surgical enhancements to product list refresh — live scraping + financial batch reporting  
**Status:** COMPLETE ✅

---

## Files Planned for Edit

| File | Scope of Change | Backup Path | Validation Status |
|---|---|---|---|
| `control_plane/run_product_list_refresh.py` | Import + instantiate `ConfigurableSupplierScraper`; **Option A:** replaced `scrape_products_from_url()` with direct per-product page visits via `get_page_content()` + `_extract_product_data_from_soup()`; cached product file updated with live data per category; `financial_report_batch_size` read + mid-run financial trigger; `matched=True` at ASIN-success site | `backup/product_refresh_live_scrape_20260314/control_plane/run_product_list_refresh.py` | COMPLETE |

---

## Files NOT Edited (confirmed)

- `tools/configurable_supplier_scraper.py` — imported only, not modified  
- `tools/amazon_playwright_extractor.py` — not touched  
- `tools/FBA_Financial_calculator.py` — imported only, not modified  
- `tools/passive_extraction_workflow_latest.py` — not touched  
- `control_plane/worker.py` — not touched  
- `control_plane/tools/product_list_refresh.py` — not touched  

---

## Restore Command

```powershell
Copy-Item `
  "backup\product_refresh_live_scrape_20260314\control_plane\run_product_list_refresh.py" `
  "control_plane\run_product_list_refresh.py" -Force
```

---

## Change Log

- [x] Change 1: Import `ConfigurableSupplierScraper`
- [x] Change 2: Instantiate scraper in `main()`
- [x] Change 3: `_flush_if_needed` upgrade (financial batch)
- [x] Change 4a: `await scraper._ensure_browser()` in `run()`
- [x] Change 4b: **Option A** — direct per-product page visits (replaces `scrape_products_from_url()`)
- [x] Change 4b-cache: Cache updated with live-scraped data per category
- [x] Change 4b-auth: **Supplier authentication** before product page visits (dynamic import of SupplierAuthenticationService, credentials from system_config.json)
- [x] Change 4b-auth-fix: Extracted base domain from sandbox string for correct credentials lookup
- [x] Change 4c: `matched=True` at ASIN-success site
- [x] Validation: import smoke test — PASSED
- [x] Validation: ruff F-check (logic/undefined) — PASSED (0 errors)
- [x] Validation: E501 line-length warnings — PRE-EXISTING, none new
