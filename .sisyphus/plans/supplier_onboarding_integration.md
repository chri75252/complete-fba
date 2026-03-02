# Supplier Onboarding Integration Plan (Chat UI)
**Status**: ACTIVE
**Model Target**: MiniMax M2.5

---

## 1. Goal
Map every step of `.claude/skills/supplier-onboarding/SKILL.md` to a multi-turn Chat UI flow, enabling the LLM to process raw `.txt` inputs into JSON config payloads, entirely avoiding direct modification of `system_config.json` by the LLM.

## 2. Tasks

### P0 — Fix Tooling & Allowlist Constraints
- [x] Task 1: Fix `enqueue_onboarding_job` to accept and pass `supplier_domain`.
- [x] Task 2: Expand `_ALLOWED_READ_DIR_PREFIXES` and `_ALLOWED_LIST_DIRS` in `repo_files.py` to include `.claude/skills/` and `setup/`.
- [x] Task 3: Expand `_ALLOWED_WRITE_DIRS` in `output_writer.py` to include `OUTPUTS/CONTROL_PLANE/jobs/onboarding_staging`.
- [x] Task 4: Update `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` with explicit skill mapping instructions to prevent direct JSON edits.
- [x] Task 5: Create `setup/` directory and test data (`setup/stationery_test.txt`).

### P1 — Execute Integration Test
- [x] Task 6: Ask the LLM to onboard `stationerywholesale.co.uk` using the newly provided `setup/stationery_test.txt` data.

---

## 3. Implementation Diffs

### Task 1: Fix `enqueue_onboarding_job`
**File**: `control_plane/tools/repo_files.py`
```diff
 def enqueue_onboarding_job(
-    repo_root: Path, run_id: str, req: OnboardingWizardRequest
+    repo_root: Path, run_id: str, req: OnboardingWizardRequest, supplier_domain: str = "unknown"
 ) -> dict[str, Any]:
 ...
     payload = {
         "schema_version": "1.0",
         "run_id": run_id,
         "job_type": "run_onboarding_wizard",
-        "supplier_domain": "",
+        "supplier_domain": supplier_domain,
         "wizard": {
```
**File**: `control_plane/chat_orchestrator.py`
```diff
         "enqueue_onboarding": {
             "type": "write",
             "params": {
+                "supplier_domain": "poundwholesale.co.uk",
                 "input_path": "path/to/input.json",
```
```diff
     if name == "enqueue_onboarding":
+        supplier_domain = str(p.get("supplier_domain") or "")
         input_path = str(p.get("input_path") or "")
         output_path = str(p.get("output_path") or "")
         timeout = int(p.get("timeout_seconds") or 3600)
         
         from control_plane.tools.repo_files import OnboardingWizardRequest, enqueue_onboarding_job
         req = OnboardingWizardRequest(input_path=input_path, output_path=output_path, timeout_seconds=timeout)
-        return enqueue_onboarding_job(repo_root, tool_call.run_id or "", req)
+        return enqueue_onboarding_job(repo_root, tool_call.run_id or "", req, supplier_domain=supplier_domain)
```

### Task 2: Expand Read Access
**File**: `control_plane/tools/repo_files.py`
```diff
 _ALLOWED_READ_DIR_PREFIXES: tuple[str, ...] = (
     "OUTPUTS/CONTROL_PLANE/reports/",
     "OUTPUTS/FBA_ANALYSIS/amazon_cache/",
     "OUTPUTS/cached_products/",
     "OUTPUTS/PRODUCTS_LISTS/",
+    ".claude/skills/",
+    "setup/",
     "tools/",
 )
 ...
 _ALLOWED_LIST_DIRS: tuple[str, ...] = (
     "OUTPUTS/CONTROL_PLANE/reports",
     "OUTPUTS/FBA_ANALYSIS/amazon_cache",
     "OUTPUTS/cached_products",
     "OUTPUTS/PRODUCTS_LISTS",
+    ".claude/skills",
+    "setup",
     "logs",
 )
```

### Task 3: Expand Write Access
**File**: `control_plane/tools/output_writer.py`
```diff
 _ALLOWED_WRITE_DIRS: tuple[str, ...] = (
     "OUTPUTS/CONTROL_PLANE/reports",
     "OUTPUTS/PRODUCTS_LISTS",
+    "OUTPUTS/CONTROL_PLANE/jobs/onboarding_staging",
 )
```

### Task 4: Planner Instructions
**File**: `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
```diff
+## Executing the Supplier Onboarding Skill
+
+When the user asks to onboard a supplier using a skill:
+1. Use `read_repo_file` to read `.claude/skills/supplier-onboarding/SKILL.md` to understand the 7-step workflow.
+2. Ask the user for the raw `.txt` file containing categories and selectors (usually in `setup/`). Read it via `read_repo_file`.
+3. Format their raw data into a JSON structure matching the Onboarding Wizard requirements.
+4. **CRITICAL:** Do NOT attempt to edit `config/system_config.json` yourself. Use `write_output_file` to save your generated JSON to `OUTPUTS/CONTROL_PLANE/jobs/onboarding_staging/wizard_input_<supplier>.json`.
+5. Use `enqueue_onboarding` and pass the `supplier_domain` and the `input_path` to the JSON file you just created. The backend python worker will safely update the system configs and generate the scripts.
```