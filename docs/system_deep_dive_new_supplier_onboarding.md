# System Deep Dive: New Supplier Onboarding
**Version**: 1.0
**Date**: October 5, 2025
**Audience**: Technical implementers and system architects
**Related**: `new_supplier_analysis_guide.md` (Quick Reference)

---

## Table of Contents
1. [System Architecture Overview](#1-system-architecture-overview)
2. [Config-Driven Implementation](#2-config-driven-implementation)
3. [Execution Flow](#3-execution-flow)
4. [Component Interactions](#4-component-interactions)
5. [Configuration Surface](#5-configuration-surface)
6. [Output Artifacts](#6-output-artifacts)
7. [Authentication Architecture](#7-authentication-architecture)
8. [State Management](#8-state-management)
9. [Technical Implementation Details](#9-technical-implementation-details)
10. [Advanced Topics](#10-advanced-topics)

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRY LAYER (Per Supplier)                   │
├─────────────────────────────────────────────────────────────────┤
│  run_custom_clearance_king.py  │  run_custom_poundwholesale.py │
└────────────┬────────────────────┴─────────────────┬─────────────┘
             │                                       │
             ▼                                       ▼
┌────────────────────────────────────────────────────────────────┐
│              CONFIGURATION LAYER (JSON-Driven)                 │
├────────────────────────────────────────────────────────────────┤
│  system_config.json  │  supplier_configs/  │  *_categories.json│
└────────────┬────────────────────┬─────────────────┬────────────┘
             │                     │                  │
             ▼                     ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 SHARED EXECUTION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  passive_extraction_workflow_latest.py (12,028 lines, shared)  │
│  configurable_supplier_scraper.py (selector-driven)            │
│  standalone_playwright_login.py (unified auth)                 │
│  FBA_Financial_calculator.py (profitability)                   │
│  amazon_playwright_extractor.py (Amazon data)                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│           SUPPLIER-SPECIFIC LAYER (Adapters Only)               │
├─────────────────────────────────────────────────────────────────┤
│  tools/clearance_king/supplier_authentication_service.py        │
│  tools/poundwholesale/supplier_authentication_service.py        │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UTILITY LAYER (Shared)                       │
├─────────────────────────────────────────────────────────────────┤
│  browser_manager.py  │  path_manager.py  │  state_manager.py   │
│  logger.py │ windows_save_guardian.py │ hash_lookup_optimizer.py│
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│            OUTPUT LAYER (Per-Supplier Isolation)                │
├─────────────────────────────────────────────────────────────────┤
│  OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/                  │
│  OUTPUTS/cached_products/{supplier}_products_cache.json         │
│  OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json│
│  OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN}.json     │
│  OUTPUTS/FBA_ANALYSIS/financial_reports/fba_financial_report_*.csv│
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Categories

| Category | Scope | Examples | Duplication |
|----------|-------|----------|-------------|
| **Shared Components** | All suppliers | `passive_extraction_workflow_latest.py`, `standalone_playwright_login.py` | ❌ Never |
| **Config Files** | Per supplier | `config/supplier_configs/{domain}.json` | ✅ Required |
| **Auth Adapters** | Per supplier | `tools/{supplier}/supplier_authentication_service.py` | ✅ Required |
| **Entry Scripts** | Per supplier | `run_custom_{supplier}.py` | ✅ Required |
| **Utility Layer** | All suppliers | `browser_manager.py`, `state_manager.py` | ❌ Never |

---

## 2. Config-Driven Implementation

### 2.1 Implementation History

**Date**: October 1-2, 2025
**Goal**: Eliminate hardcoded supplier names, enable config-only supplier onboarding
**Status**: ✅ Verified working with poundwholesale (Oct 2, 120-second test)

### 2.2 Code Changes Applied

#### Change #1: Categories Config Path
**File**: `tools/passive_extraction_workflow_latest.py`
**Line**: 1834-1841

**Before**:
```python
config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
```

**After**:
```python
categories_config_path = self.workflow_config.get("categories_config_path")
if not categories_config_path:
    # Backwards compatibility fallback
    categories_config_path = f"config/{self.supplier_name.replace('.', '_')}_categories.json"
    self.log.warning(f"⚠️ categories_config_path not in config, using fallback: {categories_config_path}")

config_path = Path(categories_config_path)
```

**Impact**:
- Eliminates hardcoded `"poundwholesale"`
- Reads path from workflow config
- Provides fallback for backwards compatibility
- Zero edits needed for new suppliers

#### Change #2: Linking Map Instance Variables
**File**: `tools/passive_extraction_workflow_latest.py`
**Lines Deleted**: 632-635 (global constants)
**Lines Added**: 1400-1404 (instance variables)

**Deleted**:
```python
# Global constant for persistent linking map in dedicated directory
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")
```

**Added (in `__init__`)**:
```python
# Initialize supplier-specific linking map path
self.linking_map_path = get_linking_map_path(self.supplier_name)
self.linking_map_dir = self.linking_map_path.parent
os.makedirs(self.linking_map_dir, exist_ok=True)
self.log.info(f"✅ Linking map directory: {self.linking_map_dir}")
```

**Impact**:
- Removes global constants causing cross-supplier conflicts
- Per-instance linking map paths
- Automatic directory creation per supplier
- Prevents race conditions if running multiple suppliers

#### Change #3 (New): Detail-Aware Field Extraction (Multi-site Safe)
**File**: `tools/configurable_supplier_scraper.py`

**What changed**:
- Title extraction prefers `field_mappings.product_detail_title` when present, then falls back to `field_mappings.title`, and finally to semantic/meta fallbacks (OG/Twitter, headings, `<title>`).
- EAN extraction remains domain-aware with JSON-LD/meta/pattern fallbacks (digits-only normalization).
- Availability uses `field_mappings.availability` with generic fallbacks.
- URL uses `field_mappings.url` with robust absolute URL joining.

**Why**:
- Many suppliers (e.g., CK) expose different selectors on category vs detail pages; this guarantees non-null titles on detail pages and reliable field extraction across sites.

**References**:
- `tools/configurable_supplier_scraper.py:1676` (selector loading)
- `:2130` (title), `:2152` (price), `:3210` (ean), `:3290` (availability)

#### Change #4 (New): Output Schema Simplification (Omit sku/image)
**Files**: `tools/configurable_supplier_scraper.py` (product dict builders)

**What changed**:
- Removed `sku` and `image_url` from product outputs to prevent cross-site drift and brittle failures.

**Why**:
- `sku` was often polluted; `image_url` structure varied and was non-essential for matching/dedup.

#### Change #5 (New): Stable Keys with Normalization + Validated EAN
**File**: `tools/passive_extraction_workflow_latest.py`

**What changed**:
- All stable_key call-sites use `stable_key(normalize_url(url), valid_ean)`.
- EAN is validated (only 8/12/13 digits) before use; otherwise key falls back to URL.

**References**:
- `_valid_ean_for_key`: `:1339`
- Call-sites: `:1572–1579`, `:4592`, `:4607`, `:4679`, `:5468`

#### Change #6 (New): Accumulator In-Place Update (Periodic Saves)
**File**: `tools/passive_extraction_workflow_latest.py`

**What changed**:
- After atomic save, the in-memory accumulator is updated in-place (`list[:] = new_list`) to preserve the list reference used by progress/appends.

**Why**:
- Prevents the “stuck at 1” counter and skipped periodic saves observed when the reference was replaced with a copy.

#### Change #3: Manifest Path
**File**: `tools/passive_extraction_workflow_latest.py`
**Line**: 7345

**Before**:
```python
manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
```

**After**:
```python
manifest_path = Path("OUTPUTS") / "manifests" / self.supplier_name / f"{slug}.json"
```

**Impact**:
- Uses `self.supplier_name` (set from config in `__init__`)
- Automatic per-supplier manifest directories
- Zero hardcoded supplier names

### 2.3 Verification Results

**Test Date**: October 2, 2025
**Duration**: 120 seconds
**Supplier**: poundwholesale

**Evidence**:
```
✅ Linking map directory: OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk
✅ Categories loaded: 230 predefined URLs from config/poundwholesale_categories.json
✅ State initialized: 10,561 products in cache, 10,746 in linking map
```

**Benefits Realized**:
- ✅ Zero workflow file edits
- ✅ Automatic directory isolation
- ✅ Config-driven category loading
- ✅ Time savings: 45-90 minutes per supplier

---

## 3. Execution Flow

### 3.1 Complete Workflow Sequence

```
START
  │
  ├─► 1. Entry Script Execution (run_custom_{supplier}.py)
  │     ├─► Load system config
  │     ├─► Get workflow config for '{supplier}_workflow'
  │     ├─► Get credentials for supplier domain
  │     └─► Initialize BrowserManager (Chrome debug port 9222)
  │
  ├─► 2. Authentication Phase
  │     ├─► Create supplier auth helper (page-based)
  │     ├─► Check if already authenticated (via price verification)
  │     │    └─► Uses StandalonePlaywrightLogin.verify_price_access()
  │     ├─► If not authenticated:
  │     │    └─► Login via StandalonePlaywrightLogin.login_workflow()
  │     │         ├─► Load selectors from supplier config
  │     │         ├─► Fill email field (force=True for hidden elements)
  │     │         ├─► Fill password field (force=True for hidden elements)
  │     │         ├─► Click login button
  │     │         └─► Verify price access on test product
  │     └─► Return authentication status
  │
  ├─► 3. Workflow Initialization (PassiveExtractionWorkflow)
  │     ├─► Set supplier_name from workflow config
  │     ├─► Load categories_config_path from config (or fallback)
  │     ├─► Initialize linking map paths (per-supplier via path_manager)
  │     ├─► Create output directories (automatic per-supplier)
  │     ├─► Initialize state manager (EnhancedStateManager)
  │     └─► Build hash indexes (EAN, URL, ASIN for O(1) lookups)
  │
  ├─► 4. Category Processing Loop
  │     │
  │     ├─► For each category URL:
  │     │    │
  │     │    ├─► 4.1 Authentication Check (before category batch)
  │     │    │     └─► Verify session still active (every N products)
  │     │    │
  │     │    ├─► 4.2 Supplier Scraping (ConfigurableSupplierScraper)
  │     │    │     ├─► Load supplier selectors from config
  │     │    │     ├─► Navigate to category page
  │     │    │     ├─► Extract products (title, price, URL, EAN, image)
  │     │    │     ├─► Handle pagination (URL-based or button-based)
  │     │    │     └─► Save to supplier cache: cached_products/{supplier}_products_cache.json
  │     │    │
  │     │    ├─► 4.3 Product Processing Loop
  │     │    │     │
  │     │    │     ├─► For each product:
  │     │    │     │    │
  │     │    │     │    ├─► Check if already processed (state manager)
  │     │    │     │    │
  │     │    │     │    ├─► 4.3.1 Amazon Extraction (AmazonPlaywrightExtractor)
  │     │    │     │    │     ├─► Search Amazon by EAN (or title fallback)
  │     │    │     │    │     ├─► Extract Amazon product data (ASIN, price, rank, etc.)
  │     │    │     │    │     └─► Save to amazon_cache/amazon_{ASIN}_{EAN}.json
  │     │    │     │    │
  │     │    │     │    ├─► 4.3.2 Update Linking Map
  │     │    │     │    │     ├─► Map supplier EAN → Amazon ASIN
  │     │    │     │    │     └─► Save to linking_maps/{supplier}/linking_map.json
  │     │    │     │    │
  │     │    │     │    ├─► 4.3.3 Financial Analysis (FBA_Financial_calculator)
  │     │    │     │    │     ├─► Calculate FBA fees, VAT, shipping
  │     │    │     │    │     ├─► Calculate profit margin
  │     │    │     │    │     └─► If profitable: Add to financial report CSV
  │     │    │     │    │
  │     │    │     │    └─► 4.3.4 State Update
  │     │    │     │          └─► Mark product as processed (atomic save)
  │     │    │     │
  │     │    │     └─► Save category state
  │     │    │
  │     │    └─► Mark category complete
  │     │
  │     └─► All categories processed
  │
  └─► 5. Completion & Cleanup
        ├─► Save final state
        ├─► Generate summary reports
        └─► Cleanup browser connections
END
```

### 3.2 Script Execution Chronology

**Verified from logs (Oct 2, 2025 test)**:

```
1. run_custom_poundwholesale.py              ← Entry point
2. config.system_config_loader               ← Load config
3. tools.supplier_authentication_service      ← Authentication
4. tools.standalone_playwright_login          ← Login workflow
5. tools.passive_extraction_workflow_latest   ← Main workflow
6. utils.enhanced_state_manager               ← State loading
7. tools.configurable_supplier_scraper        ← Category scraping
8. tools.amazon_playwright_extractor          ← Amazon extraction
9. tools.FBA_Financial_calculator             ← Profitability analysis
10. utils.enhanced_state_manager              ← State saving (atomic)
```

---

## 4. Component Interactions

### 4.1 Authentication Flow

```
Entry Script
    │
    ├─► Create {Supplier}AuthenticationHelper(page)
    │    │
    │    ├─► is_authenticated() called
    │    │    │
    │    │    ├─► Load supplier config from config/supplier_configs/{domain}.json
    │    │    ├─► Create StandalonePlaywrightLogin instance
    │    │    ├─► Set login_handler.page = self.page
    │    │    └─► Call login_handler.verify_price_access(page)
    │    │         │
    │    │         ├─► Navigate to test_product_url
    │    │         ├─► Check for price selectors from config
    │    │         └─► Return True if price visible, False otherwise
    │    │
    │    └─► login(credentials) called if not authenticated
    │         │
    │         ├─► Load supplier config
    │         ├─► Create StandalonePlaywrightLogin(email, password, supplier_config)
    │         ├─► Set login_handler.page = self.page
    │         └─► Call login_handler.login_workflow()
    │              │
    │              ├─► Check if Page already exists (skip CDP if yes)
    │              ├─► Bring page to front
    │              ├─► Check if already logged in (short-circuit)
    │              ├─► If not logged in:
    │              │    ├─► Navigate to login page
    │              │    ├─► Fill email field (config-driven selector)
    │              │    ├─► Fill password field (config-driven selector, force=True)
    │              │    ├─► Click login button (config-driven selector)
    │              │    └─► Verify login success via price access
    │              └─► Return LoginResult(success, method, price_verified)
    │
    └─► Return authentication status to workflow
```

### 4.2 Supplier Authentication Service Pattern

**Architecture**: Page-based thin wrappers around StandalonePlaywrightLogin

**Template**:
```python
class {Supplier}AuthenticationHelper:
    def __init__(self, page: Page):
        # Type guard ensures Page object (not BrowserManager)
        assert hasattr(page, "goto"), "Expects Playwright Page object"
        self.page = page
        self.log = logging.getLogger(__name__)

    async def is_authenticated(self) -> bool:
        """Uses StandalonePlaywrightLogin.verify_price_access()"""
        try:
            import json
            config_path = os.path.join("config", "supplier_configs", "{domain}.json")
            with open(config_path, 'r') as f:
                supplier_config = json.load(f)

            login_handler = StandalonePlaywrightLogin(
                supplier_config=supplier_config,
                test_product_url=supplier_config['login_config']['test_product_url']
            )
            login_handler.page = self.page

            return await login_handler.verify_price_access(self.page)
        except Exception as e:
            self.log.error(f"Error checking authentication: {e}")
            return False

    async def login(self, credentials: Dict[str, str]) -> bool:
        """Uses StandalonePlaywrightLogin.login_workflow()"""
        try:
            import json
            config_path = os.path.join("config", "supplier_configs", "{domain}.json")
            with open(config_path, 'r') as f:
                supplier_config = json.load(f)

            login_handler = StandalonePlaywrightLogin(
                email=credentials['username'],
                password=credentials['password'],
                supplier_config=supplier_config
            )
            login_handler.page = self.page

            login_result = await login_handler.login_workflow()
            return login_result.success
        except Exception as e:
            self.log.error(f"Login failed: {e}")
            return False

# Alias for workflow compatibility
SupplierAuthenticationService = {Supplier}AuthenticationHelper
```

**Key Points**:
- ✅ Uses StandalonePlaywrightLogin for actual logic
- ✅ Loads supplier config for selectors
- ✅ Type guard ensures Page object (not BrowserManager)
- ✅ Price-first authentication detection
- ✅ Config-driven selector loading

### 4.3 Scraper-Workflow Interaction

```
PassiveExtractionWorkflow
    │
    ├─► Load categories from categories_config_path
    │    └─► Returns List[str] of category URLs
    │
    ├─► For each category:
    │    │
    │    ├─► Create ConfigurableSupplierScraper instance
    │    ├─► Call scraper.scrape_category(category_url)
    │    │    │
    │    │    ├─► Load supplier config from config/supplier_configs/{domain}.json
    │    │    ├─► Extract field_mappings (title, price, URL, EAN, etc.)
    │    │    ├─► Navigate to category URL
    │    │    ├─► For each page:
    │    │    │    ├─► Select product items (product_item selector)
    │    │    │    ├─► For each product:
    │    │    │    │    ├─► Extract fields using CSS selectors
    │    │    │    │    └─► Add to products list
    │    │    │    └─► Navigate to next page (pagination config)
    │    │    │
    │    │    └─► Return List[Product]
    │    │
    │    └─► Save products to supplier cache
    │         └─► cached_products/{supplier}_products_cache.json
    │
    └─► Process products for Amazon matching and financial analysis
```

---

## 5. Configuration Surface

### 5.1 System Config Structure

**File**: `config/system_config.json`

```json
{
  "workflows": {
    "{supplier}_workflow": {
      "supplier_name": "{domain}",
      "supplier_url": "https://www.{domain}",
      "categories_config_path": "config/{supplier}_categories.json",
      "use_predefined_categories": true,
      "ai_client": null,
      "max_categories_to_process": null,
      "max_products_per_category": null,
      "max_price_gbp": 50,
      "min_price_gbp": 0.01
    }
  },
  "credentials": {
    "{domain}": {
      "username": "your_username",
      "password": "your_password"
    }
  },
  "chrome_debug_port": 9222,
  "output_root": "OUTPUTS"
}
```

**Field Descriptions**:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `supplier_name` | string | ✅ | Supplier domain (used for path construction) |
| `supplier_url` | string | ✅ | Base URL for supplier website |
| `categories_config_path` | string | ✅ | Path to categories JSON file |
| `use_predefined_categories` | boolean | ✅ | Must be `true` for HYBRID mode |
| `ai_client` | null | ✅ | Must be `null` for HYBRID mode |
| `max_categories_to_process` | number/null | ❌ | Limit categories (null = all) |
| `max_products_per_category` | number/null | ❌ | Limit products per category |
| `max_price_gbp` | number | ❌ | Maximum product price filter |
| `min_price_gbp` | number | ❌ | Minimum product price filter |

### 5.2 Supplier Config Structure

**File**: `config/supplier_configs/{domain}.json`

**Complete Template**:
```json
{
  "supplier_id": "{domain}",
  "supplier_name": "{Human Readable Name}",
  "base_url": "https://www.{domain}/",

  "login_config": {
    "login_path": "/customer/account/login/",
    "test_product_url": "https://www.{domain}/test-product-url",
    "price_selectors": [
      ".price-box .price",
      "span.price",
      ".price-wrapper .price"
    ]
  },

  "authentication": {
    "login_url": "https://www.{domain}/customer/account/login/",
    "login_selectors": {
      "email_field": "input#email",
      "password_field": "input#pass",
      "login_button": "button#send2.action.login.primary"
    },
    "authentication_check_selectors": [
      ".customer-welcome",
      ".logged-in",
      ".customer-name"
    ]
  },

  "field_mappings": {
    "product_item": [
      "li.item.product.product-item",
      ".product-item"
    ],
    "title": [
      "a.product-item-link",
      ".product-name a"
    ],
    "price": [
      ".price-box .price",
      "span.price",
      ".product-item .price"
    ],
    "url": [
      "a.product-item-link",
      ".product-link"
    ],
    "image": [
      "img.product-image-photo",
      ".product-image img"
    ],
    "ean": [
      "span.ean-code",
      "meta[itemprop='gtin13']",
      "[data-ean]"
    ],
    "out_of_stock": [
      ".stock.unavailable",
      "span:contains('Out of stock')"
    ]
  },

  "pagination": {
    "pattern": "https://www.{domain}/category?page={page}",
    "use_url_navigation": true,
    "next_button_selector": [
      "a.action.next",
      ".pagination .next a"
    ]
  },

  "scraping_config": {
    "rate_limit": {
      "requests_per_minute": 30,
      "delay_between_requests": 2.0
    }
  }
}
```

**Critical Fields**:

| Section | Field | Purpose | Notes |
|---------|-------|---------|-------|
| `login_config` | `test_product_url` | Product URL for price verification | Must require login to see price |
| `login_config` | `price_selectors` | CSS selectors for price elements | Multiple fallbacks recommended |
| `authentication.login_selectors` | `email_field` | Email input selector | Used by StandalonePlaywrightLogin |
| `authentication.login_selectors` | `password_field` | Password input selector | Force interaction enabled |
| `authentication.login_selectors` | `login_button` | Login button selector | Submit form trigger |
| `field_mappings` | `ean` | Barcode/EAN selectors | Critical for Amazon matching |
| `pagination` | `use_url_navigation` | URL vs button pagination | `true` for URL params, `false` for buttons |

### 5.3 Categories Config Structure

**File**: `config/{supplier}_categories.json`

```json
{
  "category_urls": [
    "https://www.{domain}/category-1",
    "https://www.{domain}/category-2",
    "https://www.{domain}/category-3"
  ]
}
```

**Requirements**:
- ✅ Must be valid JSON array
- ✅ URLs must be absolute (include `https://`)
- ✅ URLs must be category listing pages (not individual products)
- ✅ URLs must be accessible without authentication

---

## 6. Output Artifacts

### 6.1 Output Directory Structure

```
OUTPUTS/
├── cached_products/
│   ├── clearance-king-co-uk_products_cache.json
│   └── poundwholesale-co-uk_products_cache.json
│
├── FBA_ANALYSIS/
│   ├── linking_maps/
│   │   ├── clearance-king.co.uk/
│   │   │   └── linking_map.json
│   │   └── poundwholesale.co.uk/
│   │       └── linking_map.json
│   │
│   ├── amazon_cache/
│   │   ├── amazon_B001234ABC_1234567890123.json
│   │   └── amazon_B987654XYZ_9876543210987.json
│   │
│   └── financial_reports/
│       └── fba_financial_report_20251004_120530.csv
│
├── CACHE/
│   └── processing_states/
│       ├── clearance-king_co_uk_processing_state.json
│       └── poundwholesale_co_uk_processing_state.json
│
└── DIAGNOSTICS/
    └── save_telemetry.log
```

### 6.2 File Naming Patterns

| File Type | Pattern | Example |
|-----------|---------|---------|
| Supplier Cache | `{supplier_underscore}_products_cache.json` | `poundwholesale_co_uk_products_cache.json` |
| Linking Map Directory | `{supplier_dot}/` | `clearance-king.co.uk/` |
| Linking Map File | `{supplier_dot}/linking_map.json` | `poundwholesale.co.uk/linking_map.json` |

### 6.3 Supplier Cache Schema (Authoritative)

- Path: `OUTPUTS/cached_products/{supplier}_products_cache.json`
- Schema (per product):
  - `title`: string (detail-aware fallback applied)
  - `price`: number (GBP)
  - `url`: string (absolute)
  - `normalized_url`: string (canonical URL)
  - `ean`: string (digits only)
  - `availability`: string (when available)
  - `source_url`: string (category context)
  - `scraped_at`: ISO timestamp

Notes:
- `sku` and `image_url` are intentionally omitted across suppliers to minimize cross-site discrepancies and avoid brittle failures.
| State File | `{supplier_underscore}_processing_state.json` | `clearance-king_co_uk_processing_state.json` |
| Amazon Cache | `amazon_{ASIN}_{EAN}.json` | `amazon_B0BV7BYNYD_766871477975.json` |
| Financial Report | `fba_financial_report_{timestamp}.csv` | `fba_financial_report_20251004_120530.csv` |

**Domain Transformation Rules**:
- **Underscore format** (`_`): File names → `clearance-king.co.uk` becomes `clearance_king_co_uk`
- **Dot format** (`.`): Directory names → `clearance-king.co.uk` remains `clearance-king.co.uk`

### 6.3 Linking Map Schema

**File**: `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json`

```json
{
  "5056175900534": {
    "EAN": "5056175900534",
    "ASIN": "B0D8KH2KBD",
    "supplier_url": "https://www.poundwholesale.co.uk/product-url",
    "match_method": "ean_direct",
    "confidence": 1.0,
    "timestamp": "2025-10-02T09:21:15.123456",
    "amazon_title": "Product Title from Amazon",
    "supplier_title": "Product Title from Supplier"
  },
  "NO_MATCH_https://supplier.com/product": {
    "supplier_url": "https://supplier.com/product",
    "match_method": "none",
    "confidence": 0,
    "timestamp": "2025-10-02T09:22:30.654321",
    "reason": "No EAN found, title search yielded no results"
  }
}
```

**Entry Types**:
1. **EAN-keyed successful match**: `{EAN}` → Full product data
2. **URL-keyed no-match**: `NO_MATCH_{URL}` → No Amazon match found

**Field Descriptions**:
- `match_method`: `"ean_direct"`, `"title_fallback"`, `"none"`
- `confidence`: 0.0 to 1.0 (1.0 = perfect EAN match)
- `timestamp`: ISO 8601 format

### 6.4 Processing State Schema

**File**: `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json`

```json
{
  "last_updated": "2025-10-02T09:22:24.123456",
  "current_category_url": "https://www.poundwholesale.co.uk/toys/wholesale-big-boys-toys-gadgets",
  "current_category_index": 0,
  "processed_products": {
    "https://www.poundwholesale.co.uk/product-1": true,
    "https://www.poundwholesale.co.uk/product-2": true
  },
  "processed_categories": [
    "https://www.poundwholesale.co.uk/category-1"
  ],
  "total_products_processed": 10561,
  "total_categories_processed": 45
}
```

**Resume Logic**:
- Workflow loads state on startup
- Skips already processed categories
- Skips already processed products within current category
- Enables interruption and resumption without data loss

---

## 7. Authentication Architecture

### 7.1 StandalonePlaywrightLogin Integration

**File**: `tools/standalone_playwright_login.py`

**Key Features**:
1. **Config-driven selectors**: Reads from `supplier_config['authentication']['login_selectors']`
2. **Force interaction**: Uses `force=True` for hidden password fields
3. **Price verification**: Tests authentication by checking wholesale price access
4. **Page reuse**: Skips CDP connection if Page already exists

**Selector Loading Priority**:
```python
# 1. Config-driven (highest priority)
config_selectors = supplier_config.get('authentication', {}).get('login_selectors', {})
if config_selectors.get('email_field'):
    email_selectors.append(config_selectors['email_field'])

# 2. Platform defaults (Magento, WooCommerce, etc.)
DEFAULT_EMAIL_SELECTORS = [
    "input[name='login[username]']",  # Magento
    "input#email",                    # Generic
    "input[type='email']"             # Fallback
]

# 3. Use first working selector
for selector in email_selectors:
    element = page.locator(selector).first
    if await element.is_visible():
        await element.fill(email)
        break
```

### 7.2 Authentication Flow Fixes (October 2025)

#### Fix #1: BrowserManager vs Page Object
**Issue**: Passing BrowserManager instead of Page caused `'BrowserManager' object has no attribute 'goto'`

**Solution**:
```python
# WRONG (old pattern)
auth_service = SupplierAuthenticationService(self.browser_manager)

# CORRECT (fixed pattern)
page = await self.browser_manager.get_page(supplier_url, reuse_existing=True)
auth_service = SupplierAuthenticationService(page)
```

#### Fix #2: Unnecessary CDP Connect
**Issue**: StandalonePlaywrightLogin attempted CDP connect even when Page already provided

**Solution**:
```python
async def login_workflow(self) -> LoginResult:
    # Skip CDP if Page already exists
    if self.page is not None and hasattr(self.page, "goto"):
        log.debug("ℹ️ Reusing provided Playwright Page; skipping CDP connect")
    else:
        # Connect to browser via CDP
        if not await self.connect_browser():
            return LoginResult(success=False, error_message="Failed to connect to browser")
```

#### Fix #3: Defensive BrowserManager Guard
**Issue**: Some code paths might still pass BrowserManager by mistake

**Solution**:
```python
async def verify_price_access(self, page: Page = None) -> bool:
    target_page = page or self.page

    # Defensive guard - resolve BrowserManager to Page if needed
    if target_page is not None and not hasattr(target_page, "goto") and hasattr(target_page, "get_page"):
        try:
            target_page = await target_page.get_page(base, reuse_existing=True)
            log.debug("ℹ️ Resolved BrowserManager to Playwright Page")
        except Exception as resolve_err:
            log.error(f"❌ Could not resolve Page: {resolve_err}")
            return False
```

### 7.3 Price-First Authentication Detection

**Rationale**: Most reliable indicator of successful login is ability to see wholesale prices

**Implementation**:
```python
async def verify_price_access(self, page: Page = None) -> bool:
    # Navigate to test product (requires login for price)
    await page.goto(test_product_url)

    # Check for price selectors from config
    for selector in price_selectors:
        try:
            element = page.locator(selector).first
            if await element.is_visible(timeout=2000):
                price_text = await element.inner_text()
                if price_text and any(char.isdigit() for char in price_text):
                    log.info("✅ Price visible → authenticated")
                    return True
        except:
            continue

    log.info("❌ Price not visible → not authenticated")
    return False
```

---

## 8. State Management

### 8.1 EnhancedStateManager

**File**: `utils/enhanced_state_manager.py`

**Responsibilities**:
1. Track processed products and categories
2. Enable resume after interruption
3. Atomic state persistence (WindowsSaveGuardian)
4. Progress tracking and reporting

**Key Methods**:
```python
class EnhancedStateManager:
    async def mark_product_processed(self, product_url: str):
        """Atomically marks product as processed"""
        self.processed_products[product_url] = True
        await self._save_state()  # Uses WindowsSaveGuardian

    async def is_product_processed(self, product_url: str) -> bool:
        """Checks if product already processed"""
        return product_url in self.processed_products

    async def mark_category_complete(self, category_url: str):
        """Marks entire category as complete"""
        self.processed_categories.append(category_url)
        await self._save_state()

    async def get_resume_context(self) -> Dict:
        """Returns context for resuming workflow"""
        return {
            "current_category_url": self.current_category_url,
            "current_category_index": self.current_category_index,
            "total_processed": len(self.processed_products)
        }
```

### 8.2 Atomic State Persistence

**Mechanism**: WindowsSaveGuardian (Windows-specific file handling)

```python
from utils.windows_save_guardian import WindowsSaveGuardian

async def _save_state(self):
    """Atomic state save with Windows compatibility"""
    state_data = {
        "last_updated": datetime.now().isoformat(),
        "current_category_url": self.current_category_url,
        "processed_products": self.processed_products,
        "processed_categories": self.processed_categories
    }

    # Atomic save prevents corruption on interruption
    await WindowsSaveGuardian.safe_save(
        file_path=self.state_file_path,
        data=state_data,
        encoding='utf-8'
    )
```

**Benefits**:
- ✅ Prevents state corruption on sudden termination
- ✅ Ensures parent directories exist
- ✅ Handles Windows file locking
- ✅ UTF-8 encoding for all platforms

---

## 9. Technical Implementation Details

### 9.1 Hash Lookup Optimization

**File**: `utils/hash_lookup_optimizer.py`

**Purpose**: O(1) lookups for 10K+ products

```python
# Build hash indexes during initialization
ean_index = {}  # EAN → product data
url_index = {}  # URL → product data
asin_index = {} # ASIN → product data

# O(1) lookup instead of O(n) iteration
if ean in ean_index:
    product = ean_index[ean]
    # Already processed, skip
```

**Performance Impact**:
- 10,000 products: O(n) = 10s, O(1) = 0.001s
- 100,000 products: O(n) = 100s, O(1) = 0.001s

### 9.2 Path Manager Utility

**File**: `utils/path_manager.py`

**Key Functions**:
```python
def get_linking_map_path(supplier_name: str) -> Path:
    """Returns per-supplier linking map path"""
    base_dir = Path("OUTPUTS/FBA_ANALYSIS/linking_maps")
    supplier_dir = base_dir / supplier_name
    supplier_dir.mkdir(parents=True, exist_ok=True)
    return supplier_dir / "linking_map.json"
```

**Usage in Workflow**:
```python
# Initialize in __init__
self.linking_map_path = get_linking_map_path(self.supplier_name)
self.linking_map_dir = self.linking_map_path.parent
```

### 9.3 Browser Manager Pattern

**File**: `utils/browser_manager.py`

**Singleton Pattern**:
```python
class BrowserManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = BrowserManager()
        return cls._instance

    async def get_page(self, url: str = None, reuse_existing: bool = True) -> Page:
        """Gets or creates Playwright page"""
        if reuse_existing and self.current_page:
            return self.current_page

        # Connect to Chrome debug port
        page = await self._create_new_page()
        if url:
            await page.goto(url)

        self.current_page = page
        return page
```

**Benefits**:
- ✅ Single Chrome instance shared across workflow
- ✅ Connection reuse (no redundant CDP connects)
- ✅ Session persistence (authentication maintained)

---

## 10. Advanced Topics

### 10.1 Multi-Supplier Parallel Execution

**Current Design**: One supplier per execution
**Future Enhancement**: Parallel supplier processing

**Theoretical Implementation**:
```python
async def run_parallel_suppliers():
    suppliers = ["clearance-king.co.uk", "poundwholesale.co.uk"]

    tasks = []
    for supplier in suppliers:
        workflow_config = config_loader.get_workflow_config(f"{supplier}_workflow")
        task = asyncio.create_task(run_supplier_workflow(workflow_config))
        tasks.append(task)

    await asyncio.gather(*tasks)
```

**Challenges**:
- Browser manager singleton (need per-supplier browser instances)
- Output directory locking (already solved via per-supplier paths)
- State file conflicts (already solved via per-supplier state files)

### 10.2 Pagination Strategy Selection

**URL-Based Pagination**:
```json
{
  "pagination": {
    "pattern": "https://www.supplier.com/category?page={page}",
    "use_url_navigation": true
  }
}
```

**Button-Based Pagination**:
```json
{
  "pagination": {
    "use_url_navigation": false,
    "next_button_selector": ["a.action.next", ".pagination .next a"]
  }
}
```

**Automatic Detection** (Future):
```python
async def detect_pagination_strategy(page):
    # Check for URL pattern
    if "page=" in page.url or "p=" in page.url:
        return "url_based"

    # Check for next button
    next_button = page.locator("a:has-text('Next')")
    if await next_button.count() > 0:
        return "button_based"

    return "unknown"
```

### 10.3 Selector Robustness Strategies

**Multiple Fallbacks**:
```json
{
  "field_mappings": {
    "price": [
      ".price-box .price",           // Try primary
      "span.price",                  // Try backup 1
      ".price-wrapper .price",       // Try backup 2
      "meta[itemprop='price']",      // Try metadata
      "[data-price-amount]"          // Try data attribute
    ]
  }
}
```

**Extraction Priority**:
1. Try selectors in order
2. First visible element wins
3. If all fail, log warning and continue
4. Mark product for manual review

---

## 📚 Appendices

### Appendix A: Complete File Checklist

**Per-Supplier Files Required**:
- [ ] `config/supplier_configs/{domain}.json` (selectors, auth config)
- [ ] `config/{supplier}_categories.json` (category URLs)
- [ ] `tools/{supplier}/supplier_authentication_service.py` (auth adapter)
- [ ] `run_custom_{supplier}.py` (entry script)
- [ ] Update `config/system_config.json` (workflow + credentials)

**Shared Files (Never Duplicate)**:
- [ ] `tools/passive_extraction_workflow_latest.py`
- [ ] `tools/configurable_supplier_scraper.py`
- [ ] `tools/standalone_playwright_login.py`
- [ ] `tools/FBA_Financial_calculator.py`
- [ ] `tools/amazon_playwright_extractor.py`

### Appendix B: Configuration Templates

See Quick Reference Guide (`new_supplier_analysis_guide.md`) for complete templates.

### Appendix C: Troubleshooting Decision Tree

```
Issue: Authentication failing
  ├─► Check: Are selectors correct?
  │    └─► Fix: Test in DevTools, update config
  ├─► Check: Is password field hidden?
  │    └─► Fix: Ensure force=True in StandalonePlaywrightLogin
  └─► Check: Is test product URL correct?
       └─► Fix: Update test_product_url in login_config

Issue: Categories not loading
  ├─► Check: Is categories_config_path in workflow config?
  │    └─► Fix: Add to system_config.json
  └─► Check: Does categories JSON file exist?
       └─► Fix: Create config/{supplier}_categories.json

Issue: Wrong output directories
  ├─► Check: Is supplier_name correct in workflow config?
  │    └─► Fix: Update to match actual domain
  └─► Check: Are paths using self.supplier_name?
       └─► Verify: Config-driven implementation applied correctly
```

### Appendix D: Performance Benchmarks

| Metric | Poundwholesale (Oct 2, 2025) |
|--------|------------------------------|
| Categories loaded | 230 in <1s |
| State initialization | 10,561 products in 0.124s |
| Hash index build | 10,270 EANs in 0.124s |
| Authentication | 19.6s (first time) |
| Category scraping | ~58 products in ~30s |

---

**Document Status**: ✅ Complete
**Next Update**: As system evolves or new patterns emerge
**Feedback**: Submit issues or improvements to repository maintainer
