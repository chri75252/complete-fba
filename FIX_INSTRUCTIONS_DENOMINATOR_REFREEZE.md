# Fix Instructions: Denominator Re-Freeze Bug

**Issue**: Category denominators being frozen twice - correct value (58) overwritten by filtered worklist size (2)
**Impact**: Categories marked complete at 3.4% instead of 100%
**Priority**: CRITICAL (P0)
**Estimated Time**: 15 minutes
**Risk Level**: LOW (surgical removal of duplicate code)

---

## Quick Start: 3-Step Fix

### Step 1: Remove Second Freeze Call (CRITICAL)
**File**: `tools/passive_extraction_workflow_latest.py`
**Lines**: 5468-5474

**REMOVE THIS CODE**:
```python
supplier_total = len(needs_full_extraction_urls)
amazon_total = len(needs_amazon_only_urls) + supplier_total
if supplier_total == 0 and amazon_total == 0:
    self.log.info("🟦 Empty category after filters → marking complete and advancing PCI")
    self.state_manager.mark_category_completed(category_url, absolute_cat_index)
    continue

# Set the frozen denominators up-front so Amazon never stays at 0
try:
    self.state_manager.set_frozen_denominator(
        category_url,
        discovered_count=len(needs_full_extraction_urls),
        manifest_urls=urls_for_manifest,
    )
except Exception as e:
    self.log.warning(f"Failed to set frozen denominator: {e}")
```

**REPLACE WITH THIS CODE**:
```python
# Get existing frozen denominator (already set at line 5109 with correct value)
frozen_denom = self.state_manager.get_frozen_denominator(category_url)
if not frozen_denom:
    # Fallback to manifest total if somehow not frozen yet
    frozen_denom = len(urls_for_manifest)
    self.log.warning(
        f"⚠️ Denominator not frozen for {category_url}! Using manifest total: {frozen_denom}"
    )

# Validate: Ensure frozen value matches manifest
if frozen_denom != len(urls_for_manifest):
    self.log.error(
        f"🚨 DENOMINATOR MISMATCH: Frozen={frozen_denom}, "
        f"Manifest={len(urls_for_manifest)}, Category={category_url}. "
        f"Using frozen value as authoritative (first freeze wins)."
    )

supplier_total = frozen_denom  # Use correct frozen value
amazon_total = frozen_denom    # Both phases use same denominator

# Check for empty category AFTER getting frozen denominator
if supplier_total == 0 and amazon_total == 0:
    self.log.info(f"🟦 Empty category after filters → marking complete and advancing PCI")
    self.state_manager.mark_category_completed(category_url, absolute_cat_index)
    continue
```

---

### Step 2: Strengthen Freeze Guard (IMPORTANT)
**File**: `utils/fixed_enhanced_state_manager.py`
**Lines**: 776-778

**CURRENT CODE**:
```python
def set_frozen_denominator(
    self,
    category_url: str,
    discovered_count: int,
    manifest_urls: Optional[List[str]] = None,
    amazon_total: Optional[int] = None,
) -> bool:
    """Set frozen denominator for a category (write-once)."""
    # Guard: only allow first freeze for this category
    if self.is_category_denominator_frozen(category_url):
        self.log.warning(f"🔒 FREEZE_GUARD_VIOLATION: Attempted re-freeze of {category_url}")
        return False
```

**REPLACE WITH**:
```python
def set_frozen_denominator(
    self,
    category_url: str,
    discovered_count: int,
    manifest_urls: Optional[List[str]] = None,
    amazon_total: Optional[int] = None,
) -> bool:
    """Set frozen denominator for a category (write-once - enforced)."""
    # Guard: only allow first freeze for this category
    if self.is_category_denominator_frozen(category_url):
        existing = self.get_frozen_denominator(category_url)
        error_msg = (
            f"🚨 FREEZE_GUARD_VIOLATION: Category {category_url} already frozen at {existing} products. "
            f"Attempted to re-freeze with {discovered_count}. "
            f"Denominators are write-once and cannot be changed after initial freeze. "
            f"This indicates a critical bug in the workflow logic."
        )
        self.log.error(error_msg)
        raise ValueError(error_msg)  # Enforce with exception
```

---

### Step 3: Verify Fix with Test Run
**Command**:
```bash
python run_custom_poundwholesale.py
```

**Expected Output**:
```
✅ No FREEZE_GUARD_VIOLATION warnings
✅ RESUME PTR shows correct denominator (58, not 2)
✅ Category completion at 100% (58/58), not 3.4% (2/2)
✅ All 58 products processed or skipped with reason
```

**Failure Indicators**:
```
❌ FREEZE_GUARD_VIOLATION: Attempted re-freeze... (Should NOT appear)
❌ RESUME PTR: prod_idx=0/2 (Should be 0/58)
❌ Category marked complete after 2 products (Should process/skip all 58)
```

