# Full Test Plan — Dashboard V2 + All Fixes
**Date:** 2026-03-22
**Pre-requisite:** Restart uvicorn before any test — `uvicorn dashboard_v2_redesign.api:app --port 8001 --reload`
**Browser:** `http://127.0.0.1:8001`

---

## HOW TO USE THIS PLAN

- Work through each section top-to-bottom.
- Each check has an **Expected** column — if what you see matches, mark PASS.
- **Triangulation** sections require verifying the same fact from 2–3 independent sources before marking PASS.
- Section 7 (Main Workflow) requires the worker running: `python -m control_plane worker`

---

## SECTION 1 — DASHBOARD TAB: Sidebar & Config

| # | Action | Expected |
|---|--------|----------|
| 1 | Open `http://127.0.0.1:8001` | Dashboard tab loads; left sidebar shows: Supplier Source, Data Lineage, Financial Report, Auto Refresh, CONNECTED indicator |
| 2 | Supplier Source dropdown | Shows at least: `efghousewares.co.uk`, `poundwholesale.co.uk`, `angelwholesale.co.uk`, `clearance-king.co.uk` |
| 3 | Select `efghousewares.co.uk` → Data Lineage | Shows `Main Workflow` and any sandbox options |
| 4 | Select `Main Workflow` lineage | Dashboard loads metrics for efghousewares main workflow CSV |
| 5 | Financial Report dropdown (sidebar) | Dropdown is **populated** with CSV filenames (e.g. `fba_financial_report_efghousewares-co-uk_20260321_062255.csv`) — NOT empty |
| 6 | Select a different CSV from dropdown | Metrics cards and charts refresh to reflect the selected CSV |
| 7 | Select `— latest —` in dropdown | Dashboard reverts to most recent CSV |

---

## SECTION 2 — DASHBOARD TAB: Metric Cards

Use `efghousewares.co.uk` / Main Workflow / latest CSV for this section.

| # | What to check | Expected |
|---|--------------|----------|
| 8 | "Profitable" card | Shows a number > 0 (EAN-matched rows where NetProfit > 0) |
| 9 | "With Sales" card | Shows a number ≤ Profitable count (products with sales > 0) |
| 10 | "Avg ROI" card | Shows a realistic percentage (e.g. `87.4%`) — NOT `8740%` or `—` |
| 11 | "Avg Profit/Item" card | Shows a GBP value (e.g. `£3.24`) |
| 12 | "Total Extracted" card | Matches `OUTPUTS/cached_products/efghousewares-co-uk_products_cache.json` array length (~22,503) |
| 13 | "Total Processed" card | Matches `OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk/linking_map.json` entry count (~24,986) |

**Triangulation check 2A — Profitable count:**
- Source 1: "Profitable" card value (e.g. 125)
- Source 2: Open Analysis tab → filter Tier = T1+T2 → count rows with NetProfit > 0
- Source 3: Open the CSV directly (e.g. in Excel) → filter EAN == EAN_OnPage AND NetProfit > 0 → count
- All 3 should agree ± a few rows (small delta acceptable due to EAN normalization differences).

---

## SECTION 3 — DASHBOARD TAB: Charts

| # | Chart | What to check | Expected |
|---|-------|--------------|----------|
| 14 | ROI Distribution histogram | Bars visible; X-axis shows `%` labels (e.g. `48%`, `96%`) | NOT empty |
| 15 | Profitable Categories (horizontal bar) | Each bar label shows `CategoryName (N)` format where N = product count | e.g. `Disposable Tableware (16)` |
| 16 | Profitable Categories tooltip | Hover a bar → tooltip shows total profit and product count | e.g. `£48.65 from 16 products` |
| 17 | Net Profit vs Selling Price scatter | Points visible; color legend below chart | Green = ROI ≥ 30%, orange = 15-30%, red = < 15% |
| 18 | Profit vs Competition scatter | X-axis label = `Total Offer Count` (NOT `FBA Seller Count`) | Points cluster toward left (low competition) |
| 19 | Profit vs Competition color legend | Green dot = Profitable, red dot = Loss-making | Visible below chart |
| 20 | Profitable Categories With Sales | Bars visible; bar labels include `(count)` | e.g. `Sponge Scourer (9)` |
| 21 | Competition Level doughnut | Three segments visible: Low 1-5 / Med 6-20 / High 20+ with counts | e.g. `Low 1-5 (75)` |
| 22 | All charts — switch to poundwholesale | Charts refresh with different data | No blank charts, no JS errors in console |

