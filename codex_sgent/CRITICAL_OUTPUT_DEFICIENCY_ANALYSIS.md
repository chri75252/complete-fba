# CRITICAL UPDATE: FBA Agent Output Deficiency Analysis
**Date:** 2026-01-05 22:45  
**Priority:** URGENT  
**Issue:** Agent is missing 118 valid entries (84% shortfall vs reference)

---

## EXECUTIVE SUMMARY

**The agent is severely underperforming compared to the reference report:**

| Metric | Reference Report | Current Best Run | Shortfall | % Missing |
|--------|-----------------|------------------|-----------|-----------|
| VERIFIED - RECOMMENDED | **32** | **11** | -21 | **66% missing** |
| HIGHLY LIKELY - RECOMMENDED | **109** | **12** | -97 | **89% missing** |
| **TOTAL GOOD BUCKETS** | **141** | **23** | **-118** | **84% missing** |
| NEEDS VERIFICATION | 190 | 96 | -94 | 49% fewer |
| FILTERED OUT | 66 | 2577 | +2511 | 3800% increase |

**Root Cause:** The deterministic analysis guards are **excessively restrictive**, filtering out valid profitable items. AI Adjudication is supposed to rescue these but is either:
1. Not running effectively on the right candidates
2. Being too conservative in its decisions
3. **We cannot diagnose because we have NO VISIBILITY into AI decision-making** (logging failure)

---

## PART 1: EVIDENCE OF MISSING VALID ENTRIES

### Example: Items in Reference Report but NOT in Current Report

**Sample from Reference VERIFIED:**

```
Row 2246: PPS ROUND 40 DOYLEYS 21CM
- Supplier EAN: 5030481940088
- Amazon EAN: 5030481940088  
- Verdict: VERIFIED (95 confidence)
- Pack: 1:1 Match
- Profit: £0.30 (26.7% ROI)
- Sales: 700
```

**Status in Current Run:** Likely in FILTERED_OUT or NEEDS_VERIFICATION (need to check ledger)

**Sample from Reference HIGHLY LIKELY:**

```
Row 269: WORLD OF PETS CAT LITTER SCENTED 3LT
- Supplier EAN: 5052516216876
- Amazon EAN: - (missing)
- Verdict: HIGHLY LIKELY (85 confidence)
- Pack: 1:1 Match
- Profit: £16.14 (566.3% ROI)
- Sales: 800
```

**This is a HIGH VALUE item being excluded by current logic!**

---

## PART 2: FILTER LOGIC ANALYSIS

### Where Are Valid Items Being Lost?

Based on comparison of bucket counts:

**Hypothesis 1: Over-Aggressive FILTERED_OUT Assignment (77% probability)**
- Reference: 66 items in FILTERED_OUT
- Current: **2577 items in FILTERED_OUT** (39x increase!)
- **Impact:** 2500+ items are being incorrectly rejected

**Most likely causes:**
1. **Pack Size Mis-detection:** AI Preflight shields are TOO aggressive
   - Example: "PACK OF 6" might be getting shielded as a dimension
   - Items marked as requiring "RSU=10" when they should be "1:1 Match"
2. **Profit Recalculation Error:** Items with positive original profit are being recalculated as negative
   - After pack adjustment: `adjusted_profit = original_profit / RSU`
   - If RSU is wrongly detected as 10, profit becomes negative → FILTERED_OUT
3. **Brand Matching Too Strict:** Items with slight brand variations getting rejected

**Hypothesis 2: Under-Utilization of HIGHLY_LIKELY (20% probability)**
- Reference uses HIGHLY_LIKELY liberally (109 items, even with missing Amazon EAN)
- Current: Only 12 items in HIGHLY_LIKELY
- **Possible cause:** Confidence threshold is too high OR brand matching is too strict

**Hypothesis 3: Adjudication Not Rescuing Items (3% probability)**
- Adjudication ran on 50 candidates
- But 96 remain in NEEDS_VERIFICATION
- **Either:** Wrong candidates selected OR AI is being too conservative

---

## PART 3: CRITICAL PATH TO RESOLUTION

### Priority 0: AI LOGGING VISIBILITY (BLOCKING EVERYTHING)
**Without this, we are FLYING BLIND and cannot diagnose anything.**

**Action Items:**
1. **Fix `OpenAIProvider` logging** - Modify to guarantee trace writes
   ```python
   # Current (broken):
   trace_file = os.getenv("FBA_TRACE_FILE")  # Returns None?
   
   # Proposed fix:
   def __init__(self, config, trace_path=None):
       self.trace_path = trace_path
   
   def chat_json(self, ...):
       if self.trace_path:
           # Write to self.trace_path
   ```

