# REVERT_TRACKING

- Date: 2026-04-03
- Reason: Product-list-refresh state file appears "frozen" — counters never update when products are skipped (already in processed_keys). State only saved to disk inside `_flush_if_needed()` which never fires for skips.
- Backup root: backup/product_list_state_fix_20260403

| File | Backup Path | Validation Status |
| --- | --- | --- |
| `control_plane/run_product_list_refresh.py` | `backup/product_list_state_fix_20260403/run_product_list_refresh.py` | Completed |

## Root Cause

Two gaps in `run_product_list_refresh.py`:

1. **Skip path (line 580-581)**: When `product_key in processed_keys`, the code hits `continue` and jumps to the next iteration. No state counters update, no `save_state_atomic()` call. For a resumed run where many products are already processed, the state file stays exactly as loaded at startup.

2. **`finally` block (line 696-700)**: Updates in-memory `sp` counters after every product (including newly processed ones), but never calls `save_state_atomic()`. If the process crashes between products, all counter updates since the last `_flush_if_needed()` are lost.

## Changes Made

### control_plane/run_product_list_refresh.py

**Fix 1 — State updates on skip path.**
- After the `processed_keys` check, added counter updates and periodic save (every 10 skips + final skip).
- Added log line so skipped products are visible in logs.

**Fix 2 — State save in `finally` block.**
- Added `state_manager.save_state_atomic()` at end of `finally` block so every product (processed or errored) persists counters to disk immediately.

## Resume Mechanism

The product-list-refresh runner resumes via:
1. `results = _load_existing_linking_results()` — loads linking map from disk (line 374)
2. `processed_keys` built from `results` (lines 375-379)
3. Products already in `processed_keys` are skipped (line 580)
4. New products are processed normally

This works across new chat sessions, OS reboots, etc. — the linking map is the durable resume checkpoint. The state file counters are now kept in sync so progress is visible.

## Impact Assessment

- **Main runner scripts**: Not affected (they use `PassiveExtractionWorkflow` which has its own state management).
- **Product-list refresh**: Fixed. State now updates on every product (skip or process).
- **Performance**: `save_state_atomic()` in `finally` adds one file write per product. Acceptable — main workflow does the same.

## To Revert

```
cp backup/product_list_state_fix_20260403/run_product_list_refresh.py control_plane/run_product_list_refresh.py
```
