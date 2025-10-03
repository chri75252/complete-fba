# Supplier Config Onboarding Analysis - Detailed Implementation Plan
**Date**: September 30, 2025
**Status**: Analysis Complete - Ready for Implementation
**Context**: Analyzing config-driven approach vs manual duplication for new supplier integration

## 🎯 Task Objective

Analyze `walkthrough/SUPPLIER_CONFIG_ONBOARDING_PLAN.md` (new config-driven proposal) and compare to `walkthrough/general_new_supplier_integration_guide.md` (current duplication approach) to determine:
1. Which components can be safely config-driven (low risk)
2. Which must remain manual/hardcoded (website-specific tailoring required)
3. What steps differ between old and new approaches
4. Detailed implementation plan for config-driven improvements

**Core Principle**: Minimize risk of discrepancies when adding new supplier websites.

---

## ⚠️ CRITICAL CORRECTIONS MADE

### Error Corrected: Workflow File Size
- **My Initial Claim**: File is ~1,200 lines
- **USER CORRECTION**: File is actually **12,028 lines**
- **Verified**: `wc -l tools/passive_extraction_workflow_latest.py` = 12028 lines
- **Line 1209**: EXISTS and contains `_save_linking_map` logic as stated in plan
- **Lesson**: Always verify file sizes with actual commands before making claims

### Workflow Identification Confirmed
- **Primary Workflow**: `tools/passive_extraction_workflow_latest.py` (12,028 lines)
- **Hybrid Processing**: ENABLED and active (lines 2295-7505)
- **Used By**: Both poundwholesale and clearance-king
- **Class**: `PassiveExtractionWorkflow` (line 1340)

---

## 🔍 USER'S KEY CLARIFICATIONS

### 1. Manual Components (Hands-On Per Website)
User clarified these will be **MANUALLY created/tailored per website**:
- ✅ Login scripts (too variable for config - each site different)
- ✅ CSS selectors (manually provided by user after testing)
- ✅ Pagination approach (manually configured per website)
- ✅ Test product URLs (manually selected per website)
- ✅ Parts of configurable_supplier_scraper (website-specific modifications)
- ✅ Authentication service (website-specific login flows)

**Reasoning**: Every website has completely different structure, selectors, and behavior. Attempting to automate these would increase risk of discrepancies.

### 2. No Generic Runner
User requirement: **NO generic runner** if ANY risk of discrepancies.
- Entry scripts like `run_custom_clearance_king.py` are simple (112 lines)
- Explicit supplier-specific imports are safer than dynamic loading
- Duplication of entry scripts is low effort, high safety
- **Decision**: Keep explicit per-supplier entry scripts

### 3. Existing Files Remain Unchanged
- Keep ALL existing poundwholesale files as-is
- Keep ALL existing clearance-king files as-is
- New config-driven approach only applies to NEW suppliers going forward
- Backwards compatibility required (fallbacks if config keys missing)

### 4. Security Concerns Deferred
User stated: "Forget security concerns for now like username and password" - credential management improvements deferred to later discussion.

---

## ✅ COMPONENTS FOR CONFIG-DRIVEN APPROACH (Low Risk)

### 1. Category URLs List
**Config File**: `config/<supplier>_categories.json`
**Risk Level**: ⭐ VERY LOW
**Currently**: Already in JSON format for both suppliers
**Benefit**: No change needed - already config-driven

**Example**:
```json
{
  "categories": [
    {"name": "Category 1", "url": "https://..."},
    {"name": "Category 2", "url": "https://..."}
  ]
}
```

### 2. Workflow Parameters
**Config File**: `config/system_config.json` → `<supplier>_workflow` section
**Risk Level**: ⭐ VERY LOW
**Currently**: Partially hardcoded in workflow copies
**Change Needed**: Read from config instead of hardcoding

**Keys to Add**:
```json
{
  "poundwholesale_workflow": {
    "supplier_name": "poundwholesale.co.uk",
    "supplier_url": "https://www.poundwholesale.co.uk",
    "categories_config_path": "config/poundwholesale_categories.json",
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  }
}
```

**Where Used in Workflow**:
- **Line 1353**: `self.supplier_name = self.workflow_config.get("supplier_name")`
- **Line 1834**: Categories config path (currently hardcoded to poundwholesale)
- **Line 1357**: State manager initialization uses supplier_name
- **Line 1386-1387**: Cache directory paths constructed from supplier_name
- **Throughout**: Logging, file paths, state tracking all use supplier_name

### 3. Output Directory Paths
**Implementation**: Use `path_manager.py` utilities
**Risk Level**: ⭐ VERY LOW
**Currently**: Partially using path_manager, partially hardcoded
**Change Needed**: Consistent use of path_manager throughout

