# Troubleshooting Guide

Common issues encountered during supplier onboarding and their solutions.

---

## Issue 1: 26-Line Shim Generated Instead of Full Runner

### Symptoms
- Runner script is only 26 lines long
- File contains `BASE_RUNNER = "run_custom_poundwholesale.py"`
- File forwards to another runner using `subprocess.run(cmd)`

### Example (Wrong Output)
```python
#!/usr/bin/env python3
import sys, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent
BASE_RUNNER = "run_custom_poundwholesale.py"  # ← WRONG!

def main():
    cmd = [sys.executable, str(REPO_ROOT / BASE_RUNNER), *sys.argv[1:]]
    raise SystemExit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
```

### Root Cause
Wizard's `create_runner_shim()` function was called instead of `create_full_runner()`.

**Why this happens**:
- Old wizard version before fixes
- Missing `create_full_runner()` function
- `determine_runner()` calling wrong function

### Impact
- **CRITICAL**: Sanity check will execute wrong supplier (poundwholesale instead of target supplier)
- Wrong products scraped
- Wrong categories processed
- Validation appears successful but analyzing wrong data

### Solution

**Step 1**: Verify wizard has `create_full_runner()` function
```bash
grep -n "def create_full_runner" utils/supplier_onboarding_wizard.py
```

Expected output:
```
299:def create_full_runner(supplier_id: str, workflow_key: str, supplier_domain: str,
```

If not found → **Wizard needs update** (apply fixes from memory file)

**Step 2**: Delete incorrect shim
```bash
rm run_custom_angelwholesale-co-uk.py
```

**Step 3**: Re-run wizard
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "angelwholesale.co.uk" \
  --categories-source "config/angelwholesale_categories.json" \
  --selectors-source "config/supplier_configs/angelwholesale.co.uk.json" \
  --workflow-key "angelwholesale_workflow" \
  --mode generate \
  --authentication-required false
```

**Step 4**: Verify generated runner
```bash
wc -l run_custom_angelwholesale-co-uk.py
# Should output: 117-143 lines (NOT 26)

grep "workflow_config = config_loader.get_workflow_config" run_custom_angelwholesale-co-uk.py
# Should show: get_workflow_config('angelwholesale_workflow')
# NOT: get_workflow_config('poundwholesale_workflow')
```

---

## Issue 2: Wrong Workflow Executed During Sanity Check

### Symptoms
- Sanity check completes successfully
- BUT logs show wrong supplier:
  ```
  2025-11-11 08:59:55 - INFO - Fetching: https://www.poundwholesale.co.uk/...
  ```
- Wrong categories processed
- Output files reference different supplier

### Root Cause
Runner script references incorrect workflow_key in `get_workflow_config()` call.

**Most common cause**: Shim forwarded to wrong base runner (see Issue 1)

**Secondary cause**: Manual edit error in workflow_key

### Diagnosis

**Step 1**: Read runner script
```bash
grep "get_workflow_config" run_custom_angelwholesale-co-uk.py
```

**Step 2**: Check output
```python
# ✅ CORRECT:
workflow_config = config_loader.get_workflow_config('angelwholesale_workflow')

# ❌ WRONG:
workflow_config = config_loader.get_workflow_config('poundwholesale_workflow')
```

**Step 3**: Check logs for confirmation
```bash
tail -50 logs/debug/run_custom_angelwholesale_*.log | grep "supplier_url"
```

Should show:
```
supplier_url: https://angelwholesale.co.uk
```

NOT:
```
supplier_url: https://www.poundwholesale.co.uk
```

### Solution

**Option A: Regenerate runner** (recommended)
1. Delete incorrect runner
2. Re-run wizard (see Issue 1 solution)
3. Validate workflow_key correct

**Option B: Manual fix** (quick fix)
1. Open runner in editor
2. Find line: `workflow_config = config_loader.get_workflow_config('...')`
3. Change to correct workflow_key
4. Save
5. Re-run and verify logs

---

## Issue 3: Authentication Helper Not Generated

### Symptoms
- No `tools/{supplier-id}/` directory created
- No `supplier_authentication_service.py` file
- Runner imports auth helper but file doesn't exist
- Runtime error: `ModuleNotFoundError: No module named 'tools.angelwholesale-co-uk'`

### Root Cause
Wizard executed without `--authentication-required` flag when auth was needed.

### Diagnosis

**Check if auth was intended**:
```bash
# Check selector config
cat config/supplier_configs/angelwholesale.co.uk.json | grep "authentication_required"
# Output: "authentication_required": false

