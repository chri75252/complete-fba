---
name: stale-data-workflow
description: "Executes the authoritative, system-aligned workflow for analyzing stale Amazon FBA sourcing data (>14 days old). Prioritizes sandbox re-scraping over manual LLM validation."
risk: safe
source: internal
date_added: "2026-04-13"
---

# Stale Data Re-Analysis Workflow

## Overview

This skill handles re-evaluation of FBA product data that is older than 14 days. The goal is to identify the highest-value products and categories from the stale report, prepare them for a fresh sandbox scrape, and then validate the fresh results.

## Supporting Files

- **references/EXECUTION_ENFORCEMENT.md** — Phase-by-phase mandatory checkpoint protocol with required evidence output formats, stop conditions, and evasion detection patterns. **Read this file at the start of every invocation.** It exists because 4 prior executions failed due to step skipping, and contains the exact output templates you must produce at each phase gate.

## When to Use

Invoke this skill when the user asks to:
- "Re-analyze" or "re-evaluate" a product list or financial report older than 14 days
- "Run stale data analysis" on a supplier
- "Identify products worth re-scraping"
- "Build a sandbox target list from old data"
- "Clean up old product data for [supplier]"

## ABSOLUTE RULES — Violations That Previously Destroyed Output Quality

These rules exist because in 4 prior attempts, the agent violated them and produced unusable outputs. Each rule maps to a specific real failure.

### RULE 1: DO NOT MANUALLY SCRAPE STALE PRICES VIA BROWSER
**Failure that caused this rule:** Agent was asked to check 500+ products via `@playwright-skill` one-by-one. It realized the time cost was astronomical, silently abandoned the approach, and fell back to a Python `difflib` text-similarity script instead — producing a contaminated 1,300-row list with 76% false positives in the top bucket.

**The correct approach:** Use the browser ONLY for targeted spot-checks on the FINAL shortlist (max 20-35 products). For everything else, let the FBA system's scraper handle price/sales data via Sandbox runs.

### RULE 2: T3 MATCHES ARE GUILTY UNTIL PROVEN INNOCENT
**Failure that caused this rule:** Agent included 361 T3 (low-confidence text-similarity) matches in "Bucket A — Proven Demand." Sampling showed a 93% false-positive rate (e.g., "London Fragrances Pomegranate" matched to "Jo Malone Pomegranate Noir"; "EFG Food Processor" matched to "Kenwood FDP65").

**The correct approach:** 
- T3 matches NEVER appear in high-confidence buckets (A or C).
- T3 can appear in Bucket B ONLY with `Confidence=LOW, Validation_Required=Yes`.
- If you cannot verify a T3 match via browser or EAN cross-check, exclude it.

### RULE 3: UNIT QUANTITY MISMATCHES DESTROY PROFIT CALCULATIONS
**Failure that caused this rule:** "GORILLA WOOD GLUE 236ML" (supplier: £4.84 for 1 bottle) was matched to "Gorilla Wood Glue 236ml (Pack of 12)" (Amazon: £54.84). Reported profit: £31.57. Actual result if sourced: £3.24 LOSS (need to buy 12 bottles at £58.08).

**The correct approach:** Parse every product title for quantity indicators before including in any list. Use the detection logic in the "Unit Quantity Mismatch Detection" section below.

### RULE 4: DO NOT CLAIM TOOLS ARE UNAVAILABLE TO AVOID USING THEM
**Failure that caused this rule:** Agent claimed "browser-based match verification toolchains run synchronously" and "500+ candidates was too large to responsibly validate" as justification for using zero API calls and zero browser checks, despite having an explicit budget of 10-15 Tavily searches and being told to check only the TOP 35 candidates.

**The correct approach:** You have a tool budget. Use it. If the scope is large, REDUCE the scope to top candidates — do not eliminate the tool entirely.

