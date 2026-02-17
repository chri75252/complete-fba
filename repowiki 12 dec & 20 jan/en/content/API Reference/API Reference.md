# API Reference

<cite>
**Referenced Files in This Document**   
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [passive_extraction_workflow_latest.py API](#passive_extraction_workflow_latestpy-api)
3. [configurable_supplier_scraper.py API](#configurable_supplier_scraperpy-api)
4. [FBA_Financial_calculator.py API](#fba_financial_calculatorpy-api)
5. [fixed_enhanced_state_manager.py API](#fixed_enhanced_state_managerpy-api)
6. [Client Implementation Guidelines](#client-implementation-guidelines)
7. [Versioning and Backwards Compatibility](#versioning-and-backwards-compatibility)
8. [Error Handling](#error-handling)

## Introduction
This document provides comprehensive API documentation for the public interfaces of the Amazon FBA Agent System. It details the core modules responsible for workflow execution, product extraction, financial calculation, and state management. Each section documents the public methods, parameters, return values, and usage patterns for the respective module. Code examples demonstrate typical usage scenarios, and error conditions are thoroughly documented. The system is designed for extensibility and integration, with guidelines provided for client implementation.

## passive_extraction_workflow_latest.py API

The `PassiveExtractionWorkflow` class is the central orchestrator for the Amazon FBA product sourcing workflow. It manages the entire process from supplier product extraction to Amazon data retrieval, financial analysis, and stateful resumption.

### Class: PassiveExtractionWorkflow

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)

#### Method: `__init__(self, config_loader, workflow_config, browser_manager=None, ai_client=None)`
Initializes the workflow with configuration and service dependencies.

**Parameters:**
- `config_loader`: A configuration loader instance to retrieve system settings.
- `workflow_config`: A dictionary containing workflow-specific configuration (e.g., supplier name).
- `browser_manager`: An optional `BrowserManager` instance for shared browser control.
- `ai_client`: An optional OpenAI client for AI-powered features (currently disabled).

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L860-L989)

#### Method: `run(self)`
Executes the main product sourcing workflow. This method orchestrates the entire process, including state loading, supplier scraping, Amazon data matching, financial calculation, and result reporting.

**Returns:**
- `List[Dict[str, Any]]`: A list of profitable product results, or an empty list if no products were found or an error occurred.

**Usage Example:**
```python
from config.system_config_loader import SystemConfigLoader
from utils.browser_manager import BrowserManager

config_loader = SystemConfigLoader()
workflow_config = {"supplier_name": "poundwholesale.co.uk", "use_predefined_categories": True}
browser_manager = BrowserManager.get_instance()

workflow = PassiveExtractionWorkflow(config_loader, workflow_config, browser_manager)
results = await workflow.run()
```

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L1970-L2316)

#### Method: `_extract_supplier_products(self, supplier_url, supplier_name, category_urls_to_scrape, max_products_per_category, max_products_to_process, supplier_extraction_batch_size)`
Extracts product data from a supplier's website by scraping the provided category URLs.

**Parameters:**
- `supplier_url`: The base URL of the supplier website.
- `supplier_name`: The name of the supplier.
- `category_urls_to_scrape`: A list of category URLs to scrape.
- `max_products_per_category`: Maximum number of products to extract per category.
- `max_products_to_process`: Total maximum number of products to process.
- `supplier_extraction_batch_size`: Number of categories to process in a batch.

**Returns:**
- `List[Dict[str, Any]]`: A list of dictionaries, each containing product data (title, price, URL, EAN, etc.).

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L2318-L2435)

#### Method: `_get_amazon_data(self, supplier_product)`
Finds the corresponding product on Amazon for a given supplier product using a dual-pronged approach: EAN search first, followed by a title-based search if the EAN search fails.

**Parameters:**
- `supplier_product`: A dictionary containing the supplier product data.

**Returns:**
- `Dict[str, Any]`: A dictionary containing the matched Amazon product data, or an error dictionary if no match is found.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L2437-L2525)

## configurable_supplier_scraper.py API

The `ConfigurableSupplierScraper` class is responsible for extracting product data from supplier websites. It uses Playwright for robust browser automation and supports configurable selectors for different suppliers.

### Class: ConfigurableSupplierScraper

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L100-L1300)

#### Method: `__init__(self, ai_client=None, openai_model_name=None, headless=False, use_shared_chrome=True, auth_callback=None, browser_manager=None, state_manager=None)`
Initializes the scraper with optional AI and browser management capabilities.

**Parameters:**
- `ai_client`: An OpenAI client for AI-powered selector discovery (not currently used).
- `openai_model_name`: The name of the OpenAI model to use (not currently used).
- `headless`: Whether to run the browser in headless mode.
- `use_shared_chrome`: Whether to connect to a shared Chrome instance via CDP.
- `auth_callback`: An optional callback function to evaluate authentication status.
- `browser_manager`: An optional `BrowserManager` instance for shared browser control.
- `state_manager`: An optional `EnhancedStateManager` instance for progress tracking.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L100-L200)

