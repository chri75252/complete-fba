# New Supplier Analysis Guide
**Version**: 1.1
**Date**: October 5, 2025
**Purpose**: Concise checklist for config-driven supplier onboarding

---

## 🎯 Quick Reference

**Time Estimate**: 60-90 minutes total
**Prerequisites**: Chrome with debug port 9222, system access
**Approach**: Config-only changes, zero workflow code editing

---

## ✅ Pre-Onboarding Checklist

### System Readiness
- [ ] Chrome installed and configured for remote debugging
- [ ] Python 3.x environment active
- [ ] Repository cloned and dependencies installed
- [ ] Existing supplier working (verify system baseline)
- [ ] Config-driven implementation verified (see Deep Dive §2)

---

## 📋 Onboarding Workflow (4 Phases)

### **PHASE 1: Configuration Discovery** (15-20 min)

#### 1.1 Analyze Target Website
```
Browser DevTools Investigation:
- [ ] Product listing page structure
- [ ] Individual product page selectors
- [ ] Login form elements (email, password, submit)
- [ ] Pagination mechanism (URL params vs buttons)
- [ ] Authentication indicators (logout link, account menu)
```

#### 1.2 Document Selectors
```
Required CSS Selectors:
- [ ] Product title
- [ ] Product price (may require login)
- [ ] Product URL
- [ ] Product image
- [ ] EAN/barcode (critical for matching)
- [ ] Stock status
- [ ] Login form: email field
- [ ] Login form: password field
- [ ] Login form: submit button
```

---

### **PHASE 2: Configuration Files** (20-30 min)

#### 2.1 Create Supplier Config
**File**: `config/supplier_configs/{supplier_domain}.json`

```json
{
  "supplier_id": "new-supplier.com",
  "base_url": "https://www.new-supplier.com/",
  "login_config": {
    "test_product_url": "https://www.new-supplier.com/test-product-url",
    "price_selectors": [".price-box .price", "span.price"]
  },
  "authentication": {
    "login_selectors": {
      "email_field": "input[name='email']",
      "password_field": "input[name='password']",
      "login_button": "button[type='submit']"
    }
  },
  "field_mappings": {
    "title": ["a.product-name"],
    "product_detail_title": [".page-title .base", "h1.page-title", "h1"],
    "price": [".price-current"],
    "ean": ["span.ean-code", "meta[itemprop='gtin13']", "meta[property='product:ean']", "script[type='application/ld+json']"],
    "url": ["a.product-link"],
    "image": ["img.product-image"]
  },
  "pagination": {
    "pattern": "https://www.new-supplier.com/category?page={page}",
    "use_url_navigation": true
  }
}
```

**Checklist**:
- [ ] All selectors tested in browser DevTools
- [ ] Detail page selectors provided for title (product_detail_title)
- [ ] Test product URL verified (requires login to see price)
- [ ] Pagination pattern confirmed (URL vs button)
- [ ] JSON syntax validated

#### 2.2 Create Categories List
**File**: `config/{supplier}_categories.json`

```json
{
  "category_urls": [
    "https://www.new-supplier.com/electronics",
    "https://www.new-supplier.com/clothing"
  ]
}
```

**Checklist**:
- [ ] Category URLs manually collected
- [ ] URLs confirmed accessible
- [ ] JSON syntax validated

#### 2.3 Add to System Config
**File**: `config/system_config.json`

```json
{
  "workflows": {
    "new_supplier_workflow": {
      "supplier_name": "new-supplier.com",
      "supplier_url": "https://www.new-supplier.com",
      "categories_config_path": "config/new_supplier_categories.json",
      "use_predefined_categories": true,
      "ai_client": null
    }
  },
  "credentials": {
    "new-supplier.com": {
      "username": "your_username",
      "password": "your_password"
    }
  }
}
```

**Checklist**:
- [ ] Workflow name follows pattern: `{supplier}_workflow`
- [ ] `supplier_name` matches config file domain
- [ ] `categories_config_path` points to categories JSON
- [ ] Credentials added for supplier
- [ ] `use_predefined_categories: true`
- [ ] `ai_client: null` (HYBRID mode)

---

### **PHASE 3: Authentication Service** (15-20 min)

#### 3.1 Create Supplier Directory
```bash
mkdir -p tools/{supplier}
```

#### 3.2 Create Authentication Helper
**File**: `tools/{supplier}/supplier_authentication_service.py`

**Template**: Copy from existing supplier (clearance_king or poundwholesale)

**Required Changes**:
- [ ] Update class name: `{Supplier}AuthenticationHelper`
- [ ] Update config path: `config/supplier_configs/{domain}.json`
- [ ] Set alias: `SupplierAuthenticationService = {Supplier}AuthenticationHelper`
- [ ] Test manually: confirm login works

**Pattern** (see Deep Dive §4.2):
```python
class NewSupplierAuthenticationHelper:
    def __init__(self, page: Page):
        self.page = page
        # Type guard ensures Page object, not BrowserManager
        assert hasattr(page, "goto"), "Expects Playwright Page"

    async def is_authenticated(self) -> bool:
        # Uses StandalonePlaywrightLogin.verify_price_access()
        ...

    async def login(self, credentials: Dict[str, str]) -> bool:
        # Uses StandalonePlaywrightLogin.login_workflow()
        ...
```

---

### **PHASE 4: Entry Script & Testing** (10-20 min)

#### 4.1 Create Entry Script
**File**: `run_custom_{supplier}.py`

**Template**: Copy from existing supplier entry script

