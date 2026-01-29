# 📋 COMPREHENSIVE SURGICAL PROMPT FIX REPORT

**Generated:** 2025-12-31  
**Purpose:** Data-driven diff-style fixes for FINANCIAL REPORT PROMPT ANALYSIS.MD  
**Source Data:** part_30_dec.xlsx (2102 rows)  
**Ground Truth:** FINAL_FBA_MANUAL_ANALYSIS_CONSOLIDATED.md (133 valid entries)

---

## 📊 DATA-DRIVEN ANALYSIS

### Actual Problem Cases from part_30_dec.xlsx:

| RowID | Supplier Title | Amazon Title | Pack Issue |
|-------|----------------|--------------|------------|
| 126 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10 Containers 9x9 inch | **9x9 = SIZE not pack** |
| 135 | PPS ROUND 40 DOYLEYS 21CM | PPS 40 Doyleys 21cm | **21CM = DIAMETER, 40 = QTY/pack** |
| 317 | TIDYZ DOGGY BAGS STRONG 50 PCS | Tidyz 200 x Doggy bags (4 x 50) | **50 = QTY per pack, 4x50 = multipack** |
| 1971 | APOLLO VINEGAR SHAKER 15cm | Apollo Vinegar Shaker 15cm | **15cm = HEIGHT not pack** |
| 2021 | TALA COCKTAIL STICKS 200 | Tala Cocktail Sticks 200 | **200 = STICKS per pack not 200 packs** |
| 2089 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash Dish 16cm | **16cm = SIZE not pack** |
| 420 | SOUDAL EXPANDING FOAM 150ML | Soudal Foam 750ML | **Capacity mismatch 5x** |

---

## 🔧 FIX #1: QUANTITY-PER-PACK SHIELD (NEW SECTION)

### 📍 Location: After Stage 4 Pack Size Extraction (line ~520-575)

### ❌ CURRENT PROMPT (Missing entirely):
```markdown
### **STAGE 4: Pack Size Extraction & Profit Recalculation**

```python
def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    # ... existing patterns like 'pack of', 'x pack', etc.
```
```

### ✅ FIXED PROMPT (Add new section after patterns):
```markdown
### **STAGE 4: Pack Size Extraction & Profit Recalculation**

```python
def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    # ... existing patterns
```

### 🆕 STAGE 4B: QUANTITY-PER-PACK SHIELD (v4.1 NEW)

**CRITICAL:** Numbers describing QUANTITY INSIDE a single package are NOT pack counts.

**Examples from actual data (part_30_dec.xlsx):**

| Title Pattern | Number | Interpretation | Pack Count |
|---------------|--------|----------------|------------|
| `COCKTAIL STICKS 200` | 200 | 200 sticks per pack | **1** |
| `DOGGY BAGS 50 PCS` | 50 | 50 bags per pack | **1** |
| `ROUND 40 DOYLEYS` | 40 | 40 doilies per pack | **1** |
| `SHOT GLASSES 20PCE` | 20 | 20 glasses in set | **1** |
| `10 CONTAINERS & LID` | 10 | 10 containers per pack | **1** (unless Amazon shows different) |
| `FIRELIGHTERS 28 PACK` | 28 | 28 pieces per pack | **1** |

**Decision Rule:**
- If BOTH Supplier AND Amazon show the SAME quantity-inside number → `Pack Verdict = "1:1 Match"`
- The trailing number without "pack" keyword = items per package, NOT multipacks

**Multipack Indicators (these ARE pack counts):**
- `Pack of 10` / `10-pack` / `(10)` at end = **10 packs**
- `3 x` at START of Amazon title = **3-pack bundle**
- `4 x 50` = **4 packs of 50 each** (verify Amazon listing)

**Anti-Pattern Detection:**
```python
# WRONG: Treating quantity-inside as pack count
"COCKTAIL STICKS 200" → pack_count = 200  # ❌ WRONG

# RIGHT: Recognize 200 as items per package
"COCKTAIL STICKS 200" → pack_count = 1    # ✅ CORRECT
```
```

---

## 🔧 FIX #2: ENHANCED DIMENSION PATTERNS (Expand existing)

### 📍 Location: Stage 6 Manual Pack-Size Verification (line ~675-720)