---

## Detailed Implementation Guide

### Part 1: Code Changes

#### Change 1.1: Remove Second Freeze Call
**Location**: `tools/passive_extraction_workflow_latest.py:5468-5474`

**Before** (11 lines):
```python
supplier_total = len(needs_full_extraction_urls)
amazon_total = len(needs_amazon_only_urls) + supplier_total
if supplier_total == 0 and amazon_total == 0:
    self.log.info("🟦 Empty category after filters → marking complete and advancing PCI")
    self.state_manager.mark_category_completed(category_url, absolute_cat_index)
    continue

# Set the frozen denominators up-front so Amazon never stays at 0
try:
    self.state_manager.set_frozen_denominator(
        category_url,
        discovered_count=len(needs_full_extraction_urls),
        manifest_urls=urls_for_manifest,
    )
except Exception as e:
    self.log.warning(f"Failed to set frozen denominator: {e}")

sp = self.state_manager.state_data.setdefault("system_progression", {})
```

**After** (20 lines):
```python
# Get existing frozen denominator (already set at line 5109 with correct value)
frozen_denom = self.state_manager.get_frozen_denominator(category_url)
if not frozen_denom:
    # Fallback to manifest total if somehow not frozen yet
    frozen_denom = len(urls_for_manifest)
    self.log.warning(
        f"⚠️ Denominator not frozen for {category_url}! Using manifest total: {frozen_denom}"
    )

# Validate: Ensure frozen value matches manifest
if frozen_denom != len(urls_for_manifest):
    self.log.error(
        f"🚨 DENOMINATOR MISMATCH: Frozen={frozen_denom}, "
        f"Manifest={len(urls_for_manifest)}, Category={category_url}. "
        f"Using frozen value as authoritative (first freeze wins)."
    )

supplier_total = frozen_denom  # Use correct frozen value
amazon_total = frozen_denom    # Both phases use same denominator

# Check for empty category AFTER getting frozen denominator
if supplier_total == 0 and amazon_total == 0:
    self.log.info(f"🟦 Empty category after filters → marking complete and advancing PCI")
    self.state_manager.mark_category_completed(category_url, absolute_cat_index)
    continue

sp = self.state_manager.state_data.setdefault("system_progression", {})
```

#### Change 1.2: Strengthen Freeze Guard
**Location**: `utils/fixed_enhanced_state_manager.py:776-778`

**Before** (3 lines):
```python
    if self.is_category_denominator_frozen(category_url):
        self.log.warning(f"🔒 FREEZE_GUARD_VIOLATION: Attempted re-freeze of {category_url}")
        return False
```

**After** (11 lines):
```python
    if self.is_category_denominator_frozen(category_url):
        existing = self.get_frozen_denominator(category_url)
        error_msg = (
            f"🚨 FREEZE_GUARD_VIOLATION: Category {category_url} already frozen at {existing} products. "
            f"Attempted to re-freeze with {discovered_count}. "
            f"Denominators are write-once and cannot be changed after initial freeze. "
            f"This indicates a critical bug in the workflow logic."
        )
        self.log.error(error_msg)
        raise ValueError(error_msg)  # Enforce with exception
```

---

### Part 2: Testing & Verification

#### Test 1: Unit Test - Freeze Guard Enforcement
**File**: `tests/test_freeze_guard_enforcement.py`

```python
import pytest
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_freeze_guard_prevents_refreeze():
    """Verify freeze guard raises exception on re-freeze attempt."""
    state_manager = FixedEnhancedStateManager("test-supplier", output_dir="./test_output")

    # First freeze should succeed
    category_url = "https://test.com/category1"
    result = state_manager.set_frozen_denominator(category_url, 58)
    assert result == True
    assert state_manager.get_frozen_denominator(category_url) == 58

    # Second freeze should raise ValueError
    with pytest.raises(ValueError, match="FREEZE_GUARD_VIOLATION"):
        state_manager.set_frozen_denominator(category_url, 2)

    # Verify value unchanged after failed re-freeze
    assert state_manager.get_frozen_denominator(category_url) == 58

def test_freeze_guard_error_message_contains_details():
    """Verify error message includes existing and attempted values."""
    state_manager = FixedEnhancedStateManager("test-supplier", output_dir="./test_output")

    category_url = "https://test.com/category2"
    state_manager.set_frozen_denominator(category_url, 100)

    with pytest.raises(ValueError) as exc_info:
        state_manager.set_frozen_denominator(category_url, 50)

    error_message = str(exc_info.value)
    assert "already frozen at 100 products" in error_message
    assert "Attempted to re-freeze with 50" in error_message
    assert "write-once" in error_message.lower()
```

