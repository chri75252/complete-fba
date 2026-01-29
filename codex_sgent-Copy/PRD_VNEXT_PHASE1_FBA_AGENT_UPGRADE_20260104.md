# FBA Analysis Agent vNext — Phase 1 PRD / Tech Spec (Iteration + Regression Guard)

**Date:** 2026-01-04  
**Timezone:** Asia/Dubai (UTC+4)  
**Scope:** Phase 1 (plan only). No implementation in this document.

---

## 0) Authoritative specs (availability + mapping)

The prompt requires these mounted files:
- `/mnt/data/Main.txt`
- `/mnt/data/Manual analysis guide.md`
- `/mnt/data/Preflight.txt`
- `/mnt/data/PHASEA_MANUAL_REPORT_20260104.md`

**Audit finding:** Those `/mnt/data/*` paths are not present in this environment (Windows workspace).  
**Plan-time mapping used for this PRD (local equivalents):**
- Main spec (schema + validation + fixed-width table rules):  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md`
- Methodology guide (phases, traps, decision logic):  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md`
- Preflight calibration schema:  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md`
- Example report format target:  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\codex 1\PHASEA_MANUAL_REPORT_20260104.md`

**Conflict order:** Main > Methodology guide > Preflight.  
If conflicts are discovered during implementation, log them to `docs/spec_conflicts.md`.

---

## 1) Audit Notes (current repo state before changes)

### 1.1 Confirm preflight persistence (required)

**Loads prior supplier calibration:** YES  
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\memory_store.py` (`load_supplier_memory`)

**Runs new preflight on current sample:** YES  
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\run.py` (calls `run_preflight(sample)`)

**Merges deterministically with explicit precedence:** YES  
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\memory_store.py` (`merge_calibration`)  
- Precedence implemented: `overrides > existing calibration > preflight > defaults`

**Writes merged calibration back to disk:** PARTIALLY  
- `persist_calibration()` is called at end of successful run in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\run.py`.  
- **Gap:** when validation gates fail, calibration is not persisted; vNext requires persistence even for failed runs (so calibration drift and diagnostics are not lost).

### 1.2 Confirm “Filtered Out” semantics (required)

**Filtered Out / Excluded sections exist in the report:** YES  
The report renderer produces:
- VERIFIED - FILTERED OUT / EXCLUDED
- HIGHLY LIKELY - FILTERED OUT / EXCLUDED

This matches the Main spec’s requirement that FILTERED OUT contains confirmed matches excluded for reasons (pack/variant/profit), not “unrelated”.

**Explicit separation for “prefilter excluded” vs “filtered out (confirmed matches)”: NOT IMPLEMENTED**
- Current pipeline assumes inputs are already prefiltered (Main spec note: “input already filtered for NetProfit>0 and Sales>0”).
- **vNext requirement:** optionally ingest the full unfiltered report and apply prefiltering inside the agent, and record:
  - `prefilter_excluded_count`
  - `prefilter_rules_used`
  while still producing PhaseA tables from the remaining rows.

### 1.3 Confirm row coverage contract (required)

**Coverage contract for analyzed dataset:** YES  
- Every row is iterated in `analyze_all_rows()`  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\analysis.py`
- Coverage gate enforced by `validate_coverage()`  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\validate.py`
- Missing/duplicate RowIDs fail the run.

---

## 2) Problem to solve (why vNext)

Prompt-only runs drift and can mis-handle ambiguous cases. vNext must:
- keep deterministic spine for obvious cases (EAN strict match, clear pack, clear mismatch),
- use AI where it adds value:
  - ambiguous rows (pack/variant/EAN missing/weak match),
  - anomaly detection,
  - report critique,
  - iterative bounded corrections,
- protect against regressions via iteration diff + historical run comparison.

---

## 3) vNext system requirements (high-level)

### 3.1 Iteration loop (hard requirement)

Default `max_iterations = 2` (CLI: `--max-iterations 1..3`):
- Iter 1: baseline run (deterministic + preflight; minimal AI)
- Iter 2: refinement after critique + bounded adjustments

Never unbounded loops.

### 3.2 Trigger for Iteration 2

Run Iteration 2 if any of:
- Correctable gate failures (profit contradiction, formatting issues, etc.)
- Strong anomaly signals (extreme ROI/profit outliers, mismatch clusters)
- Regression guard flags drift vs history
- Critique proposes safe-to-apply bounded adjustments

### 3.3 Stop / finalize

Finalize when:
- Hard gates pass,
- Regression guard: not worse vs prior iteration and history beyond thresholds,
- Critique has no high severity unresolved issues.

If max iterations reached and issues remain:
- produce best-available report marked `DRAFT — NOT PASSED`,
- write failure summary + “what to verify manually”.

---

## 4) vNext pipeline (step-by-step with tools)

This section defines the runtime steps and what each step is (script vs AI).

### Step 0 — Load env + CLI args
- **Tool:** CLI entry `python -m fba_agent` → `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\cli.py`
- **Type:** Script

