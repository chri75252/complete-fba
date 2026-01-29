# V4.0 REPORTS - COMPREHENSIVE ACCURACY ANALYSIS & PROMPT REFINEMENT PLAN

**Generated:** 2025-12-29 06:30 GMT+4
**Ground Truth Source:** PARTDEC28_1.xlsx (1758 rows)
**Methodology:** v2 Manual Analysis (Known Brand Matching + Title Similarity + EAN)

---

## 1. EXECUTIVE SUMMARY

### Category Distribution Comparison

| Category             | Ground Truth | Codex v4.0 | Codex Accuracy | WebApp v4.0 | WebApp Accuracy |
|----------------------|--------------|------------|----------------|-------------|-----------------|
| **VERIFIED**         | 25           | 27         | **92.6%** ✓    | 24          | **95.8%** ✓     |
| **HIGHLY LIKELY**    | 27           | 24         | **8.3%** ✗     | 116         | **19.8%** ✗     |
| **NEEDS VERIFICATION** | 126        | 97         | **11.3%** ✗    | 9           | **0.0%** ✗      |
| **FILTERED OUT**     | 8            | 32         | **6.2%** ✗     | 33          | **15.2%** ✗     |

### Key Findings

**✅ VERIFIED Category: Both reports perform well**
- Codex: 25/27 correct (92.6%)
- WebApp: 23/24 correct (95.8%)
- Minor issues: 1-2 items from FILTERED OUT incorrectly in VERIFIED

**❌ HIGHLY LIKELY Category: Major problems in both reports**
- Codex: Only 2/24 correct (8.3%) - 12 items from OTHER, 6 from LOW_PRIORITY
- WebApp: Only 23/116 correct (19.8%) - 36 from OTHER, 27 from LOW_PRIORITY, 29 from NEEDS_VERIFICATION

**❌ NEEDS VERIFICATION Category: Opposite problems**
- Codex: 11/97 correct (11.3%) - 59 items should be OTHER, 22 should be LOW_PRIORITY  
- WebApp: 0/9 correct (0.0%) - All 9 items should be OTHER (wrongly put here)

**❌ FILTERED OUT Category: Different issues**
- Codex: 2/32 correct (6.2%) - Contains many items that should be OTHER/LOW_PRIORITY
- WebApp: 5/33 correct (15.2%) - Contains 2 items that should be VERIFIED (exact EAN matches)

---

## 2. ROOT CAUSE ANALYSIS

### Problem 1: WebApp HIGHLY LIKELY Over-Acceptance (CRITICAL)

**Symptom:** WebApp puts 116 items in HIGHLY LIKELY vs ground truth 27

**Root Cause:** The prompt allows extracting first word as "brand" even when it's NOT a known brand:
- "MONEY TIN BOX" → "MONEY" treated as brand → **WRONG**
- "HAPPY BIRTHDAY BANNER" → "HAPPY" treated as brand → **WRONG**
- "SALT & PEPPER SHAKERS" → "SALT" treated as brand → **WRONG**
- "LED FIRE FLAME LIGHT" → "LED" treated as brand → **WRONG**

**Evidence from WebApp Report:**
```text
| HIGHLY LIKELY | 80 | MONEY TIN BOX ASST LARGE | brand='money' |
| HIGHLY LIKELY | 80 | HAPPY BIRTHDAY BANNER | brand='happy' |
| HIGHLY LIKELY | 80 | SALT & PEPPER SHAKERS | brand='salt' |
```

**Fix Required:** Only accept brands from KNOWN_BRANDS list. Generic first words should NOT qualify.

### Problem 2: Codex NEEDS VERIFICATION Quality

**Symptom:** Codex puts 97 items in NEEDS VERIFICATION, but only 11 are correct

**Root Cause:** Items are being routed to NEEDS VERIFICATION without checking if brand is visible in Amazon title:
- Many items have "Brand not visible in Amazon title" as their reason
- This should disqualify them from NEEDS VERIFICATION (should go to OTHER)

**Evidence from Codex Report:**
```text
| NEEDS VERIFICATION | 51 | FLOWER SHOP INCENSE STICKS PK40 | Brand not visible in Amazon title |
| NEEDS VERIFICATION | 51 | BLACKSPUR CAR HEADLIGHT BULB | Brand not visible in Amazon title |
| NEEDS VERIFICATION | 51 | DEKTON HEAD TORCH PRO LIGHT | Brand not visible in Amazon title |
```

**Fix Required:** NEEDS VERIFICATION must require brand visible in Amazon title OR title similarity > 55%.

### Problem 3: Variant Mismatch Not Detected

