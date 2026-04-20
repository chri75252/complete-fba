===============================================================================
STALE DATA WORKFLOW — MANDATORY EXECUTION PROTOCOL
===============================================================================

⚠️  THIS FILE EXISTS BECAUSE 4 PRIOR EXECUTIONS FAILED DUE TO STEP SKIPPING
⚠️  YOU MUST FOLLOW THIS PROTOCOL EXACTLY — NO EXCEPTIONS
⚠️  EACH PHASE REQUIRES EVIDENCE OUTPUT BEFORE PROCEEDING TO THE NEXT
⚠️  CROSS-REFERENCE WITH SKILL.MD FOR DETAILED INSTRUCTIONS

===============================================================================
PRE-EXECUTION DECLARATION (MANDATORY)
===============================================================================

Before starting ANY stale data analysis, you MUST state:

"I am executing the @stale-data-workflow skill.
I have read SKILL.md and EXECUTION_ENFORCEMENT.md completely.
I will NOT substitute Python text-similarity scripts for dashboard/browser tools.
I will NOT include T3 matches in Bucket A or C.
I will scan every row for unit-quantity mismatches.
I will verify saved files by re-reading them after writing.
I will provide evidence output at each phase gate."

Failure to state this declaration = protocol violation.

===============================================================================
PHASE 1 GATE: ASSESS STALENESS & LOAD DATA
===============================================================================

**SKILL.MD Reference**: Phase 1

MANDATORY ACTIONS:
1. Read the financial report filename → extract date
2. Calculate days since report date
3. Report staleness tier (moderate / significant / critical)
4. Load the analysis CSV or financial report
5. Count total rows and list available columns

**REQUIRED OUTPUT** (Stop and confirm before Phase 2):
```
Phase 1 Complete:
- Report date: [DATE]
- Days stale: [N] → [moderate/significant/critical]
- Source file: [FULL PATH]
- Total rows loaded: [N]
- Key columns: [LIST]

READY FOR PHASE 2? Proceeding to data cleansing.
```

**STOP CONDITIONS**:
- If source file cannot be found → STOP. Ask user for correct path.
- If file has < 10 rows → STOP. Likely wrong file.
- If no price/profit columns found → STOP. Wrong file format.

===============================================================================
PHASE 2 GATE: DATA CLEANSING
===============================================================================

**SKILL.MD Reference**: Phase 2

⚠️ THIS IS THE MOST COMMONLY SKIPPED PHASE. DO NOT SKIP IT.

MANDATORY STEPS — Execute in this exact order:

### Step 2.1: T4 Removal
- Filter: Remove all rows where tier = TIER_4_REJECTED
- Count removed
- Count remaining

### Step 2.2: Brand Exclusions
- Filter: Remove rows with "Superior" in supplier title
- Count removed
- Count remaining

### Step 2.3: Price Plausibility
- Filter: Remove rows where AmazonPrice > 20× SupplierPrice AND title word overlap < 2
- Flag rows where AmazonPrice < 0.5× SupplierPrice as suspicious
- Count removed / flagged
- Count remaining

### Step 2.4: False Match Detection
- Known contamination brands to check for in AmazonTitle:
  Versace, Jo Malone, Armani, Chanel, Gucci, Dior, Prada, Dyson,
  Apple, Samsung, Kenwood, Bosch, Nespresso, KitchenAid, Le Creuset
- Rule: If supplier is a generic/wholesale brand (e.g., EFG, wholesale own-label)
  AND AmazonTitle contains a luxury/premium brand → REMOVE
- Also remove: rows where SupplierTitle and AmazonTitle share < 2 meaningful words
  (exclude stop words: the, and, with, for, in, of, a, an, to, by)
- Count removed
- Count remaining

### Step 2.5: Unit Quantity Mismatch Scan

⚠️ THIS STEP WAS SKIPPED IN 3 OF 4 PRIOR RUNS. IT IS MANDATORY.

