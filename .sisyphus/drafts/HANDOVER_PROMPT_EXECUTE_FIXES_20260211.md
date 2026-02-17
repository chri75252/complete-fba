# Handover Prompt — Execute Control Plane Chat Fixes

**Date:** 2026-02-11
**Status:** Plan APPROVED, ready for implementation
**Plan file:** `C:\Users\chris\claude-clean\plans\gentle-swimming-giraffe.md`

---

## What You Are Doing

You are implementing 8 bug fixes for the Control Plane Chat system in this repository:
```
C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-
```

The full plan with diff-format fixes is at:
```
C:\Users\chris\claude-clean\plans\gentle-swimming-giraffe.md
```

**READ THAT PLAN FILE FIRST.** It contains exact diffs for every fix.

---

## Summary of 8 Issues and Their Fixes

### Issue 1: `<run-id>` Placeholder Crashes Windows
- **Files:** `control_plane/chat_orchestrator.py`, `dashboard/chat_panel.py`, `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- **What:** LLM echoes literal `<run-id>` from tool schema. Code tries to create file `status/<run-id>.cancelled` → `[Errno 22]` on Windows.
- **Fix 1A:** In `chat_orchestrator.py` line ~778, add UUID validation + placeholder detection before the `if not run_id:` check. If run_id matches `<...>` or isn't a valid UUID, fall back to `last_run_id`.
- **Fix 1B:** In `chat_orchestrator.py` line 269, change `"run_id": "<run-id>"` to `"run_id": "UUID of the run to cancel (from context or last_run_id)"`.
- **Fix 1C:** In `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`, add hard rule: "For cancel_run, set run_id to empty string if user doesn't specify one. NEVER use literal `<run-id>`."
- **Fix 1D:** In `chat_panel.py`, BEFORE line 310 (`st.session_state["chat_messages"].append`), add cancel/stop/kill command interception that auto-resolves `last_run_id`.

### Issue 2: "Stop at N Products" During Running Job
- **File:** `dashboard/chat_panel.py`
- **What:** After user confirms a run, `pending_tool_call = None`. "Stop at 5 products" goes to LLM which returns bogus `product_list_refresh`.
- **Fix:** After the cancel intercept (Fix 1D), add a "stop at N products" pattern matcher. When matched and `last_run_id` exists, show message: "Cannot change limits on a running job. Cancel first."

### Issue 3: max_products_per_category Defaults to 2000
- **File:** `control_plane/chat_orchestrator.py`
- **What:** User says "first 13 products" → `max_products=13` but `max_products_per_category=2000` (system default). Workflow paginates 2000 URLs.
- **Fix:** After `RunRequest` construction at line ~712, if `max_products` was set by user but `max_products_per_category` was not, auto-sync: `max_products_per_category = max_products`. Use `dataclasses.replace()` since RunRequest is frozen.

### Issue 4: JSON Parse Error on system_config.json
- **File:** `control_plane/chat_orchestrator.py`
- **What:** `read_json(repo_root / "config" / "system_config.json")` at line 688 with no try/except.
- **Fix:** Wrap in try/except, return `{"ok": False, "error": "Failed to parse..."}`.

### Issue 5: EFG Unnecessary Authentication
- **File:** `config/system_config.json`
- **What:** `efghousewares_workflow.authentication_required` is `true` but should be `false`.
- **Fix:** Change `"authentication_required": true` to `"authentication_required": false` in the efghousewares_workflow section.

### Issue 6: "Both Should Be N" Not Parsed + JSONDecodeError
- **Files:** `dashboard/chat_panel.py`, `control_plane/chat_orchestrator.py`
- **Fix 6A:** In `chat_panel.py`, after the `unlimited_match` block (line ~273), add regex for "both ... N" pattern that sets both `max_products` and `max_products_per_category`.
- **Fix 6B:** In `chat_orchestrator.py`, wrap `provider.generate_json(prompt)` at line 450 in try/except for `json.JSONDecodeError` and `ValueError`. Retry twice, then return `ask_clarify`.

### Issue 7: Operator Panel — No Sandbox Isolation (BIGGEST FIX)
- **File:** `dashboard/pages/01_Operator_Control_Plane.py`
- **What:** Chat-created runs set `supplier_name` in overrides (sandbox isolation works). Operator Panel does NOT → uses main state file → resumes from stale position.
- **Fix:** After `run_id = str(uuid.uuid4())` at line 102:
  1. Create `sandbox_supplier = f"{supplier_domain}__sandbox__{run_id[:8]}"`
  2. Pass `sandbox_supplier` to `write_categories_subset` instead of `supplier_domain`
  3. Add `"supplier_name": sandbox_supplier` to the `overrides["workflows"][workflow_key]` dict
  4. Pass `sandbox_supplier=sandbox_supplier` to `enqueue_run_job`

### Issue 8: product_list_refresh Placeholder Path
- **File:** `control_plane/chat_orchestrator.py`
- **What:** Tool schema line 290 has `"products_path": "C:/path/to/products_subset.json"` → LLM echoes it.
- **Fix:** Replace with `"products_path": "path to the products JSON file (required, must exist on disk)"`.

---

## Execution Protocol

### Step 0: Read the Plan
```
Read: C:\Users\chris\claude-clean\plans\gentle-swimming-giraffe.md
```

### Step 1: SHA256 Verification (Gate 0)
Verify 5 protected files have NOT been modified. Use Python `hashlib`, NOT git:
```python
import hashlib
files = [
    "tools/configurable_supplier_scraper.py",      # expect prefix 9249228a
    "run_custom_poundwholesale.py",                 # expect prefix 2fe136a4
    "run_custom_clearance_king.py",                 # expect prefix 514fbe7c
    "run_custom_dkwholesale-com.py",                # expect prefix e4cdd37a
    "run_custom_efghousewares-co-uk.py",            # expect prefix 4f111523
]
```

### Step 2: Create Backups
Before editing ANY file, create a backup in `backup/chat_fix_20260211/`:
```
backup/chat_fix_20260211/chat_orchestrator.py
backup/chat_fix_20260211/chat_panel.py
backup/chat_fix_20260211/01_Operator_Control_Plane.py
backup/chat_fix_20260211/system_config.json
backup/chat_fix_20260211/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md
```

### Step 3: Apply Fixes (in order)
1. `control_plane/chat_orchestrator.py` — Fixes 1A, 1B, 3, 4, 6B, 8
2. `dashboard/chat_panel.py` — Fixes 1D, 2, 6A
3. `dashboard/pages/01_Operator_Control_Plane.py` — Fix 7
4. `config/system_config.json` — Fix 5
5. `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` — Fix 1C

### Step 4: Syntax Verification
After each file edit, verify syntax:
```bash
python -c "import py_compile; py_compile.compile('control_plane/chat_orchestrator.py', doraise=True)"
python -c "import py_compile; py_compile.compile('dashboard/chat_panel.py', doraise=True)"
python -c "import py_compile; py_compile.compile('dashboard/pages/01_Operator_Control_Plane.py', doraise=True)"
python -c "import json; json.load(open('config/system_config.json'))"
```

### Step 5: Post-Fix SHA256 Verification
Re-verify the 5 protected files have the SAME hashes as Step 1.

### Step 6: Functional Tests (if possible)
Run the chat orchestrator module to verify imports:
```bash
python -c "from control_plane.chat_orchestrator import plan_tool_call, execute_tool_call; print('OK')"
python -c "from dashboard.chat_panel import render_chat_panel; print('OK')"
```

---

## Key Code Locations (Line Numbers)

### `control_plane/chat_orchestrator.py`
- Line 266-271: Tool schema for `cancel_run` (Fix 1B)
- Line 286-295: Tool schema for `enqueue_product_list_refresh` (Fix 8)
- Line 318-356: `_parse_runtime_constraints()` — extracts limits from user text
- Line 359-505: `plan_tool_call()` — LLM invocation, line 450 = `generate_json` (Fix 6B)
- Line 688: `read_json(repo_root / "config" / "system_config.json")` (Fix 4)
- Line 691-712: `_coerce_or_default` and `RunRequest` construction (Fix 3)
- Line 713-743: `run_id`, `sandbox_suffix`, `sandbox_supplier`, overrides dict, `write_merged_system_config`
- Line 777-805: `cancel_run` handler (Fix 1A)

### `dashboard/chat_panel.py`
- Line 89: `render_chat_panel()` — main entry
- Line 200: `pending_tool_call = None` after confirm
- Line 215-308: NL edit parsing block (only when `pending_tool_call is not None`)
- Line 226-263: Regex matchers for max_products, natural language, unlimited
- Line 310: `st.session_state["chat_messages"].append` — where to insert intercepts (Fixes 1D, 2)
- Line 324: `plan_tool_call(user_input, Path(base_dir))` — where LLM is called

### `dashboard/pages/01_Operator_Control_Plane.py`
- Line 98-145: "Create Job" button handler
- Line 102: `run_id = str(uuid.uuid4())`
- Line 116: `write_categories_subset(run_id, supplier_domain, category_urls)` — needs sandbox
- Line 119-129: `overrides` dict — MISSING `supplier_name` (Fix 7)
- Line 143: `enqueue_run_job(run_id, request, merged_path, subset_path)` — needs `sandbox_supplier`

### `config/system_config.json`
- Line ~317: `efghousewares_workflow.authentication_required` (Fix 5)

---

## NON-NEGOTIABLE CONSTRAINTS

1. **DO NOT edit `tools/*` or `run_custom_*.py`** — these are protected files
2. **NO git commands** during execution
3. **Create backups before EVERY edit** — in `backup/chat_fix_20260211/`
4. **SHA256 verify protected files** before and after all changes
5. **Verify syntax** after each file modification
6. **Read the full plan file first** — all diffs are there
7. **No claims without verification** — after applying fixes, verify they compile

---

## What Success Looks Like

After all fixes:
1. "cancel the run" / "kill the run" → uses `last_run_id` automatically, no `<run-id>` placeholder
2. "stop at 5 products" during running job → clear message about cancelling first
3. "first 13 products" → both `max_products=13` AND `max_products_per_category=13` in job JSON
4. Corrupted `system_config.json` → clear error message, not a crash
5. EFG runs without authentication prompt
6. "both should be 13" during pending → updates both params
7. Operator Panel runs use sandbox-suffixed `supplier_name` → fresh state, not main state
8. `product_list_refresh` tool schema has no hardcoded `C:/path/to/...` placeholder