### ❌ CURRENT PROMPT (line 683-694):
```markdown
**Specific patterns that are DIMENSIONS, not pack counts:**

| Pattern | Meaning | NOT Pack |
|---------|---------|----------|
| `15 x 5.5 x 5.5 cm` | Product dimensions | ✅ |
| `16 x 16 x 4.5 cm` | Product dimensions | ✅ |
| `9 x 9 inch` | 9 inches square | ✅ |
| `40x34x4` | Dimensions | ✅ |
| `28 x 21 x 9 cm` | Dimensions | ✅ |
| `20 x 17 cm` | Dimensions | ✅ |
| `280X115MM` | 280mm by 115mm | ✅ |
| `500ML`, `1L`, `4FT` | Measurements | ✅ |
```

### ✅ FIXED PROMPT (Expand with real data patterns):
```markdown
**Specific patterns that are DIMENSIONS, not pack counts:**

| Pattern | Meaning | NOT Pack | Real Example from Data |
|---------|---------|----------|------------------------|
| `15 x 5.5 x 5.5 cm` | Product dimensions | ✅ | - |
| `16 x 16 x 4.5 cm` | Product dimensions | ✅ | - |
| `9 x 9 inch` / `9X9IN` | Square size | ✅ | **SUPERIOR FOIL 9X9IN** |
| `21CM` / `21cm` | Diameter/size | ✅ | **PPS DOYLEYS 21CM** |
| `15cm` / `15CM` | Height/length | ✅ | **APOLLO VINEGAR SHAKER 15cm** |
| `16cm` / `16CM` | Dish size | ✅ | **MASON CASH DISH 16cm** |
| `280X115MM` | Dimensions | ✅ | - |
| `500ML`, `1L`, `4FT` | Capacity/length | ✅ | **SOUDAL FOAM 750ML** |
| `85GM` / `85G` | Weight | ✅ | **PAN AROMA CANDLE 85GM** |
| `29CM` | Bowl diameter | ✅ | **MASON CASH BOWL 29CM** |
| `20X17CM` | Rectangle size | ✅ | **PYREX DISH 20X17CM** |

**🆕 SINGLE-NUMBER DIMENSION PATTERNS (v4.1 NEW):**

These patterns appear as SINGLE numbers with units - treat as dimensions:

| Pattern | Examples | Interpretation |
|---------|----------|----------------|
| `Ncm` / `NCM` | `15cm`, `21CM`, `16cm`, `29CM` | Size in centimeters |
| `Nmm` / `NMM` | `280MM`, `150MM` | Size in millimeters |
| `Nin` / `NINCH` | `4IN`, `6INCH` | Size in inches |
| `Nft` / `NFT` | `4FT`, `6FT` | Length in feet |
| `Nml` / `NML` | `500ML`, `750ML`, `150ML` | Capacity in milliliters |
| `Nltr` / `NL` | `1L`, `3LTR`, `4.1L` | Capacity in liters |
| `Ng` / `NGM` | `85G`, `85GM`, `200G` | Weight in grams |
| `Nkg` | `3KG`, `5KG` | Weight in kilograms |
| `Noz` | `8OZ` | Weight/size in ounces |

**EXPLICIT OVERRIDE RULE (MANDATORY):**
If pack parsing extracts a number that matches ANY dimension pattern above:
→ **OVERRIDE** pack_count to 1
→ Set Pack Verdict to `"1:1 Match (Ncm/Nml/etc. is measurement)"`
→ Do **NOT** calculate RSU or adjust profit based on this number
```

---

## 🔧 FIX #3: CAPACITY MISMATCH THRESHOLDS (New Section)

### 📍 Location: Add after Stage 6B (line ~760)

### ❌ CURRENT PROMPT (line 756-758):
```markdown
### Capacity Tolerance

If capacity difference is within 25-30% (e.g., 500ml vs 580ml):
- Route to **VERIFIED** with note in Pack Verdict column
- NEVER filter out Exact-EAN matches for minor capacity differences
```

### ✅ FIXED PROMPT (Add specific thresholds):
```markdown
### Capacity Tolerance & Thresholds (v4.1 ENHANCED)

**Capacity Difference Decision Matrix:**

| Difference | Example | Action | Category |
|------------|---------|--------|----------|
| **0-10%** | 407ml vs 408ml (0.25%) | ✅ Same product | VERIFIED/HIGHLY LIKELY |
| **10-25%** | 500ml vs 580ml (16%) | ⚠️ Minor variance | NEEDS VERIFICATION |
| **25-50%** | 3L vs 4.1L (37%) | ⚠️ Different SKU | NEEDS VERIFICATION → likely FILTERED OUT |
| **>50%** | 150ml vs 750ml (5x) | ❌ Different product | **FILTERED OUT** (not NEEDS VERIFICATION) |

**Real Example from Data:**
- Row 420: SOUDAL EXPANDING FOAM **150ML** vs Amazon **750ML**
- Difference: 5x (500%)
- **Correct Action:** FILTERED OUT (completely different product variant)
- **Wrong Action:** NEEDS VERIFICATION (wastes verification effort)

**Formula:**
```python
diff_pct = abs(supplier_capacity - amazon_capacity) / max(supplier_capacity, amazon_capacity) * 100

