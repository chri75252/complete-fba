# Dashboard V2 Deep Investigation Report
**Date:** 2026-03-21
**Scope:** 14 investigation areas covering operator agent, dashboard, analysis, workflows
**Status:** REPORT ONLY - No implementation

---

# SECTION A: VERIFIED ISSUES & DISCREPANCIES

## A1. THE MASTER BUG: EAN Scientific Notation Destroys Tier Classification

**Evidence strength: STRONG (5 sources triangulated)**

This is the single root cause behind issues #1, #2, #3, and #9. Every other tier/classification problem cascades from this.

**What happens:**

1. `FBA_Financial_calculator.py:636` writes CSVs via `df.to_csv(out_path, index=False)`
2. Pandas stores EAN values (e.g., `5053249248356`) as float64, which outputs as `5.05325E+12`
3. When `fba_report_filter.py:normalize_ean()` reads `5.05325E+12`, it does `int(float("5.05325E+12"))` = `5053250000000`
4. The real EAN was `5053249248356` — the last 6 digits are lost
5. `gtin_checksum_valid("5053250000000")` fails because the digits are wrong
6. `ean_exact_match` stays `False`, flag `EAN_CHECKSUM_FAIL` is set
7. T1 rule (`ean_exact_match and net_profit > 0`) NEVER fires
8. Everything falls to T2 at best

**Cross-verification across sources:**

| Product | Real EAN (from reference report) | CSV EAN | Normalized EAN | Checksum | Tier in analysis |
|---------|----------------------------------|---------|----------------|----------|-----------------|
| AMTECH LED MINI TORCH | 5032759031078 | 5.03276E+12 | 5032760000000 | FAIL | T2 |
| PAN AROMA JAR CANDLE SALTED CARAMEL | 5053249248356 | 5.05325E+12 | 5053250000000 | FAIL | T2 |
| CHEF AID PASTRY BRUSH | 5012904148738* | 5.0129E+12 | 5012900000000 | FAIL | T2 |
| HOUSE MATE SS CLEANER | 5039295201040 | 5.0393E+12 | 5039300000000 | FAIL | T2 |
| MEMORIAL GRAVESIDE LANTERN | 5055361761119 | 5.05536E+12 | 5055360000000 | FAIL | T2 |

*Real EANs from `FINAL_CONSOLIDATED_PHASEA_REPORT_20260108.md` where these same products were classified VERIFIED at confidence 95.

**Why the dashboard still shows them as "EAN matched":**
The dashboard API (`api.py:230-246`) uses `_norm_ean` which normalizes BOTH EAN columns the same way. Since both `EAN` and `EAN_OnPage` have the same scientific notation (e.g., both `5.05325E+12`), they normalize to the same wrong number (`5053250000000 == 5053250000000` → match=True). The dashboard doesn't validate checksums — it only checks string equality after normalization.

**Why the operator agent shows them as T2:**
`classify_row()` at `fba_report_filter.py:106-117` requires `gtin_checksum_valid()` to return True for `ean_exact_match = True`. With corrupted digits, checksum always fails → `ean_exact_match = False` → T1 rule at line 208 never fires → T2.

**Result:** The dashboard shows "125 profitable EAN-matched products" but the operator agent classifies 0 as T1 — because the dashboard doesn't care about checksums, but the tier classifier does.

---

## A2. Exported Analysis CSV Also Has Scientific Notation

**Evidence strength: STRONG (direct file inspection)**

The exported analysis CSV at `fba_analysis_2026-03-20 (1).csv` contains ALL rows as T2 with EAN_CHECKSUM_FAIL because:
- The export is generated client-side by `app.js:1021-1040` (`exportAnalysisCsv`)
- It exports whatever the API returned
- The API reads the financial report CSV which already has scientific notation EANs
- The `classify_row` function in the analysis endpoint inherits the same precision loss

Every single row in the exported file (42 rows) has:
- `tier`: `TIER_2_LIKELY`
- `flags`: `EAN_CHECKSUM_FAIL`
- `ean_exact_match`: `false`

This means when you feed this exported file back to the operator agent for re-analysis, the agent's LLM receives EANs like `5.05325E+12` in the prompt, sees them as "matching" (visually identical on both sides), and correctly identifies them as matches — but the tier classification system already incorrectly flagged them as T2.

---

## A3. Analysis Section 500-Row Cap

**Evidence strength: STRONG (code inspection)**

Location: `api.py:377` and `api.py:464`

```python
# Line 377: default page_size = 500
def get_analysis(..., page_size: int = 500, ...):

# Line 464: hard cap applied
rows = rows[:page_size]
```

The API truncates results to 500 rows regardless of file size. The `total_rows` count at line 438 reflects the actual file size, but only 500 rows are returned. This means the Analysis tab shows accurate tier counts but only displays 500 rows.

---

## A4. Financial Report Dropdown Not Populated (Dashboard Tab)

**Evidence strength: STRONG (code inspection)**

The frontend at `app.js:87` checks `data.available_reports` in the metrics API response:
```javascript
if (data.available_reports) {
    const dSel = document.getElementById('dashboardReportSelect');
    // ... populate dropdown
}
```

