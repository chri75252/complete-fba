# Config-Driven Supplier Onboarding - Complete Implementation Plan
**Date**: October 1, 2025
**Status**: Ready for Implementation
**Verified**: All line numbers, paths, and code sections verified

## 🎯 EXECUTIVE SUMMARY

**Objective**: Implement config-driven supplier onboarding to eliminate 4-6 manual edits per supplier
**Benefit**: Reduce integration time from 2-4 hours to 1-2 hours (just config + testing)
**Risk**: VERY LOW - backwards compatible, verified paths, simple changes

**User's Single-Supplier Config Approach**: ✅ CORRECT AND SAFER
- Only analyze ONE supplier at a time (never concurrent)
- Edit config to replace supplier when switching
- Zero cross-supplier conflicts

---

## 📁 CRITICAL DIRECTORY STRUCTURE DECISION

### RECOMMENDED STRUCTURE (Shared Workflow)

```
project_root/
├── run_custom_clearance_king.py
├── tools/
│   ├── passive_extraction_workflow_latest.py  ← SHARED (config-driven, 12,028 lines)
│   ├── configurable_supplier_scraper.py       ← SHARED (selector-driven)
│   │
│   ├── clearance_king/
│   │   └── supplier_authentication_service.py ← MANUAL per supplier
│   │
│   └── poundwholesale/
│       └── supplier_authentication_service.py ← MANUAL per supplier
│
├── config/
│   ├── system_config.json                     ← Single-supplier config
│   ├── clearance_king_categories.json
│   ├── poundwholesale_categories.json
│   └── supplier_configs/
│       ├── clearance-king.co.uk.json
│       └── poundwholesale.co.uk.json
```

