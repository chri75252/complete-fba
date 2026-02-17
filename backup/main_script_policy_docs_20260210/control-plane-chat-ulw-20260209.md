# Control Plane Chat ULW Fix Plan (2026-02-09) — OKAY (Verified, Executable)

## TL;DR

**Priority (per your instruction)**
1) Functional system: Chat → enqueue → worker executes → expected artifacts exist.
2) Cancellation without Ctrl+C and without manual deletion of `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`.
3) Follow-up chat context retention + non-generic clarify.
4) **URL/domain canonicalization refactor is LAST STEP**.

---

## 0) Evidence (file-grounded, verified)

### 0.1 Runtime limits defaulting to 0 → “INFINITE MODE”

**Root failure mode (still observable in the wild)**
- If `enqueue_run` receives missing/`null` runtime limits and those are coerced with `or 0`, the job JSON and merged config get `0`, which triggers “infinite mode”.

**Current code state (as of 2026-02-10 working tree)**
- Patched (good defaulting): `control_plane/chat_orchestrator.py:659-683`
  - Uses `_coerce_or_default()` + base `config/system_config.json` defaults.
- Still buggy (missing/None collapses to 0): `chat_orchestrator.py:659-666`
  - `max_products=int(p.get("max_products") or 0)`
  - `max_products_per_category=int(p.get("max_products_per_category") or 0)`

**New evidence (run df9037be created 2026-02-09 20:09:26Z)**
- Job runtime limits are `0/0`: `OUTPUTS/CONTROL_PLANE/jobs/done/job_df9037be-24b6-495a-8b66-8ef5bb8bc2da.json:14-17`
- Merged config limits are `0/0`: `OUTPUTS/CONTROL_PLANE/overrides/df9037be-24b6-495a-8b66-8ef5bb8bc2da/system_config.merged.json:24-28`
- Runner log shows `INFINITE MODE DETECTED`: `OUTPUTS/CONTROL_PLANE/logs/df9037be-24b6-495a-8b66-8ef5bb8bc2da.log:123-126`
- Base config defaults are non-zero: `config/system_config.json:24-28`

**Interpretation (guarded)**
- This run strongly suggests an enqueue path still exists (or was running stale code) that coerces missing limits to `0` (root-level `chat_orchestrator.py`, or a pre-patch in-memory `control_plane/chat_orchestrator.py`).

### 0.2 Angelwholesale button pagination 0 URLs
**Confirmed log line**
- `OUTPUTS/CONTROL_PLANE/logs/c012aefb-f3da-4165-b9fc-3b17dccfbf1d.log`
  - Contains: `✅ Button pagination complete: 0 unique URLs collected`

**Confirmed code location**
- `tools/configurable_supplier_scraper.py:1528-1642` contains `_collect_urls_button_pagination()`
- `tools/configurable_supplier_scraper.py:1644-1685` contains `_extract_product_urls_from_page()`
- These are the actual function names in the current code.

### 0.3 Clarify drops error_context
**Confirmed**
- `plan_tool_call()` sets `params={"user_text":..., "error_context":...}`
- `execute_tool_call()` calls `ask_clarify(user_text=..., missing_params=...)` without passing error_context
- `control_plane/tools/clarify.py` has no error_context parameter

### 0.4 Worker cleanup hazards
**Confirmed**
- `control_plane/worker.py:265-267` has unguarded `proc.wait(timeout=30)`
- No cancel flag polling exists
- Status always set to done/failed based on returncode after proc exits

---

## Next-Wave Execution Plan (2026-02-10)

> Goal: eliminate any remaining enqueue path that turns missing limits into `0`, then re-run a small sandbox job and verify via **job JSON + merged config + status JSON + processing state + logs**.

### Wave 1 — Limits Parity + Proof (P0)
1) Apply the minimal diff in **Task 1B** to `chat_orchestrator.py` so it matches `control_plane/chat_orchestrator.py` defaulting.
2) Restart the Chat UI process (Streamlit) to guarantee it is not running pre-patch code.
3) Enqueue two runs from Chat UI:
   - Case A: omit limits / provide `null` → expect defaults `1000000` and `2000`
   - Case B: explicit “first 12 products” → expect `12` (and optionally per-category)