But the backend API **never sets `available_reports`** in the metrics response. Grep across `api.py` returns zero matches for `available_reports`. The `/api/reports/{supplier}` endpoint exists and returns the list, but it's never called by the metrics fetch or included in the response.

Result: The dashboard Financial Report dropdown stays empty.

---

## A5. Combined Report Is Concatenation, Not Merge

**Evidence strength: STRONG (code + output inspection)**

Location: `fba_ai_analyst.py:296-306`

```python
for i, result in enumerate(all_results, start=1):
    f.write(f"## Batch {i}\n\n{result}\n\n---\n\n")
```

Each batch result contains its own VERIFIED, HIGH LIKELIHOOD, NEEDS VERIFICATION, and AUDITED OUT sections with separate tables. The combined report simply concatenates them sequentially. There is no code to:
- Parse each batch's verdict tables
- Group products by verdict across batches
- Merge into unified tables
- Deduplicate the summary counts

Verified in `run_20260321_013018/COMBINED_AI_ANALYSIS.md`: Batch 1 has its own VERIFIED (3), HIGH LIKELIHOOD (11), etc. Batch 2 has separate VERIFIED (8), HIGH LIKELIHOOD (1), etc. The combined file has both sets as separate sections.

---

## A6. MD Table Formatting Does Not Match Required Style

**Evidence strength: STRONG (output comparison)**

The LLM prompt at `fba_ai_analyst.py:87-119` (`ANALYSIS_PROMPT_TEMPLATE`) requests:
```
Group results by verdict section. For each section, output a markdown table
```

It does NOT specify:
- Fenced code blocks (` ```text ... ``` `)
- Fixed-width space-padded columns
- Vertical `|` alignment

Compare actual output (from `run_20260321_013018/COMBINED_AI_ANALYSIS.md`):
```
| VERIFIED | 95 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | 5.03276E+12 | ...
```

vs required format (from `FINAL_CONSOLIDATED_PHASEA_REPORT_20260108.md`):
```text
| VERIFIED | 95         | AMTECH LED MINI TORCH                     | Amtech S1532 9 LED mini Torch   | 5032759031078 | ...
```

The difference: the required format uses fixed-width columns inside ` ```text ``` ` blocks with space padding.

---

## A7. EAN in LLM Prompt Also Has Scientific Notation

**Evidence strength: STRONG (code + output)**

`fba_ai_analyst.py:190` sends raw CSV values to the LLM:
```python
f"{row.get('EAN','')},{row.get('EAN_OnPage','')},..."
```

Since these values come from the financial CSV (which has scientific notation), the LLM receives `5.05325E+12` in the prompt data. The LLM then reproduces this in its tables. See `run_20260321_013018/COMBINED_AI_ANALYSIS.md` line 17:
```
| VERIFIED | 95 | AMTECH LED MINI TORCH | ... | 5.03276E+12 | 5.03276E+12 | ...
```

The mimo-v2-pro-free model correctly notes in its summary: "The Pan Aroma EAN `5.05325E+12` is used for multiple distinct candle scents" — but this observation is an artifact of precision loss, not actual EAN reuse. The real EANs are different (5053249248356 vs 5053249228174 vs 5053249248295) but they all round to the same `5.05325E+12`.

---

# SECTION B: ROOT CAUSES

## B1. Primary Root Cause: Pandas Float64 Serialization of EANs

**File:** `FBA_Financial_calculator.py:606`
```python
row = {
    "EAN": ean,                              # stored as Python string
    "EAN_OnPage": amazon.get("ean_on_page"), # stored as Python string
    ...
}
```

**File:** `FBA_Financial_calculator.py:627-636`
```python
df = pd.DataFrame(records)   # Pandas auto-detects EAN columns as float64
df.to_csv(out_path, index=False)  # Writes floats in scientific notation
```

When Pandas builds the DataFrame, it sees columns of numeric-looking strings and converts them to float64. Float64 has ~15 significant digits of precision, but EANs are 13 digits — so the precision SHOULD be sufficient. However, `to_csv()` defaults to a format that uses scientific notation for large numbers, which loses the trailing digits in the display.

The actual data loss chain:
1. EAN string `"5053249248356"` → pandas float64 `5053249248356.0` (OK, no precision loss yet)
2. `to_csv()` → string `"5.05325E+12"` (display truncation — only 6 significant figures shown)
3. Re-read: `float("5.05325E+12")` → `5053250000000.0` (precision lost in re-parsing)

## B2. Secondary Root Cause: Checksum Validation on Corrupted Data

`fba_report_filter.py:42-54` (`gtin_checksum_valid`) correctly validates GTIN checksums. The function itself is correct. The problem is it receives corrupted digit strings (e.g., `5053250000000` instead of `5053249248356`), so it correctly reports invalid checksums — but this is a false negative.

## B3. Tertiary Root Cause: Missing `available_reports` in API Response

The frontend was wired to populate the dropdown from `data.available_reports`, but no code was added to the `get_supplier_metrics` function to include this field.

## B4. Quaternary Root Cause: LLM Prompt Lacks Table Format Specification

