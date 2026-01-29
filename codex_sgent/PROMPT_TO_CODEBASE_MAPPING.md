# PROMPT TO CODEBASE MAPPING

**Generated:** 2026-01-07 01:21 UTC+4  
**Purpose:** Map the "Manual FBA Analysis" prompt to actual codebase components

---

## CRITICAL UNDERSTANDING

**The prompt you showed is NOT implemented as a standalone script!**

It describes what **AI Adjudication (Step 8)** SHOULD do, but the current implementation doesn't match the prompt's requirements.

---

## MAPPING: PROMPT SECTIONS → CODEBASE COMPONENTS

### 1. PROMPT INPUT SECTION

**Prompt Says:**
```
## Input: Previously Generated Report
**Analyze this report:** The latest generated FBA analysis report
Example: PHASEA_MANUAL_REPORT__*_*.md

**Source financial report context:** This was the original file from which 
the above report was generated. Use ONLY to retrieve missed products.
```

**Current Codebase:**
- ❌ **NOT IMPLEMENTED** - Adjudication doesn't read the MD report
- ❓ **What actually happens:**
  - Adjudication receives DataFrame rows (from `iteration.py`)
  - Adjudication never sees the generated MD report file
  - No "retrieve missed products" logic exists

**Files involved:**
- `src/fba_agent/adjudication.py` - Select candidates
- `src/fba_agent/iteration.py` - Calls adjudication

**Current code (iteration.py, lines ~220-260):**
```python
# Step 8: AI Row Adjudication
candidate_ids = select_candidates(ledger, config, ...)
adjudication_results = []

for row_id in candidate_ids[:50]:  # Only 50 rows!
    row_data = ledger[ledger.row_id == row_id].to_dict('records')[0]
    # AI gets individual row data, NOT the full report
    result = adjudicate_row(row_data, provider, config)
    adjudication_results.append(result)
```

---

### 2. PROMPT COVERAGE CONTRACT

**Prompt Says:**
```
## Non‑Negotiable Coverage Contract
1. You must **read and evaluate every row** in the previously generated report.
2. Every row must be assigned to **exactly one** bucket
3. **Do not cap** any category (no "top 60" lists)
4. You must finish with a **reconciliation**
```

**Current Codebase:**
- ❌ **VIOLATED** - Only processes ~50-300 candidate rows (NOT all rows)
- ❌ **VIOLATED** - Never reads the full report
- ❌ **VIOLATED** - No reconciliation in adjudication output
- ❓ **What actually happens:**
  - `select_candidates()` picks ~300 rows based on triggers (line 56-114 in adjudication.py)
  - Hard cap at 50 rows actually processed (iteration.py line ~241)
  - No coverage guarantee

**Files involved:**
- `src/fba_agent/adjudication.py` lines 56-114 (select_candidates)
- `src/fba_agent/iteration.py` lines ~220-260 (adjudication loop)

---

### 3. PROMPT MANUAL ANALYSIS REQUIREMENT

**Prompt Says:**
```
## Manual Analysis Requirement (NO AUTOMATION)
You must conduct a **true manual analysis** - reading each product row 
individually, analyzing titles/metrics/EAN, and making educated decisions:

1. **Read each categorized product** in the report individually
2. **Analyze** SupplierTitle, AmazonTitle, EAN, pack sizes, adjusted profit
3. **Validate** categorization against methodology
4. **Identify errors** and understand root causes
```

**Current Codebase:**
- ❌ **NOT IMPLEMENTED** - Adjudication is automated per-row checking
- ❓ **What actually happens:**
  - AI receives isolated row data (no context of other rows)
  - AI makes quick yes/no decision per row
  - No comprehensive report review
  - No root cause analysis

**Files involved:**
- `src/fba_agent/adjudication.py` lines 120-200 (adjudicate_row function)

**Current code:**
```python
def adjudicate_row(row_data, provider, config):
    """Process a single row."""
    # AI gets this row's data only (no report context)
    system = "You are reviewing a single product match..."
    user = f"Row ID: {row_data['row_id']}\n..."
    
    response = provider.chat_json(system, user, schema=ADJUDICATION_SCHEMA)
    # Returns: {"recommended_bucket": "...", "reason": "..."}
```

---

### 4. PROMPT REVISIT LOOP

**Prompt Says:**
```
## Revisit Loop (prevents false positives + misses)
1. **False‑positive sweep:** Recheck every `VERIFIED`/`HIGHLY LIKELY` row
2. **Miss sweep:** Recheck `UNRELATED / NOT INCLUDED` rows
3. **Root cause analysis:** Document WHY errors occurred
4. Run the reconciliation check again
```

**Current Codebase:**
- ❌ **NOT IMPLEMENTED** - No sweep logic exists
- ❌ **NOT IMPLEMENTED** - No root cause analysis
- ❓ **Closest equivalent:**
  - Critique (Step 9) reviews bucket counts, not individual rows
  - No systematic false-positive checking

