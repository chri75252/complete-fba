# Sandboxed Runs Stability Fixes Plan
**Document:** `docs/plan_sandboxed_runs_stability_fixes_20260306_REVISED.md`  
**Date:** March 6, 2026  
**Status:** REVISED - Consolidated Fix Plan (Strictly Control Plane)  
**Classification:** Critical Stability Patches for Control Plane 

---

## Executive Summary

This document consolidates fixes for critical stability issues affecting the Chat UI orchestration of sandboxed workflow runs. 

**CRITICAL DIRECTIVE:** All changes respect the Main Script Protection Policy (AGENTS.md Section 13) AND the user's strict zero-touch policy for the `utils/` directory. All fixes are strictly confined to the `control_plane/` layer. 

Previous proposals attempting to edit `browser_manager.py` or core workflow scripts to silence tracebacks or handle hung tabs have been explicitly rejected and purged from this document.

---

## 1. Worker Exit Bug: FileNotFoundError During Cancellation

### Problem Description
During job cancellation, the `_move_job()` function in `control_plane/worker.py` attempts to move a job file that may have already been deleted or moved by another process. This triggers an unhandled `FileNotFoundError` that crashes the worker loop.

**Location:** `control_plane/worker.py`, lines 86-90

### Proposed Fix (Accepted)
Wrap the `os.replace()` call in a try/except block to gracefully handle the race condition:

```python
def _move_job(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        suffix = int(time.time() * 1000)
        dst = dst_dir / f"{src.stem}__dup_{suffix}{src.suffix}"
    try:
        os.replace(src, dst)
    except FileNotFoundError:
        # File already moved or deleted by another process
        return dst
    return dst
```

**Rationale:** This is a defensive fix that acknowledges the reality of filesystem race conditions in concurrent environments. The worker should not crash when a file it intended to move is already gone.

---

## 2. Category Cap Math: Correct max_products Calculation

### Problem Description
When processing multiple category URLs with `max_products_per_category` set, the system currently calculates `categories_needed = ceil(max_products / max_products_per_category)`. This leads to incorrect behavior when the user wants "10 products per category across 2 categories." The LLM sets both variables to 10, meaning `ceil(10/10) = 1` category is processed.

### Proposed Fix (Accepted)
The Control Plane orchestrator should intercept this payload before the job is queued and automatically multiply the variables.

**Location:** `control_plane/chat_orchestrator.py` (Inside `agent_plan_step` or `execute_tool_call` when `enqueue_run` is selected).

```python
        if tool == "enqueue_run":
            # ... existing logic ...
            if constraints.get("max_products") is not None and constraints.get("max_products_per_category") is not None:
                # User asked for X per category across N categories
                urls = params.get("category_urls", [])
                if urls and len(urls) > 1:
                    params["max_products"] = constraints["max_products_per_category"] * len(urls)
```

---

## 3. Cancel Run Ambiguity: Explicit run_id Resolution

### Problem Description
The LLM in the Chat UI sometimes hallucinates an empty or null `run_id` when the user asks to cancel a run.

### Proposed Fix (Accepted)
When the LLM provides an empty `run_id` for `cancel_run`, explicitly fall back to `st.session_state["last_run_id"]` which is reliably set when a run is enqueued.

**Location:** `control_plane/chat_orchestrator.py`, in the `cancel_run` execution handler.

```python
    if name == "cancel_run":
        run_id = str(p.get("run_id") or "")
        run_id = _resolve_contextual_run_id(repo_root, run_id)
        if not run_id:
            return {"ok": False, "error": "No active run_id found to cancel."}
```

---

## Implementation Order

1. **Worker Exit Bug** (`control_plane/worker.py`) - Low risk, defensive fix.
2. **Category Cap Math** (`control_plane/chat_orchestrator.py`) - Logic adjustment.
3. **Cancel Run Ambiguity** (`control_plane/chat_orchestrator.py`) - Add fallback logic.

---

## Verification Checklist

After implementing each fix:

- [ ] Worker cancellation no longer crashes on FileNotFoundError
- [ ] Multi-category runs with `max_products_per_category` calculate limits correctly
- [ ] Cancel run works even when LLM provides empty run_id

---

## References
- AGENTS.md Section 13: Main Script Protection Policy
- User Directive: ZERO EDITS PERMITTED to `utils/` or core FBA scripts.