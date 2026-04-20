# FBA Product Validation & Extraction Prompt

> **Purpose:** A comprehensive, reusable prompt to analyze an FBA analysis export CSV — summarize findings, validate product matches (especially T2/T3), detect unit-quantity mismatches, cross-reference against the original financial report, and produce a clean CSV of verified profitable & sellable products.
>
> **Template variables:** Replace `{ANALYSIS_CSV_PATH}`, `{FIN_REPORT_PATH}`, `{SUPPLIER_NAME}` before use.

---

## Reasoning & Gap Analysis That Produced This Prompt

### What went wrong in the session that generated this prompt

1. **T2/T3 products were silently discarded.** The initial filter (`NetProfit > 0 & sales_value > 0`) correctly identified 32 candidates, but the refinement script's keyword-overlap threshold (`< 2 meaningful words → drop`) was too aggressive for T2/T3 items. It dropped ALL T2s because many T2 matches have reformulated titles (e.g., "KITCH SQUARE CONTAINERS" matched exactly but had `sales_value = 0` so it was filtered by the sales gate, not the title gate). The agent never separately reported which T2/T3 items were dropped and why.

2. **Zero-sales ≠ unsellable was ignored.** 9 profitable T2 items and 8 profitable T3 items had `sales_value = 0`. The agent treated 0-sales as "not sellable" without considering that `NaN` sales (no Keepa/BSR data captured) is different from confirmed zero sales. The `@stale-data-workflow` skill explicitly warns: *"NaN sales does NOT mean zero sales — it means the scraper didn't capture it."*

3. **No cross-reference against the financial report was done proactively.** The user had to explicitly request the comparison. The prompt should have mandated it from the start, since profitability can differ between the analysis export (which uses dashboard-calculated fees) and the financial report (which uses `FBA_Financial_calculator.py` fees including PrepHouseFee, HMRC, etc.).

4. **Unit-quantity detection was surface-level.** The regex script checked Amazon titles for "Pack of N" but missed patterns like "Set 4" (e.g., "Wham Set 4 Beehive 40cm Round Plastic Pot" — a T3 item showing £8.26 profit that was silently dropped). A more comprehensive regex is needed.

5. **No verification of the output CSV was performed.** The agent saved `verified_profitable_products.csv` but never re-read it to verify contents — violating `@verification-before-completion` and `@stale-data-workflow` Rule 5.

6. **Brand mismatch flags were not investigated.** Several T1 items had `BRAND_MISMATCH` flags (e.g., Elbow Grease toilet cleaner matched to a "3 x" multipack listing under a different seller brand). The flag was noted but never investigated — the "3 x" prefix in the Amazon title means 3 units are needed from the supplier.

### Skills incorporated and where they apply

| Skill | Where Applied | Why |
|-------|--------------|-----|
| `@stale-data-workflow` | Overall structure, T3 quarantine rules, verification protocol | Core workflow engine |
| `@verification-before-completion` | Phase 7 (re-read and verify CSV) | Prevents phantom file verification |
| `@inventory-demand-planning` | Phase 4 (slow-mover deprioritization, sales velocity assessment) | Separates genuine demand from noise |
| `@data-quality-frameworks` | Phase 2 (systematic validation rules in order) | Ensures clean-before-classify |
| `@firecrawl-scraper` | Phase 5 (optional live price checks on top candidates) | Surgical Amazon page extraction |
| `@playwright-skill` | Phase 5 (browser-based Keepa/listing verification) | Active listing and price trend checks |

---

## The Prompt