### RULE 5: VERIFY SAVED FILES AFTER WRITING
**Failure that caused this rule:** Agent claimed it removed Versace, Jo Malone, and Armani false-match rows. The file on disk still contained all of them. The agent never re-read the file after saving.

**The correct approach:** After writing any output CSV, immediately read it back and spot-check:
- Are excluded brands actually gone?
- Do row counts match expectations?
- Is the `Unit_Qty_Flag` column present?

---

## User Preparation (Include at top of any prompt using this skill)

Before invoking this workflow, do these 1-3 things to dramatically improve results:

1. **Export the Analysis Tab CSV manually** and place it in the project's `temp/` folder. The dashboard "Export CSV" button is currently buggy (exports raw unfiltered data). Having the pre-tiered analysis export available saves the agent from recalculating tiers.
2. **State whether you want Category-level or Product-level sandbox targets** (or both). This determines the output format.
3. **Provide the path to the stale report** explicitly so the agent does not guess.
4. **If any products must be excluded** (for example, because they already appeared in a prior sandbox or reconciled report), provide that exclusion file path explicitly so the agent can remove overlapping items by stable identifiers.

---

## The 6-Phase Workflow

### Phase 1: Assess Staleness & Load Data

1. Check the financial report filename date (e.g., `20260108` = Jan 8, 2026).
2. Calculate staleness: `> 14 days = moderately stale` | `> 30 days = significantly stale` | `> 90 days = critically stale`.
3. Load the analysis tab CSV (if the user placed it in `temp/`). This file contains pre-calculated tiers, confidence scores, and flags. Use it as the primary working file.
4. If no analysis export exists, load the raw financial report CSV. You will need to derive tier classifications from the `confidence_score` column.
5. If multiple sales indicators exist (for example `bought_in_past_month` and `amazon_sales_badge`), treat BOTH as evidence. Do not base demand conclusions on only one sales field when two are available.

**Required output at end of Phase 1:**
```
Phase 1 Complete:
- Report date: [DATE] ([X] days old → [moderately/significantly/critically] stale)
- Source file: [PATH]
- Total rows: [N]
- Columns available: [list key columns]
```

### Phase 2: Data Cleansing (Mandatory Before Any Analysis)

Apply these filters IN THIS ORDER. Report counts at each step.

**Step 2.1 — Remove T4 Rejected Matches**
- Filter out any row with tier = `TIER_4_REJECTED`.

**Step 2.2 — Hard Brand Exclusions**
- Remove rows containing "Superior" in supplier title (known contamination source).

**Step 2.3 — Price Plausibility Gate**
- If `AmazonPrice > 20× SupplierPrice` AND title word overlap < 2 → reject (contaminated EAN mapping).
- If `AmazonPrice < 0.5× SupplierPrice` → flag as suspicious ASIN match.

**Step 2.4 — False Match Detection**
- Remove rows where Amazon title contains luxury/premium brands not matching the supplier's product type (e.g., Versace, Jo Malone, Armani, Chanel, Gucci, Dior, Prada, Dyson, Apple, Samsung matched to a generic EFG-type product).
- Remove rows where `SupplierTitle` and `AmazonTitle` share fewer than 2 meaningful words (excluding stop words like "the", "and", "with").

**Step 2.5 — Unit Quantity Mismatch Detection**

For EVERY surviving row, parse both titles for quantity indicators:

```
Regex patterns to check in AmazonTitle:
  - Pack of \d+
  - \(\d+ Pack\)
  - \d+-Pack
  - \d+Pk
  - \d+Pc
  - Set of \d+
  - Box of \d+
  - \d+ Count
  - \d+ Pieces
  - Multipack
  - x\d+ (at word boundary)

Compare against SupplierTitle using same patterns.
```

For each row, set `Unit_Qty_Flag`:
- `MATCH` — Both titles indicate same quantity, or both are single units.
- `MISMATCH_CHECK` — Amazon appears to be a multipack while supplier is single unit.
- `UNCLEAR` — Cannot determine from titles alone.