**Run Test**:
```bash
pytest tests/test_freeze_guard_enforcement.py -v
```

**Expected Output**:
```
tests/test_freeze_guard_enforcement.py::test_freeze_guard_prevents_refreeze PASSED
tests/test_freeze_guard_enforcement.py::test_freeze_guard_error_message_contains_details PASSED
```

---

#### Test 2: Integration Test - Full Category Processing
**File**: `tests/test_category_completion_accuracy.py`

```python
import pytest
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow

def test_category_completion_with_filtering():
    """Verify category tracks all products, not just remaining work."""
    workflow = PassiveExtractionWorkflow(
        supplier_name="poundwholesale.co.uk",
        output_dir="./test_output",
        use_predefined_categories=True,
        system_config={"max_products_per_category": 1000}
    )

    # Simulate category with 58 products total:
    # - 55 already in linking map (skip)
    # - 1 in cache (Amazon only)
    # - 2 need full extraction
    category_url = "https://www.poundwholesale.co.uk/toys/wholesale-big-boys-toys-gadgets"

    # Run workflow
    workflow.run()

    # Verify: Denominator is 58, not 2
    frozen_denom = workflow.state_manager.get_frozen_denominator(category_url)
    assert frozen_denom == 58, f"Expected denominator 58, got {frozen_denom}"

    # Verify: Category NOT marked complete after processing 2 products
    # (unless all 58 are accounted for in linking map + cache + processed)
    is_complete = workflow.state_manager.is_category_complete(category_url)

    if is_complete:
        # If marked complete, verify it's because all 58 are accounted for
        linking_map_count = 55  # From pre-test setup
        cache_count = 1
        processed_count = 2
        total_accounted = linking_map_count + cache_count + processed_count
        assert total_accounted == frozen_denom, (
            f"Category marked complete but only {total_accounted}/{frozen_denom} accounted for"
        )
```

**Run Test**:
```bash
pytest tests/test_category_completion_accuracy.py -v
```

**Expected Output**:
```
tests/test_category_completion_accuracy.py::test_category_completion_with_filtering PASSED
```

---

#### Test 3: End-to-End Test - Resume Pointer Accuracy
**File**: `tests/test_resume_pointer_accuracy.py`

```python
def test_resume_pointer_uses_correct_denominator():
    """Verify resume pointer always shows X/58, never X/2."""
    workflow = PassiveExtractionWorkflow(
        supplier_name="poundwholesale.co.uk",
        output_dir="./test_output",
        use_predefined_categories=True
    )

    category_url = "https://www.poundwholesale.co.uk/toys/wholesale-big-boys-toys-gadgets"

    # Process 2 products
    workflow.run()  # Processes until 2 products extracted

    # Get resume pointer
    state_manager = workflow.state_manager
    resume_info = state_manager.get_resume_pointer()

    # Verify denominator is 58, not 2
    assert resume_info["total_products"] == 58, (
        f"Resume pointer shows wrong denominator: {resume_info['total_products']}"
    )

    # Verify progress percentage is correct
    progress_pct = (resume_info["prod_idx"] / resume_info["total_products"]) * 100
    assert progress_pct < 10, (  # Should be ~3.4%, not 100%
        f"Progress shows {progress_pct}% (expected <10% after 2 products)"
    )
```

**Run Test**:
```bash
pytest tests/test_resume_pointer_accuracy.py -v
```

---

### Part 3: Deployment Checklist

#### Pre-Deployment
- [ ] Create backup of current codebase
  ```bash
  mkdir backup/denominator_fix_$(date +%Y%m%d)
  cp -r tools/passive_extraction_workflow_latest.py backup/denominator_fix_$(date +%Y%m%d)/
  cp -r utils/fixed_enhanced_state_manager.py backup/denominator_fix_$(date +%Y%m%d)/
  ```

- [ ] Run existing test suite to establish baseline
  ```bash
  pytest tests/ -v > test_baseline.log
  ```

- [ ] Review changes in diff tool
  ```bash
  git diff tools/passive_extraction_workflow_latest.py
  git diff utils/fixed_enhanced_state_manager.py
  ```

#### Deployment
- [ ] Apply Change 1.1: Remove second freeze call
- [ ] Apply Change 1.2: Strengthen freeze guard
- [ ] Run new unit tests
  ```bash
  pytest tests/test_freeze_guard_enforcement.py -v
  ```
- [ ] Run integration tests
  ```bash
  pytest tests/test_category_completion_accuracy.py -v
  pytest tests/test_resume_pointer_accuracy.py -v
  ```

#### Post-Deployment Verification
- [ ] Run test extraction on poundwholesale.co.uk
  ```bash
  python run_custom_poundwholesale.py 2>&1 | tee test_run.log
  ```

