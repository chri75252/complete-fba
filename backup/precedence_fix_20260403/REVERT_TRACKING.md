# REVERT_TRACKING

- Date: 2026-04-03
- Reason: product-list resume routing precedence fix + empty-category safety gate + product-list-aware clarify fallback
- Backup root: backup/precedence_fix_20260403
- Root cause fixed: category resume rewrite was evaluated before product-list rewrite, causing wrong job type (run_workflow instead of run_product_list_refresh) when both contexts were present. This produced semantic workflow abort on run 3aa724d3-9462-4fa1-ba06-1c14e547b357.

| File | Backup Path | Validation Status |
| --- | --- | --- |
| `control_plane/chat_orchestrator.py` | `backup/precedence_fix_20260403/control_plane/chat_orchestrator.py` | Completed |
| `control_plane/tools/clarify.py` | `backup/precedence_fix_20260403/control_plane/tools/clarify.py` | Completed |

## Changes Made

### control_plane/chat_orchestrator.py

**Fix 1a** — `_should_rewrite_category_resume` (~line 1096): Added two early-return guards:
- `if _looks_like_product_list_intent(user_text, params): return False`
- `if planner_hints.get("last_products_path"): return False`

These make the category rewrite stand down whenever product-list intent is detectable, before any other checks run.

**Fix 1b** — Block order swap (~line 1253): Moved `_should_rewrite_product_list_resume` block BEFORE `_should_rewrite_category_resume` block, with comments marking the intended precedence.

**Fix 2** — Empty-category resume gate (~line 1382): Split the existing `enqueue_run` empty-URL guard into two paths:
- NEW: if no URLs AND resume intent detected → `ask_clarify` with message "I cannot safely resume a category workflow without category URLs."
- EXISTING (unchanged): if no URLs AND no sandbox_suffix AND no runner → `ask_clarify` with generic message

This prevents the 3aa724d3-style semantic abort where an empty categories_subset.json was accepted and the workflow immediately aborted.

### control_plane/tools/clarify.py

**Fix 3** — Added `import re` and an `elif` branch in the generic fallback: when no `missing_params` are provided but the user text contains resume/product-list keywords (`product-list`, `products_path`, `resume`, `continue`, `sandbox_suffix`, `run_id`), the clarify function now asks three targeted product-list-resume questions instead of the generic workflow question.

## Validation Evidence

- `python -m py_compile control_plane/chat_orchestrator.py control_plane/tools/clarify.py` passed.

## To Revert

Restore both backup files to their original paths:

```
cp backup/precedence_fix_20260403/control_plane/chat_orchestrator.py control_plane/chat_orchestrator.py
cp backup/precedence_fix_20260403/control_plane/tools/clarify.py control_plane/tools/clarify.py
```
