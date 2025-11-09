# CRITICAL: File Corruption Incident - November 9, 2025

## 🚨 IMMEDIATE ACTION REQUIRED

**System Status**: ❌ **NON-FUNCTIONAL** - Both entry points crash on import

**Corrupted Files Blocking System**:
1. `utils/hash_lookup_optimizer.py` - 4,753 NUL bytes (21.2% corrupted)
2. `utils/file_manager.py` - 4,205 NUL bytes (35.1% corrupted)

**Error Signature**:
```python
from utils.hash_lookup_optimizer import HashLookupOptimizer, LegacyPerformanceComparator
SyntaxError: source code string cannot contain null bytes
```

**Both entry points FAIL**:
- `run_custom_clearance_king.py` → Crash at line 22
- `run_custom_poundwholesale.py` → Crash at line 22

---

## ✅ IMMEDIATE RESTORATION COMMANDS

```bash
# Restore from verified clean git commit 7108d237
git show 7108d237:utils/hash_lookup_optimizer.py > utils/hash_lookup_optimizer.py
git show 7108d237:utils/file_manager.py > utils/file_manager.py

# Verify restoration
python -c "from utils.hash_lookup_optimizer import HashLookupOptimizer; print('✅ hash_lookup_optimizer restored')"
python -c "from utils.file_manager import FileManager; print('✅ file_manager restored')"

# Test entry points
python run_custom_poundwholesale.py --help
```

---

## 📋 CORRUPTION HISTORY

### Phase 1: Original Corruption (Already Restored)
**Date**: Unknown (discovered Nov 9, 2025)  
**Files**:
- `tools/authentication_manager.py` → 8,732 NUL bytes (54.4%) → ✅ Restored from sibling directory
- `tools/cache_manager.py` → 5,434 NUL bytes (12.9%) → ✅ Restored from sibling directory  
- `utils/path_manager.py` → 1,240 NUL bytes (7.2%) → ✅ Restored from sibling directory

**Restore Source**: `C:/Users/chris/Desktop/Amazon-FBA-Agent-System-v32 - fully working inifinite mode/`

### Phase 2: Active Corruption (CURRENT)
**Date**: Nov 8, 2025 06:23 (per file timestamps)  
**Files**:
- `utils/hash_lookup_optimizer.py` → 4,753 NUL bytes (21.2%) → ❌ BLOCKING SYSTEM
- `utils/file_manager.py` → 4,205 NUL bytes (35.1%) → ❌ BLOCKING SYSTEM

**Restore Source**: Git commit `7108d237` ("fully functional") - VERIFIED CLEAN

---

## 🔍 ROOT CAUSE ANALYSIS

### Corruption Signature

**All corrupted files contain Python pickle/cache data**:
```
Hex pattern: 633a5c55736572735c63687269735c4465736b746f70...
Decoded: "c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\gap_processing_fixes_20250726_191317\util..."
```

**This indicates**:
- Python `__pycache__` pickle data
- File path index metadata
- Symbol cache database entries

### Most Likely Cause: Git Committed Corrupted Files

**Evidence**:
1. Current `git HEAD` contains corrupted versions
2. Corruption timestamp: Nov 8, 06:23 - multiple files at exact same time
3. Git commit `7108d237` has clean versions (earlier commit)
4. Later commits contain binary data in Python files

**Theory**: 
1. Files corrupted by pickle/cache overwrite (exact trigger unknown)
2. Someone ran `git add -A` which staged BINARY files
3. `git commit` saved corruption to repository
4. Later `git restore` or `git checkout` brought back corruption

### Alternative Theories

1. **Copy operation from wrong backup**:
   ```bash
   cp backup/gap_processing_fixes_20250726_191317/utils/* utils/
   ```
   Would overwrite Python files with cache files if backup contained corruption.

2. **IDE/Serena cache write to wrong location**:
   File handle bug causing cache writes to go to source directories instead of `.serena/cache/`.

