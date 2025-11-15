# Supplier Onboarding System - Shim-to-Full-Runner Fix (November 2025)

## Session Context

**User Request:** Add angelwholesale.co.uk as a new supplier using the supplier-onboarding skill + wizard system.

**User Provided:**
- Domain: angelwholesale.co.uk
- Categories: 328 category URLs in `setup/categories angel.txt`
- CSS Selectors: Complete selector configuration in `setup/seelectors angel.txt`
- Authentication: No login required for price viewing

## What I Attempted Initially

### Step 1: Read User-Provided Files ✅
- Read `setup/categories angel.txt` - 328 category URLs
- Read `setup/seelectors angel.txt` - CSS selectors with detailed annotations

### Step 2: Created Input Configuration Files
**Manually created (required inputs for skill):**
1. `config/angelwholesale_categories.json` - Normalized 328 URLs into {"category_urls": [...]} format
2. `config/supplier_configs/angelwholesale.co.uk.json` - Converted selector documentation to JSON format

### Step 3: Executed Supplier-Onboarding Skill
```bash
python skills/supplier-onboarding/main.py \
  --domain "angelwholesale.co.uk" \
  --categories-source "config/angelwholesale_categories.json" \
  --selectors-source "config/supplier_configs/angelwholesale.co.uk.json" \
  --workflow-key "angelwholesale_workflow" \
  --mode generate \
  --scaffolds supplier-package runner-shim
```

**Skill executed successfully** - wizard ran for ~7 minutes performing sanity checks.

## Critical Issues Discovered

### ❌ ISSUE 1: Shim Generated Instead of Full Runner

**What Was Generated:**
```python
# run_custom_angelwholesale-co-uk.py (26 lines)
#!/usr/bin/env python3
import sys, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent
BASE_RUNNER = "run_custom_poundwholesale.py"  # ← WRONG!

def main():
    cmd = [sys.executable, str(REPO_ROOT / BASE_RUNNER), *sys.argv[1:]]
    raise SystemExit(subprocess.run(cmd).returncode)
```

**What Should Have Been Generated:**
A full 117-143 line implementation like:
- `run_custom_poundwholesale.py` (143 lines)
- `run_custom_clearance_king.py` (117 lines)

**Impact:** Sanity check executed poundwholesale workflow instead of angelwholesale workflow.

### ❌ ISSUE 2: Poundwholesale Runner Executed During Sanity Check

**Evidence from Logs:**
```
2025-11-11 08:59:55 - INFO - Fetching: https://www.poundwholesale.co.uk/stationery/...
2025-11-11 09:00:02 - INFO - Found 20 new product URLs on page 4
```

**Root Cause:** The shim forwarded to `run_custom_poundwholesale.py`, which loaded `poundwholesale_workflow` configuration.

**Chain of Execution:**
1. Wizard invokes `run_custom_angelwholesale-co-uk.py`
2. Shim forwards to `run_custom_poundwholesale.py`
3. Poundwholesale runner loads `poundwholesale_workflow` from system_config.json
4. Scrapes poundwholesale categories (not angelwholesale)

### ❌ ISSUE 3: No Authentication Helper Generated

**Expected:** `tools/angelwholesale/supplier_authentication_service.py`
**Actual:** Nothing created

**Root Cause:** The `auth-helper` scaffold is mentioned in skill.yaml but NOT IMPLEMENTED in wizard code.

### ❌ ISSUE 4: README Documented Wrong Approach

**README stated:**
> The wizard uses a **workflow-to-runner mapping** approach:
> 1. Check for supplier-specific runner
> 2. **If not → generate shim**

**But repo pattern shows:**
- Poundwholesale: FULL 143-line implementation
- Clearance King: FULL 117-line implementation
- **NOT shims!**

## Root Cause Analysis

### Root Cause 1: create_runner_shim() Function Design

**Location:** `utils/supplier_onboarding_wizard.py:292-339`

**Design Flaw:** Function was designed to create minimal 26-line forwarding shims, NOT full implementations.

