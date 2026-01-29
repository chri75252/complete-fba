# File Specifications

Complete specifications for all files generated during supplier onboarding.

---

## Runner Script (run_custom_{supplier-id}.py)

### Basic Requirements

**File Name Pattern**: `run_custom_{supplier-id}.py` (hyphen-form)
- ✅ Example: `run_custom_angelwholesale-co-uk.py`
- ❌ Wrong: `run_custom_angelwholesale.co.uk.py`

**File Length**: 117-143 lines
- **Without Authentication**: ~117 lines
- **With Authentication**: ~143 lines
- **NEVER**: 26 lines (this indicates a shim, not full implementation)

**Encoding**: UTF-8
**Line Endings**: LF (Unix-style) preferred, CRLF (Windows) acceptable

---

### Required Imports

**Core Imports** (MUST be present):
```python
import asyncio
import logging
import sys
import os
from playwright.async_api import async_playwright
from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from utils.logger import setup_logger
from utils.browser_manager import BrowserManager
```

**Path Configuration**:
```python
# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

**Windows Console Configuration**:
```python
# Ensure Windows consoles can render Unicode
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
```

**Import Hygiene Validation** (recommended):
```python
# Validate correct module is imported
import inspect
workflow_module_path = inspect.getfile(PassiveExtractionWorkflow)
expected_path_suffix = os.path.join("tools", "passive_extraction_workflow_latest.py")
if not workflow_module_path.endswith(expected_path_suffix.replace(os.sep, "/")):
    print(f"WARNING: PassiveExtractionWorkflow imported from unexpected path: {workflow_module_path}")
```

**Authentication Import** (if auth required):
```python
from tools.{supplier-id}.supplier_authentication_service import {ClassName}AuthenticationHelper
```
- Example: `from tools.angelwholesale-co-uk.supplier_authentication_service import AngelwholesaleCoUkAuthenticationHelper`

---

### Main Function Structure

**Function Signature**:
```python
async def main():
    """Main function to run the custom extraction workflow."""
```

**Platform Detection**:
```python
import platform
system_platform = platform.system()

if system_platform == "Windows":
    print("🪟 --- Starting Custom {Supplier} Extraction Workflow (Windows Native) ---")
    print("✅ Running on Windows - Enhanced memory management enabled")
else:
    print("--- Starting Custom {Supplier} Extraction Workflow (Linux/WSL) ---")
    print("Running on Linux/WSL - Standard memory management")

print(f"Platform: {system_platform}")
print(f"Python: {platform.python_version()}")
```

**Configuration Loading**:
```python
config_loader = SystemConfigLoader()
workflow_config = config_loader.get_workflow_config('{workflow_key}')  # CRITICAL: Correct workflow_key
supplier_name = workflow_config.get('supplier_name', '{domain}')
credentials = config_loader.get_credentials(supplier_name)
chrome_debug_port = config_loader.get_system_config().get('chrome_debug_port', 9222)
```

**Logger Setup** (supplier-aware):
```python
debug_log_file = setup_logger(supplier_name=supplier_name)
log = logging.getLogger(__name__)
log.info(f"📋 Debug log file: {debug_log_file}")
```

**Expected Debug Log Filename**:
- `logs/debug/run_custom_{supplier-id}_YYYYMMDD_HHMMSS.log`

**Browser Manager Setup**:
```python
browser_manager = None
try:
    browser_manager = BrowserManager.get_instance()
    await browser_manager.launch_browser(cdp_port=chrome_debug_port)
    page = await browser_manager.get_page()

    supplier_url = workflow_config.get('supplier_url', f"https://{supplier_name}")
```

**Authentication Logic** (if required):
```python
log.info(f"🔐 Initializing {supplier_name} authentication helper...")
auth_helper = {ClassName}AuthenticationHelper(page)

if not credentials:
    log.error(f"🚨 Credentials for {supplier_name} not found in config. Exiting.")
    return

