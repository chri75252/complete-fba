# FBA Agent Workflow - AI Critique & Regression Check Explained

**Version:** 1.0  
**Last Updated:** 2026-01-07

---

## Overview

The FBA Agent has TWO DISTINCT types of AI-powered report comparison:

1. **AI CRITIQUE** - Compares CURRENT REPORT vs LAST SAVED REPORT (from memory)
2. **ITERATION REGRESSION CHECK** - Compares ITERATION 2 vs ITERATION 1 (within same run)

**These are DIFFERENT processes with DIFFERENT purposes.**

---

## Workflow Sequence Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FBA AGENT COMPLETE WORKFLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: PREFLIGHT CALIBRATION                                              │
│  ─────────────────────────────────                                          │
│  • AI analyzes Excel data structure                                         │
│  • Detects pack patterns, brand position, dimension keywords                │
│  • Outputs: calibration.json                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: LOAD MEMORY                                                        │
│  ───────────────────                                                        │
│  • Load global traps (cm, mm, inch shields)                                 │
│  • Load supplier-specific calibration                                       │
│  • Load PAST LEDGER PATH from run_history.json ◄── NEW (for AI critique)    │
│  • Merge with precedence: overrides > traps > calibration > defaults        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: ROW-BY-ROW ANALYSIS (ITERATION 1)                                  │
│  ─────────────────────────────────────────                                  │
│  • Deterministic code (not AI) analyzes each row                            │
│  • EAN matching → Brand matching → Pack detection → Profit calculation      │
│  • Assigns bucket: VERIFIED / HIGHLY_LIKELY / NEEDS_VERIFICATION / FILTERED │
│  • Outputs: ledger (DataFrame), evidence (list)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: GENERATE ITERATION 1 REPORT                                        │
│  ───────────────────────────────────                                        │
│  • Create Markdown report from ledger                                       │
│  • Save coverage_ledger.csv                                                 │
│  • Save evidence.jsonl                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌═════════════════════════════════════════════════════════════════════════════┐
║  STEP 5: AI CRITIQUE (Comparison Type 1)                                    ║
║  ═══════════════════════════════════════                                    ║
║                                                                             ║
║  PURPOSE: Compare CURRENT REPORT vs LAST SAVED REPORT from memory           ║
║                                                                             ║
║  WHAT IT CHECKS:                                                            ║
║  • CONTRADICTION DETECTION (CRITICAL):                                      ║
║    - Items with track=VERIFIED but include_in_tables=False                  ║
║    - Items with matching EANs not in VERIFIED bucket                        ║
║                                                                             ║
║  • PAST REPORT COMPARISON:                                                  ║
║    - Load coverage_ledger.csv from LAST SAVED RUN (via run_history.json)    ║
║    - Compare: Which EANs were VERIFIED before but not now?                  ║
║    - Compare: Which EANs were HIGHLY_LIKELY before but not now?             ║
║    - Flag regressions: "5 items that were VERIFIED are now missing"         ║
║                                                                             ║
║  • EAN INTEGRITY CHECK:                                                     ║
║    - How many matching EANs are in VERIFIED? HIGHLY_LIKELY? FILTERED_OUT?   ║
║    - Matching EANs in wrong buckets = HIGH severity issue                   ║
║                                                                             ║
║  • ALL ROWS REVIEWED (not just 5 samples):                                  ║
║    - ALL VERIFIED items are passed to AI                                    ║
║    - ALL HIGHLY_LIKELY items are passed to AI                               ║
║    - Statistical summary of FILTERED_OUT                                    ║
║                                                                             ║
║  OUTPUTS:                                                                   ║
║  • high_severity_issues: List of problems found                             ║
║  • proposed_changes: Config adjustments (add_shield_token, etc.)            ║
║  • recommended_action: "finalize" / "apply_and_rerun" / "block"             ║
║                                                                             ║
║  BLOCK CONDITIONS:                                                          ║
║  • ANY contradiction detected (track=VERIFIED, include_in_tables=False)    ║
║  • Significant regression from past report (many items missing)             ║
║  • Critical EAN integrity issues                                            ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: AI ADJUDICATION                                                    │
│  ───────────────────────                                                    │
│  • AI reviews individual ambiguous rows (borderline confidence)             │
│  • Suggests bucket changes for unclear cases                                │
│  • Applied if critique says "apply_and_rerun"                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────────┐
                          │ Critique recommends   │
                          │ "apply_and_rerun"?    │
                          └───────────────────────┘
                                 │         │
                        NO ◄─────┘         └────► YES
                         │                         │
                         ▼                         ▼
              ┌──────────────────┐   ┌──────────────────────────────────┐
              │  FINALIZE REPORT │   │  STEP 7: APPLY ADJUSTMENTS       │
              │  (Skip to Step 9)│   │  • Update config with AI changes │
              └──────────────────┘   │  • Add shield tokens, brand aliases│
                                     └──────────────────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: ROW-BY-ROW ANALYSIS (ITERATION 2)                                  │
