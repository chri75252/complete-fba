# QUICK START TEST GUIDE - Surgical Fixes Validation
## October 16, 2025

**Goal:** Validate PCI and phase preservation across interruptions in ~15 minutes.

---

## 🚀 Quick Test (Scenario 1 - Most Critical)

### **Setup (1 minute)**

```powershell
# Navigate to workspace
cd "c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

# Create test output directory
New-Item -ItemType Directory -Force -Path "OUTPUTS\TEST_PROTOCOLS"

# Optional: Start with clean state
Remove-Item "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" -ErrorAction SilentlyContinue
```

---

### **Run #1: Process Until Category 5 Amazon Phase (5-10 minutes)**

#### **Terminal 1: Start System**
```powershell
python run_custom_poundwholesale.py
```

#### **Terminal 2: Watch State (Optional)**
```powershell
# Real-time state monitor
while ($true) {
    $s = Get-Content "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" -ErrorAction SilentlyContinue | ConvertFrom-Json
    if ($s) {
        Write-Host "PCI: $($s.system_progression.persistent_category_index) | Phase: $($s.system_progression.current_phase) | Amazon: $($s.system_progression.amazon_products_completed)" -ForegroundColor Cyan
    }
    Start-Sleep 2
}
```

#### **Watch Logs For:**
```
🔄 PHASE TRANSITION: supplier → amazon_analysis    ← Phase changed
🔧 AMAZON PROGRESS: cat=5/X idx=15->16             ← In category 5, amazon phase
```

#### **Interrupt When:**
- **Category:** 5 or higher
- **Phase:** amazon_analysis
- **Progress:** Partially through (not at 0)

**Press `Ctrl+C` in Terminal 1**

---

### **Capture Run #1 State (1 minute)**

```powershell
# Save end state
Copy-Item "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" -Destination "OUTPUTS\TEST_PROTOCOLS\run1_end.json"

# Display critical values
$r1 = Get-Content "OUTPUTS\TEST_PROTOCOLS\run1_end.json" | ConvertFrom-Json
Write-Host "`n=== RUN #1 END STATE ===" -ForegroundColor Yellow
Write-Host "PCI: $($r1.system_progression.persistent_category_index)" -ForegroundColor Green
Write-Host "Phase: $($r1.system_progression.current_phase)" -ForegroundColor Green
Write-Host "Amazon Completed: $($r1.system_progression.amazon_products_completed)" -ForegroundColor Green
```

**Record These Values:**
- PCI = _____ (should be ≥5)
- Phase = _____ (MUST be "amazon_analysis")
- Amazon Completed = _____ (should be >0)

---

### **Run #2: Resume and Validate (5-10 minutes)**

#### **Start Resume**
```powershell
python run_custom_poundwholesale.py
```

#### **CRITICAL: Watch First 30 Seconds of Logs**

**✅ SUCCESS INDICATORS:**
```
🔍 STARTUP CHECK: is_fresh_start flag is 'False'           ← Not fresh start
🎯 WORKFLOW START CURSOR: category_index=5 (pci=5, ...)    ← Starts at 5, not 1!
✅ WORKFLOW INITIALIZED: Starting from category 5 in phase 'amazon_analysis'  ← Phase preserved!

⏭️ SKIP: Category 1 < start 5 (already processed)         ← Categories skipped
⏭️ SKIP: Category 2 < start 5 (already processed)
⏭️ SKIP: Category 3 < start 5 (already processed)
⏭️ SKIP: Category 4 < start 5 (already processed)

✅ PHASE PRESERVED: 'amazon_analysis' (loaded from state)  ← Phase guard worked
```

**❌ FAILURE INDICATORS:**
```
category_index=1                      ← PCI reset! FIX FAILED
phase 'supplier'                      ← Phase clobber! FIX FAILED
No skip messages                      ← Skip logic failed!
```

#### **Let Run for ~30 Seconds, Then Interrupt (Ctrl+C)**

---

### **Compare States (2 minutes)**

```powershell
# Load both states
$r1 = Get-Content "OUTPUTS\TEST_PROTOCOLS\run1_end.json" | ConvertFrom-Json
$r2 = Get-Content "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" | ConvertFrom-Json