is_authenticated = await auth_helper.is_authenticated()
if not is_authenticated:
    log.info(f"🔑 User not authenticated. Attempting login...")
    login_success = await auth_helper.login(credentials)

    if not login_success:
        log.error(f"❌ Login failed for {supplier_name}. Cannot proceed.")
        return

    log.info(f"✅ Successfully logged in to {supplier_name}")
else:
    log.info(f"✅ User is already authenticated on {supplier_name}")
```

**Workflow Execution**:
```python
workflow = PassiveExtractionWorkflow(
    config_loader=config_loader,
    workflow_key='{workflow_key}',  # CRITICAL: Correct workflow_key
    workflow_config=workflow_config,
    browser_manager=browser_manager
)

log.info(f"🚀 Starting workflow for {supplier_name}...")
await workflow.run()
log.info("✅ Workflow completed successfully")
```

**Exception Handling**:
```python
except KeyboardInterrupt:
    log.warning("⚠️ Workflow interrupted by user")
except Exception as e:
    log.error(f"❌ Workflow failed: {e}", exc_info=True)
    raise
finally:
    if browser_manager:
        await browser_manager.close()
        log.info("🔒 Browser manager closed")
```

**Entry Point**:
```python
if __name__ == "__main__":
    asyncio.run(main())
```

---

### Critical Lines to Verify

When validating a runner script, these lines are **CRITICAL**:

**1. Workflow Key (Line ~58-60)**:
```python
workflow_config = config_loader.get_workflow_config('{workflow_key}')
```
- ✅ Must match the supplier's workflow key
- ❌ Must NOT reference another supplier (e.g., 'poundwholesale_workflow')

**2. Workflow Instantiation (Line ~85-90)**:
```python
workflow = PassiveExtractionWorkflow(
    config_loader=config_loader,
    workflow_key='{workflow_key}',  # CRITICAL: Must be correct
    workflow_config=workflow_config,
    browser_manager=browser_manager
)
```

**3. Authentication Import** (if applicable):
```python
from tools.{supplier-id}.supplier_authentication_service import {ClassName}AuthenticationHelper
```
- Must use hyphen-form for supplier-id
- Must use PascalCase for ClassName

---

## Categories Configuration

### File Specification

**File Name Pattern**: `config/{workflow_key}_categories.json`
- Example: `config/angelwholesale_workflow_categories.json`
- Uses underscore-form workflow key

**Format**: JSON
**Encoding**: UTF-8

### Required Structure

```json
{
  "category_urls": [
    "https://supplier.com/category1",
    "https://supplier.com/category2"
  ]
}
```

**Field Requirements**:
- `category_urls` (array, required): List of category page URLs
  - Each URL must be complete (include protocol: `https://`)
  - Each URL must belong to the supplier's domain
  - No duplicate URLs allowed
  - Minimum 1 URL, typical range: 10-500 URLs

### Validation Checks

```python
import json

with open('config/angelwholesale_workflow_categories.json') as f:
    data = json.load(f)

# Check structure
assert 'category_urls' in data
assert isinstance(data['category_urls'], list)
assert len(data['category_urls']) > 0

# Check URLs
for url in data['category_urls']:
    assert url.startswith('http')
    assert 'angelwholesale.co.uk' in url  # Domain match
```

---

## Selector Configuration

### File Specification

**File Name Pattern**: `config/supplier_configs/{domain}.json` (dot-form!)
- ✅ Example: `config/supplier_configs/angelwholesale.co.uk.json`
- ❌ Wrong: `config/supplier_configs/angelwholesale-co-uk.json`

**Format**: JSON
**Encoding**: UTF-8

### Required Structure

```json
{
  "supplier_url": "https://supplier.com",
  "product_card_selector": "article.product",
  "title_selector": "h3.product-title",
  "price_selector": ".price",
  "url_selector": "a.product-link",
  "next_page_selector": "a.next-page",
  "ean_selector": ".ean-code",
  "image_selector": "img.product-image",
  "out_of_stock_selector": ".out-of-stock",
  "authentication_required": false
}
```

### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `supplier_url` | string | Yes | Full supplier URL (with protocol) |
| `product_card_selector` | string | Yes | CSS selector for product container |
| `title_selector` | string | Yes | CSS selector for product title |
| `price_selector` | string | Yes | CSS selector for product price |
| `url_selector` | string | Yes | CSS selector for product URL |
| `next_page_selector` | string | Yes | CSS selector for pagination |
| `ean_selector` | string | Yes | CSS selector for EAN/barcode |
| `image_selector` | string | Yes | CSS selector for product image |
| `out_of_stock_selector` | string | Yes | CSS selector for stock status |
| `authentication_required` | boolean | Yes | Whether login is required |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `variant_selector` | string | Selector for product variants |
| `description_selector` | string | Selector for product description |
| `category_selector` | string | Selector for product category |

### Validation Checks

```python
import json

with open('config/supplier_configs/angelwholesale.co.uk.json') as f:
    data = json.load(f)

# Required fields
required_fields = [
    'supplier_url',
    'product_card_selector',
    'title_selector',
    'price_selector',
    'url_selector',
    'next_page_selector',
    'ean_selector',
    'image_selector',
    'out_of_stock_selector',
    'authentication_required'
]

for field in required_fields:
    assert field in data, f"Missing required field: {field}"
    assert data[field] is not None and data[field] != "", f"Field {field} is empty"

# Type checks
assert isinstance(data['authentication_required'], bool)
assert data['supplier_url'].startswith('http')
```

---

## System Configuration Update

### File Location

**File**: `config/system_config.json`

### Workflow Entry Structure

**Location in JSON**: `workflows.{workflow_key}`

**Example**:
```json
{
  "workflows": {
    "angelwholesale_workflow": {
      "supplier_name": "angelwholesale.co.uk",
      "supplier_url": "https://angelwholesale.co.uk",
      "categories_config_path": "config/angelwholesale_workflow_categories.json",
      "use_predefined_categories": true,
      "ai_client": null,
      "authentication_required": false
    }
  }
}
```

### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `supplier_name` | string | Yes | Supplier domain (dot-form) |
| `supplier_url` | string | Yes | Full supplier URL |
| `categories_config_path` | string | Yes | Path to categories JSON |
| `use_predefined_categories` | boolean | Yes | Always true for onboarded suppliers |
| `ai_client` | null | Yes | Always null (AI disabled) |
| `authentication_required` | boolean | Yes | Whether login required |

### Validation Checks

```python
import json

with open('config/system_config.json') as f:
    config = json.load(f)

workflow_key = 'angelwholesale_workflow'
assert workflow_key in config['workflows']

workflow = config['workflows'][workflow_key]
assert workflow['supplier_name'] == 'angelwholesale.co.uk'  # Dot-form
assert workflow['supplier_url'].startswith('http')
assert workflow['use_predefined_categories'] == True
assert workflow['ai_client'] is None
assert isinstance(workflow['authentication_required'], bool)
```

---

## Authentication Helper (If Required)

### File Specification

**File Location**: `tools/{supplier-id}/supplier_authentication_service.py` (hyphen-form)
- Example: `tools/angelwholesale-co-uk/supplier_authentication_service.py`

**Directory Structure**:
```
tools/
└── angelwholesale-co-uk/
    ├── __init__.py
    └── supplier_authentication_service.py
```

**Format**: Python
**Encoding**: UTF-8

### Required Structure

