# AGENTIC FBA CALIBRATION (PRE-FLIGHT) v1.2 — part 3 jan.xlsx

**Input file:** `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\part 3 jan.xlsx`  
**Observed SupplierURL domain (top):** `www.efghousewares.co.uk`  
**Sheet(s):** `Sheet1`  
**Rows:** 2666  
**Columns (25):** `EAN`, `EAN_OnPage`, `ASIN`, `SupplierTitle`, `AmazonTitle`, `SupplierURL`, `AmazonURL`, `bought_in_past_month`, `fba_seller_count`, `fbm_seller_count`, `total_offer_count`, `SupplierPrice_incVAT`, `SupplierPrice_exVAT`, `SellingPrice_incVAT`, `ReferralFee`, `FBAFee`, `PrepHouseFee`, `OutputVAT`, `InputVAT`, `NetProceeds`, `HMRC`, `NetProfit`, `ROI %`, `Breakeven`, `ProfitMargin`

## Task 1: Pack quantity patterns

### SupplierTitle patterns observed
- **Explicit units present** (common formats):
  - `10PC`, `2PC`, `8PC`, `8PCS`, `12 PIECES`, `2 PCE`
  - `PACK OF 12`, `PACK OF 3`, `SET OF 2`
  - `PK6`, `PK8`, `PK12` (often appended to the end)
- **Implicit / trailing numbers** occur (less frequent but present):
  - Can be true pack counts (`BALLOONS ASSORTED 20`)
  - Can be **variant/age/model** and not a pack (`... GIRL 3`)
  - Can be **range/date-like** and should not be treated as qty (`10-15`, `05/11`)
- **Leading multipliers** like `6 x ...` / `10x ...` at the start were **not observed**.
- **Dimensions vs quantity**:
  - Compact dimensions like `70X100CM` and mixed-unit forms like `24MMx15M` appear and should be shielded from RSU logic.

### AmazonTitle capacity multipack patterns observed
- Patterns like `10 x 90g`, `7 x 100g`, `12x 280ml`, `5 x 60L` appear.
- **Rule holds:** when Amazon shows `N x [capacity]ml/g/l/kg`, use **RSU = N** (the first number only).

## Task 2: Sales signal
- **Sales column:** `bought_in_past_month` (observed as numeric `int64`, no `\"100+ bought\"` strings in this file).

## Task 3: Brand patterns
- No explicit `Brand` column found.
- Heuristic from SupplierTitle first-token frequency suggests brands are **most often at the start** (e.g., `PRIMA ...`, `DEKTON ...`, `DUNLOP ...`).
- Set `brand_position = "start"` (treat as best-effort; do not rely on this as deterministic without a brand column).

## Task 4: Calibration warnings (traps)

Row 2: `'151 WHITE NO-DRIP GLOSS PAINT 300ML'` — `151` is likely a product code/model, not a pack quantity  
Row 3: `'EUROWRAP GIANT BIRTHDAY BADGE GIRL 3'` — trailing `3` is likely variant/age, not pack qty  
Row 16: `'EASY STORAGE VACUUM BAG 70X100CM'` — `70X100CM` is dimensions; RSU=1, not RSU=7000  
Row 28: `AmazonTitle` contains `' | '` — sanitize pipes in tables (replace `|` with `/`) to avoid markdown table corruption  
Row 143: `'... Digital Microscope - 2000x ...'` — `2000x` is magnification/spec, not pack qty  
Row 173: `'SUNNEX ... PK12 05/11'` — `05/11` is date-like; do NOT treat trailing numbers as qty here  
Row 177: `'DUNLOP BIKE SPOKE WRENCH 10-15'` — `10-15` is a range; do NOT treat as pack qty  
Row 262: `AmazonTitle '10 x 90g'` — RSU=10 (units), not RSU=900 (capacity-multiplied)

Also: In a 200-row sample, SupplierTitle vs AmazonTitle had **very low token overlap in most rows**, suggesting many pairings may be mismatched; avoid using AmazonTitle-derived pack cues unless the pairing is validated.

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pack of", "piece", "pieces", "set of"],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "m", "ml", "l", "ltr", "litre", "cl", "g", "kg", "oz", "inch", "in", "ft"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "binocular", "scope", "times"],
    "table_pipe_sanitization": True
}
# ---------------------------------
```

