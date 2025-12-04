# Complete Workflow Example: wholesaletradingsupplies.com

## 📋 Overview
This example demonstrates the complete supplier onboarding workflow for `wholesaletradingsupplies.com`, showing the critical distinction between:
- **Actual domain** (from supplier URL) → Used for configuration
- **Operational naming** (.co.uk convention) → Used for file names

## 🔗 Supplier Information
- **Website**: https://wholesaletradingsupplies.com
- **Actual Domain**: wholesaletradingsupplies.com
- **Authentication**: Not required
- **Categories**: 22 predefined categories

---

## Step 0: Initial Information Gathering

### User Provides:
```
Supplier: wholesaletradingsupplies.com
URL: https://wholesaletradingsupplies.com
Authentication: No
Categories: I have them in setup/wholesaletradingsupplies_categories.txt
Test Product: https://wholesaletradingsupplies.com/product/sample-product/
Selectors: I'll provide them
Pagination: ?page=N
```

---

## Step 1: Data Preprocessing & Domain Extraction

### 1.1 Domain Extraction Protocol
```python
from urllib.parse import urlparse

url = "https://wholesaletradingsupplies.com"
extracted_domain = urlparse(url).hostname
# Result: "wholesaletradingsupplies.com"

# Record for consistency
actual_domain = extracted_domain
operational_name = "wholesaletradingsupplies-co-uk"  # .co.uk convention
```

### 1.2 Categories Validation
```bash
# Read categories file
setup/wholesaletradingsupplies_categories.txt

# Contains 22 URLs like:
https://wholesaletradingsupplies.com/shop/?_product_categories=baby
https://wholesaletradingsupplies.com/shop/?_product_categories=bath-care
# ... (all use actual domain wholesaletradingsupplies.com)
```

### 1.3 Selectors Creation
```json
{
  "supplier_url": "https://wholesaletradingsupplies.com",
  "field_mappings": {
    "product_item": ["div.w-full.md\\:w-1\\/2.lg\\:w-1\\/3.px-8.mb-16"],
    "title": ["a[href*='product/']"],
    "price": ["div.p-4.w-full.mt-auto"],
    "url": ["a[href*='product/']"],
    "image": ["img"],
    "next_page_selector": ["a.facetwp-page.next"]
  },
  "authentication_required": false
}
```

### 1.4 Domain Consistency Map
```json
{
  "extracted_domain": "wholesaletradingsupplies.com",
  "source_url": "https://wholesaletradingsupplies.com",
  "consistency_map": {
    "config_filename": "wholesaletradingsupplies.com.json",
    "system_config_supplier_name": "wholesaletradingsupplies.com",
    "config_supplier_id": "wholesaletradingsupplies.com",
    "workflow_key": "wholesaletradingsupplies_workflow"
  }
}
```

---

## Step 2: Configuration Files Creation

### 2.1 Categories Configuration
**File**: `config/wholesaletradingsupplies_workflow_categories.json`
```json
{
  "category_urls": [
    "https://wholesaletradingsupplies.com/shop/?_product_categories=baby",
    "https://wholesaletradingsupplies.com/shop/?_product_categories=bath-care",
    // ... 22 total categories
  ],
  "total_categories": 22,
  "supplier": "wholesaletradingsupplies.com",
  "source": "config/wholesaletradingsupplies_categories.json",
  "validated_at": "2025-12-03T10:30:00Z"
}
```

### 2.2 Selector Configuration
**File**: `config/supplier_configs/wholesaletradingsupplies.com.json`
```json
{
  "supplier_id": "wholesaletradingsupplies.com",  // ✅ MUST match actual domain
  "supplier_name": "Wholesale Trading Supplies UK",
  "supplier_url": "https://wholesaletradingsupplies.com",  // ✅ MUST match actual URL
  "base_url": "https://wholesaletradingsupplies.com/",
  "login_config": {
    "login_path": null,
    "test_product_url": "https://wholesaletradingsupplies.com/product/sample-product/"
  },
  "field_mappings": {
    "product_item": ["div.w-full.md\\:w-1\\/2.lg\\:w-1\\/3.px-8.mb-16"],
    "title": ["a[href*='product/']"],
    "price": ["div.p-4.w-full.mt-auto"],
    "url": ["a[href*='product/']"],
    "image": ["img"],
    "next_page_selector": ["a.facetwp-page.next"]
  },
  "authentication_required": false
}
```

### 2.3 System Configuration Update
**File**: `config/system_config.json`
```json
"wholesaletradingsupplies_workflow": {
  "supplier_name": "wholesaletradingsupplies.com",  // ✅ MUST match actual domain
  "supplier_url": "https://wholesaletradingsupplies.com",
  "categories_config_path": "config/wholesaletradingsupplies_workflow_categories.json",
  "use_predefined_categories": true,
  "authentication_required": false
}
```

---

## Step 3: Wizard Execution

### 3.1 Command
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "wholesaletradingsupplies.com" \
  --categories-source "config/wholesaletradingsupplies_workflow_categories.json" \
  --selectors-source "config/supplier_configs/wholesaletradingsupplies.com.json" \
  --workflow-key "wholesaletradingsupplies_workflow" \
  --mode generate \
  --authentication-required false
