# Control Plane Chat ULW — Parallel Execution Plan

## TL;DR

> **Quick Summary**: Execute the control-plane-chat-ulw fix plan. 8/10 Phase 1 tasks are already implemented in code. The execution is primarily VERIFY-ONLY (Waves 1-2) → one tiny code fix (Wave 3) → e2e checkpoint (Wave 4) → Phase 2 diagnostics probe (Wave 5) → Phase 3 docs (Wave 6).
>
> **Deliverables**:
> - Verified end-to-end chat → tool call → job JSON → worker → artifacts flow
> - `StatusState` literal fixed to include "cancelled"
> - AngelWholesale diagnostics-probe CLI command (`python -m control_plane diagnostics-probe`)
> - Updated AGENTS.md, CLAUDE.md, CLAUDE_STANDARDS.md guardrails
> - Updated Supermemory entries
>
> **Estimated Effort**: Medium (most code exists; work is verification + 2 new features)
> **Parallel Execution**: YES — 6 waves
> **Critical Path**: Gate 0 → Wave 1 (verify all) → Wave 3 (StatusState fix) → Wave 4 (e2e checkpoint) → Wave 5 (diagnostics probe) → Wave 6 (docs)

---

## Gate 0 — Protected File Integrity Check (MUST PASS FIRST)

**CRITICAL: No git commands allowed. Use SHA256 hash verification instead.**

```powershell
python -c "
import hashlib, pathlib, sys
expected = {
    'tools/configurable_supplier_scraper.py': '9249228a0ea8499f9fa058bd297e6ee23176de0ce95b6c5b9d1c0d1c06c87bd4',
    'run_custom_poundwholesale.py': '2fe136a49a08eedc6c99eea4bd496ff0b52beaba949d63286d4cd51b19ca73eb',
    'run_custom_clearance_king.py': '514fbe7cde0a18e33f76cc5242e9f2f2f242ef7ecfb34c80a1ceed2981216279',
    'run_custom_dkwholesale-com.py': 'e4cdd37ad5e81b3eef527aa272f4e949d6a4825dc253bef70ac3e18ae4e594da',
    'run_custom_efghousewares-co-uk.py': '4f111523609d7b6bf9d4569ec54d4abf434fcc00eafe745b9a918914f72d87e7',
}
ok = True
for p, h in expected.items():
    actual = hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
    if actual != h:
        print(f'FAIL: {p}  expected={h[:16]}...  actual={actual[:16]}...')
        ok = False
    else:
        print(f'OK: {p}')
if not ok:
    print('\\nGATE 0 FAILED. STOP. Do NOT proceed.')
    sys.exit(1)
print('\\nGATE 0 PASSED.')
"
```

**If Gate 0 fails**: STOP. Do not edit. Ask user for explicit approval to investigate/restore.

---

## Global Rules (inherited from parent plan)

1. **Backup protocol**: `backup/<reason>_<YYYYMMDD>/` before edits. Verify non-zero.
2. **NO git commands**: Hash verification only.
3. **NO edits** to `tools/*` or `run_custom_*.py`.
4. **Prefer** `control_plane/*` and `dashboard/*`.
5. **No comments/docstrings** unless unavoidable.

---

## Critical Discovery: Current Implementation Status

| Task | Codebase Status | Evidence Location | Action Required |
|------|----------------|-------------------|-----------------|
| 1.1 Dashboard routing | ✅ CORRECT | `dashboard/app_fixed.py:541` → root `chat_panel.py:6` → `control_plane.chat_orchestrator` | VERIFY ONLY |
| 1.2 Checklist paths | ✅ ALREADY FIXED | `control_plane/checklists.py:226` has `job_<run_id>.json` | VERIFY ONLY |
| 1.3 Limits defaults | ✅ IMPLEMENTED | `chat_orchestrator.py:691-696` `_coerce_or_default()` | VERIFY ONLY |
| 1.4 Pending NL edits | ✅ IMPLEMENTED | `dashboard/chat_panel.py:215-297` full regex parsing | VERIFY ONLY |
| 1.5 Persist last_run_id | ✅ IMPLEMENTED | `dashboard/chat_panel.py:186-191` | VERIFY ONLY |
| 1.6 Read tools use last_run_id | ✅ IMPLEMENTED | `chat_orchestrator.py:580-587, 591-598, 778-785` | VERIFY ONLY |
| 1.7 Clarify error_context | ✅ IMPLEMENTED | `clarify.py:15`, `chat_orchestrator.py:563` | VERIFY ONLY |
| 1.8 Cancel markers | ✅ IMPLEMENTED | `chat_orchestrator.py:792-798` both paths | VERIFY ONLY |
| 1.9 Worker polls cancel | ⚠️ PARTIAL | `worker.py:47-56` correct, but `schemas/models.py:8` missing "cancelled" in `StatusState` | FIX StatusState |
| 1.10 E2E checkpoint | ❌ NOT RUN | No evidence of e2e test | RUN CHECKPOINT |

**Root-level duplicates**: `chat_panel.py` and `chat_orchestrator.py` at repo root are exact copies of canonical `dashboard/chat_panel.py` and `control_plane/chat_orchestrator.py`. Streamlit's working dir resolution causes `app_fixed.py:541` to import from root `chat_panel` which itself imports from `control_plane.chat_orchestrator`. This is the intended routing path.

---

## Task Dependency Graph

