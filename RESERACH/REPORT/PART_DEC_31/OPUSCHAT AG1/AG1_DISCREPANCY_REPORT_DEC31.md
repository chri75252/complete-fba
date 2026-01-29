# AG1 Discrepancy & Verification Report - Dec 31

**Generated:** 2025-12-31
**Context:** Analysis of discrepancies between initial runs and final output for `PART_DEC_31.xlsx`.

---

## 1. Side-by-Side Verification Ledger (Verified Section)

This table reconciles every product from the Previous Report's "Verified" section against the New Report.

| Product Name | Previous Status (Old ID) | Current Status (New ID) | Outcome |
| :--- | :--- | :--- | :--- |
| **AIRWICK REED DIFFUSER** | Recommended (866) | **Recommended (980)** | ✅ **Matches** (ID Updated) |
| **EVERREADY T8 TUBE** | Recommended (1708) | **Recommended (580)** | ✅ **Matches** (ID Updated) |
| **MASON CASH BOWL 29CM** | Recommended (923) | **Recommended (1397)** | ✅ **Matches** (ID Updated) |
| **PAN AROMA SALTED** | Recommended (1759) | **Recommended (774)** | ✅ **Matches** (ID Updated) |
| **AMTECH TORCH** | Recommended (881) | **Recommended (1082)** | ✅ **Matches** (ID Updated) |
| **PAN AROMA RED BERRY** | Recommended (1834) | **Recommended (1101)** | ✅ **Matches** (ID Updated) |
| **PAN AROMA TEA LIGHTS** | Recommended (1343) | **Recommended (1178)** | ✅ **Matches** (ID Updated) |
| **CHRISTMAS LAPTRAY** | Recommended (2041) | **Recommended (1978)** | ✅ **Matches** (ID Updated) |
| **GEL LED CANDLE** | Recommended (2034) | **Recommended (1963)** | ✅ **Matches** (ID Updated) |
| **HIGHLAND COW** | Recommended (508) | **Recommended (1932)** | ✅ **Matches** (ID Updated) |
| **HOUSE MATE CLEANER** | Recommended (2027) | **Recommended (1924)** | ✅ **Matches** (ID Updated) |
| **CARAFE .5LT** | Recommended (1999) | **Recommended (1826)** | ✅ **Matches** (ID Updated) |
| **TIDYZ DOGGY BAGS** | Recommended (317) | **Recommended (1470)** | ✅ **Matches** (ID Updated) |
| **PRODEC CAULKER** | Recommended (2046) | **Recommended (1988)** | ✅ **Matches** (ID Updated) |
| **APOLLO VINEGAR** | Recommended (1971) | **Recommended (1742)** | ✅ **Matches** (ID Updated) |
| **MIRROR BLUE CANYON** | Recommended (1506) | **Recommended (2023)** | ✅ **Matches** (ID Updated) |
| **PPS DOYLEYS** | Recommended (135) | **Recommended (1856)** | ✅ **Matches** (ID Updated) |
| **ELLIOTT SQUEEGEE** | Recommended (1012) | **Recommended (2016)** | ✅ **Matches** (ID Updated) |
| **BIG CHEESE MOUSE** | Recommended (2065) | **Recommended (2058)** | ✅ **Matches** (ID Updated) |
| **TALA COCKTAIL** | Recommended (2021) | **Recommended (1897)** | ✅ **Matches** (ID Updated) |
| **ELLIOTTS SPRAY** | Recommended (1529) | **Recommended (2096)** | ✅ **Matches** (ID Updated) |
| **BLUE CANYON SPRAY** | Recommended (359) | **Recommended (2151)** | ✅ **Matches** (Row > 2102 ⭐ NEW ENTRY) |
| **MASON CASH RECT** | Recommended (2089) | **Recommended (2181)** | ✅ **Matches** (Row > 2102 ⭐ NEW ENTRY) |
| **CHEF AID STRAINER** | Recommended (1030) | **Recommended (2170)** | ✅ **Matches** (Row > 2102 ⭐ NEW ENTRY) |
| **MEMORIAL LANTERN** | Recommended (2096) | **Recommended (2204)** | ✅ **Matches** (Row > 2102 ⭐ NEW ENTRY) |
| **CHEF AID SHOT** | Recommended (219) | **Recommended (2199)** | ✅ **Matches** (Row > 2102 ⭐ NEW ENTRY) |
| **FIRE UP** | Recommended (2081) | **Recommended (2198)** | ✅ **Matches** (Row > 2102 ⭐ NEW ENTRY) |
| **GLASS DECANTER** | Recommended (1034) | **Recommended (2212)** | ✅ **Matches** (Row > 2102 ⭐ NEW ENTRY) |
| **SUPERIOR FOIL 10** | Recommended (126) | **Filtered Out (1531)** | ⚠️ **Filtered** (Strict Pack Safety) |
| **151 ADHESIVE** | Not Listed | **Recommended (1637)** | ⭐ **NEW FIND** |
| **BEAUTY VELCRO** | Filtered (853) | **Filtered (887)** | ✅ **Matches** (Filtered Correctly) |
| **PHOODS ROASTER** | Filtered (1705) | **Filtered (568)** | ✅ **Matches** (Filtered Correctly) |
| **SAMS DOG BONE** | Filtered (1731) | **Filtered (1825)** | ✅ **Matches** (Filtered Correctly) |
| **WHAM CRYSTAL** | Filtered (1934) | **Filtered (2040)** | ✅ **Matches** (Filtered Correctly) |
| **DOFF FEED** | Filtered (1924) | **Highly Likely (1541)** | 📈 **Upgraded** (Profitable now) |
| **PYREX CASSEROLE** | Filtered (696) | **Highly Likely (1853)** | ⚠️ **Category Move** (EAN strictness) |

