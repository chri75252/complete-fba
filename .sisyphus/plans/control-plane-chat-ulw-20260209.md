# Control Plane Chat ULW Fix Plan (3 Phases, Diff-Driven) — Revised 2026-02-10

## TL;DR

**Core objective**: make Control Plane Chat reliable end-to-end:
- Chat → tool call → job JSON → worker executes → expected artifacts exist
- Runtime limits (“first 12 products”) never silently become `0`
- Cancellation works without Ctrl+C and without manually deleting `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`
- Clarify responses include real error context
- Follow-ups can use most recent `run_id` without retyping

**Critical user guardrails**:
- Avoid editing main/original workflow scripts by default.
  - **Read-only unless explicitly approved**: `tools/*` and `run_custom_*.py`.
- **No git operations/commands during execution** (no `git pull/push/fetch/merge/rebase/reset/checkout/commit/...`).
  - If git becomes absolutely necessary, STOP and ask the user.
- Prefer fixes in `control_plane/*` and `dashboard/*`.
- **Supplier onboarding generation rule (important context)**:
  - Future supplier runners (`run_custom_*.py`) and (when applicable) supplier authentication helpers are generated via the supplier-onboarding skill:
    - `.claude/skills/supplier-onboarding/`
    - `utils/supplier_onboarding_wizard.py`
  - Treat existing runners/auth helpers as generated artifacts that will be broadly similar across suppliers.
  - If behavior needs adjusting, prefer fixing the **new workflow layer** (`control_plane/*`, `dashboard/*`) or regenerating/tweaking via onboarding, rather than hand-editing an existing runner/auth script (example: the earlier EFG auth failure temptation to patch `run_custom_efghousewares-co-uk.py`).

---

## Gate 0 — Forbidden Diffs (must pass before Phase 1)

Run:
```bash
git diff --name-only
```
Assert:
- No modified paths under `tools/`
- No modified `run_custom_*.py`

If this gate fails:
- STOP.
- Do not manually edit those core scripts.
- Ask the user for explicit approval to restore the working tree (e.g., `git checkout -- <files>`).

---

## Global Rules

### Backup protocol (MANDATORY)
Before editing any file:
1) Create `backup/<reason>_<YYYYMMDD>/`
2) Copy every file you will modify
3) Verify backups exist and are non-zero

### Verification protocol (NO_CLAIMS_WITHOUT_VERIFICATION)
Prefer 3+ truth sources:
- job JSON: `OUTPUTS/CONTROL_PLANE/jobs/*/job_<run_id>.json`
- merged config: `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`
- status JSON: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
- processing state/linking map/cached products paths
- worker log: `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`

### Comment/docstring hook
- Avoid adding new comments/docstrings unless strictly necessary.

---

## Phase 1: Control-plane chat reliability (P0) — 10 Tasks + Checkpoint

### Gate 1A — system index ready
Run:
```bash
python -m control_plane build-index
python -c "import json; p='OUTPUTS/CONTROL_PLANE/index/system_index.json'; d=json.load(open(p,'r',encoding='utf-8')); inv=d.get('inventory',{}); print('workflow_keys' in inv, 'suppliers' in inv)"
```
Assert:
- prints `True True`

### Shared variable convention (Phase 1)
- When a write tool returns `run_id`, capture it as `RUN_ID` in your shell (PowerShell or CMD).
- All Phase 1 verifications must reference `${RUN_ID}` (or `%RUN_ID%`) consistently.

---

### Task 1.1 — Verify dashboard import routing (avoid legacy root scripts)

**Goal**: ensure Streamlit UI routes through `control_plane/chat_orchestrator.py`.

**Acceptance (command-based)**:
```bash
python -c "import dashboard.chat_panel,inspect,re; s=inspect.getsource(dashboard.chat_panel); print(bool(re.search(r'control_plane\\.chat_orchestrator', s) or re.search(r'from\\s+control_plane\\.chat_orchestrator', s)))"
```
Assert:
- prints `True`

---

### Task 1.2 — Fix expected job path strings in checklists (accuracy)

**Patch targets**:
- `control_plane/checklists.py`
- (optional) root `checklists.py` ONLY if proven used by UI

**Diff sketch**:
```diff
- OUTPUTS/CONTROL_PLANE/jobs/pending/<run_id>.json
+ OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json
```

**Acceptance**:
```bash
python -c "import pathlib; t=pathlib.Path('control_plane/checklists.py').read_text(encoding='utf-8'); print('jobs/pending/job_' in t)"
```
Assert:
- prints `True`

---

### Task 1.3 — Limits semantics: missing/blank uses defaults; explicit 0 means unlimited

**Policy**:
- Missing/null/blank → use defaults from `config/system_config.json['system']`
- Explicit `0` → unlimited (keep 0)

**Patch target**:
- `control_plane/chat_orchestrator.py` (enqueue_run request construction)

**Diff sketch**:
```diff
- max_products=int(p.get('max_products') or 0)
+ max_products=_coerce_or_default(p.get('max_products'), defaults_max_products)

- max_products_per_category=int(p.get('max_products_per_category') or 0)
+ max_products_per_category=_coerce_or_default(p.get('max_products_per_category'), defaults_max_per_cat)
```

**Acceptance (3-source, command-based)**:
```bash
python -c "import json, pathlib; rid='RUN_ID'; j=json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/jobs/pending/job_{rid}.json').read_text(encoding='utf-8')); print(j['runtime'])"
```
Assert:
- runtime matches expected defaults when omitted

---

### Task 1.4 — Pending-tool natural language edits update pending params

**Patch target**:
- `dashboard/chat_panel.py`

