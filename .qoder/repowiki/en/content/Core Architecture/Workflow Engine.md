# Workflow Engine

<cite>
**Referenced Files in This Document**   
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py)
- [system_config_loader.py](file://config/system_config_loader.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Components](#core-components)
3. [Architecture Overview](#architecture-overview)
4. [Detailed Component Analysis](#detailed-component-analysis)
5. [Data Flow and Processing](#data-flow-and-processing)
6. [Resilience and State Management](#resilience-and-state-management)
7. [Integration Points](#integration-points)
8. [Sequence Diagrams](#sequence-diagrams)
9. [Conclusion](#conclusion)

## Introduction
The PassiveExtractionWorkflow class serves as the central orchestrator of the Amazon FBA Agent System, coordinating the end-to-end process of identifying profitable products for Amazon FBA resale. This workflow integrates supplier data scraping, Amazon product matching, financial analysis, and stateful processing to create a robust product sourcing pipeline. The system is designed to handle complex e-commerce websites with resilience features including stateful resume capability, integrated authentication retry, and atomic data persistence. This documentation provides a comprehensive analysis of the workflow's architecture, execution flow, and integration points.

## Core Components
The PassiveExtractionWorkflow class coordinates several key components to execute the product sourcing workflow. It manages the extraction of supplier products through the ConfigurableSupplierScraper, retrieves Amazon data using the FixedAmazonExtractor, maintains processing state with the EnhancedStateManager, and performs financial calculations through the FBA_Financial_calculator. The workflow is configured through system_config.json, which controls operational parameters such as batch sizes, financial thresholds, and processing limits. The main execution flow begins with initialization and configuration loading, proceeds through batched supplier product extraction, Amazon data retrieval with EAN-first/title-fallback matching, financial calculation, and concludes with state management and report generation.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)

## Architecture Overview
The PassiveExtractionWorkflow implements a modular, stateful architecture that coordinates multiple specialized components to achieve its product sourcing objectives. The workflow follows a sequential processing model with distinct phases: initialization, supplier data extraction, Amazon data retrieval, financial analysis, and reporting. Each phase is designed with resilience in mind, incorporating error handling, retry mechanisms, and state persistence. The architecture emphasizes separation of concerns, with dedicated components for supplier scraping, Amazon data extraction, state management, and financial calculations. Configuration is centralized in system_config.json, ensuring a single source of truth for operational parameters. The workflow processes supplier categories in configurable batches to manage memory usage and system stability, particularly important when scraping suppliers with extensive product catalogs.

```mermaid
graph TB
subgraph "Configuration"
Config[system_config.json]
end
subgraph "Orchestration"
Workflow[PassiveExtractionWorkflow]
end
subgraph "Data Extraction"
SupplierScraper[ConfigurableSupplierScraper]
AmazonExtractor[FixedAmazonExtractor]
end
subgraph "State Management"
StateManager[EnhancedStateManager]
end
subgraph "Financial Analysis"
FinancialCalculator[FBA_Financial_calculator]
end
subgraph "Data Storage"
SupplierCache[Supplier Product Cache]
AmazonCache[Amazon Data Cache]
LinkingMap[Linking Map]
end
Config --> Workflow
Workflow --> SupplierScraper
Workflow --> AmazonExtractor
Workflow --> StateManager
Workflow --> FinancialCalculator
SupplierScraper --> SupplierCache
AmazonExtractor --> AmazonCache
Workflow --> LinkingMap
StateManager --> |State Persistence| Workflow
FinancialCalculator --> |Financial Analysis| Workflow
```

**Diagram sources **
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L1-L590)

## Detailed Component Analysis
The PassiveExtractionWorkflow class implements a comprehensive product sourcing workflow through several key methods that coordinate the extraction, matching, and analysis of supplier and Amazon products. The workflow is designed to be resilient, stateful, and configurable, allowing it to adapt to different supplier websites and processing requirements.

### PassiveExtractionWorkflow Class Analysis
The PassiveExtractionWorkflow class serves as the central orchestrator of the Amazon FBA agent system, coordinating the extraction of supplier products, matching with Amazon listings, and financial analysis to identify profitable resale opportunities. The class is initialized with configuration parameters loaded from system_config.json, which define operational parameters such as batch sizes, financial thresholds, and processing limits. The workflow manages the entire product sourcing pipeline from category URL processing through final report generation, implementing a stateful approach that allows for interruption and resumption of processing.

#### Key Methods of PassiveExtractionWorkflow
```mermaid
classDiagram
class PassiveExtractionWorkflow {
+run() void
+_extract_supplier_products() Product[]
+_get_amazon_data(Product) AmazonData
+_validate_product_match(String, String) Float
+_process_existing_products_with_amazon_extraction() void
+_save_state_periodically() void
+_check_financial_report_trigger() void
+_perform_authentication_fallback() void
+_determine_price_phase() String
+_save_category_manifest() void
+_get_cached_products_path() String
+_record_ai_decision() void
}
class ConfigurableSupplierScraper {
+scrape_products_from_url(String, Int) Product[]
+fetch_html(String) String
+set_progress_callback(Callable) void
+extract_price(BeautifulSoup, String, String) Float
+_extract_text_by_selector(BeautifulSoup, String[]) String
+_extract_image_by_selector(BeautifulSoup, String[]) String
}
class FixedAmazonExtractor {
+search_by_ean_and_extract_data(String) AmazonData
+search_by_title_using_search_bar(String) AmazonData
+extract_data(String) AmazonData
+_overlap_score(String, String) Float
+connect() Browser
}
class EnhancedStateManager {
+load_state() Boolean
+save_state() void
+save_state_atomic() void
+update_processing_progress(Int, String) void
+get_resumption_ptr() ResumptionPtr
+set_resumption_ptr(String, Int, Int) void
+perform_startup_analysis() Dict~String, Any~
+update_discovered_products_in_category(String, Int) void
+validate_and_repair_state() Tuple~Boolean, String[]~
+initialize_category_processing(Int, String, Int) void
}
class FBA_Financial_calculator {
+run_calculations(String) Dict~String, Any~
+financials(Dict~String, Any~, Dict~String, Any~, Float) Dict~String, Any~
+find_amazon_json(String, String, String, String, String) Dict~String, Any~
+find_amazon_json_by_linking_map(String, String, String, String) Dict~String, Any~
+find_amazon_json_by_asin(String, String) Dict~String, Any~
+extract_keepa_fees(Dict~String, Any~) Tuple~Float, Float~
+extract_enhanced_metrics(Dict~String, Any~) Dict~String, Any~
}
PassiveExtractionWorkflow --> ConfigurableSupplierScraper : "uses"
PassiveExtractionWorkflow --> FixedAmazonExtractor : "uses"
PassiveExtractionWorkflow --> EnhancedStateManager : "uses"
PassiveExtractionWorkflow --> FBA_Financial_calculator : "uses"
ConfigurableSupplierScraper --> EnhancedStateManager : "auth_callback"
FixedAmazonExtractor --> BrowserManager : "connects"
```

**Diagram sources **
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L1-L590)

#### Main Execution Flow
```mermaid
flowchart TD
A[Start] --> B[Initialize Workflow]
B --> C[Load Configuration from system_config.json]
C --> D[Load Processing State]
D --> E[Perform Startup Analysis]
E --> F[Load Predefined Category URLs]
F --> G[Batched Supplier Product Extraction]
G --> H[Filter Products by Price Range]
H --> I[Slice Products from Last Processed Index]
I --> J{Products Remaining?}
J --> |Yes| K[Process Next Product]
K --> L[Get Amazon Data with EAN-First/Title-Fallback]
L --> M[Validate Product Match]
M --> N[Calculate Financials]
N --> O[Check Profitability Criteria]
O --> |Meets Criteria| P[Add to Profitable Results]
O --> |Does Not Meet| Q[Skip Product]
P --> R[Mark Product as Processed]
Q --> R
R --> S[Update Processing Progress]
S --> T[Check Periodic Save Condition]
T --> |Save Required| U[Save State Atomically]
T --> |No Save| V{Cycle Complete?}
U --> V
V --> |No| J
V --> |Yes| W[Finalize Processing]
W --> X[Generate Financial Report]
X --> Y[Generate Profitable Products Report]
Y --> Z[End]
```

**Diagram sources **
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L1970-L2316)
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L2318-L2435)
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L2437-L2525)

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)

## Data Flow and Processing
The PassiveExtractionWorkflow implements a comprehensive data flow that begins with category URLs and progresses through multiple processing stages to generate financial reports. The workflow starts by loading predefined category URLs from configuration, which serve as the entry points for supplier product extraction. These URLs are processed in batches to manage memory usage and system stability, with the batch size controlled by the supplier_extraction_batch_size parameter in system_config.json. For each category URL, the ConfigurableSupplierScraper extracts product data including title, price, EAN, SKU, and availability, storing this information in a supplier product cache.

After supplier product extraction, the workflow filters products based on the configured price range (MIN_PRICE to MAX_PRICE) and slices the product list to start processing from the last_processed_index provided by the EnhancedStateManager. This enables the workflow to resume interrupted processing without reprocessing already-analyzed products. For each supplier product, the workflow retrieves corresponding Amazon data using a dual-pronged matching strategy: first attempting an EAN-based search, and if that fails, falling back to a title-based search with similarity scoring to ensure rational matches.

The retrieved Amazon data is cached to disk, and a linking map entry is created to permanently associate the supplier product with the matched Amazon ASIN. This linking map serves as a persistent record of product matches, enabling efficient lookups during financial analysis and preventing redundant Amazon searches. The FBA_Financial_calculator then processes the combined supplier and Amazon data to calculate key financial metrics including ROI, net profit, referral fees, FBA fees, and VAT implications. Products that meet the defined profitability criteria (MIN_ROI_PERCENT and MIN_PROFIT_PER_UNIT) are added to the profitable results list, while all processed products contribute to the comprehensive financial report.

```mermaid
flowchart LR
A[Category URLs] --> B[ConfigurableSupplierScraper]
B --> C[Supplier Product Cache]
C --> D[Price Range Filtering]
D --> E[Resume Point Identification]
E --> F[Main Processing Loop]
F --> G[FixedAmazonExtractor]
G --> H[Amazon Data Cache]
H --> I[Linking Map]
I --> J[FBA_Financial_calculator]
J --> K[Financial Report]
J --> L[Profitable Products Report]
M[EnhancedStateManager] --> |State Management| F
M --> |State Management| K
M --> |State Management| L
```

**Diagram sources **
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L1-L590)

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L1-L590)

