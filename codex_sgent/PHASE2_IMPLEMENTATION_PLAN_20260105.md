# FBA Analysis Agent vNext — Phase 2 Implementation Plan

**Date:** 2026-01-05  
**Timezone:** Asia/Dubai (UTC+4)  
**Status:** PHASE 2 PLAN ONLY (Pending approval before implementation)  
**Authoritative PRD:** `PRD_VNEXT_PHASE1_FBA_AGENT_UPGRADE_20260104.md`

---

## DELIVERABLE A — Repository Reconnaissance

### A.1 Directory Tree: `src\fba_agent` (Code)

```
src/fba_agent/
├── __pycache__/
├── analysis.py        [11685 bytes] — Row analysis + bucket assignment
├── atomic.py          [1477 bytes]  — Atomic file write utilities
├── cli.py             [6495 bytes]  — CLI entry: analyze, top, explain, export, rerun, list-runs, show-memory
├── constants.py       [1292 bytes]  — TABLE_COLUMNS, STOPWORDS, COLORS, SCENTS, default paths
├── ean.py             [2068 bytes]  — EAN normalization + GTIN checksum validation
├── exports.py         [1503 bytes]  — Export run artifacts (md/csv/json)
├── io.py              [4641 bytes]  — load_report(), normalize_columns()
├── memory_store.py    [3768 bytes]  — Supplier memory: load, merge, persist calibration
├── moonshot.py        [1810 bytes]  — Moonshot API adapter
├── openai_client.py   [1786 bytes]  — OpenAI Chat Completions wrapper
├── pack.py            [3325 bytes]  — Pack quantity parsing + trap detection
├── preflight.py       [2760 bytes]  — LLM-assisted preflight calibration
├── render.py          [5821 bytes]  — PhaseA report renderer (Markdown)
├── run.py             [4026 bytes]  — Main orchestrator: run_analysis()
├── runs.py            [282 bytes]   — list_runs() utility
├── scoring.py         [1149 bytes]  — Confidence score computation
├── text.py            [1076 bytes]  — Text utilities (sanitize, tokenize, jaccard)
├── top.py             [1148 bytes]  — Top candidates display
├── types.py           [2872 bytes]  — Dataclasses: SupplierNamingConvention, MergedConfig, RowDecisionRecord, etc.
├── validate.py        [1351 bytes]  — Coverage + profit validation gates
└── variant.py         [1655 bytes]  — Variant parsing (capacity, color, scent)
```

### A.2 Directory Tree: `codex sgent` (Docs/Specs)

```
codex sgent/
├── AGENT REPORT/                    — Run output directory
├── CODEX_SESSION_SUMMARY_20260104.md
├── PRD_DELTA_vs_gem_AG_PHASE1.md
├── PRD_DELTA_vs_opus_agent_PHASE1.md
├── PRD_TECH_SPEC_FBA_PRODUCT_ANALYSIS_AGENT_v1.0.md
├── PRD_VNEXT_PHASE1_FBA_AGENT_UPGRADE_20260104.md   ← AUTHORITATIVE PRD
├── README.md
└── prompt_specs/
    ├── AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md      — Preflight schema
    ├── FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md     — Methodology guide
    ├── FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md — Main spec (TABLE_SCHEMA, validation)
    └── MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md
```

### A.3 Existing Modules/Functions Relevant to vNext

