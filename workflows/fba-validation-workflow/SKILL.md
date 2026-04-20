---
name: fba-validation-workflow
description: "Deterministic workflow for validating generated FBA analysis CSV outputs before sourcing decisions."
risk: safe
source: internal
date_added: "2026-04-19"
---

# FBA Validation Workflow

## Overview

This skill validates newly generated FBA analysis CSV files (typically exported from the Analysis tab) and enforces strict, auditable gates before any product list is treated as actionable.

It is designed to match the discipline level of `stale-data-workflow` while focusing on validation of already-generated analysis data.

## Supporting Files

- **references/EXECUTION_ENFORCEMENT.md** — mandatory phase-gate protocol, required evidence templates, and anti-evasion checks. Read at invocation start.

## When to Use

Invoke when user asks to:
- Validate a generated analysis CSV before acting on products
- Clean/filter profitable candidates with confidence controls
- Verify T2/T3 matches and unit-quantity correctness
- Cross-check analysis export against original financial report

## ABSOLUTE RULES

### RULE 1: NO SILENT DROPS
Every removed row must have an explicit reason in the excluded-rows audit output.

### RULE 2: NaN SALES != ZERO DEMAND
Missing sales data is UNKNOWN. Do not treat it as proven zero demand.

### RULE 3: UNIT QUANTITY SCAN IS MANDATORY
All surviving rows must pass quantity parsing checks before final bucket inclusion.

### RULE 4: CROSS-REPORT RECONCILIATION IS MANDATORY
Bucket A rows must be reconciled against financial report profit/ROI figures.

### RULE 5: SAVE + RE-READ VERIFICATION IS MANDATORY
No output is considered done until files are read back and validated.

## API/TOOL PRE-FLIGHT (DETERMINISTIC)

Before any optional live validation:
1. Read env vars first: `FIRECRAWL_API_KEY`, `TAVILY_API_KEY`, `APIFY_TOKEN`, `GEMINI_API_KEY`.
2. If requested path needs a missing key, ask user for key + budget before skipping.
3. Do not claim unavailability before checking env vars.
4. Optional alias: `SCRAPIFY_API_KEY` may exist but is excluded from default budget unless explicitly approved and key is validated.

## Validation Tool Execution Order (MANDATORY)

1. **Firecrawl** — primary extraction for specific supplier/Amazon URLs.
2. **Tavily** — macro category intelligence only.
3. **Apify** — supplementary category trend checks.
4. **Playwright** — final truth gate on shortlisted rows.

## Output Structure (MANDATORY)

Write outputs under:

```
OUTPUTS\PRODUCTS_LISTS\{supplier}_validation_{timestamp}\
  csvs\
    verified_profitable_{supplier}_{yyyymmdd}.csv
    excluded_rows_audit_{supplier}_{yyyymmdd}.csv
  reports\
    validation_summary_{supplier}_{yyyymmdd}.md
    phase2_waterfall_{supplier}_{yyyymmdd}.csv
```

## Required CSV Add-on Columns

`Bucket, Unit_Qty_Flag, Unit_Qty_Note, FinReport_NetProfit, FinReport_Match_Method, Profit_Discrepancy`

`Unit_Qty_Flag` allowed values:
- `MATCH`
- `MISMATCH_ADJUST`
- `UNCLEAR`
- `MISMATCH_REMOVED` (must be excluded from final verified CSV)

## Matching Precedence for Financial Reconciliation

For every Bucket A row, match in strict order:
1. EAN exact
2. ASIN exact
3. Normalized SupplierTitle fallback

Always emit `FinReport_Match_Method`.

## Agent Declaration (MANDATORY)

At invocation start, state:

> "I am executing `@fba-validation-workflow`. I will run deterministic preflight checks, validate T2/T3 and unit quantities, reconcile against the financial report, write auditable outputs, and verify files by re-reading them before finalizing."

Then ask for:
1. Analysis CSV path
2. Financial report path
3. Supplier identifier
4. Whether optional live validation should be attempted

## Anti-Pattern Checklist

Before claiming completion, confirm you did NOT:
- [ ] silently remove rows without reason
- [ ] treat NaN sales as zero demand
- [ ] skip quantity checks
- [ ] skip financial reconciliation
- [ ] skip post-save file readback