**Symptom:** Products with same brand but different variant are classified as matches

**Example:** 
- Supplier: "ELBOW GREASE FOAMING TOILET CLEANER **EUCALYPTUS**"
- Amazon: "Elbow Grease Foaming Toilet Cleaner **LEMON FRESH**"
- **Current Result:** HIGHLY LIKELY
- **Correct Result:** FILTERED OUT (same product family, different variant)

**Fix Required:** Add explicit variant mismatch detection (scent, color, size, capacity).

### Problem 4: Pack Mismatch Detection Inconsistent

**Symptom:** Exact EAN matches with pack mismatches incorrectly in VERIFIED

**Examples from WebApp FILTERED OUT (correct detection):**
- TIDYZ DOGGY BAGS: 50 pcs vs 200 pcs (RSU=4) → Adjusted Profit = -£1.28
- PPS ROUND DOYLEYS: 40 vs 40x (RSU=40) → Adjusted Profit = -£25.91

**But same items appear in Codex VERIFIED:**
- TIDYZ DOGGY BAGS with exact EAN marked as VERIFIED despite pack mismatch

**Fix Required:** Pack mismatch check MUST run BEFORE VERIFIED assignment, not after.

---

## 3. SUGGESTED PROMPT REFINEMENTS (v4.1)

### Refinement 1: STRICT BRAND MATCHING (CRITICAL)

```markdown
### BRAND MATCHING RULES (v4.1)

**KNOWN BRANDS LIST** (Only these qualify for "brand match"):
```
AMTECH, MASON CASH, ROLSON, KILNER, DRAPER, PYREX, CHEF AID, BLUE CANYON,
ELLIOTT, FALCON, BAKER & SALT, SCHOTT ZWIESEL, MARIGOLD, FAIRY, DETTOL,
EVERBUILD, SOUDAL, TIDYZ, BACOFOIL, HARRIS, EXTRASTAR, GIFTMAKER, PRIMA,
APOLLO, KILROCK, PRODEC, HOUSE MATE, TALA, LITTLE TREES, ELBOW GREASE,
PRICE & KENSINGTON, ULTRATAPE, FIRE UP, DOFF, GEEPAS, STATUS, ROUNDUP,
SUPERIOR, FIRST STEPS, MINKY, RUSSELL HOBBS, QUEST, YALE, VINERS,
MASTERCLASS, HEM, AIRWICK, AIR WICK, SPONTEX, PASABAHCE, RCR, SCHOTT,
DENBY, HEAT HOLDERS, KORKEN, ZEAL, OXO, JOSEPH JOSEPH
```

**INVALID "Brands" (NEVER use as brand anchor):**
- Generic nouns: MONEY, HAPPY, SALT, LED, BBQ, DOOR, PET, CAT, DOG
- Product types: CANDLE, MIRROR, BOTTLE, BASKET, GLOVES, WATCH
- Descriptors: LARGE, SMALL, PREMIUM, DELUXE, CLASSIC, MODERN

**Rule:** If supplier title starts with a word NOT in KNOWN_BRANDS, 
the item CANNOT be assigned to HIGHLY LIKELY. Route to NEEDS VERIFICATION
if title similarity >= 55%, otherwise LOW_PRIORITY or OTHER.
```

### Refinement 2: VARIANT MISMATCH DETECTION (NEW)

```markdown
### VARIANT MISMATCH = FILTERED OUT

Before assigning HIGHLY LIKELY or VERIFIED, scan BOTH titles for variant indicators:

| Variant Type | Keywords to Check | Example Mismatch |
|--------------|-------------------|------------------|
| Scent | EUCALYPTUS, LEMON, LIME, LAVENDER, VANILLA, ORANGE | Eucalyptus vs Lemon |
| Color | RED, BLUE, BLACK, WHITE, GREY, NAVY, CREAM, GREEN | Black vs White |
| Size | CUP (2-cup, 6-cup), SIZE (small, medium, large) | 2-cup vs 6-cup |
| Capacity | L, LTR, ML, CC (0.5L, 1L, 5L) when >50% different | 1L vs 5L |
| Material | ENAMEL, STAINLESS, WOOD, PLASTIC, CERAMIC, GLASS | Enamel vs Stainless |

**Decision Tree:**
IF Brand matches AND Product type matches BUT variant differs:
  → Route to FILTERED OUT
  → Reason: "Same product family, different variant ([variant type])"
```

### Refinement 3: PACK MISMATCH PRIORITY (REINFORCE)

