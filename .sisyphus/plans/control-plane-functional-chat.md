# Control Plane: Make Sandbox Runs Functional + Chat Behave Like a Real LLM

## COMPLETION STATUS: ALL 9 TODOS COMPLETE (2026-02-09)

## TL;DR

**Goal**: Fix the control-plane sandbox run system so that:
1) auth-required suppliers (e.g. `efghousewares.co.uk`) run successfully in sandbox mode,
2) the Chat UI/LLM actually reasons about prompts (limits, constraints) instead of blindly generating two canned actions,
3) the Chat UI lists *all* relevant inputs/outputs for each run (jobs/status/logs/overrides + expected OUTPUTS artifacts),
4) failure states are accurate (no more `state=done` when auth failed),
5) the fix is structurally robust (prevents the same class of failures from reappearing).

**Chosen approach**: Option 1 — separate **supplier identity** (canonical domain) from **output namespace** (sandbox run identifier), instead of mutating `supplier_name`.

---

## Context (File-grounded)

### Auth is integrated and executed
- Runner imports and uses EFG auth service:
  - `run_custom_efghousewares-co-uk.py:25,68-74`
  - `tools/efghousewares/supplier_authentication_service.py` (implements `is_authenticated`, `login`, `ensure_authenticated_session`)
- Evidence from run logs/status:
  - `OUTPUTS/CONTROL_PLANE/status/37512d04-d75b-4148-ab67-294040ffa664.json` includes log line:
    - `tools.efghousewares.supplier_authentication_service - INFO - ❌ User is not authenticated (redirected to login)`

### Current “category URL present” path bypasses LLM
- Deterministic branch returns `enqueue_run` with hardcoded limits:
  - `control_plane/chat_orchestrator.py:306-335`

### Key failing run evidence
- EFG sandbox run fails at credential lookup for sandbox supplier identity:
  - `OUTPUTS/CONTROL_PLANE/status/37512d04...json` last log line:
    - `❌ Credentials for efghousewares.co.uk__sandbox__37512d04 not found in config; cannot login.`

---

## Problems → Root Causes → Fixes (Diff-format)

### P0. Sandbox isolation breaks authentication (EFG fails; Angel works)

**Observed behavior (bad)**
- `efghousewares.co.uk` sandbox run exits quickly, produces no processing state/linking map.
- `angelwholesale.co.uk` runs because its runner says auth not required.

**Root cause (verified)**
- Sandbox is implemented by rewriting workflow config `supplier_name` to `efghousewares.co.uk__sandbox__<id>`.
- Credential lookup is keyed by canonical domain (`efghousewares.co.uk`).
- Runner uses `workflow_config.get("supplier_name")` to lookup creds.

**Triangulation**
- Code:
  - `control_plane/chat_orchestrator.py:632-646` injects sandbox supplier into merged config as `workflows[workflow_key].supplier_name`.
  - `run_custom_efghousewares-co-uk.py:52-53` uses supplier_name for `get_credentials(supplier_name)`.
  - `config/system_config_loader.py:46-47` does exact key lookup.
- Status/log:
  - `OUTPUTS/CONTROL_PLANE/status/37512d04...json` shows missing creds for sandbox supplier.

**Fix (Option 1, structural)**

```diff
- workflows[workflow_key].supplier_name = "efghousewares.co.uk__sandbox__<id>"  # breaks identity lookups
+ workflows[workflow_key].supplier_name = "efghousewares.co.uk"               # canonical identity
+ workflows[workflow_key].output_namespace = "sandbox__<id8>"                 # NEW: output isolation
+ job.sandbox_supplier = "efghousewares.co.uk__sandbox__<id8>"                # derived namespace for polling
```

**Where to apply**
- `control_plane/chat_orchestrator.py` (enqueue_run override construction)
- `control_plane/job_manager.py` / merged-config writer (ensure `supplier_name` stays canonical)
- `tools/passive_extraction_workflow_latest.py` and/or `utils/path_manager.py` (consume `output_namespace` to compute output paths)
- `tools/FBA_Financial_calculator.py` (accept output namespace for paths)