```
You are performing a comprehensive FBA Product Validation & Extraction analysis.

## SKILL REFERENCES
Read and follow these skills BEFORE proceeding:
- `@stale-data-workflow` (C:\Users\chris\.gemini\antigravity\skills\stale-data-workflow\SKILL.md) — for T3 quarantine rules, unit-quantity mismatch detection patterns, and verification protocol
- `@verification-before-completion` (C:\Users\chris\.gemini\antigravity\skills\verification-before-completion\SKILL.md) — for mandatory file re-read after saving any CSV

Reference as needed (do NOT read fully unless a specific phase requires it):
- `@inventory-demand-planning` (C:\Users\chris\.gemini\antigravity\skills\inventory-demand-planning\SKILL.md) — for slow-mover deprioritization logic in Phase 4
- `@firecrawl-scraper` (C:\Users\chris\.gemini\antigravity\skills\firecrawl-scraper\SKILL.md) — for optional live scraping in Phase 5
- `@playwright-skill` (C:\Users\chris\.gemini\antigravity\skills\playwright-skill\SKILL.md) — for browser-based verification in Phase 5

## INPUTS
- **Analysis Export CSV (primary working file):** `{ANALYSIS_CSV_PATH}`
- **Original Financial Report (cross-reference):** `{FIN_REPORT_PATH}`
- **Supplier:** `{SUPPLIER_NAME}`

## MANDATORY DECLARATION
State this before starting:
> "I am performing FBA Product Validation on {SUPPLIER_NAME}. I will:
> (1) Summarize the dataset, (2) Cleanse systematically, (3) Validate ALL T2/T3 matches by title analysis,
> (4) Detect unit-quantity mismatches on EVERY row, (5) Cross-reference against the original financial report,
> (6) Produce a clean CSV preserving the original column schema, (7) Re-read and verify the saved CSV."

---

### PHASE 1: LOAD & SUMMARIZE
1. Load the Analysis Export CSV. Report:
   - Total rows
   - Column list
   - Tier distribution (T1/T2/T3/T4 counts)
   - Flags distribution (top 10)
   - Profitable count (NetProfit > 0)
   - Items with sales data (sales_value > 0)
   - Items with sales data missing/NaN (treat as UNKNOWN, not zero)

**Output the Phase 1 summary table before proceeding.**

---

### PHASE 2: DATA CLEANSING (execute in this exact order, report counts at each step)

**Step 2.1 — Remove T4 Rejected Matches**
Filter out all rows where `tier = TIER_4_REJECTED`. These have EAN mismatches or confirmed non-matches.

**Step 2.2 — Price Plausibility Gate**
- If `SellingPrice_incVAT > 20× SupplierPrice_incVAT` AND title word overlap < 2 → reject
- If `SellingPrice_incVAT < 0.5× SupplierPrice_incVAT` → flag as suspicious

**Step 2.3 — False Match Detection**
Remove rows where `SupplierTitle` and `AmazonTitle` share fewer than 2 meaningful words (excluding stop words: the, and, with, for, in, of, a, an, to, by, at, on, is, it).
⚠️ For T1 items with EAN exact match (`ean_exact_match = True`), DO NOT remove even if word overlap is low — the EAN is the ground truth identifier.

**Step 2.4 — Unit Quantity Mismatch Detection (MANDATORY — DO NOT SKIP)**

For EVERY surviving row, parse BOTH `SupplierTitle` AND `AmazonTitle` for quantity patterns:
```
Regex patterns (case-insensitive):
  - (\d+)\s*x\s+              (e.g., "3 x Elbow Grease")
  - x\s*(\d+)                 (e.g., "x12", "x 6")
  - [Pp]ack\s*(?:of\s*)?(\d+) (e.g., "Pack of 12", "pack 6")
  - (\d+)\s*[Pp]ack           (e.g., "12 Pack", "6pack")
  - (\d+)\s*[Pp][CcKk]        (e.g., "12Pk", "6Pc")
  - [Ss]et\s*(?:of\s*)?(\d+)  (e.g., "Set of 4", "Set 4")
  - [Bb]ox\s*(?:of\s*)?(\d+)  (e.g., "Box of 12")
  - (\d+)\s*[Pp]ieces?        (e.g., "12 Pieces")
  - (\d+)\s*[Cc]ount          (e.g., "100 Count")
  - [Mm]ultipack
  - [Bb]undle\s*(?:of\s*)?(\d+)
  - \((\d+)\)                  (e.g., "(Pack 2, Leprechaun Green)")
  - (\d+)\s*×                  (Unicode multiplication sign)
