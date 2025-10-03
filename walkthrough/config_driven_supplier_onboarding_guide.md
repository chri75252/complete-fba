# Config-Driven Supplier Onboarding Guide
**Version**: 1.0
**Date**: October 1, 2025
**System Mode**: HYBRID PROCESSING (AI disabled, selector-driven)
**Status**: POST-IMPLEMENTATION GUIDE

---

## 📋 OVERVIEW

This guide provides the **complete step-by-step process** for adding a new supplier website to the Amazon FBA Agent System after the config-driven implementation.

### What Changed (Implementation Completed)
✅ **3 code changes applied** to `tools/passive_extraction_workflow_latest.py`:
- Line 1834: Categories config path now reads from `system_config.json`
- Lines 633-635: Global linking map constants removed, added instance variables
- Line 7345: Manifest path uses `self.supplier_name` instead of hardcoded value

### Key Benefits
- ✅ **ZERO** code edits to `passive_extraction_workflow_latest.py` per supplier
- ✅ **ZERO** code edits to `configurable_supplier_scraper.py` per supplier
- ✅ **ZERO** hardcoded supplier names in workflow logic
- ✅ Automatic per-supplier output directories (linking maps, manifests, cache)
- ✅ Single-supplier config (edit to switch suppliers)
- ✅ Backwards compatible with fallback behavior

---

## 🎯 WHAT YOU NEED TO DO (Per New Supplier)

### Manual Tasks Summary
1. ✅ **Test and configure CSS selectors** (in JSON file)
2. ✅ **Create categories list** (in JSON file)
3. ✅ **Update system config** (edit JSON to replace supplier)
4. ✅ **Create authentication service** (copy/modify Python script)
5. ✅ **Create entry script** (copy/modify Python script)
6. ✅ **Test thoroughly** (small batch → full run)

### What Happens Automatically
- ✅ Categories config loaded from path in `system_config.json`
- ✅ Linking map directory created at `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/`
- ✅ Manifest directory created at `OUTPUTS/manifests/{supplier_name}/`
- ✅ Cache file created at `OUTPUTS/cached_products/{supplier_name}_products_cache.json`
- ✅ Processing state created at `OUTPUTS/CACHE/processing_states/{supplier_name}_processing_state.json`

---

## 📁 FILE STRUCTURE REFERENCE

```
project_root/
├── run_custom_clearance_king.py        ← CREATE (per supplier)
├── run_custom_poundwholesale.py        ← EXISTS (reference template)
│
├── tools/
│   ├── passive_extraction_workflow_latest.py    ← SHARED (no edits needed)
│   ├── configurable_supplier_scraper.py         ← SHARED (no edits needed)
│   │
│   ├── clearance_king/                          ← CREATE (per supplier)
│   │   └── supplier_authentication_service.py   ← CREATE (manual)
│   │
│   └── poundwholesale/                          ← EXISTS (reference)
│       └── supplier_authentication_service.py
│
├── config/
│   ├── system_config.json                       ← EDIT (replace supplier)
│   ├── clearance_king_categories.json           ← CREATE (category URLs)
│   ├── poundwholesale_categories.json           ← EXISTS (reference)
│   │
│   └── supplier_configs/
│       ├── clearance-king.co.uk.json            ← CREATE (selectors)
│       └── poundwholesale.co.uk.json            ← EXISTS (reference)
```

---

## 🔄 STEP-BY-STEP: ADDING NEW SUPPLIER (clearance-king.co.uk)

### PHASE 1: Test and Configure Selectors

**Step 1.1**: Open supplier website in browser
```
https://www.clearance-king.co.uk
```

**Step 1.2**: Use Chrome DevTools to find CSS selectors

**Open DevTools**:
- Right-click on product → Inspect
- Find unique selectors for each field

**Required Fields to Find**:
```yaml
Product List Page:
  - product_item: Container for each product
  - title: Product name/link
  - price: Price (may require login)
  - url: Product detail page link
  - image: Product image
  - ean: Barcode/EAN (usually on detail page)

Product Detail Page:
  - product_detail_title: Full product name
  - product_detail_price: Price on detail page
  - ean: Barcode location on detail page
  - out_of_stock: Stock status indicator

Pagination:
  - next_button_selector: "Next page" button
  - Pattern: URL structure for page navigation
```

**Step 1.3**: Create selector configuration file

**File**: `config/supplier_configs/clearance-king.co.uk.json`