| Component | File | Key Functions | Status |
|-----------|------|---------------|--------|
| **Data Loading** | `io.py` | `load_report()`, `normalize_columns()` | ✅ Exists |
| **Preflight Calibration** | `preflight.py` | `run_preflight()`, `_heuristic_preflight()` | ✅ Exists (LLM + fallback) |
| **Memory Store** | `memory_store.py` | `load_supplier_memory()`, `merge_calibration()`, `persist_calibration()` | ✅ Exists (partial) |
| **Row Analysis** | `analysis.py` | `analyze_row()`, `analyze_all_rows()` | ✅ Exists |
| **Pack Detection** | `pack.py` | `parse_pack_quantity()`, `pack_ratio()` | ✅ Exists |
| **EAN Validation** | `ean.py` | `normalize_and_validate()`, `validate_gtin()` | ✅ Exists |
| **Validation Gates** | `validate.py` | `validate_coverage()`, `validate_profit()` | ✅ Exists |
| **Report Renderer** | `render.py` | `render_phasea_report()` | ✅ Exists |
| **Run Orchestrator** | `run.py` | `run_analysis()` | ✅ Exists |
| **CLI** | `cli.py` | `main()`, `_build_parser()` | ✅ Exists |
| **OpenAI Client** | `openai_client.py` | `chat_json()`, `load_openai_config()` | ✅ Exists |
| **Stable Key** | — | — | ❌ MISSING |
| **Global Trap Library** | — | — | ❌ MISSING |
| **Run History** | — | — | ❌ MISSING |
| **Iteration Controller** | — | — | ❌ MISSING |
| **Regression Guard** | — | — | ❌ MISSING |
| **Adjudication (AI)** | — | — | ❌ MISSING |
| **Critique (AI)** | — | — | ❌ MISSING |
| **Prefilter** | — | — | ❌ MISSING |
| **Anomaly Detection** | — | — | ❌ MISSING |

---

## DELIVERABLE B — vNext Gap Analysis vs Codex PRD

| # | Requirement (from PRD §) | Status | Evidence (file:function) | Needed Changes |
|---|--------------------------|--------|--------------------------|----------------|
| **B1** | Stable key generation (§4 Step 2) | ❌ MISSING | No `stable_key` column anywhere | • Create `stable_key.py` with `generate_stable_key()` • Prefer SupplierURL+ASIN; fallback to hash of normalized fields • Add to `normalize_columns()` |
| **B2** | Stable key collision = HARD FAIL (§4 Step 2) | ❌ MISSING | No collision detection | • Add `check_stable_key_collisions()` • On collision: emit `stable_key_collisions.json` + block finalization |
| **B3** | Global trap library (§7.1) | ❌ MISSING | No `memory/global/trap_library.jsonl` | • Create file with default dimension/spec shields • Update `memory_store.py` to load global traps |
| **B4** | Supplier run_history.json (§7.2) | ❌ MISSING | No run history tracking | • Add `run_history.json` per supplier • Track `run_id`, `timestamp`, `input_file_hash`, artifact paths |
| **B5** | Layered precedence (§5 Step 5) | ⚠️ PARTIAL | `merge_calibration()` has overrides > existing > preflight > defaults | • Add global traps layer • Correct order: overrides > supplier traps > supplier calibration > global traps > defaults |
| **B6** | Iteration loop (§3.1, §4 Steps 6-12) | ❌ MISSING | Only single-pass in `run_analysis()` | • Create `iteration.py` with `run_iteration_loop()` • Implement iter_1 → critique → iter_2 → finalize logic |
| **B7** | AI Row Adjudication (§4 Step 8) | ❌ MISSING | No adjudication module | • Create `adjudication.py` • Candidate selection: pack/variant ambiguity, EAN missing, outliers, bucket flips • Cap: min(200, 5% of rows) • Strict JSON schema |
| **B8** | AI Report Critique (§4 Step 9) | ❌ MISSING | No critique module | • Create `critique.py` • Inputs: counts, validation, anomalies, samples, regression diff • Outputs: high_severity_issues[], proposed_changes[] |
| **B9** | Bounded adjustments (§4 Step 10) | ❌ MISSING | No adjustment application | • Create `adjustments.py` • Hard clamps on threshold changes, no schema drift |
| **B10** | Regression guard (§4 Step 11) | ❌ MISSING | No historical comparison | • Create `regression.py` • Compare vs previous iter + last K runs • Missing stable keys = HARD FAIL • Good-to-bad threshold: min(30, 10%) |
| **B11** | Draft vs Final promotion (§4 Step 12) | ❌ MISSING | All outputs treated as final | • Add iteration folder structure: `iter_1/`, `iter_2/`, `final/` • Only promote to `final/` if gates pass |
| **B12** | Prefilter (§4 Step 3) | ❌ MISSING | No internal prefiltering | • Create `prefilter.py` • Rules: Sales>0, NetProfit>0 (configurable) • Track `prefilter_excluded_count` |
| **B13** | Anomaly signals (§4 Step 6) | ❌ MISSING | No outlier/cluster detection | • Create `anomalies.py` • Profit/ROI outliers, weak-match clusters |
| **B14** | Provider flexibility (§6) | ⚠️ PARTIAL | `openai_client.py` + `moonshot.py` exist | • Create unified `providers/` module • Add Gemini support • Escalation logic (small → large) |
| **B15** | CLI vNext flags (§6, §3) | ⚠️ PARTIAL | Basic flags exist | • Add: `--max-iterations`, `--ai-row-cap`, `--history-k`, `--provider`, `--model-small`, `--model-large`, `--max-escalations` |
| **B16** | Output artifacts per iteration (§5) | ❌ MISSING | Single output folder | • Add `iter_N/` folders with: coverage_ledger.csv, evidence.jsonl, run_summary.json, regression_diff.json, critique.json, config_applied.json |
| **B17** | Report filename (§5 Final) | ⚠️ INCORRECT | Uses `CODEX_MANUAL_REPORT_{MMDDHHMM}.md` | • Change canonical to `PHASEA_MANUAL_REPORT_YYYYMMDD.md` per Main spec |
| **B18** | DRAFT_NOT_PASSED behavior (§3.3) | ❌ MISSING | Raises SystemExit on failure | • On gate failure after max iterations: produce `DRAFT — NOT PASSED` report + failure summary |
| **B19** | Persist calibration on failure (§1.1) | ❌ MISSING | Only persists on success | • Always persist calibration (even on failed runs) for diagnostics |
| **B20** | Acceptance tests (§8) | ❌ MISSING | No vNext-specific tests | • Add tests for stable_key, coverage, profit, regression, iteration selection |