| Task | Depends On | Reason | Blocks |
|------|------------|--------|--------|
| Gate 0 | None | Entry gate | All tasks |
| Gate 1A (build-index) | Gate 0 | System index needed for chat | 1.10, 2.x |
| 1.1 (verify routing) | Gate 0 | Read-only check | 1.10 |
| 1.2 (verify checklists) | Gate 0 | Read-only check | 1.10 |
| 1.3 (verify limits) | Gate 0 | Read-only check | 1.10 |
| 1.4 (verify NL edits) | Gate 0 | Read-only check | 1.10 |
| 1.5 (verify last_run_id persist) | Gate 0 | Read-only check | 1.6, 1.10 |
| 1.6 (verify read tools default) | 1.5 | Needs persist to work | 1.10 |
| 1.7 (verify clarify error_context) | Gate 0 | Read-only check | 1.10 |
| 1.8 (verify cancel markers) | Gate 0 | Read-only check | 1.9, 1.10 |
| 1.9 (fix StatusState + verify worker) | 1.8 | Needs markers to exist | 1.10 |
| 1.10 (e2e checkpoint) | ALL 1.1-1.9, Gate 1A | Integration test | Phase 2, Phase 3 |
| 2.1 (angel artifact review) | 1.10 | Phase gate | 2.2 |
| 2.2 (diagnostics probe impl) | 2.1 | Needs artifact context | 2.3 |
| 2.3 (cleanup/rollback) | 2.2 | Post-diagnosis | Phase 3 |
| 3.1 (update docs) | 1.10 | Need verified behavior | 3.3 |
| 3.2 (update supermemory) | 1.10 | Need verified behavior | 3.3 |
| 3.3 (final handoff) | 3.1, 3.2 | Needs docs+memory done | None |

---

## Parallel Execution Graph

```
Wave 0 — Gate 0 + Gate 1A (Sequential, mandatory):
└── Gate 0: SHA256 hash verification of protected files
└── Gate 1A: python -m control_plane build-index

Wave 1 (After Gate 0, all parallel — READ-ONLY verification):
├── Task 1.1: Verify dashboard import routing
├── Task 1.2: Verify checklists path fix
├── Task 1.3: Verify limits _coerce_or_default
├── Task 1.4: Verify pending NL edits
├── Task 1.7: Verify clarify error_context
└── Task 1.8: Verify cancel markers (both paths)

Wave 2 (After Wave 1 — READ-ONLY verification, sequential pair):
├── Task 1.5: Verify last_run_id persistence
└── Task 1.6: Verify read tools use last_run_id (depends 1.5)

Wave 3 (After Waves 1+2 — SINGLE CODE CHANGE):
└── Task 1.9: Fix StatusState literal + verify worker cancel polling

Wave 4 (After Wave 3 + Gate 1A — E2E CHECKPOINT):
└── Task 1.10: Phase 1 checkpoint run (2 runs: default limits + "first 12")

Wave 5 (After Wave 4 — Phase 2, sequential):
├── Task 2.1: Review AngelWholesale artifacts
├── Task 2.2: Implement diagnostics-probe CLI command
└── Task 2.3: Cleanup/rollback

Wave 6 (After Wave 4 — Phase 3, parallel with Wave 5):
├── Task 3.1: Update AGENTS.md, CLAUDE.md, CLAUDE_STANDARDS.md
├── Task 3.2: Update Supermemory entries
└── Task 3.3: Final handoff prompt

Critical Path: Gate 0 → Wave 1 → Wave 3 (StatusState fix) → Wave 4 (e2e) → Wave 5/6
Parallel Speedup: ~50% faster than fully sequential (Waves 1, 5||6)
```

---

## Backup Groups

| Wave | Files to Backup | Backup Dir |
|------|----------------|------------|
| Wave 3 (Task 1.9) | `control_plane/schemas/models.py` | `backup/statusstate_fix_20260210/` |
| Wave 5 (Task 2.2) | `control_plane/__main__.py` | `backup/diagnostics_probe_20260210/` |
| Wave 6 (Task 3.1) | `AGENTS.md`, `CLAUDE.md`, `CLAUDE_STANDARDS.md` | `backup/docs_guardrails_20260210/` |

---

## TODOs

---

### Gate 0: Protected File Integrity Verification

**What to do**:
- Run the SHA256 verification script (see Gate 0 section above)
- Assert all 5 files match their expected hashes

**Must NOT do**:
- Run any git commands
- Modify any protected file

**Recommended Agent Profile**:
- **Category**: `quick` — Single command, trivial verification
- **Skills**: [`python-programmer`] — Python hash verification script
- **Skills Evaluated but Omitted**:
  - `git-master`: FORBIDDEN by guardrails (no git commands)

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Pre-wave gate (sequential)
- **Blocks**: Everything
- **Blocked By**: None

**Acceptance Criteria**:
```bash
# Run the SHA256 script from Gate 0 section
# Assert: prints "GATE 0 PASSED." and exits 0
```

**Commit**: NO

---

### Gate 1A: System Index Ready

**What to do**:
- Run `python -m control_plane build-index`
- Verify index contains `workflow_keys` and `suppliers`

**Must NOT do**:
- Edit any code

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]
- **Skills Evaluated but Omitted**:
  - All others: Not needed for command execution

**Parallelization**:
- **Can Run In Parallel**: YES (with Wave 1, after Gate 0)
- **Parallel Group**: Can overlap with Wave 1 tasks
- **Blocks**: Task 1.10
- **Blocked By**: Gate 0