```json
{
  "supplier_id": "clearance-king.co.uk",
  "supplier_name": "Clearance King UK",
  "base_url": "https://www.clearance-king.co.uk/",

  "authentication": {
    "login_url": "https://www.clearance-king.co.uk/customer/account/login/",
    "login_selectors": {
      "email_field": "input#email",
      "password_field": "input#pass",
      "login_button": "button#send2.action.login.primary"
    },
    "authentication_check_selectors": [
      ".customer-welcome",
      ".logged-in"
    ]
  },

  "field_mappings": {
    "product_item": [
      "li.item.product.product-item",
      ".product-item"
    ],
    "title": [
      ".product-item-name a",
      "a.product-item-link"
    ],
    "price": [
      ".price-box .price",
      "span.price"
    ],
    "url": [
      "a.product-item-link"
    ],
    "image": [
      "img.product-image-photo"
    ],
    "ean": [
      "span.ck-b-code-value",
      "meta[itemprop='gtin13']"
    ],
    "out_of_stock": [
      "div.stock.unavailable",
      ".stock.unavailable span"
    ]
  },

  "pagination": {
    "pattern": "https://www.clearance-king.co.uk/catalogsearch/result/index/?q={query}&p={page}",
    "use_url_navigation": true,
    "next_button_selector": [
      "a.action.next"
    ]
  }
}
```

**Step 1.4**: Test selectors manually
```
1. Open category page in browser
2. Use DevTools console to test each selector
3. Verify selectors return expected elements
4. Adjust selectors if needed
```

---

### PHASE 2: Create Categories List

**Step 2.1**: Navigate supplier website and identify product categories

**Step 2.2**: Copy category URLs

**Example categories to look for**:
- Health & Beauty
- Toys & Games
- Food & Drink
- Home & Garden
- Electronics

**Step 2.3**: Create categories configuration file

**File**: `config/clearance_king_categories.json`

```json
{
  "category_urls": [
    "https://www.clearance-king.co.uk/health-beauty",
    "https://www.clearance-king.co.uk/toys-games",
    "https://www.clearance-king.co.uk/food-drink",
    "https://www.clearance-king.co.uk/home-garden",
    "https://www.clearance-king.co.uk/electronics"
  ]
}
```

**Tips**:
- Start with 2-3 categories for initial testing
- Add more categories after successful test run
- Categories with login-required pricing need credentials

---

### PHASE 3: Update System Configuration

**Step 3.1**: Edit `config/system_config.json`

**Replace the entire `current_supplier_workflow` section**:

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
      "username": "YOUR_EMAIL@example.com",
      "password": "YOUR_PASSWORD"
    }
  }
}
```

**Step 3.2**: Verify config values
```json
✅ supplier_name: Must match domain (clearance-king.co.uk)
✅ supplier_url: Must be the base URL
✅ categories_config_path: Must match created JSON file
✅ use_predefined_categories: Must be true (HYBRID mode)
✅ credentials: Must have valid login credentials
```

---

### PHASE 4: Create Authentication Service

**Step 4.1**: Create supplier subfolder
```bash
mkdir -p tools/clearance_king
```

**Step 4.2**: Copy template from poundwholesale
```bash
cp tools/poundwholesale/supplier_authentication_service.py tools/clearance_king/
```

**Step 4.3**: Edit authentication service

**File**: `tools/clearance_king/supplier_authentication_service.py`

**Key changes needed**:

```python
# Line ~50: Update login URL
LOGIN_URL = "https://www.clearance-king.co.uk/customer/account/login/"

# Line ~70-80: Update CSS selectors (match selector config JSON)
EMAIL_SELECTOR = "input#email"
PASSWORD_SELECTOR = "input#pass"
LOGIN_BUTTON_SELECTOR = "button#send2.action.login.primary"

# Line ~90-100: Update authentication check selectors
AUTHENTICATED_INDICATORS = [
    ".customer-welcome",
    ".logged-in",
    ".customer-name"
]

# Test and adjust timing if needed (wait times for page loads)
```

**Step 4.4**: Test authentication manually
```python
# Recommended: Add debug logging to auth service
self.log.info(f"🔍 Attempting login to {LOGIN_URL}")
self.log.info(f"✅ Login successful, authenticated as: {username}")
```

---

### PHASE 5: Create Entry Script

**Step 5.1**: Copy template
```bash
cp run_custom_poundwholesale.py run_custom_clearance_king.py
```

**Step 5.2**: Edit entry script

**File**: `run_custom_clearance_king.py`

**Only ONE line needs to change**:

```python
# BEFORE (poundwholesale):
from tools.poundwholesale.supplier_authentication_service import SupplierAuthenticationService

# AFTER (clearance-king):
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
```

**That's it! Everything else stays the same because the workflow is now config-driven.**

**Full example entry script**:
```python
import asyncio
import logging
from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService  # ← ONLY CHANGE
from utils.logger import setup_logger
from utils.browser_manager import BrowserManager

