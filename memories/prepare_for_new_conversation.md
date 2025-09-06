# Prepare for New Conversation - System Audit Session

## Context Summary
**Task**: Comprehensive audit of Amazon FBA system implementation against Master Behavior Specification to determine which parts are correctly implemented vs incorrect/partial

**Current Status**: In progress - Started audit using Zen MCP and gathering evidence from logs and code files

## User's Original Request Summary

The user requested a comprehensive **Phase 1 audit** to verify which workflow steps are correct vs incorrect/partial against the **AMAZON_FBA_SYSTEM_MASTER_BEHAVIOR_SPECIFICATION.md**. This is preparation for Phase 2 where an older "stable" version will be cross-checked.

### Key Requirements:
1. **Determine exactly which parts of current system are implemented correctly** vs incorrectly/partial
2. **Audit against Master Spec** strictly - no assumptions
3. **Provide concrete evidence** for every assertion (code snippets, log excerpts, file paths)
4. **Focus on known problem areas** that were flagged as "under investigation"
5. **Use MCP tools** (Serena MCP for memory, Zen MCP for analysis) when available

### Files to Analyze:
- **Logs**: Recent full run logs showing "starts at category ~93" behavior and invariant violations
- **State files**: `poundwholesale_co_uk_processing_state.json`, manifests, `linking_map.json`
- **Core codebase**:
  - `tools/passive_extraction_workflow_latest.py` (category loop, manifest population, filtering)
  - `utils/fixed_enhanced_state_manager.py` (progression updates, resume/fresh-start)
  - `utils/url_filter.py` (linking map vs cache classification)
- **Spec docs**: Master behavior specification and implementation memories

### Steps to Audit (1:1 mapping to master spec):

**Phase 1 - Supplier-side (Category-level)**
1. **1.1 URL Discovery & Extraction** - Page scraping, URL normalization, stored in category_manifests
2. **1.2 Linking-Map Comparison** - O(1) hash lookup, completed URLs excluded
3. **1.3 Product Cache Comparison** - O(1) hash lookup, cached items skip supplier but queue for Amazon
4. **1.4 Supplier Data Extraction** - Only needs_supplier_extraction, atomic per-product saves

**Phase 2 - Amazon Processing (Category-level)**
1. **2.1 Amazon Queue Compilation** - Combined queue from needs_amazon_only + newly extracted
2. **2.2 Amazon Detail Extraction** - EAN search then title fallback, linking-map atomic saves
3. **2.3 Category Completion** - Increment category index, reset product index, save state

**Phase 3 - Category Loop Continuation**
- Absolute resume offset honored across batches, no batch-relative leakage

**State & Resume Semantics**
- **Fresh-start**: Seeds system_progression at index 0, zeros auxiliary counters
- **Resume**: update_progression_unified never overwritten by stale supplier_extraction_progress
- **Invariant validation**: Resume mismatches as warnings, not hard stops

**Filtering Transparency**
- Clear logging of linking-map vs URL cache vs product cache checks
- Filter invariant: skip + needs_amazon_only + needs_supplier_extraction == total_input

### Problem Focus Areas (Flagged as "Under Investigation")
**Must default to "UNDER INVESTIGATION" until proven with all 3 proofs**: code + logs + artifacts

1. **Absolute resume offset in category loop** - Must compute category_index = start_index + (batch * batch_size) + subindex
2. **update_progression_unified stale-overwrite bug** - New kwargs must not be overwritten by stale supplier_extraction_progress
3. **Invariant calibration on resume** - Resume product_count_consistency mismatch must be warning, not critical
4. **Fresh-start semantics** - Start at index 0 and zero auxiliary cursors (last_processed_index, progress_index, resumption_index)
5. **reset_category_accumulators contract** - Accepts only category_index, preserves total_categories, writes absolute index
6. **Save after every meaningful progression update** - Every update_progression_unified followed by save_state
7. **Discovery denominators recorded pre-filter** - update_discovered_products_in_category before filtering
8. **Per-product supplier cache saves** - Frequency-controlled atomic saves inside loop
9. **Mark cached-only categories complete** - If no work needed, call mark_category_completed
10. **Filtering transparency** - Explicit bucket logging with counts
11. **Category manifests populated prior to filtering** - URL list stored and saved before filtering/Amazon
12. **Atomic saves on all critical artifacts** - WindowsSaveGuardian usage verified
13. **Fresh-start detection avoids heuristics** - No smart resume heuristics unless explicit config

## Progress Made So Far

### ✅ Completed:
1. **Read Master Behavior Specification** - Full specification loaded and understood
2. **Read Implementation Memory** - 13 critical fixes implementation report accessed
3. **Started Zen MCP Analysis** - Initiated comprehensive system analysis (step 1/5)
4. **Located Recent Logs** - Found logs from August 20-22, 2025 runs
5. **Started Log Analysis** - Began reading most recent log (20250822_120846.log)

### 🔍 Evidence Gathered So Far:
- **Log Evidence**: Found fresh start behavior in recent log - system starts at category 0, not 93
- **Configuration**: Hybrid processing enabled with chunked mode
- **State Management**: SP-first implementation appears active
- **URL Discovery**: "always run" logging present
- **Hash Optimization**: O(1) lookups working (8819 entries, 0.327s build time)

### ⏭️ Next Steps Needed:
1. **Continue systematic evidence collection** for each audit step
2. **Search for "category 93" behavior** in logs to understand the reported problem
3. **Examine state files** (processing_state.json) for resume behavior evidence
4. **Continue Zen MCP analysis** (step 2/5) with concrete findings
5. **Use Zen Debug/Tracer** to identify specific problem points
6. **Document findings** in Problem Focus Matrix format
7. **Generate Working Implementations Index** for Phase 2

### 🎯 Expected Output Format:
**Single detailed audit report with:**
- **A. Executive snapshot** - Count of CORRECT/PARTIAL/INCORRECT steps
- **B. Per-step findings** - Spec reference + code proof + runtime proof + verdict
- **C. Working Implementations Index** - Only correct/complete snippets with paths/symbols  
- **D. Gaps Summary** - Incorrect/partial items
- **E. Appendix** - MCP analysis summaries and memory cards

## Key Instructions to Continue

### Investigation Priority:
1. **Search logs for actual "category 93" behavior** that user mentioned
2. **Use Zen MCP tools systematically**: debug, tracer, analyze for evidence gathering
3. **Apply "Under Investigation" default** to all 13 problem focus areas until proven
4. **Require all 3 proof types** for any "CORRECT" verdict: code + logs + artifacts
5. **Focus on systematic evidence collection** rather than speculation

### Evidence Standards:
- **Code Proof**: File path + function/class + 10-30 line snippets
- **Log Proof**: Timestamps and exact log excerpts showing behavior
- **Artifact Proof**: JSON fragments from state files, manifests, linking maps
- **Spec Reference**: Quote relevant section and summarize requirement

### Tools to Use:
- **Zen MCP**: analyze, debug, tracer, codereview for systematic investigation
- **Serena MCP**: write_memory to persist confirmed findings for Phase 2
- **Standard tools**: Read, Grep, Glob for file analysis

## Context for Next Assistant

Continue the comprehensive audit where left off. The user wants **hard evidence** for every finding, not assumptions. Use the MCP tools systematically to gather proof and maintain the "Under Investigation" default for problem areas until all 3 proof types are provided.

The goal is a definitive audit report that can guide Phase 2 integration work with complete confidence in what is working vs broken.