---

## SECTION 4 — DASHBOARD TAB: Data Sources Panel

| # | Action | Expected |
|---|--------|----------|
| 23 | Scroll to bottom of Dashboard tab | Collapsible "Data Sources" section visible |
| 24 | Expand Data Sources | Table shows file paths for: cached_products, linking_map, financial_report, processing_state, log_file |
| 25 | Click each path listed | Paths are absolute and correct for the selected supplier |

---

## SECTION 5 — WORKFLOWS TAB

| # | Action | Expected |
|---|--------|----------|
| 26 | Click "Workflows" in left nav | Page loads — two side-by-side cards visible |
| 27 | Left card | Heading: "Fresh Run — Identify Profitable & Sellable Products" in green |
| 28 | Right card | Heading: "Stale Data — Identify Categories & Products to Re-Analyze" in blue/purple |
| 29 | Left card content | 5 numbered phases visible, each with sub-steps |
| 30 | Right card content | 5 numbered phases visible; red warning box at bottom starting with "Do NOT" |
| 31 | Both cards readable without scroll | Content fits within viewport |

---

## SECTION 6 — OPERATOR TAB

**Pre-condition:** Have efghousewares latest CSV selected.

| # | Action | Expected |
|---|--------|----------|
| 32 | Click "Operator" in nav | Operator page loads; "Financial Report" dropdown visible |
| 33 | Select the efghousewares latest CSV | Report selected without error |
| 34 | Click "Run Analysis" (or equivalent) | Progress indicator appears; no crash |
| 35 | Wait for completion | New folder created at `OUTPUTS/CONTROL_PLANE/FINANCIAL_REPORTS/run_{timestamp}/` |
| 36 | Open `run_{timestamp}/` folder | Contains: `run_config.json`, `batch_001.md` (and more batches), `COMBINED_AI_ANALYSIS.md` |
| 37 | Open `batch_001.md` | Table is inside ` ```text ``` ` fenced code block |
| 38 | Table column alignment | `|` separators align vertically — fixed-width, space-padded |
| 39 | EAN values in table | Full 13-digit numbers (e.g. `5033601694236`) — NOT scientific notation |
| 40 | ROI values in table | Realistic percentages (e.g. `87.4%`) — NOT inflated (e.g. `8740%`) |
| 41 | Check `COMBINED_AI_ANALYSIS.md` | Contains merged/grouped content from all batches — NOT just copy-pasted batch files concatenated |
| 42 | Open `run_config.json` | Contains `completed_at` timestamp, `batches_processed` count, `errors` list |

**Triangulation check 6A — Operator vs Dashboard:**
After the operator runs, compare:
- Source 1: Operator batch MD — count VERIFIED (T1) rows
- Source 2: Dashboard Analysis tab → filter T1 → row count
- Source 3: Financial CSV directly → EAN == EAN_OnPage AND NetProfit > 0 → row count
These should agree within the batch size analyzed (if operator only analyzed a subset of rows).

---

## SECTION 7 — ANALYSIS TAB

**Pre-condition:** Select `efghousewares.co.uk` → Main Workflow → latest CSV.

| # | Action | Expected |
|---|--------|----------|
| 43 | Click "Analysis" in nav | Tab loads; tier filter badges visible (T1, T2, T3, T4, ALL) |
| 44 | Row count display | Shows actual CSV row count — NOT capped at 500 (should be ~18,095 total rows for efghousewares) |
| 45 | T1 badge count | Shows > 0 (was 0 before EAN fix; now should have T1 products) |
| 46 | Click T1 filter | Table shows only T1 rows; all have EAN_CHECKSUM_FAIL absent from flags |
| 47 | ROI column values | Realistic values (e.g. `118.6%`) — NOT inflated (e.g. `11860.0%`) |
| 48 | EAN column values | Full 13-digit numbers |
| 49 | Click "Export CSV" | Downloaded file contains ALL filtered rows (not just first 500) — check row count in downloaded file |
| 50 | Filter T2 | Table shows T2 rows; many have `EAN_CHECKSUM_FAIL` flag (old CSVs) or none (new CSVs) |
| 51 | Switch to poundwholesale latest CSV | Tier counts update; T1 rows appear |

