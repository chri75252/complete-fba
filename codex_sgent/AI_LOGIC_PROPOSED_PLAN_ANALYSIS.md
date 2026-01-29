# AI LOGIC PROPOSED PLAN ANALYSIS (IMPLEMENTED v4.3.0)

**Generated:** 2026-01-08 09:35 UTC+4  
**Implemented:** 2026-01-08 20:25 UTC+4  
**Purpose:** Thorough analysis of proposed workflow changes for Steps 5, 6, 7  
**Status:** ✅ IMPLEMENTED IN v4.3.0

---

## ⚠️ CORRECTIONS TO MY PREVIOUS MISUNDERSTANDINGS

### Correction #1: Row Count Source
| I Assumed | Correct Understanding |
|-----------|----------------------|
| 2789 rows (full Excel) | ~367 rows (MD report tables only) |

**Actual MD Report Contents:**
- VERIFIED - RECOMMENDED: 35 rows
- VERIFIED - FILTERED OUT: 6 rows
- HIGHLY LIKELY - RECOMMENDED: 192 rows
- HIGHLY LIKELY - FILTERED OUT: 36 rows
- NEEDS VERIFICATION: 98 rows
- **TOTAL IN MD TABLES: ~367 rows** (NOT 2789)

### Correction #2: "Giving Access" Meaning
| I Assumed | Correct Understanding |
|-----------|----------------------|
| Dump entire file into prompt | LLM has **tool-based access** to read/extract as needed |

**Your Intent:** The LLM is "made aware" of files and can query/read sections on demand, NOT receive everything upfront.

### Correction #3: Profit-Based Filtering
| Current Code (WRONG) | Your Policy (CORRECT) |
|---------------------|----------------------|
| `profit > £10` as selection criteria | Profit NEVER decides inclusion (only > £0) |

---

## REVISED ANALYSIS WITH CORRECT UNDERSTANDING

### PART 1: Process ALL MD Report Rows in Batches of 70

**Your Proposal:**
> "Group entries into batches of 70 products from the GENERATED MD REPORT"

**Revised Token Calculation:**

| Metric | Value |
|--------|-------|
| Total rows in MD report | ~367 |
| Batch size | **70** |
| Number of batches | **~6** |
| Est. tokens per batch | ~12K input + ~4K output |
| **Total for adjudication** | **~96K tokens** |

**Assessment:** ✅ **FULLY FEASIBLE**

6 batches at ~16K tokens each = ~96K tokens total, which is:
- **Reasonable cost** (~$0.01-0.02 per run)
- **Fewer API calls** (6 calls instead of 15, ~1-2 minutes)
- **Complete coverage** of all categorized items

### CRITICAL: Category Headers in Each Batch

When extracting batches, **each batch MUST include the category header** so the LLM knows which bucket the rows belong to.

**Example - If batch spans categories:**

```
Batch 1 (rows 1-70):
## VERIFIED - RECOMMENDED (count=35)
| Verdict  | Confidence | SupplierTitle | ...
| VERIFIED | 95         | ELBOW GREASE... | ...
[... 35 VERIFIED rows ...]

## VERIFIED - FILTERED OUT / EXCLUDED (count=6)
| Verdict      | Confidence | SupplierTitle | ...
| FILTERED_OUT | 93         | PHOODS FOIL... | ...
[... 6 rows ...]

## HIGHLY LIKELY - RECOMMENDED (count=192)
| Verdict       | Confidence | SupplierTitle | ...
| HIGHLY_LIKELY | 60         | METROPOLITAN BLUE... | ...
[... first 29 rows of HIGHLY_LIKELY ...]
```

```
Batch 2 (rows 71-140):
## HIGHLY LIKELY - RECOMMENDED (count=192) [CONTINUED from row 30]
| Verdict       | Confidence | SupplierTitle | ...
|---------------|------------|---------------|...
| HIGHLY_LIKELY | 75         | LONDON FRAGRANCES... | ...
[... next 70 rows of HIGHLY_LIKELY ...]
```

