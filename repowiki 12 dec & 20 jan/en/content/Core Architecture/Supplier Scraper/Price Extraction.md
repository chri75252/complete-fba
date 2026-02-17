# Price Extraction

<cite>
**Referenced Files in This Document**   
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py)
- [system_config.json](file://config/system_config.json)
- [supplier_config_loader.py](file://config/supplier_config_loader.py)
- [www.poundwholesale.co.uk.json](file://config/supplier_configs/www.poundwholesale.co.uk.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Implementation Strategy](#implementation-strategy)
3. [Selector Configuration and Fallback Mechanism](#selector-configuration-and-fallback-mechanism)
4. [AI-Powered Fallback Extraction](#ai-powered-fallback-extraction)
5. [Price Preprocessing and Validation](#price-preprocessing-and-validation)
6. [Handling Complex Pricing Scenarios](#handling-complex-pricing-scenarios)
7. [Configuration and Troubleshooting](#configuration-and-troubleshooting)

## Introduction
The `extract_price()` method within the `ConfigurableSupplierScraper` class is a critical component for reliably extracting pricing information from supplier websites. This method is designed to handle the variability and complexity of e-commerce websites by leveraging a multi-layered approach that combines configurable CSS selectors, preprocessing, validation, and AI-powered fallbacks. The system is built to ensure robustness against dynamic content, obfuscated rendering, and authentication requirements, making it suitable for financial analysis and integration with Amazon FBA workflows.

## Implementation Strategy
The `extract_price()` method implements a systematic strategy for price extraction that prioritizes reliability and accuracy. The process begins by loading supplier-specific CSS selectors from external configuration files, which are managed by the `supplier_config_loader.py` module. These selectors are loaded based on the domain of the supplier website, allowing for customization and adaptation to different site structures. The method then applies these selectors in a prioritized sequence to locate price elements within the HTML content of a product page.

When a price element is found, the raw text is passed to the `_parse_price()` helper method for preprocessing and conversion to a standardized float value. This two-step process—selector application followed by parsing—ensures that the system can handle a wide range of price formats and currency symbols. The method is designed to be asynchronous, allowing it to integrate seamlessly with the Playwright-based browser automation used for page navigation and content retrieval.

The implementation also includes comprehensive error handling and logging, which is crucial for diagnosing extraction failures and maintaining system reliability. The method is integrated with the system's state management and progress tracking, ensuring that price extraction failures are properly recorded and can be addressed in subsequent processing cycles.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2650-L2685)

## Selector Configuration and Fallback Mechanism
The `extract_price()` method relies on a configurable set of CSS selectors to locate price information on supplier websites. These selectors are defined in JSON configuration files located in the `config/supplier_configs/` directory, with each file corresponding to a specific supplier domain. For example, the configuration for `www.poundwholesale.co.uk` includes multiple selectors for the price field, such as `.price`, `.cost`, `[data-price]`, and `.price-current`, providing a fallback mechanism if one selector fails.

The method uses the `_get_selectors_for_domain()` function to retrieve the appropriate selector configuration based on the current URL's domain. This function implements a priority-based loading system that first checks for a validated supplier package, then falls back to the legacy configuration files. The selectors are applied in sequence, and the first successful extraction is returned, ensuring that the system can adapt to changes in the website's HTML structure.

This fallback mechanism is further enhanced by the use of the `_extract_with_selector()` helper method, which supports both simple CSS selectors and more complex configurations that include attribute extraction and regex-based post-processing. This flexibility allows the system to handle cases where the price is stored in a data attribute or embedded within a larger text string.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2650-L2685)
- [supplier_config_loader.py](file://config/supplier_config_loader.py#L1-L187)
- [www.poundwholesale.co.uk.json](file://config/supplier_configs/www.poundwholesale.co.uk.json#L1-L66)

## AI-Powered Fallback Extraction
When the selector-based extraction methods fail, the `extract_price()` method integrates with an AI-powered extraction system as a final fallback. This integration is facilitated by the OpenAI client, which is configured through the system settings in `system_config.json`. The AI client is used to analyze the HTML content of the product page and extract the price information using natural language processing.

The AI extraction is triggered when no valid price is found after applying all configured selectors. The method calls the `_ai_extract_field_from_html_element()` function, which constructs a prompt for the AI model containing the HTML snippet of the product page and a request to extract the price. The AI model is instructed to return only the extracted value, without any additional commentary, ensuring that the output is clean and can be easily processed.

This AI-powered fallback is particularly useful for handling cases where the price information is obfuscated or rendered dynamically using JavaScript, making it difficult to extract using traditional CSS selectors. The integration with the AI system is optional and can be disabled through the system configuration, allowing users to control the trade-off between extraction reliability and processing cost.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2650-L2685)
- [system_config.json](file://config/system_config.json#L1-L300)

## Price Preprocessing and Validation
The `extract_price()` method includes a comprehensive preprocessing and validation pipeline to ensure that the extracted prices are accurate and suitable for financial analysis. The preprocessing is performed by the `_parse_price()` helper method, which is responsible for cleaning the raw price text and converting it to a standardized float value.

The preprocessing pipeline begins by removing common prefixes and suffixes, such as "sale price," "was," "rrp," and "ex vat," as well as currency symbols like "£," "$," and "€." This is achieved using regular expressions that match and remove these patterns from the text. The method also handles various decimal and thousands separators, normalizing formats such as "1,234.56," "1.234,56," and "1 234.56" to a consistent decimal format.

After preprocessing, the method validates the extracted price by checking that it falls within a reasonable range (between £0.01 and £5,000,000) and that it can be successfully converted to a float. If the price fails validation, the method returns `None`, indicating that the extraction was unsuccessful. This validation step is crucial for preventing erroneous data from being used in financial calculations and ensuring the integrity of the analysis.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2687-L2735)

## Handling Complex Pricing Scenarios
The `extract_price()` method is designed to handle a variety of complex pricing scenarios that are common in e-commerce websites. One such scenario is dynamic pricing, where the price is updated in real-time based on user interactions or external factors. The method addresses this by using Playwright to render the full HTML content of the page, including any dynamically generated content, before attempting to extract the price.

Another challenge is tiered pricing displays, where multiple prices are shown for different quantities or bulk discounts. The method handles this by prioritizing the selectors that target the most relevant price, such as the base price or the price for a single unit. If multiple prices are present, the method returns the first valid price found, which is typically the most prominent one on the page.

The method also addresses the issue of obfuscated price rendering, where the price is displayed using images, CSS transformations, or other techniques that make it difficult to extract using traditional methods. In such cases, the AI-powered fallback extraction is used to analyze the visual representation of the price and extract the value. This ensures that the system can handle even the most challenging pricing displays.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2650-L2685)

## Configuration and Troubleshooting
Configuring the `extract_price()` method for a new supplier involves creating a JSON configuration file in the `config/supplier_configs/` directory. This file should define the CSS selectors for the price field, as well as any other relevant fields such as the product title, URL, and image. The selectors should be tested and validated to ensure that they accurately target the desired elements on the supplier's website.

Common extraction failures can be troubleshooted by reviewing the system logs, which provide detailed information about the extraction process, including which selectors were applied and whether the AI fallback was triggered. If a selector is not working, it may need to be updated to reflect changes in the website's HTML structure. In cases where the price is not being extracted correctly, the preprocessing pipeline should be reviewed to ensure that it is properly handling the specific format used by the supplier.

The system also includes a proactive authentication check that verifies the login status every 25 products to prevent pricing failures due to session expiration. If pricing failures are observed, this check can help identify whether the issue is related to authentication or selector configuration. Additionally, the system's state management and progress tracking can be used to resume extraction from the point of failure, minimizing the need for reprocessing.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2650-L2685)
- [supplier_config_loader.py](file://config/supplier_config_loader.py#L1-L187)
- [www.poundwholesale.co.uk.json](file://config/supplier_configs/www.poundwholesale.co.uk.json#L1-L66)