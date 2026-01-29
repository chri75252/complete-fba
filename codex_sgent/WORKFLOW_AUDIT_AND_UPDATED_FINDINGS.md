# FBA AGENT COMPLETE WORKFLOW (CURRENT IMPLEMENTATION v4.3.0)

**Date:** 2026-01-08 20:25 UTC+4  
**Version:** v4.3.0 (Current - AI Step MD Report Batch Processing)  
**Status:** Production-Ready

---

## OVERVIEW

This document describes the COMPLETE end-to-end workflow of the FBA Agent as **currently implemented**, including:
- Brand Detection Module (extracts and validates brands with AI)
- AI Logic Steps 1, 2, 3 (Per-Row Adjudication → Comprehensive Adjudication → Critique)
- Fixes implemented from `IMPLEMENTED_FIXES_STEPS_5_6_7_SUMMARY.md`

---

## AI LOGIC STEP FLOW DIAGRAM (CURRENT IMPLEMENTATION)

```
════════════════════════════════════════════════════════════════════════════════════════
                         PHASE 1: SETUP & CALIBRATION
════════════════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────┐
    │ 1. CLI + Data Loading       │
    │    • Load Excel/CSV         │
    │    • Normalize columns      │
    │    • Generate stable keys   │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ 2. Preflight Calibration    │ ← AI
    │    • Detect pack keywords   │
    │    • Detect brand position  │
    │    • Detect capacity ptrns  │
    │                             │
    │    OUTPUT: preflight_       │
    │    calibration.json         │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────────────────────────────────────────────────┐
    │ 3. Brand Detection (NEW MODULE)                                                 │
    │                                                                                 │
    │    PURPOSE:                                                                     │
    │    Extract brand candidates from supplier titles, validate with AI,             │
    │    and build a persistent known_brands dictionary.                              │
    │                                                                                 │
    │    PROCESS:                                                                     │
    │    1. Extract first 1-2 words from each SupplierTitle                           │
    │    2. Skip candidates already in known_brands.json or checked list              │
    │    3. Send NEW candidates to AI for validation (batch of 50)                    │
    │    4. AI returns: {candidate, is_brand, brand_name, confidence, reason}         │
    │    5. Store validated brands in known_brands.json                               │
    │    6. Mark all candidates as checked (avoid re-validation)                      │
    │                                                                                 │
    │    OUTPUT FILES:                                                                │
    │    • memory/global/known_brands.json       ← Validated brands dictionary        │
    │    • memory/global/brand_candidates_checked.json ← Already checked list         │
    │                                                                                 │
    │    AFFECTS:                                                                     │
    │    • brand_aliases dictionary (merged with known_brands)                        │
    │    • analysis.py brand matching logic (uses validated brands only)              │
    │                                                                                 │
    │    FILE: src/fba_agent/brand_detector.py                                        │
    └─────────────────────────────────────────────────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ 4. Load Memory + Merge      │
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
    │    PURPOSE:                 │
    │    Categorize each row into │
    │    buckets based on EAN,    │
    │    brand, pack, similarity  │
    │                             │
    │    OUTPUT FILES:            │
    │    • coverage_ledger.csv    │
    │    • evidence.jsonl         │
    │                             │
    │    BUCKETS:                 │
    │    • VERIFIED               │
    │    • HIGHLY_LIKELY          │
    │    • NEEDS_VERIFICATION     │
    │    • FILTERED_OUT           │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ Generate Iteration Report   │
    │ (iteration_N_report.md)     │
    └─────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════════════
                     PHASE 3: AI LOGIC STEPS (STEP 1, 2, 3)
════════════════════════════════════════════════════════════════════════════════════════

                │
                ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│   ╔═══════════════════════════════════════════════════════════════════════════════╗ │
│   ║  AI STEP 1: Per-Row Adjudication FROM MD REPORT (v4.3.0)                      ║ │
│   ╚═══════════════════════════════════════════════════════════════════════════════╝ │
│                                                                                     │
│   PURPOSE:                                                                          │
│   Review ALL rows from generated MD report for bucket corrections.                  │
│   Analyzes complete categorized output, not just flagged ledger rows.               │
│                                                                                     │
│   INPUT (v4.3.0):                                                                   │
│   • ALL rows from MD report (~367 rows, NOT 2789 Excel rows)                        │
│   • Processed in batches of 70 rows with category headers                           │
│   • ~6 API calls total                                                              │
│   • NOTE: Profit-based selection REMOVED (only ambiguity signals matter)            │
│                                                                                     │
│   OUTPUT:                                                                           │
│   • Per-batch bucket corrections and pack issues                                    │
│   • Stored in: iteration_details.json → "adjudication_results"                      │
│                                                                                     │
│   AFFECTS:                                                                          │
│   • coverage_ledger.csv - Bucket reassignments applied                              │
│   • Can upgrade NEEDS_VERIFICATION → HIGHLY_LIKELY                                  │
│   • Can downgrade HIGHLY_LIKELY → FILTERED_OUT if issues found                      │
│                                                                                     │
│   FUNCTIONS:                                                                        │
│   • create_md_report_batches() - Parses MD, creates 70-row batches with headers     │
│   • run_md_batch_adjudication() - Sends batch to LLM for analysis                   │
│   • apply_batch_adjudication_to_ledger() - Applies corrections to ledger            │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                             │   │
│   │   Reviews ALL MD report rows in batches of 70 with category headers         │   │
│   │   Returns: bucket_corrections, pack_issues, overall_assessment              │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │ APPLY to LEDGER                                                             │   │
│   │ (upgrade NEEDS_VER → HL)                                                    │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                                          ▼                                          │
│   ╔═══════════════════════════════════════════════════════════════════════════════╗ │
│   ║  AI STEP 2: Comprehensive Adjudication                                        ║ │
│   ╚═══════════════════════════════════════════════════════════════════════════════╝ │
│                                                                                     │
│   PURPOSE:                                                                          │
│   Review the FULL Markdown report to identify patterns, systemic errors,            │
│   and issues that span across multiple products. Provides holistic analysis.        │
│                                                                                     │
│   INPUT:                                                                            │
│   • Full Markdown report (iteration_N_report.md)                                    │
│   • coverage_ledger.csv                                                             │
│   • Source Excel path (for reference)                                               │
│                                                                                     │
│   OUTPUT:                                                                           │
│   • errors: List of identified errors with evidence                                 │
│   • recategorizations: Products to move between buckets                             │
│   • root_causes: Underlying issues in logic/data                                    │
│   • config_recommendations: Suggested config changes                                │
│   • Stored in: comprehensive_adjudication.json                                      │
│                                                                                     │
│   AFFECTS:                                                                          │
│   • coverage_ledger.csv - Recategorizations applied                                 │
│   • PASSES FINDINGS to AI Critique (Step 3)   ←── KEY INTEGRATION                   │
│                                                                                     │
│   FILE: src/fba_agent/comprehensive_adjudication.py                                 │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                             │   │
│   │   Reviews FULL markdown report                                              │   │
│   │   Returns: errors, recategorizations, root causes, config recommendations  │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │ APPLY to LEDGER                                                             │   │
│   │ (fix false positives/negatives)                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                     PASS FINDINGS ───────┼────────────────────────────────────────┐ │
│                                          │                                        │ │
│                                          ▼                                        ▼ │
│   ╔═══════════════════════════════════════════════════════════════════════════════╗ │
│   ║  AI STEP 3: Critique (Decision Maker)                                         ║ │
│   ╚═══════════════════════════════════════════════════════════════════════════════╝ │
│                                                                                     │
│   PURPOSE:                                                                          │
│   Make the final decision on report quality. Reviews all available information      │
│   including comprehensive adjudication findings. Decides: finalize, iterate, block.│
│                                               ┌─────────────────────────────────┐   │
│   INPUT:                                      │ Critique now knows:             │   │
│   • Bucket counts and anomalies               │ • N errors found                │   │
│   • Comprehensive adjudication findings  ────►│ • N recategorizations           │   │
│   • Past ledger (from memory) for comparison  │ • Root causes                   │   │
│   • EAN statistics                            │ • Config recommendations        │   │
│   • Contradiction detection results           └─────────────────────────────────┘   │
│                                                                                     │
│   OUTPUT:                                                                           │
│   • recommended_action: "finalize" | "apply_and_rerun" | "block"                    │
│   • proposed_changes: List of config adjustments to apply                           │
│   • reasoning: Explanation of decision                                              │
│   • Stored in: iteration_details.json → "critique"                                  │
│                                                                                     │
│   AFFECTS:                                                                          │
│   • Controls iteration loop (continue or stop)                                      │
│   • Can trigger config changes for next iteration                                   │
│   • Can block report if critical issues detected                                    │
│                                                                                     │
│   FILE: src/fba_agent/critique.py                                                   │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │ DECISION:                                                                   │   │
│   │ • finalize (report is good)                                                 │   │
│   │ • apply_and_rerun (fix config, iterate)                                     │   │
│   │ • block (critical issues)                                                   │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
└──────────────────────────────────────────┼──────────────────────────────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
          ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
          │ finalize        │    │ apply_and_rerun │    │ block           │
          │ Report is good  │    │ Apply changes   │    │ Critical issue  │
          │ → Go to Phase 4 │    │ → Run Iter 2    │    │ → Stop & report │
          └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
                   │                      │                      │
                   │                      ▼                      │
                   │         ┌─────────────────────────┐         │
                   │         │ Apply config changes    │         │
                   │         │ Go back to Phase 2      │         │
                   │         └───────────┬─────────────┘         │
                   │                     │                       │
                   │                     ▼                       │
                   │         ┌─────────────────────────┐         │
                   │         │ REGRESSION CHECK        │         │
                   │         │ (deterministic)         │         │
                   │         │                         │         │
                   │         │ • Compare ITER1 vs ITER2│         │
                   │         │ • Check missing rows    │         │
                   │         │ • Check bad transitions │         │
                   │         │ • If WORSENED → Rollback│         │
                   │         │                         │         │
                   │         │ FILE: regression.py     │         │
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
                    │                                             │
                    │  FILE: render.py                            │
                    └─────────────────────────────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────────┐
                    │  Save to Memory                             │
                    │  • Update run_history.json                  │
                    │  • Store ledger_path for future comparison  │
                    │                                             │
                    │  FILE: memory_store.py                      │
                    └─────────────────────────────────────────────┘
```

