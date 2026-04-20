# FBA Tier Classification — Revised Comparative Report (v2)

You pushed back — rightly — that my first report dismissed approaches based on the state they shipped in, not the state they could reach after fixing the obvious bugs. I have now **re-run every approach in its best-effort corrected form** on the full 3,205 + 7,183-row files and compared them head-to-head. The data is in `TIER_CLASSIFICATION_RESEARCH/rerun/`.

## TL;DR — Recommendation Stands

**Approach 2 (`initial_probabilistic_implementation_package/probabilistic_matcher_prototype.py`) remains the best.** The corrections made A1 and A3 no better (A1 worse, A3 structurally broken even with clean labels). A4 with 184 AI-generated labels closes the gap on holdout accuracy but is **too conservative to solve the actual problem** (false T4 rejections). My v2 (A5) is a viable simpler fallback but is more permissive than A2 without evidence it should be.

Full numbers below so you can check the reasoning.

---

## 1. What I Fixed and Reran

| Approach | Correction applied | Ran on |
|----------|--------------------|--------|
| A1 Hybrid | Column-name mapping (`'Supplier Title'` → `'SupplierTitle'` etc.) so the classifier actually sees data | EFG 3,205 + PW 7,183 |
| A3 Supervised v2 | Replaced the broken `tier`-column labels with **clean labels derived from data itself** (EAN+checksum+high title_sim → EXACT; very low similarity+brand mismatch → NON_MATCH; unlabelled otherwise) | EFG 3,205 + PW 7,183 |
| A4 Supervised labelled | Generated **184 high-confidence labels** (100 positive / 84 negative, including pack-difference positives and Amazon-listing-swap negatives), 70/15/15 split, weighted 4× vs auto-labels | EFG 3,205 + PW 7,183 |
| A5 My v2 | Re-ran on the full files (previously only tested on 681-row sample) | EFG 3,205 + PW 7,183 |
| A2 baseline | Already has results on full files | EFG 3,205 + PW 7,183 |

All corrected scripts + CSV outputs are in `TIER_CLASSIFICATION_RESEARCH/rerun/`:
- `run_a1_fixed.py`, `a1_fixed_{efg,pw}.csv`, `a1_fixed_summary.json`
- `run_a3_corrected.py`, `a3_corrected_{efg,pw}.csv`, `a3_corrected_summary.json`
- `run_a4_with_labels.py`, `a4_generated_labels.csv`, `a4_labelled_{efg,pw}.csv`, `a4_labelled_summary.json`
- `run_my_v2.py`, `my_v2_{efg,pw}.csv`, `my_v2_summary.json`

---

## 2. Tier Distributions After Correction

### EFG (3,205 rows)

| Tier | Original | A1 fixed | A2 | A3 corrected | A4 (184 labels) | A5 my v2 |
|------|----------|----------|----|-----|-----|-----|
| T1   | 251      | 395      | **1,019** | 144 | 1,006 | **1,019** |
| T2   | 768      | 14       | **695**   | 0   | 125   | 595 |
| T3   | 95       | 342      | 870   | **2,958** | 391 | 1,304 |
| T4   | 2,091    | **2,454**    | 621   | 103 | 1,683 | **287** |

### PW (7,183 rows)

| Tier | Original | A1 fixed | A2 | A3 corrected | A4 (184 labels) | A5 my v2 |
|------|----------|----------|----|-----|-----|-----|
| T1   | 1,802    | **0**    | 1,803 | 234 | 1,767 | 1,799 |
| T2   | 177      | 125      | **1,050** | 0   | 200   | 794 |
| T3   | 300      | 427      | 2,137 | **6,544** | 437 | **3,983** |
| T4   | 4,904    | **6,631**    | 2,193 | 405 | 4,779 | **607** |

### Key read