**Triangulation check 7A — T1 count verification:**
- Source 1: Analysis tab T1 badge count
- Source 2: Open CSV in Excel → filter column `EAN` == column `EAN_OnPage` (after string normalization) AND `NetProfit` > 0 → count
- Source 3: Check `OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk/linking_map.json` — count entries where `amazon_asin` is present (approximates products successfully matched)
- T1 count (Source 1) should be a subset of Source 2 count (because T1 also requires no CATEGORY_MISMATCH).

---

## SECTION 8 — AI ASSISTANT TAB: Basic Smoke Tests

| # | Prompt | Expected LLM response behavior |
|---|--------|-------------------------------|
| 52 | `"hello"` | Greeting response, no tool call, no error |
| 53 | `"what suppliers are configured?"` | Lists configured suppliers (clearance-king, poundwholesale, efghousewares, angelwholesale, etc.) — uses `read_system_index` or `show_status` |
| 54 | `"show me the processing state for efghousewares"` | Calls `read_processing_state` → returns phase, category index/total, extraction/analysis counts |
| 55 | `"what is the current status of poundwholesale?"` | Returns same structure — phase, category X/233, products extracted/analyzed |

---

## SECTION 9 — AI ASSISTANT TAB: Scenario A — Category (Sandbox) Run

**Scenario:** Run a small sandbox test on clearance-king (2 specific categories, max 5 products each).

**Step 1 — Enqueue:**

> User: `"Run clearance-king on these two categories with max 5 products each: https://www.clearance-king.co.uk/smoking-products/lighters-accessories.html and https://www.clearance-king.co.uk/electrical/switches-sockets.html"`

**Expected LLM action:**
- Tool: `enqueue_run`
- `category_urls`: list of the 2 provided URLs
- `max_products`: 5 or `max_products_per_category`: 5
- `sandbox_suffix`: auto-generated (e.g. `sandbox_xxxxxxxx`)
- Response text: "I have enqueued a sandboxed run for clearance-king.co.uk with 2 categories and max 5 products per category. Start the worker to execute: `python -m control_plane worker`"
- Processing state included in response (phase, category progress)
- Expected output files listed in approval dialog:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_{uuid}.json`
  - `OUTPUTS/CONTROL_PLANE/status/{uuid}.json`
  - `OUTPUTS/CACHE/processing_states/clearance-king-co-uk__sandbox__{8chars}_processing_state.json`
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk__sandbox__{8chars}/linking_map.json`
  - `OUTPUTS/cached_products/clearance-king-co-uk__sandbox__{8chars}_products_cache.json`

**Step 2 — Click Approve. Start worker. Wait for job to complete.**

**Step 3 — Verify job ran:**

> User: `"Did the run start?"`

**Expected LLM action:**
- Calls `show_status` with `run_id` from `active_context`
- Returns status: `running` or `completed`
- Response text includes phase, category progress, extraction count

**Step 4 — Check logs:**

> User: `"Show me the last few lines of the log"`

**Expected:**
- Calls `tail_logs` with the run's log path
- Returns last N lines from `OUTPUTS/CONTROL_PLANE/logs/{uuid}.log`
- Log lines show product extraction progress (URLs processed, products found)

**Step 5 — Triangulation after completion:**

After job completes, verify from 3 sources:
- Source 1: AI chat → `"show me the processing state for clearance-king sandbox run"` → should show phase = `completed` or final amazon_analysis counts
- Source 2: Check file `OUTPUTS/cached_products/clearance-king-co-uk__sandbox__{id}_products_cache.json` — should contain ≤ 10 products (5 per category × 2 categories)
- Source 3: Check `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk__sandbox__{id}/linking_map.json` — entry count should match or be less than cached product count (not all products get Amazon matches)
- Source 4: Check `OUTPUTS/CONTROL_PLANE/logs/{uuid}.log` — look for "Workflow complete" or final summary line

**Step 6 — Cancel and resume test:**

> User: `"Cancel the run"`

**Expected:**
- Calls `cancel_run` with `run_id` inferred from context (no UUID pasted by user)
- Cancellation file created at `OUTPUTS/CONTROL_PLANE/jobs/cancelled/`

> User: `"Actually, continue it"`

**Expected:**
- Infers `sandbox_suffix` from `active_context.last_sandbox_suffix`
- Calls `enqueue_run` with `sandbox_suffix` = previously used suffix
- Response: "Resuming clearance-king sandbox run from where it left off."

---

## SECTION 10 — AI ASSISTANT TAB: Scenario B — Main Workflow (clearance-king)

**Pre-condition:** Worker NOT yet running. Chrome in debug mode on port 9222.

**Step 1 — Launch main workflow:**