- [ ] Verify log output:
  ```bash
  # Should find NO violations
  grep "FREEZE_GUARD_VIOLATION" test_run.log

  # Should show correct denominators (58, not 2)
  grep "FROZEN DENOMINATOR" test_run.log

  # Should show correct resume pointers (X/58, not X/2)
  grep "RESUME PTR" test_run.log
  ```

- [ ] Check processing state file:
  ```bash
  python -m json.tool OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json | grep -A3 "frozen_category_denominators"
  ```

- [ ] Verify financial report completeness:
  ```bash
  # Compare product counts in linking map vs financial report
  python -c "
  import json
  with open('OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json') as f:
      linking = json.load(f)
  print(f'Linking map entries: {len(linking)}')
  "
  ```

#### Rollback Plan (If Needed)
If issues detected:
```bash
# Restore backup
cp backup/denominator_fix_$(date +%Y%m%d)/passive_extraction_workflow_latest.py tools/
cp backup/denominator_fix_$(date +%Y%m%d)/fixed_enhanced_state_manager.py utils/

# Clear corrupted state
rm OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json

# Restart from clean state
python run_custom_poundwholesale.py
```

---

## Troubleshooting Guide

### Issue 1: ValueError Raised During Normal Operation
**Symptom**: `ValueError: FREEZE_GUARD_VIOLATION` raised unexpectedly

**Diagnosis**:
```bash
# Check if denominator was already frozen correctly
python -c "
import json
with open('OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json') as f:
    state = json.load(f)
print('Frozen denominators:', state.get('frozen_category_denominators', {}))
"
```

**Resolution**:
- If denominator exists and matches manifest: This is correct behavior - the fix is working
- If exception raised during first freeze: Check if state file is corrupted - delete and restart
- If exception raised after resume: Verify state file has correct frozen values

---

### Issue 2: Denominator Mismatch Warning
**Symptom**: `DENOMINATOR MISMATCH: Frozen=X, Manifest=Y`

**Diagnosis**:
- Check log for first freeze location (should be line 5109)
- Verify manifest generation completed successfully
- Check for any resume/restart between manifest and freeze

**Resolution**:
- System will use frozen value as authoritative (correct behavior)
- Investigate why manifest count changed (pagination issue?)
- Consider re-scraping category if mismatch is large

---

### Issue 3: No Frozen Denominator Warning
**Symptom**: `Denominator not frozen for {url}! Using manifest total`

**Diagnosis**:
- Check if first freeze at line 5109 was skipped
- Verify category initialization completed
- Look for exceptions during manifest generation

**Resolution**:
- System will fallback to manifest total (safe)
- Investigate why first freeze didn't occur
- Add defensive logging around line 5109

---

## Success Criteria

### Fix is Successful When:

1. **No Violations**: Zero `FREEZE_GUARD_VIOLATION` warnings in logs
2. **Correct Denominators**: All resume pointers show X/58, none show X/2
3. **Complete Processing**: Category marked complete only after all 58 products processed/skipped
4. **Accurate Metrics**: Financial report includes all profitable products
5. **Consistent State**: Frozen denominators match manifest totals

### Metrics to Monitor:

```bash
# After fix deployment, monitor these metrics:

# 1. Category completion percentage distribution
grep "Category.*complete" logs/*.log | awk '{print $NF}' | sort | uniq -c

# 2. Denominator values distribution
grep "FROZEN DENOMINATOR" logs/*.log | grep -oP '\d+ products' | sort | uniq -c

# 3. Resume pointer denominators
grep "RESUME PTR" logs/*.log | grep -oP 'prod_idx=\d+/\d+' | awk -F'/' '{print $2}' | sort | uniq -c

# 4. Product processing counts per category
grep "products need full extraction" logs/*.log | awk '{print $(NF-3)}' | sort -n | uniq -c
```

**Expected Distributions**:
- Category completion: Mix of percentages (not all 100% after 2 products)
- Denominator values: Match manifest totals (10-100+ range, not just 1-3)
- Resume pointers: Denominators match manifest totals
- Processing counts: Small numbers (2-10) - filtered subset of larger totals

---

## Contact & Support

**Issue Severity**: CRITICAL (P0)
**Fix Complexity**: LOW
**Deployment Risk**: LOW
**Testing Time**: 30 minutes
**Total Implementation Time**: 1 hour

**Questions or Issues?**
- Check logs in `OUTPUTS/DIAGNOSTICS/`
- Review state file: `OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json`
- Run diagnostic: `python utils/fixed_enhanced_state_manager.py --validate-state`

---

**Last Updated**: October 14, 2025
**Status**: Ready for Implementation
**Reviewed By**: Root Cause Analysis Agent