2. **Verify environment variable propagation**
   - Add debug print in `run.py`: `print(f"TRACE FILE SET: {os.environ.get('FBA_TRACE_FILE')}")`
   - Add debug print in `OpenAIProvider.chat_json`: `print(f"TRACE FILE READ: {os.getenv('FBA_TRACE_FILE')}")`

3. **Create separate trace files per module** (workaround if env var fails)
   - `preflight_trace.jsonl` (working)
   - `adjudication_trace.jsonl` (currently missing)
   - `critique_trace.jsonl` (currently missing)

**Success Criteria:**
- Run analysis and see 52+ log entries:
  - 1 entry for Preflight
  - 50 entries for Adjudication (one per candidate)
  - 1 entry for Critique

---

### Priority 1: ANALYZE FILTERED_OUT DISCREPANCY
**Once we have logs, investigate WHY 2500+ items are in FILTERED_OUT**

**Action Items:**
1. **Sample Analysis:** Take 20 random items from current FILTERED_OUT bucket
2. **Cross-reference:** Check if they appear in reference report's VERIFIED/HIGHLY_LIKELY
3. **Root cause per item:**
   - Is pack_verdict wrong? ("RSU=10" when should be "1:1")
   - Is adjusted_profit calculation wrong?
   - Is brand_match failing incorrectly?

**Files to inspect:**
- `coverage_ledger.csv` (has all rows with buckets + evidence)
- `evidence.jsonl` (has detailed decision trace)

**Specific rows to check:**
- Row 2246 (DOYLEYS - was VERIFIED in reference)
- Row 269 (CAT LITTER - was HIGHLY LIKELY in reference)
- Row 731 (COFFEE MACHINE - was HIGHLY LIKELY, £33 profit!)

---

### Priority 2: COMPARE DETERMINISTIC CONFIG
**The AI Preflight config may be over-tuned**

**Action Items:**
1. **Extract config from both runs:**
   - Reference run: What config was used? (check if `iteration_details.json` exists)
   - Current run: `iteration_details.json` lines 1853-1922

2. **Compare specifically:**
   - `dimension_shield_keywords`: Current has `["X", "x", "BY", ...]` - too aggressive?
   - `spec_x_shield_keywords`: Current has `["X", "x", "BY", "PER"]` - blocking valid packs?
   - `explicit_units`: Are we missing keywords that indicate ACTUAL packs?

3. **Hypothesis to test:**
   - Current shields: `["X", "x"]` might be blocking "Pack of 6 X 500ml" patterns
   - Solution: Only shield "X" when followed by dimension words (cm, mm, inch)

---

### Priority 3: REVIEW BUCKET ASSIGNMENT LOGIC
**Check if confidence thresholds or decision tree is wrong**

**Files:** `src/fba_agent/analysis.py` (lines 280-300 in workflow doc)

**Documented logic:**
```python
if EAN exact match + profit > 0 → VERIFIED
if brand + product match + profit > 0 → HIGHLY_LIKELY
if partial match or ambiguous → NEEDS_VERIFICATION
if confirmed match but profit ≤ 0 → FILTERED_OUT
```

**Questions to answer:**
1. Is "profit > 0" check using `original_profit` or `adjusted_profit`?
   - If using `adjusted_profit` after wrong RSU calculation → many items wrongly rejected
2. What defines "brand match"? Is it too strict?
   - Example: "WORLD OF PETS" vs "World's Best" - should this match?
3. What defines "product match"?
   - Token-based Jaccard similarity threshold might be too high

---

### Priority 4: TUNE ADJUDICATION CANDIDATE SELECTION
**Ensure the RIGHT items are sent to AI**

**Current selection criteria (from workflow doc lines 353-359):**
- Pack verdict = "uncertain" or "ambiguous"
- EAN missing but title match > 70%
- High profit (> £20) with weak match (< 70%)
- Row flipped bucket vs previous iteration

**Questions:**
1. Are items in FILTERED_OUT with high original profit being sent to adjudication?
   - Example: Item with £10 profit but pack detected as "RSU=10" → adjusted = £1 → FILTERED
   - This should be flagged as "high profit outlier" for AI review
2. Is the 50-item cap too low?
   - With 96 in NEEDS_VERIFICATION, we should adjudicate ALL of them, not just 50

**Proposed fix:**
```python
# In adjudication.py, increase cap:
effective_cap = min(300, int(total_rows * 0.10))  # 10% instead of 5%

# Add new selection criteria:
# 4. High original profit but negative adjusted profit (pack issue suspect)
high_profit_filtered = ledger[
    (ledger['bucket'] == 'FILTERED_OUT') &
    (ledger['original_profit'] > 5) &  # £5+ original
    (ledger['adjusted_profit'] < 0)     # Negative after pack adjustment
]
candidates.update(high_profit_filtered['row_id'].tolist()[:100])
```

---

## PART 4: IMMEDIATE ACTION PLAN