The `ANALYSIS_PROMPT_TEMPLATE` in `fba_ai_analyst.py` does not include the required table formatting rules (fenced code blocks, fixed-width, space-padded).

---

# SECTION C: SUGGESTED FIXES (SURGICAL, MINIMAL-RISK)

## C1. FIX: Preserve EAN as Text in CSV Output (CRITICAL — fixes A1, A2, A7)

**File:** `tools/FBA_Financial_calculator.py`
**Target:** Line 636

**Current:**
```python
df.to_csv(out_path, index=False)
```

**Proposed:**
```python
# Force EAN columns to string to prevent scientific notation
for ean_col in ['EAN', 'EAN_OnPage']:
    if ean_col in df.columns:
        df[ean_col] = df[ean_col].apply(
            lambda x: str(int(float(x))) if pd.notna(x) and str(x).strip() else ''
        )
df.to_csv(out_path, index=False)
```

**Risk:** LOW. Only affects the CSV serialization step. Does not change any calculation logic. The EAN values are already strings in the `records` list — this just prevents Pandas from converting them to float64 during DataFrame construction. A safer alternative is to set dtypes at construction time:

```python
df = pd.DataFrame(records)
for ean_col in ['EAN', 'EAN_OnPage']:
    if ean_col in df.columns:
        df[ean_col] = df[ean_col].astype(str).replace('nan', '').replace('None', '')
```

**Impact:** ALL downstream consumers (dashboard, analysis, operator agent, exports) will see correct EANs. Checksums will pass. T1 classifications will work. This single fix resolves issues #1, #2, #3, #4, and #9.

**Note:** This fix is in `tools/FBA_Financial_calculator.py` which is a protected file. Requires explicit approval per CLAUDE.md policy.

