# Initial Probabilistic Matcher Regeneration Report

## Purpose

This report documents the rerun of the **initial probabilistic matcher** on the two newly attached **correct full-row analysis files**, while explicitly **ignoring the earlier 681/682-row mismatched EFG list** for row-level regeneration purposes.

This report is intended to be passed to an agent with local file access so it can reproduce the same approach, inspect the exact output files, and make minor local-path or workflow adjustments where required.

---

## What was done

I reran the initial probabilistic matcher on these two attached files:

1. `efg latestfba_analysis_2026-04-17.csv`
2. `poundhwolesalefba_analysis_2026-04-15 (1) (1).csv`

Both files already contained pre-existing tier fields:

- `tier`
- `confidence_score`
- `flags`
- `reasons`
- `ean_exact_match`

Instead of overwriting them, the rerun preserved those existing fields and appended the newly assigned matcher outputs as:

- `new_tier`
- `new_confidence_score`
- `new_reasons`
- `new_flags`
- `new_ean_exact_match`
- `posterior_match_probability`

This means the regenerated outputs are directly comparable row-by-row against the tiers already present in the attached files.

---

## Important interpretation note

These newly attached files are the correct full-row analysis files and were treated as the actual rerun targets.

No row-level dependency on the earlier 681/682-row EFG list was used here.

That earlier list was effectively a different dataset and is excluded from this regeneration workflow.

---

## Whether the script/filtering criteria needed adjustment

No major adjustment was required.

Reason:
- the two attached files use the same analysis-style schema already expected by the initial probabilistic rerun workflow,
- they already contain the key columns required by the matcher,
- therefore the same matcher thresholds and the same batch rerun logic were usable as-is.

The rerun used these matcher thresholds:

- `tier2_prob = 0.95`
- `tier3_prob = 0.10`

The deterministic handling of exact valid EAN matches was preserved by the prototype logic.

---

## Input format required

The rerun script expects each analysis CSV to contain, at minimum:

- `SupplierTitle`
- `AmazonTitle`
- `EAN`
- `EAN_OnPage`

It will also preserve and compare existing tier fields if they exist:

- `tier`
- `confidence_score`
- `flags`
- `reasons`
- `ean_exact_match`

Strongly recommended additional columns include:

- `ASIN`
- `SupplierPrice_incVAT`
- `SellingPrice_incVAT`
- `NetProfit`
- `ROI`
- `SupplierURL`
- `AmazonURL`
- `Category`

The two attached files already contained all relevant fields required for the rerun.

---

## Rerun script

The exact standalone local rerun script is provided separately as:

- `regenerate_initial_probabilistic_outputs.py`

Its job is to:

1. load `probabilistic_matcher_prototype.py`
2. load the two attached CSVs
3. run the matcher on each row set
4. preserve existing tier-related columns
5. append newly generated probabilistic outputs
6. write:
   - regenerated output CSVs
   - tier-change CSVs
   - per-file summaries
   - master summary JSON

---

## Output files generated

### Regenerated CSVs

- `initial_probabilistic_regenerated_outputs/efg_latest_analysis__probabilistic_regenerated.csv`
- `initial_probabilistic_regenerated_outputs/pound_latest_analysis__probabilistic_regenerated.csv`

### Tier-change CSVs

- `initial_probabilistic_regenerated_outputs/efg_latest_analysis__tier_changes.csv`
- `initial_probabilistic_regenerated_outputs/pound_latest_analysis__tier_changes.csv`

### Summaries

- `initial_probabilistic_regenerated_outputs/efg_latest_analysis__summary.json`
- `initial_probabilistic_regenerated_outputs/pound_latest_analysis__summary.json`
- `initial_probabilistic_regenerated_outputs/run_summary.json`

---

## Summary results

### EFG latest analysis

- Rows: 3,205
- Existing tier counts: TIER_4_REJECTED: 2,091, TIER_2_LIKELY: 768, TIER_1_VERIFIED: 251, TIER_3_NEEDS_REVIEW: 95
- New tier counts: TIER_1_VERIFIED: 1,019, TIER_3_NEEDS_REVIEW: 870, TIER_2_LIKELY: 695, TIER_4_REJECTED: 621
- Existing average confidence: 23.72
- New average confidence: 68.41
- New exact-EAN matches: 1,019
- Rows where existing tier != new tier: 2,320

### Pound latest analysis

- Rows: 7,183
- Existing tier counts: TIER_4_REJECTED: 4,904, TIER_1_VERIFIED: 1,802, TIER_3_NEEDS_REVIEW: 300, TIER_2_LIKELY: 177
- New tier counts: TIER_4_REJECTED: 2,193, TIER_3_NEEDS_REVIEW: 2,137, TIER_1_VERIFIED: 1,803, TIER_2_LIKELY: 1,050
- Existing average confidence: 19.53
- New average confidence: 55.28
- New exact-EAN matches: 1,803
- Rows where existing tier != new tier: 2,956

---

## How to interpret the regenerated outputs

Each regenerated CSV contains both:

- the **existing tier fields** already present in the attached analysis file
- the **newly generated tier fields** appended by the rerun

This allows three direct comparisons:

1. existing tier vs new tier
2. existing confidence vs new confidence
3. existing reasons/flags vs new reasons/flags

This is preferable to producing a clean overwrite, because it preserves the original state and makes the changes auditable.

---

## Expected schema of the regenerated outputs

The regenerated files retain the original input columns and append these new columns:

- `new_tier`
- `new_confidence_score`
- `new_reasons`
- `new_flags`
- `new_ean_exact_match`
- `posterior_match_probability`

If local project logic already uses these column names elsewhere, the agent may rename them, but it must log that change explicitly.

---

## What the agent should verify locally

The local agent should verify all of the following:

1. the local `probabilistic_matcher_prototype.py` is the intended version
2. the two attached files are the correct target files
3. the existing `tier` column in those files is indeed the baseline being compared against
4. the probability thresholds `0.95 / 0.10` are still intended
5. the locally generated outputs match the structure described in this report
6. any changed rows in the `tier_changes` CSVs are reviewed if needed

---

## What the agent may adjust

The agent may make **minor adjustments** if required by the local environment, including:

- correcting file paths
- mapping slightly different file names
- resolving local import issues
- adding logging
- changing output directory paths
- adapting the module-loading method if the local Python version requires it

If any such adjustment is required, the agent must:

1. log the change explicitly
2. state why it was necessary
3. state whether it affects result comparability
4. ask the user for clarification if a required assumption cannot be resolved confidently

The agent must **not silently change**:

- the input files being evaluated
- the tier probability thresholds
- the interpretation of existing vs new tiers
- the purpose of the rerun
- the row-level preservation of both existing and regenerated tier columns

unless the user explicitly approves the change.

---

## What the agent should return to the user

After reproducing this locally, the agent should provide:

1. the two regenerated CSVs
2. the two tier-change CSVs
3. a short summary of changed-row counts
4. a comparison of existing vs regenerated tier distributions
5. confirmation of whether the local prototype matched the intended version
6. any caveats, assumptions, or adjustments made

---

## Final instruction to the agent

Run the initial probabilistic matcher on the two correct full-row analysis files listed above.

Preserve the existing tier-related fields.

Append the newly generated probabilistic tier fields in the same output files.

Do not use the earlier 681/682-row EFG list for this rerun.

Measure and report the differences between the existing tiers and the regenerated tiers directly from these two attached files.