**Implementation:**
```python
def create_batch_with_headers(md_report, start_row, batch_size=70):
    """
    Extract batch of rows WITH category headers.
    If batch continues from previous category, include header + "[CONTINUED]"
    """
    batch_content = []
    current_category = None
    
    for row_idx in range(start_row, min(start_row + batch_size, total_rows)):
        row_category = get_row_category(row_idx)  # e.g., "VERIFIED - RECOMMENDED"
        
        # Add category header if new category or start of batch
        if row_category != current_category:
            if row_idx == start_row and not is_first_row_of_category(row_idx):
                # Batch starts mid-category
                batch_content.append(f"## {row_category} [CONTINUED from row {row_idx}]")
                batch_content.append(TABLE_HEADER)  # Column headers
            else:
                # New category starts
                batch_content.append(f"## {row_category}")
                batch_content.append(TABLE_HEADER)
            current_category = row_category
        
        batch_content.append(get_row_content(row_idx))
    
    return "\n".join(batch_content)
```

✅ **I AGREE** with processing all MD report rows in batches of 70 with category headers.

---

### PART 2: Tool-Based File Access for Comprehensive Adjudication & Critique

**Your Proposal:**
LLM has ACCESS to (not full content in prompt):
- MD Report
- Deterministic analysis script
- Excel file (for Critique)

**Implementation Approach:**

```python
# Instead of dumping files into prompt, provide TOOLS:

tools = [
    {
        "name": "read_md_report_section",
        "description": "Read a specific section from the MD report",
        "parameters": {
            "section": "VERIFIED | HIGHLY_LIKELY | NEEDS_VERIFICATION | FILTERED_OUT"
        }
    },
    {
        "name": "search_analysis_script",
        "description": "Search for logic in the deterministic analysis script",
        "parameters": {
            "query": "pack detection | brand matching | ean validation | bucket assignment"
        }
    },
    {
        "name": "lookup_excel_row",
        "description": "Lookup specific row(s) from source Excel by row_id",
        "parameters": {
            "row_ids": [101, 445, 892]
        }
    },
    {
        "name": "search_excel_by_criteria",
        "description": "Search Excel for rows matching criteria",
        "parameters": {
            "column": "SupplierTitle | AmazonTitle | SupplierEAN",
            "contains": "search_term"
        }
    }
]
```

**Benefits:**
- ✅ No context window explosion
- ✅ LLM retrieves only what it needs
- ✅ More accurate analysis (focused context)
- ✅ Can handle any file size

**My Assessment:** ✅ **EXCELLENT APPROACH**

This is the correct way to "give access" - the LLM has tools to query files on demand, not receive everything upfront.

---

### PART 3: Mandatory Removal - Profit-Based Selection Criteria

**Your Explicit Instruction:**
> "NET PROFIT/ROI WILL NEVER BE A DEFINING FILTER - WHICH DECIDES IF PRODUCT ROW WILL BE INCLUDED OR NOT"

**Current Code That Violates This:**
```python
# adjudication.py - select_candidates():
if row.get("adjusted_profit", 0) > 10 and row.get("confidence", 0) < 65:
    candidates.append(row_id)  # ← VIOLATES YOUR POLICY
```

