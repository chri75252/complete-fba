# Stale Data Category-List Prompt Template

> **Purpose:** A strict execution prompt template for `@stale-data-workflow` when the required final deliverable is a **category list / category sandbox target list** rather than a product list.
>
> **Template variables:** Replace `{STALE_REPORT_PATH}`, `{SUPPLIER_NAME}`, `{CATEGORY_OUTPUT_NOTE}` before use.

---

## The Prompt

```text
You are executing a full stale-data re-analysis run.

## MANDATORY SKILL REFERENCES
Read and follow these files BEFORE taking any action:
- `@stale-data-workflow` (primary canonical: `workflows/stale-data-workflow/SKILL.md`; project-native: `.opencode/skills/stale-data-workflow/SKILL.md`; fallback global: `C:\Users\chris\.gemini\antigravity\skills\stale-data-workflow\SKILL.md`)
- `workflows/stale-data-workflow/references/EXECUTION_ENFORCEMENT.md`

Reference as needed during validation:
- `@firecrawl-scraper`
- `@playwright-skill`
- `@deep-research`
- `@apify-trend-analysis`

## PRIMARY OBJECTIVE
I want a **CATEGORY LIST / CATEGORY SANDBOX TARGET LIST** as the final deliverable, built from:
- `{STALE_REPORT_PATH}`

Supplier:
- `{SUPPLIER_NAME}`

Output mode:
- `{CATEGORY_OUTPUT_NOTE}`

## STRICT EXECUTION REQUIREMENTS
1. Execute the stale-data workflow IN FULL and in phase order.
2. Prioritize category-level re-scrape targets, not product-list JSONs, unless the workflow requires orphan-product handling as supporting output.
3. Use both sales indicators where available:
   - `bought_in_past_month`
   - `amazon_sales_badge`
4. Use API-reliant tools/skills where available, within budget.
5. Produce category ranking logic grounded in demand + profit + margin-flip opportunity.

## API / TOOL USAGE RULES
### Mandatory execution order
1. Firecrawl
2. Tavily
3. Apify
4. Playwright

### Default lean action split
- Firecrawl: 15 default / 25 max
- Tavily: 3 default / 4 max
- Apify: 2 default / 4 max
- Scrapfly: 0 default
- Playwright: 6 default / 8 max

### Key retrieval discipline
1. Environment vars first
2. Then `C:\Users\chris\.env`
3. Then ask user before skipping

## REQUIRED DECLARATION
State this before starting:

> "I am executing `@stale-data-workflow` for a CATEGORY-LIST output. I will assess staleness, cleanse the stale report, use both available sales signals, detect unit-quantity mismatches, rank category sandbox opportunities, use API/browser validation within budget, and produce verified category-target outputs with full supporting artifacts."

## REQUIRED DELIVERABLES
At completion, provide:
1. Category sandbox target JSON path
2. Phase 4 summary JSON path
3. Working artifact folder path
4. Cleansing summary table
5. Bucket summary table
6. Category ranking table
7. API/tool usage summary
8. Verification checklist results after re-reading saved files

## ANTI-PATTERN REMINDER
Do NOT:
- Collapse directly into product-list output when category output was requested
- Ignore one of the sales indicators if both are available
- Skip re-read verification
```