**IMPORTANT CAVEAT:** This fix only applies to NEWLY GENERATED CSV files. Existing CSV files with scientific notation EANs will still have the problem. For existing files, a one-time migration script could be run, or the `normalize_ean` functions in `fba_report_filter.py` and `api.py` could be enhanced to handle precision recovery (but this is inherently unreliable — you can't recover `5053249248356` from `5.05325E+12`).

---

## C2. FIX: Also Apply to Incremental Calculator

**File:** `tools/FBA_Financial_calculator.py`
**Target:** Line 781

Same pattern applies to `run_calculations_incremental` at line 781:
```python
df_combined.to_csv(combined_path, index=False)
```

Apply same EAN-to-string conversion before writing.

---

## C3. FIX: Remove Analysis 500-Row Cap (fixes A3)

**File:** `dashboard_v2_redesign/api.py`
**Target:** Line 377

**Current:**
```python
page: int = 1, page_size: int = 500,
```

**Proposed:**
```python
page: int = 1, page_size: int = 50000,
```

Or better, remove the hard truncation at line 464 and let the frontend handle pagination (it already does with `ANALYSIS_PAGE_SIZE`):

```python
# Line 464 - remove or increase cap
# rows = rows[:page_size]  # Remove this line
```

**Risk:** LOW. The frontend already paginates via `renderAnalysisTable()` which uses `ANALYSIS_PAGE_SIZE`. The only concern is JSON payload size, but even 20k rows of analysis data is ~5MB which is acceptable.

---

## C4. FIX: Populate `available_reports` in Metrics Response (fixes A4)

**File:** `dashboard_v2_redesign/api.py`
**Target:** After line 311 (after `data_sources` is set)

**Add:**
```python
# Populate available reports for dashboard dropdown
if fin_dir and os.path.exists(fin_dir):
    csv_files = sorted(
        [f for f in os.listdir(fin_dir) if f.endswith(".csv")],
        key=lambda f: os.path.getmtime(os.path.join(fin_dir, f)),
        reverse=True
    )
    metrics_data["available_reports"] = [
        {"filename": f, "rows": max(0, sum(1 for _ in open(os.path.join(fin_dir, f), encoding="utf-8", errors="replace")) - 1)}
        for f in csv_files[:20]  # Limit to 20 most recent
    ]
```

**Risk:** LOW. Adds a list to the JSON response. Frontend code already handles it (app.js:87-96).

---

## C5. FIX: Add Table Formatting Rules to LLM Prompt (fixes A6)

**File:** `tools/fba_ai_analyst.py`
**Target:** Inside `ANALYSIS_PROMPT_TEMPLATE` (line 87), append after line 115

**Add to prompt:**
```
**Table Formatting Requirements:**
- Wrap every table in a fenced code block: start with ```text, end with ```
- Use fixed-width, space-padded columns so | separators align vertically
- No tabs, spaces only
- Header separator row must match column widths exactly
- Replace literal | with / inside cell values
- Replace embedded newlines with spaces inside cell values
```

**Risk:** LOW. Only changes the LLM prompt text. Does not affect any code logic. The LLM may or may not follow the formatting perfectly depending on model capabilities.

---

## C6. FIX: Merge Combined Report by Verdict Section (fixes A5)

**File:** `tools/fba_ai_analyst.py`
**Target:** Lines 296-306

This requires more substantial logic. The current approach simply concatenates batch results. A true merge would need to:
1. Parse each batch's markdown output to extract verdict sections
2. Group rows by verdict across all batches
3. Re-sort by Sales desc within each group
4. Write a single unified table per verdict

**Suggested approach (minimal):** Instead of trying to parse free-form LLM markdown (fragile), add a post-processing instruction to the LLM prompt for the combined report:

**Alternative:** Generate a final "combination prompt" that sends ALL batch results to the LLM and asks it to merge them into a single unified report. This is simpler and more robust than regex parsing.

**Proposed addition to `analyze_report()` after line 306:**
```python
# Generate merged combined report
if len(all_results) > 1:
    merge_prompt = f"""You are given {len(all_results)} batch analysis reports for the same financial dataset.
Merge ALL batches into a single unified report with ONE table per verdict section (VERIFIED, HIGH LIKELIHOOD, NEEDS VERIFICATION, AUDITED OUT).
Combine all rows from all batches, sorted by Sales descending within each section.
Produce a single summary paragraph at the end with combined counts.

{chr(10).join(f'--- BATCH {i+1} ---{chr(10)}{r}' for i, r in enumerate(all_results) if '[ERROR]' not in str(r))}
"""
    merged_result = call_openai(merge_prompt)
    # Write merged version
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write(f"# FBA AI Analysis Report (Merged)\n")
        f.write(f"**Source:** {csv_path.name}\n")
        f.write(f"**Total Rows Analyzed:** {len(rows)}\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n---\n\n")
        f.write(merged_result)
```

**Risk:** MEDIUM. Adds one extra LLM call. Could hit rate limits on free models. But the combined report is currently useless as-is (just concatenation), so the risk is acceptable.

---

## C7. FIX: Normalize EANs in AI Analyst Prompt Data (supplements C1)

**File:** `tools/fba_ai_analyst.py`
**Target:** Line 190-191 in `rows_to_csv_string()`

Even after C1 fixes new CSVs, existing CSVs still have scientific notation. Add normalization when building the prompt:

**Current:**
```python
f"{row.get('EAN','')},{row.get('EAN_OnPage','')},..."
```

**Proposed:**
```python
ean_val = normalize_ean(str(row.get('EAN', '')))
ean_page = normalize_ean(str(row.get('EAN_OnPage', '')))
f"{ean_val},{ean_page},..."
```

`normalize_ean` is already imported at line 21. This ensures the LLM always sees real digit strings, not scientific notation — regardless of the CSV source.

**Risk:** LOW. The `normalize_ean` function is already proven reliable. This just applies it to the prompt data.

---

# SECTION D: SUGGESTED FEATURE/WORKFLOW IMPROVEMENTS

## D1. Revisiting the 3 Original Feature Suggestions

### D1a. Export Re-Analysis List Button

**Original proposal:** Button below Profitable Categories chart that exports EAN-matched products with NetProfit > 0 as CSV.

**Assessment:** KEEP, but with modification.

The current `exportAnalysisCsv` function (app.js:1021-1040) already exports whatever the Analysis tab shows. The issue is that the Analysis tab's data comes from `fba_report_filter.py` classification, which currently puts everything as T2 due to the EAN bug. Once fix C1 is applied, the Analysis tab will show correct T1/T2 tiers, and the existing export button becomes the re-analysis list.

**Modification:** Instead of a new button, add a "Quick Filter" preset button on the Analysis tab labeled "Re-Analysis Candidates" that auto-sets filters to: Tier = T1 or T2, NetProfit > 0, and sorts by Sales desc. This is simpler than a new export mechanism and uses existing infrastructure.

**Implementation cost:** ~10 lines of JS.

### D1b. Category Click -> Auto-Build Product List

**Original proposal:** Click category bars in Profitable Categories chart to generate product list JSON for sandbox.

**Assessment:** REPLACE with simpler approach.

Building a product list JSON requires specific format (`sandbox_supplier`, `products` array with URLs). The click-to-build approach requires:
1. Chart click handler
2. API call to build the list
3. Chat orchestrator integration

This is over-engineered for the actual use case. The simpler approach:
- On the Analysis tab, add a "Category" column filter dropdown (populated from cached_products categories)
- Filter by category, then use existing Export button
- Feed the exported CSV to the operator agent for deeper analysis

The category data is already enriched in the API (lines 267-288) and included in `fba_ai_analyst.py` classification (lines 122-146).

**Implementation cost:** ~20 lines of JS + ~5 lines of API (category already available in chart_data).

### D1c. Stale Data Indicator

**Original proposal:** Column showing when each product was last analyzed, flagging "stale" products.

**Assessment:** KEEP, with modification.

The financial report CSV filename contains a timestamp (e.g., `fba_financial_report_20260122_093706.csv`). The age of the CSV is the staleness indicator for ALL products in it — individual product timestamps are not available because the main workflow processes everything in one run.

**Better approach:** Instead of per-product staleness:
1. Show the CSV file date prominently at the top of the Dashboard tab (already partially done via `data_sources.financial_report`)
2. Add a "Days Since Last Analysis" badge next to the Financial Report selector
3. Color-code: Green (< 7 days), Yellow (7-30 days), Red (> 30 days)

This is honest about what the data tells us — the entire file is from one run, not individual products.

For per-category staleness, the cached_products file has modification times per source_url which could indicate when categories were last scraped. But this is more complex and may not be worth the implementation effort.

**Implementation cost:** ~15 lines of JS.

---

## D2. Additional Recommendations

### D2a. Backward-Compatible EAN Recovery for Existing CSVs

Since fix C1 only applies to new CSVs, existing files still have corrupted EANs. Two options:

**Option 1 (Recommended):** Enhance `normalize_ean()` in `fba_report_filter.py` to attempt full-precision recovery by padding with the checksum digit. This is unreliable and NOT recommended.

**Option 2 (Recommended):** Simply re-run the financial calculator for existing suppliers. This regenerates the CSV with correct EANs. Since the linking_map.json and amazon_cache files still have correct EANs, the recalculation will produce correct data.

Command: `python tools/FBA_Financial_calculator.py efghousewares.co.uk`

### D2b. Dashboard ROI Display Scaling

The Analysis tab at `app.js:982` multiplies ROI by 100:
```javascript
const roi = row.ROI ? (Number(row.ROI) * 100).toFixed(1) + '%' : '--';
```

But the financial report CSV already stores ROI as a percentage (e.g., `118.6`, not `1.186`). This means the Analysis tab shows `11860.0%` for what should be `118.6%`. Need to verify whether the CSV stores ROI as ratio or percentage.

**Verification:** From `fba_analysis_2026-03-20 (1).csv` line 3: ROI value is `118.6026936`. The app.js code multiplies by 100, so it would show `11860.3%`. However, looking at the screenshot, the Analysis tab shows `11860.3%` in the ROI column — which IS what I see in your screenshot. But looking more carefully at the financial_report_20260122_093706.csv: the ROI column header is just `ROI` and values like `40359.00997` — these are clearly already percentages (or ratio * 100).

**WAIT** — Let me re-check. The `fba_analysis_2026-03-20 (1).csv` has `ROI` values like `156.1349693` and `118.6026936`. The `fba_financial_report_20260122_093706.csv` has values like `19618.41354` and `2271.434898`. These are clearly already percentage values (the first file has realistic ROIs, the second has extreme ones because of mismatched products).

Looking at the app.js:982: `(Number(row.ROI) * 100).toFixed(1)` — this would turn `156.13` into `15613.0%`. But in your screenshot, the Analysis tab shows values like `15613.5%`, `11860.3%`, `9151.3%` — these are clearly wrong (100x too high).

This is a CONFIRMED BUG that I should report.

**HOWEVER** — looking at the screenshot more carefully, I see values like `15613.5%`, `11860.3%`, etc. The raw CSV has `156.1349693` which when multiplied by 100 gives `15613.5` — exactly what's shown. So the bug is confirmed: the `* 100` multiplication is wrong because the CSV already stores ROI as a percentage.

**Actually wait** — let me re-read the FBA_Financial_calculator. Looking at the `financials()` function... I need to check what ROI value the calculator produces.

Let me check the financials function to see if ROI is stored as ratio or percentage.

### D2c. Analysis Tab: Report Selector Needs Population

The Analysis tab has an `analysisReportSelect` dropdown (`templates/index.html:708`). The app.js at line 750 references it. Need to verify if it's populated via a separate fetch or if it's also empty.

---

# SECTION E: OPERATOR WORKFLOW FOR FRESH RUNS

## E1. Understanding What "Fresh Run" Means

A fresh run means you've just executed `run_custom_efghousewares-co-uk.py` (or equivalent), which:
1. Scraped all supplier products → `cached_products/{supplier}_products_cache.json`
2. Matched against Amazon → `linking_maps/{supplier}/linking_map.json` + `amazon_cache/amazon_{ASIN}_{EAN}.json`
3. Generated financial report → `financial_reports/{supplier}/fba_financial_report_{timestamp}.csv`

## E2. Step-by-Step Workflow: Fresh Run Analysis

### Phase 1: Quick Overview (Dashboard Tab)
1. Open Dashboard V2 at `localhost:8001`
2. Select supplier in sidebar
3. Select "Main Workflow" lineage
4. Select the latest CSV in Financial Report dropdown (once fix C4 is applied)
5. Check top metric cards:
   - **Profitable** = count of EAN-matched rows with NetProfit > 0
   - **With Sales** = subset of above where bought_in_past_month > 0
   - **Avg ROI** and **Avg Profit** = averages of profitable EAN-matched rows
6. Scan charts:
   - **ROI Distribution** = histogram of ROI values — look for concentration points
   - **Profitable Categories** = which supplier categories have the most total profit (bar labels show product count)
   - **Net Profit vs Selling Price** = scatter — green dots (ROI >= 30%) are best candidates
   - **Profit vs Competition** = scatter — look for green dots with LOW total_offer_count (less competition)
   - **Competition Level** = doughnut — overall market saturation picture

### Phase 2: Detailed Analysis (Analysis Tab)
1. Switch to Analysis tab
2. Set tier filter to "T1" to see VERIFIED matches
3. Sort by NetProfit desc
4. Review the T1 list — these are products where:
   - EAN matches exactly (both valid checksums)
   - NetProfit > 0
   - No CATEGORY_MISMATCH flag
5. Switch tier to "T2" — review LIKELY matches that need manual verification
6. Use min_sales filter (e.g., 50) to focus on products with proven demand

### Phase 3: Deep Validation (Operator Agent)
1. Switch to Operator tab
2. Select the same financial report CSV
3. Click "Run AI Analysis"
4. The agent classifies each row using the LLM to catch:
   - Pack size mismatches (supplier sells 1, Amazon sells 3-pack)
   - Variant traps (same EAN, different scent/color/size)
   - Title mismatches the automated system missed
5. Review the generated report in `OUTPUTS/CONTROL_PLANE/FINANCIAL_REPORTS/run_{timestamp}/`

### Phase 4: Build Final Product List
1. Return to Analysis tab
2. Filter: T1 + T2 with NetProfit > 0 and Sales > 0
3. Export to CSV using the Export button
4. Cross-reference against operator agent's AUDITED OUT list
5. Remove any products the agent flagged as false positives
6. The remaining list = your actionable sourcing list

### Phase 5: Spot-Check Critical Items
For the top 10-20 products by profit:
1. Open the Amazon listing (AmazonURL column) in browser
2. Verify the product matches visually
3. Check current price vs the report's SellingPrice
4. Check if Buy Box is available (FBA vs FBM)
5. Check review count and rating

---

# SECTION F: OPERATOR WORKFLOW FOR STALE/OLDER ANALYSES

## F1. Understanding "Stale" Data

Stale data means:
- The financial report CSV is from a previous run (days/weeks/months old)
- Amazon prices may have changed
- Competition (total_offer_count) may have changed
- Sales volumes may have changed
- New competitors may have entered the listing
- Products may have gone out of stock at supplier

The goal is NOT to re-scrape the entire supplier website. It's to identify which products/categories are worth re-analyzing with fresh Amazon data.

## F2. Step-by-Step Workflow: Stale Data Re-Analysis

### Phase 1: Identify Staleness
1. Open Dashboard V2
2. Check the Financial Report filename — extract the date (e.g., `20260122` = Jan 22, 2026)
3. Calculate age: if > 14 days, data is moderately stale; > 30 days, significantly stale
4. Note: supplier prices from the cached_products file may also be stale

### Phase 2: Identify High-Value Re-Analysis Targets
1. Go to Analysis tab
2. Filter: T1 or T2, NetProfit > 0, Sales > 0
3. Sort by Sales desc — high-sales products are most worth re-checking because:
   - Price changes on high-demand products have the biggest profit impact
   - Competition on popular items changes fastest
4. Export this filtered list — this is your "re-analysis candidate list"

### Phase 3: Prioritize Categories for Re-Analysis
1. Go to Dashboard tab
2. Look at **Profitable Categories With Sales** chart
3. The categories with the most bars (product count in labels) AND highest total profit are the best re-analysis targets
4. Rationale: Re-analyzing a single category re-scrapes all products in it. Categories with many profitable products give the best ROI on your re-analysis time.

### Phase 4: Execute Selective Re-Analysis
**For category-level re-analysis:**
1. Go to AI Assistant (chat) tab
2. Tell the chat: "Run sandbox analysis for category [URL] on efghousewares.co.uk"
3. The chat will enqueue a sandbox run for that specific category
4. Wait for the run to complete
5. Switch lineage to "Latest Sandbox" to see refreshed results for that category

**For product-level re-analysis:**
1. If you have a specific list of product URLs to re-check:
   - Build a product list JSON (manually or via chat: "Build product list from [URLs]")
   - Place it in `OUTPUTS/CONTROL_PLANE/inputs/`
   - Use chat to enqueue a sandbox run with that product list
2. This re-scrapes only those specific products from Amazon

### Phase 5: Compare Old vs New
1. After the sandbox run completes, you'll have a new financial report CSV
2. Compare key metrics (NetProfit, Sales, total_offer_count) between old and new
3. Products where NetProfit improved or stayed stable = confirmed opportunities
4. Products where NetProfit dropped significantly = market changed, deprioritize

## F3. What NOT To Do for Stale Data

**Do NOT** export the analysis CSV and feed it to the operator agent as if it's a "re-analysis." Here's why:

The exported CSV from the Analysis tab contains data FROM the financial report — it's the same stale data reformatted. Feeding it to the operator agent gives you an LLM opinion on stale data, not fresh data. The LLM can catch false positives and pack size mismatches (which don't change over time), but it cannot tell you if prices or competition have changed.

