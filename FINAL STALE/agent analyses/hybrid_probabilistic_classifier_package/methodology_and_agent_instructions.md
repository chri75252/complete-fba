# FBA TIER CLASSIFICATION REDESIGN: APPROACH & METHODOLOGY REPORT

### **NOTE TO EVALUATING AGENT**
> **Agent Instruction:** You are evaluating a **Hybrid Probabilistic Record Linkage** approach designed to replace an ineffective additive scoring model for Amazon FBA tier classification. Because I do not have access to the entirety of the local codebase, you may make minor adjustments to variable mappings, column names, and module imports to fit the exact schema of `tools/fba_report_filter.py` and `dashboard_v2_redesign/api.py`. Please take these missing contextual aspects into consideration. If any core assumptions (e.g., the availability of pack-size data) conflict with the real data schema, halt and inform the user to request clarification.

---

### **1. Approach, Concept, and Methodology**
**The Problem:** The existing system relies on a naive "additive scorer" (e.g., +5 points for EAN match, +3 for title match). This approach is structurally brittle. It frequently triggers false rejections when EANs are missing or formatting differs, and it completely fails to catch variant/multipack discrepancies (e.g., linking a single unit supplier product to a 6-pack Amazon listing), artificially inflating ROI.

**The Solution: Hybrid Probabilistic Record Linkage with Deterministic Overrides**
I approached this as an **Entity Resolution** problem rather than a basic filtering task. The methodology utilizes a phased evaluation pipeline:
1.  **Text Normalization Layer:** Cleanses strings, standardizes casing, and removes special characters to prevent false negatives from punctuation discrepancies.
2.  **Dimensional Feature Extraction:** Extracts distinct comparison dimensions—specifically isolating EAN matching, Title Semantic Similarity (via Sequence Matching/Jaro-Winkler), and Pack-Size/Variant extraction using regex.
3.  **Probabilistic Scoring with Penalties:** Instead of merely adding points, the system establishes a base similarity probability and applies aggressive mathematical penalties for critical mismatches (e.g., differing pack sizes).
4.  **Tiered Decision Matrix:** Maps the final confidence score and categorical flags (e.g., `ean_match = True`, `pack_match = False`) into strict, explainable tiers.

---

### **2. Initial Calibration & Configuration Required**
Before running the script in production, the system requires a calibration phase to set probabilistic boundaries. The script accepts a configuration dictionary.

**Calibration Variables:**
*   **`title_similarity_threshold_tier1`** (Default `0.85`): The minimum sequence similarity ratio required to classify a match as Tier 1 or 2 when an EAN is missing.
*   **`title_similarity_threshold_tier2`** (Default `0.70`): The baseline similarity required to prevent a product from being outright rejected (Tier 4).
*   **`pack_size_penalty_weight`** (Default `0.5`): The aggressive deduction applied to the confidence score if regex detects a discrepancy in multi-pack volumes.
*   **`missing_ean_penalty`** (Default `0.2`): The deduction applied if an EAN is entirely missing from either the supplier or Amazon data.

---

### **3. Expected Input Format**
The script expects a dictionary (or Pandas Series converted to a dict) representing a single row from the provided CSVs (`fba_analysis_2026-04-15.csv`, etc.). 

**Required Keys (or their local equivalents):**
*   `'Supplier Title'` (String)
*   `'Amazon Title'` (String)
*   `'Supplier EAN'` (String/Numeric)
*   `'Amazon EAN'` (String/Numeric)

---

### **4. Python Implementation (Drop-In Replacement)**
The exact code is provided in the sibling file `fba_tier_classifier.py`.

---

### **5. Variables Reliant on Calibration**
When integrating this into `dashboard_v2_redesign/api.py`, the agent must pay attention to:
1.  **The `config` dictionary inside `__init__`:** If the user finds too many valid products are being dropped to Tier 3 because of strict pack-size rules, the `pack_size_penalty_weight` must be reduced from `0.50` to `0.30`.
2.  **Regex Tuning in `_extract_pack_size`:** The regex is reliant on standard UK/US packaging nomenclature. If the supplier feeds use niche terminology (e.g., "Outer 12", "Ctn of 6"), the regex pattern must be calibrated/expanded to catch those specific strings.

---

### **6. Expected Output Format**
The `classify_row` method returns a strictly typed `Tuple[int, str, float]`:
1.  **Tier (int):** An integer from `1` to `4` (where 1 is highest confidence, 4 is reject).
2.  **Reason (str):** A deterministic, human-readable string specifically indicating *why* the tier was chosen (e.g., "EAN Match but Pack Size Discrepancy Detected"). This satisfies the "explainability" requirement.
3.  **Confidence (float):** A float between `0.0` and `1.0` to allow for continuous color-banding or sub-sorting within the frontend UI.
