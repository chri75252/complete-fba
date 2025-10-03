# **Clearance-King Integration Task Handover - Complete Context**

## **📋 ORIGINAL USER REQUEST & STRICT REQUIREMENTS**

### **Primary Objective:**
User wants to **systemize** adding new websites to their existing Amazon FBA scanning system. Current system works perfectly with `poundwholesale.co.uk` via `run_custom_poundwholesale.py`. Goal is to add `clearance-king.co.uk` scanning capability.

### **🚨 CRITICAL CONSTRAINTS (USER'S EXACT WORDS):**
1. **"BE VERY CAREFUL AND WEARY OF NOT DISTURBING ANY STEPS FROM OUR CURRENT SYSTEM WORKFLOW, SCRIPTS, OUTFILES, ETC..."**
2. **"ANY FILE NEEDING EDITING, WILL BE COPIED AND THE COPY (WHICH YOU WILL PLACE IN A SUBFOLDER) WILL BE THE ONE TO BE EDITED"**
3. **"MAKE SURE THAT THESE NEW SUBFOLDERS AND/OR SCRIPT WILL NOT AFFECT THE CURRENT SYSTEM WORKFLOW"**
4. **"The only output files that will be 'shared' between different system runs will be the amazon_cache files"**
5. **"I want to run the system the same way I ran it for poundwholesale"**

### **Implementation Strategy Required:**
- Copy scripts requiring changes to subfolders (e.g., under tools, utils, config)
- Update copies to use parameters from config files instead of hardcoded values
- Create duplicates of supporting scripts in same subfolders for clarity
- Ensure zero impact on existing poundwholesale workflow

## **🔍 SYSTEM ANALYSIS COMPLETED**

### **Current Working System Architecture:**
```
Entry Point: run_custom_poundwholesale.py
├── Imports: tools/passive_extraction_workflow_latest.py (413KB main workflow)
├── Imports: tools/configurable_supplier_scraper.py
├── Imports: tools/supplier_authentication_service.py
├── Imports: utils/logger.py, utils/browser_manager.py
├── Config: config/system_config_loader.py
└── Categories: config/poundwholesale_categories.json
```

### **Files with Hardcoded `poundwholesale` References:**

#### **🎯 PRIMARY TARGETS (Must Copy & Modify):**

1. **`run_custom_poundwholesale.py`** (Entry Point)
   - Line 61: `workflow_config = config_loader.get_workflow_config('poundwholesale_workflow')`
   - Line 44: "Starting Custom Pound Wholesale Extraction Workflow"
   - Line 52: Print statement with "Pound Wholesale"

2. **`tools/passive_extraction_workflow_latest.py`** (Main Workflow - 413KB)
   - **Line 1834**: `config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"`
   - **Line 4288-4301**: Hardcoded URL optimization comments for poundwholesale.co.uk
   - **Line 7334**: `manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"`
   - **Line 11727**: `self.workflow_config.get("supplier_url", "https://www.poundwholesale.co.uk")`
   - **Line 11732**: `supplier_name = self.supplier_name or "poundwholesale.co.uk"`

3. **`tools/configurable_supplier_scraper.py`**
   - **Line 595**: `credentials = config_loader.get_credentials("poundwholesale.co.uk")`
   - **Line 804**: `credentials = config_loader.get_credentials("poundwholesale.co.uk")`
   - **Line 953**: `credentials = config_loader.get_credentials("poundwholesale.co.uk")`
   - **Line 1136**: `credentials = config_loader.get_credentials("poundwholesale.co.uk")`
   - **Line 3244**: `if not selectors or "poundwholesale" in (context_url or ""):`
   - **Line 3442**: Test supplier URL hardcoded

#### **🔧 SUPPORTING FILES (Copy for Isolation):**
- `tools/supplier_authentication_service.py` (No hardcoded refs, but copy for isolation)
- `utils/logger.py` (Referenced in run script)
- `utils/browser_manager.py` (Referenced in run script)
- `config/system_config_loader.py` (No hardcoded refs, but copy for isolation)
- `tools/standalone_playwright_login.py` (Referenced in run script)

## **📁 AVAILABLE RESOURCES & ASSETS**

### **Clearance-King Specific Files (Ready to Use):**
1. **`config/clearance_king_categories.json`** ✅ **155 categories in JSON format**
2. **`config/clearance_king_system_config_additions.json`** ✅ **Contains:**
   ```json
   {
     "clearance_king_credentials_addition": {
       "clearance-king.co.uk": {
         "username": "info@theblacksmithmarket.com",
         "password": "0Dqixm9c&"
       }
     },
     "clearance_king_workflow_addition": {
       "clearance_king_workflow": {
         "supplier_name": "clearance-king.co.uk",
         "supplier_url": "https://www.clearance-king.co.uk",
         "use_predefined_categories": true,
         "ai_client": null,
         "workflow_type": "passive_extraction",
         "authentication_required": true,
         "session_persistence": true
       }
     }
   }
   ```