For EVERY surviving row, check BOTH titles for quantity patterns:
- "Pack of [N]" / "[N] Pack" / "[N]-Pack"
- "[N]Pk" / "[N]Pc" / "[N] Count" / "[N] Pieces"
- "Set of [N]" / "Box of [N]" / "Multipack"
- "x[N]" at word boundary (e.g., "x12", "x6")
- Leading quantity like "12 ×" or "6x"

For each row, assign Unit_Qty_Flag:
- MATCH → Both indicate same quantity, or both are single unit
- MISMATCH_CHECK → Amazon is multipack, supplier is single unit
- UNCLEAR → Cannot determine

For MISMATCH_CHECK rows:
- Extract Amazon pack quantity
- Recalculate: AdjustedProfit = AmazonPrice - (SupplierPrice × PackQty) - EstimatedFees
- If AdjustedProfit < 0 → REMOVE (with note: "Unit qty mismatch — loss at correct qty")
- If AdjustedProfit > 0 → KEEP but update profit figure and add Unit_Qty_Note

### Step 2.6: T3 Quarantine
- Remove ALL T3 matches. They survive ONLY in Bucket B (Phase 3) with LOW confidence flag.
- Count removed
- Count remaining

**REQUIRED OUTPUT** (Stop and confirm before Phase 3):
```
Phase 2 Cleansing Summary:
| Step                    | Rows In | Removed | Rows Out | Notable Removals         |
|------------------------|---------|---------|----------|--------------------------|
| 2.1 T4 filter          | [N]     | [N]     | [N]      |                          |
| 2.2 Superior brand     | [N]     | [N]     | [N]      |                          |
| 2.3 Price plausibility  | [N]     | [N]     | [N]      | [example if any]         |
| 2.4 False match        | [N]     | [N]     | [N]      | [brands found]           |
| 2.5 Unit qty mismatch  | [N]     | [N]     | [N]      | [example: "Glue 236ml×12"]|
| 2.6 T3 quarantine      | [N]     | [N]     | [N]      |                          |
|------------------------|---------|---------|----------|--------------------------|
| TOTAL CLEANSED         | [N]     | [N]     | [N]      |                          |

Unit Qty Scan Results:
- MATCH: [N] rows
- MISMATCH_CHECK (kept, adjusted): [N] rows
- MISMATCH_CHECK (removed, loss): [N] rows
- UNCLEAR: [N] rows

READY FOR PHASE 3? Proceeding to bucket classification.
```

**STOP CONDITIONS**:
- If you removed 0 rows in ALL steps → something is wrong. Re-check your filters.
- If Unit_Qty_Flag column is missing from output → phase NOT complete.
- If T3 count in output is 0 but T3 existed in input and you didn't remove them → re-run 2.6.

===============================================================================
PHASE 3 GATE: BUCKET CLASSIFICATION
===============================================================================

**SKILL.MD Reference**: Phase 3

MANDATORY CLASSIFICATION RULES (no deviation):

**Bucket A — Proven Demand:**
- Sales > 0 AND NetProfit > 0
- ONLY T1 and T2 matches
- ⛔ ZERO T3 allowed. If T3 count in Bucket A > 0, you have violated the protocol.
- Sort by: Sales × NetProfit descending

**Bucket B — Opportunity:**
- NetProfit > 0, Sales = 0 OR Sales = NaN
- T1 and T2 primarily
- T3 allowed ONLY with: Confidence=LOW, Validation_Required=Yes
- NaN sales ≠ zero sales. NaN = scraper didn't capture the badge. Treat as UNKNOWN.

**Bucket C — Margin Flip Candidates:**
- Sales > 50 AND NetProfit between -£3.00 and +£0.50
- ONLY T1 and T2 matches
- ⛔ ZERO T3 allowed.
- Sort by: smallest absolute loss + highest sales velocity