For `MISMATCH_CHECK` rows:
- Recalculate profit: `AmazonPrice - (SupplierPrice × AmazonPackQty) - EstimatedFees`
- If recalculated profit is negative → REMOVE immediately.
- If still positive → keep but update the profit figure and add a note.

**Step 2.6 — T3 Quarantine**
- Remove ALL T3 matches from high-confidence categories. They can survive ONLY in Bucket B with `Confidence=LOW`.

**Required output at end of Phase 2:**
```
Phase 2 Cleansing Summary:
| Step                    | Rows In | Removed | Rows Out | Reason               |
|------------------------|---------|---------|----------|----------------------|
| T4 filter              | [N]     | [N]     | [N]      | Dashboard rejected   |
| Superior brand         | [N]     | [N]     | [N]      | Hard exclusion       |
| Price plausibility     | [N]     | [N]     | [N]      | >20x ratio           |
| False match detection  | [N]     | [N]     | [N]      | Brand/title mismatch |
| Unit qty mismatch      | [N]     | [N]     | [N]      | Pack vs single       |
| T3 quarantine          | [N]     | [N]     | [N]      | Low-confidence purge |
```

### Phase 3: Bucket Classification

Classify surviving clean rows into three targeting buckets:

**Bucket A — Proven Demand (Must Refresh)**
- Sales > 0 AND NetProfit > 0
- T1 (EAN Exact) and top-scoring T2 only
- Sort by `Sales × NetProfit` descending (prioritizes high-volume high-margin items).

**Bucket B — Profitable / Zero Sales (Opportunity)**
- NetProfit > 0, Sales = 0 or missing/NaN
- T1 and T2 primarily. T3 allowed ONLY with `Confidence=LOW, Validation_Required=Yes`.
- NaN sales does NOT mean zero sales — it means the scraper didn't capture it. Treat as unknown.
- Deprioritize products with zero sales for 13+ weeks and no promotional activity planned (slow-movers).

**Bucket C — Near-Profit / High Sales (Margin Flip Candidates)**
- Sales > 50 (proven demand) AND NetProfit between -£3.00 and +£0.50
- T1 and T2 only. No T3.
- These products SELL WELL but don't quite make money. The question: has a price change since the stale date flipped them to profit?
- Consider seasonality: stale data from January may understate summer product demand. Note which season the product category peaks in — this affects whether a margin flip is likely or temporary.

**Required output at end of Phase 3:**
```
Phase 3 Bucket Classification:
| Bucket | Count | Avg Profit | Avg Sales | T1 | T2 | T3 |
|--------|-------|------------|-----------|----|----|-----|
| A      | [N]   | £[X]       | [X]/mo    | [N]| [N]| 0   |
| B      | [N]   | £[X]       | —         | [N]| [N]| [N] |
| C      | [N]   | £[X]       | [X]/mo    | [N]| [N]| 0   |
```

### Phase 4: Identify Re-Scrape Targets

This is the CORE step. Do NOT skip to browser validation.

**Step 4.1 — Category Grouping**
Group Bucket A and C products by their supplier category URL. Rank categories by:
- `Total products in bucket A + C within that category`
- `Sum of (Sales × |NetProfit|)` across products in that category

The top 3-5 categories are your "Must Re-Scrape" targets. One category sandbox run refreshes all products in that category efficiently.

**Step 4.2 — Orphan Products**
Products in Bucket A/C that belong to categories NOT in the top 3-5 are "orphans." Collect their ASINs/EANs for a targeted Product List JSON refresh instead.

**Step 4.2b — Explicit Exclusion Set (if provided by user)**
- If the user provides a prior sandbox/reconciled report that must be excluded, load it explicitly.
- Build an exclusion set in this order: `EAN` -> `ASIN` -> normalized `SupplierTitle`/`AmazonTitle` fallback.
- Remove overlapping rows from final product-list outputs and ranked finalists.
- Report how many rows/products were excluded because they already appeared in the exclusion source.