**Action Required:** 
- ❌ REMOVE all profit-based selection thresholds (> £10, etc.)
- ✅ KEEP only profit > £0 check (unprofitable = don't recommend)

**Corrected Selection Criteria:**
```python
# ALLOWED selection criteria:
# - Pack verdict = "ambiguous" or "uncertain"
# - Mid-range confidence (45-70)
# - Currently in NEEDS_VERIFICATION
# - Currently in HIGHLY_LIKELY with edge-case signals

# NOT ALLOWED:
# - profit > £X (any threshold other than > 0)
# - ROI > X%
```

✅ **I FULLY AGREE** - Will remove all profit-based selection criteria.

---

### PART 4: Revised Workflow Flow

Based on your description, here is my understanding of the corrected flow:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: AI ADJUDICATION (Per-Batch)                                        │
│                                                                             │
│ Input:  ALL rows from MD report (~367 rows)                                │
│         Batches of 70 rows (with category headers)                         │
│         ~6 API calls                                                        │
│                                                                             │
│ For each batch, LLM analyzes:                                              │
│ - Is the bucket assignment correct?                                        │
│ - Any obvious mismatches?                                                  │
│ - Pack size issues?                                                        │
│ - Brand matching issues?                                                   │
│                                                                             │
│ Output: Combined analyses for all batches                                  │
│         (Saved with reference to which MD report it analyzed)              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: COMPREHENSIVE ADJUDICATION                                          │
│                                                                             │
│ Input:                                                                      │
│ - Combined adjudication analyses (from Step 5)                             │
│ - Reference to MD report (can query sections via tool if needed)           │
│ - ACCESS TO DETERMINISTIC SCRIPT (via tool, not in prompt)                 │
│                                                                             │
│ Process:                                                                    │
│ - Reviews all batch analyses                                               │
│ - Identifies PATTERNS across all products                                  │
│ - When pattern detected → uses tool to read relevant script section        │
│ - Identifies ROOT CAUSE in script logic                                    │
│                                                                             │
│ Output (Comprehensible Feedback):                                          │
│ 1) Products to REMOVE or RECATEGORIZE                                      │
│ 2) Script FIXES needed (with specific function/line references)            │
│ 3) Missing entries that can be retrieved from Excel (if detected)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: AI CRITIQUE (Decision Maker)                                       │
│                                                                             │
│ Input:                                                                      │
│ - Comprehensible Feedback (from Step 6)                                    │
│ - ACCESS TO: MD report, Excel, Deterministic script (via tools)            │
│                                                                             │
│ Critique can:                                                              │
│ - Query MD report sections to verify suggestions                           │
│ - Look up specific Excel rows if needed                                    │
│ - Search script to validate fix suggestions                                │
│ - RETRIEVE MISSING ENTRIES directly from Excel (for simple fixes)          │
│                                                                             │
│ Decision Tree:                                                             │
│                                                                             │
│ 1) Product changes (removals/recategorizations)                            │
│    → Apply directly to MD report                                           │
│                                                                             │
│ 2) Missing entries identified?                                             │
│    → If SIMPLE FIX: Retrieve from Excel + Add to report → FINALIZE         │
│    → No need for iteration 2                                               │
│                                                                             │
│ 3) Deep script issues (logic bugs, systemic errors)?                       │
│    → REQUIRES ITERATION 2 (script fixes needed)                            │
│    → Apply fixes → Re-run deterministic analysis                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
          ┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
          │ No Issues /     │ │ QUICK FIX:    │ │ DEEP ISSUES:    │
          │ Simple Changes  │ │ Retrieve from │ │ Script Fixes    │
          │ → FINALIZE      │ │ Excel + Add   │ │ → ITERATION 2   │
          └─────────────────┘ │ → FINALIZE    │ └────────┬────────┘
                              └───────────────┘          │
                                                         ▼
                                    ┌─────────────────────────────────────────┐
                                    │ REGRESSION CHECK                        │
                                    │                                         │
                                    │ Compare:                                │
                                    │ - Report v1 stats vs Report v2 stats   │
                                    │                                         │
                                    │ If WORSENED:                            │
                                    │ → Return Report v1                      │
                                    │ → Note: "Iteration attempted but failed"│
                                    │                                         │
                                    │ If IMPROVED or UNCLEAR:                 │
                                    │ → Return Report v2 (latest)             │
                                    │ → Note: "Iteration successful"          │
                                    └─────────────────────────────────────────┘
