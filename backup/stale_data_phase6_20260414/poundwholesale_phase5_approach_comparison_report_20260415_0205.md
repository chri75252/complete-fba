# Phase 5 Approach Comparison Report

Supplier: `poundwholesale-co-uk`
Generated: `2026-04-15T02:05:00+04:00`

## Goal

Compare the already executed `Playwright-first` validation pass against the missing non-browser avenues (API/search extraction style) and decide which approach should be the default in the stale-data workflow.

## What Was Executed In This Comparison

### A) Existing baseline (already done earlier)

- Baseline file: `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_validation_results_20260414_232258.json`
- Candidates: 25
- Method used earlier: Playwright browser spot-checking
- Result summary: `keep=23`, `keep_with_caution=1`, `deprioritize=1`

### B) Missing avenues executed now

1. **Tool availability and auth checks**
   - Env key presence check (runtime):
     - `TAVILY_API_KEY=false`
     - `FIRECRAWL_API_KEY=false`
     - `FIRECRAWL_KEY=false`
     - `APIFY_TOKEN=false`
     - `GEMINI_API_KEY=true`
   - `google_search` tool attempt failed with auth error (`Not authenticated with Antigravity`).

2. **Search avenue fallback (non-browser)**
   - Ran Exa web searches for category-level context via `websearch_web_search_exa`.
   - Collected current external signals for Kitchen Cleaners and Skin Care categories.

3. **API-like extraction avenue (non-browser product validation)**
   - Runner script: `backup/stale_data_phase6_20260414/api_avenue_comparison_runner.py`
   - Output: `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_api_avenue_results_20260415_0200.json`
   - Method: `requests + HTML parse` on the same 25 candidates (supplier + Amazon URLs)
   - Runtime summary:
     - `products=25`
     - `total_elapsed_s=43.16`
     - `avg_supplier_ms=230.2`
     - `avg_amazon_ms=1462.3`
     - `supplier_live=25`
     - `amazon_live=21`
     - `keep=0`
     - `deprioritize=25`

## Why The API-Like Pass Collapsed To 0 Keep

From `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_api_avenue_results_20260415_0200.json`:

- Supplier URLs commonly returned HTTP `307` with title `You are being redirected...`.
- This stripped meaningful supplier content and made title plausibility fail.
- Amazon pages were often reachable (`200`), but supplier-side extraction quality was too weak for safe keep decisions.

So the speed was high, but verification fidelity was too low for final inclusion decisions.

## Time And Outcome Comparison

| Approach | Cohort | Runtime | Keep | Caution | Deprioritize | Reliability for final decision |
|---|---:|---:|---:|---:|---:|---|
| Playwright-first (existing) | 25 | ~632s from candidate->result timestamps | 23 | 1 | 1 | High for listing-level truth |
| API-like extraction (requests/html) | 25 | 43.16s | 0 | 0 | 25 | Low due redirect/anti-bot content loss |

## Interpretation

1. **Speed winner:** API-like extraction (very fast).
2. **Decision-quality winner:** Playwright (materially higher usable verification output).
3. **Root cause of gap:** non-browser extraction could not consistently access/parse supplier content behind redirect/cookie flow, causing systematic false negatives.

## Recommendation

Use a **mixed stack** as default, with Playwright as final gate:

1. Category/context checks with search/research tools.
2. Lightweight extraction attempts where pages are static and parseable.
3. Mandatory Playwright final verification for any candidate that may be kept.

Do **not** rely on non-browser extraction alone for keep/reject decisions when supplier pages show redirect/cookie or anti-bot behavior.

## Proposed Stricter Skill Instructions

Add these constraints to stale-data workflow Phase 5:

1. "If non-browser extraction returns redirect walls, anti-bot pages, or low-text payloads on supplier URLs, escalate to Playwright before final decision."
2. "Playwright-only is allowed when candidate count <=10 and only listing-state questions remain."
3. "For >10 candidates or any Bucket B/C ambiguity, run mixed stack first; Playwright remains final gate for kept rows."
4. "If Tavily/Firecrawl keys are unavailable or tool auth fails, log this explicitly and switch to approved fallback tools; do not silently skip the avenue."
5. "Report both throughput and decision-quality deltas (keep/deprioritize reversals) when comparing approaches."

## Evidence Files

- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_validation_results_20260414_232258.json`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_api_avenue_results_20260415_0200.json`
- `backup/stale_data_phase6_20260414/api_avenue_comparison_runner.py`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_validation_candidates_20260414_232258.json`