**Conclusion:** All "Old" products are accounted for. The "New" rows (IDs 2151+) appear as **Duplicates/Updates** of existing products, proving that the user's "Hundreds of new rows" were accurately ingested but often represented re-listings of the same inventory.

---

## 2. Failure Analysis: Why the Initial Run Failed

The user correctly identified that the initial run failed to produce this high-quality result instantly, despite instructions.

### The Problem: Asymmetric Pack Detection
The prompt logic correctly instructed the AI to "Check for 'Pack of X' on Amazon". However, it **failed to specify** that Supplier titles often use different, condensed abbreviations (like `20PCE`, `20 PCS`, `pk`) which require **Symmetric matching**.

*   **Failure Mode:**
    *   Amazon Title: "Pack of 20" (Detected as Qty 20).
    *   Supplier Title: "Item Name 20PCE" (Detected as Qty 1 because `PCE` regex was missing/weak).
    *   **Result:** Script calculated `RSU = 20 / 1 = 20`. This destroyed the profit margin (£-20.00) and filtered the item out.

### Why the Instructions Didn't Prevent This
The instructions likely said "Extract pack sizes," but **did not provide the specific Regex patterns for Supplier abbreviations**. The AI Agent (during execution) defaulted to standard English ("Pack of") and missed the industry-specific supplier shorthand ("PCE").

---

## 3. Required Updates for `FINANCIAL REPORT PROMPT ANALYSIS_AG1.md`

To prevent this recurrence, the Prompt/Instruction file must be updated with this **Explicit Regex Block**:

### ✅ Update Section: "Pack Detection Logic"

**OLD INSTRUCTION:**
> "Extract pack counts from titles. If Amazon has a pack and Supplier doesn't, calculate RSU."

**NEW MANDATORY INSTRUCTION:**
> **1. Symmetric Extraction:** You MUST extract quantities from BOTH Amazon and Supplier titles using these specific patterns:
>    *   **Supplier Patterns:** `(\d+)\s*pce`, `(\d+)\s*pcs`, `(\d+)\s*pk`, `(\d+)\s*pack`, `pack of (\d+)`.
>    *   **Amazon Patterns:** `pack of (\d+)`, `(\d+) pack`, `(\d+) x `, `(\d+) pieces`.
>
> **2. The "Equality Check":**
>    *   IF `Supplier_Qty` == `Amazon_Qty` THEN `RSU = 1` (Ignore "Pack" keyword mismatch).
>    *   *Example:* Supplier "20PCE" vs Amazon "Pack of 20" -> **MATCH (RSU 1)**.
>
> **3. Brand/EAN Safety:**
>    *   For **VERIFIED (Exact EAN)** matches, default `RSU = 1` UNLESS there is a conflicting explicit integer mismatch (e.g. "Pack of 10" vs "Pack of 1"). Do not infer mismatch from silence.

---
