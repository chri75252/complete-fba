# Draft: Product-list refresh / linking map / browser investigation

## Requirements (confirmed)
- User wants a planning-grade investigation of the latest revert-tracking files, latest memory context, and current code paths.
- User wants the unresolved issue understood end-to-end before any further implementation attempt.
- Priority concerns:
  - linking map cleanup may have been documented but not actually applied as expected
  - browser fix may have been unnecessary or may have worsened crashes
- User explicitly wants exhaustive search and analysis before proceeding.

## Technical Decisions
- Mode: read-only planning/investigation only; no code implementation.
- Evidence sources in use:
  - latest `backup/*/REVERT_TRACKING.md`
  - current code in `control_plane/run_product_list_refresh.py`
  - current code in `utils/browser_manager.py`
  - supermemory / session context
  - background exploration agents

## Research Findings
- `backup/product_list_state_fix_20260403/REVERT_TRACKING.md` documents four fixes:
  - skip-path state persistence
  - finally-block state save
  - linking-map filtering via `allowed_keys`
  - browser hidden-tab HTTP-page preference
- `backup/browser_connection_stability_20260403/REVERT_TRACKING.md` documents:
  - scraper now receives explicit `browser_manager`
  - `BrowserManager.get_page()` reconnection fallback added
- `backup/revert_dedicated_run_page_20260403/REVERT_TRACKING.md` documents:
  - dedicated run-page approach was reverted
  - health-check restart behavior in `get_page()` had previously been identified as destructive
- Current `control_plane/run_product_list_refresh.py` contains:
  - `_load_existing_linking_results(..., allowed_keys=...)`
  - filtered `results` used to build `processed_keys`
  - skip-path state save logic
  - resumed-state preservation logic
  - scraper deferred until browser connection exists, then instantiated with `BrowserManager.get_instance()`
- Current `utils/browser_manager.py` contains:
  - reconnect attempt inside `get_page()` when `verify_connection_health()` fails
  - HTTP/HTTPS page preference when selecting a page from `context.pages`
  - dormant dedicated run-page methods still present (`ensure_run_page`, `release_run_page`)
- Run-artifact findings so far:
  - `logs/debug/run_custom_efghousewares-co-uk__sandbox__tabtest01__product_list_refresh_20260401_231551.log` and `_235008.log` show the dedicated run page being created and then becoming closed mid-run; one run also shows restart from inside browser management leading to `BrowserContext.new_page: Target page, context or browser has been closed`.
  - `logs/debug/run_custom_efghousewares-co-uk__sandbox__4e269fb4__product_list_refresh_20260403_123932.log` still used the singleton-browser path for scraper (`Using BrowserManager singleton page`).
  - `logs/debug/run_custom_efghousewares-co-uk__sandbox__4e269fb4__product_list_refresh_20260403_135311.log` shows auth hitting `Page.goto: Target page, context or browser has been closed` immediately after browser setup, but the product refresh loop then continues on reused page(s).
  - `logs/debug/run_custom_efghousewares-co-uk__sandbox__4e269fb4__product_list_refresh_20260403_221902.log` shows a failed launch when Chrome debug port was unavailable; despite that, linking map and financial processing still ran against existing artifacts.
  - `logs/debug/run_custom_efghousewares-co-uk__sandbox__4e269fb4__product_list_refresh_20260404_053149.log` shows the current filtered-resume path: 13 foreign entries excluded, 861 kept, manual-restored state loaded at resumption index 861, then the run proceeds until user cancellation.
  - `OUTPUTS/CONTROL_PLANE/status/4e269fb4-8eea-4589-97ad-d76c0a5a1e30.json` records the latest run as `cancelled`, with `linking_map_entries: 874`, `matched_asins: 191`, and no financial report artifact.
  - `OUTPUTS/CACHE/processing_states/efghousewares_co_uk__sandbox__4e269fb4_processing_state.json` contains explicit manual restore markers (`_writer_note: manual_restore_from_log_20260330_065122`) and counters fixed to the intended resume point.
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk__sandbox__4e269fb4/linking_map.json` currently contains mixed `match_method` values, including both `EAN` and at least one `title`, indicating that not all entries are legacy-pre-fix artifacts.

## Scope Boundaries
- INCLUDE:
  - trace what changed recently
  - identify rollback points
  - isolate likely root causes for linking-map mismatch and browser crash/latching behavior
  - prepare a surgical work plan once requirements are clear
- EXCLUDE:
  - direct code edits in this planning session
  - speculative fixes without evidence
  - changes outside the specific product-refresh / linking-map / browser path unless proven relevant

## Open Questions
- Did the user want the plan to prioritize pure reversion first, or root-cause validation before any revert?
- Which currently-present changes should be treated as suspect:
  - browser `get_page()` reconnection block
  - browser HTTP-page selection block
  - linking-map `allowed_keys` filter
  - skip/finally state-save fixes
- What test/verification strategy should govern the eventual work plan:
  - TDD
  - tests after implementation
  - no automated tests, agent QA only

## Latest User Direction
- User wants analysis anchored on run artifacts first, not immediate reversion.
- Time window requested: analyze runs from roughly 2026-03-23 / 2026-03-25 through today.
- User states they manually reverted the processing state to the intended resume point before starting the relevant run(s).
- User wants the investigation to finish by checking failed runs specifically.