**Key Methods**:
- `path_manager.get_output_path()` - for cache directories
- `path_manager.get_linking_map_path(supplier_name)` - for linking maps

---

## ❌ COMPONENTS THAT MUST REMAIN MANUAL

### 1. Login Script (Per Website)
**File Pattern**: `tools/<supplier>/standalone_playwright_login_<supplier>.py`
**Why Manual**: 
- Every website has different login flow
- Different selectors for email/password/submit
- Different wait conditions and success indicators
- Unique test product URL per website
**User Confirmed**: Will be manually created through discussion and testing

### 2. CSS Selectors (Per Website)
**File**: `config/supplier_configs/<domain>.json`
**Why Manual**:
- Every website has completely different DOM structure
- Selectors must be tested on actual live website
- Fallback arrays must be ordered by reliability
**User Confirmed**: Will provide these selectors after analyzing each website
**Note**: Values are manual, but structure is JSON config

### 3. Pagination Approach (Per Website)
**File**: `config/supplier_configs/<domain>.json` → `pagination` section
**Why Manual**:
- Different mechanisms: buttons, URL params, infinite scroll
- Must be tested on actual website
- Different failure modes per approach
**User Confirmed**: Will determine approach per website during analysis

**Examples**:
- Clearance-King: URL parameter pagination (`?p={page}`)
- Poundwholesale: Next button pagination (`a.action.next`)

### 4. Authentication Service (Per Website)
**File**: `tools/<supplier>/supplier_authentication_service.py`
**Why Manual**:
- Login sequences completely different per site
- Different selectors and multi-step flows
- Website-specific quirks (CAPTCHAs, 2FA, etc.)
**User Confirmed**: Part of hands-on tailoring per website

### 5. Test Product URL (Per Website)
**Location**: In login script
**Why Manual**:
- Must be real product requiring login to see price
- Must be stable (not discontinued)
- Must have clear numeric price display
**User Confirmed**: Will select appropriate test product per website

### 6. Configurable Scraper Modifications (Per Website)
**File**: `tools/<supplier>/configurable_supplier_scraper_<supplier>.py`
**Why Manual**:
- Website-specific navigation patterns
- Unique product detail page structures
- Custom extraction logic for non-standard fields
**User Confirmed**: At least parts require tailoring per website

---

## 🔄 COMPARISON: OLD GUIDE vs NEW CONFIG PLAN

### Steps That Remain THE SAME:
1. ✅ Phase 1: Pre-integration analysis (manual website analysis)
2. ✅ Infrastructure setup: Directory creation and file duplication
3. ✅ Authentication service creation (manual per supplier)
4. ✅ CSS selector configuration (manual values in JSON)
5. ✅ Entry script pattern (explicit imports, no generic runner)

### Steps That CHANGE (Config-Driven):
1. **Categories Config Path** (Line 1834)
   - OLD: Hardcoded `"config/poundwholesale_categories.json"`
   - NEW: Read from `workflow_config.get("categories_config_path")`
   - Benefit: Eliminates 1 manual edit per supplier

2. **Linking Map Paths** (Lines 633, 1209, 7334)
   - OLD: Global constant `LINKING_MAP_DIR` hardcoded
   - NEW: Instance variable using `path_manager.get_linking_map_path(supplier_name)`
   - Benefit: Automatic per-supplier directories, zero manual config

3. **Supplier URL/Name** (Lines 11727, 11732)
   - OLD: Hardcoded in workflow copy
   - NEW: Read from `workflow_config`
   - Benefit: Eliminates 2+ manual edits per supplier

### Steps MISSED in Old Guide:
1. ❌ Linking map path parameterization (not documented)
2. ❌ Hybrid processing mode configuration (not mentioned)
3. ❌ Output directory initialization details (not explained)

---

## 📋 DETAILED IMPLEMENTATION PLAN

### PHASE 1: Config Extraction (Zero Risk)

#### Implementation 1.1: Categories Config Path
**File**: `tools/passive_extraction_workflow_latest.py`
**Line**: 1834

**Current Code**:
```python
config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
```

**NEW Code**:
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
- `workflow_config` already passed to constructor (line 1341)
- Fallback preserves backwards compatibility
- No risk: if config key missing, uses old pattern
- Enables per-supplier category config without editing workflow

**Benefit**: Eliminates 1 manual edit per supplier integration

**Testing**: Verify poundwholesale still works with fallback, then add config key and verify it reads from config.

---

#### Implementation 1.2: Linking Map Paths (Instance Variables)
**File**: `tools/passive_extraction_workflow_latest.py`
**Lines**: 633-635, 1209, 7334

