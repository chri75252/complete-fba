# Config-Driven Supplier Onboarding - CORRECTED & COMPLETE Plan
**Date**: October 1, 2025
**Status**: Ready for Implementation with Manual Steps Clarified
**System Mode**: HYBRID PROCESSING MODE (AI disabled, selector-driven)

---

## 🎯 CRITICAL CLARIFICATIONS

### 1. NO Custom Scraper Scripts
**SHARED Script**: `tools/configurable_supplier_scraper.py`
- ✅ ONE shared scraper for ALL suppliers
- ✅ Reads selectors from `config/supplier_configs/{domain}.json`
- ❌ NOT duplicated per supplier
- ✅ Manual work = editing JSON selector config, NOT Python script

### 2. NO Workflow Duplication
**SHARED Workflow**: `tools/passive_extraction_workflow_latest.py` (12,028 lines)
- ✅ ONE workflow file for ALL suppliers (config-driven)
- ✅ Zero edits needed after config-driven changes
- ❌ NOT duplicated per supplier
- ✅ Entry scripts (`run_custom_{supplier}.py`) created per supplier for explicit imports

---

## 📁 COMPLETE FILE STRUCTURE

```
project_root/
├── run_custom_clearance_king.py        ← PER-SUPPLIER (explicit imports)
├── run_custom_poundwholesale.py        ← PER-SUPPLIER (explicit imports)
│
├── tools/
│   ├── passive_extraction_workflow_latest.py    ← SHARED (12,028 lines, config-driven)
│   ├── configurable_supplier_scraper.py         ← SHARED (selector-driven)
│   ├── FBA_Financial_calculator.py              ← SHARED
│   │
│   ├── clearance_king/
│   │   └── supplier_authentication_service.py   ← MANUAL per supplier
│   │
│   └── poundwholesale/
│       └── supplier_authentication_service.py   ← MANUAL per supplier
│
├── config/
│   ├── system_config.json                       ← SINGLE-SUPPLIER CONFIG (edit to switch)
│   ├── clearance_king_categories.json           ← MANUAL: Category URLs
│   ├── poundwholesale_categories.json
│   │
│   └── supplier_configs/
│       ├── clearance-king.co.uk.json            ← MANUAL: Selectors, pagination
│       └── poundwholesale.co.uk.json
│
└── utils/
    ├── browser_manager.py                       ← SHARED
    ├── path_manager.py                          ← SHARED
    └── enhanced_state_manager.py                ← SHARED
```

---

## 🔧 WHAT REQUIRES MANUAL WORK PER SUPPLIER

### Manual Component #1: Selector Configuration JSON
**File**: `config/supplier_configs/clearance-king.co.uk.json`
**Requires**: Manual testing in browser DevTools

**Manual Steps**:
1. Open clearance-king.co.uk in browser
2. Use DevTools to find CSS selectors for:
   - Product title
   - Price (may be login-required)
   - EAN/barcode
   - Product URL
   - Product image
   - Stock status
3. Test pagination pattern (URL params vs button clicks)
4. Update JSON file with working selectors

**Example Manual Configuration**:
```json
{
  "field_mappings": {
    "ean": ["span.ck-b-code-value", "meta[itemprop='gtin13']"],
    "price": [".price-box .price", "span.price"],
    "title": ["a.product-item-link"],
    "url": ["a.product-item-link"],
    "image": ["img.product-image-photo"]
  },
  "pagination": {
    "pattern": "https://www.clearance-king.co.uk/catalogsearch/result/index/?q={query}&p={page}",
    "use_url_navigation": true,
    "next_button_selector": ["a.action.next"]
  }
}
```

---

### Manual Component #2: Categories JSON
**File**: `config/clearance_king_categories.json`
**Requires**: Manual site navigation

**Manual Steps**:
1. Navigate clearance-king.co.uk
2. Identify product category pages
3. Copy URLs to JSON file

**Example**:
```json
{
  "category_urls": [
    "https://www.clearance-king.co.uk/health-beauty",
    "https://www.clearance-king.co.uk/toys-games",
    "https://www.clearance-king.co.uk/food-drink"
  ]
}
```

---

### Manual Component #3: Authentication Service
**File**: `tools/clearance_king/supplier_authentication_service.py`
**Requires**: Manual implementation of site-specific login flow

**Manual Steps**:
1. Copy template from poundwholesale version
2. Update login URL
3. Update CSS selectors for login form
4. Test login flow manually
5. Adjust timing/waits as needed

---

### Manual Component #4: Entry Script
**File**: `run_custom_clearance_king.py`
**Requires**: Copy/modify from poundwholesale version

**Key Changes**:
```python
# Import supplier-specific auth service
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService

# Rest stays same (uses shared workflow)
```

---

## 🔄 COMPLETE WORKFLOW: POST-IMPLEMENTATION

### For Adding Clearance-King (FIRST TIME)

**PHASE 1: Manual Configuration Files** (USER)

**Step 1.1**: Test and create selector config
```bash
# File: config/supplier_configs/clearance-king.co.uk.json
# Manual browser testing → find working selectors → save JSON
```

