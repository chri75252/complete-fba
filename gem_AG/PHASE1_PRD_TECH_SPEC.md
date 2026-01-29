# FBA Product Analysis Agent - Phase 1: Final PRD & Technical Specification

**Version:** 1.1 (Synthesized Antigravity + Codex)  
**Date:** 2026-01-04  
**Status:** DRAFT (Seeking Approval)  
**Timezone:** Asia/Dubai (UTC+4)

---

## 1. Problem Statement & Core Objectives

**Problem:**  
Current "prompt-only" FBA anaylsis workflows are inconsistent. They suffer from:
*   **Drift:** Re-running the same file yields different results.
*   **Missed Rows:** Rows are silently dropped or duplicated.
*   **Hallucination:** "Vibes-based" scoring instead of evidence-based scoring.
*   **Trap Susceptibility:** Models easily confuse "9x9 inch" with "9-pack".

**Objective:**  
Build a **deterministic, production-grade Agent** that operationalizes the `Analysis Methodology` and `Master Prompt` into a hard-coded pipeline with LLM assistance only for semantic extraction.

**Success Definition:**
*   **100% Deterministic Coverage:** Every input row maps to exactly **one** of 5 internal buckets.
*   **Zero Missed Rows:** `Sum(Buckets) == Total Input Rows`.
*   **Audit Trail:** `coverage_ledger.csv` explains every decision.
*   **Exact Output:** Markdown report matches `Main.txt` schema perfectly.

---

## 2. Authoritative Specifications (Canonical)

This build is grounded strictly in the provided prompt specifications.

1.  **Main Spec** (`Main.txt`): Defines the Report Schema, Validation Checklist, and 4-Category Contract.
2.  **Methodology** (`Manual guide.md`): Defines the Decision Trees, Phasing, and "Unrelated vs Filtered" distinction.
3.  **Preflight** (`Preflight.txt`): Defines the Supplier Calibration format.
4.  **Wrapper**: Defines the "Skip Browser" execution mode.

**Conflict Resolution Order:**  
`Main.txt` (Highest) > `Methodology Map` > `Preflight Config`.

---

## 3. System Architecture

### 3.1 Tech Stack
*   **Orchestration:** OpenAI Agents SDK (with LiteLLM adapter for Kimi/Moonshot compatibility).
*   **Language:** Python 3.10+
*   **Data Backbone:** Pandas DataFrame (for ledger and validation).
*   **Storage:** File-based JSON/JSONL for memory and artifacts.

### 3.2 Directory Structure
```text
src/
└── fba_agent/
    ├── __init__.py
    ├── core/
    │   ├── engine.py       # Main pipeline orchestrator
    │   ├── state.py        # Run state & memory loading
    │   └── memory.py       # Supplier calibration/traps/overrides management
    ├── tools/
    │   ├── loader.py       # CSV/XLSX loading & normalization
    │   ├── preflight.py    # Calibration logic (LLM-assisted)
    │   ├── analyzer.py     # Row analysis & deterministic scoring gates
    │   ├── validator.py    # Ledger integrity & gate checks
    │   └── reporting.py    # Markdown renderer & artifact writer
    └── interface/
        ├── cli.py          # Command line entry points
        └── ui.py           # (Future) Streamlit app
tests/                      # Unit checks for Traps/EANs
memory/                     # Persistent supplier knowledge
└── suppliers/
    └── {supplier_id}/
        ├── calibration.json
        ├── traps.jsonl
        ├── overrides.jsonl
        └── brand_aliases.json
runs/                       # Per-run artifacts
```

---

## 4. Pipeline Design (Deterministic Spine)

The agent orchestrates a series of **atomic, deterministic tools**.

### Step 1: Initialize & Normalize
*   **Input:** File Path (`.csv` or `.xlsx`).
*   **Action:**
    *   Load file to DataFrame.
    *   **Normalize:** Create `RowID` (1..N). Clean `EAN`/`EAN_OnPage` columns (strip whitespace, remove scientific notation). Detect `Sales` column.
    *   **Gate:** Fail if file is unreadable or empty.

### Step 2: Preflight Calibration
*   **Input:** First 50 rows.
*   **Action:**
    *   Load `memory/suppliers/{id}/calibration.json` (if exists).
    *   Run **Preflight LLM Call** to detect: Brand Position, Pack Keywords (`pk`, `pcs`), Dimension Units.
    *   **Merge:** `Overrides` > `Existing Memory` > `New Preflight` > `Defaults`.
*   **Output:** `merged_config` object.

### Step 3: Analysis Loop (The Brain)
*   **Input:** All Rows + `merged_config`.
*   **Action:** Iterate row-by-row (parallelized if possible, but sequential logic).
    *   **EAN Check:** Strict validity (Checksum + Length + Left-Padding). Exact string match required for `VERIFIED`.
    *   **Trap Check:** Regex sweep for Dimension Shields (`9x9 inch`), Spec Shields (`2x zoom`), Quantity-Inside (`Sticks 200`).
    *   **Pack Logic:** Extract Supplier Qty vs Amazon Qty.
        *   Rule: `N x [Capacity]` -> RSU = N.
        *   Rule: `(N x M)` -> Multipack logic.
    *   **Profit Calc:** `Adjusted Profit = Price - (Cost * RSU) - Fees`.
    *   **Bucketing:** Assign to one of **5 Buckets**.
    *   **Scoring:** Calculate Confidence (0-100) based on deterministic rubric.

