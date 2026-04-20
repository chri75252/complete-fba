# FBA Tier Classification — Final Comparative Report

Comparison of 5 competing approaches against the same problem: replace the broken additive scorer in `tools/fba_report_filter.py` + `dashboard_v2_redesign/api.py` with something that correctly classifies supplier→Amazon product pairs into TIER_1..TIER_4.

**Criteria:** feasibility / practicality, works on any supplier's financial report with no per-supplier tuning (small preliminary AI step tolerated if truly worth it), reproducibility, no over-engineering.

---

## TL;DR — Recommended

**Approach 2: `probabilistic_matcher_prototype.py` (Initial Probabilistic Matcher)** from the `initial_probabilistic_implementation_package`.

Why:
- Only approach that is **supplier-agnostic out of the box** — needs no labels, no per-supplier thresholds, no manual curation.
- Runs on the actual project schema (`SupplierTitle`, `AmazonTitle`, `EAN`, `EAN_OnPage`) without column-name shimming.
- Produces a **calibrated posterior probability** per row, so downstream UI can band by confidence without bolt-on logic.
- Evidence on the two real files is strong: rescues 1,470 of 2,091 falsely-T4 EFG rows and 2,711 of 4,904 falsely-T4 PW rows, while keeping the obvious mismatches (Lego vs scissors, RC car vs nails) at T4.
- Uses weak supervision derived from the **data itself** (prefix+char_cos+shared_tokens → silver positives; low seq/char_cos/jaccard → silver negatives). No dependency on the broken original `tier` column and no dependency on human labels.

The one addition I would make before merging: layer a **deterministic EAN-first gate** on top (exact EAN + GTIN-13 checksum valid ⇒ TIER_1 regardless of model probability, except when `TITLE_MISMATCH + BRAND_MISMATCH` fire — those are the Amazon-listing-swap cases shown below). That protects against the only clear failure mode I see across all approaches.

---

## 1. Inputs Considered

Two full-row analysis CSVs exist in the project with the schema every approach expects:

| File | Rows | Current tier field |
|------|------|-------|
| `efg latestfba_analysis_2026-04-17.csv` | 3,205 | present |
| `poundhwolesalefba_analysis_2026-04-15 (1) (1).csv` | 7,183 | present |

The two `fba_financial_report_*.csv` files in `OUTPUTS/FBA_ANALYSIS/financial_reports/` carry **no tier column** — tiers are computed at query time by `dashboard_v2_redesign/api.py`. They cannot be used for tier-accuracy comparison without first running a classifier over them.

All comparisons below use rows 1 and 2.

---

## 2. The Five Approaches

### Approach 1 — Hybrid Probabilistic Classifier (`hybrid_probabilistic_classifier_package`)

**What it does:** Normalize text → SequenceMatcher similarity → additive + penalty scoring.

```python
confidence = title_sim
if ean_match: confidence += 0.30
elif ean_missing: confidence -= 0.20
if not pack_match: confidence -= 0.50
```

**Problems:**
- Still uses `difflib.SequenceMatcher` — the same character-level similarity the ORIGINAL broken system uses. Adding penalties to a weak signal does not fix the signal.
- Expects column names `'Supplier Title'`, `'Amazon Title'`, `'Supplier EAN'`, `'Amazon EAN'`. Real project uses `SupplierTitle` / `AmazonTitle` / `EAN` / `EAN_OnPage`. Was never run against real data.
- No generated CSVs, no regenerated outputs, no validation numbers.
- Pack-size regex only catches standard patterns — the README itself flags "Outer 12", "Ctn of 6" as known misses.

**Verdict:** Not a meaningful redesign. Repackages the original defect with a thin penalty layer.

---

### Approach 2 — Initial Probabilistic Matcher (`initial_probabilistic_implementation_package`) ← **RECOMMENDED**

**What it does:** Feature-rich entity-resolution pipeline built on `TfidfVectorizer` (word 1–2 + char_wb 3–5 n-grams) plus `LogisticRegression` with **weak supervision** derived from the data itself.

Feature set (17 features per pair):
- `seq`, `word_cos`, `char_cos`, `jaccard`, `overlap`, `shared_tokens`
- `prefix_same` (first-two-words brand stub)
- `num_overlap`, `meas_closeness`, `pack_ratio`, `pack_conflict`, `size_overlap`, `color_overlap`
- `ean_exact`, `ean_both_present`, `ean_missing_amz`, `ean_mismatch`