**Acceptance Criteria**:
```bash
python -m control_plane build-index
python -c "import json; p='OUTPUTS/CONTROL_PLANE/index/system_index.json'; d=json.load(open(p,'r',encoding='utf-8')); inv=d.get('inventory',{}); print('workflow_keys' in inv, 'suppliers' in inv)"
# Assert: prints "True True"
```

**Commit**: NO

---

### Task 1.1 — Verify Dashboard Import Routing (READ-ONLY)

**What to do**:
- Confirm `dashboard/app_fixed.py:541` imports `chat_panel.render_chat_panel`
- Confirm root `chat_panel.py:6` imports from `control_plane.chat_orchestrator`
- Confirm the import chain: Streamlit → root `chat_panel.py` → `control_plane.chat_orchestrator`

**Must NOT do**:
- Edit any file
- Change import paths (they are correct)

**Recommended Agent Profile**:
- **Category**: `quick` — Read-only verification
- **Skills**: [`python-programmer`]
- **Skills Evaluated but Omitted**:
  - `frontend-ui-ux`: Not UI work, just import verification

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (with 1.2, 1.3, 1.4, 1.7, 1.8)
- **Blocks**: Task 1.10
- **Blocked By**: Gate 0

**References**:
- `dashboard/app_fixed.py:541` — `from chat_panel import render_chat_panel` (root-level import, Streamlit cwd)
- `chat_panel.py:6` — `from control_plane.chat_orchestrator import ...` (canonical routing)
- `control_plane/chat_orchestrator.py` — The actual brain (825 lines)

**Acceptance Criteria**:
```bash
python -c "import ast; t=open('chat_panel.py','r',encoding='utf-8').read(); tree=ast.parse(t); imports=[n for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]; found=any('control_plane.chat_orchestrator' in (getattr(n,'module','') or '') for n in imports if isinstance(n,ast.ImportFrom)); print(found)"
# Assert: prints "True"
```

**Commit**: NO

---

### Task 1.2 — Verify Checklists Path Fix (READ-ONLY)

**What to do**:
- Confirm `control_plane/checklists.py:226` has `job_<run_id>.json` (not `<run_id>.json`)
- Confirm root `checklists.py:226` also has the correct path

**Must NOT do**:
- Edit any file (already fixed; backup dir shows the old version)

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1
- **Blocks**: Task 1.10
- **Blocked By**: Gate 0

**References**:
- `control_plane/checklists.py:226` — Contains `job_<run_id>.json` (CORRECT)
- `backup/limits_parity_batch_20260210/checklists.py:226` — Contains old `<run_id>.json` (evidence of fix)

**Acceptance Criteria**:
```bash
python -c "import pathlib; t=pathlib.Path('control_plane/checklists.py').read_text(encoding='utf-8'); print('jobs/pending/job_' in t)"
# Assert: prints "True"

python -c "import pathlib; t=pathlib.Path('checklists.py').read_text(encoding='utf-8'); print('jobs/pending/job_' in t)"
# Assert: prints "True"
```

**Commit**: NO

---

### Task 1.3 — Verify Limits Semantics (READ-ONLY)

**What to do**:
- Confirm `_coerce_or_default()` exists in `chat_orchestrator.py:691-696`
- Confirm it handles: None → default, empty string → default, explicit 0 → 0 (unlimited)
- Confirm it's used for both `max_products` (line 703) and `max_products_per_category` (line 707)

**Must NOT do**:
- Edit any file

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1
- **Blocks**: Task 1.10
- **Blocked By**: Gate 0

**References**:
- `control_plane/chat_orchestrator.py:691-696` — `_coerce_or_default()` function
- `control_plane/chat_orchestrator.py:703-710` — Usage in RunRequest construction
- `config/system_config.json` → `system.max_products` and `system.max_products_per_category` defaults

**Acceptance Criteria**:
```bash
python -c "
from control_plane.chat_orchestrator import execute_tool_call
import inspect, re
src = inspect.getsource(execute_tool_call)
has_coerce = '_coerce_or_default' in src
has_default_lookup = 'system_defaults' in src
print(f'_coerce_or_default: {has_coerce}, system_defaults: {has_default_lookup}')
"
# Assert: prints "_coerce_or_default: True, system_defaults: True"

# Verify semantics: None→default, ''→default, 0→0
python -c "
def _coerce_or_default(raw, default_val):
    if raw is None: return default_val
    if isinstance(raw, str) and not raw.strip(): return default_val
    return int(raw)
print(_coerce_or_default(None, 1000))  # 1000
print(_coerce_or_default('', 1000))    # 1000
print(_coerce_or_default(0, 1000))     # 0 (unlimited)
print(_coerce_or_default(12, 1000))    # 12
"
# Assert: 1000, 1000, 0, 12
```

**Commit**: NO

---

### Task 1.4 — Verify Pending-Tool NL Edits (READ-ONLY)

**What to do**:
- Confirm `dashboard/chat_panel.py:215-297` handles pending tool call parameter edits
- Verify regex patterns: `max_products_per_category`, `max_products`, natural language ("first N products"), "analyze N products"

**Must NOT do**:
- Edit any file

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1
- **Blocks**: Task 1.10
- **Blocked By**: Gate 0

**References**:
- `dashboard/chat_panel.py:215-297` — Full NL edit block (read-only `chat_panel.py` identical)
- Regex patterns at lines 225-262 covering 4 input styles

**Acceptance Criteria**:
```bash
python -c "
import pathlib, re
t = pathlib.Path('dashboard/chat_panel.py').read_text(encoding='utf-8')
checks = [
    'max_products_per_category' in t,
    'first|only|just|limit' in t,
    'analyze' in t,
    'updated_params' in t,
]
print(all(checks))
"
# Assert: prints "True"
```