```markdown
### PACK MISMATCH OVERRIDES EXACT EAN

**STEP 1 (Before any categorization):** Extract pack counts from BOTH titles
- Patterns: "Pack of X", "X-Pack", "X x", "X pcs", "X BAGS", "(X)"

**STEP 2:** If Amazon pack > Supplier pack:
- RSU = Amazon pack / Supplier pack
- Adjusted Profit = NetProfit - (RSU - 1) × SupplierPrice

**STEP 3:** If Adjusted Profit ≤ 0:
- Route to FILTERED OUT (NOT VERIFIED, even if exact EAN)
- Reason: "Exact EAN; pack mismatch (RSU=X) makes profit £Y"

**STEP 4:** If Adjusted Profit > 0 but RSU > 1:
- Can be VERIFIED but Pack Verdict must show: "Pack Xpc (RSU=X)"
- Include warning: "Different pack size - verify this is your actual product"
```

### Refinement 4: TIGHTENED HIGHLY LIKELY CRITERIA

```markdown
### HIGHLY LIKELY Requires ALL of:
1. ✓ Brand from KNOWN_BRANDS list appears in BOTH titles (case-insensitive)
2. ✓ Product TYPE word matches (e.g., both "bowl", both "torch", both "tape")
3. ✓ No pack count word mismatch detected
4. ✓ No variant mismatch detected (scent, color, size)
5. ✓ Adjusted Profit > £0.10
6. ✓ Sales > 0

**Decision Tree:**
IF all conditions pass → HIGHLY LIKELY
ELIF Brand matches but pack/variant issue → FILTERED OUT  
ELIF Brand matches but missing other conditions → NEEDS VERIFICATION
ELIF No brand match but high similarity (>55%) → NEEDS VERIFICATION
ELSE → LOW_PRIORITY or OTHER
```

### Refinement 5: NEEDS VERIFICATION SELECTIVITY

```markdown
### NEEDS VERIFICATION Inclusion Criteria

**MUST HAVE ALL:**
1. Brand visible in Amazon title (from KNOWN_BRANDS) 
   OR Title similarity >= 55%
2. Product type word match (same category)
3. Only 1-2 specific details need confirmation:
   - Pack count needs verification
   - Variant needs confirmation
   - Size/capacity tolerance check
4. Adjusted Profit > £0.50
5. ROI > 15%
6. Sales > 0

**DO NOT INCLUDE IF:**
- Brand NOT visible in Amazon title AND similarity < 55%
- Product types clearly differ (e.g., "plates" vs "bowl")
- More than 2 details need verification
- Profit margin too thin (< £0.50)
- ROI too low (< 15%)
- No sales data

**Reason Format:** Be specific about what needs verification:
- ✓ "Pack count mismatch: confirm 6-pack vs single"
- ✓ "Size variance: confirm 16cm vs 18cm"
- ✗ "Brand not visible in title" (should be OTHER/LOW_PRIORITY)
```

---

## 4. EXPECTED DISTRIBUTION AFTER v4.1

| Category | Target Range | Description |
|----------|--------------|-------------|
| VERIFIED | 20-30 | Exact EAN matches with positive profit after pack sanity |
| HIGHLY LIKELY | 25-50 | Strong known brand + product matches, no mismatches |
| NEEDS VERIFICATION | 80-150 | Partial matches with 1-2 confirmable details |
| FILTERED OUT | 5-20 | Confirmed matches that are unprofitable (pack/variant) |
| LOW PRIORITY | 200-350 | Weak matches for later review |
| OTHER | 1000-1400 | Insufficient evidence |

---

## 5. ACTION ITEMS FOR v4.1

1. **Add KNOWN_BRANDS list to prompt** - Explicit list with instruction
2. **Add INVALID_BRANDS list to prompt** - Generic words to reject
3. **Add variant mismatch detection section** - Before HIGHLY LIKELY
4. **Move pack sanity check to BEFORE VERIFIED** - Not after
5. **Tighten NEEDS VERIFICATION criteria** - Brand must be visible OR sim > 55%
6. **Add detailed decision tree** - Clear flow from input to category
7. **Improve Filter Reason specificity** - Actionable, not vague

---

## 6. FILES GENERATED

| File | Purpose |
|------|---------|
| `GROUND_TRUTH_REFERENCE_REPORT_v2.md` | Canonical ground truth with proper table schema |
| `ground_truth_analysis.csv` | Full dataset with classifications |
| `V4_COMPREHENSIVE_ANALYSIS_AND_REFINEMENTS.md` | This analysis report |
| `comparison_output.txt` | Raw comparison data |

---

*Analysis conducted using v2 Manual Analysis Methodology with Known Brands matching.*
