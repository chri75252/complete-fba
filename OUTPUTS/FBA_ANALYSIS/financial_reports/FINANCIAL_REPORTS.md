# Financial Reports

**Location:** `OUTPUTS/FBA_ANALYSIS/financial_reports/`

## Overview

Financial reports contain profitability analysis for products that have been matched between suppliers and Amazon. Each row calculates ROI, fees, margins, and net profit.

---

## Directory Structure

```
OUTPUTS/FBA_ANALYSIS/financial_reports/
├── poundwholesale-co-uk/
│   ├── fba_financial_report_poundwholesale-co-uk_20250726.csv
│   ├── fba_financial_report_poundwholesale-co-uk_20250727.csv
│   └── fba_financial_report_poundwholesale-co-uk_combined.csv
├── clearance-king-co-uk/
├── efghousewares-co-uk/
└── {supplier}/
    ├── fba_financial_report_{supplier}_{timestamp}.csv
    └── fba_financial_report_{supplier}_combined.csv
```

---

## File: `fba_financial_report_{supplier}_{timestamp}.csv`

### Purpose
Calculates profitability for each matched product.

### CSV Columns

| Column | Type | Description |
|--------|------|-------------|
| `EAN` | string | Supplier EAN |
| `EAN_OnPage` | string | EAN as shown on Amazon page |
| `ASIN` | string | Amazon ASIN |
| `SupplierTitle` | string | Product title from supplier |
| `AmazonTitle` | string | Product title on Amazon |
| `SupplierURL` | string | URL to supplier product |
| `AmazonURL` | string | URL to Amazon product |
| `bought_in_past_month` | float | Units sold last 30 days |
| `fba_seller_count` | int | Number of FBA sellers |
| `fbm_seller_count` | int | Number of FBM sellers |
| `total_offer_count` | int | Total seller count |
| `SupplierPrice_incVAT` | float | Supplier price (inc VAT) |
| `SupplierPrice_exVAT` | float | Supplier price (ex VAT) |
| `SellingPrice_incVAT` | float | Amazon selling price (inc VAT) |
| `ReferralFee` | float | Amazon referral fee |
| `FBAFee` | float | FBA fulfillment fee |
| `PrepHouseFee` | float | Prep center fee |
| `OutputVAT` | float | VAT on sale proceeds |
| `InputVAT` | float | VAT on purchase (reclaimable) |
| `NetProceeds` | float | Sale proceeds minus fees |
| `HMRC` | float | VAT owed to HMRC |
| `NetProfit` | float | Final profit after all costs |
| `ROI` | float | Return on investment (%) |
| `Breakeven` | float | Breakeven selling price |
| `ProfitMargin` | float | Profit as % of sale price |

---

## Calculated Fields

### Fee Calculations

```python
ReferralFee = SellingPrice * 0.15  # 15% referral fee (varies by category)
FBAFee = base_fees + weight_fees  # Based on product dimensions/weight
PrepHouseFee = 0.55  # Fixed prep center fee
OutputVAT = SellingPrice * 0.20  # 20% VAT on UK sales
InputVAT = SupplierPrice * 0.20  # 20% VAT (reclaimable)
```

### Net Profit Calculation

```python
NetProceeds = SellingPrice - ReferralFee - FBAFee - PrepHouseFee - OutputVAT
NetProfit = NetProceeds - InputVAT - SupplierPrice
ROI = (NetProfit / SupplierPrice) * 100
ProfitMargin = (NetProfit / SellingPrice) * 100
```

### Breakeven

```python
Breakeven = (SellingPrice - ReferralFee - FBAFee - PrepHouseFee - OutputVAT) / (1 + VAT_RATE) - SupplierPrice
```

---

## Example Row

| Field | Value |
|-------|-------|
| EAN | 5050837373018 |
| ASIN | B0FPXFMGVT |
| SupplierPrice_incVAT | 4.00 |
| SellingPrice_incVAT | 899.99 |
| ReferralFee | 135.00 |
| FBAFee | 7.50 |
| NetProfit | -28.69 |
| ROI | -717.25% |
| ProfitMargin | -3.19% |

*Note: Negative ROI indicates buy box price doesn't cover costs at this selling price.*

---

## Combined Reports

`fba_financial_report_{supplier}_combined.csv` merges all dated reports into one file.

### Purpose
- Complete historical view
- Filtered analysis (e.g., only profitable products)
- Dashboard data source

---

## Usage

### Read in Python
```python
import pandas as pd

df = pd.read_csv("OUTPUTS/FBA_ANALYSIS/financial_reports/poundwholesale-co-uk/fba_financial_report_combined.csv")
print(df.head())
```

### Find Profitable Products
```python
profitable = df[df["NetProfit"] > 0]
print(f"Profitable: {len(profitable)} products")
```

### High ROI Products
```python
high_roi = df[df["ROI"] > 100].sort_values("ROI", ascending=False)
print(high_roi[["EAN", "SupplierPrice_incVAT", "NetProfit", "ROI"]].head(10))
```

### Sales Velocity Filter
```python
hot = df[df["bought_in_past_month"] > 50]
print(f"Fast sellers: {len(hot)}")
```

---

## Calculator Class

**Location:** `tools/FBA_Financial_calculator.py`

**Function:** `run_calculations(supplier_name)`

**Key Parameters:**
```python
def run_calculations(
    supplier_name: str,
    supplier_cache_path: str = None,
    amazon_scrape_dir: str = None,
    linking_map_path: str = None,
    output_dir: str = None
):
```

---

## Fee Structure (UK Amazon)

| Fee Type | Rate |
|----------|------|
| Referral Fee | 15% (varies 6-15% by category) |
| FBA fulfillment | £2.50-£4.00 (size dependent) |
| Prep center | £0.55 per unit |
| VAT (output) | 20% |
| VAT (input) | 20% (reclaimable) |

---

## Thresholds

Reports are generated when linking map reaches batch size:
```json
{
  "system": {
    "linking_map_batch_size": 50
  }
}
```

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Linking Map | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json` | Matched products |
| Amazon Cache | `OUTPUTS/FBA_ANALYSIS/amazon_cache/` | Amazon pricing data |

---

## Dashboard Integration

Financial reports feed the dashboard KPI displays:

```javascript
// dashboard_v2_redesign/api.py
const report = await fetchFinancialReport(supplier);
const metrics = {
  totalProducts: report.length,
  profitableCount: report.filter(r => r.NetProfit > 0).length,
  avgROI: report.reduce((a, b) => a + b.ROI, 0) / report.length,
  avgMargin: report.reduce((a, b) => a + b.ProfitMargin, 0) / report.length
};
```

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