---

## IMPLEMENTED FIXES (from IMPLEMENTED_FIXES_STEPS_5_6_7_SUMMARY.md)

### Fix 1: Increased Adjudication Candidate Cap (50 → 100)

**File:** `src/fba_agent/iteration.py` (line 233)

| Aspect | Before | After |
|--------|--------|-------|
| Candidates processed | 50 rows | **100 rows** |
| API calls | 5 batches | **10 batches** |
| Coverage | Limited | Improved |

---

### Fix 2: Reordered AI Steps (Comprehensive → Critique)

**File:** `src/fba_agent/iteration.py` (lines 257-340)

| Aspect | Before | After |
|--------|--------|-------|
| Step order | Critique → Comprehensive | **Comprehensive → Critique** |
| Critique knowledge | No findings available | Has full comprehensive findings |
| Decision quality | Uninformed | **Informed** |

---

### Fix 3: Passed Comprehensive Adjudication Findings to Critique

**File:** `src/fba_agent/critique.py` (line 307)

```python
# NEW PARAMETER ADDED:
def build_critique_inputs(
    ...
    comprehensive_adj_findings: dict | None = None,  # ← NEW
) -> dict:
```

---

### Fix 4: Added Comprehensive Findings to Critique Prompt

**File:** `src/fba_agent/critique.py` (lines 603-608)