#### Method: `scrape_products_from_url(self, url, max_products=50, product_accumulator=None)`
Extracts product data from a single supplier category URL.

**Parameters:**
- `url`: The URL of the supplier category page.
- `max_products`: The maximum number of products to extract from the page.
- `product_accumulator`: An optional list to which products are appended in real-time for progress tracking.

**Returns:**
- `List[Dict[str, Any]]`: A list of dictionaries, each containing product data.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L400-L800)

#### Method: `extract_price(self, soup, product_html, product_url)`
Extracts the product price from the HTML content using configurable selectors.

**Parameters:**
- `soup`: A BeautifulSoup object representing the product page's HTML.
- `product_html`: The raw HTML string of the product page.
- `product_url`: The URL of the product page.

**Returns:**
- `Optional[float]`: The extracted price as a float, or None if the price could not be found.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1200-L1300)

#### Method: `set_progress_callback(self, callback_func)`
Sets a callback function to be called during the scraping process to report progress.

**Parameters:**
- `callback_func`: A function that accepts parameters for the current phase, processed count, total count, product URL, and product data.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L380-L390)

## FBA_Financial_calculator.py API

The `FBA_Financial_calculator` module provides functions for calculating the profitability of products for Amazon FBA and generating financial reports.

### Module: FBA_Financial_calculator

**Section sources**
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L0-L590)

#### Function: `run_calculations(supplier_name, supplier_cache_path=None, output_dir=None, amazon_scrape_dir=None)`
Performs financial calculations for all products from a given supplier.

**Parameters:**
- `supplier_name`: The name of the supplier (e.g., "poundwholesale.co.uk").
- `supplier_cache_path`: Optional path to the supplier's product cache JSON file.
- `output_dir`: Optional directory to save the financial report.
- `amazon_scrape_dir`: Optional directory containing the Amazon product data.

**Returns:**
- `Dict[str, Any]`: A dictionary containing the results, including a pandas DataFrame, statistics, and the output file path.

**Usage Example:**
```python
from FBA_Financial_calculator import run_calculations

results = run_calculations("poundwholesale.co.uk")
print(f"Generated {results['statistics']['generated_calculations']} financial calculations")
print(f"Report saved to: {results['statistics']['output_file']}")
```

**Section sources**
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L300-L500)

#### Function: `financials(supplier, amazon, supplier_price_inc_vat)`
Calculates the detailed financial metrics for a single product.

**Parameters:**
- `supplier`: A dictionary containing the supplier product data.
- `amazon`: A dictionary containing the matched Amazon product data.
- `supplier_price_inc_vat`: The supplier's price including VAT.

**Returns:**
- `Dict[str, Any]`: A dictionary containing financial metrics such as ROI, net profit, referral fee, FBA fee, and breakeven price.

**Section sources**
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L200-L300)

## fixed_enhanced_state_manager.py API

The `FixedEnhancedStateManager` class provides a robust system for managing the workflow's state, enabling it to resume from interruptions and track progress accurately.

### Class: FixedEnhancedStateManager

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L100-L2000)

#### Method: `__init__(self, supplier_name, base_path=None, lock_timeout=5.0)`
Initializes the state manager for a specific supplier.

**Parameters:**
- `supplier_name`: The name of the supplier.
- `base_path`: The base directory path for state files (optional).
- `lock_timeout`: The timeout in seconds for acquiring the file lock.

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L100-L200)

#### Method: `load_state(self) -> bool`
Loads the existing state from the state file.

**Returns:**
- `bool`: True if a state file was found and loaded, False if starting fresh.

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L300-L400)

#### Method: `save_state_atomic(self, note="")`
Atomically saves the current state to disk using a temporary file and rename operation to ensure data integrity.

**Parameters:**
- `note`: An optional note to include in the save operation for logging.

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L800-L1000)