```

For each row, determine:
- `supplier_qty`: quantity from SupplierTitle (default 1 if none found)
- `amazon_qty`: quantity from AmazonTitle (default 1 if none found)

Assign `Unit_Qty_Flag`:
- `MATCH` — Both indicate same quantity, or both are single units
- `MISMATCH_ADJUST` — Amazon quantity > supplier quantity. Recalculate:
  - `adjusted_cost = SupplierPrice_incVAT × (amazon_qty / supplier_qty)`
  - `adjusted_profit = NetProfit - (adjusted_cost - SupplierPrice_incVAT)`
  - If `adjusted_profit ≤ 0` → set flag to `MISMATCH_REMOVED` and exclude
  - If `adjusted_profit > 0` → keep, update NetProfit and ROI, add note
- `UNCLEAR` — Cannot determine from titles alone

**⚠️ CRITICAL:** The leading "N x" pattern (e.g., "3 x Elbow Grease") is the MOST COMMON multipack indicator on Amazon UK. Do not miss it.

**Step 2.5 — T3 Title Verification (THOROUGH)**
For every T3 item that survived Steps 2.1–2.4:
- Perform a DETAILED title comparison. Do not use simple word-count overlap.
- Check: Do the core product descriptors match? (product type, brand, size/capacity, color)
- Check: Is the Amazon product a fundamentally different item? (e.g., "Wall Clock Red 35cm" vs "Wall Clock Red 38cm" — close enough. "Carpet Tape 50mm" vs "Double Sided PP Tape" — different product type)
- For each T3 item, write a 1-sentence verdict: KEEP (with justification) or DROP (with reason)
- T3 items that pass verification go to Bucket B ONLY with `Confidence=LOW`

**Step 2.6 — T2 Title Verification**
For every T2 item:
- Verify the core product identity matches (brand + product type + key specs)
- T2 items with exact title matches or strong brand+product alignment → KEEP
- T2 items where titles describe fundamentally different products → DROP
- For each T2 item, write a 1-sentence verdict

**Output the Phase 2 cleansing waterfall table:**
```
| Step                    | Rows In | Removed | Rows Out | Notable Removals         |
|------------------------|---------|---------|----------|--------------------------|
| 2.1 T4 filter          | [N]     | [N]     | [N]      |                          |
| 2.2 Price plausibility  | [N]     | [N]     | [N]      |                          |
| 2.3 False match        | [N]     | [N]     | [N]      |                          |
| 2.4 Unit qty mismatch  | [N]     | [N]     | [N]      | [examples]               |
| 2.5 T3 verification    | [N]     | [N]     | [N]      | [verdicts]               |
| 2.6 T2 verification    | [N]     | [N]     | [N]      | [verdicts]               |
```

---

### PHASE 3: CLASSIFY INTO BUCKETS

**Bucket A — Profitable & Sellable (Proven Demand)**
- `NetProfit > 0` AND `sales_value > 0` (confirmed sales)
- T1 and verified T2 ONLY. Zero T3.
- Sort by `sales_value × NetProfit` descending

**Bucket B — Profitable / Unknown Sales (Opportunity)**
- `NetProfit > 0` AND (`sales_value == 0` OR `sales_value is NaN`)
- T1 and verified T2 primarily. Verified T3 allowed ONLY with `Confidence=LOW, Validation_Required=Yes`
- ⚠️ NaN/0 sales does NOT mean zero demand — it means the scraper didn't capture it. Treat as UNKNOWN.
- Apply `@inventory-demand-planning` slow-mover logic: if a product has zero sales for 13+ weeks and no seasonal relevance, deprioritize.

**Bucket C — Near-Profit / High Sales (Margin Flip Candidates)**
- `sales_value > 50` AND `NetProfit` between `-£3.00` and `+£0.50`
- T1 and verified T2 ONLY. Zero T3.
- These sell well but barely lose money — a price movement could flip them.

**Output the Phase 3 bucket summary:**
```
| Bucket | Count | Avg Profit | Avg Sales | T1 | T2 | T3 |
|--------|-------|------------|-----------|----|----|-----|
| A      | [N]   | £[X]       | [X]/mo    | [N]| [N]| 0   |
| B      | [N]   | £[X]       | —         | [N]| [N]| [N] |
| C      | [N]   | £[X]       | [X]/mo    | [N]| [N]| 0   |
```

---

### PHASE 4: CROSS-REFERENCE AGAINST ORIGINAL FINANCIAL REPORT

This step is MANDATORY. Do not skip it. The analysis export may use different fee calculations than the original financial report.

1. Load `{FIN_REPORT_PATH}`.
2. For every product in Bucket A, look up the same `SupplierTitle` in the financial report.
3. Compare:
   - `NetProfit` (analysis export) vs `NetProfit` (financial report)
   - `ROI` (analysis export) vs `ROI` (financial report)
   - `bought_in_past_month` (financial report) — does it confirm the sales data?
4. Flag discrepancies:
   - If a product is profitable in the analysis export but unprofitable in the financial report → FLAG as `PROFIT_DISCREPANCY`
   - If the financial report shows significantly different sales data → FLAG as `SALES_DISCREPANCY`
5. For flagged products, determine which source is more reliable:
   - The financial report uses the system's `FBA_Financial_calculator.py` with full fee breakdown (ReferralFee, FBAFee, PrepHouseFee, OutputVAT, InputVAT, HMRC)
   - The analysis export uses dashboard-calculated simplified fees
   - Generally, the financial report's profit figure is more accurate if it has more fee columns

**Output a comparison table for all Bucket A products showing both profit figures and any flags.**

---

### PHASE 5: OPTIONAL LIVE VALIDATION (if API keys available)

**Only if the user confirms API keys are available OR explicitly requests live checks.**

If `FIRECRAWL_API_KEY` is set:
- Use `@firecrawl-scraper` to extract current Buy Box price, BSR, and "bought in past month" badge from the top 10 Bucket A Amazon listings.
- Budget: Max 10 page extractions.
- Compare live price vs stale price. If live price dropped > 15%, flag as `PRICE_DROP_RISK`.

If browser access available:
- Use `@playwright-skill` for top 5 Bucket B products — check if the listing is active and has any "bought in past month" badge.

**If no API keys or browser:** Skip this phase gracefully. State: "Phase 5 skipped — no live validation tools available. All profit figures are based on stale data."

---

### PHASE 6: GENERATE OUTPUT CSV

1. Create the output CSV at:
   `{ANALYSIS_CSV_PATH directory}\verified_profitable_{SUPPLIER_NAME}_{YYYYMMDD}.csv`

2. The CSV MUST have the SAME columns as the input analysis export CSV, plus these additional columns:
   - `Bucket` — A, B, or C
   - `Unit_Qty_Flag` — MATCH, MISMATCH_ADJUST, or UNCLEAR
   - `Unit_Qty_Note` — explanation if mismatch detected
   - `FinReport_NetProfit` — the profit from the original financial report (if found)
   - `Profit_Discrepancy` — YES/NO

3. Include:
   - ALL Bucket A products (verified T1 + T2, profitable, with sales)
   - ALL Bucket B products (verified T1 + T2, profitable, sales unknown/zero)
   - ALL Bucket C products (margin-flip candidates)
   - Verified T3 items in Bucket B ONLY, with `Confidence=LOW`

4. Sort by: Bucket (A first), then by `sales_value × NetProfit` descending within each bucket.

---

### PHASE 7: VERIFY SAVED FILE (MANDATORY — per @verification-before-completion)

After saving the CSV:
1. Re-read the file immediately.
2. Verify:
   - [ ] Row count matches expectation from Phase 3
   - [ ] Zero T4 items present
   - [ ] Zero T3 items in Bucket A or C
   - [ ] `Unit_Qty_Flag` column exists on all rows
   - [ ] `Bucket` column exists on all rows
   - [ ] Sample 3 random rows — do supplier/amazon titles look like plausible matches?
   - [ ] No rows with `MISMATCH_REMOVED` flag (they should have been excluded)
3. Report verification results with evidence.

---

### PHASE 8: FINAL SUMMARY REPORT

Provide a structured summary:
```
=== FBA PRODUCT VALIDATION — FINAL REPORT ===
Supplier: {SUPPLIER_NAME}
Analysis Export: {ANALYSIS_CSV_PATH}
Financial Report: {FIN_REPORT_PATH}
Date Executed: [TODAY]