**Problem**: Global constants `LINKING_MAP_DIR` and `LINKING_MAP_PATH` conflict between suppliers.

**Current Code (Line 633)**:
```python
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")
```

**NEW Code** (Move to instance variables in `__init__`):
```python
# DELETE lines 633-635 (global constants)

# ADD to __init__ method after line 1387:
def __init__(self, config_loader, workflow_config, browser_manager=None, ai_client=None):
    # ... existing initialization code ...
    
    # Initialize supplier-specific linking map path (AFTER supplier_name is set)
    self.linking_map_dir = path_manager.get_linking_map_path(self.supplier_name)
    os.makedirs(self.linking_map_dir, exist_ok=True)
    self.linking_map_path = os.path.join(self.linking_map_dir, "linking_map.json")
    self.log.info(f"✅ Linking map directory: {self.linking_map_dir}")
```

**Update Line 1209** (_save_linking_map method):
```python
# OLD: Uses global LINKING_MAP_PATH
with open(LINKING_MAP_PATH, 'w') as f:
    ...

# NEW: Use instance variable
with open(self.linking_map_path, 'w') as f:
    ...
```

**Update Line 7334** (manifest path):
```python
# OLD: Hardcoded path
Path("OUTPUTS") / "manifests" / "clearance-king.co.uk" / f"{slug}.json"

# NEW: Use instance variable
Path(self.linking_map_dir) / f"{slug}.json"
```

**Why This Works**:
- `path_manager.get_linking_map_path()` already exists and tested
- Generates: `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/`
- Each supplier gets own directory automatically
- No hardcoding needed
- No global conflicts

**Benefit**: Automatic per-supplier linking maps, zero manual configuration

**Testing**: Run both poundwholesale and clearance-king simultaneously, verify separate linking map directories created.

---

#### Implementation 1.3: System Config Additions
**File**: `config/system_config.json`

**Add for Each Supplier**:
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

**Risk**: ⭐ ZERO - Simple JSON key/value additions

---

### PHASE 2: Per-Supplier Directory Structure (KEEP AS-IS)

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
├── clearance_king/
│   ├── logger.py
│   └── browser_manager.py
└── new_supplier/
    ├── logger.py
    └── browser_manager.py
```

**Why Keep This**:
- Explicit separation per supplier (no cross-contamination)
- Easy to identify supplier-specific modifications
- Clear which files need manual tailoring
- Zero risk of conflicts

---

### PHASE 3: Entry Script Pattern (KEEP AS-IS)

**Standard Template** (replicate per supplier):
```python
# run_custom_{supplier}.py
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
            log.error("Authentication failed.")
            return
        
        workflow = PassiveExtractionWorkflow(
            config_loader=config_loader,
            workflow_config=workflow_config,
            browser_manager=browser_manager
        )
        await workflow.run()
        
    finally:
        if browser_manager:
            await browser_manager.close_browser()  # NOT cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

