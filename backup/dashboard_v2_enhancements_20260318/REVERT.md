# Revert Guide — Dashboard V2 Enhancements (2026-03-18)

## What was changed

| File | Backup |
|------|--------|
| `dashboard_v2_redesign/api.py` | `c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\dashboard_v2_enhancements_20260318/api.py.bak` |
| `dashboard_v2_redesign/templates/index.html` | `c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\dashboard_v2_enhancements_20260318/index.html.bak` |
| `dashboard_v2_redesign/static/js/app.js` | `c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\dashboard_v2_enhancements_20260318/app.js.bak` |
| `dashboard_v2_redesign/static/css/styles.css` | `c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\dashboard_v2_enhancements_20260318/styles.css.bak` |
| `tools/fba_ai_analyst.py` | `c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\dashboard_v2_enhancements_20260318/fba_ai_analyst.py.bak` |

## Core workflow scripts — UNTOUCHED
- `tools/passive_extraction_workflow_latest.py` — NOT modified
- `tools/configurable_supplier_scraper.py` — NOT modified
- `tools/amazon_playwright_extractor.py` — NOT modified
- `tools/FBA_Financial_calculator.py` — NOT modified
- `run_custom_*.py` — NOT modified
- `tools/fba_report_filter.py` — NOT modified

## Changes made

### styles.css
1. Added `select.glass-input` and `.glass-input option` dark theme rules (dropdown fix)

### api.py
1. Fix HTTP 500: `csv_files[0]` → `os.path.basename(csv_path)`
2. Added `bought_in_past_month` to numeric conversion
3. Added `count_profitable_with_sales` metric
4. Added `bought_in_past_month` to chart_cols
5. Added `bought_in_past_month` to Analysis clean_rows
6. Added `min_sales` query param to get_analysis
7. Added min_sales filter logic

### index.html
1. Added `id="profitableSubtitle"` to Profitable card subtitle
2. Replaced Match Quality chart → Profitable Categories with Sales chart
3. Replaced Fuzzy Match table → Top Products with Sales table
4. Added Min Sales/mo filter input to Analysis tab
5. Added Sales column header to Analysis table
6. Updated colspan to 9

### app.js
1. Added count_profitable_with_sales display in Profitable card subtitle
2. Replaced renderMatchQualityChart → renderCategorySalesChart
3. Replaced Fuzzy Match rendering → Top Products with Sales rendering
4. Added minSales variable and API param in loadAnalysis
5. Added Sales column to Analysis table rows
6. Updated colspan to 9 in renderAnalysisTable

### fba_ai_analyst.py
1. Updated CSV header (added Sales, renamed price columns)
2. Updated CSV row output (added bought_in_past_month, fixed ASIN column order)
3. Updated prompt template to match reference report format

## To revert any file
Copy the corresponding `.bak` file back over the live file.