# Compare critical values
Write-Host "`n=== STATE COMPARISON ===" -ForegroundColor Cyan
Write-Host "PCI:   $($r1.system_progression.persistent_category_index) → $($r2.system_progression.persistent_category_index)" -ForegroundColor $(if ($r2.system_progression.persistent_category_index -ge $r1.system_progression.persistent_category_index) { "Green" } else { "Red" })
Write-Host "Phase: $($r1.system_progression.current_phase) → $($r2.system_progression.current_phase)" -ForegroundColor $(if ($r2.system_progression.current_phase -eq $r1.system_progression.current_phase) { "Green" } else { "Red" })
Write-Host "Amazon: $($r1.system_progression.amazon_products_completed) → $($r2.system_progression.amazon_products_completed)" -ForegroundColor $(if ($r2.system_progression.amazon_products_completed -gt $r1.system_progression.amazon_products_completed) { "Green" } else { "Red" })
```

---

## ✅ Pass/Fail Decision Matrix

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| **PCI Preserved** | Run#1 PCI = Run#2 PCI (or higher) | ? → ? | ⬜ |
| **Phase Preserved** | "amazon_analysis" → "amazon_analysis" | ? → ? | ⬜ |
| **Categories Skipped** | 4 skip messages (cats 1-4) | ? messages | ⬜ |
| **is_fresh_start** | False (not True) | ? | ⬜ |
| **Progress Continued** | Amazon count increased | ? → ? | ⬜ |

**Decision:**
- ✅ **ALL PASS:** Fixes working correctly
- ❌ **ANY FAIL:** Document which fix failed and evidence

---

## 🔍 Evidence Checklist

**Must have at least 3 evidence sources per fix:**

### **Fix B (PCI Hardening)**
- [ ] Source 1: State file shows PCI preserved
- [ ] Source 2: Startup log shows `is_fresh_start=False`
- [ ] Source 3: WORKFLOW START CURSOR shows correct PCI

### **Fix A (Phase Guards)**
- [ ] Source 1: State file shows phase preserved
- [ ] Source 2: "PHASE PRESERVED" log message
- [ ] Source 3: No unexpected phase transitions

### **Fix C (MAX Logic)**
- [ ] Source 1: WORKFLOW START CURSOR shows max(pci, cursor)
- [ ] Source 2: category_index matches expected value
- [ ] Source 3: State file comparison

### **Fix D (Category Skip)**
- [ ] Source 1: "⏭️ SKIP" log messages (4 expected)
- [ ] Source 2: First processed category = start_index
- [ ] Source 3: No processing logs for cats 1-4

---

## 📝 Quick Results Form

```
TEST DATE: _______________
TESTER: _______________

RUN #1 END STATE:
  PCI: _____
  Phase: _____
  Amazon Completed: _____

RUN #2 START STATE:
  is_fresh_start: _____
  PCI: _____
  Phase: _____
  category_index: _____

SKIP MESSAGES: _____ (expected: 4)

OVERALL RESULT: PASS / FAIL
FIXES VALIDATED: ___/7

ISSUES FOUND:
_________________________________
_________________________________
_________________________________
```

---

## 🚨 Common Issues & Quick Fixes

### **Issue: No state file found**
```powershell
# Check if state file exists
Test-Path "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json"

# Check alternative location
Get-ChildItem -Recurse -Filter "*processing_state.json"
```

### **Issue: Can't read state file**
```powershell
# Validate JSON
Get-Content "OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json" | ConvertFrom-Json | Out-Null
# If no error, JSON is valid
```

### **Issue: Logs not showing expected messages**
```powershell
# Find latest log file
$latestLog = Get-ChildItem "logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latestLog.FullName -Tail 100
```

---

## 📊 Time Estimate

- Setup: **1 minute**
- Run #1: **5-10 minutes**
- Capture: **1 minute**
- Run #2: **5-10 minutes**  
- Analysis: **2 minutes**

**Total: ~15-25 minutes**

---

## 🎯 Success Criteria (Simple)

**✅ TEST PASSES IF:**
1. PCI doesn't decrease (5 stays 5, or becomes 6+)
2. Phase stays "amazon_analysis" (not reset to "supplier")
3. Categories 1-4 show skip messages
4. Amazon progress continues (not restarted from 0)

**❌ TEST FAILS IF:**
1. PCI drops (5 becomes 1) ← **CRITICAL FAILURE**
2. Phase changes to "supplier" ← **CRITICAL FAILURE**
3. No skip messages ← Fix D failed
4. Processing restarts from category 1 ← Fix C or D failed

---

**For detailed instructions, see:** `COMPREHENSIVE_TEST_PROTOCOL_OCT16_2025.md`
