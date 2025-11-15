# Supplier Onboarding Wizard - Category File Naming Fix (November 2025)

## Session Context

**Previous Session Success:**
- ✅ Template fixes implemented successfully (constructor, browser persistence, event loop)
- ✅ Runner script generates correctly (135 lines, all standards met)
- ✅ All 3 critical template errors resolved

**Current Session Issue:**
- 🚨 Script crashes immediately with `IndexError: list index out of range`
- 🎯 Root cause: File naming mismatch between wizard and state manager
- ⚠️ Unicode thread error (cosmetic only, does not affect functionality)

**Key Principle Applied:**
> **MODIFY GENERATOR OUTPUT, NOT WORKING PRODUCTION SCRIPTS**
> - Wizard = generator code (safe to modify)
> - State manager = working production code (preserve as-is)

---

## Critical Error Analysis

### Error 1: IndexError - Root Cause Chain

```
Script Execution:
1. workflow.run() starts
   ↓
2. state_manager.initialize_workflow_session()
   ↓
3. perform_startup_analysis()
   ↓
4. _get_frozen_or_live_manifest_urls()
   ↓
   WARNING: Category config file not found: config\angelwholesale_categories.json
   Returns: [] (empty list)
   ↓
5. _first_incomplete_index_by_url(manifest_urls=[], ...)
   ↓
6. 💥 IndexError: list index out of range (line 3002)
```

**The Path Mismatch:**

| Component | Looks For | Actually Exists | Match? |
|-----------|-----------|-----------------|--------|
| State Manager (line 3030) | `config/angelwholesale_categories.json` | - | - |
| Wizard Generated | - | `config/angelwholesale_workflow_categories.json` | ❌ |
| Difference | Missing `_workflow` suffix | Has `_workflow` suffix | **MISMATCH** |

**State Manager Code (Working - Do NOT Modify):**
```python
# utils/fixed_enhanced_state_manager.py:3030
config_path = (
    Path(__file__).parent.parent
    / "config"
    / f"{self.supplier_name.replace('.co.uk', '')}_categories.json"
)
# For angelwholesale.co.uk:
# Constructs: config/angelwholesale_categories.json
```

**Wizard Current Behavior (Needs Fix):**
```python
# Creates: config/angelwholesale_workflow_categories.json
#                   ^^^^^^^^^ EXTRA SUFFIX
```

---

### Error 2: Empty List Bug (State Manager Logic)

**Location:** `utils/fixed_enhanced_state_manager.py:2998-3002`

**The Bug:**
```python
def _first_incomplete_index_by_url(self, manifest_urls: List[str], ...):
    n = max(1, len(manifest_urls))  # ⚠️ Returns 1 when list empty!
    start = max(1, int(hint or 1))
    order = list(range(start-1, n)) + list(range(0, start-1))
    for i in order:
        url = manifest_urls[i]  # 💥 Crashes when manifest_urls = []
```

**Why NOT to Fix This:**
- 🔒 Production code in working state manager
- ✅ Bug only triggers when category file missing (edge case)
- ✅ Proper fix: ensure wizard creates file with correct name
- ✅ Modifying state manager risks breaking existing suppliers

---

### Error 3: Unicode Thread Error (Cosmetic)

**Error:**
```
Exception in thread Thread-1 (wait_and_read_utf8):
UnicodeDecodeError: 'utf-8' codec can't decode bytes in position 5970-5971
```

**Impact Analysis:**

| Component | Affected? | Impact |
|-----------|-----------|--------|
| File Creation | ❌ NO | WindowsSaveGuardian uses explicit UTF-8 |
| JSON Content | ❌ NO | All files correctly formatted |
| System Operation | ❌ NO | Wizard completes successfully |
| Console Output | ⚠️ YES | Some subprocess messages garbled |
| Log Files | ❌ NO | Written with explicit UTF-8 |

**Conclusion:** ⚠️ **COSMETIC ONLY** - Safe to ignore

---

## Complete Fix Plan

