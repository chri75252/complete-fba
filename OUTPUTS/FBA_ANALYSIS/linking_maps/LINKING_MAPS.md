# Linking Maps

**Location:** `OUTPUTS/FBA_ANALYSIS/linking_maps/`

## Overview

Linking maps are the core output of the system - they establish the connection between supplier products (via EAN) and Amazon ASINs. Each entry maps a supplier's EAN to an Amazon ASIN, enabling profitability analysis.

---

## Directory Structure

```
OUTPUTS/FBA_ANALYSIS/linking_maps/
├── poundwholesale.co.uk/
│   └── linking_map.json
├── poundwholesale.co.uk__sandbox__{run_id}/
│   └── linking_map.json
├── clearance-king.co.uk/
│   └── linking_map.json
├── {supplier}.{tld}/
│   └── linking_map.json
└── {supplier}.{tld}__sandbox__{run_id}/
    └── linking_map.json
```

---

## Main vs Sandbox Linking Maps

| Type | Directory Pattern | Purpose |
|-------|------------------|---------|
| **Main** | `{supplier}.{tld}/` | Production runs, persistent analysis |
| **Sandbox** | `{supplier}.{tld}__sandbox__{run_id}/` | Isolated runs, testing |

---

## File: `linking_map.json`

### Purpose
Maps supplier EANs to Amazon ASINs with match metadata.

### Schema

```json
[
  {
    "supplier_ean": "5012128582868",
    "amazon_asin": "B0DK1BVZN8",
    "supplier_title": "Giftmaker Christmas Wishes Robin Gift Bag",
    "amazon_title": "Kraft Bags With Handles...",
    "supplier_price": 0.53,
    "amazon_price": 14.35,
    "match_method": "EAN",
    "confidence": "high",
    "created_at": "2025-07-26T03:15:15.274059",
    "supplier_url": "https://www.supplier.co.uk/product"
  }
]
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `supplier_ean` | string | Yes | EAN/barcode from supplier product |
| `amazon_asin` | string\|null | Yes | Amazon ASIN if matched, null if no match |
| `supplier_title` | string | Yes | Product title from supplier website |
| `amazon_title` | string\|null | Yes | Product title on Amazon if matched |
| `supplier_price` | float | Yes | Supplier price in GBP (inc VAT) |
| `amazon_price` | float\|null | Yes | Amazon selling price in GBP |
| `match_method` | string | Yes | How match was found: `"EAN"`, `"title"`, `"none"` |
| `confidence` | string | Yes | Match confidence: `"high"`, `"medium"`, `"low"`, `"0"` |
| `created_at` | ISO 8601 | Yes | Timestamp when entry was created |
| `supplier_url` | string | Yes | Full URL to product page on supplier site |

### Match Methods

| Method | Description | Confidence |
|--------|-------------|------------|
| `EAN` | Exact barcode match on Amazon | Typically `high` |
| `title` | Fuzzy title match when no EAN match | `medium` or `low` |
| `none` | No Amazon match found | `0` |

### Confidence Levels

| Level | Meaning |
|-------|---------|
| `high` | Direct EAN match with price alignment |
| `medium` | Title match with reasonable similarity |
| `low` | Title match with some uncertainty |
| `0` | No Amazon product found |

---

## Usage

### Read via Python
```python
import json
from pathlib import Path

lm_path = Path("OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json")
with open(lm_path) as f:
    linking_map = json.load(f)

for entry in linking_map:
    print(f"{entry['supplier_ean']} -> {entry['amazon_asin']}")
```

### Count Entries
```python
import json
lm = json.load(open("OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"))
matched = [e for e in lm if e["amazon_asin"] is not None]
print(f"Matched: {len(matched)}/{len(lm)}")
```

### Filter Profitable
```python
for entry in linking_map:
    if entry["amazon_asin"] and entry["amazon_price"]:
        margin = (entry["amazon_price"] - entry["supplier_price"]) / entry["amazon_price"]
        if margin > 0.3:
            print(f"High margin: {entry['supplier_ean']}")
```

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Supplier Cache | `OUTPUTS/cached_products/{supplier}_products_cache.json` | Source products before matching |
| Amazon Cache | `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN}.json` | Amazon product details |
| Financial Report | `OUTPUTS/FBA_ANALYSIS/financial_reports/{supplier}/fba_*.csv` | Profitability calculations |

---

## State Manager Integration

The `FixedEnhancedStateManager` tracks linking map progress:

```python
"system_progression": {
    "amazon_products_needing_analysis": N,
    "amazon_products_completed": M,
    ...
}
```

---

## Backups

No automatic backups. The file is rewritten on each save operation using atomic writes via `WindowsSaveGuardian`.

---

## Cleanup / Maintenance

To reduce size:
1. Filter entries with `amazon_asin: null` and `match_method: "none"`
2. Archive old linking maps by renaming directory
3. Combined reports can be generated from multiple linking maps

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