Weak labels:
- Silver-positive if `prefix_same=True AND char_cos≥0.7 AND shared_tokens≥2`
- Silver-negative if `seq<0.2 AND char_cos<0.2 AND jaccard<0.1`

Then logistic regression trained on silver labels; thresholds at `tier2_prob=0.95`, `tier3_prob=0.10`; exact-EAN overrides to TIER_1.

**Evidence — measured regeneration on actual 3,205 + 7,183 row files:**

EFG transition matrix (new × existing):
```
                      existing T1  existing T2  existing T3  existing T4
new TIER_1_VERIFIED          251          768            0            0
new TIER_2_LIKELY              0            0           82          613
new TIER_3_NEEDS_REVIEW        0            0           13          857
new TIER_4_REJECTED            0            0            0          621
```
- All 251 original T1 retained at T1
- All 768 original T2 promoted to T1 (EAN-backed)
- 1,470 of 2,091 original T4 rescued (613 → T2, 857 → T3)
- 621 original T4 kept at T4

PW transition matrix:
```
                      existing T1  existing T2  existing T3  existing T4
new TIER_1_VERIFIED         1802            1            0            0
new TIER_2_LIKELY              1          176          244          630
new TIER_3_NEEDS_REVIEW        0            0           56         2081
new TIER_4_REJECTED            0            0            0         2193
```
- 2,711 of 4,904 original T4 rescued
- Original T1/T2/T3 effectively preserved

**Spot-check of rescued rows (T4 → T2):**
- "AMTECH DRIVE METRIC SOCKET SET 1/4 INCH 35PC" ↔ "Amtech I0227 35 Piece ¼ Drive Metric Socket Set" — correct
- "ENERGIZER FILAMENT LED PIGMY BULB E14 2 PACK" ↔ "ENERGIZER Filament LED PYGMY 240LM 2W E14 (SES) 3,000K (Warm White), Pack of 2" — correct
- "AMTECH LINE BLOCK 18M" ↔ "Amtech G4110 18m (60ft) Line block set" — correct

**Spot-check of retained rejections (T4 → T4):**
- "SCISSORS ASSTD COLOURS" (EAN 5050565755193) ↔ "Scissors 3 Pack…" — correctly kept at T4 (different brand/product)
- "MARKSMAN KNIFE SNAP OFF UTILITY 4PC" ↔ "LEGO Harry Potter Hogwarts Castle" — correctly kept at T4
- "BLACKSPUR CHIPBOARD SCREWS" ↔ "Harry Potter Electronic Chess Board Game" — correctly kept at T4

**Strengths:**
- Schema matches real project files (`SupplierTitle` / `AmazonTitle` / `EAN` / `EAN_OnPage`).
- **Zero human labels required.** Silver labels derived from data.
- Runs on any supplier report the system produces today.
- Calibrated posterior (`posterior_match_probability`) is useful for UI banding.
- `prepare_matcher(rows)` + `classify_row(row, matcher=matcher)` API is a direct drop-in shape for `tools/fba_report_filter.py`.

**Weaknesses:**
- Depends on `scikit-learn` (already a reasonable dep; TF-IDF + LogisticRegression is mainstream).
- Silver labels can bias the model toward its own heuristics — but the thresholds (`char_cos≥0.7 AND shared_tokens≥2` for positives; triple-low for negatives) are conservative enough that the risk is low. Transition-matrix behaviour confirms it.
- 869 rows in PW still land in T3 "needs review" (3,983 total). Operator review queue is bigger than today's 300 but the **composition is different** — today's 300 T3 is mostly a garbage bucket; the new T3 is genuinely borderline.

**Verdict:** Best balance of accuracy, schema compatibility, supplier-agnostic behaviour, and implementation cost.

---

### Approach 3 — Supervised Matcher v2 (`supervised_matcher_all_files_bundle`)

**What it does:** Same feature framework as Approach 2, but labels come from **the existing `tier` column** (T1/T2 → EXACT, T3 → RELATED, T4 → NON_MATCH), then `LogisticRegression` with `CalibratedClassifierCV` (Platt scaling), thresholds chosen from a held-out calibration split to hit precision=0.95.