**REQUIRED OUTPUT** (Stop and confirm before Phase 4):
```
Phase 3 Bucket Classification:
| Bucket | Description    | Count | Avg Profit | Avg Sales | T1  | T2  | T3  |
|--------|---------------|-------|------------|-----------|-----|-----|-----|
| A      | Proven Demand | [N]   | £[X]       | [X]/mo    | [N] | [N] | 0   |
| B      | Opportunity   | [N]   | £[X]       | —         | [N] | [N] | [N] |
| C      | Margin Flip   | [N]   | £[X]       | [X]/mo    | [N] | [N] | 0   |
|--------|---------------|-------|------------|-----------|-----|-----|-----|
| TOTAL  |               | [N]   |            |           |     |     |     |

Validation checks:
- T3 in Bucket A: [MUST BE 0] ✅/❌
- T3 in Bucket C: [MUST BE 0] ✅/❌
- T3 in Bucket B with LOW flag: [N] ✅

READY FOR PHASE 4? Proceeding to re-scrape target identification.
```

**STOP CONDITIONS**:
- If T3 > 0 in Bucket A or C → protocol violation. Go back and fix.
- If total classified rows ≠ total clean rows from Phase 2 → rows dropped or duplicated. Investigate.

===============================================================================
PHASE 4 GATE: RE-SCRAPE TARGET IDENTIFICATION
===============================================================================

**SKILL.MD Reference**: Phase 4

MANDATORY STEPS:

### Step 4.1: Category Grouping
- Group Bucket A + C products by supplier category URL
- For each category, calculate:
  - Product count in A+C
  - Sum of (Sales × |NetProfit|) — "value concentration"
- Rank categories by: product count × value concentration
- Select top 3-5 as sandbox re-scrape targets

### Step 4.2: Orphan Products
- Products in A/C whose category is NOT in the top 3-5
- Collect their ASINs/EANs
- Format as Product List JSON for targeted refresh

### Step 4.3: Bucket C Priority Sort
- Sort Bucket C by: smallest |NetProfit| (closest to flipping) + highest Sales
- These are the margin-flip candidates most likely to become profitable with fresh prices

**REQUIRED OUTPUT** (Stop and confirm before Phase 5):
```
Phase 4 Re-Scrape Targets:

CATEGORY SANDBOX RUNS (top [N] categories, [N] total products):
| # | Category URL                                    | Products | Value Score |
|---|------------------------------------------------|----------|-------------|
| 1 | [URL]                                          | [N]      | £[X]        |
| 2 | [URL]                                          | [N]      | £[X]        |
| 3 | [URL]                                          | [N]      | £[X]        |

PRODUCT LIST REFRESH ([N] orphan products):
- Format: JSON with ASINs/EANs
- Ready to place in OUTPUTS/CONTROL_PLANE/inputs/

TRIGGER COMMANDS:
1. "run sandbox analysis for category [URL1] on [supplier]"
2. "run sandbox analysis for category [URL2] on [supplier]"
3. "run sandbox analysis for category [URL3] on [supplier]"

READY FOR PHASE 5? User decision: execute re-scrape now, or spot-check stale data?
```

**STOP CONDITIONS**:
- If 0 categories identified → either the data is truly poor, or your grouping logic is wrong. Check.
- If user has NOT confirmed whether to re-scrape or spot-check, WAIT. Do not assume.

===============================================================================
PHASE 5 GATE: TARGETED VALIDATION
===============================================================================

**SKILL.MD Reference**: Phase 5

TWO POSSIBLE PATHS — User must choose:

### Path A: Post-Scrape Validation (user completed sandbox runs)
1. Load fresh sandbox financial report
2. Compare old vs new: NetProfit, Sales, total_offer_count
3. Products where margin held/increased → confirmed opportunity
4. Products where margin collapsed → deprioritize
5. Output comparison table

### Path B: Stale Data Spot-Check (user opted out of re-scrape)
1. Select top 15 Bucket A, top 10 Bucket B, top 10 Bucket C = max 35 products
2. Use @playwright-skill or Keepa to check:
   - Is the Amazon listing still active?
   - Current price vs stale price
   - "Bought in past month" badge present?
   - Price trend direction (Keepa)
