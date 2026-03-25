# Plan: Main Workflow Chat UI Fix

**Date:** 2026-03-21
**Scope:** 3 surgical fixes in `control_plane/` only. No main workflow scripts touched.
**Goal:** Allow the chat AI Assistant to launch full-supplier main workflow runs and auto-display processing state.

---

## Fix 1: Unblock main workflow in validation layer

**File:** `control_plane/tools/tool_param_validation.py`
**Line:** 174
**Root cause:** Validation rejects empty `category_urls` unless `sandbox_suffix` is present. Does not check for `runner_script`.

```diff
--- a/control_plane/tools/tool_param_validation.py
+++ b/control_plane/tools/tool_param_validation.py
@@ -171,7 +171,8 @@
     category_urls = category_urls or []
     # If resuming a sandbox run, we might not need category URLs directly (the system pulls from previous overrides)
     sandbox_suffix = p.get("sandbox_suffix")
-    if not category_urls and not sandbox_suffix:
+    runner_script = cleaned.get("runner_script", "")
+    if not category_urls and not sandbox_suffix and not runner_script:
         return _err(
             tool=tool, field="category_urls", message="category_urls must contain at least one URL"
         )
```

---

## Fix 2: Bypass sandbox machinery for main workflow runs

**File:** `control_plane/chat_orchestrator.py`
**Location:** Inside `_execute_tool`, the `enqueue_run` branch (around line 2012-2107)
**Root cause:** Even with `runner_script` and empty `category_urls`, the code:
1. Writes an empty `categories_subset.json`
2. Creates a merged config pointing to empty categories
3. Sets `FBA_SYSTEM_CONFIG_PATH` to this merged config
4. The runner script reads that env var and gets 0 categories

**Fix:** When `runner_script` is provided and `category_urls` is empty and no `sandbox_suffix`, skip the sandbox override path. Enqueue the job directly with the runner script and NO config override, so the runner uses its own built-in `config/system_config.json`.

```diff
--- a/control_plane/chat_orchestrator.py
+++ b/control_plane/chat_orchestrator.py
@@ -2010,6 +2010,30 @@

         sandbox_suffix = _normalize_sandbox_suffix(p.get("sandbox_suffix"), run_id)

+        # ---- MAIN WORKFLOW PATH (no sandbox) ----
+        # When runner_script is provided with empty category_urls and no sandbox_suffix,
+        # skip sandbox machinery entirely. Let the runner use its own built-in config.
+        is_main_workflow = (
+            req.runner_script
+            and not req.category_urls
+            and not str(p.get("sandbox_suffix") or "").strip()
+        )
+
+        if is_main_workflow:
+            from control_plane.tools.jobs import enqueue_run_job
+            from control_plane.tools.state import read_processing_state, summarize_processing_state
+
+            # Use default config (no override) — runner reads config/system_config.json
+            default_cfg_path = repo_root / "config" / "system_config.json"
+            default_cat_path = repo_root / "config" / f"{req.supplier_domain.replace('.co.uk', '').replace('.', '_')}_categories.json"
+
+            job_path = enqueue_run_job(
+                run_id, req, default_cfg_path, default_cat_path, sandbox_supplier=req.supplier_domain
+            )
+
+            result = {
+                "ok": True,
+                "run_id": run_id,
+                "mode": "main_workflow",
+                "runner_script": req.runner_script,
+                "supplier_domain": req.supplier_domain,
+                "job_path": str(job_path),
+                "note": "Main workflow enqueued. No sandbox overrides applied. Runner will use its built-in config.",
+            }
+
+            # Auto-attach processing state
+            state = read_processing_state(repo_root, req.supplier_domain)
+            if state:
+                result["processing_state"] = summarize_processing_state(state)
+            else:
+                result["processing_state"] = {
+                    "current_phase": "not_started",
+                    "persistent_category_index": 0,
+                    "total_categories": 0,
+                    "current_category_url": None,
+                    "supplier_products_completed": 0,
+                    "supplier_products_needing_extraction": 0,
+                    "amazon_products_completed": 0,
+                    "amazon_products_needing_analysis": 0,
+                }
+
+            return result
+
         # ---- SANDBOX PATH (existing behavior, unchanged) ----
         # Build sandbox_supplier for output paths/polling, but keep supplier_name canonical for credential lookup
         sandbox_supplier = _build_sandbox_supplier(req.supplier_domain, sandbox_suffix, run_id)
```

---

## Fix 3: Auto-attach processing state to sandbox enqueue_run responses too

**File:** `control_plane/chat_orchestrator.py`
**Location:** The existing sandbox `enqueue_run` return block (lines 2098-2107)
**Root cause:** The return dict has no processing state info, so the LLM can't show progress metrics.

```diff
--- a/control_plane/chat_orchestrator.py
+++ b/control_plane/chat_orchestrator.py
@@ -2097,7 +2097,7 @@

-        return {
+        result = {
             "ok": True,
             "run_id": run_id,
             "sandbox_supplier": sandbox_supplier,
@@ -2105,6 +2105,18 @@
             "merged_config": str(merged_cfg_path),
             "categories": str(categories_path),
         }
+
+        # Auto-attach processing state for sandbox runs too
+        from control_plane.tools.state import read_processing_state, summarize_processing_state
+        state = read_processing_state(repo_root, sandbox_supplier)
+        if not state:
+            state = read_processing_state(repo_root, req.supplier_domain)
+        if state:
+            result["processing_state"] = summarize_processing_state(state)
+        else:
+            result["processing_state"] = {"current_phase": "fresh_run", "persistent_category_index": 0, "total_categories": 0}
+
+        return result
```

---

## Fix 4: Worker must skip env override for main workflow jobs

**File:** `control_plane/worker.py`
**Location:** Lines 317-319 (where `FBA_SYSTEM_CONFIG_PATH` is set)
**Root cause:** The worker always sets `FBA_SYSTEM_CONFIG_PATH` from the job's `override.system_config_path`. For main workflow jobs, this points to `config/system_config.json` (the default), which is harmless. But to be safe and explicit:

Actually — since Fix 2 sets `default_cfg_path = repo_root / "config" / "system_config.json"`, the worker will set `FBA_SYSTEM_CONFIG_PATH` to the same default path. This is a no-op (runner would read this path anyway). **No change needed in worker.py.**

---

## What the user will see after these fixes

When asking the chat: "run the main workflow for angelwholesale"

The LLM response will include something like:
```
Enqueued main workflow for angelwholesale.co.uk (no product limits).

Current processing state:
- Phase: amazon_analysis
- Category progress: 45/52
- Supplier extraction: 1,203/1,203 completed
- Amazon analysis: 892/1,203 completed
- Current category: https://angelwholesale.co.uk/Category/...

Start the worker to execute: python -m control_plane worker
```

Or for a fresh run:
```
- Phase: not_started
- Category progress: 0/0
- No prior processing state found — this will be a fresh run.
```

---

## Files affected (3 total)

1. `control_plane/tools/tool_param_validation.py` — 1 line changed
2. `control_plane/chat_orchestrator.py` — ~45 lines added (main workflow branch + state attachment)
3. No other files touched. No main workflow scripts modified.

## Risk assessment

- **Low risk.** All changes in `control_plane/` (preferred edit zone).
- Fix 1 is additive — adds a bypass condition, existing sandbox/resume logic untouched.
- Fix 2 adds a new early-return branch BEFORE the existing sandbox path — existing sandbox logic is completely unchanged.
- Fix 3 is additive — attaches extra data to the existing return dict.
- No changes to worker.py, no changes to runner scripts, no changes to tools/.