INPUT SUMMARY:
- Total rows loaded: [N]
- T1: [N] | T2: [N] | T3: [N] | T4: [N]

CLEANSING SUMMARY:
| Step                    | Removed | Notable                           |
|------------------------|---------|-----------------------------------|
| T4 filter              | [N]     |                                   |
| Price plausibility     | [N]     |                                   |
| False match            | [N]     |                                   |
| Unit qty mismatch      | [N]     | [list examples]                   |
| T3 verification        | [N]     | [kept N / dropped N]              |
| T2 verification        | [N]     | [kept N / dropped N]              |

BUCKET RESULTS:
| Bucket | Count | Avg Profit | T1 | T2 | T3 |
|--------|-------|------------|----|----|-----|
| A      | [N]   | £[X]       |    |    | 0   |
| B      | [N]   | £[X]       |    |    |     |
| C      | [N]   | £[X]       |    |    | 0   |

CROSS-REFERENCE RESULTS:
- Products matching both reports: [N]
- Profit discrepancies found: [N]
- Products profitable in analysis but unprofitable in fin report: [N]

TOP 10 HIGHEST-CONVICTION OPPORTUNITIES:
| # | Product | Bucket | Profit | Sales | ROI% | Unit Qty | Fin Report Confirms? |
|---|---------|--------|--------|-------|------|----------|---------------------|
...

ITEMS REQUIRING MANUAL REVIEW:
- Unit qty unclear: [N] items
- Profit discrepancy: [N] items
- T3 in Bucket B (low confidence): [N] items

OUTPUT FILE: [PATH] ([N] rows) — Verified ✅

HONEST ASSESSMENT:
- Genuinely actionable products: [N] out of [ORIGINAL TOTAL]
- Confidence level: [HIGH/MEDIUM/LOW] because [reason]
```
```

---

## Usage Examples

### For EFG Housewares:
Replace:
- `{ANALYSIS_CSV_PATH}` → `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\temp\fba_analysis_202 efg newst4 (1).csv`
- `{FIN_REPORT_PATH}` → `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_efghousewares-co-uk_20260413_003445.csv`
- `{SUPPLIER_NAME}` → `efghousewares-co-uk`

### For PoundWholesale:
Replace the paths with the corresponding poundwholesale file paths and set `{SUPPLIER_NAME}` → `poundwholesale-co-uk`
