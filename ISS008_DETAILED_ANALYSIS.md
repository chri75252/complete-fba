# DETAILED BEHAVIOR ANALYSIS: ISS-008 WORKLIST CLAMPING BUG

## The Core Problem

When resuming a category, the system incorrectly applies a **saved offset from a previous context** to a **newly filtered worklist**, causing valid work items to be skipped.

---

## BEFORE vs AFTER COMPARISON

### ❌ BEFORE FIX (Current Buggy Behavior)

**Scenario: Baby-Socks-and-Booties Category**

```
STEP 1: Category Discovery
├── Total URLs discovered: 53
└── Manifest saved: ✅

STEP 2: Pre-Extraction Filtering
├── Check linking map: 27 already complete (SKIP)
├── Check supplier cache: 24 have data (AMAZON_ONLY)
├── Remaining: 2 need extraction (FULL_EXTRACTION)
└── Filter Invariant: 53 = 27 + 24 + 2 ✅ PASS

STEP 3: Build Worklist
├── worklist_type: full_extraction
├── worklist_size: 2
└── worklist_items: [gac0789, gac0801]

STEP 4: Resume Point Calculation ← BUG HERE
├── saved_offset: 401 (from previous All-Baby-and-child category!)
├── worklist_len: 2
├── CLAMP: start = min(401, 2) = 2
├── remaining = 2 - 2 = 0
└── DECISION: "All products already processed" → SKIP CATEGORY

ACTUAL RESULT: ❌ 2 products NOT extracted
```

**Log Evidence:**
```
🔧 Clamp supplier offset: saved=401 → start=2 (len=2)
📋 RESUME CATEGORY: category 3 at resume point, total products=2, resume index=2, remaining=0
📋 Resume skip: category 3 at resume point but all 2 products already processed.
```

---

### ✅ AFTER FIX (Expected Correct Behavior)

**Same Scenario: Baby-Socks-and-Booties Category**

```
STEP 1: Category Discovery
├── Total URLs discovered: 53
└── Manifest saved: ✅

STEP 2: Pre-Extraction Filtering
├── Check linking map: 27 already complete (SKIP)
├── Check supplier cache: 24 have data (AMAZON_ONLY)
├── Remaining: 2 need extraction (FULL_EXTRACTION)
└── Filter Invariant: 53 = 27 + 24 + 2 ✅ PASS

STEP 3: Build Worklist
├── worklist_type: full_extraction
├── worklist_size: 2
└── worklist_items: [gac0789, gac0801]

STEP 4: Resume Point Calculation ← FIXED
├── saved_offset: 401 (from previous category)
├── worklist_len: 2
├── CHECK: saved_offset (401) >= worklist_len (2)? YES
├── RESET: start = 0 (fresh worklist, ignore stale offset)
├── remaining = 2 - 0 = 2
└── DECISION: "2 products need processing" → PROCESS

STEP 5: Extract Products
├── Extract gac0789: ✅
├── Extract gac0801: ✅
└── Add to linking map: 2 new entries

STEP 6: SAFETY SAVE (Fix 3 triggered)
└── 💾 SAFETY SAVE: Linking map saved at 2 entries ✅

EXPECTED RESULT: ✅ 2 products extracted successfully
```

---

## WHY THE BUG HAPPENS

### The Offset Inheritance Problem

```
Category 2: All-Baby-and-child
├── Queue size: 401 products
├── Processing completes at index 401
└── saved_offset = 401 ← SAVED TO STATE

Category 3: Baby-Socks-and-Booties  
├── Queue size: 53 products
├── After filtering: 2 products in worklist
├── System tries to resume with saved_offset = 401
├── Clamp: min(401, 2) = 2 ← CORRUPTED
└── Result: start=2, remaining=0 ← SKIPPED!
```

### The Conceptual Mismatch

| Concept | Description | Value |
|---------|-------------|-------|
| **saved_offset** | Position in the TOTAL category queue | 401 |
| **worklist** | FILTERED list of items needing work | 2 items |
| **These are different lists!** | Offset cannot be applied directly | ❌ |

The saved offset (401) represents: "I was at position 401 in a 401-item queue"

The worklist (2 items) represents: "Here are the 2 items that still need extraction"

**You cannot use a position from List A to index into List B!**

---

## THE FIX

### Option A: Always Fresh Start for Filtered Worklists (RECOMMENDED)

```python
# The worklist is already filtered to only items needing work
# There's no concept of "resuming" within a filtered worklist
# Either we process all items or none
start = 0
remaining = len(worklist)
```

**Reasoning:** The filtering logic already handles resume - items in linking map are filtered out. The worklist contains ONLY items that need processing. Starting from 0 is always correct.

### Option B: Detect and Reset on Overflow

```python
# If saved offset exceeds worklist, it's from a different context
if saved_offset >= len(worklist):
    start = 0  # Fresh start for this worklist
else:
    start = saved_offset
remaining = len(worklist) - start
```

**Reasoning:** A saved offset larger than the worklist length is impossible within the same context, indicating stale data that should be ignored.

---

## IMPACT OF FIX

### Categories That Will Work After Fix

| Category | Products Needing Work | Current | After Fix |
|----------|----------------------|---------|-----------|
| Baby-Socks-and-Booties | 2 full extraction | ❌ SKIPPED | ✅ PROCESSED |
| All-Baby-and-child | 113 amazon analysis | Pending | ✅ PROCESSED |
| Baby-favours-wholesale | 13 amazon analysis | Pending | ✅ PROCESSED |
| Avengers-Theme-Party | 7 amazon analysis | Pending | ✅ PROCESSED |

### Fixes That Will Be Testable After ISS-008

| Fix | Why Currently Blocked | After ISS-008 Fix |
|-----|----------------------|-------------------|
| Fix 3 (SAFETY SAVE) | No new linking map entries | ✅ Will trigger on new entries |
| Fix 1 (ISS-003) | No Amazon phase reached | ✅ Can test queue ordering |
| Fix 2 (ISS-002/006) | No Amazon phase reached | ✅ Can test denominator alignment |
| Fix 4 (ISS-004) | No chunk processing | ✅ Can test category scope filter |
| Fix 5 (ISS-005) | No commit_amazon_progress | ✅ Can test index validation |

---

## VERIFICATION COMMANDS

After implementing the ISS-008 fix, verify with:

```bash
# 1. Confirm no "Resume skip" for categories with work
grep "Resume skip" log.txt | grep -v "0 products"
# Expected: No output (no skips when products need processing)

# 2. Confirm extraction occurs
grep "Extracting from\|extraction complete" log.txt
# Expected: Extraction messages for gac0789, gac0801

# 3. Confirm SAFETY SAVE triggers (Fix 3)
grep "SAFETY SAVE" log.txt
# Expected: "SAFETY SAVE: Linking map saved at X entries"

# 4. Confirm Amazon phase reached
grep "amazon_phase\|PHASE TRANSITION" log.txt
# Expected: Transition to Amazon phase after supplier work completes
```
