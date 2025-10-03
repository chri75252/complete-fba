# Supplier Config Onboarding: Analysis and Implementation Plan
**Date**: October 1, 2025
**Context**: Config-driven supplier onboarding approach for clearance-king.co.uk

## Critical User Clarifications

### 1. Single-Supplier Config Approach (USER IS CORRECT)
**User's Point**: "Why should I add new website variables in the same system_config file and risk discrepancies? Why don't I simply put one supplier at a time?"

**Key Facts**:
- User analyzes ONE supplier at a time (never concurrent)
- When switching suppliers, they edit config to replace entries
- Single-supplier config is SIMPLER and SAFER than multi-supplier
- Zero risk of cross-supplier conflicts

**Correct Approach**:
- `config/system_config.json` contains ONE supplier at a time
- When switching to clearance-king: edit config to replace poundwholesale entries
- This is MORE aligned with minimizing discrepancies

### 2. Linking Map Creation Mechanism
**User's Observation**: System already creates linking map folders like `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json`

**Investigation Findings**:
- Line 3301 in workflow uses: `linking_map_path = get_linking_map_path(supplier_name)`
- Global constants at lines 633-635 define base directory but NOT per-supplier paths
- `get_linking_map_path()` utility function in `utils/path_manager.py` handles per-supplier subdirectory creation
- Path manager automatically creates: `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/linking_map.json`

## Key Files Examined

### Entry Script Pattern: `run_custom_clearance_king.py` (112 lines)
```python
# Lines 22-23: Explicit supplier-specific imports
from tools.clearance_king.passive_extraction_workflow_clearance_king import PassiveExtractionWorkflow
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService

# Line 61: Load config for specific supplier
workflow_config = config_loader.get_workflow_config('clearance_king_workflow')

# Lines 93-97: Initialize workflow with config
workflow = PassiveExtractionWorkflow(
    config_loader=config_loader,
    workflow_config=workflow_config,
    browser_manager=browser_manager
)
```

### Hardcoded Paths in Workflow

**Line 1834 - Category Config Path (HARDCODED)**:
```python
config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
```
**Proposed**: Read from `workflow_config.get("categories_config_path")` instead

**Line 7334 - Manifest Path (HARDCODED)**:
```python
manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
```
**Proposed**: Read from `workflow_config.get("supplier_name")` dynamically

**Line 11727 - Supplier URL (HARDCODED)**:
```python
page = await self.browser_manager.get_page(
    self.workflow_config.get("supplier_url", "https://www.poundwholesale.co.uk")
)
```
**Status**: Already config-driven with fallback

**Line 11732 - Supplier Name (ALREADY CONFIG-DRIVEN)**:
```python
supplier_name = self.supplier_name or "poundwholesale.co.uk"
```
**Status**: Already uses `self.supplier_name` from config

## User Requirements

### Detailed Workflow Request
User wants comprehensive workflow for analyzing clearance-king.co.uk with:

1. **Current State Workflow**: Brief sequence of steps with manual edits in current setup
2. **Post-Implementation Workflow**: Detailed workflow showing:
   - Current snippets to be edited
   - Diffs (before/after)
   - Explanation/reasoning for each change
   - Why the suggested implementation approach
3. **All steps in correct chronological order**
4. **What user does vs. what coding agent does vs. what happens automatically**

### Key Questions to Answer
1. Which code snippet creates linking map folders? (Answer: `get_linking_map_path()` utility)
2. Are lines 633-635 obsolete? (Answer: Partially - they create base directory, but not per-supplier paths)
3. How to integrate clearance-king with minimal manual edits?

## Next Steps for New Conversation

1. **Present Current Workflow**: Document all manual steps from `general_new_supplier_integration_guide.md`
2. **Design Post-Implementation Workflow**: Show config-driven approach with specific code changes
3. **Provide Diffs**: Before/after for each snippet that needs modification
4. **Explain Reasoning**: Why each change improves the system
5. **Create Implementation Plan**: Step-by-step execution with validation points