### Step 1 — Load full report
- **Tool:** `load_report()` in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent\io.py`
- **Type:** Script
- **Output:** raw dataframe + schema info

### Step 2 — Normalize + stable keys
- **Tool:** `normalize_columns()` + new `stable_key` builder (vNext)
- **Type:** Script
- **Stable key strategy (required):**
  - Prefer `SupplierURL` column if present (plus ASIN if needed)
  - Else hash of `(supplier_ean_norm, asin, supplier_title_norm, amazon_title_norm)`
- **Output:** normalized df with `RowID` + `stable_key`

### Step 3 — Optional internal prefilter (new)
- **Tool:** new `prefilter.apply(df, rules)` (vNext)
- **Type:** Script
- **Rules (default):** Sales>0 and NetProfit>0 (configurable)
- **Output:**
  - `df_analyzed` (rows to be analyzed for PhaseA)
  - `prefilter_excluded_count`
  - `prefilter_rules_used`

### Step 4 — Preflight calibration (existing; must be provider-flexible)
- **Tool:** `run_preflight(df_sample)` in `C:\...\src\fba_agent\preflight.py`
- **Type:** AI (small model) + deterministic fallback
- **Output:** calibration config + warnings

### Step 5 — Memory load/merge (must implement layered precedence)
- **Tool:** vNext expanded memory store:
  - supplier memory: `memory/suppliers/<supplier_id>/...`
  - global memory: `memory/global/trap_library.jsonl`
- **Type:** Script
- **Precedence (hard):**
  1) user overrides
  2) supplier traps/calibration
  3) global traps
  4) defaults

### Step 6 — Iteration N: deterministic draft analysis
- **Tool:** `analyze_all_rows()` (existing) expanded with:
  - stable_key in ledger
  - richer evidence flags
  - anomaly signals (profit/ROI outliers, weak match clusters)
- **Type:** Script
- **Output:** draft `coverage_ledger.csv`, `evidence.jsonl`

### Step 7 — Validation gates (hard)
- **Tool:** `validate_ledger()` (vNext)
- **Type:** Script
- **Hard gates:**
  - coverage by stable_key and RowID (no missing/duplicates)
  - profit contradiction: no VERIFIED/HIGHLY_LIKELY/NEEDS_VERIFICATION with AdjustedProfit <= 0
  - report/table formatting gate

### Step 8 — AI Step A: targeted row adjudication (new)
- **Tool:** `adjudication.select_candidates(ledger, evidence)` then `adjudication.run()` (vNext)
- **Type:** AI (small model), bounded and selective
- **Cap:** default `min(200, 5% of rows)` (CLI `--ai-row-cap`)
- **Candidate triggers:**
  - pack ambiguity
  - variant ambiguity within tolerance thresholds
  - EAN missing/invalid but title anchors strong
  - extreme profit/ROI outliers with weak match
  - rows that flip bucket between iterations or vs history
- **AI output schema (strict JSON):**
  - `stable_key`, `row_id`
  - extracted brand/product/variant/pack/capacity (supplier + amazon)
  - trap detections invoked
  - recommended bucket ∈ {VERIFIED, HIGHLY_LIKELY, NEEDS_VERIFICATION, FILTERED_OUT}
  - confidence suggestion (used only as a feature; deterministic scoring remains source of truth)

### Step 9 — AI Step B: report critique + bounded adjustment proposal (new)
- **Tool:** `critique.run(summary_inputs)` (vNext)
- **Type:** AI (small model)
- **Inputs:**
  - bucket counts
  - validation results
  - anomaly summary
  - sample rows (top confidence, top profit, random)
  - regression diff summary (vs prior iteration + history)
- **Outputs (strict JSON):**
  - `high_severity_issues[]` (each with stable_key/row_id)
  - `proposed_changes[]` restricted to safe categories and bounded ranges:
    - add dimension/spec shield tokens
    - add pack keyword mappings
    - tweak similarity threshold within bounded range
    - propose explicit overrides (only if `safe_to_apply=true`)

### Step 10 — Apply bounded adjustments (new)
- **Tool:** `adjustments.apply(config, proposals)` (vNext)
- **Type:** Script
- **Hard restrictions:**
  - no uncontrolled rewrites
  - no schema changes
  - no “wild” threshold expansion

### Step 11 — Regression guard vs history (new)
- **Tool:** `regression.compare(current, previous_iter, history_k)` (vNext)
- **Type:** Script
- **History:** `memory/suppliers/<supplier_id>/run_history.json` (required)
- **Metrics:**
  - missing stable keys (hard fail)
  - bucket transition matrix
  - good→bad transitions threshold: `min(30, 10% of previously-good)`
- **Justifications:** `REGRESSION_JUSTIFICATIONS.jsonl`

### Step 12 — Finalization and promotion
- **Tool:** `finalize.promote(iter_n)` (vNext)
- **Type:** Script
- **Rule:** do not produce “final” report unless gates + regression + critique pass.

---

## 5) Output artifacts (required expansion)

Run directory:
- `codex sgent/AGENT REPORT/<run_id>/`
  - `iter_1/`
  - `iter_2/` (if used)
  - `final/`

Per iteration:
- `coverage_ledger.csv` (must include `stable_key`)
- `evidence.jsonl`
- `run_summary.json`
- `regression_diff.json` (vs prior iteration)
- `critique.json`
- `config_applied.json`

Final:
- `PHASEA_MANUAL_REPORT_YYYYMMDD.md` (Main spec structure)
- `FINAL_SUMMARY.md`
- `REGRESSION_JUSTIFICATIONS.jsonl`

---

## 6) Provider + model strategy (vNext)

### 6.1 Provider selection
CLI: `--provider openai|gemini|moonshot`  
Env vars:
- OpenAI: `OPENAI_API_KEY` (+ optional `OPENAI_BASE_URL`)
- Gemini: `GEMINI_API_KEY` (+ configured base URL for OpenAI-compat if used)
- Moonshot: `MOONSHOT_API_KEY` + base URL `https://api.moonshot.ai/v1`