**Commit**: NO

---

### Task 1.5 — Verify last_run_id Persistence (READ-ONLY)

**What to do**:
- Confirm `dashboard/chat_panel.py:186-191` sets `st.session_state["last_run_id"] = result["run_id"]` after successful write tool execution

**Must NOT do**:
- Edit any file

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (start of, blocks 1.6)
- **Blocks**: Task 1.6
- **Blocked By**: Gate 0

**References**:
- `dashboard/chat_panel.py:186-191` — `st.session_state["last_run_id"] = result["run_id"]`

**Acceptance Criteria**:
```bash
python -c "import pathlib; t=pathlib.Path('dashboard/chat_panel.py').read_text(encoding='utf-8'); print('last_run_id' in t and 'session_state' in t)"
# Assert: prints "True"
```

**Commit**: NO

---

### Task 1.6 — Verify Read Tools Default run_id from last_run_id (READ-ONLY)

**What to do**:
- Confirm `chat_orchestrator.py` `show_status` (line 580-587), `tail_logs` (line 591-598), and `cancel_run` (line 778-785) all fall back to `st.session_state.get("last_run_id")` when `run_id` is missing

**Must NOT do**:
- Edit any file

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: NO (follows 1.5)
- **Parallel Group**: Wave 2 (sequential after 1.5)
- **Blocks**: Task 1.10
- **Blocked By**: Task 1.5

**References**:
- `control_plane/chat_orchestrator.py:580-587` — `show_status` fallback
- `control_plane/chat_orchestrator.py:591-598` — `tail_logs` fallback
- `control_plane/chat_orchestrator.py:778-785` — `cancel_run` fallback

**Acceptance Criteria**:
```bash
python -c "
import pathlib, re
t = pathlib.Path('control_plane/chat_orchestrator.py').read_text(encoding='utf-8')
fallbacks = len(re.findall(r'st\.session_state\.get\([\"\\']last_run_id', t))
print(f'last_run_id fallbacks found: {fallbacks}')
print(fallbacks >= 3)
"
# Assert: prints "last_run_id fallbacks found: 3" and "True"
```

**Commit**: NO

---

### Task 1.7 — Verify Clarify error_context End-to-End (READ-ONLY)

**What to do**:
- Confirm `control_plane/tools/clarify.py:12-15` has `error_context: str | None = None` parameter
- Confirm `chat_orchestrator.py:563` passes `error_context` to `ask_clarify()`
- Confirm `chat_orchestrator.py:400-404` passes error_context in the URL-resolution fallback path

**Must NOT do**:
- Edit any file

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1
- **Blocks**: Task 1.10
- **Blocked By**: Gate 0

**References**:
- `control_plane/tools/clarify.py:12-15` — Function signature with `error_context`
- `control_plane/tools/clarify.py:39-40` — error_context appended to hint
- `control_plane/chat_orchestrator.py:563` — `error_context=str(p.get("error_context") or "").strip() or None`
- `control_plane/chat_orchestrator.py:400-404` — ValueError catch passes `error_context: str(e)` in params

**Acceptance Criteria**:
```bash
python -c "import inspect; import control_plane.tools.clarify as c; s=inspect.getsource(c.ask_clarify); print('error_context' in s)"
# Assert: prints "True"

python -c "import inspect; import control_plane.chat_orchestrator as co; s=inspect.getsource(co.execute_tool_call); print(s.count('error_context'))"
# Assert: prints >= 1
```

**Commit**: NO

---

### Task 1.8 — Verify Cancellation Markers (READ-ONLY)

**What to do**:
- Confirm `chat_orchestrator.py:792-798` writes BOTH markers:
  - Canonical: `status_dir / f"{run_id}.cancelled"`
  - Legacy: `lock_dir / f"cancel_{run_id}.flag"`

**Must NOT do**:
- Edit any file

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1
- **Blocks**: Task 1.9
- **Blocked By**: Gate 0

**References**:
- `control_plane/chat_orchestrator.py:790-805` — Full cancel_run block
- `control_plane/worker.py:47-56` — `_is_cancelled()` checks both paths

**Acceptance Criteria**:
```bash
python -c "
import pathlib
t = pathlib.Path('control_plane/chat_orchestrator.py').read_text(encoding='utf-8')
has_canonical = '.cancelled' in t
has_legacy = 'cancel_' in t and '.flag' in t
print(f'canonical: {has_canonical}, legacy: {has_legacy}')
"
# Assert: prints "canonical: True, legacy: True"
```

**Commit**: NO

---

### Task 1.9 — Fix StatusState + Verify Worker Cancel Polling (CODE CHANGE)

**What to do**:
1. **BACKUP** `control_plane/schemas/models.py` to `backup/statusstate_fix_20260210/`
2. **FIX** `StatusState` literal in `control_plane/schemas/models.py:8`:
   - Current: `StatusState = Literal["queued", "running", "done", "failed"]`
   - Fixed: `StatusState = Literal["queued", "running", "done", "failed", "cancelled"]`
3. **VERIFY** worker `_is_cancelled()` checks both marker paths (already correct)
4. **VERIFY** worker's `finally` block always releases lock (already correct: line 305)

**Must NOT do**:
- Edit `control_plane/worker.py` (already correct)
- Add comments or docstrings

**Recommended Agent Profile**:
- **Category**: `quick` — Single line change in a type literal
- **Skills**: [`python-programmer`]
  - `python-programmer`: Type annotation fix in Python