---

## DELIVERABLE C — Phase 2 Implementation Plan (File-by-File)

### C.1 NEW FILES TO CREATE

| # | File Path | Purpose | Public Functions/Classes | Inputs | Outputs | Tests |
|---|-----------|---------|--------------------------|--------|---------|-------|
| **1** | `src/fba_agent/stable_key.py` | Stable key generation + collision detection | `generate_stable_key(row, df)`, `check_collisions(df)` | Row data, SupplierURL/ASIN/EAN/titles | 16-char hash, collision report | `tests/test_stable_key.py` |
| **2** | `src/fba_agent/prefilter.py` | Internal prefiltering | `apply_prefilter(df, rules)` | DataFrame, Rules dict | Filtered df, excluded_count, rules_used | `tests/test_prefilter.py` |
| **3** | `src/fba_agent/anomalies.py` | Outlier + cluster detection | `detect_anomalies(ledger, evidence)` | Ledger, Evidence | Anomaly summary (outliers, clusters) | `tests/test_anomalies.py` |
| **4** | `src/fba_agent/adjudication.py` | AI row adjudication | `select_candidates(ledger, evidence, cap)`, `run_adjudication(candidates, config)` | Ledger, Evidence, LLM config | Adjudication results (JSON) | `tests/test_adjudication.py` |
| **5** | `src/fba_agent/critique.py` | AI report critique | `build_critique_inputs(summary)`, `run_critique(inputs, config)` | Summary dict, LLM config | Critique results (JSON) | `tests/test_critique.py` |
| **6** | `src/fba_agent/adjustments.py` | Apply bounded adjustments | `apply_adjustments(config, proposals)`, `validate_proposal(proposal)` | Config, Proposals list | Updated config, applied log | `tests/test_adjustments.py` |
| **7** | `src/fba_agent/regression.py` | Regression guard | `compare_iterations(iter1, iter2)`, `compare_vs_history(current, history_k)`, `check_thresholds(diff)` | Ledger diffs, run_history | Regression report, justifications | `tests/test_regression.py` |
| **8** | `src/fba_agent/iteration.py` | Iteration loop controller | `run_iteration_loop(input_df, config, max_iterations)` | Normalized df, merged config, max_iter | Best iteration, all artifacts | `tests/test_iteration.py` |
| **9** | `src/fba_agent/providers/__init__.py` | Provider interface | `get_provider(name)`, `ProviderInterface` | Provider name | Provider instance | — |
| **10** | `src/fba_agent/providers/openai_provider.py` | OpenAI adapter | `OpenAIProvider.chat_json()`, `OpenAIProvider.escalate()` | Config, messages | Parsed JSON | — |
| **11** | `src/fba_agent/providers/gemini_provider.py` | Gemini adapter | `GeminiProvider.chat_json()` | Config, messages | Parsed JSON | — |
| **12** | `src/fba_agent/providers/moonshot_provider.py` | Moonshot adapter (refactor) | `MoonshotProvider.chat_json()` | Config, messages | Parsed JSON | — |
| **13** | `memory/global/trap_library.jsonl` | Global trap patterns | — | — | Trap patterns | — |
| **14** | `docs/spec_conflicts.md` | Spec conflict log | — | — | — | — |
| **15** | `tests/fba_agent/golden/` | Golden dataset | — | — | — | — |