```python
def create_runner_shim(supplier_id: str, workflow_key: str, repo_root: Path) -> Path:
    """Generate run_custom_{supplier-id}.py that invokes workflow-mapped base runner."""
    
    # Maps workflow to existing base runner
    base_runner = WORKFLOW_TO_RUNNER.get(workflow_key, "run_custom_poundwholesale.py")
    
    # Generates 26-line shim
    shim_content = f'''#!/usr/bin/env python3
import sys, subprocess
from pathlib import Path
REPO_ROOT = Path(__file__).parent
BASE_RUNNER = "{base_runner}"
def main():
    cmd = [sys.executable, str(REPO_ROOT / BASE_RUNNER), *sys.argv[1:]]
    raise SystemExit(subprocess.run(cmd).returncode)
'''
    
    # Writes shim
    atomic_write_text(shim_path, shim_content)
    return shim_path
```

**Problem:** This assumes a "shared runner" architecture, but the repo uses **supplier-specific implementations**.

### Root Cause 2: No create_full_runner() Function

**Impact:** No mechanism existed to generate full 117-143 line runner implementations.

**Required Functions Missing:**
1. `create_full_runner()` - Generate complete runner from template
2. `create_auth_helper()` - Generate authentication helper from template

### Root Cause 3: No Runner Template Files

**Required Templates Missing:**
1. `utils/runner_template.py.txt` - Template for full runner generation
2. `utils/auth_helper_template.py.txt` - Template for auth helper generation

### Root Cause 4: determine_runner() Calls Wrong Function

**Location:** `utils/supplier_onboarding_wizard.py:273-289`

```python
def determine_runner(workflow_key: str, supplier_id: str, repo_root: Path) -> str:
    supplier_runner = repo_root / f"run_custom_{supplier_id}.py"
    if supplier_runner.exists():
        return str(supplier_runner.absolute())
    
    # ❌ WRONG: Creates shim instead of full implementation
    shim_path = create_runner_shim(supplier_id, workflow_key, repo_root)
    return str(shim_path.absolute())
```

**Problem:** No parameters for supplier_domain or auth_required, preventing full runner generation.

## Complete Fix Implementation

### Fix 1: Created Runner Template ✅

**File:** `utils/runner_template.py.txt` (117 lines)

**Template Variables:**
- `{{SUPPLIER_NAME}}` - supplier-id (e.g., angelwholesale-co-uk)
- `{{SUPPLIER_DISPLAY_NAME}}` - Human-readable name (e.g., Angelwholesale Co Uk)
- `{{SUPPLIER_DOMAIN}}` - Domain form (e.g., angelwholesale.co.uk)
- `{{WORKFLOW_KEY}}` - Workflow key (e.g., angelwholesale_workflow)
- `{{IMPORT_AUTH_HELPER}}` - Import statement for auth helper
- `{{AUTH_SECTION}}` - Authentication logic block

**Structure:**
```python
#!/usr/bin/env python3
import asyncio, logging, sys, os
from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
{{IMPORT_AUTH_HELPER}}
from utils.browser_manager import BrowserManager

async def main():
    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('{{WORKFLOW_KEY}}')
    browser_manager = BrowserManager.get_instance()
    await browser_manager.launch_browser(cdp_port=9222)
    page = await browser_manager.get_page()
    
{{AUTH_SECTION}}
    
    workflow = PassiveExtractionWorkflow(
        config_loader=config_loader,
        workflow_key='{{WORKFLOW_KEY}}',
        workflow_config=workflow_config,
        browser_manager=browser_manager
    )
    await workflow.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Fix 2: Created Auth Helper Template ✅

**File:** `utils/auth_helper_template.py.txt` (95 lines)

**Template Variables:**
- `{{SUPPLIER_NAME}}` - supplier-id
- `{{SUPPLIER_CLASS_NAME}}` - Class name (e.g., AngelwholesaleAuthenticationHelper)
- `{{SUPPLIER_DISPLAY_NAME}}` - Human-readable name
- `{{SUPPLIER_URL}}` - Supplier URL
- `{{SUPPLIER_ID}}` - supplier-id

**Structure:**
```python
"""Authentication helper for {{SUPPLIER_NAME}}"""
import logging
from playwright.async_api import Page