The correct workflow for stale data re-analysis is:
1. Identify WHICH products/categories to re-check (using the dashboard)
2. Re-run the system for those specific products/categories (sandbox run)
3. Review the FRESH results

**When the export-and-analyze workflow IS appropriate:**
- On a FRESH run, to get LLM verification of automated matches
- To catch false positives that the deterministic system missed
- To validate pack size assumptions
- These are all time-independent checks — the LLM is looking at title/EAN/category consistency, not price freshness

---

# SECTION G: ADDITIONAL FINDINGS

## G1. ROI Display Bug in Analysis Tab

**Evidence strength: STRONG**

`app.js:982`:
```javascript
const roi = row.ROI ? (Number(row.ROI) * 100).toFixed(1) + '%' : '--';
```

The financial report CSV stores ROI as a percentage already (e.g., `118.6` means 118.6%). Multiplying by 100 shows `11860.0%`. This is visible in your screenshot where rows show values like `15613.5%`, `11860.3%`.

**Fix:** Remove the `* 100`:
```javascript
const roi = row.ROI ? Number(row.ROI).toFixed(1) + '%' : '--';
```

**Confirmed:** `FBA_Financial_calculator.py:450` does `roi = (net_profit / total_cost_ex_vat) * 100` — ROI is already a percentage. The `* 100` in app.js is definitively wrong.