### C.2 EXISTING FILES TO MODIFY

| # | File Path | Changes Required | Functions to Add/Modify |
|---|-----------|------------------|-------------------------|
| **1** | `src/fba_agent/io.py` | Add stable_key column generation | Modify `normalize_columns()` to call `generate_stable_key()` |
| **2** | `src/fba_agent/memory_store.py` | Add global trap loading + run_history | Add `load_global_traps()`, `load_run_history()`, `persist_run_history()`, update `merge_calibration()` for layered precedence |
| **3** | `src/fba_agent/run.py` | Replace one-shot with iteration loop | Refactor `run_analysis()` to call `run_iteration_loop()`, add iter folder structure, persist calibration on failure |
| **4** | `src/fba_agent/analysis.py` | Add stable_key reference, anomaly signals | Modify `analyze_all_rows()` to return anomaly signals, include stable_key in ledger |
| **5** | `src/fba_agent/validate.py` | Add stable_key coverage gate, formatting gate | Add `validate_stable_key_coverage()`, `validate_formatting()` |
| **6** | `src/fba_agent/render.py` | Add DRAFT vs FINAL stamping, fix filename | Add `render_draft_report()`, change canonical filename to `PHASEA_MANUAL_REPORT_YYYYMMDD.md` |
| **7** | `src/fba_agent/cli.py` | Add vNext CLI flags | Add: `--max-iterations`, `--ai-row-cap`, `--history-k`, `--provider`, `--model-small`, `--model-large`, `--max-escalations` |
| **8** | `src/fba_agent/types.py` | Add new dataclasses | Add `IterationResult`, `RegressionDiff`, `AdjudicationResult`, `CritiqueResult` |
| **9** | `src/fba_agent/constants.py` | Update default paths | Update `DEFAULT_RUNS_DIRNAME` if needed |

### C.3 IMPLEMENTATION ORDER (Phases)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 2a — FOUNDATION (stable_key, memory layers, types)                 │
├──────────────────────────────────────────────────────────────────────────┤
│ 1. types.py         — Add new dataclasses                                │
│ 2. stable_key.py    — Stable key generation + collision HARD FAIL        │
│ 3. io.py            — Integrate stable_key into normalize_columns()      │
│ 4. memory_store.py  — Add global traps, run_history, precedence fix      │
│ 5. memory/global/trap_library.jsonl — Seed with defaults                 │
│                                                                          │
│ CHECKPOINT: Run existing tests + verify stable_key generation            │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 2b — VALIDATION + ANALYSIS ENHANCEMENTS                           │
├──────────────────────────────────────────────────────────────────────────┤
│ 6. validate.py      — Add stable_key coverage, formatting gate          │
│ 7. prefilter.py     — Internal prefilter + tracking                     │
│ 8. anomalies.py     — Outlier + cluster detection                       │
│ 9. analysis.py      — Integrate anomaly signals, stable_key in ledger   │
│                                                                          │
│ CHECKPOINT: Run validation tests + verify anomaly detection             │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 2c — PROVIDERS + AI MODULES                                       │
├──────────────────────────────────────────────────────────────────────────┤
│ 10. providers/__init__.py   — Unified provider interface                │
│ 11. providers/openai_provider.py   — OpenAI adapter + escalation        │
│ 12. providers/gemini_provider.py   — Gemini adapter                      │
│ 13. providers/moonshot_provider.py — Refactor existing moonshot.py      │
│ 14. adjudication.py — Candidate selection + AI adjudication             │
│ 15. critique.py     — Report critique inputs + AI critique              │
│ 16. adjustments.py  — Bounded adjustment application                    │
│                                                                          │
│ CHECKPOINT: Test AI modules with mock responses                          │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 2d — ITERATION + REGRESSION                                       │
├──────────────────────────────────────────────────────────────────────────┤
│ 17. regression.py   — Regression guard + history comparison             │
│ 18. iteration.py    — Iteration loop controller                         │
│ 19. run.py          — Refactor to use iteration loop + iter folders     │
│ 20. render.py       — DRAFT vs FINAL stamping, fix filename             │
│                                                                          │
│ CHECKPOINT: Full pipeline test with 2 iterations                        │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 2e — CLI + TESTS + DOCS                                           │
├──────────────────────────────────────────────────────────────────────────┤
│ 21. cli.py          — Add vNext CLI flags                               │
│ 22. tests/          — Add all vNext tests + golden dataset              │
│ 23. docs/           — spec_conflicts.md, README updates                 │
│                                                                          │
│ CHECKPOINT: All tests pass + end-to-end validation                      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## DELIVERABLE D — Phase 2 Implementation Prompt