## Files to Reference

- `run_custom_clearance_king.py` - Entry script example
- `tools/passive_extraction_workflow_latest.py` - Main workflow (lines 1834, 7334, 11727, 11732)
- `utils/path_manager.py` - Contains `get_linking_map_path()` function
- `walkthrough/general_new_supplier_integration_guide.md` - Current manual process
- `config/poundwholesale_categories.json` - Category URL format example
- `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json` - Existing linking map proof



# Supplier Config-Driven Onboarding Plan - Comprehensive Analysis & Implementation
**Date**: September 30, 2025 
**Status**: Analysis Complete - Ready for Implementation
**Critical Files**: 
- `walkthrough/SUPPLIER_CONFIG_ONBOARDING_PLAN.md` (proposed config-driven approach)
- `walkthrough/general_new_supplier_integration_guide.md` (current duplication approach)
- `tools/passive_extraction_workflow_latest.py` (12,028 lines - CORRECT file with hybrid processing)

## 🚨 CRITICAL CORRECTION MADE
**Initial Error**: I incorrectly stated the workflow file was 1,200 lines (FALSE)
**Actual Reality**: The file is **12,028 lines** and all line number references in the plan are ACCURATE
**Verification**: `wc -l tools/passive_extraction_workflow_latest.py` = 12028 lines
**User Concern**: Rightfully flagged this as concerning error - this is the most important file in the system

## 📋 USER'S KEY CLARIFICATIONS

### What Will Be MANUAL/HARDCODED Per Website:
1. **Login Scripts**: `tools/<supplier>/standalone_playwright_login_<supplier>.py` - Created manually through discussion and testing
2. **CSS Selectors**: Manually provided by user after analyzing website, stored in `config/supplier_configs/<domain>.json`
3. **Pagination Approach**: Manually configured per website (URL params vs next button vs infinite scroll)
4. **Authentication Service**: `tools/<supplier>/supplier_authentication_service.py` - Website-specific logic
5. **Test Product URL**: Manually selected stable product for login verification
6. **Configurable Scraper Modifications**: At least partially tailored per website
7. **Entry Scripts**: Explicit per-supplier imports (NO generic runner due to discrepancy risk)

### What Can Be CONFIG-DRIVEN (Low Risk):
1. **Category URLs List**: `config/<supplier>_categories.json` - Simple JSON array
2. **Workflow Parameters**: `system_config.json` → `<supplier>_workflow` section
3. **Output Directory Paths**: Already handled by `path_manager.py`
4. **System-Wide Settings**: Rate limits, timeouts, batch sizes

### Core Principle:
**GOAL**: Minimize risk of discrepancies when adding new websites by clearly separating low-risk config-driven components from hands-on website-specific tailoring.

## 🎯 HYBRID PROCESSING MODE VERIFICATION
**Critical Discovery**: System uses hybrid processing mode 99% of the time
- File: `tools/passive_extraction_workflow_latest.py` (NOT a separate file)
- Hybrid mode config: Lines 2295-2307, 6894+, 7428+
- Entry point: `run_custom_poundwholesale.py` imports from `tools.passive_extraction_workflow_latest`
- Clearance-king also uses copy of this workflow: `tools/clearance_king/passive_extraction_workflow_clearance_king.py`

## 📊 COMPARISON: OLD GUIDE vs NEW PLAN

### Steps That REMAIN THE SAME:
1. ✅ Phase 1: Pre-integration analysis (manual website analysis)
2. ✅ Infrastructure setup: File duplication to `tools/<supplier>/` and `utils/<supplier>/`
3. ✅ Authentication service creation (manual per website)
4. ✅ CSS selector provision (manual but stored in JSON)
5. ✅ Entry script pattern (explicit imports, NO generic runner)

### Steps That WILL BE DIFFERENT (Config-Driven Improvements):
1. **OLD**: Edit line 1834 in workflow copy to hardcode category config path
   **NEW**: Read from `workflow_config["categories_config_path"]` - zero edits needed
   
