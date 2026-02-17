# Plan: Comprehensive Documentation & Memory System

**Created**: 2026-02-09
**Scope**: Generate 7 granular workflow docs + atomize Supermemory + create Sentinel verification system

---

## Phase 1: Generate 7 Granular Documentation Files

### Task 1.1: COMPLETE_WORKFLOW_UPDATED_2026_Q1.md
**Location**: `docs/COMPLETE_WORKFLOW_UPDATED_2026_Q1.md`
**Contents**:
- System Architecture Overview (3 surfaces)
- Core Workflows (Classic, Operator, Chat)
- Data Flow & Persistence (paths table)
- Config Precedence
- Operational Runbooks
- Maintenance & Updates

### Task 1.2: CONTROL_PLANE_OPERATIONS.md
**Location**: `docs/CONTROL_PLANE_OPERATIONS.md`
**Contents**:
- Architecture (worker, orchestrator, job manager, paths)
- Job Lifecycle (pending→running→done/failed)
- RAG & Indexing
- Sandbox Isolation (critical)
- Troubleshooting matrix

### Task 1.3: DASHBOARD_CHAT_UI.md
**Location**: `docs/DASHBOARD_CHAT_UI.md`
**Contents**:
- UI Layout (3 tabs)
- Chat UI Architecture (confirmation gating, session-only persistence)
- Operator Tab Workflow
- Debugging UI Issues

### Task 1.4: STATE_AND_RESUME.md
**Location**: `docs/STATE_AND_RESUME.md`
**Contents**:
- Golden Rule (never manually edit)
- How Resume Works (pointers, deterministic vs heuristic)
- Atomic Writes (WindowsSaveGuardian)
- Resetting State procedure

### Task 1.5: KNOWN_SHARP_EDGES.md
**Location**: `docs/KNOWN_SHARP_EDGES.md`
**Contents**:
- OpenAI Key Hard-Exit
- Onboarding Wizard Category Paths inconsistency
- Chrome Port 9222 Collision
- IPv6 vs IPv4 CDP Binding
- Windows Path Length Limits

### Task 1.6: DOC_CODE_DRIFT_LEDGER_2026_Q1.md
**Location**: `docs/DOC_CODE_DRIFT_LEDGER_2026_Q1.md`
**Contents**:
- Table: Area | Doc Claim | Code Reality | Impact
- Dashboard, Config, Onboarding, Product Refresh, Analysis, Chat entries
- Action Plan

### Task 1.7: WORKFLOW_SURFACES.md (Quick Reference)
**Location**: `docs/WORKFLOW_SURFACES.md`
**Contents**:
- One-page-per-surface quick reference
- When to use which surface
- Dependencies checklist

---

## Phase 2: Atomize Supermemory (60-100 entries)

### Task 2.1: Generate granular memories from analysis
**Scope**: 28 existing → 60-100 granular entries
**Categories**:
- `project-config` (15): commands, paths, env vars
- `architecture` (30): per-file responsibilities, data flow
- `learned-pattern` (25): invariants, conventions, workflows
- `error-solution` (20): gotchas + fixes

**Rule**: 1 concept per memory, include file path + line anchor

### Task 2.2: Verify with search queries
- Test retrieval for: "control plane jobs", "FBA_SYSTEM_CONFIG_PATH", "chat confirmation", etc.

---

## Phase 3: Sentinel Verification System

### Task 3.1: Create utils/memory_sentinel.py
**Purpose**: Detect drift between code and memory/docs
**Features**:
- Scan critical files (config/*.json, tools/*.py, control_plane/*.py)
- Compare against memory checksums/timestamps
- Output drift report: "Since last update, X files changed"

### Task 3.2: Create .opencode/plugins/sentinel.ts (optional hook)
**Purpose**: Auto-detect file edits and prompt for memory update
**Events**: `file.edited`, `file.watcher.updated`
**Logic**:
1. Check if file matches critical patterns
2. Run sentinel.py check
3. Inject context hint or show toast: "⚠️ Critical change detected. Verify before updating memory."

### Task 3.3: Update AGENTS.md with Memory Policy
**Add section**:
```
## Memory & Documentation Update Policy

**When to Update**:
- Only after code changes are VERIFIED (tests pass, manual check complete)
- Never during active development (may revert)

**Verification Gate**:
1. Changes complete
2. Run tests/lint OR manual verification
3. Run: `python utils/memory_sentinel.py`
4. If drift detected, user confirms: "Update memory"
5. Then: Update docs + Supermemory

**Staging**:
- Draft changes to `docs/_MEMORY_STAGING.md`
- Only promote to canonical docs after verification
```

---

## Execution Order

1. Write all 7 doc files (Task 1.1-1.7)
2. Verify files written successfully
3. Atomize Supermemory entries (Task 2.1-2.2)
4. Create sentinel.py (Task 3.1)
5. Update AGENTS.md (Task 3.3)
6. Test sentinel with sample change

---

## Success Criteria

- [ ] All 7 docs exist in `docs/` directory
- [ ] 60-100 Supermemory entries created
- [ ] `utils/memory_sentinel.py` functional
- [ ] AGENTS.md updated with memory policy
- [ ] Drift detection works (tested)
