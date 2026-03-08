===============================================================================
SUPPLIER ONBOARDING - MANDATORY EXECUTION PROTOCOL
===============================================================================

⚠️  THIS FILE EXISTS BECAUSE PREVIOUS EXECUTIONS FAILED DUE TO SKIPPING STEPS
⚠️  YOU MUST FOLLOW THIS PROTOCOL EXACTLY - NO EXCEPTIONS
⚠️  EACH STEP REQUIRES EVIDENCE AND USER CONFIRMATION BEFORE PROCEEDING
⚠️  ALL REFERENCES INCLUDE EXACT SKILL.MD LINE NUMBERS - USE THEM

===============================================================================
PRE-EXECUTION DECLARATION (MANDATORY)
===============================================================================

Before starting ANY supplier onboarding, you MUST state:

"I am about to onboard [supplier_name] using the supplier-onboarding skill.
I have read SKILL.md completely (lines 1-682) and understand ALL steps are mandatory.
I will not skip validation checkpoints. I will provide evidence for each step.
I will stop at critical checkpoints and get user confirmation before proceeding."

===============================================================================
STEP 0: INITIAL HANDSHAKE - INFORMATION GATHERING
===============================================================================

**SKILL.MD Reference**: Lines 52-82 (Section "Step 0: Initial Handshake")

MANDATORY QUESTIONS (Must ask ALL 5 before proceeding):

1. Authentication Required? (Yes/No)
   - SKILL.MD Line 64-65: Get login_url, username, password
   - If Yes, you MUST read docs/AUTHENTICATION_CUSTOMIZATION.md (Line 15, 20, 41)

2. Category List Provided?
   - SKILL.MD Line 66: Request list or file path
   - Must validate URLs contain correct domain

3. Test Product URL? (CRITICAL - Cannot proceed without this)
   - SKILL.MD Line 67: "Provide ONE valid product URL for selector verification"
   - **STOP POINT**: Do not proceed without this

4. Existing CSS Selectors? (Yes/No)
   - SKILL.MD Line 68-69: Must be BeautifulSoup-compatible
   - If No: You MUST extract using Chrome DevTools (Step 1.4, Lines 179-189)

5. Pagination Pattern?
   - SKILL.MD Line 70: ?page=N, /page/N/, or Load More button
   - Line 79-81: If not ?page=N, document limitation

**REQUIRED OUTPUT** (Stop and get confirmation):
```
Supplier Onboarding - Initial Information:
- Domain: [domain]
- Authentication: [Yes/No] (details if yes)
- Categories: [count] URLs provided
- Test Product URL: [URL]
- Existing Selectors: [Yes/No]
- Pagination: [pattern]

USER: Please confirm all information is correct before I proceed.
```

**DOCUMENTATION TO READ BEFORE PROCEEDING**:
- If authentication=true: Read docs/AUTHENTICATION_CUSTOMIZATION.md (SKILL.MD Line 15, 20)
- Review docs/NAMING_CONVENTIONS.md (SKILL.MD Line 16)
- Review docs/FILE_SPECIFICATIONS.md (SKILL.MD Line 17)

===============================================================================
STEP 1: DATA PREPROCESSING AND VALIDATION
===============================================================================

**SKILL.MD Reference**: Lines 85-260 (Section "Step 1: Data Preprocessing")

### 1.2. Validate Categories Content (Lines 100-127)

**MANDATORY ACTIONS** (Line 101-107, 123-127):
- Read categories file line by line
- Check URL format (http/https)
- Verify domain matches supplier
- Count total valid URLs
- Report invalid URLs found

**REQUIRED OUTPUT** (Stop and get confirmation):
```
Category URL Validation (SKILL.MD Lines 108-115 format):
Line 1: https://supplier.com/category/toys - ✅ Valid
Line 5: https://wrong-supplier.com/category - ❌ Removed (wrong domain)
Line 8: supplier.com/category - ❌ Fixed (added https://)

Total Valid: 335 URLs
Total Invalid: 2 URLs (removed)

USER: Confirm I should proceed with 335 valid URLs.
```

### 1.3. Validate Selectors Content (Lines 129-177)