**Wave 1 checkpoints (must all pass)**
- `OUTPUTS/CONTROL_PLANE/jobs/*/job_<run_id>.json` shows expected `runtime.*` values.
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json` matches the same `system.*` limits.
- `OUTPUTS/CONTROL_PLANE/status/<run_id>.json` contains non-null `resolved_paths.processing_state` pointing at sandbox supplier.
- `OUTPUTS/CACHE/processing_states/<sandbox_supplier>_processing_state.json` exists and has `supplier_name == sandbox_supplier`.
- `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log` does not contain `INFINITE MODE DETECTED`.

### Wave 2 — Cancel Wiring (P0)
- Proceed with Tasks 3–4 (cancel flag polling + `cancel_run` tool) only after Wave 1 is proven.

### Wave 3 — Angelwholesale URL Collection Instrumentation (P0)
- Proceed with Task 5 (instrument `_collect_urls_button_pagination`) after Waves 1–2.

### Wave 4 — Clarify Plumbing + Follow-up Context (P1)
- Proceed with Tasks 6–7 after core stability (Waves 1–3).

### Wave 5 — URL Canonicalization (LAST)
- Proceed with Task 8 only after all above waves verified.

---

## 1) Backup Protocol (MANDATORY)

**Naming convention (per user)**: backup subfolder named after the task/group.

Before editing (for this next-wave group):
- Create: `backup/chat_orchestrator_limits_parity_20260210/`
- Copy files (every file that will be modified in this group):
  - `chat_orchestrator.py` (root)
  - `control_plane/chat_orchestrator.py`
  - `dashboard/chat_panel.py`
  - `control_plane/tools/jobs.py` (if job schema changes)

Before editing (for cancel wiring group):
- Create: `backup/control_plane_cancel_run_20260210/`
- Copy files:
  - `control_plane/worker.py`
  - `control_plane/chat_orchestrator.py`
  - `dashboard/chat_panel.py`
  - `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
  - `control_plane/tools/clarify.py`
  - (new) `control_plane/tools/cancel_run.py`

Before editing (for angelwholesale pagination instrumentation group):
- Create: `backup/angelwholesale_button_pagination_20260210/`
- Copy files:
  - `tools/configurable_supplier_scraper.py`
  - `config/supplier_configs/angelwholesale.co.uk.json` (only if selectors change)

---

## 2) Artifact Paths (authoritative)

**Job files**
- Pending: `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`
  - Verified in `control_plane/tools/jobs.py:80`
- Worker scans: `job_*.json`

**Lock**
- `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`

**Cancel flag**
- `OUTPUTS/CONTROL_PLANE/lock/cancel_<run_id>.flag`

---

## 3) Explicit Semantics

### 3.1 Runtime limits
- `0` = unlimited (infinite mode)
- If user doesn't specify limit → use config defaults (don't store 0)
- If user explicitly says "unlimited/no limit/all products" → store 0

### 3.2 Cancellation
- status JSON: `state="cancelled"`
- Job moves to `jobs/failed/`
- **Rule**: once cancelled, never overwrite to done/failed

---

## 4) Definition of Done

### 4.1 Functional run
- Chat enqueue creates `job_<run_id>.json`
- Worker processes and creates status, logs, processing state, linking map

### 4.2 Limits
- "first 12 products" → runtime contains 12, not 0
- No "INFINITE MODE DETECTED" in logs

### 4.3 Cancel
- Chat "cancel run <run_id>" works
- Status ends as cancelled, lock removed, job moved, flag removed

---

## 5) Implementation Tasks (diff-driven, verified locations)

### Task 1 (P0): Fix runtime limits defaulting to 0 (and eliminate split-brain)

**Why this is still P0**
- Run `df9037be` demonstrates the failure mode still occurs: job runtime `0/0` and merged config `0/0` even though base config defaults are non-zero.

**Patch targets (minimal surgical diffs)**
1) `control_plane/chat_orchestrator.py` (already patched in working tree; keep and verify)
2) Root `chat_orchestrator.py` (must be brought to parity to avoid any UI/entrypoint accidentally importing it)

#### 1A) `control_plane/chat_orchestrator.py` (keep current patched behavior)
- Ensure enqueue_run uses base-config defaults when params are missing/empty.
- Ensure `expected_outputs` uses `jobs/pending/job_<run_id>.json` (already correct in working tree).

#### 1B) Root `chat_orchestrator.py` (NEW: minimal diff proposal)
**Patch target**: `chat_orchestrator.py:636-703` (enqueue_run branch)

**Goal**
- Match the exact semantics in `control_plane/chat_orchestrator.py:659-683`.
- Treat “missing/null/empty” as “use base config defaults”.
- Preserve “explicit unlimited” semantics: user must explicitly set 0 for unlimited; do not default to 0.