**Step 4.3 — Bucket C Prioritization**
For Bucket C, additionally sort by: smallest absolute loss + highest sales velocity. These are the products closest to flipping.

**Required output at end of Phase 4:**
```
Re-Scrape Target Summary:
- Category Sandbox Runs: [N] categories ([N] total products)
  1. [Category URL] — [N] products, est. value £[X]
  2. [Category URL] — [N] products, est. value £[X]
  ...
- Product List Refresh: [N] orphan products for targeted ASIN refresh.
- Prompt to trigger: "run sandbox analysis for category [URL] on [supplier]"
```

### Phase 5: Targeted Validation (Post-Scrape OR Top Candidates)

**ONLY proceed here if EITHER:**
a) The user has completed a sandbox re-scrape and returned fresh data, OR
b) The user explicitly asks for immediate spot-checks on stale data (capped at 35 products max).

**If post-scrape (fresh data available):**
1. Load the fresh sandbox financial report.
2. Compare NetProfit, Sales, total_offer_count between old and new.
3. Products where margin held or increased → confirmed opportunity.
4. Products where margin collapsed → deprioritize.

**If spot-checking stale data (user opted out of re-scrape):**
Use `@playwright-skill` for browser-based checks on:
- Top 15 Bucket A products: Open Amazon listing, check Keepa for price trend, verify listing is active.
- Top 10 Bucket B products: Check "bought in past month" badge, Keepa sales rank activity, Google Trends for category.
- Top 10 Bucket C products: Check current Amazon selling price — has it gone UP since the stale date?

**API key retrieval order (deterministic):**
1. Read from environment variables first: `FIRECRAWL_API_KEY`, `TAVILY_API_KEY`, `APIFY_TOKEN`, `GEMINI_API_KEY`.
2. If an env var returns empty, check `C:\Users\chris\.env` as a fallback by reading that file directly and extracting the value. This is the durable home-level key store.
3. If a required key is absent from both sources, ask the user for the key and budget before skipping that avenue.
4. Do NOT claim tool unavailability without checking both sources explicitly.
5. Optional alias: `SCRAPIFY_API_KEY` is treated as a Scrapfly key alias but is currently **EXCLUDED** from the budget (see Scrapfly row below).
6. When the user explicitly requests that API/browser tools be used, you MUST use them within budget unless a checked prerequisite is genuinely unavailable.

**Deep research (if Gemini API key available):**
- If `GEMINI_API_KEY` is set, use `@deep-research` (from `C:\Users\chris\.gemini\antigravity\skills\deep-research`) for category-level demand synthesis on the top 3-5 product categories from Phase 4.
- This produces cited, sourced reports rather than single-search snippets.
- Do NOT use for individual product checks — Keepa and Playwright are faster for those.
- If the key is not available, skip gracefully. Do not use absence as an excuse to skip all category research.

**Validation tool execution order (mandatory sequence):**
1. **Firecrawl** — Primary extraction lane. Run first on high-priority candidates (supplier + Amazon URLs).
2. **Tavily** — Macro intelligence only. Run category-level queries after Firecrawl sweep completes.
3. **Apify** — Supplementary extraction. Only invoke if Firecrawl fails on specific Amazon pages.
4. **Playwright** — Final truth gate. Run last, only on shortlisted survivors from Firecrawl/Apify.

**Firecrawl (if FIRECRAWL_API_KEY available):**
- Use `@firecrawl-scraper` (from `C:\Users\chris\.gemini\antigravity\skills\firecrawl-scraper`) for structured data extraction directly from specific URLs (e.g., pulling live Amazon BSR, prices, or out-of-stock status directly from the listing).
- Live benchmark: 8/8 success (100%), ~3s avg, meaningful markdown from both supplier and Amazon pages.
- Do NOT use for batch scraping — the sandbox workflow handles that.

