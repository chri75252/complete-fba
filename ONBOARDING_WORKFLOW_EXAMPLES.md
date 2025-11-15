# Real-World Supplier Onboarding Workflows

Complete examples showing exactly how to use the supplier onboarding system from start to finish.

---

## 📋 Table of Contents

1. [Scenario 1: New Supplier (Clearance King)](#scenario-1-new-supplier-clearance-king)
2. [Scenario 2: Existing Supplier Update (Poundwholesale)](#scenario-2-existing-supplier-update-poundwholesale)
3. [Scenario 3: Validation Only (Reference Mode)](#scenario-3-validation-only-reference-mode)
4. [Step-by-Step User Guide](#step-by-step-user-guide)

---

## Scenario 1: New Supplier (Clearance King)

### Context

- **Supplier**: clearance-king.co.uk (brand new, not in system)
- **Goal**: Full onboarding with all scaffolds
- **Requirements**: Generate all configs, create runner shim, validate with sanity check

### Step 1: Prerequisites

```bash
# 1. Start Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug

# 2. Navigate to repo root
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

# 3. Verify Chrome is running
curl http://localhost:9222/json/version
```

### Step 2: Prepare Selectors

**Manual Method (DevTools):**

```bash
# 1. Navigate to clearance-king.co.uk/clearance in Chrome
# 2. Open DevTools (F12)
# 3. Find a product element
# 4. Right-click → Copy → Copy selector
# 5. Repeat for: title, price, ean, url, image
```

**Example Selectors:**

```json
{
  "field_mappings": {
    "product_item": [".product-item", ".product-card"],
    "title": [".product-title", "h3.title"],
    "price": [".product-price", ".price"],
    "ean": [".product-ean", "[data-ean]"],
    "url": ["a.product-link", ".product-item a"],
    "image": ["img.product-image", ".product-item img"]
  }
}
```

### Step 3: Prepare Categories

**Option A: Create categories file**

```bash
# Create config/clearance_king_categories.json
{
  "category_urls": [
    "https://clearance-king.co.uk/clearance",
    "https://clearance-king.co.uk/toys",
    "https://clearance-king.co.uk/electronics"
  ]
}
```

**Option B: Inline JSON string**

```json
{"category_urls": ["https://clearance-king.co.uk/clearance"]}
```

### Step 4: Invoke Skill

**Via Claude Code UI:**

```
Use supplier-onboarding skill to add clearance-king.co.uk with:
- categories: config/clearance_king_categories.json
- selectors: config/supplier_configs/clearance-king.co.uk.json
- workflow: clearance_king_workflow
- scaffolds: supplier-package, runner-shim
```

**Via Python:**

```bash
cd skills/supplier-onboarding

python main.py \
  --domain "https://clearance-king.co.uk" \
  --categories-source "config/clearance_king_categories.json" \
  --selectors-source '{"field_mappings": {"product_item": [".product-item"], "title": [".product-title"], "price": [".product-price"], "ean": [".product-ean"], "url": ["a.product-link"], "image": ["img.product-image"]}}' \
  --workflow-key "clearance_king_workflow" \
  --mode generate \
  --scaffolds supplier-package runner-shim
```

### Step 5: Monitor Execution

**Timeline:**

```
[00:00] Skill activated
[00:01] Session created: C:/temp/onboarding/<uuid>/
[00:02] Wizard invoked
[00:03] Domain normalized: clearance-king.co.uk
[00:04] Files generated to staging
[00:05] Atomic move to final locations
[00:06] Runner determined: run_custom_clearance-king-co-uk.py
[00:07] Sanity check started (FBA_TEST_MODE=true)
[05:00] Sanity check running... (scraping products)
[07:00] Sanity check complete
[07:05] 6-criterion verification
[07:10] Result generated
```

**Total Time: ~7 minutes**

### Step 6: Review Results

**Success Output:**

```json
{
  "success": true,
  "files_generated": [
    "C:\\...\\config\\supplier_configs\\clearance-king.co.uk.json",
    "C:\\...\\config\\clearance_king_categories.json",
    "C:\\...\\suppliers\\clearance-king-co-uk\\config\\product_selectors.json",
    "C:\\...\\suppliers\\clearance-king-co-uk\\.supplier_ready",
    "C:\\...\\run_custom_clearance-king-co-uk.py"
  ],
  "sanity_results": {
    "scraping_rate": true,
    "amazon_cache": true,
    "linking_map": true,
    "financial_csv": true,
    "processing_state": true,
    "no_critical_errors": true
  }
}
```

### Step 7: Run Full System

```bash
# Now run the full workflow (no test mode)
python run_custom_clearance-king-co-uk.py
```

---

## Scenario 2: Existing Supplier Update (Poundwholesale)

### Context

- **Supplier**: poundwholesale.co.uk (already exists)
- **Goal**: Update selectors only (site changed structure)
- **Requirements**: No new scaffolds, just update selectors

### Step 1: Prerequisites

```bash
# Chrome already running from before
# Navigate to repo root
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32..."
```

### Step 2: Update Selectors

**Find new selectors with DevTools:**

```json
{
  "field_mappings": {
    "product_item": [".new-product-class"],  // Changed
    "title": [".product-title"],
    "price": [".new-price-class"],  // Changed
    "ean": [".product-ean"],
    "url": ["a.product-link"],
    "image": ["img.product-image"]
  }
}
```

### Step 3: Invoke Skill (Update Mode)

**Via Claude Code:**

```
Use supplier-onboarding skill to update poundwholesale.co.uk with:
- selectors: <paste new JSON>
- categories: config/poundwholesale_categories.json (existing)
- workflow: poundwholesale_workflow
- mode: generate
- scaffolds: none
```

**Via Python:**

```bash
cd skills/supplier-onboarding

python main.py \
  --domain "poundwholesale.co.uk" \
  --categories-source "config/poundwholesale_categories.json" \
  --selectors-source "config/supplier_configs/poundwholesale.co.uk.json" \
  --workflow-key "poundwholesale_workflow" \
  --mode generate
  # No --scaffolds flag = no scaffolds generated
```

### Step 4: Verify Update

```bash
# Check selectors were updated
cat "config/supplier_configs/poundwholesale.co.uk.json"

# Run sanity check
# (automatically done by skill)
```

### Step 5: Results

```json
{
  "success": true,
  "files_generated": [
    "C:\\...\\config\\supplier_configs\\poundwholesale.co.uk.json"
  ],
  "sanity_results": {
    "scraping_rate": true,
    "amazon_cache": true,
    "linking_map": true,
    "financial_csv": true,
    "processing_state": true,
    "no_critical_errors": true
  }
}
```

---

## Scenario 3: Validation Only (Reference Mode)

### Context

- **Goal**: Verify configuration is correct before full run
- **Requirements**: No changes, just validate files exist

### Step 1: Invoke with Reference Mode

**Via Claude Code:**

```
Use supplier-onboarding skill to validate poundwholesale.co.uk in reference mode
```

**Via Python:**

```bash
python skills/supplier-onboarding/main.py \
  --domain "poundwholesale.co.uk" \
  --categories-source "config/poundwholesale_categories.json" \
  --selectors-source "config/supplier_configs/poundwholesale.co.uk.json" \
  --workflow-key "poundwholesale_workflow" \
  --mode reference
```

### Step 2: Results (Fast - No Sanity Check)

```json
{
  "success": true,
  "files_generated": [],
  "validation_checks": {
    "selectors_exist": true,
    "categories_exist": true
  },
  "sanity_results": {}
}
```

**Note:** Reference mode skips sanity check (fast validation only).

---

## Step-by-Step User Guide

### From Zero to Running Supplier

#### Phase 1: Environment Setup (One-Time)

**Step 1.1: Install Dependencies**

```bash
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32..."
pip install -r requirements.txt
playwright install chromium
```

**Step 1.2: Start Chrome**

```bash
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

**Keep Chrome running in background.**

#### Phase 2: Gather Supplier Information

**Step 2.1: Identify Domain**

```
Example: clearance-king.co.uk
```

**Step 2.2: Find Category URLs**

```bash
# Navigate to supplier site
# Find category/collection pages
# List URLs:
- https://clearance-king.co.uk/clearance
- https://clearance-king.co.uk/toys
```

**Step 2.3: Extract CSS Selectors**

```bash
# For EACH field (title, price, ean, url, image):
1. Navigate to a product page
2. Open DevTools (F12)
3. Click "Select Element" tool
4. Click on the element you want
5. Right-click in Elements panel → Copy → Copy selector
6. Paste into your selectors JSON
```

**Example DevTools Workflow:**

```
1. Navigate to: https://clearance-king.co.uk/clearance
2. F12 to open DevTools
3. Click product title
4. In Elements panel, right-click <h3 class="product-title">
5. Copy → Copy selector
6. Result: ".product-title"
7. Add to selectors JSON: "title": [".product-title"]
```

#### Phase 3: Create Configuration Files

**Step 3.1: Create Selectors File (if using file path)**

```bash
# Create: config/supplier_configs/clearance-king.co.uk.json
{
  "field_mappings": {
    "product_item": [".product-item"],
    "title": [".product-title"],
    "price": [".product-price"],
    "ean": [".product-ean", "[data-ean]"],
    "url": ["a.product-link"],
    "image": ["img.product-image"]
  }
}
```

**Step 3.2: Create Categories File (if using file path)**

```bash
# Create: config/clearance_king_categories.json
{
  "category_urls": [
    "https://clearance-king.co.uk/clearance",
    "https://clearance-king.co.uk/toys"
  ]
}
```

#### Phase 4: Run the Skill

**Step 4.1: Navigate to Repo Root**

```bash
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32..."
```

**Step 4.2: Invoke Skill**

**Option A: Via Claude Code UI (Easiest)**

```
Use supplier-onboarding skill to add clearance-king.co.uk with:
- categories: config/clearance_king_categories.json
- selectors: config/supplier_configs/clearance-king.co.uk.json
- workflow: clearance_king_workflow
- scaffolds: supplier-package, runner-shim
```

**Option B: Via Python (For Testing)**

```bash
cd skills/supplier-onboarding

python main.py \
  --domain "clearance-king.co.uk" \
  --categories-source "config/clearance_king_categories.json" \
  --selectors-source "config/supplier_configs/clearance-king.co.uk.json" \
  --workflow-key "clearance_king_workflow" \
  --mode generate \
  --scaffolds supplier-package runner-shim
```

**Step 4.3: Wait for Completion (~7 minutes)**

```
Progress indicators:
[  0%] Skill activated
[ 10%] Wizard invoked
[ 20%] Files generated
[ 30%] Sanity check started
[ 80%] Sanity check complete
[100%] Results ready
```

#### Phase 5: Review Results

**Step 5.1: Check Success**

```bash
# Look for success: true in output JSON
{
  "success": true,
  ...
}
```

**Step 5.2: Verify Files Generated**

```bash
# Check files exist:
ls config/supplier_configs/clearance-king.co.uk.json
ls config/clearance_king_categories.json
ls run_custom_clearance-king-co-uk.py
```

**Step 5.3: Review Sanity Results**

```json
"sanity_results": {
  "scraping_rate": true,      // ✅ Got 20+ products
  "amazon_cache": true,        // ✅ Amazon data retrieved
  "linking_map": true,         // ✅ EAN matching worked
  "financial_csv": true,       // ✅ ROI calculated
  "processing_state": true,    // ✅ State persisted
  "no_critical_errors": true   // ✅ No errors in logs
}
```

#### Phase 6: Handle Failures (If Any)

**If scraping_rate = false:**

```bash
Issue: Less than 20 products scraped
Actions:
1. Open DevTools and verify selectors still work
2. Check if site requires login (add auth helper)
3. Update selectors and re-run skill
```

**If amazon_cache = false:**

```bash
Issue: No Amazon data retrieved
Actions:
1. Verify EAN selector is correct
2. Check test product has valid EAN
3. Manually test EAN lookup
```

**If any check fails:**

```json
"remediation": {
  "scraping_rate": {
    "issue": "Less than 20 products scraped",
    "actions": [
      "Verify selectors are correct",
      "Check config/supplier_configs/clearance-king.co.uk.json",
      "Use browser DevTools to verify CSS selectors",
      "Ensure no login required"
    ]
  }
}
```

**Follow remediation actions, then re-run.**

#### Phase 7: Launch Full System

**Step 7.1: Run Full Workflow (No Test Mode)**

```bash
# Use the auto-generated runner
python run_custom_clearance-king-co-uk.py
```

**Step 7.2: Monitor Progress**

```bash
# Watch logs
tail -f logs/debug/run_custom_clearance_king_*.log
```

**Step 7.3: Check Outputs**

```bash
# Financial reports
ls OUTPUTS/FBA_ANALYSIS/financial_reports/

# Linking maps
ls OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king-co-uk/

# Processing state
ls OUTPUTS/CACHE/processing_states/clearance_king_co_uk_processing_state.json
```

---

## Quick Reference

### Skill Parameters

| Parameter | Required | Example |
|-----------|----------|---------|
| domain | Yes | `clearance-king.co.uk` |
| categories_source | Yes | `config/categories.json` or inline JSON |
| selectors_source | Yes | `config/selectors.json` or inline JSON |
| workflow_key | Yes | `clearance_king_workflow` |
| mode | No | `generate` (default) or `reference` |
| scaffolds | No | `["supplier-package", "runner-shim"]` |
| test_product_url | No | `https://...` |

### File Locations

| Type | Location | Format |
|------|----------|--------|
| Selectors | `config/supplier_configs/{domain}.json` | dot-form |
| Categories | From workflow config | any |
| Runner | `run_custom_{supplier-id}.py` | hyphen-form |
| Linking Map | `OUTPUTS/.../linking_maps/{supplier-id}/` | hyphen-form |
| Processing State | `OUTPUTS/.../processing_states/{name}_processing_state.json` | underscore-form |

### Common Commands

```bash
# New supplier (full setup)
python skills/supplier-onboarding/main.py \
  --domain "new-supplier.co.uk" \
  --categories-source "config/categories.json" \
  --selectors-source "config/selectors.json" \
  --workflow-key "new_workflow" \
  --scaffolds supplier-package runner-shim

# Update existing (selectors only)
python skills/supplier-onboarding/main.py \
  --domain "existing-supplier.co.uk" \
  --categories-source "config/categories.json" \
  --selectors-source "new_selectors.json" \
  --workflow-key "existing_workflow"

# Validate only (fast)
python skills/supplier-onboarding/main.py \
  --domain "supplier.co.uk" \
  --categories-source "config/categories.json" \
  --selectors-source "config/selectors.json" \
  --workflow-key "workflow" \
  --mode reference
```

---

## Troubleshooting

### Common Issues

**1. Wizard not found**
```bash
Error: Wizard script not found: utils/supplier_onboarding_wizard.py
Fix: Ensure you're in repo root and file exists
```

**2. Chrome not running**
```bash
Error: Cannot connect to Chrome CDP
Fix: Start Chrome with --remote-debugging-port=9222
```

**3. WindowsSaveGuardian import fails**
```bash
Error: Cannot import WindowsSaveGuardian
Fix: Ensure utils/windows_save_guardian.py exists
```

**4. Session directory creation fails**
```bash
Error: Permission denied: C:/temp/onboarding
Fix: Run as administrator or use /tmp/onboarding
```

### Debug Mode

```bash
# Keep session files for debugging
# Edit skills/supplier-onboarding/main.py
# Comment out: self._cleanup_session()

# Then inspect:
cat C:/temp/onboarding/<uuid>/input.json
cat C:/temp/onboarding/<uuid>/output.json
```

---

## Next Steps

After successful onboarding:

1. ✅ **Test Full Run**: `python run_custom_{supplier-id}.py`
2. ✅ **Monitor Logs**: `tail -f logs/debug/*.log`
3. ✅ **Check Outputs**: Review financial reports and linking maps
4. ✅ **Adjust If Needed**: Update selectors/categories and re-run skill
5. ✅ **Automate**: Schedule regular runs with cron/Task Scheduler