```

### 3.2 Expected Output
```
✅ Generated runner: run_custom_wholesaletradingsupplies-co-uk.py
✅ Generated categories: config/wholesaletradingsupplies_workflow_categories.json
✅ Registered workflow: wholesaletradingsupplies_workflow
✅ Sanity check: 6/6 criteria passed
```

---

## Step 4: File Validation

### 4.1 Config File Validation
```bash
# Check: config/supplier_configs/wholesaletradingsupplies.com.json

✅ Filename uses actual domain: wholesaletradingsupplies.com.json ✓
✅ supplier_id matches actual domain: wholesaletradingsupplies.com ✓
✅ supplier_url matches actual URL: https://wholesaletradingsupplies.com ✓
✅ All required selectors present ✓
✅ authentication_required: false ✓
```

### 4.2 System Config Validation
```bash
# Check: config/system_config.json

✅ supplier_name matches actual domain: wholesaletradingsupplies.com ✓
✅ supplier_url matches actual URL: https://wholesaletradingsupplies.com ✓
✅ categories_config_path correct: wholesaletradingsupplies_workflow_categories.json ✓
✅ authentication_required: false ✓
```

### 4.3 Runner Script Validation
```bash
# Check: run_custom_wholesaletradingsupplies-co-uk.py

✅ Line count: 135 lines (117-143 range) ✓
✅ Uses hyphen-form naming: wholesaletradingsupplies-co-uk ✓
✅ References correct workflow: wholesaletradingsupplies_workflow ✓
✅ No authentication logic (correct for non-auth supplier) ✓
✅ All template fixes present ✓
```

---

## Step 5: Operational Naming Validation

### 5.1 Verify Operational Files Use .co.uk Convention
```bash
# These files should exist and use .co.uk convention:

✅ Runner: run_custom_wholesaletradingsupplies-co-uk.py
   → Uses hyphen-form (supplier-co-uk) ✓

✅ Cache: wholesaletradingsupplies-co-uk_products_cache.json
   → Uses hyphen-form ✓

✅ Linking Map: wholesaletradingsupplies.co.uk/linking_map.json
   → Uses dot-form ✓

✅ State File: wholesaletradingsupplies_co_uk_processing_state.json
   → Uses underscore-form ✓
```

### 5.2 Verify No Domain Mismatches
```bash
# Check that operational names don't try to use .com:

❌ WRONG: run_custom_wholesaletradingsupplies.com.py  (would be wrong)
✅ CORRECT: run_custom_wholesaletradingsupplies-co-uk.py

❌ WRONG: wholesaletradingsupplies.com_products_cache.json  (would be wrong)
✅ CORRECT: wholesaletradingsupplies-co-uk_products_cache.json

❌ WRONG: wholesaletradingsupplies.com/linking_map.json  (would be wrong)
✅ CORRECT: wholesaletradingsupplies.co.uk/linking_map.json
```

---

## Step 6: Pre-Run Verification

### 6.1 Domain Consistency Check
```bash
python sample_data/working_examples/domain_consistency_validator.py --supplier wholesaletradingsupplies.com

Expected Output:
✅ Configuration Domain Consistency: PASSED
✅ System config domain consistency: PASSED
✅ Operational naming convention: PASSED
✅ ALL VALIDATIONS PASSED - Ready for execution
```

### 6.2 System Readiness Check
```bash
# Verify Chrome is running
curl http://localhost:9222/json/version

# Verify file permissions
ls -la run_custom_wholesaletradingsupplies-co-uk.py
ls -la config/supplier_configs/wholesaletradingsupplies.com.json

# Verify UTF-8 support
python -c "import locale; print(locale.getpreferredencoding())"
```

---

## Step 7: User Decision

### 7.1 Options Presented
```
═══════════════════════════════════════════════════════════
🚀 EXECUTION OPTIONS
═══════════════════════════════════════════════════════════

System verification complete. Choose how to proceed:

1️⃣ TEST RUN (Recommended)
   ⏱️ Duration: 20 seconds
   📊 Purpose: Smoke test to validate scraping begins correctly
   Command: python run_custom_wholesaletradingsupplies-co-uk.py
   # Interrupt after 20 seconds: Ctrl+C

2️⃣ MAIN RUN (Full Execution)
   ⏱️ Duration: 30-60 minutes (22 categories)
   📊 Purpose: Complete processing pipeline
   Command: python run_custom_wholesaletradingsupplies-co-uk.py

3️⃣ FIX ISSUES FIRST (If Problems Found)
   🔧 Action: Return to appropriate step
   - Content issues → Return to Step 0
   - Wizard issues → Return to Step 3
   - Validation issues → Return to Step 4

═══════════════════════════════════════════════════════════

❓ YOUR CHOICE: [ ] Test Run  [ ] Main Run  [ ] Fix Issues
═══════════════════════════════════════════════════════════
```

---

## 🎯 Success Criteria Met

✅ **Configuration Domain Consistency**: All config files use actual domain (.com)
✅ **Operational Naming Convention**: All operational files use .co.uk convention
✅ **Cross-File Validation**: No domain mismatches detected
✅ **System Integration**: All files reference correct domains
✅ **Backward Compatibility**: Existing operational naming preserved

---

## 🔍 What This Prevents

**Before this guidance**: Agent might assume .co.uk for config files, causing "No selector config file found" even when page loads successfully.

**After this guidance**: Agent correctly extracts actual domain and uses it consistently in configuration while maintaining operational .co.uk convention.""""file_path":"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\.claude\skills\supplier-onboarding\sample_data\working_examples\complete_workflow_example.md