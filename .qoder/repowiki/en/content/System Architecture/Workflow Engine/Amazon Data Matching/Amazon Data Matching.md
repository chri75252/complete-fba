# Amazon Data Matching

<cite>
**Referenced Files in This Document**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py)
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py)
- [Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt](file://Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt)
- [rag_index.json](file://OUTPUTS/CONTROL_PLANE/index/rag_index.json)
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
This document explains the Amazon data matching subsystem that links supplier products to Amazon listings using an EAN-first, title-fallback strategy. It covers the `_get_amazon_data` method, the FixedAmazonExtractor integration, sponsored ad filtering, title similarity validation using difflib scoring, confidence scoring mechanisms, fallback strategies when EAN matching fails, and integration with EnhancedStateManager for progress tracking and linking map creation. It also addresses common issues like Amazon's anti-bot measures, search result filtering, and performance optimization for large product catalogs.

## Project Structure
The Amazon data matching subsystem spans three primary areas:
- Supplier-to-Amazon matching orchestration in the workflow
- Specialized Amazon search and extraction logic in the extractor
- State management and linking map persistence

```mermaid
graph TB
subgraph "Supplier Side"
A["ConfigurableSupplierScraper"]
B["Supplier Product Data"]
end
subgraph "Matching Orchestration"
C["PassiveExtractionWorkflow"]
D["_get_amazon_data()"]
E["_validate_product_match()"]
end
subgraph "Amazon Side"
F["FixedAmazonExtractor"]
G["search_by_ean_and_extract_data()"]
H["search_by_title_using_search_bar()"]
I["extract_data()"]
end
subgraph "State & Persistence"
J["EnhancedStateManager"]
K["Linking Map"]
L["Amazon Cache"]
end
A --> B
B --> C
C --> D
D --> F
F --> G
F --> H
G --> I
H --> I
I --> J
I --> K
I --> L
```

**Diagram sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L800)

**Section sources**
- [Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt](file://Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt#L11-L47)
- [rag_index.json](file://OUTPUTS/CONTROL_PLANE/index/rag_index.json#L953-L1003)

## Core Components
- PassiveExtractionWorkflow: Orchestrates supplier product extraction, Amazon matching, validation, and persistence.
- FixedAmazonExtractor: Specialized Amazon searcher extending the base extractor, implementing EAN-first search and title fallback.
- EnhancedStateManager: Tracks progress, resumes from checkpoints, and persists state for linking map and cache.
- Linking Map: Persistent association between supplier EANs and Amazon ASINs.
- Amazon Cache: Stores extracted product data to avoid redundant scraping.

Key responsibilities:
- EAN-first matching via search_by_ean_and_extract_data
- Sponsored ad filtering during search
- Title similarity validation using difflib scoring
- Confidence scoring and fallback to title search
- Progress tracking and linking map updates

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L800)

## Architecture Overview
The matching pipeline follows a deterministic, stateful workflow:
1. Supplier product data is extracted and filtered.
2. For each product, _get_amazon_data decides between EAN-first and title-fallback matching.
3. FixedAmazonExtractor executes the chosen search strategy.
4. Results are validated using title similarity scoring.
5. Successful matches update the linking map and Amazon cache.
6. EnhancedStateManager tracks progress and persists state.

```mermaid
sequenceDiagram
participant WF as "Workflow"
participant SM as "EnhancedStateManager"
participant FE as "FixedAmazonExtractor"
participant AM as "Amazon.co.uk"
WF->>SM : "load_state()"
SM-->>WF : "state data"
WF->>WF : "filter_by_price_range()"
loop "For each product"
WF->>FE : "_get_amazon_data(product)"
alt "EAN available"
FE->>AM : "search_by_ean_and_extract_data(EAN, title)"
AM-->>FE : "search results"
FE->>FE : "filter sponsored results"
FE->>FE : "select best match"
else "No EAN"
FE->>AM : "search_by_title_using_search_bar(title)"
AM-->>FE : "search results"
end
FE-->>WF : "Amazon product data"
WF->>WF : "_validate_product_match()"
WF->>SM : "update_processing_progress()"
WF->>WF : "persist state and linking map"
end
```

**Diagram sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L800)

## Detailed Component Analysis

### _get_amazon_data Method Implementation
The `_get_amazon_data` method orchestrates the dual-pronged matching strategy:
- EAN-first search using FixedAmazonExtractor.search_by_ean_and_extract_data
- Title-fallback using FixedAmazonExtractor.search_by_title_using_search_bar
- Title similarity validation via _validate_product_match
- Confidence scoring and match acceptance thresholds

Processing logic:
- If supplier product has a valid EAN, attempt EAN search first.
- If EAN search yields no valid organic results, fall back to title search.
- Validate candidate using difflib-based similarity scoring.
- Record the search method used and persist results.

```mermaid
flowchart TD
Start(["Start _get_amazon_data"]) --> CheckEAN["Check supplier EAN"]
CheckEAN --> HasEAN{"EAN present?"}
HasEAN --> |Yes| EANSearch["search_by_ean_and_extract_data(EAN, title)"]
EANSearch --> EANSuccess{"EAN search successful?"}
EANSuccess --> |Yes| ValidateEAN["Validate candidate via _validate_product_match()"]
EANSuccess --> |No| TitleSearch["search_by_title_using_search_bar(title)"]
HasEAN --> |No| TitleSearch
TitleSearch --> ValidateTitle["Validate candidate via _validate_product_match()"]
ValidateEAN --> Accept{"Accept match?"}
ValidateTitle --> Accept
Accept --> |Yes| Persist["Persist to linking map and cache"]
Accept --> |No| NoMatch["Record no match"]
Persist --> End(["End"])
NoMatch --> End
```

**Diagram sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)
- [Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt](file://Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt#L27-L47)

### FixedAmazonExtractor Integration
FixedAmazonExtractor extends the base AmazonExtractor and implements:
- search_by_ean_and_extract_data: EAN-first search with sponsored result filtering and robust ASIN extraction.
- search_by_title_using_search_bar: Title-based search using the search bar.
- extract_data: Full extraction for the selected ASIN.

Key features:
- Sponsored ad filtering by visibility detection (DOM-based).
- Four-fallback ASIN extraction methods (data-asin, /dp/ pattern, data-uuid, regex).
- Reuse of browser pages to maintain extension state.

```mermaid
classDiagram
class AmazonExtractor {
+connect()
+extract_data(asin)
}
class FixedAmazonExtractor {
+search_by_ean_and_extract_data(ean, title)
+search_by_title_using_search_bar(title)
+extract_data(asin)
+_overlap_score(title_a, title_b)
}
AmazonExtractor <|-- FixedAmazonExtractor
```

**Diagram sources**
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)

