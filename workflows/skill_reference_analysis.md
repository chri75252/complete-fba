# Skill Reference Analysis for `@stale-data-workflow`

**Date:** 2026-04-13
**Method:** Cross-referencing documented agent failures (methodology_report.md, efg_revalidation_report.md) against each candidate skill's actual SKILL.md instructions to determine genuine relevance.

---

## Evidence Base: What Actually Went Wrong

From the [methodology_report.md](file:///C:/Users/chris/.gemini/antigravity/brain/38e24f50-feeb-49ff-9d72-5be8c09e44a6/methodology_report.md) and [efg_revalidation_report.md](file:///C:/Users/chris/.gemini/antigravity/brain/38e24f50-feeb-49ff-9d72-5be8c09e44a6/efg_revalidation_report.md), the agent failures fell into 5 categories:

| Failure Category | Specific Evidence | Impact |
|---|---|---|
| **F1: Tool avoidance** | "No external APIs or websites were called" — zero Keepa, zero Google Trends, zero Amazon, zero browser checks, zero API calls | Bucket B/C decisions made without real-time demand verification |
| **F2: Script substitution** | Used `difflib.SequenceMatcher` as sole match quality metric; built 13-category keyword dictionary manually | 76% false-positive rate in initial list; 6 iterative refinement runs needed |
| **F3: T3 contamination** | 276 T3 items in the 742-row final list; 138 T3 items in Bucket A alone | 93% false-positive rate when sampled |
| **F4: Unit-qty blindness** | Gorilla Glue 236ml matched to 12-pack; reported £31.57 profit; actual £3.24 loss | Direct financial loss if sourced |
| **F5: No file verification** | Claimed removals that didn't actually happen | User acted on incorrect data |

---

## Candidate Skill Analysis

### 1. `@playwright-skill` — ✅ KEEP (Already Referenced)

**Currently in SKILL.md:** Yes, Phase 5 (spot-checking stale data).

**Failure it addresses:** F1 (tool avoidance). The methodology report explicitly states: "No browser automation was active during this session" and lists Keepa analysis, Google Trends analysis, and Amazon listing verification as "Not Done."

**Evidence of value from revalidation run:** When the agent *did* use browser checks (revalidation report Phase 2), it:
- Caught the Beaufort 600ml ≠ 13L false match (REMOVED)
- Identified 5 Rysons ghost listings with inflated prices (DOWNGRADED)
- Confirmed 6 Bucket C products had flipped to profit via price increases (UPGRADED)

**Verdict:** Already correctly placed. No change needed.

---

### 2. `@deep-research` — ✅ ADD

**Currently in SKILL.md:** No.

**What it actually does:** Runs autonomous research tasks using Gemini API — plan, search, read, and synthesize into reports. Requires `GEMINI_API_KEY`.

**Failure it addresses:** F1 (tool avoidance). The agent's "Honesty Section" (methodology report §7) admits it did not perform:
- Google Trends analysis for seasonal demand
- Similar-product comparison for Bucket B/C
- Category-level demand research

**Where it applies in the workflow:** Phase 5 (Targeted Validation), specifically Step 5.b — when the user opts for stale-data spot-checks rather than re-scraping. The agent needs to research category-level demand signals (e.g., "UK household cleaning market 2026") to contextualize whether Bucket B's zero-sales products are in growing or dying categories.

**Why it's better than what the agent did:** The agent used "general domain knowledge" to make category assessments (e.g., "cleaning products typically have stable demand"). `@deep-research` would replace guesswork with cited, sourced findings.

**Recommended insertion:** Phase 5, alongside Tavily budget allocation. Reference it as the fallback when Tavily budget is exhausted or when the agent needs deeper category-level synthesis rather than individual product checks.

> [!NOTE]
> `@deep-research` requires a `GEMINI_API_KEY` environment variable. The agent should check for its availability and gracefully skip if not configured, rather than using key absence as an excuse to skip all research.

---

### 3. `@apify-trend-analysis` — ✅ ADD (Conditional)

**Currently in SKILL.md:** No.

**What it actually does:** Uses Apify Actors to extract trend data from Google Trends, Instagram, Facebook, YouTube, TikTok. Requires `APIFY_TOKEN` and `mcpc` CLI.

**Failure it addresses:** F1 (tool avoidance). The revalidation report (Phase 2.4) shows that Tavily searches for category-level demand signals were highly valuable:
- "DIY Home Improvement: Market growing 4.3% annually through 2034"
- "Spring garden demand high for 2026"
- "Kitchen organizers, eco-friendly products dominating Amazon UK bestsellers"

`@apify-trend-analysis` with `apify/google-trends-scraper` could provide **quantitative** trend data (search volume over time, regional interest) rather than the text-summary Tavily returns.

**Where it applies:** Phase 5, as an alternative/supplement to Tavily for category-level trend analysis. Specifically useful for:
- Bucket C margin-flip candidates: Is the category trending up (price increases likely) or down?
- Bucket B zero-sales products: Is the product category growing or dying?

**Caveat:** This skill requires `APIFY_TOKEN` and `mcpc` CLI. It adds a prerequisite dependency. Reference it as **optional** — "If `APIFY_TOKEN` is available, use `@apify-trend-analysis` with `apify/google-trends-scraper` for quantitative trend data on the top 3-5 product categories."

---

### 4. `@firecrawl-scraper` — ⚠️ ALREADY MENTIONED (Strengthen Reference)

**Currently in SKILL.md:** Mentioned as "Firecrawl" in the Agent Declaration section but not with `@` syntax and no usage guidance.

**What it actually does:** Deep web scraping via Firecrawl API — page interaction, content extraction, screenshots. Requires API key.

**Where it applies:** Phase 5 only, for surgical single-page extraction when:
- You need to extract the current Amazon selling price from a specific listing
- The Playwright browser session is unavailable or impractical
- You need to check whether a listing is still active

**Recommendation:** Upgrade the mention to use `@firecrawl-scraper` syntax and add a cost-discipline note: "Use Firecrawl for at most 5 surgical page extractions on the highest-value candidates. Do not use it for batch scraping — the sandbox re-scrape workflow handles that."

---

### 5. `@inventory-demand-planning` — ⚠️ OPTIONAL MENTION ONLY

**Currently in SKILL.md:** No.

**What it actually does:** Codified expertise for demand forecasting, safety stock optimization, replenishment planning, and promotional lift estimation at **multi-location retailers operating 40-200 stores with regional distribution centers, managing 300-800 active SKUs.**

**Relevance assessment:** This skill is designed for a fundamentally different business model:
- It assumes you're a demand planner at a multi-location retailer with ERP systems (SAP, Oracle), WMS, POS data feeds
- Its forecasting methods (Holt-Winters, Croston's, exponential smoothing) require **time-series history** — which stale data by definition lacks
- Its ABC/XYZ classification operates on CV of demand over time, not on a single snapshot

**What IS useful from it:**
- The **Seasonal Transition Management** section (§Seasonal Transition Management) contains the markdown timing decision framework, which is conceptually relevant to Bucket C margin-flip candidates
- The **slow-mover kill decision** criteria could inform which Bucket B zero-sales products to deprioritize
- The general principle that NaN ≠ zero (which we already have in the skill)

**Verdict:** Do NOT reference it as `@inventory-demand-planning` — it would load 26KB of irrelevant multi-location retailer planning methodology into context, wasting tokens and potentially confusing the agent. Instead, incorporate the 2-3 relevant concepts directly as inline rules:
- "Products with zero sales for 13+ weeks and no promotional activity planned → deprioritize" (from slow-mover kill decision)
- "If data suggests seasonal demand, note which quarter/season the product peaks — stale data from January may understate summer garden product demand" (from seasonal transition concepts)

These concepts are already partially captured in Phase 5's Tavily allocation ("seasonal signals") but could be made more explicit.

---

### 6. `@pricing-strategy` — ❌ DO NOT ADD

**Currently in SKILL.md:** No.

**What it actually does:** Designs SaaS/marketplace pricing strategies — value metrics, tier design (Good/Better/Best), Van Westendorp analysis, freemium vs. free trial decisions, enterprise pricing.

**Relevance to stale-data-workflow:** Zero. This skill is about designing **your own product's** pricing structure (subscription tiers, value metrics, price sensitivity research). The stale-data workflow is about evaluating **other people's products** on Amazon for arbitrage. The concepts don't transfer:
- "Van Westendorp Price Sensitivity Meter" — irrelevant to checking if a wholesale-to-Amazon margin still holds
- "Tier Design (Good/Better/Best)" — irrelevant to FBA arbitrage
- "Freemium vs. Free Trial" — completely unrelated domain

**Why it was probably in the original prompt:** Likely included because it sounds adjacent to "pricing analysis" — but the type of pricing analysis needed (checking if Amazon selling prices have moved since the stale date) is already covered by `@playwright-skill` (check current price) and Keepa (check price history).

**Verdict:** Adding this would waste ~7,500 tokens of SaaS pricing methodology that has no bearing on the workflow. The pricing analysis needed in this workflow is: "Has the Amazon selling price changed since the stale date?" — which is a browser lookup, not a pricing strategy exercise.

---

### 7. `@supply-chain-risk-auditor` — ❌ DO NOT ADD

**Currently in SKILL.md:** No.

**What it actually does:** Audits **software dependency** supply chain risk — evaluating npm/pip packages for single-maintainer risk, unmaintained status, CVEs, and hijacking potential. Uses the `gh` CLI tool to query GitHub repository metadata.

**Relevance to stale-data-workflow:** Zero. The name is misleading — this is a **software security** tool, not a physical supply chain tool. It:
- Evaluates git repositories for dependencies
- Checks GitHub stars, open issues, maintainer count
- Looks for `SECURITY.md` files
- Suggests alternative npm/pip packages

None of this applies to Amazon FBA product sourcing.

**Verdict:** Completely irrelevant. The "supply chain" in this skill's name refers to software supply chain attacks (like left-pad), not wholesale product supply chains.

---

### 8. `@systematic-debugging` — ❌ DO NOT ADD (But for an interesting reason)

**Currently in SKILL.md:** No.

**What it actually does:** Enforces a 4-phase root-cause analysis protocol before proposing code fixes: Investigate → Hypothesize → Verify → Fix. Core principle: "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST."

**Relevance assessment:** This is a **code debugging** skill. The stale-data workflow is a **data analysis** workflow. While the *spirit* of "investigate before acting" is relevant, the skill's actual instructions are:
- "Check error messages, stack traces, logs"
- "Read the relevant source code"
- "Identify the exact failure point"
- "Create a minimal reproduction"

These steps don't map to "clean stale product data and identify re-scrape targets."

**Why it was probably in the original prompt:** Because the stale-data analysis *does* involve debugging data quality issues (false matches, contaminated rows, reconciliation errors). But the skill's methodology is designed for software bugs, not data quality bugs.

**What we already have instead:** The EXECUTION_ENFORCEMENT.md file already serves the equivalent function — it forces the agent to stop, investigate, and provide evidence at each phase gate before proceeding. This is a data-analysis-specific version of the same principle.

**Verdict:** Do not add. The enforcement protocol already captures the relevant discipline. Adding this would load 10KB of irrelevant software debugging methodology.

---

### 9. `@data-quality-frameworks` — ❌ DO NOT ADD

**Currently in SKILL.md:** No.

**What it actually does:** Implements data quality validation with **Great Expectations**, **dbt tests**, and **data contracts**. It's about building data quality pipelines with CI/CD automation.

**Relevance assessment:** The concepts (data validation, quality checks) are relevant in spirit, but the implementation is completely wrong for this context:
- Great Expectations: A Python library for validating data in ETL pipelines — not applicable to CSV spot-checking
- dbt tests: SQL-based data transformation testing — not applicable
- Data contracts: Schema agreements between teams — not applicable to a single-user workflow

**What we already have instead:** Phase 2 (Data Cleansing) already implements the equivalent of data quality checks — T4 filtering, brand exclusions, price plausibility, false match detection, unit-qty mismatch scanning. Phase 6.2 (Verify saved files) implements the equivalent of post-write validation. These are domain-specific and more actionable than generic DQ framework instructions.

**Verdict:** Do not add. Would load irrelevant Great Expectations/dbt methodology. The workflow already has fit-for-purpose data quality steps baked in.

---

## Summary Recommendations

| Skill | Verdict | Rationale |
|---|---|---|
| `@playwright-skill` | ✅ Already present | Correctly placed at Phase 5 for browser validation |
| `@deep-research` | ✅ **Add** | Addresses F1 (tool avoidance) for category-level demand research |
| `@apify-trend-analysis` | ✅ **Add (conditional)** | Provides quantitative trend data; mark as optional (requires APIFY_TOKEN) |
| `@firecrawl-scraper` | ⚠️ **Strengthen** | Already mentioned but not with `@` syntax; add cost-discipline note |
| `@inventory-demand-planning` | ⚠️ **Inline concepts only** | 2-3 relevant ideas (seasonal timing, slow-mover criteria) but 95% of skill is irrelevant |
| `@pricing-strategy` | ❌ **Reject** | SaaS pricing methodology; zero relevance to FBA arbitrage price checking |
| `@supply-chain-risk-auditor` | ❌ **Reject** | Software dependency security audit; not physical supply chain |
| `@systematic-debugging` | ❌ **Reject** | Software bug debugging; EXECUTION_ENFORCEMENT.md already serves this purpose |
| `@data-quality-frameworks` | ❌ **Reject** | Great Expectations/dbt pipelines; Phase 2 already has domain-specific DQ steps |

### Proposed Insertions (Exact Locations)

**1. `@deep-research` → Phase 5, after Tavily budget section (line ~237):**
```markdown
**Deep research (if Gemini API key available):**
- If `GEMINI_API_KEY` is set, use `@deep-research` for category-level demand synthesis
  on the top 3-5 product categories from Phase 4.
- This produces cited, sourced reports rather than single-search snippets.
- Do NOT use for individual product checks — Keepa and Playwright are faster for those.
- If the key is not available, skip gracefully. Do not use absence as an excuse
  to skip all category research.
```

**2. `@apify-trend-analysis` → Phase 5, after deep-research block:**
```markdown
**Apify trend data (if APIFY_TOKEN available, optional):**
- Use `@apify-trend-analysis` with `apify/google-trends-scraper` to pull quantitative
  search interest data for the top 3-5 product categories.
- This gives trend direction (rising/falling/stable) backed by search volume,
  not just text summaries.
- Limit to category-level queries only. Do not run per-product.
```

**3. `@firecrawl-scraper` → Phase 5, within the spot-checking section:**
```markdown
**Firecrawl (if Firecrawl API key available):**
- Use `@firecrawl-scraper` for at most 5 surgical page extractions on the
  highest-value Bucket A candidates when Playwright is unavailable.
- Do NOT use for batch scraping — the sandbox workflow handles that.
```

**4. Inline seasonal concept (from inventory-demand-planning) → Phase 3, Bucket C description:**
```markdown
- Consider seasonality: stale data from January may understate summer product demand.
  Note which season the product category peaks in — this affects whether a margin
  flip is likely or temporary.
```