## Resilience and State Management
The PassiveExtractionWorkflow incorporates several resilience features to ensure reliable operation in the face of interruptions, authentication failures, and system constraints. The most critical resilience feature is the stateful resume capability provided by the EnhancedStateManager, which meticulously tracks processing progress and allows the workflow to be stopped and resumed without losing work. This is particularly important for long-running scraping tasks that may need to be interrupted for maintenance or due to external factors.

The EnhancedStateManager implements a sophisticated state management system that separates resumption tracking from progress tracking, preventing the common issue of processing state corruption. It maintains multiple indices including resumption_index (where to resume after interruption), progress_index (current progress in the active session), and session_products_processed (products processed in the current session). The state manager performs startup analysis to detect reverse gaps (when the linking map contains more entries than the product cache) and adjusts the resumption point accordingly. It also supports real-time updates to category totals when the scraper discovers more products than initially expected, ensuring accurate progress tracking.

In addition to state management, the workflow incorporates integrated authentication retry capabilities. During supplier product extraction, the ConfigurableSupplierScraper proactively checks authentication status every 25 products and triggers re-authentication if necessary. This prevents the common issue of session timeouts during long scraping sessions. The workflow also implements atomic data persistence, using an atomic write pattern (write to a temporary file, then rename) to ensure data integrity in the event of system crashes. Critical state files, including the linking map and processing state, are saved periodically in configurable batches during the main processing loop, balancing data safety with performance.