**Required Changes**:
- [ ] Update import: `from tools.{supplier}.supplier_authentication_service import {Supplier}AuthenticationHelper`
- [ ] Update workflow config name: `get_workflow_config('{supplier}_workflow')`
- [ ] Update supplier name default: `supplier_name = workflow_config.get('supplier_name', '{domain}')`

#### 4.2 Test Authentication (5 min)
```bash
python run_custom_{supplier}.py
# Stop after "✅ Already authenticated!" or "✅ Authentication successful"
```

**Validation**:
- [ ] No authentication errors
- [ ] Login detected or price access confirmed
- [ ] No selector errors

#### 4.3 Test Small Batch (10-15 min)
**Temporary config change**: Edit `system_config.json`
```json
"max_categories_to_process": 1,
"max_products_per_category": 10
```

**Run**:
```bash
python run_custom_{supplier}.py
```

**Validation**:
- [ ] Category scraped successfully
- [ ] Products extracted
- [ ] Linking map created in `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/`
- [ ] State saved in `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json`
- [ ] No cross-supplier contamination (other supplier files unchanged)

#### 4.4 Production Run (Restore config, full execution)
```bash
python run_custom_{supplier}.py
```

---

## 🔍 Verification Checklist

### Output Isolation Verification
```bash
# Check supplier-specific directories created
ls -la "OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/"
ls -la "OUTPUTS/cached_products/{supplier}_products_cache.json"
ls -la "OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json"

# Verify other suppliers unchanged (check timestamps)
ls -lt "OUTPUTS/FBA_ANALYSIS/linking_maps/"
```

**Expected**:
- [ ] New supplier has dedicated linking map directory
- [ ] New supplier cache file created
- [ ] New supplier state file created
- [ ] Other supplier files have OLD timestamps (no modifications)

---

## 🚨 Troubleshooting

### Authentication Issues
**Symptom**: "Could not find or fill password field"
**Fix**:
1. Verify selectors in `config/supplier_configs/{domain}.json`
2. Test selectors in browser DevTools
3. Check if password field is hidden (use `force: true` in config)

### Categories Not Loading
**Symptom**: "categories_config_path not in config"
**Fix**: Add `"categories_config_path": "config/{supplier}_categories.json"` to workflow config

### Wrong Output Directories
**Symptom**: Files appearing in wrong supplier folders
**Fix**: Verify `"supplier_name": "{correct_domain}"` in workflow config

### Selector Failures
**Symptom**: "Could not extract price/title/EAN"
**Fix**:
1. Inspect page HTML in browser
2. Update selectors in `config/supplier_configs/{domain}.json`
3. Use multiple fallback selectors: `["primary", "backup1", "backup2"]`

---

## ⏱️ Time Breakdown

| Phase | Task | Time |
|-------|------|------|
| 1 | Configuration Discovery | 15-20 min |
| 2 | Configuration Files | 20-30 min |
| 3 | Authentication Service | 15-20 min |
| 4 | Entry Script & Testing | 10-20 min |
| **Total** | **Full Onboarding** | **60-90 min** |

---

## 📚 Related Documentation

- **System Deep Dive**: `docs/system_deep_dive_new_supplier_onboarding.md` (comprehensive reference)
- **Config Examples**: See `config/supplier_configs/clearance-king.co.uk.json`
- **Memory Files**: `.serena/memories/config_driven_implementation_complete_handover_oct02_2025.md`

---

## ✅ Success Criteria

### Phase Completion
- [ ] All 4 phases completed
- [ ] All checklists verified
- [ ] Authentication working
- [ ] Output isolation confirmed

### Production Readiness
- [ ] Small batch test passed (1 category, 10 products)
- [ ] Full category processed successfully
- [ ] No errors in debug logs
- [ ] Financial reports generated

---

**Next Steps**: See Deep Dive for execution flow details and advanced configuration options.

---

## Addendum (v1.1): Multi‑Site Stability Updates

### Output Schema (Authoritative)
- Included: `title`, `price`, `url`, `normalized_url`, `ean`, `availability`, `source_url`, `scraped_at`
- Omitted: `sku`, `image_url`
  - Rationale: `sku` often polluted by non-identifiers; `image_url` brittle and not required for matching/dedup.

### Dedup & Keys (Do This Exactly)
- Build keys with `stable_key(normalize_url(url), valid_ean)`.
- Validate EAN before use (accept only 8/12/13 digits); else fall back to URL.
- Apply at index build, save-time seed/scan/update, and Step‑2 filter.

### Detail-Page Title Selectors
- In supplier JSON, add `field_mappings.product_detail_title` for product pages.
- The scraper prefers detail selectors, then `field_mappings.title`, then semantic/meta fallbacks (OG/Twitter, headings, `<title>`).

### Accumulator (Periodic Saves)
- After atomic save, update the in-memory accumulator in-place (list slice assignment) so periodic saves reflect growth and do not remain stuck at 1.

### Sample JSON updates
```json
"field_mappings": {
  "title": ["a.product-name"],
  "product_detail_title": [".page-title .base", "h1.page-title", "h1"],
  "price": [".price-current"],
  "ean": ["span.ean-code", "meta[itemprop='gtin13']", "meta[property='product:ean']", "script[type='application/ld+json']"],
  "url": ["a.product-link"],
  "image": ["img.product-image"]
}
```

### Troubleshooting (Fast Path)
- Title is null on detail pages → add `product_detail_title` selectors.
- Cache ‘stuck at 1’ / saves always ‘0 new’ → ensure accumulator updates in-place (not reassignment).
- Image/SKU discrepancies → by design, omitted from outputs across suppliers.