```python
## 📊 Comprehensive Adjudication Findings (from previous AI step)
{json.dumps(_format_comprehensive_adj_for_prompt(findings), indent=2)}
```

Critique prompt now shows:
- Number of errors found
- Number of recategorizations
- Root causes identified
- Sample errors and recommendations

---

### Fix 5: Token-Efficient Formatting Helper

**File:** `src/fba_agent/critique.py` (lines 91-134)

Created `_format_comprehensive_adj_for_prompt()` to limit output size and avoid context overflow.

---

### Fix 6: Passed Actual Source Excel Path

**File:** `src/fba_agent/iteration.py` (lines 298-302)

| Aspect | Before | After |
|--------|--------|-------|
| Source path | Empty string `""` | **Actual path from config** |
| Comprehensive adj | Cannot reference source | **Can reference source file** |

---

## OUTPUT FILES

### Run Directory: `codex sgent/AGENT REPORT/{YYYYMMDD_HHMMSS}/`

| File | Purpose | Generated By |
|------|---------|--------------|
| `PHASEA_MANUAL_REPORT_YYYYMMDD.md` | Final human-readable report | `render.py` |
| `coverage_ledger.csv` | All rows with buckets, confidence, evidence | `analysis.py` |
| `run_summary.json` | Bucket counts, timestamps, input file | `run.py` |
| `evidence.jsonl` | Per-row match evidence | `analysis.py` |
| `iteration_details.json` | Adjudication, comprehensive, critique results | `iteration.py` |
| `merged_calibration.json` | Final config used | `memory_store.py` |
| `llm_trace.jsonl` | All LLM API calls | `run.py` |
| `iteration_N_report.md` | Intermediate report for comprehensive review | `iteration.py` |

