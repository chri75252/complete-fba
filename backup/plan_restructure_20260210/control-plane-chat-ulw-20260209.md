# Control Plane Chat ULW Fix Plan (Revised 2026-02-10)

## TL;DR

**Core goal**: Make Control Plane Chat reliable end-to-end:
- Chat → tool call → job JSON → worker executes → expected artifacts exist
- Runtime limits (“first 12 products”) never silently become `0`
- Cancellation works without Ctrl+C and without manual deletion of `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`
- Follow-ups can use last `run_id`
- Clarify responses include real error context (not generic)

**CRITICAL guardrail (user requirement)**: **Do not edit main/original workflow scripts** unless explicitly approved and justified.
- Main/original scripts include `tools/*` and `run_custom_*.py`.
- Prefer changes in `control_plane/*` and `dashboard/*`.

**What changed vs previous plan**:
- Removed the old “Task 5: instrument `tools/configurable_supplier_scraper.py`” approach.
- Replaced it with a **control-plane diagnostics probe** (HTML/screenshot/network/selector evidence, optional trace/HAR) implemented **only** in `control_plane/*`.

---

## 0) Non‑Negotiable Rules (read first)

### 0.1 Safety + verification
- **No claims without verification**: verify via at least 3 truth sources when applicable:
  - job JSON (`OUTPUTS/CONTROL_PLANE/jobs/...`)
  - merged config (`OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`)
  - status JSON (`OUTPUTS/CONTROL_PLANE/status/<run_id>.json`)
  - processing state / linking map / cached products paths
  - worker log (`OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`)
- Always use absolute paths in reporting.

### 0.2 Backup protocol (MANDATORY)
Before editing any file:
1) Create `backup/<reason>_<YYYYMMDD>/`
2) Copy every file you will modify
3) Verify backup file exists and non-zero

### 0.3 Main/original workflow scripts are read-only by default
**DO NOT MODIFY** (unless user explicitly approves, and only with a rollback plan):
- `tools/passive_extraction_workflow_latest.py`
- `tools/configurable_supplier_scraper.py`
- `tools/amazon_playwright_extractor.py`
- `tools/FBA_Financial_calculator.py`
- `run_custom_*.py`

**If temporary instrumentation is ever unavoidable**:
- Must be gated behind a toggle (default OFF)
- Must include a plan step to remove/revert it after root cause identification

### 0.4 Comment/docstring hook
- Avoid adding comments/docstrings unless absolutely necessary (repo hook will flag).

---

## 1) Evidence & Known Failure Modes (file-grounded)

### 1.1 Runtime limits defaulting to 0 → “INFINITE MODE”
- Failure mode: missing/null limits get coerced via `or 0` → job JSON and merged config store `0` → workflow runs “infinite mode”.
- Evidence from plan (historical): run `df9037be` had job runtime `0/0` and merged config `0/0` while base config defaults were non-zero.

### 1.2 AngelWholesale “0 URLs collected” symptom
- Observed log signature (historical): `✅ Button pagination complete: 0 unique URLs collected`.
- Known site behavior evidence: `angelwholesale_category_snapshot.txt` indicates **LOAD MORE** / “viewed 40 of 400 products”, strongly suggesting button/infinite pagination.

### 1.3 Clarify drops error context
- Planner includes `error_context`, executor didn’t pass it through to clarify tool.

### 1.4 Cancellation hazards
- Worker needs deterministic cancel marker polling and safe lock cleanup.

---

## 2) Critical Preflight Checkpoints (Gates)

### Gate A — “No core edits” gate
Run:
```bash
git diff --name-only
```
Assert:
- No modified paths under `tools/`
- No modified `run_custom_*.py`

### Gate B — Control-plane index exists
Run:
```bash
python -m control_plane build-index
```
Assert:
- `OUTPUTS/CONTROL_PLANE/index/system_index.json` exists and contains `inventory.workflow_keys` and `inventory.suppliers`.

---

## 3) Execution Strategy (Waves + checkpoints)

