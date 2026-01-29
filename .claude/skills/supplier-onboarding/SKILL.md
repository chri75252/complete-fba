---
name: supplier-onboarding
description: Guided supplier onboarding for Amazon FBA Agent System with deterministic file generation, atomic operations, and comprehensive validation. Use when onboarding new wholesale suppliers to the FBA analysis system.
---

# Supplier Onboarding

Onboard wholesale suppliers to the Amazon FBA Agent System through automated configuration generation, runner script creation, and comprehensive validation.

## Prerequisites

Before starting, ensure:
- [ ] Chrome running with debug port: `chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug`
- [ ] Repository location known
- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] User has supplier domain/URL ready

## Workflow Overview

This skill follows a **7-step workflow**:
0. **Data Preprocessing** (LLM manual validation - Read/Write tools only)
1. **Gather Information** (Progressive discovery)
2. **Prepare Configurations** (Create JSON files)
3. **Invoke Wizard** (Generate runner + auth helper)
4. **Validate Files** (⚠️ CRITICAL: Read and analyze, not just check existence)
5. **Report Results** (Comprehensive summary)
6. **Pre-Run Verification** (LLM manual checks before execution)
7. **User Decision** (Test Run / Main Run / Fix Issues)

---

## Step 0: Data Preprocessing and Validation (LLM MANUAL WORK)

**🚨 CRITICAL**: This entire step is performed MANUALLY by Claude using Read/Write tools. NO Python scripts are executed during this phase.

**Purpose**: Prepare and validate all input files BEFORE invoking the wizard script.

**When**: ALWAYS execute this step first when user provides raw data files (.txt, .md) or inline data.

---

### 0.1. Discover What User Provided

**Check user's message for**:
- File paths: `"categories in setup/categories_{supplier}.txt"`
- Inline data: URLs or JSON pasted in chat
- Domain: e.g., `"supplier.co.uk"`, `"supplier.com"`
- Authentication: `"no login required"` or `"requires username/password"`

**Action**: Use Read tool to examine any referenced files:

```bash
# User mentioned: "categories in setup/categories_supplier.txt"
Read: setup/categories_supplier.txt

# User mentioned: "selectors in setup/selectors_supplier.txt"
Read: setup/selectors_supplier.txt
```

**Checklist**:
- [ ] Found categories source (file or inline data)
- [ ] Found selectors source (file or inline data)
- [ ] Identified data format (plain text, markdown, JSON)
- [ ] Confirmed supplier domain

---

### 0.2. Validate Categories Content (LLM Manual Inspection)

**Read the categories file line by line and check**:

1. **URL Format**: Each line must start with `http://` or `https://`
2. **Domain Match**: Each URL must contain the correct supplier domain
3. **No Wrong URLs**: Check for other suppliers' URLs
4. **Valid Syntax**: Proper URL structure
5. **Sufficient Quantity**: At least 1 URL (ideally 10+ for production)

**Example Manual Validation**:
```
Line 1: https://supplier.com/category/toys ✅ Valid
Line 2: https://supplier.com/category/gifts ✅ Valid
Line 5: https://other-supplier.com/category ❌ WRONG DOMAIN - Remove
Line 8: supplier.com/category/home ❌ Missing protocol - Add https://
Line 10: # This is a comment ✅ Skip (comment line)
```