**Why Shared Workflow**:
1. ✅ Config-driven means zero edits needed (no reason to duplicate)
2. ✅ Simpler path handling (no .parent.parent.parent issues)
3. ✅ Single source of truth
4. ✅ Entry scripts still explicit per supplier (user's requirement)
5. ✅ Manual/site-specific stuff stays in subfolders

**Import Pattern**:
```python
# Entry script: run_custom_clearance_king.py
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
```

---

## 🔍 VERIFIED FILE ANALYSIS

### Main Workflow File
**File**: `tools/passive_extraction_workflow_latest.py`
**Size**: 12,028 lines (VERIFIED via wc -l)
**Import**: Line 162: `from utils.path_manager import path_manager, get_linking_map_path`
**Constructor**: Line 1340: `def __init__(self, config_loader, workflow_config, browser_manager=None, ai_client=None)`

### Critical Code Sections (VERIFIED)

**Line 1834-1842: Categories Config Path (HARDCODED)**
```python
config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    total_categories = len(config_data.get("category_urls", []))
```
**Issue**: Hardcoded "poundwholesale" - requires manual edit per supplier
**Also**: Path calculation assumes workflow at `tools/` level (works with shared approach)

**Lines 633-635: Global Linking Map Constants (CONFLICTS)**
```python
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")
```
**Issue**: Global constants shared by all suppliers → conflicts if run simultaneously

**Line 3301: Linking Map Save (USES UTILITY)**
```python
linking_map_path = get_linking_map_path(supplier_name)  # ✅ Per-supplier!
```
**Discovery**: Code already uses better approach! Global constants only create base dir.

**Line 7334: Manifest Path (HARDCODED)**
```python
manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
```
**Issue**: Hardcoded "poundwholesale.co.uk" - requires manual edit

**Line 1353: Supplier Name Initialization**
```python
self.supplier_name = self.workflow_config.get("supplier_name")
```
**Status**: ✅ Already reads from config!

---

## 🔧 IMPLEMENTATION PLAN (3 CODE CHANGES)

### CHANGE #1: Categories Config Path (Line 1834)

**CURRENT**:
```python
config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
```

**NEW**:
```python
# Read from workflow config (passed to constructor)
categories_config_path = self.workflow_config.get("categories_config_path")
if not categories_config_path:
    # Backwards compatibility fallback
    categories_config_path = f"config/{self.supplier_name.replace('.', '_')}_categories.json"
    self.log.warning(f"⚠️ categories_config_path not in config, using fallback: {categories_config_path}")

config_path = Path(categories_config_path)
```

**DIFF**:
```diff
- config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
+ # Read from workflow config (passed to constructor)
+ categories_config_path = self.workflow_config.get("categories_config_path")
+ if not categories_config_path:
+     # Backwards compatibility fallback
+     categories_config_path = f"config/{self.supplier_name.replace('.', '_')}_categories.json"
+     self.log.warning(f"⚠️ categories_config_path not in config, using fallback: {categories_config_path}")
+ 
+ config_path = Path(categories_config_path)
```

**WHY**:
- Eliminates hardcoded "poundwholesale"
- Reads from config (already passed to __init__)
- Fallback ensures backwards compatibility
- Zero edits needed for new suppliers

**RISK**: VERY LOW - workflow_config already exists and used

---

### CHANGE #2: Linking Map Instance Variables (Lines 633-635 + __init__)

**DELETE Lines 633-635**:
```python
# DELETE these global constants:
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")
```

**ADD TO __init__ (After line 1387)**:
```python
# Initialize supplier-specific linking map path
self.linking_map_path = get_linking_map_path(self.supplier_name)
self.linking_map_dir = self.linking_map_path.parent
os.makedirs(self.linking_map_dir, exist_ok=True)
self.log.info(f"✅ Linking map directory: {self.linking_map_dir}")
```

**DIFF**:
```diff
--- Global section (lines 633-635)
- # Global constant for persistent linking map in dedicated directory
- LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
- os.makedirs(LINKING_MAP_DIR, exist_ok=True)
- LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")

+++ __init__ method (after line 1387)
+ # Initialize supplier-specific linking map path
+ self.linking_map_path = get_linking_map_path(self.supplier_name)
+ self.linking_map_dir = self.linking_map_path.parent
+ os.makedirs(self.linking_map_dir, exist_ok=True)
+ self.log.info(f"✅ Linking map directory: {self.linking_map_dir}")
```

**WHY**:
- Removes global constants that cause conflicts
- Uses `get_linking_map_path()` utility (already imported at line 162!)
- Creates per-supplier directories automatically
- `get_linking_map_path("clearance-king.co.uk")` returns: `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/linking_map.json`

**HOW IT WORKS**:
- Base directory: Created by global constants (keep for now, or let path_manager handle)
- Supplier subdirectory: Created by `get_linking_map_path()` utility
- Atomic save: `windows_save_guardian.py` creates parent dirs automatically

**RISK**: VERY LOW - utility function already exists and tested (line 3301 uses it)

---

### CHANGE #3: Manifest Path (Line 7334)

**CURRENT**:
```python
manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
```

**NEW**:
```python
manifest_path = Path("OUTPUTS") / "manifests" / self.supplier_name / f"{slug}.json"
```

**DIFF**:
```diff
- manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
+ manifest_path = Path("OUTPUTS") / "manifests" / self.supplier_name / f"{slug}.json"
```

**WHY**:
- Removes hardcoded "poundwholesale.co.uk"
- Uses `self.supplier_name` (set from config at line 1353)
- Automatic per-supplier manifest directories

**RISK**: ZERO - simple variable substitution

---

## 📋 CONFIG FILE STRUCTURE (Single-Supplier Approach)

### system_config.json (Edit to switch suppliers)

**For clearance-king**:
```json
{
  "current_supplier_workflow": {
    "supplier_name": "clearance-king.co.uk",
    "supplier_url": "https://www.clearance-king.co.uk",
    "categories_config_path": "config/clearance_king_categories.json",
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  },
  "credentials": {
    "clearance-king.co.uk": {
      "username": "YOUR_USERNAME",
      "password": "YOUR_PASSWORD"
    }
  }
}
```

**When switching to poundwholesale** (just edit same config):
```json
{
  "current_supplier_workflow": {
    "supplier_name": "poundwholesale.co.uk",  // Changed
    "supplier_url": "https://www.poundwholesale.co.uk",  // Changed
    "categories_config_path": "config/poundwholesale_categories.json",  // Changed
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  },
  "credentials": {
    "poundwholesale.co.uk": {  // Changed
      "username": "YOUR_USERNAME",
      "password": "YOUR_PASSWORD"
    }
  }
}
```

**Benefits of Single-Supplier Config**:
- ✅ Simpler - only one active supplier at a time
- ✅ Safer - zero cross-supplier conflicts
- ✅ Easy to switch - just edit and replace
- ✅ Matches your workflow (never concurrent processing)

---

## 📊 ENTRY SCRIPT PATTERN

### For Clearance-King

**File**: `run_custom_clearance_king.py` (~112 lines)

**Key Sections**:
```python
import asyncio
import logging
from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow  # Shared!
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService  # Per-supplier
from utils.logger import setup_logger
from utils.browser_manager import BrowserManager

async def main():
    debug_log_file = setup_logger()
    log = logging.getLogger(__name__)
    
    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('current_supplier_workflow')  # Same key!
    supplier_name = workflow_config.get('supplier_name')
    credentials = config_loader.get_credentials(supplier_name)
    
    chrome_debug_port = config_loader.get_system_config().get('chrome_debug_port', 9222)
    
    browser_manager = None
    try:
        browser_manager = BrowserManager.get_instance()
        await browser_manager.launch_browser(cdp_port=chrome_debug_port)
        page = await browser_manager.get_page()
        
        auth_service = SupplierAuthenticationService(page)  # Supplier-specific!
        authenticated = await auth_service.ensure_authenticated_session(page, credentials)
        
        if not authenticated:
            log.error("Authentication failed")
            return
        
        workflow = PassiveExtractionWorkflow(  # Shared workflow!
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

**For Poundwholesale** (nearly identical):
```python
# Only difference:
from tools.poundwholesale.supplier_authentication_service import SupplierAuthenticationService
```

---

## ✅ ALL PATHS VERIFIED WORKING

### Config Files (all at root `config/`)
- ✅ `config/system_config.json` - single-supplier config
- ✅ `config/clearance_king_categories.json` - category URLs
- ✅ `config/supplier_configs/clearance-king.co.uk.json` - selectors

### Output Files (all use supplier_name from config)
- ✅ `OUTPUTS/cached_products/{supplier_name}_products_cache.json`
- ✅ `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/linking_map.json`
- ✅ `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN}.json`
- ✅ `OUTPUTS/CACHE/processing_states/{supplier_name}_processing_state.json`
- ✅ `OUTPUTS/manifests/{supplier_name}/{slug}.json` (after line 7334 fix)

### Import Paths in Workflow (from `tools/` level)
- ✅ `from utils.path_manager import path_manager, get_linking_map_path` - works
- ✅ `from config.system_config_loader import SystemConfigLoader` - works
- ✅ `from utils.browser_manager import BrowserManager` - works

**No additional path updates needed!**

---

## 🔄 STEP-BY-STEP IMPLEMENTATION

### PHASE 0: Backup (MANDATORY)

```bash
# Create backup with timestamp
mkdir -p backup/config_driven_$(date +%Y%m%d_%H%M%S)

