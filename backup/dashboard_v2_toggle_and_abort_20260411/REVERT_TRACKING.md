# Revert Tracking — Dashboard V2 Sales Toggle + AbortController Fix

**Date:** 2026-04-11
**Reason:** Fix sales field toggle not changing UI counts, fix report dropdown showing stale options on supplier change, add request sequencing guard

## Files Modified

| File | Change Scope | Backup Path | Validation |
|------|-------------|-------------|------------|
| `dashboard_v2_redesign/static/js/app.js` | Added `_metricsAbortCtrl` and `_analysisAbortCtrl` globals; added AbortController abort-before-new logic to `fetchMetrics()` and `loadAnalysis()`; added `AbortError` catch blocks; changed supplier/lineage change handlers to clear `innerHTML` on report dropdowns instead of just `.value` | `backup/dashboard_v2_toggle_and_abort_20260411/app.js` | JS syntax valid (`node -c`); live browser test passed |
| `dashboard_v2_redesign/templates/index.html` | Changed sales field toggle label from backtick-wrapped to parenthetical format | `backup/dashboard_v2_toggle_and_abort_20260411/index.html` | Rendered correctly in browser |
| `dashboard_v2_redesign/api.py` | No changes in this pass (sales_field param already added in prior pass) | N/A | N/A |

## Backup Restore Commands

```cmd
copy "backup\dashboard_v2_toggle_and_abort_20260411\app.js" "dashboard_v2_redesign\static\js\app.js"
copy "backup\dashboard_v2_toggle_and_abort_20260411\index.html" "dashboard_v2_redesign\templates\index.html"
```

## Verification Results

- EFG supplier toggle OFF (bought_in_past_month): 253 profitable, 9 with sales
- EFG supplier toggle ON (amazon_sales_badge): 253 profitable, 8 with sales
- Poundwholesale toggle: 23 profitable, 4 with sales (falls back to bought_in_past_month since CSV lacks amazon_sales_badge column)
- Supplier change: dropdown clears immediately to single "— latest —" option, then repopulates with correct supplier's reports
- No JS console errors
- AbortController prevents stale responses (verified by rapid toggle switching)

## Root Causes Fixed

1. **Sales toggle appeared not to work**: Caused by auto-refresh (60s interval) sending a new `fetchMetrics()` that could overwrite the toggle-triggered response with a stale result. Fixed by adding AbortController to cancel in-flight requests before issuing new ones.

2. **Report dropdown showed stale options on supplier change**: Only `.value` was cleared, not `.innerHTML`, so old supplier's report options remained visible until the async fetch completed. Fixed by clearing `innerHTML` to just the default option immediately on change.

3. **Analysis race condition**: Same issue as metrics — `loadAnalysis()` could have stale response overwrite fresh one. Fixed with separate `_analysisAbortCtrl`.