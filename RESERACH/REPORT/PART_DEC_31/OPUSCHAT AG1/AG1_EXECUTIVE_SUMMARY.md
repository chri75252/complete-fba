# AG1 Reports: Executive Summary & Performance Analysis

## 1. Report Performance Comparison
| Metric | **OPUS AG1** | **CODEX AG1** | **webapp ag1** |
| :--- | :--- | :--- | :--- |
| **Strategy** | **High Recall** (Loose) | **High Precision** (Strict) | Balanced / Strict |
| **Verified (Rec)** | **34** | 26 | 26 |
| **Highly Likely** | **146** | 23 | 60 |
| **Key Strength** | Found the most opportunities. | Zero False Positives on pack mismatches. | Consistent with Codex. |
| **Key Weakness** | **False Positives:** Missed some "4 x 50" pack clues, incorrectly marking them as 1:1. | **False Negatives:** Valid items filtered because "20PCE" wasn't parsed as 20. | Similar to Codex. |

## 2. Areas of Concern

### A. The "Blind Spot" Risk (OPUS)
*   **Concern:** OPUS AG1 flagged `Tidyz Doggy Bags` as a **VERIFIED 1:1 Match**.
*   **Reality:** It was a **4-pack bundle** (Amazon "200 bags (4 x 50)" vs Supplier "50").
*   **Root Cause:** The prompt missed the complex multipack signal on Amazon's side.
*   **Impact:** Dangerous recommendations that would lose money.

### B. The "Over-Filtering" Risk (CODEX/webapp)
*   **Concern:** CODEX AG1 filtered `Chef Aid Shot Glasses` (20-pack) as a **LOSS**.
*   **Reality:** It was a **1:1 Match** (Amazon "Pack of 20" vs Supplier "20PCE").
*   **Root Cause:** The prompt failed to read "20PCE" as a number, defaulting Supplier to 1. RSU became 20, destroying profit.
*   **Impact:** Lost profitable opportunities.

### C. The Universal "Equality" Failure
*   **Concern:** All reports filtered `Phoods Foil Trays` (10-pack).
*   **Reality:** Both explicitly stated 10 (Amazon "10 Containers", Supplier "10...").
*   **Root Cause:** Lack of a "Shield" logic. Even if parsed correctly, slight text differences caused the LLM to doubt the match.

## 3. Solution Integrated
The **Surgical Fixes (v3)** just applied to the prompt address all three areas:
1.  **Regex Injection:** Parsing `pce`, `pcs`, `pk` fixes the **Over-Filtering** (Chef Aid).
2.  **Equality Shield:** Forcing `RSU=1` when numbers match fixes the **Universal Failure** (Phoods).
3.  **Strict Logic Retention:** By keeping the base strictness of Codex but fixing the parsing errors, we aim for **OPUS-level Recall** with **CODEX-level Safety**.