**CRITICAL REQUIREMENTS** (Lines 154-159, 173-177):
- Extract ALL selectors from source
- Verify `product_item`, `title`, `price`, `url` are present
- Confirm `field_mappings` structure (Line 150-152)
- Check CSS syntax: No Playwright extensions (Lines 160-171)
- **NO**: `:text()`, `:has-text()`, `xpath` (Line 186)

**REQUIRED SELECTORS** (Line 154-158):
- [ ] `product_item` - Container for each product
- [ ] `title` - Product title selector
- [ ] `price` - Price selector
- [ ] `url` - Product URL selector

**STOP POINT**: If any selector missing, DO NOT PROCEED.

### 1.4. Selector Retrieval Protocol (Lines 179-189)

**If no selectors provided, MANDATORY Chrome DevTools prompt** (Lines 182-188):

Use EXACT prompt:
> "I am inspecting the page to find robust CSS selectors.
> CAUTION:
> 1. Standard CSS Only: I MUST use standard CSS selectors
> 2. No Playwright Extensions: I MUST NOT use `:text()`, `:has-text()`, or `xpath`. The scraper uses BeautifulSoup.
> 3. Specificity: I will avoid overly specific chains
> 4. Verification: I will verify in Console with `document.querySelectorAll('selector')'`"

**REQUIRED OUTPUT**:
```
Chrome DevTools Selector Extraction:
- Opened: https://www.efghousewares.co.uk/shop-by-department/bathroom
- Verified selector: .grid-product - matches 24 elements ✅
- Extracted: product_item: .grid-product
- Extracted: title: .product-title a
- Extracted: price: .price-value

USER: Confirm these selectors match your site structure.
```

### 1.5. Create JSON Files (Lines 190-230)

**MANDATORY FILES** (Line 191-230):
- `setup/{supplier}_categories.json` (Lines 193-205 format)
- `setup/{supplier}_selectors.json` (Lines 208-223 format)

**CRITICAL STRUCTURE** (Line 150-152, 208-223):
```json
{
  "field_mappings": {
    "product_item": ["selector"],
    "title": ["selector"]
  }
}
```
- NOT flat: `{"price": ".price"}` ❌
- MUST be nested: `{"field_mappings": {"price": [".price"]}}` ✅

**REQUIRED OUTPUT** (Line 260 format):
```
Step 1.5 Complete - JSON Files Created:
✅ setup/efghousewares_categories.json (335 URLs)
✅ setup/efghousewares_selectors.json (7 selectors)
✅ Valid JSON syntax confirmed
✅ field_mappings structure correct (SKILL.MD Line 150-152)
✅ All required selectors present (SKILL.MD Line 154-158)

USER: Confirm these files look correct before I proceed to Step 2.
```

### 1.6. Create Wizard Input (Lines 231-245)

**MANDATORY** (Lines 233-245): Create `temp/{supplier}_wizard_input.json`

**REQUIRED FIELDS** (Lines 236-244):
- `domain`: supplier.com (dot-form)
- `categories_source`: path to categories JSON
- `selectors_source`: path to selectors JSON
- `workflow_key`: {supplier}_workflow (underscore-form)
- `mode`: "generate"
- `authentication_required`: true/false
- `test_product_url`: [required]
- `repo_root`: absolute path

**STOP POINT**: Get user confirmation before invoking wizard.

### 1.7. Validation Report (Lines 260-281)

**MANDATORY FORMAT** (Lines 262-281):
```
================================
STEP 1: DATA VALIDATION COMPLETE
================================
✅ Files Read:
   - setup/categories_{supplier}.txt (335 URLs)
   - setup/selectors_{supplier}.txt (7 selectors)
✅ Content Validated:
   - 335 valid URLs (domain verified)
   - All required selectors present
   - CSS syntax verified (no Playwright extensions)
✅ JSON Files Created (LLM Manual):
   - setup/{supplier}_categories.json (335 URLs)
   - setup/{supplier}_selectors.json (7 selectors)
✅ Wizard Input Created:
   - temp/{supplier}_wizard_input.json
STATUS: ✅ READY FOR CONFIGURATION
================================

USER: Confirm I should proceed to Step 2.
```

