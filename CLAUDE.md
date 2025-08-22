REFER TO TO[Testing Plan]/tEMPLATE WHENEVER i EXPLICETELY ASK YOU TO USE MULTI-AGENTS/WORKTRESS (testing_plan.md)  <!-- keep on one line so Claude loads it after /compact -->

🚨 **MASTER_PLAN_REFERENCE**: ALWAYS refer to ".serena/memories/AMAZON_FBA_SYSTEM_MASTER_BEHAVIOR_SPECIFICATION.md" for comprehensive implementation context and system workflow understanding when context window limits hit

🚨 **SERENA_MCP_PROGRESSIVE_MEMORY**: After each major implementation step or fix completion, generate a comprehensive memory file using Serena MCP that references the latest implementation AND provides a complete summary of all previous implementations completed (including what they consisted of and what files were edited for each) to maintain full context for future chat sessions

# CLAUDE.MD - Amazon FBA Agent System v3.7+ File Organization & Development Standards

## 🚨 CLAUDE_DIRECTIVES - EXECUTE IMMEDIATELY

### **🚨 CRITICAL TESTING & VERIFICATION STANDARDS:**
- 🚨 **MANDATORY_FIX_TESTING**: WHENEVER A FIX IS IMPLEMENTED YOU MUST THOROUGHLY TEST YOUR FIXES
- 🚨 **NO_CLAIMS_WITHOUT_VERIFICATION**: Tasks cannot be marked complete without actual verification
- 🚨 **MANDATORY_FILE_VERIFICATION_PROTOCOL**: For any future response whenever referencing files (primarily output files, scripts, folders, subfolders, etc.) you MUST:
  1. ✅ **VERIFY_ACTUAL_EXISTENCE**: Check file/directory actually exists at specified path
  2. ✅ **CHECK_TIMESTAMP**: Verify file creation/modification timestamp and confirm it's recent/relevant
  3. ✅ **VERIFY_CONTENT**: Read and analyze actual file content before making any claims about what it contains
  4. ✅ **CONFIRM_CORRECT_SUPPLIER**: Ensure files reference the correct supplier (poundwholesale.co.uk, NOT clearance-king.co.uk)
  5. ✅ **PROVIDE_FULL_PATHS**: Always provide complete absolute directory paths, timestamps, and content verification
  6. ✅ **NO_ASSUMPTIONS**: Never reference files without first reading and verifying their actual content and relevance
- 🚨 **MANDATORY_BACKUP_PROTOCOL**: Before testing any script, parameter, toggle, or making major edits that might affect functionality:
  1. ✅ **CREATE_BACKUP_DIRECTORY**: Create a "backup" folder in the same directory if it doesn't exist
  2. ✅ **DATED_SUBFOLDER**: Create subfolder titled with brief reason + date (e.g., "clear_cache_toggle_test_20250701")
  3. ✅ **BACKUP_ALL_AFFECTED**: Copy ALL files/folders/scripts that might be affected by the test/change
  4. ✅ **VERIFY_BACKUP**: Confirm backup was created successfully before proceeding