### Step 4: Validation
*   **Action:** `validate_ledger(ledger)`
    *   **Coverage:** Assert `Count(Rows) == Total Input`.
    *   **Profit:** Assert no `Adjusted Profit <= 0` in *Verified*/*Highly Likely*/*Needs Verification*.
    *   **Format:** Check table columns and separators.

### Step 5: Reporting
*   **Action:** Generate `PHASEA_MANUAL_REPORT_{Date}.md`.
    *   **Filter:** Exclude `UNRELATED` bucket from tables.
    *   **Include:** `FILTERED_OUT` bucket (Audit Trail).
    *   **Format:** Fixed-width tables using `merged_config.table_pipe_sanitization`.
*   **Action:** Write `coverage_ledger.csv`, `evidence.jsonl`, `run_summary.json`.

---

## 5. Decision Policy & Logic

### 5.1 The 5-Bucket System
We use 5 internal buckets to map to the 4-category report requirement + the exclusion requirement.

| Internal Bucket | Definition | Report Action |
| :--- | :--- | :--- |
| **VERIFIED** | Strict EAN Match + No Pack/Profit Issues. | **Print Table** |
| **HIGHLY_LIKELY** | Strong Brand/Product Match + Profit > 0. (EAN may mismatch). | **Print Table** |
| **NEEDS_VERIFICATION** | Strong Match but 1-2 ambiguities (Split candidate, Pack unclear). | **Print Table** |
| **FILTERED_OUT** | **Confirmed Match** but Unprofitable/Variant Mismatch (Audit Trail). | **Print Table** (Labeled "FILTERED OUT") |
| **UNRELATED** | Weak/Non-Match/Wrong Category. | **Exclude** (Count only in Summary) |

### 5.2 Deterministic Scoring Rubric
Confidence is **calculated code**, not LLM hallucination.

*   **Base Score:**
    *   Exact EAN: **95**
    *   Non-EAN: **0** (accumulates points)
*   **Modifiers (Non-EAN):**
    *   Brand Match: +35
    *   Product Anchor Match: +25
    *   Variant Match (Tolerance): +15
    *   Pack Match Evidence: +10
    *   Sales Signal: +5
*   **Penalties:**
    *   Pack Ambiguity: -20
    *   Capacity Delta (10-25%): -30
    *   Confirmed Mismatch: -60 (Force Filter/Unrelated)

---

## 6. Learning & Memory

We implement a **Lightweight File-Based Memory System**:

1.  **Calibration:** Stores `SUPPLIER_NAMING_CONVENTION` (e.g., "Use 'pcs' for pack").
2.  **Traps:** Stores regex patterns for known traps (e.g., "9x9 inch" -> Dimension).
3.  **Overrides:** Stores manual corrections (RowID -> Forced Bucket/Pack).

**Lifecycle:**
*   Read Memory at Verification Start.
*   Update Memory (Traps) if new patterns detected (and high confidence).
*   User can manually edit JSON files to "teach" the agent permanently.

---

## 7. Interface Requirements

### 7.1 CLI Commands (MVP)
*   `fba analyze <file> --supplier <name> --skip-browser` -> Runs the full pipeline.
*   `fba explain <run_id> <row_id>` -> Dumps the decision trace, trap checks, and scoring components.
*   `fba export <run_id> --format csv` -> Exports the Ledger.

### 7.2 Interface Gates
*   Fail fast if Input File is missing.
*   Fail fast if API Key (`MOONSHOT_API_KEY`) is missing.

---

## 8. Development Plan (Phase 2)

**Step 1: Core Framework**
*   Initialize `src/fba_agent`.
*   Implement `loader.py` and `normalizer`.
*   Implement `Schema` classes for the Ledger.

**Step 2: Preflight Module**
*   Implement `Preflight` prompt.
*   Implement `Memory` loader/merger.

**Step 3: Analysis Engine ("The Hard Part")**
*   Implement `EANValidator` (Checksums).
*   Implement `PackExtractor` with Regex Shields (Dimension/Spec).
*   Implement `ProfitCalculator`.
*   Implement `ScoringEngine`.

**Step 4: Reporting & CLI**
*   Implement `MarkdownRenderer` (Fixed-width).
*   Implement CLI entry points.

**Step 5: Testing**
*   Create `tests/golden_data.csv` (20 rows with mixed Traps, Matches, Mismatches).
*   Verify `Run 1` output == `Run 2` output (Determinism).

---

## 9. Conflict Resolution & Compliance

*   **Rule:** `UNRELATED` rows are tracked in Ledger but **hidden** from Report Tables.
*   **Rule:** `FILTERED_OUT` rows are tracked *and* shown (to prove we checked them).
*   **Rule:** `Adjusted Profit` is the *only* profit metric that matters for Verifiction.

## 10. Approval Request

**I have synthesized the requirements into this Final Phase 1 PRD.**
It guarantees:
1.  **Zero Missed Rows** (via Ledger).
2.  **Deterministic Scoring** (via Code Rubric).
3.  **Methodology Compliance** (via 5-Bucket mapping).
4.  **Persistent Learning** (via JSON memory).

**Please approve to proceed to Phase 2 (Implementation).**