```mermaid
stateDiagram-v2
[*] --> Initialization
Initialization --> StateLoading : Load state file
StateLoading --> StartupAnalysis : Perform startup analysis
StartupAnalysis --> CategoryLoading : Load predefined categories
CategoryLoading --> BatchedExtraction : Extract supplier products in batches
BatchedExtraction --> ProductFiltering : Filter by price range
ProductFiltering --> ResumePoint : Identify resume point
ResumePoint --> ProcessingLoop : Enter main processing loop
ProcessingLoop --> AmazonDataRetrieval : Retrieve Amazon data
AmazonDataRetrieval --> MatchValidation : Validate product match
MatchValidation --> FinancialCalculation : Calculate financials
FinancialCalculation --> ProfitabilityCheck : Check profitability criteria
ProfitabilityCheck --> |Meets criteria| AddToResults : Add to profitable results
ProfitabilityCheck --> |Does not meet| SkipProduct : Skip product
AddToResults --> UpdateState : Update processing state
SkipProduct --> UpdateState
UpdateState --> PeriodicSave : Check periodic save condition
PeriodicSave --> |Save required| SaveState : Save state atomically
PeriodicSave --> |No save| CheckCycle : Check cycle completion
SaveState --> CheckCycle
CheckCycle --> |Cycle complete| Finalize : Finalize processing
CheckCycle --> |More products| ProcessingLoop
Finalize --> GenerateReports : Generate financial and results reports
GenerateReports --> [*] : End
ProcessingLoop --> AuthenticationCheck : Proactive authentication check
AuthenticationCheck --> |Authenticated| ProcessingLoop
AuthenticationCheck --> |Not authenticated| Reauthentication : Attempt re-authentication
Reauthentication --> |Success| ProcessingLoop
Reauthentication --> |Failure| ErrorHandling : Handle authentication failure
ErrorHandling --> |Retry| Reauthentication
ErrorHandling --> |Abort| Finalize
```