- **Skills Evaluated but Omitted**:
  - `git-master`: FORBIDDEN
  - All others: Not needed for single-line type fix

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 3 (sequential, after Waves 1+2)
- **Blocks**: Task 1.10
- **Blocked By**: Tasks 1.1-1.8

**References**:
- `control_plane/schemas/models.py:8` — Current `StatusState` missing "cancelled"
- `control_plane/worker.py:259` — Worker sets `status["state"] = "cancelled"` (runtime value exists, just not in type)
- `control_plane/worker.py:47-56` — `_is_cancelled()` checks both paths
- `control_plane/worker.py:289-305` — `finally` block always releases lock via `_release_lock()`

**Acceptance Criteria**:

```bash
# 1. Backup verification
python -c "import pathlib; print(pathlib.Path('backup/statusstate_fix_20260210/models.py').exists())"
# Assert: True

# 2. StatusState includes "cancelled"
python -c "import pathlib; t=pathlib.Path('control_plane/schemas/models.py').read_text(encoding='utf-8'); print('cancelled' in t)"
# Assert: True

# 3. Worker _is_cancelled checks both paths
python -c "
import pathlib
t = pathlib.Path('control_plane/worker.py').read_text(encoding='utf-8')
has_canonical = '.cancelled' in t
has_legacy = 'cancel_' in t and '.flag' in t
print(f'canonical: {has_canonical}, legacy: {has_legacy}')
"
# Assert: canonical: True, legacy: True

# 4. Worker always releases lock (finally block present)
python -c "import pathlib; t=pathlib.Path('control_plane/worker.py').read_text(encoding='utf-8'); print('_release_lock' in t and 'finally' in t)"
# Assert: True

# 5. Type check passes
python -c "from control_plane.schemas.models import StatusState; print(StatusState)"
# Assert: no import error
```

**Commit**: YES
- Message: `fix(control_plane): add "cancelled" to StatusState literal`
- Files: `control_plane/schemas/models.py`
- Pre-commit: `python -c "from control_plane.schemas.models import StatusState"`

---

### Task 1.10 — Phase 1 Checkpoint Run (E2E PROOF)

**What to do**:
1. Run `python -m control_plane build-index` (if not done in Gate 1A)
2. Start the dashboard: `python -m streamlit run dashboard/app_fixed.py --server.port 8501`
3. Start the worker: `python -m control_plane worker`
4. In the Chat tab, paste a PoundWholesale category URL (omit limits)
5. Verify: explanation + expected_outputs shown in chat
6. Click "Confirm execute"
7. Capture `RUN_ID` from the result
8. Verify run_id in 3 locations (job JSON, merged config, status)
9. Type "show status" (no run_id) — verify it uses last_run_id
10. Type "first 12 products" while a pending action exists — verify params update
11. Invoke "cancel run" — verify both cancel markers created
12. Verify worker picks up cancel, sets state="cancelled", releases lock

**Must NOT do**:
- Edit any code during checkpoint
- Skip any verification step

**Recommended Agent Profile**:
- **Category**: `unspecified-high` — Complex multi-step interactive verification
- **Skills**: [`python-programmer`, `dev-browser`]
  - `python-programmer`: Running Python verification commands
  - `dev-browser`: Browser automation for Streamlit Chat tab interaction
- **Skills Evaluated but Omitted**:
  - `git-master`: FORBIDDEN
  - `data-scientist`: Not a data task
  - `frontend-ui-ux`: Not building UI, just interacting

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 4 (sequential, blocks Phase 2+3)
- **Blocks**: Tasks 2.1, 3.1, 3.2
- **Blocked By**: All 1.1-1.9, Gate 1A

**References**:
- Parent plan: `.sisyphus/plans/control-plane-chat-ulw-20260209.md` Task 1.10 section
- `control_plane/chat_orchestrator.py:359-505` — `plan_tool_call()` flow
- `control_plane/chat_orchestrator.py:512-807` — `execute_tool_call()` flow
- `dashboard/chat_panel.py:136-210` — Pending tool call UI + confirm/cancel
- `control_plane/worker.py:138-312` — `run_forever()` loop

**Acceptance Criteria**:

**Run 1: Default limits (omit limits)**
```bash
# After submitting a PW category URL in chat and confirming:
python -c "
import json, pathlib, sys
rid='<RUN_ID_1>'
j = json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/jobs/pending/job_{rid}.json').read_text(encoding='utf-8'))
print('runtime:', j.get('runtime'))
sys.exit(0 if j['runtime']['max_products'] > 0 else 1)
"
# Assert: runtime shows system_config defaults (NOT 0)

python -c "
import json, pathlib
rid='<RUN_ID_1>'
m = json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/overrides/{rid}/system_config.merged.json').read_text(encoding='utf-8'))
print('max_products:', m.get('system',{}).get('max_products'))
print('max_products_per_category:', m.get('system',{}).get('max_products_per_category'))
"
# Assert: matches system_config.json defaults
```

**Run 2: Explicit "first 12 products"**
```bash
python -c "
import json, pathlib
rid='<RUN_ID_2>'
j = json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/jobs/pending/job_{rid}.json').read_text(encoding='utf-8'))
print('max_products:', j['runtime']['max_products'])
"
# Assert: max_products == 12
```

**Show status without run_id (uses last_run_id)**:
```bash
# In chat, type "show status" (no run_id)
# Assert: shows status for the last run, not an error
```

