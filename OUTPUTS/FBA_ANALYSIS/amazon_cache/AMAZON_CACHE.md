# Amazon Cache

**Location:** `OUTPUTS/FBA_ANALYSIS/amazon_cache/`

## Overview

Amazon cache files store product data retrieved from Amazon during the matching process. Each file represents one Amazon product with pricing, competition, and sales data.

---

## Directory Structure

```
OUTPUTS/FBA_ANALYSIS/amazon_cache/
├── amazon_B0DK1BVZN8_5012128582868.json
├── amazon_B0CKN59PNZ_5012128593574.json
├── amazon_B09W64GKR4_5050375010819.json
└── amazon_{ASIN}_{EAN}.json
```

---

## File: `amazon_{ASIN}_{EAN}.json`

### Naming Pattern
`amazon_{ASIN}_{EAN}.json`

- `{ASIN}` - Amazon Standard Identification Number
- `{EAN}` - Supplier EAN that matched this product

### Purpose
Cache Amazon product data to avoid repeated API/HTML requests.

### Schema

```json
{
  "asin": "B0DK1BVZN8",
  "ean": "5012128582868",
  "title": "LEGO City Great Camelot Building Set...",
  "price": 14.99,
  "buy_box_price": 14.35,
  "fba_eligible": true,
  "seller_count": {
    "fba": 5,
    "fbm": 3,
    "total": 8
  },
  "sales_rank": 12345,
  "bought_in_past_month": 50,
  "buy_box_owner": "FBA",
  "category": "Toys & Games > Building Toys",
  "prime": true,
  "extracted_at": "2025-07-26T03:15:15",
  "_search_method_used": "EAN"
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `asin` | string | Amazon ASIN |
| `ean` | string | Supplier EAN that matched |
| `title` | string | Product title on Amazon |
| `price` | float | Current listing price |
| `buy_box_price` | float | Buy box price |
| `fba_eligible` | boolean | FBA eligibility |
| `seller_count` | object | {fba, fbm, total} |
| `sales_rank` | int | Category sales rank |
| `bought_in_past_month` | float | Units sold last 30 days |
| `buy_box_owner` | string | "FBA" or "FBM" |
| `category` | string | Amazon category path |
| `prime` | boolean | Prime eligibility |
| `extracted_at` | ISO 8601 | When data was extracted |
| `_search_method_used` | string | "EAN" or "title" |

---

## Extraction Methods

### 1. EAN Search (Preferred)
```python
# Search by exact barcode
amazon_url = f"https://www.amazon.co.uk/s?k={ean}"
# Extract first result matching EAN
```

### 2. Title Search (Fallback)
```python
# When no EAN match found
amazon_url = f"https://www.amazon.co.uk/s?k={supplier_title}"
# Fuzzy match returned results
```

---

## Cache Hit Logic

```python
def get_amazon_data(asin, ean):
    cache_file = f"amazon_{asin}_{ean}.json"
    
    if cache_file.exists():
        return json.load(open(cache_file))
    
    # Fetch from Amazon
    data = extract_from_amazon(asin)
    
    # Save cache
    with open(cache_file, "w") as f:
        json.dump(data, f)
    
    return data
```

---

## Usage

### Load Cache Entry
```python
import json
from pathlib import Path

cache_dir = Path("OUTPUTS/FBA_ANALYSIS/amazon_cache")
for cache_file in cache_dir.glob("amazon_B0DK1BVZN8_*.json"):
    data = json.load(open(cache_file))
    print(data["title"])
```

### Find All FBA Products
```python
fba_products = []
cache_dir = Path("OUTPUTS/FBA_ANALYSIS/amazon_cache")
for f in cache_dir.glob("*.json"):
    data = json.load(open(f))
    if data.get("fba_eligible"):
        fba_products.append(data)
print(f"FBA eligible: {len(fba_products)}")
```

### Fast Sellers
```python
fast = []
cache_dir = Path("OUTPUTS/FBA_ANALYSIS/amazon_cache")
for f in cache_dir.glob("*.json"):
    data = json.load(open(f))
    if data.get("bought_in_past_month", 0) > 50:
        fast.append(data)
```

---

## Data Sources

Amazon data is extracted via Playwright CDP:

1. **Direct Page Scrape** - HTML parsing
2. **Keepa Extension** - Historical data (if available)
3. **SellerAmp Extension** - Competitor analysis (if available)

---

## Extractor Class

**Location:** `tools/amazon_playwright_extractor.py`

**Class:** `FixedAmazonExtractor`

**Key Methods:**
- `extract_by_asin(asin)` - Get data for specific ASIN
- `search_by_ean(ean)` - Search Amazon by barcode
- `search_by_title(title)` - Search by product title
- `extract_page_data(page)` - Parse HTML response

---

## Cache Size

Typical sizes:
- Average file: ~2-5 KB
- Full cache (10K products): ~50-100 MB

---

## Maintenance

### Clear Old Cache
```python
from pathlib import Path
from datetime import datetime, timedelta

cache_dir = Path("OUTPUTS/FBA_ANALYSIS/amazon_cache")
threshold = datetime.now() - timedelta(days=30)

for f in cache_dir.glob("*.json"):
    data = json.load(open(f))
    extracted = datetime.fromisoformat(data["extracted_at"])
    if extracted < threshold:
        f.unlink()
```

### Rebuild Cache
```python
# Delete cache files
for f in Path("OUTPUTS/FBA_ANALYSIS/amazon_cache").glob("*.json"):
    f.unlink()

# Re-run workflow - will fetch fresh data
```

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Linking Map | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json` | Match records |
| Financial Report | `OUTPUTS/FBA_ANALYSIS/financial_reports/{supplier}/fba_*.csv` | Profitability |

---

## Performance Notes

- Cache prevents redundant Amazon requests
- Each file is ~2-5 KB
- Total cache size can grow to GBs
- Consider periodic cleanup of old entries

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