**⚠️ IMPORTANT:** The implementation prompt has been moved to a **self-contained file** that includes complete workflow context for use in a fresh chat session.

### File Location
📄 **`codex sgent/PHASE2_IMPLEMENTATION_PROMPT_SELFCONTAINED.md`**

### What the Self-Contained Prompt Includes

The prompt is designed to be pasted into a **FRESH chat with no prior context**. It contains:

1. ✅ **Complete explanation of what the FBA Agent does** (workflow purpose, bucket definitions)
2. ✅ **Current pipeline architecture** (6-step single-pass flow diagram)
3. ✅ **All existing files and their functions** (21 modules mapped)
4. ✅ **Authoritative spec hierarchy** (Main > Manual > Preflight with file paths)
5. ✅ **vNext upgrade summary** (iteration loop diagram, what's being added)
6. ✅ **Non-negotiables** (6 hard rules with full explanations)
7. ✅ **Target codebase paths** (exact Windows paths)
8. ✅ **Phase 2a complete implementation details** (code snippets included)
9. ✅ **Checkpoint instructions** (what to test after Phase 2a)
10. ✅ **Clear next steps** (explicit instruction to begin Phase 2a)

### To Use This Prompt

1. Open `codex sgent/PHASE2_IMPLEMENTATION_PROMPT_SELFCONTAINED.md`
2. Copy the **entire contents** of the file
3. Paste into a new chat session
4. The agent will begin implementing Phase 2a

---

## DELIVERABLE E — Open Questions (With Proposed Defaults)

| # | Question | Proposed Default | Blocking? |
|---|----------|------------------|-----------|
| Q1 | Coverage gate: RowID, stable_key, or BOTH? | **BOTH** (RowID for backward compat, stable_key for regression) | No (default set) |
| Q2 | Default prefilter rules | Sales > 0 AND NetProfit > 0 | No (default set) |
| Q3 | Default `--model-small` | `gpt-4o-mini` | No (default set) |
| Q4 | Default `--model-large` | `gpt-4o` | No (default set) |
| Q5 | Stable key fallback when SupplierURL missing | Use hash of (EAN_norm, ASIN, SupplierTitle[:50], AmazonTitle[:50]) | No (default set) |
| Q6 | Collision = HARD FAIL, no RowID disambiguation | **Confirmed per user instruction** | No (resolved) |
| Q7 | Canonical filename | `PHASEA_MANUAL_REPORT_YYYYMMDD.md` per Main spec | No (resolved) |

No blocking questions remain. All have proposed defaults.

---

## STOP — APPROVAL REQUIRED

**Phase 1 reconnaissance and planning is complete.**

I have:
1. ✅ Inspected the actual repository code at `src/fba_agent`
2. ✅ Inspected the docs/specs at `codex sgent`
3. ✅ Identified 21 existing modules + their functions
4. ✅ Produced gap analysis (20 requirements checked)
5. ✅ Created file-by-file implementation plan (15 new files, 9 files to modify)
6. ✅ Generated the exact Phase 2 Implementation Prompt
7. ✅ Resolved all open questions with defaults

**NO CODE CHANGES MADE IN THIS RESPONSE.**

---

**To proceed:**
1. Review this plan
2. Reply **"APPROVED"** to begin Phase 2 implementation
3. I will start with PHASE 2a and stop at each checkpoint for verification

---

**STOP — approval required.**
