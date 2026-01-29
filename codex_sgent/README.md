# FBA Agent System - README

**Version:** v4.3.0 (Current Implementation)  
**Last Updated:** 2026-01-08 20:25 UTC+4

---

## Overview

The FBA Agent System is an AI-enhanced product analysis tool that identifies profitable Amazon FBA opportunities from supplier financial reports. It uses a combination of **deterministic analysis** and **AI-powered adjudication** to categorize products into confidence buckets.

---

## Current Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        FBA AGENT WORKFLOW v4.2.0 (CURRENT)                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════════════
                         PHASE 1: SETUP & CALIBRATION
════════════════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────┐
    │ 1. CLI + Data Loading       │
    │    Load Excel/CSV           │
    │    Normalize columns        │
    │    Generate stable keys     │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ 2. Preflight Calibration    │ ← AI (pattern detection)
    │    Detect pack keywords     │
    │    Detect brand position    │
    │    Detect capacity patterns │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ 3. Brand Detection (NEW)    │ ← AI (brand validation)
    │                             │
    │ PURPOSE: Extract brand      │
    │ candidates from titles,     │
    │ validate with AI, store     │
    │ in known_brands.json        │
    │                             │
    │ OUTPUT FILES:               │
    │ • memory/global/            │
    │   known_brands.json         │
    │ • memory/global/            │
    │   brand_candidates_checked  │
    │   .json                     │
    │                             │
    │ AFFECTS:                    │
    │ • brand_aliases (merged)    │
    │ • analysis.py brand logic   │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ 4. Load Memory + Merge      │ ← Deterministic
    │    Config precedence:       │
    │    1. User overrides        │
    │    2. Supplier traps        │
    │    3. Global traps          │
    │    4. Preflight calibration │
    │    5. Base/default          │
    └─────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════════════
                         PHASE 2: DETERMINISTIC ANALYSIS
════════════════════════════════════════════════════════════════════════════════════════

                │
                ▼
    ┌─────────────────────────────┐
    │ 5. Row-by-Row Analysis      │ ← Deterministic (analysis.py)
    │                             │
    │ PURPOSE: Categorize each    │
    │ row into buckets based on   │
    │ EAN matching, brand logic,  │
    │ pack detection, similarity  │
    │                             │
    │ OUTPUT FILES:               │
    │ • coverage_ledger.csv       │
    │ • evidence.jsonl            │
    │                             │
    │ BUCKET CATEGORIES:          │
    │ • VERIFIED (high confidence)│
    │ • HIGHLY_LIKELY (good match)│
    │ • NEEDS_VERIFICATION        │
    │ • FILTERED_OUT              │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ Generate MD Report          │
    │ (iteration_N_report.md)     │
    └─────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════════════
                         PHASE 3: AI LOGIC STEPS (5, 6, 7)
════════════════════════════════════════════════════════════════════════════════════════

                │
                ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│   AI STEP 1: Per-Row Adjudication FROM MD REPORT                                 │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │ PURPOSE: Review ALL rows from MD report for bucket corrections             │   │