3. **`config/supplier_configs/clearance-king.co.uk.json`** ✅ **Supplier selectors ready**
4. **`run_custom_clearance_king.py`** ✅ **Basic entry point created**

## **🏗️ IMPLEMENTATION PROGRESS**

### **✅ COMPLETED TASKS:**
1. **Subfolder Structure Created:**
   ```
   tools/clearance_king/     ← New isolated folder
   config/clearance_king/    ← New isolated folder
   utils/clearance_king/     ← New isolated folder
   ```

### **🔄 IN PROGRESS TASKS:**
1. **Entry Point Script Modification** - Started but incomplete
2. **Main Workflow Parameterization** - Identified changes needed

### **⏸️ PENDING TASKS:**
1. **Complete script copying and modification**
2. **System config integration**
3. **Supporting file copies**
4. **Testing and validation**

## **📝 DETAILED IMPLEMENTATION PLAN**

### **Phase 1: Script Copying & Modification**

#### **Task 1.1: Entry Point Script**
- **Source**: `run_custom_poundwholesale.py`
- **Target**: `run_custom_clearance_king.py` (already exists but needs completion)
- **Changes Required**:
  ```python
  # Line 61: Change workflow config name
  workflow_config = config_loader.get_workflow_config('clearance_king_workflow')

  # Line 44: Update display text
  print("🪟 --- Starting Custom Clearance King Extraction Workflow (Windows Native) ---")

  # Line 52: Update workflow name in prints
  print("--- Starting Custom Clearance King Extraction Workflow ---")

  # Line 107: Update final message
  print("--- Custom Clearance King Extraction Workflow Finished ---")

  # Import from clearance_king subfolders:
  from tools.clearance_king.passive_extraction_workflow_clearance_king import PassiveExtractionWorkflow
  from tools.clearance_king.configurable_supplier_scraper_clearance_king import *
  ```

#### **Task 1.2: Main Workflow Script**
- **Source**: `tools/passive_extraction_workflow_latest.py` (413KB file)
- **Target**: `tools/clearance_king/passive_extraction_workflow_clearance_king.py`
- **Critical Changes Required**:
  ```python
  # Line 1834: Change category file path
  config_path = Path(__file__).parent.parent.parent / "config" / "clearance_king_categories.json"

  # Lines 4288-4301: Remove poundwholesale-specific URL optimization
  # Replace with generic URL handling or clearance-king specific logic

  # Line 7334: Update manifest path
  manifest_path = Path("OUTPUTS") / "manifests" / "clearance-king.co.uk" / f"{slug}.json"

  # Line 11727: Update default supplier URL
  self.workflow_config.get("supplier_url", "https://www.clearance-king.co.uk")

  # Line 11732: Update default supplier name
  supplier_name = self.supplier_name or "clearance-king.co.uk"
  ```

#### **Task 1.3: Supplier Scraper Script**
- **Source**: `tools/configurable_supplier_scraper.py`
- **Target**: `tools/clearance_king/configurable_supplier_scraper_clearance_king.py`
- **Changes Required**:
  ```python
  # Replace all hardcoded credential calls:
  # FROM: credentials = config_loader.get_credentials("poundwholesale.co.uk")
  # TO: credentials = config_loader.get_credentials(self.supplier_name or "clearance-king.co.uk")

  # Line 3244: Update selector logic
  # FROM: if not selectors or "poundwholesale" in (context_url or ""):
  # TO: if not selectors or "clearance-king" in (context_url or ""):

  # Line 3442: Update test supplier URL
  # FROM: "url": "https://www.poundwholesale.co.uk/",
  # TO: "url": "https://www.clearance-king.co.uk/",
  ```

### **Phase 2: Supporting File Copies**
Copy these files to subfolders for complete isolation:
```
tools/supplier_authentication_service.py → tools/clearance_king/supplier_authentication_service.py
utils/logger.py → utils/clearance_king/logger.py
utils/browser_manager.py → utils/clearance_king/browser_manager.py
config/system_config_loader.py → config/clearance_king/system_config_loader.py
tools/standalone_playwright_login.py → tools/clearance_king/standalone_playwright_login.py
```

### **Phase 3: System Configuration Integration**
**Add to `config/system_config.json`**:

**At line 246 (in credentials section):**
```json
"clearance-king.co.uk": {
  "username": "info@theblacksmithmarket.com",
  "password": "0Dqixm9c&"
}
```

**At line 253 (in workflows section):**
```json
"clearance_king_workflow": {
  "supplier_name": "clearance-king.co.uk",
  "supplier_url": "https://www.clearance-king.co.uk",
  "use_predefined_categories": true,
  "ai_client": null,
  "workflow_type": "passive_extraction",
  "authentication_required": true,
  "session_persistence": true
}
```