- 🚨 **TASK_SUCCESS_CRITERIA**/**TASK_TESTING_CRITERIA**: For any task TESTING involving file/folder/script output through the use of full workflow or specific scripts to be considered successfully completed:
  1. ✅ **CORRECT_TIMESTAMP**: EVERY File must have accurate creation/modification timestamp based on the script or workflow involved in the test
  2. ✅ **CORRECT_FILE_PATH**: Exact absolute path must be verified and accessible and match the expected output location ( as per line 90 - 233 which the output tracker)
  3. ✅ **CORRCT_SCRIPT_EXECUTION_&_CHRONOLOGY**: Chekc if all exepcted script ran and in the correct order ( as per Workflow Diagram 12 - 138 which workflow diagram )
  3. ✅ **CONTENT_VERIFICATION**: File content must be analyzed and verified against expectations
- 🚨 **NO_FAKE_OUTPUTS**: Never claim file paths or content that haven't been actually verified
- 🚨 **ASK_FOR_SCREENSHOTS**: When fix involves verification you cannot perform (like LangSmith dashboard), explicitly ask user for screenshots

## 🔍 **CRITICAL INVESTIGATION METHODOLOGY - EXECUTE IMMEDIATELY**

### **🚨 LOGIC-FIRST DEBUGGING MANDATE**
- 🚨 **FUNDAMENTAL ASSUMPTION**: Existing architecture likely has necessary data and components
- 🚨 **PRIMARY FOCUS**: Logic interpretation gaps, NOT missing implementations  
- 🚨 **EVIDENCE REQUIREMENT**: Every proposed architectural change must be justified by proof that logic fixes won't work
- 🚨 **SURGICAL PREFERENCE**: Single-line logic corrections over multi-component integration

### **⚠️ MANDATORY INVESTIGATION SEQUENCE**
**🚨 EXECUTE IN ORDER - DO NOT SKIP STEPS:**

1. **📊 DATA FLOW TRACE**: What data exists and flows correctly? 
   - ✅ Read logs to identify where system shows success (data populated, operations completed)
   - ✅ Follow successful data through the system step-by-step
   - ✅ Document what data is available at each stage

2. **🔍 DECISION POINT ANALYSIS**: Where does correct data get ignored/misclassified?
   - ✅ Find the exact transition from "data exists" to "system fails"
   - ✅ Identify the specific conditional logic or workflow routing
   - ✅ Focus on if/else branches, classification rules, workflow decisions

3. **🎯 LOGIC BRANCH REVIEW**: What conditions cause wrong paths?
   - ✅ Examine the logic that determines system behavior
   - ✅ Look for classification errors, misinterpretation of data
   - ✅ Check workflow routing logic and decision trees

4. **🔧 MINIMAL FIX IDENTIFICATION**: What's the smallest logic change that fixes the flow?
   - ✅ Prefer single-line conditional changes
   - ✅ Focus on interpretation logic, not data generation
   - ✅ Use existing data structures and workflows

5. **🏗️ ARCHITECTURE CHANGES**: Only if steps 1-4 prove insufficient
   - ✅ Must provide concrete evidence that logic fixes are impossible
   - ✅ Document why existing architecture cannot support the fix
   - ✅ Justify the architectural complexity

### **🚨 INVESTIGATION RED FLAGS - STOP AND RECONSIDER**
- ❌ **Proposing callback systems** → Check if existing communication just needs logic fixes
- ❌ **Suggesting new components** → Verify existing components don't already have the data
- ❌ **Building integration layers** → Confirm the integration isn't just a conditional logic error
- ❌ **Tests pass but production fails** → Look for logic interpretation, not implementation gaps
- ❌ **"Missing implementation" conclusions** → Verify implementation doesn't exist but is bypassed

### **✅ KIRO-STYLE SPECIFICATION APPROACH**
**When conducting major investigations, ALWAYS create structured specifications:**

1. **📋 REQUIREMENTS.MD**: Define exactly what should happen vs. what is happening
   - ✅ User stories with acceptance criteria
   - ✅ Expected behavior vs. actual behavior
   - ✅ Success criteria with specific metrics

2. **🏗️ DESIGN.MD**: Document the investigation approach and solution architecture
   - ✅ Investigation methodology and steps
   - ✅ Root cause analysis framework
   - ✅ Solution options with trade-offs

3. **📝 TASKS.MD**: Break down implementation into atomic, verifiable tasks
   - ✅ Task dependencies and sequence
   - ✅ Verification criteria for each task
   - ✅ Risk mitigation and rollback plans

### **🎯 INVESTIGATION TEMPLATES**

#### **Logic Flow Tracing Template**
```
1. **What data is correctly generated?** [Log evidence: line X shows data Y]
2. **Where does correct data get dropped/ignored?** [Code location: file.py:line]
3. **What logic condition causes the drop?** [if/else branch, classification rule]
4. **What's the minimal fix?** [Single condition change, classification adjustment]
```

#### **Success-to-Failure Trace Template**  
```
1. **Success Point**: [Log line showing system working correctly]
2. **Failure Point**: [Log line showing system failing]  
3. **Decision Point**: [Code location between success and failure]
4. **Logic Fix**: [Minimal change to preserve success path]
```

### **🔍 EVIDENCE-DRIVEN DEBUGGING PHRASES**
**Use these investigation approaches:**
- ✅ "The system generates correct data but makes wrong decisions - trace the decision logic"
- ✅ "Assume all components work, find where good data gets misclassified" 
- ✅ "Focus on workflow routing and conditional logic, not component integration"
- ✅ "Look for single-line logic errors before proposing architectural changes"
- ✅ "The data exists but isn't being used correctly - find the interpretation gap"

## ⚠️ MANDATORY_PROTOCOLS

### 🚀 AGENT / TOOL INVOCATION QUICK‑START
## IMPROTANT

Refer to the *Awesome Claude Agents* orchestration protocol. 
- For any multi-step or feature development, START by invoking the `tech-lead-orchestrator`.
- WAIT for its structured routing map (named agents; specified order).
- Then, use ONLY the agents listed in the routing map, in the sequence, for each task.
- All information handoff and filtering is to be managed by the main agent, not by sub-agent-to-sub-agent calls.
Never improvise agent selection or skip the orchestrator step.


### **⚠️ UPDATE PROTOCOL - CRITICAL COMPLIANCE**
<!-- LOAD_FOR: ALL_COMPLEXITY_LEVELS -->
<!-- SELECTIVE: false -->

**⚠️ MANDATORY EXECUTION - Whenever you update ANY file, script, output, or folder:**

1. **⚠️ CASCADING UPDATES** (All complexity levels)
   - ✅ REQUIRED: Check ALL related files that reference the changed item
   - ✅ REQUIRED: Update ALL scripts that use the modified paths/functions
   - ✅ REQUIRED: Update ALL documentation that mentions the changed item
   - ✅ REQUIRED: Update ALL configuration files with new references

2. **⚠️ DOCUMENTATION SYNC** (Medium+ complexity)
   - ✅ REQUIRED: Update ALL relevant documentation in `docs/`
   - ✅ REQUIRED: Update README.md with new paths/procedures
   - ✅ REQUIRED: Update architecture diagrams if applicable
   - ✅ REQUIRED: Update troubleshooting guides with new references

3. **⚠️ PATH CONSISTENCY CHECK** (All complexity levels)
   - ✅ REQUIRED: Verify path_manager.py reflects changes
   - ✅ REQUIRED: Update system_config.json if paths changed
   - ✅ REQUIRED: Test that all scripts still work with new paths


### **🔧 SERENA MCP INTEGRATION - CODE ANALYSIS & EXPLORATION:**

**⚠️ PRIMARY FUNCTION: Serena MCP for continuous code analysis and exploration (READ-ONLY)**

**Current Configuration:** Amazon FBA Agent System v3.8+
- **Mode**: Read-Only (SAFE: Analysis only, no code modifications)
- **Primary Use**: Continuous code exploration, bug investigation, architecture analysis
- **Memory**: Enabled for storing findings and architectural insights

#### **Serena Core Analysis Tools (Always Available):**
- **get_symbols_overview**: Map class structures and methods
- **find_symbol**: Locate method/attribute definitions  
- **find_referencing_symbols**: Find usage patterns and dependencies
- **search_for_pattern**: Analyze code patterns and integration points
- **read_file**: Examine implementation details
- **write_memory/read_memory**: Store and retrieve investigation findings

#### **Serena Analysis Modes (Prompt-Driven):**
- **Diagnostic Mode**: `"Use diagnostic mode to trace processing state corruption"`
- **Forensic Mode**: `"Use forensic mode to follow authentication flow from start to failure"`
- **Exploratory Mode**: `"Use exploratory mode to map passive extraction workflow structure"`
- **Focused Mode**: `"Use focused mode to analyze only state management methods"`
- **Comprehensive Mode**: `"Use comprehensive mode for deep system architecture analysis"`

### **🎯 OPTIMAL WORKFLOW STRATEGY:**

#### **Phase 1: Investigation (Serena MCP - Continuous Use)**
```bash
# Safe exploration and analysis - use freely
get_symbols_overview([target_file])     # Map code structure
find_symbol([method_name])              # Verify symbols exist
search_for_pattern([error_pattern])     # Find patterns
write_memory("findings", "analysis")    # Store insights
```

#### **Phase 2: Implementation (ZEN MCP - Only When Explicitly Requested)**
```bash
# Use ONLY when user explicitly requests ZEN MCP tools
zen_debug() or zen_codereview()         # Expert-guided fixes
zen_thinkdeep() or zen_analyze()        # Complex reasoning
```

### **🚨 TOOL USAGE RULES:**
- ✅ **Serena MCP**: Use continuously for all code analysis, exploration, and investigation
- ⚠️ **ZEN MCP**: Use ONLY when explicitly requested by user during conversation
- 🔒 **Read-Only Safety**: Serena cannot break code - perfect for continuous exploration

### **🔧 ZEN MCP TOOLS AVAILABLE (Secondary):**
When Serena MCP is insufficient or user explicitly requests ZEN MCP tools:
- **thinkdeep**: Multi-stage comprehensive investigation and reasoning
- **debug**: Root cause analysis and systematic debugging
- **analyze**: Comprehensive code analysis and architectural assessment
- **codereview**: Step-by-step code review with expert analysis

### **MANDATORY_SESSION_INITIALIZATION:**
- 🚨 **SELECTIVE_FILE_ACCESS**: REQUIRED - Only read files when explicitly requested or necessary for specific tasks
- 🚨 **PATH_MANAGEMENT_ACTIVE**: REQUIRED - Ensure path_manager.py functions are used when working with paths

### **MANDATORY_ONGOING_BEHAVIOR:**
- ⚠️ **UPDATE_PROTOCOL_COMPLIANCE**: CRITICAL - Cascading updates for ANY file changes
- ⚠️ **DOCUMENTATION_SYNC**: Update ALL related docs when changes occur
- 🚨 **API_KEY_PRESERVATION**: CRITICAL - NEVER remove or modify existing API keys in scripts or env files
- 🚨 **SURGICAL_CODE_MODIFICATION_COMPLIANCE**: MANDATORY - Follow rules in `.kiro/steering/surgical-code-modification-rules.md`
- 🚨 **SERENA_MCP_PROTOCOL_COMPLIANCE**: MANDATORY - Use Serena MCP tools for all code analysis and modifications




## 🎯 LATEST SYSTEM ENHANCEMENTS (July 29, 2025)

### **🚨 P0 CRITICAL FIXES COMPLETED**
- **✅ UTF-8 ENCODING RESOLUTION**: Fixed `'charmap' codec can't decode byte 0x9d` errors system-wide
- **✅ PRODUCT CACHE PATH FIX**: Resolved state manager file location mismatch (dots vs hyphens)
- **✅ LINKING MAP SCHEMA STANDARDIZATION**: Consistent schema for all entry types (`match_method: "none"`, `confidence: 0`)
- **✅ FILE-GROUNDED STATE IMPLEMENTATION**: State calculations based on actual files, not memory variables
- **CRITICAL INSIGHT**: Character encoding issues indicate deeper architectural problems
- **CRITICAL INSIGHT**: Path consistency is fundamental to data integrity across system components
- **CRITICAL INSIGHT**: Complete schema coverage required - every processing outcome must be recorded
- **CRITICAL INSIGHT**: File-grounded state is essential for reliable recovery in long-running systems

### **🧹 SMART MEMORY MANAGEMENT SYSTEM**
- **✅ VERIFIED WORKING**: Smart memory clearing with sliding window approach prevents accumulation
- **Smart Cache Clearing**: Only clears when >500 products accumulated, keeps recent 100 for continuity
- **Sliding Window Approach**: Maintains processing continuity while preventing memory leaks
- **Linking Map Management**: Clears every 500 entries after saving to prevent memory leaks
- **Python Garbage Collection**: Triggered automatically when Python memory >3GB
- **Node.js Monitoring**: Monitors Node.js processes (>2GB triggers browser restart)
- **CRITICAL**: Files are NEVER cleared - only in-memory variables are cleared
- **Smart Memory Strategy**: Write to disk → Smart sliding window clear → Continue processing
- **Intelligent Clearing**: Only triggers when significant accumulation occurs (>500 products)
- **File-Based Progress Tracking**: Six methods for zero-risk progress monitoring from persistent files
- **Safe Memory Clearing**: `safe_memory_clear_with_file_fallback()` preserves critical counters while clearing large data structures
- **Authentication Tracking**: `get_authentication_fallback_count_from_state()` monitors products without pricing data
- **Comprehensive Progress**: `get_current_progress_from_files()` provides complete status with zero memory dependency

### **🔄 BROWSER RESTART SYSTEM**
- **✅ VERIFIED WORKING**: Automatic browser restart every 2.5 hours
- **Time-Based Restart**: Prevents authentication connection degradation
- **Memory-Based Restart**: Triggers on high Python/Node.js memory usage
- **Connection Recovery**: Automatic restart on connection timeouts
- **Zero Downtime**: ~2.7 second restart time with immediate recovery
- **Authentication Integration**: Restart triggers before category batch processing

### **🔐 AUTHENTICATION RESILIENCE**
- **Category Batch Authentication**: Checks authentication before each category batch
- **Connection Timeout Handling**: Automatic browser restart on CDP timeouts
- **Fallback Recovery**: Multiple authentication methods with graceful degradation
- **Session Persistence**: Maintains authentication across browser restarts

## 🧠 **CRITICAL LESSONS LEARNED FROM P0 FIXES**

### **🎯 NON-OBVIOUS TECHNICAL DISCOVERIES**

#### **1. Encoding Issues as System Architecture Indicators**
- **Discovery**: Character encoding problems reveal deeper architectural issues
- **Insight**: UTF-8 must be explicitly specified at every file boundary
- **Implication**: Treat encoding as first-class architectural concern
- **Best Practice**: Never rely on system default encodings in production code

#### **2. Path Consistency as Data Integrity Foundation**  
- **Discovery**: Inconsistent file naming cascades through entire system
- **Insight**: Centralized path management prevents systematic failures
- **Implication**: Single source of truth for all file path construction
- **Best Practice**: Standardize naming conventions at architectural level

#### **3. Complete Schema Coverage Principle**
- **Discovery**: Every processing outcome must be explicitly handled and recorded
- **Insight**: No-match scenarios are as important as successful matches
- **Implication**: Design schemas for complete operational coverage
- **Best Practice**: Create entries for all possible processing states

#### **4. File-Grounded State as Recovery Strategy**
- **Discovery**: Memory-based state becomes unreliable in long-running systems
- **Insight**: Persistent state must reflect actual file system reality
- **Implication**: Calculate state from persistent data, not memory variables
- **Best Practice**: Use files as single source of truth for system state

#### **5. Gap Processing as Efficiency Multiplier**
- **Discovery**: Processing decisions based on current state enable massive optimization
- **Insight**: System intelligence comes from understanding its own state
- **Implication**: Always analyze what work is actually necessary
- **Best Practice**: Implement gap detection for all bulk processing operations

### **🎯 DEBUGGING METHODOLOGY INSIGHTS**

#### **1. Systematic Issue Identification**
- **Method**: Start with observable symptoms, trace to root architectural causes
- **Key**: Don't fix symptoms, fix underlying architectural problems
- **Success Pattern**: P0 fixes addressed fundamental design issues, not surface problems

#### **2. File-First Debugging Approach**
- **Method**: Always verify actual file contents before making assumptions
- **Key**: System state must match file reality, not memory state
- **Success Pattern**: File-grounded state calculations eliminated state inconsistencies

#### **3. Schema-First Data Design**
- **Method**: Define complete schemas before implementation
- **Key**: Account for all possible outcomes, including failure cases
- **Success Pattern**: Standardized linking map schemas eliminated downstream errors


# Amazon FBA Agent System

This repository hosts the simplified Amazon FBA Agent workflow used to scrape supplier products, match them to Amazon listings and calculate profitability.

The process's emtry point in `run_custom_poundwholesale.py` and is orchestrated by `PassiveExtractionWorkflow` and progresses through authentication, supplier scraping, Amazon data extraction, financial analysis and state management.

See [docs/readme.md](docs/readme.md) for the full documentation and historical notes.

## Quick Start
```bash
# install dependencies
pip install -r requirements.txt

# run the workflow (Chrome must be running with debug port 9222)
python run_custom_poundwholesale.py
```
The LangGraph-based features are currently **disabled**; the standard workflow runs without LangGraph integration.

Configuration is controlled through [config/system_config.json](config/system_config.json). Before contributing, review [docs/PULL_REQUEST_CHECKLIST.md](docs/PULL_REQUEST_CHECKLIST.md) for development and security guidelines
### **PROJECT_DIRECTIVE_EXECUTION_CHECKLIST:**
```
✅ EXECUTION_VALIDATION (Update after completion):
- [ ] Path management functions verified active
- [ ] Update protocol compliance confirmed
- [ ] Documentation sync mechanisms active
```

### **AUTO_UPDATE_TRIGGER_CONDITIONS:**
```
🚨 DIRECTIVE: AUTO_REGENERATION
TRIGGERS:
- File modifications in tools/, config/, docs/
- CLAUDE_STANDARDS.md changes
- New supplier configurations
- Security policy updates
- Path structure changes
ACTIONS: Regenerate dependent files, update documentation, validate consistency
```

---

## 🎯 Purpose
This document establishes the standardized file organization system for the Amazon FBA Agent System v3.8+. All scripts, tools, and processes MUST follow these conventions to maintain consistency, enable proper automation, and ensure maintainability.

## 🔧 SERENA MCP SETUP INSTRUCTIONS

### **📋 Quick Setup for Claude Code Integration:**
```bash
# From your project directory:
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
```

### **🎯 Project Activation and Indexing:**
```bash
# Index the project for faster performance (recommended for large projects):
uvx --from git+https://github.com/oraios/serena serena project index

# The project will auto-activate with the name:
# "Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy"
```

### **📁 Serena Project Configuration Status:**
- **Project File**: `.serena/project.yml` (configured for Python)
- **Language**: Python with full symbolic analysis support
- **Context**: `ide-assistant` (optimized for surgical code modifications)
- **Read-Only Mode**: `false` (editing enabled with safety protocols)
- **Ignored Paths**: Follows `.gitignore` patterns
- **Memory Location**: `.serena/memories/` (for storing architectural insights)

### Key System Characteristics

- **Configurable Entry Point:**  
  The system is launched via `run_custom_poundwholesale.py`, which loads all operational toggles, batch sizes, and output directories from `config/system_config.json`.
- **No AI Logic:**  
  All AI-driven features (category selection, data extraction, diagnostics) are **disabled**. The system uses only deterministic, selector-based scraping and matching.
- **Single-Phase Price Scraping:**  
  The workflow scrapes the full price range as defined in the config (`min_price_gbp` to `max_price_gbp`).
- **Complete, Resumable Processing Loop:**  
  The main workflow (`PassiveExtractionWorkflow`) is fully implemented, including supplier scraping, Amazon extraction, financial analysis, and profitability checking.  
  The system saves its state after every product and batch, allowing interruption and seamless resumption.
- **Robust Output Directory Handling:**  
  All output, cache, and report files are written to directories defined by `output_root` in the config, or default to `OUTPUTS/` if not set.  
  This includes supplier cache, Amazon cache, linking maps, financial reports, and processing state.
- **Centralized State Management:**  
  The `EnhancedStateManager` ensures that all progress (including supplier scraping, Amazon extraction, and financial analysis) is checkpointed and can be resumed from the exact point of interruption.

---

## 2. Complete Workflow Diagram

```
[run_custom_poundwholesale.py] (Entry Point)
     │
     ▼
[PassiveExtractionWorkflow::run] (use_predefined_categories=True, ai_client=None)
     │
     ├─> 1. Load Predefined Categories from `config/poundwholesale_categories.json`
     │
     ├─> 2. [ConfigurableSupplierScraper] -> Scrape Supplier Product Data
     │   └─> Saves to: {output_root}/cached_products/poundwholesale-co-uk_products_cache.json
     │
     ├─> 3. [COMPLETE PROCESSING LOOP]
     │   └─> For each supplier product:
     │         ├─> a. [AmazonExtractor] -> Search Amazon by EAN (or Title fallback)
     │         │     └─> Extracts full product data (no AI fallbacks)
     │         │     └─> Saves to: {output_root}/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN or title}.json
     │         ├─> b. [Linking Map] -> Update EAN-to-ASIN mapping
     │         │     └─> Saves to: {output_root}/FBA_ANALYSIS/linking_maps/poundwholesale-co-uk/linking_map.json
     │         ├─> c. [FBA_Financial_calculator] -> Calculate Profitability
     │         │     └─> Reads config for VAT, fees, etc.
     │         │     └─> Saves profitable products to: {output_root}/FBA_ANALYSIS/financial_reports/fba_financial_report_{timestamp}.csv
     │         └─> d. [EnhancedStateManager] -> Mark Product as Processed
     │               └─> Saves to: {output_root}/CACHE/processing_states/poundwholesale-co-uk_processing_state.json
     │
     └─> 4. [Resume Logic]
         └─> On restart, loads state and resumes from last unprocessed product/category
```

---

## 2.a Main scripts part of workflow ( ALWAYS CROSS CHECK IF THE UTILITIES & OPTIMIAZATION SCRIPTS ARE PART OF THE WORFKLOW AND/OR IF THEY HAVE BEEN MAYBE REPLACE FOR ISNTANCE )
Entry Point & Orchestrator:
run_custom_poundwholesale.py
passive_extraction_workflow_latest.py (the 413 KB version)

Core Services & Managers:
SystemConfigLoader.py
utils/browser_manager.py
tools/supplier_authentication_service.py
utils/enhanced_state_manager.py
utils/path_manager.py
utils/logger.py
utils/file_manager.py

Data Extraction & Processing Tools:
tools/configurable_supplier_scraper.py
tools/amazon_playwright_extractor.py
tools/FBA_Financial_calculator.py

Utilities & Optimizers:
utils/windows_save_guardian.py
utils/hash_lookup_optimizer.py
utils/sentinel_monitor.py
utils/url_cache_filter.py
utils/browser_circuit_breaker.py
tools/category_completion_tracker.py

## 3. Output Tracker (Complete)

| Output Type             | File Path (relative to `output_root`)                                                      | Status         | Content                                                              |
|-------------------------|--------------------------------------------------------------------------------------------|----------------|----------------------------------------------------------------------|
| **Category Config**     | `config/poundwholesale_categories.json`                                                    | ✅ **Input**    | Predefined list of category URLs to scrape.                          |
| **Supplier Cache**      | `cached_products/poundwholesale-co-uk_products_cache.json`                                 | ✅ **Generated**| Raw product data scraped from the supplier.                          |
| **Amazon Data Cache**   | `FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN or title}.json`                              | ✅ **Active**   | Detailed product data from a single Amazon page.                     |
| **Linking Map**         | `FBA_ANALYSIS/linking_maps/poundwholesale-co-uk/linking_map.json`                          | ✅ **Active**   | Links supplier EANs to the corresponding Amazon ASINs.               |
| **Financial Report**    | `FBA_ANALYSIS/financial_reports/fba_financial_report_{timestamp}.csv`                      | ✅ **Active**   | Complete financial breakdown for all profitable products.            |
| **Processing State**    | `CACHE/processing_states/poundwholesale-co-uk_processing_state.json`                       | ✅ **Active**   | Tracks processed products for resumability.                          |
| **Logs**                | `logs/debug/run_custom_poundwholesale_{timestamp}.log`                                     | ✅ **Active**   | Full debug logs for each run.                                        |

---

## 4. Quick Start & Execution

To run the system, execute the entry point script from your terminal.  
**The system will perform full end-to-end processing, including supplier scraping, Amazon extraction, financial analysis, and profitability reporting.**

```bash
# Navigate to the project directory
cd C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32

# Run the custom script
python run_custom_poundwholesale.py

```


## Configuration (AUTO-UPDATE TRIGGER: New suppliers, system settings, or browser requirements)

### System Configuration
Main system settings are detailed in `docs/README.md` and `config/system-config-toggle-v2.md`. The security suite validates configuration integrity through `tools/security_checks.py`.

### Supplier Configuration  
- System configs: `config/system_configs/*.json`
- Supplier-specific scraping rules
- Category mappings and pricing filters
- Authentication and navigation settings

## Security Management (AUTO-UPDATE TRIGGER: New security protocols, API changes, or safety requirements)

### 🚨 CRITICAL API KEY PRESERVATION POLICY
**🚨 MANDATORY DIRECTIVE: NEVER REMOVE OR MODIFY EXISTING API KEYS**
- ✅ **PRESERVE ALL EXISTING API KEYS** in scripts and environment files --> if needed comment out api keys
- ✅ **ADD KEYS WHEN NEEDED** but never remove working configurations
- ✅ **MAINTAIN FUNCTIONALITY** - Keep all working API integrations intact

**Current Working API Keys (USE THESE WHEN NEEDED/REQUESTED):**
- OpenAI API Key: `sk-ZVcoRkU6brREgixWUDk7lTq_aBNRZwdh_PWwOZuJwKT3BlbkFJvOyKLWAM8OhjyHN0b8e66E1O2G7N2Ew_g3SngsDToA`
- GitHub Token: `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`
	
---


### **✅ Advanced FBA Analysis Workflows**
<!-- RELEVANCE_KEYWORDS: fba, analysis, financial, roi, profitability -->
<!-- ZEN_MCP_PRIORITY: thinkdeep:HIGH, analyze:HIGH, debug:MEDIUM -->



---

## 📋 DOCUMENTATION_REFERENCE
<!-- LOAD_ON_DEMAND: true -->
<!-- SELECTIVE: true -->

### **📋 Complete Technical Documentation**
<!-- RELEVANCE_KEYWORDS: documentation, technical, architecture, system -->
<!-- ZEN_MCP_PRIORITY: thinkdeep:MEDIUM, analyze:LOW, debug:LOW -->

**📋 REFERENCE - Load when documentation context is detected:**

**Complete technical details available in:**
- `/mnt/c/Users/chris/Cloud-Drive_christianhaddad8@gmail.com/Cloud-Drive/Full/claude code/Amazon-FBA-Agent-System-v3/docs/README.md`


## 🔄 Trigger Definitions

### Content-Driven Regeneration
- **CLAUDE_STANDARDS.md changes** → Regenerate claude.md (filtered) + docs/CLAUDE_STANDARDS.md (full)
- **New rules/policies** → Update all target files
- **Path updates** → Cascade through automation scripts

### Event-Driven Regeneration  
- **Script output changes** → Update documentation references
- **Test completion** → Prompt for sync opportunities
- **Git activity** → Smart prompting based on workflow state


## 🚨 CRITICAL IMPLEMENTATION NOTES




---

## 📚 Related Documentation

**Complete technical details available in:**
- `/mnt/c/Users/chris/Cloud-Drive_christianhaddad8@gmail.com/Cloud-Drive/Full/claude code/Amazon-FBA-Agent-System-v3/docs/README.md`
- `/mnt/c/Users/chris/Desktop/Amazon-FBA-Agent-System-v32/config/system-config-toggle-v2.md`
---

**Last Updated**: 2025-06-23
**Version**: 3.6
**Maintained By**: Amazon FBA Agent System Team
**Status**: ACTIVE STANDARD - All development must comply

**⚠️ NOTICE**: This file is auto-generated from CLAUDE_STANDARDS.md. For complete development guidance, see CLAUDE_STANDARDS.md