# General New Supplier Integration Guide
**Version**: 1.1 (Corrected)
**Date**: September 29, 2025
**Based on**: Clearance-king.co.uk integration experience
**System**: Amazon FBA Agent System v3.7+

## 🎯 Purpose

This guide provides a complete step-by-step walkthrough for integrating new suppliers into the Amazon FBA Agent System. The process is based on actual implementation experience and focuses on practical, tested procedures.

## ⚠️ Prerequisites

### Required Knowledge
- Basic understanding of Python async/await patterns
- Familiarity with Playwright browser automation
- Understanding of JSON configuration files
- Basic command line usage

### System Requirements
- Chrome browser with debug port capability
- Python 3.8+ with required dependencies
- Sufficient disk space for product caches (1GB+ recommended)
- Stable internet connection for supplier authentication

### Existing System Status
- Existing supplier systems (e.g., poundwholesale.co.uk) must be functioning
- Amazon extraction components must be operational
- Browser automation infrastructure must be stable

## 🚀 Phase 1: Pre-Integration Analysis

### Step 1.1: Supplier Website Analysis
Before starting integration, analyze the target supplier website:

**Document the following:**
- Supplier URL: `https://www.{supplier}.com`
- Authentication method: Login form, OAuth, etc.
- Category structure: How products are organized
- Product data format: What information is available
- Anti-bot measures: Rate limits, CAPTCHA, etc.
- Product URL patterns
- Pricing display format
- EAN/SKU availability

### Step 1.2: Credential Preparation
Obtain valid credentials for the supplier:
- Username/email
- Password
- Any additional authentication tokens
- **Test credentials manually in browser first**

### Step 1.3: Category URL Collection
Create a list of category URLs to scrape:
- Identify all product categories
- Document category URLs
- Estimate total product count per category
- Plan processing order (start with smaller categories for testing)

## 🏗️ Phase 2: Infrastructure Setup

### Step 2.1: Core Script Duplication
Create supplier-specific versions of core scripts:

```bash
# 1. Create supplier directory
mkdir tools/{supplier_name}

# 2. Copy core workflow script
cp passive_extraction_workflow_latest.py tools/{supplier_name}/passive_extraction_workflow_{supplier_name}.py

# 3. Copy supplier scraper
cp tools/configurable_supplier_scraper.py tools/{supplier_name}/configurable_supplier_scraper_{supplier_name}.py

# 4. Create entry point
cp run_custom_poundwholesale.py run_custom_{supplier_name}.py
```

**⚠️ DO NOT copy circuit breaker dependencies - they are intentionally disabled**

### Step 2.2: Entry Point Configuration
Edit `run_custom_{supplier_name}.py`:

```python
# Update these key lines:
supplier_name = "{supplier_name}.com"  # Line ~15
config_key = "{supplier_name}_workflow"  # Line ~20

# Import supplier-specific modules
from tools.{supplier_name}.passive_extraction_workflow_{supplier_name} import PassiveExtractionWorkflow
```

### Step 2.3: Workflow Script Parameterization
Edit `tools/{supplier_name}/passive_extraction_workflow_{supplier_name}.py`:

**Critical Lines to Update**:
- Line ~1834: Category config path
- Line ~7334: Manifest path
- Line ~11727: Supplier URL
- Line ~11732: Supplier name
- All credential reference keys

```python
# Example updates:
# Line 1834: Category config path
category_config_path = f"config/{supplier_name}_categories.json"

# Line 7334: Manifest path
manifest_path = f"OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/"

# Line 11727: Supplier URL
supplier_url = f"https://www.{supplier_name}.com"

# Line 11732: Supplier name
supplier_name = f"{supplier_name}.com"
```

### Step 2.5: Authentication Verification Parameters (Update Test Product URL)
To validate login deterministically, the standalone login helper verifies that a real product page shows a numeric price (not text like “Login to view price”). Update these parameters for the new supplier:

- File: `tools/standalone_playwright_login.py`
- What to change:
  - `self.base_url` to the supplier’s base URL.
  - The test product path used for price verification to a known product that requires login to see prices.

Example (values to replace):
```python
# tools/standalone_playwright_login.py
# Set supplier base URL
self.base_url = "https://www.<supplier-domain>"
self.login_url = f"{self.base_url}/customer/account/login/"

# Use a real, stable product URL on the same supplier for price check
# (This product must show a numeric price only after authentication)
test_product = f"{self.base_url}/<path-to-known-product>"
```

Price verification criterion (accept/reject):
- Accept if a visible price element contains a currency symbol (e.g., `£`) and numeric digits.
- Reject if extracted text contains non-price prompts (e.g., “login”, “sign in”, “login to view price”).

Notes
- The login verifier iterates multiple price selectors; it returns success on the first visible, numeric price it finds. Keep the test product consistent to avoid flakiness.
- If the supplier exposes prices without login, use a different indicator (e.g., account menu selector) in addition to the price check.

### Step 2.4: Configuration Files Setup

**A. System Configuration**
Add to `config/system_config.json`:

```json
{
  "{supplier_name}.com": {
    "username": "your_username",
    "password": "your_password"
  },
  "{supplier_name}_workflow": {
    "supplier_name": "{supplier_name}.com",
    "supplier_url": "https://www.{supplier_name}.com",
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  }
}
```

**B. Category Configuration**
Create `config/{supplier_name}_categories.json`:

```json
{
  "categories": [
    {
      "name": "Category 1",
      "url": "https://www.{supplier_name}.com/category1"
    },
    {
      "name": "Category 2",
      "url": "https://www.{supplier_name}.com/category2"
    }
  ]
}
```

## 🔧 Phase 3: Authentication Service Implementation