**Diff sketch**:
```diff
+ if re.search(r"(?:first|only|just|top)\s+(\d+)\s+products?", user_input, re.I):
+     new_params['max_products'] = int(match.group(1))
+
+ if re.search(r"\b(unlimited|no\s+limit|all\s+products)\b", user_input, re.I):
+     new_params['max_products'] = 0
```

**Acceptance**:
- Verified via Phase 1 checkpoint run (Task 1.10) + audit JSONL entry.

---

### Task 1.5 — Persist `last_run_id` after successful write tool execution

**Patch target**:
- `dashboard/chat_panel.py`

**Diff sketch**:
```diff
+ if result.get('run_id'):
+     st.session_state['last_run_id'] = result['run_id']
```

**Acceptance**:
```bash
python -c "import pathlib; t=pathlib.Path('dashboard/chat_panel.py').read_text(encoding='utf-8'); print('last_run_id' in t)"
```
Assert:
- prints `True`

---

### Task 1.6 — Read tools default run_id from `last_run_id` (UI-layer only)

**Rule**: Do NOT rely on `st.session_state` inside `control_plane/*` modules.

**Acceptance**:
- Verified in Phase 1 checkpoint by calling `show_status` without run_id and observing it uses the last run.

---

### Task 1.7 — Clarify includes error_context end-to-end

**Patch targets**:
- `control_plane/tools/clarify.py`
- `control_plane/chat_orchestrator.py`

**Diff sketch**:
```diff
- def ask_clarify(user_text: str, missing_params: list[str]) -> dict:
+ def ask_clarify(user_text: str, missing_params: list[str], error_context: str | None = None) -> dict:
```

**Acceptance**:
```bash
python -c "import inspect; import control_plane.tools.clarify as c; s=inspect.getsource(c.ask_clarify); print('error_context' in s)"
```
Assert:
- prints `True`

---

### Task 1.8 — Cancellation tool writes canonical + legacy markers

Markers:
- Canonical: `OUTPUTS/CONTROL_PLANE/status/<run_id>.cancelled`
- Legacy: `OUTPUTS/CONTROL_PLANE/lock/cancel_<run_id>.flag`

**Acceptance**:
- After invoking cancel tool, both files exist.

---

### Task 1.9 — Worker polls cancel markers and always releases lock

**Patch target**:
- `control_plane/worker.py`

**Acceptance (command-based)**:
```bash
python -c "import json, pathlib; rid='RUN_ID'; p=pathlib.Path(f'OUTPUTS/CONTROL_PLANE/status/{rid}.json'); d=json.loads(p.read_text(encoding='utf-8')); print(d.get('state'))"
```
Assert:
- prints `cancelled`

---

### Task 1.10 — Phase 1 checkpoint run (e2e proof)

Run two runs:
1) omit limits
2) explicit “first 12 products”

Evidence commands:
```bash
python -c "import json, pathlib; rid='RUN_ID'; j=json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/jobs/pending/job_{rid}.json').read_text(encoding='utf-8')); print('runtime', j['runtime'])"
python -c "import json, pathlib; rid='RUN_ID'; m=json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/overrides/{rid}/system_config.merged.json').read_text(encoding='utf-8')); print('system', m.get('system',{}).get('max_products'), m.get('system',{}).get('max_products_per_category'))"
python -c "import json, pathlib; rid='RUN_ID'; s=json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/status/{rid}.json').read_text(encoding='utf-8')); print('state', s.get('state')); print('resolved', s.get('resolved_paths',{}).get('processing_state'))"
```

Acceptance:
- runtime + merged config agree
- status points to sandbox processing_state path

---

## Phase 2: AngelWholesale pagination diagnosis WITHOUT core edits (P0)

### Task 2.1 — Use existing repo artifacts (no new code)
Use:
- `extract_angelwholesale_urls.py`
- `angelwholesale_category_snapshot.txt`
- latest logs under `logs/debug/run_custom_angelwholesale-co-uk__sandbox__*.log`

### Task 2.2 — Implement diagnostics probe (control-plane only)
Artifacts:
- `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/`
- HTML via `page.content()`, screenshot, `report.json`
- Optional opt-in: trace/HAR/Playwright DEBUG

Acceptance:
```bash
python -m control_plane diagnostics-probe --url "<angel_category_url>" --probe-id "angel_probe_001" --html --screenshot
```

### Task 2.3 — Cleanup / rollback
- delete diagnostics folder after root cause identified

---

## Phase 3: Guardrails recorded + handoff readiness (P1)

### Task 3.1 — Update docs (executor must do)
Update:
- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE_STANDARDS.md`

Must include:
- core scripts read-only by default
- prefer `control_plane/*` and `dashboard/*`
- pre-announce + backup + rollback
- remove temporary instrumentation
- **no git operations during execution**

### Task 3.2 — Update Supermemory
Store policy in project memory.

### Task 3.3 — Final handoff prompt

---

## Handoff Prompt (executor agent)

```markdown
You are executing the plan:
`.sisyphus/plans/control-plane-chat-ulw-20260209.md`

NON‑NEGOTIABLE GUARDRAILS:
- Do NOT edit main/original workflow scripts (`tools/*`, `run_custom_*.py`) unless the user explicitly approves.
- Do NOT run git commands (`git pull/push/fetch/merge/rebase/reset/checkout/commit/...`).
- Prefer changes in `control_plane/*` and `dashboard/*`.
- Always create backups under `backup/<reason>_<YYYYMMDD>/` and verify non-zero before editing.

STOP after Phase 1 checkpoint and report evidence.
```