**Step 1.2**: Create categories list
```bash
# File: config/clearance_king_categories.json
# Manual site navigation → copy URLs → save JSON
```

**Step 1.3**: Update system config
```bash
# File: config/system_config.json
# Edit to replace poundwholesale with clearance-king
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

---

**PHASE 2: Manual Authentication Service** (USER)

**Step 2.1**: Create supplier subfolder
```bash
mkdir -p tools/clearance_king
```

**Step 2.2**: Create authentication service
```bash
# File: tools/clearance_king/supplier_authentication_service.py
# Copy from poundwholesale version
# Update selectors for clearance-king login page
# Test manually
```

---

**PHASE 3: Entry Script** (USER)

**Step 3.1**: Create entry script
```bash
# File: run_custom_clearance_king.py
# Copy from run_custom_poundwholesale.py
# Change ONE line:
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
```

---

**PHASE 4: Testing** (USER)

**Step 4.1**: Test authentication
```bash
python run_custom_clearance_king.py
# Verify login works
# Stop after authentication confirmed
```

**Step 4.2**: Test scraping (small batch)
```bash
# Edit system_config.json temporarily:
# Set max_products: 5
python run_custom_clearance_king.py
```

**Step 4.3**: Verify outputs created
```bash
ls -la OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/
```

**Step 4.4**: Full run (restore max_products)
```bash
python run_custom_clearance_king.py
```

---

### For Switching Back to Poundwholesale

**Step 1**: Edit system_config.json
```json
{
  "current_supplier_workflow": {
    "supplier_name": "poundwholesale.co.uk",
    "supplier_url": "https://www.poundwholesale.co.uk",
    "categories_config_path": "config/poundwholesale_categories.json",
    ...
  }
}
```

**Step 2**: Run poundwholesale
```bash
python run_custom_poundwholesale.py
```

---

## 🛠️ CODE CHANGES (Config-Driven Workflow)

### CHANGE #1: Categories Config Path (Line ~1834)

**File**: `tools/passive_extraction_workflow_latest.py`

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

---

### CHANGE #2: Linking Map Instance Variables

**DELETE** (Lines ~633-635):
```python
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")
```

**ADD TO __init__** (After line ~1387):
```python
# Initialize supplier-specific linking map path
self.linking_map_path = get_linking_map_path(self.supplier_name)
self.linking_map_dir = self.linking_map_path.parent
os.makedirs(self.linking_map_dir, exist_ok=True)
self.log.info(f"✅ Linking map directory: {self.linking_map_dir}")
```

---

### CHANGE #3: Manifest Path (Line ~7334)

**BEFORE**:
```python
manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
```

**AFTER**:
```python
manifest_path = Path("OUTPUTS") / "manifests" / self.supplier_name / f"{slug}.json"
```

---

## ✅ BENEFITS SUMMARY

**Before Config-Driven**:
1. ❌ Edit line 1834 (categories path) → hardcoded supplier name
2. ❌ Edit line 7334 (manifest path) → hardcoded supplier name
3. ❌ Edit linking map constants → potential conflicts
4. ✅ Manual: Selector config JSON
5. ✅ Manual: Categories JSON
6. ✅ Manual: Authentication service
7. ✅ Manual: Entry script

**After Config-Driven**:
1. ✅ **ZERO** edits to workflow file (automatic from config)
2. ✅ **ZERO** edits to scraper file (selector-driven)
3. ✅ **ZERO** hardcoded supplier names
4. ✅ Manual: Selector config JSON (unchanged - still needed)
5. ✅ Manual: Categories JSON (unchanged - still needed)
6. ✅ Manual: Authentication service (unchanged - still needed)
7. ✅ Manual: Entry script (unchanged - still needed)

**Time Savings**: ~30-60 minutes per supplier (no code editing/testing)

---

## 🚨 SYSTEM MODE VERIFICATION

**Current System Mode**: HYBRID PROCESSING MODE
- ✅ AI features DISABLED (`ai_client=None`)
- ✅ Selector-based extraction ENABLED
- ✅ Predefined categories ENABLED (`use_predefined_categories=True`)
- ✅ State management ENABLED (resume capability)
- ✅ Financial analysis ENABLED

**Config Verification**:
```json
// system_config.json should have:
{
  "current_supplier_workflow": {
    "use_predefined_categories": true,  // ← REQUIRED
    "use_ai_category_progression": false  // ← REQUIRED
  }
}
```

---

## 📊 VALIDATION CHECKLIST

### Pre-Implementation
- [ ] System in HYBRID mode (AI disabled)
- [ ] Backup created
- [ ] Line numbers verified
- [ ] Baseline run successful

### Post-Implementation
- [ ] All 3 code changes applied
- [ ] Syntax validation passed
- [ ] Backwards compatibility works
- [ ] Config-driven mode works
- [ ] New supplier (clearance-king) works
- [ ] Output isolation verified
- [ ] Manual components documented

---

**READY FOR IMPLEMENTATION**
**NEXT**: Create backup → Apply changes → Test → Generate guide