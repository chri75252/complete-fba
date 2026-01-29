# FBA Analysis Agent — Complete Workflow Documentation

**Version:** vNext (with Iteration Loop)  
**Date:** 2026-01-05  
**Purpose:** Detailed step-by-step workflow with tool types and data interpretation

---

## WORKFLOW OVERVIEW

The FBA Analysis Agent processes supplier product data to identify profitable Amazon FBA resale opportunities. The vNext workflow operates in **iterative mode** (max 2-3 passes) to refine results.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        FBA ANALYSIS AGENT WORKFLOW (vNext)                          │
│                                                                                     │
│  INPUT: Supplier CSV/XLSX → PROCESS: Iterative Analysis → OUTPUT: PhaseA Report    │
└─────────────────────────────────────────────────────────────────────────────────────┘

STEP 0: CLI Entry Point ────────────────────────── [SCRIPT]
STEP 1: Load & Normalize Data ──────────────────── [SCRIPT]
STEP 2: Generate Stable Keys ───────────────────── [SCRIPT]
STEP 3: Optional Pre-filter ────────────────────── [SCRIPT]
STEP 4: Preflight Calibration ──────────────────── [LLM + SCRIPT FALLBACK]
STEP 5: Memory Load & Merge ────────────────────── [SCRIPT]
                    │
            ╔═══════╧═══════╗
            ║ ITERATION LOOP ║ (max 2-3 times)
            ╚═══════╤═══════╝
                    │
STEP 6: Row Analysis (Deterministic) ───────────── [SCRIPT]
STEP 7: Validation Gates ───────────────────────── [SCRIPT]
STEP 8: AI Row Adjudication (Ambiguous Rows) ───── [LLM — BOUNDED]
STEP 9: AI Report Critique ─────────────────────── [LLM — BOUNDED]
STEP 10: Apply Bounded Adjustments ─────────────── [SCRIPT]
STEP 11: Decision: Run Another Iteration? ──────── [SCRIPT]
                    │
            ╔═══════╧═══════╗
            ║ EXIT ITERATION ║
            ╚═══════╤═══════╝
                    │
STEP 12: Regression Guard ──────────────────────── [SCRIPT]
STEP 13: Finalization & Output ─────────────────── [SCRIPT]
STEP 14: Memory Persistence ────────────────────── [SCRIPT]
```

---

## DETAILED STEP-BY-STEP BREAKDOWN

---

### STEP 0: CLI Entry Point

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/cli.py` |
| **Function** | `main()` |
| **AI Used** | ❌ No |

**What happens:**
- User invokes: `python -m fba_agent analyze --input path/to/report.xlsx --supplier "SupplierName"`
- CLI parses arguments: input file, supplier name, max iterations, AI settings
- Calls `run_analysis()` to start the pipeline

**Data Interpretation:**
- `--input`: Path to supplier financial report (CSV/XLSX)
- `--supplier`: Supplier identifier (used for memory lookup)
- `--max-iterations`: How many refinement passes (default: 2)
- `--skip-browser`: Whether to skip live Amazon page checks (default: true)

---

### STEP 1: Load & Normalize Data

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/io.py` |
| **Functions** | `load_report()`, `normalize_columns()` |
| **AI Used** | ❌ No |

**What happens:**
1. Load CSV/XLSX file into pandas DataFrame
2. Detect column names (case-insensitive matching)
3. Generate `RowID` for each row (1-indexed)
4. Normalize text fields (sanitize pipes, quotes)
5. Parse financial values (remove £, commas)
6. Extract EAN values from various formats

**Data Interpretation:**

| Input Column | Normalized Column | Processing |
|--------------|-------------------|------------|
| `SupplierTitle`, `Supplier Title` | `SupplierTitle` | Text cleanup, sanitization |
| `AmazonTitle`, `Amazon Title` | `AmazonTitle` | Text cleanup, sanitization |
| `EAN`, `Supplier EAN` | `SupplierEAN_raw` | Raw value preserved |
| `EAN_OnPage`, `Amazon EAN` | `AmazonEAN_raw` | Raw value preserved |
| `ASIN` | `ASIN` | Uppercase, trimmed |
| `NetProfit` | `NetProfit` | Parsed to float |
| `Sales`, `bought_in_past_month` | `Sales` | Parsed to numeric |
| `SellingPrice_incVAT` | `SellingPrice` | Parsed to float |
| `SupplierPrice_incVAT` | `SupplierPrice` | Parsed to float |
| `ROI` | `ROI` | Parsed to percentage |

---

### STEP 2: Generate Stable Keys

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/stable_key.py` (NEW) |
| **Functions** | `generate_stable_key()`, `check_collisions()` |
| **AI Used** | ❌ No |

