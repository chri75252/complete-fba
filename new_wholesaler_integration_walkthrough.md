# New Wholesaler Integration Walkthrough

## Verified Artifacts Consulted
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\run_custom_poundwholesale.py` (LastWriteTime: 2025-09-17 15:32:25)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\tools\passive_extraction_workflow_latest.py` (LastWriteTime: 2025-09-17 20:43:22)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\tools\configurable_supplier_scraper.py` (LastWriteTime: 2025-09-15 23:14:02)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\utils\fixed_enhanced_state_manager.py` (LastWriteTime: 2025-09-17 19:06:32)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\system_config.json` (LastWriteTime: 2025-08-31 10:14:07)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\system_config_loader.py` (LastWriteTime: 2025-08-11 15:40:21)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\poundwholesale_categories.json` (LastWriteTime: 2025-09-17 21:12:42)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\supplier_configs\poundwholesale-co-uk.json` (LastWriteTime: 2025-07-13 09:47:54)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\supplier_config_loader.py` (LastWriteTime: 2025-06-06 01:54:18)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\manifests` (verified directories `poundwholesale.co.uk` and `poundwholesale_co_uk` exist; LastWriteTime root: 2025-09-17 15:47:00)

## Detailed Integration Walkthrough

1. **Create a dedicated runner for the new supplier**
   - Duplicate `run_custom_poundwholesale.py` and rename it (for example `run_custom_<new_supplier_slug>.py`). Lines `run_custom_poundwholesale.py:61-98` show how the runner pulls `poundwholesale_workflow`, derives `supplier_name`, loads credentials, and hands control to `PassiveExtractionWorkflow`. Update the workflow key, printed banners, and any user-facing strings so they reflect the new wholesaler.
   - Ensure the new runner still imports `SystemConfigLoader`, `PassiveExtractionWorkflow`, `SupplierAuthenticationService`, and `BrowserManager` exactly as in lines `run_custom_poundwholesale.py:19-97`. The authentication flow will work for another supplier as long as valid credentials and selectors are supplied later in this checklist.

2. **Extend the global configuration**
   - Add the new supplier credentials under the `"credentials"` section in `config/system_config.json:242-247`, mirroring the structure used for `poundwholesale.co.uk`. Use the clean supplier domain as the key so `SystemConfigLoader.get_credentials()` can discover the entry.
   - Insert a new workflow block beside `"poundwholesale_workflow"` (see `config/system_config.json:249-253`). Give it a distinct key (for example `"<new_supplier_slug>_workflow"`) and set `"supplier_name"` to the domain that the workflow will use elsewhere.
   - If the new supplier has different VAT, fee, or price handling rules, extend the adjacent `"financial"`, `"supplier"`, or other sections in `system_config.json` so that the settings are accessible when `PassiveExtractionWorkflow` loads `self.system_config` at `tools/passive_extraction_workflow_latest.py:1371-1424`.

3. **Provide a category source file**
   - Use `config/poundwholesale_categories.json` as the template for category URL structure. Create a new file such as `config/<new_supplier_slug>_categories.json` that lists the new site’s category URLs.
   - Update `tools/passive_extraction_workflow_latest.py:1834-1861`, where `_get_authoritative_category_count` currently hard codes `poundwholesale_categories.json`, to resolve the file dynamically. A safe change is to construct the filename from `self.supplier_name` (or a mapping) so each supplier can load its specific list before falling back to `SystemConfigLoader`.
   - Ensure the new category file is UTF-8 encoded and that the URL list is exhaustive because the resumable workflow and `FixedEnhancedStateManager` rely on a complete category inventory.

4. **Prepare supplier-specific selectors**
   - Copy `config/supplier_configs/poundwholesale-co-uk.json` and adapt selectors, navigation, and pagination to match the new site. `tools/configurable_supplier_scraper.py:1661-1768` loads selector definitions by domain, first checking validated supplier packages and then the JSON files under `config/supplier_configs`.
   - Keep field names (`field_mappings`, `navigation_configuration`, etc.) consistent. The loader at `config/supplier_config_loader.py:20-94` strips the `www.` prefix, so name the file using the bare domain (for example `examplewholesaler.com.json`).
   - Update any login-selector or price-gating fields if the new supplier hides pricing until authentication. Those fields feed downstream into the scraper logic that raises authentication callbacks.