**Checkpoint policy**: Stop after each wave and request review/testing output.
- Wave 1 checkpoint: limits + job artifacts consistent
- Wave 2 checkpoint: cancel end-to-end
- Wave 3 checkpoint: AngelWholesale probe produces actionable evidence
- Wave 4 checkpoint: clarify + follow-up UX correctness
- Wave 5 checkpoint: documentation + memory guardrails recorded

---

## 4) TODOs (Granular, agent-executable)

### Wave 0 — Undo/verify previous risky edits (P0)

**0.1 Verify main scripts are reverted**
- Confirm no diffs under `tools/` or `run_custom_*.py` (Gate A).

**0.2 Record what was reverted (for audit trail)**
- Note that prior exploratory edits to `tools/configurable_supplier_scraper.py` and several `run_custom_*.py` were reverted to reduce risk.
- Backups retained under `backup/main_scripts_pre_revert_20260210/`.

Acceptance:
- Gate A passes.

---

### Wave 1 — Limits parity + proof (P0)

**Goal**: Ensure missing runtime limits use base config defaults (not `0`).

**Important constraint**: Prefer `control_plane/*` + `dashboard/*`. Avoid editing root-level legacy chat scripts unless verified necessary.

**1.1 Verify which orchestrator the dashboard actually uses**
- Determine whether `dashboard/chat_panel.py` imports `control_plane/chat_orchestrator.py` vs root `chat_orchestrator.py`.
- If dashboard is already using control-plane orchestrator, **do not edit** root `chat_orchestrator.py`; treat it as legacy.
- If dashboard uses root orchestrator, refactor dashboard import routing to use `control_plane/chat_orchestrator.py` (preferred), rather than patching root scripts.

**1.2 Enqueue run with omitted limits (null/blank)**
- Use Chat UI tool flow to enqueue a run without specifying `max_products` / `max_products_per_category`.

**1.3 Verify 3+ sources for limits**
- Job JSON: `OUTPUTS/CONTROL_PLANE/jobs/*/job_<run_id>.json` → `runtime.max_products` and `runtime.max_products_per_category` are non-zero defaults.
- Merged config: `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json` → `system.max_products` and `system.max_products_per_category` match.
- Logs: `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log` does not contain `INFINITE MODE DETECTED`.

**1.4 Enqueue run with explicit “first 12 products”**
- Use pending-tool edit flow in chat panel.

Acceptance:
- Both runs show correct runtime values in job + merged config.
- Status JSON points to sandbox paths.

---

### Wave 2 — Cancel wiring (P0)

**Goal**: Cancellation works without Ctrl+C; lock always released.

**2.1 Canonical cancel marker**
- Canonical file: `OUTPUTS/CONTROL_PLANE/status/<run_id>.cancelled`.
- Backward compatible marker (optional): `OUTPUTS/CONTROL_PLANE/lock/cancel_<run_id>.flag`.

**2.2 Worker behavior**
- Worker must poll cancel marker while subprocess running.
- On cancel:
  - terminate subprocess
  - set status `state="cancelled"`
  - write final status with tail log lines
  - move job to `jobs/failed/`
  - release `active_run.lock`
  - remove cancel marker(s)

Acceptance:
- Cancelling a running run produces a final status with `state="cancelled"`.
- `OUTPUTS/CONTROL_PLANE/lock/active_run.lock` removed.

---

### Wave 3 — AngelWholesale pagination diagnosis WITHOUT core edits (P0)

**Goal**: Produce actionable evidence for why URL collection yielded 0, without touching `tools/*`.

#### 3.1 Use existing non-core diagnostics first (no new code)
- Run `extract_angelwholesale_urls.py` against a single category URL known to exhibit LOAD MORE.
- Compare results to:
  - `angelwholesale_category_snapshot.txt`
  - latest Angel sandbox logs under `logs/debug/run_custom_angelwholesale-co-uk__sandbox__*.log`

Acceptance:
- Record whether raw HTML contains product URLs (yes/no) and sample patterns.

#### 3.2 Implement a control-plane “diagnostics probe” (new workflow layer only)

**Implementation constraints**:
- Must be implemented under `control_plane/*` (and optionally `dashboard/*`).
- Must NOT import `tools/amazon_playwright_extractor.py` (OpenAI key hard-gate risk).
- Default capture must avoid secrets/PII as much as possible.

