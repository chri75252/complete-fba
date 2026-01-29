# AI CRITIQUE ENHANCED ARCHITECTURE PROPOSAL
# Generated: 2026-01-11
# Purpose: Tool-based access for comprehensive final validation

## OVERVIEW

This document proposes an enhanced AI Critique architecture that allows the LLM
to access files on-demand (without sending full content upfront), validate the
MD report, and either finalize or recommend changes.

---

## 1. FILES AI CRITIQUE NEEDS ACCESS TO

| File | Purpose | Size | Access Method |
|------|---------|------|---------------|
| Source Excel | Verify missed products, lookup row data | 3,063 rows | Tool-based query |
| MD Report | Validate entries, check formatting | ~400 rows | Section-based read |
| coverage_ledger.csv | All analysis results | 3,063 rows | Tool-based query |
| evidence.jsonl | Detailed match evidence | 3,063 objects | Tool-based query |
| run_summary.json | Run metadata, bucket counts | ~200 lines | Full read (small) |
| iteration_details.json | Anomalies, critiques | Variable | Full read (small) |
| analysis.py | Deterministic logic (for fix suggestions) | ~300 lines | Section/function read |
| calibration config | Shield keywords, thresholds | ~50 lines | Full read (small) |

---

## 2. PROPOSED TOOL DEFINITIONS

```python
CRITIQUE_TOOLS = [
    # ========== EXCEL ACCESS TOOLS ==========
    {
        "name": "lookup_excel_rows",
        "description": "Fetch specific rows from source Excel by row_id",
        "parameters": {
            "row_ids": {"type": "array", "items": {"type": "integer"}},
            "columns": {"type": "array", "items": {"type": "string"}, "optional": True}
        },
        "max_rows": 50  # Safety limit
    },
    {
        "name": "search_excel",
        "description": "Search Excel for rows matching a criteria",
        "parameters": {
            "column": {"type": "string"},  # e.g., "SupplierTitle", "EAN"
            "contains": {"type": "string"},  # Search term
            "limit": {"type": "integer", "default": 20}
        }
    },
    {
        "name": "get_excel_statistics",
        "description": "Get statistics about a column (count, unique, etc.)",
        "parameters": {
            "column": {"type": "string"},
            "filter_bucket": {"type": "string", "optional": True}
        }
    },
    
    # ========== MD REPORT TOOLS ==========
    {
        "name": "read_md_section",
        "description": "Read a specific section of the MD report",
        "parameters": {
            "section": {
                "type": "string",
                "enum": ["VERIFIED", "VERIFIED_AUDITED_OUT", "HIGHLY_LIKELY", 
                         "HIGHLY_LIKELY_AUDITED_OUT", "NEEDS_VERIFICATION", "SUMMARY"]
            }
        }
    },
    {
        "name": "search_md_report",
        "description": "Search MD report for entries containing text",
        "parameters": {
            "search_term": {"type": "string"},
            "section": {"type": "string", "optional": True}
        }
    },
    
    # ========== LEDGER ACCESS TOOLS ==========
    {
        "name": "query_ledger",
        "description": "Query the analysis ledger with filters",
        "parameters": {
            "bucket": {"type": "string", "optional": True},
            "min_confidence": {"type": "integer", "optional": True},
            "max_confidence": {"type": "integer", "optional": True},
            "ean_match": {"type": "boolean", "optional": True},
            "limit": {"type": "integer", "default": 30}
        }
    },
    {
        "name": "get_ledger_row",
        "description": "Get full details for specific ledger rows",
        "parameters": {
            "row_ids": {"type": "array", "items": {"type": "integer"}}
        }
    },
    
    # ========== ANALYSIS SCRIPT TOOLS ==========
    {
        "name": "read_script_function",
        "description": "Read a specific function from analysis.py",
        "parameters": {
            "function_name": {"type": "string"}  # e.g., "_extract_pack_size"
        }
    },
    {
        "name": "search_script",
        "description": "Search analysis.py for code containing pattern",
        "parameters": {
            "pattern": {"type": "string"}  # e.g., "pack", "ean", "brand"
        }
    },
    
    # ========== ACTION TOOLS ==========
    {
        "name": "add_product_to_report",
        "description": "Add a product row to the MD report",
        "parameters": {
            "row_id": {"type": "integer"},
            "target_section": {"type": "string"},
            "justification": {"type": "string"}
        }
    },
    {
        "name": "remove_product_from_report",
        "description": "Remove a product row from the MD report",
        "parameters": {
            "row_id": {"type": "integer"},
            "reason": {"type": "string"}
        }
    },
    {
        "name": "recategorize_product",
        "description": "Move a product to a different section",
        "parameters": {
            "row_id": {"type": "integer"},
            "from_section": {"type": "string"},
            "to_section": {"type": "string"},
            "reason": {"type": "string"}
        }
    },
    {
        "name": "propose_script_fix",
        "description": "Propose a fix to the deterministic analysis script",
        "parameters": {
            "target_function": {"type": "string"},
            "issue_description": {"type": "string"},
            "affected_row_ids": {"type": "array", "items": {"type": "integer"}},
            "suggested_fix": {"type": "string"},
            "severity": {"type": "string", "enum": ["critical", "high", "medium"]}
        }
    },
    {
        "name": "finalize_report",
        "description": "Mark the report as finalized and complete",
        "parameters": {
            "summary": {"type": "string"},
            "changes_made": {"type": "array", "items": {"type": "string"}}
        }
    }
]
```