2. **OLD**: Edit line 7334 to hardcode linking map paths
   **NEW**: Use `path_manager.get_linking_map_path(supplier_name)` - automatic per supplier
   
3. **OLD**: Global `LINKING_MAP_DIR` constant causes conflicts
   **NEW**: Instance variables in `__init__` - proper per-supplier isolation

### Steps MISSED in Old Guide:
1. ❌ Linking map path parameterization (3 locations: lines 633, 1209, 7334)
2. ❌ Hybrid processing mode configuration requirements
3. ❌ Output directory initialization details

## 🔍 WHERE CONFIG VALUES ARE USED (Critical Flow Analysis)

### 1. `categories_config_path` Flow:
```
system_config.json 
  → workflow_config["categories_config_path"]
    → Line 1834: Load JSON file in _get_total_category_count()
      → Extract category_urls array
        → len(category_urls) = total_categories
          → State manager initialization
            → Progress tracking throughout workflow
```

**Affected Lines**:
- Line 1834-1842: `_get_total_category_count()` method
- Line 3730: Secondary category count retrieval
- Impacts: Total category count calculation for state management

### 2. `supplier_name` Flow:
```
system_config.json
  → workflow_config["supplier_name"]
    → Line 1353: self.supplier_name = workflow_config.get("supplier_name")
      → Line 1357: EnhancedStateManager(supplier_name)
        → Line 1386-1387: Path construction (supplier_cache_dir, amazon_cache_dir)
          → All state persistence uses this:
            - {supplier_name}_processing_state.json
            - {supplier_name}_products_cache.json
            - linking_maps/{supplier_name}/
```

**Affected Lines**:
- Line 1353: Constructor initialization
- Line 1357: State manager initialization
- Line 1386-1387: Cache directory paths
- Line 2295+: Hybrid processing mode checks
- Everywhere: Logging, file paths, state tracking

### 3. `supplier_url` (Currently Hardcoded):
**Location**: Line 11727-11730 in workflow copies
**Should Read From**: `workflow_config.get("supplier_url")`
**Used In**: Browser navigation, URL validation, logging

## 📋 DETAILED IMPLEMENTATION PLAN

### PHASE 1: Safe Config Extraction (ZERO RISK)

#### Implementation 1.1: Categories Config Path
**File**: `tools/passive_extraction_workflow_latest.py`
**Line**: 1834

**BEFORE**:
```python
config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
```

**AFTER**:
```python
# Read from workflow config (passed to constructor)
categories_config_path = self.workflow_config.get("categories_config_path")
if not categories_config_path:
    # Backwards compatibility fallback
    categories_config_path = f"config/{self.supplier_name.replace('.', '_')}_categories.json"
    self.log.warning(f"⚠️ categories_config_path not in config, using fallback: {categories_config_path}")

config_path = Path(categories_config_path)
```

**Why This Works**:
- `workflow_config` already passed to constructor
- Fallback preserves backwards compatibility
- No risk if config key missing
- Eliminates 1 manual edit per supplier

**Benefit**: Zero edits needed in workflow file when adding new supplier

---

#### Implementation 1.2: Add Config Entries
**File**: `config/system_config.json`

**Add for each supplier**:
```json
{
  "poundwholesale_workflow": {
    "supplier_name": "poundwholesale.co.uk",
    "supplier_url": "https://www.poundwholesale.co.uk",
    "categories_config_path": "config/poundwholesale_categories.json",
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  },
  "clearance_king_workflow": {
    "supplier_name": "clearance-king.co.uk",
    "supplier_url": "https://www.clearance-king.co.uk",
    "categories_config_path": "config/clearance_king_categories.json",
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  }
}
```

**Risk**: ZERO - Simple JSON key/value pairs

---

#### Implementation 1.3: Linking Map Paths
**File**: `tools/passive_extraction_workflow_latest.py`
**Multiple Locations**: Lines 633, 1209, 7334