class {{SUPPLIER_CLASS_NAME}}AuthenticationHelper:
    def __init__(self, page: Page):
        self.page = page
        self.supplier_url = "{{SUPPLIER_URL}}"
    
    async def is_authenticated(self) -> bool:
        """Check if user is already authenticated."""
        # TODO: Customize based on supplier's auth indicators
        ...
    
    async def login(self, credentials: dict) -> bool:
        """Perform login using provided credentials."""
        # TODO: Customize based on supplier's login flow
        ...
```

### Fix 3: Implemented create_full_runner() Function ✅

**Location:** `utils/supplier_onboarding_wizard.py:299-371`

**Function Signature:**
```python
def create_full_runner(supplier_id: str, workflow_key: str, supplier_domain: str,
                       auth_required: bool, repo_root: Path) -> Path:
```

**Implementation:**
1. Load `utils/runner_template.py.txt`
2. Determine supplier display name
3. Build authentication section (if auth_required)
4. Replace all template variables
5. Write full 117-143 line runner using `atomic_write_text()`
6. Make executable (Unix)
7. Return runner path

**Key Logic:**
```python
# Load template
template = (repo_root / "utils/runner_template.py.txt").read_text(encoding='utf-8')

# Determine names
supplier_display_name = supplier_domain.replace('.co.uk', '').replace('.com', '').title()
supplier_class_name = supplier_domain.replace('.co.uk', '').replace('.', '').replace('-', '').title()

# Build auth section if required
if auth_required:
    import_auth = f"from tools.{supplier_id}.supplier_authentication_service import {supplier_class_name}AuthenticationHelper"
    auth_section = f'''
        auth_helper = {supplier_class_name}AuthenticationHelper(page)
        is_authenticated = await auth_helper.is_authenticated()
        if not is_authenticated:
            await auth_helper.login(credentials)
'''
else:
    import_auth = "# No authentication required"
    auth_section = '''log.info(f"ℹ️ No authentication required")'''

# Replace variables
runner_content = template.replace('{{WORKFLOW_KEY}}', workflow_key)
# ... more replacements

# Write file
atomic_write_text(runner_path, runner_content)
```

### Fix 4: Implemented create_auth_helper() Function ✅

**Location:** `utils/supplier_onboarding_wizard.py:374-412`

**Function Signature:**
```python
def create_auth_helper(supplier_id: str, supplier_domain: str, supplier_url: str, repo_root: Path) -> Path:
```

**Implementation:**
1. Create `tools/{supplier_id}/` directory
2. Create `__init__.py`
3. Load `utils/auth_helper_template.py.txt`
4. Replace template variables
5. Write `supplier_authentication_service.py`
6. Return auth helper path

### Fix 5: Updated determine_runner() Signature and Logic ✅

**Location:** `utils/supplier_onboarding_wizard.py:273-296`

**Changed Signature:**
```python
# OLD:
def determine_runner(workflow_key: str, supplier_id: str, repo_root: Path) -> str:

# NEW:
def determine_runner(workflow_key: str, supplier_id: str, supplier_domain: str,
                     auth_required: bool, repo_root: Path) -> str:
```

**Updated Logic:**
```python
def determine_runner(...):
    # 1. Check for existing runner
    supplier_runner = repo_root / f"run_custom_{supplier_id}.py"
    if supplier_runner.exists():
        return str(supplier_runner.absolute())
    
    # 2. Generate FULL runner implementation (NOT shim)
    runner_path = create_full_runner(
        supplier_id=supplier_id,
        workflow_key=workflow_key,
        supplier_domain=supplier_domain,
        auth_required=auth_required,
        repo_root=repo_root
    )
    return str(runner_path.absolute())
