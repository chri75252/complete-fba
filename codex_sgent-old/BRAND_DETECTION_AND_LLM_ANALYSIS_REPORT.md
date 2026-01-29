# COMPREHENSIVE BRAND DETECTION & LLM ANALYSIS REPORT

**Generated:** 2026-01-08 04:10 UTC+4

---

## PART 1: LLM RESPONSES - WHAT CONCLUSIONS IS THE AI MAKING?

### A. Brand Detection (10 Batches of 50 Candidates Each)

The AI receives batches of brand candidates and makes highly intelligent decisions. Here are examples:

#### EXAMPLES OF AI REASONING:

**Correct Brand Identifications:**
| Candidate | AI Decision | Reason |
|-----------|-------------|--------|
| `KILNER` | ✅ is_brand: true | "Kilner is a well-known UK brand for preserving jars and glassware." |
| `MINKY` | ✅ is_brand: true | "MINKY is a well-known brand for household cleaning, ironing and laundry products (UK and other markets)." |
| `MASON CASH` | ✅ is_brand: true | "Mason Cash is a well-known, established brand (traditional kitchenware and mixing bowls)." |
| `JCB` | ✅ is_brand: true | "Well-known global engineering/construction brand (J. C. Bamford)." |
| `IMPERIAL LEATHER` | ✅ is_brand: true | "Well-known toiletry/soap brand." |

**Correct Non-Brand Rejections:**
| Candidate | AI Decision | Reason |
|-----------|-------------|--------|
| `HEARTS` | ❌ is_brand: false | "Generic noun/shape term; not known as a company or product line name." |
| `LADIES THERMAL` | ❌ is_brand: false | "Generic descriptor for thermal clothing for women, not a brand." |
| `INCENSE STICKS` | ❌ is_brand: false | "Generic product description, not a brand." |
| `MICROWAVE` | ❌ is_brand: false | "Generic product type (microwave), not a brand." |
| `KNEELING PAD` | ❌ is_brand: false | "Generic product type (kneeling pad), not a brand." |

**Nuanced Decisions (Brand + Product combinations):**
| Candidate | AI Decision | Reason |
|-----------|-------------|--------|
| `MINKY ANTIBACTERIAL` | ✅ is_brand: true (→MINKY) | "Clearly references MINKY brand with an antibacterial product variant." |
| `KILNER 1LTR` | ✅ is_brand: true (→Kilner) | "Contains the Kilner brand with a size suffix (product variant), canonical brand is Kilner." |
| `HOBBY BUTTER` | ❌ is_brand: false | "Appears to be a product name/variant (butter dish/style) using HOBBY as brand; the whole phrase is not a distinct brand." |

### B. Adjudication Step

The AI reviews 50 candidate rows and provides recommendations:

```json
{
  "recommended_bucket": "NEEDS_VERIFICATION",
  "confidence": "medium",
  "reasoning": "The supplier and Amazon products show strong similarity in product type 
               (cat litter) but cannot confirm exact brand match. Recommend verification.",
  "key_match_evidence": "Shared product tokens: CAT, LITTER"
}
```

### C. Critique Step

The AI provides high-level assessment of the entire report:

```json
{
  "recommended_action": "block",
  "high_severity_issues": 2,
  "proposed_changes": 5,
  "overall_assessment": "Critical contradictions detected. The highest-priority integrity 
                        issue is that exact EAN matches are not consistently being 
                        classified as VERIFIED (19 rows). Pack detection and RSU 
                        calculation anomalies detected (841 anomaly rows)..."
}
```

---

## PART 2: BRAND LIST APPROACH - TWO SEPARATE LISTS

### The TWO-LIST Architecture:

**YES, there are TWO separate lists - this is the correct approach!**

| File | Purpose | Current Count |
|------|---------|---------------|
| **`known_brands.json`** | AI-validated brands with canonical names | 500 entries |
| **`brand_candidates_checked.json`** | ALL candidates sent to AI (both brands AND non-brands) | 1500 entries |

### Why TWO Lists?