**Tavily (if TAVILY_API_KEY available):**
- Reserve exclusively for broad market intelligence (e.g., macro category trends if Deep Research is unavailable).
- Do NOT waste searches on individual product names, ASINs, or Amazon URLs. Tavily returns LLM-optimized summaries, not live Amazon data.
- Live benchmark: 2/2 success (100%), ~1.5s avg.

**Apify (if APIFY_TOKEN available, optional):**
- Use `@apify-trend-analysis` (from `C:\Users\chris\.gemini\antigravity\skills\apify-trend-analysis`) with `apify/google-trends-scraper` to pull quantitative search interest data for the top 3-5 product categories.
- Live benchmark: Token valid, but actor reliability mixed (website-content-crawler failed, web-scraper produced empty dataset). Capped at 2 actions due to $5 free-tier budget.
- Limit to category-level queries only. Do not run per-product.

**Default lean action split (per 25-candidate validation run):**

| Tool | Actions | Max | Role | Evidence |
|------|---------|-----|------|----------|
| **Firecrawl** | **15** | 25* | Primary extraction — supplier & Amazon pages | 8/8 success, 100%, ~3s avg |
| **Tavily** | **3** | 4 | Macro category intelligence | 2/2 success, 100%, ~1.5s avg |
| **Apify** | **2** | 4 | Supplementary Amazon-only fallback | Token valid, actor output mixed |
| **Scrapfly** | **0** | 2** | Excluded — both tested keys returned 401 Unauth | 0/1 success, 401 Unauthorized |
| **Playwright** | **6** | 8 | Final truth gate on shortlisted survivors | 25/25 products checked, 92% keep rate |

*\* Firecrawl escalation rule: If early success rate is high (>90%) and the candidate set is large (>25), additional Firecrawl actions may be allocated up to 25 total. Escalation beyond the default 18 requires explicit user confirmation in the same session. Document the escalation count and reason in the Phase 6 final report.*

*\*\* Scrapfly conditional: Max 2 actions IF the user provides a validated key that returns 200. Both tested keys (fingerprints: `f6ba...2c1` and `3f61...ef15`) returned 401. Remove this exclusion row only after a key is confirmed working.*

**Split rationale:** Firecrawl is the only API that reliably extracts content past poundwholesale.co.uk redirect walls (raw requests failed 100%). Tavily is a low-volume macro layer. Apify is capped due to mixed actor reliability and $5 free-tier budget. Scrapfly is excluded until a valid key is confirmed. Playwright remains the final truth gate because non-browser extraction produced 0 usable results on this supplier domain.

### Phase 6: Save, Verify, and Report

**Step 6.1 — Organize output files**

All stale-data outputs go into a structured layout under `OUTPUTS\PRODUCTS_LISTS\`:

```
OUTPUTS\PRODUCTS_LISTS\
  product_list_{supplier}_{timestamp}.json              ← SINGLE FINAL OUTPUT (the deliverable)
  {supplier}_stale_analysis_{timestamp}\                ← WORKING ARTIFACTS FOLDER
    csvs\                                                ← CSV outputs
      {supplier}_VALIDATED_master_{timestamp}.csv
      {supplier}_VALIDATED_bucketA_{timestamp}.csv
      {supplier}_VALIDATED_bucketBC_{timestamp}.csv
    categories\                                         ← Category and summary JSONs
      {supplier}_category_sandbox_targets_{timestamp}.json
      {supplier}_phase4_summary_{timestamp}.json
    scripts\                                            ← Pipeline reproducibility scripts
      {supplier}_phase6_pipeline.py
    {supplier}_validations_ranked_products_{timestamp}.json
    {supplier}_phase5_validation_candidates_{timestamp}.json
    {supplier}_phase5_validation_results_{timestamp}.json
    {supplier}_stale_data_final_report_{timestamp}.md
