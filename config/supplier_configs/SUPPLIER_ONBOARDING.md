# Supplier Onboarding Skill

**Location:** `.claude/skills/supplier-onboarding/`

## Overview

The supplier onboarding skill provides a guided workflow for adding new wholesale suppliers to the FBA agent system. It automates configuration generation, runner script creation, and validation.

---

## Directory Structure

```
.claude/skills/supplier-onboarding/
├── SKILL.md           # Main skill documentation
└── supplier-onboarding.zip  # Archived version
```

---

## Purpose

When onboarding a new supplier, the skill generates:
1. **Categories Configuration** - List of category URLs
2. **Selectors Configuration** - CSS selectors for scraping
3. **Runner Script** - `run_custom_{supplier-id}.py`
4. **Auth Helper** - Authentication service (if required)
5. **System Config** - Workflow registration

---

## Prerequisites

Before running the onboarding wizard:
- [ ] Chrome running with debug port: `chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug`
- [ ] Repository location known
- [ ] Python dependencies installed
- [ ] Supplier domain/URL ready

---

## 7-Step Workflow

### Step 0: Data Preprocessing

**Type:** LLM Manual Validation

Validates and prepares input files:
- Verify URL formats
- Check domain matches
- Extract CSS selectors
- Create JSON files

### Step 1: Gather Information

**Type:** Progressive Discovery

Collects missing information:
- Supplier domain
- Category URLs
- CSS selectors
- Authentication requirement
- Credentials (if needed)

### Step 2: Prepare Configurations

**Type:** File Generation

Creates two JSON files:

#### Categories Config
```json
{
  "category_urls": [
    "https://supplier.com/category1",
    "https://supplier.com/category2"
  ]
}
```
**Location:** `config/{workflow_key}_categories.json`

#### Selectors Config
```json
{
  "supplier_url": "https://supplier.com",
  "product_item": ".product-card",
  "title": ".product-title",
  "price": ".price",
  "ean": ".ean-code",
  "url": ".product-link"
}
```
**Location:** `config/supplier_configs/{domain}.json`

### Step 3: Invoke Wizard

**Type:** Script Execution

```bash
python utils/supplier_onboarding_wizard.py \
  --domain "supplier.com" \
  --categories-source "config/supplier_categories.json" \
  --selectors-source "config/supplier_configs/supplier.com.json" \
  --workflow-key "supplier_workflow" \
  --mode generate \
  --authentication-required false
```

### Step 4: Validate Generated Files

**Type:** Critical Validation

Validates:
- Runner script structure (117-143 lines)
- Workflow key correctness
- Naming conventions
- Configuration files
- System config registration

### Step 5: Pre-Run Verification

**Type:** LLM Manual Checks

Performs comprehensive checks:
- File existence
- Content accuracy
- URL domain verification
- Selector syntax
- System readiness

### Step 6: User Decision

Presents options:
- Test Run (20 seconds)
- Main Run (full execution)
- Fix Issues first

### Step 7: Auth Helper (if applicable)

For authenticated suppliers:
- Generate template auth helper
- Document customization points
- Provide TODO comments

---

## Wizard Script

**Location:** `utils/supplier_onboarding_wizard.py`

**Class:** `SupplierOnboardingWizard`

**Key Methods:**
```python
def generate_runner(self, domain: str, workflow_key: str):
    # Creates run_custom_{supplier-id}.py
    
def generate_auth_helper(self, domain: str, credentials: dict):
    # Creates tools/{supplier-id}/supplier_authentication_service.py
    
def validate_generated_files(self, output_dir: Path):
    # Validates all generated files
```

---

## Generated Files

### Runner Script

**Pattern:** `run_custom_{supplier-id}.py`