> User: `"Launch the main workflow for clearance-king"`

**Expected LLM action:**
- Tool: `enqueue_run`
- `runner_script`: `run_custom_clearance-king.py`
- `category_urls`: `[]` (empty — runner uses built-in categories config)
- `max_products`: `null`
- `max_products_per_category`: `null`
- `sandbox_suffix`: NOT set / empty
- Approval dialog JSON shows `mode: "main_workflow"` in result
- Response text after approval: includes processing state metrics:
  ```
  Main workflow for clearance-king.co.uk enqueued successfully.

  Prior processing state (will resume from here):
  - Phase: amazon_analysis
  - Category progress: 35/155
  - Last category: https://www.clearance-king.co.uk/electrical/switches-sockets.html
  - Supplier extraction: 66/66 completed
  - Amazon analysis: 0/0 (pending)

  Start the worker to execute: python -m control_plane worker
  ```
- Expected output files:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_{uuid}.json`
  - `OUTPUTS/CONTROL_PLANE/logs/{uuid}.log` (created when worker starts)
  - `OUTPUTS/CACHE/processing_states/clearance-king-co-uk_processing_state.json` (updated by runner)
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/linking_map.json` (updated by runner)
  - `OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json` (updated by runner)
  - `OUTPUTS/FBA_ANALYSIS/financial_reports/clearance-king-co-uk/fba_financial_report_clearance-king-co-uk_{timestamp}.csv` (generated on completion)

**Step 2 — Verify enqueue is correct (pre-worker check):**

Check file `OUTPUTS/CONTROL_PLANE/jobs/pending/job_{uuid}.json`:
- `job_type` = `run_workflow`
- `runner_script` = `run_custom_clearance-king.py`
- `override.system_config_path` = `{project_root}/config/system_config.json` (the default, NOT a sandbox merged config)
- `runtime.max_products` = `null`
- `runtime.max_products_per_category` = `null`
- `sandbox_supplier` = `clearance-king.co.uk` (no suffix — main workflow)

**Step 3 — Start worker and monitor:**

Start worker: `python -m control_plane worker`

> User: `"Is the clearance-king run running?"`

**Expected:**
- Calls `show_status` → returns `running` once worker picks up the job
- Response includes current phase, category progress

**Step 4 — Triangulation: Confirm run is using correct config (3 sources):**
- Source 1: Job JSON file (`override.system_config_path`) points to default `config/system_config.json`
- Source 2: Worker log shows `FBA_SYSTEM_CONFIG_PATH=...config/system_config.json` (not a sandbox path)
- Source 3: Debug log at `logs/debug/run_custom_clearance-king-co-uk_{timestamp}.log` — first lines show category list loading from `config/clearance_king_categories.json` (all 155 categories, not a 2-category subset)

**Step 5 — After completion triangulation (4 sources):**
- Source 1: AI chat → `"show me processing state for clearance-king"` → `phase = completed`, `persistent_category_index = 155`
- Source 2: `OUTPUTS/CACHE/processing_states/clearance-king-co-uk_processing_state.json` → `system_progression.total_categories = 155`, `current_phase = completed`
- Source 3: `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/linking_map.json` → entry count significantly higher than the 35-category partial run (~66 entries currently, should be much higher after full run)
- Source 4: `OUTPUTS/FBA_ANALYSIS/financial_reports/clearance-king-co-uk/` → new CSV file generated with timestamp after run start, containing product rows

**Step 6 — Dashboard verification after completion:**
- Open Dashboard tab → select `clearance-king.co.uk` → Main Workflow → new CSV
- Metrics cards show values (Profitable, With Sales, Avg ROI)
- Profitable Categories chart shows clearance-king categories
- Analysis tab shows clearance-king products with T1/T2 classifications
- EAN column in Analysis tab: full 13-digit numbers (new CSV was generated with EAN fix applied)

---

## SECTION 11 — AI ASSISTANT TAB: Scenario C — Product List Workflow

**Step 1 — Create product list:**

> User: `"Create a product list for clearance-king using products from the cached data"`

**Expected:**
- Calls `build_product_list_from_cached` for `clearance-king.co.uk`
- Creates file at `OUTPUTS/PRODUCTS_LISTS/product_list_clearance-king_DDMMYY.json` (or similar deterministic name)
- Response: "I've built a product list from clearance-king's cached products and saved it to `OUTPUTS/PRODUCTS_LISTS/product_list_clearance-king_{date}.json` with N products."