**Diff sketch (minimal, surgical)**
```diff
--- a/chat_orchestrator.py
+++ b/chat_orchestrator.py
@@
     if name == "enqueue_run":
         workflow_key = str(p.get("workflow_key") or "")
@@
-        req = RunRequest(
+        base_cfg = read_json(repo_root / "config" / "system_config.json")
+        system_defaults = base_cfg.get("system") or {}
+
+        def _coerce_or_default(raw: object, default_val: int) -> int:
+            if raw is None:
+                return default_val
+            if isinstance(raw, str) and not raw.strip():
+                return default_val
+            return int(raw)
+
+        req = RunRequest(
             supplier_domain=str(p.get("supplier_domain") or ""),
             workflow_key=workflow_key,
             runner_script=str(p.get("runner_script") or ""),
             category_urls=list(p.get("category_urls") or []),
-            max_products=int(p.get("max_products") or 0),
-            max_products_per_category=int(p.get("max_products_per_category") or 0),
+            max_products=_coerce_or_default(
+                p.get("max_products"),
+                int(system_defaults.get("max_products") or 0),
+            ),
+            max_products_per_category=_coerce_or_default(
+                p.get("max_products_per_category"),
+                int(system_defaults.get("max_products_per_category") or 0),
+            ),
             notes=p.get("notes"),
         )
```

**Also update root `expected_outputs` path string (accuracy)**
- Root `chat_orchestrator.py:375-382` still advertises `OUTPUTS/CONTROL_PLANE/jobs/pending/<run_id>.json`.
- Update to `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json` to match real jobs.

**Verification (must check multiple artifacts, not logs alone)**
For a run enqueued *without* specifying limits:
- `OUTPUTS/CONTROL_PLANE/jobs/*/job_<run_id>.json` → `runtime.max_products == 1000000` and `runtime.max_products_per_category == 2000`
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json` → `system.max_products == 1000000` and `system.max_products_per_category == 2000`
- `OUTPUTS/CONTROL_PLANE/status/<run_id>.json` → `resolved_paths.processing_state` points to sandbox supplier path
- `OUTPUTS/CACHE/processing_states/<sandbox_supplier>_processing_state.json` exists and has `supplier_name == sandbox_supplier`
- `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log` does **not** contain `INFINITE MODE DETECTED`

For a run enqueued with explicit limits (e.g. first 12 products):
- Job JSON runtime values match `12` (and/or per-category limit)
- Merged config uses same non-zero limits

---

### Task 2 (P0): Pending-tool edits support natural language

**Patch target**: `dashboard/chat_panel.py`

**Diff sketch**
```diff
--- a/dashboard/chat_panel.py
+++ b/dashboard/chat_panel.py
@@
         mp_match = re.search(
             r"max[_ ]?products(?![_ ]?per[_ ]?category)\s*(?:from\s+\d+\s+)?(?:to|=|:)?\s*(\d+)",
             user_input,
             re.IGNORECASE,
         )
+        if not mp_match:
+            mp_match = re.search(
+                r"(?:first|only|just|limit(?:ed)?\s+to|top)\s+(\d+)\s+products?",
+                user_input,
+                re.IGNORECASE,
+            )
+        if not mp_match and re.search(r"\b(unlimited|no\s+limit|all\s+products)\b", user_input, re.IGNORECASE):
+            new_params["max_products"] = 0
+            updated_params = True
+        elif mp_match:
+            new_params["max_products"] = int(mp_match.group(1))
+            updated_params = True
```

---

### Task 3 (P0): Worker cancel polling + lock safety

**Patch target**: `control_plane/worker.py:216-281`

**Implementation spec**
- Add `was_cancelled = False` before loop
- Check cancel flag every poll iteration
- If cancelled: set was_cancelled=True, status=cancelled, terminate proc, delete flag, break
- In cleanup: guard proc.wait with try/except; kill if timeout
- Finalization: if was_cancelled, preserve cancelled state, move to failed, release lock

**Diff sketch**
```diff
--- a/control_plane/worker.py
+++ b/control_plane/worker.py
@@ -216,6 +216,7 @@
             with open(log_path, "w", encoding="utf-8") as log_file:
                 try:
                     proc = subprocess.Popen(...)
+                    was_cancelled = False
                 except Exception as e:
                     ...
@@ -238,6 +239,18 @@
                     while True:
                         ret = proc.poll()
                         now = time.time()
