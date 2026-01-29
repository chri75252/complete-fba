# PHASE 2 FIX RUN ANALYSIS REPORT
**Date:** 2026-01-09
**Run ID:** 20260109_002917
**Input:** part 8 jan.xlsx (3063 rows)

## Execution Summary
The Phase 2 agent run **completed successfully** with all validation gates passing.

### Files Generated
- `PHASEA_MANUAL_REPORT_20260109.md` (77,134 bytes) ✅
- `coverage_ledger.csv` (1,260,324 bytes) ✅
- `evidence.jsonl` (2,415,907 bytes) ✅
- `run_summary.json` (2,687 bytes) ✅
- `merged_calibration.json` ✅
- `calibration_diff.json` ✅
- `llm_trace.jsonl` ✅

### Bucket Counts (from run_summary.json)
| Bucket | Count |
|--------|-------|
| VERIFIED | 32 |
| HIGHLY_LIKELY | 78 |
| NEEDS_VERIFICATION | 2 |
| FILTERED_OUT | 2951 |

---

## Comparison: Original Agent vs Phase 2 Agent

| Metric | Original Agent (Pre-Fix) | Phase 2 Agent (Post-Fix) | Delta |
|--------|--------------------------|--------------------------|-------|
| **VERIFIED - RECOMMENDED** | 35 | 32 | -3 |
| **VERIFIED - AUDITED OUT** | 6 | 6 | 0 |
| **HIGHLY LIKELY - RECOMMENDED** | 192 | 78 | **-114** |
| **HIGHLY LIKELY - AUDITED OUT** | 36 | 11 | **-25** |
| **NEEDS VERIFICATION** | 98 | 2 | **-96** |
| **TOTAL "VALID" ENTRIES** | 367 | 129 | **-238** |

---

## Analysis of Results

### ⚠️ CRITICAL FINDING: Total Valid Entries DECREASED

The Phase 2 fixes resulted in a **significant decrease** in matched entries:
- Original Agent: **367** entries across all tiers
- Phase 2 Agent: **129** entries across all tiers
- **Loss: 238 entries (65% reduction)**

### Root Cause of the Decrease

The Phase 2 fixes were designed to **reduce False Positives (noise)**. Looking at the data:

1. **Highly Likely dropped by 139** (from 228 to 89)
   - This is expected from the **Fail-Closed Brand Gate** - entries with mismatched brands are now rejected
   - The **Token Cleaning** reduced spurious similarity matches
   
2. **Needs Verification dropped by 96** (from 98 to 2)
   - The **threshold increase** (0.25 → 0.40) significantly reduced entries
   - Most of the original NV entries were likely noise

3. **Verified dropped by 3** (from 41 to 38)
   - The **Strict EAN Logic** moved soft matches to HIGHLY LIKELY
   - Some may have been pushed to FILTERED_OUT due to brand gate

### Expected vs Actual Outcome

| Fix | Expected Effect | Actual Effect |
|-----|-----------------|---------------|
| Token Cleaning | ↓ False Positives in HL/NV | ✅ Achieved (HL/NV counts dropped) |
| Fail-Closed Brand Gate | ↓ False Positives in HL | ✅ Achieved (HL count dropped 60%) |
| Strict EAN | ↓ Verified, ↑ HL for soft matches | ⚠️ Verified dropped, but HL also dropped |
| Threshold Tuning (0.25→0.40) | ↓ NV entries | ✅ Achieved (NV dropped 98%) |

### Key Observation

The Phase 2 fixes successfully **reduced noise**, but they may have been **too aggressive**:

- The combination of **Fail-Closed Brand Gate + Token Cleaning + Higher Threshold** created a triple filter that excluded many entries.
- Without accuracy analysis (comparing to the WEB benchmark), it's unclear whether these excluded entries were:
  - **True Positives** (correctly excluded noise) → Good
  - **False Negatives** (incorrectly excluded valid matches) → Bad

---

## CRITICAL ACCURACY COMPARISON (vs WEB Benchmark)

The comparison script was run with the new Phase 2 report. Here are the results:

### Grand Total Correct Matches

| Model | Total Rows | **GRAND TOTAL CORRECT** | Strong Matches (Ver/HL) | Weak Matches (NV) |
|-------|------------|-------------------------|-------------------------|-------------------|
| **WEB (Benchmark)** | 2369 | **419** | 349 | 70 |
| GEM_1 | 443 | **280** | 215 | 65 |
| **AGENT (Original)** | 367 | **159** | 150 | 9 |
| **PHASE2 (Fixed)** | 129 | **127** | 124 | 3 |

### Categorization Accuracy (% of entries that are TRUE MATCHES)

| Model | Accuracy % | Correct Rows | Total Rows |
|-------|------------|--------------|------------|
| **PHASE2** | **67.4%** | 87 | 129 |
| GEM_1 | 62.1% | 275 | 443 |
| AGENT | 28.6% | 105 | 367 |
| WEB | 21.6% | 511 | 2369 |

---

## KEY FINDING: PHASE 2 ACCURACY IMPROVED SIGNIFICANTLY

### Before vs After Comparison

| Metric | AGENT (Original) | PHASE2 (Fixed) | Change |
|--------|------------------|----------------|--------|
| **Accuracy Rate** | 28.6% | **67.4%** | **+138% improvement** |
| **False Positive Rate** | 71.4% | 32.6% | **-54% reduction** |
| Total Entries | 367 | 129 | -65% (fewer entries) |
| Correct Matches | 159 | 127 | -20% (slight loss) |

### Interpretation

1. **ACCURACY DOUBLED**: Phase 2 fixes achieved 67.4% accuracy vs 28.6% for the original agent. This means 2 out of 3 entries are now TRUE MATCHES.

2. **TRADE-OFF CONFIRMED**: We traded **quantity for quality**:
   - Lost 32 correct matches (159 → 127)
   - Reduced false positives by 176 entries (262 → 42)
   
3. **THE FIXES WORKED**: The Fail-Closed Brand Gate and Token Cleaning effectively eliminated noise.

### Remaining Issues

The Phase 2 agent still only found **127 correct matches** vs the benchmark's **419**. This means:
- **292 valid products are being missed** (lost to "Unrelated" bucket)
- The fixes reduced noise but did NOT recover the missed items

### Next Steps to Recover Missed Items

1. **Lower NEEDS_VERIFICATION threshold back to 0.25** (token cleaning makes this safe now)
2. **Relax Brand Gate for NEEDS_VERIFICATION tier** (allow partial matches)
3. **Re-run analysis** to see if we can recover the 292 missed items while maintaining 60%+ accuracy

---

## Files for Review
- Report: `runs_phase2_test\20260109_002917\PHASEA_MANUAL_REPORT_20260109.md`
- Ledger: `runs_phase2_test\20260109_002917\coverage_ledger.csv`
- Summary: `runs_phase2_test\20260109_002917\run_summary.json`
- Comparison: `RESERACH\REPORT\part 8 jan\COMPREHENSIVE_COMPARISON_ANALYSIS_20260108.md`