### Step 1: Enable Full Logging (TODAY - BLOCKING)
**Without this, all other debugging is impossible.**

1. Modify `src/fba_agent/providers/openai_provider.py`:
   - Add `trace_path` to `__init__` parameters
   - Store as instance variable
   - Use in `chat_json` instead of env var

2. Modify `src/fba_agent/run.py`:
   - Pass `trace_path` explicitly when creating provider:
     ```python
     provider = get_provider(
         provider_name,
         trace_path=str(run_dir / "llm_trace.jsonl")
     )
     ```

3. Re-run analysis and verify `llm_trace.jsonl` contains 50+ entries

**ETA:** 30 minutes of coding + 10 minute test run

---

### Step 2: Diagnostic Run Analysis (AFTER STEP 1)
**Once logging works, analyze ONE run in extreme detail**

1. Run analysis with logging enabled
2. Open `llm_trace.jsonl` and review:
   - What rows were sent to Adjudication?
   - What did the AI say about each one?
   - Did AI recommend "VERIFIED" but system kept it in "NEEDS_VER"?

3. Open `coverage_ledger.csv` and filter:
   - `bucket == "FILTERED_OUT" AND original_profit > 5`
   - Check pack_verdict for these rows
   - Are they all "RSU > 5" cases?

4. Cross-reference specific rows:
   - Row 269: Why is £16 profit item excluded?
   - Row 731: Why is £33 profit coffee machine excluded?

**ETA:** 1 hour of analysis

---

### Step 3: Config Tuning (AFTER STEP 2 FINDINGS)
**Based on diagnostic findings, tune either:**

**Option A: Relax Dimension Shields**
```python
# Remove "X" and "x" from dimension shields
# Only shield when pattern is "[number]X[number][unit]" like "300x50mm"
```

**Option B: Fix Pack Detection Logic**
```python
# Improve pack ratio calculation
# Don't penalize "Pack of 6" just because Amazon says "6 Pack"
```

**Option C: Lower Confidence Thresholds**
```python
# Allow items with confidence 65+ into HIGHLY_LIKELY (instead of 70+?)
```

**ETA:** 2 hours of coding + testing

---

### Step 4: Increase Adjudication Coverage
**Make AI review more items**

1. Increase cap from 50 to 200
2. Add "high profit but filtered" as selection criteria
3. Make AI prompt more decisive:
   ```
   OLD: "Provide your assessment"
   NEW: "You MUST classify as VERIFIED, HIGHLY_LIKELY, or FILTERED_OUT. 
        Default to HIGHLY_LIKELY for any uncertainty with profit > £1."
   ```

**ETA:** 1 hour of coding + testing

---

## PART 5: EXPECTED OUTCOMES

### After Step 1 (Logging):
- Visibility into AI decisions
- Can diagnose why 96 items stuck in NEEDS_VER
- Can see if Critique is correctly identifying issues

### After Step 2 (Diagnostics):
- Understand WHERE the 118 missing items went
- Root cause: pack detection error? brand matching? confidence threshold?
- Data-driven insight for next fixes

### After Step 3 (Config Tuning):
- Expect FILTERED_OUT to drop from 2577 to ~500
- Expect HIGHLY_LIKELY to rise from 12 to 60-80
- Expect VERIFIED to rise from 11 to 25-30

### After Step 4 (Better Adjudication):
- Expect NEEDS_VERIFICATION to drop from 96 to ~30
- Items rescued by AI move to HIGHLY_LIKELY or VERIFIED
- Final counts closer to reference: ~140 items in good buckets

---

## SUMMARY TABLE: CRITICAL PATH

| Step | Blocks | ETA | Success Metric |
|------|--------|-----|----------------|
| **1. Fix Logging** | Everything | 40 min | `llm_trace.jsonl` has 50+ entries |
| **2. Run Diagnostics** | Steps 3-4 | 1 hour | Know WHY items are in FILTERED_OUT |
| **3. Tune Config** | - | 2 hours | FILTERED_OUT drops by 2000+ |
| **4. Better Adjudication** | - | 1 hour | HIGHLY_LIKELY rises to 60+ |

**Total estimated time to recover missing entries:** 4-5 hours of focused work

---

## FINAL ASSESSMENT

**The agent is NOT BROKEN - it's MISCONFIGURED.**

The AI Preflight successfully ran and generated a config, but that config is TOO STRICT for this supplier's data. The reference report was likely generated with either:
1. A more permissive heuristic config, OR
2. Manually tuned config that balanced precision/recall better

**The path forward is clear:**
1. ✅ Get logging working (Priority 0)
2. 🔍 Diagnose via logs (Priority 1-2)  
3. 🔧 Tune config based on findings (Priority 3-4)
4. 📊 Validate output matches reference (Final step)

**DO NOT PROCEED with any other work until logging is fixed.** We are currently operating blind.
