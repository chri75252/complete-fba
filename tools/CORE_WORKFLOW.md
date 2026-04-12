# Core Workflow Engine

**Location:** `tools/passive_extraction_workflow_latest.py`

## Overview

The PassiveExtractionWorkflow is the main orchestrator that coordinates the entire FBA product sourcing pipeline - from supplier scraping through Amazon matching to financial analysis.

---

## Class: PassiveExtractionWorkflow

### Purpose
Coordinates all phases of the product sourcing pipeline:
1. Supplier extraction (scraping)
2. Amazon analysis (matching)
3. Linking (mapping)
4. Financial calculation

### Initialization

```python
class PassiveExtractionWorkflow:
    def __init__(
        self,
        supplier_name: str,
        workflow_config: dict,
        browser_manager: BrowserManager,
        system_config: dict = None,
        state_manager: FixedEnhancedStateManager = None,
        logger: Logger = None
    ):
        self.supplier_name = supplier_name
        self.workflow_config = workflow_config
        self.browser_manager = browser_manager
        self.state_manager = state_manager
```

---

## Workflow Phases

### Phase 1: INITIALIZATION

```python
async def _initialize(self):
    # 1. Load configuration
    # 2. Initialize or resume state
    # 3. Setup browser page
    # 4. Load category URLs
```

### Phase 2: SUPPLIER_EXTRACTION

```python
async def _run_supplier_extraction(self):
    # For each category URL:
    #   1. Navigate to page
    #   2. Extract products via ConfigurableSupplierScraper
    #   3. Apply filters (price, availability)
    #   4. Deduplicate via hash
    #   5. Append to supplier cache
    #   6. Save cache atomically
    #   7. Update progress
```

### Phase 3: AMAZON_ANALYSIS

```python
async def _run_amazon_analysis(self):
    # For each unanalyzed product:
    #   1. Search Amazon by EAN (preferred)
    #   2. Fallback to title search
    #   3. Extract Amazon data via FixedAmazonExtractor
    #   4. Cache Amazon data
    #   5. Update linking map
    #   6. Trigger financial calc at threshold
```

### Phase 4: FINANCIAL_CALCULATION

```python
def _run_financial_calculation(self):
    # When linking_map_batch_size reached:
    #   1. Call FBA_Financial_calculator.run_calculations()
    #   2. Generate CSV report
```

---

## Key Components

### ConfigurableSupplierScraper

**Location:** `tools/configurable_supplier_scraper.py`

Scrapes supplier websites using CSS selectors.

```python
scraper = ConfigurableSupplierScraper(
    page=self.page,
    supplier_config=supplier_config
)

products = await scraper.scrape_category(category_url)
```

**Key Methods:**
- `scrape_category(url)` - Extract products from category
- `scrape_all_categories()` - Full scrape
- `_extract_product_details()` - Parse individual product

### FixedAmazonExtractor

**Location:** `tools/amazon_playwright_extractor.py`

Extracts Amazon product data.

```python
extractor = FixedAmazonExtractor(
    page=self.page,
    browser_manager=self.browser_manager
)

# EAN-first search
amazon_data = await extractor.search_by_ean(ean)

# Title fallback
amazon_data = await extractor.search_by_title(title)
```

**Key Methods:**
- `search_by_ean(ean)` - Search by barcode
- `search_by_title(title)` - Fuzzy title match
- `extract_by_asin(asin)` - Direct ASIN lookup
- `extract_page_data()` - Parse Amazon HTML

---

## State Management

**Location:** `utils/fixed_enhanced_state_manager.py`

Manages resumable state for long-running sessions.

```python
state_manager = FixedEnhancedStateManager(
    supplier_name=self.supplier_name
)

# Resume or initialize
if state_manager.should_resume():
    state_manager.resume()
else:
    state_manager.initialize()

# Update progress
state_manager.advance_category(category_index)
state_manager.save_state_atomic()
```

---

## Caching Strategy

### Supplier Cache
```
OUTPUTS/cached_products/{supplier}_products_cache.json
```
- Accumulated across all categories
- Hash-based deduplication
- Atomic saves

### Amazon Cache
```
OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN}.json
```
- One file per Amazon product
- Avoids redundant fetches

### Linking Map
```
OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json
```
- Maps supplier EAN to Amazon ASIN
- Incremental updates
- Batch financial triggers

---

## Batch Processing

```python
# Config thresholds
supplier_extraction_batch_size = 100  # Products per save
linking_map_batch_size = 50           # Entries before financial calc

# Processing flow
if len(new_products) >= supplier_extraction_batch_size:
    save_supplier_cache()
    
if len(pending_analysis) >= linking_map_batch_size:
    run_calculations()
```

---

## Deduplication

```python
def _filter_unprocessed_products(self, products: list) -> list:
    # Hash each product
    product_hashes = set()
    for p in products:
        h = hashlib.md5(f"{p.ean}:{p.url}".encode()).hexdigest()
        if h not in product_hashes:
            product_hashes.add(h)
```

---

## Authentication

For authenticated suppliers:

```python
async def _handle_authentication(self):
    if self.workflow_config.get('authentication_required'):
        auth_helper = SupplierAuthenticationHelper(self.page)
        if not await auth_helper.is_authenticated():
            await auth_helper.login(self.credentials)
```

---

## Error Handling

```python
async def _safe_extract_product(self, product):
    try:
        return await self.amazon_extractor.extract(product)
    except Exception as e:
        self.logger.warning(f"Extract failed: {e}")
        return None
```

---

## Memory Management

```python
# Smart memory clearing
if len(products_in_memory) > 500:
    recent = products_in_memory[-100:]
    products_in_memory.clear()
    products_in_memory.extend(recent)
    gc.collect()
```

---

## Workflow Configuration

**Source:** `config/system_config.json`

```json
{
  "system": {
    "max_products": 1000000,
    "max_products_per_category": 1000,
    "supplier_extraction_batch_size": 100,
    "linking_map_batch_size": 50,
    "reuse_browser": true
  },
  "processing_limits": {
    "min_price_gbp": 0.01,
    "max_price_gbp": 20.0
  }
}
```

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Supplier Scraper | `tools/configurable_supplier_scraper.py` | Supplier extraction |
| Amazon Extractor | `tools/amazon_playwright_extractor.py` | Amazon matching |
| Financial Calculator | `tools/FBA_Financial_calculator.py` | Profitability calc |
| State Manager | `utils/fixed_enhanced_state_manager.py` | Resumable state |
| Browser Manager | `utils/browser_manager.py` | Chrome CDP |

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
