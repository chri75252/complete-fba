# FBA PRODUCT MATCH AUDIT - MANUAL ANALYSIS PROMPT

## Input Files

**Four MD Reports to Analyze:**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\CODEX\PHASEA_MANUAL_REPORT_20251228.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\FLASH\PHASEA_MANUAL_REPORT_20251228.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\GEMINI\PHASEA_MANUAL_REPORT_20251228.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\opus\PHASEA_MANUAL_REPORT_20251228.md`

**Main Reference Dataset:**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.xlsx`

---

## Role

You are a forensic "product-match + report-quality" auditor. Your job is to evaluate how correct and complete **four** Markdown (MD) reports are, using the underlying financial dataset as the reference source. 

**CRITICAL REQUIREMENT:** You must perform **MANUAL, ROW-BY-ROW ANALYSIS** of each product entry. **DO NOT USE SCRIPTS OR AUTOMATED APPROACHES.** Read each row yourself, apply human reasoning to determine match validity, and document your thought process.

---

## MANDATORY MANUAL ANALYSIS METHODOLOGY

### How to Manually Analyze Each Product Row

For EVERY product row you evaluate, you MUST follow this step-by-step reasoning process:

#### Step 1: EAN Check
- Read the Supplier EAN value
- Read the Amazon EAN value
- Ask: Do they match exactly?
- If YES → Proceed to Step 2 (EAN match is necessary but NOT sufficient)
- If NO or MISSING → Skip to Step 3 (Non-EAN validation)

#### Step 2: Title-Based Verification (Even with EAN Match)
Parse BOTH titles manually and extract these elements:

| Element | What to Extract |
|:--------|:----------------|
| **Brand** | First word(s), usually in CAPS or title case (e.g., "MASON CASH", "Eveready") |
| **Product Type** | Core product description (e.g., "MIXING BOWL", "TUBE LIGHT") |
| **Size/Variant** | Dimensions, capacity, color, scent (e.g., "29CM", "4L", "CREAM", "EUCALYPTUS") |
| **Pack Quantity** | Explicit pack indicators (e.g., "PK5", "PACK OF 10", "20PCE", "3x") |

Then compare:
- Does brand match? (case variations OK)
- Does product type match?
- Does size/variant match?
- Do pack quantities match?

#### Step 3: Pack Size Detection (CRITICAL)

**CAREFULLY distinguish between PACK SIZES and DIMENSIONS:**

| Pattern | Meaning | Example |
|:--------|:--------|:--------|
| "Pack of X", "PK X", "X PACK" | PACK SIZE | "Pack of 10" = 10 units |
| "X x Product" | PACK SIZE | "3 x Foil" = 3 rolls |
| "XxY cm/mm/inch" | DIMENSIONS | "9x9 inch" = tray SIZE, NOT pack |
| "X LED" | SPECIFICATION | "9 LED" = LED count, NOT pack |
| "Xx magnification" | FEATURE | "2x magnification" = optical zoom, NOT pack |
| "LxWxH" | DIMENSIONS | "15 x 5.5 x 5.5 cm" = product SIZE |

**RULE:** If a number is followed by a UNIT (cm, mm, inch, ml, L, W, kg, g), it is a DIMENSION/SPECIFICATION, NOT a pack size.

#### Step 4: Contradiction Detection

Flag as INVALID or NEEDS REVIEW if you find:
- Pack size mismatch (e.g., "50 PCS" vs "Pack of 200")
- Size mismatch (e.g., "24mm" vs "48mm")
- Scent/color mismatch (e.g., "EUCALYPTUS" vs "LEMON")
- Capacity mismatch (e.g., "2 CUP" vs "6 CUP")
- Product type mismatch (e.g., "POINTING TROWEL" vs "MARGIN TROWEL")

#### Step 5: Classification Decision

Based on your manual analysis, classify each row:

| Category | Criteria |
|:---------|:---------|
| **VALID** | EAN matches + Titles align + Pack matches + No contradictions |
| **LIKELY VALID** | EAN missing BUT brand matches + product matches + specs align |
| **NEEDS REVIEW** | Strong partial match BUT 1-2 blocking details unclear |
| **INVALID** | Clear mismatch confirmed (size, scent, pack, product type) |

---

## EXAMPLE MANUAL REASONING (Follow This Pattern)

### Example 1: VALID Entry

**Row Data:**
```
SupplierTitle: MASON CASH MIXING BOWL CREAM 29CM
AmazonTitle: Mason Cash Colour Mix Cream Mixing Bowl 29cm
Supplier EAN: 5010853235530
Amazon EAN: 5010853235530
```

**Manual Reasoning:**
1. EAN Check: 5010853235530 == 5010853235530 ✅ EXACT MATCH
2. Brand: "MASON CASH" vs "Mason Cash" ✅ MATCH (case variant)
3. Product Type: "MIXING BOWL" vs "Mixing Bowl" ✅ MATCH
4. Size: "29CM" vs "29cm" ✅ MATCH
5. Color: "CREAM" vs "Cream" ✅ MATCH
6. Pack Size: Neither mentions pack → Both single units ✅ MATCH
7. Contradictions: None found
8. **VERDICT: VALID**

### Example 2: INVALID Entry (Dimension Misread as Pack)

**Row Data:**
```
SupplierTitle: APOLLO VINEGAR SHAKER
AmazonTitle: apollo Glass Vinegar Shaker 15 x 5.5 x 5.5 cm
```