async def main():
    debug_log_file = setup_logger()
    log = logging.getLogger(__name__)

    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('current_supplier_workflow')
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
            log.error("Authentication failed")
            return

        workflow = PassiveExtractionWorkflow(
            config_loader=config_loader,
            workflow_config=workflow_config,
            browser_manager=browser_manager
        )
        await workflow.run()

    finally:
        if browser_manager:
            await browser_manager.close_browser()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### PHASE 6: Testing

#### Test 6.1: Authentication Test (Quick Check)

**Purpose**: Verify login works before running full workflow

```bash
# Temporarily set max_products to 0 in system_config.json for auth-only test
python run_custom_clearance_king.py
```

**Expected logs**:
```
✅ Login successful
✅ Authenticated as: your_email@example.com
```

**If authentication fails**:
1. Verify credentials in `system_config.json`
2. Check login selectors in `tools/clearance_king/supplier_authentication_service.py`
3. Verify login URL is correct
4. Test login manually in browser to confirm credentials work

---

#### Test 6.2: Small Batch Test

**Purpose**: Verify scraping, extraction, and financial analysis work

**Step 1**: Edit `system_config.json` temporarily:
```json
{
  "current_supplier_workflow": {
    "max_products": 5,  // ← Set to 5 for testing
    ...
  }
}
```

**Step 2**: Run workflow:
```bash
python run_custom_clearance_king.py
```

**Step 3**: Verify outputs created:
```bash
# Check supplier cache
ls -lh "OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json"

# Check linking map directory
ls -lh "OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/"

# Check linking map file
ls -lh "OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/linking_map.json"

# Check financial report
ls -lh "OUTPUTS/FBA_ANALYSIS/financial_reports/fba_financial_report_*.csv"

# Check processing state
ls -lh "OUTPUTS/CACHE/processing_states/clearance-king-co-uk_processing_state.json"
```

**Expected outputs**:
```
✅ clearance-king-co-uk_products_cache.json (supplier data)
✅ clearance-king.co.uk/linking_map.json (EAN-to-ASIN mapping)
✅ fba_financial_report_TIMESTAMP.csv (profitable products)
✅ clearance-king-co-uk_processing_state.json (resume capability)
```

**Step 4**: Verify data quality:
```bash
# Open supplier cache
cat "OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json" | head -50

# Check for valid fields:
# - title: Product names present
# - price: Prices extracted (or "Login Required")
# - ean: Barcodes present
# - url: Valid product URLs
```

**If scraping fails**:
1. Check selector config in `config/supplier_configs/clearance-king.co.uk.json`
2. Test selectors manually in browser DevTools
3. Adjust selectors and retry

---

#### Test 6.3: Full Production Run

**Purpose**: Process all categories with full product limits

**Step 1**: Restore full settings in `system_config.json`:
```json
{
  "current_supplier_workflow": {
    "max_products": 10000,  // ← Restore to full limit
    "max_products_per_category": 1000,
    ...
  }
}
```

**Step 2**: Run full workflow:
```bash
python run_custom_clearance_king.py
```

**Monitor logs for**:
```
✅ Category processing progress
✅ Products scraped per category
✅ Amazon matches found
✅ Profitable products identified
✅ State saves (every N products)
```

**Step 3**: Verify isolation (no cross-contamination):
```bash
# Check poundwholesale files UNCHANGED
stat "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
# Timestamp should NOT have changed

# List both linking map directories
ls -la "OUTPUTS/FBA_ANALYSIS/linking_maps/"
# Should show TWO separate directories:
# clearance-king.co.uk/
# poundwholesale.co.uk/
```

---

## 🔄 SWITCHING BACK TO ANOTHER SUPPLIER

### Quick Switch Process

**Step 1**: Edit `config/system_config.json`

Replace `current_supplier_workflow` section:
```json
{
  "current_supplier_workflow": {
    "supplier_name": "poundwholesale.co.uk",
    "supplier_url": "https://www.poundwholesale.co.uk",
    "categories_config_path": "config/poundwholesale_categories.json",
    ...
  },
  "credentials": {
    "poundwholesale.co.uk": {
      "username": "YOUR_USERNAME",
      "password": "YOUR_PASSWORD"
    }
  }
}
```

**Step 2**: Run the supplier's entry script:
```bash
python run_custom_poundwholesale.py
```

**That's it!** All output directories are automatically managed per supplier.

---

## ✅ VALIDATION CHECKLIST

### Pre-Run Validation
- [ ] Selector config JSON created and tested
- [ ] Categories JSON created with valid URLs
- [ ] System config updated with correct supplier details
- [ ] Credentials added to system config
- [ ] Authentication service created and tested
- [ ] Entry script created with correct import
- [ ] Chrome browser running on debug port 9222

