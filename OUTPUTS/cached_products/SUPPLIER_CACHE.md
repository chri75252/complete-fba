# Supplier Cache (Cached Products)

**Location:** `OUTPUTS/cached_products/`

## Overview

Supplier cache files store all scraped products from wholesale supplier websites. These are the raw inputs that feed into the Amazon matching pipeline.

---

## Directory Structure

```
OUTPUTS/cached_products/
├── poundwholesale-co-uk_products_cache.json
├── clearance-king-co-uk_products_cache.json
├── efghousewares-co-uk_products_cache.json
├── angelwholesale-co-uk_products_cache.json
└── {supplier}_products_cache.json
```

---

## File: `{supplier}_products_cache.json`

### Purpose
Stores all products scraped from a supplier website, before Amazon matching.

### Schema

```json
[
  {
    "title": "'Welcome' Wellies Door Mat",
    "price": 1.18,
    "url": "https://www.supplier.co.uk/welcome-wellies-door-mat",
    "ean": "5055056750510",
    "sku": "5051",
    "availability": "Out of stock",
    "image_url": "https://www.supplier.co.uk/media/...",
    "source_url": "https://www.supplier.co.uk/category",
    "scraped_at": "2025-07-29T04:35:25.293789"
  }
]
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Product display name |
| `price` | float | Yes | Price in GBP (typically inc VAT) |
| `url` | string | Yes | Full URL to product page |
| `ean` | string\|null | Yes | EAN/barcode (may be null) |
| `sku` | string\|null | No | Supplier SKU |
| `availability` | string | Yes | Stock status: `"In stock"`, `"Out of stock"`, etc. |
| `image_url` | string\|null | No | Product image URL |
| `source_url` | string | Yes | Category URL where product was found |
| `scraped_at` | ISO 8601 | Yes | When product was scraped |

### Availability Values

Common values observed:
- `"In stock"`
- `"Out of stock"`
- `"Limited availability"`
- `"Pre-order"`
- `"Discontinued"`

---

## Scraping Process

```
1. Load category URLs from config
2. For each category URL:
   a. Navigate to page
   b. Extract product cards using CSS selectors
   c. For each product:
      - Parse title, price, EAN, URL
      - Apply price filters (min/max)
      - Deduplicate (hash lookup)
      - Add to cache
   d. Handle pagination
3. Save cache atomically
```

---

## Deduplication

Products are deduplicated using a hash of `(ean, url)` to prevent duplicates across categories.

```python
product_hash = hashlib.md5(f"{ean}:{url}".encode()).hexdigest()
if product_hash not in existing_hashes:
    products.append(product)
```

---

## Usage

### Load All Products
```python
import json
from pathlib import Path

cache = json.load(open("OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"))
print(f"Total products: {len(cache)}")
```

### Filter by Price Range
```python
in_stock = [p for p in cache if p["availability"] == "In stock"]
in_range = [p for p in in_stock if 0.01 <= p["price"] <= 20.0]
print(f"Products in stock & price range: {len(in_range)}")
```

### Filter by EAN
```python
with_ean = [p for p in cache if p["ean"]]
print(f"Products with EAN: {len(with_ean)}")
```

### Find by Category
```python
category_products = [p for p in cache if "/toys/" in p["source_url"]]
```

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Processing State | `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json` | Progress tracking |
| Linking Map | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json` | After Amazon matching |

---

## Scraper Class

**Location:** `tools/configurable_supplier_scraper.py`

**Class:** `ConfigurableSupplierScraper`

**Key Methods:**
- `scrape_category(url)` - Extract products from single category
- `scrape_all_categories()` - Full scrape
- `get_products()` - Return cached products

---

## Cache Size

Typical sizes (approximate):
- `poundwholesale-co-uk_products_cache.json`: ~118,000 entries (~40MB)
- `clearance-king-co-uk_products_cache.json`: ~10,000 entries (~3MB)

---

## Maintenance

### Reduce Size
1. Filter out-of-stock products
2. Remove products without EAN (unmatchable)
3. Archive to dated file

### Example Archive Script
```python
import json
from pathlib import Path
from datetime import datetime

cache = json.load(open("poundwholesale-co-uk_products_cache.json"))
in_stock = [p for p in cache if p["availability"] == "In stock"]
date = datetime.now().strftime("%Y%m%d")
with open(f"archive/poundwholesale_{date}.json", "w") as f:
    json.dump(in_stock, f, indent=2)
```

---

## Data Flow

```
Supplier Website
      │
      ▼
ConfigurableSupplierScraper
      │
      ▼
Supplier Cache (JSON)
      │
      ├──► PassiveExtractionWorkflow
      │         │
      │         ▼
      │    FixedAmazonExtractor (EAN/title match)
      │         │
      │         ▼
      │    Linking Map
      │         │
      │         ▼
      │    FBA_Financial_calculator
      │         │
      │         ▼
      │    Financial Report (CSV)
      │
      └──► Dashboard Display
```

---

## Supplier Config

CSS selectors used for scraping are defined in:
`config/supplier_configs/{supplier}.{tld}.json`

```json
{
  "product_item": ".product-item",
  "title": ".product-title",
  "price": ".price",
  "ean": ".ean-code",
  "url": ".product-link"
}
```

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
