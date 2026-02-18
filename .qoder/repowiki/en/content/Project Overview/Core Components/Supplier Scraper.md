# Supplier Scraper

<cite>
**Referenced Files in This Document**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py)
- [url_cache_filter.py](file://utils/url_cache_filter.py)
- [supplier_config_loader.py](file://config/supplier_config_loader.py)
- [system_config_loader.py](file://config/system_config_loader.py)
- [poundwholesale.co.uk.json](file://config/supplier_configs/poundwholesale.co.uk.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document explains the Supplier Scraper component that extracts product data from supplier websites. It covers the configurable scraping architecture with dynamic selector support, URL filtering mechanisms, multi-category deduplication logic, supplier configuration system, authentication handling, and batch processing capabilities. It also documents the URL cache filter implementation that prevents duplicate processing of the same product URLs across categories, and integrates the scraper with the caching system to maintain consistency with the overall workflow execution.

## Project Structure
The Supplier Scraper is implemented as a configurable, Playwright-backed web scraper with externalized selector configuration and integrated caching and deduplication. Key elements:
- Scraper engine: tools/configurable_supplier_scraper.py
- URL cache filter: utils/url_cache_filter.py
- Supplier configuration loader: config/supplier_config_loader.py
- System configuration loader: config/system_config_loader.py
- Supplier selector configuration examples: config/supplier_configs/*.json

```mermaid
graph TB
subgraph "Scraper Engine"
CSS["ConfigurableSupplierScraper<br/>tools/configurable_supplier_scraper.py"]
end
subgraph "Configuration"
SCL["Supplier Config Loader<br/>config/supplier_config_loader.py"]
SSI["System Config Loader<br/>config/system_config_loader.py"]
SCF["Supplier Selector JSON<br/>config/supplier_configs/*.json"]
end
subgraph "Caching & Filtering"
UCF["URL Cache Filter<br/>utils/url_cache_filter.py"]
end
CSS --> SCL
CSS --> SSI
CSS --> SCF
CSS --> UCF
```

**Diagram sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L82-L167)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L31-L47)
- [supplier_config_loader.py](file://config/supplier_config_loader.py#L23-L69)
- [system_config_loader.py](file://config/system_config_loader.py#L9-L27)
- [poundwholesale.co.uk.json](file://config/supplier_configs/poundwholesale.co.uk.json#L1-L137)

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L100)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L1-L50)
- [supplier_config_loader.py](file://config/supplier_config_loader.py#L1-L40)
- [system_config_loader.py](file://config/system_config_loader.py#L1-L30)
- [poundwholesale.co.uk.json](file://config/supplier_configs/poundwholesale.co.uk.json#L1-L40)

## Core Components
- ConfigurableSupplierScraper: Orchestrates scraping with Playwright, loads supplier-specific selectors, handles pagination, filters URLs, and performs extraction with AI fallbacks.
- URL Cache Filter: Provides fast, in-memory duplicate detection for product URLs across suppliers and categories.
- Supplier Config Loader: Loads domain-specific selector configurations from JSON files and provides helper utilities.
- System Config Loader: Loads system-wide configuration (e.g., processing limits, batch sizes) used by the scraper.
- Supplier Selector JSON: Per-domain configuration files defining selectors, pagination, and navigation settings.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L82-L167)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L31-L98)
- [supplier_config_loader.py](file://config/supplier_config_loader.py#L23-L69)
- [system_config_loader.py](file://config/system_config_loader.py#L9-L27)
- [poundwholesale.co.uk.json](file://config/supplier_configs/poundwholesale.co.uk.json#L1-L137)

## Architecture Overview
The Supplier Scraper follows a layered architecture:
- Configuration Layer: Loads supplier and system configuration.
- Selector Resolution: Resolves domain-specific selectors from JSON or validated supplier packages.
- Browser Layer: Uses Playwright via a centralized BrowserManager for robust, anti-detection navigation.
- Extraction Layer: Extracts product data from category and product pages using selectors and AI fallbacks.
- Caching & Deduplication: Filters URLs against cached and linking-map URLs to avoid redundant processing.
- Authentication: Integrates with per-supplier authentication services to maintain session validity.

```mermaid
sequenceDiagram
participant Orchestrator as "Workflow Orchestrator"
participant Scraper as "ConfigurableSupplierScraper"
participant BM as "BrowserManager"
participant Cache as "URL Cache Filter"
participant Supplier as "Supplier Website"
Orchestrator->>Scraper : "scrape_products_from_url(category_url)"
Scraper->>BM : "get_page()"
Scraper->>Supplier : "fetch category page"
Scraper->>Scraper : "extract product elements"
Scraper->>Scraper : "collect product URLs (pagination)"
Scraper->>Cache : "filter_new_urls(urls)"
Cache-->>Scraper : "new URLs only"
loop For each new URL
Scraper->>BM : "get_page()"
Scraper->>Supplier : "visit product page"
Scraper->>Scraper : "extract title/price/EAN/availability"
Scraper->>Cache : "add_url_to_cache(url)"
end
Scraper-->>Orchestrator : "extracted products"
```

**Diagram sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L477-L880)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L153-L171)

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L477-L880)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L153-L171)

## Detailed Component Analysis

### ConfigurableSupplierScraper
The scraper encapsulates:
- Initialization and configuration loading (system and AI settings).
- Browser management via BrowserManager (Playwright).
- Category and product page navigation, pagination (URL and button-based).
- Dynamic selector resolution from supplier JSON or validated supplier packages.
- Extraction helpers for title, price, URL, image, EAN/identifier, availability.
- AI-assisted selector discovery and field extraction.
- URL filtering and caching integration.
- Authentication integration hooks for per-supplier services.
- Batch processing and progress callbacks for workflow integration.

Key behaviors:
- Selector loading prioritizes validated supplier packages, then legacy JSON files, then filesystem fallbacks.
- Pagination supports URL-based patterns and button-based “Load More” interactions with JavaScript or CSS selectors.
- URL filtering uses CachedURLManager to pre-filter URLs against cached product lists and linking maps.
- Memory management and cleanup are built-in to prevent leaks during long-running extractions.

```mermaid
classDiagram
class ConfigurableSupplierScraper {
+__init__(ai_client, openai_model_name, headless, use_shared_chrome, auth_callback, browser_manager, state_manager)
+scrape_products_from_url(url, max_products, product_accumulator) List
+scrape_products_from_prefiltered_urls(filtered_urls, category_url, product_accumulator) List
+_collect_all_product_urls(url, max_products) List
+_set_page_limiter(url) bool
+extract_title(element, element_html, context_url) str
+extract_price(element, element_html, context_url) float
+extract_url(element, element_html, context_url, base_url) str
+extract_image(element, element_html, context_url, base_url) str
+extract_identifier(element_soup, element_html, context_url) str
+extract_ean(product_page_soup, context_url) str
+extract_availability(product_page_soup, context_url) str
+extract_out_of_stock_status(product_page_soup, context_url) bool
+discover_categories(base_url) List
+discover_subpages(category_url, max_depth, current_depth) List
+auto_configure_supplier(supplier_url, save_config) Dict
+close_session() void
}
```

**Diagram sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L82-L167)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1327-L1387)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2355-L2410)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2412-L2430)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2432-L2449)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2495-L2514)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2516-L2717)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L3470-L3550)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L3573-L3599)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L3601-L3639)

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L82-L167)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1327-L1387)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2355-L2410)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2412-L2430)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2432-L2449)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2495-L2514)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2516-L2717)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L3470-L3550)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L3573-L3599)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L3601-L3639)

### URL Cache Filter
The URL Cache Filter provides:
- In-memory set-based lookup for O(1) duplicate detection.
- Loading cached URLs from supplier product cache files.
- Loading URLs from linking maps to prevent reprocessing already linked entries.
- Real-time updates to cache during extraction.
- Statistics and logging for monitoring.

```mermaid
classDiagram
class CachedURLManager {
+__init__(output_root)
+load_supplier_cache_urls(supplier_name, force_reload) int
+is_url_cached(url) bool
+add_url_to_cache(url) bool
+get_cache_stats() Dict
+filter_new_urls(product_urls) List
+clear_cache() void
+load_linking_map_urls(linking_map_path) set
+filter_urls_against_linking_map(urls) List
}
```

**Diagram sources**
- [url_cache_filter.py](file://utils/url_cache_filter.py#L31-L47)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L49-L98)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L104-L138)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L140-L151)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L153-L171)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L179-L206)

**Section sources**
- [url_cache_filter.py](file://utils/url_cache_filter.py#L31-L98)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L140-L171)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L179-L206)

### Supplier Configuration System
The configuration system supports:
- Domain-specific selector JSON files under config/supplier_configs/.
- Default fallback selector JSON.
- Validation of supplier packages with a .supplier_ready marker and validated product_selectors.json.
- Helper functions to load selectors, derive domains from URLs, and save configurations.

```mermaid
flowchart TD
Start(["Load Supplier Selectors"]) --> CheckPackage["Check validated supplier package"]
CheckPackage --> |Exists| LoadPackage["Load validated selectors from supplier package"]
CheckPackage --> |Missing| CheckLegacy["Check domain-specific JSON"]
CheckLegacy --> |Found| LoadLegacy["Load selectors from config/supplier_configs/<domain>.json"]
CheckLegacy --> |Missing| CheckDefault["Check default.json"]
CheckDefault --> |Found| LoadDefault["Load selectors from default.json"]
CheckDefault --> |Missing| ReturnEmpty["Return empty config"]
```

**Diagram sources**
- [supplier_config_loader.py](file://config/supplier_config_loader.py#L23-L69)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1897-L2003)

**Section sources**
- [supplier_config_loader.py](file://config/supplier_config_loader.py#L23-L69)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1897-L2003)

### Authentication Handling
The scraper integrates with per-supplier authentication services:
- Dynamically imports supplier-specific authentication modules.
- Periodically verifies authentication during extraction.
- Supports credential retrieval from system configuration for login checks.
- Logs actionable messages when authentication fails.

```mermaid
sequenceDiagram
participant Scraper as "ConfigurableSupplierScraper"
participant BM as "BrowserManager"
participant AuthSvc as "SupplierAuthenticationService"
participant Cfg as "SystemConfigLoader"
Scraper->>BM : "get_page()"
Scraper->>Cfg : "get_credentials(domain)"
Scraper->>AuthSvc : "ensure_authenticated_session(credentials)"
AuthSvc-->>Scraper : "authenticated?"
alt authenticated
Scraper-->>Scraper : "continue extraction"
else not authenticated
Scraper-->>Scraper : "log recommendation to re-authenticate"
end
```

**Diagram sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L800-L842)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1114-L1176)

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L800-L842)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1114-L1176)

### Batch Processing and Progress Tracking
The scraper supports:
- Real-time progress updates via a progress callback.
- Debounced state persistence through a state manager.
- Accumulation of extracted products into a shared list for live reporting.
- Price filtering based on system configuration limits.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L705-L767)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1061-L1101)

### Multi-Category Deduplication Logic
The scraper implements multi-category deduplication by:
- Pre-loading cached URLs from supplier product cache files.
- Loading URLs from linking maps to exclude already-processed entries.
- Classifying discovered URLs into new vs known, returning “stub” products for known URLs to maintain list length consistency.
- Updating the cache incrementally during extraction.

```mermaid
flowchart TD
Start(["Scrape Category"]) --> Collect["Collect all product URLs"]
Collect --> LoadCache["Load supplier cache URLs"]
Collect --> LoadLinking["Load linking map URLs"]
LoadCache --> Filter["Filter new URLs"]
LoadLinking --> Filter
Filter --> Visit["Visit product pages for new URLs"]
Visit --> Extract["Extract product data"]
Extract --> CacheUpdate["Add URL to cache"]
CacheUpdate --> End(["Return products"])
```

**Diagram sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L513-L575)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L582-L591)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L49-L98)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L179-L196)

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L513-L575)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L582-L591)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L49-L98)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L179-L196)

### Practical Examples

#### Supplier Configuration Setup
- Place a domain-specific JSON file in config/supplier_configs/<domain>.json.
- Define field_mappings for product_item, title, price, url, image, ean, barcode, product_code, sku, out_of_stock, stock_status.
- Configure pagination with pattern and next_button_selector or next_button_javascript for button-based pagination.
- Optionally enable page_limiter to increase products per page.

Example reference:
- [poundwholesale.co.uk.json](file://config/supplier_configs/poundwholesale.co.uk.json#L1-L137)

**Section sources**
- [poundwholesale.co.uk.json](file://config/supplier_configs/poundwholesale.co.uk.json#L1-L137)

#### Custom Selector Creation
- Use auto_configure_supplier to discover selectors from a supplier homepage.
- Review and refine discovered selectors in the generated configuration.
- Save the configuration for reuse.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2269-L2331)

#### Troubleshooting Scraping Issues
Common issues and resolutions:
- Navigation failures: Check rate limits and bot detection responses; the scraper includes retry logic and delays.
- Missing prices: The scraper triggers authentication checks and falls back to AI extraction.
- Memory pressure: Built-in memory checks and forced cleanup are executed periodically.
- Duplicate processing: Ensure URL cache and linking map are loaded and updated during extraction.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L338-L467)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L772-L845)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L857-L862)

## Dependency Analysis
The Supplier Scraper depends on:
- Configuration loaders for supplier and system settings.
- Centralized BrowserManager for Playwright instances.
- URL Cache Filter for efficient duplicate detection.
- Per-supplier authentication services for session maintenance.

```mermaid
graph LR
CSS["ConfigurableSupplierScraper"] --> SCL["Supplier Config Loader"]
CSS --> SSI["System Config Loader"]
CSS --> BM["BrowserManager"]
CSS --> UCF["URL Cache Filter"]
CSS --> PAS["Per-Supplier Auth Services"]
```

**Diagram sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L58-L68)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L243-L283)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L515-L552)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L942-L985)

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L58-L68)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L243-L283)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L515-L552)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L942-L985)

## Performance Considerations
- Efficient URL filtering reduces unnecessary page visits and speeds up extraction.
- Memory management includes periodic garbage collection and forced cleanup to prevent leaks.
- Browser reuse via BrowserManager minimizes startup overhead.
- Pagination safety limits prevent excessive resource consumption.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Rate limiting and bot detection: The scraper includes retry logic and delays; monitor logs for 429/403 responses.
- Authentication failures: The scraper proactively checks authentication and logs recommendations.
- Selector mismatches: Use AI-assisted discovery and refine selector configurations.
- Cache inconsistencies: Verify cache file paths and linking map locations; ensure cache updates occur during extraction.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L395-L410)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L818-L828)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2171-L2267)
- [url_cache_filter.py](file://utils/url_cache_filter.py#L60-L102)

## Conclusion
The Supplier Scraper provides a robust, configurable, and efficient solution for extracting product data from supplier websites. Its dynamic selector system, URL caching and deduplication, authentication integration, and batch processing capabilities ensure reliable operation across diverse supplier environments while maintaining consistency with the broader workflow.