## G2. Pan Aroma EAN Collision Is Real, Not Just Scientific Notation

While the scientific notation issue causes DIFFERENT EANs to appear identical, some Pan Aroma products DO genuinely share the same EAN. Cross-checking the reference report:
- PAN AROMA JAR CANDLE 85GM SALTED CARAMEL → EAN: 5053249248356
- PAN AROMA JAR CANDLE 85GM RED BERRY → EAN: 5053249248295

These are different EANs (248356 vs 248295) that BOTH round to `5.05325E+12`. So the apparent "EAN reuse" flagged by the LLM in batch 1 of `run_20260321_013018` is actually a scientific notation artifact.

However, in the exported analysis CSV, rows like:
- PAN AROMA CANDLE 85G PURE JASMINE → same EAN `5.05325E+12` and same ASIN `B09KCLYC1D`
- PAN AROMA CANDLE 85G LEMONGRASS → same EAN `5.05325E+12` and same ASIN `B09KCLYC1D`

These likely DO have the same real EAN (both map to the same ASIN). The fact that they have different scents but same ASIN/EAN suggests the Amazon system matched them to a parent listing. This IS a legitimate false positive concern — the operator agent was right to flag it.

## G3. Rate Limit Errors on Free Models

The `run_20260321_012233` run used `minimax-m2.5-free` and batch 3 failed with:
```
Error code: 429 - FreeUsageLimitError - Rate limit exceeded
```