===============================================================================
STEP 2: PREPARE CONFIGURATION FILES
===============================================================================

**SKILL.MD Reference**: Lines 284-337 (Section "Step 2: Prepare Configuration Files")

### 2.1. Categories Configuration (Lines 288-309)

**SKIP THIS STEP** - Already completed in Step 1.5

### 2.2. Selector Configuration (Lines 311-337)

**SKIP THIS STEP** - Already completed in Step 1.5

**STOP POINT**: Both files should already exist from Step 1.5

**NOTE**: If files missing, something went wrong. Return to Step 1.

===============================================================================
STEP 3: INVOKE WIZARD
===============================================================================

**SKILL.MD Reference**: Lines 339-402 (Section "Step 3: Invoke Wizard")

### 3.1. Construct Command (Lines 343-384)

**Execute wizard** using file from Step 1.6:
```bash
python .claude/skills/supplier-onboarding/wizard.py --wizard-input temp/{supplier}_wizard_input.json
```

**MANDATORY FLAGS** (if auth required, Lines 379-383):
- `--authentication-required true`
- `--username "user@example.com"`
- `--password "pass123"`

### 3.2. Execute and Monitor (Lines 386-402)

**CAPTURE ALL OUTPUT** and verify:
- ✅ Generated runner (Lines 396-397)
- ✅ Generated categories (Line 398)
- ✅ Registered workflow (Line 399)
- ✅ Sanity check: 6/6 criteria passed (Line 399)

**REQUIRED OUTPUT**:
```
Wizard Execution Output:
[capture all output here]

Expected Results Checklist (SKILL.MD Lines 396-399):
✅ Generated runner: run_custom_efghousewares-co-uk.py
✅ Generated categories: config/efghousewares_workflow_categories.json
✅ Registered workflow: efghousewares_workflow
✅ Sanity check: 6/6 criteria passed

Generated Files:
1. run_custom_efghousewares-co-uk.py (____ lines)
2. config/efghousewares_workflow_categories.json
3. config/supplier_configs/efghousewares.co.uk.json
4. config/system_config.json (updated)
5. tools/efghousewares-co-uk/supplier_authentication_service.py (____ lines)
6. tools/efghousewares-co-uk/__init__.py

USER: Confirm wizard succeeded before I proceed to Step 4.
```

**STOP POINT**: If wizard reports errors or warnings, DO NOT PROCEED to Step 4.

===============================================================================
STEP 4: STRICT MANUAL VERIFICATION (MANDATORY)
===============================================================================

**SKILL.MD Reference**: Lines 404-650 (Section "Step 4: Strict Manual Verification")

**⚠️ CRITICAL WARNING** (Line 406): "You MUST read and verify EVERY generated file. Do not rely on the Wizard's success message."

### 4.1. Runner Script Validation (Lines 418-499)

#### A. Structure Checks (Lines 423-452)

**MANDATORY VERIFICATION** (Line 425-427):
- [ ] Line count: _____ (MUST be 117-143, NEVER 26)
- [ ] If 26 lines: ❌ CRITICAL ERROR - This is a shim

**Import Checks** (Lines 429-439):
- [ ] asyncio
- [ ] logging
- [ ] sys
- [ ] os
- [ ] playwright.async_api
- [ ] config.system_config_loader
- [ ] tools.passive_extraction_workflow_latest
- [ ] utils.browser_manager

**Main Function** (Lines 441-445): Must exist

**Entry Point** (Lines 447-449): Must use `if __name__ == "__main__"`

#### B. Workflow Integration Checks (Lines 453-468)

**System Config Loading** (Lines 454-459):
- [ ] `SystemConfigLoader()` called
- [ ] `efghousewares_workflow` key accessed
- [ ] All config values extracted

**PassiveExtractionWorkflow Instantiation** (Lines 461-467):
- [ ] `PassiveExtractionWorkflow()` created
- [ ] Supplier name passed correctly
- [ ] Workflow executed

#### C. Authentication Integration Checks (Lines 470-488)

**If authentication_required=true** (SKILL.MD Lines 470-488):

