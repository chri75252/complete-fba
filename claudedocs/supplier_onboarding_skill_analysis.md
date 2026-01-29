# Supplier Onboarding Skill - Analysis & Improvements Needed

## Current State Analysis

### What Works Well
- Comprehensive 7-step workflow structure
- Clear naming conventions (dot-form, hyphen-form, underscore-form)
- Detailed validation protocols
- Atomic file operations with WindowsSaveGuardian
- Good error detection for common issues

### Critical Gaps Identified

#### 1. ❌ MISSING: Mandatory Authentication Customization Step
**Current State**:
- Auth helper mentioned as a "warning" in Step 4
- Generic placeholder comment: "⚠️ Auth helper is a TEMPLATE - customize it"
- No detailed instructions on HOW to customize
- No supplier-specific guidance

**Problem**:
- Users don't know they MUST customize the auth helper
- Generic instructions don't work for different website architectures
- Each supplier has unique authentication patterns:
  - **Shopify sites** (dkwholesale.com): Use `/account/login`, email/password fields, account dropdown
  - **Magento sites**: Use `/customer/account/login/`, different selectors, CSRF tokens
  - **WooCommerce sites**: Use `/my-account/`, different form structure
  - **Custom sites**: Unique login flows, multi-step authentication, CAPTCHA

**Required Fix**:
- Create NEW Step 5: "Customize Authentication Helper (MANDATORY)"
- Make it non-optional for auth_required=true
- Include supplier-specific instructions based on website architecture
- Provide detailed selector identification workflow
- Include testing protocol before full run

#### 2. ❌ MISSING: Supplier-Specific Authentication Patterns
**Current State**:
- Generic "check for logout button" advice
- No recognition of different e-commerce platforms
- No guidance on handling common patterns

**Required Fix**:
Create supplier-specific customization sections:

**For Shopify Sites** (dkwholesale.com):
```python
# Login URL pattern: https://{domain}/account/login
# Email field: #RecoverEmail or input[name="customer[email]"]
# Password field: #CustomerPassword or input[name="customer[password]"]
# Login button: button[type="submit"] or input[type="submit"]
# Auth indicators: a[href*="/account"], .customer-logout
```

**For Magento Sites**:
```python
# Login URL pattern: https://{domain}/customer/account/login/
# Email field: #email or input[name="login[username]"]
# Password field: #pass or input[name="login[password]"]
# Login button: #send2 or button[type="submit"]
# Auth indicators: .logged-in, a[href$="/customer/account/logout/"]
```

**For WooCommerce Sites**:
```python
# Login URL pattern: https://{domain}/my-account/
# Email field: #username
# Password field: #password
# Login button: button[name="login"]
# Auth indicators: .woocommerce-MyAccount-navigation, a[href*="customer-logout"]
```

#### 3. ❌ MISSING: Authentication Testing Protocol
**Current State**:
- No testing before main run
- Users discover auth failures during full workflow

**Required Fix**:
Add to Step 5 (NEW):
```python
# Test authentication in isolation:
python -c "
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0, '.')
from tools.dkwholesale_com.supplier_authentication_service import DkwholesaleAuthenticationHelper

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    helper = DkwholesaleAuthenticationHelper(page)

    # Test is_authenticated
    is_auth = helper.is_authenticated()
    print(f'Authenticated: {is_auth}')

    # Test login if not authenticated
    if not is_auth:
        result = helper.login({'username': 'test@example.com', 'password': 'test'})
        print(f'Login result: {result}')

    browser.close()
"
```

#### 4. ❌ BROKEN: Reference Auth Example Path
**Current State**:
- SKILL.md references: `sample_data/reference_auth/poundwholesale_auth.py`
- File does not exist

**Required Fix**:
- Create reference implementations for each platform type
- Or remove reference and provide inline examples
- Add to docs/ folder with proper structure

#### 5. ⚠️ INCOMPLETE: Python Import Path Issue
**Current Issue**:
- Wizard generates: `from tools.dkwholesale-com.supplier_authentication_service import ...`
- Python doesn't allow hyphens in import paths
- Must rename directory to `dkwholesale_com`
- Fix import to: `from tools.dkwholesale_com.supplier_authentication_service import ...`