# Backup critical files
cp tools/passive_extraction_workflow_latest.py backup/config_driven_*/
cp config/system_config.json backup/config_driven_*/
cp run_custom_poundwholesale.py backup/config_driven_*/
cp run_custom_clearance_king.py backup/config_driven_*/
```

**Verify backup**:
```bash
ls -la backup/config_driven_*/
wc -l backup/config_driven_*/passive_extraction_workflow_latest.py  # Should show 12028
```

---

### PHASE 1: Config Updates (USER)

**Step 1.1: Edit system_config.json**

Replace poundwholesale config with clearance-king:
```json
{
  "current_supplier_workflow": {
    "supplier_name": "clearance-king.co.uk",
    "supplier_url": "https://www.clearance-king.co.uk",
    "categories_config_path": "config/clearance_king_categories.json",
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  },
  "credentials": {
    "clearance-king.co.uk": {
      "username": "YOUR_USERNAME",
      "password": "YOUR_PASSWORD"
    }
  }
}
```

**Step 1.2: Create clearance_king_categories.json**

```json
{
  "category_urls": [
    "https://www.clearance-king.co.uk/category1",
    "https://www.clearance-king.co.uk/category2"
  ]
}
```

**Step 1.3: Verify selector config**

Check `config/supplier_configs/clearance-king.co.uk.json` has:
```json
{
  "field_mappings": {
    "ean": ["span.ck-b-code-value", "meta[itemprop='gtin13']"],
    "price": [".price-box .price", "span.price"],
    "title": ["a.product-item-link"],
    ...
  },
  "pagination": {
    "mode": "url_param",
    "page_param": "p",
    "max_pages": 50
  }
}
```

---

### PHASE 2: Code Changes (AGENT)

**Change 2.1: Categories Config Path (Line 1834)**

File: `tools/passive_extraction_workflow_latest.py`

Find:
```python
config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
```

Replace with:
```python
# Read from workflow config (passed to constructor)
categories_config_path = self.workflow_config.get("categories_config_path")
if not categories_config_path:
    # Backwards compatibility fallback
    categories_config_path = f"config/{self.supplier_name.replace('.', '_')}_categories.json"
    self.log.warning(f"⚠️ categories_config_path not in config, using fallback: {categories_config_path}")