**What happens:**
1. For each row, generate a deterministic 16-character hash
2. Primary strategy: `sha256(SupplierURL + ASIN)[:16]`
3. Fallback (no URL): `sha256(EAN + ASIN + SupplierTitle[:50] + AmazonTitle[:50])[:16]`
4. Check for collisions (duplicate keys)
5. If collision → **HARD FAIL** + emit collision report

**Data Interpretation:**
- `stable_key` enables cross-run comparison (regression detection)
- Same product across runs should have same stable_key
- Collision = data quality issue requiring manual fix

**Output:** Each row now has a `stable_key` column

---

### STEP 3: Optional Pre-filter

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/prefilter.py` (NEW) |
| **Function** | `apply_prefilter()` |
| **AI Used** | ❌ No |

**What happens:**
1. Apply configurable filter rules to exclude obviously unprofitable rows
2. Default rules: `Sales > 0` AND `NetProfit > 0`
3. Track excluded rows separately (not lost, just pre-filtered)

**Data Interpretation:**
- Pre-filter removes rows that have zero/negative profit BEFORE pack analysis
- These are tracked as `prefilter_excluded_count`, NOT as FILTERED_OUT
- FILTERED_OUT = confirmed match excluded for reason (different concept)

**Output:**
- `df_to_analyze`: Rows to process through analysis
- `prefilter_excluded_count`: Number excluded
- `prefilter_rules_applied`: Which rules triggered

---

### STEP 4: Preflight Calibration

| Attribute | Value |
|-----------|-------|
| **Tool Type** | 🤖 **LLM** (with Script Fallback) |
| **File** | `src/fba_agent/preflight.py` |
| **Functions** | `run_preflight()`, `_heuristic_preflight()` |
| **AI Used** | ✅ Yes — Small Model (gpt-4o-mini or equivalent) |

**What happens:**
1. Sample 50 rows from the dataset
2. Send sample to LLM with calibration prompt
3. LLM analyzes patterns and returns JSON configuration:
   - `explicit_units`: Pack quantity keywords (e.g., ["pce", "pcs", "pk"])
   - `dimension_shield_keywords`: Words to NOT interpret as pack (e.g., ["cm", "mm", "inch"])
   - `spec_x_shield_keywords`: Spec patterns to shield (e.g., ["magnification", "zoom"])
   - `brand_position`: Where brand appears in title ("start" or "mixed")
   - `sales_column`: Which column contains sales data
   - `capacity_pattern_as_rsu`: Whether "3x500ml" means RSU=3
4. If LLM fails or no API key → fallback to heuristic detection

**LLM Prompt (simplified):**
```
Analyze these 50 sample rows and output JSON with:
- explicit_units: list of unit keywords found
- dimension_shield_keywords: measurement words to shield
- brand_position: "start" or "mixed"
- sales_column: detected column name
...
Return ONLY valid JSON.
```

**Data Interpretation:**
- LLM detects supplier-specific naming patterns
- These patterns customize how we parse pack quantities
- Example: Supplier A uses "Pk 6" but Supplier B uses "Pack of 6"

**Output:** `SupplierNamingConvention` dataclass with all calibration settings

---

### STEP 5: Memory Load & Merge

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/memory_store.py` |
| **Functions** | `load_supplier_memory()`, `load_global_traps()`, `merge_calibration()` |
| **AI Used** | ❌ No |

**What happens:**
1. Load global trap library: `memory/global/trap_library.jsonl`
2. Load supplier-specific memory: `memory/suppliers/{supplier_id}/`
   - `calibration.json`: Previous preflight results
   - `trap_library.jsonl`: Supplier-specific traps
   - `overrides.jsonl`: User-approved overrides
   - `run_history.json`: Previous run summaries