### Step 3.1: Authentication Service Creation
Create `tools/{supplier_name}/supplier_authentication_service.py`:

```python
from playwright.async_api import Page
from typing import Dict
import asyncio

class SupplierAuthenticationService:
    def __init__(self, page: Page):
        self.page = page

    async def ensure_authenticated_session(self, page: Page, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with supplier website
        Returns True if authentication successful
        """
        try:
            # Navigate to login page
            await page.goto(f"https://www.{supplier_name}.com/login")

            # Fill login form (customize selectors)
            await page.fill('input[name="username"]', credentials["username"])
            await page.fill('input[name="password"]', credentials["password"])

            # Submit login
            await page.click('button[type="submit"]')

            # Wait for authentication confirmation
            await page.wait_for_selector('.user-dashboard', timeout=30000)

            return True

        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
```

### Step 3.2: Dependency Management
**⚠️ IMPORTANT**: Do NOT copy circuit breaker dependencies
- Circuit breaker is intentionally disabled in the system
- Only copy absolutely necessary dependencies
- Avoid creating `utils/{supplier_name}` directories unless specifically required

## 🧪 Phase 4: Testing and Verification

### Step 4.1: Initial Connection Test
Test basic connectivity:

```bash
# Run entry point script
python run_custom_{supplier_name}.py

# Expected outputs:
# 1. Authentication success message
# 2. Category loading confirmation
# 3. At least 1 product extraction
```

### Step 4.2: Critical Error Resolution

**Common Error Patterns**:

**Error 1: File Corruption**
```
Symptom: SyntaxError when importing modules
Solution: Verify all .py files contain Python code, not JSON
Action: Re-copy from source if corrupted
```

**Error 2: Method Signature Mismatch**
```
Symptom: "takes X arguments but Y were given"
Solution: Update method signatures to match calling code
Action: Check constructor parameters and method calls
```

**Error 3: Configuration Format Issues**
```
Symptom: KeyError when loading categories
Solution: Support multiple configuration formats
Action: Add flexible parsing logic
```

### Step 4.3: Output Verification
Verify all expected files are created:

```bash
# Check product cache
ls -la "OUTPUTS/cached_products/{supplier_name}_products_cache.json"

# Check processing state
ls -la "OUTPUTS/CACHE/processing_states/{supplier_name}_processing_state.json"

# Check Amazon cache files
ls -la "OUTPUTS/FBA_ANALYSIS/amazon_cache/" | head -10

# Check debug logs
ls -la "logs/debug/run_custom_poundwholesale_*.log" | tail -1

# Check linking map directory and file (created automatically if missing)
ls -la "OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/"
ls -la "OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/linking_map.json"
```

Linking map generation details
- The workflow writes the linking map via a centralized path (`utils.path_manager.get_linking_map_path`).
- Parent directories are created automatically if they don’t exist (Windows-safe atomic save via `utils/windows_save_guardian.py`, which calls `path.parent.mkdir(parents=True, exist_ok=True)` before writing).
- The `linking_map.json` file is created on first save as soon as at least one linking entry is generated.

### Step 4.4: System Isolation Verification
Ensure existing systems are unaffected:

```bash
# Check poundwholesale files haven't changed
ls -la "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"

# Verify timestamps are unchanged
stat "OUTPUTS/CACHE/processing_states/poundwholesale-co-uk_processing_state.json"
```

## 🚨 Critical Success Factors

### 1. File Integrity Verification
Always verify that copied files contain expected content:
```bash
# Check first few lines of Python files
head -5 tools/{supplier_name}/supplier_authentication_service.py
# Should show Python imports, not JSON data
```

### 2. Method Signature Consistency
Always verify method signatures match usage:
- Check constructor parameters match initialization code
- Verify async method signatures are consistent
- Test all method calls have correct parameter counts

### 3. Configuration Format Flexibility
Build robust configuration parsers:
- Support multiple JSON structures
- Provide clear error messages for invalid configs
- Default to safe fallback values when possible

### 4. Authentication Validation
Test authentication independently:
- Verify credentials work in browser first
- Test authentication service in isolation
- Monitor authentication success rates in production

## 📋 Troubleshooting Checklist

### Pre-Flight Checklist
- [ ] Supplier credentials tested manually in browser
- [ ] All required files copied to supplier directories
- [ ] Configuration files created with correct format
- [ ] Import paths updated in all modules
- [ ] Entry point script configured for new supplier

### Runtime Verification
- [ ] Authentication succeeds on first attempt
- [ ] Categories load without errors
- [ ] At least 1 product extracts successfully
- [ ] Output files created in expected locations
- [ ] Processing state updates correctly

### Post-Integration Validation
- [ ] No impact on existing supplier systems
- [ ] All expected output files contain valid data
- [ ] System can resume from interruption
- [ ] Performance metrics meet expectations
- [ ] Error rates within acceptable limits

## 🎯 Success Metrics

A successful integration should achieve:

- **Authentication Success**: 100% on first attempt
- **Product Extraction**: At least 1 product extracted
- **Output Files**: All expected files created with valid data
- **System Isolation**: Zero impact on existing suppliers
- **Performance**: 3-5 products extracted per minute
- **Resumability**: System can restart and continue from interruption

## 🔄 Maintenance and Updates

### Regular Monitoring
- Check authentication success rates weekly
- Monitor product extraction rates
- Verify output file integrity
- Watch for supplier website changes

### Update Procedures
- Test authentication changes in staging first
- Update category configurations quarterly
- Monitor for new anti-bot measures
- Keep documentation synchronized with changes

---

**Generated**: September 29, 2025
**Based on**: Clearance-King integration experience (1 product successfully extracted)
**Next Update**: Upon completion of next supplier integration
**Contact**: Amazon FBA Agent System Team
