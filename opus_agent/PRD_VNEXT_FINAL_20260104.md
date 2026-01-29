# PRD / Tech Spec — FBA Analysis Agent vNext (Opus Pipeline Upgrade)

**Version:** vNext Final v2  
**Date:** 2026-01-04 (Asia/Dubai)  
**Status:** PHASE 1 — PLANNING ONLY (Implementation requires explicit approval)  
**Author:** Staff Engineer / Agent Architect

---

## TABLE OF CONTENTS

1. [Authoritative Inputs & Conflict Resolution](#1-authoritative-inputs--conflict-resolution)
2. [Current State Audit (Opus Pipeline)](#2-current-state-audit-opus-pipeline)
3. [Problem Statement](#3-problem-statement)
4. [Requirements Summary (From BUILD PROMPT)](#4-requirements-summary-from-build-prompt)
5. [Parity Checklist: Opus Current vs Required Behavior](#5-parity-checklist-opus-current-vs-required-behavior)
6. [Technical Design](#6-technical-design)
7. [Implementation Plan](#7-implementation-plan)
8. [Acceptance Tests & Golden Dataset](#8-acceptance-tests--golden-dataset)
9. [Open Questions for Approval](#9-open-questions-for-approval)
10. [STOP — Approval Required](#10-stop--approval-required)

---

## 1. AUTHORITATIVE INPUTS & CONFLICT RESOLUTION

### 1.1 Input Sources (Precedence Order)

| Priority | Source | Role |
|----------|--------|------|
| **1** | User BUILD PROMPT (this thread) | Authoritative requirements |
| **2** | My previous PRD (`PHASE1_VNEXT_PRD.md`) | Baseline design |
| **3** | `FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md` ("Main.txt") | Report schema + validation checklist |
| **4** | `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md` ("Manual guide") | Methodology + decision trees |
| **5** | `AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md` ("Preflight.txt") | Calibration schema |
| **6** | Codex PRD (`PRD_TECH_SPEC_FBA_PRODUCT_ANALYSIS_AGENT_v1.0.md`) | Feature reference baseline |
| **7** | Sample report (`PHASEA_MANUAL_REPORT_20260104.md`) | Output format target |

### 1.1.1 `/mnt/data/*` Sandbox Paths vs Local Repo Paths (Mapped Equivalents)

Some earlier prompts/PRDs reference specs under `/mnt/data/*`. That path is a **ChatGPT sandbox convention**.
The real implementation uses **local repo paths**; treat the entries below as the authoritative mapped equivalents.

**Repo root (absolute):**
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

| Sandbox reference | Local repo equivalent (authoritative for implementation) |
|---|---|
| `/mnt/data/Main.txt` | `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md` |
| `/mnt/data/Manual analysis guide.md` | `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md` |
| `/mnt/data/Preflight.txt` | `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md` |
| `/mnt/data/PHASEA_MANUAL_REPORT_20260104.md` | `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\codex 1\PHASEA_MANUAL_REPORT_20260104.md` |
| `/mnt/data/PRD_VNEXT_PHASE1_FBA_AGENT_UPGRADE_20260104.md` | `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\PRD_VNEXT_PHASE1_FBA_AGENT_UPGRADE_20260104.md` |
| `/mnt/data/PHASE1_VNEXT_PRD.md` | `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\opus_agent\PHASE1_VNEXT_PRD.md` |

### 1.2 Conflict Resolution Order (From BUILD PROMPT + Main Spec)

> **Main.txt > Manual guide > Preflight.txt**

If conflicts are detected, document them in `docs/spec_conflicts.md`.

### 1.3 Detected Conflicts & Resolutions

| # | Conflict | Resolution |
|---|----------|------------|
| C1 | Main.txt says "FILTERED OUT rows MUST appear in report tables." My baseline PRD mentioned "count-only for UNRELATED." | **Resolved:** FILTERED OUT = printed in tables. UNRELATED = count-only, NOT printed. These are semantically distinct categories. |
| C2 | Codex PRD uses output path `codex sgent\AGENT REPORT\`. BUILD PROMPT says use `AGENT REPORT\` in workspace root. | **Resolved:** Use `{workspace_root}\AGENT REPORT\` per BUILD PROMPT. |
| C3 | Main spec requires `PHASEA_MANUAL_REPORT_YYYYMMDD.md`. Previous PRD proposed `CODEX_MANUAL_REPORT_MMDDHHMM.md`. | **Resolved:** Per conflict order (Main > Manual > Preflight), use **`PHASEA_MANUAL_REPORT_YYYYMMDD.md`** as the canonical filename. Additionally generate `PHASEA_MANUAL_REPORT_YYYYMMDD_HHMM.md` as a timestamped archive copy to avoid overwrites on same-day runs. |

---

## 2. CURRENT STATE AUDIT (OPUS PIPELINE)

### 2.1 Existing Structure

```
opus_agent/
├── src/fba_agent/
│   ├── agent.py              # Main orchestrator
│   ├── cli.py                # CLI interface
│   ├── config.py             # Configuration dataclasses
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   └── tools/
│       ├── categorization.py # Core bucketing logic
│       ├── data_loading.py   # CSV/XLSX loader
│       ├── ean_validation.py # GTIN checksum
│       ├── output.py         # Report generation
│       ├── pack_detection.py # Pack extraction + traps
│       ├── profit_calculation.py
│       ├── scoring.py        # Confidence computation
│       ├── title_parsing.py  # Brand/product extraction
│       └── validation.py     # Coverage + profit gates
├── memory/
│   └── suppliers/            # Empty directory
├── tests/
└── runs/
```

### 2.2 Gap Assessment

| Requirement | Current Status | Gap |
|-------------|----------------|-----|
| **Preflight persistence lifecycle** | ❌ Not implemented. `agent.py:_get_calibration()` returns static defaults. | **MISSING** |
| **Global trap library** | ❌ Not implemented. | **MISSING** |
| **Supplier trap library** | ❌ Not implemented. | **MISSING** |
| **Memory precedence (overrides > supplier > global > defaults)** | ❌ Not implemented. | **MISSING** |
| **Iteration engine (iter_1 → critique → iter_2)** | ❌ Not implemented. One-shot only. | **MISSING** |
| **Regression guard vs previous runs** | ❌ Not implemented. | **MISSING** |
| **Stable key generation** | ❌ Not implemented. Uses RowID only. | **MISSING** |
| **UNRELATED tracking (count-only)** | ⚠️ Partially. Weak rows go to NEEDS_VERIFICATION, not a separate count. | **INCOMPLETE** |
| **Pre-filter support (track excluded separately)** | ❌ Not implemented. | **MISSING** |
| **AI adjudication (row-level, capped)** | ❌ Not implemented. | **MISSING** |
| **AI critique (report-level)** | ❌ Not implemented. | **MISSING** |
| **Multi-provider support (OpenAI/Gemini/Moonshot)** | ⚠️ Moonshot only via env var. | **INCOMPLETE** |
| **Coverage gate** | ✅ Implemented in `validation.py`. | OK |
| **Profit gate** | ✅ Implemented in `validation.py`. | OK |
| **FILTERED OUT in report tables** | ✅ Implemented in `output.py`. | OK |

---

## 3. PROBLEM STATEMENT

### 3.1 Why Current Approach is Inconsistent

1. **No learning persistence:** Supplier patterns (pack keywords, dimension shields) are not remembered across runs.
2. **No regression detection:** Same file can produce different bucket counts across runs without warning.
3. **No iterative refinement:** One-shot analysis without self-critique or correction.
4. **LLM only in preflight:** Core analysis is deterministic (good), but ambiguous rows get no AI help.
5. **No historical comparison:** Cannot detect drift vs previous supplier runs.

### 3.2 What vNext Solves

- **Deterministic spine** for obvious cases (EAN match → VERIFIED).
- **Bounded AI** for ambiguous rows (capped adjudication queue).
- **Iterative refinement** with critique → bounded adjustments → re-run.
- **Regression guard** to ensure output is not worse than prior iteration or historical baseline.
- **Persistent memory** per supplier (calibration, traps, overrides, run history).

---

## 4. REQUIREMENTS SUMMARY (FROM BUILD PROMPT)

### 4.1 Core Capabilities (Must Implement)

| # | Requirement | Source |
|---|-------------|--------|
| R1 | Preflight persistence lifecycle (load → run → merge → write) | BUILD PROMPT §1.1 |
| R2 | Global trap library (`memory/global/trap_library.jsonl`) | BUILD PROMPT §8 |
| R3 | Supplier trap library + overrides with precedence | BUILD PROMPT §8 |
| R4 | Iteration engine: iter_1 (baseline) → critique → iter_2 (refined) | BUILD PROMPT §3 |
| R5 | Regression guard vs previous iteration AND last K historical runs | BUILD PROMPT §6 |
| R6 | UNRELATED tracking (count-only, NOT in tables) | BUILD PROMPT §1.2, Main.txt |
| R7 | Optional internal pre-filtering with tracking | BUILD PROMPT §1.2 |
| R8 | AI Row Adjudication (capped: min(200, 5% of rows)) | BUILD PROMPT §5.1 |
| R9 | AI Report Critique with structured JSON output | BUILD PROMPT §5.2 |
| R10 | Stable key for cross-run comparison | BUILD PROMPT §6.2 |
| R11 | Multi-provider support (OpenAI, Gemini, Moonshot) | BUILD PROMPT §9 |
| R12 | Model escalation (small → large on failure) | BUILD PROMPT §9.5 |

### 4.2 Semantic Requirements (From Main.txt)

| # | Requirement | Type |
|---|-------------|------|
| S1 | FILTERED OUT rows MUST appear in report tables | HARD GATE |
| S2 | UNRELATED rows tracked count-only, NOT printed | HARD GATE |
| S3 | VERIFIED/HIGHLY_LIKELY require Sales > 0, NetProfit > 0, AdjustedProfit > 0 | HARD GATE |
| S4 | If AdjustedProfit ≤ 0 after pack sanity → **route to FILTERED OUT** (NOT a stop condition) | ROUTING RULE |
| S5 | Coverage: every RowID in exactly one bucket, no duplicates, no missing | HARD GATE |
| S6 | Report uses exact TABLE_SCHEMA from Main.txt | HARD GATE |

### 4.3 Clarification: Hard Gates vs Routing Rules

**Hard fail / block finalization (do NOT promote `final/`):**
- Coverage/reconciliation failure: missing or duplicate `RowID` and/or `stable_key`
- `stable_key` collision (no silent disambiguation): emit a collision report and block finalization
- Report schema/table-format violations that prevent valid output (missing required columns, invalid fixed-width tables)

**NOT a hard fail by itself:**
- `AdjustedProfit ≤ 0` is a **routing rule**: any such rows must be moved to **FILTERED OUT** (and FILTERED OUT rows are printed).

**Bug definition / iteration trigger:**
- If any row remains in VERIFIED/HIGHLY_LIKELY/NEEDS_VERIFICATION with `AdjustedProfit ≤ 0` after pack sanity, that is a
  correctness bug → triggers automatic re-bucketing and/or an iteration and blocks finalization until corrected.

| Type | Behavior | Examples |
|------|----------|----------|
| **HARD GATE** | Failure blocks finalization; triggers iter_2 if correctable | Coverage missing rows, stable_key collisions |
| **ROUTING RULE** | Does NOT stop pipeline; routes row to correct bucket | AdjustedProfit ≤ 0 → FILTERED OUT |

**Critical:** `AdjustedProfit ≤ 0` is a ROUTING RULE, not a stop condition. The pipeline continues; the row moves to FILTERED OUT (which is printed in tables per Main.txt).

### 4.4 Iteration Rules (From BUILD PROMPT §3)

- **Max iterations:** 2 (default), configurable via `--max-iterations {1..3}`
- **Trigger for iter_2:** Any correctable hard gate failure, large anomaly signals, regression guard issue, or critique-identified safe rule additions
- **Stop condition:** All hard gates pass AND regression guard says "not worse" AND no high-severity unresolved issues
- **On failure (max iterations reached or blocked):** Produce `DRAFT_NOT_PASSED/` with explicit gate failures + "What to verify manually" section; do not promote `final/`.

### 4.5 Regression Guard Rules (From BUILD PROMPT §6.3)

- Missing stable keys vs history: **HARD BLOCK**
- Good-to-bad transitions (VERIFIED/HIGHLY_LIKELY → NEEDS_VERIFICATION/FILTERED_OUT/UNRELATED): Block if > 10% of previously-good OR > 30 rows
- Justifications required in `regression_justifications.jsonl`

---

## 5. PARITY CHECKLIST: OPUS CURRENT vs REQUIRED BEHAVIOR

This section compares what Opus currently implements vs what is required by the specs (Main.txt, Manual guide, Codex PRD, BUILD PROMPT).

| Feature | Required Behavior | Opus Current | Gap |
|---------|-------------------|--------------|-----|
| **Preflight persistence** | Load existing calibration → run preflight → merge → persist | ❌ Returns static defaults | **MISSING** |
| **Global trap library** | `memory/global/trap_library.jsonl` with universal shields | ❌ Not implemented | **MISSING** |
| **Supplier trap library** | `memory/suppliers/{id}/trap_library.jsonl` with supplier-specific traps | ❌ Not implemented | **MISSING** |
| **Supplier calibration** | Persisted merged preflight output per supplier (not global) | ❌ Not implemented | **MISSING** |
| **Merge precedence** | overrides > supplier traps > supplier calibration > global traps > defaults | ❌ Not implemented | **MISSING** |
| **Iteration engine** | iter_1 → validate/critique → bounded adjustments → iter_2 | ❌ One-shot only | **MISSING** |
| **AI Critique** | LLM reviews bucket counts, anomalies, samples; proposes safe changes | ❌ Not implemented | **MISSING** |
| **AI Adjudication** | LLM reviews capped ambiguous rows; outputs structured signals | ❌ Not implemented | **MISSING** |
| **Regression guard** | Compare current vs previous iteration AND last K historical runs | ❌ Not implemented | **MISSING** |
| **Stable key** | Hash-based key for cross-run comparison; collision = HARD FAIL | ❌ Uses RowID only | **MISSING** |
| **UNRELATED tracking** | Count-only, NOT in tables; distinct from FILTERED OUT | ⚠️ Routes weak rows to NEEDS_VERIFICATION | **INCOMPLETE** |
| **Pre-filter support** | Track `prefilter_excluded_count` separately | ❌ Not implemented | **MISSING** |
| **Coverage gate** | Every RowID in exactly one bucket | ✅ Implemented | OK |
| **Profit gate** | No positive bucket with AdjustedProfit ≤ 0 | ✅ Implemented | OK |
| **FILTERED OUT in tables** | Print FILTERED OUT rows (confirmed matches, excluded for reason) | ✅ Implemented | OK |
| **Report filename** | `PHASEA_MANUAL_REPORT_YYYYMMDD.md` (per Main.txt) | ⚠️ Uses different format | **INCORRECT** |
| **Multi-provider** | Support OpenAI, Gemini, Moonshot | ⚠️ Moonshot only | **INCOMPLETE** |
| **Model escalation** | small → large on parse failure | ❌ Not implemented | **MISSING** |

---

## 6. TECHNICAL DESIGN

### 6.1 Memory Layout

```
memory/
├── global/
│   ├── trap_library.jsonl        # Universal traps (dimension shields, spec-x)
│   │                              # Applied BEFORE supplier-specific layers
│   └── brand_corrections.json    # Known brand typos/aliases
└── suppliers/
    └── {supplier_id}/
        ├── calibration.json      # Persisted MERGED preflight output per supplier
        │                          # (NOT global; specific to this supplier's patterns)
        ├── trap_library.jsonl    # Supplier-specific traps (overrides global)
        ├── overrides.jsonl       # User-approved row/rule overrides (highest precedence)
        ├── brand_aliases.json    # Supplier-specific brand mappings
        └── run_history.json      # Last K run pointers
```

### 6.2 Merge Precedence (Deterministic)

```python
def merge_config(supplier_id: str) -> Dict:
    """
    Merge calibration with explicit precedence.
    
    Precedence (highest to lowest):
    1. User overrides (row-specific or rule-specific)
    2. Supplier traps (supplier-specific trap patterns)
    3. Supplier calibration (persisted merged preflight for THIS supplier)
    4. Global trap library (universal dimension/spec shields)
    5. Defaults (hardcoded fallbacks)
    """
    result = load_defaults()                                    # 5. Defaults
    result = deep_merge(result, load_global_traps())            # 4. Global traps
    result = deep_merge(result, load_supplier_calibration(supplier_id))  # 3. Supplier calibration
    result = deep_merge(result, load_supplier_traps(supplier_id))        # 2. Supplier traps
    result = deep_merge(result, load_supplier_overrides(supplier_id))    # 1. User overrides
    return result
```

**Explicit clarifications:**
- **Supplier calibration** = the persisted merged preflight output for THIS supplier, NOT a copy of global config.
- **Global trap library** = universal traps (e.g., dimension shields like "cm", "inch", "ml") applied before supplier overrides.
- **Supplier traps** = supplier-specific trap patterns discovered from this supplier's data.

### 6.3 Stable Key Strategy

**Primary strategy (if `SupplierURL` exists):**
```python
stable_key = sha256(f"{SupplierURL}|{ASIN}").hexdigest()[:16]
```

**Fallback strategy (if SupplierURL missing):**
```python
stable_key = sha256(f"{normalize(EAN)}|{ASIN}|{normalize(SupplierTitle)[:50]}|{normalize(AmazonTitle)[:50]}").hexdigest()[:16]
```

**Collision handling: HARD FAIL**
- If any two rows produce the same stable_key, this is a **HARD FAILURE**.
- Emit `stable_key_collisions.json` listing the colliding rows.
- Block finalization until collisions are resolved (either via data fix or override).
- Do NOT use RowID as disambiguation (breaks cross-run comparability).

### 6.4 Complete Pipeline Flow with Iteration Engine

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FBA ANALYSIS PIPELINE vNext                                       │
│                              (with Iteration Loop + Memory System)                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: LOAD & NORMALIZE                                                                           │
│ ┌─────────────┐    ┌─────────────────┐    ┌─────────────────────────────────────────────────────┐  │
│ │ load_report │───►│normalize_columns│───►│ DataFrame with RowID, stable_key, clean EANs        │  │
│ │ (CSV/XLSX)  │    │ + stable_key    │    │ Optional: prefilter_excluded rows tracked separately│  │
│ └─────────────┘    └─────────────────┘    └─────────────────────────────────────────────────────┘  │
│                                                                                                     │
│ STABLE KEY COLLISION CHECK: If any collision detected → HARD FAIL + emit stable_key_collisions.json│
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: MEMORY & PREFLIGHT CALIBRATION                                                             │
│                                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              MEMORY SYSTEM                                                   │   │
│  │  ┌─────────────────────┐    ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │  memory/global/     │    │  memory/suppliers/{supplier_id}/                         │   │   │
│  │  │  ├─trap_library.jsonl│    │  ├─ calibration.json      (persisted merged preflight)  │   │   │
│  │  │  │ (universal traps) │    │  ├─ trap_library.jsonl    (supplier-specific traps)     │   │   │
│  │  │  └─brand_corrections │    │  ├─ overrides.jsonl       (user-approved overrides)     │   │   │
│  │  │       .json          │    │  ├─ brand_aliases.json    (supplier brand mappings)     │   │   │
│  │  │                     │    │  └─ run_history.json      (last K run pointers)         │   │   │
│  │  └─────────────────────┘    └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                │                                                    │
│  ┌─────────────┐    ┌──────────────┐    ┌─────▼────────┐    ┌────────────────────────────────────┐ │
│  │ sample_rows │───►│ run_preflight│───►│load_supplier_│───►│ merge_calibration                  │ │
│  │ (n=50)      │    │ (LLM-assist) │    │   memory     │    │ Precedence: overrides > supplier   │ │
│  └─────────────┘    └──────────────┘    └──────────────┘    │ traps > supplier calib > global    │ │
│                                                              │ traps > defaults                   │ │
│                                                              └────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                ┌───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                           │
│   ╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗   │
│   ║                              🔄 ITERATION LOOP (max_iterations=2)                                 ║   │
│   ╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝   │
│                                                                                                           │
│      ┌──────────────────────────────────────────────────────────────────────────────────────────────┐     │
│      │                                                                                              │     │
│      │   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐     ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐                │     │
│      │          ITERATION 1                            ITERATION 2                                  │     │
│      │   │      (Baseline)               │     │  (Refined, if triggered)        │                │     │
│      │   │                               │     │                                 │                │     │
│      │   │ ┌───────────────────────────┐ │     │ ┌───────────────────────────┐  │                │     │
│      │   │ │ STAGE 3: ROW ANALYSIS     │ │     │ │ STAGE 3: ROW ANALYSIS     │  │                │     │
│      │   │ │ FOR EACH ROW:             │ │     │ │ + adjudication results    │  │                │     │
│      │   │ │  ├─EAN validation         │ │     │ │ + applied safe changes    │  │                │     │
│      │   │ │  ├─Title parsing          │ │     │ └───────────────────────────┘  │                │     │
│      │   │ │  ├─Pack detection + traps │ │     │              │                 │                │     │
│      │   │ │  ├─RSU + adjusted profit  │ │     │              ▼                 │                │     │
│      │   │ │  ├─Bucket assignment      │ │     │ ┌───────────────────────────┐  │                │     │
│      │   │ │  │  (ROUTING RULE:        │ │     │ │ STAGE 4: VALIDATION       │  │                │     │
│      │   │ │  │   AdjProfit≤0 →        │ │     │ │ ├─Coverage gate (HARD)    │  │                │     │
│      │   │ │  │   FILTERED_OUT)        │ │     │ │ ├─Profit gate (HARD)      │  │                │     │
│      │   │ │  └─Confidence score       │ │     │ │ ├─Trap gates              │  │                │     │
│      │   │ └───────────────────────────┘ │     │ │ └─Distribution sanity     │  │                │     │
│      │   │              │                │     │ └───────────────────────────┘  │                │     │
│      │   │              ▼                │     │              │                 │                │     │
│      │   │ ┌───────────────────────────┐ │     │              ▼                 │                │     │
│      │   │ │ STAGE 4: VALIDATION       │ │     │ ┌───────────────────────────┐  │                │     │
│      │   │ │ ├─Coverage gate (HARD)    │ │     │ │ VALIDATE + COMPARE        │  │                │     │
│      │   │ │ ├─Profit gate (HARD)      │ │     │ │ vs iter_1 + history       │  │                │     │
│      │   │ │ ├─Trap gates              │ │     │ └───────────────────────────┘  │                │     │
│      │   │ │ └─Distribution sanity     │ │     │                                 │                │     │
│      │   │ └───────────────────────────┘ │     └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘                │     │
│      │   │              │                │                    ▲                                   │     │
│      │   │              ▼                │                    │                                   │     │
│      │   │ ┌───────────────────────────┐ │                    │ YES (trigger)                     │     │
│      │   │ │ AI CRITIQUE               │ │                    │                                   │     │
│      │   │ │ ├─Review bucket counts    │ │     ┌──────────────┴───────────────────┐               │     │
│      │   │ │ ├─Identify anomalies      │ │     │     SHOULD RUN ITERATION 2?      │               │     │
│      │   │ │ ├─Sample row analysis     │ │     │ ├─ Hard gate failure correctable? │               │     │
│      │   │ │ └─Propose safe changes    │ │     │ ├─ Critique found safe changes?  │               │     │
│      │   │ └───────────────────────────┘ │     │ ├─ Large anomaly signals?        │               │     │
│      │   │              │                │     │ └─ Regression guard triggered?  │               │     │
│      │   │              ▼                │     └──────────────┬───────────────────┘               │     │
│      │   │ ┌───────────────────────────┐ │                    │                                   │     │
│      │   │ │ AI ADJUDICATION (capped)  │ │                    │ NO                                │     │
│      │   │ │ ├─Pack ambiguity rows     │ │                    │                                   │     │
│      │   │ │ ├─Variant ambiguity rows  │ │                    ▼                                   │     │
│      │   │ │ ├─High profit outliers    │ │     ┌──────────────────────────────────┐               │     │
│      │   │ │ └─Max: min(200, 5% rows)  │ │     │       SKIP TO FINALIZE           │               │     │
│      │   │ └───────────────────────────┘ │     └──────────────────────────────────┘               │     │
│      │   │              │                │                                                        │     │
│      │   │              └────────────────┼───────────────────────────────────────────────────────►│     │
│      │   │                               │                                                        │     │
│      │   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘                                                        │     │
│      │                                                                                              │     │
│      └──────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: REGRESSION GUARD                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ compare_iterations(iter_1, iter_2) + compare_vs_history(last_k_runs)                            │ │
│ │   ├── Missing stable keys vs history → HARD BLOCK                                              │ │
│ │   ├── Good-to-bad transitions > threshold → BLOCK (unless justified)                           │ │
│ │   │   └── Threshold: >10% of previously-good OR >30 absolute rows                              │ │
│ │   ├── Generate regression_justifications.jsonl for allowed transitions                         │ │
│ │   └── SELECT BEST ITERATION (iter_1 or iter_2)                                                 │ │
│ └─────────────────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 6: OUTPUT GENERATION & MEMORY PERSISTENCE                                                     │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ render_phasea_report(coverage_ledger, metadata) → PHASEA_MANUAL_REPORT_YYYYMMDD.md              │ │
│ │   ├── VERIFIED — RECOMMENDED (in table)                                                        │ │
│ │   ├── VERIFIED — FILTERED OUT / EXCLUDED (in table)                                            │ │
│ │   ├── HIGHLY LIKELY — RECOMMENDED (in table)                                                   │ │
│ │   ├── HIGHLY LIKELY — FILTERED OUT / EXCLUDED (in table)                                       │ │
│ │   ├── NEEDS VERIFICATION (in table)                                                            │ │
│ │   └── UNRELATED / NOT INCLUDED (count-only, NOT in tables)                                     │ │
│ │                                                                                                 │ │
│ │ Also generate: PHASEA_MANUAL_REPORT_YYYYMMDD_HHMM.md (timestamped archive copy)                 │ │
│ │                                                                                                 │ │
│ │ write_run_artifacts(run_id, outputs) → {run_id}/final/                                         │ │
│ │   ├── coverage_ledger.csv (with stable_key column)                                             │ │
│ │   ├── evidence.jsonl                                                                           │ │
│ │   ├── run_summary.json                                                                         │ │
│ │   ├── FINAL_SUMMARY.md (iteration comparison, gates passed, warnings)                          │ │
│ │   └── REGRESSION_JUSTIFICATIONS.jsonl                                                          │ │
│ │                                                                                                 │ │
│ │ persist_supplier_memory(supplier_id, merged_config, new_traps, overrides)                      │ │
│ │   └── Updates memory/suppliers/{supplier_id}/ for next run                                     │ │
│ └─────────────────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Iteration Trigger Rules:**
- Iteration 2 runs if Iteration 1 has:
  - Any hard gate failure that is correctable
  - Large anomaly signals (>10 outliers, >5% bucket flip)
  - Regression guard detects >10% "good-to-bad" transitions vs history
  - Critique identifies safe rule additions

**Stop Conditions:**
- All hard gates pass
- Regression guard says "not worse"
- Critique has no high-severity unresolved issues
- Max iterations (default 2) reached

**NOT a stop condition:**
- `AdjustedProfit ≤ 0` — This is a ROUTING RULE (row → FILTERED OUT), not a stop.

### 6.5 AI Adjudication Schema

**Selector (who gets AI review):**
- Pack verdict contains "uncertain"
- Variant match is "ambiguous"
- EAN missing but confidence > 60
- High profit outlier (> £20) with weak match (confidence < 70)
- Row flipped bucket vs iter_1 or historical baseline

**Cap:** `min(200, 5% of total_rows)`

**Input to LLM:**
```json
{
  "row_id": 123,
  "supplier_title": "AMTECH TROWEL 150MM",
  "amazon_title": "Amtech 150mm Pointing Trowel",
  "supplier_ean": "5032759027644",
  "amazon_ean": "-",
  "current_bucket": "NEEDS_VERIFICATION",
  "current_confidence": 65,
  "pack_verdict": "1:1 Match",
  "adjusted_profit": 0.63,
  "traps_detected": []
}
```

**Output schema (strict JSON):**
```json
{
  "row_id": 123,
  "extracted_signals": {
    "supplier_brand": "AMTECH",
    "amazon_brand": "Amtech",
    "brand_match": true,
    "supplier_product_type": "trowel",
    "amazon_product_type": "trowel",
    "product_match": true,
    "supplier_pack": 1,
    "amazon_pack": 1,
    "pack_match": true
  },
  "trap_detections": [],
  "recommended_bucket": "HIGHLY_LIKELY",
  "confidence_suggestion": 80,
  "reasoning": "Brand match (case-insensitive), product type match, no pack contradiction."
}
```

**Constraint:** AI confidence is a SUGGESTION. Deterministic scoring formula remains authoritative.

### 6.6 AI Critique Schema

**Input to critique:**
- Bucket counts (VERIFIED, HIGHLY_LIKELY, NEEDS_VERIFICATION, FILTERED_OUT, UNRELATED)
- Validation results (which gates passed/failed)
- Top 20 profit outliers
- Top 20 title-mismatch anomalies
- Regression diff summary (if iter_2 or historical comparison)
- Sample rows: 10 per bucket (random) + 10 highest confidence + 10 lowest confidence

**Output schema (strict JSON):**
```json
{
  "high_severity_issues": [
    {
      "issue_id": "HSI_001",
      "description": "3 rows with RSU>10 have no dimension trap despite patterns like '9x9 inch'",
      "affected_rows": [456, 789, 1012],
      "suggested_resolution": "Add 'inch' to dimension_shield_keywords"
    }
  ],
  "proposed_changes": [
    {
      "change_type": "add_shield_token",
      "target": "dimension_shield_keywords",
      "value": "inch",
      "safe_to_apply": true
    }
  ],
  "overall_assessment": "Minor issues. Safe to finalize after applying 1 shield token.",
  "recommended_action": "apply_and_rerun"
}
```

**Safe change types:**
- `add_shield_token` (dimension or spec_x)
- `add_pack_keyword`
- `add_brand_alias`
- `add_override` (row-specific, requires explicit approval unless marked safe)
- `adjust_threshold` (within ±5 points of default; NOT safe by default)

### 6.7 Provider Configuration

**Environment variables:**
```bash
# OpenAI (default)
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1  # optional

# Gemini (via OpenAI-compatible endpoint)
GEMINI_API_KEY=...
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# Moonshot/Kimi
MOONSHOT_API_KEY=...
MOONSHOT_BASE_URL=https://api.moonshot.ai/v1
```

**CLI flags:**
```bash
--provider {openai|gemini|moonshot}  # Default: openai
--model-small <name>                  # Default: gpt-4o-mini
--model-large <name>                  # Default: gpt-4o
--max-escalations <n>                 # Default: 2
```

**Escalation logic:**
1. Try with small model
2. If JSON parse fails twice, escalate to large model
3. If still fails, log error and use deterministic fallback

### 6.8 Output Artifact Structure

```
AGENT REPORT/
└── {run_id}/
    ├── iter_1/
    │   ├── coverage_ledger.csv       # Includes stable_key column
    │   ├── evidence.jsonl
    │   ├── run_summary.json
    │   ├── config_applied.json
    │   ├── adjudication_results.jsonl
    │   └── critique.json
    ├── iter_2/                       # Only if iter_2 ran
    │   ├── coverage_ledger.csv
    │   ├── evidence.jsonl
    │   ├── run_summary.json
    │   ├── config_applied.json
    │   ├── adjudication_results.jsonl
    │   ├── critique.json
    │   └── regression_diff.json
    ├── DRAFT_NOT_PASSED/             # Only if run cannot be promoted to final
    │   ├── PHASEA_MANUAL_REPORT_YYYYMMDD.md      # Draft, clearly marked NOT PASSED
    │   ├── coverage_ledger.csv
    │   ├── evidence.jsonl
    │   ├── run_summary.json
    │   ├── FINAL_SUMMARY.md                    # Includes explicit gate failures
    │   └── REGRESSION_JUSTIFICATIONS.jsonl
    └── final/                        # Created/promoted ONLY if gates + critique + regression guard pass
        ├── PHASEA_MANUAL_REPORT_YYYYMMDD.md      # Canonical (per Main.txt)
        ├── PHASEA_MANUAL_REPORT_YYYYMMDD_HHMM.md # Timestamped archive
        ├── coverage_ledger.csv
        ├── evidence.jsonl
        ├── run_summary.json
        ├── FINAL_SUMMARY.md
        └── REGRESSION_JUSTIFICATIONS.jsonl
```

---

## 7. IMPLEMENTATION PLAN

### 7.1 Phase 2a — Memory & Preflight (Foundation)

| # | File | Action | Description |
|---|------|--------|-------------|
| 1 | `core/memory.py` | **NEW** | Memory manager: load/save calibration, traps, overrides, run_history |
| 2 | `core/preflight.py` | **NEW** | LLM-assisted preflight with persistence |
| 3 | `tools/stable_key.py` | **NEW** | Stable key generation; collision detection (HARD FAIL) |
| 4 | `tools/data_loading.py` | **MODIFY** | Add stable_key column; collision check; optional pre-filter |
| 5 | `models/schemas.py` | **MODIFY** | Add `stable_key`, `prefilter_excluded` fields |
| 6 | `agent.py` | **MODIFY** | Integrate memory + preflight lifecycle |
| 7 | `memory/global/trap_library.jsonl` | **NEW** | Seed with default dimension/spec shields |

### 7.2 Phase 2b — Iteration Engine

| # | File | Action | Description |
|---|------|--------|-------------|
| 8 | `core/iteration.py` | **NEW** | Iteration loop controller (iter_1 → critique → iter_2 → finalize) |
| 9 | `core/regression.py` | **NEW** | Regression guard: compare iterations + historical runs |
| 10 | `tools/validation.py` | **MODIFY** | Return soft vs hard gate results for iteration logic |
| 11 | `agent.py` | **MODIFY** | Integrate iteration engine |

### 7.3 Phase 2c — AI Logic

| # | File | Action | Description |
|---|------|--------|-------------|
| 12 | `core/provider.py` | **NEW** | Multi-provider support (OpenAI, Gemini, Moonshot) |
| 13 | `core/escalation.py` | **NEW** | Model escalation logic (small → large on failure) |
| 14 | `tools/adjudication.py` | **NEW** | Row adjudication selector + LLM call + result merger |
| 15 | `tools/critique.py` | **NEW** | Report critique step + safe change application |

### 7.4 Phase 2d — Output & CLI

| # | File | Action | Description |
|---|------|--------|-------------|
| 16 | `tools/output.py` | **MODIFY** | Iteration-based folder structure; dual filename output |
| 17 | `cli.py` | **MODIFY** | Add flags: `--max-iterations`, `--history-k`, `--provider`, etc. |
| 18 | `config.py` | **MODIFY** | Add new config fields for all new features |

### 7.5 Phase 2e — Testing & Validation

| # | File | Action | Description |
|---|------|--------|-------------|
| 19 | `tests/test_stable_key.py` | **NEW** | Stable key generation + collision detection tests |
| 20 | `tests/test_memory.py` | **NEW** | Memory load/save/merge tests |
| 21 | `tests/test_regression.py` | **NEW** | Regression guard tests |
| 22 | `tests/test_iteration.py` | **NEW** | Iteration selection logic tests |
| 23 | `tests/fixtures/golden_dataset.csv` | **NEW** | 100-row curated test set with expected outcomes |
| 24 | `tests/fixtures/golden_expected.json` | **NEW** | Expected bucket assignments + confidence ranges |

---

## 8. ACCEPTANCE TESTS & GOLDEN DATASET

### 8.1 Gate Tests (Automated)

| Test ID | Gate | Pass Condition |
|---------|------|----------------|
| G1 | Coverage | `len(ledger) == len(input_df)` AND no duplicate RowIDs |
| G2 | Profit routing | No row in VERIFIED/HIGHLY_LIKELY has AdjustedProfit ≤ 0 (must be in FILTERED_OUT) |
| G3 | FILTERED_OUT in tables | FILTERED_OUT section exists in report AND count > 0 implies rows are printed |
| G4 | UNRELATED count-only | UNRELATED count appears in Summary AND no UNRELATED section in tables |
| G10 | UNRELATED != NEEDS_VERIFICATION | A known-unrelated fixture row must land in UNRELATED and must not appear in NEEDS_VERIFICATION tables or samples |
| G5 | Stable keys unique | All rows have non-empty stable_key; **zero collisions** (else HARD FAIL) |
| G6 | Iteration selection | Final iteration is not worse than iter_1 by regression metrics |
| G7 | Report schema | All columns from TABLE_SCHEMA present in correct order |
| G8 | Report filename | `PHASEA_MANUAL_REPORT_YYYYMMDD.md` exists (per Main.txt) |
| G9 | Fixed-width | All `|` characters in table rows align within ±1 character |

### 8.2 Golden Dataset Plan

**Dataset:** 100 curated rows from `part 4 jan.xlsx` covering:
- 20 exact EAN matches (VERIFIED candidates)
- 20 brand+product matches (HIGHLY_LIKELY candidates)
- 20 weak matches (NEEDS_VERIFICATION candidates)
- 20 pack mismatch cases (FILTERED_OUT candidates)
- 20 clearly unrelated (UNRELATED candidates)

**Expected outcomes file:**
```json
{
  "stable_key_abc123": {
    "expected_bucket": "VERIFIED",
    "confidence_min": 90,
    "confidence_max": 100,
    "expected_adjusted_profit_sign": "positive"
  },
  ...
}
```

**Regression test:**
Run agent on golden dataset → compare outcomes → fail if >5% mismatch from expected.

---

## 9. OPEN QUESTIONS FOR APPROVAL

### Q1: Default `--max-iterations`
**Proposed:** 2  
**Rationale:** One baseline + one refinement is sufficient for most cases. 3 risks over-correction.  
**Approve?** [ ]

### Q2: Default `--history-k`
**Proposed:** 2 (compare against last 2 historical runs for the same supplier)  
**Rationale:** More than 2 adds complexity without much benefit; less than 2 misses drift detection.  
**Approve?** [ ]

### Q3: Pre-filter rules (if `--prefilter` enabled)
**Proposed:**
- Exclude rows where `NetProfit <= 0` (before pack adjustment)
- Exclude rows where `Sales == 0` (if sales column exists)
- Track as `prefilter_excluded_count` in summary  
**Approve?** [ ]

### Q4: Stable key collision reporting format
**Locked requirement:** Collision = **HARD FAIL** + collision report (no disambiguation).  
**Question:** Preferred collision report format?  
- [ ] JSON only (`stable_key_collisions.json`)  
- [ ] JSON + CSV (`stable_key_collisions.json` + `stable_key_collisions.csv`)

### Q5: Adjudication cap
**Proposed:** `min(200, 5% of total_rows)`  
**Rationale:** Balances AI cost with coverage. 5000-row file = 250 rows max adjudicated.  
**Approve?** [ ]

### Q6: Regression block threshold (good-to-bad transitions)
**Proposed:** Block if > 10% of previously-good rows OR > 30 absolute rows transition good-to-bad without justification.  
**Approve?** [ ]

### Q7: Report filename format
**Proposed:** `PHASEA_MANUAL_REPORT_YYYYMMDD.md` (per Main.txt conflict order).  
**Also generate:** `PHASEA_MANUAL_REPORT_YYYYMMDD_HHMM.md` as timestamped archive.  
**Approve?** [ ]

---

## 10. STOP — APPROVAL REQUIRED

**Phase 1 is complete.**

I have:
1. ✅ Fixed the parity checklist to focus on Opus gaps vs required behavior
2. ✅ Changed stable key collision handling to HARD FAIL (no RowID disambiguation)
3. ✅ Updated report filename to `PHASEA_MANUAL_REPORT_YYYYMMDD.md` per Main.txt
4. ✅ Clarified that AdjustedProfit ≤ 0 is a ROUTING RULE (→ FILTERED OUT), not a stop condition
5. ✅ Explicitly documented memory layer precedence and supplier calibration definition
6. ✅ Updated Open Questions with approval checkboxes

---

**⏹️ STOPPED. NO CODE CHANGES MADE.**

**Awaiting explicit approval to proceed to Phase 2 (Implementation).**

**To proceed, please:**
1. Review this PRD
2. Answer the Open Questions (Q1–Q7) by marking [X]
3. Reply with "APPROVED" to begin implementation

If you want changes, specify them and I will update the PRD before proceeding.