### Memory Directory: `memory/`

| File | Purpose | Scope |
|------|---------|-------|
| `global/trap_library.jsonl` | Universal shields | All suppliers |
| `global/known_brands.json` | AI-validated brands | All suppliers |
| `global/brand_candidates_checked.json` | Checked candidates | All suppliers |
| `suppliers/{id}/calibration.json` | Supplier config | Per supplier |
| `suppliers/{id}/run_history.json` | Past runs + ledger_path | Per supplier |
| `suppliers/{id}/overrides.jsonl` | User overrides | Per supplier |

---

## AI STEPS PURPOSE SUMMARY

| Step | Purpose | Input | Output | Affects |
|------|---------|-------|--------|---------|
| **Brand Detection** | Validate brand candidates | Supplier titles | `known_brands.json` | Brand matching logic |
| **Preflight** | Detect patterns | Sample rows | `preflight_calibration.json` | Merged config |
| **AI Step 1** (Per-Row Adj) | Review 99 flagged rows (sorted by profit) | Flagged candidates | Bucket recommendations | `coverage_ledger.csv` |
| **AI Step 2** (Comprehensive Adj) | Review full report for patterns | Full MD report | Errors, recategorizations | `coverage_ledger.csv`, Critique |
| **AI Step 3** (Critique) | Final decision | All findings | finalize/rerun/block | Iteration loop |
| **Regression** | Compare iterations | ITER1 vs ITER2 | Diff, rollback | Final report |

---

## COMMANDS

```bash
# Main analysis
python -m fba_agent analyze --input "path/to/report.xlsx" --enable-ai true

# List runs
python -m fba_agent list-runs

# View top candidates
python -m fba_agent top --run-id "YYYYMMDD_HHMMSS" --min-confidence 80

# Explain a row
python -m fba_agent explain --run-id "YYYYMMDD_HHMMSS" --rowid 123

# Export
python -m fba_agent export --run-id "YYYYMMDD_HHMMSS" --format md

# Show memory
python -m fba_agent show-memory --supplier "poundwholesale"

# Rerun with overrides
python -m fba_agent rerun --run-id "YYYYMMDD_HHMMSS" --apply-overrides "fixes.jsonl"
```

---

## BEHAVIORAL CHANGES (Before Fixes vs After Fixes)

| Aspect | BEFORE Fixes | AFTER Fixes (v4.3.0) |
|--------|-------------|-------------|
| **Step 1 Input** | Ledger flagged rows | **MD Report ALL rows (~367)** |
| **Batch size** | 33 rows/call | **70 rows/call with headers** |
| **API calls** | 3 | **~6** |
| **Profit-based selection** | Yes (> £10) | **REMOVED** |
| **Category headers in batch** | No | **Yes** |
| Step order | Critique → Comprehensive | **Comprehensive → Critique** |
| Critique knowledge | No comprehensive findings | **Receives comprehensive findings** |
| Comprehensive Adj input | MD report only | **MD report + Step 1 results** |
| Source file access | Empty string | **Actual path passed** |
| MD report tables | Arbitrary order | **Sorted by confidence descending** |

---

## ⚠️ IMPORTANT: Analyzing a NEW Supplier

When analyzing from a **NEW supplier website**, you **MUST specify a unique supplier name**:

```bash
# CORRECT: Use unique supplier name for new supplier
python -m fba_agent analyze \
  --input "path/to/new_supplier_report.xlsx" \
  --supplier "new_supplier_name"

# WRONG: Using 'auto' may load wrong supplier memory
python -m fba_agent analyze \
  --input "path/to/new_supplier_report.xlsx" \
  --supplier "auto"  # ← DON'T DO THIS FOR NEW SUPPLIERS
```

**Why this matters:**
- Each supplier has its own `memory/suppliers/{supplier_id}/` directory
- Memory files include: `calibration.json`, `run_history.json`, `trap_library.jsonl`
- Using "auto" or wrong supplier name → loads wrong memory → wrong results

---

## PAST REPORT COMPARISON - DETAILED EXPLANATION

### Which Step Retrieves and Compares Past Reports?

