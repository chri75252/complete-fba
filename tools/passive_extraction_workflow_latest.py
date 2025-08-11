"""
passive_extraction_workflow_latest.py - Architectural Summary & Script Index
================================================================================
**High-Level Summary:**
This script is the central engine for a multi-stage workflow that identifies profitable products for Amazon FBA. When executed by a targeted runner like `run_custom_poundwholesale.py`, it operates in a deterministic mode, using a predefined list of category URLs to ensure reliable and repeatable scraping runs. The system is architected for resilience and statefulness, allowing it to resume interrupted sessions and handle supplier authentication, making it ideal for the thorough analysis of complex e-commerc
e websites.
**Key Features & Concepts:**
- **Centralized Configuration:** The workflow is now exclusively controlled by `system_config.json`. The launcher script (`run_custom_poundwholesale.py`) is a simple trigger, and the `PassiveExtractionWorkflow` class itself is responsible for loading and respecting all operational toggles, ensuring a single source of truth.
- **Batched Supplier Scraping:** The system processes supplier categories in configurable chunks (defined by `supplier_extraction_batch_size`). This provides critical memory management and stability, preventing the system from being overwhelmed when scraping suppliers with many categories.
- **Stateful Resume Capability:** The workflow's progress is meticulously tracked using an `EnhancedStateManager`. This component saves the index of the last processed product, allowing the script to be stopped and resumed without losing work—a critical feature for long-running, interruptible scraping tasks.
- **Integrated Authentication & Retry:** The workflow is designed to handle supplier logins. It can detect authentication failures during a run, trigger a re-login attempt via the `SupplierAuthenticationService`, and retry the workflow, making it resilient to session timeouts.
- **Robust Dual-Pronged Product Matching:** The system employs a powerful two-step process to find products on Amazon. It first attempts a high-confidence match using the product's EAN. If that fails, it falls back to a title-based search that uses an advanced similarity scoring algorithm to ensure the match is rational.
- **Comprehensive Financial Analysis:** After a match is validated, the script invokes the `FBA_Financial_calculator` to determine ROI, net profit, and other key financial metrics, ensuring only genuinely profitable products are flagged.
- **Atomic & Batched Data Persistence:** To ensure data integrity against crashes, critical state files (like the linking map and processing state) are saved using an atomic write pattern (write to a temp file, then rename). These saves occur periodically in configurable batches during the main processing loop.
**--(Latent AI Capabilities - Bypassed in this Workflow)--**
*   **(Inactive) AI-Powered Category Selection:** The codebase contains sophisticated logic (`_get_ai_suggested_categories_enhanced`) to use an OpenAI client to intelligently select categories. This is bypassed when using a predefined category list.
*   **(Inactive) Hierarchical Category Processing:** The script has the capability (`_hierarchical_category_selection`) to explore a supplier's site by prioritizing FBA-friendly categories first, then moving to other phases. This is not used in the custom Pound Wholesale run.
**Core Workflow Logic (as executed by `run_custom_poundwholesale.py`):**
1.  **Initialization and Configuration Loading:** The workflow starts, initializing the `EnhancedStateManager`. Its first action is to load `system_config.json` to set all operational parameters (`max_products`, `max_products_per_category`, batch sizes, etc.).
2.  **Predefined Category Loading:** The `use_predefined_categories=True` flag is detected. The workflow bypasses all AI logic and instead calls `_get_predefined_categories` to load a hard-coded list of URLs from a specific config file.
3.  **Batched Supplier Product Scraping & Caching:** Using the predefined category list, `_extract_supplier_products` is called. This method now processes the category URLs in batches (controlled by `supplier_extraction_batch_size`), scraping the products from each batch sequentially before moving to the next.
4.  **Product Filtering and Resume Point Identification:** After all scraping is complete, the collected products are filtered by the configured price range. The script then slices the product list to start processing from the `last_processed_index` provided by the state manager.
5.  **Main Processing Loop (Cycled Analysis):** The script enters its main analysis loop, iterating through the products in configurable cycles (`max_products_per_cycle`).
6.  **Amazon Data Retrieval:** For each supplier product, `_get_amazon_data` is called. This method orchestrates the search on Amazon, executing the EAN-first, title-fallback strategy.
7.  **Data Caching & Linking:** The retrieved Amazon data is cached to disk. A "linking map" entry is created in memory to permanently associate the supplier product with the matched Amazon ASIN.
8.  **Financial Calculation:** The `FBA_Financial_calculator` is run on the combined supplier and Amazon data.
9.  **Profitability Check & State Update:** If the product meets the defined ROI and profit criteria, it's added to a list of profitable results. The product's URL is then marked as processed in the state manager to prevent re-analysis.
10. **Periodic Saves:** At configurable intervals (e.g., every 4 products, per `linking_map_batch_size`), the entire state (including the linking map and processing index) is saved to disk using an atomic write pattern.
11. **Finalization & Dual Reporting:** Once the loop completes, a final save is performed. Two reports are generated: a simple JSON list of profitable products from the current session, and a comprehensive CSV financial report for all cached products for the supplier.
**Class & Function Directory (with Line Numbers):**
- `FixedAmazonExtractor` (Lines: 435-830): A specialized class that extends the base `AmazonExtractor`. It is responsible for all interactions with Amazon.co.uk, including searching and data extraction.
  - `search_by_ean_and_extract_data()` (Lines: 625-795): The primary, high-confidence search method. It searches by EAN, filters out sponsored ads, and uses title similarity scoring to select the best match.
  - `extract_data()` (Lines: 824-848): The main data extraction method for a given ASIN. It reuses existing browser pages to ensure Chrome extensions function correctly.
- `PassiveExtractionWorkflow` (Lines: 851-2650): The main orchestrator class for the entire product sourcing workflow.
  - `__init__()` (Lines: 860-989): Initializes the system, loading configurations, setting up paths, and instantiating the scraper and extractor clients.
  - `run()` (Lines: 1970-2316): The main execution entry point. **It now loads all operational parameters directly from `self.system_config`**, orchestrating the entire process from state loading to final report generation.
  - `_extract_supplier_products()` (Lines: 2318-2435): Manages scraping product data from a list of category URLs. **This method now processes categories in batches controlled by `supplier_extraction_batch_size`**.
  - `_get_amazon_data()` (Lines: 2437-2525): Implements the EAN-first, title-fallback logic for finding a supplier product on Amazon and performs the critical title similarity validation.
  - `_validate_product_match()` (Lines: 2548-2563): A helper method that calculates a confidence score for a potential match based on title similarity.
- **--(Inactive Methods in this Workflow)--**
  - `_get_ai_suggested_categories_enhanced()` (Lines: 1412-1633): **(Bypassed)** The core AI interaction method.
  - `_hierarchical_category_selection()` (Lines: 1809-1968): **(Bypassed)** Manages the high-level strategy for choosing categories.
- `main()` (Lines: 2634-2647): A generic command-line entry point. **(Note: The `run_custom_poundwholesale.py` script serves as the actual, simplified entry point for this specific workflow).**
**Architect's Note:**
The system's architecture is now properly decoupled. The `PassiveExtractionWorkflow` is a self-contained engine driven by its configuration file. The "runner" script (`run_custom_poundwholesale.py`) acts as a simple, clean trigger, which is a much more robust and maintainable design.
"""
import os, logging
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = (
        "sk-s2-Q4jjFLfsmK1su4XzrXFdsYbTsZH4SWSES8efNDBT3BlbkFJGYMdHui-NLIdqGTgob3syatBmf40zqu9v8VPG6adUA"
    )
    logging.warning("OPENAI_API_KEY not supplied – using hard-coded fallback")
import os
import asyncio
import logging
import json
import sys
import argparse
import glob  # Added for fast Amazon cache search optimization
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from collections import defaultdict
import re
import time
import xml.etree.ElementTree as ET
import requests
from urllib.parse import urlparse, parse_qs, urljoin, parse_qsl, urlencode, urlunparse
from url_filter import filter_urls