3. Merge with strict precedence order

**Memory Precedence (highest → lowest):**
```
1. User Overrides         ← Explicit row/rule corrections
2. Supplier Traps         ← Learned trap patterns for this supplier
3. Supplier Calibration   ← Merged preflight output for this supplier
4. Global Trap Library    ← Universal shields (dimension, spec-x, LED)
5. Defaults               ← Hardcoded fallbacks
```

**Data Interpretation:**
- Memory allows the agent to "learn" from previous runs
- Fixed false positives persist as overrides
- Supplier-specific patterns don't need re-detection

**Output:** `MergedConfig` with all settings ready for analysis

---

## ITERATION LOOP BEGINS HERE

The following steps (6-11) execute inside the iteration loop (max 2-3 times).

---

### STEP 6: Row Analysis (Deterministic Core)

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) — **DETERMINISTIC** |
| **File** | `src/fba_agent/analysis.py` |
| **Functions** | `analyze_all_rows()`, `analyze_row()` |
| **AI Used** | ❌ No — This is the **deterministic spine** |

**What happens for EACH ROW:**

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ ROW ANALYSIS PIPELINE (per row)                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

A. EAN VALIDATION
   ├── Normalize EAN (strip spaces, handle scientific notation)
   ├── Left-pad to 12/13/14 digits if needed
   ├── Validate GTIN checksum
   └── Output: supplier_ean_valid, amazon_ean_valid, strict_exact_ean_match

B. TITLE PARSING
   ├── Extract brand from SupplierTitle (first token or mixed)
   ├── Extract brand from AmazonTitle
   ├── Extract product tokens (exclude stopwords)
   └── Output: brand_match, product_type_match, jaccard_similarity

C. PACK QUANTITY DETECTION (with Trap Shields)
   ├── Check dimension shields: "150x50mm" → NOT a pack
   ├── Check spec-x shields: "10x magnification" → NOT a pack
   ├── Check LED spec: "48 LED" → NOT a pack
   ├── Parse Supplier pack: "Pack of 6" → 6
   ├── Parse Amazon pack: "3x500ml" → 3 (if capacity_pattern_as_rsu)
   └── Output: supplier_pack_qty, amazon_pack_qty, pack_verdict

D. PROFIT CALCULATION
   ├── Calculate pack_ratio: amazon_pack / supplier_pack
   ├── Calculate RSU (Required Supplier Units): pack_ratio rounded up
   ├── Calculate adjusted_profit: original_profit / RSU
   └── Output: adjusted_profit, rsu, pack_ratio

E. BUCKET ASSIGNMENT (Decision Tree)
   ├── If EAN exact match + profit > 0 → VERIFIED
   ├── If brand + product match + profit > 0 → HIGHLY_LIKELY
   ├── If partial match or ambiguous → NEEDS_VERIFICATION
   ├── If confirmed match but profit ≤ 0 → FILTERED_OUT
   └── If no match at all → UNRELATED

F. CONFIDENCE SCORING
   ├── Start at 50
   ├── +30 if EAN exact match
   ├── +20 if brand match
   ├── +10 if product type match
   ├── -20 if pack mismatch detected
   ├── -10 per trap detected
   └── Output: confidence (0-100)
```

**Data Interpretation (Bucket Definitions):**

| Bucket | Meaning | In Report? |
|--------|---------|------------|
| **VERIFIED** | Exact EAN match, brand match, pack OK, profit > 0 → **BUY** | ✅ Yes (Table) |
| **HIGHLY_LIKELY** | Strong brand/product match, profit > 0 → **Likely BUY** | ✅ Yes (Table) |
| **NEEDS_VERIFICATION** | Ambiguous signals → **Manual review required** | ✅ Yes (Table) |
| **FILTERED_OUT** | Confirmed match but excluded (pack issue, profit ≤ 0) → **Do NOT buy** | ✅ Yes (Table) |
| **UNRELATED** | Completely different products → **Ignore** | ❌ Count only |

**Output:**
- `coverage_ledger.csv`: All rows with bucket, confidence, evidence
- `evidence.jsonl`: Detailed decision trace per row

---

### STEP 7: Validation Gates

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/validate.py` |
| **Functions** | `validate_coverage()`, `validate_profit()`, `validate_stable_key_coverage()` |
| **AI Used** | ❌ No |