**Diagram sources **
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)

## Integration Points
The PassiveExtractionWorkflow integrates with several key components to achieve its product sourcing objectives. The primary integration points include the ConfigurableSupplierScraper for supplier data extraction, the FixedAmazonExtractor for Amazon data retrieval, the EnhancedStateManager for state management, and the FBA_Financial_calculator for financial analysis. These components are tightly integrated through well-defined interfaces that enable seamless data flow and coordination.

The integration with the ConfigurableSupplierScraper is established during workflow initialization, where the scraper is instantiated with the same AI client and configuration as the workflow. The scraper uses Playwright for robust browser automation with anti-bot evasion and JavaScript support, maintaining backward compatibility with the orchestrator while using an improved Playwright-based approach. The scraper is configured with externalized selector configuration loaded from supplier-specific JSON files, allowing it to adapt to different supplier website structures. During product extraction, the scraper can invoke an authentication callback to evaluate pricing and trigger re-authentication if necessary, creating a feedback loop between data extraction and authentication management.

The integration with the FixedAmazonExtractor enables the workflow to retrieve Amazon product data using a dual-pronged matching strategy. The extractor extends the base AmazonExtractor class, adding EAN search capabilities and enhanced title similarity scoring. It reuses browser pages and avoids unnecessary page creation/closure to maintain extension stability, connecting to the browser through the centralized BrowserManager singleton. This integration ensures that Amazon searches are performed efficiently and reliably, with the extractor handling the complexities of Amazon's dynamic content and anti-bot measures.

State management is handled through integration with the EnhancedStateManager, which provides thread-safe, atomic operations for state persistence. The state manager separates resumption tracking from progress tracking, preventing state corruption and enabling reliable interruption and resumption of processing. It maintains a comprehensive state structure that includes processing progress, category performance metrics, error logs, and user-facing metrics. The workflow updates the state manager throughout processing, with periodic atomic saves ensuring data integrity.

Financial analysis is performed through integration with the FBA_Financial_calculator, which processes the combined supplier and Amazon data to calculate key financial metrics. The calculator uses a linking map to associate supplier products with Amazon ASINs, enabling efficient lookups and preventing redundant Amazon searches. It calculates ROI, net profit, referral fees, FBA fees, and VAT implications based on configurable parameters loaded from system_config.json. The calculator generates comprehensive financial reports in CSV format, sorted by ROI to highlight the most profitable opportunities.

