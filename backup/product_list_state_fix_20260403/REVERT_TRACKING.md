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

## To Revert (Fix 1 + Fix 2 only — yesterday's skip/finally changes)

```
cp backup/product_list_state_fix_20260403/run_product_list_refresh.py control_plane/run_product_list_refresh.py
```

---

## Fix 3 — Linking map filter + resume counter preservation (2026-04-04)

**Backup before this fix:** `backup/product_list_state_fix_20260403/run_product_list_refresh_pre_filter_fix.py`

### Root Cause

Two additional bugs found:

1. **`_load_existing_linking_results` loaded ALL linking map entries** including 13 foreign entries from a different run (EANs not in the current product list). Since ALL 1776 product list products were already in the linking map (run had previously completed), `processed_keys` contained all 1776 keys → every product skipped on startup.

2. **Lines 407-410 unconditionally overwrote state counters** from `len(results)` on every startup, stomping the manually-restored 861 value back to 1776/1789.

### Changes Made (exact diff: run_product_list_refresh_pre_filter_fix.py → current)

**Change 1 — `_load_existing_linking_results` signature + filter logic (line 265):**
- Added `allowed_keys: set[str] | None = None` parameter
- Added `excluded` counter and filter: if `allowed_keys` supplied and key not in it, skip the row
- Logs count of excluded foreign entries

**Change 2 — Build `product_keys` before loading linking map (line 374 area):**
- Added loop over `products` to build `product_keys` set
- Pass `allowed_keys=product_keys` to `_load_existing_linking_results`

**Change 3 — Resume-aware counter initialisation (lines 407-410 area):**
- If `not resumed`: set counters from `len(results)` as before (fresh start)
- If `resumed`: use `setdefault()` to preserve state file values; only compute `needing_extraction` fields

### To Revert Fix 3 Only

```
cp backup/product_list_state_fix_20260403/run_product_list_refresh_pre_filter_fix.py control_plane/run_product_list_refresh.py
```

### To Revert ALL Three Fixes (back to original)

```
cp backup/product_list_state_fix_20260403/run_product_list_refresh.py control_plane/run_product_list_refresh.py
```

---

## Fix 4 — Browser hidden-tab fix (2026-04-04)

**File**: `utils/browser_manager.py`
**Backup**: `backup/product_list_state_fix_20260403/browser_manager_pre_tab_fix.py`

### Root Cause

`get_page()` (line 267) iterated `context.pages` and took the **first non-closed page** with no preference for visible user tabs. Chrome extension background pages (uBlock Origin etc.) register as CDP targets and appear first in `context.pages`. The system latched onto an extension background page — invisible to the user — and navigated supplier URLs into it.

### Change Made (lines 267-282)

**Old** — took first non-closed page blindly:
```python
if page is None:
    for existing_page in self.context.pages:
        if not existing_page.is_closed():
            page = existing_page
            break
```

**New** — prefers pages with http/https URLs (user-facing tabs) over others:
```python
if page is None:
    http_pages = [p for p in self.context.pages if not p.is_closed() and str(p.url or "").startswith(("http://", "https://"))]
    other_pages = [p for p in self.context.pages if not p.is_closed() and not str(p.url or "").startswith(("http://", "https://"))]
    candidate = http_pages[0] if http_pages else (other_pages[0] if other_pages else None)
    if candidate is not None:
        page = candidate
```

Also updated the `else` log line to show the actual page URL for diagnostics.

### To Revert Fix 4 Only

```
cp backup/product_list_state_fix_20260403/browser_manager_pre_tab_fix.py utils/browser_manager.py
```