# Check system config
cat config/system_config.json | grep -A 5 "angelwholesale_workflow" | grep "authentication_required"
# Output: "authentication_required": false
```

**Check if runner expects auth**:
```bash
grep "AuthenticationHelper" run_custom_angelwholesale-co-uk.py
```

If output found but files don't exist → **Mismatch**

### Solution

**If authentication IS required**:

**Step 1**: Delete incorrect files
```bash
rm run_custom_angelwholesale-co-uk.py
rm config/supplier_configs/angelwholesale.co.uk.json
```

**Step 2**: Update selector config
```json
{
  ...
  "authentication_required": true
}
```

**Step 3**: Re-run wizard WITH auth
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "angelwholesale.co.uk" \
  --categories-source "config/angelwholesale_categories.json" \
  --selectors-source "config/supplier_configs/angelwholesale.co.uk.json" \
  --workflow-key "angelwholesale_workflow" \
  --mode generate \
  --authentication-required true \
  --username "user@example.com" \
  --password "SecurePass123"
```

**Step 4**: Verify auth helper generated
```bash
ls -la tools/angelwholesale-co-uk/
# Should show:
# __init__.py
# supplier_authentication_service.py
```

**If authentication is NOT required**:

**Step 1**: Edit runner - remove auth imports
```python
# Delete this line:
from tools.angelwholesale-co-uk.supplier_authentication_service import AngelwholesaleCoUkAuthenticationHelper

# Delete auth logic section (lines ~70-85)
```

**Step 2**: Add comment
```python
# No authentication required for this supplier
log.info(f"ℹ️ No authentication required for {supplier_name}")
```

---

## Issue 4: Naming Convention Violations

### Symptoms
- Config file not found: `FileNotFoundError: config/supplier_configs/angelwholesale-co-uk.json`
- Import error: `ModuleNotFoundError: No module named 'tools.angelwholesale.co.uk'`
- Workflow not found in system_config.json

### Common Violations

**Violation 1**: Hyphens in config filename
```
❌ config/supplier_configs/angelwholesale-co-uk.json
✅ config/supplier_configs/angelwholesale.co.uk.json
```

**Violation 2**: Dots in runner filename
```
❌ run_custom_angelwholesale.co.uk.py
✅ run_custom_angelwholesale-co-uk.py
```

**Violation 3**: Dots in tool directory
```
❌ tools/angelwholesale.co.uk/
✅ tools/angelwholesale-co-uk/
```

**Violation 4**: Wrong form in workflow key
```
❌ "angelwholesale-co-uk_workflow"
❌ "angelwholesale.co.uk_workflow"
✅ "angelwholesale_workflow"
```

### Solution

**Step 1**: Identify violated files
```bash
# Check config file
ls config/supplier_configs/ | grep angelwholesale

# Check runner
ls run_custom_* | grep angelwholesale

# Check tool directory
ls tools/ | grep angelwholesale
```

**Step 2**: Rename files to correct form

**For config file** (should be dot-form):
```bash
mv config/supplier_configs/angelwholesale-co-uk.json \
   config/supplier_configs/angelwholesale.co.uk.json
```

**For runner** (should be hyphen-form):
```bash
mv run_custom_angelwholesale.co.uk.py \
   run_custom_angelwholesale-co-uk.py
```

**For tool directory** (should be hyphen-form):
```bash
mv tools/angelwholesale.co.uk \
   tools/angelwholesale-co-uk
```

**Step 3**: Update references in files

