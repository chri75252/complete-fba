# COMPREHENSIVE TEST PROTOCOL - Surgical Fixes Validation
## October 16, 2025

**Objective:** Validate all 6 surgical fixes (A.1, A.2, A.3, B, C, D, E) prevent state reset issues and ensure resumption persistence.

**Core Requirement:** System must continue exactly where it left off when interrupted, with PCI and phase preserved across runs.

---

## 🎯 Expected System Behavior (Reference Specification)

### **Core Principle: "PCI Must Never Decrease"**

**From Initial Prompt:**
> System resets from PCI=5, phase="amazon_analysis" to PCI=1, phase="supplier" between runs

**Expected Behavior After Fixes:**
1. ✅ **PCI Preservation:** If Run #1 ends at PCI=5, Run #2 MUST start at PCI=5 (never PCI=1)
2. ✅ **Phase Preservation:** If Run #1 ends in "amazon_analysis", Run #2 MUST resume in "amazon_analysis"
3. ✅ **Category Skip:** Categories 1-4 must be skipped with clear logging when resuming from PCI=5
4. ✅ **Monotonic Advancement:** PCI can only increase (5→6→7), never decrease (5→4 or 5→1)
5. ✅ **Resumption from Exact Point:** No reprocessing of completed work

---

## 📋 Test Scenarios (3-Scenario Framework)

### **Scenario 1: Resume Mid-Amazon (PRIMARY - Highest Priority)**
Tests: Fixes A.1, A.2, A.3, B, C, D, E

### **Scenario 2: Resume Mid-Supplier**
Tests: Fixes B, C, D

### **Scenario 3: Empty Category**
Tests: Fix C, category completion logic

---

## 🧪 SCENARIO 1: Resume Mid-Amazon (Critical Test)

### **Purpose**
Validate that interrupting during Amazon analysis phase preserves both PCI and phase across runs.

### **Setup Requirements**

1. **Clean State (Optional - for baseline)**
   ```powershell
   # Delete existing state file to start fresh
   Remove-Item "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" -ErrorAction SilentlyContinue
   ```

2. **Configuration Check**
   ```powershell
   # Verify supplier configuration
   type config\poundwholesale_categories.json
   # Should show multiple categories (at least 10)
   ```

---

### **PART A: Run #1 - Process Until Mid-Amazon**

#### **Step 1.A.1: Start Processing**
```powershell
# Navigate to workspace
cd "c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

# Start system
python run_custom_poundwholesale.py
```

#### **Step 1.A.2: Monitor Logs - Watch for Phase Transition**

**What to Watch For:**
```
🎯 WORKFLOW START CURSOR: category_index=1 (pci=1, cursor=1, max=1)
✅ WORKFLOW INITIALIZED: Starting from category 1 in phase 'supplier'

... (supplier extraction logs) ...

🔄 PHASE TRANSITION: supplier → amazon_analysis
🔧 AMAZON PROGRESS: cat=1/X idx=0->Y

... (continue processing through multiple categories) ...

🔧 AMAZON PROGRESS: cat=5/X idx=N->M
```

**Key Indicators:**
- ✅ Phase transition from supplier → amazon_analysis
- ✅ PCI advancing (1→2→3→4→5)
- ✅ Amazon progress being made in category 5

#### **Step 1.A.3: Interrupt at Target State**

**When to Interrupt:**
- **Target:** Category 5 or higher
- **Phase:** Must be in "amazon_analysis"
- **Progress:** Partially through Amazon queue (not 0, not complete)

**How to Interrupt:**
```
Press Ctrl+C in terminal
```

**Expected Shutdown Logs:**
```
^C
KeyboardInterrupt
... (cleanup logs) ...
```

#### **Step 1.A.4: Capture End State (Run #1)**

**Command:**
```powershell
# Copy state file for evidence
Copy-Item "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" -Destination "OUTPUTS\TEST_PROTOCOLS\run1_end_state.json"

# Display critical values
type "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" | Select-String "persistent_category_index|current_phase|amazon_products_completed|supplier_products_completed"
```

**Expected Output (Evidence Source 1 - State File):**
```json
"persistent_category_index": 5,
"current_phase": "amazon_analysis",
"amazon_products_completed": 15,
"supplier_products_completed": 142
```

**Critical Values to Record:**
- `persistent_category_index` = ? (should be ≥5)
- `current_phase` = "amazon_analysis" (MUST be this)
- `amazon_products_completed` = ? (should be >0)
- `current_category_url` = ? (record for comparison)

---

### **PART B: Run #2 - Resume and Validate**

#### **Step 1.B.1: Start Resume**