```python
"""
Authentication helper for {supplier_name}
Auto-generated by supplier_onboarding_wizard.py

⚠️ THIS IS A TEMPLATE - REQUIRES MANUAL CUSTOMIZATION
"""
import logging
from playwright.async_api import Page

log = logging.getLogger(__name__)

class {ClassName}AuthenticationHelper:
    """Authentication helper for {supplier_display_name}."""

    def __init__(self, page: Page):
        self.page = page
        self.supplier_url = "{supplier_url}"

    async def is_authenticated(self) -> bool:
        """
        Check if user is already authenticated.

        TODO: Customize this method based on supplier's authentication indicators.
        """
        try:
            await self.page.goto(self.supplier_url, wait_until="domcontentloaded", timeout=10000)

            # TODO: Replace with actual authentication check
            logout_button = await self.page.query_selector('a[href*="logout"]')
            if logout_button:
                log.info("✅ User is authenticated")
                return True

            log.info("❌ User is not authenticated")
            return False

        except Exception as e:
            log.warning(f"Authentication check failed: {e}")
            return False

    async def login(self, credentials: dict) -> bool:
        """
        Perform login using provided credentials.

        TODO: Customize this method based on supplier's login flow.
        """
        try:
            username = credentials.get('username')
            password = credentials.get('password')

            if not username or not password:
                log.error("Missing username or password")
                return False

            log.info(f"Navigating to {self.supplier_url} for login...")
            await self.page.goto(self.supplier_url, wait_until="domcontentloaded")

            # TODO: Replace with actual login selectors
            log.error("⚠️ Login method not implemented - please customize auth helper")
            return False

        except Exception as e:
            log.error(f"Login failed: {e}")
            return False
```

### Class Name Convention

**Pattern**: `{CapitalizedSupplierName}AuthenticationHelper`

**Conversion**:
```
angelwholesale.co.uk → AngelwholesaleCoUkAuthenticationHelper
poundwholesale.co.uk → PoundwholesaleCoUkAuthenticationHelper
clearance-king.co.uk → ClearanceKingCoUkAuthenticationHelper
```

### TODO Comments

**EXPECTED**: Auth helper should contain TODO comments indicating manual customization required:
```python
# TODO: Customize based on supplier's auth indicators
# TODO: Customize based on supplier's login flow
```

**These are NOT errors** - they indicate template status.

### Validation Checks

```python
import ast
import os

# Check directory exists
assert os.path.exists('tools/angelwholesale-co-uk/')
assert os.path.exists('tools/angelwholesale-co-uk/__init__.py')
assert os.path.exists('tools/angelwholesale-co-uk/supplier_authentication_service.py')

# Check class name
with open('tools/angelwholesale-co-uk/supplier_authentication_service.py') as f:
    content = f.read()
    assert 'class AngelwholesaleCoUkAuthenticationHelper:' in content
    assert 'async def is_authenticated(self) -> bool:' in content
    assert 'async def login(self, credentials: dict) -> bool:' in content
    assert 'TODO' in content  # Template markers present
```

---

## Summary Checklist

When validating all generated files:

### Runner Script
- [ ] File name uses hyphen-form: `run_custom_{supplier-id}.py`
- [ ] File is 117-143 lines (NOT 26 lines)
- [ ] All required imports present
- [ ] Correct workflow_key referenced (2 places)
- [ ] Authentication import present (if auth required)
- [ ] Main function structure correct
- [ ] Entry point present: `asyncio.run(main())`

### Categories Configuration
- [ ] File name uses workflow_key: `{workflow_key}_categories.json`
- [ ] JSON structure correct: `{"category_urls": [...]}`
- [ ] All URLs complete and valid
- [ ] URLs belong to correct supplier domain

### Selector Configuration
- [ ] File name uses dot-form: `{domain}.json`
- [ ] All 10 required fields present
- [ ] No empty values
- [ ] `authentication_required` boolean correct

### System Configuration
- [ ] Workflow entry exists: `workflows.{workflow_key}`
- [ ] `supplier_name` uses dot-form
- [ ] `supplier_url` complete and valid
- [ ] All required fields present

### Authentication Helper (if applicable)
- [ ] Directory uses hyphen-form: `tools/{supplier-id}/`
- [ ] `__init__.py` present
- [ ] `supplier_authentication_service.py` present
- [ ] Class name correct (PascalCase)
- [ ] Both methods present: `is_authenticated()`, `login()`
- [ ] TODO comments present (expected for template)

---

**End of FILE_SPECIFICATIONS.md**