│   │                                                                             │   │
│   │ INPUT (NEW - v4.3.0):                                                       │   │
│   │ • ALL rows from generated MD report (~367 rows, NOT 2789 Excel rows)        │   │
│   │ • Batched in groups of 70 rows with category headers                        │   │
│   │ • ~6 API calls total                                                        │   │
│   │ • NOTE: Profit-based selection REMOVED (only ambiguity signals matter)      │   │
│   │                                                                             │   │
│   │ OUTPUT:                                                                     │   │
│   │ • Bucket recommendations per row                                            │   │
│   │ • Reasoning for each recommendation                                         │   │
│   │ • Stored in: iteration_details.json → "adjudication_results"                │   │
│   │                                                                             │   │
│   │ AFFECTS:                                                                    │   │
│   │ • coverage_ledger.csv (bucket reassignments)                                │   │
│   │ • Can upgrade NEEDS_VERIFICATION → HIGHLY_LIKELY                            │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │ APPLY to LEDGER                                                             │   │
│   │ (upgrade NEEDS_VER → HIGHLY_LIKELY based on AI recommendations)             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                                          ▼                                          │
│   AI STEP 2: Comprehensive Adjudication                                             │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │ PURPOSE: Review the FULL Markdown report for patterns, errors, and         │   │
│   │ systemic issues across all products                                         │   │
│   │                                                                             │   │
│   │ INPUT:                                                                      │   │
│   │ • Full Markdown report (iteration_N_report.md)                              │   │
│   │ • coverage_ledger.csv (current state)                                       │   │
│   │ • Source Excel path (for reference)                                         │   │
│   │                                                                             │   │
│   │ OUTPUT:                                                                     │   │
│   │ • errors: List of identified errors                                         │   │
│   │ • recategorizations: Products to move between buckets                       │   │
│   │ • root_causes: Underlying issues identified                                 │   │
│   │ • config_recommendations: Suggested config changes                          │   │
│   │ • Stored in: comprehensive_adjudication.json                                │   │
│   │                                                                             │   │
│   │ AFFECTS:                                                                    │   │
│   │ • coverage_ledger.csv (fix false positives/negatives)                       │   │
│   │ • PASSES FINDINGS to AI Critique (Step 3)                                   │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │ APPLY to LEDGER                                                             │   │
│   │ (apply recategorizations from comprehensive adjudication)                   │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                     PASS FINDINGS ───────┼────────────────────────────────────────┐ │
│                                          │                                        │ │
│                                          ▼                                        ▼ │
│   AI STEP 3: Critique (Decision Maker)                    ┌───────────────────────┐ │
│   ┌────────────────────────────────────────────────────┐  │ Critique receives:    │ │
│   │ PURPOSE: Make final decision on report quality     │  │ • N errors found      │ │
│   │ and whether to finalize, iterate, or block         │  │ • N recategorizations │ │
│   │                                                    │  │ • Root causes         │ │
│   │ INPUT:                                             │  │ • Config recs         │ │
│   │ • Bucket counts and anomalies                      │  └───────────────────────┘ │
│   │ • Comprehensive adjudication findings              │                            │
│   │ • Past ledger (from memory) for comparison         │                            │
│   │ • EAN statistics                                   │                            │
│   │                                                    │                            │
│   │ OUTPUT:                                            │                            │
│   │ • recommended_action: finalize / apply_and_rerun   │                            │
│   │                       / block                      │                            │
│   │ • proposed_changes: Config adjustments to apply    │                            │
│   │ • reasoning: Explanation of decision               │                            │
│   │ • Stored in: iteration_details.json → "critique"   │                            │
│   │                                                    │                            │
│   │ AFFECTS:                                           │                            │
│   │ • Controls iteration loop (rerun or finalize)      │                            │
│   │ • Can trigger config changes                       │                            │
│   │ • Can block report if critical issues              │                            │
│   └────────────────────────────────────────────────────┘                            │
│                                          │                                          │
└──────────────────────────────────────────┼──────────────────────────────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
          ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
          │ finalize        │    │ apply_and_rerun │    │ block           │
          │ (report is good)│    │ (iterate)       │    │ (critical issue)│
          └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
                   │                      │                      │
                   │                      ▼                      │
                   │         ┌─────────────────────────┐         │
                   │         │ Apply config changes    │         │
                   │         │ Go back to Phase 2      │         │
                   │         │ Run Iteration 2         │         │
                   │         └───────────┬─────────────┘         │
                   │                     │                       │
                   │                     ▼                       │
                   │         ┌─────────────────────────┐         │
                   │         │ REGRESSION CHECK        │         │
                   │         │ (deterministic)         │         │
                   │         │                         │         │
                   │         │ Compare ITER1 vs ITER2  │         │
                   │         │ If WORSENED → Rollback  │         │
                   │         └───────────┬─────────────┘         │
                   │                     │                       │
                   └─────────────────────┼───────────────────────┘
                                         │
════════════════════════════════════════════════════════════════════════════════════════
                         PHASE 4: FINALIZATION
════════════════════════════════════════════════════════════════════════════════════════
                                         │
                                         ▼
                    ┌─────────────────────────────────────────────┐
                    │  Generate Final Report                      │
                    │  PHASEA_MANUAL_REPORT_YYYYMMDD.md           │
                    └─────────────────────────────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────────┐
                    │  Save to Memory                             │
                    │  Update run_history.json (with ledger_path) │
                    └─────────────────────────────────────────────┘
