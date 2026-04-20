# Supervised Matcher Experiment Report

## Purpose

This package contains the materials for the **supervised matcher experiment** intended to compare a **supervised pair-classification approach** against the **weak probabilistic matcher** on the correct full financial reports.

This package is meant to be run locally by an agent that has access to the full project files, local workflows, and any related scripts that may not exist in this sandbox.

## Core objective

Measure, on a **manually reviewed holdout set**, whether the supervised matcher is more accurate than the weak probabilistic matcher.

Do not infer the answer from model type. Measure it.

---

## What was attempted in the sandbox

A supervised benchmark pipeline was designed and partially implemented, but it did not complete here because the execution environment repeatedly timed out before the full experiment finished.

What was established:
- the benchmark should be **binary** for evaluation: `plausible match` vs `reject`
- exact valid EAN matches should still map deterministically to `TIER_1_VERIFIED`
- the supervised model should learn from reviewed examples rather than relying only on weak heuristics
- the correct evaluation set must come from the **full financial reports themselves**, not from mismatched dashboard/tier exports

---

## Required supervision before running the experiment

This experiment depends on a reviewed label set. Without that, there is no honest way to claim that one approach is more accurate than the other.

### Label definition
Use a binary target:
- `1` = plausible same product / plausible same variant / should not be auto-rejected
- `0` = not the same product / should be rejected

### Recommended annotation guidance
Label `1` when the pair is:
- exact same product
- same product with pack-size difference
- same product with size difference
- same product with colour difference
- same product where Amazon EAN is missing
- same product family where it is clearly the intended listing target and should not be auto-rejected

Label `0` when the pair is:
- different product entirely
- same category but not the same product
- different brand with no convincing attribute alignment
- generic substitute rather than the same product
- semantically mismatched item

### Minimum reviewed set
Recommended:
- 300 to 600 reviewed rows total across both suppliers

Minimum viable:
- 150 reviewed rows total

Recommended split:
- 70% train
- 15% validation
- 15% holdout

The final accuracy comparison must use the **holdout** split only.

---

## Required input formats

### Financial report CSVs
Required columns:
- `SupplierTitle`
- `AmazonTitle`
- `EAN`
- `EAN_OnPage`

Strongly recommended additional columns:
- `ASIN`
- `SupplierPrice_incVAT`
- `SellingPrice_incVAT`
- `NetProfit`
- `ROI`
- `SupplierURL`
- `AmazonURL`

### Reviewed labels CSV
Required columns:
- `source` (`efg` or `pound`)
- `local_idx` (zero-based row index within that source file)
- `label_binary` (`1` or `0`)
- `split` (`train`, `validation`, `holdout`)

Recommended optional columns:
- `reviewer`
- `review_note`
- `review_confidence`
- `adjudication_needed`

Example:

```csv
source,local_idx,label_binary,split,reviewer,review_note,review_confidence,adjudication_needed
efg,1068,1,holdout,Chris,"same product family; should not be rejected",high,no
efg,2387,0,holdout,Chris,"different product despite some lexical overlap",high,no
pound,3880,1,holdout,Chris,"same product/variant; Amazon EAN missing",high,no
pound,1148,0,holdout,Chris,"category similar but not same item",high,no
```

### Optional weak baseline outputs
If pre-generated weak outputs exist, they should contain at least:
- `tier`
- `posterior_match_probability`
- `ean_exact_match`

If they do not exist, the agent should generate them first or adapt the experiment script to call the local weak matcher directly.

---

## Supervised model design

### Evaluation target
The supervised model is not trained directly on T1/T2/T3/T4. It is trained on:
- `plausible match` vs `reject`

### Tier mapping after prediction
Recommended mapping:
- exact valid EAN match -> `TIER_1_VERIFIED`
- probability >= `0.85` -> `TIER_2_LIKELY`
- probability >= `0.35` and < `0.85` -> `TIER_3_NEEDS_REVIEW`
- probability < `0.35` -> `TIER_4_REJECTED`

### Feature families
The provided script uses lightweight structured features, including:
- token overlap
- shared numeric anchors
- brand agreement/conflict
- exact EAN
- Amazon-EAN-missing state
- EAN mismatch state
- pack agreement/difference
- price ratio

### Auto-derived weak labels for scale
The training process can be supplemented with auto-derived weak labels:
- exact-EAN rows as auto positives
- strongly rejected weak rows as auto negatives

Manually reviewed rows are weighted more heavily than auto-derived rows.

---

## What parts depend on the supervision step

The following are not universal constants. They depend on the reviewed labels and may need controlled adjustment:
- positive vs negative class definition
- probability thresholds
- train/validation/holdout composition
- class weights
- feature usefulness on local data
- exact-EAN handling if the local workflow has extra constraints

Any change to these must be logged explicitly.

---

## Expected outputs

The agent should produce:
- `efg_financial__supervised_output.csv`
- `pound_financial__supervised_output.csv`
- `manual_holdout_benchmark.csv`
- `supervised_experiment_summary.json`

The holdout benchmark must include, at minimum:
- source
- local index
- binary label
- weak model prediction
- supervised model prediction
- weak model correctness
- supervised model correctness
- weak probability
- supervised probability

---

## What the final local benchmark must answer

The agent must explicitly answer:
1. Which approach had better holdout accuracy?
2. Which approach had better precision?
3. Which approach had better recall?
4. Which approach had better F1?
5. Which approach reduced false T4 rejections more effectively?
6. Did the supervised model over-promote too many generic lookalikes?
7. Which rows changed in the correct direction, and which changed in the wrong direction?

---

## Required cautionary note to the agent

The agent may make **minor adjustments** if the local project state differs from the assumptions in this package, including:
- correcting paths
- mapping slightly different filenames
- adapting the weak baseline loading step to the actual local weak matcher
- reconciling column names
- adjusting runtime settings
- excluding malformed rows
- splitting the experiment supplier-by-supplier if needed for runtime or memory reasons

However, the agent must:
1. log every adjustment explicitly
2. explain why the adjustment was necessary
3. tell the user if the adjustment affects comparability
4. ask for clarification if any critical assumption cannot be resolved confidently

The agent must not silently alter:
- the label definition
- the holdout principle
- the benchmark target
- the probability-to-tier mapping
- the weak-vs-supervised comparison scope

unless the user approves or the local project state makes the original assumption impossible.

---

## Final instruction

Run the supervised matcher experiment locally on the full EFG and Pound financial reports using the reviewed label set, then report whether the supervised matcher is **actually more accurate** than the weak probabilistic matcher on the reviewed holdout benchmark.
