# Revert Tracking - max_products corruption fix

Task: Remove silent `max_products` multiplier that corrupted values post-approval.
Date: 2026-03-16

## Changes

### Fix 1 — `control_plane/tools/tool_param_validation.py` (PRIMARY)

**Removed lines 206-215** — the `should_normalize_total` block:

```python
# REMOVED:
should_normalize_total = (
    max_products is not None
    and max_per_cat is not None
    and max_products > 0
    and max_per_cat > 0
    and len(category_urls) > 1
    and max_products == max_per_cat
)
if should_normalize_total:
    cleaned["max_products"] = max_per_cat * len(category_urls)
```

The blank line between `cleaned["max_products_per_category"] = max_per_cat` and `ok, run_id, msg = _optional_str(...)` was also removed.

**Revert**: Insert the block above between line `cleaned["max_products_per_category"] = max_per_cat` and `ok, run_id, msg = _optional_str("run_id", p.get("run_id"))` in `_validate_enqueue_run`.

---

### Fix 2 — `control_plane/chat_orchestrator.py` (SECONDARY)

**Removed lines 1994-2001** — the redundant multiplier in `_enqueue_run` handler:

```python
# REMOVED:
if (
    raw_max_products is not None
    and raw_max_products_per_category is not None
    and len(requested_category_urls) > 1
    and max_products_val == max_products_per_cat_val
    and max_products_per_cat_val > 0
):
    max_products_val = max_products_per_cat_val * len(requested_category_urls)
```

The blank line before `req = RunRequest(` was also removed.

**Revert**: Insert the block above between `max_products_per_cat_val = _coerce_or_default(...)` and `req = RunRequest(` in the `enqueue_run` handler.

---

## Why These Were Removed

Both blocks fired when `max_products == max_products_per_category` and `len(category_urls) > 1`, silently multiplying `max_products` by the number of categories post-approval. The approval UI showed the pre-normalization value (e.g. 4), but the stored job and merged config contained the multiplied value (e.g. 12). On resume, the corrupted stored value was read back and fed to the LLM as authoritative context, perpetuating the wrong number.

Fix 1 was the actual first-to-fire corruption (validator runs before handler). Fix 2 was a redundant duplicate that didn't fire in the failing case but was dangerous for edge cases.

---

# Revert Tracking - opencode-compaction-dual-output

Task: Patch `opencode.json` to tune compaction headroom.
Date: 2026-03-13

## Backup Information
- **Original File**: `C:\Users\chris\.config\opencode\opencode.json`
- **Backup Location**: `C:\Users\chris\.config\opencode\backup\compaction_dual_output_20260313\opencode.json`
- **Backup Verified**: Yes (Size: 21,431 bytes)

## Changes
- Added top-level `compaction` key to `opencode.json`:
  ```json
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 20000
  }
  ```

## Revert Procedure
1. Delete the modified `C:\Users\chris\.config\opencode\opencode.json`.
2. Copy the backup from `C:\Users\chris\.config\opencode\backup\compaction_dual_output_20260313\opencode.json` to `C:\Users\chris\.config\opencode\opencode.json`.
3. Verify JSON validity: `python -c "import json; json.load(open(r'C:\Users\chris\.config\opencode\opencode.json','r',encoding='utf-8'))"`
