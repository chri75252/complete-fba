"""
passive_extraction_workflow_latest.py - Architectural Summary & Script Index
================================================================================

**High-Level Summary:**
This script is the central engine for a multi-stage workflow that identifies profitable products for Amazon FBA. When executed by a targeted runner like `run_custom_poundwholesale.py`, it operates in a deterministic mode, using a predefined list of category URLs to ensure reliable and repeatable scraping runs. The system is architected for resilience and statefulness, allowing it to resume interrupted sessions and handle supplier authentication, making it ideal for the thorough analysis of complex e-commerce websites.

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
    logging.warning("OPENAI_API_KEY not set – AI features disabled")

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
import difflib # Added for enhanced title similarity
import shutil
from abc import ABC, abstractmethod

# Import Windows Save Guardian for atomic persistence
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.windows_save_guardian import WindowsSaveGuardian
from dataclasses import dataclass, field
from pathlib import Path # ADDED IMPORT
import aiohttp  # Added for async HTTP requests

# 🚨 SENTINEL MONITORING: Import sentinel monitoring system
from utils.sentinel_monitor import get_sentinel_monitor, SentinelMonitor
# 🚨 SENTINEL MONITORING: Import sentinel monitoring system
from utils.sentinel_monitor import get_sentinel_monitor, SentinelMonitor
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Assuming OpenAI client; ensure it's installed: pip install openai
from openai import OpenAI
# For enhanced HTML parsing
from bs4 import BeautifulSoup

# Import required custom modules
# FIXED: Change relative imports to absolute imports when running as standalone script
import sys
import os
# Add both tools directory and parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))

# 🚀 HASH OPTIMIZATION: Import hash lookup optimizer for O(1) performance
sys.path.append(os.path.join(current_dir, '..', 'utils'))
from hash_lookup_optimizer import HashLookupOptimizer, LegacyPerformanceComparator
from url_filter import filter_urls
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from amazon_playwright_extractor import AmazonExtractor # Base class for FixedAmazonExtractor
# MODIFIED: Use ConfigurableSupplierScraper
from configurable_supplier_scraper import ConfigurableSupplierScraper
# Zero-token triage module available but not activated by default
# from zero_token_triage_module import perform_zero_token_triage
# Import FBA Calculator for accurate fee calculations
from FBA_Financial_calculator import run_calculations, financials as calc_financials
from cache_manager import CacheManager
# Removed LinkingMapWriter - using internal linking map methods
# Import enhanced state manager
# The utils directory is at the parent level (project root), not in tools/
try:
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager as EnhancedStateManager
    from tools.category_completion_tracker import get_completion_metrics
except ImportError:
    from fixed_enhanced_state_manager import FixedEnhancedStateManager as EnhancedStateManager
    try:
        from category_completion_tracker import get_completion_metrics
    except ImportError:
        def get_completion_metrics(base_path=None):
            """Fallback if category tracker not available - load from config"""
            try:
                # 🚨 FIX 1: Load actual category count from config instead of returning 0
                from config.system_config_loader import SystemConfigLoader
                config_loader = SystemConfigLoader()
                config_data = config_loader.load_config()
                supplier_config = config_data.get("supplier_configs", {}).get("poundwholesale.co.uk", {})
                category_urls = supplier_config.get("category_urls", [])
                return {
                    "total_categories": len(category_urls), 
                    "category_completion_status": {}, 
                    "last_analyze_url": None
                }
            except Exception as e:
                # Ultimate fallback - but log the issue
                print(f"⚠️ WARNING: Cannot load category count from config: {e}")
                return {"total_categories": 0, "category_completion_status": {}, "last_analyze_url": None}

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from utils.browser_manager import BrowserManager
from utils.path_manager import path_manager, get_linking_map_path
from config.system_config_loader import SystemConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"fba_extraction_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
log = logging.getLogger(__name__)

# ──────────────────────── ①  Enhanced FBA Priority Patterns (Research-Based) ──────────────────────
FBA_FRIENDLY_PATTERNS = {
    "home_kitchen":      ["home","kitchen","dining","storage","decor","organization","household"],     # Priority #1
    "pet_supplies":      ["pet","dog","cat","animal","bird","aquarium","fish"],                  # Priority #2
    "beauty_care":       ["beauty","personal","skincare","grooming","cosmetic","health"],            # Priority #3
    "sports_outdoor":    ["sport","fitness","camping","outdoor","exercise","yoga","garden"],     # Priority #4
    "office_stationery": ["office","stationery","desk","paper","business","school"],           # Priority #5
    "diy_tools":         ["diy","tool","hardware","hand-tool","craft","workshop","repair"],           # Priority #6
    "baby_nursery":      ["baby","infant","nursery","toddler","child-safe","kids"],               # Priority #7
    "toys_games":        ["toy","game","puzzle","educational","learning","play"],              # Priority #8
    "automotive":        ["car","auto","vehicle","motorcycle","bike","cycling"],                # Priority #9
    "kids_books":        ["kids book","children book","coloring book","sticker book","activity book","playbook","educational book","picture book","story book"],  # Priority #10
    "clearance_value":   ["pound","poundline","50p","under","clearance","sale","discount","bargain","cheap","value","deal"],  # Priority #11 (Medium-Low)
    "crafts_hobbies":    ["craft","hobby","sewing","knitting","art","creative","scrapbook","drawing"],  # Priority #12 (Lower)
    "seasonal_items":    ["christmas","halloween","easter","valentine","seasonal","holiday","party"],  # Priority #13 (Lower)
    "miscellaneous":     ["misc","other","general","various","assorted","mixed"]                # Priority #14 (Lower)
}
FBA_AVOID_PATTERNS = {
    "dangerous_goods": ["battery","power","lithium","flammable","hazmat","explosive"],           # CRITICAL AVOID
    "electronics":     ["electronic","tech","computer","phone","gadget","digital","tv"],     # HIGH AVOID
    "clothing":        ["clothing","fashion","apparel","shoe","sock","wear","dress"],             # HIGH AVOID
    "medical":         ["medical","pharma","medicine","healthcare","therapeutic","prescription"],          # HIGH AVOID
    "food":            ["food","beverage","grocery","snack","drink","edible","alcohol"],               # HIGH AVOID
    "large_bulky":     ["appliance","sofa","mattress","wardrobe","furniture","heavy"],          # MEDIUM AVOID
    "high_value":      ["jewelry","jewellery","watch","precious","gold","diamond","expensive"],      # MEDIUM AVOID
    "adult_books":     ["novel","fiction","romance","thriller","biography","autobiography","textbook","academic book","adult book","paperback novel"]  # AVOID adult reading books
}

# Third category for when FBA friendly categories are exhausted
FBA_NEUTRAL_PATTERNS = {
    "collectibles":    ["collectible","vintage","antique","memorabilia"],
    "media_dvd_cd":    ["dvd","cd","music","movie","film","media"]  # Removed general "book" from here since it's now classified above
}

# ──────────────────────── BACKUP UTILITY FUNCTIONS ──────────────────────
def create_backup_with_experiment_number(file_path: str, experiment_number: int) -> str:
    """Create backup with .bakN suffix for experiment tracking"""
    if not os.path.exists(file_path):
        return None
    
    backup_path = f"{file_path}.bak{experiment_number}"
    shutil.copy2(file_path, backup_path)
    return backup_path

# DISABLED: backup_experiment_files and callers per P0 requirements
# def backup_experiment_files(experiment_number: int, output_root: str = "OUTPUTS") -> Dict[str, str]:
#     """Backup all files that need .bakN suffix (EXCEPT Amazon cache)"""
#     backup_results = {}
#     
#     # System config
#     config_path = "config/system_config.json"
#     if os.path.exists(config_path):
#         backup_results["system_config"] = create_backup_with_experiment_number(config_path, experiment_number)
#     
#     # Processing state
#     state_path = os.path.join(output_root, "CACHE/processing_states/poundwholesale_co_uk_processing_state.json")
#     if os.path.exists(state_path):
#         backup_results["processing_state"] = create_backup_with_experiment_number(state_path, experiment_number)
#     
#     # Linking map
#     linking_path = os.path.join(output_root, "FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json")
#     if os.path.exists(linking_path):
#         backup_results["linking_map"] = create_backup_with_experiment_number(linking_path, experiment_number)
#     
#     # Supplier product cache
#     supplier_cache_path = os.path.join(output_root, "cached_products/poundwholesale-co-uk_products_cache.json")
#     if os.path.exists(supplier_cache_path):
#         backup_results["supplier_cache"] = create_backup_with_experiment_number(supplier_cache_path, experiment_number)
#     
#     return backup_results

# ──────────────────────── ②  Add OpenAI client initialization (after imports) ────────────

# Battery filtering patterns - products containing these will be excluded
BATTERY_KEYWORDS = [
    "battery", "batteries", "lithium", "alkaline", "rechargeable", 
    "power cell", "coin cell", "button cell", "watch battery", 
    "hearing aid battery", "cordless phone battery", "9v battery",
    "aa battery", "aaa battery", "c battery", "d battery",
    "cr2032", "cr2025", "cr2016", "cr1220", "cr1632", "cr2354",
    "lr44", "lr41", "lr20", "lr14", "lr6", "lr03",
    "ag13", "ag10", "ag4", "ag3", "ag1", "sr626", "sr621",
    "18650", "26650", "14500", "16340", "10440",
    "4lr44", "23a", "27a", "n battery", "aaaa battery"
]

BATTERY_BRAND_CONTEXT = [
    "duracell", "energizer", "panasonic", "rayovac", "eveready",
    "maxell", "renata", "vinnic", "gp", "varta", "sony",
    "toshiba", "philips", "uniross", "extrastar", "infapower",
    "eunicell", "jcb battery", "tesco battery"
]

# Non-FBA friendly product filtering patterns - products containing these will be excluded
NON_FBA_FRIENDLY_KEYWORDS = [
    # Smoking/Drug-related products
    "smoking pipe", "glass pipe", "water pipe", "tobacco pipe", "hookah", "shisha",
    "bong", "vaporizer", "vape", "e-cigarette", "cigarette", "cigar", "rolling paper",
    "grinder", "herb grinder", "smoking accessories", "pipe cleaner", "pipe screen",
    
    # Weapons and dangerous items
    "knife", "blade", "sword", "dagger", "machete", "tactical", "self defense",
    "pepper spray", "stun gun", "taser", "brass knuckles", "nunchucks",
    
    # Adult/inappropriate content
    "adult toy", "sex toy", "erotic", "pornographic", "xxx", "adult entertainment",
    
    # Hazardous materials
    "flammable", "explosive", "toxic", "corrosive", "radioactive", "biohazard",
    "chemical", "pesticide", "insecticide", "poison", "acid",
    
    # Restricted electronics
    "laser pointer", "high power laser", "jamming device", "signal jammer",
    "surveillance", "spy camera", "hidden camera", "wiretap",
    
    # Medical devices (restricted)
    "prescription", "medical device", "surgical", "diagnostic", "therapeutic device",
    "hearing aid", "pacemaker", "insulin pump", "blood glucose",
    
    # Counterfeit indicators
    "replica", "fake", "knockoff", "copy", "imitation", "unauthorized",
    
    # Alcohol and controlled substances
    "alcohol", "wine", "beer", "spirits", "liquor", "alcoholic",
    
    # Live animals and perishables
    "live animal", "pet", "fish", "bird", "reptile", "fresh food", "perishable"
]

NON_FBA_FRIENDLY_BRAND_CONTEXT = [
    # Smoking brands
    "zippo", "clipper", "bic lighter", "dunhill", "peterson pipe", "savinelli",
    "chacom", "stanwell", "missouri meerschaum", "raw papers", "zig zag",
    
    # Weapon brands
    "gerber", "benchmade", "spyderco", "cold steel", "ka-bar", "smith wesson",
    
    # Vaping brands
    "juul", "pax", "volcano", "storz bickel", "davinci", "arizer"
]

# Price criteria for supplier products
MIN_PRICE = float(os.getenv("MIN_PRICE", "0.1"))
MAX_PRICE = float(os.getenv("MAX_PRICE", "20.0"))

# Profitability and Amazon listing criteria
MIN_ROI_PERCENT = float(os.getenv("MIN_ROI_PERCENT", "35.0"))
MIN_PROFIT_PER_UNIT = float(os.getenv("MIN_PROFIT_PER_UNIT", "3.0")) # Added explicit min profit
MIN_RATING = float(os.getenv("MIN_RATING", "4.0"))
MIN_REVIEWS = int(os.getenv("MIN_REVIEWS", "50"))
MAX_SALES_RANK = int(os.getenv("MAX_SALES_RANK", "150000"))

DEFAULT_SUPPLIER_URL = os.getenv("DEFAULT_SUPPLIER_URL", None)
DEFAULT_SUPPLIER_NAME = os.getenv("DEFAULT_SUPPLIER", None)

EXTENSION_DATA_WAIT = int(os.getenv("EXTENSION_DATA_WAIT", "25"))
DEFAULT_NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))
POST_NAVIGATION_STABILIZE_WAIT = int(os.getenv("STABILIZE_WAIT", "10"))

import json

# Initial constants and paths
# Get the base directory path dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "OUTPUTS", "FBA_ANALYSIS"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load cache directories from config/system_config.json
def _load_cache_directories():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "system_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        cache_dirs = config.get("cache", {}).get("directories", {})
        return cache_dirs
    except Exception as e:
        logging.warning(f"Failed to load cache directories from config: {e}")
        return {}

cache_directories = _load_cache_directories()

# Global constant for persistent linking map in dedicated directory
LINKING_MAP_DIR = os.path.join(OUTPUT_DIR, "linking_maps")
os.makedirs(LINKING_MAP_DIR, exist_ok=True)
LINKING_MAP_PATH = os.path.join(LINKING_MAP_DIR, "linking_map.json")

# Other directories
SUPPLIER_CACHE_DIR = os.path.join(BASE_DIR, "OUTPUTS", "cached_products")
AMAZON_CACHE_DIR = os.path.join(OUTPUT_DIR, "amazon_cache")
AI_CATEGORY_CACHE_DIR = os.path.join(OUTPUT_DIR, "ai_category_cache")

os.makedirs(SUPPLIER_CACHE_DIR, exist_ok=True)
os.makedirs(AMAZON_CACHE_DIR, exist_ok=True)
os.makedirs(AI_CATEGORY_CACHE_DIR, exist_ok=True)

# Load OpenAI configuration from system config
def _load_openai_config():
    """Load OpenAI configuration from system_config.json"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "system_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        openai_config = config.get("integrations", {}).get("openai", {})
        return {
            "api_key": openai_config.get("api_key", ""),
            "model": openai_config.get("model", "gpt-4o-mini"),
            "enabled": openai_config.get("enabled", False)
        }
    except Exception as e:
        log.warning(f"Failed to load OpenAI config from system_config.json: {e}")
        return {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "enabled": True
        }

# Load OpenAI configuration
_openai_config = _load_openai_config()

# Load API key and model from environment variables or config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or _openai_config.get("api_key", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_PRIMARY", "gpt-4o-mini-2024-07-18")
OPENAI_ENABLED = bool(OPENAI_API_KEY) and _openai_config.get("enabled", True)

if not OPENAI_API_KEY:
    log.error("🚨 OPENAI_API_KEY not found in environment variables or config!")
    log.error("Please set OPENAI_API_KEY environment variable or update config/system_config.json")
    sys.exit(1)
# REMOVED: SUPPLIER_CONFIGS dictionary, as this is now handled by ConfigurableSupplierScraper and supplier_config_loader.py

# Battery product detection constants
BATTERY_KEYWORDS = ("battery", "batteries", "cell", "cr20", "lr41", "lithium", "alkaline")

def is_battery_title(title: str) -> bool:
    """Check if a product title indicates it's a battery product."""
    if not title:
        return False
    return any(k in title.lower() for k in BATTERY_KEYWORDS)

class FixedAmazonExtractor(AmazonExtractor):
    """
    Extension of AmazonExtractor.
    Includes EAN search capabilities and attempts EAN extraction from product pages.
    It reuses browser pages and avoids unnecessary page creation/closure for extension stability.
    """

    def __init__(self, chrome_debug_port: int, ai_client: Optional[OpenAI] = None):
        super().__init__(chrome_debug_port, ai_client)
        # self.ai_client is already set by parent constructor if ai_client is passed.

    async def connect(self) -> Browser: # type: ignore
        """
        Connect to browser using the centralized BrowserManager singleton.
        All browser operations now go through the shared BrowserManager instance.
        """
        log.info(f"🔧 FixedAmazonExtractor connecting via BrowserManager singleton")
        try:
            # Use the browser manager singleton for centralized browser management
            browser_manager = BrowserManager.get_instance()
            
            # Ensure browser manager is properly launched
            if not hasattr(browser_manager, 'browser') or not browser_manager.browser:
                await browser_manager.launch_browser(cdp_port=self.chrome_debug_port)
            
            # Get the shared browser instance
            self.browser = browser_manager.browser
            log.info("✅ FixedAmazonExtractor connected via BrowserManager singleton")
            
            return self.browser
        except Exception as e:
            log.error(f"❌ FixedAmazonExtractor failed to connect via BrowserManager: {e}")
            log.error("Ensure Chrome is running with --remote-debugging-port=9222 and BrowserManager is properly initialized")
            raise

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))

    async def search_by_title_using_search_bar(self, title: str, page: Optional[Page] = None) -> Dict[str, Any]:
        """Search Amazon by title using search bar interaction (not URL building)"""
        if not self.browser or not self.browser.is_connected():
            await self.connect()

        log.info(f"Searching Amazon by title using search bar: '{title}'")
        
        # Get page from parameter or use BrowserManager
        if page is None:
            from utils.browser_manager import get_page_for_url
            log.info("No page provided to search_by_title, getting one from BrowserManager.")
            page = await get_page_for_url("https://www.amazon.co.uk", reuse_existing=True)
        
        try:
            # Navigate to Amazon UK and search by typing title into search bar
            log.info(f"Navigating to Amazon UK to search for title: {title}")
            await page.goto("https://www.amazon.co.uk", timeout=60000)
            
            # Type title into search box and press Enter
            await page.fill("input#twotabsearchtextbox", title, timeout=5000)
            await page.press("input#twotabsearchtextbox", "Enter")
            
            # Wait for search results
            await page.wait_for_selector("div.s-search-results", timeout=15000)
            
            # Parse search results - extract first few results with improved element selection
            potential_asins_info = []
            
            # Try multiple selectors for search result elements
            search_result_elements = []
            search_selectors = [
                "div.s-search-results > div[data-asin]",
                "div[data-component-type='s-search-result']",
                "div[data-asin]:not([data-asin=''])",
                "[cel_widget_id*='MAIN-SEARCH_RESULTS'] div[data-asin]"
            ]
            
            for selector in search_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        search_result_elements = elements
                        log.info(f"Title search found {len(elements)} elements using selector: {selector}")
                        break
                except Exception as e:
                    log.debug(f"Title search selector '{selector}' failed: {e}")
                    continue
            
            for element in search_result_elements[:10]:  # More results for title search
                asin = await element.get_attribute("data-asin")
                # FIX: Remove overly restrictive 10-character requirement for ASIN validation
                # ASINs can be valid with fewer than 10 characters
                if asin and len(asin) >= 8 and len(asin) <= 12:  # More reasonable range for ASIN validation
                    # Use improved title extraction
                    result_title = await self._extract_title_from_element(element, asin)
                    
                    potential_asins_info.append({
                        "asin": asin,
                        "title": result_title
                    })
            
            # Create search_results_data in expected format
            if potential_asins_info:
                search_results_data = {
                    "results": potential_asins_info,
                    "search_method": "title_search_bar_interaction"
                }
                log.info(f"Title search found {len(potential_asins_info)} results for '{title}'")
            else:
                search_results_data = {"error": f"No valid ASINs found for title '{title}'"}
                log.warning(f"No valid ASINs found for title '{title}'")
                
        except Exception as search_error:
            log.error(f"Error during title search for '{title}': {search_error}")
            search_results_data = {"error": f"Search error for title '{title}': {str(search_error)}"}
            
        return search_results_data

    async def _extract_title_from_element(self, element, asin: str) -> str:
        """Extract title from search result element using multiple fallback selectors"""
        title_selectors = [
            "h2 a span.a-text-normal",
            "h2 a span",
            ".s-title-instructions-style span.a-text-normal",
            "span.a-size-medium.a-color-base.a-text-normal",
            "h2 span.a-size-base-plus",
            "h2 a",
            "h2",
            "[data-cy='title-recipe-title']",
            ".s-line-clamp-2 span",
            ".s-line-clamp-3 span",
            ".s-line-clamp-4 span",
            ".s-size-mini .s-link-style a span",
            ".s-size-mini .s-link-style span",
            "span[data-a-text-type='title']",
            "a.a-link-normal > span.a-text-normal",
            "a span[aria-label]",
            "a[href*='/dp/'] span",
            ".a-link-normal span"
        ]
        
        for selector in title_selectors:
            try:
                title_element = await element.query_selector(selector)
                if title_element:
                    title_text = await title_element.inner_text()
                    if title_text and title_text.strip() and title_text.strip() != "":
                        log.debug(f"ASIN {asin} title extracted using selector '{selector}': {title_text.strip()[:50]}...")
                        return title_text.strip()
            except Exception as e:
                log.debug(f"Selector '{selector}' failed for ASIN {asin}: {e}")
                continue
        
        # Fallback level 1: Try any element with "title" in class or data attributes
        try:
            title_containing_selectors = [
                "[class*='title']",
                "[data-cy*='title']",
                "[data-a-target*='title']",
                ".a-size-base-plus",
                ".a-size-medium"
            ]
            
            for fallback_selector in title_containing_selectors:
                fallback_element = await element.query_selector(fallback_selector)
                if fallback_element:
                    fallback_text = await fallback_element.inner_text()
                    if fallback_text and fallback_text.strip():
                        log.debug(f"ASIN {asin} title extracted using fallback selector '{fallback_selector}': {fallback_text.strip()[:50]}...")
                        return fallback_text.strip()
        except Exception as e:
            log.debug(f"Fallback title extraction with selectors failed for ASIN {asin}: {e}")
        
        # Fallback level 2: Try to get any text content from h2 or other common title containers
        try:
            fallback_element = await element.query_selector("h2, .a-text-normal, .a-link-normal")
            if fallback_element:
                fallback_text = await fallback_element.inner_text()
                if fallback_text and fallback_text.strip():
                    log.debug(f"ASIN {asin} title extracted using last-resort fallback: {fallback_text.strip()[:50]}...")
                    return fallback_text.strip()
        except Exception as e:
            log.debug(f"Last-resort fallback title extraction failed for ASIN {asin}: {e}")
        
        log.warning(f"Could not extract title for ASIN {asin} using any selector")
        return "Unknown Title"

    async def search_by_ean_and_extract_data(self, ean: str, supplier_product_title: str, page: Optional[Page] = None) -> Dict[str, Any]:
        """
        Search Amazon by EAN and extract data for the best match.
        Uses AI for disambiguation if multiple results are found.
        Uses robust search result selection and sponsored ad detection.
        """
        if not self.browser or not self.browser.is_connected():
            await self.connect()

        log.info(f"Searching Amazon by EAN: {ean} for supplier product: '{supplier_product_title}' (FixedAmazonExtractor)")
        
        # Get page from parameter or use BrowserManager
        if page is None:
            from utils.browser_manager import get_page_for_url
            log.info("No page provided to search_by_ean, getting one from BrowserManager.")
            page = await get_page_for_url("https://www.amazon.co.uk", reuse_existing=True)
        
        try:
            # Navigate to Amazon UK and search by typing EAN into search bar
            log.info(f"Navigating to Amazon UK to search for EAN: {ean}")
            
            await page.goto("https://www.amazon.co.uk", timeout=60000)
            
            # Type EAN into search box and press Enter
            await page.fill("input#twotabsearchtextbox", ean, timeout=5000)
            await page.press("input#twotabsearchtextbox", "Enter")
            
            # Wait for search results with enhanced multiple selector approach - REQUIREMENT 1
            log.info(f"Waiting for search results page to load for EAN {ean}...")
            search_result_containers_found = False
            container_selectors = [
                "div.s-search-results", 
                "div[data-component-type='s-search-results']", 
                "[data-cy='search-result-list]",
                "div.s-result-list",
                "div.s-main-slot"
            ]
            
            # Wait for any of the container selectors with a longer timeout
            for container_selector in container_selectors:
                try:
                    await page.wait_for_selector(container_selector, timeout=20000)
                    log.info(f"Found search results container with selector: {container_selector}")
                    search_result_containers_found = True
                    break
                except Exception as container_error:
                    log.debug(f"Container selector '{container_selector}' not found: {container_error}")
            
            if not search_result_containers_found:
                # Check for a direct product page (Amazon sometimes redirects to product page for exact EAN match)
                try:
                    direct_product_selectors = ["div#dp-container", "div#ppd", "div#centerCol"]
                    for direct_selector in direct_product_selectors:
                        if await page.query_selector(direct_selector):
                            log.info(f"EAN search redirected to a direct product page (selector: {direct_selector})")
                            # Extract ASIN from URL
                            current_url = page.url
                            asin_match = re.search(r"/dp/([A-Z0-9]{10})", current_url)
                            if asin_match:
                                direct_asin = asin_match.group(1)
                                log.info(f"Found direct product match for EAN {ean}: ASIN {direct_asin}")
                                # Return the data directly
                                return await super().extract_data(direct_asin)
                            break
                except Exception as direct_page_error:
                    log.debug(f"Error checking for direct product page: {direct_page_error}")
                
                log.warning(f"No search results containers found for EAN {ean}")
                return {"error": f"No search results found for EAN {ean}"}
            
            # Add a brief stabilization wait to ensure all elements are loaded
            await asyncio.sleep(2)
                        
            # REQUIREMENT 2: Search Result Element (Tile) Selection with improved selectors 
            organic_results = []
            search_result_elements = []
            
            # Enhanced list of selectors for finding individual product tiles
            search_selectors = [
                # Try to exclude obvious ad containers at the selection stage
                "div[data-asin]:not([data-asin='']):not(.AdHolder):not([class*='s-widget-sponsored-product'])",
                "div.s-result-item[data-asin]:not([data-asin=''])",
                "div[data-component-type='s-search-result'][data-asin]:not([data-asin=''])",
                "div.s-search-results > div[data-asin]",
                "div[data-cel-widget*='search_result_'][data-asin]:not([data-asin=''])",
                "[cel_widget_id*='MAIN-SEARCH_RESULTS'] div[data-asin]",
                "div[data-uuid][data-asin]:not([data-asin=''])"
            ]
            
            for selector in search_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        search_result_elements = elements
                        log.info(f"Found {len(elements)} search result elements using selector: {selector}")
                        break
                except Exception as e:
                    log.debug(f"Search selector '{selector}' failed: {e}")
                    continue
            
            if not search_result_elements:
                log.warning(f"No search result elements found for EAN {ean}")
                return {"error": "no_elements_found"}
            else:
                log.info(f"Processing {len(search_result_elements)} search result elements for EAN {ean}")
                
                # Look at more elements (up to 15) to find organic results
                for i, element in enumerate(search_result_elements[:15]):
                    asin = await element.get_attribute("data-asin")
                    # FIX: Remove overly restrictive 10-character requirement for ASIN validation
                    # ASINs can be valid with fewer than 10 characters
                    if not asin or len(asin) < 8 or len(asin) > 12:  # More reasonable range for ASIN validation
                        log.debug(f"Element {i+1}: Invalid or missing ASIN: {asin}")
                        continue
                        
                    log.debug(f"Processing element {i+1}: ASIN {asin}")
                    
                    # --- REQUIREMENT 4: Enhanced sponsored detection logic (Iteration 3) ---
                    is_sponsored = False
                    sponsor_detection_reason = ""
                    
                    # Add debug logging for first few elements
                    if i < 3:
                        try:
                            element_html_debug = await element.evaluate("element => element.outerHTML")
                            log.debug(f"ASIN {asin} HTML structure sample: {element_html_debug[:600]}...")
                        except Exception as html_error:
                            log.debug(f"Could not get HTML for element debug: {html_error}")
                    
                    # Check 1: Explicit "Sponsored" text directly visible within the element
                    try:
                        sponsored_badge_locator = element.locator("span:visible", has_text=re.compile(r"^\\s*Sponsored\\s*$", re.IGNORECASE))
                        if await sponsored_badge_locator.count() > 0: 
                            is_sponsored = True
                            sponsor_detection_reason = "visible 'Sponsored' text badge"
                    except Exception as e_badge:
                        log.debug(f"Error checking sponsored badge for ASIN {asin}: {e_badge}")

                    # Check 2: Aria-label on the element or a significant child
                    if not is_sponsored:
                        try:
                            if await element.locator('[aria-label="Sponsored"]:visible').count() > 0:
                                is_sponsored = True
                                sponsor_detection_reason = "aria-label='Sponsored'"
                        except Exception as e_aria:
                            log.debug(f"Error checking aria-label for ASIN {asin}: {e_aria}")
                    
                    # Check 3: Data attributes on the element itself (tile)
                    if not is_sponsored:
                        try:
                            is_sponsored = await element.evaluate("""el => {
                                if (el.getAttribute('data-component-type') === 'sp-sponsored-result') return true;
                                if (el.getAttribute('data-ad-marker') === 'true') return true;
                                if (el.querySelector('[data-component-type="sp-sponsored-result"]')) return true;
                                if (el.querySelector('[data-cel-widget*="advertising"]')) return true;
                                if (el.querySelector('[data-ad-id]')) return true;
                                return false;
                            }""")
                            if is_sponsored:
                                sponsor_detection_reason = "data attributes indicating sponsored content"
                        except Exception as e_data_attr:
                            log.debug(f"Error checking data-attributes for ASIN {asin}: {e_data_attr}")

                    # Check 4: Presence of known ad-specific classes on the main element (tile)
                    if not is_sponsored:
                        try:
                            element_classes = await element.get_attribute("class") or ""
                            known_ad_classes = [
                                "AdHolder", 
                                "s-widget-sponsored-product", 
                                "sponsored-results-padding",
                                "s-result-item-sponsored-popup",
                                "puis-sponsored-container-component",
                                "ad-feedback"
                            ] 
                            for ad_class in known_ad_classes:
                                if ad_class in element_classes:
                                    is_sponsored = True
                                    sponsor_detection_reason = f"ad-specific class: '{ad_class}'"
                                    break
                        except Exception as e_class:
                            log.debug(f"Error checking tile classes for ASIN {asin}: {e_class}")

                    # Check 5: Text content contains typical ad indicators
                    if not is_sponsored:
                        try:
                            ad_indicators_locator = element.locator("text=/sponsored|advertisement|ad for/i")
                            if await ad_indicators_locator.count() > 0:
                                is_sponsored = True
                                sponsor_detection_reason = "text containing ad indicators"
                        except Exception as e_text:
                            log.debug(f"Error checking text for ad indicators for ASIN {asin}: {e_text}")

                    if is_sponsored:
                        log.info(f"Skipping sponsored result: ASIN {asin} (detected by {sponsor_detection_reason})")
                        continue
                    
                    # Process organic result with improved title extraction from helper method
                    title = await self._extract_title_from_element(element, asin)
                    
                    organic_results.append({
                        "asin": asin,
                        "title": title
                    })
                    log.info(f"Found organic result: ASIN {asin} - {title[:60]}...")
                    
                    # Break after finding a reasonable number of organic results to improve performance
                    if len(organic_results) >= 5:
                        log.info(f"Found {len(organic_results)} organic results, stopping search to improve performance.")
                        break
            
                # Check if we have any organic results
                if not organic_results:
                    log.warning(f"EAN {ean} returned no organic results - skipping")
                    search_results_data = {"error": "no_organic_results"}
                else:
                    # FIX 1: EAN search should use exact EAN matching, NOT title scoring
                    # When EAN search returns results, use the first organic result (highest relevance)
                    if len(organic_results) == 1:
                        chosen_result = organic_results[0]
                        log.info(f"Single organic result found for EAN {ean}: ASIN {chosen_result['asin']}")
                    else:
                        # Multiple EAN search results - use first organic result (most relevant by Amazon's ranking)
                        chosen_result = organic_results[0]
                        log.info(f"Multiple organic results ({len(organic_results)}) found for EAN {ean}. Using first organic result (most relevant): ASIN {chosen_result['asin']}")
                        log.info(f"FIXED: No title scoring on EAN search results - using Amazon's search relevance ranking")
                    
                    search_results_data = {
                        "results": [chosen_result],  # Single chosen result
                        "search_method": "ean_search_bar_with_verification"
                    }
                    log.info(f"EAN search selected ASIN {chosen_result['asin']} for {ean}")
                
        except Exception as search_error:
            log.error(f"Error during EAN search for {ean}: {search_error}")
            search_results_data = {"error": f"Search error for EAN {ean}: {str(search_error)}"}

        if "error" in search_results_data or not search_results_data.get("results"):
            log.warning(f"No Amazon results or error for EAN '{ean}'. Details: {search_results_data.get('error', 'No results list')}")
            # FIX 1: EAN search → title match fallback
            log.info(f"Falling back to title search for supplier product: '{supplier_product_title}'")
            title_search_results = await self.search_by_title_using_search_bar(supplier_product_title, page=page)
            if title_search_results and "error" not in title_search_results and title_search_results.get("results"):
                log.info(f"Title search successful for '{supplier_product_title}' after EAN '{ean}' failed")
                # FIXED: Extract complete data for title search result instead of returning search result only
                fallback_asin = title_search_results["results"][0].get("asin")
                if fallback_asin:
                    log.info(f"Extracting complete data for fallback ASIN {fallback_asin} from title search")
                    product_data = await super().extract_data(fallback_asin)
                    if product_data and "error" not in product_data:
                        # Set search method for linking map
                        product_data["_search_method_used"] = "title"
                    return product_data
                else:
                    return {"error": f"No ASIN found in title search result for EAN {ean}"}
            else:
                log.warning(f"Both EAN '{ean}' and title '{supplier_product_title}' searches failed")
                return {"error": f"No results for EAN {ean} or title search"}

        potential_asins_info = search_results_data["results"]
        chosen_asin_data = None

        if len(potential_asins_info) == 1:
            chosen_asin_data = potential_asins_info[0]
            log.info(f"Single ASIN {chosen_asin_data.get('asin')} found for EAN {ean}.")
        elif len(potential_asins_info) > 1:
            # FIX 1: EAN search → stop title scoring when search initiated by EAN
            # Trust Amazon's search relevance ranking for EAN searches
            chosen_asin_data = potential_asins_info[0]
            log.info(f"Multiple ASINs ({len(potential_asins_info)}) found for EAN {ean}. Using Amazon's first result: ASIN {chosen_asin_data.get('asin')}")
            log.info(f"FIXED: No title scoring on EAN search results - using Amazon's search relevance ranking")

            # EAN search complete - skip AI disambiguation to trust Amazon's ranking
            # AI disambiguation removed to prevent title scoring on EAN results
            if False:  # Disabled AI disambiguation for EAN searches
                log.info(f"AI disambiguation disabled for EAN {ean} - trusting Amazon's ranking")
                prompt = (
                    f"The EAN '{ean}' (from supplier product '{supplier_product_title}') "
                    f"returned multiple products on Amazon. Which of the following Amazon products is the most likely match to the supplier product title?\n"
                )
                for i, item in enumerate(potential_asins_info[:3]): # Limit to top 3 for AI prompt
                    prompt += f"{i+1}. ASIN: {item.get('asin')}, Title: {item.get('title')}\n"
                prompt += "Respond with the ASIN of the best match, or 'NONE' if no good match."
                
                try:
                    # Ensure ai_client is not None before calling create
                    if self.ai_client:
                        chat_completion = await asyncio.to_thread(
                            self.ai_client.chat.completions.create, # type: ignore
                            messages=[{"role": "user", "content": prompt}],
                            model=OPENAI_MODEL_NAME,
                        )
                        ai_response = chat_completion.choices[0].message.content.strip() # type: ignore
                        log.info(f"AI response for EAN {ean} disambiguation: {ai_response}")
                        
                        # Find the item that matches the AI's chosen ASIN
                        matched_item_by_ai = next((item for item in potential_asins_info if item.get('asin') == ai_response), None)
                        if matched_item_by_ai:
                            chosen_asin_data = matched_item_by_ai
                            log.info(f"AI selected ASIN {chosen_asin_data.get('asin')} for EAN {ean}.")
                        elif ai_response != "NONE":
                             log.warning(f"AI suggested ASIN {ai_response} not in search results. Using first result.")
                        else: # AI responded "NONE"
                            log.warning(f"AI could not confidently match EAN {ean}. Using first result.")
                    else:
                        log.warning("AI client not available for EAN disambiguation. Using first result.")
                except Exception as ai_err:
                    log.error(f"AI disambiguation failed for EAN {ean}: {ai_err}")
        
        if not chosen_asin_data or not chosen_asin_data.get("asin"):
            log.warning(f"No suitable ASIN found for EAN {ean} after search and disambiguation.")
            return {"error": f"No suitable ASIN for EAN {ean}"}

        chosen_asin = chosen_asin_data.get("asin")
        log.info(f"Proceeding with ASIN: {chosen_asin} for EAN: {ean}")
        
        # Extract detailed data for the chosen ASIN using the base class method
        product_data = await super().extract_data(chosen_asin) # type: ignore

        # 🚨 CRITICAL FIX: Explicitly record that this was an EAN search
        if "error" not in product_data:
            product_data["_search_method_used"] = "EAN"
            log.info(f"✅ Recorded search method 'EAN' for ASIN {chosen_asin}")
        else:
            log.warning(f"Failed to extract data for ASIN {chosen_asin}, cannot set search method")

        # The base AmazonExtractor's extract_data method should now attempt to get 'ean_on_page'.
        # No need for redundant EAN extraction here if the base class handles it.
        if "error" not in product_data and product_data.get("title"):
            log.info(f"Successfully extracted data for ASIN {chosen_asin} (EAN on page: {product_data.get('ean_on_page', 'N/A')})")

        return product_data


    async def extract_data(self, asin: str) -> Dict[str, Any]:
        """
        Extract data for an Amazon product by ASIN.
        This implementation reuses existing pages to ensure extensions work properly.
        The base class method is called, which should handle EAN extraction.
        """
        # This method primarily relies on the superclass's extract_data.
        # The FixedAmazonExtractor's role is more about specialized search (like by EAN)
        # and ensuring the correct browser context is used.
        if not self.browser or not self.browser.is_connected():
            await self.connect() # Ensure connection

        # Call the parent's extract_data method
        result = await super().extract_data(asin) # type: ignore

        # The base class's extract_data should now be responsible for finding 'ean_on_page'.
        # Any additional EAN logic specific to FixedAmazonExtractor could go here if needed,
        # but it's better if the base class is comprehensive.
        
        # The stabilization wait is also part of the base class's extract_data
        # log.info(f"Waiting {EXTENSION_DATA_WAIT}s for extensions to stabilize (FixedAmazonExtractor.extract_data)...")
        # await asyncio.sleep(EXTENSION_DATA_WAIT) # This is in the base class
        return result


