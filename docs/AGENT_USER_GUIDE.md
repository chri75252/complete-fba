# FBA Agent User Guide

**Version:** 1.0  
**Last Updated:** 2026-01-07  

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Complete Command Reference](#2-complete-command-reference)
3. [How to Reset/Fresh Start](#3-how-to-resetfresh-start)
4. [Running for a New Supplier](#4-running-for-a-new-supplier)
5. [Understanding the Workflow](#5-understanding-the-workflow)
6. [Memory System Explained](#6-memory-system-explained)
7. [Output Files Explained](#7-output-files-explained)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. QUICK START

### Basic Command to Analyze a Report

```powershell
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

python -m fba_agent analyze --input "path\to\your\report.xlsx" --supplier "supplier_name"
```

### Example: Analyze "part 5 jan.xlsx"

```powershell
python -m fba_agent analyze --input "RESERACH\REPORT\part 5 jan\part 5 jan.xlsx" --supplier "part_5_jan" --enable-ai true
```

---

## 2. COMPLETE COMMAND REFERENCE

### Main Analysis Command

```powershell
python -m fba_agent analyze [OPTIONS]
```

| Option | Required | Description | Example |
|--------|----------|-------------|---------|
| `--input` | ✅ Yes | Path to Excel/CSV file | `"RESERACH\REPORT\file.xlsx"` |
| `--supplier` | ✅ Yes | Unique identifier for this supplier | `"efg_housewares"` |
| `--enable-ai` | No | Enable AI features (critique, adjudication) | `true` or `false` |
| `--max-iterations` | No | Maximum iteration loops (default: 1) | `1`, `2`, `3` |
| `--memory-dir` | No | Custom memory directory (default: `memory`) | `"custom_memory"` |
| `--runs-dir` | No | Custom output directory (default: `codex sgent/AGENT REPORT`) | `"output"` |
| `--skip-browser` | No | Skip browser verification (default: true) | `true` or `false` |

### Other Commands

```powershell
# Show supplier memory status
python -m fba_agent show-memory --supplier "supplier_name"

# View help
python -m fba_agent --help
python -m fba_agent analyze --help
```

---

## 3. HOW TO RESET/FRESH START

### Option A: Complete Fresh Start (Remove ALL Memory)

Delete the entire memory folder to start completely fresh for ALL suppliers:

```powershell
# From the project root directory
Remove-Item -Recurse -Force "memory\suppliers"
```

This removes:
- All supplier calibrations
- All run history
- All trap libraries
- All overrides

**Global traps are preserved** in `memory\global\trap_library.jsonl`.

### Option B: Fresh Start for ONE Supplier Only

Delete only that supplier's memory folder:

```powershell
# Replace "supplier_name" with your actual supplier ID
Remove-Item -Recurse -Force "memory\suppliers\supplier_name"
```

Example for "part_5_jan":
```powershell
Remove-Item -Recurse -Force "memory\suppliers\part_5_jan"
```

### Option C: Keep Calibration, Reset History Only

If you want to keep the calibration (pack keywords, shields) but reset run history:

```powershell
# Delete only run_history.json
Remove-Item "memory\suppliers\supplier_name\run_history.json"
```

### What Gets Reset

| File Deleted | What Happens |
|--------------|--------------|
| `calibration.json` | Agent will re-run preflight calibration |
| `run_history.json` | No past runs to compare against |
| `trap_library.jsonl` | Supplier-specific traps removed |
| `overrides.jsonl` | User overrides removed |

---

## 4. RUNNING FOR A NEW SUPPLIER

### Step 1: Prepare Your Excel File

Ensure your file has these columns (or similar names that can be auto-detected):

| Column Type | Common Names |
|-------------|--------------|
| Supplier EAN | `EAN`, `SupplierEAN`, `Barcode` |
| Amazon EAN | `EAN_OnPage`, `AmazonEAN`, `ASIN_EAN` |
| Supplier Title | `SupplierTitle`, `Title`, `ProductName` |
| Amazon Title | `AmazonTitle`, `AmazonProductTitle` |
| Supplier Price | `SupplierPrice_incVAT`, `Cost`, `Price` |
| Selling Price | `SellingPrice_incVAT`, `AmazonPrice` |
| Net Profit | `NetProfit`, `Profit` |
| Sales | `bought_in_past_month`, `Sales`, `sales_numeric` |
| ASIN | `ASIN` |

### Step 2: Choose a Supplier ID

The supplier ID should be:
- Lowercase
- No spaces (use underscores)
- Descriptive

Examples:
- `efg_housewares`
- `homebase_jan_2026`
- `part_5_jan`

### Step 3: Run the Analysis

```powershell
python -m fba_agent analyze \
    --input "path\to\new_supplier_report.xlsx" \
    --supplier "new_supplier_id" \
    --enable-ai true \
    --max-iterations 1
```

### Step 4: Find Your Output

Output is saved to: `codex sgent\AGENT REPORT\{YYYYMMDD_HHMMSS}\`

Files generated:
- `PHASEA_MANUAL_REPORT_YYYYMMDD.md` - The human-readable report
- `coverage_ledger.csv` - All rows with categorizations
- `run_summary.json` - Summary statistics
- `evidence.jsonl` - Detailed match evidence

---

## 5. UNDERSTANDING THE WORKFLOW

### Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FBA AGENT WORKFLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PREFLIGHT CALIBRATION                                       │
│     └─ AI analyzes data structure, detects pack patterns       │
│                                                                 │
│  2. LOAD MEMORY                                                 │
│     └─ Merge global traps + supplier traps + calibration       │
│                ↓                                                │
│  3. ROW-BY-ROW ANALYSIS (Deterministic)                         │
│     └─ For each row: EAN match → Brand match → Pack parse      │
│     └─ Assign: VERIFIED / HIGHLY_LIKELY / NEEDS_VERIF / FILTER │
│                ↓                                                │
│  4. GENERATE REPORT (Iteration 1)                               │
│     └─ Create Markdown report + coverage ledger                 │
│                ↓                                                │
│  5. AI CRITIQUE (if --enable-ai true)                           │
│     ├─ Review bucket distribution                               │
│     ├─ Check for contradictions                                 │
│     ├─ Compare against past report (1 previous run)             │
│     └─ Recommend: "finalize" / "apply_and_rerun" / "block"      │
│                ↓                                                │
│  6. AI ADJUDICATION (if --enable-ai true)                       │
│     └─ AI reviews ambiguous rows (borderline confidence)        │
│                ↓                                                │
│  [IF max-iterations > 1 AND critique says "apply_and_rerun"]    │
│  7. APPLY ADJUSTMENTS                                           │
│     └─ Update config based on critique suggestions              │
│                ↓                                                │
│  8. RE-RUN ANALYSIS (Iteration 2)                               │
│     └─ Same as Step 3-6 but with updated config                 │
│                ↓                                                │
│  9. REGRESSION CHECK                                            │
│     ├─ Compare Iteration 2 vs Iteration 1                       │
│     ├─ Check: Did VERIFIED/HIGHLY_LIKELY drop?                  │
│     ├─ Check: Did invalid items get added?                      │
│     ├─ Check: Did items move to wrong categories?               │
│     └─ If regression detected: BLOCK and use Iteration 1        │
│                ↓                                                │
│  10. FINALIZE                                                   │
│      └─ Select best iteration, save to output folder            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Distinction: Two Types of AI Comparison

| Comparison Type | When It Happens | What It Compares | Purpose |
|-----------------|-----------------|------------------|---------|
| **Past Report Comparison** | During AI Critique (Step 5) | Current report vs. LAST SAVED report from memory | Find discrepancies, identify regressions from previous runs |
| **Iteration Regression Check** | During Regression Check (Step 9) | Iteration 2 vs. Iteration 1 | Ensure changes didn't make report WORSE |

---

## 6. MEMORY SYSTEM EXPLAINED

### Memory Folder Structure

```
📁 memory/
│
├── 📁 global/                           # Applied to ALL suppliers
│   └── 📄 trap_library.jsonl            # Universal shield keywords
│
└── 📁 suppliers/                        # Per-supplier data
    └── 📁 {supplier_id}/
        ├── 📄 calibration.json          # Config from preflight
        ├── 📄 run_history.json          # Bucket counts from past runs
        ├── 📄 trap_library.jsonl        # Supplier-specific shields
        ├── 📄 overrides.jsonl           # User overrides (highest priority)
        └── 📄 brand_aliases.json        # Brand name mappings
```

### What Each File Contains

| File | Contents | Example |
|------|----------|---------|
| `calibration.json` | Pack keywords, dimension shields, brand position | `{"explicit_units": ["pk", "pack"], "dimension_shield_keywords": ["cm", "mm"]}` |
| `run_history.json` | Summary of past runs (bucket counts, paths) | `[{"run_id": "20260107_061219", "bucket_counts": {"VERIFIED": 40}}]` |
| `trap_library.jsonl` | Shield patterns specific to this supplier | `{"type": "dimension_shield", "keywords": ["oz"]}` |
| `overrides.jsonl` | User-specified overrides (top priority) | `{"SUPPLIER_NAMING_CONVENTION": {"allow_trailing_number_as_qty": false}}` |

### Precedence Order (Highest to Lowest)

1. **User overrides** (`overrides.jsonl`) — Always wins
2. **Supplier traps** (`trap_library.jsonl`)
3. **Supplier calibration** (`calibration.json`)
4. **Global traps** (`memory/global/trap_library.jsonl`)
5. **Preflight output** (current run)
6. **Defaults** (hardcoded)

---

## 7. OUTPUT FILES EXPLAINED

### Output Folder Location

```
codex sgent\AGENT REPORT\{YYYYMMDD_HHMMSS}\
```

Each run creates a timestamped folder.

### Files Generated

| File | Purpose | Format |
|------|---------|--------|
| `PHASEA_MANUAL_REPORT_YYYYMMDD.md` | Human-readable report with all categorized products | Markdown |
| `coverage_ledger.csv` | Every row with full categorization data | CSV (1MB+) |
| `run_summary.json` | Summary statistics, bucket counts, validation status | JSON |
| `evidence.jsonl` | Detailed match evidence for each row | JSONL |
| `calibration_diff.json` | What changed in calibration vs. previous | JSON |
| `merged_calibration.json` | Final merged config used for this run | JSON |
| `iteration_details.json` | Details per iteration (if multiple) | JSON |
| `llm_trace.jsonl` | LLM API calls (for debugging) | JSONL |

---

## 8. TROUBLESHOOTING

### Problem: "VERIFIED count is lower than expected"

**Cause:** Items with matching EANs may be getting filtered due to:
- Pack size mismatch (bundle detection)
- Capacity gate (size difference > 25%)
- Negative adjusted profit after pack calculation

**Solution:** Check `coverage_ledger.csv` for items with:
- `track=VERIFIED` but `bucket=FILTERED_OUT`
- Review `filter_reason` column

### Problem: "AI Critique shows 'block'"

**Cause:** The AI detected high-severity issues.

**Solution:** Check `run_summary.json` → `critique_summary` for details.

### Problem: "Output folder is empty"

**Cause:** Run may have failed before completion.

**Solution:** Check terminal output for errors. Common issues:
- Missing columns in Excel file
- Invalid file path
- Memory permission errors

### Problem: "Want to re-run with different settings"

**Solution:** Delete supplier memory and re-run:
```powershell
Remove-Item -Recurse -Force "memory\suppliers\supplier_name"
python -m fba_agent analyze --input "file.xlsx" --supplier "supplier_name"
```

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────────┐
│                    FBA AGENT QUICK REFERENCE                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  BASIC RUN:                                                    │
│  python -m fba_agent analyze --input "file.xlsx" \            │
│      --supplier "name" --enable-ai true                        │
│                                                                │
│  FRESH START (ONE SUPPLIER):                                   │
│  Remove-Item -Recurse -Force "memory\suppliers\supplier_name"  │
│                                                                │
│  FRESH START (ALL SUPPLIERS):                                  │
│  Remove-Item -Recurse -Force "memory\suppliers"                │
│                                                                │
│  VIEW MEMORY:                                                  │
│  python -m fba_agent show-memory --supplier "name"             │
│                                                                │
│  OUTPUT LOCATION:                                              │
│  codex sgent\AGENT REPORT\{timestamp}\                        │
│                                                                │
│  KEY OUTPUT FILES:                                             │
│  - PHASEA_MANUAL_REPORT_*.md  (human-readable report)          │
│  - coverage_ledger.csv         (all rows with categories)      │
│  - run_summary.json            (statistics)                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

*End of User Guide*
