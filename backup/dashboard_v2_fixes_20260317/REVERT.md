# Revert Guide — Dashboard V2 Fixes (2026-03-17)

## What was changed

| File | Backup |
|------|--------|
| `dashboard_v2_redesign/api.py` | `backup/dashboard_v2_fixes_20260317/api.py.bak` |
| `dashboard_v2_redesign/templates/index.html` | `backup/dashboard_v2_fixes_20260317/index.html.bak` |
| `dashboard_v2_redesign/static/js/app.js` | `backup/dashboard_v2_fixes_20260317/app.js.bak` |
| `tools/fba_ai_analyst.py` | `backup/dashboard_v2_fixes_20260317/fba_ai_analyst.py.bak` |
| `tools/fba_report_filter.py` | `backup/dashboard_v2_fixes_20260317/fba_report_filter.py.bak` |

## Core workflow scripts — UNTOUCHED
- `tools/passive_extraction_workflow_latest.py` — NOT modified
- `tools/configurable_supplier_scraper.py` — NOT modified
- `tools/amazon_playwright_extractor.py` — NOT modified
- `tools/FBA_Financial_calculator.py` — NOT modified
- `run_custom_*.py` — NOT modified

## Changes made

### api.py
1. **Fix 1** (line ~159): `total_products` overridden from cached_products file count
2. **Fix 2** (line ~210-214): `_norm_ean` handles scientific notation (e.g. `5.03E+12`)
3. **Fix 3** (line ~189): Added `[METRICS-DEBUG]` logging for CSV block
4. **Fix 4** (after line ~482): New `GET /api/categories/{supplier}` endpoint
5. **Fix 5** (line ~488+): `run_ai_analysis` accepts `supplier` param; category filter uses cached products lookup
6. **Fix 6** (line ~332): `get_analysis` accepts `report` query param

### index.html
1. **Fix 7** (line ~564-568): Category filter → `<select>` dropdown instead of text input
2. **Fix 8** (line ~686+): Analysis tab gains Financial Report `<select>` dropdown

### app.js
1. **Fix 9** (after line ~662): New `loadAiCategories()` function
2. **Fix 10** (after loadAiCategories): New `loadAnalysisReports()` function
3. **Fix 11** (line ~672+): `aiFilterToggle` calls `loadAiCategories()` when category mode selected
4. **Fix 12** (line ~700+): `runAiAnalysis` sends `supplier` in request body; category filter reads select value
5. **Fix 13** (line ~779-781): `setupRefresh()` called on supplier/lineage change
6. **Fix 14** (line ~785+): Init block calls `loadAiCategories()` and `loadAnalysisReports()`
7. **Fix 15** (line ~815+): `loadAnalysis()` sends `report` param

### fba_ai_analyst.py
1. **Fix 16** (after imports): New `_load_category_map()` function
2. **Fix 17** (`load_and_classify`): Injects `Category` per row, logs tier breakdown
3. **Fix 18** (`analyze_report`): Saves run config JSON before LLM call
4. **Fix 19** (`ANALYSIS_PROMPT_TEMPLATE`): Updated columns to match reference report format
5. **Fix 20** (`rows_to_csv_string`): Added ASIN and Category columns

### fba_report_filter.py
1. **Fix 21** (`normalize_ean`): Handles scientific notation

## To revert any file
Copy the corresponding `.bak` file back over the live file.
Example: copy `backup/dashboard_v2_fixes_20260317/api.py.bak` → `dashboard_v2_redesign/api.py`