class PassiveExtractionWorkflow:
    def __init__(self, config_loader: SystemConfigLoader, workflow_config: dict, browser_manager: BrowserManager):
        self.config_loader = config_loader
        self.workflow_config = workflow_config
        self.browser_manager = browser_manager
        self.log = logging.getLogger(self.__class__.__name__)
        
        # 🚨 IMPORT HYGIENE: Log module path to confirm correct workflow is running
        self.log.info(f"MODULE PATH: {__file__}")
        
        # Core components initialized here
        self.supplier_name = self.workflow_config.get('supplier_name')
        self.full_config = self.config_loader.get_full_config()
        self.system_config = self.full_config.get("system", {})
        
        # Check for test mode environment variables for audit testing
        self.test_mode = os.getenv('FBA_TEST_MODE', 'false').lower() == 'true'
        self.test_limit = int(os.getenv('FBA_TEST_LIMIT', '0'))
        self.audit_mode = os.getenv('FBA_AUDIT_MODE', 'false').lower() == 'true'
        
        if self.test_mode:
            self.log.info(f"TEST MODE: Processing limit set to {self.test_limit} products")
        if self.audit_mode:
            self.log.info(f"AUDIT MODE: Enhanced logging and validation enabled")
        
        # Initialize paths using centralized path management
        self.output_dir = self._initialize_output_directory()
        self.supplier_cache_dir = str(path_manager.get_output_path('cached_products'))
        self.amazon_cache_dir = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache'))
        
        # 🚨 CRITICAL FIX: Enhanced directory creation with error handling
        try:
            self.log.info(f"🔍 DEBUG: output_dir = '{self.output_dir}'")
            self.log.info(f"🔍 DEBUG: supplier_cache_dir = '{self.supplier_cache_dir}'")
            os.makedirs(self.supplier_cache_dir, exist_ok=True)
            self.log.info(f"✅ Created supplier cache directory: {self.supplier_cache_dir}")
            os.makedirs(self.amazon_cache_dir, exist_ok=True)
            self.log.info(f"✅ Created amazon cache directory: {self.amazon_cache_dir}")
        except Exception as e:
            self.log.error(f"🚨 CRITICAL: Failed to create cache directories: {e}")
            self.log.error(f"🚨 Output dir: {self.output_dir}")
            self.log.error(f"🚨 Supplier cache dir: {self.supplier_cache_dir}")
            raise
        self.state_manager = EnhancedStateManager(self.supplier_name)
        
        # 🚨 FIX 3: Initialize state manager with accurate totals BEFORE startup analysis
        try:
            # Get total cache and category counts for proper initialization
            cache_file, cache_count = self._find_actual_supplier_cache_file(self.supplier_name)
            
            # Load categories from config to get accurate total
            from config.system_config_loader import SystemConfigLoader
            config_loader = SystemConfigLoader()
            config_data = config_loader.load_config()
            supplier_config = config_data.get("supplier_configs", {}).get(self.supplier_name, {})
            category_urls = supplier_config.get("category_urls", [])
            
            # Update runtime settings with accurate counts
            if hasattr(self.state_manager, 'state_data'):
                runtime_settings = self.state_manager.state_data.setdefault('runtime_settings', {})
                runtime_settings['supplier_cache_count'] = cache_count
                runtime_settings['total_categories'] = len(category_urls)
                runtime_settings['max_products_to_process'] = cache_count  # Set reasonable default
                
                # Also update main state fields for consistency
                self.state_manager.state_data['total_products'] = cache_count
                
                self.log.info(f"✅ State manager initialized with accurate totals: {cache_count} products, {len(category_urls)} categories")
        except Exception as e:
            self.log.warning(f"⚠️ Could not initialize state manager with totals: {e}")
        
        # 🚨 SURGICAL FIX: Perform startup analysis to detect reverse gap scenario
        if hasattr(self.state_manager, 'perform_startup_analysis'):
            try:
                self.state_manager.perform_startup_analysis()
                self.log.info("✅ Startup analysis performed - gap processing detection initialized")
            except Exception as e:
                self.log.warning(f"⚠️ Startup analysis failed: {e}")
        else:
            # Fallback: manually update gap processing status
            if hasattr(self.state_manager, 'state_data'):
                gap_data = self.state_manager.state_data.setdefault('gap_processing', {})
                gap_data['startup_analysis_completed'] = True
                # Check linking map vs cache to set reverse gap detection
                linking_map_count = self.state_manager.state_data.get('runtime_settings', {}).get('linking_map_count', 0)
                supplier_cache_count = self.state_manager.state_data.get('runtime_settings', {}).get('supplier_cache_count', 0)
                if linking_map_count > supplier_cache_count:
                    gap_data['reverse_gap_detected'] = True
                    gap_data['phase'] = 'reverse_gap_fresh_categories'
                    self.log.info(f"🔄 REVERSE GAP DETECTED: Linking map ({linking_map_count}) > Cache ({supplier_cache_count})")
        
        # 🔧 CRITICAL FIX: Validate category count consistency across all sources
        if hasattr(self.state_manager, 'validate_category_count_consistency'):
            try:
                validation_result = self.state_manager.validate_category_count_consistency()
                if not validation_result.get('is_consistent', False):
                    self.log.warning(f"⚠️ Category count discrepancies found and corrected: {validation_result.get('corrected_values', [])}")
                    if validation_result.get('auto_corrected', False):
                        self.log.info("✅ Category count consistency restored automatically")
                else:
                    self.log.info(f"✅ Category count validation passed: {validation_result.get('authoritative_count', 0)} categories")
            except Exception as e:
                self.log.error(f"❌ Category count validation failed: {e}")
        
        # Pass the single browser_manager instance to the tools
        self.amazon_extractor = self._initialize_amazon_extractor()
        self.supplier_scraper = self._initialize_supplier_scraper()
        
        self.extractor = self.amazon_extractor
        
        self.web_scraper = self.supplier_scraper
        
        # Initialize linking map as an array of detailed objects (matching archived format)
        self.linking_map = []
        self.log.debug(f"🔍 DEBUG: linking_map initialized as type: {type(self.linking_map)}")
        
        # 🚀 HASH OPTIMIZATION: Initialize O(1) hash lookup system for 3,650x performance improvement
        self.hash_optimizer = HashLookupOptimizer(logger=self.log)
        self.performance_comparator = LegacyPerformanceComparator(logger=self.log)
        self.log.info("🚀 Hash-based lookup optimization system initialized")
        
        # 🚨 SENTINEL MONITORING: Initialize proactive monitoring system
        self.sentinel_monitor = get_sentinel_monitor(self.supplier_name)
        self.log.info("🚨 SENTINEL MONITORING: Proactive monitoring system initialized")
        
        # 🛡️ WINDOWS SAVE GUARDIAN: Initialize atomic persistence system
        self.save_guardian = WindowsSaveGuardian()
        self.log.info("🛡️ WINDOWS SAVE GUARDIAN: Atomic persistence system initialized")
        
        # self.performance_tracker = PerformanceTracker()  # Removed - not defined

        # Workflow state attributes
        self.consecutive_amazon_price_misses = 0
        self.products_for_fba_analysis = []
        self.last_processed_index = 0
        
        # 🔧 AUTHENTICATION FALLBACK TRACKING
        self.products_without_price_count = 0
        self.products_processed_since_auth = 0
        self.last_authentication_time = None
        self.auth_fallback_config = {
            "price_missing_threshold": 3,  # Trigger after 3 products without price
            "products_per_auth": 100,      # Re-auth every 100 products
            "hours_per_auth": 2            # Re-auth every 2 hours
        }
        
        self.results_summary = {
            "total_supplier_products": 0,
            "profitable_products": 0,
            "products_analyzed_ean": 0,
            "products_analyzed_title": 0,
            "errors": 0
        }

        self.log.info(f"✅ Output directory set to: {self.output_dir}")
        
        self._validate_initialization()

    def _add_linking_map_entry_optimized(self, entry: Dict[str, Any]) -> None:
        """
        Add entry to linking map with hash index optimization.
        
        🚀 HASH OPTIMIZATION: This method adds entries to both the linking_map list
        and the hash indexes for O(1) lookups, providing 3,650x performance improvement.
        
        Args:
            entry: Linking map entry to add
        """
        # Add to hash indexes first to detect duplicates
        is_new_entry = self.hash_optimizer.add_entry(entry)

        if is_new_entry:
            # Only append to main linking map if truly new
            self.linking_map.append(entry)
            self.log.debug(
                f"🚀 HASH OPTIMIZATION: Added entry to linking map and indexes - EAN: {entry.get('supplier_ean', 'N/A')}, URL: {entry.get('supplier_url', 'N/A')}"
            )
        else:
            self.log.debug(
                f"🔄 HASH OPTIMIZATION: Duplicate entry updated - EAN: {entry.get('supplier_ean', 'N/A')}, URL: {entry.get('supplier_url', 'N/A')}"
            )
        
        # Update performance metrics
        stats = self.hash_optimizer.get_index_stats()
        if stats['total_lookups'] > 0 and stats['total_lookups'] % 100 == 0:
            self.log.info(f"🚀 HASH PERFORMANCE: {stats['total_lookups']} lookups, {stats['cache_hit_rate']:.1f}% hit rate, {stats['performance_improvement']:.1f}x improvement")

    def log_hash_optimization_summary(self) -> None:
        """
        🚀 HASH OPTIMIZATION: Log comprehensive performance summary with timing metrics.
        
        This method provides detailed performance analysis showing the massive improvement
        from O(n) linear searches to O(1) hash lookups.
        """
        try:
            stats = self.hash_optimizer.get_index_stats()
            
            self.log.info("=" * 80)
            self.log.info("🚀 HASH LOOKUP OPTIMIZATION PERFORMANCE SUMMARY")
            self.log.info("=" * 80)
            
            # Index Statistics
            self.log.info(f"📊 INDEX STATISTICS:")
            self.log.info(f"   🔍 EAN Index Entries: {stats['ean_entries']:,}")
            self.log.info(f"   🔗 URL Index Entries: {stats['url_entries']:,}")
            self.log.info(f"   📦 ASIN Index Entries: {stats['asin_entries']:,}")
            self.log.info(f"   ✅ Index Valid: {stats['index_valid']}")
            self.log.info(f"   🔧 Index Builds: {stats['index_builds']}")
            
            # Performance Metrics
            self.log.info(f"🚀 PERFORMANCE METRICS:")
            self.log.info(f"   ⚡ Total Lookups: {stats['total_lookups']:,}")
            self.log.info(f"   🚀 Hash Lookups: {stats['hash_lookups']:,}")
            self.log.info(f"   🐌 Linear Lookups: {stats['linear_lookups']:,}")
            self.log.info(f"   🎯 Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
            
            # Timing Analysis
            if stats['hash_lookups'] > 0:
                self.log.info(f"⏱️ TIMING ANALYSIS:")
                self.log.info(f"   ⚡ Avg Hash Lookup Time: {stats['avg_hash_lookup_time_ms']:.3f}ms")
                if stats['linear_lookups'] > 0:
                    self.log.info(f"   🐌 Avg Linear Lookup Time: {stats['avg_linear_lookup_time_ms']:.3f}ms")
                    self.log.info(f"   🚀 Performance Improvement: {stats['performance_improvement']:.1f}x FASTER")
                
                # Calculate theoretical savings
                linking_map_size = len(self.linking_map)
                theoretical_linear_time = linking_map_size * stats['avg_hash_lookup_time_ms'] / 1000
                actual_hash_time = stats['hash_lookup_time']
                time_saved = theoretical_linear_time - actual_hash_time
                
                self.log.info(f"💰 EFFICIENCY GAINS:")
                self.log.info(f"   🔍 Linking Map Size: {linking_map_size:,} entries")
                self.log.info(f"   ⏱️ Time Saved: {time_saved:.3f} seconds")
                self.log.info(f"   🚀 Expected Performance: {linking_map_size}x improvement over linear search")
            
            # Memory Usage
            linking_map_memory = len(self.linking_map) * 1024  # Rough estimate
            index_memory = (stats['ean_entries'] + stats['url_entries'] + stats['asin_entries']) * 512  # Rough estimate
            
            self.log.info(f"🧠 MEMORY ANALYSIS:")
            self.log.info(f"   📋 Linking Map Memory: ~{linking_map_memory/1024:.1f}KB")
            self.log.info(f"   🔍 Hash Index Memory: ~{index_memory/1024:.1f}KB")
            self.log.info(f"   📊 Memory Overhead: {(index_memory/max(1, linking_map_memory))*100:.1f}%")
            
            self.log.info("=" * 80)
            
        except Exception as e:
            self.log.error(f"❌ Error generating hash optimization summary: {e}")

    def benchmark_hash_performance(self, sample_size: int = 100) -> Dict[str, Any]:
        """
        🚀 HASH OPTIMIZATION: Benchmark hash lookup performance against linear search.
        
        Args:
            sample_size: Number of test lookups to perform
            
        Returns:
            Dictionary with benchmark results
        """
        try:
            if not self.linking_map or len(self.linking_map) < 10:
                self.log.warning("⚠️ Insufficient linking map data for benchmarking")
                return {}
            
            # Extract test data
            test_eans = [entry.get('supplier_ean') for entry in self.linking_map[:sample_size] if entry.get('supplier_ean')]
            test_urls = [entry.get('supplier_url') for entry in self.linking_map[:sample_size] if entry.get('supplier_url')]
            
            if not test_eans and not test_urls:
                self.log.warning("⚠️ No valid test data found for benchmarking")
                return {}
            
            # Run benchmark
            results = self.performance_comparator.benchmark_performance(
                linking_map=self.linking_map,
                test_eans=test_eans[:min(50, len(test_eans))],
                test_urls=test_urls[:min(50, len(test_urls))],
                hash_optimizer=self.hash_optimizer
            )
            
            self.log.info("🧪 HASH OPTIMIZATION BENCHMARK COMPLETED:")
            self.log.info(f"   🚀 Hash Lookup Average: {results.get('avg_hash_time_ms', 0):.3f}ms")
            self.log.info(f"   🐌 Linear Lookup Average: {results.get('avg_linear_time_ms', 0):.3f}ms")
            self.log.info(f"   ⚡ Performance Improvement: {results.get('performance_improvement', 0):.1f}x faster")
            self.log.info(f"   ✅ Match Consistency: {results.get('match_consistency', False)}")
            
            return results
            
        except Exception as e:
            self.log.error(f"❌ Error running hash optimization benchmark: {e}")
            return {}

    def _initialize_output_directory(self):
        """Creates and returns the absolute path to the output directory."""
        output_dir = self.system_config.get("output_root", "OUTPUTS")
        os.makedirs(output_dir, exist_ok=True)
        return os.path.abspath(output_dir)

    def _initialize_amazon_extractor(self):
        """Initializes the Amazon extractor with the shared browser manager."""
        chrome_debug_port = self.system_config.get('chrome_debug_port', 9222)
        return FixedAmazonExtractor(
            chrome_debug_port=chrome_debug_port,
            ai_client=None  # AI features disabled
        )

    def _initialize_supplier_scraper(self):
        """Initializes the supplier scraper with the shared browser manager."""
        return ConfigurableSupplierScraper(
            ai_client=None,  # AI features disabled
            headless=False,  # Keep browser visible for debugging
            use_shared_chrome=True,  # Use existing Chrome instance
            auth_callback=None,  # No authentication callback needed
            browser_manager=self.browser_manager
        )

    def _get_product_identifier(self, product_url: str) -> str:
        """
        Get a readable identifier for a product from URL for debugging
        
        Args:
            product_url: Product URL or product dict
            
        Returns:
            Short identifier for logging
        """
        if isinstance(product_url, dict):
            # If it's a product dict, try to get title or URL
            title = product_url.get('title', '')
            if title and len(title) > 3:
                return title[:30] + ("..." if len(title) > 30 else "")
            url = product_url.get('url', '')
            if url:
                return url.split('/')[-1][:20]
            return "Unknown Product"
        elif isinstance(product_url, str):
            # If it's a URL string, extract the last part
            return product_url.split('/')[-1][:20] if product_url else "Unknown URL"
        else:
            return str(product_url)[:20]

    def _validate_initialization(self):
        """Validates that all critical attributes are properly initialized."""
        required_attributes = {
            'results_summary': dict,
            'extractor': object,
            'amazon_extractor': object,
            'supplier_scraper': object,
            'system_config': dict,
            'output_dir': str,
            'supplier_cache_dir': str,
            'state_manager': object
        }
        
        for attr_name, expected_type in required_attributes.items():
            if not hasattr(self, attr_name):
                raise AttributeError(f"Critical attribute '{attr_name}' not initialized in PassiveExtractionWorkflow")
            
            attr_value = getattr(self, attr_name)
            if attr_value is None:
                raise AttributeError(f"Critical attribute '{attr_name}' is None in PassiveExtractionWorkflow")
            
            if not isinstance(attr_value, expected_type):
                raise AttributeError(f"Critical attribute '{attr_name}' has wrong type. Expected {expected_type}, got {type(attr_value)}")
        
        self.log.info("✅ Initialization validation passed - all critical attributes verified")
    
    def _get_authoritative_category_count(self, category_urls_to_scrape: List[str] = None) -> int:
        """
        Get authoritative category count from configuration as the single source of truth.
        This replaces hardcoded fallbacks with dynamic configuration loading.
        
        Args:
            category_urls_to_scrape: Optional list of category URLs for fallback counting
            
        Returns:
            int: Authoritative category count from configuration
        """
        try:
            # Primary source: Direct configuration file loading
            from pathlib import Path
            import json
            config_path = Path(__file__).parent.parent / "config" / "poundwholesale_categories.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                total_categories = len(config_data.get("category_urls", []))
                self.log.info(f"📊 AUTHORITATIVE COUNT: {total_categories} categories from config file")
                return total_categories
                
        except Exception as e:
            self.log.warning(f"Failed to load categories from config file: {e}")
            
        try:
            # Secondary source: SystemConfigLoader
            from config.system_config_loader import SystemConfigLoader
            config_loader = SystemConfigLoader()
            config_data = config_loader.load_config()
            supplier_config = config_data.get("supplier_configs", {}).get(self.supplier_name, {})
            category_urls_from_config = supplier_config.get("category_urls", [])
            if category_urls_from_config:
                total_categories = len(category_urls_from_config)
                self.log.info(f"📊 AUTHORITATIVE COUNT: {total_categories} categories from SystemConfigLoader")
                return total_categories
                
        except Exception as e:
            self.log.warning(f"Failed to load categories from SystemConfigLoader: {e}")
            
        # Tertiary source: Runtime category URLs parameter
        if category_urls_to_scrape and hasattr(self, 'category_urls_to_scrape'):
            total_categories = len(self.category_urls_to_scrape)
            self.log.info(f"📊 AUTHORITATIVE COUNT: {total_categories} categories from category_urls_to_scrape attribute")
            return total_categories
        elif category_urls_to_scrape:
            total_categories = len(category_urls_to_scrape)
            self.log.info(f"📊 AUTHORITATIVE COUNT: {total_categories} categories from parameter")
            return total_categories
            
        # Final fallback: File-grounded calculation from state manager
        if hasattr(self, 'state_manager') and self.state_manager:
            try:
                file_grounded = self.state_manager._calculate_file_grounded_totals()
                total_categories = file_grounded.get("total_categories", 0)
                if total_categories > 0:
                    self.log.info(f"📊 AUTHORITATIVE COUNT: {total_categories} categories from state manager file-grounded calculation")
                    return total_categories
            except Exception as e:
                self.log.warning(f"Failed to get categories from state manager: {e}")
        
        # Ultimate fallback - log warning but don't use hardcoded value
        self.log.error("❌ CRITICAL: Could not determine authoritative category count from any source")
        self.log.error("This indicates a configuration or system error that needs investigation")
        return 0  # Return 0 instead of hardcoded fallback to make the issue visible

    async def run(self):
        """Main execution loop for the workflow."""
        profitable_results: List[Dict[str, Any]] = []
        session_id = f"{self.supplier_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log.info(f"--- Starting Passive Extraction Workflow for: {self.supplier_name} ---")
        self.log.info(f"Session ID: {session_id}")

        # FIXED: Load configuration values directly from system_config (no hardcoded fallbacks)
        # This ensures all toggle experiments work correctly
        
        # So we don't need to access ["system"] again - it's already the system section
        max_products_to_process = self.system_config.get("max_products", 10)
        max_products_per_category = self.system_config.get("max_products_per_category", 5)
        max_analyzed_products = self.system_config.get("max_analyzed_products", 5)
        max_products_per_cycle = self.system_config.get("max_products_per_cycle", 5)
        supplier_extraction_batch_size = self.system_config.get("supplier_extraction_batch_size", 3)
        
        # Get the full config for accessing root level values
        full_config = self.config_loader._config
        max_categories_per_request = full_config.get("max_categories_per_request", 5)
        
        self.max_price = full_config.get("processing_limits", {}).get("max_price_gbp", 20.0)
        
        # Apply batch synchronization if enabled
        batch_sync_config = full_config.get("batch_synchronization", {})
        if batch_sync_config.get("enabled", False):
            max_products_per_cycle, supplier_extraction_batch_size = self._apply_batch_synchronization(
                max_products_per_cycle, supplier_extraction_batch_size, batch_sync_config
            )
        
        self.log.info(f"📊 CONFIGURATION VALUES:")
        self.log.info(f"   max_products_to_process: {max_products_to_process}")
        self.log.info(f"   max_products_per_category: {max_products_per_category}")
        self.log.info(f"   max_analyzed_products: {max_analyzed_products}")
        self.log.info(f"   max_products_per_cycle: {max_products_per_cycle}")
        self.log.info(f"   supplier_extraction_batch_size: {supplier_extraction_batch_size}")
        self.log.info(f"   max_categories_per_request: {max_categories_per_request}")

        # Load state and linking map
        self.state_manager.load_state()
        if hasattr(self.state_manager, 'validate_and_repair_state'):
            self.state_manager.validate_and_repair_state()
        self.last_processed_index = self.state_manager.get_resumption_index()
        self.consecutive_amazon_price_misses = self.state_manager.state_data.get('consecutive_amazon_price_misses', 0)
        self.log.info(f"📋 Loaded existing processing state for {self.supplier_name}")
        self.log.info(f"🔄 Resuming from index {self.last_processed_index}")

        # 🚨 REMOVED: Hard reset logic removed per user request - was causing incorrect cache validation
        # System will now always attempt to resume from processing state without validation conflicts
        self.log.info("✅ Processing state loaded - system will resume from last position")
        
        # Load the linking map for the current supplier
        self.linking_map = self._load_linking_map(self.supplier_name)
        self.log.debug(f"🔍 DEBUG: linking_map loaded as type: {type(self.linking_map)}, length: {len(self.linking_map)}")
        
        # 🚨 CRITICAL: Two-Phase Detection Logic - Find actual supplier cache file
        supplier_cache_file, supplier_cache_count = self._find_actual_supplier_cache_file(self.supplier_name)
        supplier_cache_exists = bool(supplier_cache_file)
        
        # 🚨 FIX 2: Store total cache count for proper state updates
        self.total_cache_count = supplier_cache_count
        
        linking_map_count = len(self.linking_map) if self.linking_map else 0
        
        # 🚨 SENTINEL MONITORING: Check for session vs global totals divergence
        self.sentinel_monitor.check_totals_divergence(
            linking_map_count, supplier_cache_count, 'supplier_cache_vs_linking_map'
        )
        
        # Phase detection logic - FIXED to handle reverse gap scenario correctly
        if supplier_cache_count == 0:
            current_phase = "SUPPLIER_EXTRACTION"
            self.log.info(f"🔍 PHASE DETECTION: SUPPLIER_EXTRACTION (no supplier cache found)")
        elif linking_map_count == 0:
            current_phase = "AMAZON_ANALYSIS"
            self.log.info(f"🔍 PHASE DETECTION: AMAZON_ANALYSIS (supplier cache: {supplier_cache_count} products, no linking map)")
        elif linking_map_count > supplier_cache_count:
            # REVERSE GAP: More linking map entries than cache entries
            current_phase = "FRESH_CATEGORIES"
            self.log.info(f"🔍 PHASE DETECTION: FRESH_CATEGORIES (reverse gap - linking map: {linking_map_count} > cache: {supplier_cache_count})")
            self.log.info("✅ System will start with first URL in config and skip already processed products")
        elif linking_map_count < supplier_cache_count:
            # NORMAL GAP: More cache entries than linking map entries
            current_phase = "GAP_PROCESSING"
            gap_size = supplier_cache_count - linking_map_count
            self.log.info(f"🔍 PHASE DETECTION: GAP_PROCESSING (normal gap - cache: {supplier_cache_count} > linking map: {linking_map_count})")
            self.log.info(f"📊 GAP SIZE: {gap_size} products need Amazon analysis first")
        else:
            current_phase = "COMPLETED"
            self.log.info(f"🔍 PHASE DETECTION: COMPLETED (supplier: {supplier_cache_count}, linking map: {linking_map_count})")
        
        self.current_phase = current_phase
        
        config_hash = str(hash(str(self.system_config)))
        runtime_settings = {
            "max_products_to_process": max_products_to_process,
            "max_products_per_category": max_products_per_category,
            "current_phase": current_phase,
            "supplier_cache_count": supplier_cache_count,
            "linking_map_count": linking_map_count
        }
        # 🚨 SURGICAL WORKFLOW FIX: STATE CONTRADICTION GUARDRAIL (ENHANCED)
        # Fixed to read from correct state tracking system and add comprehensive debug logging
        current_state = self.state_manager.state_data
        is_fresh_start_flag = current_state.get("is_fresh_start", True)
        successful_products = current_state.get("successful_products", 0)
        
        # Check BOTH tracking systems for evidence of work (dual tracking fix)
        system_progression = current_state.get("system_progression", {})
        supplier_extraction = current_state.get("supplier_extraction_progress", {})
        
        # System progression tracking
        system_category = system_progression.get("current_category_index")
        
        # Supplier extraction tracking (more reliable for detecting actual work)
        supplier_category = supplier_extraction.get("current_category_index", 0)
        completed_categories = supplier_extraction.get("categories_completed", [])
        
        # Enhanced evidence detection using both tracking systems
        has_evidence_of_work = (
            successful_products > 0 or
            (system_category is not None and system_category > 0) or
            supplier_category > 0 or
            len(completed_categories) > 0
        )

        # Debug logging to show actual state values being read
        self.log.info("🔍 STATE CONTRADICTION CHECK DEBUG:")
        self.log.info(f"   is_fresh_start: {is_fresh_start_flag}")
        self.log.info(f"   successful_products: {successful_products}")
        self.log.info(f"   system_progression.current_category_index: {system_category}")
        self.log.info(f"   supplier_extraction.current_category_index: {supplier_category}")
        self.log.info(f"   supplier_extraction.categories_completed: {len(completed_categories)} categories")
        self.log.info(f"   has_evidence_of_work: {has_evidence_of_work}")

        if is_fresh_start_flag and has_evidence_of_work:
            self.log.warning("🚨 STATE CONTRADICTION DETECTED - PREVENTING start_processing() CALL...")
            self.log.warning(f"   Fresh start flag=True but evidence shows {successful_products} successful products")
            self.log.warning(f"   and {len(completed_categories)} completed categories")
            self.state_manager.state_data["is_fresh_start"] = False
            self.log.info("✅ State contradiction resolved - preserved existing progress")
        else:
            self.log.info("✅ No state contradiction - proceeding with start_processing() call...")
            self.state_manager.start_processing(config_hash, runtime_settings)
            self.log.info("✅ Processing state initialized and started")

        try:
            # Note: Supplier configuration is loaded automatically by ConfigurableSupplierScraper
            # Load the linking map for the current supplier
            self.linking_map = self._load_linking_map(self.supplier_name)

            # --- CUSTOM CATEGORY LOGIC ---
            if self.workflow_config.get('use_predefined_categories'):
                self.log.info("CUSTOM MODE: Using predefined category list.")
                category_urls_to_scrape = await self._get_predefined_categories(self.supplier_name)
                if not category_urls_to_scrape:
                    self.log.error("CUSTOM MODE FAILED: No URLs found in predefined list. Aborting.")
                    return []
                # 🚨 DYNAMIC CATEGORY CALCULATION: Calculate categories needed based on max_products / max_products_per_category
                import math
                
                system_config = self.config_loader.get_system_config()
                max_products = system_config.get('max_products')
                max_products_per_category = system_config.get('max_products_per_category')
                
                def is_infinite_mode(max_products, max_products_per_category):
                    """Detect infinite mode based on multiple indicators"""
                    mp = max_products or 0
                    mppc = max_products_per_category or 0
                    
                    return any([
                        mp <= 0,                    # Zero or negative
                        mppc <= 0,                  # Zero or negative  
                        mp >= 99999,                # High value threshold
                        mppc >= 99999,              # High value threshold
                    ])
                
                # Apply infinite mode detection
                total_available_categories = len(category_urls_to_scrape)
                
                if is_infinite_mode(max_products, max_products_per_category):
                    # INFINITE MODE: Process all available categories
                    self.log.info(f"🌟 INFINITE MODE DETECTED: max_products={max_products}, max_products_per_category={max_products_per_category}")
                    self.log.info(f"📋 Processing ALL {total_available_categories} predefined categories (infinite mode)")
                    # No slicing - use all categories
                else:
                    # FINITE MODE: Safe calculation with error handling
                    try:
                        if max_products > 0 and max_products_per_category > 0:
                            categories_needed = math.ceil(max_products / max_products_per_category)
                            categories_needed = min(categories_needed, total_available_categories)
                            
                            self.log.info(f"📊 FINITE MODE: {max_products} max_products ÷ {max_products_per_category} max_products_per_category = {categories_needed} categories needed")
                            category_urls_to_scrape = category_urls_to_scrape[:categories_needed]
                            self.log.info(f"📋 Processing {len(category_urls_to_scrape)} predefined categories (finite mode)")
                        else:
                            # Fallback to infinite mode
                            self.log.warning(f"⚠️ Invalid finite mode values, falling back to infinite mode")
                            self.log.info(f"📋 Processing ALL {total_available_categories} predefined categories (fallback infinite mode)")
                    except Exception as e:
                        # Any error defaults to infinite mode
                        self.log.error(f"❌ Calculation error: {e}, falling back to infinite mode")
                        self.log.info(f"📋 Processing ALL {total_available_categories} predefined categories (error fallback)")
            else:
                # Original AI-based category selection
                self.log.info("STANDARD MODE: Using AI-based hierarchical category selection.")
                category_urls_to_scrape = await self._hierarchical_category_selection(self.workflow_config.get('supplier_url'), self.supplier_name)
                if not category_urls_to_scrape:
                    self.log.warning("No categories selected for scraping. Workflow cannot continue.")
                    return []

            # Check hybrid processing configuration (from full config, not system section)
            hybrid_config = full_config.get("hybrid_processing", {})
            if hybrid_config.get("enabled", False):
                self.log.info("🔄 HYBRID PROCESSING MODE: Enabled")
                return await self._run_hybrid_processing_mode(
                    self.workflow_config.get('supplier_url'), self.supplier_name, category_urls_to_scrape, 
                    max_products_per_category, max_products_to_process, 
                    max_analyzed_products, max_products_per_cycle, supplier_extraction_batch_size
                )
            
            supplier_products = await self._extract_supplier_products(
                self.workflow_config.get('supplier_url'), self.supplier_name, category_urls_to_scrape, max_products_per_category, max_products_to_process, supplier_extraction_batch_size
            )

            if not supplier_products:
                self.log.warning(f"No products extracted from {self.supplier_name}. Workflow cannot continue.")
                return []

            self.results_summary["total_supplier_products"] = len(supplier_products)
            self.log.info(f"Successfully got {len(supplier_products)} products from {self.supplier_name}")
            
            # Save supplier products to cache immediately after extraction using centralized path management
            supplier_cache_file = str(path_manager.get_output_path('cached_products', f"{self.supplier_name.replace('.', '-')}_products_cache.json"))
            self.log.info(f"🔍 DEBUG: supplier_cache_dir = '{self.supplier_cache_dir}'")
            self.log.info(f"🔍 DEBUG: supplier_cache_file = '{supplier_cache_file}'")
            # 🚨 ATOMIC FIX 8: Save products to cache atomically
            new_count = self._save_products_to_cache(supplier_products, supplier_cache_file)
            self.log.info(f"💾 ATOMIC INITIAL SAVE: Saved {len(supplier_products)} products ({new_count} new) to cache")

            # Filter products based on price and validity
            valid_supplier_products = [
                p for p in supplier_products
                if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
            ]
            price_filtered_products = [
                p for p in valid_supplier_products
                if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
            ]
            self.log.info(f"Found {len(valid_supplier_products)} valid supplier products, {len(price_filtered_products)} within price range [£{MIN_PRICE}-£{MAX_PRICE}]")
            
            # Check if all cached products have been processed
            if self.last_processed_index >= len(price_filtered_products):
                self.log.info(f"📋 All cached products have been processed in previous runs (index {self.last_processed_index} >= total {len(price_filtered_products)}). Continuing with fresh data...")
                self.last_processed_index = 0
            
            # Apply max_products_to_process limit starting from resume index
            if max_products_to_process <= 0:
                # Unlimited mode - process all remaining products
                products_to_analyze = price_filtered_products[self.last_processed_index:]
                self.log.info(f"🔄 UNLIMITED MODE: Processing ALL {len(products_to_analyze)} remaining products starting from index {self.last_processed_index}")
            else:
                # Limited mode - process up to max_products_to_process starting from resume index
                end_index = min(self.last_processed_index + max_products_to_process, len(price_filtered_products))
                products_to_analyze = price_filtered_products[self.last_processed_index:end_index]
                self.log.info(f"🔄 LIMITED MODE: Processing {len(products_to_analyze)} products (from index {self.last_processed_index} to {end_index-1})")
            
            # Update processing state with total products to analyze
            # 🚨 FIX 2: Use total cache count instead of current filtered batch
            total_products_for_state = getattr(self, 'total_cache_count', len(price_filtered_products))
            self.state_manager.update_processing_index(self.last_processed_index, total_products_for_state)

            # Batch processing logic - group products by max_products_per_cycle
            batch_size = max_products_per_cycle
            total_batches = (len(products_to_analyze) + batch_size - 1) // batch_size
            self.log.info(f"🚀 BATCH PROCESSING: {len(products_to_analyze)} products in {total_batches} batches of {batch_size}")

            # Process products in batches
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(products_to_analyze))
                batch_products = products_to_analyze[start_idx:end_idx]
                
                self.log.info(f"🔄 Processing batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
                
                # Process each product in the current batch
                for i, product_data in enumerate(batch_products):
                    # Calculate the absolute index in the full product list (considering resume index)
                    current_index = self.last_processed_index + start_idx + i + 1
                    # 🚨 FIX 2: Show correct total in log messages
                    total_for_display = getattr(self, 'total_cache_count', len(price_filtered_products))
                    self.log.info(f"--- Processing supplier product {current_index}/{total_for_display}: '{product_data.get('title')}' ---")
                    
                    # 🚨 FIX: Update state manager with consistent index tracking
                    if hasattr(self, 'state_manager') and self.state_manager:
                        # Use unified state update method
                        self.state_manager.update_processing_index(current_index, total_for_display)
                        
                        # Also update detailed progress for category tracking
                        if hasattr(self.state_manager, 'update_supplier_extraction_progress'):
                            self.state_manager.update_supplier_extraction_progress(
                                category_index=batch_num + 1,
                                total_categories=len(category_urls),
                                subcategory_index=i + 1,
                                total_subcategories=len(batch_products),
                                category_url=product_data.get('source_url', 'unknown'),
                                extraction_phase="amazon_analysis"
                            )
                        
                        # Save state after every product to ensure resumability
                        self.state_manager.save_state()
                    
                    # 🔧 AUTHENTICATION FALLBACK CHECK
                    if self._check_authentication_fallback_needed():
                        self.log.warning("🔐 Authentication fallback needed - attempting re-authentication...")
                        auth_success = await self._perform_authentication_fallback()
                        if not auth_success:
                            self.log.error("❌ Authentication fallback failed - continuing with current session")
                    
                    self.log.info(f"🔍 DEBUG: Updating processing index to {current_index}/{len(price_filtered_products)}")
                    self.state_manager.update_processing_index(current_index, len(price_filtered_products))
                    # Verify the update worked
                    current_state = self.state_manager.get_state_summary()
                    self.log.info(f"🔍 DEBUG: State after update - last_processed_index: {current_state.get('progress', 'unknown')}")
                    
                    # 🚨 CRITICAL FIX: Amazon Analysis Resumption Logic
                    # Check linking map to avoid re-processing already analyzed Amazon products
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    supplier_url = product_data.get("url")
                    
                    # 🚀 HASH OPTIMIZATION: Check if this product already exists in linking map (Amazon analysis completed)
                    # Using O(1) hash lookup instead of O(n) linear search for 3,650x performance improvement
                    already_in_linking_map, existing_entry = self.hash_optimizer.check_product_in_linking_map(
                        supplier_ean=supplier_ean, supplier_url=supplier_url
                    )
                    if already_in_linking_map and existing_entry:
                        self.log.info(f"✅ AMAZON SKIP: Product '{product_data.get('title')}' already in linking map (ASIN: {existing_entry.get('amazon_asin')}) - skipping Amazon analysis")
                        self.log.debug(f"🚀 HASH LOOKUP: O(1) lookup found existing entry instantly")
                    
                    # Check if product has been previously processed in state manager
                    is_already_processed = self.state_manager.is_product_processed(supplier_url)
                    
                    # Skip if already processed OR already in linking map (Amazon analysis complete)
                    if is_already_processed or already_in_linking_map:
                        if is_already_processed:
                            self.log.info(f"SUPPLIER SKIP: Product already processed in state: {supplier_url}")
                        
                        # If in linking map but not marked as processed, update state
                        if already_in_linking_map and not is_already_processed:
                            self.state_manager.mark_product_processed(supplier_url, "completed_from_linking_map")
                            self.log.info(f"📋 Updated state: Marked product as completed from linking map")
                        
                        continue  # Skip further processing - Amazon analysis already complete

                    # 🚨 LOGIN SCRIPT TRIGGER - Before Amazon product detail extraction as required
                    await self._trigger_authentication_check(f"amazon_extraction_product_{processed_products}")
                    
                    # Extract Amazon data
                    self.log.info(f"🔍 DEBUG: About to extract Amazon data for product: '{product_data.get('title')}'")
                    self.log.info(f"🔍 DEBUG: Product EAN/barcode: {product_data.get('ean')} / {product_data.get('barcode')}")
                    
                    amazon_data = await self._get_amazon_data(product_data)
                    
                    self.log.info(f"🔍 DEBUG: Amazon data extraction result: {type(amazon_data)}")
                    if amazon_data:
                        self.log.info(f"🔍 DEBUG: Amazon data keys: {list(amazon_data.keys()) if isinstance(amazon_data, dict) else 'not a dict'}")
                        if isinstance(amazon_data, dict) and "error" not in amazon_data:
                            self.log.info(f"🔍 DEBUG: Amazon ASIN extracted: {amazon_data.get('asin')}")
                        
                    if not amazon_data or "error" in amazon_data:
                        self.log.warning(f"Could not retrieve valid Amazon data for '{product_data.get('title')}'. Creating no-match linking entry to prevent reprocessing.")
                        self.log.warning(f"🔍 DEBUG: Amazon data failure: {amazon_data}")
                        
                        # 🚨 FIX: Create no-match linking entry to prevent infinite reprocessing loops
                        supplier_ean = product_data.get("ean") or product_data.get("barcode")
                        if supplier_ean == "None" or supplier_ean is None:
                            supplier_ean = None
                            
                        # Determine the reason for no match
                        error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                        no_match_reason = f"Amazon search failed: {error_info}"
                        
                        # Create no-match linking entry
                        no_match_entry = {
                            "supplier_ean": supplier_ean,
                            "amazon_asin": None,
                            "supplier_title": product_data.get("title"),
                            "amazon_title": None,
                            "supplier_price": product_data.get("price"),
                            "amazon_price": None,
                            "match_method": "none",  # NEW: Indicates no match found
                            "confidence": 0,    # NEW: No confidence for failed matches
                            "created_at": datetime.now().isoformat(),
                            "supplier_url": product_data.get("url"),
                            "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                        }
                        
                        # Add no-match entry to linking map using optimized method
                        self._add_linking_map_entry_optimized(no_match_entry)
                        self.log.info(f"✅ Added NO-MATCH linking entry: {supplier_ean or 'NO_EAN'} → NO MATCH ({no_match_reason})")
                        self.log.info(f"🔍 DEBUG: Current linking_map size: {len(self.linking_map)} entries")
                        
                        # Mark as processed to prevent state manager reprocessing
                        self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                        continue

                    # Save the Amazon data with the correct filename
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    # Ensure we don't get None values
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                    
                    # Use supplier product title when EAN is not available
                    if not supplier_ean:
                        # Sanitize supplier product title for filename
                        supplier_title = product_data.get("title", "NO_TITLE")
                        # Remove/replace characters that aren't safe for filenames
                        import re
                        filename_identifier = re.sub(r'[<>:"/\\|?*]', '_', supplier_title)
                        filename_identifier = re.sub(r'\s+', '_', filename_identifier)  # Replace spaces with underscores
                        filename_identifier = filename_identifier[:50]  # Limit length to prevent long filenames
                        self.log.info(f"🔧 Using supplier title for Amazon cache filename: '{supplier_title}' -> '{filename_identifier}'")
                    else:
                        filename_identifier = supplier_ean
                    
                    asin = amazon_data.get("asin", "NO_ASIN")
                    amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                    success = self.save_guardian.save_json_atomic(amazon_cache_path, amazon_data)
                    if success:
                        self.log.info(f"Saved Amazon data to {amazon_cache_path}")
                    else:
                        self.log.error(f"❌ Failed to save Amazon data to {amazon_cache_path}")

                    self.log.info(f"🔍 DEBUG: supplier_ean='{supplier_ean}', asin='{asin}', product_ean='{product_data.get('ean')}'")
                    self.log.info(f"🔍 DEBUG: Checking linking conditions - supplier_ean valid: {bool(supplier_ean)}, asin valid: {bool(asin and asin != 'NO_ASIN')}")
                    
                    # Get actual search method used (fixed logic)
                    actual_search_method = amazon_data.get("_search_method_used", "unknown")
                    
                    # Create linking entry with accurate method and confidence
                    self.log.info(f"🔍 DEBUG: Linking map entry conditions check:")
                    self.log.info(f"   supplier_ean: '{supplier_ean}' (valid: {bool(supplier_ean)})")
                    self.log.info(f"   product_title: '{product_data.get('title')}' (valid: {bool(product_data.get('title'))})")
                    self.log.info(f"   asin: '{asin}' (valid: {bool(asin and asin != 'NO_ASIN')})")
                    self.log.info(f"   overall condition: {bool((supplier_ean or product_data.get('title')) and asin and asin != 'NO_ASIN')}")
                    
                    if (supplier_ean or product_data.get("title")) and asin and asin != "NO_ASIN":
                        # Determine confidence based on actual search success, not just supplier data availability
                        if actual_search_method == "EAN":
                            confidence = "high"  # EAN search actually worked
                        elif actual_search_method == "title":
                            confidence = "medium"  # Title search worked
                        else:
                            confidence = "low"  # Unknown method
                            
                        linking_entry = {
                            "supplier_ean": supplier_ean,
                            "amazon_asin": asin,
                            "supplier_title": product_data.get("title"),
                            "amazon_title": amazon_data.get("title"),
                            "supplier_price": product_data.get("price"),
                            "amazon_price": amazon_data.get("current_price"),
                            "match_method": actual_search_method,  # Use actual method, not assumption
                            "confidence": confidence,
                            "created_at": datetime.now().isoformat(),
                            "supplier_url": product_data.get("url")
                        }
                        # 🚀 HASH OPTIMIZATION: Use optimized method to add entry and update indexes
                        self._add_linking_map_entry_optimized(linking_entry)
                        self.log.info(f"✅ Added linking map entry: {actual_search_method.upper()} search {supplier_ean or 'NO_EAN'} → ASIN {asin}")
                        self.log.info(f"🔍 DEBUG: Current linking_map size: {len(self.linking_map)} entries")
                        self.log.info(f"🔍 DEBUG: Linking entry created: {linking_entry}")
                        
                        # 🚨 CRITICAL FIX: Check financial report trigger after each linking map entry
                        financial_batch_size = self.config_loader.get_financial_batch_size()
                        current_linking_map_count = len(self.linking_map)
                        
                        if current_linking_map_count > 0 and current_linking_map_count % financial_batch_size == 0:
                            try:
                                self.log.info(f"🚨 FINANCIAL REPORT TRIGGER: Reached {current_linking_map_count} linking map entries (trigger every {financial_batch_size})")
                                from tools.FBA_Financial_calculator import run_calculations
                                financial_results = run_calculations(self.supplier_name)
                                if financial_results and financial_results.get('statistics', {}).get('output_file'):
                                    self.log.info(f"✅ Financial report EXECUTED: {financial_results['statistics']['output_file']}")
                                else:
                                    self.log.warning("⚠️ Financial report executed but no file path returned")
                            except ImportError as ie:
                                self.log.error(f"❌ Could not import FBA_Financial_calculator: {ie}")
                            except Exception as e:
                                self.log.error(f"❌ Error executing financial report: {e}")
                        elif current_linking_map_count > 0:
                            next_trigger_count = ((current_linking_map_count // financial_batch_size) + 1) * financial_batch_size
                            self.log.info(f"💡 FINANCIAL REPORT TRIGGER: Next trigger at {next_trigger_count} linking map entries (current: {current_linking_map_count}, trigger frequency: {financial_batch_size})")
                    else:
                        self.log.error(f"❌ CRITICAL: Could not create linking map entry - condition failed!")
                        self.log.error(f"   supplier_ean: '{supplier_ean}' (bool: {bool(supplier_ean)})")
                        self.log.error(f"   product_title: '{product_data.get('title')}' (bool: {bool(product_data.get('title'))})")
                        self.log.error(f"   asin: '{asin}' (bool: {bool(asin and asin != 'NO_ASIN')})")
                        self.log.error(f"   This means NO linking map entries will be created and saved!")

                    # Perform financial analysis for individual product
                    try:
                        # Import financial calculation functions directly to avoid full cache dependency
                        # Already imported at top of file - from FBA_Financial_calculator import financials as calc_financials
                        
                        # Extract supplier price with validation from the linking map entry
                        supplier_price_inc_vat = linking_entry.get("supplier_price", 0)
                        
                        # 🔧 AUTHENTICATION FALLBACK: Record price status for monitoring
                        has_supplier_price = supplier_price_inc_vat and supplier_price_inc_vat > 0
                        self._record_product_price_status(product_data, has_supplier_price)
                        if isinstance(supplier_price_inc_vat, str):
                            # Clean price string and convert to float
                            import re
                            price_clean = re.sub(r'[^0-9.]', '', supplier_price_inc_vat)
                            supplier_price_inc_vat = float(price_clean) if price_clean else 0
                        elif supplier_price_inc_vat is None:
                            supplier_price_inc_vat = 0
                            
                        # Calculate financial metrics for this specific product
                        # 🚨 FIX: Use correct function signature - pass individual values, not full objects
                        try:
                            supplier_price = float(product_data.get('price', 0))
                            amazon_price = float(amazon_data.get('current_price') or amazon_data.get('price', 0))
                            
                            if amazon_price > 0:
                                financials = calc_financials(
                                    supplier_price=supplier_price,
                                    amazon_price=amazon_price,
                                    amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                                    amazon_rating=amazon_data.get("rating", 0),
                                    amazon_review_count=amazon_data.get("reviews", 0)
                                )
                                if financials:
                                    self.log.info(f"✅ Financial analysis complete for {product_data.get('title')}")
                                else:
                                    self.log.warning(f"⚠️ Financial calculation returned empty for {product_data.get('title')}")
                                    financials = None
                            else:
                                self.log.warning(f"❌ No valid Amazon price found for {product_data.get('title')}")
                                financials = None
                        except (ValueError, TypeError) as e:
                            self.log.error(f"Financial calculation error: {e}")
                            self.log.info(f"❌ Financial analysis failed: {e}")
                            financials = None
                        except Exception as e:
                            self.log.error(f"Unexpected financial calculation error: {e}")
                            self.log.debug(f"Product data: {product_data.get('title')}, Amazon price fields: {list(amazon_data.keys()) if isinstance(amazon_data, dict) else 'Not a dict'}")
                            financials = None
                        
                        if not financials:
                            self.log.warning(f"Financial calculation returned empty for '{product_data.get('title')}'")
                            financials = {}
                            
                    except Exception as e:
                        self.log.error(f"Financial calculation failed for '{product_data.get('title')}': {e}")
                        self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
                        # Continue with empty financials rather than failing completely
                        financials = {}

                    # Combine all data
                    combined_data = {**product_data, "amazon_data": amazon_data, "financials": financials}
                                
                    # Check for profitability
                    if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                        self.log.info(f"✅ Profitable product found: '{product_data.get('title')}' (ROI: {financials.get('ROI'):.2f}%, Profit: £{financials.get('NetProfit'):.2f})")
                        profitable_results.append(combined_data)
                        self.results_summary["profitable_products"] += 1
                        self.state_manager.mark_product_processed(product_data.get("url"), "profitable")
                    else:
                        self.log.info(f"Product not profitable: '{product_data.get('title')}' (ROI: {financials.get('ROI', 0):.2f}%, Profit: £{financials.get('NetProfit', 0):.2f})")
                        self.state_manager.mark_product_processed(product_data.get("url"), "not_profitable")

                    # Save state periodically using configurable batch sizes
                    overall_product_index = start_idx + i + 1
                    linking_map_batch = self.system_config.get("linking_map_batch_size", 1)
                    
                    if overall_product_index % linking_map_batch == 0:
                        self.state_manager.save_state(preserve_interruption_state=True)
                        self._save_linking_map(self.supplier_name)
                        self.log.info(f"📊 Periodic save at product {overall_product_index} (linking_map_batch_size: {linking_map_batch})")
                        
                        # 🚨 CRITICAL FIX #4: SMART MEMORY MANAGEMENT
                        # Implement periodic memory clearing with sliding window approach
                        self._perform_smart_memory_management(overall_product_index, batch_products)

            # Final save and completion
            self.log.info("🔍 DEBUG: Starting final save and completion phase...")
            try:
                self.log.info("🔍 DEBUG: Calling state_manager.complete_processing()...")
                self.state_manager.complete_processing()
                self.log.info("✅ State manager processing completed")
                
                self.log.info(f"🔍 DEBUG: Calling _save_linking_map with supplier_name='{self.supplier_name}'...")
                self._save_linking_map(self.supplier_name)
                self.log.info("✅ Linking map save completed")
                
                self.log.info(f"🔍 DEBUG: Calling _save_final_report with {len(profitable_results)} profitable results...")
                self._save_final_report(profitable_results, self.supplier_name)
                self.log.info("✅ Final report save completed")
                
            except Exception as final_save_error:
                self.log.error(f"❌ CRITICAL: Error during final save phase: {final_save_error}", exc_info=True)
                self.log.error("This explains why linking map and financial reports are not being saved!")
            # This must happen regardless of whether products were processed or skipped
            self.log.info("🔍 DEBUG: Starting mandatory final save and completion phase...")
            try:
                self.log.info("🔍 DEBUG: Calling state_manager.complete_processing()...")
                self.state_manager.complete_processing()
                self.log.info("✅ State manager processing completed")
                
                self.log.info(f"🔍 DEBUG: Calling _save_linking_map with supplier_name='{self.supplier_name}'...")
                self._save_linking_map(self.supplier_name)
                self.log.info("✅ Linking map save completed")
                
                self.log.info(f"🔍 DEBUG: Calling _save_final_report with {len(profitable_results)} profitable results...")
                self._save_final_report(profitable_results, self.supplier_name)
                self.log.info("✅ Final report save completed")
                
            except Exception as final_save_error:
                self.log.error(f"❌ CRITICAL: Error during mandatory final save phase: {final_save_error}", exc_info=True)
                self.log.error("This explains why linking map and financial reports are not being saved!")
            
            try:
                self.log.info("🧮 Generating comprehensive financial report...")
                financial_results = run_calculations(self.supplier_name)
                if financial_results and financial_results.get('statistics', {}).get('output_file'):
                    self.log.info(f"✅ Financial report generated: {financial_results['statistics']['output_file']}")
                else:
                    self.log.warning("⚠️ Financial report generated but no file path returned")
            except ImportError as ie:
                self.log.error(f"❌ Could not import FBA_Financial_calculator: {ie}")
            except Exception as e:
                self.log.error(f"❌ Error generating financial report: {e}")
            
            self.log.info(f"📊 Processing state file saved: {self.state_manager.state_file_path}")
            self.log.info(f"📊 Final state summary: {self.state_manager.get_state_summary()}")
            
            # 🚀 HASH OPTIMIZATION: Log comprehensive performance summary
            self.log_hash_optimization_summary()
            
            # 🧪 HASH OPTIMIZATION: Run performance benchmark
            if len(self.linking_map) > 50:  # Only benchmark if we have sufficient data
                benchmark_results = self.benchmark_hash_performance(sample_size=min(100, len(self.linking_map)//2))
                if benchmark_results:
                    self.log.info(f"🧪 BENCHMARK: Hash optimization validated with {benchmark_results.get('performance_improvement', 0):.1f}x improvement")
            
            # 🚨 SENTINEL MONITORING: Finalize monitoring and generate summary
            self.sentinel_monitor.finalize_monitoring()
            
            self.log.info("--- Passive Extraction Workflow Finished ---")
            self.log.info(f"Summary: {self.results_summary}")
        
            return profitable_results

        except Exception as e:
            self.log.error(f"Unexpected error occurred during workflow execution: {e}", exc_info=True)
            return []


    async def _process_gap_products(self, gap_size: int, supplier_cache_count: int, linking_map_count: int) -> List[Dict[str, Any]]:
        """
        Process the gap between cache and linking map entries.
        This processes cached products that haven't been analyzed on Amazon yet.
        """
        self.log.info(f"🔄 Starting gap processing: {gap_size} products need Amazon analysis")
        
        profitable_results = []
        
        # Load cached products
        supplier_cache_file, _ = self._find_actual_supplier_cache_file(self.supplier_name)
        if not supplier_cache_file:
            self.log.error("❌ No supplier cache file found for gap processing")
            return profitable_results
        
        try:
            with open(supplier_cache_file, 'r', encoding='utf-8') as f:
                all_cached_products = json.load(f)
        except Exception as e:
            self.log.error(f"❌ Failed to load cached products: {e}")
            return profitable_results
        
        # Get products that need processing (from linking_map_count to supplier_cache_count)
        gap_products = all_cached_products[linking_map_count:supplier_cache_count]
        
        self.log.info(f"📊 Gap processing: Processing products {linking_map_count+1} to {supplier_cache_count}")
        
        # Process each gap product
        for i, product_data in enumerate(gap_products):
            current_gap_index = i + 1
            overall_product_index = linking_map_count + current_gap_index
            
            self.log.info(f"--- Processing gap product {current_gap_index}/{gap_size}: '{product_data.get('title')}' ---")
            
            # Update gap processing progress
            self.state_manager.update_gap_processing_progress(
                current_gap_index, 
                len([r for r in profitable_results if r.get('profitable', False)]),
                product_data.get('url', '')
            )
            
            # Check if already processed
            supplier_url = product_data.get("url")
            if self.state_manager.is_product_processed(supplier_url):
                self.log.info("Product already processed: skipping")
                continue
            
            # 🚀 HASH OPTIMIZATION: Check if already in linking map using O(1) lookup
            supplier_ean = product_data.get("ean") or product_data.get("barcode")
            already_in_linking_map, existing_entry = self.hash_optimizer.check_product_in_linking_map(
                supplier_ean=supplier_ean, supplier_url=supplier_url
            )
            if already_in_linking_map:
                self.log.info(f"✅ Product already in linking map - skipping (O(1) hash lookup)")
                self.log.debug(f"🚀 HASH LOOKUP: Found existing entry with ASIN: {existing_entry.get('amazon_asin') if existing_entry else 'N/A'}")
            
            if already_in_linking_map:
                continue
            
            # Process through Amazon analysis
            try:
                amazon_data = await self._get_amazon_data(product_data)
                
                if amazon_data and amazon_data.get("asin"):
                    # Create successful linking map entry
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                    
                    actual_search_method = amazon_data.get("_search_method_used", "unknown")
                    if actual_search_method == "EAN":
                        confidence = "high"
                    elif actual_search_method == "title":
                        confidence = "medium"
                    else:
                        confidence = "low"
                    
                    linking_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": amazon_data.get("asin"),
                        "supplier_title": product_data.get("title"),
                        "amazon_title": amazon_data.get("title"),
                        "supplier_price": product_data.get("price"),
                        "amazon_price": amazon_data.get("current_price"),
                        "match_method": actual_search_method,
                        "confidence": confidence,
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url")
                    }
                    # 🚀 HASH OPTIMIZATION: Use optimized method to add entry and update indexes
                    self._add_linking_map_entry_optimized(linking_entry)
                    
                    # Run financial analysis
                    financial_result = await self._run_financial_analysis(product_data, amazon_data)
                    
                    if financial_result and financial_result.get('profitable', False):
                        profitable_results.append(financial_result)
                        self.log.info(f"✅ Profitable gap product found: {product_data.get('title')}")
                    else:
                        self.log.info(f"❌ Not profitable gap product: {product_data.get('title')}")
                else:
                    # 🚨 FIX: Create no-match linking entry for gap processing (same as main processing)
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Gap processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"❌ No Amazon match for gap product: {product_data.get('title')} - Added no-match linking entry")
                
                # Mark as processed
                self.state_manager.mark_product_processed(supplier_url, "completed_gap_processing")
                
                # Save periodically
                if current_gap_index % 5 == 0:
                    self._save_linking_map(self.supplier_name)
                    self.state_manager.save_state(preserve_interruption_state=True)
                    self.log.info(f"📊 Gap processing checkpoint: {current_gap_index}/{gap_size}")
                
            except Exception as e:
                self.log.error(f"❌ Error processing gap product {current_gap_index}: {e}")
                continue
        
        # Final save
        self._save_linking_map(self.supplier_name)
        self.state_manager.save_state(preserve_interruption_state=True)
        
        self.log.info(f"✅ Gap processing completed: {len(profitable_results)} profitable products found")
        return profitable_results
        """Process the gap products (products in cache but not in linking map)"""
        self.log.info(f"🔄 Starting gap processing for {gap_size} products")
        
        profitable_results = []
        
        # Load cached products
        supplier_cache_file, _ = self._find_actual_supplier_cache_file(self.supplier_name)
        if not supplier_cache_file:
            self.log.error("❌ No supplier cache file found for gap processing")
            return profitable_results
        
        try:
            with open(supplier_cache_file, 'r', encoding='utf-8') as f:
                all_cached_products = json.load(f)
        except Exception as e:
            self.log.error(f"❌ Error loading cached products: {e}")
            return profitable_results
        
        # 🚀 HASH OPTIMIZATION: Get products that need processing using O(1) hash lookup
        # Replace O(n) URL set creation with O(1) hash-based processing
        processed_urls_set = self.hash_optimizer.get_processed_urls_set()
        
        gap_products = []
        for product in all_cached_products:
            product_url = product.get("url")
            if product_url and product_url not in processed_urls_set:
                gap_products.append(product)
        
        self.log.info(f"🚀 HASH OPTIMIZATION: Gap processing using O(1) lookups on {len(processed_urls_set)} processed URLs")
        
        self.log.info(f"📊 Found {len(gap_products)} products to process in gap")
        
        # Process gap products
        for i, product_data in enumerate(gap_products[:gap_size]):
            self.log.info(f"--- Processing gap product {i + 1}/{gap_size}: '{product_data.get('title')}' ---")
            
            try:
                amazon_data = await self._get_amazon_data(product_data)
                if amazon_data and amazon_data.get("asin"):
                    # Create linking map entry
                    linking_entry = self._create_linking_map_entry(product_data, amazon_data)
                    # 🚀 HASH OPTIMIZATION: Use optimized method to add entry and update indexes
                    self._add_linking_map_entry_optimized(linking_entry)
                    
                    # Check profitability
                    if self._is_profitable(product_data, amazon_data):
                        profitable_results.append({
                            "supplier_data": product_data,
                            "amazon_data": amazon_data,
                            "linking_entry": linking_entry
                        })
                        self.log.info(f"✅ PROFITABLE GAP: {product_data.get('title')}")
                    
                    # Update gap processing progress
                    self.state_manager.update_gap_processing_progress(
                        i + 1, len(profitable_results), product_data.get("url", "")
                    )
                
            except Exception as e:
                self.log.error(f"❌ Error processing gap product: {e}")
        
        return profitable_results

    def _load_linking_map(self, supplier_name: str) -> List[Dict[str, str]]:
        """Load linking map from supplier-specific JSON file using centralized path management"""
        # Use path_manager for standardized, canonical dotted path construction
        linking_map_path = str(get_linking_map_path(supplier_name=supplier_name))
        
        # Only use canonical path - no fallback patterns
        if os.path.exists(linking_map_path):
            try:
                with open(linking_map_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    
                    # Handle both formats: convert old dict format to new array format
                    if isinstance(raw_data, dict):
                        # Old simple format: {"EAN": "ASIN", "EAN2": "ASIN2"} -> convert to array
                        linking_map = []
                        for ean, asin in raw_data.items():
                            linking_map.append({
                                "supplier_product_identifier": f"EAN_{ean}",
                                "supplier_title_snippet": "",
                                "chosen_amazon_asin": asin,
                                "amazon_title_snippet": "",
                                "amazon_ean_on_page": ean,
                                "match_method": "EAN_cached"
                            })
                        self.log.info(f"✅ Converted linking map from dict format to array format from {linking_map_path} with {len(linking_map)} entries")
                    elif isinstance(raw_data, list):
                        # New detailed format: [{"supplier_product_identifier": "EAN_123", "chosen_amazon_asin": "ABC", ...}]
                        linking_map = raw_data
                        self.log.info(f"✅ Loaded linking map (array format) from {linking_map_path} with {len(linking_map)} entries")
                    else:
                        self.log.error(f"Unexpected linking map format: {type(raw_data)} - Creating new map")
                        return []
                        
                    # 🚀 HASH OPTIMIZATION: Build hash indexes for O(1) lookups
                    self.linking_map = linking_map
                    self.hash_optimizer.build_indexes(linking_map)
                    self.log.info(f"🚀 HASH INDEXES BUILT: Ready for O(1) lookups on {len(linking_map)} entries")
                    
                    return linking_map
            except (json.JSONDecodeError, UnicodeDecodeError, Exception) as e:
                self.log.error(f"Error loading linking map from {linking_map_path}: {e}")
                return []  # Return empty list on error
        
        # No valid linking map found at canonical path
        self.log.info(f"✅ No existing linking map found at {linking_map_path} - Creating new map")
        
        # 🚀 HASH OPTIMIZATION: Initialize empty hash indexes
        self.linking_map = []
        self.hash_optimizer.build_indexes([])
        
        return []

    def _save_linking_map(self, supplier_name: str):
        """Save linking map to supplier-specific JSON file using Windows atomic save"""
        self.log.info(f"🔍 DEBUG: _save_linking_map called with {len(self.linking_map)} entries for supplier {supplier_name}")
        
        # 🚨 SENTINEL MONITORING: Track linking map size before save
        previous_size = 0
        linking_map_path = get_linking_map_path(supplier_name)
        # 🚨 SENTINEL MONITORING: Check for path variants
        self.sentinel_monitor.check_path_variants(str(linking_map_path), "linking_map_access")
        if linking_map_path.exists():
            try:
                with open(linking_map_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    previous_size = len(existing_data) if isinstance(existing_data, list) else 0
            except Exception as e:
                self.log.warning(f"⚠️ Could not read existing linking map for size comparison: {e}")
        
        sample_entry = self.linking_map[0] if self.linking_map else {}
        truncated_sample = {k: str(v)[:50] + '...' if len(str(v)) > 50 else v for k, v in sample_entry.items()}
        self.log.info(f"🔍 DEBUG: linking_map type: {type(self.linking_map)}, entries: {len(self.linking_map)}, sample: {truncated_sample}")
        
        if not self.linking_map:
            self.log.warning("⚠️ CRITICAL: Empty linking map - nothing to save. This suggests linking map entries are not being created!")
            # 🚨 SENTINEL MONITORING: Alert on empty linking map
            self.sentinel_monitor.check_linking_map_shrinkage(0, previous_size)
            return
            
        # Use consistent path naming with get_linking_map_path
        try:
            self.log.info(f"🔍 DEBUG: Target file path: {linking_map_path}")
            
        except Exception as path_error:
            self.log.error(f"❌ CRITICAL: Failed to create linking map path: {path_error}")
            return
        
        # 🔧 ATOMIC SAVE: Use Windows Save Guardian with alt-temp strategy
        self.log.info(f"🔧 ATOMIC SAVE: Attempting to save {len(self.linking_map)} entries using atomic strategy...")
        
        try:
            # 🚨 SENTINEL MONITORING: Track save attempt
            current_size = len(self.linking_map)
            save_success = False
            retry_count = 1
            
            # 🛡️ Use Windows Save Guardian with anti-truncation protection
            success = self.save_guardian.save_json_atomic(
                linking_map_path, 
                self.linking_map, 
                min_entries_guard=1000
            )
            
            if success:
                save_success = True
                self.log.info(f"✅ Successfully saved linking map with {len(self.linking_map)} entries to {linking_map_path}")
                
                # Verify the file was actually created and has content
                if linking_map_path.exists():
                    file_size = linking_map_path.stat().st_size
                    self.log.info(f"✅ VERIFICATION: File exists at {linking_map_path} with size {file_size} bytes")
                    
                    # 🚀 HASH OPTIMIZATION: Rebuild hash indexes after saving linking map
                    self.hash_optimizer.build_indexes(self.linking_map)
                    self.log.info(f"🚀 HASH INDEXES REBUILT: Updated indexes for {len(self.linking_map)} entries")
                    
                    # 🚨 SENTINEL MONITORING: Check for linking map shrinkage
                    self.sentinel_monitor.check_linking_map_shrinkage(current_size, previous_size)
                    self.sentinel_monitor.track_save_retry("windows_save_guardian", True, retry_count)
                else:
                    self.log.error(f"❌ CRITICAL: File was not created at {linking_map_path}")
                    self.sentinel_monitor.track_save_retry("windows_save_guardian", False, retry_count)
            else:
                self.log.error(f"❌ CRITICAL: Windows Save Guardian failed for {linking_map_path}")
                self.sentinel_monitor.track_save_retry("windows_save_guardian", False, retry_count)
                
        except Exception as e:
            self.log.error(f"❌ CRITICAL: Error in Windows Save Guardian: {e}", exc_info=True)
            self.sentinel_monitor.track_save_retry("windows_save_guardian", False, retry_count)

    def _classify_url(self, url: str) -> str:
        """return 'friendly' | 'avoid' | 'neutral' based on patterns (priority order)."""
        path = url.lower()
        for kws in FBA_FRIENDLY_PATTERNS.values():
            if any(k in path for k in kws):
                return "friendly"
        for kws in FBA_AVOID_PATTERNS.values():
            if any(k in path for k in kws):
                return "avoid"
        return "neutral"

    # ------------------------------------------------------------------
    def _save_category_manifest(self, supplier_name: str, category_url: str, urls: List[str]) -> str:
        """Persist the ground-truth list of product URLs for a category with atomic write using WindowsSaveGuardian."""
        from utils.normalization import normalize_url
        from utils.windows_save_guardian import WindowsSaveGuardian
        import re
        
        # Generate category slug for consistent naming
        slug = re.sub(r"[^a-z0-9]+", "-", category_url.lower()).strip("-")[:50]  # Limit length for filesystem
        manifest_dir = Path("OUTPUTS") / "manifests" / supplier_name
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / f"{slug}.json"
        
        # Normalize URLs for consistency
        normalized_urls = [normalize_url(u) for u in urls]
        
        # Check for existing manifest to detect overwrites
        overwritten = False
        prev_count = None
        if manifest_path.exists():
            try:
                prev_data = json.loads(manifest_path.read_text(encoding='utf-8'))
                prev_count = prev_data.get("count", 0)
                overwritten = True
            except Exception as e:
                self.log.warning(f"Could not read existing manifest for {category_url}: {e}")
        
        # Create manifest document with all required fields
        doc = {
            "category_url": category_url,
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "product_urls": normalized_urls,
            "count": len(normalized_urls),
            "supplier_name": supplier_name,
            "slug": slug
        }

    def _normalize_url_for_filtering(self, url):
        """Normalize URL specifically for duplicate detection in filtering pipeline"""
        if not url:
            return ""

        import re
        from urllib.parse import urlparse

        try:
            # Parse URL components
            parsed = urlparse(url)

            # Remove query parameters and fragments
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

            # Remove 'www.' prefix for consistency
            clean_url = re.sub(r'^(https?://)www\.', r'\1', clean_url)

            # Standardize case and remove trailing slash
            clean_url = clean_url.lower().rstrip('/')

            return clean_url

        except Exception as e:
            log.debug(f"URL normalization failed for '{url}': {e}")
            return url.lower().rstrip('/')  # Basic fallback
        
        # Use WindowsSaveGuardian for atomic write
        guardian = WindowsSaveGuardian()
        success = guardian.save_json_atomic(manifest_path, doc)
        
        if success:
            # Log manifest save with appropriate format
            self.log.info(f"📝 MANIFEST: {len(normalized_urls)} URLs → {manifest_path}")
            
            # Log manifest overwrite if applicable
            if overwritten and prev_count is not None:
                # Generate category index for logging (approximate from current processing state)
                category_index = getattr(self, '_current_category_index', 0)
                self.log.info(f"MANIFEST UPDATE[C{category_index} {slug}]: overwritten=true prev={prev_count} curr={len(normalized_urls)}")
                
                # Log count mismatch warning if significant difference
                if abs(prev_count - len(normalized_urls)) > 0:
                    self.log.warning(f"MANIFEST COUNT CHANGE: {category_url} changed from {prev_count} to {len(normalized_urls)} URLs")
            
            return str(manifest_path)
        else:
            self.log.error(f"❌ Failed to save manifest for {category_url}")
            raise RuntimeError(f"Failed to save category manifest: {manifest_path}")
    
    def _set_current_category_index(self, index: int):
        """Set current category index for manifest logging."""
        self._current_category_index = index
    
    def _generate_category_slug(self, category_url: str) -> str:
        """Generate readable slug from category URL path"""
        try:
            from urllib.parse import urlparse
            import re
            
            # Parse URL and extract path
            parsed = urlparse(category_url)
            path = parsed.path.strip('/')
            
            # Get the last meaningful part of the path
            if path:
                path_parts = path.split('/')
                # Take the last part, or second-to-last if last is very short
                if len(path_parts) > 1 and len(path_parts[-1]) < 5:
                    slug_base = path_parts[-2] if len(path_parts) > 1 else path_parts[-1]
                else:
                    slug_base = path_parts[-1]
            else:
                # Fallback to domain if no path
                slug_base = parsed.netloc.replace('www.', '').replace('.', '-')
            
            # Clean up the slug
            slug = re.sub(r'[^a-z0-9]+', '-', slug_base.lower()).strip('-')
            
            # Limit length and ensure it's not empty
            slug = slug[:30] if slug else 'unknown'
            
            return slug
            
        except Exception as e:
            self.log.warning(f"Failed to generate slug for {category_url}: {e}")
            return 'unknown'
    
    def _create_normalized_linking_entry(self, product_data: Dict[str, Any], amazon_data: Dict[str, Any], 
                                       confidence: str = "medium", search_method: str = "unknown") -> Dict[str, Any]:
        """Create a normalized linking map entry with consistent EAN and URL normalization."""
        from utils.normalization import normalize_url, normalize_ean
        
        # Extract and normalize EAN
        supplier_ean = product_data.get("ean") or product_data.get("barcode")
        if supplier_ean == "None" or supplier_ean is None:
            supplier_ean = None
        else:
            supplier_ean = normalize_ean(supplier_ean)
        
        # Extract and normalize URL
        supplier_url = product_data.get("url")
        if supplier_url:
            supplier_url = normalize_url(supplier_url)
        
        # Create normalized linking entry
        linking_entry = {
            "supplier_ean": supplier_ean,
            "supplier_url": supplier_url,
            "amazon_asin": amazon_data.get("asin"),
            "supplier_title": product_data.get("title"),
            "amazon_title": amazon_data.get("title"),
            "confidence": confidence,
            "search_method": search_method,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return linking_entry

    async def _collect_urls_only(self, category_url: str, max_products: int) -> List[str]:
        """Collect product URLs only without extracting product data"""
        try:
            # Use the scraper's URL collection method without product extraction
            all_product_urls = await self.supplier_scraper._collect_all_product_urls(category_url, max_products)

            # Store the discovered count for state manager integration
            self.supplier_scraper.last_discovered_count = len(all_product_urls)

            return all_product_urls
        except Exception as e:
            self.log.error(f"Failed to collect URLs from {category_url}: {e}")
            return []

    # Removed _scrape_with_retries_filtered method - confirmed broken and leads to extraction failures
    # Use _scrape_with_retries instead for successful product extraction per project memory
    
    def _load_cached_products_for_urls(self, urls: List[str], supplier_name: str) -> List[Dict[str, Any]]:
        """Load cached products for specific URLs that need Amazon analysis only"""
        try:
            # Load supplier cache
            actual_cache_file, _ = self._find_actual_supplier_cache_file(supplier_name)
            if not actual_cache_file:
                self.log.warning(f"No cache file found for {supplier_name}")
                return []
            
            with open(actual_cache_file, 'r', encoding='utf-8') as f:
                cached_products = json.load(f)
            
            # Filter to only products with URLs in the specified list
            matching_products = []
            for product in cached_products:
                if product.get('url') in urls:
                    matching_products.append(product)
            
            self.log.info(f"📋 CACHE LOAD: Found {len(matching_products)} cached products for {len(urls)} URLs")
            return matching_products
            
        except Exception as e:
            self.log.error(f"Failed to load cached products for URLs: {e}")
            return []

    async def _scrape_with_retries(self, url: str, max_products_per_category: int, product_accumulator: List[Dict[str, Any]]):
        """Wrapper around supplier scraper with exponential backoff retries."""
        from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
        import logging

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            before_sleep=before_sleep_log(self.log, logging.WARNING),
        )
        async def _inner():
            return await self.supplier_scraper.scrape_products_from_url(
                url, max_products_per_category, product_accumulator=product_accumulator
            )

        return await _inner()

    # ──────────────────────── ③  Enhanced State tracking helpers ──────────────────────
    def _load_history(self):
        """Load comprehensive scraping history to prevent duplicate processing"""
        if self.state_path and Path(self.state_path).exists(): # MODIFIED HERE
            try:
                history = json.loads(Path(self.state_path).read_text()) # AND HERE for consistency
                # Ensure all required keys exist with backward compatibility
                default_history = {
                    "categories_scraped": [],
                    "products_processed": [],
                    "pages_visited": [],
                    "subpages_scraped": [],
                    "ai_suggested_categories": [],
                    "failed_categories": [],
                    "last_scrape_timestamp": None,
                    "scrape_sessions": [],
                    "category_performance": {},
                    "url_hash_cache": {},
                    "ai_decision_history": []  # New field for AI decisions
                }
                # Merge with defaults to handle missing keys
                for key, default_value in default_history.items():
                    if key not in history:
                        history[key] = default_value
                return history
            except (json.JSONDecodeError, Exception) as e:
                log.warning(f"Failed to load history, creating new: {e}")
                return self._get_default_history()
        return self._get_default_history()

    def _load_ai_memory(self, supplier_name: str) -> Dict[str, Any]:
        """
        🧠 Load AI memory from AI cache file to prevent re-suggesting same categories.

        Args:
            supplier_name: Name of the supplier

        Returns:
            Dictionary containing AI memory data
        """
        try:
            ai_cache_file = os.path.join(AI_CATEGORY_CACHE_DIR, f"{supplier_name.replace('.', '_')}_ai_category_cache.json")

            if os.path.exists(ai_cache_file):
                with open(ai_cache_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content or content == "{}":  # File is empty or just empty JSON
                        log.info(f"🧠 AI cache file is empty for {supplier_name} - starting fresh")
                        # Don't raise error - return empty memory but let the system continue
                        return {
                            "previously_suggested_urls": [],
                            "total_products_processed": 0,
                            "ai_history": [],
                            "total_ai_calls": 0,
                            "price_phase": "low"
                        }
                    ai_cache_data = json.loads(content)

                # Extract all previously suggested URLs from AI history
                previously_suggested_urls = set()
                total_products_processed = 0

                ai_history = ai_cache_data.get("ai_suggestion_history", [])
                for entry in ai_history:
                    ai_suggestions = entry.get("ai_suggestions", {})

                    # Collect all suggested URLs
                    top_urls = ai_suggestions.get("top_3_urls", [])
                    secondary_urls = ai_suggestions.get("secondary_urls", [])

                    previously_suggested_urls.update(top_urls)
                    previously_suggested_urls.update(secondary_urls)

                    # Track products processed
                    session_context = entry.get("session_context", {})
                    total_products_processed += session_context.get("total_products_processed", 0)

                log.info(f"🧠 AI Memory loaded: {len(previously_suggested_urls)} previously suggested URLs, {total_products_processed} products processed")
                log.debug(f"🧠 Previously suggested URLs: {list(previously_suggested_urls)}")

                return {
                    "previously_suggested_urls": list(previously_suggested_urls),
                    "total_products_processed": total_products_processed,
                    "ai_history": ai_history,
                    "total_ai_calls": ai_cache_data.get("total_ai_calls", 0),
                    "price_phase": ai_cache_data.get("price_phase", "low")  # Default to Phase 1
                }
            else:
                log.info(f"🧠 No AI cache file found for {supplier_name} - starting fresh")

        except Exception as e:
            log.error(f"Error loading AI memory for {supplier_name}: {e}")

        # Return default empty memory
        return {
            "previously_suggested_urls": [],
            "total_products_processed": 0,
            "ai_history": [],
            "total_ai_calls": 0,
            "price_phase": "low"  # Default to Phase 1
        }

    def _get_default_history(self):
        """Get default history structure"""
        return {
            "categories_scraped": [],
            "products_processed": [],
            "pages_visited": [],
            "subpages_scraped": [],
            "ai_suggested_categories": [],
            "failed_categories": [],
            "last_scrape_timestamp": None,
            "scrape_sessions": [],
            "category_performance": {},
            "url_hash_cache": {},
            "ai_decision_history": []  # New field for AI decisions
        }

    async def _get_predefined_categories(self, supplier_name: str) -> list:
        """Load predefined category URLs from a custom JSON file."""
        log.info(f"Attempting to load predefined categories for {supplier_name}")
        try:
            # Robust path construction using pathlib
            config_path = Path(__file__).parent.parent / "config" / f"{supplier_name.replace('.co.uk', '')}_categories.json"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    category_urls = data.get("category_urls", [])
                    log.info(f"✅ Successfully loaded {len(category_urls)} predefined category URLs from {config_path}")
                    return category_urls
            else:
                log.warning(f"⚠️ Predefined category file not found at {config_path}")
                return []
        except FileNotFoundError:
            log.error(f"❌ Configuration file not found: {config_path}")
            return []
        except json.JSONDecodeError as e:
            log.error(f"❌ Invalid JSON in configuration file: {e}")
            return []
        except Exception as e:
            log.error(f"❌ Unexpected error loading predefined categories: {e}")
            return []

    def _save_history(self, hist: dict):
        """Save comprehensive scraping history with atomic write"""
        if self.state_path:
            # Add current timestamp
            hist["last_scrape_timestamp"] = datetime.now().isoformat()
            
            # Use atomic write to prevent corruption
            # Ensure self.state_path is a Path object for .with_suffix and os.replace
            state_path_obj = Path(self.state_path)
            temp_path = state_path_obj.with_suffix(".tmp")
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(hist, f, indent=2, ensure_ascii=False)
                os.replace(temp_path, state_path_obj) # Use Path object here too
                log.debug(f"History saved with {len(hist.get('categories_scraped', []))} categories, {len(hist.get('pages_visited', []))} pages")
            except Exception as e:
                log.error(f"Failed to save history: {e}")
                if os.path.exists(temp_path): # os.path.exists is fine for string or Path
                    try:
                        os.remove(temp_path)
                    except:
                        pass

    def _record_ai_decision(self, hist: dict, ai_response: dict):
        """Record AI decision for future reference and learning"""
        hist.setdefault("ai_decision_history", []).append({
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "categories_suggested": ai_response["top_3_urls"],
            "skip_urls": ai_response["skip_urls"],
            "reasoning": ai_response.get("detailed_reasoning", {}),
            "progression_strategy": ai_response.get("progression_strategy", "unknown")
        })
        # DEPRECATED: Replaced by EnhancedStateManager to prevent state conflicts
        # self._save_history(hist)

    def _is_url_previously_scraped(self, url: str, hist: dict) -> bool:
        """Check if URL has been previously scraped using multiple tracking methods"""
        if not url:
            return False
            
        # Direct URL check
        if url in hist.get("categories_scraped", []):
            return True
        if url in hist.get("pages_visited", []):
            return True
        if url in hist.get("subpages_scraped", []):
            return True
            
        # URL hash check for similar URLs (handles pagination, query params)
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in hist.get("url_hash_cache", {}):
            cached_url = hist["url_hash_cache"][url_hash]
            log.debug(f"URL hash match found: {url} matches previously scraped {cached_url}")
            return True
            
        # Normalize URL and check (remove trailing slashes, query params for base comparison)
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        
        for scraped_url in hist.get("categories_scraped", []) + hist.get("pages_visited", []):
            scraped_parsed = urlparse(scraped_url)
            scraped_base = f"{scraped_parsed.scheme}://{scraped_parsed.netloc}{scraped_parsed.path.rstrip('/')}"
            if base_url == scraped_base:
                log.debug(f"Base URL match: {url} matches {scraped_url}")
                return True
                
        return False

    def _add_url_to_history(self, url: str, hist: dict, url_type: str = "page"):
        """Add URL to appropriate history list and hash cache"""
        if not url:
            return
            
        # Add to appropriate list
        if url_type == "category":
            if url not in hist.get("categories_scraped", []):
                hist.setdefault("categories_scraped", []).append(url)
        elif url_type == "subpage":
            if url not in hist.get("subpages_scraped", []):
                hist.setdefault("subpages_scraped", []).append(url)
        else:  # default to pages_visited
            if url not in hist.get("pages_visited", []):
                hist.setdefault("pages_visited", []).append(url)
        
        # Add to hash cache
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        hist.setdefault("url_hash_cache", {})[url_hash] = url
        
        log.debug(f"Added {url_type} URL to history: {url}")

    def _record_category_performance(self, category_url: str, products_found: int, hist: dict):
        """Record performance metrics for categories to improve future AI suggestions"""
        hist.setdefault("category_performance", {})[category_url] = {
            "products_found": products_found,
            "last_scraped": datetime.now().isoformat(),
            "performance_score": min(products_found / 10.0, 1.0)  # Normalize to 0-1 scale
        }

    def _get_category_performance_summary(self, hist: dict) -> str:
        """Get summary of category performance for AI context"""
        performance = hist.get("category_performance", {})
        if not performance:
            return "No previous category performance data available."
        
        summary_lines = ["Previous category performance:"]
        sorted_categories = sorted(performance.items(), key=lambda x: x[1]["performance_score"], reverse=True)
        
        for url, metrics in sorted_categories[:5]:  # Top 5 performing categories
            summary_lines.append(f"- {url}: {metrics['products_found']} products (score: {metrics['performance_score']:.2f})")
        
        if len(sorted_categories) > 5:
            summary_lines.append(f"... and {len(sorted_categories) - 5} more categories")
            
        return "\n".join(summary_lines)

    # ──────────────────────── PHASE 3: SUBCATEGORY DEDUPLICATION ──────────────────────────
    def _detect_parent_child_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        Detect parent-child URL relationships to prevent double processing.
        Returns dict where keys are parent URLs and values are lists of child URLs.
        
        Example:
        Input: ['/health-beauty.html', '/health-beauty/cosmetics.html', '/gifts-toys.html']
        Output: {'/health-beauty.html': ['/health-beauty/cosmetics.html'], '/gifts-toys.html': []}
        """
        from urllib.parse import urlparse
        
        parent_child_map = {}
        processed_urls = set()
        
        # Sort URLs by path depth (shorter paths first)
        sorted_urls = sorted(urls, key=lambda url: urlparse(url).path.count('/'))
        
        for url in sorted_urls:
            if url in processed_urls:
                continue
                
            parsed_url = urlparse(url)
            url_path = parsed_url.path.rstrip('/')
            
            # Find potential child URLs
            child_urls = []
            for other_url in sorted_urls:
                if other_url == url or other_url in processed_urls:
                    continue
                    
                other_parsed = urlparse(other_url)
                other_path = other_parsed.path.rstrip('/')
                
                # Check if other_url is a child of current url
                # Child URL should start with parent path + '/'
                if other_path.startswith(url_path + '/') and other_path != url_path:
                    # Additional validation: ensure it's direct child, not grandchild
                    remaining_path = other_path[len(url_path + '/'):]
                    if '/' not in remaining_path or remaining_path.count('/') <= 1:
                        child_urls.append(other_url)
                        processed_urls.add(other_url)
            
            parent_child_map[url] = child_urls
            processed_urls.add(url)
            
        log.info(f"Parent-child URL analysis: {len(parent_child_map)} parent categories, "
                f"{sum(len(children) for children in parent_child_map.values())} child categories")
        
        return parent_child_map

    async def _filter_urls_by_subcategory_deduplication(self, category_urls: List[str]) -> List[str]:
        """
        Apply subcategory deduplication logic: only include subcategories if parent category has <2 products.
        
        This prevents double processing of URLs like:
        - /health-beauty.html AND /health-beauty/cosmetics.html
        - /gifts-toys.html AND /gifts-toys/toys-games.html
        """
        if not category_urls:
            return category_urls
            
        # Detect parent-child relationships
        parent_child_map = self._detect_parent_child_urls(category_urls)
        
        # Validate each parent category for product count
        filtered_urls = []
        validation_cache = {}  # Cache validation results to avoid duplicate checks
        
        for parent_url, child_urls in parent_child_map.items():
            # Check parent category product count (use cache if available)
            if parent_url not in validation_cache:
                validation_result = await self._validate_category_productivity(parent_url)
                validation_cache[parent_url] = validation_result
            else:
                validation_result = validation_cache[parent_url]
            
            parent_product_count = validation_result.get("product_count", 0)
            
            # CORE LOGIC: Apply subcategory deduplication rule
            if parent_product_count >= 2:
                # Parent has sufficient products - skip subcategories, use pagination only
                filtered_urls.append(parent_url)
                log.info(f"✅ PARENT CATEGORY SUFFICIENT: {parent_url} ({parent_product_count} products) "
                        f"- SKIPPING {len(child_urls)} subcategories: {child_urls}")
            else:
                # Parent has <2 products - include subcategories for more products
                filtered_urls.append(parent_url)
                filtered_urls.extend(child_urls)
                log.info(f"⚠️  PARENT CATEGORY INSUFFICIENT: {parent_url} ({parent_product_count} products) "
                        f"- INCLUDING {len(child_urls)} subcategories: {child_urls}")
        
        log.info(f"SUBCATEGORY DEDUPLICATION: Reduced {len(category_urls)} URLs to {len(filtered_urls)} "
                f"(eliminated {len(category_urls) - len(filtered_urls)} redundant subcategories)")
        
        return filtered_urls

    # ──────────────────────── ②  Enhanced AI method ──────────────────────────
    async def _get_ai_suggested_categories_enhanced(
        self,
        supplier_url: str,
        supplier_name: str,
        discovered_categories: list[dict],
        previous_categories: list[str] | None = None,
        processed_products: int | None = None,
    ) -> dict:
        """🧠 FBA-aware AI selection with UK business intelligence & enhanced memory."""
        prev_cats = previous_categories or []

        # 🧠 ENHANCED: Filter out previously suggested categories more thoroughly
        available_categories = []
        for c in discovered_categories:
            if (
                self._classify_url(c["url"]) == "friendly" and
                c["url"] not in prev_cats and
                not any(prev_url in c["url"] or c["url"] in prev_url for prev_url in prev_cats)
            ):
                available_categories.append(c)

        # Limit to reasonable number for AI processing
        category_limit = self.system_config.get("ai_features", {}).get("category_selection", {}).get("max_categories_per_request", 3)
        friendly = available_categories[:category_limit]
        formatted = "\n".join(f'- {c["name"]}: {c["url"]}' for c in friendly)

        # 🧠 ENHANCED: Include comprehensive memory context with failure tracking
        memory_context = ""
        if prev_cats:
            memory_context = f"\n\n🧠 IMPORTANT - PREVIOUSLY SUGGESTED CATEGORIES (DO NOT REPEAT):\n"
            for i, prev_cat in enumerate(prev_cats[-10:], 1):  # Show last 10 to avoid token limit
                memory_context += f"{i}. {prev_cat}\n"
            memory_context += "\n⚠️ You MUST suggest DIFFERENT categories that have NOT been suggested before!"

        # Add failure tracking from AI memory
        ai_memory = self._load_ai_memory(supplier_name)
        failed_urls = []
        failed_errors = {}

        # Extract failed URLs from AI history
        for entry in ai_memory.get("ai_history", []):
            if isinstance(entry, dict) and "ai_suggestions" in entry:
                suggestions = entry["ai_suggestions"]
                if "failed_urls" in suggestions:
                    failed_urls.extend(suggestions["failed_urls"])
                if "failed_url_errors" in suggestions:
                    failed_errors.update(suggestions["failed_url_errors"])

        # Add failure context to prompt
        if failed_urls:
            memory_context += f"\n\n❌ FAILED CATEGORIES (DO NOT SUGGEST THESE):\n"
            for i, failed_url in enumerate(set(failed_urls[-15:]), 1):  # Show last 15 failures
                error_msg = failed_errors.get(failed_url, "Unknown error")
                memory_context += f"{i}. {failed_url} (Error: {error_msg})\n"
            memory_context += "\n⚠️ These URLs failed validation - DO NOT suggest them again!"
        prompt = f"""
AMAZON FBA UK CATEGORY ANALYSIS FOR: {supplier_name}

You are an expert Amazon FBA consultant specializing in UK marketplace product sourcing and category analysis.

DISCOVERED CATEGORIES FROM WEBSITE HOMEPAGE:
{formatted}

{memory_context}

PREVIOUSLY PROCESSED CATEGORIES: {prev_cats or "None"}
PREVIOUSLY PROCESSED PRODUCTS: {processed_products or "None"}

🚨 CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. **YOU MUST ONLY SELECT URLs FROM THE "DISCOVERED CATEGORIES" LIST ABOVE**
2. **DO NOT INVENT OR CREATE NEW URLs - ONLY USE THE PROVIDED ONES**
3. **DO NOT SUGGEST URLs THAT ARE NOT IN THE DISCOVERED CATEGORIES LIST**
4. ONLY select URLs that appear to be PRODUCT LISTING PAGES, not search forms or filters
5. Avoid URLs containing: "search", "advanced", "filter", "sort", "login", "account"
6. Prioritize URLs with clear category names that suggest product listings
7. Avoid URLs that look like individual product pages (containing specific product names)

URL SELECTION RULES:
- **ONLY SELECT FROM THE DISCOVERED CATEGORIES LIST ABOVE**
- **DO NOT CREATE NEW URLs OR MODIFY EXISTING ONES**
- GOOD patterns from the list: URLs ending in category names like "/household.html", "/baby-kids.html"
- BAD patterns from the list: URLs containing "search", "advanced", "filter", "catalogsearch"

Based on your FBA expertise, select categories from the DISCOVERED CATEGORIES list that are most likely to contain profitable, scrapeable products for Amazon FBA UK.

⚠️ **IMPORTANT: ALL URLs in your response MUST come from the DISCOVERED CATEGORIES list above. Do not invent new URLs.**

Return a JSON object with EXACTLY these keys:
{{
    "top_3_urls": [list of 3 best PRODUCT LISTING category URLs],
    "secondary_urls": [list of 3-5 backup category URLs],
    "skip_urls": [list of category URLs to avoid - include search/filter pages],
    "detailed_reasoning": {{\"category_name\": \"detailed reason for selection/skipping including URL pattern analysis\"}},
    "progression_strategy": "description of your category selection strategy focusing on product listing identification",
    "url_pattern_confidence": {{\"high_confidence\": [\"urls you're very confident contain products\"], \"medium_confidence\": [\"urls that might contain products\"], \"low_confidence\": [\"urls unlikely to contain products\"]}}
}}

PRIORITIZE CATEGORIES LIKELY TO CONTAIN:
HIGH PRIORITY:
- Home & Kitchen products (high profit margins, consistent demand)
- Pet Supplies (growing market, good margins)
- Beauty & Personal Care (repeat purchases, brand loyalty)
- Sports & Outdoors (seasonal opportunities)
- Office & Stationery (business demand)
- DIY & Tools (practical demand)
- Baby & Nursery products (premium pricing potential)
- Toys & Games (consistent demand)
- Kids Books (coloring books, sticker books, activity books, picture books)

MEDIUM PRIORITY:
- Clearance/Value categories (pound lines, 50p & under, clearance, sale, discount)
- Crafts & Hobbies (creative supplies, art materials)
- Seasonal items (Christmas, Halloween, party supplies)
- Automotive accessories (small car accessories)

AVOID CATEGORIES WITH:
- Electronics (high competition, warranty issues)
- Clothing/Fashion (size/fit issues, returns)
- Medical/Pharmaceutical (regulatory restrictions)
- Food/Beverages (expiry dates, regulations)
- Large/bulky items (shipping costs, storage issues)
- High-value jewelry (authentication, insurance)
- Dangerous goods (batteries, flammables, restricted)
- Adult Books (novels, fiction, textbooks, academic books - AVOID these)
- Search/filter pages (no actual products)

IMPORTANT BOOK DISTINCTION:
- INCLUDE: Kids books, coloring books, sticker books, activity books, picture books
- EXCLUDE: Adult novels, fiction, textbooks, academic books, biographies

REASONING REQUIREMENTS:
For each selected URL, explain:
1. Why the URL pattern suggests it contains product listings
2. What type of products you expect to find
3. Why those products are suitable for FBA
4. Estimated profit potential (High/Medium/Low)

Return ONLY valid JSON, no additional text."""
        # ---------- AI CALL ----------
        # 🔧 FIXED: Use regular model since search-enabled model doesn't support json_object format
        model_to_use = "gpt-4.1-mini-2025-04-14"  # Use gpt-4.1-mini for consistency

        # Log API call details for debugging
        log.info(f"🤖 OpenAI API Call - Model: {model_to_use}, Max Tokens: 1200")
        log.info(f"🤖 Prompt Length: {len(prompt)} characters")
        log.debug(f"🤖 Full Prompt: {prompt[:500]}..." if len(prompt) > 500 else f"🤖 Full Prompt: {prompt}")

        raw = await asyncio.to_thread(
            self.ai_client.chat.completions.create,
            model=model_to_use,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=1200,  # Increased for better reasoning
        )

        # Log token usage
        if hasattr(raw, 'usage') and raw.usage:
            log.info(f"🤖 Token Usage - Input: {raw.usage.prompt_tokens}, Output: {raw.usage.completion_tokens}, Total: {raw.usage.total_tokens}")

        # Save detailed API call log
        self._save_api_call_log(prompt, raw, model_to_use, "category_suggestion")

        # ---------- STRICT VALIDATION ----------
        try:
            ai = json.loads(raw.choices[0].message.content.strip())
            # Fix: Add missing keys with default values instead of failing
            required = {"top_3_urls", "secondary_urls", "skip_urls"}
            if not required.issubset(ai):
                self.log.warning(f"AI JSON missing keys: {required - set(ai)} - adding defaults")
                # Add missing keys with defaults
                if "top_3_urls" not in ai:
                    ai["top_3_urls"] = [c["url"] for c in discovered_categories
                                      if self._classify_url(c["url"]) == "friendly"
                                      and c["url"] not in (previous_categories or [])][:3]
                if "secondary_urls" not in ai:
                    ai["secondary_urls"] = []
                if "skip_urls" not in ai:
                    ai["skip_urls"] = []
            
            # Ensure lists are actually lists
            for key in ["top_3_urls", "secondary_urls", "skip_urls"]:
                if not isinstance(ai[key], list):
                    self.log.warning(f"AI JSON '{key}' is not a list - fixing")
                    ai[key] = [ai[key]] if ai[key] else []
                    
        except Exception as e:
            self.log.error("AI JSON invalid → %s – falling back to heuristic list", e)
            friendly_urls = [c["url"] for c in discovered_categories
                             if self._classify_url(c["url"]) == "friendly"
                             and c["url"] not in (previous_categories or [])][:3]
            ai = {"top_3_urls": friendly_urls,
                  "secondary_urls": [],
                  "skip_urls": [],
                  "detailed_reasoning": {"fallback": "heuristic-friendly"},
                  "progression_strategy": "simple-first-3"}

        # hard filter avoid patterns
        ai["top_3_urls"] = [u for u in ai["top_3_urls"] if self._classify_url(u) != "avoid"]
        ai["skip_urls"]  = list(set(ai.get("skip_urls",[]) + [u for u in ai["top_3_urls"] if self._classify_url(u)=="avoid"]))
        return ai

    async def _validate_category_productivity(self, url: str) -> dict:
        """Check if category URL actually contains products (Solution 3)"""
        try:
            log.info(f"Validating category productivity for: {url}")

            # Quick scrape to count products on first page
            session = await self.web_scraper._get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    return {
                        "url": url,
                        "product_count": 0,
                        "is_productive": False,
                        "error": f"HTTP {response.status}"
                    }

                html_content = await response.text()

            # Use the same product detection logic as the scraper
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Try configured selectors first
            product_elements = []
            try:
                supplier_config = self.web_scraper.get_supplier_config(url)
                if supplier_config and supplier_config.get("selectors", {}).get("product_container"):
                    product_selector = supplier_config["selectors"]["product_container"]
                    product_elements = soup.select(product_selector)
            except Exception as e:
                log.debug(f"Failed to use configured selectors for {url}: {e}")

            # Fallback to generic selectors if no configured ones work
            if not product_elements:
                generic_selectors = [
                    'div.product',
                    '.product-item',
                    '.product-container',
                    '[class*="product"]',
                    '.item'
                ]
                for selector in generic_selectors:
                    product_elements = soup.select(selector)
                    if product_elements:
                        break

            product_count = len(product_elements)
            is_productive = product_count >= 2  # Minimum 2 products required

            log.info(f"Category validation: {url} -> {product_count} products (productive: {is_productive})")

            return {
                "url": url,
                "product_count": product_count,
                "is_productive": is_productive,
                "validation_method": "product_count_check"
            }

        except Exception as e:
            log.warning(f"Category productivity validation failed for {url}: {e}")
            return {
                "url": url,
                "product_count": 0,
                "is_productive": False,
                "error": str(e)
            }

    def _optimize_category_urls(self, urls: list, price_range: str = "low") -> list:
        """DEPRECATED: URL optimization is now handled by supplier-specific extraction scripts"""
        optimized_urls = []

        for url in urls:
            # Base parameters for better product retrieval (generic, no price filtering)
            # ❌ COMMENTED OUT - hardcoded for different website, not compatible with poundwholesale.co.uk
            # base_params = "product_list_limit=64&product_list_order=price&product_list_dir=asc"

            # Add parameters to URL
            # ❌ COMMENTED OUT - using raw URLs for poundwholesale.co.uk compatibility
            # if '?' in url:
            #     optimized_url = f"{url}&{base_params}"
            # else:
            #     optimized_url = f"{url}?{base_params}"

            # ✅ USE RAW URL for poundwholesale.co.uk
            optimized_url = url
            optimized_urls.append(optimized_url)
            log.info(f"Using raw URL (poundwholesale.co.uk): {url}")

        return optimized_urls

    def _save_api_call_log(self, prompt: str, response, model: str, call_type: str):
        """Save detailed OpenAI API call logs for debugging and token tracking"""
        try:
            from pathlib import Path

            # Create API logs directory using proper path management (claude.md standards)
            from utils.path_manager import get_api_log_path
            log_file = get_api_log_path("openai")  # This creates the proper path

            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "call_type": call_type,
                "model": model,
                "prompt_length": len(prompt),
                "prompt": prompt,
                "response_content": response.choices[0].message.content if response.choices else "No response",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') and response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') and response.usage else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
                }
            }

            # Save to daily log file (already created by get_api_log_path)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

            log.info(f"💾 API call logged to {log_file}")

        except Exception as e:
            log.warning(f"Failed to save API call log: {e}")

    def _determine_price_phase(self, ai_memory: dict) -> str:
        """Determine current price phase based on AI memory"""
        # Check if Phase 2 has been initiated
        if ai_memory.get("price_phase") == "medium":
            return "medium"

        # Default to Phase 1 (low price range)
        return "low"

    def _store_phase_2_continuation_point(self, category_url: str, page_num: int, products_scraped: int):
        """Store pagination state for Phase 2 continuation"""
        try:
            from utils.path_manager import get_phase_continuation_path

            # Create continuation points file using path_manager (claude.md standards)
            continuation_file = get_phase_continuation_path()
            continuation_file.parent.mkdir(parents=True, exist_ok=True)

            # Load existing continuation points
            continuation_data = {}
            if continuation_file.exists():
                try:
                    with open(continuation_file, 'r', encoding='utf-8') as f:
                        continuation_data = json.load(f)
                except Exception as e:
                    log.warning(f"Could not load continuation points: {e}")

            # Store continuation point for this category
            base_url = category_url.split('?')[0]  # Remove any existing parameters
            continuation_data[base_url] = {
                "last_page": page_num,
                "products_scraped": products_scraped,
                "timestamp": datetime.now().isoformat(),
                "phase_1_complete": True
            }

            # Save updated continuation points using atomic save
            success = self.save_guardian.save_json_atomic(continuation_file, continuation_data)
            if not success:
                self.log.error(f"❌ Failed to save continuation data to {continuation_file}")

            log.info(f"📍 Stored Phase 2 continuation point for {base_url}: page {page_num}, {products_scraped} products")

        except Exception as e:
            log.error(f"Failed to store Phase 2 continuation point: {e}")

    def _reset_ai_memory_for_phase_2(self, supplier_name: str, current_memory: dict):
        """Reset AI memory for Phase 2 while preserving Phase 1 history"""
        try:
            from pathlib import Path

            cache_file_path = Path(AI_CATEGORY_CACHE_DIR) / f"{supplier_name.replace('.', '_')}_ai_category_cache.json"

            if cache_file_path.exists():
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # Add Phase 2 marker to cache
                phase_2_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "phase_transition": f"Phase 1 (£{self.min_price}-£{self.price_midpoint}) complete, starting Phase 2 (£{self.price_midpoint}-£{MAX_PRICE})",
                    "phase_1_summary": {
                        "total_categories_processed": len(current_memory.get("previously_suggested_urls", [])),
                        "total_products_processed": current_memory.get("total_products_processed", 0)
                    }
                }

                cache_data["ai_suggestion_history"].append(phase_2_entry)
                cache_data["last_updated"] = datetime.now().isoformat()
                cache_data["price_phase"] = "medium"  # Mark as Phase 2

                # Reset category suggestions for Phase 2 but keep history
                cache_data["phase_2_started"] = datetime.now().isoformat()

                with open(cache_file_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)

                log.info(f"🔄 Phase 2 transition recorded in AI cache: {cache_file_path}")

        except Exception as e:
            log.error(f"Failed to reset AI memory for Phase 2: {e}")

    # COMMENTED OUT: Perplexity API integration for future use
    # async def _get_category_suggestions_with_perplexity(self, supplier_url: str) -> dict:
    #     """Use Perplexity API for enhanced category research"""
    #     try:
    #         import httpx
    #
    #         perplexity_api_key = "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"
    #
    #         prompt = f"""
    #         Research the website {supplier_url} and identify the best product categories
    #         for Amazon FBA sourcing. Focus on categories with:
    #         - Small, lightweight products
    #         - Good profit margins
    #         - Consistent demand
    #         - Low competition
    #
    #         Avoid categories with electronics, clothing, food, or dangerous goods.
    #         Return specific category URLs if possible.
    #         """
    #
    #         async with httpx.AsyncClient() as client:
    #             response = await client.post(
    #                 "https://api.perplexity.ai/chat/completions",
    #                 headers={
    #                     "Authorization": f"Bearer {perplexity_api_key}",
    #                     "Content-Type": "application/json"
    #                 },
    #                 json={
    #                     "model": "sonar-small-online",  # Lightweight, cost-effective
    #                     "messages": [{"role": "user", "content": prompt}],
    #                     "max_tokens": 500,
    #                     "temperature": 0.1
    #                 }
    #             )
    #
    #             if response.status_code == 200:
    #                 result = response.json()
    #                 return {"perplexity_research": result["choices"][0]["message"]["content"]}
    #             else:
    #                 log.warning(f"Perplexity API error: {response.status_code}")
    #                 return {"error": "Perplexity API failed"}
    #
    #     except Exception as e:
    #         log.warning(f"Perplexity integration failed: {e}")
    #         return {"error": str(e)}

    def _classify_category_type(self, url: str, name: str = "") -> str:
        """Classify category as friendly, avoid, or neutral for FBA"""
        url_lower = url.lower()
        name_lower = name.lower()
        combined_text = f"{url_lower} {name_lower}"

        # Check FBA friendly patterns
        for category_type, keywords in FBA_FRIENDLY_PATTERNS.items():
            if any(keyword in combined_text for keyword in keywords):
                return "friendly"

        # Check FBA avoid patterns
        for category_type, keywords in FBA_AVOID_PATTERNS.items():
            if any(keyword in combined_text for keyword in keywords):
                return "avoid"

        # Check neutral patterns
        for category_type, keywords in FBA_NEUTRAL_PATTERNS.items():
            if any(keyword in combined_text for keyword in keywords):
                return "neutral"

        return "unknown"

    def _save_products_to_cache(self, products: list, cache_file_path: str):
        """Save products to cache file with atomic deduplication and deterministic filtering."""
        try:
            # --- PATH CORRECTION FIX V5 ---
            # Use pathlib for robust, cross-platform path handling.
            path_obj = Path(str(cache_file_path))
            self.log.info(f"🔍 DEBUG: Initial path object: {path_obj}")
            self.log.info(f"🔍 DEBUG: Path is absolute: {path_obj.is_absolute()}")
            self.log.info(f"🔍 DEBUG: Path as_posix: {path_obj.as_posix()}")

            # 🚨 CRITICAL FIX: Windows native path handling
            original_path = str(path_obj)
            
            # Use standard Windows path handling
            directory = path_obj.parent
            directory.mkdir(parents=True, exist_ok=True)
            final_path = str(path_obj)
            self.log.info(f"✅ Cache directory ensured: {directory}")

            # Get cache control configuration
            cache_config = self.system_config.get("supplier_cache_control", {})
            if cache_config.get("enabled", True):
                self.log.info(f"💾 CACHE SAVE: Starting save of {len(products)} products to cache...")
                
            self.log.info(f"🔍 DEBUG: Final path for file operations: {final_path}")

            # 🚨 ATOMIC FIX 1: Atomic read-modify-write operation
            # Use Windows Save Guardian for atomic operations with file locking
            def atomic_cache_operation():
                existing_products = []
                if os.path.exists(final_path):
                    try:
                        with open(final_path, 'r', encoding='utf-8') as f:
                            existing_products = json.load(f)
                        self.log.info(f"🔍 ATOMIC: Loaded {len(existing_products)} existing products for deduplication")
                    except Exception as e:
                        self.log.warning(f"Could not load existing cache for deduplication: {e}")

                # 🚨 ATOMIC FIX 2: Deterministic deduplication with URL normalization
                existing_urls = set()
                existing_eans = set()
                
                for p in existing_products:
                    url = p.get('url', '').strip().lower()  # Normalize URLs
                    ean = p.get('ean', '')
                    
                    if url:
                        existing_urls.add(url)
                    if ean and ean != 'None' and ean.strip():
                        existing_eans.add(ean.strip())

                new_products = []
                ean_duplicates_skipped = 0
                url_duplicates_skipped = 0
                scanned = 0

                for p in products:
                    # 🚨 ATOMIC FIX 3: Consistent URL normalization for comparison
                    product_url = p.get('url', '').strip().lower()
                    product_ean = p.get('ean', '').strip() if p.get('ean') else ''
                    scanned += 1

                    # Reduced logging: only periodic debug updates during scan
                    if self.log.isEnabledFor(logging.DEBUG) and scanned % 100 == 0:
                        self.log.debug(f"🔍 DEDUP SCAN: scanned={scanned} url_dupes={url_duplicates_skipped} ean_dupes={ean_duplicates_skipped}")
                    
                    if product_url and product_url in existing_urls:
                        url_duplicates_skipped += 1
                        continue

                    if product_ean and product_ean != 'None' and product_ean in existing_eans:
                        ean_duplicates_skipped += 1
                        continue

                    new_products.append(p)
                    if product_url:
                        existing_urls.add(product_url)
                    if product_ean and product_ean != 'None':
                        existing_eans.add(product_ean)

                if url_duplicates_skipped > 0 or ean_duplicates_skipped > 0:
                    self.log.info(f"🔄 ATOMIC DEDUPLICATION: Skipped {url_duplicates_skipped} URL duplicates and {ean_duplicates_skipped} EAN duplicates.")

                # 🚨 ATOMIC FIX 4: Log deduplication results for debugging
                self.log.info(f"🔍 ATOMIC RESULT: {len(existing_products)} existing + {len(new_products)} new = {len(existing_products) + len(new_products)} total")
                
                return existing_products + new_products, len(new_products)

            # 🚨 ATOMIC FIX 5: Execute atomic operation and use Windows Save Guardian
            all_products, new_count = atomic_cache_operation()
            
            # Use Windows Save Guardian for atomic write with file locking
            success = self.save_guardian.save_json_atomic(final_path, all_products)
            
            if success:
                file_size = os.path.getsize(final_path)
                self.log.info(f"✅ ATOMICALLY saved {len(all_products)} products ({new_count} new) to cache: {os.path.basename(final_path)} (size: {file_size} bytes)")
                
                # 🚨 ATOMIC FIX 6: Update in-memory cache to match disk state
                if hasattr(self, '_current_all_products'):
                    self._current_all_products = all_products.copy()
                    self.log.debug(f"🔄 SYNC: In-memory cache synchronized with disk cache ({len(all_products)} products)")
                    
                return new_count  # Return count of new products added
            else:
                self.log.error(f"❌ ATOMIC SAVE FAILED: Windows Save Guardian failed to save cache")
                raise RuntimeError(f"Atomic cache save failed: {final_path}")

        except Exception as e:
            self.log.error(f"❌ An unexpected error occurred during atomic cache save: {e}", exc_info=True)
            return 0

    def _check_category_exhaustion_status(self, discovered_categories: list, processed_categories: list) -> dict:
        """Check how many categories of each type remain to be processed"""
        friendly_total = 0
        friendly_processed = 0
        neutral_total = 0
        neutral_processed = 0

        for category in discovered_categories:
            category_type = self._classify_category_type(category["url"], category.get("name", ""))
            if category_type == "friendly":
                friendly_total += 1
                if category["url"] in processed_categories:
                    friendly_processed += 1
            elif category_type == "neutral":
                neutral_total += 1
                if category["url"] in processed_categories:
                    neutral_processed += 1

        friendly_remaining = friendly_total - friendly_processed
        neutral_remaining = neutral_total - neutral_processed

        return {
            "friendly_total": friendly_total,
            "friendly_processed": friendly_processed,
            "friendly_remaining": friendly_remaining,
            "neutral_total": neutral_total,
            "neutral_processed": neutral_processed,
            "neutral_remaining": neutral_remaining,
            "should_continue": friendly_remaining > 0 or neutral_remaining > 0,
            "phase": "friendly" if friendly_remaining > 0 else ("neutral" if neutral_remaining > 0 else "complete")
        }

    # ──────────────────────── ④  Hierarchical selector ───────────────────────
    async def _hierarchical_category_selection(self, supplier_url, supplier_name):
        # DEPRECATED: Replaced by EnhancedStateManager to prevent state conflicts
        # hist = self._load_history()
        hist = {"categories_scraped": [], "ai_suggested_categories": []}  # Minimal hist for legacy compatibility

        # 🧠 FIXED: Load AI memory from AI cache file, not processing state
        ai_memory = self._load_ai_memory(supplier_name)

        # Use the new discover_categories method that returns dict format
        discovered_categories = await self.web_scraper.discover_categories(supplier_url)

        if not discovered_categories:
            log.warning(f"No categories discovered for {supplier_url}, using fallback")
            # Fallback to basic homepage categories
            basic_cats = await self.web_scraper.get_homepage_categories(supplier_url)
            discovered_categories = [{"name": url.split('/')[-1] or "category", "url": url} for url in basic_cats[:10]]

        # PHASE 3: SUBCATEGORY DEDUPLICATION - Apply before AI processing
        log.info(f"PHASE 3: Applying subcategory deduplication to {len(discovered_categories)} discovered categories")
        category_urls_only = [cat["url"] for cat in discovered_categories]
        filtered_category_urls = await self._filter_urls_by_subcategory_deduplication(category_urls_only)
        
        # Rebuild discovered_categories with filtered URLs
        filtered_discovered_categories = []
        for cat in discovered_categories:
            if cat["url"] in filtered_category_urls:
                filtered_discovered_categories.append(cat)
        
        # Update discovered_categories with filtered results
        original_count = len(discovered_categories)
        discovered_categories = filtered_discovered_categories
        eliminated_count = original_count - len(discovered_categories)
        
        log.info(f"PHASE 3 RESULT: Eliminated {eliminated_count} redundant subcategories, "
                f"proceeding with {len(discovered_categories)} optimized categories")

        # Check category exhaustion status using AI memory instead of processing state
        exhaustion_status = self._check_category_exhaustion_status(discovered_categories, ai_memory["previously_suggested_urls"])
        log.info(f"Category exhaustion status: {exhaustion_status}")

        # Determine current price phase based on AI memory
        current_price_phase = self._determine_price_phase(ai_memory)
        log.info(f"Current price phase: {current_price_phase}")

        if not exhaustion_status["should_continue"] and current_price_phase == "low":
            log.info(f"All categories processed in Phase 1 (£{self.min_price}-£{self.price_midpoint}). Moving to Phase 2 (£{self.price_midpoint}-£{MAX_PRICE})...")
            # Reset AI memory for Phase 2 but keep track of Phase 1 completion
            self._reset_ai_memory_for_phase_2(supplier_name, ai_memory)
            current_price_phase = "medium"
        elif not exhaustion_status["should_continue"] and current_price_phase == "medium":
            log.info("All FBA-friendly and neutral categories have been processed in both phases. Scraping complete.")
            return []

        # 🧠 FIXED: Pass AI memory instead of processing state history
        ai_suggestions = await self._get_ai_suggested_categories_enhanced(
            supplier_url, supplier_name, discovered_categories,
            previous_categories=ai_memory["previously_suggested_urls"],
            processed_products=ai_memory["total_products_processed"],
        )
        
        # Validate category productivity (Solution 3)
        log.info("Validating AI-suggested categories for product content...")
        validated_urls = []
        validation_results = []

        for url in ai_suggestions["top_3_urls"]:
            validation_result = await self._validate_category_productivity(url)
            validation_results.append(validation_result)

            if validation_result["is_productive"]:
                validated_urls.append(url)
                log.info(f"✅ Category validated: {url} ({validation_result['product_count']} products)")
            else:
                log.warning(f"❌ Category rejected: {url} ({validation_result['product_count']} products - below minimum of 2)")
                # Add to skip_urls in AI suggestions
                if url not in ai_suggestions.get("skip_urls", []):
                    ai_suggestions.setdefault("skip_urls", []).append(url)

        # Update AI suggestions with validated URLs
        ai_suggestions["top_3_urls"] = validated_urls
        ai_suggestions["validation_results"] = validation_results

        # If no validated URLs, try secondary URLs
        if not validated_urls and ai_suggestions.get("secondary_urls"):
            log.warning("No productive primary URLs found. Validating secondary URLs...")
            for url in ai_suggestions["secondary_urls"][:3]:  # Try up to 3 secondary URLs
                validation_result = await self._validate_category_productivity(url)
                if validation_result["is_productive"]:
                    validated_urls.append(url)
                    log.info(f"✅ Secondary category validated: {url}")
                    if len(validated_urls) >= 3:  # Limit to 3 URLs
                        break
            ai_suggestions["top_3_urls"] = validated_urls

        # Record AI decision in history
        self._record_ai_decision(hist, ai_suggestions)

        # Update history with validated categories only
        hist["categories_scraped"] += validated_urls
        # DEPRECATED: Replaced by EnhancedStateManager to prevent state conflicts

        # Apply URL optimization to validated URLs FIRST
        if validated_urls:
            log.info("Applying URL optimization parameters...")
            optimized_urls = self._optimize_category_urls(validated_urls, price_range=current_price_phase)
            log.info(f"Optimized {len(validated_urls)} URLs with product display parameters for {current_price_phase} price phase")

            # Update AI suggestions with optimized URLs and failure tracking
            ai_suggestions["optimized_urls"] = optimized_urls
            ai_suggestions["failed_urls"] = [r["url"] for r in validation_results if not r["is_productive"]]
            ai_suggestions["failed_url_errors"] = {r["url"]: r.get("error", "Unknown") for r in validation_results if not r["is_productive"]}

            # 🔧 FIX: Replace top_3_urls with optimized URLs for caching
            ai_suggestions["top_3_urls"] = optimized_urls[:3]  # Keep only top 3 optimized URLs
            ai_suggestions["original_urls"] = validated_urls  # Store original URLs for reference
        else:
            log.warning("No validated URLs to optimize. Using fallback categories.")
            optimized_urls = []
            # Fallback to known working categories
            fallback_categories = [
                f"{supplier_url.rstrip('/')}/pound-lines.html",
                f"{supplier_url.rstrip('/')}/household.html",
                f"{supplier_url.rstrip('/')}/health-beauty.html"
            ]
            # Validate fallback categories
            fallback_validated = []
            for url in fallback_categories:
                validation_result = await self._validate_category_productivity(url)
                if validation_result["is_productive"]:
                    fallback_validated.append(url)

            if fallback_validated:
                optimized_urls = self._optimize_category_urls(fallback_validated, price_range="low")
                log.info(f"Using {len(optimized_urls)} validated fallback categories")
                # Update AI suggestions with fallback optimized URLs
                ai_suggestions["top_3_urls"] = optimized_urls[:3]
                ai_suggestions["optimized_urls"] = optimized_urls
                ai_suggestions["original_urls"] = fallback_validated
            else:
                log.error("No productive categories found. Cannot proceed with scraping.")
                return []

        # 🧠 FIXED: Save AI category suggestions to cache AFTER URL optimization
        try:
            Path(AI_CATEGORY_CACHE_DIR).mkdir(parents=True, exist_ok=True)
            cache_file_path = Path(AI_CATEGORY_CACHE_DIR) / f"{supplier_name.replace('.', '_')}_ai_category_cache.json"

            # Load existing cache data
            existing_cache = {}
            if cache_file_path.exists():
                try:
                    with open(cache_file_path, 'r', encoding='utf-8') as f:
                        existing_cache = json.load(f)
                except Exception as e:
                    log.warning(f"Could not load existing AI cache: {e}")

            # Create new entry for this AI suggestion session (now with optimized URLs)
            new_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_context": {
                    "categories_discovered": len(discovered_categories),
                    "total_products_processed": ai_memory["total_products_processed"] if isinstance(ai_memory["total_products_processed"], int) else 0,
                    "previous_categories_count": len(ai_memory["previously_suggested_urls"]) if ai_memory["previously_suggested_urls"] else 0
                },
                "ai_suggestions": ai_suggestions,  # Now contains optimized URLs
                "validation_summary": {
                    "total_suggested": len(ai_suggestions.get("top_3_urls", [])),
                    "productive_categories": len(validated_urls),
                    "rejected_categories": len([r for r in validation_results if not r["is_productive"]])
                }
            }

            # Initialize or update cache structure
            if not existing_cache:
                cache_data = {
                    "supplier": supplier_name,
                    "url": supplier_url,
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_ai_calls": 1,
                    "ai_suggestion_history": [new_entry]
                }
            else:
                # Append to existing history
                cache_data = existing_cache
                cache_data.setdefault("ai_suggestion_history", []).append(new_entry)
                cache_data["total_ai_calls"] = cache_data.get("total_ai_calls", 0) + 1
                cache_data["last_updated"] = datetime.now().isoformat()

            # Save updated cache data
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            log.info(f"🧠 Saved AI category suggestions to cache: {cache_file_path}")

        except Exception as e:
            log.error(f"Error saving AI category suggestions to cache: {e}")

        return optimized_urls

    async def _extract_supplier_products(self, supplier_url: str, supplier_name: str, category_urls: List[str], max_products_per_category: int, max_products_to_process: int = None, supplier_extraction_batch_size: int = 3) -> List[Dict[str, Any]]:
        """Extract products from a list of category URLs with overall product limit enforcement."""
        import json  # Import at function level to ensure availability
        
        # 🔄 SUPPLIER CACHE FRESHNESS CHECK
        # If we have cached products and processing state indicates progress, skip supplier scraping
        actual_cache_file, cache_count = self._find_actual_supplier_cache_file(supplier_name)
        
        if actual_cache_file and hasattr(self, 'state_manager') and self.state_manager:
            try:
                # Check if we have processing state indicating previous progress
                if hasattr(self.state_manager, 'state_data') and self.state_manager.state_data:
                    last_index = self.state_manager.state_data.get('last_processed_index', 0)
                    processing_status = self.state_manager.state_data.get('processing_status', 'not_started')
                    
                    # Check cache file age (fresh within 24 hours)
                    import time
                    cache_age_hours = (time.time() - os.path.getmtime(actual_cache_file)) / 3600
                    cache_is_fresh = cache_age_hours < 24
                    
                    if last_index > 0 and cache_is_fresh:
                        # Check if supplier extraction is complete before returning cache
                        import json
                        with open(actual_cache_file, 'r', encoding='utf-8') as f:
                            cached_products = json.load(f)
                        
                        # 🚨 CRITICAL FIX: Use system_progression as canonical source of truth
                        sp = self.state_manager.state_data.get('system_progression', {})
                        extraction_progress = sp  # Use system_progression data
                        products_extracted = sp.get('current_product_index_in_category', len(cached_products))
                        
                        # 🚨 HYBRID MODE FIX: Check if current chunk categories are already in cache
                        chunk_category_urls = set(category_urls)
                        products_for_chunk_categories = [
                            product for product in cached_products 
                            if product.get('source_url', '') in chunk_category_urls
                        ]
                        
                        # 🚨 RESUMPTION FIX: Check cache but always perform fresh extraction
                        if len(products_for_chunk_categories) > 0:
                            if hasattr(self, 'last_processed_index') and self.last_processed_index > 0:
                                self.log.info(
                                    f"🔄 RESUMPTION DETECTED: Found {len(products_for_chunk_categories)} cached products but resuming from index {self.last_processed_index}"
                                )
                                self.log.info("🔄 EXTRACTION NEEDED: Continuing supplier extraction to complete interrupted category")
                            else:
                                self.log.info(
                                    f"🔄 CHUNK CACHE REFERENCE: {len(products_for_chunk_categories)} cached products exist for current chunk categories – performing fresh extraction to detect updates"
                                )
                                self.log.info(f"🔄 CHUNK CATEGORIES: {list(chunk_category_urls)}")
                        else:
                            self.log.info(
                                f"🔄 CHUNK CACHE MISS: No cached products found for chunk categories: {list(chunk_category_urls)}"
                            )
                            self.log.info("🔄 EXTRACTION NEEDED: Continuing with supplier extraction for new categories")
                        # Fall through to continue with supplier extraction regardless of cache state
                        
                    elif last_index > 0 and not cache_is_fresh:
                        self.log.info(f"🔄 CACHE STALE: Cache age {cache_age_hours:.1f}h > 24h threshold, proceeding with fresh scraping")
                        # Reset processing index since we're re-scraping (product list may have changed)
                        if hasattr(self, 'last_processed_index'):
                            self.last_processed_index = 0
                            self.log.info(f"⚠️ Reset processing index to 0 due to stale cache")
                    elif last_index > 0:
                        # This handles the case where cache exists but extraction was incomplete
                        import json
                        with open(actual_cache_file, 'r', encoding='utf-8') as f:
                            cached_products = json.load(f)
                        # 🚨 CRITICAL FIX: Use system_progression as canonical source
                        sp = self.state_manager.state_data.get('system_progression', {})
                        extraction_progress = sp  # Use system_progression data
                        products_extracted = sp.get('current_product_index_in_category', len(cached_products))
                        
                        self.log.info(f"🔄 SUPPLIER EXTRACTION INCOMPLETE: {products_extracted}/{max_products_per_category} products extracted")
                        self.log.info(f"🔄 RESUMPTION: Continuing supplier scraping from product {products_extracted + 1}")
                        # Set the starting counter to resume from where we left off
                        if not hasattr(self, '_supplier_product_counter'):
                            self._supplier_product_counter = products_extracted
                            self.log.info(f"📊 RESUMPTION: Setting product counter to {self._supplier_product_counter}")
                    else:
                        self.log.info(f"🔄 NO PROCESSING PROGRESS: index={last_index}, proceeding with scraping")
                        
            except Exception as e:
                self.log.warning(f"⚠️ Error checking supplier cache freshness: {e}, proceeding with scraping")
        
        # Proceed with normal supplier scraping with batching
        # supplier_extraction_batch_size is now passed as a parameter
        self.log.info(f"🕷️ PERFORMING SUPPLIER SCRAPING from {len(category_urls)} categories")
        self.log.info(f"📦 Using supplier extraction batch size: {supplier_extraction_batch_size}")
        
        # Process categories in batches for better memory management
        all_products = []
        # Mapping of category_url -> full list of product URLs for manifest generation
        self.category_manifests = {}
        
        # 🚨 CRITICAL FIX: Load existing cached products and filter against linking map
        actual_cache_file, existing_cache_count = self._find_actual_supplier_cache_file(supplier_name)
        if actual_cache_file:
            try:
                with open(actual_cache_file, 'r', encoding='utf-8') as f:
                    existing_cached_products = json.load(f)
                
                # 🚨 CRITICAL FIX: Filter against linking map to only return unprocessed products
                if self.linking_map and len(self.linking_map) > 0:
                    # Build hash set for O(1) lookup performance
                    processed_urls = {entry.get("supplier_url") for entry in self.linking_map 
                                    if entry.get("supplier_url")}
                    processed_eans = {entry.get("supplier_ean") for entry in self.linking_map 
                                    if entry.get("supplier_ean")}
                    
                    # Filter out already processed products
                    unprocessed_products = []
                    for product in existing_cached_products:
                        if isinstance(product, dict) and not product.get("_cache_metadata"):
                            product_url = product.get("url", "")
                            product_ean = product.get("ean", "") or product.get("barcode", "")
                            
                            # Skip if already in linking map (processed by either EAN or URL)
                            if (product_ean and product_ean in processed_eans) or \
                               (product_url and product_url in processed_urls):
                                continue
                            
                            unprocessed_products.append(product)
                    
                    all_products = unprocessed_products
                    self.log.info(f"🔍 FILTERING APPLIED: {len(existing_cached_products)} total → {len(unprocessed_products)} unprocessed ({len(processed_urls)} already in linking map)")
                    self.log.info(f"📊 EFFICIENCY GAIN: {((len(existing_cached_products) - len(unprocessed_products)) / max(len(existing_cached_products), 1) * 100):.1f}% products skipped (already processed)")
                else:
                    # No linking map available, process all cached products
                    all_products = existing_cached_products.copy()
                    self.log.info(f"⚠️ NO LINKING MAP: Processing all {len(existing_cached_products)} cached products (no filtering applied)")
                    
            except Exception as e:
                self.log.warning(f"⚠️ Could not load existing cache during resumption: {e}")
                all_products = []  # Fallback to empty list
        
        # Store as instance variable for progress callback access
        self._current_all_products = all_products
        category_batches = [category_urls[i:i + supplier_extraction_batch_size] for i in range(0, len(category_urls), supplier_extraction_batch_size)]
        
        # Get progress tracking configuration
        progress_config = self.system_config.get("supplier_extraction_progress", {})
        cache_config = self.system_config.get("supplier_cache_control", {})
        
        # Initialize extraction progress tracking
        if progress_config.get("enabled", True):
            self.log.info(f"📊 PROGRESS TRACKING: Extracting from {len(category_urls)} categories in {len(category_batches)} batches")
        
        for batch_num, category_batch in enumerate(category_batches, 1):
            # Check if we've reached the overall product limit before starting a new batch
            if max_products_to_process and len(all_products) >= max_products_to_process:
                self.log.info(f"🛑 STOPPING: Reached max_products_to_process limit of {max_products_to_process} products before batch {batch_num}")
                break
                
            self.log.info(f"📦 Processing category batch {batch_num}/{len(category_batches)} ({len(category_batch)} categories)")
            
            # 🚨 LOGIN SCRIPT TRIGGER - At start of every supplier category extraction after Amazon product detail extraction
            # This ensures authentication is verified before each new category batch processing
            await self._trigger_authentication_check(f"category_batch_{batch_num}")
            
            for subcategory_index, category_url in enumerate(category_batch, 1):
                # Update detailed progress tracking
                if progress_config.get("enabled", True) and hasattr(self, 'state_manager'):
                    if self.system_config.get("pipeline_toggles", {}).get("resume_abs_index_math", True):
                        resume_cat_idx = self.state_manager.state_data["system_progression"].get("current_category_index", 0)
                        category_index = resume_cat_idx + ((batch_num - 1) * supplier_extraction_batch_size) + subcategory_index
                    else:
                        category_index = (batch_num - 1) * supplier_extraction_batch_size + subcategory_index
                    # Initialize category tracking for precise resumption
                    self.state_manager.initialize_category_processing(
                        category_index=category_index - 1,
                        category_url=category_url,
                        total_categories=len(category_urls)
                    )
                    self.state_manager.update_supplier_extraction_progress(
                        category_index=category_index,
                        total_categories=len(category_urls),
                        subcategory_index=subcategory_index,
                        total_subcategories=len(category_batch),
                        batch_number=batch_num,
                        total_batches=len(category_batches),
                        category_url=category_url,
                        extraction_phase="categories"
                    )
                    
                    if progress_config.get("progress_display", {}).get("show_subcategory_progress", True):
                        self.log.info(f"🔄 EXTRACTION PROGRESS: Processing subcategory {subcategory_index}/{len(category_batch)} in batch {batch_num} (Category {category_index}/{len(category_urls)})")
                
                # Setup progress callback for individual product tracking
                if hasattr(self.supplier_scraper, 'set_progress_callback'):
                    self.supplier_scraper.set_progress_callback(self._create_product_progress_callback(category_url, progress_config))
                # Check if we've reached the overall product limit
                if max_products_to_process and len(all_products) >= max_products_to_process:
                    self.log.info(f"🛑 STOPPING: Reached max_products_to_process limit of {max_products_to_process} products")
                    break
                    
                self.log.info(f"Scraping category: {category_url}")

                # 🚨 SURGICAL FIX: PRE-EXTRACTION URL COLLECTION AND FILTERING
                # First, collect URLs without extracting product data
                urls_for_manifest = await self._collect_urls_only(category_url, max_products_per_category)
                
                if not urls_for_manifest:
                    self.log.warning(f"No product URLs found for {category_url}")
                    continue
                
                # Generate category slug for logging
                slug = self._generate_category_slug(category_url)
                
                # Use same absolute index calculation for consistency
                if self.system_config.get("pipeline_toggles", {}).get("resume_abs_index_math", True):
                    resume_cat_idx = self.state_manager.state_data["system_progression"].get("current_category_index", 0)
                    category_index = resume_cat_idx + ((batch_num - 1) * supplier_extraction_batch_size) + subcategory_index
                else:
                    category_index = (batch_num - 1) * supplier_extraction_batch_size + subcategory_index
                
                # Get pagination info from scraper
                page_count = getattr(self.supplier_scraper, 'last_page_count', 1)
                urls_per_page = getattr(self.supplier_scraper, 'last_urls_per_page', [])
                
                # Log pagination summary as specified in requirements
                if urls_per_page and len(urls_per_page) > 0:
                    urls_per_page_str = ",".join(map(str, urls_per_page))
                    self.log.info(f"PAGINATION[C{category_index} {slug}]: pages={page_count} urls_page={urls_per_page_str} total={len(urls_for_manifest)}")
                    
                    # Validate pagination completeness invariant
                    if sum(urls_per_page) != len(urls_for_manifest):
                        self.log.warning(f"⚠️ PAGINATION MISMATCH: sum(urls_page)={sum(urls_per_page)} != total={len(urls_for_manifest)} for {category_url}")
                else:
                    # Fallback for scrapers that don't provide per-page breakdown
                    self.log.info(f"PAGINATION[C{category_index} {slug}]: pages={page_count} urls_page={len(urls_for_manifest)} total={len(urls_for_manifest)}")

                # 🚨 SURGICAL FIX: DETAILED TWO-STEP PRE-EXTRACTION FILTERING
                self.log.info(f"🔗 DETAILED PRE-EXTRACTION FILTERING: Analyzing {len(urls_for_manifest)} collected URLs")

                # STEP 1: LINKING MAP FILTERING
                # 🚨 SURGICAL FIX #1: UNIFIED FILTERING LOGIC (EAN + URL)
                # Build hash sets for O(1) lookup performance against linking map
                processed_urls = {entry.get("supplier_url") for entry in self.linking_map if entry.get("supplier_url")} if self.linking_map else set()
                processed_eans = {entry.get("supplier_ean") for entry in self.linking_map if entry.get("supplier_ean")} if self.linking_map else set()
                
                self.log.debug(f"🔗 UNIFIED FILTER: Loaded {len(processed_eans)} EANs and {len(processed_urls)} URLs from linking map")

                # Filter URLs against linking map (SKIP_ENTIRELY)
                skip_entirely_urls = []
                remaining_after_linking_map = []

                for url in urls_for_manifest:
                    # Primary check: URL-based filtering (always available)
                    if url in processed_urls:
                        skip_entirely_urls.append(url)
                    else:
                        # 🚨 ENHANCEMENT: Try EAN-based filtering if product cache is available
                        # Load product from cache to get EAN for enhanced filtering
                        product_ean = None
                        
                        # Build cache indexes if not already available
                        if not hasattr(self, 'product_cache_ean_index') or not hasattr(self, 'product_cache_url_index'):
                            cached_products = self._load_supplier_cache(supplier_name)
                            if cached_products:
                                self.product_cache_ean_index = {p.get('ean'): p for p in cached_products if p.get('ean')}
                                self.product_cache_url_index = {p.get('url'): p for p in cached_products if p.get('url')}
                        
                        # Get product EAN from cache if available
                        if hasattr(self, 'product_cache_url_index') and url in self.product_cache_url_index:
                            product_ean = self.product_cache_url_index[url].get('ean')
                        
                        # Secondary check: EAN-based filtering (when available)
                        if product_ean and product_ean in processed_eans:
                            skip_entirely_urls.append(url)
                            self.log.debug(f"🔗 EAN-based skip: {url} (EAN: {product_ean})")
                        else:
                            remaining_after_linking_map.append(url)

                # STEP 2: PRODUCT CACHE FILTERING
                # Load product cache for EAN/URL checking
                product_cache_ean_index = set()
                product_cache_url_index = set()
                if hasattr(self, 'product_cache_ean_index'):
                    product_cache_ean_index = self.product_cache_ean_index
                if hasattr(self, 'product_cache_url_index'):
                    product_cache_url_index = self.product_cache_url_index

                # Filter remaining URLs against product cache
                needs_amazon_only_urls = []
                needs_full_extraction_urls = []

                for url in remaining_after_linking_map:
                    # Check if URL has cached supplier data (needs Amazon analysis only)
                    if url in product_cache_url_index:
                        needs_amazon_only_urls.append(url)
                    else:
                        # URL needs full extraction (not in linking map, not in cache)
                        needs_full_extraction_urls.append(url)

                # 🚨 ENHANCED TRANSPARENCY: Implement transparent filter classification logging
                self.log.info(f"🔗 STEP 1 - LINKING MAP CHECK: {len(skip_entirely_urls)} complete (skipped)")
                self.log.info(f"💾 STEP 2 - PRODUCT CACHE CHECK: {len(needs_amazon_only_urls)} have supplier data; {len(needs_full_extraction_urls)} need supplier extraction")
                
                # 🚨 SURGICAL FIX #3: FILTERING CONTRACT COMPLIANCE VERIFICATION
                filter_invariant_check = len(urls_for_manifest) == (len(skip_entirely_urls) + len(needs_amazon_only_urls) + len(needs_full_extraction_urls))
                self.log.info(f"🧮 Filter Invariant: in={len(urls_for_manifest)} == skip+amz_only+full={len(skip_entirely_urls) + len(needs_amazon_only_urls) + len(needs_full_extraction_urls)} → {'✅ VALID' if filter_invariant_check else '❌ INVALID'}")
                
                # 🚨 CONTRACT ENFORCEMENT: Fail fast if filtering contract is violated
                if not filter_invariant_check:
                    self.log.error(f"🚨 FILTERING CONTRACT VIOLATION: Totals don't match!")
                    self.log.error(f"   Input URLs: {len(urls_for_manifest)}")
                    self.log.error(f"   Skip entirely: {len(skip_entirely_urls)}")
                    self.log.error(f"   Needs Amazon only: {len(needs_amazon_only_urls)}")
                    self.log.error(f"   Needs full extraction: {len(needs_full_extraction_urls)}")
                    self.log.error(f"   Sum of outputs: {len(skip_entirely_urls) + len(needs_amazon_only_urls) + len(needs_full_extraction_urls)}")
                    raise ValueError("Filtering contract violation: URL counts don't add up correctly")
                
                # 🚨 CRITICAL TRANSPARENCY: Log specific product classification for visibility
                if len(skip_entirely_urls) > 0:
                    self.log.info(f"✅ SKIP_ENTIRELY ({len(skip_entirely_urls)}): {skip_entirely_urls[:5]}{'...' if len(skip_entirely_urls) > 5 else ''}")
                if len(needs_amazon_only_urls) > 0:
                    self.log.info(f"🚀 NEEDS_AMAZON_ONLY ({len(needs_amazon_only_urls)}): {needs_amazon_only_urls[:5]}{'...' if len(needs_amazon_only_urls) > 5 else ''}")
                if len(needs_full_extraction_urls) > 0:
                    self.log.info(f"📊 NEEDS_FULL_EXTRACTION ({len(needs_full_extraction_urls)}): {needs_full_extraction_urls[:5]}{'...' if len(needs_full_extraction_urls) > 5 else ''}")

                # 📊 EFFICIENCY METRICS
                total_urls = len(urls_for_manifest)
                total_skipped = len(skip_entirely_urls)
                total_cached = len(needs_amazon_only_urls)
                total_needs_extraction = len(needs_full_extraction_urls)

                self.log.info(f"📈 FILTERING EFFICIENCY: {total_skipped}/{total_urls} = {(total_skipped/total_urls*100) if total_urls > 0 else 0:.1f}% already processed")
                self.log.info(f"💾 CACHE UTILIZATION: {total_cached}/{total_urls} = {(total_cached/total_urls*100) if total_urls > 0 else 0:.1f}% have supplier data")
                self.log.info(f"📊 EXTRACTION NEEDED: {total_needs_extraction}/{total_urls} = {(total_needs_extraction/total_urls*100) if total_urls > 0 else 0:.1f}% need fresh extraction")

                # 🚨 CRITICAL FIX: Only extract products that need full extraction
                if needs_full_extraction_urls:
                    self.log.info(f"🚀 PROCEEDING WITH EXTRACTION: {len(needs_full_extraction_urls)} products need full extraction")
                    
                    # 🚨 SURGICAL FIX #3: CONTRACT COMPLIANCE - Track extraction promise
                    promised_extraction_count = len(needs_full_extraction_urls)
                    self.log.info(f"📝 EXTRACTION CONTRACT: Promising to extract exactly {promised_extraction_count} products")
                    
                    # Use pre-filtered extraction method that respects filtering contract
                    # This ensures we process exactly the N products identified by filtering
                    products = await self.supplier_scraper.scrape_products_from_prefiltered_urls(
                        needs_full_extraction_urls, category_url, all_products
                    )
                    
                    # 🚨 CONTRACT VERIFICATION: Ensure we extracted what we promised
                    actual_extraction_count = len(products)
                    contract_fulfilled = actual_extraction_count == promised_extraction_count
                    
                    self.log.info(f"📝 EXTRACTION CONTRACT VERIFICATION:")
                    self.log.info(f"   Promised: {promised_extraction_count} products")
                    self.log.info(f"   Delivered: {actual_extraction_count} products")
                    self.log.info(f"   Contract: {'✅ FULFILLED' if contract_fulfilled else '⚠️ PARTIAL'}")
                    
                    if not contract_fulfilled:
                        self.log.warning(f"⚠️ EXTRACTION CONTRACT WARNING: Expected {promised_extraction_count}, got {actual_extraction_count}")
                        self.log.warning(f"   This may indicate scraping issues or URL accessibility problems")
                    
                else:
                    self.log.info(f"✅ NO EXTRACTION NEEDED: All products are either already processed or have cached supplier data")
                    products = []
                    # 🚨 CRITICAL FIX: Skip to next category to prevent legacy path execution
                    continue
                
                # Add products that only need Amazon analysis to the accumulator
                if needs_amazon_only_urls:
                    self.log.info(f"📋 ADDING TO AMAZON ANALYSIS: {len(needs_amazon_only_urls)} products have supplier data and need Amazon analysis")
                    # Load these products from cache and add to accumulator
                    cached_products = self._load_cached_products_for_urls(needs_amazon_only_urls, supplier_name)
                    if cached_products:
                        all_products.extend(cached_products)
                        self.log.info(f"✅ Added {len(cached_products)} cached products to Amazon analysis queue")
                # 🚨 SURGICAL FIX: Update state manager with current category URL being processed
                if hasattr(self, 'state_manager') and self.state_manager:
                    if hasattr(self.state_manager, 'update_current_category_url'):
                        self.state_manager.update_current_category_url(category_url)
                    else:
                        # Fallback: directly update the category URL in supplier_extraction_progress
                        if hasattr(self.state_manager, 'state_data'):
                            self.state_manager.state_data.setdefault('supplier_extraction_progress', {})['current_category_url'] = category_url
                if urls_for_manifest:
                    # Frozen category denominator per run (Step 3)
                    if self.system_config.get("pipeline_toggles", {}).get("frozen_category_denominator", True):
                        discovered_count = len(urls_for_manifest)  # pre-filter
                        # write both: discovery API (for visibility) and a frozen snapshot
                        self.state_manager.update_discovered_products_in_category(category_url, discovered_count)
                        self.state_manager.set_frozen_denominator(category_url, discovered_count)  # new helper
                        self.state_manager.save_state(preserve_interruption_state=True)
                        self.log.info(f"🔒 FROZEN DENOMINATOR: Category {category_url} → {discovered_count} products (snapshot taken)")
                    
                    self._set_current_category_index(category_index)
                    self._save_category_manifest(supplier_name, category_url, urls_for_manifest)
                    
                    # Update state manager with accurate totals for breadcrumb logging
                    if hasattr(self, 'state_manager') and self.state_manager:
                        # Load total categories directly from config as authoritative source
                        total_categories = self._get_authoritative_category_count(category_urls)
                        
                        # Update system progression with accurate totals
                        sp = self.state_manager.state_data.setdefault("system_progression", {})
                        sp.update({
                            "total_categories": total_categories,
                            "current_category_index": category_index,
                            "current_category_url": category_url,
                            "total_products_in_current_category": len(urls_for_manifest),
                            "current_product_index_in_category": 0
                        })
                
                self.category_manifests[category_url] = urls_for_manifest
                self.log.info(
                    f"Finished scraping category {category_url}: Found {len(urls_for_manifest)} products across {page_count} pages."
                )

                # 🚨 REMOVED: Price filtering and product extension now handled in progress callback
                # Products are added to all_products immediately when found via progress_callback
                # This ensures per-product cache saves work correctly with live data
                self.log.info(
                    f"📊 Category completed: {len(products)} raw products extracted, {len(all_products)} total products accumulated"
                )
                
                # 🚨 SURGICAL FIX: Update state manager with discovered product count for accurate processing state
                if hasattr(self, 'state_manager') and self.state_manager and len(products) > 0:
                    # Get the actual discovered count from scraper (may be more than extracted due to URL cache filtering)
                    # This ensures processing state shows real-time discovery totals, not just processed totals
                    discovered_count = getattr(self.supplier_scraper, 'last_discovered_count', len(products))
                    self.state_manager.correct_category_totals_realtime(category_url, discovered_count)
                    self.log.info(f"🔄 STATE UPDATE: Updated category {category_url} with {discovered_count} discovered products")
                
                # 🚨 REMOVED: Category-based cache saving logic (now handled per-product in progress callback)
                # This was causing the update_frequency_products to only save after complete categories
                # instead of respecting the per-product frequency configuration
                
                # Check again after adding products from this category
                if max_products_to_process and len(all_products) >= max_products_to_process:
                    # Trim to exact limit if we exceeded it
                    all_products = all_products[:max_products_to_process]
                    self.log.info(f"🛑 TRIMMED: Limited to exactly {max_products_to_process} products")
                    break
            
            # Batch completion logging
            self.log.info(f"✅ Completed batch {batch_num}: {len(all_products)} total products extracted so far")
                
        # 🚨 CRITICAL FIX #1: LINKING MAP FILTERING
        # Filter out products that have already been processed (exist in linking map)
        # This prevents loading all 2,335 cached products when only 50-100 are unprocessed
        unprocessed_products = self._filter_unprocessed_products_with_hash_lookup(all_products, supplier_name)
        
        if len(unprocessed_products) != len(all_products):
            self.log.info(f"🔍 GAP PROCESSING FILTER: {len(all_products)} total cached products → {len(unprocessed_products)} unprocessed products")
            self.log.info(f"🔍 FILTERING EFFICIENCY: Removed {len(all_products) - len(unprocessed_products)} already processed products")
        else:
            self.log.info(f"🔍 GAP PROCESSING FILTER: All {len(all_products)} products are unprocessed (first run or fresh cache)")
        
        return unprocessed_products

    def _create_product_progress_callback(self, category_url: str, progress_config: Dict[str, Any]):
        """Create a progress callback for individual product extraction with proper caching"""
        # Initialize a simple counter if it doesn't exist
        if not hasattr(self, '_supplier_product_counter'):
            self._supplier_product_counter = 0
            
        def progress_callback(operation_type: str, product_index: int, total_products: int, product_url: str, product_data: dict = None):
            if operation_type == 'supplier_extraction':
                # 🚨 FIX: Update counter based on actual cache length, not callback attempts
                if hasattr(self, '_current_all_products') and product_data:
                    # Only increment counter when product is actually added to cache
                    self._supplier_product_counter = len(self._current_all_products)
                else:
                    # Fallback increment if cache not available
                    self._supplier_product_counter += 1
                
                if hasattr(self, 'state_manager') and self.state_manager:
                    try:
                        # Update the main processing index during supplier extraction based on actual cache length
                        actual_cache_count = len(getattr(self, '_current_all_products', []))
                        self.state_manager.update_processing_index(actual_cache_count, total_products)
                        if product_url:
                            self.state_manager.update_supplier_extraction_progress_new(product_url)
                        self.log.info(f"🔍 SUPPLIER STATE UPDATE: Index updated to {actual_cache_count}/{total_products}")
                    except Exception as e:
                        self.log.error(f"❌ SUPPLIER STATE UPDATE FAILED: {e}")
                
                # 🚨 DEFINITIVE FIX: Products are now added by scraper directly to shared list
                # Progress callback only needs to track progress and trigger cache saves
                if product_data and hasattr(self, '_current_all_products'):
                    self.log.info(f"📊 PROGRESS: Product {self._supplier_product_counter} processed (total in cache: {len(self._current_all_products)})")
                
                # Simple index-based logging (matching Amazon analysis style)
                if progress_config.get("progress_display", {}).get("show_product_progress", True):
                    self.log.info(f"🔄 SUPPLIER EXTRACTION: Processing product {self._supplier_product_counter}")
                
                # 🚨 NEW: Per-product cache saving logic (now works because list is populated)
                cache_config = self.system_config.get("supplier_cache_control", {})
                update_frequency = cache_config.get("update_frequency_products", 1)  # Use config value
                
                # Debug logging for cache save logic
                self.log.info(f"🔍 CACHE CHECK: Product {self._supplier_product_counter}, frequency={update_frequency}, enabled={cache_config.get('enabled', True)}")
                self.log.info(f"🔍 CACHE CHECK: List length={len(getattr(self, '_current_all_products', []))}, modulo={self._supplier_product_counter % update_frequency}")
                
                # Skip redundant saves when nothing new was added
                current_count = len(getattr(self, '_current_all_products', []))
                last_count = getattr(self, "_last_cache_count", None)
                if last_count is not None and current_count == last_count:
                    self.log.debug("💤 PERIODIC SAVE SKIPPED: 0 new since last")
                    return
                
                if (cache_config.get("enabled", True) and 
                    hasattr(self, '_current_all_products') and
                    len(self._current_all_products) > 0 and
                    self._supplier_product_counter % update_frequency == 0):
                    
                    # Use centralized path management for consistent cache file construction
                    cache_filename = f"{self.supplier_name.replace('.', '-')}_products_cache.json"
                    cache_file_path = str(path_manager.get_output_path('cached_products', cache_filename))
                    
                    # 🚨 ATOMIC FIX 7: Save current products to cache atomically
                    new_count = self._save_products_to_cache(self._current_all_products, cache_file_path)
                    self.log.info(f"💾 ATOMIC PERIODIC SAVE: Saved {len(self._current_all_products)} products ({new_count} new) to cache (every {update_frequency} products)")
                    
                    # Track last cache count to avoid redundant saves
                    self._last_cache_count = current_count
                    
                    # 🚨 ATOMIC FIX 9: Only update state AFTER successful cache write
                    if hasattr(self, 'state_manager') and new_count >= 0:  # new_count >= 0 indicates successful save
                        progress = self.state_manager.state_data["supplier_extraction_progress"]
                        # Use actual cache length from successful save
                        progress["products_extracted_total"] = len(self._current_all_products)
                        progress["current_product_url"] = product_url
                        progress["extraction_phase"] = "products"
                        progress["last_cache_save_count"] = new_count  # Track incremental saves
                        self.state_manager.save_state(preserve_interruption_state=True)
                        self.log.debug(f"🔄 ATOMIC STATE: State synchronized with cache after saving {new_count} new products")
                
                # 🚨 ATOMIC FIX 10: Separate state update for non-cache-save cycles (maintains progress tracking)
                elif hasattr(self, 'state_manager'):
                    progress = self.state_manager.state_data["supplier_extraction_progress"]
                    # Lightweight state update without cache write
                    progress["current_product_url"] = product_url
                    progress["extraction_phase"] = "products"
                    # Don't update products_extracted_total here - only after cache saves
                    self.state_manager.save_state(preserve_interruption_state=True)
                    
        return progress_callback

    def _check_amazon_cache_by_asin(self, asin: str, supplier_ean: str = None) -> Optional[Dict[str, Any]]:
        """Check for existing Amazon cache data by ASIN with multiple filename patterns."""
        
        # FIX 2: Amazon cache reuse logic - Enhanced ASIN/EAN matching
        amazon_cache_dir = self.amazon_cache_dir
        
        # First: Check for exact EAN match
        if supplier_ean:
            exact_pattern = f"amazon_{asin}_{supplier_ean}.json"
            exact_file = os.path.join(amazon_cache_dir, exact_pattern)
            if os.path.exists(exact_file):
                try:
                    with open(exact_file, 'r', encoding='utf-8') as f:
                        self.log.info(f"📋 Found exact EAN match in cache: {exact_pattern}")
                        return json.load(f)
                except Exception as e:
                    self.log.error(f"Error loading exact EAN match cache: {e}")
        
        # Second: Check for ASIN with different EAN - copy to new filename
        cache_patterns = [
            f"amazon_{asin}_*.json",  # ASIN with any suffix
            f"amazon_{asin}.json"     # ASIN only
        ]
        
        for pattern in cache_patterns:
            cache_path_pattern = os.path.join(amazon_cache_dir, pattern)
            matching_files = sorted(glob.glob(cache_path_pattern), key=os.path.getmtime, reverse=True)

            for cache_file in matching_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                except Exception as e:
                    self.log.error(f"Error loading cached Amazon data from {cache_file}: {e}")
                    continue

                # Gather all EAN values present in the cache file
                eans_in_cache = set()
                if cached_data.get("ean"):
                    eans_in_cache.add(str(cached_data.get("ean")))
                if cached_data.get("ean_on_page"):
                    eans_in_cache.add(str(cached_data.get("ean_on_page")))
                for ean in cached_data.get("eans_on_page", []):
                    eans_in_cache.add(str(ean))

                if supplier_ean and supplier_ean not in eans_in_cache:
                    self.log.info(
                        f"Skipping cache file {os.path.basename(cache_file)} due to EAN mismatch"
                    )
                    continue

                # Copy existing cache to new EAN-specific filename if needed
                if supplier_ean:
                    new_filename = f"amazon_{asin}_{supplier_ean}.json"
                    new_filepath = os.path.join(amazon_cache_dir, new_filename)

                    if not os.path.exists(new_filepath):
                        try:
                            with open(new_filepath, 'w', encoding='utf-8') as f:
                                json.dump(cached_data, f, indent=2, ensure_ascii=False)
                            self.log.info(
                                f"📋 Copied existing cache to EAN-specific file: {new_filename}"
                            )
                        except Exception as copy_error:
                            self.log.error(f"Error copying cache to EAN-specific file: {copy_error}")

                self.log.info(f"📋 Found ASIN match in cache: {os.path.basename(cache_file)}")
                return cached_data
        
        return None

    async def _get_amazon_data(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle Amazon search logic (EAN first, then title)."""
        supplier_ean = product_data.get("ean")
        if hasattr(self, 'state_manager'):
            self.state_manager.update_amazon_analysis_progress_new(product_data.get("url", ""))
        
        # 🚨 FIX: Handle multiple EANs - use first valid EAN only for Amazon search
        if supplier_ean:
            original_ean = str(supplier_ean)
            # Extract first valid EAN (12-14 digits) from various formats: "123/456", "123 456", "123,456", etc.
            import re
            ean_pattern = re.findall(r'\b\d{12,14}\b', original_ean)
            if ean_pattern and len(ean_pattern) > 1:
                supplier_ean = ean_pattern[0]  # Use first valid EAN found
                self.log.info(f"🔧 Multiple EANs detected, using first valid EAN for Amazon search: '{original_ean}' → '{supplier_ean}'")
            elif '/' in original_ean or ' ' in original_ean.strip():
                # Fallback: split by common separators and take first part
                for separator in ['/', ' ', ',', ';', '|']:
                    if separator in original_ean:
                        supplier_ean = original_ean.split(separator)[0].strip()
                        self.log.info(f"🔧 Multiple EANs detected (separator '{separator}'), using first EAN: '{original_ean}' → '{supplier_ean}'")
                        break
        
        amazon_product_data = None
        actual_search_method = None  # Track which method actually worked
        
        # 🚨 FIX: Ensure null EAN products attempt title search
        if supplier_ean and supplier_ean.strip() and supplier_ean != "None":
            self.log.info(f"Attempting Amazon search using EAN: {supplier_ean}")
            amazon_product_data = await self.extractor.search_by_ean_and_extract_data(supplier_ean, product_data["title"])
            actual_search_method = amazon_product_data.get("_search_method_used", "EAN") if amazon_product_data else "EAN"
            
            if amazon_product_data and "error" not in amazon_product_data:
                self.log.info(f"✅ EAN search successful for {supplier_ean}. Using EAN result without title fallback.")
                amazon_product_data["_search_method_used"] = actual_search_method
                return amazon_product_data
            else:
                self.log.info(f"❌ EAN search failed for {supplier_ean}. Will fall back to title search.")
        
        # 🚨 FIX: Always attempt title search for null EAN or failed EAN search
        if not amazon_product_data:
            if supplier_ean: 
                self.log.info("EAN search failed. Falling back to title search.")
            else: 
                self.log.info("No EAN provided. Using title search.")
                
            amazon_search_results = await self.extractor.search_by_title_using_search_bar(product_data["title"])
            
            if amazon_search_results and "error" not in amazon_search_results and amazon_search_results.get("results"):
                self.log.info(f"✅ Title search successful for '{product_data['title']}'")
                # Process title search results with existing logic
                best_result = None
                best_confidence = 0.0
                
                # Use configurable confidence threshold instead of hardcoded value
                matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
                min_confidence = matching_thresholds.get("title_similarity", 0.6)
                
                for result in amazon_search_results["results"][:3]:  # Check top 3 results
                    validation = self._validate_product_match(product_data, result)
                    confidence = validation.get("confidence", 0.0)
                    if confidence > best_confidence and confidence >= min_confidence:
                        best_confidence = confidence
                        best_result = result
                
                if best_result:
                    asin = best_result.get("asin")
                    if asin:
                        self.log.info(f"🎯 Title match found: {best_result.get('title')} (confidence: {best_confidence:.2f})")
                        amazon_product_data = await self.extractor.extract_data(asin)
                        if amazon_product_data:
                            amazon_product_data["_search_method_used"] = "title"
                            amazon_product_data["_match_confidence"] = best_confidence
                            return amazon_product_data
            else:
                self.log.warning(f"❌ Both EAN and title searches failed for '{product_data['title']}'")
                return None
        
        return amazon_product_data
        
        if supplier_ean:
            self.log.info(f"Attempting Amazon search using EAN: {supplier_ean}")
            self.results_summary["products_analyzed_ean"] += 1
            
            # FIX 2: Enhanced Amazon cache reuse logic - Check cache before scraping
            # First try to find cached data by EAN before performing any searches
            cached_data = None
            found_asin = None
            
            # PERFORMANCE OPTIMIZATION: Fast glob-based Amazon cache search using centralized path management
            amazon_cache_dir = str(path_manager.get_output_path("FBA_ANALYSIS", "amazon_cache"))
            if os.path.exists(amazon_cache_dir):
                # Method 1: Fast EAN-based filename search using glob
                ean_pattern = os.path.join(amazon_cache_dir, f"*{supplier_ean}*.json")
                ean_matches = glob.glob(ean_pattern)
                
                if ean_matches:
                    # Found EAN match in filename - read the first match
                    cache_file = os.path.basename(ean_matches[0])
                    try:
                        with open(ean_matches[0], 'r', encoding='utf-8') as f:
                            cached_data = json.load(f)
                            found_asin = cached_data.get("asin") or cached_data.get("asin_extracted_from_page")
                            self.log.info(f"📋 Found cached Amazon data for EAN {supplier_ean} in file: {cache_file} (fast search)")
                    except Exception as e:
                        self.log.debug(f"Error reading cache file {cache_file}: {e}")
                
                # 🚀 HASH OPTIMIZATION: Method 2 - If no EAN match found, try O(1) hash lookup for ASIN-based search
                if not found_asin and hasattr(self, 'hash_optimizer'):
                    existing_entry = self.hash_optimizer.get_entry_by_ean(supplier_ean)
                    if existing_entry:
                        asin = existing_entry.get('amazon_asin') or existing_entry.get('chosen_amazon_asin')
                        if asin:
                            self.log.debug(f"🚀 HASH LOOKUP: Found ASIN {asin} for EAN {supplier_ean} using O(1) lookup")
                            # Fast ASIN-based glob search
                            asin_pattern = os.path.join(amazon_cache_dir, f"amazon_{asin}_*.json")
                            asin_matches = glob.glob(asin_pattern)
                            if asin_matches:
                                cache_file = os.path.basename(asin_matches[0])
                                try:
                                    with open(asin_matches[0], 'r', encoding='utf-8') as f:
                                        cached_data = json.load(f)
                                        found_asin = cached_data.get("asin") or cached_data.get("asin_extracted_from_page")
                                        self.log.info(f"📋 Found cached Amazon data via linking map: EAN {supplier_ean} -> ASIN {asin} in file: {cache_file} (fast search)")
                                except Exception as e:
                                    self.log.debug(f"Error reading cache file {cache_file}: {e}")
                                        
                # OLD SLOW METHOD COMMENTED OUT - Performance improvement: 90%+ faster
                # The old method that was causing infinite loops:
                # for cache_file in os.listdir(amazon_cache_dir):  # SLOW: scans all files
                #     if cache_file.endswith(".json"):
                #         if supplier_ean in cache_file:  # SLOW: opens files to check EAN
                #             try:
                #                 with open(os.path.join(amazon_cache_dir, cache_file), 'r', encoding='utf-8') as f:
                #                     cached_data = json.load(f)
                #                     found_asin = cached_data.get("asin") or cached_data.get("asin_extracted_from_page")
                #                     self.log.info(f"📋 Found cached Amazon data for EAN {supplier_ean} in file: {cache_file}")
                #                     break
                #             except Exception as e:
                #                 self.log.debug(f"Error reading cache file {cache_file}: {e}")
            
            if cached_data:
                # 🚨 FIX: Validate cached data completeness before using it
                required_fields = ['current_price', 'price', 'original_price']
                has_price_data = any(field in cached_data and cached_data[field] is not None for field in required_fields)
                
                if has_price_data:
                    # Cached data is complete - use it
                    amazon_product_data = cached_data
                    actual_search_method = "EAN_cached"
                    self.log.info(f"✅ Using complete cached Amazon data for EAN {supplier_ean}")
                else:
                    # Cached data is incomplete - trigger fresh scraping
                    self.log.warning(f"⚠️ Cached data for EAN {supplier_ean} missing price fields. Triggering fresh scraping.")
                    amazon_product_data = await self.extractor.search_by_ean_and_extract_data(supplier_ean, product_data["title"])
                    # Don't hardcode method - let extractor set it based on what actually worked
                    search_method = amazon_product_data.get("_search_method_used") if amazon_product_data else None
                    if not search_method:
                        self.log.warning(f"🚨 MISSING SEARCH METHOD: No _search_method_used found for EAN {supplier_ean}")
                        self.log.warning(f"   This may indicate a bug in search method assignment")
                        actual_search_method = "UNKNOWN"  # Explicit unknown instead of dangerous default
                    else:
                        actual_search_method = search_method
            else:
                # No cache found - perform EAN search
                amazon_product_data = await self.extractor.search_by_ean_and_extract_data(supplier_ean, product_data["title"])
                # Don't hardcode method - let extractor set it based on what actually worked
                search_method = amazon_product_data.get("_search_method_used") if amazon_product_data else None
                if not search_method:
                    self.log.warning(f"🚨 MISSING SEARCH METHOD: No _search_method_used found for EAN {supplier_ean}")
                    self.log.warning(f"   This may indicate a bug in search method assignment")
                    actual_search_method = "UNKNOWN"  # Explicit unknown instead of dangerous default
                else:
                    actual_search_method = search_method
            
            if amazon_product_data and "error" not in amazon_product_data:
                # EAN search succeeded (or we used cached data)
                found_asin = amazon_product_data.get("asin") or amazon_product_data.get("asin_extracted_from_page")
                
                if found_asin and actual_search_method != "EAN_cached":
                    # For fresh EAN search results, check if we need to copy to EAN-specific cache file
                    # Keep the actual search method as determined by the extractor
                    pass  # Don't override actual_search_method here
                elif not found_asin:
                    actual_search_method = "EAN"  # EAN search succeeded but no ASIN found
                
                # FIX 1: EAN search successful - skip title search completely
                self.log.info(f"✅ EAN search successful for {supplier_ean}. Using EAN result without title fallback.")
                
                # Add search method info and return immediately to prevent title search
                amazon_product_data["_search_method_used"] = actual_search_method
                return amazon_product_data
            else:
                amazon_product_data = None # Reset if EAN search failed
                self.log.info(f"❌ EAN search failed for {supplier_ean}. Will fall back to title search.")
                
        if not amazon_product_data:
            if supplier_ean: self.log.info("EAN search failed. Falling back to title search.")
            else: self.log.info("No EAN. Using title search.")
            self.results_summary["products_analyzed_title"] += 1
            amazon_search_results = await self.extractor.search_by_title_using_search_bar(product_data["title"])
            if not amazon_search_results or "error" in amazon_search_results or not amazon_search_results.get("results"):
                # 🚨 SURGICAL FIX #4: ENHANCED SEARCH FALLBACK
                # Improve error handling without replacing existing working logic
                error_detail = amazon_search_results.get("error") if isinstance(amazon_search_results, dict) else "No results returned"
                self.log.warning(f"No Amazon results for title '{product_data['title']}'. Error: {error_detail}")
                
                # 🚀 ENHANCEMENT: Try simplified title search if original fails
                if product_data.get('title') and len(product_data['title']) > 10:
                    # Extract first few meaningful words for simplified search
                    simplified_title = ' '.join(product_data['title'].split()[:4])  # First 4 words
                    self.log.info(f"🔄 FALLBACK: Trying simplified title search: '{simplified_title}'")
                    
                    simplified_results = await self.extractor.search_by_title_using_search_bar(simplified_title)
                    if simplified_results and "error" not in simplified_results and simplified_results.get("results"):
                        self.log.info(f"✅ SIMPLIFIED SEARCH SUCCESS: Found {len(simplified_results['results'])} results")
                        amazon_search_results = simplified_results
                    else:
                        self.log.warning(f"💫 SIMPLIFIED SEARCH ALSO FAILED: No results for simplified title '{simplified_title}'")
                        return None
                else:
                    return None
                
            best_result = None
            best_confidence = 0.0
            
            # Use configurable confidence threshold instead of hardcoded value
            matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
            confidence_threshold = matching_thresholds.get("medium_title_similarity", 0.5)  # More conservative than old 0.4
            
            self.log.info(f"🔍 PRODUCT VALIDATION: Evaluating {len(amazon_search_results['results'])} Amazon results for '{product_data['title']}'")
            
            for i, result in enumerate(amazon_search_results["results"][:5]):  # Check top 5 results
                # Use existing _validate_product_match method (now fixed)
                amazon_product_data = {"title": result.get("title", "")}
                validation = self._validate_product_match(product_data, amazon_product_data)
                
                confidence = validation.get("confidence", 0.0)
                match_quality = validation.get("match_quality", "low")
                overlap_score = validation.get("title_overlap_score", 0.0)
                
                self.log.info(f"📊 Result {i+1}: ASIN {result.get('asin')} - Confidence: {confidence:.3f} ({match_quality}) - Overlap: {overlap_score:.3f} - '{result.get('title', 'No title')[:60]}...'")
                
                if confidence > best_confidence and confidence >= confidence_threshold:
                    best_confidence = confidence
                    best_result = result
            
            if not best_result:
                # 🚨 SURGICAL FIX #4: ENHANCED NO-MATCH HANDLING
                self.log.warning(f"🚨 NO CONFIDENT MATCH: All Amazon results below {confidence_threshold:.1%} confidence threshold for '{product_data['title']}'. Skipping to prevent irrational matches.")
                
                # 🚀 ENHANCEMENT: Log detailed analysis for debugging
                self.log.info(f"📊 CONFIDENCE ANALYSIS SUMMARY:")
                self.log.info(f"   🎯 Threshold: {confidence_threshold:.1%}")
                self.log.info(f"   📈 Best confidence achieved: {best_confidence:.1%}")
                self.log.info(f"   📉 Results analyzed: {len(amazon_search_results['results'][:5])}")
                
                # 💫 ADDITIONAL FALLBACK: Try with even more simplified title if confidence is close
                if best_confidence > (confidence_threshold * 0.8):  # Within 80% of threshold
                    # Extract brand or key product identifier
                    title_words = product_data['title'].split()
                    if len(title_words) >= 2:
                        brand_search = title_words[0]  # Assume first word is brand
                        self.log.info(f"🎯 BRAND FALLBACK: Trying brand-only search: '{brand_search}'")
                        
                        brand_results = await self.extractor.search_by_title_using_search_bar(brand_search)
                        if brand_results and "error" not in brand_results and brand_results.get("results"):
                            # Quick confidence check on brand results
                            for result in brand_results["results"][:3]:  # Check top 3 brand results
                                amazon_product_data = {"title": result.get("title", "")}
                                validation = self._validate_product_match(product_data, amazon_product_data)
                                if validation.get("confidence", 0.0) >= confidence_threshold:
                                    self.log.info(f"✅ BRAND SEARCH SUCCESS: Found match with {validation.get('confidence', 0.0):.1%} confidence")
                                    best_result = result
                                    best_confidence = validation.get("confidence", 0.0)
                                    break
                
                if not best_result:
                    return None
            
            self.log.info(f"✅ BEST MATCH: ASIN {best_result.get('asin')} with {best_confidence:.1%} confidence")
            asin = best_result.get("asin")
            if not asin:
                self.log.warning(f"Could not determine ASIN for '{product_data['title']}'. Skipping.")
                return None
            
            # ENHANCEMENT: Check Amazon cache before scraping
            amazon_product_data = self._check_amazon_cache_by_asin(asin, supplier_ean)
            
            if amazon_product_data:
                # Cache hit - use cached data
                actual_search_method = "title_cached"
                self.log.info(f"📋 Using cached Amazon data for ASIN {asin}")
            else:
                # Cache miss - perform fresh extraction
                amazon_product_data = await self.extractor.extract_data(asin)
                if amazon_product_data and "error" not in amazon_product_data:
                    actual_search_method = "title"  # Title search succeeded
                
        if not amazon_product_data or "error" in amazon_product_data:
            self.log.warning(f"Failed to get valid Amazon data for '{product_data['title']}'. Skipping.")
            self.results_summary["errors"] += 1
            return None
            
        # Add search method info to the returned data for accurate linking map creation
        amazon_product_data["_search_method_used"] = actual_search_method
        return amazon_product_data

    def _save_final_report(self, profitable_results: List[Dict[str, Any]], supplier_name: str):
        """Generate CSV financial report using FBA_Financial_calculator."""
        self.log.info(f"🔍 DEBUG: _save_final_report called with {len(profitable_results) if profitable_results else 0} profitable results")
        
        # Always call FBA_Financial_calculator to generate CSV report regardless of profitable_results
        # The calculator will process linking_map and generate comprehensive financial analysis
        try:
            self.log.info("📊 Calling FBA_Financial_calculator.run_calculations to generate CSV financial report...")
            
            # Call run_calculations with supplier_name to generate CSV report
            run_calculations(supplier_name)
            
            self.log.info("✅ Financial report CSV generation completed successfully")
            
        except Exception as e:
            self.log.error(f"❌ CRITICAL: Error generating financial report CSV: {e}", exc_info=True)

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _run_hybrid_processing_mode(self, supplier_url: str, supplier_name: str, 
                                         category_urls_to_scrape: List[str], 
                                         max_products_per_category: int, max_products_to_process: int,
                                         max_analyzed_products: int, max_products_per_cycle: int, 
                                         supplier_extraction_batch_size: int) -> List[Dict[str, Any]]:
        """
        Hybrid processing mode that allows switching between supplier extraction and Amazon analysis.
        Supports chunked, sequential, and balanced processing modes.
        """
        profitable_results: List[Dict[str, Any]] = []
        full_config = self.config_loader._config
        hybrid_config = full_config.get("hybrid_processing", {})
        processing_modes = hybrid_config.get("processing_modes", {})
        switch_after_categories = hybrid_config.get("switch_to_amazon_after_categories")
        
        self.log.info(f"🔄 HYBRID PROCESSING: Mode configuration loaded")
        self.log.info(f"   switch_to_amazon_after_categories: {switch_after_categories}")
        
        if processing_modes.get("chunked", {}).get("enabled", False):
            # Chunked mode: Alternate between supplier extraction and Amazon analysis
            chunk_size = processing_modes.get("chunked", {}).get("chunk_size_categories")
            if not chunk_size:
                self.log.error("❌ CONFIGURATION ERROR: chunk_size_categories not found in hybrid_processing.processing_modes.chunked")
                return profitable_results
            
            self.log.info(f"🔄 HYBRID MODE: Chunked processing (chunk size: {chunk_size} categories)")
            

            # Process categories in chunks
            for chunk_start in range(0, len(category_urls_to_scrape), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(category_urls_to_scrape))
                chunk_categories = category_urls_to_scrape[chunk_start:chunk_end]
                
                self.log.info(f"🔄 Processing chunk {chunk_start//chunk_size + 1}: categories {chunk_start+1}-{chunk_end}")
                
                chunk_products = await self._extract_supplier_products(
                    supplier_url, supplier_name, chunk_categories,
                    max_products_per_category, max_products_to_process, supplier_extraction_batch_size
                )

                if chunk_products:
                    actual_cache_file, _ = self._find_actual_supplier_cache_file(supplier_name)
                    cached_products: List[Dict[str, Any]] = []
                    if actual_cache_file:
                        try:
                            with open(actual_cache_file, 'r', encoding='utf-8') as fh:
                                cached_products = json.load(fh)
                        except Exception as e:
                            self.log.warning(f"⚠️ Could not read supplier cache: {e}")

                    # Sequential category processing: complete supplier → Amazon for each category before advancing
                    for idx_offset, category_url in enumerate(chunk_categories):
                        # 🚨 Track category processing start time for summary logging
                        self._category_start_time = datetime.now()
                        
                        urls = self.category_manifests.get(category_url, [])
                        # Set category index for manifest logging
                        category_index = chunk_start + idx_offset + 1
                        self._set_current_category_index(category_index)
                        
                        # 🚨 CRITICAL FIX: Generate atomic manifest BEFORE filtering (authoritative bridge)
                        try:
                            self._save_category_manifest(supplier_name, category_url, urls)
                            self.log.debug(f"📝 MANIFEST: Successfully saved manifest for category {category_index} before filtering")
                        except Exception as e:
                            self.log.error(f"❌ MANIFEST ERROR: Failed to save manifest for category {category_index}: {e}")
                            # Continue processing but log the failure
                            
                        # 🚨 LEGACY FILTERING PATH REMOVED - Now using the new pre-extraction filtering from lines 3907-3975
                        # This prevents double URL extraction and conflicting filtering decisions
                        # 🚨 PERMANENT REMOVAL: Legacy filtering approach permanently disabled
                        # DO NOT RE-INTEGRATE: This legacy filtering code has been permanently removed
                        # because it conflicts with the new 2-step pre-extraction filtering.
                        # 
                        # The new filtering correctly handles (per project memory specification):
                        # 1. SKIP_ENTIRELY: Products in linking map (fully processed)
                        # 2. NEEDS_AMAZON_ONLY: Products in cache but not linking map  
                        # 3. NEEDS_FULL_EXTRACTION: Products in neither file
                        # 
                        # Legacy approach was causing:
                        # - Double URL extraction
                        # - Filter bypass due to missing load_linking_map_urls method
                        # - Processing all 59 URLs despite filter saying only 5 needed
                        # 
                        # All filtering is now handled in the pre-extraction phase (lines 3907-3975).
                        # If debugging is needed, check the pre-extraction filtering logs:
                        # - "🔗 DETAILED PRE-EXTRACTION FILTERING: Analyzing X collected URLs"
                        # - "🔗 STEP 1 - LINKING MAP CHECK: X complete (skipped)"
                        # - "💾 STEP 2 - PRODUCT CACHE CHECK: X have supplier data; X need supplier extraction"
                        
                        # Skip legacy filtering entirely - use pre-extraction results
                        self.log.info(f"⚡ LEGACY FILTER BYPASSED: Using pre-extraction filter results for chunk {chunk_start + 1}")
                        continue  # Move to next chunk/category

    def _validate_filter_invariant(self, input_urls: List[str], filtered: Dict[str, List[str]], 
                                  category_index: int = None, slug: str = None) -> None:
        """
        🚨 CRITICAL FIX: Validate filter invariant and log results per project specification.
        Ensures that filter logic correctly accounts for all input URLs.
        
        Args:
            input_urls: Original list of URLs to filter
            filtered: Result from filter_urls() containing skip_entirely, needs_amazon_only, needs_full_extraction
            category_index: Category index for logging context
            slug: Category slug for logging context
        
        Raises:
            RuntimeError: If filter invariant is violated (data integrity compromised)
        """
        skip_count = len(filtered['skip_entirely'])
        amazon_count = len(filtered['needs_amazon_only'])
        full_count = len(filtered['needs_full_extraction'])
        total_input = len(input_urls)
        total_output = skip_count + amazon_count + full_count
        
        # Enhanced logging with filter transparency - removed to avoid duplication
        # Main filter transparency logs appear in hybrid workflow (lines 4472-4474)
        context = f"[C{category_index} {slug}]" if category_index and slug else "[Filter]"
        
        # 🚨 CRITICAL INVARIANT VALIDATION per project memory requirement
        if total_input != total_output:
            self.log.error(f"❌ FILTER INVARIANT VIOLATION: in={total_input} != out={total_output}")
            self.log.error(f"   skip={skip_count} + amz_only={amazon_count} + full={full_count} = {total_output}")
            self.log.error(f"   This indicates a bug in the filtering logic - data integrity compromised")
            
            # Detailed debugging information
            difference = total_input - total_output
            self.log.error(f"   Difference: {difference} products {'missing' if difference > 0 else 'extra'}")
            
            # This is a critical data integrity issue - raise exception
            raise RuntimeError(f"Filter invariant violation in {context}: data integrity compromised")
        else:
            # Project specification format: "🧮 Filter Invariant: in=<N> == skip=<A> + amz_only=<B> + full=<C>"
            self.log.info(f"🧮 Filter Invariant: in={total_input} == skip={skip_count} + amz_only={amazon_count} + full={full_count}")
            
            # Compact logging for backward compatibility
            self.log.info(
                f"FILTER{context}: in={total_input} "
                f"skip={skip_count} "
                f"needs_amz={amazon_count} "
                f"needs_full={full_count}"
            )
            
    def _log_category_summary(self, category_index: int, category_url: str, 
                             discovered_count: int, skip_count: int, 
                             amazon_count: int, full_count: int, 
                             start_time: datetime, profitable_count: int = 0) -> None:
        """
        📊 Log comprehensive category completion summary per project specification.
        Required by project memory: "00d39165-8042-4d53-b3c2-0d1591864be4"
        
        Args:
            category_index: Absolute category index (1-based for user display)
            category_url: Category URL being processed
            discovered_count: Total products discovered (frozen denominator)
            skip_count: Products skipped due to linking map
            amazon_count: Products requiring Amazon-only analysis
            full_count: Products requiring full extraction
            start_time: Category processing start time
            profitable_count: Number of profitable products found
        """
        try:
            # Generate category slug for consistent logging
            slug = re.sub(r"[^a-z0-9]+", "-", category_url.lower()).strip("-")[:30]
            duration = datetime.now() - start_time
            
            # 🚨 PROJECT MEMORY COMPLIANCE: Structured category summary format
            self.log.info(f"📊 CATEGORY SUMMARY[C{category_index} {slug}]")
            self.log.info(f"  discovered (frozen) : {discovered_count}")
            self.log.info(f"  skipped (LM)        : {skip_count}")
            self.log.info(f"  amazon_only (cache) : {amazon_count}")
            self.log.info(f"  full_extraction     : {full_count}")
            self.log.info(f"  profitable_found    : {profitable_count}")
            self.log.info(f"  duration            : {duration}")
            
            # Additional metrics for analysis
            if discovered_count > 0:
                skip_percentage = (skip_count / discovered_count) * 100
                processing_percentage = ((amazon_count + full_count) / discovered_count) * 100
                self.log.info(f"  efficiency          : {skip_percentage:.1f}% skipped, {processing_percentage:.1f}% processed")
                
            if amazon_count + full_count > 0:
                profitability_rate = (profitable_count / (amazon_count + full_count)) * 100
                self.log.info(f"  profitability_rate  : {profitability_rate:.1f}% ({profitable_count}/{amazon_count + full_count})")
                
        except Exception as e:
            self.log.error(f"❌ CATEGORY SUMMARY ERROR: Failed to log summary for category {category_index}: {e}")
            
    def _validate_resume_point(self, resume_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        🚨 CRITICAL: Validate resume point integrity with hard guards per project specification.
        Required by project memory for safe resumption without corruption.
        
        Args:
            resume_data: State data for resumption validation
            
        Returns:
            Tuple of (is_valid, error_list) where is_valid is bool and error_list contains validation failures
        """
        errors = []
        sp = resume_data.get("system_progression", {})
        
        try:
            # 🚨 CRITICAL: Validate required fields exist
            required_fields = ["current_phase", "current_category_index", "current_product_index_in_category"]
            for field in required_fields:
                if field not in sp:
                    errors.append(f"Missing required field: {field}")
            
            # 🚨 CRITICAL: Validate field types and bounds
            current_category_index = sp.get("current_category_index", -1)
            current_product_index = sp.get("current_product_index_in_category", -1)
            total_categories = sp.get("total_categories", 0)
            total_products = sp.get("total_products_in_current_category", 0)
            
            # Validate category bounds
            if current_category_index < 0:
                errors.append(f"Invalid current_category_index: {current_category_index} (must be >= 0)")
            elif total_categories > 0 and current_category_index >= total_categories:
                errors.append(f"Category index out of bounds: {current_category_index} >= {total_categories}")
            
            # Validate product bounds
            if current_product_index < 0:
                errors.append(f"Invalid current_product_index_in_category: {current_product_index} (must be >= 0)")
            elif total_products > 0 and current_product_index > total_products:
                errors.append(f"Product index out of bounds: {current_product_index} > {total_products}")
            
            # 🚨 CRITICAL: Validate phase consistency
            current_phase = sp.get("current_phase", "")
            valid_phases = ["supplier", "amazon_analysis", "financial_analysis", "complete"]
            if current_phase not in valid_phases:
                errors.append(f"Invalid phase: {current_phase} (must be one of {valid_phases})")
            
            # 🚨 CRITICAL: Cross-validate with file system state
            current_category_url = sp.get("current_category_url", "")
            if current_category_url:
                # Check if category manifests exist for consistency
                try:
                    slug = re.sub(r"[^a-z0-9]+", "-", current_category_url.lower()).strip("-")[:30]
                    manifest_path = Path("OUTPUTS") / "manifests" / "poundwholesale.co.uk" / f"{slug}.json"
                    if not manifest_path.exists():
                        self.log.warning(f"⚠️ RESUME INTEGRITY: Manifest missing for current category {current_category_url}")
                        # This is a warning, not an error - we can continue without the manifest
                except Exception as manifest_error:
                    self.log.warning(f"⚠️ RESUME INTEGRITY: Could not check manifest: {manifest_error}")
            
            # 🚨 CRITICAL: Validate timestamp integrity
            last_updated = sp.get("last_updated", "")
            if last_updated:
                try:
                    from datetime import datetime, timezone
                    last_update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    time_since_update = datetime.now(timezone.utc) - last_update_time
                    
                    # Warn if resume point is very old (>24 hours)
                    if time_since_update.total_seconds() > 86400:  # 24 hours
                        hours_old = time_since_update.total_seconds() / 3600
                        self.log.warning(f"⚠️ RESUME INTEGRITY: Resume point is {hours_old:.1f} hours old")
                        
                except Exception as time_error:
                    errors.append(f"Invalid timestamp format: {last_updated}")
            
            # 🚨 CRITICAL: Log validation results
            if errors:
                self.log.error(f"❌ RESUME VALIDATION FAILED: {len(errors)} integrity errors found")
                for error in errors:
                    self.log.error(f"   - {error}")
                return False, errors
            else:
                self.log.info(f"✅ RESUME VALIDATION PASSED: Resume point integrity confirmed")
                self.log.info(f"   Phase: {current_phase}, Category: {current_category_index}/{total_categories}, Product: {current_product_index}/{total_products}")
                return True, []
                
        except Exception as e:
            error_msg = f"Resume validation exception: {e}"
            errors.append(error_msg)
            self.log.error(f"❌ RESUME VALIDATION ERROR: {error_msg}")
            return False, errors

    def _check_financial_report_trigger(self, supplier_name: str) -> bool:
        """
        🚨 CRITICAL FIX: Financial Report Triggering Mechanism - Monitor linking map count as TRIGGER
        Returns True if financial report was triggered, False otherwise
        """
        financial_batch_size = self.config_loader.get_financial_batch_size()
        if not financial_batch_size:
            self.log.error("❌ CONFIGURATION ERROR: financial_report_batch_size not found in system config")
            return False
        
        current_linking_map_count = len(self.linking_map)
        
        # ✅ CORRECTED LOGIC: financial_report_batch_size is TRIGGER MECHANISM (every N linking map entries)
        if current_linking_map_count > 0 and current_linking_map_count % financial_batch_size == 0:
            try:
                self.log.info(f"🚨 FINANCIAL REPORT TRIGGER: Reached {current_linking_map_count} linking map entries (trigger every {financial_batch_size})")
                from tools.FBA_Financial_calculator import run_calculations
                financial_results = run_calculations(supplier_name)
                if financial_results and financial_results.get('statistics', {}).get('output_file'):
                    self.log.info(f"✅ Financial report EXECUTED: {financial_results['statistics']['output_file']}")
                else:
                    self.log.warning("⚠️ Financial report executed but no file path returned")
                return True
            except ImportError as ie:
                self.log.error(f"❌ Could not import FBA_Financial_calculator: {ie}")
            except Exception as e:
                self.log.error(f"❌ Error executing financial report: {e}")
        elif current_linking_map_count > 0:
            next_trigger_count = ((current_linking_map_count // financial_batch_size) + 1) * financial_batch_size
            self.log.info(f"💡 FINANCIAL REPORT TRIGGER: Next trigger at {next_trigger_count} linking map entries (current: {current_linking_map_count}, trigger frequency: {financial_batch_size})")
        
        return False
    
    async def _run_hybrid_processing_mode(self, supplier_url: str, supplier_name: str, 
                                         category_urls_to_scrape: List[str], 
                                         max_products_per_category: int, max_products_to_process: int,
                                         max_analyzed_products: int, max_products_per_cycle: int, 
                                         supplier_extraction_batch_size: int) -> List[Dict[str, Any]]:
        """
        Hybrid processing mode that allows switching between supplier extraction and Amazon analysis.
        Supports chunked, sequential, and balanced processing modes.
        """
        profitable_results: List[Dict[str, Any]] = []
        full_config = self.config_loader._config
        hybrid_config = full_config.get("hybrid_processing", {})
        processing_modes = hybrid_config.get("processing_modes", {})
        switch_after_categories = hybrid_config.get("switch_to_amazon_after_categories")
        
        self.log.info(f"🔄 HYBRID PROCESSING: Mode configuration loaded")
        self.log.info(f"   switch_to_amazon_after_categories: {switch_after_categories}")
        
        if processing_modes.get("chunked", {}).get("enabled", False):
            # Chunked mode: Alternate between supplier extraction and Amazon analysis
            chunk_size = processing_modes.get("chunked", {}).get("chunk_size_categories")
            if not chunk_size:
                self.log.error("❌ CONFIGURATION ERROR: chunk_size_categories not found in hybrid_processing.processing_modes.chunked")
                return profitable_results
            
            self.log.info(f"🔄 HYBRID MODE: Chunked processing (chunk size: {chunk_size} categories)")
            
            # Process categories in chunks
            for chunk_start in range(0, len(category_urls_to_scrape), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(category_urls_to_scrape))
                chunk_categories = category_urls_to_scrape[chunk_start:chunk_end]
                
                self.log.info(f"🔄 Processing chunk {chunk_start//chunk_size + 1}: categories {chunk_start+1}-{chunk_end}")
                
                # Extract from this chunk of categories
                chunk_products = await self._extract_supplier_products(
                    supplier_url, supplier_name, chunk_categories, 
                    max_products_per_category, max_products_to_process, supplier_extraction_batch_size
                )
                
                if chunk_products:
                    # Immediately analyze these products
                    # Use the same detailed processing logic as main workflow
                    chunk_results = await self._process_chunk_with_main_workflow_logic(
                        chunk_products, max_products_per_cycle, category_urls=category_urls_to_scrape
                    )
                    profitable_results.extend(chunk_results)
                    
                    # Check memory management
                    memory_config = hybrid_config.get("memory_management", {})
                    if memory_config.get("clear_cache_between_phases", False):
                        self.log.info("🧹 Clearing cache between processing phases")
                        # Add cache clearing logic here if needed
                
        elif processing_modes.get("balanced", {}).get("enabled", False):
            # Balanced mode: Extract in batches, analyze each batch
            self.log.info(f"🔄 HYBRID MODE: Balanced processing")
            
            # Extract all products first
            all_products = await self._extract_supplier_products(
                supplier_url, supplier_name, category_urls_to_scrape, 
                max_products_per_category, max_products_to_process, supplier_extraction_batch_size
            )
            
            if all_products:
                # Process in analysis batches if enabled
                if processing_modes.get("balanced", {}).get("analysis_after_extraction_batch", True):
                    batch_size = max_products_per_cycle
                    for batch_start in range(0, len(all_products), batch_size):
                        batch_end = min(batch_start + batch_size, len(all_products))
                        batch_products = all_products[batch_start:batch_end]
                        
                        self.log.info(f"🔄 Analyzing batch {batch_start//batch_size + 1}: products {batch_start+1}-{batch_end}")
                        # Use the same detailed processing logic as main workflow
                        batch_results = await self._process_chunk_with_main_workflow_logic(
                            batch_products, max_products_per_cycle
                        )
                        profitable_results.extend(batch_results)
                else:
                    # Analyze all products at once
                    # Use the same detailed processing logic as main workflow
                    profitable_results = await self._process_chunk_with_main_workflow_logic(
                        all_products, max_products_per_cycle
                    )
        else:
            # Sequential mode (default): Complete supplier extraction, then Amazon analysis
            self.log.info(f"🔄 HYBRID MODE: Sequential processing (extract all, then analyze all)")
            
            # Standard sequential processing - extract all first
            all_products = await self._extract_supplier_products(
                supplier_url, supplier_name, category_urls_to_scrape, 
                max_products_per_category, max_products_to_process, supplier_extraction_batch_size
            )
            
            if all_products:
                profitable_results = await self._analyze_products_batch(
                    all_products, supplier_name, max_products_per_cycle
                )
        
        try:
            # Save linking map with all collected entries
            self._save_linking_map(supplier_name)
            self.log.info("✅ Hybrid mode: Linking map save completed")
            
            # Save final report of profitable products  
            self._save_final_report(profitable_results, supplier_name)
            self.log.info("✅ Hybrid mode: Final report save completed")
            
            # Save processing state
            self.state_manager.save_state(preserve_interruption_state=True)
            self.log.info("--- Hybrid Processing Mode Finished ---")
            
        except Exception as save_error:
            self.log.error(f"❌ CRITICAL: Error during final save operations in hybrid mode: {save_error}", exc_info=True)
        
        return profitable_results

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    def _combine_data(self, supplier_data: Dict[str, Any], amazon_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Combine supplier and Amazon data and calculate financial metrics."""
        combined = {
            "supplier_product_info": supplier_data,
            "amazon_product_info": amazon_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        # Financial calculation is now handled within the main run loop before this function is called
        # This function is primarily for combining data and adding match validation
        match_validation = self._validate_product_match(supplier_data, amazon_data)
        combined["match_validation"] = match_validation
        return combined

    def _overlap_score(self, title_a: str, title_b: str) -> float:
        """Calculate word overlap score between two titles"""
        a = set(re.sub(r'[^\w\s]', ' ', title_a.lower()).split())
        b = set(re.sub(r'[^\w\s]', ' ', title_b.lower()).split())
        return len(a & b) / max(1, len(a))
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize product title for use in filename"""
        if not title:
            return "unknown_title"
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length to 50 chars

    def _validate_product_match(self, supplier_product: Dict[str, Any], amazon_product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the match between supplier and Amazon products using configurable thresholds."""
        matching_thresholds = self.system_config.get("performance", {}).get("matching_thresholds", {})
        
        # Get configurable thresholds with fallback to more conservative defaults
        title_similarity_threshold = matching_thresholds.get("title_similarity", 0.25)
        medium_title_similarity = matching_thresholds.get("medium_title_similarity", 0.5) 
        high_title_similarity = matching_thresholds.get("high_title_similarity", 0.75)
        
        title_overlap_score = self._overlap_score(supplier_product.get("title", ""), amazon_product.get("title", ""))

        match_quality = "low"
        confidence = 0.0
        
        # Use configurable thresholds - much more strict than previous hardcoded values
        if title_overlap_score >= high_title_similarity:
            match_quality = "high"
            confidence = 0.9
        elif title_overlap_score >= medium_title_similarity:
            match_quality = "medium"
            confidence = 0.6
        elif title_overlap_score >= title_similarity_threshold:
            match_quality = "low"
            confidence = 0.3
        else:
            match_quality = "very_low"
            confidence = 0.1

        self.log.debug(f"🔍 MATCH VALIDATION: '{supplier_product.get('title', 'Unknown')}' vs '{amazon_product.get('title', 'Unknown')}' = {title_overlap_score:.2f} ({match_quality}, {confidence:.1%})")
        
        return {"match_quality": match_quality, "confidence": confidence, "title_overlap_score": title_overlap_score}

    def _is_product_meeting_criteria(self, combined_data: Dict[str, Any]) -> bool:
        """Check if a product meets all defined business criteria."""
        # This function is now largely redundant as profitability checks are done in the main loop.
        # However, it can be used for other criteria like sales rank, reviews, etc.
        amazon_data = combined_data.get("amazon_product_info", {})
        financials = combined_data.get("financials", {})
        # Check profitability (already done, but for completeness)
        is_profitable = financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT
        # Check Amazon listing quality
        meets_rating = amazon_data.get("rating", 0) >= MIN_RATING
        meets_reviews = amazon_data.get("reviews", 0) >= MIN_REVIEWS
        meets_sales_rank = amazon_data.get("sales_rank", MAX_SALES_RANK + 1) <= MAX_SALES_RANK
        # Check for battery products (using the helper function)
        is_battery = is_battery_title(amazon_data.get("title", "")) or is_battery_title(combined_data["supplier_product_info"].get("title", ""))
        # Check for other non-FBA friendly keywords
        is_non_fba_friendly = any(k in amazon_data.get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS) or \
                              any(k in combined_data["supplier_product_info"].get("title", "").lower() for k in NON_FBA_FRIENDLY_KEYWORDS)
        # All criteria must be met
        return is_profitable and meets_rating and meets_reviews and meets_sales_rank and not is_battery and not is_non_fba_friendly

    def _apply_batch_synchronization(self, max_products_per_cycle: int, 
                                   supplier_extraction_batch_size: int,
                                   batch_sync_config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Apply batch synchronization to align all batch sizes consistently.
        Returns updated max_products_per_cycle and supplier_extraction_batch_size.
        """
        target_batch_size = batch_sync_config.get("target_batch_size", 3)
        synchronize_all = batch_sync_config.get("synchronize_all_batch_sizes", False)
        validation_config = batch_sync_config.get("validation", {})
        
        self.log.info(f"🔄 BATCH SYNCHRONIZATION: Enabled")
        self.log.info(f"   target_batch_size: {target_batch_size}")
        self.log.info(f"   synchronize_all_batch_sizes: {synchronize_all}")
        
        original_values = {
            "max_products_per_cycle": max_products_per_cycle,
            "supplier_extraction_batch_size": supplier_extraction_batch_size,
            "linking_map_batch_size": self.system_config.get("linking_map_batch_size", 1),
            "financial_report_batch_size": self.config_loader.get_financial_batch_size()
        }
        
        # Check for mismatched sizes and warn if configured
        if validation_config.get("warn_on_mismatched_sizes", True):
            unique_sizes = set(original_values.values())
            if len(unique_sizes) > 1:
                self.log.warning(f"⚠️ BATCH SYNC WARNING: Mismatched batch sizes detected: {original_values}")
                self.log.warning(f"   Unique sizes found: {sorted(unique_sizes)}")
        
        if synchronize_all:
            # Synchronize all batch sizes to target
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            # Also update system config values in memory for consistency
            if "system" in self.system_config:
                self.system_config["max_products_per_cycle"] = target_batch_size
                self.system_config["supplier_extraction_batch_size"] = target_batch_size
                self.system_config["linking_map_batch_size"] = target_batch_size
                # financial_report_batch_size managed by config_loader
            
            self.log.info(f"✅ BATCH SYNC: All batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
            
        else:
            # Only synchronize the two main processing batch sizes
            new_max_products_per_cycle = target_batch_size
            new_supplier_extraction_batch_size = target_batch_size
            
            self.log.info(f"✅ BATCH SYNC: Main processing batch sizes synchronized to {target_batch_size}")
            self.log.info(f"   Updated values: max_products_per_cycle={new_max_products_per_cycle}, supplier_extraction_batch_size={new_supplier_extraction_batch_size}")
        
        return new_max_products_per_cycle, new_supplier_extraction_batch_size

    async def _analyze_products_batch(self, products: List[Dict[str, Any]], 
                                    supplier_name: str, max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Analyze a batch of supplier products for Amazon matching and profitability."""
        profitable_results = []
        
        # Filter and prepare products for analysis
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        self.log.info(f"🔍 Analyzing {len(price_filtered_products)} products in batch mode")
        
        # Process products in cycles
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            self.log.info(f"🔄 Processing analysis batch {batch_num + 1}/{total_batches} ({len(batch_products)} products)")
            
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"🔍 Analyzing product {current_index}: '{product_data.get('title')}'")
                
                # Check if already processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue
                
                # Amazon data extraction and analysis
                amazon_data = await self._get_amazon_data(product_data)
                if not amazon_data or "error" in amazon_data:
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # 🚨 FIX: Create no-match linking entry for batch processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Batch processing - Amazon search failed: {error_info}"
                    
                    # Create no-match linking entry
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title"),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",  # NEW: Indicates no match found
                        "confidence": 0,    # NEW: No confidence for failed matches
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason  # NEW: Audit trail explaining why no match
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for batch product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                    continue
                
                # Save Amazon cache and create linking map
                supplier_ean = product_data.get("ean") or product_data.get("barcode")
                asin = amazon_data.get("asin", "NO_ASIN")
                
                # Save Amazon data
                filename_identifier = supplier_ean if supplier_ean else re.sub(r'[<>:"/\\|?*\s]+', '_', product_data.get("title", "NO_TITLE")[:50])
                amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{asin}_{filename_identifier}.json"))
                with open(amazon_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(amazon_data, f, indent=2, ensure_ascii=False)
                
                # Financial analysis
                try:
                    # Already imported at top of file: from FBA_Financial_calculator import financials as calc_financials
                    supplier_price = float(product_data.get("price", 0))
                    current_price = amazon_data.get("current_price", 0)
                    
                    if supplier_price > 0 and current_price > 0:
                        financials = calc_financials(
                            supplier_price=supplier_price,
                            amazon_price=current_price,
                            amazon_sales_rank=amazon_data.get("sales_rank", 999999),
                            amazon_rating=amazon_data.get("rating", 0),
                            amazon_review_count=amazon_data.get("reviews", 0)
                        )
                        
                        # Check profitability
                        if financials.get("ROI", 0) > MIN_ROI_PERCENT and financials.get("NetProfit", 0) > MIN_PROFIT_PER_UNIT:
                            self.log.info(f"✅ PROFITABLE: ROI {financials['ROI']:.1f}%, Profit £{financials['NetProfit']:.2f}")
                            
                            combined_data = self._combine_supplier_amazon_data(product_data, amazon_data, "hybrid_batch")
                            combined_data["financials"] = financials
                            profitable_results.append(combined_data)
                            
                            self.state_manager.update_success_metrics(True, True, financials.get("NetProfit", 0))
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                        else:
                            self.log.info(f"Not profitable: ROI {financials.get('ROI', 0):.1f}%, Profit £{financials.get('NetProfit', 0):.2f}")
                            self.state_manager.update_success_metrics(True, False)
                            self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                            
                except Exception as e:
                    self.log.error(f"Financial calculation failed: {e}")
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
        
        return profitable_results

    def _get_cached_products_path(self, category_url: str):
        """Helper to get the path for a category's product cache file."""
        category_filename = f"{self.supplier_name}_{category_url.split('/')[-1]}_products.json"
        return str(path_manager.get_cache_path('supplier_cache', category_filename))

    # Removed duplicate _load_linking_map method - using the one at line 1354



    async def _process_chunk_with_main_workflow_logic(self, products: List[Dict[str, Any]], max_products_per_cycle: int, *, category_urls) -> List[Dict[str, Any]]:
        """Process products using the same detailed logic as main workflow (not simplified batch processing)"""
        profitable_results = []
        
        # Filter and prepare products for analysis (same as main workflow)
        valid_products = [
            p for p in products
            if p.get("title") and isinstance(p.get("price"), (float, int)) and p.get("price", 0) > 0 and p.get("url")
        ]
        
        price_filtered_products = [
            p for p in valid_products
            if MIN_PRICE <= p.get("price", 0) <= MAX_PRICE
        ]
        
        # 🚨 SURGICAL FIX #2: ELIMINATE DUPLICATE PROCESSING
        # Deduplicate products by URL to prevent same product being processed multiple times
        seen_urls = set()
        deduplicated_products = []
        for product in price_filtered_products:
            product_url = product.get('url')
            if product_url and product_url not in seen_urls:
                seen_urls.add(product_url)
                deduplicated_products.append(product)
            elif product_url:
                self.log.debug(f"🔄 DEDUP: Skipping duplicate URL: {product_url}")
        
        price_filtered_products = deduplicated_products
        self.log.info(f"🔍 Processing {len(price_filtered_products)} products with main workflow logic (after deduplication)")
        
        # Use the same logic as the main workflow
        batch_size = max_products_per_cycle
        total_batches = (len(price_filtered_products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(price_filtered_products))
            batch_products = price_filtered_products[start_idx:end_idx]
            
            # Process each product in the current batch using main workflow logic
            for i, product_data in enumerate(batch_products):
                current_index = start_idx + i + 1
                self.log.info(f"--- Processing supplier product {current_index}/{len(price_filtered_products)}: '{product_data.get('title')}' ---")
                
                # 🚨 SURGICAL FIX: Update state manager with product index tracking (gap processing)
                if hasattr(self, 'state_manager') and self.state_manager:
                    if hasattr(self.state_manager, 'update_product_extraction_progress'):
                        self.state_manager.update_product_extraction_progress(current_index, len(price_filtered_products))
                    else:
                        # Fallback: directly update the product index in supplier_extraction_progress
                        if hasattr(self.state_manager, 'state_data'):
                            progress_data = self.state_manager.state_data.setdefault('supplier_extraction_progress', {})
                            progress_data['current_product_index_in_category'] = current_index
                            progress_data['total_products_in_current_category'] = len(price_filtered_products)
                
                # 🔄 UPDATE PROCESSING STATE: Update detailed progress tracking for hybrid mode
                if hasattr(self, 'state_manager') and self.state_manager:
                    # Calculate current category and subcategory indexes
                    # For hybrid mode, we process by chunks, so category index = batch_num + 1
                    self.state_manager.update_supplier_extraction_progress(
                        category_index=batch_num + 1,
                        total_categories=len(category_urls),
                        subcategory_index=i + 1,
                        total_subcategories=len(batch_products),
                        batch_number=batch_num + 1,
                        total_batches=total_batches,
                        category_url=product_data.get('source_url', 'unknown'),
                        extraction_phase="amazon_analysis"
                    )
                    # Also update the main processing index
                    self.state_manager.update_processing_index(current_index, len(price_filtered_products))
                
                # Check if product has been previously processed
                if self.state_manager.is_product_processed(product_data.get("url")):
                    self.log.info(f"Product already processed: {product_data.get('url')}. Skipping.")
                    continue

                # Extract Amazon data using the same logic as main workflow
                amazon_data = await self._get_amazon_data(product_data)
                
                if amazon_data:
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    amazon_asin = amazon_data.get("asin") or amazon_data.get("asin_extracted_from_page")
                    
                    # Save Amazon data to cache file  
                    # 🚨 FIX: Sanitize supplier_ean to handle multiple EANs or invalid characters
                    if supplier_ean:
                        # Take first EAN if multiple exist, sanitize invalid filename characters
                        filename_identifier = str(supplier_ean).split('/')[0].split('\\')[0].replace(" ", "_").replace(":", "_").replace("?", "_").replace("*", "_").replace("<", "_").replace(">", "_").replace("|", "_").replace('"', "_")
                    else:
                        filename_identifier = product_data.get("title", "NO_TITLE")[:50].replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "_").replace("*", "_").replace("<", "_").replace(">", "_").replace("|", "_").replace('"', "_")
                    amazon_cache_path = str(path_manager.get_output_path('FBA_ANALYSIS', 'amazon_cache', f"amazon_{amazon_asin}_{filename_identifier}.json"))
                    success = self.save_guardian.save_json_atomic(amazon_cache_path, amazon_data)
                    if success:
                        self.log.info(f"💾 Saved Amazon data to {amazon_cache_path}")
                    else:
                        self.log.error(f"❌ Failed to save Amazon data to {amazon_cache_path}")
                    
                    # Create linking map entry
                    
                    if amazon_asin:  # Only require ASIN, EAN can be None for title matches
                        # DEBUG: Check linking_map type before assignment
                        self.log.debug(f"🔍 DEBUG: linking_map type: {type(self.linking_map)}, size: {len(self.linking_map)} entries")
                        
                        # Create detailed linking map entry (matching working pre-minor-fix format)
                        # Get the actual search method used from Amazon data
                        actual_search_method = amazon_data.get("_search_method_used", "unknown")
                        
                        linking_entry = {
                            "supplier_ean": supplier_ean,
                            "amazon_asin": amazon_asin,
                            "supplier_title": product_data.get("title", ""),
                            "amazon_title": amazon_data.get("title", ""),
                            "supplier_price": product_data.get("price"),
                            "amazon_price": amazon_data.get("current_price"),
                            "match_method": actual_search_method,
                            "confidence": "high" if actual_search_method == "EAN" else "medium" if actual_search_method == "title" else "low",
                            "created_at": datetime.now().isoformat(),
                            "supplier_url": product_data.get("url")
                        }
                        # 🚀 HASH OPTIMIZATION: Use optimized method to add entry and update indexes
                        self._add_linking_map_entry_optimized(linking_entry)
                        
                        # 🚨 CRITICAL FIX: Check financial report trigger after each linking map entry
                        financial_batch_size = self.config_loader.get_financial_batch_size()
                        current_linking_map_count = len(self.linking_map)
                        
                        if current_linking_map_count > 0 and current_linking_map_count % financial_batch_size == 0:
                            try:
                                self.log.info(f"🚨 FINANCIAL REPORT TRIGGER: Reached {current_linking_map_count} linking map entries (trigger every {financial_batch_size})")
                                from tools.FBA_Financial_calculator import run_calculations
                                financial_results = run_calculations(self.supplier_name)
                                if financial_results and financial_results.get('statistics', {}).get('output_file'):
                                    self.log.info(f"✅ Financial report EXECUTED: {financial_results['statistics']['output_file']}")
                                else:
                                    self.log.warning("⚠️ Financial report executed but no file path returned")
                            except ImportError as ie:
                                self.log.error(f"❌ Could not import FBA_Financial_calculator: {ie}")
                            except Exception as e:
                                self.log.error(f"❌ Error executing financial report: {e}")
                        elif current_linking_map_count > 0:
                            next_trigger_count = ((current_linking_map_count // financial_batch_size) + 1) * financial_batch_size
                            self.log.info(f"💡 FINANCIAL REPORT TRIGGER: Next trigger at {next_trigger_count} linking map entries (current: {current_linking_map_count}, trigger frequency: {financial_batch_size})")
                    
                    # Combine supplier and Amazon data
                    combined_data = {**product_data, **amazon_data}
                    
                    # Run financial analysis using same logic as main workflow
                    try:
                        # Extract supplier price with validation
                        supplier_price_inc_vat = combined_data.get("price", 0)
                        if isinstance(supplier_price_inc_vat, str):
                            # Clean price string and convert to float
                            import re
                            price_clean = re.sub(r'[^0-9.]', '', supplier_price_inc_vat)
                            supplier_price_inc_vat = float(price_clean) if price_clean else 0
                        elif supplier_price_inc_vat is None:
                            supplier_price_inc_vat = 0
                            
                        # Calculate financial metrics for this specific product
                        financials = calc_financials(combined_data, combined_data, supplier_price_inc_vat)
                        
                        if not financials:
                            self.log.warning(f"Financial calculation returned empty for '{combined_data.get('title')}'")
                            financial_result = {"error": "Financial calculation returned empty", "is_profitable": False}
                        else:
                            # Extract profitability from financials result
                            is_profitable = financials.get("is_profitable", False)
                            financial_result = {
                                **financials,
                                "is_profitable": is_profitable
                            }
                            
                    except Exception as calc_error:
                        self.log.error(f"Financial calculation error: {calc_error}")
                        financial_result = {"error": str(calc_error), "is_profitable": False}
                    
                    if financial_result and financial_result.get("is_profitable"):
                        profitable_results.append(financial_result)
                        self.log.info(f"✅ Profitable product found: {product_data.get('title')}")
                        self.state_manager.mark_product_processed(product_data.get("url"), "completed_profitable")
                    elif financial_result and financial_result.get("error"):
                        self.log.info(f"❌ Financial analysis failed: {financial_result.get('error')}")
                        self.state_manager.mark_product_processed(product_data.get("url"), "failed_financial_calculation")
                    else:
                        self.log.info(f"❌ Not profitable product: {product_data.get('title')}")
                        self.state_manager.mark_product_processed(product_data.get("url"), "completed_not_profitable")
                
                else:
                    # Handle no Amazon data or error cases
                    self.log.warning(f"Could not retrieve Amazon data for '{product_data.get('title')}'. Creating no-match linking entry.")
                    
                    # Create no-match linking entry for chunk processing
                    supplier_ean = product_data.get("ean") or product_data.get("barcode")
                    if supplier_ean == "None" or supplier_ean is None:
                        supplier_ean = None
                        
                    # Determine the reason for no match
                    error_info = amazon_data.get("error") if isinstance(amazon_data, dict) else "No Amazon data returned"
                    no_match_reason = f"Chunk processing - Amazon search failed: {error_info}"
                    
                    no_match_entry = {
                        "supplier_ean": supplier_ean,
                        "amazon_asin": None,
                        "supplier_title": product_data.get("title", ""),
                        "amazon_title": None,
                        "supplier_price": product_data.get("price"),
                        "amazon_price": None,
                        "match_method": "none",
                        "confidence": 0,
                        "created_at": datetime.now().isoformat(),
                        "supplier_url": product_data.get("url"),
                        "no_match_reason": no_match_reason
                    }
                    
                    # Add no-match entry to linking map using optimized method
                    self._add_linking_map_entry_optimized(no_match_entry)
                    self.log.info(f"✅ Added NO-MATCH linking entry for chunk product: {supplier_ean or 'NO_EAN'} → NO MATCH")
                    
                    self.state_manager.mark_product_processed(product_data.get("url"), "failed_amazon_extraction")
                
                # Save state periodically using configurable batch size
                linking_map_batch = self.system_config.get("linking_map_batch_size", 1)
                if current_index % linking_map_batch == 0:
                    self.state_manager.save_state(preserve_interruption_state=True)
                    self._save_linking_map(self.supplier_name)
                    self.log.info(f"📊 Periodic save at product {current_index} (linking_map_batch_size: {linking_map_batch})")
        
        try:
            # Final save of linking map with all entries
            self._save_linking_map(self.supplier_name)
            self.log.info("✅ Chunk processing: Final linking map save completed")
            
            # Final save of financial results
            if profitable_results:
                # Note: _save_final_report expects supplier_name as second parameter
                self._save_final_report(profitable_results, self.supplier_name)
                self.log.info("✅ Chunk processing: Final report save completed")
            
            self.log.info("--- Chunk Processing with Main Workflow Logic Finished ---")
            
        except Exception as save_error:
            self.log.error(f"❌ CRITICAL: Error during final save operations in chunk processing: {save_error}", exc_info=True)
        
        return profitable_results
    
    def _check_authentication_fallback_needed(self) -> bool:
        """
        🔧 AUTHENTICATION FALLBACK: Check if re-authentication is needed based on various triggers
        """
        # Trigger 1: Too many products without prices
        if self.products_without_price_count >= self.auth_fallback_config["price_missing_threshold"]:
            self.log.warning(f"🔐 AUTH TRIGGER: {self.products_without_price_count} products without price (threshold: {self.auth_fallback_config['price_missing_threshold']})")
            return True
            
        # Trigger 2: Product count-based re-authentication
        if self.products_processed_since_auth >= self.auth_fallback_config["products_per_auth"]:
            self.log.warning(f"🔐 AUTH TRIGGER: {self.products_processed_since_auth} products processed since last auth (threshold: {self.auth_fallback_config['products_per_auth']})")
            return True
            
        # Trigger 3: Time-based re-authentication
        if self.last_authentication_time:
            from datetime import datetime, timedelta
            hours_since_auth = (datetime.now() - self.last_authentication_time).total_seconds() / 3600
            if hours_since_auth >= self.auth_fallback_config["hours_per_auth"]:
                self.log.warning(f"🔐 AUTH TRIGGER: {hours_since_auth:.1f} hours since last auth (threshold: {self.auth_fallback_config['hours_per_auth']})")
                return True
                
        return False
    
    async def _perform_authentication_fallback(self) -> bool:
        """
        🔧 AUTHENTICATION FALLBACK: Perform re-authentication using SupplierAuthenticationService
        """
        try:
            self.log.info("🔐 Performing authentication fallback...")
            
            # Import and use the authentication service
            from tools.supplier_authentication_service import SupplierAuthenticationService
            
            # Get credentials from config
            supplier_config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config", "supplier_configs", f"{self.supplier_name.replace('.', '-')}.json"
            )
            
            # Create authentication service
            auth_service = SupplierAuthenticationService(
                supplier_name=self.supplier_name,
                supplier_url=f"https://{self.supplier_name}",
                config_path=supplier_config_path
            )
            
            # Get a page from browser manager
            page = None
            if hasattr(self, 'browser_manager') and self.browser_manager:
                try:
                    page = await self.browser_manager.get_page()
                except:
                    self.log.warning("Could not get page from browser manager for authentication")
            
            if page:
                # Use hardcoded credentials (as shown in the auth service)
                credentials = {
                    "email": "info@theblacksmithmarket.com",
                    "password": "0Dqixm9c&"
                }
                
                success, method = await auth_service.ensure_authenticated_session(page, credentials, force_reauth=True)
                
                if success:
                    self.log.info(f"✅ Authentication fallback successful using {method}")
                    # Reset counters and update timestamp
                    self.products_without_price_count = 0
                    self.products_processed_since_auth = 0
                    self.last_authentication_time = datetime.now()
                    return True
                else:
                    self.log.error("❌ Authentication fallback failed")
                    return False
            else:
                self.log.error("❌ Could not get browser page for authentication")
                return False
                
        except Exception as e:
            self.log.error(f"❌ Authentication fallback error: {e}")
            return False
    
    def _record_product_price_status(self, product_data: dict, has_price: bool):
        """
        🔧 AUTHENTICATION FALLBACK: Record whether product has price for authentication monitoring
        """
        # Update product processing counter
        self.products_processed_since_auth += 1
        
        # Track price missing for authentication fallback
        if not has_price:
            self.products_without_price_count += 1
            self.log.info(f"🔍 PRICE MISSING: Product without price ({self.products_without_price_count}/{self.auth_fallback_config['price_missing_threshold']})")
        else:
            # Reset counter on successful price extraction
            if self.products_without_price_count > 0:
                self.log.info(f"✅ PRICE FOUND: Resetting price missing counter (was {self.products_without_price_count})")
                self.products_without_price_count = 0
    
    def _get_supplier_cache_path_fix(self) -> str:
        """Get the path to supplier cache file"""
        supplier_name_clean = self.supplier_name.replace('.', '-')
        return os.path.join(self.supplier_cache_dir, f"{supplier_name_clean}_products_cache.json")
    
    def _find_actual_supplier_cache_file(self, supplier_name: str) -> tuple[str, int]:
        """
        🚨 CRITICAL FIX: Find actual supplier cache file including fallback files
        Returns: (file_path, product_count) or ("", 0) if not found
        """
        # Pattern 1: Expected filename (matches save method)
        expected_filename = f"{supplier_name.replace('.', '-')}_products_cache.json"
        expected_path = os.path.join(self.supplier_cache_dir, expected_filename)
        
        # Pattern 2: Alternative sanitized filename (legacy compatibility)
        sanitized_filename = f"{supplier_name.replace('.', '_')}_products_cache.json"
        sanitized_path = os.path.join(self.supplier_cache_dir, sanitized_filename)
        
        # Check expected patterns first
        for pattern_name, file_path in [("expected", expected_path), ("sanitized", sanitized_path)]:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        products = json.load(f)
                    count = len(products)
                    self.log.info(f"✅ CACHE FOUND: {pattern_name} pattern - {count} products in {os.path.basename(file_path)}")
                    return file_path, count
                except Exception as e:
                    self.log.warning(f"⚠️ Could not read {pattern_name} cache file: {e}")
        
        # Pattern 3: Search for fallback files (cache_fallback_*.json)
        try:
            import glob
            fallback_pattern = os.path.join(self.supplier_cache_dir, "cache_fallback_*.json")
            fallback_files = glob.glob(fallback_pattern)
            
            if fallback_files:
                # Use the most recent fallback file
                latest_fallback = max(fallback_files, key=os.path.getmtime)
                try:
                    with open(latest_fallback, 'r', encoding='utf-8') as f:
                        products = json.load(f)
                    count = len(products)
                    self.log.info(f"✅ CACHE FOUND: fallback pattern - {count} products in {os.path.basename(latest_fallback)}")
                    return latest_fallback, count
                except Exception as e:
                    self.log.warning(f"⚠️ Could not read fallback cache file: {e}")
        except Exception as e:
            self.log.warning(f"⚠️ Could not search for fallback files: {e}")
        
        self.log.info(f"📝 NO CACHE FOUND: No supplier cache file found for {supplier_name}")
        return "", 0

    # 🚨 CRITICAL FIX 1: Processing State Resumption Logic
    def _should_continue_supplier_scraping(self) -> bool:
        """Check if supplier scraping should continue from previous index"""
        try:
            # Check processing state for extraction progress
            if hasattr(self.state_manager, 'state_data') and self.state_manager.state_data:
                # 🚨 CRITICAL FIX: Use system_progression as canonical source
                sp = self.state_manager.state_data.get('system_progression', {})
                extraction_progress = sp  # Use system_progression data
                products_extracted = sp.get('current_product_index_in_category', 0)
                
                # Get the target from runtime settings
                metadata = self.state_manager.state_data.get('metadata', {})
                runtime_settings = metadata.get('runtime_settings', {})
                target_products = runtime_settings.get('max_products_per_category', 8)
                
                self.log.info(f"🔍 SUPPLIER SCRAPING CHECK: extracted {products_extracted}/{target_products} products")
                
                # Continue scraping if we haven't reached the target
                if products_extracted < target_products:
                    self.log.info(f"🔄 SUPPLIER SCRAPING NEEDED: {products_extracted} < {target_products}")
                    return True
                else:
                    self.log.info(f"✅ SUPPLIER SCRAPING COMPLETE: {products_extracted} >= {target_products}")
                    return False
            else:
                self.log.info("🔄 NO PROCESSING STATE: Proceeding with supplier scraping")
                return True
                
        except Exception as e:
            self.log.warning(f"⚠️ Error checking supplier scraping status: {e}, proceeding with scraping")
            return True

    # 🚨 CRITICAL FIX 2: 276-Chunk Skip Logic  
    def _should_skip_chunk_processing(self) -> bool:
        """Check if chunk processing should be skipped due to already processed products"""
        try:
            # Check if we have extracted products
            cache_path = self._get_supplier_cache_path_fix()
            if not os.path.exists(cache_path):
                self.log.info("🔄 NO SUPPLIER CACHE: Cannot skip chunk processing")
                return False
            
            # Check if we have processed products through Amazon (linking map exists)
            linking_map = self._load_linking_map(self.supplier_name)
            if not linking_map:
                self.log.info("🔄 NO LINKING MAP: Cannot skip chunk processing")
                return False
            
            # Check if financial reports already exist
            financial_reports_dir = Path(self.output_dir) / "FBA_ANALYSIS" / "financial_reports"
            if financial_reports_dir.exists():
                report_files = list(financial_reports_dir.glob("fba_financial_report_*.csv"))
                if report_files:
                    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
                    # Check if report is recent (within last hour)
                    import time
                    if (time.time() - latest_report.stat().st_mtime) < 3600:
                        self.log.info(f"✅ RECENT FINANCIAL REPORT EXISTS: {latest_report.name} - skipping chunk reprocessing")
                        return True
            
            self.log.info("🔄 CONDITIONS NOT MET: Proceeding with chunk processing")
            return False
            
        except Exception as e:
            self.log.warning(f"⚠️ Error checking chunk skip conditions: {e}, proceeding with processing")
            return False
    
    def _load_existing_profitable_results(self) -> List[Dict[str, Any]]:
        """Load existing profitable results from recent financial reports"""
        try:
            financial_reports_dir = Path(self.output_dir) / "FBA_ANALYSIS" / "financial_reports"
            if not financial_reports_dir.exists():
                return []
            
            report_files = list(financial_reports_dir.glob("fba_financial_report_*.csv"))
            if not report_files:
                return []
            
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            self.log.info(f"📊 Loading existing profitable results from: {latest_report.name}")
            
            # Read CSV and convert to results format
            import pandas as pd
            df = pd.read_csv(latest_report)
            profitable_results = []
            
            for _, row in df.iterrows():
                if row.get('profit_gbp', 0) > 0:  # Only profitable products
                    result = {
                        'supplier_product': {
                            'title': row.get('supplier_title', ''),
                            'price': row.get('supplier_price_gbp', 0),
                            'ean': row.get('ean', ''),
                            'url': row.get('supplier_url', '')
                        },
                        'amazon_product': {
                            'asin': row.get('asin', ''),
                            'title': row.get('amazon_title', ''),
                            'price': row.get('amazon_price_gbp', 0)
                        },
                        'profit_gbp': row.get('profit_gbp', 0),
                        'roi_percentage': row.get('roi_percentage', 0)
                    }
                    profitable_results.append(result)
            
            self.log.info(f"✅ Loaded {len(profitable_results)} existing profitable results")
            return profitable_results
            
        except Exception as e:
            self.log.warning(f"⚠️ Error loading existing profitable results: {e}")
            return []

    # 🚨 LOGIN SCRIPT TRIGGER IMPLEMENTATION - Uses same authentication script as system startup
    async def _trigger_authentication_check(self, context: str = "category_processing") -> bool:
        """
        Trigger the same login script that runs at system startup before each category extraction.
        This ensures authentication is refreshed at workflow boundaries as required.
        """
        try:
            self.log.info(f"🔐 LOGIN SCRIPT TRIGGER: Checking authentication before {context}")
            
            # Import the same authentication service used at system startup
            from tools.supplier_authentication_service import SupplierAuthenticationService
            
            if hasattr(self, 'browser_manager') and self.browser_manager:
                # Initialize authentication service using same pattern as run_custom_poundwholesale.py
                auth_service = SupplierAuthenticationService(self.browser_manager)
                
                # Get a page from browser manager to check authentication
                page = await self.browser_manager.get_page(
                    self.workflow_config.get('supplier_url', 'https://www.poundwholesale.co.uk')
                )
                
                if page:
                    # Get supplier credentials from system config (hybrid processing enabled)
                    supplier_name = self.supplier_name or "poundwholesale.co.uk"
                    credentials_config = self.system_config.get("credentials", {}).get(supplier_name, {})
                    credentials = {
                        "email": credentials_config.get("username", "info@theblacksmithmarket.com"),
                        "password": credentials_config.get("password", "0Dqixm9c&")
                    }
                    
                    # Use the same authentication method as startup script
                    authenticated = await auth_service.ensure_authenticated_session(page, credentials)
                    
                    if authenticated:
                        self.log.info(f"✅ LOGIN SCRIPT SUCCESS: Authentication verified for {context}")
                        return True
                    else:
                        self.log.warning(f"⚠️ LOGIN SCRIPT FAILED: Authentication failed for {context}")
                        return False
                else:
                    self.log.warning(f"⚠️ LOGIN SCRIPT ERROR: Could not get page for authentication check in {context}")
                    return True  # Continue processing even if can't check
                    
            else:
                self.log.warning(f"⚠️ LOGIN SCRIPT UNAVAILABLE: No browser manager for authentication in {context}")
                return True  # Continue processing if no browser manager
                
        except Exception as e:
            self.log.warning(f"⚠️ LOGIN SCRIPT TRIGGER ERROR: {e} in {context}, continuing processing")
            return True  # Continue processing on error to avoid blocking workflow

    # 🚨 CRITICAL FIX 3: Authentication Fallback Integration (Deprecated - replaced by _trigger_authentication_check)
    async def _check_authentication_before_category(self) -> bool:
        """Check authentication before category and trigger fallback if needed"""
        try:
            # Import the authentication service
            from tools.supplier_authentication_service import SupplierAuthenticationService
            
            if hasattr(self, 'browser_manager') and self.browser_manager:
                auth_service = SupplierAuthenticationService(self.browser_manager)
                
                # Check if authenticated
                is_authenticated = await auth_service.is_authenticated()
                
                if not is_authenticated:
                    self.log.warning("⚠️ AUTHENTICATION LOST: Triggering login fallback")
                    
                    # Trigger standalone login script
                    try:
                        from tools.standalone_playwright_login import StandalonePlaywrightLogin
                        login_handler = StandalonePlaywrightLogin(self.browser_manager)
                        login_result = await login_handler.perform_login(self.supplier_name)
                        
                        if login_result:
                            self.log.info("✅ Authentication fallback successful")
                            return True
                        else:
                            self.log.error("❌ Authentication fallback failed")
                            return False
                    except Exception as login_error:
                        self.log.error(f"❌ Authentication fallback error: {login_error}")
                        return False
                else:
                    self.log.info("✅ Authentication verified")
                    return True
            else:
                self.log.warning("⚠️ No browser manager available for authentication check")
                return True  # Assume authenticated if can't check
                
        except Exception as e:
            self.log.warning(f"⚠️ Error checking authentication: {e}, proceeding")
            return True  # Assume authenticated on error

    # Helper methods for CRITICAL FIX 1 integration
    async def _load_cached_supplier_products(self) -> List[Dict[str, Any]]:
        """Load cached supplier products"""
        try:
            cache_path = self._get_supplier_cache_path_fix()
            if os.path.exists(cache_path):
                import json
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_products = json.load(f)
                self.log.info(f"✅ Loaded {len(cached_products)} cached supplier products")
                return cached_products
            return []
        except Exception as e:
            self.log.warning(f"⚠️ Error loading cached products: {e}")
            return []

    async def _process_existing_products_with_amazon_extraction(self, products: List[Dict[str, Any]], max_products_per_cycle: int) -> List[Dict[str, Any]]:
        """Process existing cached products with Amazon extraction only"""
        self.log.info(f"🔄 Processing {len(products)} existing products with Amazon extraction")
        return await self._process_chunk_with_main_workflow_logic(products, max_products_per_cycle)

    def _filter_unprocessed_products_with_hash_lookup(self, all_products: List[Dict[str, Any]], supplier_name: str) -> List[Dict[str, Any]]:
        """
        🚨 CRITICAL FIX #1 & #3: Filter products using hash-based O(1) lookup against linking map AND product cache
        
        This method implements:
        - Hash-based lookup for O(1) performance instead of O(n) linear searches  
        - Linking map filtering to only return unprocessed products
        - 🚀 ENHANCEMENT: Product cache filtering to skip products already extracted  
        - Comprehensive logging for debugging gap processing
        
        Args:
            all_products: All cached supplier products (e.g., 2,335 products)
            supplier_name: Name of supplier for linking map path
            
        Returns:
            List of unprocessed products (e.g., 50-100 products that haven't been processed)
        """
        import json
        import os
        from typing import Set
        
        # 🔍 Step 1: Load linking map to identify already processed products
        linking_map_path = self._get_linking_map_path_for_supplier(supplier_name)
        processed_eans: Set[str] = set()
        processed_urls: Set[str] = set()
        
        if os.path.exists(linking_map_path):
            try:
                with open(linking_map_path, 'r', encoding='utf-8') as f:
                    linking_map_data = json.load(f)
                
                # 🚨 CRITICAL FIX: Build both EAN and URL sets for comprehensive filtering
                processed_eans = {
                    entry.get('supplier_ean') 
                    for entry in linking_map_data 
                    if entry.get('supplier_ean')
                }
                # 🚨 FIX 4: Normalize URLs for consistent filtering
                processed_urls = {
                    self._normalize_url_for_filtering(entry.get('supplier_url')) 
                    for entry in linking_map_data 
                    if entry.get('supplier_url')
                }
                
                self.log.info(f"🔍 HASH LOOKUP: Loaded {len(processed_eans)} processed EANs and {len(processed_urls)} processed URLs from linking map")
                self.log.info(f"🔍 LINKING MAP: {linking_map_path}")
                
            except Exception as e:
                self.log.warning(f"⚠️ Could not load linking map for filtering: {e}")
                self.log.info(f"🔍 FALLBACK: Processing all products (no linking map available)")
                return all_products
        else:
            self.log.info(f"🔍 NO LINKING MAP: {linking_map_path} does not exist, processing all products")
            return all_products

        # 🚀 ENHANCEMENT: Build product cache hash indexes for duplicate prevention
        if not hasattr(self, 'product_cache_ean_index') or not hasattr(self, 'product_cache_url_index'):
            self.log.info(f"🔍 Building product cache hash indexes for duplicate prevention...")
            
            # Load product cache
            cached_products = self._load_supplier_cache(supplier_name)
            
            if cached_products:
                # Build hash indexes for O(1) lookup
                cache_hash_index = self._build_product_hash_index(cached_products)
                
                # Separate EAN and URL indexes
                self.product_cache_ean_index = {}
                self.product_cache_url_index = {}
                
                for product in cached_products:
                    product_ean = product.get('ean', '')
                    product_url = product.get('url', '')
                    
                    if product_ean:
                        self.product_cache_ean_index[product_ean] = True
                    if product_url:
                        # 🚨 FIX 4: Normalize URL for consistent cache lookup
                        normalized_product_url = self._normalize_url_for_filtering(product_url)
                        self.product_cache_url_index[normalized_product_url] = True
                
                self.log.info(f"✅ Product cache indexes built:")
                self.log.info(f"   📊 URL Index: {len(self.product_cache_url_index)} entries")
                self.log.info(f"   📊 EAN Index: {len(self.product_cache_ean_index)} entries")
            else:
                # No cache available - initialize empty indexes
                self.product_cache_ean_index = {}
                self.product_cache_url_index = {}
                self.log.info(f"📊 No product cache found - cache optimization disabled")
        
        # 🔍 Step 2: Filter products using O(1) hash lookup for both EAN and URL

        # 🚨 CRITICAL FIX: Add pre-extraction visibility logs
        self.log.info(f"🔗 PRE-EXTRACTION PRODUCT FILTERING: Starting with {len(all_products)} products from cache")
        self.log.info(f"🔗 Filtering against linking map and product cache to identify unprocessed products")

        unprocessed_products = []
        processed_count = 0
        skipped_by_linking_map_ean = 0
        skipped_by_linking_map_url = 0
        skipped_by_cache_ean = 0
        skipped_by_cache_url = 0
        included_missing_ean = 0
        
        for product in all_products:
            product_ean = product.get('ean', '')
            product_url = product.get('url', '')
            
            # 🚨 CRITICAL FIX: Skip if product is processed by EITHER EAN OR URL in linking map
            skip_product = False
            
            # Check linking map EAN-based skipping
            if product_ean and product_ean in processed_eans:
                skipped_by_linking_map_ean += 1
                processed_count += 1
                skip_product = True
                self.log.debug(f"🔄 Linking map hit (EAN): {product.get('title', 'Unknown')} - skipping extraction")
            
            # Check linking map URL-based skipping (for products without EAN or as additional check)
            # 🚨 FIX 4: Normalize URL for consistent comparison
            elif product_url and self._normalize_url_for_filtering(product_url) in processed_urls:
                skipped_by_linking_map_url += 1
                processed_count += 1  
                skip_product = True
                self.log.debug(f"🔄 Linking map hit (URL): {product.get('title', 'Unknown')} - skipping extraction")
            
            # 🚨 CORRECTED: Products with cached supplier data but NOT in linking map need Amazon analysis
            # Cache hits should NOT be skipped - they indicate supplier data is available for Amazon lookup
            # 🚨 FIX 4: Normalize URL for consistent cache comparison
            if (product_ean and product_ean in self.product_cache_ean_index) or \
               (product_url and self._normalize_url_for_filtering(product_url) in self.product_cache_url_index):
                # Has cached supplier data - can proceed directly to Amazon analysis
                # Verbose logging removed per user request - product found in cache
                pass

            if skip_product:
                continue
                
            # Track products without EAN for visibility
            if not product_ean:
                included_missing_ean += 1
            
            # Product not found in either set - include for processing
            unprocessed_products.append(product)
        
        # 🚨 CRITICAL FIX: Enhanced filtering visibility with 2-step breakdown
        total_skipped_linking_map = skipped_by_linking_map_ean + skipped_by_linking_map_url

        # Count products with cached supplier data (not skipped, just optimized)
        cached_supplier_data = sum(1 for product in unprocessed_products
                                 if (product.get('ean') and product.get('ean') in self.product_cache_ean_index) or
                                    (product.get('url') and product.get('url') in self.product_cache_url_index))

        # Calculate products that need full extraction (not cached, not skipped)
        needs_full_extraction = len(unprocessed_products) - cached_supplier_data

        # 🚨 ENHANCED VISIBILITY: Show the complete 2-step filtering breakdown
        self.log.info(f"🔗 LINKING MAP FILTER (Step 1): {total_skipped_linking_map} products already processed")
        self.log.info(f"   📊 EAN-based skips: {skipped_by_linking_map_ean}")
        self.log.info(f"   📊 URL-based skips: {skipped_by_linking_map_url}")

        self.log.info(f"💾 PRODUCT CACHE FILTER (Step 2): {cached_supplier_data} products have supplier data cached")
        self.log.info(f"📊 FULL EXTRACTION NEEDED: {needs_full_extraction} products need fresh extraction")

        # Verify filter invariant
        expected_total = total_skipped_linking_map + len(unprocessed_products)
        if expected_total != len(all_products):
            self.log.error(f"🚨 FILTER INVARIANT VIOLATION: {expected_total} != {len(all_products)}")
            self.log.error(f"   This indicates a bug in the filtering logic")

        self.log.info(f"🧮 FILTER INVARIANT: in={len(all_products)} == skip={total_skipped_linking_map} + remaining={len(unprocessed_products)}")

        self.log.info(f"🔍 CORRECTED FILTER RESULTS:")
        self.log.info(f"   📊 Input products: {len(all_products)}")
        self.log.info(f"   ✅ Linking map skipped (fully processed): {total_skipped_linking_map}")
        self.log.info(f"   🚀 Cached supplier data available: {cached_supplier_data} (will use for Amazon analysis)")
        self.log.info(f"   📋 Need Amazon analysis: {len(unprocessed_products)}")
        self.log.info(f"   📈 Efficiency: {total_skipped_linking_map}/{len(all_products)} = {(total_skipped_linking_map/len(all_products)*100) if len(all_products) > 0 else 0:.1f}% reduction")
        
        return unprocessed_products
    
    def _load_supplier_cache(self, supplier_name: str) -> List[Dict[str, Any]]:
        """
        Load cached supplier products for hash indexing and duplicate prevention
        
        Args:
            supplier_name: Name of supplier to load cache for
            
        Returns:
            List of cached products, or empty list if no cache found
        """
        import json
        
        supplier_cache_file, _ = self._find_actual_supplier_cache_file(supplier_name)
        if not supplier_cache_file:
            self.log.debug(f"📊 No supplier cache file found for {supplier_name}")
            return []
        
        try:
            with open(supplier_cache_file, 'r', encoding='utf-8') as f:
                cached_products = json.load(f)
                self.log.debug(f"📊 Loaded {len(cached_products)} products from supplier cache: {supplier_cache_file}")
                return cached_products
        except Exception as e:
            self.log.warning(f"⚠️ Error loading supplier cache {supplier_cache_file}: {e}")
            return []
    
    def _build_product_hash_index(self, products: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Build hash index for O(1) product lookups
        
        Args:
            products: List of products to index
            
        Returns:
            Dict mapping product identifiers to True (for fast existence checking)
        """
        hash_index = {}
        
        for product in products:
            # Index by EAN if available
            product_ean = product.get('ean', '')
            if product_ean:
                hash_index[product_ean] = True
            
            # Index by URL if available
            product_url = product.get('url', '')
            if product_url:
                hash_index[product_url] = True
        
        return hash_index
    
    def _get_linking_map_path_for_supplier(self, supplier_name: str) -> str:
        """Get the linking map file path for a given supplier using centralized path management"""
        # Use path_manager for standardized path construction - ensures canonical dotted path
        return str(get_linking_map_path(supplier_name=supplier_name))
    
    def _perform_smart_memory_management(self, current_product_index: int, batch_products: list):
        """
        🚨 CRITICAL FIX #4: Smart Memory Management with Sliding Window Approach
        
        Implements periodic memory clearing with preservation of recent context for debugging continuity.
        Prevents memory accumulation while maintaining processing efficiency.
        
        Args:
            current_product_index: Current product being processed
            batch_products: Current batch of products being processed
        """
        import gc
        
        # Memory management configuration
        memory_config = self.system_config.get("memory_management", {})
        clear_frequency = memory_config.get("clear_frequency_products", 500)  # Clear every 500 products
        sliding_window_size = memory_config.get("sliding_window_size", 100)   # Keep last 100 for continuity
        enabled = memory_config.get("enabled", True)
        
        if not enabled:
            return
        
        # Check if it's time for memory clearing
        if current_product_index % clear_frequency == 0:
            self.log.info(f"🧹 SMART MEMORY MANAGEMENT: Starting memory clearing at product {current_product_index}")
            
            # Step 1: Clear large data structures if they exist
            cleared_items = 0
            
            # Clear any accumulated results lists (while preserving recent items)
            if hasattr(self, 'profitable_results') and len(self.profitable_results) > sliding_window_size:
                original_count = len(self.profitable_results)
                # Keep only the last N items for continuity
                self.profitable_results = self.profitable_results[-sliding_window_size:]
                cleared_count = original_count - len(self.profitable_results)
                cleared_items += cleared_count
                self.log.info(f"🧹 MEMORY: Cleared {cleared_count} old profitable results, kept {len(self.profitable_results)} recent items")
            
            # Clear product accumulation lists if they exist and are large
            if hasattr(self, '_current_all_products') and len(self._current_all_products) > sliding_window_size * 2:
                # For product lists, we need to be more careful - only clear if we have persistent cache
                cache_file_exists = False
                try:
                    cache_file, _ = self._find_actual_supplier_cache_file(self.supplier_name)
                    cache_file_exists = cache_file and os.path.exists(cache_file)
                except:
                    pass
                
                if cache_file_exists:
                    original_count = len(self._current_all_products)
                    # Keep recent products for continuity
                    self._current_all_products = self._current_all_products[-sliding_window_size:]
                    cleared_count = original_count - len(self._current_all_products)
                    cleared_items += cleared_count
                    self.log.info(f"🧹 MEMORY: Cleared {cleared_count} old cached products, kept {len(self._current_all_products)} recent items")
                    self.log.info(f"🧹 MEMORY: Product cache file available for recovery: {cache_file}")
            
            # Step 2: Clear any large temporary variables
            if hasattr(self, '_temp_amazon_data'):
                delattr(self, '_temp_amazon_data')
                cleared_items += 1
                
            if hasattr(self, '_temp_search_results'):
                delattr(self, '_temp_search_results')
                cleared_items += 1
            
            # Step 3: Force garbage collection
            collected = gc.collect()
            
            # Step 4: Log memory management results
            self.log.info(f"🧹 SMART MEMORY CLEARED: {cleared_items} data structures, {collected} objects collected")
            self.log.info(f"🧹 MEMORY CONFIG: clear_frequency={clear_frequency}, sliding_window={sliding_window_size}")
            self.log.info(f"🧹 MEMORY CONTINUITY: Recent context preserved for debugging and state recovery")