```

---

## Output Files

Each run generates files in: `codex sgent/AGENT REPORT/{YYYYMMDD_HHMMSS}/`

| File | Description | Generated By |
|------|-------------|--------------|
| `PHASEA_MANUAL_REPORT_YYYYMMDD.md` | Main human-readable report with product tables | `render.py` |
| `coverage_ledger.csv` | ALL rows with bucket assignments, confidence, evidence | `analysis.py` |
| `run_summary.json` | Summary statistics (bucket counts, timestamps) | `run.py` |
| `evidence.jsonl` | Per-row match evidence (EAN, similarity, brand) | `analysis.py` |
| `iteration_details.json` | All AI step results (adjudication, critique) | `iteration.py` |
| `merged_calibration.json` | Final merged configuration used | `memory_store.py` |
| `calibration_diff.json` | Changes from base to merged config | `run.py` |
| `llm_trace.jsonl` | ALL LLM API calls with prompts/responses | `run.py` |
| `iter_1/` | Per-iteration artifacts | `iteration.py` |
| `iteration_N_report.md` | Intermediate report for comprehensive review | `iteration.py` |

### Key File Details

**PHASEA_MANUAL_REPORT_YYYYMMDD.md:**
```
# FBA ANALYSIS REPORT - PHASE A
## Summary
- Total analyzed: N rows
- VERIFIED: X | HIGHLY LIKELY: Y | NEEDS VERIFICATION: Z | FILTERED OUT: W

## VERIFIED - RECOMMENDED (count=X)
| Verdict | Confidence | SupplierTitle | AmazonTitle | ... |

## VERIFIED - FILTERED OUT / EXCLUDED (count=A)
...

## HIGHLY LIKELY - RECOMMENDED (count=Y)
...
```

**iteration_details.json:**
```json
{
  "adjudication_results": { ... },
  "comprehensive_adjudication": { ... },
  "critique": {
    "recommended_action": "finalize",
    "proposed_changes": [],
    "reasoning": "..."
  },
  "regression_diff": { ... }
}
```

---

## Memory System

The agent maintains a **layered memory system** for configuration and learning.

### Memory Directory Structure

```
📁 memory/                           
├── 📁 global/                        
│   ├── 📄 trap_library.jsonl         ← Universal shield keywords (ALL suppliers)
│   ├── 📄 known_brands.json          ← AI-validated brand names (NEW)
│   └── 📄 brand_candidates_checked.json ← Already-checked candidates (NEW)
│
└── 📁 suppliers/                     
    └── 📁 {supplier_id}/             ← E.g., "poundwholesale"
        ├── 📄 calibration.json       ← Supplier-specific config
        ├── 📄 run_history.json       ← Past run summaries + ledger_path
        ├── 📄 trap_library.jsonl     ← Supplier-specific traps
        ├── 📄 overrides.jsonl        ← User manual overrides (HIGHEST PRIORITY)
        └── 📄 brand_aliases.json     ← Brand name mappings
```

### Memory Files Explained

| File | Scope | Description | Used By |
|------|-------|-------------|---------|
| **global/trap_library.jsonl** | ALL | Dimension shields (cm, mm), spec shields (LED) | `analysis.py` |
| **global/known_brands.json** | ALL | AI-validated brand names with canonical forms | `brand_detector.py`, `analysis.py` |
| **global/brand_candidates_checked.json** | ALL | Candidates already validated (skip recheck) | `brand_detector.py` |
| **suppliers/{id}/calibration.json** | Per supplier | Pack keywords, brand position, patterns | `analysis.py` |
| **suppliers/{id}/run_history.json** | Per supplier | Past run stats + ledger_path | `critique.py` |
| **suppliers/{id}/trap_library.jsonl** | Per supplier | Supplier-specific shields | `analysis.py` |
| **suppliers/{id}/overrides.jsonl** | Per supplier | User overrides (highest priority) | `memory_store.py` |
| **suppliers/{id}/brand_aliases.json** | Per supplier | Brand name mappings | `analysis.py` |

### Configuration Merge Precedence

```
1. User Overrides (overrides.jsonl)        ← HIGHEST PRIORITY
2. Supplier Traps (supplier/trap_library)
3. Global Traps (global/trap_library)
4. Preflight Calibration (current run)
5. Base/Default Config                     ← LOWEST PRIORITY
```

---

## Commands

All commands run from project root.

### Main Analysis Command

```bash
# Basic analysis
python -m fba_agent analyze --input "path/to/report.xlsx"

# Full options
python -m fba_agent analyze \
  --input "path/to/report.xlsx" \
  --supplier "poundwholesale" \
  --runs-dir "runs" \
  --memory-dir "memory" \
  --overrides "overrides.jsonl" \
  --fee-rate 0.30 \
  --max-iterations 2 \
  --enable-ai true \
  --provider "gemini"
```

### Command Options

| Option | Default | Description |
|--------|---------|-------------|
| `--input` | (required) | Path to input Excel/CSV file |
| `--supplier` | `auto` | Supplier name or `auto` to detect |
| `--runs-dir` | `runs` | Directory to save outputs |
| `--memory-dir` | `memory` | Directory for memory files |
| `--overrides` | None | User overrides JSONL file |
| `--fee-rate` | `0.30` | Amazon fee rate fallback |
| `--max-iterations` | `2` | Max iteration count |
| `--enable-ai` | `true` | Enable AI features |
| `--provider` | `auto` | LLM: `openai`, `gemini`, `moonshot` |

### Other Commands

```bash
# List runs
python -m fba_agent list-runs