**Why This Works**:
- Explicit supplier-specific imports (safe)
- No dynamic loading risk
- Clear config key reference (`'{supplier}_workflow'`)
- Simple to duplicate and modify (5 minutes per supplier)
- **IMPORTANT**: Use `close_browser()` not `cleanup()` (cleanup method doesn't exist)

---

## 🎯 BENEFITS SUMMARY

### Old Approach (Duplication):
- ❌ Requires editing 4-6 hardcoded lines per supplier copy
- ❌ Manual linking map path edits
- ❌ Global constants conflict between suppliers
- ❌ Easy to miss an edit location
- ✅ Explicit imports (good)
- ✅ Per-supplier directories (good)

### New Config-Driven Approach:
- ✅ **Zero hardcoded path edits in workflow** (down from 4-6)
- ✅ Automatic linking map per supplier
- ✅ Instance variables instead of globals (no conflicts)
- ✅ Backwards compatible fallbacks
- ✅ Keep explicit imports (no generic runner risk)
- ✅ Keep per-supplier directories
- ✅ Reduces manual edits from **4-6 lines to 0 lines** per supplier

### Risk Assessment:
- **Config changes**: ⭐ ZERO risk (simple JSON keys)
- **Path manager usage**: ⭐ VERY LOW (utility already exists and tested)
- **Instance vs global**: ⭐ LOW (improves architecture, easy to test)
- **Backwards compatibility**: ⭐ ZERO risk (fallbacks preserve old behavior)

---

## 📊 AFFECTED WORKFLOW SECTIONS

### Where Config Values Are Used:

#### 1. `categories_config_path` Flow:
```
system_config.json 
  → workflow_config["categories_config_path"] = "config/poundwholesale_categories.json"
    → Line 1834: Load JSON file from path
      → Extract category_urls array
        → len(category_urls) = total_categories
          → State manager initialization (line 1357)
            → Progress tracking throughout workflow
              → Hybrid processing mode decisions (lines 2295+)
```

#### 2. `supplier_name` Flow:
```
system_config.json
  → workflow_config["supplier_name"] = "poundwholesale.co.uk"
    → Line 1353: self.supplier_name = workflow_config.get("supplier_name")
      → Line 1357: EnhancedStateManager(self.supplier_name)
        → State persistence file: {supplier_name}_processing_state.json
          → Line 1386-1387: Cache paths construction
            → supplier_cache_dir = path_manager.get_output_path("cached_products")
              → Cache file: {supplier_name}_products_cache.json
                → Linking map dir: path_manager.get_linking_map_path(supplier_name)
                  → linking_maps/{supplier_name}/linking_map.json
```

#### 3. `supplier_url` Usage (Currently hardcoded in copies):
- Browser navigation
- URL validation
- Logging context
- Future: Should read from `workflow_config.get("supplier_url")`

---

## ⚠️ CRITICAL NOTES FOR NEXT SESSION

### 1. File Size Verification
Always verify file sizes with commands before making claims:
```bash
wc -l tools/passive_extraction_workflow_latest.py
# Correct output: 12028 lines (NOT 1200)
```

### 2. Workflow Identification
System uses **ONE primary workflow** with **hybrid processing enabled**:
- File: `tools/passive_extraction_workflow_latest.py` (12,028 lines)
- Hybrid processing: Lines 2295-7505
- Used by: Both poundwholesale and clearance-king
- **NOT** two separate workflows - one workflow with hybrid mode toggle

### 3. Browser Manager Method
**CRITICAL**: Browser manager exposes `close_browser()` NOT `cleanup()`:
```python
# CORRECT:
await browser_manager.close_browser()

# WRONG (will raise AttributeError):
await browser_manager.cleanup()
```

### 4. Implementation Order
When implementing, follow this exact order to minimize risk:
1. Add config keys to system_config.json (no code changes yet)
2. Update line 1834 (categories_config_path with fallback)
3. Test fallback works with missing config key
4. Test config read works with key present
5. Update linking map paths (lines 633, 1209, 7334)
6. Test both suppliers run simultaneously without conflicts
7. Document all changes

### 5. Testing Requirements
Before considering implementation complete:
- [ ] Poundwholesale runs with config (not fallback)
- [ ] Clearance-king runs with config (not fallback)
- [ ] Both create separate linking map directories
- [ ] No global constant conflicts
- [ ] Backwards compatibility works (fallback when config missing)
- [ ] Output files match previous runs (except timestamps)

---

## 📁 KEY FILES ANALYZED

1. `tools/passive_extraction_workflow_latest.py` - 12,028 lines
   - Line 1340: Class definition
   - Line 1341: Constructor signature
   - Line 1353: supplier_name initialization
   - Line 1834: Categories config path (HARDCODED - needs fix)
   - Line 633: LINKING_MAP_DIR global (needs instance variable)
   - Line 1209: _save_linking_map method (needs instance path)
   - Line 7334: Manifest path (needs instance path)

2. `run_custom_poundwholesale.py` - Entry point
   - Imports: `tools.passive_extraction_workflow_latest`
   - Config key: `'poundwholesale_workflow'`

3. `run_custom_clearance_king.py` - Entry point
   - Imports: `tools.clearance_king.passive_extraction_workflow_clearance_king`
   - Config key: `'clearance_king_workflow'`

4. `config/system_config.json` - Configuration
   - Needs: `{supplier}_workflow` sections with keys:
     - supplier_name
     - supplier_url
     - categories_config_path
     - use_predefined_categories
     - max_price_gbp, min_price_gbp

5. `utils/path_manager.py` - Path utilities
   - Method: `get_linking_map_path(supplier_name)`
   - Method: `get_output_path(...)`
   - Already exists and tested

---

## 🚀 NEXT STEPS FOR IMPLEMENTATION

1. **Create backup** of `tools/passive_extraction_workflow_latest.py`
2. **Implement Phase 1.1**: Categories config path with fallback (line 1834)
3. **Test fallback**: Remove config key temporarily, verify fallback works
4. **Add config keys**: Update system_config.json with supplier configs
5. **Test config read**: Verify config keys are read correctly
6. **Implement Phase 1.2**: Linking map instance variables (lines 633, 1209, 7334)
7. **Test isolation**: Run both suppliers, verify separate linking map directories
8. **Document changes**: Update implementation guide with config-driven approach
9. **Monitor logs**: Verify no hardcoded paths remain in log output

---

**End of Analysis** - Ready for implementation with clear, low-risk plan.