3. If API keys available (Tavily): allocate 3-5 searches for category demand trends

⚠️ DO NOT attempt to browser-check more than 35 products.
⚠️ DO NOT claim "browser tools unavailable" — use them on a reduced scope.
⚠️ DO NOT substitute a Python script for browser checks.

**REQUIRED OUTPUT**:
```
Phase 5 Validation Summary:

[Path A]
| Product (top N) | Old Profit | New Profit | Change  | Status      |
|----------------|------------|------------|---------|-------------|
| [title]        | £[X]       | £[X]       | [+/-]   | Confirmed/Drop |

[OR Path B]
| Product          | Listing Active | Current Price | Stale Price | Badge | Trend |
|-----------------|---------------|---------------|-------------|-------|-------|
| [title]         | ✅/❌          | £[X]          | £[X]        | Y/N   | ↑/↓/→ |

READY FOR PHASE 6? Proceeding to save and verify.
```

===============================================================================
PHASE 6 GATE: SAVE, VERIFY, AND REPORT
===============================================================================

**SKILL.MD Reference**: Phase 6

### Step 6.1: Save Output Files
Target directory: OUTPUTS\PRODUCTS_LISTS\

Files to create:
- {supplier}_VALIDATED_master_{timestamp}.csv
- {supplier}_VALIDATED_bucketA_{timestamp}.csv
- {supplier}_VALIDATED_bucketBC_{timestamp}.csv

All files MUST include column: Unit_Qty_Flag

### Step 6.2: Verify Saved Files (MANDATORY — DO NOT SKIP)

⚠️ IN PRIOR RUNS, THE AGENT CLAIMED TO HAVE REMOVED ITEMS THAT WERE STILL IN THE FILE.

After saving EACH file, immediately re-read it and verify:
- [ ] Zero luxury/premium brand false matches
- [ ] Zero T3 items in Bucket A or C files
- [ ] Zero "Superior" brand items
- [ ] Unit_Qty_Flag column exists on ALL rows
- [ ] Row count matches expected count from Phase 3
- [ ] Sample 3 random rows — do supplier/amazon titles look like plausible matches?

### Step 6.3: Final Report

**REQUIRED OUTPUT** (this is the deliverable):
```
===============================================================================
STALE DATA ANALYSIS — FINAL REPORT
===============================================================================
Supplier: [NAME]
Report Date: [DATE] ([N] days stale)
Executed: [CURRENT DATE]
Protocol: EXECUTION_ENFORCEMENT.md

CLEANSING SUMMARY:
| Step                    | Removed |
|------------------------|---------|
| T4 filter              | [N]     |
| Superior brand         | [N]     |
| Price plausibility     | [N]     |
| False match detection  | [N]     |
| Unit qty mismatch      | [N]     |
| T3 quarantine          | [N]     |
| TOTAL REMOVED          | [N]     |

BUCKET SUMMARY:
| Bucket | Count | Avg Profit | T1 | T2 | T3 |
|--------|-------|------------|----|----|-----|
| A      | [N]   | £[X]       | [N]| [N]| 0   |
| B      | [N]   | £[X]       | [N]| [N]| [N] |
| C      | [N]   | £[X]       | [N]| [N]| 0   |

RE-SCRAPE TARGETS:
- [N] category sandbox runs ([N] total products)
- [N] orphan products for product-list refresh

TOP 10 HIGHEST-CONVICTION OPPORTUNITIES:
| # | Supplier Title | Amazon Title | Bucket | Profit | Sales | Unit Qty |
|---|---------------|-------------|--------|--------|-------|----------|
...

FILES SAVED:
- [path1] ([N] rows) — verified ✅
- [path2] ([N] rows) — verified ✅
- [path3] ([N] rows) — verified ✅

HONEST ASSESSMENT:
- Genuinely actionable products: [N] out of [ORIGINAL TOTAL]
- Products requiring unit-qty manual review: [N]
- Confidence in results: [HIGH/MEDIUM/LOW] because [reason]
===============================================================================
```