**Note**: Already fixed manually for dkwholesale.com, but needs to be fixed in wizard template.

#### 6. ⚠️ MISSING: Selector Verification Workflow
**Current State**:
- Validates selector syntax (CSS brackets)
- Doesn't validate selectors actually work on target site

**Required Addition**:
Add Step 5.B: "Verify Selectors with Chrome DevTools MCP"
```python
# Verify each selector finds elements:
# product_item = await page.query_selector('.card.card--card')
# title = await page.query_selector('h3')
# price = await page.query_selector('.product-price')
# ... etc
```

#### 7. ⚠️ MISSING: Error Handling & Debugging
**Current State**:
- Basic exception handling in template
- No screenshots on failure
- No detailed error logging

**Required Addition**:
Enhanced error handling with:
- Screenshots on auth failure (already added for dkwholesale.com)
- Detailed logging of which selector failed
- Retry logic with exponential backoff
- Clear error messages indicating next steps

## Recommended Skill Structure Update

### New Workflow: 8 Steps

0. **Initial Handshake & Information Gathering** (FRONT-LOADED)
   - Add: "Analyze website platform (Shopify/Magento/WooCommerce/Custom)"

1. **Data Preprocessing and Validation** (LLM MANUAL WORK)
   - ✅ Current: Categories validation
   - ✅ Current: Selectors validation
   - ✅ Current: JSON creation

2. **Prepare Configuration Files**
   - ✅ Current: Categories config
   - ✅ Current: Selectors config
   - ✅ Current: System config

3. **Invoke Wizard**
   - ✅ Current: Generate runner + auth helper

4. **Validate Generated Files** (MANDATORY)
   - ✅ Current: Runner validation
   - ✅ Current: Config validation
   - ✅ Current: Auth helper TEMPLATE check
   - ⚠️ IMPROVED: Flag auth helper as "MUST CUSTOMIZE" (not just warning)

5. **🆕 CUSTOMIZE AUTHENTICATION HELPER** (MANDATORY FOR AUTH=True)
   - **NEW**: Identify website platform
   - **NEW**: Select appropriate authentication pattern
   - **NEW**: Customize is_authenticated() with supplier-specific selectors
   - **NEW**: Customize login() with supplier-specific flow
   - **NEW**: Verify import paths (fix hyphen→underscore)
   - **NEW**: Syntax validation

6. **Pre-Run Verification**
   - ✅ Current: File verification
   - **NEW**: Test authentication in isolation
   - **NEW**: Verify selectors with real page
   - **NEW**: Check Chrome connectivity

7. **User Decision Point**
   - ✅ Current: Test run / Main run / Fix issues
   - **IMPROVED**: Add "Re-customize auth" option

## Specific Changes to SKILL.md

### Section 0: Add Platform Detection
```markdown
> 6. **Website Platform**: What e-commerce platform does the site use?
>     *   Options: Shopify, Magento, WooCommerce, Custom, Unknown
>     *   This determines authentication patterns and selector strategies
```

### Section 4.3: Enhance Auth Helper Validation
**Current** (lines 561-574):
```markdown
**⚠️ IMPORTANT**: Auth helper is a TEMPLATE requiring manual customization.
**Warn user**:
```

