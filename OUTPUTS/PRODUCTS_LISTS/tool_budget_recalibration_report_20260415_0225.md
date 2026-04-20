# Tool Budget Recalibration Report

Date: 2026-04-15
Scope: Recalibrate Phase 5 action counts using live checks with currently configured keys.

## What Was Re-Tested

- Firecrawl live scrape probes on supplier + Amazon URLs.
- Tavily live macro search probes.
- Scrapfly alias probe using `SCRAPIFY_API_KEY`.
- Apify token validity and small actor runs.
- Oracle + Librarian recommendations for lean allocation.

## Live Benchmark Evidence

Source: `OUTPUTS/PRODUCTS_LISTS/tool_action_benchmark_20260415_0220.json`

- **Firecrawl:**
  - 8 actions tested, 8/8 successful (`100%`)
  - Avg latency: `3009 ms`
  - Returned meaningful markdown for both supplier and Amazon pages.
- **Tavily:**
  - 2 actions tested, 2/2 successful (`100%`)
  - Avg latency: `1493 ms`
  - Good for macro category signal, not product-page truth.
- **Scrapfly alias (`SCRAPIFY_API_KEY`):**
  - 1 action tested, `401 Unauthorized`
  - Current key appears invalid for Scrapfly API.
- **Apify (`APIFY_TOKEN`):**
  - Token check successful (`200`).
  - One heavyweight actor (`website-content-crawler`) failed in limited-permissions runtime.
  - One lightweight actor (`web-scraper`) succeeded quickly but produced empty dataset for trivial test input.

## Decision

Previous split (`45 / 8 / 12 / 5`) is over-allocated.

Revised lean split for a 25-candidate run:

- **Firecrawl:** `15` actions (max `18`)
- **Tavily:** `3` actions (max `4`)
- **Apify:** `2` actions (max `4`)
- **Scrapfly alias:** `0` actions by default (max `2` only if key is validated first)
- **Playwright:** `6` product truth-gate checks (max `8`)

## Why This Split

1. Firecrawl demonstrated strong extraction reliability on tested URLs, so it remains primary.
2. Tavily is useful but should stay a low-volume macro layer.
3. Apify token is valid, but actor behavior/cost justifies a tight cap in this workflow.
4. Scrapfly should not receive budget until key/auth is confirmed.
5. Playwright remains necessary as final high-confidence gate on shortlisted survivors.

## Implemented Skill Updates

- `workflows/stale-data-workflow/SKILL.md`
- `.opencode/skills/stale-data-workflow/SKILL.md`

Both now reflect the revised lean split above.