**Files involved:**
- `src/fba_agent/critique.py` - Reviews aggregates, not individual rows

---

### 5. PROMPT OUTPUT REQUIREMENTS

**Prompt Says:**
```
### **Output File: PHASEA_MANUAL_REPORT_MMDDHHSS.md**
The report must contain:
1. **Summary counts**
2. **VERIFIED — RECOMMENDED**
3. **VERIFIED — AUDITED OUT / EXCLUDED**
4. **HIGHLY LIKELY — RECOMMENDED**
5. **HIGHLY LIKELY — AUDITED OUT / EXCLUDED**
6. **NEEDS VERIFICATION**
```

**Current Codebase:**
- ✅ **IMPLEMENTED** - MD report generation exists
- ⚠️ **Partial match** - Report structure is similar but not identical
- ❓ **What actually happens:**
  - Report generated by `report.py` from final ledger
  - Structure matches prompt mostly
  - But adjudication results are NOT applied to ledger (bug!)

**Files involved:**
- `src/fba_agent/report.py` - Generates MD report
- `src/fba_agent/run.py` - Main orchestrator writes report

**Current code:**
```python
# In run.py (after iteration loop)
from fba_agent.report import write_markdown_report

report_path = write_markdown_report(
    ledger=final_ledger,
    config=config,
    output_dir=output_dir,
    supplier_name=supplier_name
)
```

---

## COMPLETE MAPPING TABLE

| Prompt Section | Prompt Requirement | Codebase Component | Implementation Status | Files |
|----------------|-------------------|-------------------|----------------------|-------|
| **Input** | Read MD report + source Excel | AI Adjudication (Step 8) | ❌ NOT IMPLEMENTED | `adjudication.py` |
| **Coverage Contract** | Process ALL rows, reconcile | Adjudication candidate selection | ❌ VIOLATED (only ~50-300 rows) | `adjudication.py` lines 56-114 |
| **Manual Analysis** | Read each product, analyze individually | Adjudication per-row processing | ⚠️ PARTIAL (automated, not manual) | `adjudication.py` lines 120-200 |
| **Revisit Loop** | False-positive sweep, miss sweep | Critique + Adjudication | ❌ NOT IMPLEMENTED | `critique.py`, `adjudication.py` |
| **Root Cause Analysis** | Document WHY errors occurred | Adjudication output | ❌ NOT IMPLEMENTED | None |
| **Output Format** | Generate corrected MD report | Report generation | ✅ IMPLEMENTED | `report.py`, `run.py` |
| **Table Schema** | Fixed-width tables with specific columns | Report formatting | ✅ IMPLEMENTED | `report.py` |
| **Reconciliation** | Verify all rows accounted for | Final validation | ❌ NOT IMPLEMENTED | None |

---

## WORKFLOW STEP EQUIVALENTS

### What Each Step Actually Does

| Workflow Step | Script/File | What It Does | AI Used? | Matches Prompt? |
|---------------|-------------|--------------|----------|-----------------|
| **Step 0: CLI Entry** | `cli.py` | Parse command line args | ❌ No | N/A |
| **Step 1: Load Data** | `io.py` | Load Excel/CSV into DataFrame | ❌ No | ✅ Loads source file |
| **Step 2: Stable Keys** | `stable_key.py` | Generate deterministic row IDs | ❌ No | N/A |
| **Step 3: Pre-filter** | `prefilter.py` | Remove obviously unprofitable rows | ❌ No | N/A |
| **Step 4: Preflight** | `preflight.py` | Detect supplier naming patterns | ✅ LLM | N/A |
| **Step 5: Memory Load** | `memory.py` | Load previous run data | ❌ No | N/A |
| **Step 6: Analysis** | `analysis.py` | Deterministic row-by-row analysis | ❌ No | ⚠️ PARTIAL (analyzes rows, but not "manual") |
| **Step 7: Validation** | `validation.py` | Check for data quality issues | ❌ No | N/A |
| **Step 8: Adjudication** | `adjudication.py` | AI reviews ~50 ambiguous rows | ✅ LLM | ⚠️ **SHOULD BE** the manual analysis prompt, but ISN'T |
| **Step 9: Critique** | `critique.py` | AI reviews bucket counts & anomalies | ✅ LLM | ❌ Different purpose |
| **Step 10: Apply Adjustments** | `adjustments.py` | Apply critique changes to config | ❌ No | N/A |
| **Step 11: Iteration Decision** | `iteration.py` | Decide if another pass needed | ❌ No | N/A |
| **Step 12: Regression Guard** | N/A (not implemented) | Compare to previous run | ❌ No | N/A |
| **Step 13: Generate Report** | `report.py` | Write MD report from ledger | ❌ No | ✅ Generates the report file |
| **Step 14: Memory Save** | `memory.py` | Save results for next run | ❌ No | N/A |

---

## THE DISCONNECT

### What The Prompt Describes:
**"Comprehensive Manual Review of Generated Report"**
- Input: Already-generated MD report file
- Process: AI reads ENTIRE report like a human analyst
- Output: Corrected/validated report with root cause analysis

