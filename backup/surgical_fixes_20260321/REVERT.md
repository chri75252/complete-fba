# REVERT TRACKING - surgical_fixes_20260321
Generated: 2026-03-21T06:08:42.047409

## Changes Made
1. tools/FBA_Financial_calculator.py - C1: EAN to-string before to_csv() at line ~636
   - C2: Same fix for run_calculations_incremental() at line ~781
2. dashboard_v2_redesign/api.py - C3: Removed 500-row page_size cap in get_analysis()
   - C4: Added available_reports to get_supplier_metrics() response
3. dashboard_v2_redesign/static/js/app.js - G1: Removed *100 from ROI display
4. tools/fba_ai_analyst.py - C5: Added table formatting spec to ANALYSIS_PROMPT_TEMPLATE
   - C7: normalize_ean() applied to EAN/EAN_OnPage before sending to LLM
5. dashboard_v2_redesign/templates/index.html - Added Workflows tab (Section E+F)

## To Revert
Copy all files from this backup folder back to their original locations.