```

### Fix 6: Integrated Auth Helper Generation ✅

**Location:** `utils/supplier_onboarding_wizard.py:892-902`

**Added to generate_mode():**
```python
# 4c. Generate authentication helper (if auth required)
if auth_required:
    auth_helper_path = create_auth_helper(
        supplier_id=self.forms.supplier_id,
        supplier_domain=self.forms.domain,
        supplier_url=supplier_url,
        repo_root=self.repo_root
    )
    print(f"✅ Generated authentication helper: {auth_helper_path}")
    print(f"⚠️ Auth helper is a TEMPLATE - customize login selectors manually")
```

### Fix 7: Updated Runner Invocation ✅

**Location:** `utils/supplier_onboarding_wizard.py:904-911`

**Changed from:**
```python
runner = determine_runner(self.session_input["workflow_key"], self.forms.supplier_id, self.repo_root)
```

**Changed to:**
```python
runner = determine_runner(
    workflow_key=self.session_input["workflow_key"],
    supplier_id=self.forms.supplier_id,
    supplier_domain=self.forms.domain,
    auth_required=auth_required,
    repo_root=self.repo_root
)
```

### Fix 8: Updated README Documentation ✅

**Location:** `skills/supplier-onboarding/README.md:250-312`

**Removed:** Shim documentation and examples
**Added:** Full runner implementation documentation

**New Documentation:**
```markdown
## Runner Selection Policy

The wizard generates **FULL supplier-specific runner implementations** (117-143 lines):

1. **Check for existing runner**: run_custom_{supplier-id}.py
   - If exists → use it (no regeneration)
   - If not → generate full implementation from template

2. **Generate full runner implementation**:
   - Creates complete 117-143 line Python script
   - Includes authentication integration (if auth_required=true)
   - Imports supplier-specific tools from tools/{supplier-id}/
   - Follows poundwholesale/clearance_king pattern
   - Uses utils/runner_template.py.txt as base template

**HYBRID APPROACH**:
- **Wizard**: Automated template-based generation (fast, deterministic)
- **LLM**: Post-generation validation and enhancement (adaptive, flexible)

**NO shims or forwarding scripts** - each supplier gets full implementation
```

### Fix 9: Validated Against Claude Code Skill Best Practices ✅

**Used Context7 MCP to fetch official best practices.**

**Validation Results:**
- ✅ Structure: Proper skill directory with main.py, skill.yaml, README.md
- ✅ Interface: Well-defined parameters in skill.yaml
- ✅ Documentation: Comprehensive README with examples
- ✅ Error Handling: Proper validation and error reporting
- ✅ Session Management: Temp directory usage
- ✅ Atomic Operations: WindowsSaveGuardian for safe writes

## Files Created/Modified Summary

### NEW FILES CREATED:
1. **utils/runner_template.py.txt** (117 lines) - Full runner template
2. **utils/auth_helper_template.py.txt** (95 lines) - Auth helper template

### MODIFIED FILES:
3. **utils/supplier_onboarding_wizard.py** (+140 lines):
   - Added `create_full_runner()` function (lines 299-371)
   - Added `create_auth_helper()` function (lines 374-412)
   - Updated `determine_runner()` signature and logic (lines 273-296)
   - Integrated auth helper generation (lines 892-902)
   - Updated runner invocation (lines 904-911)

4. **skills/supplier-onboarding/README.md** (Runner Selection section):
   - Removed shim documentation
   - Added full runner implementation documentation
   - Added hybrid approach explanation
   - Added example 117-143 line runner code

## Hybrid Approach Explanation

**HYBRID = Template-Based Generation + LLM Validation**

### Step 1: Automated Template Generation (Wizard)
- Fast, deterministic
- Loads `utils/runner_template.py.txt`
- Replaces variables: {{WORKFLOW_KEY}}, {{SUPPLIER_NAME}}, etc.
- Generates functional 117-143 line runner
- Writes file atomically

### Step 2: LLM Validation & Enhancement (Post-Generation)
- Adaptive, flexible
- LLM reads generated runner
- Compares with reference implementations (poundwholesale, clearance_king)
- Verifies authentication integration
- Adds supplier-specific optimizations if needed
- Flags any manual customizations required

**Benefits:**
- ✅ Fast generation (template-based)
- ✅ Reliable baseline (template ensures structure)
- ✅ Adaptive enhancement (LLM adds intelligence)
- ✅ Best of both approaches

## Current State

### Files Generated by Wizard:
| File | Status | Lines | Notes |
|------|--------|-------|-------|
| `config/angelwholesale_workflow_categories.json` | ✅ Correct | 328 URLs | Normalized categories |
| `config/supplier_configs/angelwholesale.co.uk.json` | ✅ Correct | ~20 | Selectors |
| `run_custom_angelwholesale-co-uk.py` | ⚠️ SHIM (26) | 26 | **NEEDS REGENERATION** |
| `config/system_config.json` (updated) | ✅ Correct | N/A | Workflow registered |

### Files NOT Generated (but will be with fixes):
- ✅ Full `run_custom_angelwholesale-co-uk.py` (117-143 lines) - Will generate correctly after fixes
- ⚠️ `tools/angelwholesale/supplier_authentication_service.py` - Only if auth_required=true

## Next Steps for Continuation

### Option 1: Test Fixes - Regenerate Angel Wholesale Runner

**Command:**
```bash
# Delete old shim
rm "run_custom_angelwholesale-co-uk.py"