**Structure:**
```python
import asyncio
import logging
import sys
from playwright.async_api import async_playwright
from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from utils.browser_manager import BrowserManager

async def main():
    # 1. Setup logging
    setup_logger(supplier_name="supplier.com")
    
    # 2. Load config
    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config("supplier_workflow")
    
    # 3. Connect to Chrome
    browser_mgr = BrowserManager()
    
    # 4. Optional: Authenticate
    # if requires_auth:
    #     auth_helper = SupplierAuthHelper(page)
    #     await auth_helper.login(credentials)
    
    # 5. Run workflow
    workflow = PassiveExtractionWorkflow(...)
    await workflow.run()
    
    # 6. Calculate financials
    run_calculations("supplier.com")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Naming Conventions

| Context | Form | Example |
|---------|------|---------|
| Config files | Dot-form | `supplier.com.json` |
| System config | Dot-form | `"supplier_name": "supplier.com"` |
| Runner script | Hyphen-form | `run_custom_supplier-com.py` |
| Tool directory | Hyphen-form | `tools/supplier-com/` |
| Workflow key | Underscore-form | `supplier_workflow` |

---

## Authentication Helper

**Location Pattern:** `tools/{supplier-id}/supplier_authentication_service.py`

**Structure:**
```python
class SupplierComAuthenticationHelper:
    def __init__(self, page):
        self.page = page
        
    async def is_authenticated(self) -> bool:
        # Check for auth indicators
        # Return True if logged in
        pass
    
    async def login(self, credentials: dict) -> bool:
        # Navigate to login page
        # Fill credentials
        # Submit form
        # Verify success
        pass
```

**Required Methods:**
- `is_authenticated()` - Check login status
- `login()` - Perform login

---

## System Config Update

The wizard registers the workflow in `config/system_config.json`:

```json
{
  "workflows": {
    "supplier_workflow": {
      "supplier_name": "supplier.com",
      "supplier_url": "https://supplier.com",
      "categories_config_path": "config/supplier_workflow_categories.json",
      "use_predefined_categories": true,
      "ai_client": null,
      "authentication_required": false
    }
  }
}
```

---

## Validation Checklist

### Runner Script
- [ ] Length: 117-143 lines
- [ ] Imports present
- [ ] Main function defined
- [ ] Entry point: `if __name__ == "__main__"`
- [ ] Workflow key correct

### Selectors
- [ ] All required keys present
- [ ] Values non-empty
- [ ] CSS syntax valid

### Categories
- [ ] All URLs complete (https://)
- [ ] Domain matches
- [ ] No duplicates

### System Config
- [ ] Workflow entry exists
- [ ] Paths resolve
- [ ] Auth flag correct

---

## Quick Start

### 1. Prepare Input Files
```bash
# Create categories file
echo "https://supplier.com/category1" > categories.txt
echo "https://supplier.com/category2" >> categories.txt

# Create selectors file (markdown format)
cat > selectors.md << 'EOF'
### Product Item
```css
.product-card
```

### Title
```css
.product-card h3 a
```
EOF
```

### 2. Run Wizard
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "supplier.com" \
  --categories-source "categories.txt" \
  --selectors-source "selectors.md" \
  --workflow-key "supplier_workflow" \
  --mode generate \
  --authentication-required false
```

### 3. Validate
```bash
# Check generated files
ls -la run_custom_supplier-com.py
python -m py_compile run_custom_supplier-com.py
```

### 4. Test Run
```bash
# 20 second test
timeout 20 python run_custom_supplier-com.py
```

---

## Common Issues

### Wrong Workflow Key
**Symptom:** Runner executes wrong supplier

**Fix:**
```python
# In runner script, verify:
workflow_config = config_loader.get_workflow_config('supplier_workflow')  # Correct
```

### Auth Helper Not Generated
**Symptom:** No auth helper created

**Fix:**
```bash
# Re-run with auth flags:
python utils/supplier_onboarding_wizard.py \
  --authentication-required true \
  --username "user@email.com" \
  --password "secret"
```

### 26-Line Shim Generated
**Symptom:** Runner is too short (26 lines)

**Cause:** Wrong wizard function called

**Fix:** Verify wizard has `create_full_runner()` function

---

## Reference Implementation

**Example with Authentication:**
`sample_data/reference_runners/run_custom_poundwholesale.py` (143 lines)

**Example without Authentication:**
`sample_data/reference_runners/run_custom_clearance_king.py` (117 lines)

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Wizard Script | `utils/supplier_onboarding_wizard.py` | Onboarding automation |
| Runner Template | `templates/runner_template.py.txt` | Runner generation |
| Auth Template | `templates/auth_helper_template.py.txt` | Auth helper generation |
| Naming Docs | `docs/NAMING_CONVENTIONS.md` | Naming rules |

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