**MANDATORY IMPORT** (Line 474-476):
```python
from tools.efghousewares-co-uk.supplier_authentication_service import EfghousewaresCoUkAuthenticationHelper
```

**Instantiation** (Line 478-479):
```python
auth_helper = EfghousewaresCoUkAuthenticationHelper(page)
```

**Authentication Logic** (Line 481-487):
```python
is_authenticated = await auth_helper.is_authenticated()
if not is_authenticated:
    login_success = await auth_helper.login(credentials)
```

#### D. Naming Convention Checks (Lines 491-498)

**CRITICAL - Reference docs/NAMING_CONVENTIONS.md** (Line 492):

- [ ] **File Name**: Uses hyphen-form ✅
  - Line 494: Correct: `run_custom_supplier-com.py`
  - Line 495: Wrong: `run_custom_supplier.com.py` ❌
  - Line 496: Wrong: `run_custom_supplier_com.py` ❌

- [ ] **Supplier ID in imports/paths**: Uses hyphen-form (Line 497-498)
  - Example: `tools/efghousewares-co-uk/` ✅
  - NOT: `tools/efghousewares_co_uk/` ❌
  - NOT: `tools/efghousewares.co.uk/` ❌

**REQUIRED OUTPUT** (stop and verify):
```
Runner Script Validation (SKILL.MD Section 4.1, Lines 418-499):

A. Structure (Lines 423-452):
- Line count: 153 ✅ (within 117-143 range)
- All imports present ✅ (Lines 429-439)
- Main function exists ✅ (Lines 441-445)
- Entry point correct ✅ (Lines 447-449)

B. Workflow Integration (Lines 453-468):
- SystemConfigLoader: called ✅
- PassiveExtractionWorkflow: instantiated ✅

C. Authentication (Lines 470-488):
- Import present: from tools.efghousewares-co-uk... ✅
- Auth helper instantiated: YES ✅
- Auth logic: is_authenticated() → login() ✅

D. Naming Convention (Lines 491-498, docs/NAMING_CONVENTIONS.md):
- File name: run_custom_efghousewares-co-uk.py (hyphen-form) ✅
- Import path: tools.efghousewares-co-uk (hyphen-form) ✅

Status: ✅ PASS (See SKILL.MD Lines 418-499 for complete validation)

USER: Confirm runner validation before I check config files.
```

**STOP POINT**: Fix any failures before proceeding to 4.2.

### 4.2. Configuration Files Validation (Lines 500-549)

#### A. Categories Configuration (Lines 502-510)

**Read** `config/efghousewares_workflow_categories.json`:

- [ ] JSON format: `{"category_urls": [...]}` (Line 505)
- [ ] URLs include protocol `https://` (Line 506)
- [ ] URL count matches expected (Line 507)
- [ ] No duplicate URLs (Line 508)
- [ ] All URLs correct domain (Line 509)

#### B. Selector Configuration (Lines 511-530)

**CRITICAL - File Name Check** (Line 514-516):
- [ ] Uses dot-form: `efghousewares.co.uk.json` ✅
- [ ] NOT hyphen-form: `efghousewares-co-uk.json` ❌

**Read** `config/supplier_configs/efghousewares.co.uk.json`:

**All Required Selectors** (Line 517-529):
- [ ] `supplier_url` present
- [ ] `product_item` present (Line 519)
- [ ] `title` present (Line 520)
- [ ] `price` present (Line 521)
- [ ] `url` present (Line 522)
- [ ] `ean` present (Line 523)
- [ ] `next_page_selector` present (Line 524)
- [ ] `image` present (Line 525)
- [ ] `quantity` present (if required)
- [ ] `authentication_required` boolean (Line 527)
- [ ] All values non-empty (Line 528)

**Authentication Match** (Line 529):
- [ ] `authentication_required` matches what user provided

#### C. System Config Update (Lines 531-549)

**Read** `config/system_config.json` (workflow section):

- [ ] Entry exists: `efghousewares_workflow` (Line 534)
- [ ] `supplier_name`: dot-form (Line 538, 546)
- [ ] `supplier_url`: correct (Line 539, 547)
- [ ] `categories_config_path`: correct (Line 540, 548)
- [ ] `authentication_required`: matches (Line 543, 549)
- [ ] `use_predefined_categories`: true (Line 541)
- [ ] `ai_client`: null (Line 542)