```

---

### PART 5: Tool Definitions for File Access

For Comprehensive Adjudication:
```python
comp_adj_tools = [
    # 1. Query MD report by section
    Tool("read_md_section", params=["section_name"]),
    
    # 2. Search deterministic script
    Tool("search_script", params=["query"]),  # Returns relevant code snippet
    
    # 3. Get specific function from script
    Tool("get_function", params=["function_name"]),  # e.g., "_extract_pack_size"
]
```

For Critique:
```python
critique_tools = [
    # All tools from comp_adj, PLUS:
    
    # 4. Lookup Excel rows
    Tool("lookup_excel_row", params=["row_ids"]),
    
    # 5. Search Excel
    Tool("search_excel", params=["column", "search_term"]),
    
    # 6. Get Excel statistics
    Tool("get_excel_stats", params=["column"]),  # e.g., count, unique values
]
```

---

### PART 6: Comprehensive Feedback Schema

Output from Comprehensive Adjudication:

```python
comprehensible_feedback = {
    # Part 1: Product-level changes
    "product_changes": [
        {
            "row_id": 892,
            "current_bucket": "VERIFIED",
            "action": "REMOVE",
            "reason": "Supplier: PAINT, Amazon: TV - completely unrelated",
            "evidence": "..."
        },
        {
            "row_id": 1023,
            "current_bucket": "FILTERED_OUT",
            "action": "RECATEGORIZE_TO",
            "new_bucket": "HIGHLY_LIKELY",
            "reason": "Same brand (MINKY), same product type",
            "evidence": "..."
        }
    ],
    
    # Part 2: Script fixes
    "script_fixes": [
        {
            "issue_pattern": "Dimension numbers read as pack sizes",
            "affected_count": 23,
            "sample_row_ids": [445, 892, 1203],
            "target_file": "analysis.py",
            "target_function": "_extract_pack_size",
            "current_logic_summary": "Regex matches any number pattern",
            "fix_description": "Add dimension shield check before treating number as pack",
            "suggested_code": "if re.match(...) and not _is_shielded(...):",
            "confidence": "high"  # high | medium | low
        }
    ],
    
    # Part 3: Config changes (non-code)
    "config_changes": [
        {
            "target": "dimension_shield_keywords",
            "action": "add",
            "values": ["inch", "cm", "mm"],
            "reason": "23 rows have 'X inch' being misread"
        }
    ],
    
    # Summary
    "summary": {
        "products_to_remove": 3,
        "products_to_recategorize": 11,
        "script_fixes_suggested": 2,
        "config_changes_suggested": 3,
        "overall_severity": "medium",  # high | medium | low
        "recommend_iteration_2": True
    },
    
    # Reference
    "source_md_report": "20260108_031613/PHASEA_MANUAL_REPORT_20260108.md"
}
```

---

### PART 7: Critique Decision Logic (with Quick-Fix Option)

**NEW: Quick-Fix Capability**

Critique can now perform **simple fixes directly** without triggering iteration 2:
- If missing entries can be retrieved from Excel → do it in this step
- Only trigger iteration 2 for **deep script issues** that require logic changes

```python
class CritiqueDecision:
    # After reviewing comprehensible feedback + using tools:
    
    def decide(self, feedback, tools):
        decisions = {
            "apply_product_changes": False,
            "quick_fixes_applied": [],
            "run_iteration_2": False,
            "iteration_2_reason": None
        }
        
        # ─────────────────────────────────────────────────────────────────────
        # Decision 1: Apply product changes (removals/recategorizations)
        # ─────────────────────────────────────────────────────────────────────
        if feedback["products_to_remove"] + feedback["products_to_recategorize"] > 0:
            # Verify a sample using tools
            sample_change = feedback["product_changes"][0]
            md_data = tools.read_md_section(sample_change["current_bucket"])
            excel_data = tools.lookup_excel_row([sample_change["row_id"]])
            
            if self._verify_change_is_valid(sample_change, md_data, excel_data):
                decisions["apply_product_changes"] = True
                decisions["product_changes_to_apply"] = feedback["product_changes"]
        
        # ─────────────────────────────────────────────────────────────────────
        # Decision 2: QUICK FIX - Retrieve missing entries from Excel
        # ─────────────────────────────────────────────────────────────────────
        if feedback.get("missing_entries"):
            for missing in feedback["missing_entries"]:
                # Check if this is a SIMPLE fix (can retrieve directly)
                if self._is_simple_retrieval(missing):
                    # Use tool to retrieve from Excel
                    excel_rows = tools.search_excel(
                        column=missing["search_column"],
                        search_term=missing["search_term"]
                    )
                    
                    if excel_rows:
                        # Add to report directly (no iteration 2 needed)
                        decisions["quick_fixes_applied"].append({
                            "type": "add_missing_entry",
                            "source": "excel_retrieval",
                            "rows_added": excel_rows,
                            "target_bucket": missing["suggested_bucket"]
                        })
                        
                        # Log the quick fix
                        log.info(f"Quick fix: Retrieved {len(excel_rows)} rows from Excel")
        
        # ─────────────────────────────────────────────────────────────────────
        # Decision 3: DEEP ISSUES - Trigger iteration 2 for script fixes
        # ─────────────────────────────────────────────────────────────────────
        if feedback.get("script_fixes"):
            for fix in feedback["script_fixes"]:
                # Classify the fix severity
                fix_severity = self._classify_fix_severity(fix)
                
                if fix_severity == "DEEP":
                    # This requires re-running the deterministic analysis
                    # Cannot be fixed by simple retrieval
                    decisions["run_iteration_2"] = True
                    decisions["iteration_2_reason"] = fix["issue_pattern"]
                    decisions["script_fixes_to_apply"] = [fix]
                    break  # One deep issue is enough to trigger iteration 2
                
                elif fix_severity == "SIMPLE":
                    # Config change or minor adjustment
                    # Can be applied without full re-run
                    decisions["quick_fixes_applied"].append({
                        "type": "config_change",
                        "fix": fix
                    })
        
        return decisions
    
    def _is_simple_retrieval(self, missing: dict) -> bool:
        """
        Determine if a missing entry issue can be fixed by simple Excel retrieval.
        
        SIMPLE (no iteration 2):
        - Missing product with known EAN
        - Missing product with known supplier title
        - Wrongly excluded item (just move to correct bucket)
        
        NOT SIMPLE (needs iteration 2):
        - Logic bug causing incorrect pack detection
        - Brand matching algorithm failure
        - Similarity calculation error
        """
        simple_types = ["missing_by_ean", "missing_by_title", "wrong_exclusion"]
        return missing.get("issue_type") in simple_types
    
    def _classify_fix_severity(self, fix: dict) -> str:
        """
        Classify if a script fix is DEEP (needs iteration 2) or SIMPLE.
        
        DEEP (trigger iteration 2):
        - Pack size detection logic bug
        - Bucket assignment logic error
        - Similarity calculation bug
        - Brand matching algorithm failure
        
        SIMPLE (apply directly):
        - Add keyword to shield list
        - Add brand alias
        - Adjust threshold value
        """
        deep_patterns = [
            "pack detection", "bucket assignment", "similarity", 
            "brand matching", "confirmed_match", "ean validation"
        ]
        
        issue = fix.get("issue_pattern", "").lower()
        target = fix.get("target_function", "").lower()
        
        if any(pattern in issue or pattern in target for pattern in deep_patterns):
            return "DEEP"
        
        return "SIMPLE"