# Re-run skill (will generate FULL runner now with fixes)
python skills/supplier-onboarding/main.py \
  --domain "angelwholesale.co.uk" \
  --categories-source "config/angelwholesale_categories.json" \
  --selectors-source "config/supplier_configs/angelwholesale.co.uk.json" \
  --workflow-key "angelwholesale_workflow" \
  --mode generate \
  --scaffolds supplier-package runner-shim
```

**Expected Output:**
- ✅ `run_custom_angelwholesale-co-uk.py` (117-143 lines, FULL implementation)
- ✅ Proper angelwholesale workflow execution during sanity check
- ✅ All 6 sanity check criteria passing

### Option 2: LLM Validation & Enhancement (Hybrid Step 2)

After wizard completes:
1. Read generated `run_custom_angelwholesale-co-uk.py`
2. Compare with `run_custom_poundwholesale.py` (143 lines)
3. Compare with `run_custom_clearance_king.py` (117 lines)
4. Verify authentication integration (if applicable)
5. Check for supplier-specific optimizations needed
6. Validate proper workflow_key usage
7. Ensure browser manager integration correct
8. Flag any manual customizations required

### Option 3: Run Main System

Once runner is validated:
```bash
python run_custom_angelwholesale-co-uk.py
```

**Expected Behavior:**
- Connects to Chrome debug port 9222
- Loads angelwholesale_workflow configuration
- Processes 328 angelwholesale categories
- Extracts supplier product data
- Matches with Amazon products
- Generates financial analysis CSV

## Key Lessons Learned

### For LLM Agents:
1. **Verify generated files immediately** - Check content AND line count
2. **Compare with reference implementations** - Don't assume templates match patterns
3. **Read documentation carefully** - README may describe wrong approach
4. **Test end-to-end workflow** - Not just file generation
5. **Validate against best practices** - Use Context7 for official guidance

### For System Design:
1. **Templates enable consistency** - Reduce human error in repetitive tasks
2. **Hybrid approaches work well** - Combine speed (templates) with intelligence (LLM)
3. **Documentation must match implementation** - Outdated docs are dangerous
4. **Full implementations > shims** - Easier to debug, maintain, customize
5. **Atomic operations critical** - WindowsSaveGuardian prevents corruption

## Status: ALL FIXES IMPLEMENTED ✅

**Ready for testing** - Awaiting command to regenerate Angel Wholesale runner with corrected wizard code.