### Fix 1: Wizard Category File Naming (CRITICAL)

**File to Modify:** `utils/supplier_onboarding_wizard.py`  
**Priority:** 🔴 CRITICAL  
**Justification:** Wizard is generator code, safe to modify

**Solution: Create BOTH Filenames**

```python
# =============================================================================
# FIX: Create category file with BOTH naming patterns for compatibility
# =============================================================================

def create_category_config_files(supplier_domain: str, supplier_id: str, workflow_key: str, 
                                  category_urls: List[str], repo_root: Path):
    """
    Create category configuration file with DUAL NAMING for compatibility.
    
    Creates two files with identical content:
    1. {supplier_id}_workflow_categories.json  (for system_config.json)
    2. {supplier_name}_categories.json         (for state manager)
    """
    from datetime import datetime
    
    # Prepare category data
    categories_data = {
        "category_urls": category_urls,
        "total_categories": len(category_urls),
        "generated_at": datetime.now().isoformat(),
        "supplier": supplier_domain,
        "workflow": workflow_key
    }
    
    # Pattern 1: With workflow suffix (for system_config.json)
    categories_filename_workflow = f"{supplier_id}_workflow_categories.json"
    categories_path_workflow = repo_root / "config" / categories_filename_workflow
    
    # Pattern 2: Without workflow suffix (for state manager)
    supplier_name_clean = supplier_domain.replace('.co.uk', '').replace('.com', '').replace('.', '')
    categories_filename_legacy = f"{supplier_name_clean}_categories.json"
    categories_path_legacy = repo_root / "config" / categories_filename_legacy
    
    # Save with BOTH filenames
    save_json_atomic(categories_path_workflow, categories_data)
    print(f"✅ Created: {categories_filename_workflow}")
    
    save_json_atomic(categories_path_legacy, categories_data)
    print(f"✅ Created: {categories_filename_legacy} (state manager compatibility)")
    
    # Validate files
    if not category_urls:
        print("\n⚠️  WARNING: No category URLs were provided!")
        print("   The category file will be empty.")
        print("   Workflow will enter fresh_start mode.")
    else:
        print(f"\n✅ Category file validation:")
        print(f"   - Total URLs: {len(category_urls)}")
        print(f"   - Created with both naming patterns")
        
        # Verify state manager can find the file
        if categories_path_legacy.exists():
            print(f"   - ✅ State manager will find: {categories_filename_legacy}")
        else:
            print(f"   - ❌ ERROR: State manager file missing!")
    
    return categories_filename_workflow  # Return workflow pattern for system_config.json
```

**Why This Works:**
- ✅ Creates file with BOTH naming patterns
- ✅ State manager finds file (uses legacy pattern)
- ✅ System config references workflow pattern
- ✅ No existing code modified
- ✅ Future-proof (handles both conventions)
- ✅ Zero risk to working scripts

---

### Fix 2: Add Validation (IMPORTANT)

**File to Modify:** `utils/supplier_onboarding_wizard.py`  
**Priority:** 🟡 IMPORTANT  
**Location:** After file creation

```python
# Validate category file is not empty
if not category_urls:
    print("\n⚠️  WARNING: No category URLs were provided!")
    print("   The category file will be empty.")
    print("   This will cause the workflow to enter fresh_start mode.")
    print("   You may need to provide categories later.")
else:
    print(f"\n✅ Category file validation:")
    print(f"   - Total URLs: {len(category_urls)}")
    print(f"   - Created with both naming patterns:")
    print(f"     • {categories_filename_workflow}")
    print(f"     • {categories_filename_legacy}")

# Validate state manager can find the file
state_manager_path = repo_root / "config" / categories_filename_legacy
if state_manager_path.exists():
    print(f"   - ✅ State manager will find: {categories_filename_legacy}")
else:
    print(f"   - ❌ ERROR: State manager file missing: {categories_filename_legacy}")
```

---

### Alternative Quick Fix (Temporary Testing)

**If immediate testing needed:**