```

---

### PART 8: Regression Check Implementation

```python
def regression_check(report_v1_path, report_v2_path):
    """
    Compare iteration 1 vs iteration 2 reports.
    Returns: ("IMPROVED" | "WORSENED" | "UNCLEAR", score, details)
    """
    
    v1_stats = extract_stats(report_v1_path)
    v2_stats = extract_stats(report_v2_path)
    
    # Compare bucket counts
    changes = {
        "verified": v2_stats["VERIFIED"] - v1_stats["VERIFIED"],
        "highly_likely": v2_stats["HIGHLY_LIKELY"] - v1_stats["HIGHLY_LIKELY"],
        "needs_ver": v2_stats["NEEDS_VERIFICATION"] - v1_stats["NEEDS_VERIFICATION"],
        "filtered": v2_stats["FILTERED_OUT"] - v1_stats["FILTERED_OUT"],
    }
    
    # Improvement scoring:
    # + items moving UP the funnel (filtered → needs_ver → highly_likely → verified)
    # - items moving DOWN the funnel
    
    score = 0
    score += changes["verified"] * 3          # Verified gains = very good
    score += changes["highly_likely"] * 2     # HL gains = good
    score -= changes["needs_ver"] * 0.5       # More uncertainty = slightly bad
    score -= changes["filtered"] * 0.1        # More filtered = slightly bad (unless correct)
    
    if score > 5:
        return "IMPROVED", score, changes
    elif score < -5:
        return "WORSENED", score, changes
    else:
        return "UNCLEAR", score, changes