# View top candidates
python -m fba_agent top --run-id "20260108_031613" --min-confidence 80

# Explain a row
python -m fba_agent explain --run-id "20260108_031613" --rowid 123

# Export
python -m fba_agent export --run-id "20260108_031613" --format md

# Show memory
python -m fba_agent show-memory --supplier "poundwholesale"

# Rerun with overrides
python -m fba_agent rerun --run-id "20260108_031613" --apply-overrides "fixes.jsonl"
```

---

## AI Logic Summary Table

| AI Step | File | Purpose | Input | Output | Affects |
|---------|------|---------|-------|--------|---------|
| Brand Detection | `brand_detector.py` | Validate brand candidates | Supplier titles | `known_brands.json` | `brand_aliases` |
| Preflight | `preflight.py` | Detect patterns | Sample rows | `preflight_calibration.json` | `merged_config` |
| Per-Row Adj (Step 1) | `adjudication.py` | Review 99 flagged rows (sorted by profit) | Ledger + candidates | `adjudication_results` | `coverage_ledger.csv` |
| Comprehensive Adj (Step 2) | `comprehensive_adjudication.py` | Review full report | MD report | Errors, recategorizations | `coverage_ledger.csv`, Critique |
| Critique (Step 3) | `critique.py` | Final decision | All findings | `recommended_action` | Iteration loop |
| Regression | `regression.py` | Compare iterations | ITER1 vs ITER2 | Diff, rollback decision | Final report |

---

## Environment Variables

```bash
# Required for AI features
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Optional
FBA_TRACE_FILE=llm_trace.jsonl
FBA_LOG_LEVEL=INFO
```

---

## Current Implementation Status (v4.3.0)

### Implemented Fixes from IMPLEMENTED_FIXES_STEPS_5_6_7_SUMMARY.md:

| Fix | Description | Status |
|-----|-------------|--------|
| 1 | Reordered: Comprehensive Adj → Critique | ✅ Implemented |
| 2 | Passed comprehensive findings to critique | ✅ Implemented |
| 3 | Added findings to critique prompt | ✅ Implemented |
| 4 | Token-efficient formatting helper | ✅ Implemented |
| 5 | Passed actual source Excel path | ✅ Implemented |
| 6 | MD report tables sorted by confidence | ✅ Implemented |
| **7** | **Step 1 now processes MD REPORT (not ledger)** | ✅ **NEW v4.3.0** |
| **8** | **Batch size: 70 rows with category headers** | ✅ **NEW v4.3.0** |
| **9** | **Profit-based selection REMOVED** | ✅ **NEW v4.3.0** |
| **10** | **Comprehensive Adj receives Step 1 results** | ✅ **NEW v4.3.0** |

### AI Step 1 Changes (v4.3.0):

| Aspect | Before (v4.2.x) | After (v4.3.0) |
|--------|-----------------|----------------|
| **Input source** | Ledger (flagged rows) | **MD Report (ALL rows)** |
| **Row count** | ~99 flagged rows | **~367 MD report rows** |
| **Batch size** | 33 rows/batch | **70 rows/batch** |
| **API calls** | 3 | **~6** |
| **Category headers** | No | **Yes** |
| **Profit-based selection** | Yes (> £10) | **REMOVED** |

### Brand Detection Module:

- Extracts first 1-2 words as brand candidates
- Validates with AI (batch of 50 candidates per API call)
- Stores validated brands in `memory/global/known_brands.json`
- Tracks checked candidates to avoid re-validation
- Merges into `brand_aliases` for analysis

### MD Report Sorting:

- All tables in MD report are **sorted by confidence score descending**
- Highest-confidence products appear first in each section (VERIFIED, HIGHLY LIKELY, etc.)

---

## ⚠️ IMPORTANT: Analyzing a NEW Supplier

When analyzing a report from a **NEW supplier website**, you **MUST specify a unique supplier name** to avoid memory file mixing:

```bash
# CORRECT: Use unique supplier name for new supplier
python -m fba_agent analyze \
  --input "path/to/new_supplier_report.xlsx" \
  --supplier "new_supplier_name"