Update runner imports:
```python
# Change this:
from tools.angelwholesale.co.uk.supplier_authentication_service import ...

# To this:
from tools.angelwholesale-co-uk.supplier_authentication_service import ...
```

**Step 4**: Verify
```bash
# Test import
python -c "from tools.angelwholesale-co-uk.supplier_authentication_service import AngelwholesaleCoUkAuthenticationHelper"

# Test config load
python -c "import json; print(json.load(open('config/supplier_configs/angelwholesale.co.uk.json'))['supplier_url'])"
```

**Reference**: See `docs/NAMING_CONVENTIONS.md` for complete specification

---

## Issue 5: Sanity Check Failures

### Symptoms
Wizard reports sanity check failures:
```
❌ Sanity Check Results:
   Scraping Rate: FAIL (0 products found)
   Amazon Cache: FAIL (no cache files created)
   ...
```

### Diagnosis Matrix

| Failed Check | Likely Cause | Investigation |
|--------------|--------------|---------------|
| Scraping Rate | Wrong selectors or wrong supplier | Check logs for HTTP errors, selector failures |
| Amazon Cache | No products extracted | Depends on Scraping Rate passing first |
| Linking Map | No EAN matches | Check if products have valid EANs |
| Financial CSV | No profitable products | Check if any products analyzed |
| Processing State | State file write failure | Check permissions on OUTPUTS/CACHE/ |
| No Critical Errors | Exception occurred | Check logs for stack traces |

### Common Causes

**Cause 1: Wrong Supplier Scraped**
```bash
# Check logs
grep "Fetching:" logs/debug/run_custom_angelwholesale_*.log | head -5

# Should show:
# Fetching: https://angelwholesale.co.uk/...

# NOT:
# Fetching: https://www.poundwholesale.co.uk/...
```

**Solution**: See Issue 2

**Cause 2: Invalid CSS Selectors**
```bash
# Test selectors manually
python <<EOF
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://angelwholesale.co.uk/category-page")

    # Test product card selector
    cards = page.query_selector_all("article.product")
    print(f"Found {len(cards)} product cards")
EOF
```

**Solution**: Update selectors in `config/supplier_configs/{domain}.json`

**Cause 3: Chrome Not Running**
```bash
# Check Chrome process
curl http://localhost:9222/json/version

# If fails:
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

**Cause 4: Authentication Required But Not Configured**

Check logs for:
```
"Price not visible - authentication may be required"
"Login required to view prices"
```

**Solution**: Re-run wizard with `--authentication-required true`

---

## Issue 6: Template Placeholders Not Replaced

### Symptoms
- Generated files contain `{{WORKFLOW_KEY}}` or similar placeholders
- Import errors with literal `{{SUPPLIER_NAME}}`
- Runner fails with undefined variable

### Example (Wrong Output)
```python
workflow_config = config_loader.get_workflow_config('{{WORKFLOW_KEY}}')  # ← NOT REPLACED
```

### Root Cause
Template variable replacement failed in wizard.

### Diagnosis
```bash
# Search for unreplaced placeholders
grep -r "{{" run_custom_angelwholesale-co-uk.py
grep -r "{{" tools/angelwholesale-co-uk/

