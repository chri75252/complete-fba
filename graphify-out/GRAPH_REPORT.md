# Graph Report - graphify-flat  (2026-04-11)

## Corpus Check
- 27 files · ~123,073 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 976 nodes · 3205 edges · 19 communities detected
- Extraction: 48% EXTRACTED · 52% INFERRED · 0% AMBIGUOUS · INFERRED: 1673 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `SystemConfigLoader` - 320 edges
2. `BrowserManager` - 263 edges
3. `WindowsSaveGuardian` - 247 edges
4. `FixedEnhancedStateManager` - 236 edges
5. `ConfigurableSupplierScraper` - 210 edges
6. `AmazonExtractor` - 172 edges
7. `FixedAmazonExtractor` - 162 edges
8. `SentinelMonitor` - 153 edges
9. `SimpleMetrics` - 151 edges
10. `PassiveExtractionWorkflow` - 106 edges

## Surprising Connections (you probably didn't know these)
- `Comprehensive Amazon data extraction using Playwright connected to Chrome with d` --uses--> `BrowserManager`  [INFERRED]
  graphify-flat\amazon_playwright_extractor.py → graphify-flat\browser_manager.py
- `Comprehensive background mode setup to prevent browser from coming to front.` --uses--> `BrowserManager`  [INFERRED]
  graphify-flat\amazon_playwright_extractor.py → graphify-flat\browser_manager.py
- `Extract all data from the Amazon product page including extensions.         Res` --uses--> `BrowserManager`  [INFERRED]
  graphify-flat\amazon_playwright_extractor.py → graphify-flat\browser_manager.py
- `Extension of AmazonExtractor.     Includes EAN search capabilities and attempts` --uses--> `BrowserManager`  [INFERRED]
  graphify-flat\amazon_playwright_extractor.py → graphify-flat\browser_manager.py
