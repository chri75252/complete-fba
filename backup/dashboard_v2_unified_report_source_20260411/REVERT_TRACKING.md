# REVERT TRACKING - dashboard_v2_unified_report_source_20260411

## Planned file scope
- dashboard_v2_redesign/static/js/app.js
  - Remove dashboard report list population from `fetchMetrics()` so dropdown options are no longer sourced from metrics payload
  - Add `_reportsAbortCtrl` request sequencing guard
  - Replace `loadAnalysisReports()` with `loadFinancialReportsUnified()`
  - Populate both `dashboardReportSelect` and `analysisReportSelect` from one `/api/reports/{supplier}?lineage=...` response
  - Preserve prior selection when still present; fallback to `-- latest --` if not present
  - Rewire supplier/lineage/init calls to unified loader

## Backup source paths
- backup/dashboard_v2_unified_report_source_20260411/app.js

## Restore command
copy "backup\dashboard_v2_unified_report_source_20260411\app.js" "dashboard_v2_redesign\static\js\app.js"

## Validation status
- JS syntax: PASS (`node -c dashboard_v2_redesign/static/js/app.js`)
- Live browser verification: PASS
  - Pound/base: dashboard and analysis report dropdown counts both 7
  - EFG/latest_sandbox: dashboard and analysis report dropdown counts both 18
  - Supplier switch: both dropdowns update together from unified source
  - Sales toggle still functional (`8 with sales` on EFG latest_sandbox with toggle ON)
- LSP diagnostics: NOT AVAILABLE (typescript-language-server not installed in environment)