**Improved**:
```markdown
**🚨 CRITICAL: Auth Helper Customization Required**

The auth helper at `tools/{supplier-id}/supplier_authentication_service.py` is a **TEMPLATE**
and **MUST** be customized before use. This is **NOT OPTIONAL**.

**Why Customization is Mandatory**:
Each supplier website has unique:
- Login page URL structure
- Form field selectors
- Authentication indicators
- Session management patterns

**Generic templates will FAIL** - you MUST customize for this specific supplier.

**Required Customizations**:

1. **Update `is_authenticated()` Method**:
   - Analyze the supplier website's logged-in state
   - Look for authenticated-user elements:
     * Account dropdown/menu
     * Logout button/link
     * "My Account" link
     * User profile indicator
   - Replace generic selectors with supplier-specific ones
   - Test manually in browser console

2. **Update `login()` Method**:
   - Navigate to actual login page URL
   - Identify correct form field selectors:
     * Email/username field
     * Password field
     * Submit button
   - Fill form with credentials from parameter
   - Wait for proper redirection
   - Verify login success

3. **Test Authentication** (before full workflow):
   ```bash
   # Run this test script to verify auth works
   python -c "
   from playwright.sync_api import sync_playwright
   import sys
   sys.path.insert(0, '.')
   from tools.{supplier_id}.supplier_authentication_service import {ClassName}AuthenticationHelper

   with sync_playwright() as p:
       browser = p.chromium.launch(headless=False)
       page = browser.new_page()
       helper = {ClassName}AuthenticationHelper(page)

       # Test authentication check
       is_auth = helper.is_authenticated()
       print(f'Authenticated: {is_auth}')

       browser.close()
   "
   ```

**Reference Examples by Platform**:
- For Shopify sites: See docs/examples/auth/shopify_auth.md
- For Magento sites: See docs/examples/auth/magento_auth.md
- For WooCommerce sites: See docs/examples/auth/woocommerce_auth.md

**Common Authentication Patterns**:

**Shopify Sites** (e.g., dkwholesale.com):
```python
# Login URL: https://{domain}/account/login
# Email selector: #RecoverEmail
# Password selector: #CustomerPassword
# Auth indicators: a[href*="/account"], summary[aria-label*="Account"]
```

**Magento Sites**:
```python
# Login URL: https://{domain}/customer/account/login/
# Email selector: #email or input[name="login[username]"]
# Password selector: #pass or input[name="login[password]"]
# Auth indicators: a[href$="/customer/account/logout/"]
```

**WooCommerce Sites**:
```python
# Login URL: https://{domain}/my-account/
# Email selector: #username
# Password selector: #password
# Auth indicators: .woocommerce-MyAccount-navigation
```

**⚠️ WARNING**: If you skip this step, authentication will FAIL and the workflow will exit.
```

### New Section 5: Step-by-Step Auth Customization Guide
```markdown
---

## Step 5: 🆕 CUSTOMIZE AUTHENTICATION HELPER (MANDATORY FOR AUTH=True)

**🚨 CRITICAL**: This step is **REQUIRED** when `authentication_required=true`. Do not skip.

**Purpose**: Transform the generic auth helper template into supplier-specific working implementation.

**Timeline**: 10-30 minutes depending on supplier complexity

---

### 5.1. Identify Website Platform Architecture

Before customizing, determine the supplier's e-commerce platform:

**Method 1**: Check the website source code
```bash
# Look for platform indicators:
curl -s https://supplier.com | grep -i "shopify"    # Shopify sites
curl -s https://supplier.com | grep -i "magento"    # Magento sites
curl -s https://supplier.com | grep -i "woocommerce" # WooCommerce sites
```

**Method 2**: Analyze login page structure
- Shopify: `/account/login`, Shopify-specific CSS classes
- Magento: `/customer/account/login/`, Magento-specific classes
- WooCommerce: `/my-account/`, WooCommerce-specific markup

**Method 3**: Check cookies and scripts
- Shopify: `cart_currency`, `shopify_pay_redirect`
- Magento: `magento`, `form_key`
- WooCommerce: `woocommerce`, `wp_woocommerce`

**Platform Detection Table**:
| Platform | Login URL Pattern | Auth Indicator Selector | Form Structure |
|----------|------------------|------------------------|----------------|
| Shopify | `/account/login` | `a[href*="/account"]` | Email: #RecoverEmail, Password: #CustomerPassword |
| Magento | `/customer/account/login/` | `a[href$="/logout/"]` | Email: #email, Password: #pass |
| WooCommerce | `/my-account/` | `.woocommerce-MyAccount-navigation` | Email: #username, Password: #password |
| Custom | Varies | Varies | Requires manual analysis |

**Document the platform**: Add to wizard input JSON for future reference.

---

### 5.2. Customize is_authenticated() Method

**Location**: `tools/{supplier_id}/supplier_authentication_service.py`

**Action**: Replace the generic authentication check with supplier-specific logic.

**Process**:

1. **Visit supplier website in browser**
   - Open Chrome DevTools
   - Navigate to supplier homepage
   - Check if already logged in (look for account indicators)

2. **Identify authentication indicators** (when logged in):
   - Right-click on account menu/logout button
   - "Inspect" to see HTML/CSS selector
   - Test in Console: `document.querySelector('YOUR_SELECTOR')`
   - Should return element if authenticated, null if not

3. **Update the method**:
```python
async def is_authenticated(self) -> bool:
    """
    Check if user is already authenticated on SUPPLIER_NAME.

    SUPPLIER_NAME-specific authentication indicators:
    - AUTH_INDICATOR_1: DESCRIPTION
    - AUTH_INDICATOR_2: DESCRIPTION
    """
    try:
        await self.page.goto(self.supplier_url, wait_until="domcontentloaded", timeout=10000)

        # SUPPLIER_NAME authentication indicators
        # Found on actual site: SELECTOR_FOUND
        account_indicators = [
            'a[href*="/account"]',  # My Account link
            'SELECTOR_FOUND_FROM_INSPECTION',  # Description
        ]

        for selector in account_indicators:
            element = await self.page.query_selector(selector)
            if element:
                log.info(f"✅ User is authenticated (found: {selector})")
                return True

        log.info("❌ User is not authenticated")
        return False

    except Exception as e:
        log.warning(f"Authentication check failed: {e}")
        # Take screenshot for debugging
        await self.page.screenshot(path=f"OUTPUTS/{supplier_name}_auth_check_failed.png")
        return False