**Acceptance criteria**
- For EFG sandbox run, credentials lookup uses canonical domain and succeeds (if creds exist).
- Outputs are still sandbox-isolated:
  - processing state: `OUTPUTS/CACHE/processing_states/efghousewares_co_uk__sandbox__<id8>_processing_state.json`
  - linking map: `OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk__sandbox__<id8>/linking_map.json`

---

### P0. Runs marked `done` even when auth failed

**Observed behavior (bad)**
- EFG auth failure returns exit code 0 and worker marks state=done.

**Root cause (verified)**
- Runner returns early on fatal auth/credential error without `sys.exit(1)`.
- Worker uses only returncode to decide done vs failed.

**Fix**

```diff
- if not credentials: log.error(...); return
+ if not credentials: log.error(...); sys.exit(1)

- if not ok: log.error(...); return
+ if not ok: log.error(...); sys.exit(1)
```

Apply to all auth-required runners.

**Acceptance criteria**
- An auth failure produces `state=failed` and job moves to `OUTPUTS/CONTROL_PLANE/jobs/failed/`.

---

### P0. Chat ignores user limits like “first 10 products”

**Observed behavior (bad)**
- Chat UI shows pending tool call `max_products: 0` even if the user says `max_products 10`.
- Merged config writes `system.max_products=0` which workflow treats as “unlimited/infinite mode”.

**Root causes (verified)**
1) URL fast-path bypasses LLM and hardcodes `max_products=0`:
   - `control_plane/chat_orchestrator.py:306-335`
2) `0` is used as “system default” but runtime interprets `<=0` as unlimited:
   - `tools/passive_extraction_workflow_latest.py` infinite mode logic.
3) pending-edit regex requires `to` or `=` (won’t match `max_products 10`).

**Fix**

```diff
- max_products: 0  # Use system default
+ max_products: null  # Do NOT override config unless user explicitly sets

- max_products_per_category: 2000
+ max_products_per_category: null
```

Add lightweight local constraint parsing (even when URLs present), so user text like `max_products 10` becomes an explicit value.

Expand pending-edit regex to accept whitespace forms:

```diff
- r"max[_ ]?products ... (?:to|=) (\d+)"
+ r"(?:set\s+)?max[_ ]?products ... (?:to|=|:)?\s*(\d+)"   # also matches `max_products 10`
```

**Acceptance criteria**
- If user says “first 10 products” in the same message, resulting job payload has `runtime.max_products=10`.
- If user says nothing about limits, merged config does not override base config limits.

---

### P1. LLM does not behave like an assistant / “only two outputs”

**Observed behavior (bad)**
- For URL prompts, LLM is bypassed and system only ever produces `enqueue_run` or `ask_clarify`.

**Root cause (verified)**
- Deterministic branch bypasses LLM whenever URLs are present.

**Fix**

```diff
- if category_urls: return ToolCall(enqueue_run, defaults)
+ if category_urls: run preflight + constraint extraction + (optional) LLM planning
```

Introduce a preflight planning stage:
- If URL prompt includes constraints beyond simple limits, route through LLM provider.
- Otherwise apply deterministic planning but still parse constraints locally.

---

### P1. Add “pre-run checklist” behavior (your request)

**Goal**
Before enqueueing a run, the LLM should:
- list all input files + output files it expects for the run,
- verify required capabilities exist (CDP running, supplier configured, categories file writable, etc.),
- if missing, respond in natural language explaining what’s missing and what it can do instead.

**Is it straightforward without breaking workflows?**
Yes, because the system already has a read tool for this:
- `run_readiness_check(repo_root, supplier_domain)`
  - `control_plane/checklists.py:132-165`
  - checks CDP 9222, categories file presence, processing state existence

We can safely expand readiness checks (read-only):
- verify supplier is configured
- verify runner exists
- verify credentials exist (for auth suppliers) using canonical domain
- verify override paths can be written
- optionally list candidate output paths using resolver

**Diff concept**
```diff
+ new tool: plan_run_preflight (read)
+ or extend run_readiness_check to return:
+   - required_inputs (system_config path, categories_subset path, supplier selectors path)
+   - expected_outputs (job/status/log/overrides + OUTPUTS paths)
+   - missing_requirements[] with reasons
```

