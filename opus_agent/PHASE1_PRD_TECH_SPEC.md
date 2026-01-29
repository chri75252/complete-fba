# 📋 PHASE 1: PRD / TECHNICAL SPECIFICATION
## FBA Product Analysis Agent (Kimi/Moonshot + OpenAI Agents SDK)

**Version:** 1.0  
**Created:** 2026-01-04 (Asia/Dubai)  
**Author:** Agent System Architect  
**Status:** AWAITING APPROVAL

---

## 📑 TABLE OF CONTENTS

1. [Problem Statement & Constraints](#1-problem-statement--constraints)
2. [User Stories](#2-user-stories)
3. [Detailed Pipeline Flow](#3-detailed-pipeline-flow)
4. [Tool Contracts & Data Schemas](#4-tool-contracts--data-schemas)
5. [Deterministic Scoring Rubric](#5-deterministic-scoring-rubric)
6. [Memory / Learning Design](#6-memory--learning-design)
7. [UI Plan](#7-ui-plan)
8. [Validation Gates & Failure Handling](#8-validation-gates--failure-handling)
9. [Test Plan & Evaluation Dataset](#9-test-plan--evaluation-dataset)
10. [Implementation Milestones](#10-implementation-milestones)
11. [Risks & Mitigations](#11-risks--mitigations)
12. [Conflict Resolution Log](#12-conflict-resolution-log)
13. [Approval Request](#13-approval-request)

---

## 1. PROBLEM STATEMENT & CONSTRAINTS

### 1.1 Why Prompt-Only Execution Is Inconsistent

The current workflow relies on providing detailed prompts (Preflight Calibration + Main Prompt v4.1 AG1 + Manual Methodology Guide) to an LLM in separate chat sessions. This approach produces **inconsistent results**:

| Problem | Symptom | Root Cause |
|---------|---------|------------|
| **Missing Rows** | Some RowIDs are silently skipped | LLM truncation, context limits, or early termination |
| **Score Drift** | Same product gets 85 in one session, 72 in another | Scores computed via "LLM vibes" not deterministic rules |
| **Trap Inconsistency** | Sometimes `9x9 inch` is treated as pack, sometimes as dimension | No persistent trap library; LLM "forgets" between chats |
| **Pack Logic Errors** | `(4 x 50)` sometimes → RSU=4, sometimes → RSU=1 | No code-enforced multipack parsing |
| **Calibration Loss** | Previous preflight config isn't carried forward | No supplier memory between sessions |

### 1.2 What This Agent Solves

By shifting from **prompt-only reasoning** to a **tool-driven deterministic pipeline**, we achieve:

- **100% Row Coverage:** Code iterates over every RowID; no LLM truncation possible
- **Deterministic Scoring:** Scores computed by fixed rubric in code, not LLM estimation
- **Persistent Learning:** Supplier calibration, trap patterns, and overrides stored on disk
- **Audit Artifacts:** Coverage ledger + evidence JSONL enable post-run verification

### 1.3 Hard Constraints (Non-Negotiable)

| Constraint | Enforcement |
|------------|-------------|
| Every RowID ends in exactly one bucket | `validate_ledger()` fails if any RowID missing or duplicated |
| Score differences across runs minimized | Scoring is code-driven formula; LLM only provides reasoning summaries |
| Browser verification OFF by default | Tool interface stubbed; `--skip-browser true` is default |
| Output matches Main.txt requirements | `render_phasea_report()` uses exact table schema + fixed-width formatting |

### 1.4 Authoritative Specification Hierarchy

Per the BUILD PROMPT, conflicts are resolved in this order:

1. **Main.txt** (FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md) — highest authority
2. **Manual analysis guide.md** (FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md)
3. **Preflight.txt** (AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md)

---

## 2. USER STORIES

### 2.1 Primary User Stories

| ID | As a... | I want to... | So that... | Acceptance Criteria |
|----|---------|--------------|------------|---------------------|
| US-1 | Seller | Run analysis on a new supplier file | I get a complete PhaseA report with all rows categorized | `coverage_ledger.csv` has exactly N rows; no missing RowIDs |
| US-2 | Seller | See top candidates sorted by confidence | I know which products to prioritize | `top` command returns items filtered by `--min-confidence` |
| US-3 | Seller | Explain why a specific row was categorized | I understand the decision logic | `explain` command returns full evidence record for RowID |
| US-4 | Seller | Export results in different formats | I can use data in Excel or other tools | `export` supports md, csv, json |
| US-5 | Seller | Rerun with manual overrides applied | I can correct agent mistakes and reprocess | `rerun --apply-overrides` merges override file before analysis |

### 2.2 Secondary User Stories (Optional UI)

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US-6 | Seller | Upload a file via web UI | I don't need to use command line |
| US-7 | Seller | Ask "show top 20" in chat | I get interactive results |
| US-8 | Seller | Filter by bucket in UI | I can focus on NEEDS VERIFICATION items |

---

## 3. DETAILED PIPELINE FLOW

### 3.1 High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FBA ANALYSIS PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: LOAD & NORMALIZE                                                       │
│ ┌─────────────┐    ┌─────────────────┐    ┌─────────────────────────────────┐  │
│ │ load_report │───►│normalize_columns│───►│ DataFrame with RowID, clean EANs│  │
│ └─────────────┘    └─────────────────┘    └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: PREFLIGHT CALIBRATION                                                  │
│ ┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌───────────────┐ │
│ │ sample_rows │───►│ run_preflight│───►│load_supplier_  │───►│merge_         │ │
│ │ (n=50)      │    │              │    │memory          │    │calibration    │ │
│ └─────────────┘    └──────────────┘    └────────────────┘    └───────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: ROW-BY-ROW ANALYSIS                                                    │
│ ┌───────────────────────────────────────────────────────────────────────────┐  │
│ │ FOR EACH ROW:                                                              │  │
│ │   analyze_row(row, merged_config) → row_decision_record                   │  │
│ │     ├── EAN validation (strict checksum + left-padding)                   │  │
│ │     ├── Title parsing (brand, product type, variant, pack)                │  │
│ │     ├── Pack detection (dimension shield, capacity multipack, traps)     │  │
│ │     ├── RSU calculation + adjusted profit                                 │  │
│ │     ├── Bucket assignment (VERIFIED/HIGHLY_LIKELY/NEEDS_VERIFICATION/     │  │
│ │     │                      FILTERED_OUT)                                  │  │
│ │     └── Deterministic confidence score                                    │  │
│ └───────────────────────────────────────────────────────────────────────────┘  │
│ analyze_all_rows(df, merged_config) → coverage_ledger                          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: VALIDATION                                                             │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ validate_ledger(coverage_ledger, df) → validation_result                   │ │
│ │   ├── Coverage gate: every RowID present exactly once                     │ │
│ │   ├── Profit gate: no positive-bucket items with adjusted_profit ≤ 0     │ │
│ │   ├── Trap gates: dimension, quantity-inside, multipack checks           │ │
│ │   └── Distribution sanity checks                                          │ │
│ └────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: OUTPUT GENERATION                                                      │
│ ┌─────────────────────────────────────────────────────────────────────────────┐│
│ │ render_phasea_report(coverage_ledger, metadata) → markdown_report          ││
│ │ write_run_artifacts(run_id, outputs) → file_paths                          ││
│ │ persist_supplier_memory(supplier_id, merged_config, new_traps, overrides)  ││
│ └─────────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Step-by-Step Pipeline Description

| Step | Tool | Input | Output | Notes |
|------|------|-------|--------|-------|
| 1 | `load_report()` | File path (CSV/XLSX) | DataFrame + schema_info | Auto-detect column names |
| 2 | `normalize_columns()` | DataFrame | Normalized DataFrame | Create RowID; clean EANs (strip spaces, handle floats) |
| 3 | `sample_rows()` | DataFrame, n=50 | Sample rows | For preflight analysis |
| 4 | `run_preflight()` | Sample rows | calibration_config + warnings | Detect patterns per Preflight.txt |
| 5 | `load_supplier_memory()` | supplier_id | memory_bundle (or empty) | Load from disk if exists |
| 6 | `merge_calibration()` | memory_bundle, preflight_config | merged_config + diff_report | Precedence: overrides > existing > new preflight > defaults |
| 7 | `analyze_row()` | row, merged_config | row_decision_record | Core deterministic logic |
| 8 | `analyze_all_rows()` | DataFrame, merged_config | coverage_ledger | Iterate over all rows |
| 9 | `validate_ledger()` | coverage_ledger, DataFrame | validation_result | Fail if gates not passed |
| 10 | `render_phasea_report()` | coverage_ledger, metadata | markdown_report | Fixed-width tables per Main.txt |
| 11 | `write_run_artifacts()` | run_id, outputs | file_paths | Write all files to /runs/{run_id}/ |
| 12 | `persist_supplier_memory()` | supplier_id, config, traps, overrides | Updated memory files | Save for next run |

---

## 4. TOOL CONTRACTS & DATA SCHEMAS

### 4.1 Tool Definitions

#### 4.1.1 `load_report(input_path: str) -> Tuple[DataFrame, SchemaInfo]`

```python
@dataclass
class SchemaInfo:
    detected_columns: List[str]
    ean_column: str          # "EAN" or detected variant
    ean_onpage_column: str   # "EAN_OnPage" or detected variant
    sales_column: str        # "sales_numeric" | "bought_in_past_month" | None
    has_rowid: bool
    row_count: int
    file_format: str         # "csv" | "xlsx"
```

#### 4.1.2 `normalize_columns(df: DataFrame) -> DataFrame`

Creates/normalizes:
- `RowID`: 1-indexed if not present
- `EAN_clean`: Strip whitespace, remove `.0`, handle NaN
- `EAN_OnPage_clean`: Same normalization
- `EAN_digits`: Digits only
- `EAN_digits_normalized`: After left-padding attempt

#### 4.1.3 `run_preflight(rows: List[Row]) -> Tuple[CalibrationConfig, List[Warning]]`

```python
@dataclass
class CalibrationConfig:
    explicit_units: List[str]           # ["pce", "pcs", "pk", "pack"]
    allow_trailing_number_as_qty: bool
    leading_multiplier_check: bool
    dimension_shield_keywords: List[str] # ["cm", "mm", "ml", "inch", ...]
    brand_position: str                  # "start" | "mixed"
    sales_column: str
    capacity_pattern_as_rsu: bool        # True: "3 x 400ml" → RSU=3
    spec_x_shield_keywords: List[str]    # ["magnification", "zoom", ...]
    table_pipe_sanitization: bool

@dataclass
class PreflightWarning:
    row_id: int
    description: str                     # "Row 5: '200' looks like quantity but is part of model number"
```

#### 4.1.4 `analyze_row(row: Row, config: MergedConfig) -> RowDecisionRecord`

```python
@dataclass
class ParsedAttributes:
    brand: Optional[str]
    product_type: Optional[str]
    variant: Optional[str]
    size_capacity: Optional[str]
    pack_count_supplier: int             # Default 1
    pack_count_amazon: int               # Default 1
    rsu: float                           # Required Supplier Units

@dataclass
class TrapDetection:
    trap_type: str                       # "dimension_trap" | "quantity_inside" | "spec_x" | "capacity_multipack"
    pattern_matched: str
    action_taken: str                    # "ignored_as_dimension" | "treated_as_pack"

@dataclass
class MatchChecks:
    ean_strict_valid_supplier: bool
    ean_strict_valid_amazon: bool
    is_exact_ean_strict: bool
    brand_match: bool
    product_type_match: bool
    variant_match: bool                  # True | False | "ambiguous"
    pack_match: bool
    capacity_delta_percent: Optional[float]

@dataclass
class RowDecisionRecord:
    row_id: int
    bucket: str                          # "VERIFIED" | "HIGHLY_LIKELY" | "NEEDS_VERIFICATION" | "FILTERED_OUT"
    confidence: int                      # 0-100, deterministically computed
    pack_verdict: str                    # "1:1 Match" | "BUNDLE (4x) - OK" | "BUNDLE (3x) - LOSS"
    adjusted_profit: float
    supplier_attributes: ParsedAttributes
    amazon_attributes: ParsedAttributes
    trap_detections: List[TrapDetection]
    match_checks: MatchChecks
    key_match_evidence: str              # Concise evidence string
    filter_reason: str                   # "-" if not filtered
    required_next_action: Optional[str]  # For NEEDS_VERIFICATION
    _raw_row: Dict                       # Original row data for reference
```

### 4.2 Output Schemas

#### 4.2.1 Coverage Ledger (`coverage_ledger.csv`)

| Column | Type | Description |
|--------|------|-------------|
| row_id | int | Original RowID |
| bucket | str | Final categorization |
| confidence | int | Deterministic score 0-100 |
| pack_ratio | float | Amazon pack / Supplier pack |
| adjusted_profit | float | After RSU adjustment |
| is_exact_ean_strict | bool | Strict EAN match |
| brand_match | bool | Brand tokens match |
| product_match | bool | Product type match |
| trap_flags | str | Comma-separated trap types detected |
| evidence_pointer | str | Path reference to evidence.jsonl line |

#### 4.2.2 Evidence File (`evidence.jsonl`)

One JSON line per RowID:
```json
{
  "row_id": 626,
  "supplier_attributes": {...},
  "amazon_attributes": {...},
  "trap_detections": [...],
  "match_checks": {...},
  "deterministic_reasons": ["exact_ean_match", "pack_1_to_1", "profit_positive"],
  "required_next_action": null
}
```

#### 4.2.3 Run Summary (`run_summary.json`)

```json
{
  "run_id": "20260104_153000",
  "input_file": "part_1_jan.xlsx",
  "supplier_id": "efghousewares",
  "row_count": 1500,
  "bucket_counts": {
    "VERIFIED": 45,
    "HIGHLY_LIKELY": 82,
    "NEEDS_VERIFICATION": 37,
    "FILTERED_OUT": 156
  },
  "validation_passed": true,
  "validation_details": {...},
  "timing_ms": 45230,
  "model_calls": 15,
  "created_at": "2026-01-04T15:30:00+04:00"
}
```

---

## 5. DETERMINISTIC SCORING RUBRIC

### 5.1 Core Principle

**Scores are computed by code, not LLM.** The LLM may produce reasoning summaries and extraction hints, but confidence score computation follows a fixed formula.

### 5.2 Base Scores by Bucket

| Bucket | Base Score | Adjustment Range |
|--------|------------|------------------|
| VERIFIED (exact EAN) | 95 | -5 to 0 (downgrade for ambiguities) |
| HIGHLY_LIKELY | 80 | -10 to +5 |
| NEEDS_VERIFICATION | 60 | -10 to +15 |
| FILTERED_OUT | N/A | Score reflects what it WOULD be if not filtered |

### 5.3 Scoring Formula

```python
def compute_confidence(row: RowDecisionRecord) -> int:
    """Deterministic confidence scoring."""
    
    if row.bucket == "VERIFIED":
        # Base: 95
        score = 95
        # Deductions
        if row.match_checks.capacity_delta_percent and row.match_checks.capacity_delta_percent > 5:
            score -= 2  # Minor capacity variance
        if row.trap_detections:
            score -= 1  # Had to apply trap logic
        if row.rsu > 1 and row.adjusted_profit < 5:
            score -= 2  # Marginal profit after adjustment
        return max(85, min(95, score))
    
    elif row.bucket == "HIGHLY_LIKELY":
        # Base: 80
        score = 80
        # Additions
        if row.match_checks.brand_match and row.match_checks.product_type_match:
            score += 5
        if row.match_checks.ean_strict_valid_amazon == False:
            # Missing Amazon EAN is more forgiving than different EAN
            score += 2
        # Deductions
        if row.match_checks.ean_strict_valid_amazon and not row.match_checks.is_exact_ean_strict:
            # Different EAN (not missing) requires stronger evidence
            score -= 5
        if row.match_checks.variant_match == "ambiguous":
            score -= 3
        return max(70, min(90, score))
    
    elif row.bucket == "NEEDS_VERIFICATION":
        # Base: 60
        score = 60
        # Additions for stronger evidence
        if row.match_checks.brand_match:
            score += 10
        if row.match_checks.product_type_match:
            score += 5
        # Deductions
        if not row.match_checks.brand_match and not row.match_checks.product_type_match:
            score -= 10
        return max(40, min(79, score))
    
    else:  # FILTERED_OUT
        # Return score it would have had
        base = 80 if row.match_checks.is_exact_ean_strict else 70
        return base
```

### 5.4 Evidence Weighting

| Evidence Type | Weight |
|---------------|--------|
| Exact EAN strict match | +35 (immediate VERIFIED track) |
| Brand match (case-insensitive) | +15 |
| Product type match | +10 |
| Variant match (size/color/scent) | +10 |
| Pack match (1:1) | +10 |
| Capacity within 10% | +5 |
| Model number match | +8 |
| Missing Amazon EAN (not different) | +2 (vs different) |

---

## 6. MEMORY / LEARNING DESIGN

### 6.1 Storage Structure

```
/memory/
└── suppliers/
    └── {supplier_id}/
        ├── calibration.json          # Most recent preflight config
        ├── trap_library.jsonl        # Known trap patterns with corrections
        ├── overrides.jsonl           # User-approved manual corrections
        └── brand_aliases.json        # Known brand name variations
```

### 6.2 File Schemas

#### 6.2.1 `calibration.json`

```json
{
  "supplier_id": "efghousewares",
  "last_updated": "2026-01-04T15:30:00+04:00",
  "source_file": "part_1_jan.xlsx",
  "config": {
    "explicit_units": ["pce", "pcs", "pk", "pack"],
    "allow_trailing_number_as_qty": true,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch"],
    "brand_position": "mixed",
    "capacity_pattern_as_rsu": true,
    "spec_x_shield_keywords": ["magnification", "zoom", "led"]
  },
  "validation_status": "validated"
}
```

#### 6.2.2 `trap_library.jsonl`

```json
{"pattern": "9x9 inch", "trap_type": "dimension_trap", "correct_interpretation": "tray_size_not_pack", "first_seen": "2026-01-03", "occurrences": 5}
{"pattern": "STICKS 200", "trap_type": "quantity_inside", "correct_interpretation": "200_per_pack_not_200_packs", "first_seen": "2026-01-03", "occurrences": 3}
{"pattern": "2x magnification", "trap_type": "spec_x", "correct_interpretation": "optical_feature_not_pack", "first_seen": "2026-01-04", "occurrences": 1}
```

#### 6.2.3 `overrides.jsonl`

```json
{"row_id": 626, "original_bucket": "NEEDS_VERIFICATION", "overridden_bucket": "VERIFIED", "reason": "Confirmed 5-pack via browser", "approved_by": "user", "date": "2026-01-04"}
{"supplier_pattern": "PK5", "interpretation": "5-pack", "approved_by": "user", "date": "2026-01-03"}
```

### 6.3 Merge Precedence

On each run:

```python
def merge_calibration(memory_bundle, preflight_config) -> MergedConfig:
    """
    Precedence (highest to lowest):
    1. overrides (user-approved corrections)
    2. existing calibration (from memory)
    3. new preflight inference (current run)
    4. defaults (hardcoded safe values)
    """
    merged = defaults.copy()
    merged.update(preflight_config)
    merged.update(memory_bundle.get("calibration", {}))
    merged.apply_overrides(memory_bundle.get("overrides", []))
    return merged
```

### 6.4 Lifecycle

1. **First Run for Supplier:** No memory → run preflight → save calibration
2. **Subsequent Runs:** Load memory → run preflight anyway → compare → update if drift detected
3. **User Override:** User approves correction → append to overrides.jsonl → takes precedence on future runs

---

## 7. UI PLAN

### 7.1 CLI (MVP Required)

#### 7.1.1 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Run full analysis on input file | `python -m fba_agent analyze --input "C:\path\file.xlsx" --skip-browser true` |
| `top` | Show top candidates from a run | `python -m fba_agent top --run-id 20260104_153000 --min-confidence 80 --limit 30` |
| `explain` | Explain decision for specific row | `python -m fba_agent explain --run-id 20260104_153000 --rowid 626` |
| `export` | Export results in different format | `python -m fba_agent export --run-id 20260104_153000 --format csv` |
| `rerun` | Rerun with overrides applied | `python -m fba_agent rerun --run-id 20260104_153000 --apply-overrides corrections.jsonl` |
| `list-runs` | List all runs | `python -m fba_agent list-runs` |
| `show-memory` | Display supplier memory | `python -m fba_agent show-memory --supplier efghousewares` |

#### 7.1.2 CLI Options

```
fba_agent analyze
  --input PATH         Path to input file (required)
  --supplier NAME      Supplier ID (auto-detected from filename if omitted)
  --skip-browser       Skip Phase 5 browser verification (default: true)
  --output-dir PATH    Custom output directory (default: ./runs/{run_id}/)
  --verbose            Enable verbose logging
```

### 7.2 Chat Interface (Optional - Streamlit)

If feasible without scope explosion:

#### 7.2.1 Features

- File upload / selection
- Run analysis button
- Natural language queries: "show top 20", "explain RowID 1402"
- Bucket filtering (tabs or dropdown)
- Table view with sorting
- Evidence modal for each row

#### 7.2.2 Implementation Notes

- Use Streamlit for rapid development
- If Streamlit too complex → implement CLI REPL mode instead:

```python
# CLI REPL mode
> analyze part_1_jan.xlsx
Analysis complete. Run ID: 20260104_153000
> top 20
[Shows top 20 candidates]
> explain 626
[Shows detailed evidence for RowID 626]
> filter NEEDS_VERIFICATION
[Shows all NEEDS_VERIFICATION items]
> exit
```

---

## 8. VALIDATION GATES & FAILURE HANDLING

### 8.1 Coverage Gate

```python
def validate_coverage(ledger: DataFrame, original_df: DataFrame) -> ValidationResult:
    """Every RowID from original must appear exactly once in ledger."""
    expected_rows = set(original_df['RowID'].tolist())
    ledger_rows = set(ledger['row_id'].tolist())
    
    missing = expected_rows - ledger_rows
    duplicates = ledger_rows - set(ledger['row_id'].unique())
    
    if missing or duplicates:
        return ValidationResult(
            passed=False,
            error=f"Coverage failed. Missing: {missing}, Duplicates: {duplicates}"
        )
    return ValidationResult(passed=True)
```

**Failure Action:** Hard fail. Do not generate report. Log error with details.

### 8.2 Profit Gate

```python
def validate_profit(ledger: DataFrame) -> ValidationResult:
    """No VERIFIED/HIGHLY_LIKELY/NEEDS_VERIFICATION with adjusted_profit <= 0."""
    positive_buckets = ["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION"]
    violations = ledger[
        (ledger['bucket'].isin(positive_buckets)) & 
        (ledger['adjusted_profit'] <= 0)
    ]
    
    if len(violations) > 0:
        return ValidationResult(
            passed=False,
            error=f"Profit gate failed. {len(violations)} rows in positive buckets with non-positive profit.",
            violation_rows=violations['row_id'].tolist()
        )
    return ValidationResult(passed=True)
```

**Failure Action:** Hard fail. These rows should have been routed to FILTERED_OUT.

### 8.3 Trap Gates

| Gate | Check | Failure Action |
|------|-------|----------------|
| Dimension Trap | No dimension patterns (9x9, 15cm) caused RSU > 1 | Soft fail + warning; may indicate trap library needs update |
| Quantity-Inside | No "STICKS 200" patterns caused pack=200 | Soft fail + warning |
| Multipack | All "(4 x 50)" patterns correctly computed RSU | Hard fail if multipack parsing broken |
| Brand Upgrade | All brand+product matches in HIGHLY_LIKELY, not NEEDS_VERIFICATION | Soft fail + warning |
| Capacity | >50% capacity difference → FILTERED_OUT | Hard fail if in positive bucket |

### 8.4 Output Formatting Gate

```python
def validate_output_format(report_path: str) -> ValidationResult:
    """Verify fixed-width table formatting."""
    with open(report_path, 'r') as f:
        content = f.read()
    
    # Check for tabs (forbidden)
    if '\t' in content:
        return ValidationResult(passed=False, error="Report contains tabs")
    
    # Check for pipe characters in cell content (should be sanitized)
    # This is checked during generation, not post-hoc
    
    return ValidationResult(passed=True)
```

### 8.5 Failure Handling Strategy

| Severity | Action |
|----------|--------|
| **Hard Fail** | Abort run. No artifacts generated. Return error code 1. Log full details. |
| **Soft Fail** | Generate report with warnings section. Return code 0 but log warnings. |
| **LLM Error** | Retry with exponential backoff (max 3 attempts). Fail hard after retries exhausted. |
| **File I/O Error** | Fail hard with descriptive message. |

---

## 9. TEST PLAN & EVALUATION DATASET

### 9.1 Unit Tests

| Test Category | Test Cases |
|---------------|------------|
| EAN Normalization | Valid 13-digit, valid 8-digit, needs left-padding, invalid checksum, scientific notation, NaN |
| Pack Parsing | "Pack of 10", "10 PACK", "(4 x 50)", "STICKS 200", "9x9 inch", "15 x 5.5 x 5.5 cm" |
| Dimension Shield | All patterns in Main.txt must NOT trigger RSU calculation |
| Spec-X Shield | "2x magnification", "9 LED", "3500k" must NOT be pack counts |
| Adjusted Profit | RSU=1 → no change, RSU=4 → multiply cost by 4, negative result detection |
| GTIN Checksum | Valid checksums pass, invalid fail, left-padding then recheck |

### 9.2 Integration Tests

| Test | Input | Expected Output |
|------|-------|-----------------|
| End-to-end small file | 10-row fixture | coverage_ledger with 10 rows, report generated |
| Missing EAN handling | File with some missing EANs | No crash, correct routing to HIGHLY_LIKELY or NEEDS_VERIFICATION |
| Pack mismatch detection | Known pack mismatch rows | Correct RSU calculation, routed to FILTERED_OUT if negative profit |
| Dimension trap | Rows with "9x9 inch" | Pack = 1, not 81 or 9 |

### 9.3 Regression Tests (Golden Dataset)

Create a "golden" dataset of ~50 manually verified rows:

```
/tests/golden_dataset/
├── input_golden.xlsx           # 50 rows with known correct categorizations
├── expected_ledger.csv         # Expected coverage_ledger output
└── test_golden.py              # Pytest to compare actual vs expected
```

**Stability Requirement:** Across runs, bucket assignments and scores should be identical (±2 points for confidence allowed due to LLM reasoning extraction variance).

### 9.4 Evaluation Metrics

| Metric | Target |
|--------|--------|
| Coverage | 100% (no missing RowIDs) |
| Score Stability | ±2 points across runs |
| Bucket Stability | 0 bucket changes across runs for same input |
| False Positive Rate | < 5% of VERIFIED/HIGHLY_LIKELY later found incorrect |
| Miss Rate | < 10% of valid matches routed to FILTERED_OUT |

---

## 10. IMPLEMENTATION MILESTONES

### 10.1 MVP (Phase 2a)

**Goal:** Working CLI with core analysis, deterministic scoring, file output.

| Component | Deliverable |
|-----------|-------------|
| Core Pipeline | `load_report`, `normalize_columns`, `analyze_row`, `analyze_all_rows` |
| Validation | `validate_ledger` with coverage + profit gates |
| Output | `render_phasea_report`, `write_run_artifacts` |
| CLI | `analyze`, `top`, `explain`, `export` commands |
| Model Integration | Kimi/Moonshot via LiteLLM adapter |
| Tests | Unit tests for EAN, pack parsing, dimension shield |

**Estimate:** 3-4 days

### 10.2 V2 (Phase 2b)

**Goal:** Memory/learning, enhanced validation, optional UI.

| Component | Deliverable |
|-----------|-------------|
| Preflight | `run_preflight`, `sample_rows` |
| Memory | `load_supplier_memory`, `merge_calibration`, `persist_supplier_memory` |
| CLI Enhancements | `rerun`, `list-runs`, `show-memory` commands |
| Trap Library | Persistent trap detection + learning |
| UI | Streamlit app or CLI REPL mode |
| Tests | Golden dataset regression, integration tests |

**Estimate:** 2-3 days

### 10.3 Future (V3+)

- Browser verification tool (Phase 5 stub → implementation)
- Multi-file batch processing
- Supplier comparison reports
- API endpoint for programmatic access

---

## 11. RISKS & MITIGATIONS

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Kimi/Moonshot API rate limits | Medium | High | Implement backoff; batch LLM calls where possible |
| Model output parsing failures | Medium | Medium | Strict output schema; fallback to regex extraction |
| Large file memory issues | Low | High | Process rows in chunks; don't load entire DataFrame in memory for analysis |
| LiteLLM adapter incompatibility | Low | High | Test adapter early; have fallback to direct API calls |

### 11.2 Accuracy Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM extracts wrong brand | Medium | Medium | Use code-based brand list matching as primary; LLM as secondary |
| Pack parsing edge cases | High | High | Comprehensive trap library; continuous updates from user feedback |
| Score drift despite deterministic formula | Low | Medium | LLM only for reasoning text; all numeric scores computed in code |

### 11.3 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Secrets in logs | Low | High | Never log API keys; use env vars only |
| Report format changes break downstream | Medium | Medium | Version the report format; migration scripts if needed |
| Memory files corrupted | Low | High | Validate on load; backup before modification |

---

## 12. CONFLICT RESOLUTION LOG

Per BUILD PROMPT Section 1, conflicts between specifications are resolved with precedence: Main.txt > Manual guide > Preflight.txt.

### 12.1 Documented Resolutions

| Conflict | Source A | Source B | Resolution | Rationale |
|----------|----------|----------|------------|-----------|
| NEEDS_VERIFICATION scope | Main.txt: "highly selective" | Manual guide: broader interpretation | Follow Main.txt: selective (1-2 confirmable details) | Main.txt is v4.1.1 with latest refinements |
| Capacity tolerance thresholds | Main.txt: 0-10%, 10-25%, 25-50%, >50% | Manual guide: ≤15% acceptable | Follow Main.txt's detailed tiers | More granular guidance |
| FILTERED_OUT definition | Main.txt: confirmed matches only | Preflight: not mentioned | Follow Main.txt: only confirmed matches | Preflight doesn't define output categories |

---

## 13. APPROVAL REQUEST

### 13.1 What Is Included in This PRD

✅ Problem statement and constraints  
✅ User stories (primary + optional UI)  
✅ Detailed pipeline flow (diagram + step-by-step)  
✅ Tool contracts and data schemas (input mapping + output)  
✅ Deterministic scoring rubric (formula + weights)  
✅ Memory/learning design (storage, schemas, precedence, lifecycle)  
✅ UI plan (CLI required, chat optional)  
✅ Validation gates and failure handling strategy  
✅ Test plan + evaluation dataset approach  
✅ Implementation milestones (MVP + V2)  
✅ Risks and mitigations  
✅ Conflict resolution log  

### 13.2 What Happens Next (After Approval)

1. Create repo structure:
   - `/src/fba_agent/`
   - `/tests/`
   - `/runs/`
   - `/memory/`
   - `/docs/`

2. Implement MVP (Phase 2a):
   - Core tools
   - CLI commands
   - Kimi/Moonshot integration via LiteLLM
   - Unit tests

3. Implement V2 (Phase 2b):
   - Preflight + memory
   - Enhanced validation
   - Optional Streamlit UI

4. Document:
   - `README.md` with setup & usage
   - `.env.example`
   - Sample run output in `/docs/examples/`

---

## ⏸️ STOP — APPROVAL REQUIRED

**This document represents the complete Phase 1 planning artifact.**

**Before I proceed with Phase 2 (Implementation), please review this PRD and confirm:**

1. ✅ The pipeline design meets your requirements
2. ✅ The scoring rubric is acceptable
3. ✅ The memory/learning approach is what you envisioned
4. ✅ The validation gates are sufficient
5. ✅ The milestones and scope are realistic

**Please reply with APPROVED to proceed with implementation, or provide feedback on any sections that need revision.**

---

*PRD Version: 1.0*  
*Created: 2026-01-04*  
*Based on: Main.txt (v4.1.1 AG1), Manual analysis guide (v1.1), Preflight (v1.2)*