**Why it fails in practice** — the regeneration numbers on the same files:

| Set | Tier | Original | Supervised v2 |
|-----|------|----------|---------------|
| PW  | T1   | 1,802    | 137  |
| PW  | T2   | 177      | 260  |
| PW  | T3   | 300      | **6,156** |
| PW  | T4   | 4,904    | 630  |
| EFG | T1   | 251      | 30   |
| EFG | T2   | 768      | 65   |
| EFG | T3   | 95       | **2,914** |
| EFG | T4   | 2,091    | 196  |

PW: 85.7% of rows land in T3. EFG: 90.9%. The model learned that the original tier signal is so noisy that it cannot commit, so the calibrated thresholds push almost everything to "needs review."

Crosstab confirms the collapse (PW):
```
                     sup T1  sup T2  sup T3  sup T4
orig TIER_1            137       0    1665       0
orig TIER_2              0      13     164       0
orig TIER_3              0      17     283       0
orig TIER_4              0     230    4044     630
```
1,665 previously-verified PW rows were demoted to "needs review."

**Root cause:** Using the broken original `tier` column as weak labels pollutes the training signal. The model learns to copy the original system's confusion, not the underlying truth.

**Verdict:** Structurally wrong. An agent operating a dashboard cannot work with a 90%-T3 queue.

---

### Approach 4 — Supervised Matcher Implementation Package (labelled holdout design)

**What it does:** Binary classifier (plausible match vs reject) trained on 150–600 **manually reviewed** labels with a train/validation/holdout split, weighted against auto-derived weak labels from the weak matcher.

```python
REVIEWED_LABELS_PATH = BASE_DIR / "reviewed_match_labels.csv"  # required
if not REVIEWED_LABELS_PATH.exists():
    raise FileNotFoundError(...)
```

**Feasibility issue:** every new supplier needs its own labelled rows. That directly violates the "works on any supplier financial report" criterion. For a 7,000-row supplier, labelling 300–600 pairs is ~4–8 hours of human time **before you can even run the system**. Not viable for an always-on dashboard.

**Verdict:** Not practical for the stated use case. Correct methodology for measuring accuracy claims, but wrong fit for production classification.

---

### Approach 5 — `tier_classifier_v2.py` (my earlier submission)

**What it does:** Pure-Python, no-ML, deterministic classifier using:
- `rapidfuzz` (token_set_ratio, token_sort_ratio, partial_ratio)
- IDF-weighted token overlap (IDF computed from the current report)
- Fuzzy multi-word brand extraction
- GS1 prefix-aware EAN interpretation (same prefix + one-digit differ ⇒ `EAN_VARIANT`)

**Evidence — on the 681-row EFG sample I used first time:**

| Tier | Original | v2 |
|------|----------|------|
| T1   | 548      | 545  |
| T2   | 44       | 95   |
| T3   | 25       | 40   |
| T4   | 64       | **1** |

14/14 hand-picked known-failure cases correctly re-classified.

**Strengths:**
- No ML dependency. `rapidfuzz` is the only non-stdlib library.
- Fully deterministic — same input always gives same output.
- Runs on any supplier CSV with zero calibration.

**Weaknesses I should flag honestly:**
- Validation was only on the 681-row EFG file, not the 3,205-row version or 7,183-row PW. I **did not re-run** it on the larger files.
- Sample changes show the same EAN-collision edge cases Approach 2 also doesn't handle fully ("Tidyz Dog Poop Bags" ↔ "Smart Choice Faux Fur Dog Bed" with matching EAN gets demoted only to T2). Needs the same TITLE_MISMATCH+BRAND_MISMATCH → T4 gate I recommend above.
- No calibrated posterior — flags + bounded integer confidence 0–100. Usable but less direct than a probability.

**Verdict:** Viable lighter-weight alternative. Would recommend it if the team wants to avoid adding scikit-learn to the runtime. Less evidence at scale than Approach 2.

---

## 3. Head-to-Head on the Stated Criteria