### What The Codebase Actually Does:
**"Automated Per-Row Adjudication of Ambiguous DataFrame Entries"**
- Input: DataFrame subset (~50 rows)
- Process: AI makes quick decisions on isolated rows
- Output: List of per-row recommendations (NOT applied!)

---

## WHERE THE PROMPT SHOULD FIT

The prompt describes what **Step 8: Adjudication** SHOULD do in the redesigned system:

```
Current Broken Flow:
1. Generate initial report from deterministic analysis
2. Adjudication: Check ~50 isolated rows → Results ignored
3. Critique: Review bucket counts → Suggests config changes
4. Generate final report (same as initial, adjudication not applied!)

Correct Flow (Per Prompt):
1. Generate initial report from deterministic analysis
2. **Adjudication: AI reads FULL MD report, validates ALL entries, finds errors**
3. Apply adjudication fixes to ledger
4. Critique: Review adjudication findings, suggest config changes
5. Iteration 2: Re-run with fixes
6. Generate final corrected report
```

---

## FILES THAT NEED TO BE CREATED/MODIFIED

### To Implement The Prompt:

**1. CREATE: Comprehensive Adjudication Function**
```python
# File: src/fba_agent/comprehensive_adjudication.py (NEW)

def run_comprehensive_adjudication(
    report_path: str,  # Path to generated MD report
    ledger: pd.DataFrame,  # Original DataFrame
    source_excel_path: str,  # Source file for missed products
    config: MergedConfig,
    provider: BaseProvider
) -> ComprehensiveAdjudicationResult:
    """
    Implements the manual analysis prompt requirements:
    1. Read full MD report
    2. Validate EVERY entry
    3. Identify errors and root causes
    4. Recommend recategorizations
    5. Retrieve missed products from source
    6. Return reconciliation
    """
    # Read full MD report as text
    with open(report_path, 'r') as f:
        report_content = f.read()
    
    # Send to AI with comprehensive review prompt
    system = """You are a Principal E-Commerce Analyst...
    [Full prompt from MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md]
    """
    
    user = f"""Review this complete report:
    {report_content}
    
    Source file for missed products: {source_excel_path}
    """
    
    # AI performs comprehensive analysis
    result = provider.chat_json(system, user, schema=COMPREHENSIVE_SCHEMA)
    
    # Parse and return structured results
    return ComprehensiveAdjudicationResult(
        errors_found=result['errors'],
        recategorizations=result['recategorizations'],
        root_causes=result['root_causes'],
        missed_products=result['missed_products'],
        reconciliation=result['reconciliation']
    )
```

**2. MODIFY: iteration.py**
```python
# Replace current adjudication call with comprehensive version

# OLD (current):
adjudication_results = []
for row_id in candidate_ids[:50]:
    result = adjudicate_row(...)
    adjudication_results.append(result)

# NEW (comprehensive):
adjudication_result = run_comprehensive_adjudication(
    report_path=iteration_report_path,
    ledger=ledger,
    source_excel_path=config.input_path,
    config=config,
    provider=provider
)

# Apply recategorizations to ledger
ledger = apply_adjudication_recategorizations(ledger, adjudication_result)
```

**3. CREATE: Apply Adjudication Function**
```python
# File: src/fba_agent/adjudication_apply.py (NEW)

def apply_adjudication_recategorizations(
    ledger: pd.DataFrame,
    adjudication: ComprehensiveAdjudicationResult
) -> pd.DataFrame:
    """Apply adjudication recommendations to ledger."""
    for recat in adjudication.recategorizations:
        row_id = recat['row_id']
        new_bucket = recat['new_bucket']
        reason = recat['reason']
        
        # Update ledger
        ledger.loc[ledger.row_id == row_id, 'bucket'] = new_bucket
        ledger.loc[ledger.row_id == row_id, 'filter_reason'] = reason
    
    return ledger
```

---

## SUMMARY

**Direct Answer to Your Question:**

| What The Prompt Describes | Equivalent Codebase Component | Implementation Status |
|--------------------------|------------------------------|----------------------|
| **"Thorough Manual FBA Product Analysis"** | **Step 8: AI Adjudication** | ❌ **NOT IMPLEMENTED AS DESCRIBED** |

**The prompt is a design specification for what Adjudication SHOULD do, but current code does something different!**

### Current Reality:
- **Step 8 (Adjudication):** Quick automated checks on ~50 isolated rows
- **Step 9 (Critique):** Reviews aggregate statistics, not individual products
- **Result:** No comprehensive manual review happens anywhere in the workflow

### What Needs To Happen:
1. Replace current `adjudication.py` with comprehensive review logic
2. Make it read the full MD report file
3. Process ALL entries, not just 50
4. Return detailed error analysis + recategorizations
5. Actually apply the results to the ledger

**Would you like me to implement the comprehensive adjudication system as described in the prompt?**