**Step 2 — Refresh that list:**

> User: `"Now run a product list refresh on that file for clearance-king"`

**Expected:**
- Infers file path from previous message context
- Calls `enqueue_product_list_refresh` with `products_path = OUTPUTS/PRODUCTS_LISTS/product_list_clearance-king_{date}.json`
- Response: "Enqueued product list refresh for clearance-king.co.uk using the file we just created."

**Triangulation after completion:**
- Source 1: Chat → `"show me status"` → phase and product counts
- Source 2: `OUTPUTS/cached_products/clearance-king-co-uk_{sandbox}_products_cache.json` — contains the re-analyzed products
- Source 3: `OUTPUTS/CONTROL_PLANE/logs/{uuid}.log` — shows each product being processed

---

## SECTION 12 — AI ASSISTANT TAB: Scenario D — Conversational Context Memory

> User: `"Check the processing state for angelwholesale"`

> User (follow-up, no UUID): `"How many categories are left?"`

**Expected:** LLM infers angelwholesale from `active_context` and correctly calculates remaining = `total_categories - persistent_category_index`.

> User: `"Cancel it"`

**Expected:** Calls `cancel_run` inferring `last_run_id` from context — does NOT ask "which run?".

> User: `"Resume it"`

**Expected:** Calls `enqueue_run` with `sandbox_suffix` = previous run's suffix — does NOT ask for URLs.

---

## SECTION 13 — AI ASSISTANT TAB: Scenario E — State Read After Enqueueing (Auto-attach)

> User: `"Launch the main workflow for poundwholesale with no limits"`

After approving:

**Expected response text includes ALL of:**
1. Confirmation that job was enqueued
2. `processing_state` block showing:
   - `current_phase`
   - `persistent_category_index / total_categories`
   - `current_category_url`
   - `supplier_products_completed / supplier_products_needing_extraction`
   - `amazon_products_completed / amazon_products_needing_analysis`
3. Instruction to start the worker

**Verify NO second prompt is needed** — the state appears in the same response as the enqueue confirmation.

---

## SECTION 14 — REGRESSION CHECKS

| # | What to check | Expected |
|---|--------------|----------|
| 57 | All 5 nav items visible | Dashboard, Operator, AI Assistant, Analysis, Workflows |
| 58 | Switch between all 5 tabs | Each loads without blank screen or JS error |
| 59 | Refresh page mid-session | Dashboard reloads; last selected supplier/lineage remembered |
| 60 | CONNECTED indicator (bottom of sidebar) | Green dot + "CONNECTED" text |
| 61 | Sandbox lineage entries visible | After running sandbox tests, dropdown shows sandbox options (e.g. `sandbox_xxxxxxxx`) |
| 62 | Sandbox lineage: no dropdown for financial report | Sandbox lineage shows `— latest —` only (no multi-CSV dropdown — acceptable) |
| 63 | Auto-refresh toggle works | Setting to 60 seconds → metrics refresh every 60s without manual action |
| 64 | Operator: per-run subfolder | Each analysis creates a new `run_{timestamp}/` folder — not overwriting previous |
| 65 | Analysis: export on large CSV | Export on 18,000-row efghousewares CSV completes; file contains > 500 rows |
| 66 | No JS console errors on any tab | Open Chrome DevTools → Console → no red errors on page load or tab switch |

---

## NOTES & KNOWN CAVEATS

- **EAN fix (C1+C2) only applies to CSVs generated after 2026-03-21.** Old CSVs still have scientific notation EANs. If T1 count is still 0, verify the CSV was generated by the new calculator (check EAN column directly in the file).
- **Clearance-king main workflow will resume** from category 35/155 (last stopped at `switches-sockets.html`). This is expected — not a fresh start.
- **Angelwholesale linking_map.json** has only 12 entries in the live folder (overwritten by sandbox runs). The real 9,777-entry map is saved as `angelwholesale actual linkingmap.json` in the same folder. Dashboard metrics for angelwholesale are based on the freshly generated CSV from 2026-03-21, which was produced using the real linking map.
- **Worker must be running** for any enqueued job to execute. Enqueueing only places a JSON in `OUTPUTS/CONTROL_PLANE/jobs/pending/`. Nothing runs until `python -m control_plane worker` is active.
- **Main workflow for clearance-king** will use `config/clearance_king_categories.json` (155 categories). Confirm the worker log shows all categories loading — if it only shows 2, the sandbox config override leaked through (revert to check Fix 14 in implementation summary).
