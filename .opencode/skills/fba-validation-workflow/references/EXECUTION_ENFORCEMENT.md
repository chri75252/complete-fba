# EXECUTION ENFORCEMENT — FBA Validation Workflow

This reference is mandatory when running `@fba-validation-workflow`.

If the agent skips phase gates, fails to provide evidence, or silently substitutes logic, execution is invalid.

---

## Gate 0 — Preflight Evidence

Required evidence:
1. Absolute paths of analysis CSV + financial report
2. File existence confirmation
3. Critical column mapping table
4. Env-var checks for: `FIRECRAWL_API_KEY`, `TAVILY_API_KEY`, `APIFY_TOKEN`, `GEMINI_API_KEY`

Stop condition:
- If critical columns cannot be mapped, STOP and ask for clarification.

---

## Gate 1 — Load & Summary

Required evidence:
- Total rows
- Tier distribution
- Flags distribution (top 10)
- Profitable row count
- Sales present vs missing counts

---

## Gate 2 — Cleansing Waterfall (In Exact Order)

Required order:
1. T4 filter
2. Price plausibility
3. False match detection
4. Unit quantity pass
5. T3 verification
6. T2 verification

Required evidence:
- Waterfall table with rows in / removed / rows out for each step
- Excluded rows audit entries with reason codes

Hard rule:
- No row can be removed without a reason code.

---

## Gate 3 — Bucketing

Required evidence:
- Bucket A/B/C summary with T1/T2/T3 distribution
- Explicit confirmation: T3 count is zero in A and C

---

## Gate 4 — Financial Reconciliation

Required evidence:
- Comparison table for Bucket A
- Match method shown per row: EAN/ASIN/SupplierTitle
- Discrepancy counts (`PROFIT_DISCREPANCY`, `SALES_DISCREPANCY`)

Hard rule:
- Do not skip this gate.

---

## Gate 5 — Optional Live Validation

Run only if requested and tools available.

Required tool order:
1. Firecrawl
2. Tavily
3. Apify
4. Playwright

Hard rules:
- No product-level Tavily usage
- No per-product Apify scraping

---

## Gate 6 — Save + Verify

Required outputs:
- `verified_profitable_*.csv`
- `excluded_rows_audit_*.csv`
- `validation_summary_*.md`
- `phase2_waterfall_*.csv`

Required checks after save:
- Re-read files from disk
- Row counts match expected
- Required columns exist
- No `MISMATCH_REMOVED` rows in final verified CSV

---

## Evasion/Failure Patterns (Reject If Seen)

- "Skipped due to time" without reduced-scope alternative
- "Tool unavailable" without env-var evidence
- Cleansing summary without excluded-rows audit
- Output written but not re-read
- T3 rows appearing in Bucket A/C