**What happens:**

| Gate | Check | Consequence if Failed |
|------|-------|----------------------|
| **Coverage Gate** | Every RowID appears exactly once | HARD FAIL (missing rows = bug) |
| **Stable Key Gate** | Every stable_key appears exactly once | HARD FAIL (collision = data issue) |
| **Profit Gate** | No VERIFIED/HIGHLY_LIKELY with adjusted_profit ≤ 0 | HARD FAIL (those rows should be FILTERED_OUT) |
| **Format Gate** | All table columns present, fixed-width alignment | SOFT FAIL (can be auto-fixed) |

**Data Interpretation:**
- Gates ensure data integrity and report correctness
- HARD FAIL = triggers another iteration (if possible) or blocks finalization
- All gates must pass before producing "final" report

---

### STEP 8: AI Row Adjudication (Ambiguous Rows Only)

| Attribute | Value |
|-----------|-------|
| **Tool Type** | 🤖 **LLM** — Bounded & Selective |
| **File** | `src/fba_agent/adjudication.py` (NEW) |
| **Functions** | `select_candidates()`, `run_adjudication()` |
| **AI Used** | ✅ Yes — Small Model, **CAPPED** |

**What happens:**
1. Select candidate rows for AI review (NOT all rows):
   - Pack verdict = "uncertain" or "ambiguous"
   - Variant match = "ambiguous"
   - EAN missing but title match > 70%
   - High profit outlier (> £20) with weak match (< 70%)
   - Row flipped bucket vs previous iteration
2. CAP: Only review `min(200, 5% of total rows)`
3. For each candidate, send to LLM with structured prompt
4. Parse strict JSON response

**LLM Input (per row):**
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