if diff_pct <= 10:
    category = "VERIFIED/HIGHLY LIKELY"  # Same product
elif diff_pct <= 25:
    category = "NEEDS VERIFICATION"      # Minor variance
elif diff_pct <= 50:
    category = "FILTERED OUT"            # Different SKU
else:
    category = "FILTERED OUT"            # Completely different product
```
```

---

## 🔧 FIX #4: NEEDS VERIFICATION COUNT LIMITS (Stricter)

### 📍 Location: NEEDS VERIFICATION SCOPING RULES (line ~360-365)

### ❌ CURRENT PROMPT (line 360-363):
```markdown
**Expected NEEDS VERIFICATION Count Guidance:**
- A well-analyzed dataset of ~1700 rows should have approximately **50-150 items** in NEEDS VERIFICATION
- If NEEDS VERIFICATION exceeds 200 items, you are likely being too conservative with HIGHLY LIKELY categorization
- If NEEDS VERIFICATION exceeds 300 items, you are almost certainly including items that should be FILTERED OUT or upgraded to HIGHLY LIKELY
```

### ✅ FIXED PROMPT:
```markdown
**Expected NEEDS VERIFICATION Count Guidance (v4.1 TIGHTENED):**

| Dataset Size | Target Count | Max Acceptable | Action if Exceeded |
|--------------|--------------|----------------|-------------------|
| ~2000 rows | **40-60** | 80 | Re-evaluate categorization |
| ~1700 rows | **35-50** | 70 | Re-evaluate categorization |
| ~1000 rows | **20-35** | 50 | Re-evaluate categorization |

**Ground Truth Reference:** 
- `part_30_dec.xlsx` (2102 rows) → **48 NEEDS VERIFICATION** items in manual analysis

**If your NEEDS VERIFICATION count exceeds target by >50%:**
1. **STOP** and re-evaluate before proceeding
2. Check: Are items with Brand + Product match in NEEDS VERIFICATION? → **Upgrade to HIGHLY LIKELY**
3. Check: Are items with negative Adjusted Profit in NEEDS VERIFICATION? → **Move to FILTERED OUT**
4. Check: Are items with >50% capacity difference in NEEDS VERIFICATION? → **Move to FILTERED OUT**
5. Check: Are Exact EAN matches with dimension patterns downgraded? → **Restore to VERIFIED**

**Mandatory Self-Check:** Before finalizing report, if NEEDS_VERIFICATION_COUNT > 100 for ~2000 row dataset:
→ You MUST reduce by upgrading qualifying items to HIGHLY LIKELY
→ You MUST reduce by filtering out negative-profit items
→ Do NOT submit report until count is within target range
```

---

## 🔧 FIX #5: HIGHLY LIKELY UPGRADE TRIGGERS (Strengthen)

### 📍 Location: UPGRADE TRIGGERS section (line ~333-344)

### ❌ CURRENT PROMPT (line 337-344):
```markdown
**Upgrade to HIGHLY LIKELY if ALL of these are TRUE:**
1. Brand name matches between titles (case-insensitive, e.g., "AMTECH" = "Amtech")
2. Product type matches (e.g., both are "trowel", "hammer", "bowl")
3. No proven pack mismatch (or pack is clearly 1:1)
4. Profit remains positive

**If these conditions are met → Upgrade to HIGHLY LIKELY instead of NEEDS VERIFICATION.**
```