```
┌────────────────────────────────────────────────────────────────┐
│ RUN 1: Extract 2000 candidates from titles                     │
├────────────────────────────────────────────────────────────────┤
│ Load known_brands.json: 0 brands                               │
│ Load checked_candidates.json: 0 already checked                │
│                                                                │
│ NEW candidates = 2000 - 0 = 2000 to check                      │
│                                                                │
│ Process 10 batches × 50 = 500 candidates via API               │
│                                                                │
│ Results: 201 are brands, 299 are NOT brands                    │
│                                                                │
│ Save known_brands.json: 201 validated brands                   │
│ Save checked_candidates.json: 500 (both brands AND non-brands) │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ RUN 2: Extract 2222 candidates from titles                     │
├────────────────────────────────────────────────────────────────┤
│ Load known_brands.json: 201 brands                             │
│ Load checked_candidates.json: 500 already checked              │
│                                                                │
│ NEW candidates = 2222 - 500 = 1722 to check                    │
│ (SKIPS the 500 previously sent, including non-brands!)         │
│                                                                │
│ Process 10 batches × 50 = 500 new candidates via API           │
│                                                                │
│ Results: 156 are brands, 344 are NOT brands                    │
│                                                                │
│ Save known_brands.json: 357 validated brands (201 + 156)       │
│ Save checked_candidates.json: 1000 (500 + 500 new)             │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ RUN 3 (Latest): Extract 2222 candidates from titles            │
├────────────────────────────────────────────────────────────────┤
│ Load known_brands.json: 357 brands                             │
│ Load checked_candidates.json: 1000 already checked             │
│                                                                │
│ NEW candidates = 2222 - 1000 = 1222 to check                   │
│ (CRITICAL: Does NOT re-check the 1000 already processed!)      │
│                                                                │
│ Process 10 batches × 50 = 500 new candidates via API           │
│                                                                │
│ Results: 143 are brands, 357 are NOT brands                    │
│                                                                │
│ Save known_brands.json: 500 validated brands (357 + 143)       │
│ Save checked_candidates.json: 1500 (1000 + 500 new)            │
└────────────────────────────────────────────────────────────────┘
```

### KEY DIFFERENCE BETWEEN THE TWO LISTS:

| `known_brands.json` | `brand_candidates_checked.json` |
|---------------------|--------------------------------|
| Only contains VALID brand names | Contains ALL sent candidates |
| Used for matching during analysis | Used for SKIPPING already-processed |
| Maps variant → canonical (e.g., "AIRWICK" → "AIR WICK") | Simple list of strings |
| 500 entries | 1500 entries |

### CODE THAT IMPLEMENTS THIS:

**Loading Previous Checks (line 132-142):**
```python
def load_checked_candidates(memory_dir: Path) -> set[str]:
    """Load the set of candidates that have already been checked by AI."""
    checked_path = memory_dir / CHECKED_CANDIDATES_FILE
    if checked_path.exists():
        try:
            with open(checked_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("checked", []))
        except Exception:
            return set()
    return set()
```

**Filtering to NEW Candidates Only (main function):**
```python
# Step 3: Filter to NEW candidates only
new_candidates = all_candidates - known_brands_keys - checked_candidates
print(f"[NEW] Found {len(new_candidates)} NEW candidates to validate")
```

**Saving Checked Candidates (after processing):**
```python
# Mark processed candidates as checked
checked_candidates.update(processed)  # Add ALL processed, not just brands

# Save
save_checked_candidates(memory_dir, checked_candidates)
```

---

## PART 3: HAVE ALL WORDS BEEN SENT FOR VERIFICATION?

### Current Status:

| Metric | Value |
|--------|-------|
| Total unique candidates extracted | 2222 |
| Previously checked (sent to API) | 1500 |
| Remaining to check | 722 |

**Answer: NO, not all words have been verified yet.**

The system processes **500 candidates per run** (10 batches × 50). With 2222 unique candidates:
- Run 1: Processed 500 → 1722 remaining
- Run 2: Processed 500 → 1222 remaining  
- Run 3: Processed 500 → 722 remaining
- Run 4 (next): Will process 500 → 222 remaining
- Run 5: Will process 222 → COMPLETE