│  ─────────────────────────────────────────                                  │
│  • Same as Step 3, but with UPDATED config                                  │
│  • May produce different categorizations due to config changes              │
│  • Outputs: ledger_iter2, evidence_iter2                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌═════════════════════════════════════════════════════════════════════════════┐
║  STEP 9: ITERATION REGRESSION CHECK (Comparison Type 2)                     ║
║  ══════════════════════════════════════════════════════                     ║
║                                                                             ║
║  PURPOSE: Compare ITERATION 2 vs ITERATION 1 (within SAME RUN)              ║
║                                                                             ║
║  THIS IS DIFFERENT FROM AI CRITIQUE!                                        ║
║  • AI Critique: Compares against LAST SAVED REPORT (from memory)            ║
║  • Regression Check: Compares ITER2 vs ITER1 (within current run)           ║
║                                                                             ║
║  WHAT IT CHECKS:                                                            ║
║  • Missing stable_keys: Were any rows in ITER1 not in ITER2? → HARD FAIL   ║
║  • Good-to-bad transitions: Did VERIFIED/HIGHLY_LIKELY items drop?          ║
║  • Bad-to-good transitions: Did FILTERED_OUT items get promoted? (OK)       ║
║  • Wrong category moves: Did items move to incorrect categories?            ║
║                                                                             ║
║  REGRESSION DEFINITION (COMPREHENSIVE):                                     ║
║  Regression is NOT just "report got shorter". A report regressed if:        ║
║                                                                             ║
║  1. VERIFIED count dropped significantly                                    ║
║  2. HIGHLY_LIKELY count dropped significantly                               ║
║  3. Valid items were INCORRECTLY moved to FILTERED_OUT                      ║
║  4. INVALID items were ADDED to VERIFIED/HIGHLY_LIKELY (false positives)    ║
║  5. Items moved to WRONG categories (VERIFIED → NEEDS_VERIFICATION)         ║
║  6. Rows are MISSING entirely (stable_key not found)                        ║
║                                                                             ║
║  THRESHOLDS:                                                                ║
║  • Missing keys: ANY = HARD FAIL                                            ║
║  • Good-to-bad: >10% of previously-good OR >30 absolute = BLOCK             ║
║                                                                             ║
║  IF REGRESSION DETECTED:                                                    ║
║  • Block ITERATION 2                                                        ║
║  • Use ITERATION 1 as final output                                          ║
║  • Report the regression in run_summary.json                                ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 10: FINALIZE                                                          │
│  ─────────────────                                                          │
│  • Select best iteration (ITER1 if regression, else ITER2)                  │
│  • Save final report to output folder                                       │
│  • Update run_history.json with ledger_path for next run's comparison       │
└─────────────────────────────────────────────────────────────────────────────┘

```

---

## Comparison Summary Table

| Aspect | AI CRITIQUE (Step 5) | ITERATION REGRESSION CHECK (Step 9) |
|--------|---------------------|-------------------------------------|
| **When** | After each iteration | After ITERATION 2 only |
| **Compares** | Current report vs. LAST SAVED REPORT from memory | ITERATION 2 vs. ITERATION 1 |
| **Purpose** | Find discrepancies from previous reliable run | Ensure config changes didn't make it worse |
| **Data Source** | `run_history.json` → `ledger_path` | In-memory comparison |
| **Scope** | Full ledger comparison | Full ledger comparison |
| **Blocks If** | Contradictions, critical issues | Missing rows, excessive good-to-bad |
| **Action on Block** | Stop run, require manual review | Use ITERATION 1 instead |

---

## What Constitutes a "Regression"?

A regression is NOT just "the report got shorter". The report is considered REGRESSED if:

### Quality Regressions (Bad Changes)

| Regression Type | Description | Severity |
|-----------------|-------------|----------|
| **Missing Rows** | Rows in previous not in current | HARD FAIL |
| **VERIFIED → FILTERED** | Valid EAN matches excluded | HIGH |
| **HIGHLY_LIKELY → FILTERED** | Strong matches excluded | HIGH |
| **VERIFIED → NEEDS_VERIFICATION** | Downgrade without reason | MEDIUM |
| **Items added to wrong bucket** | Invalid items in VERIFIED | HIGH |
| **False positives added** | Products that don't match | CRITICAL |

### Acceptable Changes (Not Regressions)

| Change Type | Description | Impact |
|-------------|-------------|--------|
| **FILTERED → VERIFIED** | Previously missed items found | GOOD |
| **FILTERED → HIGHLY_LIKELY** | Previously missed strong matches | GOOD |
| **NEEDS_VERIFICATION → VERIFIED** | Confirmation achieved | GOOD |
| **NEEDS_VERIFICATION → FILTERED** | Confirmed non-match | NEUTRAL |

---

## Files That Store Past Reports

| File | Location | Contains | Used By |
|------|----------|----------|---------|
| `run_history.json` | `memory/suppliers/{supplier}/` | Bucket counts, ledger_path, run metadata | AI Critique |
| `coverage_ledger.csv` | `codex sgent/AGENT REPORT/{run_id}/` | Full ledger with all rows | AI Critique (loaded from ledger_path) |
| iteration ledgers | In-memory during run | Full ledger per iteration | Regression Check |

---

## Implementation Files

| File | Contains | AI Logic |
|------|----------|----------|
| `src/fba_agent/critique.py` | AI Critique logic | System/user prompts for report review |
| `src/fba_agent/regression.py` | Regression check logic | Deterministic comparison (not AI) |
| `src/fba_agent/adjudication.py` | Row-level AI review | System/user prompts for ambiguous rows |
| `src/fba_agent/iteration.py` | Iteration loop | Orchestrates critique, adjudication, regression |
| `src/fba_agent/run.py` | Main entry point | Loads past ledger, saves run history |

---

*End of Workflow Documentation*