**Manual Reasoning:**
1. Amazon title shows "15 x 5.5 x 5.5 cm"
2. Common script error: Reading "15" as pack size
3. **Correct interpretation:** "15 x 5.5 x 5.5 cm" = DIMENSIONS (Height × Width × Depth)
4. This is a SINGLE shaker with dimensions 15cm tall
5. **VERDICT: VALID (1:1 match, dimensions correctly interpreted)**

### Example 3: INVALID Entry (Pack Mismatch)

**Row Data:**
```
SupplierTitle: KILROCK MOULD REMOVER 500ML (SOLD EACH)
AmazonTitle: Kilrock 3 X Blast Away Mould Spray 500ml
Supplier EAN: 5014353093294
Amazon EAN: (missing)
```

**Manual Reasoning:**
1. EAN Check: Amazon EAN missing → Cannot verify via EAN
2. Brand: "KILROCK" vs "Kilrock" ✅ MATCH
3. Product Type: "MOULD REMOVER" vs "Mould Spray" ✅ MATCH
4. Size: "500ML" vs "500ml" ✅ MATCH
5. Pack Size: "(SOLD EACH)" = 1 unit vs "3 X" = 3 units ❌ MISMATCH
6. Pack Ratio: 1 → 3 (need 3 supplier units for 1 Amazon listing)
7. **VERDICT: NEEDS REVIEW (pack adjustment required, verify profitability)**

### Example 4: INVALID Entry (Scent Mismatch)

**Row Data:**
```
SupplierTitle: ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G
AmazonTitle: 3 x Elbow Grease Foaming Toilet Cleaner Lemon Fresh 500g
```

**Manual Reasoning:**
1. Brand: "ELBOW GREASE" ✅ MATCH
2. Product Type: "FOAMING TOILET CLEANER" ✅ MATCH
3. Size: "500G" vs "500g" ✅ MATCH
4. Scent: "EUCALYPTUS" vs "Lemon Fresh" ❌ MISMATCH
5. Pack: Single vs "3 x" = 3-pack ❌ MISMATCH
6. **VERDICT: INVALID (wrong scent variant + pack mismatch)**

---

## Task & Goals

### Primary Goal — Identify which report contains the most VALID/CORRECT entries

Using your MANUAL ANALYSIS methodology, determine which of the 4 reports contains the highest number of **valid/correct product matches**.

**For EACH report, provide:**
- Count of VALID entries (you manually verified)
- Count of INVALID entries (you manually found contradictions)
- Count of NEEDS REVIEW entries (unclear, needs further checking)
- Validity rate = VALID / (VALID + INVALID + NEEDS REVIEW)

**Name ONE winner** based on "most valid/correct entries."

### Secondary Goal — Accuracy Assessment

After primary goal, summarize which report is most "accurate" in terms of:
- High validity rate
- Correct categorization
- Consistency between claimed metrics and reality

### Goal A — Baseline Dataset Analysis

1. Read the Excel file and note:
   - Total rows
   - Rows with SupplierTitle present
   - Rows with AmazonTitle present
   - Rows with Supplier EAN present
   - Rows with Amazon EAN present (for EAN matching)
   - Rows with ASIN present
   - Rows with Sales > 0
   - Rows with NetProfit > 0

2. Apply your manual validity assessment to key rows.

### Goal B — Analyze Each MD Report (Manually)

For EACH of the 4 MD reports:

1. Read and parse the report tables manually
2. For each product row listed, apply your step-by-step manual reasoning
3. Count VALID / INVALID / NEEDS REVIEW
4. Note any concerning patterns (e.g., dimension misreads, pack size errors)

### Goal C — Missing Rows Analysis

Check for rows in the Excel that were:
- Missed by each individual report
- Missed by ALL FOUR reports

Provide:
- Count of Excel rows not covered by each report
- "Missed-by-all-4" list (Top 10-25 rows)
- Brief diagnosis of why rows were missed

### Goal D — Select Winner + Explain Weaknesses

1. Choose the best report based on:
   - **HIGHEST priority:** Most valid/correct entries
   - **Tie-breakers:** Higher validity rate, better coverage of high-profit rows

2. For the winner, also identify:
   - Top 10 products missing from winner
   - Top 10 questionable entries in winner

---

## Constraints

- **DO NOT BROWSE THE WEB.** Use only provided files.
- **DO NOT USE SCRIPTS.** Perform manual, human-readable analysis.
- **DO NOT INVENT DATA.** If field is missing, state "unknown."
- If tables are broken/truncated, state what could not be parsed.
- Show your reasoning for classification decisions (at least for examples).

---

## Output Contract (Markdown Only)

### Required Output Structure:

1. **Executive Summary** (winner + counts; 5-10 bullets)
2. **Dataset Baseline Analysis** (counts from Excel)
3. **Manual Validity Rubric** (your criteria, restated briefly)
4. **Per-Report Evaluation** (4 sections, with VALID/INVALID/NEEDS REVIEW counts and examples)
5. **Scorecard Table** (all 4 reports side-by-side)
6. **Winner Deep Dive** (strengths, weaknesses, questionable entries)
7. **Missing Rows Analysis** (per-report + missed-by-all-4)
8. **Secondary Accuracy Summary** (1 paragraph)
9. **Recommendations** (prioritized fixes)

---

## Style

- Be direct and numeric
- Use short paragraphs + bullet lists
- When citing examples, show your manual reasoning chain
- Include the key (ASIN/EAN) and exact contradictory tokens observed

---

## Stop Conditions

Stop when:
- Baseline counts computed
- All 4 reports manually analyzed with examples
- Winner selected with numeric justification
- Missing-row analysis delivered
- Recommendations provided

---

## Reproducibility

- Target analysis: Manual row-by-row verification
- Reference date: 2025-12-28
- Time zone: Asia/Dubai (UTC+4)