**Section sources**
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)
- [Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt](file://Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt#L36-L47)

### Sponsored Ad Filtering
During EAN search, the system filters out sponsored results:
- Visibility-based detection: sponsored results are often hidden by AdBlocker and thus invisible in the DOM.
- Organic-first selection: the first visible organic result is chosen, trusting Amazon’s ranking.

This simplifies matching and reduces false positives from paid placements.

**Section sources**
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)

### Title Similarity Validation Using difflib Scoring
The `_validate_product_match` function computes a confidence score using word overlap:
- Normalizes titles (remove punctuation, lowercase).
- Computes Jaccard similarity between word sets.
- Accepts matches meeting configured thresholds.

```mermaid
flowchart TD
A["Normalize supplier title"] --> B["Tokenize words"]
C["Normalize Amazon title"] --> D["Tokenize words"]
B --> E["Compute intersection and union"]
D --> E
E --> F["Confidence = |intersection| / |union|"]
F --> G{"Confidence ≥ threshold?"}
G --> |Yes| H["Accept match"]
G --> |No| I["Reject match"]
```

**Diagram sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)

### Confidence Scoring Mechanisms and Fallback Strategies
Confidence scoring:
- EAN-first matches are treated as authoritative; validation focuses on title similarity to confirm identity.
- Title-fallback uses difflib scoring with configurable thresholds.

Fallback strategies:
- If EAN search fails or returns no valid organic results, the system falls back to title search.
- If title search also fails, the product is recorded as unmatched.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)
- [Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt](file://Architectural_Summary_passive_extraction_workflow_latest-enhanced.txt#L27-L47)

### Integration with EnhancedStateManager and Linking Map Creation
EnhancedStateManager tracks:
- Resumption pointers and progress across supplier and Amazon phases.
- Category denominators and completed counts.
- Metrics and validation for resume correctness.

Linking Map creation:
- On successful match, the system creates an entry associating supplier EAN/url with Amazon ASIN.
- Entries include titles, prices, match method, confidence, and timestamps.

```mermaid
sequenceDiagram
participant WF as "Workflow"
participant SM as "EnhancedStateManager"
participant LM as "Linking Map"
participant AC as "Amazon Cache"
WF->>SM : "update_processing_progress()"
WF->>LM : "add_linking_map_entry(supplier_ean, asin, metadata)"
WF->>AC : "cache_amazon_data(asin, data)"
SM-->>WF : "save_state_atomic()"
```

**Diagram sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L800)
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L800)
- [rag_index.json](file://OUTPUTS/CONTROL_PLANE/index/rag_index.json#L3578-L3643)

## Dependency Analysis
The matching subsystem exhibits clear separation of concerns:
- Workflow depends on Extractor for Amazon interactions.
- Extractor depends on BrowserManager for browser lifecycle.
- State Manager persists progress and linking map.
- Linking Map and Cache provide persistence for matches and extracted data.

```mermaid
graph TB
WF["PassiveExtractionWorkflow"] --> FE["FixedAmazonExtractor"]
FE --> BM["BrowserManager"]
WF --> SM["EnhancedStateManager"]
WF --> LM["Linking Map"]
WF --> AC["Amazon Cache"]
FE --> AC
```

**Diagram sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L800)

**Section sources**
- [rag_index.json](file://OUTPUTS/CONTROL_PLANE/index/rag_index.json#L953-L1003)

## Performance Considerations
- EAN-first search minimizes title parsing overhead and reduces false positives.
- Sponsored ad filtering avoids expensive validations on paid placements.
- Hash-based linking map and cache reduce repeated scraping.
- Batched state saves and atomic writes prevent partial writes and corruption.
- Memory monitoring and garbage collection help sustain long runs.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and remedies:
- Anti-bot measures: The system uses realistic navigation and visibility-based sponsored filtering to avoid detection.
- Missing EANs: Fall back to title search; ensure supplier scraping extracts EANs reliably.
- False matches: Increase similarity thresholds; validate with additional metadata.
- Performance bottlenecks: Enable caching, batch saves, and monitor memory usage.
- Resume inconsistencies: EnhancedStateManager enforces monotonicity and validates resume pointers.

**Section sources**
- [amazon_playwright_extractor.py](file://tools/amazon_playwright_extractor.py#L435-L850)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L800)
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L6145-L6573)

## Conclusion
The Amazon data matching subsystem combines deterministic EAN-first matching with robust title-fallback validation, sponsored ad filtering, and strong state management. The FixedAmazonExtractor encapsulates Amazon-specific logic, while EnhancedStateManager and the linking map ensure reliable progress tracking and persistence. Together, these components deliver scalable, auditable, and high-confidence supplier-to-Amazon linkage suitable for large catalogs.