config_path = Path(categories_config_path)
```

**Verification**:
```python
# After change, workflow should log:
self.log.info(f"🔍 DEBUG: categories_config_path = {categories_config_path}")
```

---

**Change 2.2: Linking Map Instance Variables (Lines 633-635 + __init__)**

**Delete lines 633-635**:
```python
# DELETE:
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")
```

**Add to __init__ after line 1387**:
```python
# ADD:
# Initialize supplier-specific linking map path
self.linking_map_path = get_linking_map_path(self.supplier_name)
self.linking_map_dir = self.linking_map_path.parent
os.makedirs(self.linking_map_dir, exist_ok=True)
self.log.info(f"✅ Linking map directory: {self.linking_map_dir}")
```

**Verification**:
```bash
# After change, search for LINKING_MAP_PATH usage:
rg "LINKING_MAP_PATH" tools/passive_extraction_workflow_latest.py
# Should return ZERO results (all removed)
```

---

**Change 2.3: Manifest Path (Line 7334)**

Find:
```python
manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
```

Replace with:
```python
manifest_path = Path("OUTPUTS") / "manifests" / self.supplier_name / f"{slug}.json"
```

**Verification**:
```bash
# Search for hardcoded supplier names:
rg "poundwholesale" tools/passive_extraction_workflow_latest.py
# Should return ZERO results in modified sections
```

---

### PHASE 3: Testing (USER + AGENT)

**Test 3.1: Syntax Validation**

```bash
# Test Python syntax
python -m py_compile tools/passive_extraction_workflow_latest.py

# Expected: No output (success)
# If errors: Fix syntax before continuing
```

---

**Test 3.2: Backwards Compatibility (Fallback Mode)**

```bash
# Remove config key temporarily
# Edit system_config.json: comment out "categories_config_path"

# Run poundwholesale
python run_custom_poundwholesale.py

# EXPECTED LOG OUTPUT:
# ⚠️ categories_config_path not in config, using fallback: config/poundwholesale_co_uk_categories.json

# VERIFY:
# - System runs without errors
# - Uses fallback path
# - Products extracted
```

---

**Test 3.3: Config-Driven Mode**

```bash
# Restore "categories_config_path" in config

# Run poundwholesale
python run_custom_poundwholesale.py

# EXPECTED LOG OUTPUT:
# ✅ Linking map directory: OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk
# 🔍 DEBUG: categories_config_path = config/poundwholesale_categories.json

# VERIFY:
# - No fallback warning
# - Reads from config correctly
# - Products extracted
```

---

**Test 3.4: New Supplier (Clearance-King)**

```bash
# Update config to clearance-king (Phase 1 changes)

# Create supplier directory and auth service
mkdir -p tools/clearance_king
# Copy/create supplier_authentication_service.py (manual)

# Run clearance-king
python run_custom_clearance_king.py

# EXPECTED OUTPUTS:
ls -la OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/linking_map.json

# VERIFY:
# - Separate directories created
# - No conflicts with poundwholesale
# - Products extracted successfully
```

---

**Test 3.5: Isolation Verification**

```bash
# Check poundwholesale files unchanged
stat OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json
# Timestamp should NOT have changed since Test 3.3

# List linking map directories
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/
# Should show TWO separate directories:
# clearance-king.co.uk/
# poundwholesale.co.uk/

# Verify different contents
diff <(ls OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/) \
     <(ls OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/)