```

**Key rules:**
- The root of `PRODUCTS_LISTS` receives ONE final product list JSON per supplier per run: `product_list_{supplier}_{timestamp}.json`. This is compatible with `control_plane/tools/product_list_builder.py` and `control_plane/tools/product_list_refresh.py` which validate `OUTPUTS/PRODUCTS_LISTS/` as the allowed root path.
- All intermediate/working artifacts (CSVs, validation JSONs, reports, scripts) go into the timestamped subfolder — never in the PRODUCTS_LISTS root.
- Previous run artifacts may coexist; the timestamp in the folder name prevents collisions.

**Required columns in all CSV files:**
`Supplier_Title, Amazon_Title, ASIN, EAN, Match_Type, Tier, Confidence_Score, EAN_Exact_Match, Sales, Net_Profit, ROI, Supplier_Price, Amazon_Price, Bucket, Inclusion_Reason, Confidence, Validation_Required, Priority, Similarity, Unit_Qty_Flag, Unit_Qty_Note, Category, Supplier_URL, Amazon_URL, FBA_Sellers, Dashboard_Flags`

**Step 6.2 — Verify saved files (MANDATORY):**
Read each file back from its new subfolder path and confirm:
- [ ] Zero luxury/premium brand false matches
- [ ] Zero T3 items in Buckets A or C
- [ ] Zero "Superior" brand items
- [ ] `Unit_Qty_Flag` column exists on all rows
- [ ] Row counts match expectations
- [ ] Any specific items flagged for removal are actually absent
- [ ] Final product list JSON exists at `OUTPUTS/PRODUCTS_LISTS/product_list_{supplier}_{timestamp}.json`

**Step 6.3 — Final report** with:
1. Final counts per bucket
2. T1 / T2 / T3 distribution
3. Rows removed for each cleansing reason
4. Top 10 highest-conviction opportunities
5. Categories with strongest re-scrape value
6. Re-scrape trigger commands for user to execute
7. Honest assessment: how many products are genuinely actionable
8. Items with `Unit_Qty_Flag = MISMATCH_CHECK` requiring manual review

---

## Agent Declaration (MANDATORY at start of every invocation)

When this skill is invoked, immediately state:

> "I am executing the `@stale-data-workflow`. I will clean the stale CSV, extract high-value targets, detect unit-quantity mismatches, quarantine T3 matches, and prepare Sandbox refresh targets. I will NOT manually check hundreds of Amazon listings via browser — I will validate only the top 20-35 candidates after cleansing, and recommend re-scrape targets for the rest."

Then ask the user for:
1. Path to the analysis CSV or financial report
2. Whether they want Category sandbox targets, Product List targets, or both
3. Whether they have API keys available (Firecrawl, Tavily, Apify, Gemini) and what budget (only if missing from env vars). Note: Scrapfly is currently EXCLUDED from the workflow budget — both tested keys returned 401 Unauthorized. Do not ask about Scrapfly unless the user volunteers a new key.
4. Whether any prior sandbox/reconciled output should be treated as an exclusion source for final product outputs.

---

## Anti-Pattern Checklist (Review Before Submitting ANY Output)

Before claiming the task is complete, verify you did NOT:
- [ ] Use `difflib` or any local text-similarity scoring as a substitute for the system's existing tier classifications
- [ ] Include T3 matches in Bucket A or Bucket C
- [ ] Skip the Unit Quantity Mismatch scan
- [ ] Claim tools were unavailable rather than using them on a reduced scope
- [ ] Save a file and not re-read it to verify contents
- [ ] Produce a list larger than your own "genuinely actionable" estimate
- [ ] Use zero API calls while claiming to "preserve credits"
- [ ] Generate a Python script as a substitute for using the dashboard or existing system tools
- [ ] Ignore one of the sales indicators when both `bought_in_past_month` and `amazon_sales_badge` are available
- [ ] Leave products from an explicit exclusion source in the final product-list output