**LLM Output (strict JSON):**
```json
{
  "row_id": 123,
  "extracted_signals": {
    "supplier_brand": "AMTECH",
    "amazon_brand": "Amtech",
    "brand_match": true,
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

**Data Interpretation:**
- LLM provides **suggestions**, not final decisions
- Deterministic scoring remains authoritative
- `confidence_suggestion` is a signal, not the final score
- If LLM recommends VERIFIED but deterministic scoring disagrees → deterministic wins

---

### STEP 9: AI Report Critique

| Attribute | Value |
|-----------|-------|
| **Tool Type** | 🤖 **LLM** — Bounded |
| **File** | `src/fba_agent/critique.py` (NEW) |
| **Functions** | `build_critique_inputs()`, `run_critique()` |
| **AI Used** | ✅ Yes — Small Model |

**What happens:**
1. Build summary inputs:
   - Bucket counts (VERIFIED: N, HIGHLY_LIKELY: M, etc.)
   - Validation results
   - Anomaly summary (outliers, clusters)
   - Sample rows (10 per bucket + top profit + top confidence)
   - Regression diff vs previous iteration
2. Send to LLM for holistic review
3. Parse strict JSON response

**LLM Output (strict JSON):**
```json
{
  "high_severity_issues": [
    {
      "issue_id": "HSI_001",
      "description": "3 rows with RSU>10 have no dimension trap despite '9x9 inch' patterns",
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

**Data Interpretation:**
- Critique reviews the report as a whole, not individual rows
- Identifies systemic issues (e.g., missing trap patterns)
- Proposes bounded adjustments (never unbounded rewrites)
- `safe_to_apply=true` means can be auto-applied; otherwise requires confirmation

---

### STEP 10: Apply Bounded Adjustments

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/adjustments.py` (NEW) |
| **Functions** | `validate_proposal()`, `apply_adjustments()` |
| **AI Used** | ❌ No |

**What happens:**
1. For each proposed change from critique:
   - Validate it's within allowed bounds
   - Add shield token? ✅ Allowed
   - Add pack keyword? ✅ Allowed
   - Adjust threshold by ±5 points? ⚠️ Requires flag
   - Rewrite report? ❌ NEVER allowed
2. Apply safe changes to config
3. Log all applied adjustments

**Bounded Change Types:**

| Change Type | Auto-Apply? | Example |
|-------------|-------------|---------|
| `add_shield_token` | ✅ Yes | Add "inch" to dimension_shield_keywords |
| `add_pack_keyword` | ✅ Yes | Add "packet" to pack detection |
| `add_brand_alias` | ✅ Yes | Map "AMZN" → "Amazon" |
| `adjust_threshold` | ⚠️ Bounded | Change title_match from 0.22 to 0.25 |
| `add_override` | ❌ Manual | Requires explicit user approval |

**Output:** Updated `MergedConfig` ready for next iteration

---

### STEP 11: Decision — Run Another Iteration?

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/iteration.py` (NEW) |
| **Function** | `should_run_next_iteration()` |
| **AI Used** | ❌ No |

**What happens:**

```
DECISION TREE: Run Iteration N+1?
                    │
    ┌───────────────┴───────────────┐
    │ Already at max_iterations?    │
    └───────────────┬───────────────┘
           YES ─────┤───── NO
            │       │
            ▼       ▼
         STOP    Continue checking...
                    │
    ┌───────────────┴───────────────┐
    │ Any correctable gate failure? │
    └───────────────┬───────────────┘
           YES ─────┤───── NO
            │       │
            ▼       ▼
         RUN N+1  Continue checking...
                    │
    ┌───────────────┴───────────────┐
    │ Critique has safe_to_apply    │
    │ changes AND recommended_action│
    │ = "apply_and_rerun"?          │
    └───────────────┬───────────────┘
           YES ─────┤───── NO
            │       │
            ▼       ▼
         RUN N+1  Continue checking...
                    │
    ┌───────────────┴───────────────┐
    │ Large anomaly signals?        │
    │ (>10 outliers, >5% flip)      │
    └───────────────┬───────────────┘
           YES ─────┤───── NO
            │       │
            ▼       ▼
         RUN N+1    STOP (Finalize)
```

**Output:** Boolean — whether to run another iteration

---

## ITERATION LOOP ENDS — POST-PROCESSING

---

### STEP 12: Regression Guard

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/regression.py` (NEW) |
| **Functions** | `compare_iterations()`, `compare_vs_history()`, `check_thresholds()` |
| **AI Used** | ❌ No |

**What happens:**
1. Compare final iteration vs iteration 1 (iteration diff)
2. Compare final iteration vs last K historical runs (historical diff)
3. Check thresholds:

| Check | Threshold | Consequence |
|-------|-----------|-------------|
| Missing stable keys vs history | Any | **HARD BLOCK** |
| Good-to-bad transitions | > 10% of previously-good OR > 30 rows | **BLOCK** unless justified |
| Bad-to-good transitions | Any | OK (improvement) |

4. If blocked → require justification OR produce DRAFT report

**Data Interpretation:**
- Regression guard prevents output from getting worse
- "Good" buckets: VERIFIED, HIGHLY_LIKELY
- "Bad" buckets: NEEDS_VERIFICATION, FILTERED_OUT, UNRELATED
- Missing stable key = row that existed before is now gone (data loss)

**Output:**
- `RegressionDiff` with transition matrix
- `regression_justifications.jsonl` if exceptions approved

---

### STEP 13: Finalization & Output

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/render.py`, `src/fba_agent/run.py` |
| **Functions** | `render_phasea_report()`, `render_draft_report()` |
| **AI Used** | ❌ No |

**What happens:**

**If ALL gates pass + regression OK:**
1. Promote winning iteration to `final/` folder
2. Generate `PHASEA_MANUAL_REPORT_YYYYMMDD.md` (canonical)
3. Generate `PHASEA_MANUAL_REPORT_YYYYMMDD_HHMM.md` (timestamped archive)
4. Write final artifacts:
   - `coverage_ledger.csv`
   - `evidence.jsonl`
   - `run_summary.json`
   - `FINAL_SUMMARY.md`
   - `REGRESSION_JUSTIFICATIONS.jsonl`

**If blocked (gates failed / regression blocked):**
1. Generate `DRAFT_NOT_PASSED_YYYYMMDD.md` with:
   - "⚠️ DRAFT — NOT PASSED" header
   - Which gates failed
   - "What to verify manually" section
2. Do NOT promote to final

**Report Structure:**
```markdown
# PHASEA MANUAL REPORT

**Generated:** 2026-01-05
**Input File:** part_4_jan.xlsx
**Supplier:** efghousewares_co_uk

## Summary Counts
- VERIFIED - RECOMMENDED: 12
- VERIFIED - FILTERED OUT / EXCLUDED: 3
- HIGHLY LIKELY - RECOMMENDED: 28
- HIGHLY LIKELY - FILTERED OUT / EXCLUDED: 5
- NEEDS VERIFICATION: 45
- UNRELATED / NOT INCLUDED: 892
- **TOTAL ANALYZED: 985**

## VERIFIED - RECOMMENDED (count=12)
[Fixed-width table with all columns]

## VERIFIED - FILTERED OUT / EXCLUDED (count=3)
[Fixed-width table]

...
```

---

### STEP 14: Memory Persistence

| Attribute | Value |
|-----------|-------|
| **Tool Type** | Script (Python) |
| **File** | `src/fba_agent/memory_store.py` |
| **Functions** | `persist_calibration()`, `persist_run_history()` |
| **AI Used** | ❌ No |

**What happens:**
1. Save merged calibration to `memory/suppliers/{id}/calibration.json`
2. Append run entry to `memory/suppliers/{id}/run_history.json`:
   ```json
   {
     "run_id": "20260105_123456",
     "timestamp": "2026-01-05T12:34:56",
     "input_file": "part_4_jan.xlsx",
     "input_file_hash": "abc123...",
     "bucket_counts": {"VERIFIED": 12, "HIGHLY_LIKELY": 28, ...},
     "gates_passed": true,
     "artifacts_path": "AGENT REPORT/20260105_123456/final/"
   }
   ```
3. If new traps discovered → append to `trap_library.jsonl`
4. Persist even on failure (for diagnostics)

---

## SUMMARY: AI vs SCRIPT BREAKDOWN

| Step | Tool Type | AI Model | Purpose |
|------|-----------|----------|---------|
| 0. CLI Entry | Script | — | Parse arguments, start pipeline |
| 1. Load & Normalize | Script | — | Read file, normalize columns |
| 2. Stable Keys | Script | — | Generate cross-run identifiers |
| 3. Pre-filter | Script | — | Exclude obviously unprofitable rows |
| 4. Preflight Calibration | **LLM** | Small (gpt-4o-mini) | Detect supplier patterns |
| 5. Memory Merge | Script | — | Load + merge config layers |
| 6. Row Analysis | **Script** | — | **DETERMINISTIC CORE** |
| 7. Validation Gates | Script | — | Check data integrity |
| 8. Row Adjudication | **LLM** | Small (gpt-4o-mini) | Review ambiguous rows (capped) |
| 9. Report Critique | **LLM** | Small (gpt-4o-mini) | Holistic review + propose changes |
| 10. Apply Adjustments | Script | — | Apply bounded config changes |
| 11. Iteration Decision | Script | — | Decide if another pass needed |
| 12. Regression Guard | Script | — | Prevent quality regression |
| 13. Finalization | Script | — | Generate report + artifacts |
| 14. Memory Persistence | Script | — | Save state for next run |

**AI Usage Summary:**
- **3 steps use AI:** Steps 4, 8, 9
- **AI is always bounded:** Capped rows, strict JSON schemas, suggestions only
- **Deterministic spine is authoritative:** AI cannot override final bucket assignments

---

## KEY INVARIANTS (NEVER VIOLATED)

1. **Every row gets a bucket** — No row is lost or uncategorized
2. **Stable key collision = HARD FAIL** — No disambiguation via RowID
3. **AI is bounded** — Max 200 rows adjudicated, suggestions only
4. **Deterministic scoring wins** — AI confidence is a signal, not final
5. **FILTERED OUT printed, UNRELATED count-only** — Clear distinction
6. **Profit ≤ 0 → FILTERED OUT** — Never in positive buckets
7. **Regression guard protects quality** — No worse than before
8. **Memory persists learning** — Patterns survive across runs