```

**Example for dkwholesale.com** (Shopify):
```python
async def is_authenticated(self) -> bool:
    try:
        await self.page.goto(self.supplier_url, wait_until="domcontentloaded", timeout=10000)

        # Dkwholesale.com uses Shopify - account link appears when logged in
        account_indicators = [
            'a[href*="/account"]',
            'summary[aria-label*="Account"]',
        ]

        for selector in account_indicators:
            element = await self.page.query_selector(selector)
            if element:
                log.info(f"✅ User is authenticated (found: {selector})")
                return True

        log.info("❌ User is not authenticated")
        return False

    except Exception as e:
        log.warning(f"Authentication check failed: {e}")
        return False
```

---

### 5.3. Customize login() Method

**Location**: Same file, `login()` method

**Action**: Implement actual login flow using verified selectors.

**Process**:

1. **Navigate to login page**
   - Visit supplier login URL in browser
   - Identify form field selectors:
     * Email field: Right-click → Inspect → Test selector
     * Password field: Same process
     * Submit button: Same process

2. **Test form filling** (in browser console):
```javascript
// Test email field
document.querySelector('#email').value = 'test@example.com'

// Test password field
document.querySelector('#password').value = 'test123'

// Test submit button click
document.querySelector('button[type="submit"]').click()
```

3. **Update the method**:
```python
async def login(self, credentials: dict) -> bool:
    """
    Perform login on SUPPLIER_NAME using provided credentials.

    Login flow based on actual site structure:
    1. Navigate to LOGIN_URL
    2. Fill email field: EMAIL_SELECTOR
    3. Fill password field: PASSWORD_SELECTOR
    4. Click submit: SUBMIT_SELECTOR
    5. Verify success
    """
    try:
        username = credentials.get('username')
        password = credentials.get('password')

        if not username or not password:
            log.error("Missing username or password in credentials")
            return False

        login_url = "ACTUAL_LOGIN_URL_FOUND"
        log.info(f"Navigating to {login_url}...")
        await self.page.goto(login_url, wait_until="domcontentloaded")

        log.info("Filling login form...")
        log.info(f"  → Username: {username}")
        await self.page.fill('EMAIL_SELECTOR', username)

        log.info("  → Password: [REDACTED]")
        await self.page.fill('PASSWORD_SELECTOR', password)

        log.info("  → Clicking login button")
        await self.page.click('SUBMIT_SELECTOR')

        log.info("  → Waiting for authentication...")
        await self.page.wait_for_timeout(3000)  # Allow redirect

        # Verify success
        if await self.is_authenticated():
            log.info("✅ Login successful")
            return True

        log.error("❌ Login failed - authentication check returned False")
        # Screenshot for debugging
        screenshot_path = f"OUTPUTS/{supplier_name}_login_failed.png"
        await self.page.screenshot(path=screenshot_path)
        log.error(f"📸 Screenshot saved: {screenshot_path}")
        return False

    except Exception as e:
        log.error(f"Login failed: {e}")
        screenshot_path = f"OUTPUTS/{supplier_name}_login_error.png"
        await self.page.screenshot(path=screenshot_path)
        log.error(f"📸 Error screenshot: {screenshot_path}")
        return False