**What to do if issues found**:
- Remove lines with wrong domains
- Add `https://` to URLs missing protocol
- Skip comment lines (starting with # or //)
- Count total valid URLs after cleanup

**Checklist**:
- [ ] Examined every URL manually
- [ ] Verified correct supplier domain on each URL
- [ ] Removed or fixed any invalid URLs
- [ ] Counted total valid URLs

---

### 0.3. Validate Selectors Content (LLM Manual Inspection)

**Read the selectors file and extract CSS selectors**:

**If markdown format**:
```markdown
### Product Item Container
```css
.product-card
```

### Title
```css
.product-card h3 a
```
```

**LLM extracts from code blocks**:
- Find all `### Header` lines
- Extract CSS from following ` ```css ... ``` ` blocks
- Map headers to selector keys (e.g., "Product Item" → `product_item`)

**Required Selectors** (must be present):
- `product_item` - Container for each product card
- `title` - Product title selector
- `price` - Price selector
- `url` - Product URL selector

**CSS Syntax Validation** (check manually):
```css
✅ Valid: .product-card h3 a
✅ Valid: span.price
✅ Valid: button:contains('Next Page')
✅ Valid: [data-product-id]

❌ Invalid: .product[data-id  (missing closing bracket)
❌ Invalid: span(price  (unbalanced parentheses)
❌ Invalid: :contains('Next'  (missing closing parentheses)
```

**Checklist**:
- [ ] Extracted all selectors from source file
- [ ] Verified required keys present
- [ ] Checked CSS syntax (balanced brackets/parentheses)
- [ ] No empty values

---

### 0.4. Create JSON Files (LLM Manual Work)

**Use Write tool to create TWO JSON files in setup/ folder**:

#### **File 1**: `setup/{supplier_name}_categories.json`

```json
{
  "category_urls": [
    "https://supplier.com/category/toys",
    "https://supplier.com/category/gifts",
    ... paste all valid URLs from validation ...
  ],
  "total_categories": 150,
  "supplier": "supplier.com",
  "source": "setup/categories_supplier.txt (LLM converted)",
  "validated_at": "2025-11-13T06:32:00Z"
}
```

**Action**:
```bash
Write: setup/{supplier_name}_categories.json
# Paste the complete JSON with all validated URLs
```

#### **File 2**: `setup/{supplier_name}_selectors.json`

```json
{
  "supplier_url": "https://supplier.com",
  "product_item": ".product-card",
  "title": ".product-card h3 a",
  "price": "span.price",
  "url": ".product-card a[href]",
  "image": ".product-card img",
  "ean": ".product-info .barcode",
  "next_page_button": "a.pagination-next"
}
```

**Action**:
```bash
Write: setup/{supplier_name}_selectors.json
# Paste the complete JSON with all extracted selectors
```

**Checklist**:
- [ ] Created categories JSON in setup/ folder
- [ ] Created selectors JSON in setup/ folder
- [ ] Both files have valid JSON syntax
- [ ] All URLs and selectors included

---

### 0.5. Create Wizard Input (LLM Manual Work)

**Use Write tool to create wizard input JSON in temp/ folder**:

**File**: `temp/{supplier_name}_wizard_input.json`

```json
{
  "domain": "supplier.com",
  "categories_source": "setup/{supplier_name}_categories.json",
  "selectors_source": "setup/{supplier_name}_selectors.json",
  "workflow_key": "{supplier_name}_workflow",
  "mode": "generate",
  "authentication_required": false,
  "test_product_url": "https://supplier.com/sample-product",
  "repo_root": "ABSOLUTE_PATH_TO_REPO"
}
```

**Notes**:
- `{supplier_name}` should be domain without TLD (e.g., "supplier" from "supplier.com")
- `workflow_key` follows pattern: `{supplier_name}_workflow`
- `authentication_required`: Set to `true` if login needed, `false` otherwise
- `repo_root`: Use absolute path to repository root

**Action**:
```bash
Write: temp/{supplier_name}_wizard_input.json
# Paste the wizard input JSON
```

**Checklist**:
- [ ] Created wizard input in temp/ folder
- [ ] `categories_source` points to setup/ JSON file
- [ ] `selectors_source` points to setup/ JSON file
- [ ] `workflow_key` follows pattern: {supplier}_workflow
- [ ] `repo_root` is absolute path

---

### 0.6. Validation Report

**Before proceeding to Step 1**, report completion:

```
================================
STEP 0: LLM MANUAL VALIDATION COMPLETE
================================

✅ Files Read:
   - setup/categories_{supplier}.txt (150 URLs)
   - setup/selectors_{supplier}.txt (markdown format)

✅ Content Validated:
   - 150 valid {supplier}.com URLs
   - All required selectors present
   - CSS syntax verified

✅ JSON Files Created (LLM Manual):
   - setup/{supplier_name}_categories.json (150 URLs)
   - setup/{supplier_name}_selectors.json (8 selectors)

✅ Wizard Input Created:
   - temp/{supplier_name}_wizard_input.json

STATUS: ✅ READY FOR STEP 1

Next: Proceed to Step 1 (Gather Information)
================================
```

---

## Step 1: Gather Required Information (Progressive Discovery)

**IMPORTANT**: Ask ONLY for missing information. Don't repeat what user already provided.

### 1.1. Check What User Has Provided

Review user's message for:
- ✅ Domain/URL mentioned (e.g., "supplier.co.uk", "https://supplier.com")
- ✅ File paths referenced (e.g., "categories in setup/categories.txt")
- ✅ Inline data provided (pasted URLs or selector JSON)
- ✅ Authentication status mentioned ("no login needed", "requires login")
- ✅ Credentials provided (username/password)

### 1.2. Read Provided Files

If user referenced file paths, read them:

**Categories File**:
```bash
# User said: "categories in setup/categories_{supplier}.txt"
# Action: Read the file
```

**Selectors File**:
```bash
# User said: "selectors in setup/selectors_{supplier}.txt"
# Action: Read the file
```

### 1.3. Identify Missing Information

Create checklist of what's still needed:
- [ ] Domain/URL
- [ ] Category URLs (list or file)
- [ ] CSS Selectors (document or JSON)
- [ ] Authentication requirement (yes/no)
- [ ] If auth: Username
- [ ] If auth: Password

### 1.4. Ask ONLY for Missing Information

Example response:
```
I have the following for {supplier_domain}:
✅ Domain: {supplier_domain}
✅ Categories: Found 150 URLs in setup/categories_{supplier}.txt
✅ Selectors: Found detailed selectors in setup/selectors_{supplier}.txt

I still need:
❓ Authentication Requirement: Does {supplier_domain} require login to view product prices?
   - If YES, please provide:
     - Username (email)
     - Password
   - If NO, we can proceed without authentication

Please confirm the authentication requirement.
```

**DO NOT ASK** for information already provided!

---

## Step 2: Prepare Configuration Files

Once all information is gathered, create two configuration files:

### 2.1. Categories Configuration

**Location**: `config/{workflow_key}_categories.json`

**Format**:
```json
{
  "category_urls": [
    "https://supplier.com/category1",
    "https://supplier.com/category2"
  ]
}
```

**Determine workflow_key**:
- Pattern: `{supplier_name}_workflow` (underscore-form)
- Example: `supplier_workflow` (for supplier.com)

**Create the file**:
- Parse provided categories (list, file, or inline)
- Ensure all URLs are complete (include https://)
- Save as JSON in correct location

### 2.2. Selector Configuration

**Location**: `config/supplier_configs/{domain}.json` (⚠️ Use dot-form)

**Format**:
```json
{
  "supplier_url": "https://supplier.com",
  "product_card_selector": "...",
  "title_selector": "...",
  "price_selector": "...",
  "url_selector": "...",
  "next_page_selector": "...",
  "ean_selector": "...",
  "image_selector": "...",
  "out_of_stock_selector": "...",
  "authentication_required": false
}
```

**Create the file**:
- File name uses DOT-FORM: `supplier.com.json` (NOT `supplier-com.json`)
- Parse provided selectors (document, JSON, or inline)
- Ensure all required selectors present (see docs/FILE_SPECIFICATIONS.md)
- Set `authentication_required` to true/false based on user confirmation

---

## Step 3: Invoke Wizard

Execute the supplier onboarding wizard to generate runner script and authentication helper:

### 3.1. Construct Command

**Base Command**:
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "{domain}" \
  --categories-source "{categories_path}" \
  --selectors-source "{selectors_path}" \
  --workflow-key "{workflow_key}" \
  --mode generate \
  --authentication-required {true/false}
```

**If Authentication Required**, add:
```bash
  --username "{username}" \
  --password "{password}"
```

**Example (No Auth)**:
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "supplier.com" \
  --categories-source "config/supplier_categories.json" \
  --selectors-source "config/supplier_configs/supplier.com.json" \
  --workflow-key "supplier_workflow" \
  --mode generate \
  --authentication-required false
```

**Example (With Auth)**:
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "supplier.co.uk" \
  --categories-source "config/supplier_categories.json" \
  --selectors-source "config/supplier_configs/supplier.co.uk.json" \
  --workflow-key "supplier_workflow" \
  --mode generate \
  --authentication-required true \
  --username "user@example.com" \
  --password "SecurePass123"
```

### 3.2. Execute and Monitor

Run the command and monitor output for:
- ✅ File generation confirmations
- ✅ System config registration
- ✅ Sanity check execution
- ⚠️ Any warnings or errors

**Expected Output**:
```
✅ Generated runner: run_custom_{supplier-id}.py
✅ Generated categories: config/{supplier_name}_workflow_categories.json
✅ Registered workflow: {supplier_name}_workflow
✅ Sanity check: 6/6 criteria passed
```

---

## Step 4: Validate Generated Files ⚠️ CRITICAL

**🚨 YOU MUST READ AND ANALYZE FILES - NOT JUST CHECK EXISTENCE 🚨**

This is the most critical step. You must thoroughly validate all generated files.

### 4.1. Runner Script Validation

**File Location**: `run_custom_{supplier-id}.py` (hyphen-form)
- Example: `run_custom_supplier-com.py`

**Read the file** and perform these checks:

#### A. Structure Checks (Compare with Reference Implementations)

Read reference implementations:
- `sample_data/reference_runners/run_custom_poundwholesale.py` (143 lines, with auth)
- `sample_data/reference_runners/run_custom_clearance_king.py` (117 lines, no auth)

Verify generated runner:
- [ ] **Length**: 117-143 lines (NEVER 26 lines)
  - If 26 lines → **CRITICAL ERROR** - This is a shim, not full implementation
  - Report: "❌ CRITICAL: Generated runner is only 26 lines - this is a shim forwarding to wrong base runner"

- [ ] **Imports Present**:
  ```python
  import asyncio
  import logging
  import sys
  import os
  from playwright.async_api import async_playwright
  from config.system_config_loader import SystemConfigLoader
  from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
  from utils.browser_manager import BrowserManager
  ```

- [ ] **Main Function**:
  ```python
  async def main():
      # ... implementation ...
  ```

- [ ] **Entry Point**:
  ```python
  if __name__ == "__main__":
      asyncio.run(main())
  ```

#### B. Workflow Integration Checks

**CRITICAL**: Verify workflow_key is correct:

Search for this line:
```python
workflow_config = config_loader.get_workflow_config('...')
```

- [ ] Workflow key is CORRECT for this supplier
- [ ] NOT referencing wrong supplier

If wrong workflow_key found:
```
❌ CRITICAL ERROR: Runner references wrong workflow
   Found: 'other_supplier_workflow'
   Expected: '{supplier_name}_workflow'

   This will cause sanity check to scrape wrong supplier!
```

#### C. Authentication Integration Checks

**If authentication_required=true**:

- [ ] Auth helper import present:
  ```python
  from tools.{supplier-id}.supplier_authentication_service import {ClassName}AuthenticationHelper
  ```

- [ ] Auth helper instantiated:
  ```python
  auth_helper = {ClassName}AuthenticationHelper(page)
  ```

- [ ] Authentication logic present:
  ```python
  is_authenticated = await auth_helper.is_authenticated()
  if not is_authenticated:
      login_success = await auth_helper.login(credentials)
  ```

**If authentication_required=false**:

- [ ] NO auth helper imports
- [ ] Comment stating: `# No authentication required` or similar

#### D. Naming Convention Checks

Reference: `docs/NAMING_CONVENTIONS.md`

- [ ] **File Name**: Uses hyphen-form
  - ✅ Correct: `run_custom_supplier-com.py`
  - ❌ Wrong: `run_custom_supplier.com.py`
  - ❌ Wrong: `run_custom_supplier_com.py`

- [ ] **Supplier ID** in imports/paths uses hyphen-form:
  - Example: `tools/supplier-com/`

#### E. Output Filename Checks (Logs + Reports)

- [ ] Runner calls `setup_logger(supplier_name=supplier_name)` (not `setup_logger()`)
- [ ] Debug log filename includes supplier identifier (e.g. `run_custom_supplier-co-uk_YYYYMMDD_HHMMSS.log`)
- [ ] Financial reports are generated under supplier folder AND include supplier identifier in filename


### 4.2. Configuration Files Validation

#### A. Categories Configuration

**Location**: `config/{workflow_key}_categories.json`
- Example: `config/supplier_workflow_categories.json`

**Read the file** and verify:
- [ ] JSON format correct: `{"category_urls": [...]}`
- [ ] URLs are complete (include protocol: `https://`)
- [ ] URL count matches expected
- [ ] No duplicate URLs
- [ ] All URLs belong to correct supplier domain

#### B. Selector Configuration

**Location**: `config/supplier_configs/{domain}.json` (dot-form!)
- Example: `config/supplier_configs/supplier.com.json`

**Read the file** and verify:

- [ ] **File Name**: Uses dot-form (NOT hyphen-form)
  - ✅ Correct: `supplier.com.json`
  - ❌ Wrong: `supplier-com.json`

- [ ] **All Required Selectors Present**:
  - [ ] `supplier_url`
  - [ ] `product_card_selector`
  - [ ] `title_selector`
  - [ ] `price_selector`
  - [ ] `url_selector`
  - [ ] `ean_selector`
  - [ ] `next_page_selector`
  - [ ] `image_selector`
  - [ ] `out_of_stock_selector`
  - [ ] `authentication_required` (boolean)

- [ ] **Values are non-empty** (not null or "")

- [ ] **authentication_required matches** what was provided

#### C. System Config Update

**Location**: `config/system_config.json`

**Read the workflows section** and verify:

- [ ] New workflow entry exists: `{workflow_key}: {...}`

- [ ] Entry contains required fields:
  ```json
  "{supplier_name}_workflow": {
    "supplier_name": "supplier.com",
    "supplier_url": "https://supplier.com",
    "categories_config_path": "config/{supplier_name}_workflow_categories.json",
    "use_predefined_categories": true,
    "ai_client": null,
    "authentication_required": false
  }
  ```

- [ ] `supplier_name` uses dot-form
- [ ] `supplier_url` is correct
- [ ] `categories_config_path` is correct
- [ ] `authentication_required` matches what was provided

### 4.3. Authentication Helper Validation (If Applicable)

**If authentication_required=true**, validate auth helper:

#### A. File Location

**Directory**: `tools/{supplier-id}/` (hyphen-form)
- Example: `tools/supplier-com/`

**Files**:
- [ ] Directory exists
- [ ] `__init__.py` exists
- [ ] `supplier_authentication_service.py` exists

#### B. Auth Helper Content

**Read** `tools/{supplier-id}/supplier_authentication_service.py`:

- [ ] Class name correct (PascalCase, no dots/hyphens):
  ```python
  class SupplierComAuthenticationHelper:
  ```

- [ ] Required methods present:
  ```python
  async def is_authenticated(self) -> bool:
      # ... implementation ...

  async def login(self, credentials: dict) -> bool:
      # ... implementation ...
  ```

- [ ] Contains TODO comments (EXPECTED):
  ```python
  # TODO: Customize based on supplier's auth indicators
  # TODO: Customize based on supplier's login flow
  ```

**⚠️ IMPORTANT**: Auth helper is a TEMPLATE requiring manual customization.

**Warn user**:
```
⚠️ Authentication Helper Generated as TEMPLATE

The auth helper at tools/{supplier-id}/supplier_authentication_service.py
requires manual customization:

1. Update is_authenticated() selectors:
   - Replace generic logout button check with actual auth indicators
   - Test on actual supplier website

2. Update login() implementation:
   - Add actual login form selectors
   - Implement login flow specific to this supplier

See sample_data/reference_auth/poundwholesale_auth.py for complete example.
```

### 4.4. Naming Convention Compliance Summary

**Verify all three naming forms used correctly**:

| Context | Form | Example | Location |
|---------|------|---------|----------|
| **Config Files** | Dot-form | `supplier.com.json` | `config/supplier_configs/` |
| **System Config** | Dot-form | `"supplier_name": "supplier.com"` | `config/system_config.json` |
| **Runner Script** | Hyphen-form | `run_custom_supplier-com.py` | Root directory |
| **Tool Directory** | Hyphen-form | `tools/supplier-com/` | `tools/` |
| **Workflow Key** | Underscore-form | `supplier_workflow` | `config/system_config.json` |
| **State Files** | Underscore-form | `supplier_com_processing_state.json` | `OUTPUTS/CACHE/processing_states/` |

**Reference**: See `docs/NAMING_CONVENTIONS.md` for complete specification.

### 4.5. Validation Summary

After completing all checks, create summary:

**✅ PASSED Validations**:
- List all checks that passed

**❌ FAILED Validations**:
- List all checks that failed with specific details

**⚠️ WARNINGS**:
- List any warnings (e.g., auth helper needs customization)

**If ANY critical errors found**:
1. Report the issue clearly
2. Identify root cause
3. Provide remediation steps
4. DO NOT proceed to Step 5 until resolved

---

## Step 5: Report Results

Provide comprehensive summary to user:

### 5.1. Success Summary

```
✅ Supplier Onboarding Complete: {SUPPLIER_DOMAIN}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 FILES GENERATED:

1. Runner Script (Full Implementation)
   Location: run_custom_{supplier-id}.py
   Size: 117-143 lines
   Status: ✅ Validated - Full implementation (NOT shim)
   Workflow: {supplier_name}_workflow (correct)
   Authentication: [Yes/No]

2. Categories Configuration
   Location: config/{supplier_name}_workflow_categories.json
   URLs: [count] category URLs
   Status: ✅ Validated - All URLs valid

3. Selector Configuration
   Location: config/supplier_configs/{domain}.json
   Selectors: 9 required selectors present
   Status: ✅ Validated - All selectors configured

4. System Configuration
   Location: config/system_config.json
   Workflow: {supplier_name}_workflow registered
   Status: ✅ Validated - Workflow registered correctly

[If auth required:]
5. Authentication Helper (TEMPLATE)
   Location: tools/{supplier-id}/supplier_authentication_service.py
   Status: ⚠️ Generated as template - Requires manual customization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 VALIDATION RESULTS:

Structure Checks:           ✅ PASSED (117-143 lines, full implementation)
Workflow Integration:       ✅ PASSED (correct workflow_key)
Naming Conventions:         ✅ PASSED (all three forms correct)
Configuration Files:        ✅ PASSED (all required fields present)
System Config Registration: ✅ PASSED (workflow registered)
[Authentication Integration: ✅ PASSED (template generated)]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SANITY CHECK RESULTS:

Scraping Rate:          ✅ PASS ([count] products found)
Amazon Cache:           ✅ PASS (cache files created)
Linking Map:            ✅ PASS (EAN mappings generated)
Financial CSV:          ✅ PASS (report generated)
Processing State:       ✅ PASS (state file created)
No Critical Errors:     ✅ PASS (no errors in logs)

Overall: 6/6 Criteria Passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 PROCEED TO STEP 6: PRE-RUN VERIFICATION

Next: LLM will perform comprehensive pre-run verification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.2. Failure Summary (If Issues Found)

```
❌ Supplier Onboarding Failed: {SUPPLIER_DOMAIN}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 CRITICAL ISSUES:

[List all critical issues with specific details and remediation steps]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ WARNINGS:

[List any warnings]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NEXT STEPS:

1. Address all critical issues listed above
2. Re-validate after fixes
3. Do NOT proceed to Step 6 until all issues resolved

For detailed troubleshooting: See docs/TROUBLESHOOTING.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 6: Pre-Run Verification (LLM MANUAL WORK)

**🚨 CRITICAL**: This step is performed MANUALLY by Claude using Read/Write tools ONLY. NO scripts executed.

**Purpose**: Comprehensive validation BEFORE executing the runner script to ensure all files are correct and system is ready.

**When**: ALWAYS execute after Step 5 (wizard execution) and BEFORE running the actual system.

---

### 6.1. Generated Files Verification

**Action**: Read and analyze ALL wizard-generated files:

#### A. Runner Script Deep Inspection

```bash
Read: run_custom_{supplier-id}.py
```

**Verify** (beyond Step 4 checks):
- [ ] **Line Count**: Confirm 117-143 lines (count actual lines)
- [ ] **All Template Fixes Present**:
  - [ ] No `workflow_key` parameter in PassiveExtractionWorkflow constructor
  - [ ] No `browser_manager.close()` in finally block
  - [ ] Windows event loop handling present (Python 3.13+)
  - [ ] UTF-8 stdout reconfiguration present
- [ ] **Syntax Validation**: Run `python -m py_compile {filename}`
  ```bash
  python -m py_compile run_custom_{supplier-id}.py
  # Should output nothing (success) or syntax errors
  ```

#### B. Categories File Content Accuracy

```bash
Read: config/{supplier_name}_workflow_categories.json
```

**Verify**:
- [ ] **Correct Supplier URLs**: ALL URLs contain correct supplier domain
  - ❌ Check for: Wrong supplier URLs (poundwholesale, clearance-king, etc.)
  - ✅ Verify: All URLs match the supplier being onboarded
- [ ] **All User-Provided URLs Present**: Compare with original source
- [ ] **JSON Structure Valid**: Proper formatting, no syntax errors
- [ ] **URL Count Matches**: Count should match original source

**Example Check**:
```bash
# Count URLs containing correct supplier domain
grep -c "{supplier_domain}" config/{supplier_name}_workflow_categories.json
# Should equal total URL count
```

#### C. Selectors File Accuracy

```bash
Read: config/supplier_configs/{domain}.json
```

**Verify**:
- [ ] **All Required Selectors Present**: product_item, title, price, url
- [ ] **Selectors Match User-Provided Data**: Compare with original source
- [ ] **CSS Syntax Valid**: No unbalanced brackets/parentheses
- [ ] **No Empty Values**: All selector fields populated

#### D. System Config Integration

```bash
Read: config/system_config.json
# Navigate to workflows section
```

**Verify**:
- [ ] **Workflow Entry Created**: {supplier_name}_workflow exists
- [ ] **categories_config_path Correct**:
  - ✅ Points to: `config/{supplier_name}_categories.json` OR
  - ✅ Points to: `config/{supplier_name}_workflow_categories.json`
  - ❌ NO `_workflow` suffix IF single-file approach used
- [ ] **All Paths Resolve**: Referenced files exist at specified paths

---

### 6.2. Content Accuracy Verification

**Action**: Cross-reference all files for consistency:

#### A. URL Domain Consistency Check

**Critical Check**: Verify NO wrong supplier URLs exist

```bash
# Manually inspect categories file
Read: config/{supplier_name}_workflow_categories.json

# For each URL, verify:
1. Starts with https:// or http://
2. Contains correct supplier domain: {supplier_domain}
3. No other supplier domains present
```

**If wrong domains found**:
```
❌ CRITICAL: Wrong Supplier URLs Detected

Found URLs from: [other_supplier.com]
Expected domain: {supplier_domain}

Action Required: Return to Step 0, fix categories file, re-run wizard
```

#### B. Selector Consistency Check

**Verify selectors match user-provided data**:

```bash
# Compare selectors in config with original source
# Ensure no loss or modification during conversion
```

**Check**:
- [ ] `product_item` selector matches original
- [ ] `title` selector matches original
- [ ] `price` selector matches original
- [ ] All other selectors match original

#### C. Metadata Validation

**Verify timestamps and file consistency**:

```bash
# Check file creation timestamps (should be recent)
ls -la run_custom_{supplier-id}.py
ls -la config/{supplier_name}_workflow_categories.json
ls -la config/supplier_configs/{domain}.json

# All should have recent timestamps (within last hour)
```

**Check**:
- [ ] All files created recently (same session)
- [ ] No stale files from previous attempts
- [ ] File sizes reasonable (not empty, not corrupted)

---

### 6.3. System Readiness Check

**Action**: Verify system prerequisites and dependencies:

#### A. Atomic Operations Verification

```bash
# Test file permissions
# Verify UTF-8 encoding support
```

**Check**:
- [ ] Write permissions on OUTPUTS/ directory
- [ ] Write permissions on OUTPUTS/CACHE/processing_states/
- [ ] UTF-8 encoding available for all file operations

#### B. Chrome Browser Connectivity

```bash
# Verify Chrome debug port accessible
curl http://localhost:9222/json/version
# Should return Chrome version JSON
```

**Check**:
- [ ] Chrome running with debug port 9222
- [ ] Chrome responding to CDP connections
- [ ] No port conflicts

#### C. Memory and Resource Assessment

**Check**:
- [ ] Available RAM for processing (recommend 4GB+ free)
- [ ] Disk space for OUTPUTS (recommend 1GB+ free)
- [ ] No resource-intensive processes running

#### D. State Manager Compatibility

**Check**:
- [ ] Single-file approach verified (ONE categories file)
- [ ] State manager can read categories file location
- [ ] No conflicting dual files from previous attempts

---

### 6.4. Pre-Run Verification Summary

**After completing all checks, generate comprehensive report**:

```
═══════════════════════════════════════════════════════════
🔍 PRE-RUN VERIFICATION COMPLETE
═══════════════════════════════════════════════════════════

✅ GENERATED FILES VERIFICATION:

Runner Script:
  File: run_custom_{supplier-id}.py
  Lines: 135 ✅
  Syntax: Valid ✅
  Template Fixes: All present ✅
  Workflow Key: {supplier_name}_workflow ✅

Categories:
  File: config/{supplier_name}_workflow_categories.json
  URLs: 150 ✅
  Domain: All {supplier_domain} ✅
  No Wrong URLs: Verified ✅

Selectors:
  File: config/supplier_configs/{domain}.json
  Required Keys: All present ✅
  CSS Syntax: Valid ✅
  Match Original: Verified ✅

System Config:
  Workflow Entry: Created ✅
  Paths: All resolve correctly ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CONTENT ACCURACY:

URL Domain Check:     ✅ All URLs verified correct supplier domain
Selector Accuracy:    ✅ All selectors match user-provided data
Integration:          ✅ Cross-file consistency verified
Metadata:             ✅ Recent timestamps, proper file sizes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SYSTEM READINESS:

Atomic Operations:    ✅ File permissions verified
Chrome Connectivity:  ✅ Debug port 9222 accessible
UTF-8 Encoding:       ✅ Available
Memory:               ✅ 8GB free (sufficient)
Disk Space:           ✅ 50GB free (sufficient)
State Manager:        ✅ Single-file approach verified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 OVERALL STATUS: ✅ READY FOR EXECUTION

All verification stages passed. System is ready to proceed.

═══════════════════════════════════════════════════════════
```

---

## Step 7: User Decision Point

**After LLM completes all verification**, present options to user:

```
═══════════════════════════════════════════════════════════
🚀 EXECUTION OPTIONS
═══════════════════════════════════════════════════════════

System verification complete. Choose how to proceed:

1️⃣ TEST RUN (Recommended)
   ⏱️ Duration: 20 seconds
   📊 Purpose: Smoke test to validate scraping begins correctly
   ✅ Validates: Chrome connection, first category access, initial product extraction
   ⚠️ Note: Interrupts after 20 seconds (Ctrl+C)

   Command:
   python run_custom_{supplier-id}.py
   # Interrupt after 20 seconds: Ctrl+C

2️⃣ MAIN RUN (Full Execution)
   ⏱️ Duration: 30-60 minutes (depends on URL count)
   📊 Purpose: Complete 150-URL processing pipeline
   ✅ Produces: Full financial analysis, linking maps, state persistence

   Command:
   python run_custom_{supplier-id}.py

3️⃣ FIX ISSUES FIRST (If Problems Found)
   🔧 Action: Return to appropriate step
   - Content issues → Return to Step 0 (LLM preprocessing)
   - Wizard issues → Return to Step 3 (Re-run wizard)
   - Validation issues → Return to Step 4 (Re-validate)

═══════════════════════════════════════════════════════════

❓ YOUR CHOICE: [ ] Test Run  [ ] Main Run  [ ] Fix Issues

Please indicate your choice, and I will proceed accordingly.
═══════════════════════════════════════════════════════════
```

---

## Reference Documentation

Comprehensive documentation available:

- **Naming Conventions**: [docs/NAMING_CONVENTIONS.md](docs/NAMING_CONVENTIONS.md)
  - Three naming forms (dot, hyphen, underscore)
  - Usage contexts and examples
  - Common mistakes to avoid

- **File Specifications**: [docs/FILE_SPECIFICATIONS.md](docs/FILE_SPECIFICATIONS.md)
  - Runner script structure (117-143 lines)
  - Configuration file formats
  - Authentication helper structure

- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
  - Common issues and solutions
  - Root cause analysis
  - Recovery procedures

## Reference Implementations

Use these for comparison during validation:

- **Runner with Authentication**: [sample_data/reference_runners/run_custom_poundwholesale.py](sample_data/reference_runners/run_custom_poundwholesale.py)
  - 143 lines
  - Complete authentication integration
  - Import hygiene validation

- **Runner without Authentication**: [sample_data/reference_runners/run_custom_clearance_king.py](sample_data/reference_runners/run_custom_clearance_king.py)
  - 117 lines
  - Simple workflow execution
  - No auth overhead

- **Authentication Helper Example**: [sample_data/reference_auth/poundwholesale_auth.py](sample_data/reference_auth/poundwholesale_auth.py)
  - Complete is_authenticated() implementation
  - Complete login() implementation
  - Magento-specific selectors

## Templates

Templates used by wizard for file generation:

- **Runner Template**: [templates/runner_template.py.txt](templates/runner_template.py.txt)
  - Base structure for all runners
  - Variable placeholders: {{WORKFLOW_KEY}}, {{SUPPLIER_NAME}}, etc.
  - Authentication integration logic

- **Auth Helper Template**: [templates/auth_helper_template.py.txt](templates/auth_helper_template.py.txt)
  - Base structure for authentication helpers
  - TODO comments for customization points
  - Standard method signatures

---

## Common Issues and Quick Fixes

### Issue: 26-Line Shim Generated

**Symptom**: Runner file is only 26 lines, forwards to another supplier
**Root Cause**: Wizard called wrong function (create_runner_shim vs create_full_runner)
**Fix**: Delete shim, verify wizard has create_full_runner(), re-run

### Issue: Wrong Workflow Executed

**Symptom**: Sanity check scrapes wrong supplier
**Root Cause**: Runner references wrong workflow_key
**Fix**: Edit runner, change workflow_key, save, re-run

### Issue: Auth Helper Not Generated

**Symptom**: No tools/{supplier-id}/ directory created
**Root Cause**: Missing --authentication-required flag in wizard command
**Fix**: Re-run wizard with --authentication-required true --username X --password Y

For complete troubleshooting guide: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Success Criteria

Onboarding is successful when:

✅ All files generated in correct locations
✅ Runner is 117-143 lines (full implementation, NOT 26-line shim)
✅ Workflow_key correct throughout all files
✅ All three naming forms used correctly (dot, hyphen, underscore)
✅ All configuration files valid and complete
✅ System config updated with new workflow
✅ Sanity check passes all 6 criteria
✅ [If auth] Auth helper generated as template with TODO comments
✅ Pre-run verification passes all checks
✅ Content accuracy verified (no wrong supplier URLs)
✅ System readiness confirmed

---

**End of SKILL.md**