**AI Critique (AI Step 3)** retrieves and compares the previous run's report.

### How It Works:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: run.py loads past ledger path BEFORE iteration loop                       │
│                                                                                   │
│   from fba_agent.memory_store import load_run_history                             │
│   history = load_run_history(memory_dir, supplier_id, k=1)                        │
│   past_ledger_path = history[-1].get("ledger_path")                               │
│                                                                                   │
│   Source: memory/suppliers/{supplier_id}/run_history.json                         │
│   Contains: { "ledger_path": "previous_run/coverage_ledger.csv" }                 │
└───────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: iteration.py passes past_ledger_path to critique                          │
│                                                                                   │
│   critique_inputs = build_critique_inputs(                                        │
│       ...                                                                         │
│       past_ledger_path=past_ledger_path,  # ← PASSED HERE                         │
│       comprehensive_adj_findings=comprehensive_adj_result,                        │
│   )                                                                               │
└───────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: critique.py calls compare_with_past_ledger()                              │
│                                                                                   │
│   if past_ledger_path:                                                            │
│       inputs["past_comparison"] = compare_with_past_ledger(ledger, past_ledger_path)
│                                                                                   │
│   This function compares:                                                         │
│   • Bucket counts (past vs current)                                               │
│   • EANs in VERIFIED (past vs current) → finds regressions                        │
│   • EANs in HIGHLY_LIKELY (past vs current) → finds regressions                   │
│   • Identifies missing products that were previously captured                     │
└───────────────────────────────────────────────────────────────────────────────────┘
```

**NOTE:** If this is the FIRST RUN for a supplier, there is NO past report. `past_ledger_path` will be `None`, and comparison is skipped.

---

## WHAT DOES AI CRITIQUE USE TO DECIDE?

**AI Critique uses 7 data sources to make its decision:**

| # | Source | Description | Possible Outcome |
|---|--------|-------------|------------------|
| 1 | **Bucket Counts** | VERIFIED, HIGHLY_LIKELY, NEEDS_VER, FILTERED counts | Flags unusual distributions |
| 2 | **Contradiction Detection** | Rows marked VERIFIED but `include_in_tables=False` | Triggers **BLOCK** |
| 3 | **EAN Statistics** | Matching EANs, by bucket | Flags EAN matches in wrong buckets |
| 4 | **Past Report Comparison** | Compares current vs previous ledger | Flags regressions |
| 5 | **Comprehensive Adj Findings** | Errors, recategorizations from Step 2 | Reviews what comp adj found |
| 6 | **Anomaly Summary** | Pack anomalies, profit outliers | Flags unusual patterns |
| 7 | **Sample Rows** | ALL VERIFIED and HIGHLY_LIKELY rows | Validates data quality |

### Code Flow (critique.py → build_critique_inputs):

```python
# 1. Contradiction detection (CRITICAL - can trigger BLOCK)
contradictions = detect_contradictions(ledger)

# 2. EAN statistics 
ean_stats = compute_ean_statistics(ledger)

# 3. Past report comparison
if past_ledger_path:
    past_comparison = compare_with_past_ledger(ledger, past_ledger_path)

# 4. Comprehensive adjudication findings (from Step 2)
comprehensive = _format_comprehensive_adj_for_prompt(comprehensive_adj_findings)

# 5. Anomaly summary (from analysis)
anomalies = anomaly_summary

# 6,7. Bucket counts and sample rows are extracted from ledger

# ALL added to critique prompt for LLM to review
```

---

## LATEST RUN STATISTICS (20260108_031613)

From `run_summary.json`:

| Metric | Value |
|--------|-------|
| **Total Rows** | 2789 |
| **VERIFIED** | 35 |
| **HIGHLY_LIKELY** | 192 |
| **NEEDS_VERIFICATION** | 98 |
| **FILTERED_OUT** | 2464 |
| **Adjudication Count** | 50 (before fix to 100) |

### Critique Decision:

| Field | Value |
|-------|-------|
| **recommended_action** | `block` |
| **high_severity_issues** | 2 |
| **proposed_changes** | 5 |
| **overall_assessment** | 19 EAN matches not classified as VERIFIED, 841 anomalies detected |

**Note:** The adjudication count shows 50 - this run was BEFORE the fix to increase to 99.

---

**Last Updated:** 2026-01-08 19:10 UTC+4  
**Agent Version:** v4.2.1 (Current Implementation)