**Location 1 - Line 633 (Global Constants)**:

**BEFORE**:
```python
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")
```

**PROBLEM**: Global constants conflict between suppliers!

**AFTER (Move to __init__ method after line 1387)**:
```python
# DELETE lines 633-635 (global constants)

# ADD to __init__ after line 1387:
def __init__(self, config_loader, workflow_config, browser_manager=None, ai_client=None):
    # ... existing code ...
    
    # Initialize supplier-specific linking map path
    self.linking_map_dir = path_manager.get_linking_map_path(self.supplier_name)
    os.makedirs(self.linking_map_dir, exist_ok=True)
    self.linking_map_path = os.path.join(self.linking_map_dir, "linking_map.json")
    self.log.info(f"✅ Linking map directory: {self.linking_map_dir}")
```

**Why This Works**:
- Removes hardcoded global path
- Uses existing `path_manager` utility
- Automatically creates per-supplier directory
- `path_manager.get_linking_map_path()` generates: `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/`

**Benefit**: Automatic per-supplier linking maps, zero manual configuration

---

**Location 2 - Line 1209 (_save_linking_map method)**:

**BEFORE**:
```python
def _save_linking_map(self, ...):
    # Uses global LINKING_MAP_PATH
    with open(LINKING_MAP_PATH, 'w') as f:
        ...
```

**AFTER**:
```python
def _save_linking_map(self, ...):
    # Use instance variable instead
    with open(self.linking_map_path, 'w') as f:
        ...
```

**Why This Works**: Instance variable set in `__init__`, each supplier gets own path automatically

---

**Location 3 - Line 7334 (Manifest Path)**:
Similar change - use `self.linking_map_dir` instead of hardcoded path

---

### PHASE 2: Per-Supplier Directory Structure (KEEP THIS)

**Standard Structure**:
```
tools/
├── poundwholesale/
│   ├── passive_extraction_workflow_poundwholesale.py
│   └── supplier_authentication_service.py
├── clearance_king/
│   ├── passive_extraction_workflow_clearance_king.py
│   └── supplier_authentication_service.py
└── new_supplier/
    ├── passive_extraction_workflow_new_supplier.py
    └── supplier_authentication_service.py

utils/
├── poundwholesale/
│   ├── logger.py
│   └── browser_manager.py
└── new_supplier/
    ├── logger.py
    └── browser_manager.py
```

**Why Keep Duplication**:
- Explicit separation per supplier
- Easy to identify supplier-specific modifications
- Zero risk of cross-supplier contamination
- Clear which files need manual tailoring

---

### PHASE 3: Entry Script Pattern (NO GENERIC RUNNER)

**User Requirement**: NO generic runner if ANY risk of discrepancies

**Decision**: ✅ AGREE - Explicit entry scripts are safer

**Standard Template** (replicate per supplier):

**File**: `run_custom_{supplier}.py` (112 lines)

```python
import asyncio
import logging
from config.system_config_loader import SystemConfigLoader
from tools.{supplier}.passive_extraction_workflow_{supplier} import PassiveExtractionWorkflow
from tools.{supplier}.supplier_authentication_service import SupplierAuthenticationService
from utils.{supplier}.logger import setup_logger
from utils.{supplier}.browser_manager import BrowserManager

async def main():
    debug_log_file = setup_logger()
    log = logging.getLogger(__name__)
    
    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('{supplier}_workflow')
    supplier_name = workflow_config.get('supplier_name')
    credentials = config_loader.get_credentials(supplier_name)
    
    chrome_debug_port = config_loader.get_system_config().get('chrome_debug_port', 9222)
    
    browser_manager = None
    try:
        browser_manager = BrowserManager.get_instance()
        await browser_manager.launch_browser(cdp_port=chrome_debug_port)
        page = await browser_manager.get_page()
        
        auth_service = SupplierAuthenticationService(page)
        authenticated = await auth_service.ensure_authenticated_session(page, credentials)
        
        if not authenticated:
            log.error("Authentication failed. Exiting workflow.")
            return
        
        workflow = PassiveExtractionWorkflow(
            config_loader=config_loader,
            workflow_config=workflow_config,
            browser_manager=browser_manager
        )
        await workflow.run()
        
    finally:
        if browser_manager:
            await browser_manager.close_browser()  # NOT cleanup()!

if __name__ == "__main__":
    asyncio.run(main())
```

