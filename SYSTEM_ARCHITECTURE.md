# Amazon FBA Agent System - Complete System Architecture & File Reference

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Entry Points](#2-entry-points)
3. [Core Workflow Engine](#3-core-workflow-engine)
4. [Configuration](#4-configuration)
5. [Control Plane (Dashboard + Orchestration)](#5-control-plane-dashboard--orchestration)
6. [Utilities](#6-utilities)
7. [Skills & Extensions](#7-skills--extensions)
8. [Output Files Reference](#8-output-files-reference)
9. [Sandbox Workflows](#9-sandbox-workflows)
10. [File Naming Conventions](#10-file-naming-conventions)

---

## 1. System Overview

The Amazon FBA Agent System is an automated product sourcing platform that:
1. Scrapes wholesale supplier websites for product data (EAN, title, price, URL)
2. Matches products to Amazon listings via EAN or title search
3. Calculates profitability (ROI, fees, net profit)
4. Persists state for resumable, long-running sessions

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ENTRY POINTS                                │
│   run_custom_{supplier}.py  (per-supplier runners)            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CORE WORKFLOW ENGINE                           │
│   tools/passive_extraction_workflow_latest.py                  │
│   - Supplier scraping (ConfigurableSupplierScraper)             │
│   - Amazon matching (FixedAmazonExtractor)                     │
│   - State management (FixedEnhancedStateManager)                │
│   - Financial calculation (FBA_Financial_calculator)           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     UTILITIES                                   │
│   utils/browser_manager.py      - Chrome CDP lifecycle          │
│   utils/windows_save_guardian.py - Atomic file operations      │
│   utils/sentinel_monitor.py    - System health monitoring      │
│   utils/path_manager.py         - Centralized path resolution   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONTROL PLANE                                 │
│   dashboard_v2_redesign/    - Live metrics dashboard          │
│   control_plane/             - Job orchestration & AI chat    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUTS                                      │
│   OUTPUTS/FBA_ANALYSIS/linking_maps/    - EAN→ASIN mappings   │
│   OUTPUTS/FBA_ANALYSIS/financial_reports/ - Profitability CSVs  │
│   OUTPUTS/cached_products/                - Supplier products   │
│   OUTPUTS/CACHE/processing_states/       - Resumable state     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Entry Points

### 2.1 Per-Supplier Runner Scripts

| File | Supplier | Auth | Purpose |
|------|----------|------|---------|
| `run_custom_poundwholesale.py` | poundwholesale.co.uk | Yes | Primary supplier - high volume |
| `run_custom_clearance_king.py` | clearance-king.co.uk | No | Clearance products |
| `run_custom_dkwholesale-com.py` | dkwholesale.com | Yes | DK wholesale |
| `run_custom_efghousewares-co-uk.py` | efghousewares.co.uk | Yes | Housewares |
| `run_custom_kdwholesale-co-uk.py` | kdwholesale.co.uk | Yes | KD wholesale |
| `run_custom_laceywholesale-co-uk.py` | laceywholesale.co.uk | Yes | Lacey |
| `run_custom_wholesaletradingsupplies-co-uk.py` | wholesaletradingsupplies.co.uk | Yes | Trading supplies |
| `run_custom_stationerywholesale-co-uk.py` | stationerywholesale.co.uk | Yes | Stationery |
| `run_custom_angelwholesale-co-uk.py` | angelwholesale.co.uk | Yes | Angel wholesale |

### 2.2 Run Structure

```python
# Typical run_custom_{supplier}.py structure:
async def main():
    # 1. Setup logging
    setup_logger(supplier_name=...)
    
    # 2. Load config
    config = SystemConfigLoader.get_full_config()
    
    # 3. Connect to Chrome
    browser_mgr = BrowserManager()
    
    # 4. Optional: Authentication
    if requires_auth:
        auth_helper = SupplierAuthenticationHelper(page)
        await auth_helper.login(credentials)
    
    # 5. Run workflow
    workflow = PassiveExtractionWorkflow(...)
    await workflow.run()
    
    # 6. Generate financials
    run_calculations(supplier_name)
```

---

## 3. Core Workflow Engine

### 3.1 PassiveExtractionWorkflow

**Location:** `tools/passive_extraction_workflow_latest.py`

The main orchestrator class that coordinates the entire pipeline.

**Key Responsibilities:**
- Loads category URLs from config
- Initializes/resumes state via FixedEnhancedStateManager
- Runs supplier extraction in batches
- Triggers Amazon matching for each product
- Saves caches atomically
- Calls FBA_Financial_calculator when linking map grows

### 3.2 Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `ConfigurableSupplierScraper` | `tools/configurable_supplier_scraper.py` | Scrapes supplier websites using CSS selectors |
| `FixedAmazonExtractor` | `tools/amazon_playwright_extractor.py` | Extracts Amazon data via Playwright CDP |
| `FBA_Financial_calculator` | `tools/FBA_Financial_calculator.py` | Calculates ROI, fees, net profit |
| `CacheManager` | `tools/cache_manager.py` | Manages supplier + Amazon caches |

### 3.3 Workflow Phases

```
INITIALIZATION
    │
    ▼
SUPPLIER_EXTRACTION ──────► (loops through categories)
    │                           - Scrapes products from each category URL
    │                           - Deduplicates via hash lookup
    │                           - Caches to supplier JSON
    │
    ▼
AMAZON_ANALYSIS ──────────► (loops through unanalyzed products)
    │                           - Search by EAN (preferred)
    │                           - Fallback to title search
    │                           - Cache Amazon data
    │
    ▼
LINKING ──────────────────► (builds mapping)
                                - Maps supplier EAN → Amazon ASIN
                                - Records match method + confidence
                                - Updates linking_map.json
                                
    ▼
FINANCIAL_CALCULATION ────► (runs when threshold reached)
                                - Reads linking map
                                - Computes ROI, fees, margins
                                - Outputs CSV report
```

---

## 4. Configuration

### 4.1 System Configuration

**Location:** `config/system_config.json`

**Key Sections:**
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
  },
  "workflows": {
    "poundwholesale_workflow": {
      "supplier_name": "poundwholesale.co.uk",
      "categories_config_path": "config/poundwholesale_workflow_categories.json"
    }
  }
}
```

### 4.2 Per-Supplier Configs

**Location:** `config/supplier_configs/{domain}.json`

Contains CSS selectors for scraping:
```json
{
  "supplier_url": "https://www.poundwholesale.co.uk",
  "product_item": ".product-item",
  "title": ".product-title",
  "price": ".price",
  "ean": ".ean-code",
  "url": ".product-link",
  "next_page_button": ".pagination-next"
}
```

### 4.3 Category Configs

**Location:** `config/{workflow_key}_categories.json`

```json
{
  "category_urls": [
    "https://supplier.com/category/toys",
    "https://supplier.com/category/home"
  ]
}
```

---

## 5. Control Plane (Dashboard + Orchestration)

### 5.1 Dashboard V2 Redesign

**Location:** `dashboard_v2_redesign/`

Modern dashboard with live metrics, AI assistant, and operator control.

**Key Files:**
| File | Purpose |
|------|---------|
| `operator_control_plane.html` | Main operator interface with real-time metrics |
| `precision_dashboard.html` | KPI-focused dashboard |
| `ai_assistant.html` | AI-powered analysis and chat |
| `api.py` | Backend API for dashboard data |

**Features:**
- Real-time processing metrics
- Product count, profitability statistics
- Run status and progress
- AI assistant for analysis queries

### 5.2 Control Plane Orchestration

**Location:** `control_plane/`

**Key Modules:**
| Module | Purpose |
|--------|---------|
| `chat_orchestrator.py` | AI chat interface for job management |
| `worker.py` | Job execution engine |
| `job_manager.py` | Job queue and state management |
| `run_product_list_refresh.py` | Product list refresh workflow |
| `paths.py` | Centralized path resolution |
| `rag_index.py` | RAG for context-aware AI responses |
| `rag_retriever.py` | Retrieval augmented generation |
| `tools/` | Tool implementations (status, financial, linking maps) |

### 5.3 Product List Refresh Workflow

The product list refresh is a separate workflow from category-based extraction:

**Workflow Types:**
1. **Category Workflow** - Extracts from predefined category URLs
2. **Product List Workflow** - Processes specific product URLs

**State Handling:**
- Uses sandboxed output directories for isolation
- Can write sandboxed supplier cache (not currently used)
- Updates linking maps in sandbox directories

---

## 6. Utilities

### 6.1 Browser Manager

**Location:** `utils/browser_manager.py`

Manages Chrome browser lifecycle via CDP (Chrome DevTools Protocol).

**Features:**
- Singleton pattern for shared browser instance
- LRU page cache (1 page)
- Health monitoring and auto-restart
- IPv6/IPv4 dual-stack support

### 6.2 Windows Save Guardian

**Location:** `utils/windows_save_guardian.py`

Provides atomic file operations for Windows.

**Strategies:**
1. Temp file → atomic replace (preferred)
2. Timestamped backup → temp → replace
3. Retry with backoff
4. Alternative temp directory

### 6.3 Sentinel Monitor

**Location:** `utils/sentinel_monitor.py`

Monitors system health and detects divergence.

**Checks:**
- Cached data counts vs linking map entries
- State file consistency
- Processing anomalies

### 6.4 Path Manager

**Location:** `utils/path_manager.py`

Centralized path resolution for all system paths.

### 6.5 Fixed Enhanced State Manager

**Location:** `utils/fixed_enhanced_state_manager.py`

Manages processing state for resumable sessions.

**Key Features:**
- Monotonic index tracking (never decreases)
- Atomic saves
- Frozen category denominators
- Session tracking with UUID

---

## 7. Skills & Extensions

### 7.1 Supplier Onboarding Skill

**Location:** `.claude/skills/supplier-onboarding/`

Guided workflow for adding new suppliers to the system.

**7-Step Process:**
1. Gather supplier information
2. Prepare configurations (JSON selectors, categories)
3. Invoke wizard to generate runner script
4. Validate generated files
5. Pre-run verification
6. User decision (test/main run)
7. Auth helper customization if needed

### 7.2 GitNexus Integration

**Location:** `.claude/skills/gitnexus/`

Code knowledge graph for architecture understanding.

---

## 8. Output Files Reference

### 8.1 Linking Map

**Location:** `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json`

**Purpose:** Maps supplier EANs to Amazon ASINs

**Structure:**
```json
[
  {
    "supplier_ean": "5012128582868",
    "amazon_asin": "B0DK1BVZN8",
    "supplier_title": "Giftmaker Christmas Wishes Robin Gift Bag",
    "amazon_title": "Kraft Bags With Handles...",
    "supplier_price": 0.53,
    "amazon_price": 14.35,
    "match_method": "EAN",        // or "title"
    "confidence": "high",         // high/medium/low
    "created_at": "2025-07-26T03:15:15.274059",
    "supplier_url": "https://www.supplier.co.uk/product"
  }
]
```

**Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| `supplier_ean` | string | EAN/barcode from supplier |
| `amazon_asin` | string/null | Amazon ASIN if matched |
| `supplier_title` | string | Product title from supplier |
| `amazon_title` | string/null | Product title on Amazon |
| `supplier_price` | float | Price from supplier (GBP) |
| `amazon_price` | float/null | Selling price on Amazon (GBP) |
| `match_method` | string | How match was made: "EAN", "title", "none" |
| `confidence` | string | Match confidence: "high", "medium", "low", "0" |
| `created_at` | ISO date | When entry was created |
| `supplier_url` | string | URL on supplier website |

---

### 8.2 Supplier Cache (Cached Products)

**Location:** `OUTPUTS/cached_products/{supplier}_products_cache.json`

**Purpose:** Stores all scraped products from supplier

**Structure:**
```json
[
  {
    "title": "'Welcome' Wellies Door Mat",
    "price": 1.18,
    "url": "https://www.supplier.co.uk/welcome-wellies-door-mat",
    "ean": "5055056750510",
    "sku": "5051",
    "availability": "In stock",
    "image_url": "https://...",
    "source_url": "https://www.supplier.co.uk/category",
    "scraped_at": "2025-07-29T04:35:25.293789"
  }
]
```

**Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Product title |
| `price` | float | Price in GBP |
| `url` | string | Product page URL |
| `ean` | string/null | EAN/barcode |
| `sku` | string/null | Supplier SKU |
| `availability` | string | Stock status |
| `image_url` | string/null | Product image URL |
| `source_url` | string | Category URL where found |
| `scraped_at` | ISO date | When product was scraped |

---

### 8.3 Processing State

**Location:** `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json`

**Purpose:** Tracks resumable processing progress

**Structure:**
```json
{
  "schema_version": "1.2_THREAD_SAFE",
  "created_at": "2025-11-19T15:55:04.947693+00:00",
  "last_updated": "2026-03-25T05:44:09.933594+00:00",
  "supplier_name": "poundwholesale.co.uk",
  "total_products": 10828,
  "successful_products": 11362,
  "processing_status": "initialized",
  "category_progress": "1/230",
  "system_progression": {
    "current_phase": "amazon_analysis",
    "persistent_category_index": 231,
    "current_category_index": 1,
    "total_categories": 230,
    "category_freeze_timestamp": "2026-03-23T15:06:24.295547+00:00",
    "supplier_products_needing_extraction": 1,
    "supplier_products_completed": 0,
    "amazon_products_needing_analysis": 1,
    "amazon_products_completed": 1,
    "frozen_category_denominators": {
      "https://supplier.co.uk/category1": 58,
      "https://supplier.co.uk/category2": 15
    }
  }
}
```

**Key Fields:**
| Field | Purpose |
|-------|---------|
| `schema_version` | Version for compatibility |
| `supplier_name` | Which supplier this state belongs to |
| `total_products` | Total products found |
| `successful_products` | Products successfully matched to Amazon |
| `processing_status` | Current phase: "initialized", "supplier_extraction", "amazon_analysis" |
| `system_progression.current_phase` | Active processing phase |
| `persistent_category_index` | Resumable category position |
| `frozen_category_denominators` | Category product counts (frozen at start) |

---

### 8.4 Financial Report (CSV)

**Location:** `OUTPUTS/FBA_ANALYSIS/financial_reports/{supplier}/fba_financial_report_{supplier}_{timestamp}.csv`

**Purpose:** Profitability analysis for each matched product

**Structure (CSV columns):**
```
EAN,EAN_OnPage,ASIN,SupplierTitle,AmazonTitle,SupplierURL,AmazonURL,
bought_in_past_month,fba_seller_count,fbm_seller_count,total_offer_count,
SupplierPrice_incVAT,SupplierPrice_exVAT,SellingPrice_incVAT,
ReferralFee,FBAFee,PrepHouseFee,OutputVAT,InputVAT,NetProceeds,
HMRC,NetProfit,ROI,Breakeven,ProfitMargin
```

**Key Calculations:**
| Field | Formula |
|-------|---------|
| `NetProceeds` | SellingPrice - ReferralFee - FBAFee - PrepHouseFee - OutputVAT |
| `NetProfit` | NetProceeds - InputVAT - SupplierPrice |
| `ROI` | (NetProfit / SupplierPrice) * 100 |
| `ProfitMargin` | (NetProfit / SellingPrice) * 100 |

---

### 8.5 Amazon Cache

**Location:** `OUTPUTS/FBA_ANALYSIS/amazon_cache/`

Individual Amazon product data files.

**File Pattern:** `amazon_{ASIN}_{EAN}.json`

**Structure:**
```json
{
  "asin": "B0DK1BVZN8",
  "ean": "5012128582868",
  "title": "Product Title on Amazon",
  "price": 14.99,
  "fba_eligible": true,
  "seller_count": 10,
  "buy_box_price": 14.35,
  "sales_rank": 12345,
  "bought_in_past_month": 50,
  "extracted_at": "2025-07-26T03:15:15",
  "_search_method_used": "EAN"
}
```

---

## 9. Sandbox Workflows

Sandbox workflows run isolated from main processing, using separate output directories.

### 9.1 Sandbox Naming Convention

**Pattern:** `{supplier}.{tld}__sandbox__{run_id}`

**Examples:**
- `poundwholesale.co.uk__sandbox__44b12007`
- `efghousewares.co.uk__sandbox__cea25747`
- `angelwholesale.co.uk__sandbox__008fb410`

**Components:**
| Part | Description |
|------|-------------|
| `{supplier}.{tld}` | Supplier domain (dot-form) |
| `__sandbox__` | Literal separator |
| `{run_id}` | UUID or identifier for this run |

### 9.2 Main vs Sandbox Differences

| Aspect | Main Workflow | Sandbox Workflow |
|--------|--------------|-----------------|
| **Output Directory** | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/` | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}__sandbox__{run_id}/` |
| **Supplier Cache** | `OUTPUTS/cached_products/{supplier}_products_cache.json` | Sandbox-specific in sandbox dir |
| **Processing State** | `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json` | Sandbox-specific in sandbox dir |
| **Use Case** | Production runs | Testing, category experiments |

### 9.3 Product List Refresh (Special Sandbox)

Product list refresh uses sandbox-like isolation:

**Identifiable by:**
- `run_id` in the output directory name
- Often located in `__sandbox__` prefixed directories
- May have separate `linking_map.json` per run

### 9.4 Sandbox Output Files

Each sandbox directory contains:
```
{supplier}.{tld}__sandbox__{run_id}/
├── linking_map.json          # Same structure as main
├── amazon_cache/             # Amazon data for this run
│   ├── amazon_{ASIN1}_{EAN1}.json
│   └── amazon_{ASIN2}_{EAN2}.json
└── (optional) processing_state.json
```

---

## 10. File Naming Conventions

### 10.1 Three Naming Forms

| Context | Form | Example |
|---------|------|---------|
| **Config files** | Dot-form | `supplier.com.json` |
| **System config** | Dot-form | `"supplier_name": "supplier.com"` |
| **Runner scripts** | Hyphen-form | `run_custom_supplier-com.py` |
| **Tool directories** | Hyphen-form | `tools/supplier-com/` |
| **Workflow keys** | Underscore-form | `supplier_workflow` |
| **State files** | Underscore-form | `supplier_com_processing_state.json` |
| **Sandbox dirs** | Dot + underscore | `supplier.com__sandbox__uuid` |

### 10.2 Output Directory Naming

| Output Type | Pattern | Example |
|-------------|---------|---------|
| Linking maps | Dot-form | `poundwholesale.co.uk/linking_map.json` |
| Sandbox linking maps | Dot + underscore | `poundwholesale.co.uk__sandbox__44b12007/linking_map.json` |
| Supplier cache | Hyphen-form | `poundwholesale-co-uk_products_cache.json` |
| Processing state | Underscore-form | `poundwholesale_co_uk_processing_state.json` |
| Financial reports | Hyphen-form | `poundwholesale-co-uk/fba_financial_report_...csv` |

### 10.3 Identifying File Types

| File Pattern | Type | Purpose |
|--------------|------|---------|
| `*_products_cache.json` | Supplier cache | All scraped products |
| `*_processing_state.json` | State file | Resumable progress |
| `linking_map.json` | Linking map | EAN → ASIN mapping |
| `amazon_{ASIN}_{EAN}.json` | Amazon cache | Amazon product data |
| `fba_financial_report_*.csv` | Financial report | Profitability analysis |
| `*.log` | Log file | Debug/execution logs |

---

## Quick Reference

### Run a Supplier
```bash
python run_custom_poundwholesale.py
```

### View Dashboard
```bash
python dashboard_v2_redesign/api.py
# Then open dashboard_v2_redesign/operator_control_plane.html
```

### Check Processing State
```bash
type OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json
```

### Onboard New Supplier
```bash
# Use the supplier-onboarding skill in Claude
# See .claude/skills/supplier-onboarding/SKILL.md
```

---

*Last Updated: 2026-04-11*