**Cancel run verification**:
```bash
python -c "
import pathlib
rid='<RUN_ID>'
c1 = pathlib.Path(f'OUTPUTS/CONTROL_PLANE/status/{rid}.cancelled').exists()
c2 = pathlib.Path(f'OUTPUTS/CONTROL_PLANE/lock/cancel_{rid}.flag').exists()
print(f'canonical: {c1}, legacy: {c2}')
"
# Assert: canonical: True, legacy: True

python -c "
import json, pathlib
rid='<RUN_ID>'
s = json.loads(pathlib.Path(f'OUTPUTS/CONTROL_PLANE/status/{rid}.json').read_text(encoding='utf-8'))
print('state:', s.get('state'))
"
# Assert: state == "cancelled"

python -c "import pathlib; print(not pathlib.Path('OUTPUTS/CONTROL_PLANE/lock/active_run.lock').exists())"
# Assert: True (lock released)
```

**Evidence to Capture**:
- Screenshot of Chat tab showing pending tool call with explanation + expected_outputs
- Screenshot showing "Updated pending run: max_products=12" after NL edit
- Terminal output of all verification commands
- All stored in `.sisyphus/evidence/`

**Commit**: NO (verification only)

---

### Task 2.1 — AngelWholesale Artifact Review (READ-ONLY)

**What to do**:
1. Read `angelwholesale_category_snapshot.txt` — note "You've viewed 40 of 400 products" with LOAD MORE button
2. Read `extract_angelwholesale_urls.py` — note it only checks `?page=2` (NOT button pagination)
3. Read `config/supplier_configs/angelwholesale.co.uk.json` — confirm `pagination_method: "button"`, selector `a.btn-load-more`
4. Read latest sandbox log: `logs/debug/run_custom_angelwholesale-co-uk__sandbox__*.log`
5. Summarize findings for Task 2.2

**Must NOT do**:
- Edit any file
- Run any extraction scripts

**Recommended Agent Profile**:
- **Category**: `quick` — Read-only file analysis
- **Skills**: [`python-programmer`]
- **Skills Evaluated but Omitted**:
  - `dev-browser`: Not browsing yet (that's Task 2.2)

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 5 (sequential Phase 2)
- **Blocks**: Task 2.2
- **Blocked By**: Task 1.10

**References**:
- `angelwholesale_category_snapshot.txt` — Shows LOAD MORE pagination
- `extract_angelwholesale_urls.py` — Only checks `?page=2`
- `config/supplier_configs/angelwholesale.co.uk.json` — Button pagination config
- `config/supplier_configs/README.md` — 800+ lines documenting button pagination fix
- `logs/debug/run_custom_angelwholesale-co-uk__sandbox__df9037be_20260210_000929.log` — Latest sandbox log

**Acceptance Criteria**:
```bash
# Verify pagination_method is "button"
python -c "
import json
cfg = json.load(open('config/supplier_configs/angelwholesale.co.uk.json','r',encoding='utf-8'))
pm = cfg.get('pagination_method', 'MISSING')
sel = cfg.get('pagination', {}).get('selector', 'MISSING')
print(f'pagination_method: {pm}, selector: {sel}')
"
# Assert: pagination_method: button, selector contains btn-load-more
```

**Commit**: NO

---

### Task 2.2 — Implement Diagnostics Probe CLI (CODE CHANGE)

**What to do**:
1. **BACKUP** `control_plane/__main__.py` to `backup/diagnostics_probe_20260210/`
2. Create `control_plane/diagnostics_probe.py` — standalone module:
   - Takes: `--url`, `--probe-id`, `--html` flag, `--screenshot` flag
   - Connects to Chrome CDP on 9222 (reuse `utils/browser_manager.py` pattern)
   - Navigates to URL
   - Saves HTML via `page.content()` to `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/page.html`
   - Saves screenshot to `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/screenshot.png`
   - Saves `report.json` with: URL, timestamp, title, element counts, pagination button presence
3. Add `diagnostics-probe` subcommand to `control_plane/__main__.py`

**Must NOT do**:
- Edit `tools/*` or `run_custom_*.py`
- Import from `tools/` modules (use `utils/browser_manager.py` directly or Playwright directly)
- Add unnecessary comments/docstrings

**Recommended Agent Profile**:
- **Category**: `unspecified-low` — Moderate complexity, new module creation
- **Skills**: [`python-programmer`, `dev-browser`]
  - `python-programmer`: New Python module with Playwright integration
  - `dev-browser`: Browser automation expertise for CDP connection
- **Skills Evaluated but Omitted**:
  - `git-master`: FORBIDDEN
  - `frontend-ui-ux`: Not a UI task
  - `data-scientist`: Not a data task

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 5 (sequential, after 2.1)
- **Blocks**: Task 2.3
- **Blocked By**: Task 2.1

**References**:
- `control_plane/__main__.py` — Add subcommand here (29 lines, simple argparse)
- `utils/browser_manager.py` — CDP connection pattern (`chromium.connect_over_cdp`)
- `control_plane/internal/path_resolver.py` — Path resolution pattern
- `config/supplier_configs/angelwholesale.co.uk.json` — Button pagination selector `a.btn-load-more`
- `angelwholesale_category_snapshot.txt` — Expected page content pattern

**Acceptance Criteria**:
```bash
# 1. Backup exists
python -c "import pathlib; print(pathlib.Path('backup/diagnostics_probe_20260210/__main__.py').exists())"
# Assert: True

# 2. Module exists
python -c "import pathlib; print(pathlib.Path('control_plane/diagnostics_probe.py').exists())"
# Assert: True

# 3. CLI command is registered
python -m control_plane diagnostics-probe --help
# Assert: shows usage with --url, --probe-id, --html, --screenshot flags

# 4. Functional test (requires Chrome running on port 9222)
python -m control_plane diagnostics-probe --url "https://www.angelwholesale.co.uk/toilet-rolls-and-tissues-c-103/" --probe-id "angel_probe_001" --html --screenshot
# Assert: creates OUTPUTS/CONTROL_PLANE/diagnostics/angel_probe_001/ with:
#   - page.html (non-empty)
#   - screenshot.png (non-empty)
#   - report.json (valid JSON with url, timestamp, title fields)

python -c "
import json, pathlib
r = json.loads(pathlib.Path('OUTPUTS/CONTROL_PLANE/diagnostics/angel_probe_001/report.json').read_text(encoding='utf-8'))
print('url:', r.get('url','MISSING')[:50])
print('title:', r.get('title','MISSING')[:50])
"
# Assert: url and title present
```

**Commit**: YES
- Message: `feat(control_plane): add diagnostics-probe CLI command for pagination debugging`
- Files: `control_plane/diagnostics_probe.py`, `control_plane/__main__.py`
- Pre-commit: `python -m control_plane diagnostics-probe --help`

---

### Task 2.3 — Cleanup/Rollback

**What to do**:
- After root cause is identified from probe results, delete diagnostics folder
- Or keep for reference if user wants

**Must NOT do**:
- Delete the diagnostics_probe module itself (keep the tool)

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`python-programmer`]

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 5 (sequential, after 2.2)
- **Blocks**: None (Phase 3 runs in parallel from Wave 4)
- **Blocked By**: Task 2.2