#### Method: `get_resumption_ptr(self) -> ResumptionPtr`
Retrieves the current resumption pointer, which indicates where the workflow should resume processing.

**Returns:**
- `ResumptionPtr`: A named tuple containing the current phase, category index, and product index.

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1200-L1300)

#### Method: `set_resumption_ptr(self, phase, cat_idx, prod_idx_next)`
Sets the resumption pointer to a specific location in the workflow.

**Parameters:**
- `phase`: The current phase ("supplier" or "amazon_analysis").
- `cat_idx`: The index of the current category.
- `prod_idx_next`: The index of the next product to process in the current category.

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1100-L1200)

## Client Implementation Guidelines

To extend or integrate with the Amazon FBA Agent System, clients should follow these guidelines:

1.  **Use the Public API:** Interact with the system through the documented public methods of the `PassiveExtractionWorkflow`, `ConfigurableSupplierScraper`, `FBA_Financial_calculator`, and `FixedEnhancedStateManager` classes. Avoid accessing internal attributes or methods that are not part of the public API.
2.  **Handle Asynchronous Operations:** The core workflow and scraper methods are asynchronous (use `async/await`). Ensure your client code is also asynchronous or properly handles the returned coroutines.
3.  **Respect Configuration:** The system is heavily driven by the `system_config.json` file. Clients should load and respect these configurations rather than hardcoding values.
4.  **Implement Progress Callbacks:** For long-running operations, use the `set_progress_callback` method on the scraper to receive real-time updates on the scraping progress.
5.  **Manage State Correctly:** Use the `FixedEnhancedStateManager` to load and save the workflow state. Always call `load_state()` at the beginning of a session and rely on `get_resumption_ptr()` to determine where to resume processing.
6.  **Handle Errors Gracefully:** Implement robust error handling around calls to the API, as network requests and browser automation can fail. Refer to the [Error Handling](#error-handling) section for details.

## Versioning and Backwards Compatibility

The system uses a schema versioning system within the state file (`schema_version` field) to manage backwards compatibility.

*   **State File Schema:** The `FixedEnhancedStateManager` is designed to handle state files from older versions. The `load_state` method includes logic to migrate legacy state formats to the current enhanced format.
*   **Public API Stability:** The public methods of the core classes are considered stable. Changes to these interfaces will be made cautiously and will be documented in a changelog.
*   **Configuration Backwards Compatibility:** The `system_config.json` file is designed to be backwards compatible. New configuration options are added as optional fields, and the system provides sensible defaults for missing values.
*   **Deprecation:** If a public method must be deprecated, it will be marked as such in the documentation and will remain functional for at least one major version before being removed.

## Error Handling

The system employs comprehensive error handling throughout its components.

### Exception Handling in `PassiveExtractionWorkflow.run()`
The `run()` method is designed to be resilient. It catches exceptions during the main processing loop and logs them, allowing the workflow to continue processing other products. Critical errors that prevent the entire workflow from continuing (e.g., failure to load configuration) will cause the method to return an empty list.

### Error Conditions in `configurable_supplier_scraper.py`
*   **Network Errors:** The `get_page_content` method implements retries with exponential backoff for network timeouts and rate limiting (HTTP 429).
*   **Authentication Failures:** The scraper can detect when a login is required (e.g., by checking for "Log in to view prices" text) and can trigger an authentication callback.
*   **Selector Failures:** If configured selectors fail to extract data, the scraper will log a warning and attempt to use fallback selectors or AI-powered extraction (if enabled).
*   **Memory Management:** The scraper includes proactive memory cleanup to prevent crashes during long scraping sessions.

### Error Conditions in `FBA_Financial_calculator.py`
*   **Missing Files:** The `run_calculations` function will raise an exception if the supplier cache file or Amazon data directory cannot be found.
*   **Missing Data:** If a product is missing critical data (EAN, ASIN, title), it will be skipped with a warning logged.
*   **Price Extraction:** If no price can be found in the Amazon data, the product is skipped, and a detailed warning is logged listing all the price fields that were checked.

### Error Conditions in `fixed_enhanced_state_manager.py`
*   **File I/O Errors:** The `save_state_atomic` method uses multiple fallback strategies (thread-safe writer, legacy atomic save, basic temp file) to ensure the state is saved even if one method fails.
*   **State Corruption:** The `validate_and_repair_state` method can detect and repair common state corruption patterns, such as impossible index states or phase contamination.
*   **Concurrency:** The state manager uses file locking to prevent data corruption when multiple processes attempt to write to the state file simultaneously.