# Should return NO matches
```

### Solution

**Step 1**: Check wizard version
```bash
grep "def create_full_runner" utils/supplier_onboarding_wizard.py -A 20 | grep "replace"
```

Should show multiple `.replace()` calls:
```python
runner_content = template.replace('{{WORKFLOW_KEY}}', workflow_key)
runner_content = runner_content.replace('{{SUPPLIER_NAME}}', supplier_id)
# ... more replacements
```

**Step 2**: If replacements present but still failing → Check parameters

Verify wizard invocation includes all required parameters:
```bash
--workflow-key "angelwholesale_workflow"  # NOT None or empty
```

**Step 3**: Regenerate files
```bash
rm run_custom_angelwholesale-co-uk.py
# Re-run wizard with correct parameters
```

---

## Issue 7: Permission Denied Errors (Windows)

### Symptoms
```
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
```

### Common Scenarios

**Scenario 1**: File open in editor
- **Solution**: Close file in editor, retry

**Scenario 2**: Previous wizard run still holding lock
- **Solution**: Kill Python process, retry
  ```bash
  taskkill /F /IM python.exe
  ```

**Scenario 3**: Antivirus scanning file
- **Solution**: Add project directory to antivirus exclusions

**Scenario 4**: Chrome process holding file lock
- **Solution**: Restart Chrome with debug port

---

## Issue 8: Module Import Errors at Runtime

### Symptoms
```
ModuleNotFoundError: No module named 'tools.passive_extraction_workflow_latest'
ImportError: cannot import name 'PassiveExtractionWorkflow'
```

### Diagnosis

**Check 1**: Verify file exists
```bash
ls -la tools/passive_extraction_workflow_latest.py
```

**Check 2**: Verify Python path
```bash
python -c "import sys; print('\\n'.join(sys.path))"
```

**Check 3**: Test import directly
```bash
python -c "from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow"
```

### Solution

**Solution 1**: Run from correct directory
```bash
cd /path/to/Amazon-FBA-Agent-System/
python run_custom_angelwholesale-co-uk.py
```

**Solution 2**: Verify sys.path insertion
```python
# In runner, should have:
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

**Solution 3**: Check file encoding
```bash
file run_custom_angelwholesale-co-uk.py
# Should show: UTF-8 Unicode text
```

---

## Quick Diagnostic Commands

**Check all generated files**:
```bash
# Runner
test -f run_custom_angelwholesale-co-uk.py && echo "✅ Runner exists" || echo "❌ Runner missing"

# Categories
test -f config/angelwholesale_workflow_categories.json && echo "✅ Categories exist" || echo "❌ Categories missing"

# Selectors
test -f config/supplier_configs/angelwholesale.co.uk.json && echo "✅ Selectors exist" || echo "❌ Selectors missing"

# Auth helper (if applicable)
test -f tools/angelwholesale-co-uk/supplier_authentication_service.py && echo "✅ Auth helper exists" || echo "⚠️ Auth helper missing (may not be required)"
```

**Validate runner structure**:
```bash
# Check line count
wc -l run_custom_angelwholesale-co-uk.py

# Check workflow key
grep "get_workflow_config" run_custom_angelwholesale-co-uk.py

# Check imports
grep "^import\|^from" run_custom_angelwholesale-co-uk.py | head -15
```

**Test wizard version**:
```bash
grep -E "def (create_full_runner|create_auth_helper|determine_runner)" utils/supplier_onboarding_wizard.py
```

Should show:
```
def determine_runner(workflow_key: str, supplier_id: str, supplier_domain: str, auth_required: bool, repo_root: Path) -> str:
def create_full_runner(supplier_id: str, workflow_key: str, supplier_domain: str, auth_required: bool, repo_root: Path) -> Path:
def create_auth_helper(supplier_id: str, supplier_domain: str, supplier_url: str, repo_root: Path) -> Path:
```

---

## Getting Help

If issues persist after trying solutions:

1. **Check Serena Memory Files**:
   ```bash
   ls .serena/memories/ | grep supplier_onboarding
   ```

2. **Review Latest Session Logs**:
   ```bash
   ls -t logs/debug/run_custom_angelwholesale_*.log | head -1 | xargs cat
   ```

3. **Validate Against Reference**:
   - Compare with `sample_data/reference_runners/run_custom_poundwholesale.py`
   - Check docs/FILE_SPECIFICATIONS.md
   - Review docs/NAMING_CONVENTIONS.md

4. **Re-run with Fresh Start**:
   ```bash
   # Delete all generated files
   rm run_custom_angelwholesale-co-uk.py
   rm config/angelwholesale_workflow_categories.json
   rm config/supplier_configs/angelwholesale.co.uk.json
   rm -rf tools/angelwholesale-co-uk/

   # Remove workflow from system_config.json manually
   # Re-run wizard from scratch
   ```

---

**End of TROUBLESHOOTING.md**
