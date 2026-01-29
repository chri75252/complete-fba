        # MANUAL FBA PRODUCT ANALYSIS - COMPLETE METHODOLOGY GUIDE

        **Version:** v1.1.2  
        **Last Updated:** 2026-01-09  

        ## Purpose
        This guide documents the complete step-by-step methodology for manually analyzing FBA product data to identify profitable arbitrage opportunities. Follow this guide exactly to replicate the analysis process.

        ---

        ## 0. EXECUTION MODE (MANDATORY)

        This guide has two execution modes. You MUST choose ONE mode before starting and state it explicitly:

        - **REVIEW MODE (DEFAULT when an MD report already exists)**
          - Input = previously generated MD report (`PHASEA_MANUAL_REPORT_*.md`).
          - You MUST manually adjudicate the rows already printed in that MD report (row-by-row).
          - You MUST NOT re-run a pipeline over the source XLSX/CSV to re-decide verdicts.
          - You MAY consult the XLSX/CSV ONLY to verify a disputed field for a row that already appears in the MD report.

        - **FRESH ANALYSIS MODE (when no MD report exists)**
          - Input = source XLSX/CSV (financial report).
          - You generate a new MD report from scratch using Phases 1–7.

        **If an MD report exists, you MUST use REVIEW MODE.**

        ### 0.1 Review Mode tool boundary (hard rules)

        In REVIEW MODE:
        - Manual reading decides the verdict. Calculations are allowed ONLY as spot-checks AFTER the verdict is decided from row evidence.
        - Do NOT use similarity scoring, automated pack parsing, or scripted filtering to decide which rows “count.”
        - Do NOT silently drop rows. All removals must be documented in a Corrections section (REMOVE / MOVE / EDIT).

        ### 0.2 EAN import / normalization guardrail (applies even to spot-checks)

        When an EAN value may come from Excel, the normalization order is mandatory:
        1) Convert to text (string)
        2) Strip whitespace
        3) Remove a trailing `.0` (Excel float artifact) **before** any digits-only cleaning
        4) If the value contains scientific notation (`e+` / `E+`), treat the EAN as **CORRUPTED / UNTRUSTED** (do not use it as a hard gate)
        5) Only then: remove non-digits, validate length/checksum, and compare

        **Evidence rule:** whenever you use EAN logic, you must show BOTH the raw and normalized EAN values for that row (Supplier + Amazon).

        ### 0.3 Pre-submission anomaly gate

        If a bucket collapses unexpectedly after normalization (example: VERIFIED becomes 0 or drops sharply), STOP and output:
        - the suspected normalization issue (e.g., `.0`/scientific notation causing false mismatch),
        - the impacted RowIDs/fields,
        - the exact correction required.

        ---

        ## TABLE OF CONTENTS

        1. [Overview & Inputs](#1-overview--inputs)
        2. [Phase 1: Data Extraction & Initial Filtering](#2-phase-1-data-extraction--initial-filtering)
        3. [Phase 2: EAN Match Analysis](#3-phase-2-ean-match-analysis)
        4. [Phase 3: Title-Based Verification](#4-phase-3-title-based-verification)
        5. [Phase 4: Pack Size Detection & Analysis](#5-phase-4-pack-size-detection--analysis)
        6. [Phase 5: Browser Verification](#6-phase-5-browser-verification) -- ** IGNORE UNLESS EXPLICETELY REQUESTED ** 
        7. [Phase 6: Adjusted Profit Calculation](#7-phase-6-adjusted-profit-calculation)
        8. [Phase 7: Final Categorization](#8-phase-7-final-categorization)
        9. [Decision Trees & Flowcharts](#9-decision-trees--flowcharts)
        10. [Common Pitfalls to Avoid](#10-common-pitfalls-to-avoid)
        11. [Quick Reference Checklists](#11-quick-reference-checklists)

        ---

        ## 1. OVERVIEW & INPUTS

        ### 1.1 Required Input Files

        | File Type | Description | Example |
        |:----------|:------------|:--------|
        | **Previously Generated Report** (if reviewing) | Report to validate and correct | `PHASEA_MANUAL_REPORT_*.md` |
        | **Financial Report** | Excel/CSV with supplier products matched to Amazon | `PART3.xlsx` |
        | **LLM Reports** (optional) | Other reports for comparison | Various |

        **Note:** If you are reviewing a previously generated report rather than analyzing fresh source data:
        - Use the generated report as your PRIMARY input
        - Reference the source financial data only when needed for verification
        - The goal is to validate and correct the existing analysis, not start fresh

        ### 1.2 Expected Columns in Financial Report

        | Column Name | Description | Required |
        |:------------|:------------|:--------:|
        | `RowID` | Unique row identifier (or use index+1) | ✅ |
        | `ASIN` | Amazon Standard Identification Number | ✅ |
        | `EAN` | Supplier product barcode (13 digits typically) | ✅ |
        | `EAN_OnPage` | Amazon listing barcode | ✅ |
        | `SupplierTitle` | Product title from supplier | ✅ |
        | `AmazonTitle` | Product title from Amazon | ✅ |
        | `SupplierPrice_incVAT` | Supplier cost including VAT | ✅ |
        | `SellingPrice_incVAT` | Amazon selling price | ✅ |
        | `NetProfit` | Pre-calculated profit | ✅ |
        | `ROI` | Return on Investment percentage | Optional |
        | `Sales` | Estimated monthly sales | Optional |

        ### 1.3 Output Categories

        | Category | Definition |
        |:---------|:-----------|
        | **VERIFIED** | **Strict exact EAN match** (after mandatory normalization) **AND** brand/product/variant/pack confirmed **AND** adjusted profit > 0 |
        | **HIGHLY LIKELY** | No strict EAN confirmation is possible (**EAN missing/untrusted** OR **EAN conflict**) **BUT** brand + product-type match is strong **AND** at least one **unique anchor** matches (model/MPN/SKU/part number/series) **AND** adjusted profit > 0 |
        | **NEEDS VERIFICATION** | Strong candidate match, but 1–2 blocking details remain (e.g., pack ambiguity, variant ambiguity, or EAN conflict that is not yet explained/validated) |
        | **AUDITED OUT** | **Confirmed match** (confirmed via VERIFIED-path OR HIGHLY-LIKELY-path) but excluded due to actionability gates (pack/variant/profit/compliance). Listed as an audit trail. |
        | **UNRELATED / NOT INCLUDED** | Not a confirmed match (weak/contradictory evidence). **Do not list in report tables** (count only). |

        **Critical distinctions (do not mix):**
        - **UNRELATED / NOT INCLUDED** = not confirmed; count-only; not printed in tables.
        - **AUDITED OUT** = confirmed match, excluded for a specific actionability reason; printed as an audit trail.

        **EAN conflict policy (MANDATORY):**
        - If BOTH EANs are present, strict-valid, and DIFFERENT: this **reduces** match likelihood but does **not** automatically eliminate the row.
        - Default routing for EAN conflict is **NEEDS VERIFICATION**, unless pack/variant evidence and unique anchors clearly explain the difference (e.g., Amazon multipack EAN vs supplier single EAN).


        ---

        ## 2. PHASE 1: DATA EXTRACTION & INITIAL FILTERING

        ### Step 2.0: Coverage & Reconciliation Contract (MANDATORY)

        To prevent “missed rows” and silent omissions:

        1. **Read every row** in the input file (previously generated report or financial source).
        2. Assign each row to **exactly one** bucket:
           - VERIFIED / HIGHLY LIKELY / NEEDS VERIFICATION / AUDITED OUT / UNRELATED (NOT INCLUDED)
        3. **Do not cap** categories (especially NEEDS VERIFICATION). If output length is an issue, split across multiple outputs/files.
        4. End with a reconciliation check:
           - `VERIFIED + HIGHLY LIKELY + NEEDS VERIFICATION + AUDITED OUT + UNRELATED = TOTAL ROWS`
           - No duplicate RowIDs across buckets.

        ### Step 2.0A: Review Mode (If Analyzing Previously Generated Report)

        If your input is a previously generated report:

        1. **Extract all categorized products** from the report
        2. **Validate each categorization** against the methodology:
           - Check EAN matches are truly exact
           - Check pack sizes correctly identified (no dimension traps)
           - Check adjusted profit calculations
           - Check variants match (size, color, scent)
        3. **Identify errors:**
           - False positives: Products incorrectly included
           - False negatives: Valid products that were excluded
           - Miscategorizations: Products in wrong category
        4. **Root cause analysis:**
           - WHY were false positives included? (e.g., dimension misread as pack)
           - WHY were valid products missed? (e.g., brand not in detection list)
           - What criteria need adjustment?
        5. **Generate correction list:**
           - Products to REMOVE (false positives)
           - Products to ADD (missed due to fixable criteria)
           - Products to MOVE (wrong category)

        **Output structure should include:**
        - Section 1: Corrections Made (what changed and why)
        - Section 2: Final Validated Report (corrected version)

        ### Step 2.1: READ and Normalize Data


        ```

        ### Step 2.2: Validate EAN Format

        A valid barcode for “Exact EAN match” classification must be **strict-valid**:
        - Digits-only after cleaning (remove spaces, hyphens, “.0”, etc.)
        - Length is a plausible GTIN length: 8 / 12 / 13 / 14
        - **Checksum-valid** for its length (where applicable)
        - If shorter than 12/13/14, attempt **left-padding** (zero-fill) and re-validate checksum
        - Reject suspicious placeholders/corruption (e.g., long trailing-zero runs)

        ### Step 2.3: IDENTIFY Exact EAN Matches

        **Expected Result:** A list of all rows where supplier EAN exactly matches Amazon EAN.

        ---

        ## 3. PHASE 2: EAN MATCH ANALYSIS

        ### Step 3.1: Initial EAN Match ≠ Automatic VERIFIED

        > **CRITICAL RULE:** An exact EAN match is necessary but NOT sufficient for VERIFIED status.
        > The EAN only confirms the barcode matches. You must still verify:
        > 1. Pack sizes match (supplier 1x vs Amazon 10x = NOT a match)
        > 2. Product variant matches (size, color, scent)
        > 3. Profit is positive after pack adjustment

        ### Step 3.2: Create EAN Match Working List

        For each EAN match, extract:
        - RowID, ASIN, EAN
        - SupplierTitle (full text)
        - AmazonTitle (full text)
        - SupplierPrice, SellingPrice, NetProfit
        - ROI, Sales

        ### Step 3.3: Flag Potential Pack Discrepancies

        Scan titles for pack indicators:
        - Numbers followed by "pack", "pk", "x", "pcs", "pieces"
        - Phrases like "Pack of X", "Set of X", "X count"
        - **BUT NOT** dimensions like "15cm", "9x9 inch", "280x115mm"

        ---

        ## 4. PHASE 3: TITLE-BASED VERIFICATION

        ### Step 4.1: Parse Supplier Title

        For each product, manually read the supplier title and extract:

        | Element | What to Look For | Example |
        |:--------|:-----------------|:--------|
        | **Brand** | **Explicit brand token(s)** when clearly stated. **Do NOT assume the first word is a brand** if it looks like a generic product noun/spec/pack. If unclear → set **Brand = MISSING**. | "EVERREADY", "MASON CASH" |
        | **Product Type** | Core product description | "T8 TUBE LIGHT", "MIXING BOWL" |
        | **Size/Variant** | Dimensions, capacity, color | "4FT 36W", "29CM", "CREAM" |
        | **Pack Quantity** | Explicit pack indicators | "PK5", "28 PACK", "20PCE" |

        ### Step 4.2: Parse Amazon Title

        Apply the same extraction to the Amazon title.

        ### Step 4.3: Compare Extracted Elements

        | Element | Supplier | Amazon | Match? |
        |:--------|:---------|:-------|:------:|
        | Brand | EVERREADY | Eveready | ✅ Yes (case variant) |
        | Product | T8 4FT 36W TUBE LIGHT | T8 Tube 4ft 36w White 3500k | ✅ Yes |
        | Size | 4FT 36W | 4ft 36w | ✅ Yes |
        | Pack | (none stated) | (none stated) | ✅ Yes (both single) |

        ### Step 4.4: Identify Numbers That Are NOT Pack Quantities

        **CRITICAL:** These numbers are specifications, NOT pack sizes:

        | Pattern | Meaning | Example |
        |:--------|:--------|:--------|
        | `Xcm`, `Xmm`, `Xinch` | Dimension | "15 x 5.5 x 5.5 cm" = size |
        | `XL`, `Xlitre`, `Xml` | Capacity | "4 Litre", "580ml" |
        | `XW` | Wattage | "36W" |
        | `X LED` | LED count | "9 LED" = spec |
        | `Xx magnification` | Optical zoom | "2x magnification" = feature |
        | `XxX` followed by unit | Dimensions | "9x9 inch", "280x115mm" |

        ### Step 4.5: Decision Matrix for Title Analysis

        Use this matrix when EAN evidence is **not** a strict exact match (i.e., EAN missing/untrusted or EAN conflict) and you must route based on title evidence.

        **SCOPE GUARD (MANDATORY):**
        - Apply this matrix only when **Strict exact EAN match = NO**.
        - If **Strict exact EAN match = YES**, route through pack/variant + profit gates (VERIFIED / AUDITED OUT / NEEDS VERIFICATION for remaining ambiguity).

        #### Brand status gate (MANDATORY)
        - If both titles explicitly state a brand and the brands are different (**BRAND_CONFLICT**) → **UNRELATED / NOT INCLUDED** (count‑only; do not list).

        #### Product-type anchor strength (MANDATORY)
        - If core product nouns are **WEAK or conflicting** → **UNRELATED / NOT INCLUDED** (count‑only; do not list).

        #### Unique-anchor gate (ANTI‑NOISE) — MANDATORY
        - If there is **NO unique anchor** (model/MPN/SKU/part‑number/series token) → **UNRELATED / NOT INCLUDED** (count‑only; do not list).

        #### Routing (when gates pass)
        - **EAN missing/invalid/untrusted (less negative than conflict):**
          - Brand matches and product‑type anchors STRONG + unique anchor → **HIGHLY LIKELY**
          - Brand present on one title but missing on the other + STRONG product‑type anchors + unique anchor → **NEEDS VERIFICATION**
        - **Both EANs strict‑valid and different (likelihood penalty; not an auto‑elimination):**
          - If STRONG product‑type anchors + unique anchor and a plausible pack/variant explanation exists in-row → **HIGHLY LIKELY** (rare; must note the explanation)
          - Otherwise (still eligible) → **NEEDS VERIFICATION** (state exactly what must be checked)

        Anything not meeting the gates above must be **UNRELATED / NOT INCLUDED** (count‑only; do not list).



        ## 5. PHASE 4: PACK SIZE DETECTION & ANALYSIS

        ### Step 5.1: Extract Pack Quantity from Supplier Title

        Read the supplier title manually. Look for:

        | Pattern | Example | Pack Size |
        |:--------|:--------|----------:|
        | `PK5`, `PK 5` | "AIRWICK DIFFUSER PK5" | 5 |
        | `28 PACK` | "FIRELIGHTERS 28 PACK" | 28 |
        | `20PCE`, `20 PCS` | "SHOT GLASSES 20PCE" | 20 |
        | `40 DOYLEYS` | "PPS ROUND 40 DOYLEYS" | 40 |
        | `(SOLD EACH)` | "KILROCK MOULD REMOVER (SOLD EACH)" | 1 |
        | No indicator | "APOLLO VINEGAR SHAKER" | 1 (default) |

        ### Step 5.2: Extract Pack Quantity from Amazon Title

        | Pattern | Example | Pack Size |
        |:--------|:--------|----------:|
        | `Pack of X` | "Pack of 10 Trays" | 10 |
        | `X x Product` | "3 x Easy Cut Refill" | 3 |
        | `X Bottles` | "5 Bottles X 30ml" | 5 |
        | `(X x Y)` | "(4 x 50)" | Multipack: total items = 4×50 (if 50 is quantity-inside) |
        | `Set of X` | "Set of 2 Glasses" | 2 |

        **Multipack interpretation rules (CRITICAL):**
        1. If Amazon shows **`N x [capacity]`** (e.g., `3 x 400ml`, `6 x 33g`, `2 x 1L`), then:
           - `N` is the **pack count** (RSU = N)
           - The capacity describes size of each unit (do **not** compute 3×400=1200 as “units”)
        2. If Amazon shows **`N x [dimension]`** (e.g., `9 x 9 inch`, `30cm x 36cm`, `280 x 115mm`), treat as **dimensions**, not pack.
        3. If Amazon shows `(N x M)` with no measurement units, treat as a **quantity-inside multipack** (total items = N×M) and compare against the supplier’s quantity-inside.

        ### Step 5.3: Calculate Pack Ratio

        ```
        Pack Ratio = Amazon Pack / Supplier Pack

        Examples:
        - Supplier 50 bags, Amazon 200 bags → Ratio = 4 (need 4x supplier units)
        - Supplier 5-pack, Amazon 5-pack → Ratio = 1 (1:1 match)
        - Supplier 28-pack, Amazon 24-pack → Ratio = 0.86 (supplier has MORE)

        ### Step 5.4: Pack Analysis Decision Tree

        IF Supplier Pack == Amazon Pack:
            → 1:1 Match → Continue to profit check
        ELSE IF Amazon Pack > Supplier Pack:
            → Calculate Adjusted Profit (need multiple supplier units)
            → IF Adjusted Profit > 0: VERIFIED (Pack Adjustment)
            → ELSE: AUDITED OUT (unprofitable after adjustment)
        ELSE IF Supplier Pack > Amazon Pack:
            → Supplier has more per unit (favorable)
            → VERIFIED (note: supplier provides extra)
        ```

        **Critical correction (SPLIT is not automatic):**
        - If **Supplier Pack > Amazon Pack**, do **not** label as VERIFIED by default.
        - This is a **SPLIT CANDIDATE** and must be routed to **NEEDS VERIFICATION** unless you have explicit evidence that:
          - Amazon listing unit count matches what you can supply, and
          - splitting/repackaging is compliant and practical for your workflow.

        ---

        ## 6. PHASE 5: BROWSER VERIFICATION ** IGNORE UNLESS EXPLICETELY REQUESTED ** 

        ### Step 6.1: When to Use Browser Verification

        Use browser verification when:
        - Pack size is ambiguous from titles alone
        - Numbers in title could be dimensions OR pack size
        - EAN missing on Amazon side
        - Need to confirm product variant (color, scent, size)

        ### Step 6.2: Browser Verification Steps

        1. **Navigate to Amazon Product Page**
           ```
           URL: https://www.amazon.co.uk/dp/{ASIN}
           ```

        2. **Extract and Verify**
           - Full product title
           - Selected size/variant (dropdown value)
           - "About this item" bullet points
           - Technical details table
           - Unit count
           - Customer review mentions of pack contents

        3. **Look for Pack Indicators On Page**
           - Size Name: "Pack of 10", "500 ml (Pack of 3)"
           - Unit Count: "3.0 count"
           - Title includes "X x" or "Pack of X"

        4. **Take Screenshot Evidence**
           - Capture the product page showing title and price
           - Save for documentation

        ### Step 6.3: Browser Verification Checklist

        ```
        ☐ Product title matches supplier description
        ☐ Pack size explicitly stated or confirmed
        ☐ No variant differences (color, size, scent)
        ☐ Price matches expected selling price
        ☐ Product is in stock / available
        ```

        ### Step 6.4: Recording Verification Results

        Document each verification:
        ```
        | ASIN       | URL                           | Finding                          | Date       |
        |------------|-------------------------------|----------------------------------|------------|
        | B0DJDH23JW | amazon.co.uk/dp/B0DJDH23JW    | 10-Pack confirmed (9x9 = size)   | 2025-12-27 |
        | B07WDRQ4J7 | amazon.co.uk/dp/B07WDRQ4J7    | 5 Bottles confirmed              | 2025-12-27 |
        ```

        ---

        ## 7. PHASE 6: ADJUSTED PROFIT CALCULATION

        ### Step 7.1: When Pack Sizes Differ

        If Amazon requires more units than supplier sells individually:

        ```
        Pack Ratio = Amazon Pack Size / Supplier Pack Size
        Adjusted Cost = Supplier Price × Pack Ratio
        FBA Fees ≈ Selling Price × 0.30 (estimate)
        Adjusted Profit = Selling Price - Adjusted Cost - FBA Fees
        ```

        ### Step 7.2: Worked Example: TIDYZ DOGGY BAGS

        | Field | Value |
        |:------|:------|
        | Supplier Title | TIDYZ DOGGY BAGS STRONG 50 PCS |
        | Amazon Title | Tidyz 200 x Extra Large Doggy bags (4 x 50) |
        | Supplier Pack | 50 bags |
        | Amazon Pack | 200 bags |
        | Pack Ratio | 200 ÷ 50 = **4** |
        | Supplier Price | £0.67 |
        | Selling Price | £6.50 |
        | Adjusted Cost | £0.67 × 4 = **£2.68** |
        | FBA Fees (30%) | £6.50 × 0.30 = **£1.95** |
        | **Adjusted Profit** | £6.50 - £2.68 - £1.95 = **£1.87** |
        | **Result** | ✅ PROFITABLE after adjustment |

        ### Step 7.3: Worked Example: PHOODS FOIL TRAY (Unprofitable)

        | Field | Value |
        |:------|:------|
        | Supplier Title | PHOODS FOIL TRAY ROASTER |
        | Amazon Title | Superior Sandwich Platter Trays - Pack of 10 |
        | Supplier Pack | 1 tray |
        | Amazon Pack | 10 trays |
        | Pack Ratio | 10 ÷ 1 = **10** |
        | Supplier Price | £1.08 |
        | Selling Price | £14.97 |
        | Adjusted Cost | £1.08 × 10 = **£10.80** |
        | FBA Fees (30%) | £14.97 × 0.30 = **£4.49** |
        | **Adjusted Profit** | £14.97 - £10.80 - £4.49 = **-£0.32** |
        | **Result** | ❌ LOSS - AUDITED OUT |

        ### Step 7.4: Alternative Calculation Method

        Some reports use:
        ```
        Adjusted Profit = NetProfit - (SupplierPrice × (Pack Ratio - 1))
        ```

        Choose one method and apply consistently.

        ---

        ## 8. PHASE 7: FINAL CATEGORIZATION

        ### Step 8.1: VERIFIED Criteria

        A product is **VERIFIED** if ALL of the following are true:
        - ☐ Exact EAN match (Supplier EAN == Amazon EAN)
        - ☐ Pack sizes match (or supplier has more)
        - ☐ Brand/product/variant confirmed via title analysis
        - ☐ Adjusted profit > £0

        ### Step 8.2: HIGHLY LIKELY Criteria (Non‑Exact EAN)

        Use **HIGHLY LIKELY** only when the evidence is **strong enough to treat as a practical match**, but one key element is missing or untrusted (typically an EAN) and you still need a final confirmation later.

        **Mandatory gates (ALL must pass):**
        - ☐ **NO explicit brand conflict** (both titles explicitly state brands and they are different)  
          → If explicit brand conflict exists: **UNRELATED / NOT INCLUDED** (count‑only; do not list)
        - ☐ **Product‑type anchors are STRONG** (same core product nouns; no conflicting core nouns)
        - ☐ **At least one unique anchor exists** (model / MPN / SKU / part‑number / series token)  
          → If **no unique anchor**: **UNRELATED / NOT INCLUDED** (count‑only; do not list)
        - ☐ **No confirmed variant contradiction** (size/scent/color/model conflict proven)
        - ☐ **Financials plausibly positive** (Net Profit / Adjusted Profit > 0 using best‑available pack assumption)

        **EAN handling (critical):**
        - If **one EAN is missing / invalid / untrusted** (e.g., scientific notation, corrupted digits) → this is **less negative** than an EAN conflict.
        - If **both EANs are present, strict‑valid, and different** → apply a **likelihood penalty** (do **NOT** auto‑eliminate).  
          Default routing in this case is **NEEDS VERIFICATION** (if the gates above pass).  
          You may keep **HIGHLY LIKELY** only when the row itself contains an explicit pack/variant explanation that plausibly causes different EANs (e.g., supplier single vs Amazon multipack clearly stated) **and** the unique anchor is decisive.

        Output rule: HIGHLY LIKELY rows are **listed** in the report, with explicit “why it’s likely” + “what remains to confirm”.

        ### Step 8.3: NEEDS VERIFICATION Criteria (Anti‑Noise)

        Use **NEEDS VERIFICATION** only when the candidate looks real, but you must confirm **one or two critical details** before upgrading/downgrading.

        #### Eligibility gate (ANTI‑NOISE) — MANDATORY
        **A row may be listed under NEEDS VERIFICATION ONLY if ALL of the following are true:**
        - ☐ **NO explicit brand conflict** (both explicit + different)
        - ☐ **Product‑type anchors are at least MODERATE** (core product nouns align; no hard conflict)
        - ☐ **At least one unique anchor exists** (model/MPN/SKU/part‑number/series token)

        If any of the above fails → route to **UNRELATED / NOT INCLUDED** (count‑only; not printed), even if brand loosely matches.

        **Common “blocking detail” triggers for NEEDS VERIFICATION** (one or two is enough once eligible):
        - ☐ **EAN conflict** (both EANs present + strict‑valid + different) and no explicit in‑row pack/variant explanation
        - ☐ **Brand present on one title but missing on the other** (brand confirmation needed)
        - ☐ **Pack/quantity ambiguity** (single vs multipack not certain; “x” tokens ambiguous)
        - ☐ **Variant ambiguity** (size/scent/color/model may differ but not proven)
        - ☐ **Split / repack candidate** (Supplier pack > Amazon pack) — verify feasibility + true per‑unit economics
        - ☐ Any other case where evidence is strong but not sufficient to confirm the exact product/variant/pack

        **Routing constraints (MANDATORY):**
        - If **EAN is strict‑exact MATCH**:  
          → This is a **confirmed match**. It must route to **VERIFIED** or **AUDITED OUT**, unless a specific pack/variant ambiguity remains unresolved (in that case NEEDS VERIFICATION is allowed, but you must state exactly what is ambiguous).
        - If **both EANs are strict‑valid and different**:  
          → Allowed in NEEDS VERIFICATION **only** when eligibility gates pass (brand ok + product‑type ok + unique anchor exists). Otherwise **UNRELATED / NOT INCLUDED**.
        - If **one/both EANs missing/invalid/untrusted**:  
          → Allowed in NEEDS VERIFICATION only when eligibility gates pass **and** at least one blocking detail exists. Otherwise **UNRELATED / NOT INCLUDED**.

        Output rule: NEEDS VERIFICATION rows are **listed** in the report, with explicit “what must be checked” notes.

        ### Step 8.4: AUDITED OUT Criteria (Confirmed Match, Not Actionable)

        A row is **AUDITED OUT** only if it is a **confirmed match**, but excluded due to actionability/workflow gates.

        **Confirmed match definition (must be true):**
        - ☐ **Strict exact EAN match after normalization**, OR
        - ☐ (**Brand matches** AND **product‑type anchors STRONG** AND **a unique anchor matches** and no contradictions)

        **AUDITED OUT reasons (any one):**
        - ☐ **Adjusted Profit ≤ 0** after a **confirmed** pack ratio adjustment
        - ☐ **Confirmed variant mismatch** within the same product family (size/scent/color/model)  
          (i.e., it is related but not the exact sellable variant)
        - ☐ **Confirmed pack/quantity mismatch** that makes it non‑actionable in your workflow (e.g., splitting not allowed, compliance constraint)
        - ☐ Any other explicit “confirmed match but excluded” gate you define (must be stated)

        **Never route to AUDITED OUT** for:
        - Product‑type clearly different
        - Completely unrelated products
        - Weak/contradictory evidence with no confirmable path  
          → These are **UNRELATED / NOT INCLUDED** (count‑only; not printed)



        ## 9. DECISION TREES & FLOWCHARTS

        ### 10.1: Master Decision Tree (Revised; Brand and EAN handled correctly)

        ```
        START
          │
          ▼
        Normalize EANs (strip whitespace → remove trailing ".0" → reject scientific notation → digits-only → left-pad attempts → checksum) and parse titles
          │
          ▼
        1) Determine Brand Status
           ├─ BRAND_CONFLICT (both explicit + different) → UNRELATED / NOT INCLUDED (count-only; do not list)
           └─ else continue
          │
          ▼
        2) Strict exact EAN match?
           ├─ YES → Check pack/variant + Adjusted Profit
           │        ├─ Actionable + no remaining ambiguity → VERIFIED
           │        ├─ Confirmed match but not actionable (AdjProfit ≤ 0 / confirmed variant mismatch / confirmed non-compliant workflow requirement) → AUDITED OUT
           │        └─ Match but pack/variant ambiguity remains → NEEDS VERIFICATION (state what must be checked)
           └─ NO → continue
          │
          ▼
        3) Evaluate Product-Type Anchor Strength (STRONG / MODERATE / WEAK)
           ├─ WEAK or conflicting core product nouns → UNRELATED / NOT INCLUDED (count-only; do not list)
           └─ else continue
          │
          ▼
        4) Determine Unique-Anchor Presence (ANTI-NOISE gate)
           ├─ NO unique anchor (model/MPN/SKU/part-number/series token) → UNRELATED / NOT INCLUDED (count-only; do not list)
           └─ else continue
          │
          ▼
        5) EAN state (non-exact):
           ├─ One EAN missing/invalid/untrusted → proceed on title/pack/anchor evidence (less negative than conflict)
           └─ Both EANs strict-valid and different → apply likelihood penalty (still eligible; do NOT auto-eliminate)
          │
          ▼
        6) Route (non-exact EAN cases):
           ├─ BRAND_MATCH + STRONG product-type anchors + unique anchor + profit>0 + no confirmed variant contradiction
           │       ├─ If EANs different → NEEDS VERIFICATION by default unless an explicit pack/variant explanation is present in-row
           │       └─ If EAN missing/invalid → HIGHLY LIKELY (higher confidence than EAN-different case)
           ├─ BRAND_MISSING_ONE_SIDE + STRONG product-type anchors + unique anchor → NEEDS VERIFICATION
           │       (rare HIGHLY LIKELY only if the unique anchor is decisive)
           └─ else → UNRELATED / NOT INCLUDED (count-only; do not list)
        END
        ```

        ### 10.2: Pack Size Detection Flowchart

        ```
        READ TITLE
            │
            ▼
        Contains "Pack of X"? ──YES──► Pack = X
            │ NO
            ▼
        Contains "X PACK"? ──YES──► Pack = X
            │ NO
            ▼
        Contains "XPCE" or "X PCS"? ──YES──► Pack = X
            │ NO
            ▼
        Contains "X x Y" before unit? ──YES──► Dimensions, Pack = 1
            │ NO
            ▼
        Contains "X x Product"? ──YES──► Pack = X
            │ NO
            ▼
        Default: Pack = 1
        ```


        ---

        ## 10. COMMON PITFALLS TO AVOID

        ### 10.1: Dimension Misreading

        | ❌ WRONG | ✅ CORRECT |
        |:---------|:-----------|
        | "15 x 5.5 x 5.5 cm" = Pack of 15 | "15 x 5.5 x 5.5 cm" = Dimensions (15cm height) |
        | "9x9 inch" = Pack of 9 | "9x9 inch" = Tray size (9" × 9") |
        | "2x magnification" = Pack of 2 | "2x magnification" = Optical feature |
        | "9 LED" = Pack of 9 | "9 LED" = Number of LEDs in torch |

        ### 10.2: Pack Size in Supplier Title

        Always check the SUPPLIER title for pack indicators:
        - "DOYLEYS 40" = 40-pack (not Amazon mismatch)
        - "SHOT GLASSES 20PCE" = 20-pack
        - "(SOLD EACH)" = Single unit

        ### 10.3: EAN Match ≠ Automatic Match

        An exact EAN ensures same barcode, but:
        - Amazon may sell multipacks of the EAN product
        - Supplier may sell singles of the same EAN
        - Always verify pack sizes independently

        ### 10.4: Fee Calculation Consistency

        Use one method throughout:
        ```
        Method A: Adjusted Profit = Selling Price - (Supplier Price × Ratio) - (Selling Price × 0.30)
        Method B: Adjusted Profit = NetProfit - (Supplier Price × (Ratio - 1))
        ```

        ---

        ## 11. 📊 OUTPUT REQUIREMENTS
        

### Output File: PHASEA_MANUAL_REPORT_MMDDHHSS.md

The report must follow this section structure (STRICT):

1. **Summary Counts** at the top (include recommended vs excluded sub-counts)
2. **VERIFIED — RECOMMENDED (count=Xr)**  
   Exact EAN matches that pass pack/variant/profit/workflow gates (actionable).
3. **VERIFIED — AUDITED OUT / EXCLUDED (count=Xf)**  
   Exact EAN matches (confirmed same product) that fail pack/variant/profit/workflow gates (non-actionable, kept for audit trail).
4. **HIGHLY LIKELY — RECOMMENDED (count=Yr)**  
   Strong non-exact-EAN matches that pass profitable/sellable gates (actionable).
5. **HIGHLY LIKELY — AUDITED OUT / EXCLUDED (count=Yf)**  
   Strong non-exact-EAN matches that are very likely the same product but fail pack/variant/profit/workflow gates (non-actionable, kept for audit trail).
6. **NEEDS VERIFICATION (count=Z)**  
   Upgradeable items needing 1–2 confirmable details to move to HIGHLY LIKELY or VERIFIED.
7. (Optional) **Additional Notes** (e.g., IP complaint risk, gating caveats)

---

## 🆕 TABLE SCHEMA (USE THIS EXACT SCHEMA IN ALL TABLES)

Use the SAME schema for all tables in all sections:
- VERIFIED — RECOMMENDED
- VERIFIED — AUDITED OUT / EXCLUDED
- HIGHLY LIKELY — RECOMMENDED
- HIGHLY LIKELY — AUDITED OUT / EXCLUDED
- NEEDS VERIFICATION

Put exclusion reasons into **Filter Reason**.

Expected columns:

| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |

### Table Formatting Requirements (MANDATORY)
- All tables must be fixed-width, space-padded so `|` separators align vertically in a plain-text editor.
- Wrap every table in a fenced code block using triple backticks with language `text`:

  Start: ```text  
  End:   ```

*Example:**
```text
| Verdict  | Confidence | SupplierTitle                    | AmazonTitle                                           | Supplier EAN  | Amazon EAN    | ASIN       | SupplierPrice | SellingPrice | NetProfit | ROI    | Sales | Pack Verdict                    | Adjusted Profit | Key Match Evidence              | Filter Reason |
|----------|------------|----------------------------------|-------------------------------------------------------|---------------|---------------|------------|---------------|--------------|-----------|--------|-------|---------------------------------|-----------------|---------------------------------|---------------|
| VERIFIED | 95         | AMTECH LED MINI TORCH            | Amtech S1532 9 LED mini Torch                         | 5032759031078 | 5032759031078 | B003XKPUSQ | £1.72         | £7.99        | £2.35     | 118.6% | 200   | 1:1 (9 LED is spec)             | £2.35           | Exact EAN match; titles align   | -             |
```

- No tabs. Spaces only.
- Column width calculation is mandatory. Header separator row must match widths exactly.
- Table safety:
  - Replace literal `|` with `/` inside cell values.
  - Replace embedded newlines inside any cell with spaces before writing the row.

### Column Notes
- **Verdict** must be exactly one of:
  - `VERIFIED`
  - `VERIFIED — AUDITED OUT`
  - `HIGHLY LIKELY`
  - `HIGHLY LIKELY — AUDITED OUT`
  - `NEEDS VERIFICATION`
- **Supplier EAN / Amazon EAN**: Use `-` if missing, invalid, or untrusted after normalization.
- **Filter Reason**:
  - Use `-` for recommended rows
  - For audited-out rows: state the explicit exclusion reason (pack/variant/profit/workflow)
  - For needs-verification rows: state what 1–2 details must be confirmed

---

## 📋 REPORT STRUCTURE (MATCHING REFERENCE FORMAT)

The final report must follow this structure exactly:

```markdown
# PHASEA MANUAL REPORT
**Generated:** YYYY-MM-DD
**Input File:** [path to CSV]
**Supplier:** [supplier name if known]

## Summary Counts
- VERIFIED — RECOMMENDED: Xr
- VERIFIED — AUDITED OUT / EXCLUDED: Xf
- HIGHLY LIKELY — RECOMMENDED: Yr
- HIGHLY LIKELY — AUDITED OUT / EXCLUDED: Yf
- NEEDS VERIFICATION: Z
- UNRELATED / NOT INCLUDED: U
- TOTAL ANALYZED: N


        ### 12.1: Pre-Analysis Checklist

        ```
        ☐ Financial report loaded
        ☐ EAN columns normalized
        ☐ RowID column created
        ☐ Valid EAN filter applied
        ☐ Working list of EAN matches extracted

        ### 12.2: Per-Product Analysis Checklist

        ☐ Supplier title parsed (brand, product, size, pack)
        ☐ Amazon title parsed (brand, product, size, pack)
        ☐ Pack sizes identified (not dimensions)
        ☐ Pack ratio calculated
        ☐ Adjusted profit calculated (if ratio ≠ 1)
        ☐ Browser verification (if ambiguous)
        ☐ Final category assigned

        ### 12.3: Browser Verification Checklist

        ☐ Navigate to correct ASIN URL
        ☐ Verify product title matches
        ☐ Check size/variant selector
        ☐ Read "About this item" for pack info
        ☐ Check technical details for unit count
        ☐ Take screenshot for documentation
        ☐ Record finding in verification log

        ### 12.4: Report Generation Checklist

        ☐ VERIFIED products listed with all columns
        ☐ HIGHLY LIKELY products listed with evidence
        ☐ NEEDS VERIFICATION products with blocking details
        ☐ AUDITED OUT products with exclusion reason
        ☐ Tables formatted correctly
        ☐ Profit summary included
        ☐ Pack corrections documented
        ☐ UNRELATED / NOT INCLUDED is count-only (no table)
        ☐ Reconciliation: buckets sum to TOTAL ROWS; no duplicate RowIDs
        ☐ Sanitize titles: replace '|' with '/' and remove newlines
        ```

        ---

        ## APPENDIX A: COLUMN DEFINITIONS FOR OUTPUT TABLES
        ### Output formatting hard rules (MANDATORY)

        - Output tables MUST use the **full column set** defined below (do not replace headers with `...`, do not omit columns).
        - Before printing any table: **replace newlines/tabs in titles with spaces**.
        - Escape the pipe character inside cell text (`|` → `\|`) so markdown tables do not break.
        - Never print scientific notation for numeric fields (e.g., RSU). Use plain integers/decimals.
        - If a value is unknown, leave it blank; do NOT invent.

        ### Consistency invariants (MANDATORY)

        - If `EAN_status == MATCH`, the row MUST be either **VERIFIED** or **AUDITED OUT** (confirmed match path).
          - Exception: ONLY if **both titles explicitly state different brands**, then use **NEEDS VERIFICATION (ANOMALY CHECK)**.
        - If `AdjustedProfit <= 0` after confirmed RSU, the row cannot be VERIFIED → **AUDITED OUT**.
        - NEEDS VERIFICATION rows must satisfy the unique-anchor eligibility gate; otherwise they must be UNRELATED.



        | Column | Description | Example |
        |:-------|:------------|:--------|
        | Verdict | Final category | VERIFIED, HIGHLY LIKELY, etc. |
        | Confidence | 0-100 score | 95 |
        | SupplierTitle | Full supplier product name | MASON CASH MIXING BOWL CREAM 29CM |
        | AmazonTitle | Full Amazon product name (truncated) | Mason Cash Colour Mix Cream... |
        | Supplier EAN | Barcode from supplier | 5010853235530 |
        | Amazon EAN | Barcode from Amazon | 5010853235530 |
        | ASIN | Amazon product ID | B01IFIJ91Y |
        | SupplierPrice | Cost inc VAT | £7.66 |
        | SellingPrice | Amazon price inc VAT | £24.99 |
        | NetProfit | Original profit before adjustment | £5.11 |
        | ROI | Return on investment % | 73.8% |
        | Sales | Estimated monthly sales | 200 |
        | Pack Verdict | Pack analysis result | 1:1, Pack mismatch 1→4, etc. |
        | Adjusted Profit | Profit after pack adjustment | £5.11 or -£1.28 |
        | Key Match Evidence | Why this is a match | Exact EAN match, Brand match |
        | Filter Reason | Why audited out / excluded (if applicable) | Different SKU, Unprofitable |

        ---

        ## APPENDIX B: SAMPLE WORKFLOW EXECUTION

        ### Example: Analyzing Row 964 (SUPERIOR FOIL)

        **Step 1: Extract Data**
        ```
        RowID: 964
        ASIN: B0DJDH23JW
        Supplier EAN: 5060357990107
        Amazon EAN: 5060357990107
        SupplierTitle: SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN
        AmazonTitle: Superior 10-Pack Aluminium Foil Trays...9x9 inch
        ```

        **Step 2: EAN Match Check**
        - Supplier EAN: 5060357990107
        - Amazon EAN: 5060357990107
        - Result: ✅ EXACT MATCH

        **Step 3: Title Analysis**
        - Supplier: "10 CONTAINERS" → 10-pack
        - Supplier: "9X9IN" → Tray size (9 inches × 9 inches)
        - Amazon: "10-Pack" → 10-pack
        - Amazon: "9x9 inch" → Tray size

        **Step 4: Pack Size Determination**
        - Supplier Pack: 10
        - Amazon Pack: 10
        - Ratio: 10/10 = 1 (1:1 match)
        - **CRITICAL:** "9X9" is tray SIZE, not pack count!

        **Step 5: Profit Check**
        - NetProfit: £2.13
        - No adjustment needed (ratio = 1)

        **Step 6: Final Category**
        - EAN matches: ✅
        - Pack matches: ✅
        - Profit positive: ✅
        - **VERDICT: VERIFIED**

        ---

        ## APPENDIX C: DETAILED REASONING EXAMPLES (15+ Products)

        This section provides the exact thought process and logic chains used when classifying each product. Study these examples to understand the reasoning methodology.

        ---

        ### C.1: VERIFIED PRODUCT EXAMPLES

        #### Example C.1.1: EVERREADY T8 4FT 36W TUBE LIGHT (Row 370)

        **Raw Data:**
        ```
        Supplier EAN: 5050028016069
        Amazon EAN: 5050028016069
        SupplierTitle: EVERREADY T8 4FT 36W TUBE LIGHT
        AmazonTitle: Eveready T8 Tube 4ft 36w White 3500k
        SupplierPrice: £2.99
        SellingPrice: £18.99
        NetProfit: £8.00
        ```

        **Step-by-Step Reasoning:**

        1. **EAN Check:**
           - Supplier: 5050028016069
           - Amazon: 5050028016069
           - **EXACT MATCH** ✅
           - *Reasoning: Both are valid 13-digit EAN codes and they match exactly*

        2. **Brand Extraction:**
           - Supplier: "EVERREADY" (first word, uppercase)
           - Amazon: "Eveready" (first word, title case)
           - **MATCH** ✅
           - *Reasoning: Same brand, different capitalization is acceptable*

        3. **Product Type Analysis:**
           - Supplier: "T8 TUBE LIGHT"
           - Amazon: "T8 Tube"
           - **MATCH** ✅
           - *Reasoning: Both describe the same fluorescent tube type (T8)*

        4. **Size/Spec Analysis:**
           - Supplier: "4FT 36W" (4 feet length, 36 watts)
           - Amazon: "4ft 36w" (4 feet length, 36 watts)
           - **MATCH** ✅
           - *Reasoning: Identical specifications, case difference irrelevant*

        5. **Pack Size Detection:**
           - Supplier: No pack indicator → Single unit
           - Amazon: No pack indicator → Single unit
           - **1:1 MATCH** ✅
           - *Reasoning: Neither title contains "pack", "pcs", or quantity indicators*

        6. **Number Interpretation Check:**
           - "4FT" → Length (4 feet) → NOT pack size
           - "36W" → Wattage (36 watts) → NOT pack size
           - "3500k" → Color temperature (3500 Kelvin) → NOT pack size
           - *Reasoning: All numbers are product specifications, not quantities*

        7. **Profit Verification:**
           - NetProfit: £8.00 > £0
           - No pack adjustment needed
           - **PROFITABLE** ✅

        8. **Final Classification:**
           ```
           EAN Match: ✅
           Title Match: ✅
           Pack Match: ✅ (1:1)
           Profit: ✅ (£8.00)
           
           VERDICT: VERIFIED
           Confidence: 95
           ```

        ---

        #### Example C.1.2: SUPERIOR FOIL 10 CONTAINERS (Row 964) - Dimension Pitfall Avoided

        **Raw Data:**
        ```
        Supplier EAN: 5060357990107
        Amazon EAN: 5060357990107
        SupplierTitle: SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN
        AmazonTitle: Superior 10-Pack Aluminium Foil Trays with Paper Lids...9x9 inch
        ```

        **Critical Reasoning - Why "9X9" is NOT Pack Size:**

        1. **Initial Scan - Potential Pack Indicators:**
           - Supplier: "10 CONTAINERS" ← PACK SIZE (10)
           - Supplier: "9X9IN" ← COULD BE misread as pack
           - Amazon: "10-Pack" ← PACK SIZE (10)
           - Amazon: "9x9 inch" ← COULD BE misread as pack

        2. **Context Analysis for "9X9":**
           - Question: What comes AFTER "9X9"?
           - Answer: "IN" (inches) or "inch"
           - *Conclusion: "9X9IN" means 9 inches × 9 inches = TRAY DIMENSIONS*

        3. **Verification Logic:**
           ```
           IF number followed by unit (inch, cm, mm):
               → It's a DIMENSION, not pack size
           ELSE IF number followed by "pack", "pcs", "containers":
               → It's a PACK SIZE
           ```

        4. **Correct Pack Extraction:**
           - Supplier Pack: 10 (from "10 CONTAINERS")
           - Amazon Pack: 10 (from "10-Pack")
           - Ratio: 1:1

        5. **Why This Matters:**
           - A regex script incorrectly read "9" as pack size
           - Manual analysis correctly identifies context
           - "9x9" ALWAYS refers to tray dimensions in food container context

        **Final Classification:**
        ```
        VERDICT: VERIFIED
        Pack Verdict: 1:1 (10-pack; 9x9 is tray SIZE, not pack count)
        Confidence: 95
        ```

        ---

        #### Example C.1.3: APOLLO VINEGAR SHAKER (Row 1103) - Another Dimension Pitfall

        **Raw Data:**
        ```
        SupplierTitle: APOLLO VINEGAR SHAKER
        AmazonTitle: apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker, Clear 15 x 5.5 x 5.5 cm
        ```

        **Critical Reasoning - Why "15" is NOT Pack Size:**

        1. **Suspicious Element Identified:**
           - Amazon has: "15 x 5.5 x 5.5 cm"
           - Script might extract "15" as pack size

        2. **Context Analysis:**
           - Question: What is "15 x 5.5 x 5.5"?
           - Answer: Three numbers followed by "cm"
           - Pattern: Length × Width × Height
           - *Conclusion: These are DIMENSIONS in centimeters*

        3. **Physical Reasoning:**
           - 15cm = ~6 inches (reasonable shaker height)
           - 5.5cm = ~2.2 inches (reasonable diameter)
           - A "pack of 15" shakers for £6.58 would be ~£0.44 each (unrealistic)

        4. **Final Check:**
           - Supplier: No pack indicator → Single unit
           - Amazon: "15 x 5.5 x 5.5 cm" = Dimensions → Single unit
           - **1:1 MATCH**

        **Key Learning:**
        ```
        RULE: When you see "X x Y x Z" followed by a unit (cm, mm, inch):
              → These are ALWAYS dimensions (L×W×H)
              → NEVER interpret as pack size
        ```

        ---

        ### C.2: HIGHLY LIKELY / NEEDS VERIFICATION EXAMPLES (EAN NOT VERIFIED)

        These are examples where strict exact-EAN verification is not available (EAN missing/untrusted) OR where there is an EAN conflict that must be resolved.

        **Rule reminder:** If BOTH EANs are present, strict-valid, and different → do NOT eliminate the row.
        Default routing is **NEEDS VERIFICATION** unless pack/variant evidence and unique anchors clearly explain the difference.
        If brands are explicit and different → **UNRELATED / NOT INCLUDED**.


#### Example C.2.1: EAN conflict (both EANs present + strict-valid + different)

        **Scenario**
        - Supplier EAN: `1234567890123` (strict-valid)
        - Amazon EAN: `9876543210987` (strict-valid)
        - Supplier Title: `BRANDX Shampoo 250 ml`
        - Amazon Title: `BRANDX Shampoo 4 x 250 ml`

        **How to route**
        1) Brand gate: passes (same brand).
        2) Product-type anchors: passes (shampoo / same format).
        3) Pack logic: Amazon explicitly indicates a multipack (4 × 250 ml).
        4) EAN conflict: expected to reduce confidence, but does **not** eliminate the row.
           Multipacks commonly carry a different barcode than the single unit.

        **Verdict**
        - Default: **NEEDS VERIFICATION** (EAN conflict must be validated).
        - Upgrade to **HIGHLY LIKELY** only if a unique anchor also matches (model/MPN/SKU/part number/series token),
          and there are no contradictions.

        **What must be verified**
        - Confirm the Amazon listing is truly a 4-pack (not a misleading title).
        - Confirm the supplier product is a single unit.
        - Confirm the Amazon EAN corresponds to the multipack, and the supplier EAN corresponds to the single unit (manufacturer/barcode evidence).

Example C.2.2: AMTECH POINTING TROWEL (Row 1167) - Browser Verified

        **Raw Data:**
        ```
        Supplier EAN: 5032759027644
        Amazon EAN: (missing)
        SupplierTitle: AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP
        AmazonTitle: Amtech G0230 150mm (6") Pointing trowel with soft grip
        ```

        **Reasoning Chain:**

        1. **EAN Check:**
           - Supplier: 5032759027644 (valid)
           - Amazon: Missing/blank
           - **NO EAN AVAILABLE** → Cannot be VERIFIED via EAN alone

        2. **Brand Analysis:**
           - Supplier: "AMTECH" (UK tool brand)
           - Amazon: "Amtech" (same)
           - **EXACT MATCH** ✅

        3. **Product Type:**
           - Supplier: "POINTING TROWEL"
           - Amazon: "Pointing trowel"
           - **EXACT MATCH** ✅

        4. **Size Analysis:**
           - Supplier: "150M(6")" = 150mm = 6 inches
           - Amazon: "150mm (6")" = 150mm = 6 inches
           - **EXACT MATCH** ✅

        5. **Feature Analysis:**
           - Supplier: "WITH SOFT GRIP"
           - Amazon: "with soft grip"
           - **EXACT MATCH** ✅

        6. **Model Number Check:**
           - Amazon includes: "G0230"
           - Supplier: Not mentioned
           - *This doesn't disqualify - supplier just omitted model*

        7. **Browser Verification Performed:**
           - Navigated to amazon.co.uk/dp/B00ABJQTPU
           - Confirmed: 150mm (6") Pointing trowel
           - Confirmed: Soft grip feature
           - Confirmed: Single unit (not multi-pack)

        **Why HIGHLY LIKELY instead of VERIFIED:**
        - No Amazon EAN to compare
        - Strong match confirmed via browser, but barcode unverified

        **Final Classification:**
        ```
        VERDICT: HIGHLY LIKELY
        Confidence: 90
        Evidence: Exact title match + Browser verified
        Risk: Amazon EAN missing - confirm barcode at purchase
        ```

        ---

        ### C.3: NEEDS VERIFICATION EXAMPLES

        #### Example C.3.1: FAIRY DISH BRUSH & REFILLS 3PCS (Row 1168) - Pack Ambiguity

        **Raw Data:**
        ```
        SupplierTitle: FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3PCS
        AmazonTitle: Fairy Soap Dispensing Dish Brush
        ASIN: B0BYKDX25N
        ```

        **Reasoning Chain:**

        1. **Brand Match:**
           - Supplier: "FAIRY"
           - Amazon: "Fairy"
           - **MATCH** ✅

        2. **Product Type Match:**
           - Both: "Soap Dispensing Dish Brush"
           - **MATCH** ✅

        3. **Pack/Contents Analysis:**
           - Supplier: "& REFILLS 3PCS"
           - Amazon: No mention of refills
           - **MISMATCH** ⚠️

        4. **Interpretation of "3PCS":**
           - Option A: 1 brush + 2 refills = 3 pieces
           - Option B: 3 brushes total
           - **AMBIGUOUS** → Need verification

        5. **Browser Verification Performed:**
           - Amazon page shows: Single brush handle only
           - No refills included in this ASIN
           - Refills sold separately (B0BYKDLJ5Z)

        6. **Blocking Details:**
           - Supplier includes refills, Amazon doesn't
           - If "3PCS" = 1 brush + 2 refills, then it's a different bundle

        **Why NEEDS VERIFICATION instead of UNRELATED / NOT INCLUDED:**
        - Base product (brush) matches
        - Could be supplier bundling their own set
        - Need to confirm what supplier actually ships

        **Final Classification:**
        ```
        VERDICT: NEEDS VERIFICATION
        Blocking Detail: Amazon = single brush, Supplier = 3-piece set
        Action Needed: Verify if "3PCS" means brush+2 refills or 3 brushes
        ```

        ---

        #### Example C.3.2: PRIMA vs LARA SHOWERHEAD (Row 157) — Brand differs (both explicit) → UNRELATED / NOT INCLUDED

        **Raw Data:**
        ```
        SupplierTitle: PRIMA MULTI SHOWERHEAD CHROME
        AmazonTitle: Lara | Multi Spray Shower Head - Chrome
        ASIN: B00569FG1S
        ```

        **Reasoning Chain:**

        1. **Brand Analysis:**
           - Supplier: "PRIMA"
           - Amazon: "Lara"
           - **DIFFERENT BRANDS** ⚠️

        2. **Product Type:**
           - Supplier: "MULTI SHOWERHEAD"
           - Amazon: "Multi Spray Shower Head"
           - **MATCH** ✅

        3. **Feature Analysis:**
           - Both: "CHROME" color
           - **MATCH** ✅

        4. **Hard-block rule (explicit brand difference):**
           - Both brands are explicitly present and different.
           - Under the boolean gates, treat as **UNRELATED / NOT INCLUDED** (do not list).
           - Only escalate to NEEDS VERIFICATION if there are uunmistakable unique anchors (model number, exact SKU, highly distinctive token set).


        **Final Classification:**
        ```
        VERDICT: UNRELATED / NOT INCLUDED
        Reason: Brand differs and both brands are explicit (hard mismatch)
        ```

        ---

        ### C.4: AUDITED OUT EXAMPLES

        #### Example C.4.1: ULTRATAPE 24MM vs 48MM (Row 1155) - Size Mismatch

        **Raw Data:**
        ```
        SupplierTitle: ULTRATAPE PICTURE FRAME TAPE 24MMX50M
        AmazonTitle: Ultratape | Picture Frame Tape | 48mm x 33m
        ```

        **Reasoning Chain:**

        1. **Brand Match:**
           - Both: "ULTRATAPE" / "Ultratape"
           - **MATCH** ✅

        2. **Product Type Match:**
           - Both: "PICTURE FRAME TAPE"
           - **MATCH** ✅

        3. **Size Analysis:**
           - Supplier WIDTH: 24mm
           - Amazon WIDTH: 48mm
           - **MISMATCH** ❌ (2x difference!)

        4. **Length Analysis:**
           - Supplier LENGTH: 50m
           - Amazon LENGTH: 33m
           - **MISMATCH** ❌ (different)

        5. **Browser Verification:**
           - Confirmed Amazon is 48mm × 33m
           - No 24mm variant available on this listing

        6. **Why This Cannot Match:**
           - 24mm tape ≠ 48mm tape (physically different)
           - Different SKU entirely
           - Customer expecting 48mm would receive 24mm

        **Final Classification:**
        ```
        VERDICT: AUDITED OUT
        Filter Reason: Width mismatch (24mm supplier vs 48mm Amazon)
        This is NOT a pack size difference - it's a different product
        ```

        ---

        #### Example C.4.2: ELBOW GREASE EUCALYPTUS vs LEMON (Row 1095) - Scent + Pack Mismatch

        **Raw Data:**
        ```
        SupplierTitle: ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G
        AmazonTitle: 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning Action, Lemon Fresh
        ```

        **Reasoning Chain:**

        1. **Brand Match:**
           - Both: "ELBOW GREASE"
           - **MATCH** ✅

        2. **Product Type:**
           - Both: "FOAMING TOILET CLEANER"
           - **MATCH** ✅

        3. **Scent Analysis:**
           - Supplier: "EUCALYPTUS"
           - Amazon: "Lemon Fresh"
           - **MISMATCH** ❌

        4. **Pack Analysis:**
           - Supplier: (single) 500G
           - Amazon: "3 x" (3-pack)
           - **MISMATCH** ❌

        5. **Double Disqualification:**
           - Problem 1: Wrong scent (Eucalyptus ≠ Lemon)
           - Problem 2: Need 3 units (pack adjustment)

        6. **Even if we ignored scent:**
           - Adjusted Profit = £0.82 - (£2.09 × 2) = -£3.35
           - **UNPROFITABLE** ❌

        **Final Classification:**
        ```
        VERDICT: AUDITED OUT
        Filter Reason: Scent mismatch (Eucalyptus vs Lemon) + Pack mismatch (1 vs 3)
        Note: Even without scent issue, adjusted profit is negative
        ```

        ---

        #### Example C.4.3: PHOODS FOIL TRAY 1x vs 10-Pack (Row 363) - Unprofitable After Adjustment

        **Raw Data:**
        ```
        Supplier EAN: 5060357991357
        Amazon EAN: 5060357991357  ← EXACT MATCH!
        SupplierTitle: PHOODS FOIL TRAY ROASTER
        AmazonTitle: Superior Sandwich Platter Trays - Pack of 10
        SupplierPrice: £1.08
        SellingPrice: £14.97
        NetProfit: £3.90
        ```

        **Reasoning Chain:**

        1. **EAN Check:**
           - **EXACT MATCH** ✅
           - *Initial thought: This should be VERIFIED...*

        2. **Pack Analysis:**
           - Supplier: No pack indicator → 1 unit
           - Amazon: "Pack of 10" → 10 units
           - **MISMATCH: Need 10 supplier units!**

        3. **Browser Verification:**
           - Confirmed Amazon listing is Pack of 10 trays
           - £14.97 for 10 trays = £1.50 each

        4. **Adjusted Profit Calculation:**
           ```
           Adjusted Cost = £1.08 × 10 = £10.80
           FBA Fees = £14.97 × 0.30 = £4.49
           Adjusted Profit = £14.97 - £10.80 - £4.49 = -£0.32
           ```

        5. **Why AUDITED OUT despite EAN Match:**
           - EAN confirms same product barcode
           - BUT Amazon bundles 10 units of this product
           - Supplier sells individually
           - After buying 10 and paying fees, we LOSE money

        **Key Learning:**
        ```
        RULE: EAN match is NOT enough!
              Always verify pack sizes.
              Calculate adjusted profit when ratios differ.
              Audit out if adjusted profit ≤ £0
        ```

        **Final Classification:**
        ```
        VERDICT: AUDITED OUT
        Filter Reason: Pack 1→10 requires 10 units = Unprofitable (-£0.32)
        Note: Despite exact EAN match, this is a LOSS after adjustment
        ```

        ---

        ### C.5: REASONING SUMMARY TABLE


        **Note:** “Confirmed match” means confirmed via either:
        - **VERIFIED-path** (strict exact EAN equality after normalization), OR
        - **HIGHLY-LIKELY-path** (brand + product-type + unique anchor confirmation as defined in Step 8.4 Part B).

        | Scenario | Key Question | Answer → Action |
        |:---------|:-------------|:----------------|
        | EAN matches | Pack sizes same? | YES → Check profit → VERIFIED |
        | EAN matches | Pack sizes differ | Calculate adjusted profit → VERIFIED or AUDITED OUT |
        | EAN missing | Brand exact match? | YES → Check all specs → HIGHLY LIKELY |
        | EAN conflict (both strict-valid, different) | Confidence impact | Default → NEEDS VERIFICATION (upgrade only if pack/variant explanation + unique anchors confirm) |
        | Brand differs (both explicit) | Treat as match? | NO → UNRELATED / NOT INCLUDED |
        | Size differs | Confirmed match? | YES → AUDITED OUT; NO → UNRELATED / NOT INCLUDED |
        | Scent differs | Confirmed match? | YES → AUDITED OUT; NO → UNRELATED / NOT INCLUDED |
        | Numbers in title | Followed by unit? | YES → Dimension, not pack |
        | "X x Y" format | Followed by unit? | YES → Dimensions |
        | "2x magnification" | Pack of 2? | NO → Optical feature |
        | Adjusted profit <0 | Keep product? | NO → AUDITED OUT |

        ---

        ### C.6: BROWSER VERIFICATION REASONING EXAMPLES

        #### When Browser Verification Confirmed VERIFIED:

        **Product: AIR WICK REED DIFFUSER PK5 (Row 626)**
        ```
        Initial State:
        - SupplierTitle says "PK5" (5-pack)
        - AmazonTitle says "5 Bottles X 30ml"
        - Could "5 Bottles" be 5 separate units or 1 pack of 5?

        Browser Action:
        - Navigate to amazon.co.uk/dp/B07WDRQ4J7
        - Check size selector: "5 Bottles x 30ml" selected
        - Check product images: Shows 5 boxes of diffuser
        - Check "About this item": Confirms 5 individual bottles

        Conclusion:
        - Supplier sells 5-pack
        - Amazon sells 5-pack (5 × 30ml bottles)
        - 1:1 Match → VERIFIED
        ```

        #### When Browser Verification Caused EXCLUSION:

        **Product: PRICE & KENSINGTON TEAPOT (Row 1402)**
        ```
        Initial State:
        - SupplierTitle: "2 CUP TEAPOT MATT NAVY"
        - AmazonTitle: "Black 6 Cup Teapot"
        - Two potential issues: cup size + color

        Browser Action:
        - Navigate to amazon.co.uk/dp/B0013IUIPA
        - Check title: "Price & Kensington Black 6 Cup Teapot"
        - Check color: Gloss Black (not Matt Navy)
        - Check size: 6 Cup (not 2 Cup)
        - Check variations: No 2-cup or Navy options available

        Conclusion:
        - Size mismatch: 2 cup ≠ 6 cup
        - Color mismatch: Matt Navy ≠ Black
        - Different SKU entirely → AUDITED OUT
        ```

        ---

        *End of Detailed Reasoning Appendix*

        ---

        *End of Methodology Guide*
        *Version: 1.1 (Enhanced with Detailed Reasoning)*
        *Last Updated: 2025-12-28*