## **🎯 OUTPUT ISOLATION STRATEGY**

### **Shared Files (Both Systems):**
- `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_*.json` ← **ONLY shared files**

### **Poundwholesale Outputs (Unchanged):**
```
OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json
OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/
OUTPUTS/CACHE/processing_states/poundwholesale-co-uk_processing_state.json
OUTPUTS/manifests/poundwholesale.co.uk/
```

### **Clearance-King Outputs (New, Isolated):**
```
OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json
OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/
OUTPUTS/CACHE/processing_states/clearance-king-co-uk_processing_state.json
OUTPUTS/manifests/clearance-king.co.uk/
```

## **🧪 TESTING STRATEGY**

### **Validation Steps:**
1. **Test Original System**: Run `python run_custom_poundwholesale.py` to ensure no impact
2. **Test New System**: Run `python run_custom_clearance_king.py`
3. **Verify Isolation**: Check output directories are separate
4. **Verify Sharing**: Check amazon_cache is shared between both

### **Success Criteria:**
- ✅ Both entry points work independently
- ✅ No cross-contamination of supplier-specific outputs
- ✅ Amazon cache sharing works correctly
- ✅ No modifications to original system files
- ✅ Categories load correctly for clearance-king (155 categories)

## **⚠️ CRITICAL IMPLEMENTATION NOTES**

### **Path Resolution Strategy:**
- Use relative imports within clearance_king subfolders
- Update sys.path if needed for subfolder imports
- Ensure config file paths resolve correctly from subfolders

### **Import Strategy for New Scripts:**
```python
# In run_custom_clearance_king.py:
from tools.clearance_king.passive_extraction_workflow_clearance_king import PassiveExtractionWorkflow
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
from utils.clearance_king.logger import setup_logger
from utils.clearance_king.browser_manager import BrowserManager
from config.clearance_king.system_config_loader import SystemConfigLoader
```

### **Error Handling Considerations:**
- Ensure all hardcoded paths are parameterized
- Test category file loading from new location
- Verify authentication works with clearance-king credentials
- Check manifest and output directory creation

## **📊 CURRENT STATUS SUMMARY**

### **Progress Percentage: ~25% Complete**
- ✅ **Analysis Phase**: 100% Complete
- ✅ **Folder Structure**: 100% Complete
- 🔄 **Script Modification**: 10% Complete
- ⏸️ **Config Integration**: 0% Complete
- ⏸️ **Testing**: 0% Complete

### **Files Ready for Use:**
- `config/clearance_king_categories.json` (155 categories)
- `config/clearance_king_system_config_additions.json` (credentials & workflow)
- `config/supplier_configs/clearance-king.co.uk.json` (selectors)
- Subfolder structure created

### **Next Immediate Actions:**
1. **Complete copying and modifying the 3 core scripts**
2. **Update all hardcoded references with parameters**
3. **Copy supporting files to subfolders**
4. **Integrate config additions into system_config.json**
5. **Test both systems work independently**

## **🔧 TECHNICAL CONTEXT**

### **Working Directory:**
```
C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-
```

### **Key Technology Stack:**
- Python 3.12+ (Windows event loop considerations in entry scripts)
- Playwright browser automation
- Async/await throughout
- JSON-based configuration
- Modular architecture with utils, tools, config separation

### **Authentication Details:**
- Clearance-King URL: `https://www.clearance-king.co.uk`
- Login: `info@theblacksmithmarket.com` / `0Dqixm9c&`
- Uses same authentication service as poundwholesale

### **Category Management:**
- Poundwholesale: `config/poundwholesale_categories.json`
- Clearance-King: `config/clearance_king_categories.json` (155 categories ready)
- Both use `use_predefined_categories: true` mode

## **📋 HANDOVER CHECKLIST**

### **For Next Developer:**
- [ ] Read user's strict requirements about isolation
- [ ] Complete script copying and modification (3 core files)
- [ ] Update all hardcoded `poundwholesale` references
- [ ] Copy supporting files to subfolders
- [ ] Integrate config additions into system_config.json
- [ ] Test both systems work independently
- [ ] Verify output isolation (except amazon_cache sharing)
- [ ] Generate detailed implementation report
- [ ] Document all changes made to each file

### **Critical Success Factors:**
1. **Zero impact on existing poundwholesale workflow**
2. **Complete output isolation (except amazon_cache)**
3. **All hardcoded references parameterized**
4. **Both entry points work identically to original**

---

**Created**: 2025-01-27
**Task Status**: 25% Complete - Ready for handover
**Priority**: High - User expects systematic approach for future websites
**Risk Level**: Medium - Must not break existing system