def iteration_loop(max_iterations=2):
    """Main iteration loop with regression check."""
    
    # Run iteration 1
    report_v1, stats_v1 = run_iteration(iteration=1)
    
    # Get critique decision
    critique_decision = run_critique(report_v1)
    
    if critique_decision.run_iteration_2:
        # Apply script fixes
        apply_script_fixes(critique_decision.script_fixes_to_apply)
        
        # Run iteration 2
        report_v2, stats_v2 = run_iteration(iteration=2)
        
        # Regression check
        outcome, score, changes = regression_check(report_v1, report_v2)
        
        if outcome == "WORSENED":
            # ROLLBACK to v1
            final_report = report_v1
            user_note = f"""
⚠️ ITERATION 2 ATTEMPTED BUT WORSENED
Score: {score}
Changes: {changes}

Returning INITIAL report. Please review what happened.
The script fixes that were applied:
{json.dumps(critique_decision.script_fixes_to_apply, indent=2)}
            """
        else:
            # Use v2
            final_report = report_v2
            user_note = f"""
✓ ITERATION 2 {'IMPROVED' if outcome == 'IMPROVED' else 'COMPLETED (unclear if better)'}
Score: {score}
Changes: {changes}
            """
    else:
        final_report = report_v1
        user_note = "Single iteration - no script fixes applied."
    
    return final_report, user_note
```

---

## SUMMARY: MY ASSESSMENT OF YOUR PROPOSAL

| Proposed Change | Feasibility | Improvement | My Verdict |
|-----------------|-------------|-------------|------------|
| Process ALL MD report rows (~367, not 2789) | ✅ Easy | ✅ HIGH | **AGREE** |
| Batches of 70 (with category headers) | ✅ Easy | ✅ Optimal | **AGREE** |
| Remove profit-based selection | ✅ Easy | ✅ CRITICAL | **AGREE 100%** |
| Pass adjudication to comprehensive | ✅ Easy | ✅ HIGH | **AGREE** |
| Tool-based file access (not full dump) | ✅ Correct approach | ✅ HIGH | **AGREE** |
| Comprehensive outputs: removals + script fixes | ✅ Easy | ✅ HIGH | **AGREE** |
| Critique quick-fix: retrieve from Excel directly | ✅ Smart | ✅ HIGH | **AGREE** |
| Critique iteration 2: only for deep script issues | ✅ Efficient | ✅ HIGH | **AGREE** |
| Regression check loop | ✅ Easy | ✅ CRITICAL | **AGREE** |

### NO DISAGREEMENTS

After understanding your correct intent:
- **MD report rows (~367)** instead of Excel rows (2789) → Token cost is manageable
- **Tool-based access** instead of prompt dump → Correct approach
- **Profit never decides inclusion** → Correct policy

---

## IMPLEMENTATION CHECKLIST

**Status:** Core items IMPLEMENTED in v4.3.0 (2026-01-08 20:25 UTC+4)

1. ✅ **Remove profit-based selection criteria** from `adjudication.py` - **DONE**
2. ✅ **Modify Step 5 (Adjudication)** to: - **DONE**
   - Read MD report instead of ledger
   - Process ALL rows in batches of **70 with category headers**
   - Save combined analyses with report reference
3. ✅ **Modify Step 6 (Comprehensive Adjudication)** to: - **DONE**
   - Receive adjudication analyses (adjudication_results parameter)
   - ⏳ Add tools for file access (MD, script) - *Future enhancement*
   - ⏳ Output comprehensible feedback schema - *Future enhancement*
   - ⏳ Identify missing entries that can be retrieved from Excel - *Future enhancement*
4. ⏳ **Modify Step 7 (Critique)** - *Future enhancement*
   - Receive comprehensible feedback
   - Add tools for file access (MD, script, Excel)
   - Quick-fix capability (retrieve from Excel directly)
   - Only trigger iteration 2 for deep script issues
5. ⏳ **Add Regression Check** after iteration 2 - *Future enhancement*
6. ⏳ **Add Rollback Logic** if iteration 2 worsens - *Future enhancement*

---

**END OF ANALYSIS REPORT - v4.3.0 IMPLEMENTED**

*Core fixes applied. Future enhancements marked with ⏳.*