5. **Generalize `PassiveExtractionWorkflow` for multiple suppliers**
   - Constructor setup at `tools/passive_extraction_workflow_latest.py:1341-1521` relies on `self.supplier_name` for path building, but several later helpers still embed `poundwholesale`. Replace those literals with dynamic references:
     - `_get_authoritative_category_count` (lines `1834-1861`) should select the new category file by supplier rather than a fixed filename.
     - `_optimize_category_urls` (lines `4228-4241`) logs “Using raw URL (poundwholesale.co.uk)”. Update both the comment and the log call to interpolate `self.supplier_name` so other suppliers do not inherit the wrong label.
     - Resume validation (lines `7021-7029`) writes manifests to `OUTPUTS/manifests/poundwholesale.co.uk`. Route this through `path_manager.get_output_path("manifests", self.supplier_name, ...)` so each supplier has its own directory (mirroring the existing manifest folders verified in `OUTPUTS\manifests`).
     - The on-demand authentication helper (lines `11245-11275`) defaults the URL and fallback credentials to `poundwholesale.co.uk`. Use the workflow config’s `supplier_url` and credentials so the logic stays correct after the new workflow key is introduced.
   - After removing the hard-coded domain references, confirm that logging, manifest generation, and state checkpointing all draw their supplier identity from `self.supplier_name`. This keeps `FixedEnhancedStateManager.initialize_category_processing` (lines `utils/fixed_enhanced_state_manager.py:787-807`) accurate during resumptions.

6. **Ensure scraper state and caching directories are supplier aware**
   - The workflow already calls `path_manager.get_output_path(...)` at `tools/passive_extraction_workflow_latest.py:1386-1396` and `5139-5143` to produce supplier-scoped cache and manifest paths. Verify that `path_manager` can derive correct subdirectories for the new supplier; if not, extend its mapping so new domains resolve to dedicated folders under `OUTPUTS`.
   - Check that `tools/configurable_supplier_scraper.py` writes cache and URL filters per domain. Around lines `539-552` the scraper loads caches based on `domain`, so providing selectors under the correct filename automatically isolates cache entries for the new wholesaler.

7. **Add credentials and login automation**
   - Confirm the authentication helpers (`SupplierAuthenticationService.ensure_authenticated_session`) recognise the new site. If the login flow differs materially, extend that helper so it can drive the correct selectors after the runner passes `SupplierAuthenticationService` a page object (see `run_custom_poundwholesale.py:73-88`).
   - Update any static prompts or dashboard monitors that mention `poundwholesale` so operational alerts point to the right supplier when authentication fails.

8. **Prime output folders for resumable runs**
   - Create supplier-specific directories under `OUTPUTS` if they do not exist yet (for example `OUTPUTS\cached_products\<new_supplier_slug>_products_cache.json`, `OUTPUTS\FBA_ANALYSIS\linking_maps\<new_supplier_domain>\`). The workflow and state manager expect these paths to be present when they call `os.makedirs(..., exist_ok=True)` during initialization.
   - After the initial scraping pass, verify the state file (`OUTPUTS\CACHE\processing_states\<new_supplier_domain>_processing_state.json`) is generated so resumptions function like they do for `poundwholesale`.

9. **Register the new workflow entry point**
   - Update any automation or scheduling scripts that invoke `run_custom_poundwholesale.py` so they can call the new runner when processing the new supplier. Keep Chrome debugging settings and environment variables identical unless the new site needs a different port or concurrency cap.

10. **Test end-to-end before production runs**
    - Execute the new runner with a small product cap (`python run_custom_<new_supplier_slug>.py --test-mode --max-products=5`) after populating the configuration and selectors. Confirm that Amazon cache files, linking maps, financial reports, and processing state files appear under supplier-specific folders with current timestamps. This satisfies the mandatory verification directive before shipping the new workflow.

## Quick Reference Summary
- Runner template: duplicate `run_custom_poundwholesale.py:61-98` and change the workflow key, supplier name, and log banners for the new site.
- Configuration: add credentials and a workflow block in `config/system_config.json:242-253`; drop matching category URLs into a new `config/<supplier>_categories.json` file.
- Selectors: clone `config/supplier_configs/poundwholesale-co-uk.json`, adjust CSS selectors, and ensure the filename matches the new domain so `config/supplier_config_loader.py:20-94` can load it.
- Workflow hard-codes to neutralize: update `tools/passive_extraction_workflow_latest.py:1834-1861`, `4228-4241`, `7021-7029`, and `11245-11275` so they use `self.supplier_name` instead of `poundwholesale` literals.
- State and manifests: verify `path_manager.get_output_path` produces directories for the new supplier, and ensure `OUTPUTS\manifests\<supplier_domain>` exists for resume checks.