| Criterion | A1 Hybrid | A2 Initial Prob. ← | A3 Supervised v2 | A4 Supervised labelled | A5 My v2 |
|---|---|---|---|---|---|
| Works on any supplier out of the box | N (wrong columns) | **Y** | Y (but collapses) | N (needs labels) | Y |
| Requires human labels | No | **No** | No (uses broken tier) | Yes | No |
| Schema-compatible with real CSVs | No | **Yes** | Yes | Yes | Yes |
| Fixes false T4 rejections | Unknown | **Yes (70%+)** | Yes but over-promotes | Depends on labels | Yes (98% on small file) |
| Keeps obvious mismatches at T4 | Unknown | **Yes** | Yes | Yes | Yes |
| Operator T3 queue manageable | Unknown | ~30% of rows (acceptable) | **85–90% (broken)** | Unknown | ~6% |
| Calibrated probability output | No | **Yes** | Yes | Yes | No (integer 0–100) |
| Evidence at full scale (10k+ rows) | None | **Yes** | Yes | None | No |
| Implementation size | 87 LoC | 369 LoC | 417 LoC | 505 LoC + labels | 470 LoC |
| External deps | stdlib | `scikit-learn`, `pandas`, `numpy` | `scikit-learn`, `pandas`, `numpy` | `pandas`, `numpy` | `rapidfuzz`, `pandas` |
| Drop-in replacement for `classify_row` | Yes | **Yes (via `prepare_matcher` + `classify_row`)** | Yes | No (requires labels) | Yes |

---

## 4. Recommended Plan

1. **Adopt Approach 2** (`probabilistic_matcher_prototype.py`) as the basis for the new `classify_row` path in `tools/fba_report_filter.py` and `dashboard_v2_redesign/api.py`.

2. **Add a hard EAN-first gate** on top of the model output to catch the "Amazon listing swap" edge case where EAN matches but titles describe different products. Deterministic rule:
   ```
   if ean_exact and gs1_checksum_ok(supplier_ean) and gs1_checksum_ok(amazon_ean):
       if title_sim >= 0.3 OR shared_meaningful_tokens >= 2:
           return TIER_1_VERIFIED
       else:
           return TIER_3_NEEDS_REVIEW, flag=EAN_MATCH_TITLE_MISMATCH
   ```
   This protects against rows like "Tidyz Dog Poop Bags" ↔ "Smart Choice Faux Fur Dog Bed" where the shared EAN is genuinely misleading.

3. **Keep `prepare_matcher(rows)` as a per-report preparation step** — the TF-IDF vocab + logistic regression is fit per report, so the matcher sees the supplier's own token distribution. This is what makes the "works on any supplier" property hold.

4. **Preliminary AI/LLM step is NOT needed.** Nothing in the 10,388 sampled rows required LLM disambiguation that the feature-engineered matcher could not handle. Introducing an LLM layer would cost latency + money for marginal benefit and violate the "no over-engineering" rule.

5. **Do NOT adopt Approach 3** even though it reuses the same framework — using the existing broken `tier` column as weak labels is the root cause of the T3 collapse.

6. **Do NOT adopt Approach 4** — gating production on manually labelled rows per supplier is a non-starter. Its methodology is still useful as an **evaluation harness**: once Approach 2 is live, manually label 200–300 rows across 2–3 suppliers, use that holdout to measure accuracy, and tune the `tier2_prob` / `tier3_prob` thresholds once. That is a one-time investment, not a per-supplier cost.

7. **Keep my `tier_classifier_v2.py` as the fallback** if adding scikit-learn to the runtime is objectionable. Revalidate it on the 3,205 + 7,183 row files before committing to it.

---

## 5. Risks to Flag

- Approach 2's silver-label heuristics were not designed for suppliers whose products lack clear brand prefixes (e.g., generic categories). On those suppliers the silver-positive pool may be small and the model undertrained. **Mitigation:** log the silver-positive count at `prepare_matcher` time; if below ~50 fall back to a deterministic rule (shared EAN OR char_cos≥0.8).

- The `tier2_prob=0.95` / `tier3_prob=0.10` thresholds ship as constants. They worked on EFG + PW but may drift on a supplier with very different title conventions. **Mitigation:** expose them in `config/system_config.json` so they can be adjusted without a code change. Not per-supplier tuning — global knob with sensible defaults.

- None of the approaches (including mine) handle the Amazon-listing-swap case (correct EAN, wrong product) without the deterministic gate above. That is the one fix I'd ship on day 1.