- `Connect to browser using the centralized BrowserManager singleton.         All` --uses--> `BrowserManager`  [INFERRED]
  graphify-flat\amazon_playwright_extractor.py → graphify-flat\browser_manager.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (103): FixedEnhancedStateManager, normalize_url(), Fixed Enhanced State Manager - Comprehensive solution for processing state issue, Public wrapper for real-time category total correction.          This method s, CRITICAL FIX 5: Update progress tracking AND resumption index for exact recovery, Initialize tracking for a new category, Update progress during supplier extraction phase, Update progress during Amazon analysis phase (+95 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (89): ENHANCED TITLE MATCHING - COMMENTED OUT         System will now select first pr, Calculate word overlap score between two titles - COMMENTED OUT, Normalize EAN for comparison (remove spaces, leading zeros).          Args:, Extract EAN/Barcode from Amazon product details section.          Tries multip, Handle navigation requests while keeping browser in background, Connect to browser using centralized BrowserManager singleton only., BrowserManager, Check if browser should restart based on time interval or memory threshold (+81 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (106): AmazonExtractor, FixedAmazonExtractor, Comprehensive Amazon data extraction using Playwright connected to Chrome with d, Extension of AmazonExtractor.     Includes EAN search capabilities and attempts, Connect to browser using the centralized BrowserManager singleton.         All, Comprehensive background mode setup to prevent browser from coming to front., Extract all data from the Amazon product page including extensions.         Res, Enhanced Cache Manager for Amazon FBA Agent System  This module provides a centr (+98 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (59): normalize_ean(), normalize_url(), PassiveExtractionWorkflow, Process products using the same detailed logic as main workflow (not simplified, AUTHENTICATION FALLBACK: Check if re-authentication is needed based on various t, AUTHENTICATION FALLBACK: Perform re-authentication using SupplierAuthenticationS, AUTHENTICATION FALLBACK: Record whether product has price for authentication mon, CRITICAL FIX: Find actual supplier cache file including fallback files (+51 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (44): agent_plan_step(), build_prompt(), _build_sandbox_supplier(), _compute_planner_hints(), _compute_rag_info(), _ensure_enqueue_preview_run_id(), execute_tool_call(), _extract_category_urls() (+36 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (34): ApproveRequest, _archive_current_turn(), _begin_new_chat_session(), chat_approve(), chat_history(), chat_reset(), chat_send(), ChatRequest (+26 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (27): _amazon_cache_dir(), _amazon_cache_path(), _append_supplier_cache(), _cancel_marker_path(), _cancel_requested(), _canonical_amazon_cache_path(), _finalize_refresh_run(), _group_products_by_source() (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (13): return 'friendly' | 'avoid' | 'neutral' based on patterns (priority order)., Load AI memory from AI cache file to prevent re-suggesting same categories., Record AI decision for future reference and learning, Detect parent-child URL relationships to prevent double processing.         Ret, Apply subcategory deduplication logic: only include subcategories if parent cate, FBA-aware AI selection with UK business intelligence & enhanced memory., Check if category URL actually contains products (Solution 3), DEPRECATED: URL optimization is now handled by supplier-specific extraction scri (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.1
Nodes (16): close_page_for_url(), get_browser_status(), get_instance(), get_page_for_url(), global_cleanup(), Browser Manager with LRU Cache for Amazon FBA Agent System v3 Provides centrali, Restart browser - alias for restart_browser_gracefully for workflow compatibilit, Restart Chrome process while preserving session state                  Returns (+8 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (4): ControlPlanePaths, ensure_dirs(), get_paths(), get_repo_root()

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (22): extract_enhanced_metrics(), extract_keepa_fees(), financials(), find_amazon_json(), find_amazon_json_by_asin(), find_amazon_json_by_linking_map(), get_supplier_specific_paths(), load_linking_map() (+14 more)

### Community 11 - "Community 11"
Cohesion: 0.2
Nodes (16): addChatBubble(), addThinking(), destroyChart(), escapeHtml(), fetchMetrics(), removeThinking(), renderAllCharts(), renderApproval() (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (16): _acquire_lock(), ControlPlaneWorker, _count_amazon_cache_files(), _count_linking_map_entries(), _count_matched_asins(), _has_run_scoped_financial_report(), _is_cancelled(), main() (+8 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (9): Check if anti-truncation guard should be applied.                  Args:, Merge new data with existing data and deduplicate.                  Args:, Strategy 1: Temp file then atomic replace with retries and backoff., Strategy 2: Create timestamped backup, write temp, then replace., Strategy 3: Use alternative temp directory when target is locked., Strategy 4: Use shutil.move when atomic replace fails.                  Args:, Strategy 5: Direct write (last resort - not atomic).                  Args:, Log telemetry data for save attempts.                  Args:             stra (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (11): get_sentinel_monitor(), get_state(), Record dedicated save retry attempts for later diagnostics., Factory used by the workflow to obtain a monitor instance., Sentinel monitoring utilities used by PassiveExtractionWorkflow.  The original, Global registry that aggregates monitoring data across sessions., Compare cached data counts and log when they diverge significantly., register_session() (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.24
Nodes (5): Search Amazon by title using search bar interaction (not URL building), Extract title from search result element using multiple fallback selectors, Extract ASIN with 4 fallback methods for maximum reliability.          Based o, Search Amazon by EAN and extract data for the best match.         Uses AI for d, Extract data for an Amazon product by ASIN.         This implementation reuses

### Community 16 - "Community 16"
Cohesion: 0.25
Nodes (7): get_domain_from_url(), load_supplier_selectors(), Supplier Config Loader module. Loads supplier-specific CSS selectors and configu, Saves domain-specific selectors to a JSON config file.          Args:         do, Loads selectors for a given domain from a JSON config file.          Args:, Extract domain name from a URL.          Args:         url: The URL to extract d, save_supplier_selectors()

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (2): PathManager, Path Manager - Centralized file path management for Amazon FBA Agent System v3.5

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **78 isolated node(s):** `Search Amazon by title using search bar interaction (not URL building)`, `Browser Manager with LRU Cache for Amazon FBA Agent System v3 Provides centrali`, `Singleton browser manager with LRU page cache.     Provides shared Chrome insta`, `Fallback to Playwright's bundled Chromium when Chrome CDP fails`, `Verify Chrome debug port is accessible (IPv6/IPv4 dual-stack for v139 compatibil` (+73 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (2 nodes): `run_custom_efghousewares-co-uk.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SystemConfigLoader` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.311) - this node is a cross-community bridge._
- **Why does `BrowserManager` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 6`, `Community 7`, `Community 8`, `Community 15`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `FixedEnhancedStateManager` connect `Community 0` to `Community 2`, `Community 3`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Are the 308 inferred relationships involving `SystemConfigLoader` (e.g. with `ToolCall` and `AgentStep`) actually correct?**
  _`SystemConfigLoader` has 308 INFERRED edges - model-reasoned connections that need verification._
- **Are the 227 inferred relationships involving `BrowserManager` (e.g. with `AmazonExtractor` and `FixedAmazonExtractor`) actually correct?**
  _`BrowserManager` has 227 INFERRED edges - model-reasoned connections that need verification._
- **Are the 231 inferred relationships involving `WindowsSaveGuardian` (e.g. with `SimpleMetrics` and `FixedEnhancedStateManager`) actually correct?**
  _`WindowsSaveGuardian` has 231 INFERRED edges - model-reasoned connections that need verification._
- **Are the 150 inferred relationships involving `FixedEnhancedStateManager` (e.g. with `SystemConfigLoader` and `WindowsSaveGuardian`) actually correct?**
  _`FixedEnhancedStateManager` has 150 INFERRED edges - model-reasoned connections that need verification._