**REQUIRED OUTPUT**:
```
Configuration Files Validation (SKILL.MD Section 4.2, Lines 500-549):

A. Categories Config (Lines 502-510):
- JSON format: ✅ valid
- URL count: 335 ✅
- No duplicates: ✅

B. Selector Config (Lines 511-530):
- File name: efghousewares.co.uk.json (dot-form) ✅ (Line 514-516)
- All 7 required selectors present ✅ (Lines 517-529)
- field_mappings structure: ✅ (SKILL.MD Line 150-152)
- authentication_required matches: ✅ (Line 529)

C. System Config (Lines 531-549):
- Workflow entry exists: efghousewares_workflow ✅ (Line 534)
- All fields correct: ✅ (Lines 537-549)

Status: ✅ PASS (See SKILL.MD Lines 500-549 for complete validation)

USER: Confirm config validation before I check authentication helper.
```

**STOP POINT**: Fix any failures before proceeding to 4.3.

### 4.3. Authentication Helper Validation (Lines 551-588)

**If AND ONLY IF authentication_required=true**:

#### A. File Location (Lines 554-560)

**Directory**: `tools/efghousewares-co-uk/` (hyphen-form) ✅

**Files** (Lines 558-560):
- [ ] Directory exists
- [ ] `__init__.py` exists
- [ ] `supplier_authentication_service.py` exists

#### B. Auth Helper Content (Lines 562-574)

**Read** `tools/efghousewares-co-uk/supplier_authentication_service.py`:

**Class Name** (Line 564-566):
- MUST be PascalCase: `EfghousewaresCoUkAuthenticationHelper` ✅
- NO dots/hyphens in class name

**Required Methods** (Line 568-573):
- [ ] `async def is_authenticated(self) -> bool:`
- [ ] `async def login(self, credentials: dict) -> bool:`

#### C. Authentication Customization (CRITICAL - Lines 581-588)

**🚨 WARNING** (Line 585): "The auth helper generated by the wizard is a TEMPLATE ONLY and WILL FAIL without supplier-specific customization."

**⚠️ DO NOT SKIP** - Must read: `docs/AUTHENTICATION_CUSTOMIZATION.md` (Line 588)

**REQUIRED OUTPUT**:
```
Authentication Helper Validation (SKILL.MD Section 4.3, Lines 551-588):

A. File Location (Lines 554-560):
- Directory: tools/efghousewares-co-uk/ ✅ (hyphen-form)
- __init__.py: present ✅ (Line 559)
- supplier_authentication_service.py: present ✅ (Line 560)

B. Auth Helper Content (Lines 562-574):
- Class name: EfghousewaresCoUkAuthenticationHelper ✅ (PascalCase, Line 564-566)
- is_authenticated(): present ✅ (Line 568-571)
- login(): present ✅ (Line 568-572)

C. Customization Status:
- Docs read: docs/AUTHENTICATION_CUSTOMIZATION.md ✅ (Line 588)
- Login flow customized: YES
- Auth methods implemented: YES
- Tested in isolation: YES

Status: ✅ PASS (See SKILL.MD Lines 551-588 for complete validation)

WARNING: If auth helper is still template (lots of TODOs), DO NOT PROCEED.
Must read docs/AUTHENTICATION_CUSTOMIZATION.md and implement methods.
```

**STOP POINT**: If auth helper not customized, return to Step 4 customization.

### 4.4. Naming Convention Compliance Summary (Lines 617-630)

**Reference**: `docs/NAMING_CONVENTIONS.md` (Line 492, 617)

**Three Forms** (Lines 9-69 of docs/NAMING_CONVENTIONS.md):

1. **Dot-Form**: `supplier.co.uk` (config files, Line 10-21)
2. **Hyphen-Form**: `supplier-co-uk` (scripts, dirs, Line 25-43)
3. **Underscore-Form**: `supplier_co_uk` (workflows, state, Line 47-69)