### Example of Unprocessed Candidates (from the 722 remaining):
```
- ZOFLORA
- ZEST
- ZERO
- YANKEE CANDLE
- WONDER
- WOODEN SPOON
- (etc...)
```

---

## PART 4: SUMMARY OF THE ROOT CAUSE FIX

### THE PROBLEM (Before Fixes):

**NEEDS_VERIFICATION count: ONLY 2 entries (0.07%)**

### ROOT CAUSES:

#### 1. Missing Logic Path
The code only had 2 paths to NEEDS_VERIFICATION:
- Path 1: Exact EAN + split candidate (supplier pack > Amazon pack)
- Path 2: HIGHLY_LIKELY + 10-25% capacity difference

**There was NO path for:**
- Partial brand matches (brand in ONE title only)
- Moderate product similarity without brand match
- Strong product matches where brand detection failed

#### 2. Over-Aggressive Brand Exclusion
```python
# BEFORE: Any first word was treated as a "brand"
brand_s = "151"  # From "151 WHITE PAINT 300ML"
brand_a = "LG"   # From "LG OLED TV"
different_brands = True  # 151 ≠ LG → FILTERED OUT!
```

This caused **2512 items (90%)** to be filtered as "Different brands detected" even when:
- "151" is NOT a brand (it's a product code)
- The products were completely unrelated (paint vs TV)

#### 3. Brand Validation Not Used for Exclusion
The `known_brands.json` existed but wasn't being checked before applying the exclusion rule.

### THE FIX:

#### 1. Added Validation Tracking
```python
brand_s_validated = False
brand_a_validated = False

if brand_aliases:
    if brand_s and brand_s in brand_aliases:
        brand_s = brand_aliases[brand_s]
        brand_s_validated = True
```

#### 2. Changed Exclusion Rule
```python
# BEFORE: Excluded if ANY first words differ
different_brands = bool(brand_s and brand_a and brand_s != brand_a)

# AFTER: Only exclude if BOTH are validated known brands
different_brands_validated = bool(
    brand_s_validated and brand_a_validated  # BOTH must be in known brands
    and brand_s and brand_a 
    and brand_s != brand_a
)
```

#### 3. Added NEEDS_VERIFICATION Path
```python
elif not different_brands_validated and (
    partial_brand_match  # Brand in ONE title only
    or (similarity >= 0.25 and len(product_s & product_a) >= 2)  # Some similarity
):
    if adjusted_profit is not None and adjusted_profit > 0.50:
        bucket = "NEEDS_VERIFICATION"
        filter_reason = f"Moderate product similarity ({shared}) - requires verification"
```

### RESULTS:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| NEEDS_VERIFICATION | 2 | **98** | **+4800%** |
| HIGHLY_LIKELY | 78 | 192 | +146% |
| False "different brands" exclusions | 2512 | ~200 | -92% |

### EXAMPLE OF FIX IN ACTION:

**Before:**
```
Supplier: "TIDYZ WHEELY BIN LINERS 5 BAGS 300L"
Amazon:   "Heavy Duty Garden Bin Bags Extra Strong 300L Pack of 10"

brand_s = "TIDYZ"
brand_a = "Heavy"  
different_brands = True ("TIDYZ" ≠ "Heavy")
→ FILTERED_OUT ❌
```

**After:**
```
brand_s = "TIDYZ", brand_s_validated = True (TIDYZ is in known_brands)
brand_a = "Heavy", brand_a_validated = False (Heavy is NOT a known brand)
different_brands_validated = False (both must be validated)

shared_tokens = ["BIN", "BAGS", "300L"] (3 tokens)
similarity = 0.32

→ Continues to product matching
→ NEEDS_VERIFICATION ✓ (moderate similarity, profit > £0.50)
```

---

## APPENDIX: FILES & LOCATIONS

| File | Path | Size |
|------|------|------|
| **Known Brands** | `memory/global/known_brands.json` | 500 entries |
| **Checked Candidates** | `memory/global/brand_candidates_checked.json` | 1500 entries |
| **LLM Trace** | `codex sgent/AGENT REPORT/{run_id}/llm_trace.jsonl` | All API calls logged |


**END OF REPORT**
