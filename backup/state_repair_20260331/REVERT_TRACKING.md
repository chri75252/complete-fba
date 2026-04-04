## Revert Tracking - state_repair_20260331

Date: 2026-03-31
Scope: Resume-safe processing state correction for efghousewares sandbox run lineage `4e269fb4`.

### Planned files

1) `OUTPUTS/CACHE/processing_states/efghousewares_co_uk__sandbox__4e269fb4_processing_state.json`
- Change scope: Correct resume pointers/counters to last confirmed checkpoint from log `run_custom_efghousewares-co-uk__sandbox__4e269fb4__product_list_refresh_20260330_012249.log`.
- Backup source: `backup/state_repair_20260331/efghousewares_co_uk__sandbox__4e269fb4_processing_state.json.bak`
- Planned validation:
  - Re-read file and verify target fields
  - Cross-check with log-derived checkpoint values
- Status: COMPLETED

2) `OUTPUTS/CONTROL_PLANE/status/4e269fb4-8eea-4589-97ad-d76c0a5a1e30.json`
- Change scope: No direct edits applied; backed up for forensic rollback parity.
- Backup source: `backup/state_repair_20260331/status_4e269fb4-8eea-4589-97ad-d76c0a5a1e30.json.bak`
- Status: NO_EDIT

3) `OUTPUTS/CONTROL_PLANE/jobs/running/job_4e269fb4-8eea-4589-97ad-d76c0a5a1e30.json`
- Change scope: Relocated stale duplicate from `running/` to `failed/` for folder consistency.
- Backup source: `backup/state_repair_20260331/job_4e269fb4-8eea-4589-97ad-d76c0a5a1e30.running.bak`
- New location: `OUTPUTS/CONTROL_PLANE/jobs/failed/job_4e269fb4-8eea-4589-97ad-d76c0a5a1e30__dup_manual_cleanup_20260331.json`
- Status: COMPLETED

### Validation results

- Re-read state file and confirmed resume checkpoint values:
  - `last_processed_index=795`
  - `resumption_index=796`
  - `system_progression.current_phase="supplier"`
  - `system_progression.persistent_category_index=3`
  - `system_progression.current_category_url="https://www.efghousewares.co.uk/shop-by-department/pound-lines/diy---tools"`
  - `system_progression.supplier_products_completed=870`
  - `system_progression.supplier_products_needing_extraction=906`
  - `system_progression.amazon_products_completed=870`
  - `system_progression.amazon_products_needing_analysis=906`
- Verified no remaining `job_4e269fb4-...` file under `jobs/running/`.
- Verified relocated stale duplicate exists under `jobs/failed/`.

### Rollback procedure

1. Restore state file from backup:
   - from `backup/state_repair_20260331/efghousewares_co_uk__sandbox__4e269fb4_processing_state.json.bak`
   - to `OUTPUTS/CACHE/processing_states/efghousewares_co_uk__sandbox__4e269fb4_processing_state.json`
2. (Optional forensic parity) Restore status file backup if needed.
