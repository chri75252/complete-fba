# REVERT TRACKING - Dashboard V2 Fixes 2026-03-20

## Backup Location
`backup/dashboard_v2_fixes_20260320/`

## How to Revert
Copy backup files back to their original locations:
```
cp backup/dashboard_v2_fixes_20260320/api.py dashboard_v2_redesign/api.py
cp backup/dashboard_v2_fixes_20260320/app.js dashboard_v2_redesign/static/js/app.js
cp backup/dashboard_v2_fixes_20260320/index.html dashboard_v2_redesign/templates/index.html
cp backup/dashboard_v2_fixes_20260320/fba_report_filter.py tools/fba_report_filter.py
cp backup/dashboard_v2_fixes_20260320/fba_ai_analyst.py tools/fba_ai_analyst.py
cp backup/dashboard_v2_fixes_20260320/chat_orchestrator.py control_plane/chat_orchestrator.py
cp backup/dashboard_v2_fixes_20260320/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md
```

## Changes Made

### 1. dashboard_v2_redesign/api.py
- **Line 206-213**: Removed `nrows=2000` from `pd.read_csv()` so metrics use ALL CSV rows
- **Line ~214**: Added column name normalization (`ROI ( % )` -> `ROI`, etc.)
- **Line 125**: Added `report` query parameter to `get_supplier_metrics()`
- **Line ~203**: Added report override logic (use specific CSV when `report` param provided)
- **Line ~284**: Changed `.head(500)` to `.head(2000)` for chart data (browser perf cap)
- **Line ~300**: Added `data_sources` dict to return payload (file paths for each metric)

### 2. dashboard_v2_redesign/static/js/app.js
- **renderCategoryProfitChart()**: Bar labels now show `"CategoryName (count)"`, tooltip shows `"total profit + count products"`
- **renderProfitCompetitionChart()**: x-axis changed from `fba_seller_count` to `total_offer_count`, axis label updated, tooltip updated
- **renderSellerMixChart()**: Replaced FBA/FBM doughnut with Competition Level (Low 1-5 / Med 6-20 / High 20+) using `total_offer_count`
- **renderCategorySalesChart()**: Bar labels now show `"CategoryName (count)"`, tooltip shows `"X products with sales + total profit"`
- **fetchMetrics()**: Now passes `report` query param from `dashboardReportSelect` dropdown
- **After renderDashboard()**: Populates `dataSourcesPanel` with file paths and `dashboardReportSelect` dropdown with available reports

### 3. dashboard_v2_redesign/templates/index.html
- Added `Financial Report` dropdown (`dashboardReportSelect`) in sidebar before Auto Refresh
- Added color legend below Net Profit vs Selling Price chart
- Added color legend below Profit vs Competition chart
- Renamed "Seller Mix (FBA vs FBM)" heading to "Competition Level"
- Added collapsible "Data Sources" section at bottom of dashboard (before operator view)

### 4. tools/fba_report_filter.py (lines 207-214)
- T1: `ean_exact_match AND net_profit > 0 AND no CATEGORY_MISMATCH` (removed confidence >= 60 requirement)
- T2: `ean_exact_match` (any EAN match without profit or with category mismatch)
- T2: Non-EAN with confidence >= 40 and no flags (unchanged, but now explicitly T2 max for non-EAN)
- T3/T4: Unchanged

### 5. tools/fba_ai_analyst.py
- **call_openai()**: Added try/except, handles None content and empty choices (returns error string instead of crashing)
- **analyze_report()**: Creates per-run subfolder `run_{timestamp}/` inside output_dir
- All output files (run_config.json, batch_*.md, COMBINED_AI_ANALYSIS.md) now in run subfolder
- After completion, updates run_config.json with `completed_at`, `batches_processed`, `errors`

### 6. control_plane/chat_orchestrator.py
- **Line 1263**: Added `runner = params.get("runner_script", "")` variable
- **Line 1268**: Added `and not runner` to validation check (allows empty category_urls when runner_script provided)
- **Line 1442**: Same change at second validation block (line ~1446)

### 7. control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md
- Added "Main Workflow Rules" section after "Sandboxed Run Rules" (lines 45-53)
- Instructs LLM to use `enqueue_run` with empty `category_urls` and `runner_script` for main workflow
- Instructs LLM to call `read_processing_state` after enqueueing to show progress
