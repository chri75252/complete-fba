## Revert Tracking - finalists_4e269fb4_20260415

Date: 2026-04-15

Planned files:

1. `backup/finalists_4e269fb4_20260415/build_sandbox_finalists.py`
   - Scope: One-off analysis/export script to build a finalists file from sandbox `4e269fb4` artifacts only.
   - Validation: Run script successfully; inspect generated CSV rows against linking map + sandbox override Amazon cache.
   - Restore source: Delete file if rollback required.

2. `backup/finalists_4e269fb4_20260415/compare_dashboard_export_to_report.py`
   - Scope: One-off verification script to compare the dashboard export CSV against the sandbox reconciled report on shared rows.
   - Validation: Run script successfully and inspect summary counts / sampled mismatches.
   - Restore source: Delete file if rollback required.

3. `backup/finalists_4e269fb4_20260415/build_dashboard_export_finalists.py`
   - Scope: One-off analysis/export script to build the final single-file shortlist from the dashboard export, with authoritative sandbox linking-map/cache verification and manual-review buckets.
   - Validation: Run script successfully; inspect generated summary and output CSV; manually inspect doubtful rows before finalizing inclusion policy.
   - Restore source: Delete file if rollback required.

4. `FINAL STALE/efg_4e269fb4_sandbox_finalists_verified_20260415.csv`
   - Scope: Single-file output containing profitable + sellable + matching rows from sandbox `4e269fb4` with prior/current metrics and verification columns.
   - Validation: Confirm rows are grounded to linking map/cache and exclude corrupted report-only ASIN/title mismatches.
   - Restore source: Delete file if rollback required.