### ✅ FIXED PROMPT:
```markdown
**Upgrade to HIGHLY LIKELY if ANY of these combinations are TRUE:**

**Combination 1: Brand + Product Match (Primary)**
1. Brand name matches between titles (case-insensitive)
   - ✅ "AMTECH TROWEL" matches "Amtech Pointing Trowel"
   - ✅ "ROLSON HAMMER" matches "Rolson Claw Hammer"
2. Product type matches (tool/container/food/etc.)
3. No proven pack mismatch
4. Profit is positive
→ **MANDATORY: Upgrade to HIGHLY LIKELY**

**Combination 2: Brand-in-Prefix Pattern (v4.1 NEW)**
- Supplier title STARTS with known brand (e.g., "EVERBUILD", "DRAPER", "PYREX")
- Amazon title CONTAINS same brand (anywhere in title)
- Product description aligns
→ **MANDATORY: Upgrade to HIGHLY LIKELY**

**Combination 3: Model Number Match (v4.1 NEW)**
- Both titles share product model/code (e.g., "S1532", "32LTR")
- Brand may be missing from one title
→ **MANDATORY: Upgrade to HIGHLY LIKELY**

**Real Examples from Data:**

| Supplier | Amazon | Upgrade Reason | Category |
|----------|--------|----------------|----------|
| ROLSON CLAW HAMMER | Rolson 8oz Stubby Claw Hammer | Brand + Product | **HIGHLY LIKELY** |
| AMTECH POINTING TROWEL 150MM | Amtech Pointing Trowel | Brand + Product + Size | **HIGHLY LIKELY** |
| PYREX AIR FRYER DISH 20X17CM | PYREX Square Dish 20 x 17 cm | Brand + Dimensions | **HIGHLY LIKELY** |
| EVERBUILD BITUMEN MASTIC 1L | Everbuild Bitumen Trowel Mastic | Brand + Product | **HIGHLY LIKELY** |

**Anti-Pattern:** Do NOT leave these in NEEDS VERIFICATION:
- ❌ "AMTECH TROWEL" vs "Amtech Trowel" → Brand matches! Upgrade!
- ❌ "FAIRY DISH BRUSH" vs "Fairy Max Power Brush" → Brand matches! Upgrade!
```

---

## 🔧 FIX #6: FILTERED OUT MANDATORY TRIGGERS (New Section)

### 📍 Location: Add to CATEGORY DEFINITIONS → FILTERED OUT (line ~304-330)

### ❌ CURRENT PROMPT (implicit/scattered):
```markdown
### **FILTERED OUT (Confirmed Matches - Unprofitable for Audit)**

⚠️ **CRITICAL DISTINCTION:** FILTERED OUT contains **CONFIRMED product matches** that cannot be actioned profitably.
```

### ✅ FIXED PROMPT (Add explicit triggers):
```markdown
### **FILTERED OUT (Confirmed Matches - Unprofitable for Audit)**

⚠️ **CRITICAL DISTINCTION:** FILTERED OUT contains **CONFIRMED product matches** that cannot be actioned profitably.

### 🆕 MANDATORY FILTERED OUT TRIGGERS (v4.1)

You **MUST** place a product in FILTERED OUT (never NEEDS VERIFICATION) if ANY of these are true:

| Trigger | Condition | Example |
|---------|-----------|---------|
| **Negative Adjusted Profit** | Adjusted_Profit ≤ 0 | Any pack ratio that creates loss |
| **Pack Ratio > 5:1** | Amazon multipack requires 6+ supplier units | WHAM CRYSTAL BOX 1→3 sets |
| **Capacity Difference > 50%** | 5x or greater difference | SOUDAL 150ML vs 750ML |
| **Explicit Set Mismatch** | Supplier single vs Amazon "Set of N" | PYREX CASSEROLE 1 vs Set of 3 |
| **Clear Variant Mismatch** | Same brand, different product | 1L vs 5L (5x capacity) |

**Decision Tree:**
```
Is Adjusted Profit > 0?
├─ NO → FILTERED OUT (mandatory)
└─ YES → Continue...
    Is capacity difference > 50%?
    ├─ YES → FILTERED OUT (different product variant)
    └─ NO → Continue...
        Is pack ratio > 5:1 with confirmed brand match?
        ├─ YES → FILTERED OUT (unprofitable multipack)
        └─ NO → Check other categories
```

**Real Examples from Data:**

| Row | Product | Pack Issue | Adj Profit | Category |
|-----|---------|------------|------------|----------|
| 1705 | PHOODS FOIL TRAY ROASTER | 1→10 | -£5.82 | **FILTERED OUT** |
| 1934 | WHAM CRYSTAL UNDERBED BOX | 1→3 | -£8.60 | **FILTERED OUT** |
| 696 | PYREX CASSEROLE 6.7LTR | 1→3 set | -£23.96 | **FILTERED OUT** |
| 420 | SOUDAL FOAM 150ML vs 750ML | 5x capacity | N/A | **FILTERED OUT** |
```