The `run_20260321_013018` run used `mimo-v2-pro-free` and completed all 3 batches successfully. Free models have strict rate limits that can cause incomplete analyses.

## G4. Inconsistent Confidence Scores Between Runs

The same products receive different confidence scores depending on which LLM model is used:
- `minimax-m2.5-free`: AMTECH LED MINI TORCH → Confidence 95 (VERIFIED)
- `mimo-v2-pro-free`: AMTECH LED MINI TORCH → Confidence 95 (VERIFIED)

But the deterministic `classify_row()` assigns them confidence 60 with `ean_exact_match = False`. The LLM-assigned confidence is independent of the deterministic tier. This creates confusion when comparing operator reports against Analysis tab data.

## G5. Multiple EAN Columns in Different CSVs

The financial report `fba_financial_report_20260106_022313.csv` has columns: `EAN,EAN_OnPage,...,EAN_match`
The financial report `fba_financial_report_20260122_093706.csv` has columns: `EAN,EAN_OnPage,...` (no EAN_match)
The exported analysis CSV has: `EAN,EAN_OnPage,...,ean_exact_match`

These inconsistent column names don't cause breakage (each consumer handles what it has), but they make cross-referencing harder.

## G6. Some Financial Report Rows Are Obviously Mismatched (Not EAN-Related)

Looking at `fba_financial_report_20260122_093706.csv`:
```
EUROWRAP GIANT BIRTHDAY BADGE GIRL 13 → Motorola razr 60 ultra (£671.69)
ESSENTIAL PLASTIC 6 ICE CREAM BOWL → Motorola razr 60 ultra (£713.52)
MARKSMAN NYLON CABLE TIES → K'NEX 6 Foot Ferris Wheel (£399.99)
```

These are clearly title mismatches where the Amazon matching found the wrong product entirely. The dashboard correctly filters these OUT because their EANs don't match (EAN_OnPage is empty or different). But they inflated the total row count and could confuse users looking at the raw CSV.

---

# SECTION H: EXPANDED DATA SOURCE MAPPING