```

**Example for dkwholesale.com** (Shopify):
```python
async def login(self, credentials: dict) -> bool:
    try:
        username = credentials.get('username')
        password = credentials.get('password')

        login_url = "https://dkwholesale.com/account/login"
        await self.page.goto(login_url, wait_until="domcontentloaded")

        await self.page.fill('#RecoverEmail', username)
        await self.page.fill('#CustomerPassword', password)
        await self.page.click('button[type="submit"]')
        await self.page.wait_for_timeout(3000)

        if await self.is_authenticated():
            log.info("✅ Login successful")
            return True

        log.error("❌ Login failed")
        return False

    except Exception as e:
        log.error(f"Login failed: {e}")
        return False
```

---

### 5.4. Test Authentication in Isolation

**Before running full workflow**, test authentication separately:

**Test Script**:
```bash
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

python -c "
import asyncio
import sys
sys.path.insert(0, '.')
from playwright.async_api import async_playwright
from tools.dkwholesale_com.supplier_authentication_service import DkwholesaleAuthenticationHelper

async def test_auth():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        helper = DkwholesaleAuthenticationHelper(page)

        # Test authentication check
        print('Testing is_authenticated()...')
        is_auth = await helper.is_authenticated()
        print(f'Result: {is_auth}')

        if not is_auth:
            print('Testing login()...')
            credentials = {
                'username': 'info@theblacksmithmarket.com',
                'password': '0Dqixm9c&'
            }
            result = await helper.login(credentials)
            print(f'Login result: {result}')

        await browser.close()

asyncio.run(test_auth())
"
```

**Expected Output**:
```
Testing is_authenticated()...
Result: True  # Or False if not logged in

# If False:
Testing login()...
Filling login form...
  → Username: info@theblacksmithmarket.com
  → Password: [REDACTED]
  → Clicking login button
  → Waiting for authentication...
✅ Login successful
Login result: True
```

**Troubleshooting**:
- If authentication check fails: Update selectors in `is_authenticated()`
- If login fails: Verify login URL, form selectors, and button selector
- If timeout errors: Increase wait times or check network speed
- Always check screenshots in OUTPUTS/ folder for visual debugging

---

### 5.5. Verify Selector Accuracy

Authentication is just one part - verify product selectors too:

**Test Script**:
```bash
python -c "
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Navigate to a product category
    page.goto('https://dkwholesale.com/collections/advanced-accessories')

    # Test each selector
    product_item = page.query_selector('.card.card--card')
    print(f'Product item found: {product_item is not None}')

    if product_item:
        title = product_item.query_selector('h3')
        price = product_item.query_selector('.product-price')
        print(f'Title: {title.inner_text() if title else \"NOT FOUND\"}')
        print(f'Price: {price.inner_text() if price else \"NOT FOUND\"}')

    browser.close()