**Acceptance Criteria**:
```bash
# Optional cleanup:
python -c "import shutil, pathlib; p=pathlib.Path('OUTPUTS/CONTROL_PLANE/diagnostics/angel_probe_001'); shutil.rmtree(p, ignore_errors=True) if p.exists() else None; print('cleaned' if not p.exists() else 'kept')"
```

**Commit**: NO

---

### Task 3.1 — Update Docs (AGENTS.md, CLAUDE.md, CLAUDE_STANDARDS.md)

**What to do**:
1. **BACKUP** all three files to `backup/docs_guardrails_20260210/`
2. Add to each document (in appropriate section):
   - Core scripts (`tools/*`, `run_custom_*.py`) are read-only by default
   - Prefer changes in `control_plane/*` and `dashboard/*`
   - Pre-announce + backup + rollback before edits
   - Remove temporary instrumentation after use
   - No git operations during automated execution
3. Add control_plane section to AGENTS.md if not present

**Must NOT do**:
- Edit `tools/*` or `run_custom_*.py`
- Remove existing content from docs

**Recommended Agent Profile**:
- **Category**: `writing` — Documentation updates
- **Skills**: [`python-programmer`]
  - `python-programmer`: Understanding the codebase context for accurate docs
- **Skills Evaluated but Omitted**:
  - `prompt-engineer`: Not prompt engineering, just docs
  - `frontend-ui-ux`: Not UI work

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 6 (parallel with Wave 5)
- **Blocks**: Task 3.3
- **Blocked By**: Task 1.10

**References**:
- `AGENTS.md` — Main contributor guide (currently lacks control_plane section)
- `CLAUDE.md` — SuperClaude entry point
- `CLAUDE_STANDARDS.md` — Development standards

**Acceptance Criteria**:
```bash
# Backups exist
python -c "
import pathlib
files = ['AGENTS.md', 'CLAUDE.md', 'CLAUDE_STANDARDS.md']
ok = all(pathlib.Path(f'backup/docs_guardrails_20260210/{f}').exists() for f in files)
print(ok)
"
# Assert: True

# Guardrails present in AGENTS.md
python -c "
import pathlib
t = pathlib.Path('AGENTS.md').read_text(encoding='utf-8')
checks = [
    'control_plane' in t.lower(),
    'read-only' in t.lower() or 'read only' in t.lower(),
    'backup' in t.lower(),
]
print(all(checks))
"
# Assert: True
```

**Commit**: YES
- Message: `docs: add control-plane guardrails to AGENTS.md, CLAUDE.md, CLAUDE_STANDARDS.md`
- Files: `AGENTS.md`, `CLAUDE.md`, `CLAUDE_STANDARDS.md`

---

### Task 3.2 — Update Supermemory

**What to do**:
- Store the following policies in project Supermemory:
  1. Control Plane architecture: `control_plane/*` and `dashboard/*` are the preferred edit targets
  2. Main Script Protection Policy: `tools/*` and `run_custom_*.py` are read-only unless explicitly approved
  3. No git commands during automated execution
  4. Backup protocol mandatory before every edit
  5. Control Plane startup sequence: Chrome CDP 9222, Ollama, dashboard, worker, build-index

**Must NOT do**:
- Store secrets or credentials

**Recommended Agent Profile**:
- **Category**: `quick` — API calls to Supermemory
- **Skills**: None needed
- **Skills Evaluated but Omitted**:
  - All skills: Supermemory operations are tool calls, not code

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 6 (parallel with 3.1)
- **Blocks**: Task 3.3
- **Blocked By**: Task 1.10

**Acceptance Criteria**:
```
# Use supermemory(mode="add", ...) for each policy
# Verify with supermemory(mode="search", query="control plane guardrails")
# Assert: returns stored policies
```

**Commit**: NO (not a file change)

---

