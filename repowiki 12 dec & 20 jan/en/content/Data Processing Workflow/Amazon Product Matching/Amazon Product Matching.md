# Amazon Product Matching

<cite>
**Referenced Files in This Document**   
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py)
- [amazon_playwright_extractor.py](file://tools\amazon_playwright_extractor.py)
- [system_config.json](file://config\system_config.json)
</cite>

## Update Summary
**Changes Made**   
- Updated documentation to reflect the simplified matching strategy that selects the first visible organic product result from Amazon search.
- Added detailed information about the four-fallback method for ASIN extraction.
- Enhanced description of visibility filtering to skip sponsored products using AdBlocker detection.
- Documented the implementation of the FixedAmazonExtractor class and its EAN-based search functionality.
- Updated product match validation section to reflect removal of title similarity scoring for EAN searches.

## Table of Contents
1. [Introduction](#introduction)
2. [Core Matching Strategy](#core-matching-strategy)
3. [FixedAmazonExtractor Implementation](#fixedamazonextractor-implementation)
4. [Linking Map and Persistent Associations](#linking-map-and-persistent-associations)
5. [Product Match Validation](#product-match-validation)
6. [Integration with Financial Analysis](#integration-with-financial-analysis)
7. [Common Issues and Solutions](#common-issues-and-solutions)
8. [Performance Optimization Techniques](#performance-optimization-techniques)

## Introduction
The Amazon product matching sub-feature is a critical component of the FBA agent system, responsible for identifying corresponding products on Amazon.co.uk for supplier items from poundwholesale.co.uk. This document details the implementation of the dual-pronged matching strategy, the FixedAmazonExtractor class, and the integration between supplier product extraction, Amazon search, and financial analysis. The system employs sophisticated techniques to ensure accurate product matching while optimizing performance through caching and batch processing.

## Core Matching Strategy
The product matching system implements a dual-pronged approach that prioritizes EAN-based matching and falls back to title-based matching when EAN is unavailable. This strategy ensures high-confidence matches while maintaining flexibility for products without standardized identifiers.

The primary matching workflow begins with EAN-based search using the `search_by_ean_and_extract_data` method. When an EAN is present in the supplier product data, the system searches Amazon.co.uk using the EAN as the query parameter. If the EAN search fails or no EAN is available, the system automatically falls back to title-based matching by invoking `search_by_title_using_search_bar` with the supplier product title.

This fallback mechanism is implemented in the `_get_amazon_data` method, which first attempts EAN search and only proceeds to title search if the EAN search returns no valid results. The system records the search method used in the `_search_method_used` field of the product data, providing an audit trail of the matching process.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L6470-L6538)

## FixedAmazonExtractor Implementation
The FixedAmazonExtractor class extends the base AmazonExtractor to provide specialized functionality for EAN-based product matching on Amazon.co.uk. This class implements the `search_by_ean_and_extract_data` method, which orchestrates the entire EAN search and data extraction process.

The method begins by connecting to the browser through the centralized BrowserManager singleton, ensuring consistent browser state across the application. It then navigates to Amazon.co.uk and inputs the EAN into the search bar, simulating user behavior to avoid detection. The search results are processed using multiple selectors to identify product tiles, with robust error handling to accommodate Amazon's dynamic page structure.

A critical feature of this implementation is the filtering of sponsored results. The system employs a visibility-based detection strategy that examines whether search result elements are visible in the DOM. Sponsored products hidden by AdBlocker (uBlock Origin) are automatically filtered out, as they are typically concealed using CSS. This approach replaces the previous complex five-check sponsored detection system with a simpler, more reliable method.

When organic results are found, the system selects the first visible organic product based on Amazon's relevance ranking rather than applying title similarity scoring, as EAN matches are considered authoritative. This simplified strategy trusts Amazon's search algorithm to return the most relevant product first.

The system implements a four-fallback method for ASIN extraction to ensure maximum reliability:
1. **data-asin attribute**: Extracts ASIN from the `data-asin` HTML attribute
2. **href /dp/ASIN pattern**: Extracts ASIN from product link URLs containing `/dp/` patterns
3. **data-uuid attribute**: Uses alternative Amazon format identifiers
4. **Regex search in HTML**: Performs pattern matching on the element's inner HTML as a last resort

```mermaid
sequenceDiagram
participant Workflow as PassiveExtractionWorkflow
participant Extractor as FixedAmazonExtractor
participant Browser as BrowserManager
participant Amazon as Amazon.co.uk
Workflow->>Extractor : search_by_ean_and_extract_data(ean, title)
Extractor->>Browser : get_page_for_url(amazon.co.uk)
Browser-->>Extractor : Page instance
Extractor->>Amazon : Navigate to amazon.co.uk
Extractor->>Amazon : Fill search box with EAN
Extractor->>Amazon : Press Enter
Amazon-->>Extractor : Search results
Extractor->>Extractor : Filter sponsored results by visibility
Extractor->>Extractor : Apply 4-fallback ASIN extraction
Extractor->>Extractor : Select first visible organic result
Extractor->>Extractor : extract_data(asin)
Extractor-->>Workflow : Amazon product data
```

**Diagram sources**
- [amazon_playwright_extractor.py](file://tools\amazon_playwright_extractor.py#L2141-L2349)

**Section sources**
- [amazon_playwright_extractor.py](file://tools\amazon_playwright_extractor.py#L2141-L2349)

## Linking Map and Persistent Associations
The linking map in `linking_maps/poundwholesale.co.uk` maintains persistent associations between supplier products and Amazon ASINs, serving as the system's memory for product matching decisions. This JSON file contains entries that map supplier EANs to Amazon ASINs along with metadata about the match.

Each entry in the linking map includes:
- `supplier_ean`: The EAN from the supplier product
- `amazon_asin`: The corresponding ASIN on Amazon.co.uk
- `supplier_title` and `amazon_title`: Product titles for reference and validation
- `supplier_price` and `amazon_price`: Pricing information
- `match_method`: The method used for matching (EAN, title, or none)
- `confidence`: Confidence score of the match
- `created_at`: Timestamp of when the association was created
- `supplier_url`: Source URL of the supplier product

The linking map prevents redundant processing by allowing the system to skip Amazon analysis for products that have already been matched. Before initiating a new search, the system checks the linking map using the HashLookupOptimizer for O(1) performance. If a match exists, the previously retrieved Amazon data is reused, significantly improving processing speed.

For products that cannot be matched, the system creates "no-match" entries with `match_method: "none"` and includes a `no_match_reason` field to document why the matching failed. This prevents infinite reprocessing loops and provides valuable diagnostic information.

```mermaid
erDiagram
LINKING_MAP {
string supplier_ean PK
string amazon_asin
string supplier_title
string amazon_title
float supplier_price
float amazon_price
string match_method
float confidence
datetime created_at
string supplier_url
string no_match_reason
}
```

**Diagram sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L2400-L2600)

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L2400-L2600)

## Product Match Validation
The system has been updated to simplify the product match validation process. For EAN-based searches, the system now trusts Amazon's search relevance ranking and selects the first visible organic result without applying title similarity scoring. This change eliminates the need for confidence scoring based on title overlap for EAN matches, as the EAN provides a definitive product identifier.

The `_validate_product_match` function has been effectively bypassed for EAN-based matches, as the match quality is considered high by default when an EAN is successfully matched. For title-based fallback searches, the system still uses title overlap scoring to validate matches, but this is now only applied when EAN is unavailable.

The validation thresholds remain configurable through the system configuration:
- High similarity (≥0.75): High confidence (0.9)
- Medium similarity (≥0.5): Medium confidence (0.6)
- Low similarity (≥0.25): Low confidence (0.3)
- Below threshold: Very low confidence (0.1)

However, these thresholds are only applied in the title-based fallback scenario, not for EAN-based matches.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L6602-L6628)
- [system_config.json](file://config\system_config.json#L144-L148)

## Integration with Financial Analysis
The product matching system is tightly integrated with the financial analysis pipeline, forming a critical link between product identification and profitability assessment. Once a product match is validated, the system passes the combined supplier and Amazon data to the FBA_Financial_calculator for ROI and profit margin analysis.

The integration occurs in the main processing loop of the PassiveExtractionWorkflow class, where successful Amazon data retrieval triggers the financial calculation process. The calculator uses Amazon's FBA fee structure, including fulfillment fees, referral fees, and storage costs, to determine net profit and return on investment.

Products that meet the configured profitability criteria (minimum ROI percentage and minimum profit per unit) are added to the list of profitable results, while others are filtered out. This integration ensures that only genuinely profitable products are recommended, aligning the technical matching process with business objectives.

The linking map serves as the bridge between these systems, storing the matched product data in a format that can be easily consumed by the financial analyzer. The atomic write pattern used for updating the linking map ensures data integrity even if the process is interrupted.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L1970-L2316)

## Common Issues and Solutions
The product matching system addresses several common challenges in e-commerce product matching:

**False Matches**: The system mitigates false matches through sponsored result filtering and the simplified matching strategy. By excluding sponsored products and selecting the first organic result for EAN searches, the system reduces the risk of matching to incorrect or irrelevant products.

**Sponsored Product Interference**: The visibility-based sponsored detection system examines whether search result elements are visible in the DOM. Products hidden by AdBlocker (uBlock Origin) are automatically filtered out, as they are typically concealed using CSS. This prevents the system from selecting promoted products that may not represent the best organic match.

**Missing EANs**: When EANs are unavailable, the system falls back to title-based matching with similarity scoring. For products without EANs, the system uses a sanitized version of the product title as the filename identifier in the Amazon cache, enabling retrieval and reuse of previously matched data.

**Authentication Issues**: The system includes authentication fallback mechanisms that detect login requirements and trigger re-authentication through the SupplierAuthenticationService. This ensures uninterrupted operation even when supplier site sessions expire.

**State Corruption**: The EnhancedStateManager with atomic write operations prevents state corruption during interruptions. The system can resume from the last processed index, avoiding duplicate processing and data inconsistencies.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L992-L1020)

## Performance Optimization Techniques
The system employs several performance optimization techniques to handle large product catalogs efficiently:

**O(1) Hash Lookups**: The HashLookupOptimizer enables constant-time lookups in the linking map, replacing linear searches that would scale poorly with large datasets. This optimization provides approximately 3,650x performance improvement for linking map queries.

**Batched Processing**: Supplier products are processed in configurable batches, with periodic saves of the linking map and processing state. This batched approach provides memory management benefits and allows for progress tracking and resumption.

**Cached Data Reuse**: The system extensively caches Amazon product data to avoid redundant API calls and page loads. When a product has been previously matched, the cached data is reused instead of reprocessing.

**Browser Reuse**: The FixedAmazonExtractor reuses existing browser pages through the BrowserManager singleton, maintaining Chrome extension functionality and reducing the overhead of browser initialization.

**Atomic Persistence**: Critical state files are saved using an atomic write pattern (write to temp file, then rename), ensuring data integrity even if the process is interrupted during a save operation.

**Parallelizable Design**: The architecture supports parallel processing of product batches, though the current implementation processes sequentially to maintain state consistency.

```mermaid
graph TD
A[Performance Optimizations] --> B[O(1) Hash Lookups]
A --> C[Batched Processing]
A --> D[Cached Data Reuse]
A --> E[Browser Reuse]
A --> F[Atomic Persistence]
B --> G[HashLookupOptimizer]
C --> H[Batch Size Configuration]
D --> I[Amazon Cache Directory]
E --> J[BrowserManager Singleton]
F --> K[Atomic File Operations]
```

**Diagram sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L2400-L2600)

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools\passive_extraction_workflow_latest.py#L2400-L2600)