```bash
# Quick workaround: Copy file with state manager's expected name
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

# Copy (don't rename, keep both)
cp config/angelwholesale_workflow_categories.json config/angelwholesale_categories.json

# Verify both exist
ls -la config/angelwholesale*categories.json

# Test runner
python run_custom_angelwholesale-co-uk.py
```

---

## What NOT to Fix

### Do NOT Modify State Manager

**File:** `utils/fixed_enhanced_state_manager.py`  
**Status:** 🔒 **WORKING PRODUCTION CODE - DO NOT MODIFY**

**Why NOT:**
1. ✅ State manager works correctly for existing suppliers (poundwholesale, clearance-king)
2. ✅ Bug only affects NEW supplier onboarding
3. ✅ Proper fix is at source (wizard generates wrong filename)
4. ✅ Modifying state manager risks breaking working suppliers

**Tempting "Fixes" to AVOID:**

❌ **Don't change path construction (line 3030):**
```python
# DO NOT DO THIS:
config_path = f"{self.supplier_name.replace('.co.uk', '')}_workflow_categories.json"
# This would break existing suppliers
```

❌ **Don't add empty list handling (lines 2998-3002):**
```python
# DO NOT DO THIS:
def _first_incomplete_index_by_url(...):
    if not manifest_urls:
        return 1
# This masks the real issue
```

---

### Do NOT Modify Workflow Script

**File:** `tools/passive_extraction_workflow_latest.py`  
**Status:** 🔒 **WORKING PRODUCTION CODE - DO NOT MODIFY**

**Why NOT:**
- Works correctly with all existing suppliers
- Issue is upstream (wrong filename generated)

---

## Implementation Steps

### Phase 1: Wizard Modifications (CRITICAL)

1. **Locate category file creation in wizard:**
   ```bash
   # Search for this pattern in wizard:
   grep -n "categories.json" utils/supplier_onboarding_wizard.py
   ```

2. **Find function that creates category config:**
   - Look for function like `create_category_config()` or similar
   - Should be where it saves category_urls to JSON file

3. **Apply dual-filename fix:**
   - Replace single file creation with dual creation
   - Use code from "Fix 1" section above

4. **Add validation:**
   - Insert validation code after file creation
   - Use code from "Fix 2" section above

---

### Phase 2: Test Wizard (IMPORTANT)

```bash
# Delete old generated files
rm run_custom_angelwholesale-co-uk.py
rm config/angelwholesale*.json

# Run wizard with modifications
python utils/supplier_onboarding_wizard.py \
  --input temp/angelwholesale_session_input.json \
  --output temp/angelwholesale_test_output.json

# Verify BOTH category files created
ls -la config/angelwholesale*categories.json
```

**Expected Output:**
```
✅ Created: angelwholesale_workflow_categories.json
✅ Created: angelwholesale_categories.json (state manager compatibility)

Category file validation:
  - Total URLs: 328
  - Created with both naming patterns:
    • angelwholesale_workflow_categories.json
    • angelwholesale_categories.json
  - ✅ State manager will find: angelwholesale_categories.json
```

---

### Phase 3: Test Runner (CRITICAL)

```bash
# Test runner execution
python run_custom_angelwholesale-co-uk.py
```

**Expected Success Indicators:**
```
2025-11-11 XX:XX:XX - INFO - 📂 Loaded 328 category URLs from config
2025-11-11 XX:XX:XX - INFO - 🎯 START MODE: is_fresh_start=False, pci=1, session_cursor=1
2025-11-11 XX:XX:XX - INFO - 🚀 Starting workflow for angelwholesale.co.uk...
```

**Should NOT See:**
```
⚠️ Category config file not found: ...
IndexError: list index out of range
```

---

### Phase 4: 20-Second Smoke Test (IMPORTANT)

```bash
# Run for 20 seconds to verify no early crashes
timeout 20 python run_custom_angelwholesale-co-uk.py
```

**Expected Behavior:**
- ✅ Script runs for full 20 seconds
- ✅ No IndexError
- ✅ Category file loaded successfully
- ✅ Workflow begins processing
- ⏱️ Timeout after 20 seconds (normal)