**Why This Works**:
- Explicit supplier-specific imports
- No dynamic loading risk
- Clear config key reference
- Simple to duplicate (5 minutes per supplier)
- ZERO risk of wrong imports

---

## 📊 FINAL SUMMARY

### Benefits of Config-Driven Approach:
1. ✅ **Reduces manual edits from 4-6 hardcoded lines to 0 lines**
2. ✅ Automatic per-supplier linking maps
3. ✅ Eliminates global constant conflicts
4. ✅ Backwards compatible fallbacks
5. ✅ Maintains explicit control (no generic runner)
6. ✅ Zero cross-supplier contamination risk

### What Remains Manual (As Required):
1. ❌ Login scripts (too variable)
2. ❌ CSS selectors (manual values)
3. ❌ Pagination config (manual per website)
4. ❌ Authentication service (website-specific)
5. ❌ Test product URL selection
6. ❌ Scraper modifications if needed
7. ❌ Entry script duplication (explicit imports)

### Risk Assessment:
- **Config changes**: ⭐ ZERO risk (simple JSON)
- **Path manager usage**: ⭐ VERY LOW (utility exists and tested)
- **Instance vs global**: ⭐ LOW (improves architecture)
- **Overall implementation**: ⭐ VERY LOW risk

### Implementation Priority:
1. **HIGH**: Categories config path (line 1834) - most impactful
2. **HIGH**: Linking map paths (lines 633, 1209, 7334) - architectural improvement
3. **MEDIUM**: Add config entries for existing suppliers
4. **LOW**: Document new process in guides

---

## 🔄 NEXT STEPS FOR IMPLEMENTATION

1. **Backup Protocol**: Create backup of `tools/passive_extraction_workflow_latest.py`
2. **Implement Changes**: Apply 3 code changes (categories path, linking map initialization, method usage)
3. **Add Config**: Update `system_config.json` with workflow configs for poundwholesale and clearance-king
4. **Test Existing Suppliers**: Run poundwholesale and clearance-king to verify no regressions
5. **Verify Output**: Check that linking maps still created correctly per supplier
6. **Update Guides**: Modify `walkthrough/general_new_supplier_integration_guide.md` to document config approach
7. **New Supplier Integration**: Use updated process for next supplier

---

## 🚨 CRITICAL NOTES FOR NEXT AGENT

1. **File Verification**: Always verify actual file exists and line counts before making claims
2. **Workflow File**: `tools/passive_extraction_workflow_latest.py` is 12,028 lines - this is CORRECT
3. **Hybrid Processing**: System uses hybrid mode 99% of time - this is in the main workflow, not separate file
4. **No Generic Runner**: User explicitly wants NO generic runner due to discrepancy risk - keep explicit imports
5. **Manual Components**: Many components MUST remain manual per user's requirements - don't over-automate
6. **Existing Systems**: Keep ALL existing poundwholesale/clearance-king files unchanged during implementation
7. **Testing Required**: User personally tests all supplier-specific scripts before running system

---

## 📁 KEY FILE REFERENCES

- Main workflow: `tools/passive_extraction_workflow_latest.py` (12,028 lines)
- Poundwholesale entry: `run_custom_poundwholesale.py`
- Clearance-king entry: `run_custom_clearance_king.py`
- Config file: `config/system_config.json`
- Path utilities: `utils/path_manager.py`
- Old guide: `walkthrough/general_new_supplier_integration_guide.md`
- New plan: `walkthrough/SUPPLIER_CONFIG_ONBOARDING_PLAN.md`

**Status**: Analysis complete, ready for careful implementation with user oversight.