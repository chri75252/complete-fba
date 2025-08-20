# State Consistency Recovery Playbook

**Incident**: State Persistence Inconsistencies  
**Created**: 2025-08-16  
**Status**: Ready for Execution  

## Quick Assessment

### 1. Assess Current State
```bash
# Run diagnostic to capture current state
python scripts/state_dump.py

# Check for critical inconsistencies
python scripts/state_reconcile.py --dry-run
```

**Expected Output**: 
- Inconsistency count and types
- Backup location confirmation
- Repair plan summary

### 2. Validate System Health
```bash
# Check if main state file is accessible
python -c "import json; json.load(open('OUTPUTS/processing_state.json')); print('✅ State file readable')"

# Verify state manager can load
python -c "from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager; sm = FixedEnhancedStateManager(); print('✅ State manager functional')"
```

## Recovery Procedures

### Procedure A: Standard Reconciliation (Recommended)

**When to use**: Normal inconsistencies detected, system otherwise functional

```bash
# Step 1: Create diagnostic snapshot
python scripts/state_dump.py > recovery_assessment.log

# Step 2: Run dry-run reconciliation
python scripts/state_reconcile.py --dry-run

# Step 3: Review planned changes
# Check the output for reasonableness

# Step 4: Apply reconciliation
python scripts/state_reconcile.py

# Step 5: Validate repair
python scripts/state_dump.py
```

**Success Criteria**:
- ✅ `products_extracted_total == successful_products`
- ✅ `current_category_url` consistent across sections
- ✅ `current_category_index` consistent across sections
- ✅ No invariant violations reported

### Procedure B: Manual State Repair (Advanced)

**When to use**: Reconciliation script fails or complex corruption detected

```bash
# Step 1: Create backup
mkdir -p artifacts/backups/manual_$(date +%Y%m%d_%H%M%S)
cp OUTPUTS/processing_state.json artifacts/backups/manual_$(date +%Y%m%d_%H%M%S)/

# Step 2: Extract key values
python -c "
import json
with open('OUTPUTS/processing_state.json') as f:
    state = json.load(f)
    print('successful_products:', state.get('successful_products', 0))
    sep = state.get('supplier_extraction_progress', {})
    print('current_category_url:', sep.get('current_category_url', ''))
    print('current_category_index:', sep.get('current_category_index', 0))
"

# Step 3: Apply manual fixes using Python
python -c "
import json
with open('OUTPUTS/processing_state.json') as f:
    state = json.load(f)

# Fix product count mismatch
successful = state.get('successful_products', 0)
state.setdefault('supplier_extraction_progress', {})['products_extracted_total'] = successful

# Ensure URL consistency (use supplier_extraction_progress as source of truth)
sep = state.get('supplier_extraction_progress', {})
sp = state.setdefault('system_progression', {})
if 'current_category_url' in sep:
    sp['current_category_url'] = sep['current_category_url']
if 'current_category_index' in sep:
    sp['current_category_index'] = sep['current_category_index']

# Save atomically
import os
temp_file = 'OUTPUTS/processing_state.json.tmp'
with open(temp_file, 'w') as f:
    json.dump(state, f, indent=2)
os.replace(temp_file, 'OUTPUTS/processing_state.json')
print('✅ Manual repair completed')
"

# Step 4: Validate
python scripts/state_dump.py
```

### Procedure C: Emergency Reset (Last Resort)

**When to use**: State file corrupted beyond repair, system cannot start

⚠️ **WARNING**: This will reset processing progress

```bash
# Step 1: Backup corrupted state
mkdir -p artifacts/backups/emergency_$(date +%Y%m%d_%H%M%S)
cp OUTPUTS/processing_state.json artifacts/backups/emergency_$(date +%Y%m%d_%H%M%S)/corrupted_state.json

# Step 2: Reset to minimal valid state
python -c "
import json
from datetime import datetime

minimal_state = {
    'schema_version': '1.1_FIXED',
    'created_at': datetime.now().isoformat(),
    'last_updated': datetime.now().isoformat(),
    'supplier_name': 'poundwholesale.co.uk',
    'resumption_index': 0,
    'total_products': 0,
    'successful_products': 0,
    'supplier_extraction_progress': {
        'current_category_url': '',
        'current_category_index': 0,
        'products_extracted_total': 0,
        'total_products_in_current_category': 0,
        'current_product_index_in_category': 0
    },
    'system_progression': {
        'current_phase': 'supplier',
        'current_category_url': '',
        'current_category_index': 0
    },
    'processed_products': {}
}

with open('OUTPUTS/processing_state.json', 'w') as f:
    json.dump(minimal_state, f, indent=2)

print('✅ Emergency reset completed - system will start fresh')
"
```

