# State Consistency Recovery Playbook

## 🚨 CRITICAL: State Persistence Failure Recovery

### Problem Summary
Multiple state files with contradictory data:
- Main state shows 2337 products, Cache shows 8386 products
- Index inconsistencies (3097 vs 0)
- Timestamp format mismatches
- No single source of truth

### Assessment Commands

#### 1. Diagnose Current State
```bash
# Run diagnostic analysis
python scripts/state_dump.py

# Check for multiple state files
find OUTPUTS -name "*state*.json" -type f

# Verify state manager configuration
python -c "from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager; print('State manager imports OK')"
```

#### 2. Backup Current State
```bash
# Create timestamped backup
mkdir -p artifacts/recovery/$(date +%Y%m%d_%H%M%S)
cp OUTPUTS/processing_state.json artifacts/recovery/$(date +%Y%m%d_%H%M%S)/
cp OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json artifacts/recovery/$(date +%Y%m%d_%H%M%S)/
```

### Recovery Options

#### Option A: Choose Single Source of Truth (RECOMMENDED)
```bash
# Use cache state as SoT (more recent, more complete)
python scripts/state_reconcile.py --source cache --dry-run
python scripts/state_reconcile.py --source cache --apply
```

#### Option B: Merge States Intelligently
```bash
# Merge with conflict resolution
python scripts/state_reconcile.py --merge --dry-run
python scripts/state_reconcile.py --merge --apply
```

#### Option C: Fresh Start with Data Preservation
```bash
# Preserve processed products, reset indices
python scripts/state_reconcile.py --fresh-start --preserve-products --dry-run
python scripts/state_reconcile.py --fresh-start --preserve-products --apply
```

### Validation Steps

#### 1. Verify State Consistency
```bash
# Run invariant checks
python scripts/state_verify.py

# Check single source of truth
find OUTPUTS -name "*state*.json" -type f | wc -l  # Should be 1
```

#### 2. Test Resume Functionality
```bash
# Simulate resume
python scripts/test_resume.py --dry-run
```

#### 3. Validate Metrics
```bash
# Check product counts match
python -c "
import json
with open('OUTPUTS/processing_state.json') as f:
    state = json.load(f)
print(f'Products: {state.get(\"successful_products\", 0)}')
print(f'Total: {state.get(\"total_products\", 0)}')
"
```

### Emergency Rollback

If recovery fails:
```bash
# Restore from backup
BACKUP_DIR=$(ls -1t artifacts/recovery/ | head -1)
cp artifacts/recovery/$BACKUP_DIR/processing_state.json OUTPUTS/
cp artifacts/recovery/$BACKUP_DIR/poundwholesale_co_uk_processing_state.json OUTPUTS/CACHE/processing_states/
```

### Prevention Measures

1. **Single State File**: Enforce one canonical state file
2. **Atomic Operations**: All state updates must be atomic
3. **Invariant Checks**: Validate state consistency on every save
4. **Backup Strategy**: Automatic backups before state changes
5. **Monitoring**: Alert on state file proliferation

### Success Criteria

- [ ] Only one state file exists
- [ ] All product counts consistent
- [ ] Timestamps use consistent format
- [ ] Resume functionality works
- [ ] Invariant checks pass
- [ ] No data loss occurred