---

## 3. AI CRITIQUE WORKFLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: INITIAL ANALYSIS (LLM receives summary, not full files)           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ System Prompt:                                                               │
│ "You are an expert FBA analyst performing final validation.                  │
│  You have access to tools to query files. DO NOT ask for full files.        │
│  Use tools to fetch specific data as needed."                                │
│                                                                              │
│ User Prompt:                                                                 │
│ "Here's the run summary:                                                     │
│  - Total rows: 3,063                                                         │
│  - VERIFIED: 34 (6 audited out)                                              │
│  - HIGHLY_LIKELY: 186 (45 audited out)                                       │
│  - NEEDS_VERIFICATION: 86                                                    │
│  - FILTERED_OUT: 2,705                                                       │
│                                                                              │
│  Pre-computed contradictions detected:                                       │
│  - 6 rows have matching EANs but are in FILTERED_OUT                         │
│  - 3 rows have VERIFIED track but include_in_tables=False                    │
│                                                                              │
│  What would you like to investigate?"                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: TOOL-BASED INVESTIGATION (Multi-turn)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ LLM Response Turn 1:                                                         │
│ "I need to investigate the 6 EAN matches in FILTERED_OUT."                   │
│ Tool Call: query_ledger(bucket="FILTERED_OUT", ean_match=True)               │
│                                                                              │
│ Tool Returns: [                                                              │
│   {"row_id": 1847, "supplier_ean": "5060357991357", ...},                    │
│   {"row_id": 2103, "supplier_ean": "5014749165598", ...},                    │
│   ... (6 rows)                                                               │
│ ]                                                                            │
│                                                                              │
│ LLM Response Turn 2:                                                         │
│ "These have adjusted_profit <= 0. Let me verify they're in AUDITED_OUT."     │
│ Tool Call: read_md_section(section="VERIFIED_AUDITED_OUT")                   │
│                                                                              │
│ Tool Returns: [6 rows in AUDITED_OUT section]                                │
│                                                                              │
│ LLM Response Turn 3:                                                         │
│ "Good - they ARE in the report. Now let me check for missed products        │
│  in FILTERED_OUT that might have valid matches."                             │
│ Tool Call: query_ledger(bucket="FILTERED_OUT", min_confidence=60, limit=20)  │
│                                                                              │
│ ... (continues investigation)                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: DECISION & ACTIONS                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ OPTION A: MINOR FIXES → FINALIZE                                             │
│ ──────────────────────────────────                                           │
│ If issues are fixable by adding/removing/recategorizing a few products:     │
│                                                                              │
│ LLM: "I found 3 products incorrectly excluded. Adding them to report."       │
│ Tool Calls:                                                                  │
│   - add_product_to_report(row_id=2451, target_section="HIGHLY_LIKELY", ...)  │
│   - add_product_to_report(row_id=2789, target_section="HIGHLY_LIKELY", ...)  │
│   - remove_product_from_report(row_id=1502, reason="Different variant")      │
│   - finalize_report(summary="Fixed 4 issues", changes_made=[...])            │
│                                                                              │
│ Result: MD report updated, marked as FINALIZED                               │
│                                                                              │
│ ──────────────────────────────────                                           │
│ OPTION B: SYSTEMIC ISSUES → PROPOSE FIXES                                    │
│ ──────────────────────────────────                                           │
│ If issues require script logic changes:                                      │
│                                                                              │
│ LLM: "I found 47 products with dimension trap issues. Need script fix."      │
│ Tool Calls:                                                                  │
│   - read_script_function(function_name="_extract_pack_size")                 │
│   - propose_script_fix(                                                      │
│       target_function="_extract_pack_size",                                  │
│       issue_description="Dimensions like '9x9 inch' parsed as 81 pack",      │
│       affected_row_ids=[123, 456, 789, ...],                                 │
│       suggested_fix="Add check: if 'inch' in text, skip pack extraction",   │
│       severity="critical"                                                    │
│     )                                                                        │
│                                                                              │
│ Result: Script fix proposal saved, agent run marked as NEEDS_ITERATION       │
│                                                                              │
│ ──────────────────────────────────                                           │
│ OPTION C: CRITICAL ISSUES → BLOCK                                            │
│ ──────────────────────────────────                                           │
│ If issues are too severe and numerous to fix in-session:                     │
│                                                                              │
│ LLM: "Found 200+ systemic errors. This needs human review."                  │
│ Result: Agent run marked as BLOCKED, report is DRAFT                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. REGARDING ITERATION STEP

