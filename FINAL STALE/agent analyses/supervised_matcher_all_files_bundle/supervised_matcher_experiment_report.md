# Supervised Matcher Experiment Report (v2)

## Inputs (ONLY)
- poundhwolesalefba_analysis_2026-04-15 (1) (1)(1).csv (7183 rows)
- efg latestfba_analysis_2026-04-17 (1).csv (3205 rows)
Ignored: the ~681/682-row list (per your instruction).

## Outputs (ONLY these newly generated tiered reports + stats)
- poundwholesale_supervised_tiered.csv
- efghousewares_supervised_tiered.csv
- supervised_matcher_summary_counts.csv
- supervised_matcher_summary.json
- poundwholesale_original_vs_supervised_crosstab.csv
- efghousewares_original_vs_supervised_crosstab.csv

## What changed vs v1
v1 used fixed probability thresholds and collapsed into TIER_3 because model probabilities did not reach the fixed cutoffs.
v2 **selects thresholds from the held-out calibration split** to meet a precision target (default 0.95) with minimum support (default 200).

Selected thresholds from this run:
- P_EXACT_T2 = 0.2979
- P_EXACT_T1 = 0.2979
- P_NONMATCH_T4 = 0.6782

## Methodology (replicable)
1) Build pairwise features from SupplierTitle/AmazonTitle/EAN/EAN_OnPage (plus aux numeric fields).
2) Use weak labels derived from `tier`:
   - T1/T2 -> EXACT(2), T3 -> RELATED(1), T4 -> NON_MATCH(0)
3) Split into train vs calibration.
4) Train multinomial LogisticRegression.
5) Calibrate probabilities with Platt scaling on the calibration split.
6) Choose thresholds from calibration to hit precision target.
7) Predict on both full reports.
8) Map to tiers and write outputs.

## Calibration/config knobs (what an agent may need to tune)
- dictionaries: STOP_WORDS, UNIT_WORDS, COLOR_WORDS, CATEGORY_KEYWORDS
- pack parsing patterns
- precision_target and min_support used when selecting thresholds
- hard conflict gates: category_disjoint, measure_conflict
- model type/hyperparams

## Output schema (key columns)
Original columns preserved, plus:
- tier_original / confidence_original / flags_original / reasons_original / ean_exact_match_original
- tier_supervised
- match_state_supervised
- p_exact / p_related / p_nonmatch

## Counts summary
Pound original: {'TIER_4_REJECTED': 4904, 'TIER_1_VERIFIED': 1802, 'TIER_3_NEEDS_REVIEW': 300, 'TIER_2_LIKELY': 177}
Pound supervised: {'TIER_3_NEEDS_REVIEW': 6156, 'TIER_4_REJECTED': 630, 'TIER_2_LIKELY': 260, 'TIER_1_VERIFIED': 137}

EFG original: {'TIER_4_REJECTED': 2091, 'TIER_2_LIKELY': 768, 'TIER_1_VERIFIED': 251, 'TIER_3_NEEDS_REVIEW': 95}
EFG supervised: {'TIER_3_NEEDS_REVIEW': 2914, 'TIER_4_REJECTED': 196, 'TIER_2_LIKELY': 65, 'TIER_1_VERIFIED': 30}

## Agent note (required)
Your agent may make **minor adjustments** if needed because it has access to your full local workflow.
If it changes schema assumptions, dictionaries, thresholds, features, or model settings, it must document what changed and ask for confirmation where tier semantics may shift.


---
## Full runnable script
Saved alongside this report as: `fba_supervised_matcher_experiment.py`
