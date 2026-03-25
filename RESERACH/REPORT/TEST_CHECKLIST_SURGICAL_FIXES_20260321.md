# Test Checklist — Surgical Fixes 2026-03-21
Restart uvicorn before testing: `uvicorn dashboard_v2_redesign.api:app --port 8001 --reload`

---

## FIX C1+C2 — EAN Serialization (FBA_Financial_calculator.py)
*These only apply to newly generated CSVs. Test after running the solo calculator scripts.*

| # | What to check | Expected |
|---|---|---|
| 1 | Open a newly generated `fba_financial_report_*.csv` in a text editor | EAN column shows full 13-digit numbers (e.g. `5032759031078`), NOT scientific notation (e.g. `5.03276E+12`) |
| 2 | Check EAN_OnPage column in the same CSV | Same — full digits, no scientific notation |
| 3 | Open Analysis tab in dashboard with the new CSV | T1 rows appear (previously 0 T1 — now should show some) |
| 4 | Confirm AMTECH LED MINI TORCH is T1 (if present in new CSV) | Tier = T1_VERIFIED, flag = nothing or BRAND_MISMATCH only (no EAN_CHECKSUM_FAIL) |

---

## FIX C3 — Analysis Tab: No 500-Row Cap

| # | What to check | Expected |
|---|---|---|
| 5 | Open Analysis tab → select a CSV with > 500 rows → click Refresh | `X results` counter shows actual row count, NOT capped at 500 |
| 6 | Total rows counter (top of Analysis tab) matches the CSV row count | E.g. if CSV has 21,000 rows and 800 pass tier filter, counter shows 800 |
| 7 | Export CSV from Analysis tab | Exported file contains all filtered rows, not just first 500 |

---

## FIX C4 — Dashboard Financial Report Dropdown Populated

| # | What to check | Expected |
|---|---|---|
| 8 | Open Dashboard tab → look at sidebar FINANCIAL REPORT dropdown | Dropdown is populated with available CSV filenames (e.g. `fba_financial_report_20260122_093706.csv (X rows)`) |
| 9 | Select a different CSV from the dropdown → dashboard refreshes | Metrics and charts update to reflect the selected CSV |
| 10 | Select `— latest —` option | Dashboard reverts to the most recent CSV |

---

## FIX G1 — ROI Display in Analysis Tab

| # | What to check | Expected |
|---|---|---|
| 11 | Open Analysis tab → look at the ROI column | Values show realistic percentages (e.g. `118.6%`, `91.5%`), NOT inflated values (e.g. `11860.3%`, `9150.0%`) |
| 12 | A product with ~100% ROI in the CSV shows ~100% in the column | ROI = 100.0%, not 10000.0% |

---

## FIX C5 — Operator Agent: Table Formatting

| # | What to check | Expected |
|---|---|---|
| 13 | Run operator analysis on a CSV → open the generated `batch_001.md` | Tables are wrapped in ` ```text ... ``` ` fenced code blocks |
| 14 | Open the batch MD file and check column alignment | `|` separators align vertically — columns are space-padded to equal width |
| 15 | Check `COMBINED_AI_ANALYSIS.md` | Same fixed-width table format throughout |

---

## FIX C7 — EAN Values in Operator Agent Prompt/Output

| # | What to check | Expected |
|---|---|---|
| 16 | Run operator analysis → open a batch MD file | EAN columns show full digit strings (e.g. `5032759031078`), NOT scientific notation (e.g. `5.03276E+12`) |
| 17 | The summary paragraph no longer says "EAN reuse" for clearly different products | Different Pan Aroma scents show different EAN values in the table |

---

## FIX WF — Workflows Page in Dashboard

| # | What to check | Expected |
|---|---|---|
| 18 | Look at the left sidebar navigation | A new "Workflows" nav item appears after "Analysis" |
| 19 | Click "Workflows" in the nav | Page loads with two side-by-side cards |
| 20 | Left card heading | "Fresh Run — Identify Profitable & Sellable Products" in green |
| 21 | Right card heading | "Stale Data — Identify Categories & Products to Re-Analyze" in blue/purple |
| 22 | Red warning box visible at bottom of right card | Warning text starts with "Do NOT" |
| 23 | Both cards contain numbered phase lists (Phase 1 through Phase 5) | All 5 phases visible in each card with step-by-step instructions |

---

## Regression Checks — Nothing Else Should Have Changed

| # | What to check | Expected |
|---|---|---|
| 24 | Dashboard tab loads and metrics display correctly | Profitable, With Sales, Avg ROI, Avg Profit cards all show values |
| 25 | Profitable Categories chart still shows bars with `(count)` in labels | No regression |
| 26 | Profit vs Competition scatter plot shows `total_offer_count` on X axis | No regression |
| 27 | Analysis tab tier counts display (T1, T2, T3, T4) | All 4 badges show correct counts |
| 28 | Operator agent runs successfully and produces batch + combined MD files | No crash, files saved to `OUTPUTS/CONTROL_PLANE/FINANCIAL_REPORTS/run_{timestamp}/` |
| 29 | AI Assistant (chat) tab still works — send a message | Response received, no error |

---

## Notes
- Fixes C1+C2 only affect NEWLY generated CSVs. Existing CSVs still have scientific notation EANs.
- After the solo calculator scripts run (step 9), re-test items 1-4 and 11 using the newly generated reports.
- If tier counts still show 0 T1 after running on a new CSV, check the EAN column in the CSV directly before assuming a bug.