**Command:**
```powershell
# Start system again (same command)
python run_custom_poundwholesale.py
```

#### **Step 1.B.2: Monitor Startup Logs (CRITICAL)**

**Expected Logs (Evidence Source 2 - Startup Logs):**

```
🔍 STARTUP CHECK: is_fresh_start flag is 'False'
🎯 START MODE: is_fresh_start=False, pci=5, session_cursor=5

🎯 WORKFLOW START CURSOR: category_index=5 (pci=5, cursor=5, max=5)
✅ WORKFLOW INITIALIZED: Starting from category 5 in phase 'amazon_analysis'
```

**✅ PASS Indicators:**
1. `is_fresh_start` = False (not True)
2. `pci` = 5 (matches Run #1 end state)
3. `category_index` = 5 (not 1!)
4. `phase` = "amazon_analysis" (not "supplier"!)

**❌ FAIL Indicators (Would indicate fixes didn't work):**
1. `category_index` = 1 (backslide!)
2. `phase` = "supplier" (phase clobber!)
3. `pci` = 1 (PCI reset!)

#### **Step 1.B.3: Monitor Category Skip Logs (Fix D Validation)**

**Expected Logs (Evidence Source 3 - Skip Logs):**
```
⏭️ SKIP: Category 1 < start 5 (already processed)
⏭️ SKIP: Category 2 < start 5 (already processed)
⏭️ SKIP: Category 3 < start 5 (already processed)
⏭️ SKIP: Category 4 < start 5 (already processed)

🎯 CATEGORY PROCESSING: abs_index=5, display_index=5, url=...
```

**✅ PASS Indicators:**
- Categories 1-4 explicitly skipped with "⏭️ SKIP" messages
- Processing starts at category 5

**❌ FAIL Indicators:**
- No skip messages
- Processing starts at category 1

#### **Step 1.B.4: Monitor Phase Preservation (Fix A.1, A.2, A.3 Validation)**

**Expected Logs (Evidence Source 4 - Phase Logs):**
```
✅ PHASE PRESERVED: 'amazon_analysis' (loaded from state)

📋 CATEGORY INIT COMPLETE:
  PCI (persistent_category_index): 5
  Phase (current_phase): amazon_analysis
  Category URL: ...
```

**✅ PASS Indicators:**
- "PHASE PRESERVED" message appears
- Phase shows "amazon_analysis" throughout
- No "supplier → amazon_analysis" transition (already in amazon)

**❌ FAIL Indicators:**
- Phase shows "supplier"
- Phase transition log appears (would mean phase was reset)

#### **Step 1.B.5: Monitor Progress Continuation**

**Expected Logs (Evidence Source 5 - Progress Logs):**
```
🔧 AMAZON PROGRESS: cat=5/X idx=15->16
🔧 AMAZON PROGRESS: cat=5/X idx=16->17
```

**✅ PASS Indicators:**
- Amazon progress continues from where Run #1 left off
- No reprocessing of products 0-14

#### **Step 1.B.6: Capture Resume State (Run #2)**

**Command:**
```powershell
# Wait ~30 seconds for processing, then Ctrl+C again
# Copy resume state
Copy-Item "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" -Destination "OUTPUTS\TEST_PROTOCOLS\run2_resume_state.json"

# Compare states
fc "OUTPUTS\TEST_PROTOCOLS\run1_end_state.json" "OUTPUTS\TEST_PROTOCOLS\run2_resume_state.json"
```

**Expected Comparison:**
- `persistent_category_index`: SAME or HIGHER (never lower)
- `current_phase`: SAME ("amazon_analysis")
- `amazon_products_completed`: HIGHER (progress advanced)

---

### **PART C: Evidence Collection and Validation**

#### **Step 1.C.1: State File Analysis**

**Command:**
```powershell
# Extract critical fields for comparison
type "OUTPUTS\TEST_PROTOCOLS\run1_end_state.json" | ConvertFrom-Json | Select-Object -ExpandProperty system_progression | Format-List persistent_category_index,current_phase,amazon_products_completed

type "OUTPUTS\TEST_PROTOCOLS\run2_resume_state.json" | ConvertFrom-Json | Select-Object -ExpandProperty system_progression | Format-List persistent_category_index,current_phase,amazon_products_completed
```

**Create Evidence Table:**

| Metric | Run #1 End | Run #2 Start | Status |
|--------|------------|--------------|--------|
| persistent_category_index | ? | ? | ✅ SAME/HIGHER |
| current_phase | amazon_analysis | ? | ✅ PRESERVED |
| amazon_products_completed | ? | ? | ✅ HIGHER |

#### **Step 1.C.2: Log File Analysis**

**Command:**
```powershell
# Search logs for critical patterns
Select-String -Path "logs\*.log" -Pattern "WORKFLOW START CURSOR" | Select-Object -Last 2

Select-String -Path "logs\*.log" -Pattern "SKIP: Category" | Select-Object -First 10

Select-String -Path "logs\*.log" -Pattern "PHASE PRESERVED|PHASE TRANSITION"
```

**Validation Checklist:**
- [ ] WORKFLOW START CURSOR shows correct category_index
- [ ] SKIP messages appear for categories < start_index
- [ ] PHASE PRESERVED message appears (not PHASE TRANSITION)

#### **Step 1.C.3: Multi-Source Evidence Summary**

**Evidence Source Summary:**

| Source | Type | Key Metric | Expected | Actual | Status |
|--------|------|------------|----------|--------|--------|
| 1 | State File (Run #1 End) | PCI | ≥5 | ? | ? |
| 2 | Startup Logs (Run #2) | is_fresh_start | False | ? | ? |
| 3 | Skip Logs (Run #2) | Skip messages | Present | ? | ? |
| 4 | Phase Logs (Run #2) | PHASE PRESERVED | Yes | ? | ? |
| 5 | Progress Logs (Run #2) | Continuation | No reprocess | ? | ? |
| 6 | State File (Run #2 Resume) | PCI | Same/Higher | ? | ? |

---

## 🧪 SCENARIO 2: Resume Mid-Supplier

### **Purpose**
Validate PCI preservation and category skip when interrupting during supplier phase.

### **Setup**
Same as Scenario 1, but interrupt during supplier extraction phase.

### **Execution**

#### **Step 2.A: Run #1 - Interrupt During Supplier**

```powershell
# Start fresh
Remove-Item "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json"
python run_custom_poundwholesale.py

# Watch for supplier extraction logs
# Interrupt after category 3 or 4 completes, BEFORE amazon_analysis starts
```

**Target State:**
- PCI = 3 or 4
- Phase = "supplier"
- supplier_products_completed > 0

**Capture End State:**
```powershell
Copy-Item "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" -Destination "OUTPUTS\TEST_PROTOCOLS\scenario2_run1_end.json"
```

#### **Step 2.B: Run #2 - Resume**

```powershell
python run_custom_poundwholesale.py
```

**Expected Startup Logs:**
```
🔍 STARTUP CHECK: is_fresh_start flag is 'False'
🎯 WORKFLOW START CURSOR: category_index=3 (pci=3, cursor=3, max=3)
✅ WORKFLOW INITIALIZED: Starting from category 3 in phase 'supplier'

⏭️ SKIP: Category 1 < start 3 (already processed)
⏭️ SKIP: Category 2 < start 3 (already processed)
```

**✅ PASS Criteria:**
- PCI preserved (3 or 4, not 1)
- Phase preserved ("supplier")
- Categories 1-2 skipped
- Processing resumes at category 3/4

---

## 🧪 SCENARIO 3: Empty Category

### **Purpose**
Validate PCI advancement and proper handling when category has 0 products.

### **Setup**
This requires a category URL that returns no products (may need to temporarily add a bad URL to category list).

### **Alternative Test**
Monitor natural empty category handling during normal processing.

### **Expected Behavior:**

**Logs:**
```
No product URLs found for {category_url}
🔄 EMPTY CATEGORY HANDLING: Category 7 has no products, resetting index to 0
🔒 FROZEN DENOMINATOR: Empty category 7 → 0 products
🔒 TOTALS COMMITTED: Resume pointers now enabled for empty category
✅ EMPTY CATEGORY COMPLETED: Category 7 marked as completed
```

**State Changes:**
- PCI increments (6 → 7)
- Per-category counters reset to 0
- No PTR (progress tracking) until denominator > 0
- Category marked completed immediately

---

## 📊 Monitoring Dashboard

### **Files to Monitor (Real-Time)**

#### **1. State File (Primary Evidence Source)**
```powershell
# Watch in separate terminal
while ($true) {
    Clear-Host
    Write-Host "=== STATE MONITOR ===" -ForegroundColor Cyan
    $state = Get-Content "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" | ConvertFrom-Json
    $sp = $state.system_progression
    
    Write-Host "PCI: $($sp.persistent_category_index)" -ForegroundColor Yellow
    Write-Host "Phase: $($sp.current_phase)" -ForegroundColor Yellow
    Write-Host "Supplier Completed: $($sp.supplier_products_completed)" -ForegroundColor Green
    Write-Host "Amazon Completed: $($sp.amazon_products_completed)" -ForegroundColor Green
    Write-Host "Category URL: $($sp.current_category_url.Substring(0,[Math]::Min(50,$sp.current_category_url.Length)))..." -ForegroundColor Gray
    
    Start-Sleep -Seconds 2
}
```

#### **2. Log Tail (Secondary Evidence Source)**
```powershell
# In another terminal
Get-Content -Path "logs\*.log" -Wait -Tail 50
```

#### **3. Quick State Check (On-Demand)**
```powershell
# Single command to check critical values
type "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" | ConvertFrom-Json | Select-Object -ExpandProperty system_progression | Select-Object persistent_category_index,current_phase,amazon_products_completed,supplier_products_completed,current_category_url | Format-List
```

---

## 🔍 What to Look Out For (Red Flags)

### **❌ CRITICAL FAILURES (Fix Didn't Work)**

#### **1. PCI Backslide**
```
Run #1 End: persistent_category_index = 5
Run #2 Start: persistent_category_index = 1  ❌ FAIL
```
**Indicates:** Fix B (PCI hardening) failed

#### **2. Phase Clobber**
```
Run #1 End: current_phase = "amazon_analysis"
Run #2 Start: current_phase = "supplier"  ❌ FAIL
```
**Indicates:** Fix A.1, A.2, or A.3 failed

#### **3. No Category Skip**
```
Run #2 Logs: Processing category 1, 2, 3, 4, 5...  ❌ FAIL
(Should skip 1-4, start at 5)
```
**Indicates:** Fix D (category skip) failed

#### **4. Index Not Using MAX**
```
Run #2 Start: pci=5, cursor=3, category_index=3  ❌ FAIL
(Should be max(5,3) = 5)
```
**Indicates:** Fix C (MAX logic) failed

#### **5. Reprocessing**
```
Run #2 Logs: Processing products 1-14 again in category 5  ❌ FAIL
(Should continue from product 15)
```
**Indicates:** Progress tracking issue

---

### **⚠️ WARNINGS (Potential Issues)**

#### **1. High Water Mark Corruption Warning**
```
🚨 STATE CORRUPTION DETECTED: pci=X < hwm=Y
```
**Action:** This is validation-only; system will log but continue

#### **2. Phase Transition During Resume**
```
🔄 PHASE TRANSITION: supplier → amazon_analysis
```
**Context Matters:**
- ✅ OK if starting new category in supplier phase
- ❌ BAD if should be resuming in amazon phase

#### **3. PCI Missing Warning**
```
⚠️ PCI MISSING ON RESUME: Preserving existing state and not defaulting to 1
```
**Indicates:** Fix B is working (prevented default to 1)

---

## ✅ Success Criteria (Multi-Source Validation)

### **Primary Success Metrics**

#### **1. PCI Preservation (Fix B)**
- **Source 1:** State file comparison (Run #1 end vs Run #2 start)
- **Source 2:** Startup logs showing pci value
- **Source 3:** WORKFLOW START CURSOR log
- **Criteria:** PCI never decreases across runs

#### **2. Phase Preservation (Fix A.1, A.2, A.3)**
- **Source 1:** State file `current_phase` field
- **Source 2:** "PHASE PRESERVED" log message
- **Source 3:** No unexpected phase transitions in logs
- **Criteria:** Phase matches between Run #1 end and Run #2 start

#### **3. Category Skip (Fix D)**
- **Source 1:** "⏭️ SKIP" log messages
- **Source 2:** First processed category matches start index
- **Source 3:** No processing logs for skipped categories
- **Criteria:** All categories < start_index show skip messages

#### **4. Index Binding (Fix C)**
- **Source 1:** WORKFLOW START CURSOR shows max(pci, cursor)
- **Source 2:** category_index calculation in logs
- **Source 3:** State file verification
- **Criteria:** Start index = MAX(pci, cursor), never less

#### **5. Observability (Fix E)**
- **Source 1:** Enhanced log messages show pci, cursor, max values
- **Source 2:** Log verbosity allows debugging
- **Source 3:** All decision points are logged
- **Criteria:** Logs provide complete audit trail

---

## 📝 Test Execution Checklist

### **Pre-Test**
- [ ] Backup current state files
- [ ] Clear logs directory or note current log file names
- [ ] Verify configuration (categories, limits)
- [ ] Prepare monitoring terminals (state watcher, log tail)

### **During Test**
- [ ] Record exact commands used
- [ ] Capture screenshots of critical logs
- [ ] Note exact interrupt times/states
- [ ] Save state files at each step

### **Post-Test**
- [ ] Compare state files (Run #1 end vs Run #2 start)
- [ ] Extract and analyze logs
- [ ] Fill in evidence table
- [ ] Document any anomalies
- [ ] Calculate success rate (fixes working vs total)

---

## 📄 Test Results Template

```markdown
# Test Results - Scenario 1: Resume Mid-Amazon
Date: [DATE]
Tester: [NAME]

## Run #1 End State
- PCI: [VALUE]
- Phase: [VALUE]
- Amazon Products Completed: [VALUE]
- Supplier Products Completed: [VALUE]

## Run #2 Start State
- is_fresh_start: [True/False]
- PCI: [VALUE]
- Phase: [VALUE]
- category_index: [VALUE]

## Evidence Sources
1. State File Comparison: [PASS/FAIL]
2. Startup Logs: [PASS/FAIL]
3. Skip Logs: [PASS/FAIL]
4. Phase Logs: [PASS/FAIL]
5. Progress Logs: [PASS/FAIL]

## Fix Validation
- Fix A.1 (Phase Guard - Update): [PASS/FAIL]
- Fix A.2 (Phase Guard - Commit): [PASS/FAIL]
- Fix A.3 (Phase Guard - Init): [PASS/FAIL]
- Fix B (PCI Hardening): [PASS/FAIL]
- Fix C (MAX Logic): [PASS/FAIL]
- Fix D (Category Skip): [PASS/FAIL]
- Fix E (Observability): [PASS/FAIL]

## Overall Result
Status: [PASS/FAIL]
Confidence: [HIGH/MEDIUM/LOW]
Issues Found: [LIST]
```

---

## 🚨 Troubleshooting Guide

### **Issue: State file not found after Run #1**
**Solution:** Check path_manager.py for correct state file location

### **Issue: No skip messages appear**
**Solution:** Verify _start_category_index is set correctly (check WORKFLOW START CURSOR log)

### **Issue: Phase still clobbers**
**Solution:** Check which phase assignment is causing issue (grep for phase transitions in logs)

### **Issue: PCI still resets to 1**
**Solution:** Check is_fresh_start flag value in logs; verify Fix B implementation

---

## 📚 Reference Commands

### **Quick State Snapshot**
```powershell
$s = Get-Content "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" | ConvertFrom-Json; $s.system_progression | Select persistent_category_index,current_phase,amazon_products_completed,supplier_products_completed
```

### **Log Search Patterns**
```powershell
# Find all workflow start cursors
Select-String -Path "logs\*.log" -Pattern "WORKFLOW START CURSOR"

# Find all phase changes
Select-String -Path "logs\*.log" -Pattern "PHASE.*:"

# Find all skip messages
Select-String -Path "logs\*.log" -Pattern "SKIP:"

# Find all PCI changes
Select-String -Path "logs\*.log" -Pattern "persistent_category_index"
```

### **State File Comparison**
```powershell
# Side-by-side comparison
$r1 = Get-Content "OUTPUTS\TEST_PROTOCOLS\run1_end_state.json" | ConvertFrom-Json
$r2 = Get-Content "OUTPUTS\TEST_PROTOCOLS\run2_resume_state.json" | ConvertFrom-Json

Write-Host "PCI: $($r1.system_progression.persistent_category_index) → $($r2.system_progression.persistent_category_index)"
Write-Host "Phase: $($r1.system_progression.current_phase) → $($r2.system_progression.current_phase)"
```

---

## 🎯 Expected Timeline

**Scenario 1 (Complete):** ~15-20 minutes
- Run #1: 5-10 minutes (process until category 5)
- State capture: 1 minute
- Run #2: 5-10 minutes (validate resume)
- Evidence analysis: 3-5 minutes

**Scenario 2 (Complete):** ~10-15 minutes
**Scenario 3 (If applicable):** ~5-10 minutes

**Total Test Time:** ~30-45 minutes for complete validation

---

## 📊 Final Validation Report Template

```markdown
# Surgical Fixes Validation Report
Date: [DATE]
System: Amazon FBA Agent System v32

## Test Summary
- Total Scenarios: 3
- Scenarios Passed: [X/3]
- Fixes Validated: [X/7]
- Overall Status: [PASS/FAIL]

## Evidence Summary
- State Files Analyzed: [COUNT]
- Log Files Analyzed: [COUNT]
- Evidence Sources: [COUNT]

## Fix-by-Fix Results
[TABLE OF FIX RESULTS]

## Issues Identified
[LIST]

## Recommendations
[LIST]

## Conclusion
[SUMMARY]
```

---

**Test Protocol Version:** 1.0  
**Created:** October 16, 2025  
**Status:** Ready for Execution  
**Confidence:** HIGH