### Current Design (With Manual Script Edits)
```
Iteration 1: Deterministic → AI Review → Propose Fixes
     ↓
Human/Gemini applies script fixes
     ↓
Iteration 2: Deterministic (with fixes) → AI Review → Finalize
```

### Proposed Design (With Config-Only Adjustments)
```
Iteration 1: Deterministic → AI Critique → Propose Config Changes
     ↓ (automatic)
Apply config changes (shield tokens, thresholds, brand aliases)
     ↓ (automatic)
Iteration 2: Deterministic (with new config) → AI Critique → Finalize
```

### Recommendation: KEEP ITERATION STEP BUT MAKE IT CONFIG-BASED

**Why:**
1. Script changes are risky and require human oversight
2. BUT many issues CAN be fixed via configuration:
   - Add "inch", "mm", "cm" to dimension_shield_keywords
   - Add brand aliases for missed brands
   - Adjust title_match_threshold by ±0.05

**Workflow:**
1. AI Critique detects issues
2. If fixable by config → Apply config, run Iteration 2 automatically
3. If requires script change → Propose fix, BLOCK, wait for human
4. After human applies script fix → User runs agent again (new run, not iteration)

---

## 5. IMPLEMENTATION CHECKLIST

### Phase 1: Tool Implementation (Immediate)
- [ ] Create `critique_tools.py` with tool function implementations
- [ ] Integrate with OpenAI function calling API
- [ ] Add tool result handling loop

### Phase 2: Action Tools (Next Sprint)
- [ ] Implement `add_product_to_report()` - modifies ledger + MD
- [ ] Implement `remove_product_from_report()` - modifies ledger + MD
- [ ] Implement `recategorize_product()` - moves between sections

### Phase 3: Script Analysis Tools (Future)
- [ ] Implement `read_script_function()` using AST parsing
- [ ] Implement `search_script()` for pattern matching
- [ ] Implement `propose_script_fix()` for structured recommendations

---

## 6. TOKEN EFFICIENCY COMPARISON

### Current (Without Tools)
| What's Sent | Tokens |
|-------------|--------|
| All VERIFIED rows (34) | ~3,400 |
| All HIGHLY_LIKELY rows (186) | ~18,600 |
| Sample NEEDS_VERIFICATION (20) | ~2,000 |
| Filtered summary | ~500 |
| Pre-computed issues | ~1,000 |
| **TOTAL PER CRITIQUE CALL** | **~25,500** |

### With Tool-Based Access
| What's Sent | Tokens |
|-------------|--------|
| Initial summary | ~500 |
| Tool call overhead | ~200/call |
| Fetched data (on-demand) | ~1,000-5,000 |
| **TOTAL (typical critique)** | **~5,000-10,000** |

**Savings: 60-80% fewer tokens per critique**

---

## 7. CONCLUSION

The proposed architecture allows AI Critique to:

1. **ACCESS files on-demand** without sending everything upfront
2. **INVESTIGATE issues** by querying specific rows/sections
3. **FIX minor issues** by adding/removing/recategorizing products
4. **PROPOSE script fixes** when config changes aren't enough
5. **FINALIZE** when report is validated

The iteration step remains valuable for **config-based adjustments** but **script changes should require human approval** (via me, Gemini, applying the changes).

---

Do you want me to proceed with implementing Phase 1 (Tool Implementation)?
