# Phase 1 — Applied Changes Log

This file will be updated as changes are applied to existing core scripts.

## Backups
Backups stored under:
- `SYSTEM_CHAT_UI_PRDS/backups/phase1_impl_20260125/`

## Changes
- (pending) `config/system_config_loader.py` — add `FBA_SYSTEM_CONFIG_PATH` env override
- (pending) `tools/passive_extraction_workflow_latest.py` — respect `workflow_config.categories_config_path` in `_get_predefined_categories`

## New files / folders added
- `control_plane/` (new package)
- `dashboard/pages/01_Operator_Control_Plane.py` (new Streamlit Operator UI page)
- `SYSTEM_CHAT_UI_PRDS/phase1_control_plane/WALKTHROUGH_PHASE1.md`
