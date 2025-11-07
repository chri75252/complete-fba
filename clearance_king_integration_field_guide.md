# Clearance King Integration Field Guide

## Verified Assets and Current Status
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\clearance-king_product_categories.txt` — LastWriteTime 2025-09-18 08:09:00, 155 category URLs detected via manual line count.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\supplier_configs\clearance-king.co.uk.json` — LastWriteTime 2025-06-27 01:48:31, lean selector file automatically resolved by `load_supplier_selectors()` for domain `clearance-king.co.uk`.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\supplier_configs\clearance-king.json` — LastWriteTime 2025-06-27 01:48:31, extended selector/map variant containing richer field metadata.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\tools\configurable_supplier_scraper.py` — LastWriteTime 2025-09-15 23:14:02; includes Clearance King specific parsing logic at `tools/configurable_supplier_scraper.py:2262`, `:2770`, and `:2940`.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\system_config.json` — LastWriteTime 2025-08-31 10:14:07; **currently contains no `clearance-king` workflow or credential blocks** (verified by search).

## Category Source Inventory
- Location: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\clearance-king_product_categories.txt`
- Count: 155 lines (command: `(Get-Content).Count`).
- Sample excerpt for confirmation:
  ```text
  https://www.clearance-king.co.uk/baby-kids/baby-accessories.html
  https://www.clearance-king.co.uk/baby-kids/baby-bath-time.html
  https://www.clearance-king.co.uk/baby-kids/baby-care.html
  https://www.clearance-king.co.uk/baby-kids/baby-changing.html
  https://www.clearance-king.co.uk/baby-kids/baby-feeding.html
  ```
- Recommendation: mirror the PoundWholesale handling by copying this list into a JSON payload (`config/clearance_king_categories.json`) once the workflow accepts dynamic filenames (see next section).

## Existing Selector Configuration (Confirmed Footprint)
- `clearance-king.co.uk.json` (lean profile):
  ```json
  {
      "field_mappings": {
          "product_item": ["li.item.product.product-item"],
          "title": ["a.product-item-link"],
          "price": ["span.price"],
          "url": ["a.product-item-link"],
          "image": ["img.product-image-photo"],
          "ean": [""],
          "barcode": [""]
      },
      "pagination": {
          "pattern": "?p={page_num}",
          "next_button_selector": "a.action.next"
      }
  }
  ```
  - Minimal selectors only; lacks product-page EAN/Barcode hooks. Useful for quick bootstrap but insufficient for full barcode harvesting.
- `clearance-king.json` (rich profile): adds multi-selector fallback matrices, description, stock status, brand, breadcrumb handling, and post-processing rules. Use this as the canonical reference when populating a new supplier package so the scraper can downgrade gracefully across layouts.

## Workflow Touchpoints That Already Reference Clearance King
- Barcode extraction override: `tools/configurable_supplier_scraper.py:2262-2283` detects textual patterns unique to Clearance King product pages.
- Navigation discovery hints: `tools/configurable_supplier_scraper.py:2770-2787` prioritises `.navigation ul li a` because the site runs Magento-style menus.
- Category heuristics: `tools/configurable_supplier_scraper.py:2940-2964` lists Clearance King specific keywords (`"clearance"`, `"pound"`, `"smoking"`, etc.) for URL vetting.
- **Gap confirmed**: `tools/passive_extraction_workflow_latest.py` still hardcodes the `poundwholesale` category JSON path (`:1834-1861`). Clearance King onboarding will require parameterising this lookup using the new supplier key before the workflow can ingest the text-based category file.

## Configuration Gaps to Close
1. **system_config.json additions**
   - Add credentials at `config/system_config.json:242` using:
     ```json
     "clearance-king.co.uk": {
       "username": "info@theblacksmithmarket.com",
       "password": "0Dqixm9c&"
     }
     ```
   - Insert a workflow block near `config/system_config.json:249`:
     ```json
     "clearance_king_workflow": {
       "supplier_name": "clearance-king.co.uk",
       "use_predefined_categories": true,
       "ai_client": null
     }
     ```
   - Update any financial or supplier-specific settings if Clearance King pricing deviates (VAT already typically standard at 20%).
2. **Passive workflow category loader**
   - Replace the literal `poundwholesale_categories.json` reference at `tools/passive_extraction_workflow_latest.py:1834` with logic that resolves `config/clearance_king_categories.json` (or a mapped filename) when `self.supplier_name == "clearance-king.co.uk"`.
3. **Output directory wiring**
   - Ensure `utils/path_manager.py` (current timestamp 2025-07-18 02:08:44) maps `clearance-king.co.uk` to dedicated cache folders before first run to avoid mixing with PoundWholesale artifacts.

## Authentication & Browser Requirements
- Login page: `https://www.clearance-king.co.uk/customer/account/login/`
- Credentials (verified from request):
  - Username: `info@theblacksmithmarket.com`
  - Password: `0Dqixm9c&`
- Runner should call `SupplierAuthenticationService.ensure_authenticated_session()` with these credentials before scraping (pattern identical to `run_custom_poundwholesale.py:73-88`).

## Manual Data Capture Needed From User
To finalise production selectors and confirm DOM stability, please provide the following via Chrome DevTools (logged-in session):
1. **Price element CSS selector**
   - Inspect a product listing and copy the full CSS path for the price span displayed **after login**.
2. **Product detail barcode selector**
   - Open any product page where a barcode/EAN is shown. Provide the CSS selector and DOM snippet (outerHTML) covering the barcode text.
3. **Pagination behaviour**
   - Confirm whether the `a.action.next` button remains visible after login on deep category pages (> page 5). If an infinite scroll appears instead, note the triggering JavaScript event names.
4. **In-stock indicator**
   - Capture the exact HTML block that toggles between “In stock” / “Out of stock” so we can wire `field_mappings.stock_status` appropriately.
5. **Any JavaScript-required interactions**
   - If categories rely on XHR calls or require filters to surface prices, record the network endpoints (copy URL + method) so headless Playwright sessions can whitelist them.

Provide each snippet in a text file or paste directly; note the category URL used for context. With these artefacts we can validate or update the rich supplier config and confirm the scraper’s dynamic fallbacks.

## Next-Step Checklist (Post-Data Collection)
1. Parameterise category file loading in `PassiveExtractionWorkflow` and drop a JSON copy of `clearance-king_product_categories.txt` for parity with other suppliers.
2. Extend `system_config.json` with credentials + workflow block, then add any Clearance King specific rate limits under the `suppliers` or `workflow_overrides` sections if required.
3. Sync `supplier_configs/clearance-king.json` into the canonical format expected by `load_supplier_selectors()` (ensure UTF-8 encoding) and prune redundant copies to avoid ambiguity.
4. Run `python run_custom_clearance_king.py --test-mode --max-products=5` (after creating the runner) to generate `OUTPUTS\FBA_ANALYSIS\linking_maps\clearance-king.co.uk\linking_map.json` and confirm timestamps in `OUTPUTS\CACHE\processing_states`.