## Validation Steps

### Post-Recovery Validation
```bash
# 1. Run full diagnostic
python scripts/state_dump.py

# 2. Check invariants
python -c "
import json
with open('OUTPUTS/processing_state.json') as f:
    state = json.load(f)

sep = state.get('supplier_extraction_progress', {})
sp = state.get('system_progression', {})

# Check product count consistency
products_extracted = sep.get('products_extracted_total', 0)
successful = state.get('successful_products', 0)
assert products_extracted == successful, f'Product count mismatch: {products_extracted} != {successful}'

# Check URL consistency
sep_url = sep.get('current_category_url', '')
sp_url = sp.get('current_category_url', '')
if sep_url and sp_url:
    assert sep_url == sp_url, f'URL mismatch: {sep_url} != {sp_url}'

# Check index consistency  
sep_idx = sep.get('current_category_index')
sp_idx = sp.get('current_category_index')
if sep_idx is not None and sp_idx is not None:
    assert sep_idx == sp_idx, f'Index mismatch: {sep_idx} != {sp_idx}'

print('✅ All invariants validated')
"

# 3. Test state manager functionality
python -c "
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
sm = FixedEnhancedStateManager()
sm.load_state()
print('✅ State manager can load state successfully')
print(f'Current category URL: {sm.get_current_category_url()}')
"
```

### Resume Functionality Test
```bash
# Test that system can resume properly
python -c "
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
sm = FixedEnhancedStateManager()
sm.load_state()

# Get resume point
resume_data = sm.calculate_resume_data()
print('✅ Resume calculation successful')
print(f'Resume index: {resume_data.get(\"resumption_index\", 0)}')
print(f'Current category: {resume_data.get(\"current_category_url\", \"None\")}')
"
```

## Prevention Measures

### 1. Add State Validation to Workflow
Add this check at workflow startup:
```python
# In passive_extraction_workflow_latest.py
def validate_state_consistency(self):
    state_data = self.state_manager.state_data
    sep = state_data.get("supplier_extraction_progress", {})
    
    # Check product count consistency
    products_extracted = sep.get("products_extracted_total", 0)
    successful = state_data.get("successful_products", 0)
    
    if products_extracted != successful:
        self.log.warning(f"🚨 State inconsistency detected: products_extracted_total ({products_extracted}) != successful_products ({successful})")
        # Auto-repair
        sep["products_extracted_total"] = successful
        self.state_manager.save_state_atomic()
        self.log.info("✅ Auto-repaired product count inconsistency")
```

### 2. Implement Atomic State Updates
Replace multiple separate updates with single atomic operations:
```python
# Instead of:
# self.state_data["supplier_extraction_progress"]["current_category_url"] = url
# self.state_data["system_progression"]["current_category_url"] = url

# Use:
def update_category_atomic(self, url, index):
    with self._state_lock:
        self.state_data["supplier_extraction_progress"]["current_category_url"] = url
        self.state_data["supplier_extraction_progress"]["current_category_index"] = index
        self.state_data["system_progression"]["current_category_url"] = url  
        self.state_data["system_progression"]["current_category_index"] = index
        self.save_state_atomic()
```

### 3. Add Invariant Checks
```python
def validate_invariants(self):
    """Validate state invariants before saving"""
    sep = self.state_data.get("supplier_extraction_progress", {})
    sp = self.state_data.get("system_progression", {})
    
    # Invariant 1: Product counts must match
    products_extracted = sep.get("products_extracted_total", 0)
    successful = self.state_data.get("successful_products", 0)
    assert products_extracted == successful, f"Product count invariant violated"
    
    # Invariant 2: URLs must be consistent
    sep_url = sep.get("current_category_url", "")
    sp_url = sp.get("current_category_url", "")
    if sep_url and sp_url:
        assert sep_url == sp_url, f"URL consistency invariant violated"
    
    return True
```

## Monitoring

### Health Check Command
```bash
# Add to system monitoring
python scripts/state_dump.py --health-check
```

### Automated Repair
```bash
# Add to cron/scheduled tasks
python scripts/state_reconcile.py --dry-run --alert-on-issues
```

---

**Recovery Playbook Version**: 1.0  
**Last Updated**: 2025-08-16  
**Tested**: Ready for validation  
**Contact**: System Administrator