---

## 🔧 FIX #7: EXPECTED REPORT DISTRIBUTION (Update ranges)

### 📍 Location: EXPECTED REPORT DISTRIBUTION (line ~864-877)

### ❌ CURRENT PROMPT (line 866-871):
```markdown
| Category | Expected Range | Contents |
|----------|----------------|----------|
| VERIFIED | 15-50 | All exact EAN matches that pass validation with positive profit |
| HIGHLY LIKELY | 30-100 | Strong brand + product matches with positive profit |
| NEEDS VERIFICATION | 50-150 | Only items upgradeable via 1-2 confirmable details |
| FILTERED OUT | 20-100 | **CONFIRMED matches** that are unprofitable due to pack/variant issues (for audit) |
```

### ✅ FIXED PROMPT:
```markdown
| Category | Expected Range | Ground Truth (2102 rows) | Contents |
|----------|----------------|--------------------------|----------|
| VERIFIED — RECOMMENDED | **25-40** | 33 | Exact EAN + positive profit |
| VERIFIED — FILTERED OUT | **8-15** | 12 | Exact EAN + pack/profit issue |
| HIGHLY LIKELY — RECOMMENDED | **45-60** | 52 | Brand+Product + positive profit |
| HIGHLY LIKELY — FILTERED OUT | **20-35** | 29 | Brand+Product + pack issue |
| NEEDS VERIFICATION | **40-60** | 48 | Only upgradeable via 1-2 details |
| TOTAL ACTIONABLE | **130-175** | 133 | VERIFIED + HL + NEEDS VERIF |

**Validation Check:** If your counts differ significantly from Ground Truth ranges:
- VERIFIED too low? → Check if dimension patterns caused incorrect filtering
- HIGHLY LIKELY too low? → Check if brand matches are stuck in NEEDS VERIFICATION
- NEEDS VERIFICATION too high? → Upgrade brand matches, filter out negative profits
- FILTERED OUT too low? → Ensure all negative-profit items are captured
```

---

## 📋 SUMMARY OF ALL FIXES

| Fix # | Section | Issue | Solution |
|-------|---------|-------|----------|
| 1 | Stage 4B (NEW) | Quantity-inside treated as packs | Shield for items-per-pack numbers |
| 2 | Stage 6 | Dimension patterns incomplete | Expand with real data patterns (NCM, NML, etc.) |
| 3 | After Stage 6B (NEW) | No capacity thresholds | Add 0-10%, 10-25%, 25-50%, >50% matrix |
| 4 | NEEDS VERIF Scoping | Count limits too loose | Tighten to 40-60 for ~2000 rows |
| 5 | Upgrade Triggers | Too conservative | Add mandatory upgrade combinations |
| 6 | FILTERED OUT (NEW) | No explicit triggers | Add mandatory filtering conditions |
| 7 | Report Distribution | Ranges incorrect | Update to match ground truth |

---

## ✅ SELF-AUDIT CHECKLIST (Add to end of prompt)

```markdown
## 📋 PRE-SUBMISSION VALIDATION CHECKLIST (v4.1)

Before finalizing report, verify ALL of the following:

- [ ] **Dimension Check:** No patterns like `9x9in`, `21CM`, `15cm` caused incorrect RSU calculation
- [ ] **Quantity-Inside Check:** No patterns like `200 sticks`, `50 PCS`, `40 doyleys` caused incorrect RSU
- [ ] **Brand Upgrade Check:** All Brand+Product matches are in HIGHLY LIKELY, not NEEDS VERIFICATION
- [ ] **Negative Profit Check:** All items with Adjusted Profit ≤ 0 are in FILTERED OUT
- [ ] **Capacity Check:** All items with >50% capacity difference are in FILTERED OUT
- [ ] **Count Validation:** NEEDS VERIFICATION count is within 40-60 range for ~2000 rows
- [ ] **Evidence Check:** Key Match Evidence cites only tokens from current row's titles
- [ ] **Pack Verdict Check:** Pack Verdicts are consistent with actual title analysis

If ANY check fails, revise categorization before submission.
```

---

*Report generated by Antigravity Analysis System*
*Data Source: part_30_dec.xlsx (2102 rows)*
*Ground Truth: FINAL_FBA_MANUAL_ANALYSIS_CONSOLIDATED.md*
*Date: 2025-12-31*