+
+                        cancel_flag = paths.lock_dir / f"cancel_{run_id}.flag"
+                        if cancel_flag.exists():
+                            was_cancelled = True
+                            status["state"] = "cancelled"
+                            status["error"]["summary"] = "Cancelled by user"
+                            write_json_atomic(status_path, status)
+                            try:
+                                proc.terminate()
+                            except Exception:
+                                pass
+                            cancel_flag.unlink(missing_ok=True)
+                            break
+
                         if now - last_status_refresh >= self.config.status_refresh_seconds:
                             ...
@@ -265,7 +278,14 @@
                         time.sleep(0.5)
 
                 finally:
-                    proc.wait(timeout=30)
+                    try:
+                        proc.wait(timeout=30)
+                    except Exception:
+                        try:
+                            proc.kill()
+                        except Exception:
+                            pass
+                        proc.wait(timeout=10)
 
             status["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
             status["error"]["last_log_lines"] = _tail_file(log_path, 200)
@@ -271,7 +291,13 @@
-            if proc.returncode == 0:
+            if was_cancelled:
+                status["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
+                status["error"]["last_log_lines"] = _tail_file(log_path, 200)
+                write_json_atomic(status_path, status)
+                _move_job(running_job_path, paths.jobs_failed)
+            elif proc.returncode == 0:
                 status["state"] = "done"
                 write_json_atomic(status_path, status)
                 _move_job(running_job_path, paths.jobs_done)
```

---

### Task 4 (P0): Add cancel_run tool with full wiring

**Tool contract**
- Name: `cancel_run`
- Params: `{ "run_id": "<run_id>" }`
- Returns: `{ "ok": true/false, "run_id": "...", "cancel_flag_path": "...", "message": "..." }`

**Path module**: Use `control_plane.paths.get_paths()`

**Required wiring**
1. New file: `control_plane/tools/cancel_run.py`
2. Export in `control_plane/tools/__init__.py`
3. Add to `WRITE_TOOLS` in `control_plane/chat_orchestrator.py:56-60`
4. Add schema in `build_prompt()` tools_desc
5. Add dispatch in `execute_tool_call()`
6. Update `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`

**Verification**
- Planner can select `cancel_run`
- Tool writes flag to correct path
- Worker observes and cancels

---

### Task 5 (P0): Angelwholesale instrumentation

**Patch targets**: `tools/configurable_supplier_scraper.py`
- `_collect_urls_button_pagination()` (lines ~1528-1642)
- `_extract_product_urls_from_page()` (lines ~1644-1685)

**Diff sketch**
```diff
--- a/tools/configurable_supplier_scraper.py
+++ b/tools/configurable_supplier_scraper.py
@@ -1658,6 +1658,7 @@
         for selector in url_selectors:
             elements = await page.query_selector_all(selector)
+            log.info(f"[URL-SELECTOR] {selector} matches={len(elements)}")
             for element in elements:
                 href = await element.get_attribute("href")
                 if href:
                     ...
+        if product_urls:
+            log.info(f"[URL-SAMPLE] {product_urls[:3]}")
         return product_urls
```

```diff
--- a/tools/configurable_supplier_scraper.py
+++ b/tools/configurable_supplier_scraper.py
@@ -1579,6 +1579,7 @@
             current_urls = await self._extract_product_urls_from_page(page)
             new_urls = set(current_urls) - all_product_urls
+            log.info(f"[PAGINATION] click={clicks} new={len(new_urls)} total={len(all_product_urls)}")
@@ -1593,6 +1594,7 @@
             if button_javascript:
                 result = await page.evaluate(button_javascript)
+                log.info(f"[PAGINATION] js_click_result={result}")
```

**Verification**
- Re-run category URL
- If 0 URLs: logs show selector counts, sample hrefs, js click results

---

### Task 6 (P1): Clarify plumbing

**Patch targets**
- `control_plane/tools/clarify.py`: add error_context param
- `control_plane/chat_orchestrator.py`: pass error_context

---

### Task 7 (P1): Follow-up context retention

**Key fix**: Use `st.session_state["last_run_id"]` (verified exists in `dashboard/pages/01_Operator_Control_Plane.py:145`)

**Implementation**
- In `dashboard/chat_panel.py`: after successful enqueue, set `st.session_state["last_run_id"] = run_id`
- In `execute_tool_call()` for read tools: if no run_id provided, use `st.session_state.get("last_run_id")`

---

### Task 8 (LAST): URL canonicalization

Do after Tasks 1-7 verified.

---

## 6) Start Work

Run: `/start-work`