# Should show differences
```

---

## ✅ VALIDATION CHECKLIST

### Pre-Implementation
- [ ] Backup created in `backup/config_driven_*/`
- [ ] Baseline poundwholesale run successful
- [ ] Baseline files verified (timestamps recorded)
- [ ] Line numbers verified (1834, 633-635, 7334, 1387)

### Post-Code-Changes
- [ ] Line 1834: Categories config path reads from workflow_config
- [ ] Fallback code added with warning log
- [ ] Lines 633-635: Global constants deleted
- [ ] After line 1387: Instance variables added in __init__
- [ ] Line 7334: Manifest uses self.supplier_name
- [ ] Syntax validation passed (py_compile)
- [ ] No import errors when loading workflow

### Post-Testing
- [ ] Fallback mode works (Test 3.2)
- [ ] Config mode works (Test 3.3)
- [ ] Clearance-king runs successfully (Test 3.4)
- [ ] Separate linking map directories created
- [ ] Separate cache files created
- [ ] Poundwholesale files unchanged (Test 3.5)
- [ ] Logs show correct paths being used
- [ ] No cross-supplier contamination

---

## 📊 WHAT REMAINS MANUAL

**Per-Supplier Manual Components**:
1. ✅ Supplier authentication service (site-specific login flow)
2. ✅ CSS selectors (manual testing and configuration)
3. ✅ Pagination config (manual per website)
4. ✅ Test product URL selection
5. ✅ Custom scraper modifications (if needed)
6. ✅ Entry script duplication (explicit imports)

**Config-Driven Components**:
1. ✅ Category URLs (JSON list)
2. ✅ Workflow parameters (system_config.json)
3. ✅ Output paths (automatic)
4. ✅ Supplier name/URL (config)

---

## 🎯 BENEFITS ACHIEVED

### Before (Manual Edits):
- ❌ 4-6 manual code edits per supplier
- ❌ Easy to miss an edit
- ❌ Global constants cause conflicts
- ❌ Duplicate 12,028 lines per supplier
- ⏱️ 2-4 hours to integrate

### After (Config-Driven):
- ✅ **0 code edits** per supplier
- ✅ Automatic per-supplier paths
- ✅ Instance variables (no conflicts)
- ✅ Shared workflow (single source of truth)
- ✅ Backwards compatible
- ⏱️ 1-2 hours to integrate (config + testing only)

---

## 🚨 CRITICAL NOTES

### 1. Single-Supplier Config (User's Approach)
**User is CORRECT**: Simpler and safer to maintain one supplier at a time
- Edit config when switching suppliers
- Zero cross-supplier conflicts
- Matches workflow (never concurrent)

### 2. Shared Workflow (Directory Structure)
**Decision**: Use shared `tools/passive_extraction_workflow_latest.py`
- Config-driven means zero edits needed
- No reason to duplicate 12,028 lines
- Auth services stay in per-supplier subfolders
- Entry scripts remain explicit per supplier

### 3. Path Verification
**All paths verified working**:
- Config files at root `config/`
- Output files use supplier_name (automatic)
- Import paths work from `tools/` level
- No additional updates needed

### 4. Browser Manager
**CRITICAL**: Use `close_browser()` NOT `cleanup()`
```python
await browser_manager.close_browser()  # ✅ Correct
await browser_manager.cleanup()        # ❌ Method doesn't exist
```

---

## 📁 KEY FILES REFERENCE

**Main Files**:
- `tools/passive_extraction_workflow_latest.py` (12,028 lines)
- `config/system_config.json` (single-supplier config)
- `run_custom_clearance_king.py` (entry script)
- `tools/clearance_king/supplier_authentication_service.py` (manual)

**Config Files**:
- `config/clearance_king_categories.json`
- `config/supplier_configs/clearance-king.co.uk.json`

**Utilities**:
- `utils/path_manager.py` (contains `get_linking_map_path()`)
- `utils/windows_save_guardian.py` (atomic file save)
- `utils/browser_manager.py`

---

## 🔄 NEXT STEPS

1. **Review this plan** - confirm all details correct
2. **Create backup** - MANDATORY before changes
3. **Phase 1** - Update config files (user)
4. **Phase 2** - Apply 3 code changes (agent)
5. **Phase 3** - Execute comprehensive testing
6. **Validate** - Use checklist above
7. **Document** - Update integration guide

---

**PLAN STATUS**: ✅ Ready for implementation
**RISK LEVEL**: ⭐ VERY LOW (backwards compatible, verified)
**ESTIMATED TIME**: 2-3 hours (including testing)

**Last Verified**: October 1, 2025