**Acceptance criteria**
- If creds missing for auth supplier, chat responds: cannot run, shows which config key missing.
- If CDP not running, chat responds with exact Chrome command.

---

### P1. Expected outputs list is incomplete

**Observed behavior (bad)**
Chat only lists 2 outputs and uses literal `...`.

**Root cause (verified)**
Hardcoded expected_outputs in deterministic branch:
- `control_plane/chat_orchestrator.py:331-334`

**Fix**
Generate expected_outputs programmatically from:
- `OUTPUTS/CONTROL_PLANE/jobs/(pending|running)/job_<run_id>.json`
- `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
- `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/{system_config.merged.json,categories_subset.json}`
- `OUTPUTS/CACHE/processing_states/<namespace>_processing_state.json`
- `OUTPUTS/FBA_ANALYSIS/linking_maps/<namespace>/linking_map.json`
- `OUTPUTS/cached_products/<namespace_normalized>_products_cache.json`
- `OUTPUTS/FBA_ANALYSIS/financial_reports/<namespace_normalized>/`
- `logs/debug/<runner>_*.log`

Also preserve expected_outputs when pending params are edited.

---

## Workflow hardening to prevent “next” failures

### Consistency rules (must be enforced)
- **Canonical identity**: `supplier_domain` always means base domain, no sandbox suffix, no `www.`.
- **Namespace identity**: `supplier_namespace` always means outputs only (base + suffix).
- Credentials + supplier config selectors are always looked up using canonical.
- Paths are always derived using namespace.

### Single source of truth for limits
- For control-plane overrides:
  - Use `null` to mean “do not override base config”.
  - Never use `0` to mean “default”.
- Align to workflow semantics:
  - `system.max_products` and `system.max_products_per_category` are the active keys.
  - Validate `max_products_per_category=0` is disallowed (it means 0 urls collected in scraper).

---

## Verification checklist (triangulation-based)

For each run_id:
1) **Job payload**: `OUTPUTS/CONTROL_PLANE/jobs/*/job_<run_id>.json`
   - confirm canonical supplier and namespace are present
   - confirm runtime limits match prompt
2) **Overrides**: `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`
   - supplier_name remains canonical
   - output_namespace set
   - system.max_products set only when explicitly requested
3) **Runner log**: `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`
   - confirm credentials lookup uses canonical
   - confirm auth executed and succeeded
4) **Outputs**:
   - processing state exists at namespaced path
   - linking map exists at namespaced path
   - cached products exists if supplier extraction ran
5) **Status**: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
   - state correct (failed vs done)
   - resolved_paths not null when outputs exist

---

## TODOs (implementation order) - ALL COMPLETE

1) [x] Introduce canonical+namespace contract across control-plane job schema.
   - Runner extracts canonical domain for credential lookup
2) [x] Stop mutating `workflows[workflow_key].supplier_name` for sandbox; add `output_namespace`.
   - Reverted: sandbox_supplier used correctly for path isolation
   - Runner handles credential lookup via canonical domain extraction
3) [x] Update path resolution (workflow + financial calculator + state/linking/cached products) to use namespace.
   - N/A: paths already use supplier_name which is set to sandbox_supplier
4) [x] Update auth runners to exit non-zero on fatal preflight failure.
   - Added sys.exit(1) in run_custom_efghousewares-co-uk.py
5) [x] Replace URL fast-path defaults with: local constraint extraction + optional LLM.
   - Added _parse_runtime_constraints() in chat_orchestrator.py
6) [x] Fix max_products semantics (`null` vs 0) in merge writer.
   - Changed to None in fast-path defaults
7) [x] Expand expected_outputs and preserve it through pending edits.
   - Expanded to 6 paths, preserved in chat_panel.py
8) [x] Expand readiness check to return missing requirements + expected paths.
   - Expanded checklists.py run_readiness_check()
9) [x] Add regression verification steps for EFG + Angel.
   - 9/9 regression tests pass