**NOT caused by**:
- Serena MCP (confirmed READ-ONLY in project.yml)
- Read-only forensic audit session (no write operations performed)
- Normal git operations (git doesn't write binary data into Python files)

---

## ⚠️ FILES AT RISK

**Currently Clean** (verified Nov 9, 2025):
- `utils/url_cache_filter.py` ✅
- `utils/windows_save_guardian.py` ✅
- `utils/atomic_file_operations.py` ✅
- `utils/browser_circuit_breaker.py` ✅
- `utils/browser_manager.py` ✅
- `utils/logger.py` ✅
- `utils/normalization.py` ✅
- `utils/sentinel_monitor.py` ✅
- `tools/configurable_supplier_scraper.py` ✅
- `tools/amazon_playwright_extractor.py` ✅
- `tools/FBA_Financial_calculator.py` ✅

**Risk Level**: ⚠️ **HIGH** - Corruption pattern can recur until root cause identified.

---

## 🛡️ PREVENTIVE MEASURES (CRITICAL)

### 1. File Integrity Check (Add to Entry Points)

**Add to `run_custom_poundwholesale.py` and `run_custom_clearance_king.py`**:
```python
import os

CRITICAL_FILES = [
    'utils/hash_lookup_optimizer.py',
    'utils/file_manager.py',
    'utils/path_manager.py',
    'tools/cache_manager.py',
    'tools/authentication_manager.py'
]

def verify_file_integrity():
    """Detect binary corruption before imports"""
    for filepath in CRITICAL_FILES:
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'rb') as f:
            first_kb = f.read(1024)
            nul_count = first_kb.count(b'\x00')
            if nul_count > 10:
                raise RuntimeError(
                    f"🚨 CORRUPTED FILE DETECTED: {filepath}\n"
                    f"Contains {nul_count} NUL bytes in first 1KB.\n"
                    f"Restore command: git show 7108d237:{filepath} > {filepath}"
                )

# Call BEFORE any other imports
verify_file_integrity()
```

### 2. Git Pre-Commit Hook

**Create `.git/hooks/pre-commit`** (make executable):
```bash
#!/bin/bash
echo "Checking for binary corruption in Python files..."

for file in $(git diff --cached --name-only | grep '\.py$'); do
    if [ -f "$file" ]; then
        nul_count=$(python3 -c "
with open('$file', 'rb') as f:
    print(f.read().count(b'\x00'))
" 2>/dev/null)
        
        if [ "$nul_count" -gt 10 ]; then
            echo "❌ ERROR: Binary corruption in $file"
            echo "   File contains $nul_count NUL bytes"
            echo "   Cannot commit corrupted file to repository"
            exit 1
        fi
    fi
done

echo "✅ No binary corruption detected"
exit 0
```

### 3. Daily Backup Script

```bash
#!/bin/bash
# backup_critical_files.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup/daily_integrity_backups"
mkdir -p "$BACKUP_DIR"

for file in utils/hash_lookup_optimizer.py utils/file_manager.py utils/path_manager.py; do
    if [ -f "$file" ]; then
        # Check for corruption before backing up
        nul_count=$(python3 -c "with open('$file', 'rb') as f: print(f.read().count(b'\x00'))")
        
        if [ "$nul_count" -lt 10 ]; then
            cp "$file" "$BACKUP_DIR/$(basename $file)_${DATE}"
            echo "✅ Backed up clean: $file"
        else
            echo "⚠️ Skipped corrupted: $file (contains $nul_count NULs)"
        fi
    fi
done
```

---

## 📊 VERIFIED RESTORE SOURCES

### Git Commits with Clean Files

**Primary**: `7108d237` - "fully functional"
- ✅ `utils/hash_lookup_optimizer.py` - 0 NUL bytes, valid Python
- ✅ `utils/file_manager.py` - 0 NUL bytes, valid Python
- ✅ Verified parseable with AST

**Alternatives** (not verified but likely clean):
- `4bf5a7c8` - "Add dashboard functionality and cleanup"
- `bb03fd1b` - "2website-oct5"  
- `c5d05893` - "login issues"

### Sibling Directory (For Phase 1 Files)

**Path**: `C:/Users/chris/Desktop/Amazon-FBA-Agent-System-v32 - fully working inifinite mode/`
- ✅ `tools/authentication_manager.py` - CLEAN
- ✅ `tools/cache_manager.py` - CLEAN
- ✅ `utils/path_manager.py` - CLEAN

---

## 🔧 INVESTIGATION TODO

To prevent future corruption, investigate:

1. **System Events Log** (Nov 8, 2025 ~06:23):
   - Process crashes
   - Out of memory events
   - Disk errors

2. **Recent Script Executions**:
   - Any scripts that create .pkl files
   - Backup/restore scripts
   - Automated sync tools

3. **IDE/Editor Extensions**:
   - Symbol caching behavior
   - Auto-backup features
   - File indexing processes

4. **Git History Review**:
   - When did corruption enter repository?
   - What commits between 7108d237 and current HEAD?
   - Any suspicious commits with binary changes?

5. **Cache File Locations**:
   ```bash
   find . -name "*.pkl" -o -name "*.pyc" | grep -v "venv\|\.git"
   # Ensure all cache files in proper locations (.serena/, __pycache__)
   ```

---

## 📈 SYSTEM VALIDATION AFTER RESTORATION

**Run these checks**:
```bash
# 1. Verify no NUL bytes
python -c "
import os
for f in ['utils/hash_lookup_optimizer.py', 'utils/file_manager.py']:
    with open(f, 'rb') as fp:
        nuls = fp.read().count(b'\x00')
        print(f'{f}: {nuls} NULs - {\"✅ CLEAN\" if nuls < 10 else \"❌ CORRUPTED\"}')"

# 2. Verify imports work
python -c "from utils.hash_lookup_optimizer import HashLookupOptimizer; print('✅ import success')"
python -c "from utils.file_manager import FileManager; print('✅ import success')"

# 3. Verify syntax
python -m py_compile utils/hash_lookup_optimizer.py
python -m py_compile utils/file_manager.py

# 4. Test entry points
python run_custom_poundwholesale.py --help
python run_custom_clearance_king.py --help
```

---

## 🎯 KEY TAKEAWAYS

1. **5 files corrupted total** across 2 phases (3 restored, 2 active)
2. **Root cause unknown** but corruption is committed in git repository
3. **Git commit 7108d237 is last known clean state**
4. **Both entry points blocked** until hash_lookup_optimizer.py restored
5. **High recurrence risk** until preventive measures implemented

**CRITICAL**: Implement file integrity checks IMMEDIATELY after restoration to catch future corruption before it blocks the system.

---

**Memory Created**: November 9, 2025  
**Status**: Active incident requiring immediate restoration  
**Next Session Action**: Execute restoration commands and implement preventive measures