**Final Validation** (Lines 618-630):
```
✅ Config Files: Use dot-form
✅ Runner/Tool Dirs: Use hyphen-form
✅ Workflow/State: Use underscore-form
```

### 4.5. Validation Summary (Lines 631-650)

**MANDATORY BEFORE PROCEEDING**:

```
================================
STEP 4 VALIDATION COMPLETE
================================
(SKILL.MD Section 4.1-4.3, Lines 418-588)

✅ Runner Script (Lines 418-499):
   - Structure: valid
   - Auth integration: correct
   - Naming: hyphen-form

✅ Configuration Files (Lines 500-549):
   - Categories: valid
   - Selectors: all present
   - System config: registered

✅ Authentication Helper (Lines 551-588):
   - Class: PascalCase
   - Methods: implemented
   - Customized: YES

✅ Naming Convention (docs/NAMING_CONVENTIONS.md):
   - All forms correct

🚨 READY FOR STEP 5
================================

USER: Confirm ALL validations passed before I proceed.
```

**STOP POINT**: If ANY validation failed, DO NOT PROCEED to Step 5.

===============================================================================
STEP 5: VALIDATE FILES (COMPLETED IN STEP 4)
===============================================================================

**SKILL.MD Reference**: Lines 404-588 already completed above

**Note**: Section 4 IS the validation step. If you completed 4.1-4.3, you're done.

===============================================================================
STEP 6: PRE-RUN VERIFICATION
===============================================================================

**SKILL.MD Reference**: Lines 682-699 (Section "Step 6: Pre-Run Verification")

**MANDATORY CHECKS** (Line 684-699):

- [ ] All files generated (Line 688-696 list)
- [ ] Runner script exists and valid
- [ ] Config files present
- [ ] Auth helper (if required) customized
- [ ] Chrome running on port 9222
- [ ] All configuration paths correct

**REQUIRED OUTPUT** (Line 685):
```
Step 6: Pre-Run Verification Complete (SKILL.MD Lines 682-699)

✅ All files generated:
   - Runner script
   - Categories config
   - Selector config
   - System config (updated)
   - Auth helper (if required)

✅ Configuration Paths:
   - Chrome debug port: 9222
   - All file paths correct
   - Repository location confirmed

🚨 READY FOR TEST RUN (Step 7)
================================

USER: Confirm I should execute test run now.
```

**STOP POINT**: Wait for explicit confirmation before running test.

===============================================================================
STEP 7: TEST RUN / MAIN RUN
===============================================================================

**SKILL.MD Reference**: Lines 700-711 (User Decision)

### 7.1. Test Run Protocol

**MANDATORY** (Line 703-710): Execute with limited scope first

**Command with limits**:
```bash
# Test run (LIMITED)
python run_custom_efghousewares-co-uk.py --max-categories 3 --max-products 10

# Main run (FULL)
python run_custom_efghousewares-co-uk.py
```

**CAPTURE AND REPORT** (required evidence):
- Test date and time
- Categories processed
- Products extracted per category
- Authentication success/failure
- Any errors with full tracebacks
- Final summary statistics

**CRITICAL SUCCESS CRITERIA**:
- [ ] At least 1 product found in first category
- [ ] Authentication works (if required)
- [ ] No Python errors
- [ ] Log shows products being extracted

**REQUIRED OUTPUT**:
```
Test Run Results:
- Categories processed: 3
- Products extracted:
  - Category 1: 24 products ✅
  - Category 2: 18 products ✅
  - Category 3: 31 products ✅
- Authentication: successful ✅
- Total products: 73

✅ SUCCESS CRITERIA MET

Analysis:
- Selector extraction working
- Auth flow functional
- System operational

USER: Test run successful. Ready for main run or additional testing?
```

### 7.2. Failure Handling

**If test run extracts 0 products** (or errors):

1. **IMMEDIATE ACTION**: STOP. Do not proceed to main run.
2. **Check logs**: Look for selector matching issues
3. **Debug selectors**: May need Chrome DevTools re-inspection
4. **Fix configuration**: Update selector config
5. **Re-test**: Must re-run test until products found

**Follow SKILL.MD Troubleshooting** (docs/TROUBLESHOOTING.md, Line 19)