# WRONG: Using 'auto' may use wrong supplier memory
python -m fba_agent analyze \
  --input "path/to/new_supplier_report.xlsx" \
  --supplier "auto"  # ← DON'T DO THIS FOR NEW SUPPLIERS
```

**Why this matters:**
- Each supplier has its own `memory/suppliers/{supplier_id}/` directory
- Memory files include: `calibration.json`, `run_history.json`, `trap_library.jsonl`
- Using "auto" or wrong supplier name → loads wrong memory → wrong results

---

## Past Report Comparison - Where Does It Happen?

### The Step: AI Critique (Step 3)

**AI Critique** is the step that retrieves and compares the **previous run's report** with the **current report**.

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ AI CRITIQUE: Past Report Comparison                                               │
│                                                                                   │
│ HOW IT WORKS:                                                                     │
│                                                                                   │
│ 1. BEFORE critique runs, run.py loads the past ledger path:                       │
│                                                                                   │
│    from fba_agent.memory_store import load_run_history                            │
│    history = load_run_history(memory_dir, supplier_id, k=1)                       │
│    past_ledger_path = history[-1].get("ledger_path")                              │
│                                                                                   │
│    This loads from: memory/suppliers/{supplier_id}/run_history.json              │
│    Which contains: { "ledger_path": "previous_run/coverage_ledger.csv" }         │
│                                                                                   │
│ 2. CRITIQUE receives this path and calls:                                         │
│                                                                                   │
│    compare_with_past_ledger(current_ledger, past_ledger_path)                     │
│                                                                                   │
│ 3. This function COMPARES:                                                        │
│    • Bucket counts (past vs current)                                              │
│    • EANs that were VERIFIED in past but not in current (regressions)            │
│    • EANs that are NEW in VERIFIED (improvements)                                 │
│    • Same for HIGHLY_LIKELY                                                       │
│                                                                                   │
│ NOTE: If this is the FIRST RUN for a supplier, there is NO past report.          │
│       past_ledger_path will be None, and comparison is skipped.                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## What Does AI Critique Use to Decide?

**AI Critique uses MULTIPLE sources to make its decision:**

| Source | Description | How Critique Uses It |
|--------|-------------|---------------------|
| **1. Bucket Counts** | VERIFIED, HIGHLY_LIKELY, NEEDS_VER, FILTERED counts | Checks if distribution is reasonable |
| **2. Contradiction Detection** | Rows flagged VERIFIED but excluded from tables | Triggers **BLOCK** if detected |
| **3. EAN Statistics** | Matching EANs by bucket | Flags EAN matches in wrong buckets |
| **4. Past Report Comparison** | Compares against previous run's ledger | Flags regressions from last run |
| **5. Comprehensive Adj Findings** | Errors/recategorizations from Step 2 | Reviews what comp adj found |
| **6. Anomaly Summary** | Pack anomalies, profit outliers | Flags unusual patterns |
| **7. Sample Rows** | ALL VERIFIED and HIGHLY_LIKELY rows | Validates actual data quality |

### How Critique Identifies Errors and Decides:

```python
# In critique.py - these are called during build_critique_inputs():

# 1. Contradiction detection (CRITICAL - can trigger BLOCK)
contradictions = detect_contradictions(ledger)

# 2. EAN statistics (checks EAN integrity)
ean_stats = compute_ean_statistics(ledger)

# 3. Past report comparison (checks for regressions)
past_comparison = compare_with_past_ledger(ledger, past_ledger_path)

# 4. Comprehensive adjudication findings (from Step 2)
comprehensive_findings = _format_comprehensive_adj_for_prompt(comprehensive_adj_findings)

# 5. Anomaly summary (passed from analysis)
anomalies = anomaly_summary

# ALL OF THESE are included in the critique prompt for the LLM to review
```

---

## Latest Run Statistics (20260108_031613)

From the latest run's `run_summary.json`:

| Metric | Value |
|--------|-------|
| **Total Rows** | 2789 |
| **VERIFIED** | 35 |
| **HIGHLY_LIKELY** | 192 |
| **NEEDS_VERIFICATION** | 98 |
| **FILTERED_OUT** | 2464 |
| **Adjudication Count** | 50 (candidates processed by per-row adjudication) |

### Critique Decision:
- **Recommended Action:** `block`
- **High Severity Issues:** 2
- **Proposed Changes:** 5
- **Reason:** Critical contradictions detected - 19 EAN matches not classified as VERIFIED, 841 anomalies detected

**Note:** The adjudication count shows 50 - this run was before the fix to increase to 100.

---

**For detailed workflow documentation, see:** `WORKFLOW_AUDIT_AND_UPDATED_FINDINGS.md`