### 6.2 Model selection + escalation
CLI:
- `--model-small <name>`
- `--model-large <name>`
- `--max-escalations <n>`

Defaults (example; must remain configurable):
- small: `gpt-5-mini`
- large: `gpt-5` (or whichever you configure)

Escalate to large only when:
- JSON schema fails twice,
- ambiguity persists after adjudication,
- critique marks an issue high severity.

---

## 7) Memory layout (required)

### 7.1 Global memory (new)
- `memory/global/trap_library.jsonl`

### 7.2 Supplier memory (expand)
- `memory/suppliers/<supplier_id>/calibration.json`
- `memory/suppliers/<supplier_id>/trap_library.jsonl`
- `memory/suppliers/<supplier_id>/overrides.jsonl`
- `memory/suppliers/<supplier_id>/run_history.json`

Runtime precedence:
1) overrides
2) supplier traps/calibration
3) global traps
4) defaults

---

## 8) Acceptance tests (required)

Add automated tests for:
- stable_key generation
- coverage gate correctness (RowID and stable_key)
- profit contradiction gate (no positive buckets with AdjustedProfit <= 0)
- trap shields: dimensions/spec-x/LED not misread as pack
- iteration selection: final iteration must be best per regression guard
- historical diff: detect missing stable keys

Golden dataset fixture (50–100 rows) with expected outcomes.

---

## 9) Implementation checklist (Phase 2 only; file-by-file)

### Modify existing
- `src/fba_agent/run.py`: implement iter loop + iter_#/final promotion + write configs/critique/regression outputs
- `src/fba_agent/analysis.py`: add stable_key, anomaly signals, adjudication hooks, structured evidence references
- `src/fba_agent/validate.py`: add formatting gate + stable_key coverage + profit contradiction auto-fix or iteration trigger
- `src/fba_agent/memory_store.py`: add global traps + run_history.json read/write + strict precedence
- `src/fba_agent/render.py`: draft vs final stamping; ensure Main schema and fixed-width rules always applied
- `src/fba_agent/cli.py`: flags `--max-iterations`, `--ai-row-cap`, `--history-k`, `--provider`, `--model-small`, `--model-large`, `--max-escalations`

### Add new modules
- `src/fba_agent/stable_key.py`: stable key builder + normalization helpers
- `src/fba_agent/prefilter.py`: internal prefilter + summary outputs
- `src/fba_agent/anomalies.py`: outlier detection + mismatch clusters
- `src/fba_agent/adjudication.py`: candidate selection + strict JSON parsing + bounded application
- `src/fba_agent/critique.py`: critique inputs builder + strict JSON parsing
- `src/fba_agent/adjustments.py`: apply bounded adjustments with hard clamps
- `src/fba_agent/regression.py`: diff logic + transition matrix + thresholds + justifications output
- `src/fba_agent/providers/*.py`: provider adapters (OpenAI/Gemini/Moonshot) behind a single interface

### Docs
- `docs/spec_conflicts.md`: record spec conflicts (Main > Manual > Preflight)
- `docs/fba_agent/README.md`: document provider setup + new CLI + iteration artifacts

### Tests
- `tests/fba_agent/test_stable_key.py`
- `tests/fba_agent/test_iteration_selection.py`
- `tests/fba_agent/test_regression_guard.py`
- `tests/fba_agent/test_prefilter_semantics.py`
- Add golden dataset under `tests/fba_agent/golden/`

---

## STOP — Approval required

Approve Phase 2 implementation? If yes, confirm:
1) Do you want `RowID` coverage, `stable_key` coverage, or BOTH as hard gates?
2) What are your default prefilter rules (Sales>0 and NetProfit>0, or something else)?
3) Default provider/models for `--model-small` and `--model-large`.

