# Stale Data Product-List Prompt Template

> **Purpose:** A strict execution prompt template for `@stale-data-workflow` when the required final deliverable is a **product list** rather than a category list. This template is designed to force full compliance with the stale-data workflow, enforcement rules, API/tool budgets, and output verification protocol.
>
> **Template variables:** Replace `{STALE_REPORT_PATH}`, `{SUPPLIER_NAME}`, `{OUTPUT_MODE_NOTE}`, `{OPTIONAL_EXCLUSION_SOURCE_PATH}`, `{OPTIONAL_EXCLUSION_NOTE}` before use.

---

## The Prompt

```text
You are executing a full stale-data re-analysis run.

## MANDATORY SKILL REFERENCES
Read and follow these files BEFORE taking any action:
- `@stale-data-workflow` (primary canonical: `workflows/stale-data-workflow/SKILL.md`; project-native: `.opencode/skills/stale-data-workflow/SKILL.md`; fallback global: `C:\Users\chris\.gemini\antigravity\skills\stale-data-workflow\SKILL.md`)
- `workflows/stale-data-workflow/references/EXECUTION_ENFORCEMENT.md`

Reference as needed during Phase 5:
- `@firecrawl-scraper` — primary extraction lane
- `@playwright-skill` — final truth gate
- `@deep-research` — category-level synthesis only
- `@apify-trend-analysis` — category trend support only

## PRIMARY OBJECTIVE
I do NOT want a category list as the final deliverable.
I want a **carefully tailored PRODUCT LIST** built from:
- `{STALE_REPORT_PATH}`

Supplier:
- `{SUPPLIER_NAME}`

Output mode:
- `{OUTPUT_MODE_NOTE}`

## STRICT EXECUTION REQUIREMENTS
1. Execute the stale-data workflow IN FULL. Do not skip phases.
2. Follow the exact phase order from the skill and enforcement reference.
3. Use API-reliant tools/skills where available; do NOT avoid them by claiming they are unavailable without checking env vars first.
4. Treat **both sales columns** as evidence where available:
   - `bought_in_past_month`
   - `amazon_sales_badge`
   Do not rely only on a single sales field if both exist.
5. Apply unit-quantity mismatch detection before allowing any product into the final product list.
6. T3 items must NEVER appear in high-confidence outputs. If retained in lower-confidence outputs, label them clearly and justify them.
7. The final deliverable must be a product-list JSON in the root of `OUTPUTS\PRODUCTS_LISTS\` plus the full working-artifact subfolder.

## EXCLUSION INSTRUCTIONS
{OPTIONAL_EXCLUSION_NOTE}

If an exclusion source path is provided, you MUST:
- Load it explicitly: `{OPTIONAL_EXCLUSION_SOURCE_PATH}`
- Build an exclusion set from stable identifiers in this order: EAN -> ASIN -> SupplierTitle/AmazonTitle fallback
- Remove any overlapping products from the final product-list deliverable and from ranked finalist outputs
- Report exactly how many rows/products were excluded due to prior sandbox inclusion

## API / TOOL USAGE RULES
Use the stale-data workflow budgets and sequence strictly:

### Mandatory execution order
1. **Firecrawl** — primary extraction lane
2. **Tavily** — macro category intelligence only
3. **Apify** — supplementary category trend support only
4. **Playwright** — final truth gate on shortlisted survivors

### Default lean action split (per 25-candidate validation run)
- **Firecrawl:** 15 actions default, up to 25 max with escalation logic
- **Tavily:** 3 actions default, 4 max
- **Apify:** 2 actions default, 4 max
- **Scrapfly:** 0 actions by default (excluded unless key is validated)
- **Playwright:** 6 checks default, 8 max

### Key retrieval discipline
Check in this order:
1. Environment vars: `FIRECRAWL_API_KEY`, `TAVILY_API_KEY`, `APIFY_TOKEN`, `GEMINI_API_KEY`
2. If empty, check `C:\Users\chris\.env`
3. If still unavailable, ask user before skipping

Do NOT claim tool unavailability without checking both env vars and `C:\Users\chris\.env`.

## REQUIRED DECLARATION
State this before starting:

> "I am executing `@stale-data-workflow` for a PRODUCT-LIST output. I will assess staleness, cleanse the stale report, use both available sales signals, detect unit-quantity mismatches, quarantine weak matches, use API/browser validation within budget, exclude any products from the explicit exclusion source if provided, and produce a verified product-list deliverable plus full supporting artifacts."

## REQUIRED DELIVERABLES
At completion, provide:
1. Final product list JSON path in `OUTPUTS\PRODUCTS_LISTS\`
2. Working artifact folder path
3. Cleansing summary table
4. Bucket summary table
5. API/tool usage summary with actual actions used per tool
6. Explicit exclusion summary (if exclusion source provided)
7. Verification checklist results after re-reading saved files

## ANTI-PATTERN REMINDER
Do NOT:
- Skip phase gates
- Replace API/browser checks with local heuristic shortcuts
- Ignore one of the sales indicators if both are available
- Keep excluded products in the final product list
- Save outputs without re-reading them
```