"
```

**If selectors fail**:
1. Return to Step 1 and re-inspect the page
2. Update `config/supplier_configs/{domain}.json`
3. Re-test until all selectors work

---

### 5.6. Python Import Path Verification

**Check**: Ensure auth helper can be imported correctly.

**Problem**: Python doesn't allow hyphens in module names.
- ❌ WRONG: `from tools.dkwholesale-com.supplier_authentication_service import ...`
- ✅ CORRECT: `from tools.dkwholesale_com.supplier_authentication_service import ...`

**Action**:
1. Verify directory name uses underscore: `tools/dkwholesale_com/`
2. Verify import in runner script uses underscore
3. Test import:
```bash
python -c "from tools.dkwholesale_com.supplier_authentication_service import DkwholesaleAuthenticationHelper; print('Import successful')"
```

**If import fails**:
- Rename directory from `dkwholesale-com` to `dkwholesale_com`
- Update import in `run_custom_dkwholesale-com.py`
- Re-test import

---

## Step 5 Completion Criteria

Before proceeding to Step 6, confirm:

- [ ] `is_authenticated()` method customized with supplier-specific selectors
- [ ] `login()` method customized with supplier-specific flow
- [ ] Authentication test script runs successfully
- [ ] is_authenticated() returns True when logged in
- [ ] login() successfully authenticates when not logged in
- [ ] Python import path uses underscores (not hyphens)
- [ ] Selectors verified on actual product pages
- [ ] Screenshots saved to OUTPUTS/ if authentication fails

**If ANY check fails**: Return to appropriate sub-step in Step 5 and fix.

---

## Step 6: Pre-Run Verification (IMPROVED)

**Now includes authentication testing as prerequisite**:

### 6.1. Document Authentication Test Results
```markdown
Authentication Test Results:
- is_authenticated() test: ✅ PASSED / ❌ FAILED
- login() test: ✅ PASSED / ❌ FAILED (if applicable)
- Screenshots captured: YES / NO
- Final auth status: AUTHENTICATED / NOT_AUTHENICATED
```

### 6.2. Verify Authentication State
- [ ] Auth helper properly customized (not using template)
- [ ] Test results documented
- [ ] Screenshots saved (if failures occurred)
- [ ] Final auth status confirmed

**Then continue with existing verification steps**:
- [ ] Runner script structure valid
- [ ] Configuration files accurate
- [ ] System readiness confirmed
```

## Other Improvements Needed (Not Authentication-Related)

### A. Fix Wizard Import Path Generation
**File**: `templates/auth_helper_template.py.txt` and wizard code
**Issue**: Generates `tools.dkwholesale-com` (invalid Python import)
**Fix**: Generate `tools.dkwholesale_com` and correct import

### B. Create Missing Reference Files
**Files**:
- `sample_data/reference_auth/shopify_auth.md`
- `sample_data/reference_auth/magento_auth.md`
- `sample_data/reference_auth/woocommerce_auth.md`
- `docs/examples/auth/shopify_auth.md`
- `docs/examples/auth/magento_auth.md`
- `docs/examples/auth/woocommerce_auth.md`

### C. Add Platform Detection to Wizard
**Enhancement**: Automatically detect platform during Step 0
- Check response headers
- Analyze HTML/JS artifacts
- Suggest appropriate auth pattern

### D. Enhance Error Messages in Auth Helper Template
**Current**: Generic "Login failed: {e}"
**Improved**: Specific guidance on what to check

### E. Add Context7 MCP Integration for Documentation
**Use Context7** to get Claude Code skills best practices and integrate them

## Summary

### Critical (Must Fix)
1. ✅ Create new Step 5: Customize Authentication Helper (MANDATORY)
2. ✅ Add supplier-specific authentication patterns
3. ✅ Include authentication testing protocol
4. ✅ Fix wizard import path generation
5. ✅ Create missing reference files
6. ⚠️ Update skill documentation with new Step 5
7. ⚠️ Test entire workflow end-to-end

### Recommended (Should Add)
1. Platform auto-detection in wizard
2. Enhanced error messages
3. Better debugging (screenshots already added)
4. Context7 MCP integration for Claude Code best practices

### Nice to Have
1. Auth helper validation script
2. Automated selector testing
3. Platform-specific templates
4. Video tutorial links

---

**Next Actions**:
1. Create new Step 5 section in SKILL.md
2. Move auth customization from warning to mandatory step
3. Add supplier-specific examples
4. Fix wizard template for import paths
5. Create reference auth examples
6. Test complete workflow with dkwholesale.com
7. Update summary section with new 8-step workflow