===============================================================================
EVASION DETECTION — COMMON AGENT SHORTCUTS TO WATCH FOR
===============================================================================

The following shortcuts were observed in prior runs. If you catch yourself
doing any of these, STOP and correct course:

1. PYTHON SCRIPT SUBSTITUTION
   Symptom: Writing a local Python script with difflib/fuzzywuzzy to "score"
   matches instead of using the dashboard tiers and browser validation.
   Why it fails: Text similarity ≠ product match quality. "Pomegranate" matches
   "Pomegranate Noir" at 85% similarity but they're completely different products.
   Correct action: Use the pre-calculated tier classifications from the analysis CSV.

2. TOOL BUDGET ELIMINATION
   Symptom: Setting API call budget to 0 and claiming "credit preservation."
   Why it fails: User explicitly allocated a tool budget. Ignoring it wastes
   the allocated resources AND produces lower-quality output.
   Correct action: USE the allocated budget on top candidates. If scope is too
   large, REDUCE scope — don't eliminate the tool.

3. SILENT T3 INCLUSION
   Symptom: Including T3 matches in high-confidence buckets without flagging.
   Why it fails: 93% false-positive rate. Contaminates the entire output.
   Correct action: T3 goes to Bucket B only, with LOW confidence flag.

4. PHANTOM FILE VERIFICATION
   Symptom: Claiming "file saved and verified" without actually re-reading it.
   Why it fails: The file may not contain what you think it does (encoding issues,
   partial writes, wrong dataframe serialized).
   Correct action: Re-read. Sample rows. Count. Compare. Report.

5. SCOPE ABANDONMENT
   Symptom: Being assigned 35 spot-checks, doing 0, and producing a CSV instead.
   Why it fails: The CSV is the output of the cleansing phases, not a substitute
   for validation. Validation is a separate step.
   Correct action: Do the spot-checks on the reduced scope. Report findings.

===============================================================================
VIOLATION CONSEQUENCES
===============================================================================

If you skip any phase from this protocol:
- T3 contamination → 93% of flagged items are false positives → user wastes
  hours investigating products that don't exist as matches
- Unit qty mismatches → user orders 1 unit expecting £31 profit, receives
  a £3 loss because Amazon listing was a 12-pack
- Unverified files → user acts on data that doesn't match what was reported
- No re-scrape targets → user manually checks 500+ stale listings instead
  of letting the system refresh the top 50 in 20 minutes

THIS IS NOT HYPOTHETICAL — ALL OF THESE HAPPENED IN PRIOR EXECUTIONS.

===============================================================================
FINAL MEMORIZATION AID — FIVE RULES
===============================================================================

Before starting ANY stale data analysis, internalize these five rules:

1. TRIAGE FIRST, SCRAPE SECOND, VALIDATE THIRD
   Never validate stale prices manually when the system can refresh them.

2. CLEAN BEFORE YOU CLASSIFY
   Phase 2 (cleansing) comes before Phase 3 (buckets). Never classify dirty data.

3. T3 IS TOXIC TO BUCKET A AND C
   Zero tolerance. No exceptions. No "but it looks like a good match."

4. PACK OF 12 ≠ PACK OF 1
   Every row gets scanned. Every mismatch gets flagged or removed.

5. SAVED ≠ VERIFIED
   Writing a file is not the same as confirming its contents. Re-read it.

===============================================================================
ACKNOWLEDGMENT
===============================================================================

By proceeding with stale data analysis, you confirm:

✅ I have read SKILL.md completely
✅ I have read EXECUTION_ENFORCEMENT.md completely
✅ I understand all 6 phases are mandatory
✅ I will provide evidence output at each phase gate
✅ I will not substitute Python scripts for dashboard/browser tools
✅ I will not include T3 in Bucket A or C
✅ I will scan for unit quantity mismatches
✅ I will re-read saved files to verify their contents
✅ I will not claim tools are unavailable to avoid using them

===============================================================================
END OF EXECUTION ENFORCEMENT PROTOCOL
===============================================================================