**Probe outputs (per probe_id)**
Write under:
- `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/`

Artifacts:
- `page_00_initial.html` (from `page.content()`)
- `page_00_initial.png` (screenshot)
- `page_01_after_click.html`
- `page_01_after_click.png`
- `report.json` containing:
  - URL
  - url selector match counts
  - extracted href samples
  - pagination button selector resolution (found/visible)
  - requests summary after click (count, status>=400)

**Optional artifacts (opt-in flags only)**
- Playwright trace (`trace.zip`)
- HAR (`network.har`) using `record_har_content="omit"`
- Playwright DEBUG logs via subprocess env `DEBUG=pw:api` / `DEBUG=pw:browser*`

#### 3.3 Privacy / PII mitigations
- Default: do NOT write HAR/trace unless user opts in.
- If trace/HAR is enabled:
  - require `--redact` mode in probe
  - store under run-specific diagnostics dir
  - include explicit cleanup step (below)

#### 3.4 Cleanup / rollback (MANDATORY)
- Provide a deterministic deletion step for `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/` once root cause identified.

Acceptance (agent-executable):
```bash
python -m control_plane diagnostics-probe --url "<angel_category_url>" --probe-id "angel_probe_001" --html --screenshot
```
Assert:
- exit code 0
- `OUTPUTS/CONTROL_PLANE/diagnostics/angel_probe_001/report.json` exists and non-empty
- html/png artifacts exist and non-empty

---

### Wave 4 — Clarify + follow-up context (P1)

**4.1 Clarify must include error_context**
- Ensure tool schema includes `error_context`.
- Ensure execution passes it into clarify tool.

**4.2 Remember last_run_id**
- After successful enqueue, store `st.session_state["last_run_id"]`.
- Read tools (`show_status`, `tail_logs`) should fall back to that when run_id omitted.

Acceptance:
- Run a tool call missing run_id and confirm it resolves to last_run_id.

---

### Wave 5 — Guardrails recorded in docs + memory (P1)

**Important**: Prometheus cannot edit repo docs outside `.sisyphus/*`. The executor agent must apply doc edits.

**5.1 Update human + agent guidance docs**
Add a short “Main Script Change Policy” section to:
- `AGENTS.md` (best placement: after Backup Protocol)
- `CLAUDE.md` (best placement: after Mandatory Backup Protocol)
- `CLAUDE_STANDARDS.md` (best placement: after Update Protocol)

Content must include:
- “tools/* and run_custom_*.py are read-only by default”
- “prefer control_plane/dashboard changes”
- “must pre-announce + backup + rollback plan before any core edit”
- “temporary instrumentation must be removed after diagnosis”

**5.2 Update project memory**
- Store the same policy in Supermemory as a persistent project preference.

Acceptance:
- Diffs show only documentation updates (no core script edits).

---

## 5) Handoff Prompt (for the next executor agent)

Use this prompt verbatim:

```markdown
You are executing the revised ULW plan:
`.sisyphus/plans/control-plane-chat-ulw-20260209.md`

NON-NEGOTIABLE GUARDRAILS:
- Do NOT edit main/original workflow scripts (`tools/*`, `run_custom_*.py`) unless the user explicitly approves.
- Prefer changes in `control_plane/*` and `dashboard/*`.
- Always create backups under `backup/<reason>_<YYYYMMDD>/` and verify non-zero before editing.
- Avoid comments/docstrings unless absolutely necessary (repo hook).

CHECKPOINTS:
- Stop after each wave and report evidence (job JSON + merged config + status JSON + processing state paths + logs).

WAVE 3 KEY CHANGE:
- Do NOT add instrumentation to `tools/configurable_supplier_scraper.py`.
- Instead, implement a `control_plane` diagnostics probe that emits HTML/screenshot/network evidence under `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/`, with opt-in HAR/trace.
- Include mandatory cleanup step for probe artifacts.

Before starting, run Gate A:
`git diff --name-only` and confirm no `tools/` or `run_custom_*.py` modifications.
```