### Post-Run Validation
- [ ] Supplier cache file created with products
- [ ] Linking map directory created for supplier
- [ ] Linking map file created with EAN-ASIN mappings
- [ ] Financial report CSV generated
- [ ] Processing state file created
- [ ] Logs show successful category processing
- [ ] No errors in logs related to paths or config
- [ ] Other supplier files unchanged (isolation verified)

---

## 🚨 TROUBLESHOOTING

### Issue: "categories_config_path not in config" Warning

**Symptom**: Warning log shows fallback path being used

**Cause**: `categories_config_path` missing from `system_config.json`

**Fix**: Add to `current_supplier_workflow` section:
```json
"categories_config_path": "config/clearance_king_categories.json"
```

---

### Issue: Authentication Fails

**Symptom**: "Authentication failed" error in logs

**Possible causes**:
1. Invalid credentials in `system_config.json`
2. Incorrect login selectors in authentication service
3. Wrong login URL
4. Site requires CAPTCHA or additional verification

**Fix**:
1. Test login manually in browser
2. Update selectors in authentication service
3. Check login URL is correct
4. Add wait times if page loads slowly

---

### Issue: No Products Scraped

**Symptom**: Supplier cache file empty or missing products

**Possible causes**:
1. Incorrect product_item selector
2. Wrong category URLs
3. Site requires login for product viewing
4. Pagination not working

**Fix**:
1. Test selectors in browser DevTools
2. Verify category URLs load products
3. Ensure authentication successful before scraping
4. Check pagination pattern in selector config

---

### Issue: No Amazon Matches Found

**Symptom**: Linking map empty, no ASINs

**Possible causes**:
1. EAN field not extracted (selector wrong)
2. Products don't exist on Amazon
3. Title search failing (product names too generic)

**Fix**:
1. Verify EAN extraction working (check supplier cache)
2. Test manual Amazon search for sample EAN
3. Check product titles are descriptive

---

### Issue: Cross-Supplier Contamination

**Symptom**: Wrong supplier data in cache files

**Cause**: Config not updated or entry script using wrong import

**Fix**:
1. Verify `supplier_name` in `system_config.json`
2. Check entry script imports correct auth service
3. Restart Python process to clear cached modules

---

## 📊 EXPECTED TIME PER SUPPLIER

### Initial Setup (First Supplier)
- Selector testing and config: 45-60 minutes
- Categories identification: 15-20 minutes
- Authentication service: 20-30 minutes
- Entry script: 5 minutes
- Testing (small batch): 10-15 minutes
- **Total**: ~2-2.5 hours

### Additional Suppliers (After First)
- Selector testing and config: 30-45 minutes
- Categories identification: 10-15 minutes
- Authentication service: 15-20 minutes
- Entry script: 3-5 minutes
- Testing (small batch): 10-15 minutes
- **Total**: ~1-1.5 hours

### Time Savings vs Pre-Implementation
- **Before**: 2-4 hours (with code editing, debugging, path updates)
- **After**: 1-2.5 hours (config only, zero code edits)
- **Savings**: 30-60 minutes per supplier + reduced error risk

---

## 📚 REFERENCE FILES

### Example Templates (Copy From)
```
tools/poundwholesale/supplier_authentication_service.py
run_custom_poundwholesale.py
config/poundwholesale_categories.json
config/supplier_configs/poundwholesale.co.uk.json
```

### System Files (DO NOT EDIT)
```
tools/passive_extraction_workflow_latest.py  ← Config-driven, ZERO edits needed
tools/configurable_supplier_scraper.py       ← Selector-driven, ZERO edits needed
```

### Config Files (EDIT These)
```
config/system_config.json                    ← Edit to switch suppliers
config/clearance_king_categories.json        ← Create per supplier
config/supplier_configs/clearance-king.co.uk.json  ← Create per supplier
```

---

## 🎯 SUMMARY

### What You Need to Remember
1. ✅ **ZERO code edits** to workflow or scraper files
2. ✅ **FOUR manual files per supplier**: selector config, categories, auth service, entry script
3. ✅ **ONE config edit** to switch suppliers (system_config.json)
4. ✅ **Automatic output isolation** per supplier
5. ✅ **Test thoroughly** before full production run

### Success Criteria
- ✅ Authentication works without errors
- ✅ Products scraped with valid data
- ✅ Amazon matches found for EANs
- ✅ Financial reports generated
- ✅ State saves allow resume
- ✅ No cross-supplier contamination

---

**Guide Version**: 1.0
**Last Updated**: October 1, 2025
**Next Review**: After 2-3 supplier integrations

**Support**: Refer to `walkthrough/general_new_supplier_integration_guide.md` for additional context on pre-implementation process.