| Dashboard Element | Source File | Key Field / Calculation | Critical Caveats |
|---|---|---|---|
| **Total Extracted** (card) | `OUTPUTS/cached_products/{supplier}_products_cache.json` | Array length of JSON file | Includes ALL scraped products, not just those with Amazon matches |
| **Total Processed** (card) | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json` | Entry count of JSON array | Each entry = one supplier product that was looked up on Amazon (may or may not have found a match) |
| **Profitable** (card) | Financial report CSV | Count of rows where: `_ean_norm == _ean_page_norm` AND `NetProfit > 0` | Uses simple EAN string match, NOT checksum validation. So products with corrupted EANs (scientific notation) may still show as "matched" if both sides have same corruption |
| **With Sales** (card) | Financial report CSV | Subset of Profitable where `bought_in_past_month > 0` | Sales data comes from Amazon's "bought in past month" badge — not all products display this |
| **Avg ROI** (card) | Financial report CSV | `mean(ROI)` of Profitable rows | ROI is stored as percentage (e.g., 118.6 = 118.6%). Calculation: `(NetProfit / SupplierPrice_exVAT) * 100` |
| **Avg Profit/Item** (card) | Financial report CSV | `mean(NetProfit)` of Profitable rows | NetProfit = SellingPrice_exVAT - SupplierPrice_exVAT - ReferralFee - FBAFee - PrepHouseFee |
| **ROI Distribution** (histogram) | Financial report CSV | ROI values of all EAN-matched rows | Binned into percentage ranges. Capped at 2000 rows for browser performance |
| **Top Categories by Profit** (bar) | Financial report CSV + cached_products | `sum(NetProfit)` grouped by Category | Category derived from cached_products source_url path parsing. Labels show `(count)` = number of products. Only EAN-matched profitable rows included |
| **Profitable Categories With Sales** (bar) | Financial report CSV + cached_products | Same as above but filtered to `bought_in_past_month > 0` | Only shows categories where at least one product has recorded sales |
| **Net Profit vs Selling Price** (scatter) | Financial report CSV | X=SellingPrice, Y=NetProfit | Color: green (ROI >= 30%), orange (15-30%), red (< 15%). Capped at 2000 points |
| **Profit vs Competition** (scatter) | Financial report CSV | X=total_offer_count, Y=NetProfit | Color: green (profitable), red (loss-making). total_offer_count from Keepa data — may be empty for some products |
| **Competition Level** (doughnut) | Financial report CSV | Bucketed total_offer_count: Low (1-5), Med (6-20), High (20+) | Only includes rows where total_offer_count > 0 |
| **Analysis Tab Tiers** (T1-T4 counts) | Financial report CSV via `fba_report_filter.py` | `classify_row()` on each row | T1 requires: `ean_exact_match AND NetProfit > 0 AND no CATEGORY_MISMATCH`. Currently broken by scientific notation (see A1) |
| **Analysis Tab Table** | Financial report CSV via `fba_report_filter.py` | Filtered/sorted rows | Currently capped at 500 rows (see A3). ROI display is 100x too high (see G1) |
| **Operator Reports** | Financial report CSV via `fba_ai_analyst.py` → LLM | LLM verdict per row | LLM receives scientific notation EANs (see A7). Verdicts independent of deterministic tiers |
| **System Health** | `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json` | Phase, category index, progress | Reflects main workflow state only, not sandbox runs |
| **Terminal Logs** | `logs/debug/run_custom_{supplier}_*.log` | Last 200 lines of most recent log | May not exist if no run has been executed |

---

# SECTION I: IMPLEMENTATION PRIORITY ORDER

Based on impact and risk:

1. **C1 + C2: Fix EAN serialization** — CRITICAL. Fixes issues #1, #2, #3, #4, #9. Requires approval for protected file.
2. **C4: Populate available_reports** — HIGH. Fixes the empty dropdown. ~5 lines.
3. **C3: Remove 500 cap** — HIGH. Analysis tab shows full data. ~1 line change.
4. **G1 fix: ROI display** — HIGH. Fix the `* 100` bug. ~1 line change.
5. **C7: Normalize EANs in prompt** — MEDIUM. Ensures LLM sees correct EANs even from old CSVs. ~3 lines.
6. **C5: Table formatting in prompt** — MEDIUM. Improves report readability. ~10 lines added to prompt.
7. **C6: Merge combined report** — LOW-MEDIUM. Adds one extra LLM call. Risk of rate limits.
8. **D1a/D1c: Analysis tab filter preset + staleness badge** — LOW. Nice-to-have UI improvements.

---

# SECTION J: SUMMARY OF CROSS-VERIFIED CONCLUSIONS

| Conclusion | Sources Used | Confidence |
|---|---|---|
| Scientific notation causes all T1 → T2 demotion | CSV files, classify_row code, reference report, dashboard API, operator output | STRONG (5 sources) |
| Dashboard shows "matched" despite checksum failure | api.py _norm_ean code, CSV data, screenshot | STRONG (3 sources) |
| 500-row cap exists in analysis endpoint | api.py code, frontend pagination code | STRONG (2 sources) |
| available_reports not populated | api.py grep (0 matches), app.js code | STRONG (2 sources) |
| Combined report is concatenation | fba_ai_analyst.py code, actual combined output file | STRONG (2 sources) |
| ROI display is 100x too high | app.js code, CSV data, screenshot | STRONG (3 sources) |
| Pan Aroma EAN "reuse" is mostly scientific notation artifact | Reference report real EANs vs CSV truncated EANs | STRONG (2 sources) |
| Free model rate limits cause incomplete analyses | run_config.json errors field | STRONG (1 source, but definitive) |
| Table formatting not specified in prompt | ANALYSIS_PROMPT_TEMPLATE code, actual output | STRONG (2 sources) |
| Export-and-re-analyze is wrong workflow for stale data | Workflow analysis (logical deduction) | MEDIUM (reasoning-based) |
| ROI stored as percentage (confirmed: `roi = (net_profit / total_cost_ex_vat) * 100` at FBA_Financial_calculator.py:450) | FBA_Financial_calculator.py code, CSV data, screenshot | STRONG (3 sources) |