===============================================================================
POST-EXECUTION REPORT (MANDATORY)
===============================================================================

**SKILL.MD Reference**: Provide comprehensive report regardless of outcome.

**REQUIRED FORMAT**:
```
Supplier Onboarding Execution Report
=====================================

Supplier: efghousewares.co.uk
Date: 2025-12-14
Executor: Claude Code
Protocol Version: EXECUTION_ENFORCEMENT.md v1.0
SKILL.MD Reference: Lines 1-682 (full document)

Execution Status: [✅ SUCCESS / ⚠️ PARTIAL / ❌ FAILURE]

PHASE 1: INFORMATION GATHERING (Lines 52-82)
- Authentication required: YES
- Categories provided: 335
- Test product URL: [provided]
- Pagination pattern: hash-based (#)
✅ COMPLETE

PHASE 2: DATA VALIDATION (Lines 85-260)
- Categories validated: 335 valid
- Selectors extracted: Chrome DevTools (Lines 179-189)
- Required selectors: 7/7 present (Lines 154-158)
- field_mappings: correct structure (Lines 150-152)
- JSON files created: 2 files
✅ COMPLETE

PHASE 3: WIZARD INVOCATION (Lines 339-402)
- Files generated: 6 files
- Sanity check: 6/6 passed (Line 399)
- No errors reported
✅ COMPLETE

PHASE 4: VALIDATION (Lines 404-588)
- Runner script: ✅ PASS (Lines 418-499)
- Config files: ✅ PASS (Lines 500-549)
- Auth helper: ✅ PASS (Lines 551-588)
- Naming conventions: ✅ PASS (Lines 491-498, 617-630)
✅ COMPLETE

PHASE 5-6: PRE-RUN CHECKS (Lines 682-699)
- All files verified
- Chrome running
- Config paths correct
✅ COMPLETE

PHASE 7: EXECUTION (Lines 700-711)
- Test categories: 3
- Products extracted: 73
- Auth success: YES
- Errors: none
✅ SUCCESS

FINAL STATUS: ✅ SYSTEM READY FOR PRODUCTION

Notes:
- All SKILL.MD steps followed
- All validations completed
- All checkboxes verified
- User confirmation at each stop point
```

===============================================================================
VIOLATION CONSEQUENCES (READ BEFORE EACH EXECUTION)
===============================================================================

**If you skip any validation step from above**:
- Product extraction will fail → 0 products found
- Authentication will fail → import errors or timeout
- Naming violations → Python module import errors
- Selector mismatches → BeautifulSoup returns empty results
- User will have to start over from Step 1

**THIS IS NOT HYPOTHETICAL - PREVIOUS EXECUTIONS FAILED FOR THESE EXACT REASONS**

===============================================================================
FINAL MEMORIZATION AID - THREE RULES
===============================================================================

Before starting ANY supplier onboarding, state these three rules:

1. **NEVER GUESS SELECTORS** (SKILL.MD Lines 179-189)
   - Always use Chrome DevTools
   - Always verify with `document.querySelectorAll()`
   - Never use Playwright extensions (`:text()`, `:has-text()`)

2. **NEVER SKIP VALIDATION** (SKILL.MD Section 4, Lines 404-588)
   - Every checkbox in Section 4 is mandatory
   - Every file must be read and verified
   - Wizard success message is not sufficient

3. **NEVER ASSUME IT WORKS** (SKILL.MD Lines 585-588)
   - Wizard generates templates, not finished code
   - Auth helper MUST be customized
   - Test run REQUIRED before main run

**When in doubt: STOP AND READ SKILL.MD**

===============================================================================
ACKNOWLEDGMENT
===============================================================================

By proceeding with supplier onboarding, you confirm:

✅ I have read SKILL.md completely (Lines 1-682)
✅ I understand all steps are mandatory
✅ I have EXECUTION_ENFORCEMENT.md open
✅ I will not skip validation checkpoints
✅ I will provide evidence for each step
✅ I will stop at critical checkpoints
✅ I will get user confirmation before proceeding

===============================================================================
END OF EXECUTION ENFORCEMENT PROTOCOL
===============================================================================