- **A1 fixed is worse than original.** PW ended with **zero** T1 verifications and T4 increased from 4,904 → 6,631. `SequenceMatcher` on long Amazon titles vs short supplier titles produces ratios too low to clear any sensible threshold. Fixing the column names did not fix the signal. **Verdict: dead end.**
- **A3 corrected still collapses to T3.** With clean labels the model trains cleanly — `pos=2,801 neg=1,664` — but the Platt calibration + precision=0.95 threshold selection drove `P_EXACT_T2`, `P_EXACT_T1`, `P_NONMATCH_T4` all to **1.000**, meaning almost nothing clears any cut. 92% of EFG and 91% of PW landed in T3. This is a **structural property of the supervised-v2 calibration+threshold selection loop**, not a label problem. **Verdict: not salvageable within that framework.**
- **A4 with 184 generated labels** runs cleanly. On the 29-row holdout it scores 100% vs A2's 96.5%. But look at what it actually does to the full report: rescues only 408 false T4s on EFG (vs A2's 1,470) and only 125 on PW (vs A2's 2,711). It is **too conservative for the actual job** — the whole point is to recover false rejections and it recovers far fewer than A2.
- **A5 (my v2) on full files** rescues the most T4s (EFG 287 remaining, PW 607 remaining) but has no supporting evidence those rescues are correct at scale.

---

## 3. How Many False T4s Does Each Approach Rescue?

Measured as: original-T4 rows that moved to T1/T2/T3 under each approach.

| Approach | EFG rescued from T4 | PW rescued from T4 | Combined |
|----------|-------|-----|-----|
| A1 fixed | 94    | 31    | 125 |
| A2       | 1,470 | 2,711 | **4,181** |
| A3 corrected | 1,988 | 4,499 | 6,487 *(but nearly all to T3)* |
| A4 labelled  | 408   | 125   | 533 |
| A5 my v2     | 1,816 | 4,297 | 6,113 *(mix of T2/T3)* |

Of those rescues, how many landed in actionable tiers (T1 + T2, not "needs review")?

| Approach | EFG T4→T1/T2 | PW T4→T1/T2 | Combined |
|----------|--------------|-------------|----------|
| A1 fixed | 33  | 1   | 34 |
| A2       | 613 | 630 | **1,243** |
| A3 corrected | 0 | 0 | 0 *(zeroed T2 entirely)* |
| A4 labelled  | ~20 | ~30 | ~50 |
| A5 my v2     | ~512 | ~627 | ~1,139 |

A2 puts the most rows into the "actually promote to listing" bucket. A5 is close. Everything else abandons the rescue problem.

---

## 4. Holdout Accuracy (A4's 29-row holdout)

| Model | Acc | Precision | Recall | F1 | FP | FN |
|-------|-----|-----------|--------|-----|-----|-----|
| A2 weak baseline | 0.966 | 0.944 | 1.000 | 0.971 | 1 | 0 |
| A4 supervised (184 labels) | **1.000** | 1.000 | 1.000 | 1.000 | 0 | 0 |

A4 wins the holdout by one false positive. But the holdout is only 29 rows, so the difference is statistically not meaningful, and the holdout was drawn from the same high-confidence pool the labels came from — it does **not** test the hard cases (listing swaps, pack-size matches, missing EAN). This is the exact measurement pitfall the A4 README warned about.

Even accepting A4's marginally better calibration, **on the actual 10,388-row job it rescues roughly 12% of what A2 rescues into usable tiers**. That is the wrong trade-off for the stated use case.

---

## 5. Corrected Ranking

| Rank | Approach | Why |
|------|----------|-----|
| **1** | **A2 — Initial Probabilistic Matcher** | Largest actionable rescue (1,243 rows into T1/T2); no labels needed; schema-native; calibrated posterior; confirmed by manual spot-check of ~30 rescued and kept rows |
| 2 | A5 — my v2 | Similar T1 count to A2; rescues more but more of them land in T3 "needs review"; no ML dep (`rapidfuzz` only). Viable if you do not want `scikit-learn` in the runtime |
| 3 | A4 — labelled supervised | Best holdout precision, but too conservative on the full data; 184 labels was enough to train, meaning scaling to 300–500 labels is feasible if you wanted to pursue this; not worth it over A2 for current needs |
| 4 | A3 — supervised v2 even with clean labels | Structurally collapses to T3 because Platt-calibrated thresholds + precision=0.95 drive cuts to 1.000. Not fixable without rewriting the threshold-selection logic |
| 5 | A1 — hybrid probabilistic (fixed) | `SequenceMatcher` is the wrong algorithm for this data regardless of column mapping; gets worse than the original |

---

## 6. Why A2 Still Wins After Corrections

- **A3 could not be rescued without rewriting the calibration step** — the threshold-selection logic is the failure, not the labels.
- **A4's labels are expensive at scale.** Generating 184 took a rule-based scan of the data. Scaling to 500 for real coverage means ~3–5 hours of either manual review OR an LLM call per candidate pair. A2 avoids this cost entirely.
- **A1 has a fundamental algorithm problem.** No column fix changes that.
- **A5 is close to A2 but has less validated coverage.** Could replace A2 if a no-sklearn runtime is required.

---

## 7. One Caveat I Want to Flag

My rule-based label generator found only **11 ambiguous-positive** (pack-size difference, same product) pairs and **3 listing-swap** (EAN match, different product) pairs. Those are the cases that matter most for stress-testing, and a rule-based labeller cannot find enough of them. A real 200-row human-labelled set would contain far more of these edge cases and would be a better evaluation set for A4. If you want, the next useful step is not more model experimentation — it is **label 200 rows across those specific edge cases** so we can measure each approach's behaviour on them in isolation. That would give a defensible accuracy number rather than the "rescue count" proxy used above.

---

## 8. Unchanged Recommendation

Ship A2 as the classifier in `tools/fba_report_filter.py` and `dashboard_v2_redesign/api.py`, with the deterministic EAN+title gate I described in the first report to handle the Amazon-listing-swap edge case:

```python
if ean_exact and gtin_checksum_ok(supplier_ean) and gtin_checksum_ok(amazon_ean):
    if title_sim >= 0.25 or shared_meaningful_tokens >= 2:
        return TIER_1_VERIFIED
    else:
        # EAN matches but titles describe different products — Amazon listing swap
        return TIER_3_NEEDS_REVIEW, flag="EAN_MATCH_TITLE_MISMATCH"
```

No LLM pre-step is needed. The evidence after correcting all four competing approaches does not change that answer.