---

## Verification Checklist

### After Wizard Modifications:

- [ ] Wizard creates `angelwholesale_workflow_categories.json`
- [ ] Wizard creates `angelwholesale_categories.json` (same content)
- [ ] Both files contain same 328 category URLs
- [ ] system_config.json references workflow pattern
- [ ] Wizard outputs validation success messages

### After Runner Test:

- [ ] No `IndexError: list index out of range`
- [ ] Log shows: `📂 Loaded X category URLs from config`
- [ ] Log shows: `🎯 START MODE: is_fresh_start=False`
- [ ] Workflow begins processing categories
- [ ] No crashes in first 20 seconds

### Template Fixes (Already Verified):

- [x] No TypeError: workflow_key (constructor fixed)
- [x] No AttributeError: close() (browser persistence fixed)
- [x] No RuntimeError: event loop closed (Windows loop fixed)
- [x] Runner script 135 lines (compliant)

### Skill Structure (Already Verified):

- [x] Location: `.claude/skills/supplier-onboarding/` ✅
- [x] Format: SKILL.md with YAML frontmatter ✅
- [x] Structure: docs/, sample_data/, templates/ ✅
- [x] Follows Context7/Anthropic best practices ✅

---

## Status Summary

### Completed (Previous Session):

| Component | Status | Details |
|-----------|--------|---------|
| Template Constructor | ✅ DONE | No workflow_key parameter |
| Template Browser Logic | ✅ DONE | Browser persistence, no close() |
| Template Event Loop | ✅ DONE | Windows Python 3.13+ compatibility |
| Template Line Count | ✅ DONE | 135 lines (compliant) |
| Skill Structure | ✅ DONE | Follows best practices |

### Required (Current Session):

| Component | Status | Action |
|-----------|--------|--------|
| Wizard Category Naming | 🔴 PENDING | Create both filename patterns |
| Category File Validation | 🟡 PENDING | Add post-creation validation |
| State Manager | 🔒 NO ACTION | Working correctly, preserve |
| Workflow Script | 🔒 NO ACTION | Working correctly, preserve |

### Not Required:

| Component | Status | Reason |
|-----------|--------|--------|
| Unicode Error | ⚠️ IGNORE | Cosmetic only |
| Empty List Bug | 🔒 LEAVE | Fix at source (wizard) |

---

## Success Criteria

**System is Ready When:**

1. ✅ Wizard creates category file with BOTH naming patterns
2. ✅ Runner executes without IndexError
3. ✅ Categories loaded successfully from config
4. ✅ Workflow begins processing
5. ✅ No crashes in 20-second test
6. ✅ All template fixes remain working

**Then Proceed To:**
- 6-point sanity check
- Full workflow validation
- Production testing

---

## Key Lessons

### Lesson 1: Modify Generator, Not Consumer
When generator creates wrong output, fix the generator (wizard), not all consumers (state manager, workflow).

### Lesson 2: Dual Compatibility
Creating file with BOTH naming patterns ensures compatibility with all code paths without modifying any existing scripts.

### Lesson 3: Preserve Working Code
State manager works correctly for existing suppliers. Modifying it risks breaking working functionality.

### Lesson 4: Cosmetic vs Functional Errors
Unicode thread error is cosmetic (garbled console output). IndexError is functional (system crash). Prioritize accordingly.

---

## Files to Locate in Wizard

**Search for these patterns in `utils/supplier_onboarding_wizard.py`:**

1. Category file creation:
   ```python
   # Look for:
   categories_filename = ...
   # OR
   save_json(...categories...)
   ```

2. Function likely named:
   - `create_category_config()`
   - `generate_categories_file()`
   - `save_categories()`
   - Or similar

3. Location in workflow:
   - After category URLs collected
   - Before system_config.json update
   - Probably in main onboarding sequence

---

**END OF MEMORY**

This comprehensive memory captures all context needed to continue the fix implementation in a new session.