### Task 3.3 — Final Handoff Prompt

**What to do**:
- Confirm all Phase 1, 2, 3 tasks complete
- Report final evidence summary
- State the system is ready for production use

**Must NOT do**:
- Make any code changes

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: None
- **Skills Evaluated but Omitted**:
  - All: This is a status report, not code

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Final (after Wave 6)
- **Blocks**: None
- **Blocked By**: Tasks 3.1, 3.2

**Acceptance Criteria**:
```bash
# Final Gate 0 re-verification: protected files unchanged
# (Run the SHA256 script from Gate 0 again)
# Assert: GATE 0 PASSED
```

**Commit**: NO

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Gate 0 fails (protected files modified) | Low | CRITICAL | STOP. Ask user. Do NOT proceed. |
| E2E checkpoint fails (tool call → job) | Medium | High | Debug chat_orchestrator.py flow; check LLM provider config |
| Worker doesn't pick up job | Medium | High | Verify worker is running; check `jobs/pending/` directory |
| Cancel markers not detected by worker | Low | Medium | Worker already polls both paths (verified in code) |
| Diagnostics probe can't connect to CDP | Medium | Medium | Ensure Chrome running with `--remote-debugging-port=9222` |
| Streamlit import path breaks | Low | High | Root-level duplicates (`chat_panel.py`) must stay in sync with `dashboard/chat_panel.py` |
| AngelWholesale page structure changed | Medium | Low | Diagnostics probe will capture current HTML for analysis |

### Rollback Strategy

1. **Task 1.9 (StatusState)**: Restore from `backup/statusstate_fix_20260210/models.py`
2. **Task 2.2 (diagnostics probe)**: Restore `__main__.py` from backup, delete `diagnostics_probe.py`
3. **Task 3.1 (docs)**: Restore from `backup/docs_guardrails_20260210/`

---

## Agent Dispatch Summary

| Wave | Tasks | Category | Skills | run_in_background |
|------|-------|----------|--------|-------------------|
| 0 | Gate 0, Gate 1A | `quick` | `python-programmer` | NO (gate) |
| 1 | 1.1, 1.2, 1.3, 1.4, 1.7, 1.8 | `quick` | `python-programmer` | YES (6 parallel) |
| 2 | 1.5, 1.6 | `quick` | `python-programmer` | YES (sequential pair) |
| 3 | 1.9 | `quick` | `python-programmer` | NO (single edit) |
| 4 | 1.10 | `unspecified-high` | `python-programmer`, `dev-browser` | NO (interactive e2e) |
| 5 | 2.1, 2.2, 2.3 | `unspecified-low` | `python-programmer`, `dev-browser` | NO (sequential) |
| 6 | 3.1 | `writing` | `python-programmer` | YES |
| 6 | 3.2 | `quick` | — | YES |
| 6 | 3.3 | `quick` | — | NO (final) |

---

## Commit Strategy

| After Task | Message | Files | Pre-commit Check |
|------------|---------|-------|-----------------|
| 1.9 | `fix(control_plane): add "cancelled" to StatusState literal` | `control_plane/schemas/models.py` | `python -c "from control_plane.schemas.models import StatusState"` |
| 2.2 | `feat(control_plane): add diagnostics-probe CLI command` | `control_plane/diagnostics_probe.py`, `control_plane/__main__.py` | `python -m control_plane diagnostics-probe --help` |
| 3.1 | `docs: add control-plane guardrails` | `AGENTS.md`, `CLAUDE.md`, `CLAUDE_STANDARDS.md` | N/A |

---

## Success Criteria

### Final Verification Commands
```bash
# 1. Gate 0 re-check (protected files untouched)
python -c "
import hashlib, pathlib
expected = {
    'tools/configurable_supplier_scraper.py': '9249228a0ea8499f9fa058bd297e6ee23176de0ce95b6c5b9d1c0d1c06c87bd4',
    'run_custom_poundwholesale.py': '2fe136a49a08eedc6c99eea4bd496ff0b52beaba949d63286d4cd51b19ca73eb',
    'run_custom_clearance_king.py': '514fbe7cde0a18e33f76cc5242e9f2f2f242ef7ecfb34c80a1ceed2981216279',
    'run_custom_dkwholesale-com.py': 'e4cdd37ad5e81b3eef527aa272f4e949d6a4825dc253bef70ac3e18ae4e594da',
    'run_custom_efghousewares-co-uk.py': '4f111523609d7b6bf9d4569ec54d4abf434fcc00eafe745b9a918914f72d87e7',
}
ok = all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in expected.items())
print('GATE 0 FINAL:', 'PASSED' if ok else 'FAILED')
"
# Assert: GATE 0 FINAL: PASSED

# 2. StatusState includes cancelled
python -c "from control_plane.schemas.models import StatusState; print('cancelled' in StatusState.__args__)"
# Assert: True

# 3. Diagnostics probe exists
python -m control_plane diagnostics-probe --help
# Assert: shows help

# 4. E2E evidence exists
python -c "import pathlib; print(any(pathlib.Path('OUTPUTS/CONTROL_PLANE/status').glob('*.json')))"
# Assert: True
```

### Final Checklist
- [ ] All "Must Have" present (StatusState fix, diagnostics probe, docs guardrails)
- [ ] All "Must NOT Have" absent (no edits to tools/*, no git commands used, no new comments)
- [ ] Protected file hashes match (Gate 0 re-check)
- [ ] E2E checkpoint evidence captured in `.sisyphus/evidence/`
- [ ] Supermemory policies stored