**Section sources**
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L1-L590)
- [system_config_loader.py](file://config/system_config_loader.py#L1-L84)

## Sequence Diagrams
The following sequence diagrams illustrate the main processing loop and error recovery scenarios for the PassiveExtractionWorkflow, highlighting the interactions between key components and the flow of data and control.

### Main Processing Loop
```mermaid
sequenceDiagram
participant Workflow as PassiveExtractionWorkflow
participant StateManager as EnhancedStateManager
participant Scraper as ConfigurableSupplierScraper
participant Extractor as FixedAmazonExtractor
participant Calculator as FBA_Financial_calculator
participant Cache as Amazon Cache
Workflow->>StateManager : load_state()
StateManager-->>Workflow : state data
Workflow->>StateManager : perform_startup_analysis()
Workflow->>Workflow : load_predefined_categories()
Workflow->>Scraper : scrape_products_from_url()
Scraper->>Scraper : fetch_html()
Scraper->>Scraper : extract_product_data()
Scraper-->>Workflow : product list
Workflow->>Workflow : filter_by_price_range()
Workflow->>Workflow : slice_from_resumption_index()
loop For each product
Workflow->>Extractor : _get_amazon_data(product)
Extractor->>Extractor : search_by_ean_and_extract_data()
alt EAN search successful
Extractor-->>Workflow : Amazon data
else EAN search failed
Extractor->>Extractor : search_by_title_using_search_bar()
Extractor->>Extractor : _overlap_score()
Extractor-->>Workflow : Amazon data
end
Workflow->>Workflow : _validate_product_match()
Workflow->>Calculator : run_calculations()
Calculator->>Calculator : find_amazon_json_by_linking_map()
alt Match found
Calculator->>Calculator : financials()
Calculator-->>Workflow : financial data
Workflow->>Workflow : check_profitability_criteria()
alt Meets criteria
Workflow->>Workflow : add_to_profitable_results()
end
end
Workflow->>StateManager : update_processing_progress()
Workflow->>StateManager : save_state_periodically()
end
Workflow->>Calculator : generate_financial_report()
Workflow->>Workflow : generate_profitable_products_report()
```

**Diagram sources **
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L1970-L2316)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)
- [FBA_Financial_calculator.py](file://tools/FBA_Financial_calculator.py#L1-L590)

### Error Recovery Scenario
```mermaid
sequenceDiagram
participant Workflow as PassiveExtractionWorkflow
participant StateManager as EnhancedStateManager
participant Scraper as ConfigurableSupplierScraper
participant BrowserManager as BrowserManager
participant AuthService as SupplierAuthenticationService
Workflow->>Scraper : scrape_products_from_url()
Scraper->>Scraper : get_page_content()
Scraper->>BrowserManager : get_page()
BrowserManager-->>Scraper : Page
Scraper->>Scraper : navigate_to_url()
alt Authentication failure detected
Scraper->>Workflow : auth_callback(price, product_index)
Workflow->>Workflow : detect_authentication_failure()
Workflow->>AuthService : ensure_authenticated_session()
AuthService->>AuthService : login_to_supplier()
AuthService->>AuthService : verify_login()
AuthService-->>Workflow : authentication_result
alt Authentication successful
Workflow->>Scraper : retry_current_product()
Scraper->>Scraper : get_page_content()
else Authentication failed
Workflow->>Workflow : log_error()
Workflow->>StateManager : save_state_atomic()
Workflow->>Workflow : abort_processing()
end
end
alt System interruption
Workflow->>StateManager : save_state_atomic()
StateManager-->>Workflow : save_confirmation
Workflow->>Workflow : graceful_shutdown()
end
```

**Diagram sources **
- [passive_extraction_workflow_latest.py](file://tools/passive_extraction_workflow_latest.py#L851-L2650)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L1-L3938)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py#L1-L2412)
- [tools/supplier_authentication_service.py](file://tools/supplier_authentication_service.py)

## Conclusion
The PassiveExtractionWorkflow class serves as a sophisticated orchestrator for the Amazon FBA agent system, integrating multiple specialized components to create a robust product sourcing pipeline. Its architecture emphasizes resilience, statefulness, and configurability, enabling it to handle complex e-commerce websites and long-running scraping tasks. The workflow's key strengths include its stateful resume capability, which allows processing to be interrupted and resumed without data loss; its integrated authentication retry mechanism, which handles session timeouts proactively; and its atomic data persistence, which ensures data integrity in the event of system failures.

The workflow's modular design, with clear separation between data extraction, matching, analysis, and state management components, enables maintainability and extensibility. By centralizing configuration in system_config.json, the workflow provides a single source of truth for operational parameters, making it easy to adjust processing behavior without code changes. The implementation of batched supplier product extraction helps manage memory usage and system stability, particularly important when processing suppliers with extensive product catalogs.

Future enhancements could include expanding the AI-powered category selection capabilities that are currently bypassed in the deterministic mode, implementing more sophisticated product matching algorithms, and adding support for additional e-commerce platforms beyond Amazon. The workflow's architecture provides a solid foundation for these and other enhancements, positioning it as a powerful tool for identifying profitable products in the competitive Amazon FBA marketplace.