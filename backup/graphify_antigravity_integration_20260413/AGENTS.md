# AGENTS.md

Authoritative contributor guide for the Amazon FBA Agent System. This file consolidates the December 3rd wiki (`wiki-dec-3`), legacy CLAUDE guidance, and the current codebase into a single, file-grounded reference. References to automation tooling are intentionally excluded; this document is for humans working in this repository.

---

## 0. ABSOLUTE RULES (CRITICAL)

- **NO PROACTIVE SCRIPT EDITS**
  NEVER proactive edit any script, configuration, or structural file if the user explicitly instructs "DO NOT EDIT ANY FILES/SCRIPTS FOR NOW" or gives a similar directive to only investigate/report. Do not ignore this instruction under *any* circumstances, even if you spot an obvious or trivial bug that is blocking progress. You must report the issue and WAIT for explicit permission to edit.

### 0.1 OpenCode Custom Registry

Custom OpenCode assets currently available and intended for active use:

- **Agents** (`C:\Users\chris\.config\opencode\agents\`):
  - `deep-research-agent`
  - `root-cause-analyst`
  - `system-architect`
  - `business-panel-experts`
- **Commands** (`C:\Users\chris\.config\opencode\command\`):
  - `/sc-research`
  - `/sc-product-brief`
  - `/sc-brainstorm`

Usage guidance:
- Use `/sc-research` for broad external research and source-ranked synthesis.
- Use `/sc-product-brief` when turning ideas into execution-ready briefs.
- Use `/sc-brainstorm` for structured ideation and prioritized options.
- Prefer `root-cause-analyst` for failure analysis, `system-architect` for architecture tradeoffs, and `business-panel-experts` for strategic decision framing.

### 0.2 Engineering Heuristics (CRITICAL — Apply Before Implementation)

**Before writing any code, check Section 8.5 for the full decision rules.** Key principles:

- **O(1) over O(n) for lookups:** Always use `dict`/`set` for membership tests and keyed retrieval, never linear scan through lists.
- **Foreground over background processes:** Run long-lived servers (`uvicorn`, `streamlit`) in the foreground of the launching terminal. Never use `start`, `cmd /k`, or detached windows — they orphan processes and leak ports.
- **No `--reload` in stable runs:** Use `--reload` only during active development iteration, never in run scripts that ship to users or run in production-like contexts.
- **One port, one terminal, one process:** Each service gets its own terminal. Kill with Ctrl+C. No `taskkill` should ever be needed.
- **Cache at the right layer:** In-memory singleton caches (dict with mtime invalidation) for data that doesn't change between requests. TTL-based response caching for API responses. Never re-read unchanged files on every request.
- **Atomic writes, never partial:** Use temp-file-then-rename for any persistent state writes. Never overwrite a valid file directly.

---

## 1. Verification, Backup, and Update Protocols

### 1.1 Mandatory Verification Protocols

- **NO_CLAIMS_WITHOUT_VERIFICATION**  
  Never claim that a task is done without reproducible, file-grounded proof.

- **FILE_VERIFICATION** – For any path you reference in code review, docs, or analysis:
  1. **VERIFY_EXISTENCE** – Check that the file/directory actually exists (e.g. `Get-ChildItem`).
  2. **CHECK_TIMESTAMP** – Confirm that timestamps are consistent with the workflow you are describing.
  3. **VERIFY_CONTENT** – Read and analyze the file content before making assertions about behaviour.
  4. **CONFIRM_SUPPLIER** – Ensure you are reasoning about the correct supplier (default: `poundwholesale.co.uk`).
  5. **USE_ABSOLUTE_PATHS** – When describing locations, use full paths rooted at  
     `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`.
  6. **NO ASSUMPTIONS** – Do not reference files or settings you have not actually opened.

### 1.2 Backup Protocol (Critical)

Before editing code, configuration, or key documentation:

1. **CREATE_BACKUP_DIR** – Under the repo root, create  
   `backup/<reason>_<YYYYMMDD>/`.  
   Example for documentation edits:  
   `backup\agents_update_20251203\AGENTS.md`.
2. **COPY_ALL_AFFECTED** – Copy every file you plan to modify into that directory.
3. **VERIFY_BACKUP** – Confirm the backup file(s) exist and have non-zero length before editing.

This mirrors the behaviour described in `wiki-dec-3\6. State Management System\6.2. Fixedenhancedstatemanager Implementation.md` and `utils\fixed_enhanced_state_manager.py`, which always create safe, atomic snapshots before modifying processing state files.

### 1.3 Update Protocol – Cascading Changes

When you change any code, path, or configuration:

1. **CASCADING UPDATES**  
   - Check all files that reference the modified symbol or path (use `rg` + `diagnostics_output\workflow_files.json`).  
   - Update acceptance tests and integration tests if behaviour changes.
2. **DOCUMENTATION SYNC**  
   - Update `AGENTS.md` when high-level workflow or structure changes.  
   - Update `CLAUDE.md` and `CLAUDE_STANDARDS.md` to keep human and tool guidance coherent.  
   - Update relevant `wiki-dec-3` pages if they have diverged from the actual code paths.
3. **PATH CONSISTENCY**  
   - Verify that `utils\path_manager.py` and `config\system_config.json` reflect any path changes.  
   - Check that the dashboard still resolves the same output locations.

### 1.4 Atomic Save and Resume Semantics

The system is intentionally designed to be **file-grounded** and **resumable**, as detailed in:

- `wiki-dec-3\6. State Management System\6.1. Processing State Tracking.md`  
- `wiki-dec-3\6. State Management System\6.3. Resumption Logic And Recovery.md`  
- `utils\fixed_enhanced_state_manager.py`  
- `utils\windows_save_guardian.py`

Key rules:

- Resume pointers (e.g. `system_progression.resumption_ptr`, `persistent_category_index`) **must only advance**; do not reduce them manually in state files.
- All critical writes to:
  - `OUTPUTS\CACHE\processing_states\*`  
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\*`  
  - `OUTPUTS\FBA_ANALYSIS\amazon_cache\*`  
  must go through atomic write patterns (WindowsSaveGuardian, `save_json_atomic`, or equivalent temp-then-replace logic in code).
- When repairing or migrating state, always:
  - Back up the original file under `backup\state_repair_<YYYYMMDD>\`.  
  - Record what changed and why in a small markdown note under `docs\` or `wiki-dec-3\11. Troubleshooting Guide\11.3. State Management Issues\`.

### 1.5 Agreed Implementation Workflow Additions (Word-For-Word)

The following instruction text is intentionally preserved word-for-word from the agreed Oracle/Momus review outcomes and workflow reconstruction:

- "Before any non-trivial implementation, produce a surgical plan for user review that names target files, minimum required fixes, explicit non-goals, edit order, validation order, and rollback scope."
- "Create `backup/<reason>_<YYYYMMDD>/REVERT_TRACKING.md` before edits; list each planned file, intended scope, planned validation, and exact restore source paths."
- "When notes, handoffs, memory, and code disagree, current code plus concrete artifacts/logs/outputs are the source of truth; stale handoffs must be marked superseded, not trusted."
- "After compaction or multi-session interruption, update `.sisyphus/notepads/handoff/session_handoff.md` with authoritative current state, superseded claims, completed work, open questions, next checks, and backup location."
- "For surgical passes, follow explicit step order: evidence gathering -> plan/review -> backup + revert tracker -> implementation -> targeted verification -> docs/memory updates only if verified and approved."
- "In plans and reports, separate minimum required fixes from supporting corrections and optional mitigations; do not present plausible mitigations as mandatory work."
- "Immediately after a compaction event or session resume, you MUST read the latest handoff to re-anchor context and explicitly ignore stale prior interpretations."
- "Create a `REVERT_TRACKING.md` in the backup directory for every implementation pass, mapping each file to its specific change scope, backup path, and validation status."
- "Execute implementation tasks in the exact order specified in the approved plan to maintain dependency integrity and prevent cascading failures."
- "Verify all claims using triangulation across code, logs, and raw run artifacts (e.g., `chat_tool_calls.jsonl`) rather than relying on single-source assertions or heuristic previews."
- "Before editing, generate a surgical implementation plan for review that identifies the minimum necessary changes to address the root cause without over-scoping."
- "Perform verification (LSP, compilation, and targeted sanity checks) after each logical phase of implementation, not just at the end of the session."
- "When internal agent reports or prior handoffs conflict, the current codebase and raw run artifacts are the only authoritative tie-breakers."
- "Explicitly verify that all prompt-defined placeholders (e.g., `{sandbox_id}`, `{run_id}`) are correctly handled and substituted in the implementation logic."

---

## 2. Architecture Overview (Code-Grounded)

This section aligns with `wiki-dec-3\1. Project Overview.md` and `3. Core Architecture\3.1. Workflow Engine.md`, but is constrained to what the current code actually does.

### 2.1 Primary Entry Points

The system uses per-supplier runner scripts as the primary entry points. Each supplier has its own `run_custom_{supplier}.py` file:

| Runner Script | Supplier Domain | Auth Helper Location |
|---------------|-----------------|---------------------|
| `run_custom_poundwholesale.py` | poundwholesale.co.uk | `tools/poundwholesale/` |
| `run_custom_clearance_king.py` | clearance-king.co.uk | `tools/clearance_king/` |
| `run_custom_angelwholesale-co-uk.py` | angelwholesale.co.uk | `tools/angelwholesale-co-uk/` |
| `run_custom_dkwholesale-com.py` | dkwholesale.com | `tools/dkwholesale-com/` |
| `run_custom_efghousewares-co-uk.py` | efghousewares.co.uk | `tools/efghousewares-co-uk/` |
| `run_custom_kdwholesale-co-uk.py` | kdwholesale.co.uk | `tools/kdwholesale-co-uk/` |
| `run_custom_laceywholesale-co-uk.py` | laceywholesale.co.uk | `tools/laceywholesale-co-uk/` |
| `run_custom_wholesaletradingsupplies-co-uk.py` | wholesaletradingsupplies.co.uk | `tools/wholesaletradingsupplies-co-uk/` |

Each runner follows the same structure:
- Initializes logging via `utils\logger.py`
- Loads configuration from `config\system_config.json` through `SystemConfigLoader`
- Connects to an existing Chrome instance via `utils\browser_manager.BrowserManager`
- Performs authentication (if required) using the supplier-specific authentication service
- Invokes `tools\passive_extraction_workflow_latest.PassiveExtractionWorkflow.run()`

- **Legacy master runner** – `run_complete_fba_system.py`  
  - Older orchestration script that still sets a hard-coded OpenAI key and uses `tools\output_verification_node` and `tools\supplier_guard`.  
  - Behaviour differs from the per-supplier runners documented in `wiki-dec-3`; treat it as **legacy** unless you have a specific reason to use it.

### 2.2 Core Workflow Engine

The central orchestrator is:

- `tools\passive_extraction_workflow_latest.py` → class `PassiveExtractionWorkflow`

Responsibilities (as confirmed by the wiki and code):

- Loads the full configuration via `SystemConfigLoader.get_full_config()` and derives the `system` section into `self.system_config`.
- Initializes:
  - State management via `utils\fixed_enhanced_state_manager.FixedEnhancedStateManager` (imported as `EnhancedStateManager` in code).  
  - Supplier scraping via `tools\configurable_supplier_scraper.ConfigurableSupplierScraper`.  
  - Amazon data extraction via `tools\amazon_playwright_extractor.FixedAmazonExtractor`.  
  - Atomic persistence via `utils\windows_save_guardian.WindowsSaveGuardian`.  
  - Path handling via `utils\path_manager.path_manager`.  
  - Monitoring via `utils\sentinel_monitor.SentinelMonitor`.
- Coordinates the full loop:
  1. Load predefined category URLs from `config\*_categories.json` using `_get_predefined_categories`.
  2. Initialize or resume state using the `FixedEnhancedStateManager` and `system_progression` fields.
  3. Run supplier extraction and Amazon analysis in **hybrid mode** (see `hybrid_processing` in `config\system_config.json`) so long as the config enables it.
  4. Save supplier caches, Amazon caches, linking maps, and processing state using atomic operations.
  5. Trigger financial calculations in `tools\FBA_Financial_calculator.run_calculations` once sufficient linking map entries exist.

For detailed sequence diagrams and method-level breakdowns, see:

- `wiki-dec-3\3. Core Architecture\3.1. Workflow Engine.md`
- `wiki-dec-3\5. Data Processing Workflow\5.2. Amazon Product Matching\`

###  No Git Operations During Execution
Do NOT use git commands for verification. No git operations of any kind during execution.

Do not run any git commands (`pull`, `push`, `fetch`, `merge`, `rebase`, `reset`, `checkout`, `commit`, `stash`, etc.) during automated execution. If git becomes necessary, STOP and ask the user.

Note: ** SPECIALLY WHEN ASKED TO REVERTT CHANGES DO NOT USE GIT CMMANDS ( LIKE:git checkout) , when asked to revert you should trace back your steps and revert any edits based on previous steps/responses executed **.

### 2.3 Browser Management

Browser lifecycle is centralized in:

- `utils\browser_manager.py`  
- `wiki-dec-3\8. Browser Automation\8.1. Browser Management.md`

Key facts:

- Uses Playwright’s `chromium.connect_over_cdp` to attach to an **existing** Chrome instance. It does not launch Chromium on its own.  
- Supports IPv6 (`[::1]`) and IPv4 (`127.0.0.1`) endpoints for CDP.  
- Maintains a single, shared browser instance with an LRU page cache (`MAX_CACHED_PAGES = 1`) to keep extension behaviour stable.  
- Implements health monitoring, restart intervals, and memory thresholds to protect long-running sessions.

When running locally:

- Start Chrome explicitly, for example:  
  `chrome --remote-debugging-port=9222 --user-data-dir=C:\ChromeDebugProfile`
- The connection port is currently hard-coded to `9222` in the runners and the workflow’s `_initialize_amazon_extractor`, regardless of the `"chrome"` block in `system_config.json`. Changing `chrome.debug_port` alone will not change the actual port without code changes.

---

## 3. Configuration Management (system_config.json and Supplier Configs)

This section is aligned with `wiki-dec-3\4. Configuration Management\4.1. System Configuration.md` and `4.2. Supplier Configuration.md`, adjusted for the current code.

### 3.1 System Configuration Structure

Primary configuration file:

- `config\system_config.json`

Important top-level sections (as used by current code):

- `"system"` – Global processing settings:
  - `max_products`, `max_products_per_category`, `max_products_per_cycle`, `max_analyzed_products`.  
  - `supplier_extraction_batch_size`, `linking_map_batch_size`, `financial_report_batch_size`.  
  - `reuse_browser`, `max_tabs`, `output_root`.
- `"processing_limits"` – Price and quantity limits:
  - `min_price_gbp`, `max_price_gbp` (the £20 upper bound documented in wiki-dec-3).
- `"performance"` – Request concurrency, timeouts, and rate limiting.
- `"chrome"` – Browser-related settings (currently **not wired** to the actual CDP port in runners or workflow).
- `"analysis"` – ROI and profitability thresholds.
- `"amazon"` – Marketplace, currency, VAT, and fee defaults.
- `"supplier"` – Flags such as `prices_include_vat`.
- `"workflows"` – Per-supplier workflow definitions (PoundWholesale, Clearance King, etc.).
- `"hybrid_processing"` – Controls whether supplier extraction and Amazon analysis are interleaved.

The wiki’s configuration mermaid diagram in `4.1. System Configuration.md` accurately reflects these blocks and how they are intended to be used.

### 3.2 Configuration Loader Usage

File: `config\system_config_loader.py`

- `get_system_config()` – Returns the `"system"` block.  
- `get_full_config()` – Returns the entire parsed JSON; use this when you need access to `"chrome"`, `"performance"`, `"hybrid_processing"`, etc.  
- `get_workflow_config(key)` – Returns `full_config["workflows"][key]`.  
- `get_supplier_config(supplier_name)` and `get_credentials(supplier_name)` – Provide supplier defaults and credentials.

Important nuance:

- The workflow engine uses `get_full_config()` for root-level settings like `"hybrid_processing"` and `"processing_limits"`, but still attempts to read the CDP port from `self.system_config.get("chrome_debug_port", 9222)`. That key does not exist in the current `"system"` block; the default of `9222` is therefore always used.

### 3.3 Supplier Configuration Files

Directory:

- `config\supplier_configs\`

Examples:

- `poundwholesale.co.uk.json`  
- `clearance-king.co.uk.json`

Each supplier config typically includes:

- `base_url` – e.g. `https://www.poundwholesale.co.uk`  
- `login_config`:
  - `login_path`  
  - `test_product_url`  
  - `price_selectors`  
  - `authentication.login_selectors`

These are consumed by:

- `tools\standalone_playwright_login.py`  
- Supplier-specific authentication helpers under `tools\poundwholesale\` and `tools\clearance_king\`.

When adding a supplier, follow `wiki-dec-3\12. Supplier Integration Guide\` and ensure the new config aligns with these patterns.

---

## 4. Data Processing Workflow (Supplier → Amazon → Financials)

Reference wiki: `wiki-dec-3\5. Data Processing Workflow\`.

High-level sequence (mirrors the diagrams in `1. Project Overview.md` and `5. Data Processing Workflow`):

1. **Initialization**
   - Runners prepare logging and connect to Chrome via `BrowserManager`.
   - `PassiveExtractionWorkflow` loads configuration and state.

2. **Supplier Scraping**
   - `ConfigurableSupplierScraper` uses predefined category lists to scrape products in batches (`supplier_extraction_batch_size`).  
   - Products are cached under `OUTPUTS\cached_products\<supplier-normalized>_products_cache.json`.

3. **Amazon Matching**
   - `FixedAmazonExtractor` uses EAN-first, then title-based search to find candidate products on Amazon.  
   - Matching uses configurable similarity thresholds (see `"performance.matching_thresholds"` in `system_config.json`).
   - Results are cached to `OUTPUTS\FBA_ANALYSIS\amazon_cache\amazon_<ASIN>_<identifier>.json`.

4. **Linking and State Updates**
   - Each supplier product is associated with one Amazon ASIN in a linking map:  
     `OUTPUTS\FBA_ANALYSIS\linking_maps\<supplier>\linking_map.json`.  
   - `FixedEnhancedStateManager` updates:
     - `system_progression` (phase, persistent category index, resume pointers).  
     - Product and category counters.  
   - All writes are done atomically via WindowsSaveGuardian or equivalent.

5. **Financial Analysis**
   - `tools\FBA_Financial_calculator.run_calculations(supplier_name)` reads:
     - Supplier cache (`OUTPUTS\cached_products\...`).  
     - Amazon cache (`OUTPUTS\FBA_ANALYSIS\amazon_cache\`).  
     - Supplier-specific linking map.  
   - Computes ROI, net profit, margins, and writes CSVs under:  
     `OUTPUTS\FBA_ANALYSIS\financial_reports\<supplier-normalized>\*.csv`.

6. **Reports and Dashboard**
   - The Streamlit dashboard (`dashboard\app_fixed.py`) reads:
     - Processing state files under `OUTPUTS\CACHE\processing_states\`.  
     - Linking maps and financial reports under `OUTPUTS\FBA_ANALYSIS\`.  
     - Logs under `logs\debug\` and `OUTPUTS\DIAGNOSTICS\`.

For full diagrams, see:

- `wiki-dec-3\1. Project Overview.md` (workflow mermaid graph)  
- `wiki-dec-3\5. Data Processing Workflow\5.2. Amazon Product Matching\`  
- `wiki-dec-3\7. Financial Analysis Module\7.1. Profitability Analysis.md`

---

## 5. State Management System

Reference wiki: `wiki-dec-3\6. State Management System\`.

### 5.1 Processing State Files

Primary state paths (per `utils\path_manager.get_processing_state_path`):

- `OUTPUTS\CACHE\processing_states\<supplier-with-dots-replaced-by-underscores>_processing_state.json`

The state schema is documented in `6.1. Processing State Tracking.md` and implemented in `utils\fixed_enhanced_state_manager.py`. Key fields include:

- `schema_version` – e.g. `"1.2_THREAD_SAFE"`.  
- `created_at`, `last_updated` – ISO timestamps.  
- `supplier_name`.  
- `system_progression` – the authoritative resume pointer structure.  
- `supplier_extraction_progress` – per-category progress.  
- `metadata` – configuration hashes and fix markers.

### 5.2 FixedEnhancedStateManager Behaviour

`FixedEnhancedStateManager` (see `6.2. Fixedenhancedstatemanager Implementation.md`) is responsible for:

- Separating resumption indices from session progress so that interruptions do not reset progress.  
- Freezing category denominators once at startup and guarding against accidental overwrites.  
- Ensuring that `persistent_category_index` and other indices advance monotonically.  
- Providing atomic save methods to commit state safely on Windows.

Whenever you work on this area:

- Use the helper methods already present (e.g. `initialize_workflow_session`, `set_total_categories`, `save_state_atomic`).  
- Do not write ad-hoc JSON writes directly to processing state files.

---

## 6. Browser Automation and Diagnostics

Reference wiki: `wiki-dec-3\8. Browser Automation\`.

Key files:

- `utils\browser_manager.py` – browser lifecycle, CDP attachment, health checks.  
- `utils\browser_circuit_breaker.py` – circuit breaker for repeated failures.  
- `utils\sentinel_monitor.py` – monitors divergence between linking maps and caches.  
- `wiki-dec-3\8. Browser Automation\8.3. Chrome Devtools Protocol Diagnostics.md` – CDP troubleshooting.

Operational notes:

- Always use an existing Chrome instance with `--remote-debugging-port`.  
- Use the wiki troubleshooting guides if:
  - The workflow cannot connect to CDP.  
  - Keepa or SellerAmp extensions are not visible.  
  - The browser becomes unstable during long runs.

---

## 7. Financial Analysis and Reporting

Reference wiki: `wiki-dec-3\7. Financial Analysis Module\`.

Primary implementation:

- `tools\FBA_Financial_calculator.py`

Important details:

- Reads VAT and fee settings from `config\system_config.json` (`"amazon"` and `"supplier"` blocks).  
- Uses `get_supplier_specific_paths(supplier_name)` to:
  - Resolve supplier caches under `OUTPUTS\cached_products\`.  
  - Resolve linking maps under `OUTPUTS\FBA_ANALYSIS\linking_maps\<supplier>\`.  
  - Create supplier-specific financial reports under `OUTPUTS\FBA_ANALYSIS\financial_reports\<supplier-normalized>\`.
- Surfaces CSV fields described in `AGENTS.md`’s original financial section and elaborated in the wiki’s `7.1. Profitability Analysis.md`.

---

## 8. Coding Standards and Development Practices

These standards combine the existing `CLAUDE_STANDARDS.md` expectations with the repo’s formatting and typing rules.

- **Python version** – Target 3.12+ (3.13 is used in tests and examples).  
- **Style** – 4-space indentation, 100-character lines, imports ordered per `pyproject.toml` (Black + Ruff/isort).  
- **Typing** – Public functions should include type hints; avoid implicit `Any`.  
- **Logging** – Use `logging.getLogger(__name__)` and the shared logger configuration in `utils\logger.py`. Avoid bare `print` for runtime events.  
- **Minimal blast radius** – Keep changes as small and focused as possible; follow the update and backup protocols above.  
- **No committed secrets** – Credentials and API keys must be moved into environment variables or ignored configuration files; do not introduce new secrets into tracked files.

For detailed standards, see:

- `CLAUDE_STANDARDS.md` – development guidelines.  
- `wiki-dec-3\2. Installation And Setup.md` – environment and dependency expectations.

### 8.5 Engineering Heuristics (Decision Rules)

These rules guide **architectural and implementation decisions before code is written**. Violating them requires an explicit note explaining why the exception is justified.

#### Data Retrieval Patterns

| Pattern | Always Use | Never Use | Why |
|---------|-----------|-----------|-----|
| Key-based lookup | `dict[key]`, `set.__contains__` | `if item in list`, `list.index()` | Dict/set lookup is O(1); list scan is O(n). At 1,000+ items the difference is measurable; at 10,000+ it becomes a bottleneck. |
| Deduplication | `set()`, `dict.fromkeys()` | `if x not in result: result.append(x)` | Set/dict dedup is O(n); list dedup is O(n²). |
| Group-by | `defaultdict(list)` | Nested loops with `if group == current` | Single-pass grouping vs multi-pass scanning. |
| Existence check | `key in dict` / `key in set` | `any(x == target for x in collection)` | O(1) vs O(n). |

#### Process Lifecycle Patterns

| Context | Correct Pattern | Anti-Pattern | Why |
|---------|----------------|-------------|-----|
| Start a server (uvicorn, streamlit, any long-lived process) | Run in foreground: `uvicorn app:app --port 8000` | `start "Title" cmd /k "uvicorn ..."` or `subprocess.Popen(detached=True)` | Detached/orphan processes ignore Ctrl+C, leak ports, and require manual `taskkill`. Foreground processes die cleanly with Ctrl+C. |
| Development hot-reload | `uvicorn app:app --reload` → developer's terminal only | `--reload` in `run.bat`, shell scripts, or any script that ships to users | `--reload` spawns a reloader subprocess. If the parent dies unexpectedly, the reloader becomes an orphan zombie. Use only during active development, never in launch scripts. |
| Multiple services | One terminal per service, one Ctrl+C per terminal | Single batch file with `start` spawning multiple windows | `start` creates detached processes. Single-terminal multi-service requires PID tracking which is fragile on Windows. |
| Graceful shutdown | `Ctrl+C` → process catches SIGINT → clean exit | `taskkill /F /PID` → process killed mid-operation | Force-kill risks corrupting state files, orphaning browser connections, and leaving temp files. |

#### Caching Patterns

| Context | Correct Pattern | Anti-Pattern | Why |
|---------|----------------|-------------|-----|
| Per-request data that rarely changes (file contents, computed metrics) | Singleton object with mtime-based cache invalidation | Instantiate a new loader per request, each with empty cache | Every new instance starts with empty state, re-reading all source files. The singleton's internal cache gets warm after the first request. |
| HTTP API responses | TTL-based response cache (e.g., 30s dict with timestamp) | Re-compute every response from scratch | Users don't notice 30-second staleness. They do notice 13-second response times. |
| Configuration loading | Load once, cache in memory, reload on file change (mtime) | Re-read config file on every function call | Config rarely changes. File I/O on every call is wasteful. |
| Persistent state writes | Atomic: write to temp file, then `os.replace()` to final path | Overwrite the target file directly | If the process crashes mid-write, the direct approach leaves a corrupted file. Atomic writes guarantee either the old or new version exists — never a partial file. |
| Cross-request state | Module-level singleton or app state (e.g., `_loader_instance = None` with lock) | `MetricsLoader()` on every request | Module-level singletons persist across requests in uvicorn's process model. Per-request instantiation discards all cached data. |

#### Error Handling Patterns

| Context | Correct Pattern | Anti-Pattern |
|---------|----------------|-------------|
| Missing data files | Return empty dict with `state_file_found: False` and continue with defaults | Raise exception that crashes the whole request |
| Network timeouts | Set explicit timeout (e.g., `httpx.Client(timeout=30.0)`) and catch `TimeoutException` | Let requests hang indefinitely |
| Browser connection failures | Circuit breaker pattern: fail fast after N repeated failures, then retry after cooldown | Infinite retry loops that accumulate memory |
| State file corruption | Detect (via JSON parse error), backup the corrupt file, re-initialize with defaults | Assume state files are always valid |

#### Port and Network Patterns

| Rule | Description |
|------|-------------|
| One service, one port | Never run two HTTP services on the same port. Each service gets its own port and terminal. |
| Prevent port conflicts at startup | Check `netstat -ano | findstr :PORT` before attempting to bind. If the port is occupied, report which PID holds it and exit with a clear message rather than crashing with `Errno 10048`. |
| Clean shutdown on port release | Use `try/finally` or `atexit` to ensure sockets are released. On Windows, `SO_REUSEADDR` is not always respected — proper process lifecycle management is required. |
| Document default ports | Every project must document its default port (e.g., "FBA Dashboard: 8001", "Lead Engine Backend: 8000", "Lead Engine Frontend: 8501") in its run instructions. |

#### When to Apply These Rules

1. **Before any new file creation** — Check: does this file need O(1) lookups? Does it start a server? Does it write state?
2. **Before any new function** — Check: does it load data that could be cached? Does it scan a collection?
3. **Before any new `run.bat` / `run.sh`** — Check: does it use `start` or `cmd /k`? If so, remove them. Does it pass `--reload`? If shipping to users, remove it.
4. **Before any new API endpoint** — Check: does it create new object instances per request when a singleton would share cached data?

If uncertain, default to the pattern listed under "Always Use" / "Correct Pattern" and explain the deviation in a comment.

---

## 9. Testing, Quality Gates, and Tooling

Quality gates (mirroring earlier AGENTS content, still valid):

- **Static checks**
  - `ruff check .`  
  - `black --check .`  
  - `mypy tools config utils`
- **Tests**
  - `pytest -q`  
  - `pytest -m "requires_browser"` (with Chrome CDP running)  
  - `pytest --cov=tools --cov=config --cov=utils -q`
- **Optional tox**
  - `tox -e py312,lint,type-check,coverage-report`  
  - `tox -e security` (safety, pip-audit, bandit)

When modifying core workflow, state management, or configuration:

- Prefer targeted tests under `tests\` when available.  
- For configuration changes, run a short dry run (limit categories/products), then inspect:
  - `OUTPUTS\CACHE\processing_states\...`  
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\...`  
  - `OUTPUTS\FBA_ANALYSIS\financial_reports\...`

---

## 10. Dashboard and Monitoring

Reference wiki: `wiki-dec-3\13. Dashboard.md`, plus `11. Troubleshooting Guide\`.

### 10.1 Dashboard

- Entry point: `dashboard\run_dashboard.py`.  
- Main app: `dashboard\app_fixed.py`.  
- Requires `streamlit` and `pandas`.

Launch examples:

```bash
python dashboard/run_dashboard.py
# or
python -m streamlit run dashboard/app_fixed.py --server.port 8501
```

The dashboard reads:

- Processing state files from `OUTPUTS\CACHE\processing_states\`.  
- Linking maps and financial CSVs from `OUTPUTS\FBA_ANALYSIS\`.  
- Debug logs from `logs\debug\`.

### 10.2 Diagnostics

- `OUTPUTS\DIAGNOSTICS\save_telemetry.log` – WindowsSaveGuardian telemetry.  
- `OUTPUTS\DIAGNOSTICS\monitor_trace.log` – run monitor output.  
- `logs\application\*.log`, `logs\debug\*.log`, `logs\api_calls\*.jsonl` – historical behaviour and API traces.

When investigating issues:

- Consult the relevant wiki troubleshooting section under `wiki-dec-3\11. Troubleshooting Guide\`.  
- Cross-check state files and linking maps for consistency (SentinelMonitor logs divergence).

---

## 11. Supplier Onboarding

For onboarding new wholesale suppliers, use the **supplier-onboarding** skill:

- **Skill location**: `.claude/skills/supplier-onboarding/SKILL.md`
- **Wizard utility**: `utils/supplier_onboarding_wizard.py`

### 11.1 Automated 7-Step Workflow

The skill provides a guided workflow:

1. **Data Preprocessing** - LLM validates categories and selectors
2. **Gather Information** - Collects domain, auth requirements, credentials
3. **Prepare Configurations** - Creates JSON config files
4. **Invoke Wizard** - Generates runner script and auth helper
5. **Validate Files** - Verifies generated files are correct
6. **Pre-Run Verification** - Checks system readiness
7. **User Decision** - Test run, main run, or fix issues

### 11.2 Naming Conventions

The system uses three distinct naming forms:

| Context | Form | Example |
|---------|------|---------|
| Config files | Dot-form | `supplier.com.json` |
| System config | Dot-form | `"supplier_name": "supplier.com"` |
| Runner scripts | Hyphen-form | `run_custom_supplier-com.py` |
| Tool directories | Hyphen-form | `tools/supplier-com/` |
| Workflow keys | Underscore-form | `supplier_workflow` |
| State files | Underscore-form | `supplier_com_processing_state.json` |

### 11.3 Quick Wizard Command

```bash
python utils/supplier_onboarding_wizard.py \
  --domain "supplier.com" \
  --categories-source "config/supplier_categories.json" \
  --selectors-source "config/supplier_configs/supplier.com.json" \
  --workflow-key "supplier_workflow" \
  --mode generate \
  --authentication-required false
```

---

## 12. References and Knowledge Base

- High-level guidance: `CLAUDE.md`, `CLAUDE_STANDARDS.md`  
- Installation and setup: `wiki-dec-3\2. Installation And Setup.md`  
- Core architecture and workflow: `wiki-dec-3\1. Project Overview.md`, `3. Core Architecture\3.1. Workflow Engine.md`  
- State management: `wiki-dec-3\6. State Management System\`  
- Financial analysis: `wiki-dec-3\7. Financial Analysis Module\`  
- Browser automation: `wiki-dec-3\8. Browser Automation\`  
- Caching and deduplication: `wiki-dec-3\9. Caching And Deduplication\`  
- Dashboard and monitoring: `wiki-dec-3\13. Dashboard.md`  
- Tooling and project layout: `PROJECT_INDEX.md`, `PROJECT_INDEX.json`, `pyproject.toml`, `tox.ini`

When in doubt, treat `wiki-dec-3` and this `AGENTS.md` as the primary documentation sources and reconcile any older documents (e.g. archived reports under `archive\` or older wiki folders) against the current code paths before relying on them.

---

## 13. Main Script Protection Policy

### 13.1 Protected Files (Read-Only by Default)

The following files are generated artifacts and MUST NOT be edited without explicit user approval:

| File | SHA256 Prefix | Purpose |
|------|---------------|---------|
| `tools/configurable_supplier_scraper.py` | `9249228a` | Core supplier scraping engine |
| `run_custom_poundwholesale.py` | `2fe136a4` | PoundWholesale launcher |
| `run_custom_clearance_king.py` | `514fbe7c` | Clearance King launcher |
| `run_custom_dkwholesale-com.py` | `e4cdd37a` | DK Wholesale launcher |
| `run_custom_efghousewares-co-uk.py` | `4f111523` | EFG Housewares launcher |

Additionally, all files under `tools/` and all `run_custom_*.py` files are protected.

### 13.2 Verification Protocol

Before and after any work session, verify protected file integrity using Python hashlib:

```python
import hashlib, pathlib
h = hashlib.sha256(pathlib.Path(filepath).read_bytes()).hexdigest()[:8]
```


### 13.3 Where to Make Changes

Prefer changes in `control_plane/*` and `dashboard/*`. If behaviour needs adjusting in a runner or tool, prefer fixing the control plane layer or regenerating via the supplier-onboarding skill.


### 13.5 Control Plane Diagnostics

A diagnostics probe is available for investigating supplier pagination and page structure:

```bash
python -m control_plane diagnostics-probe --url <url> --probe-id <id> --html --screenshot
```

Output goes to `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/` including `report.json`, optional `page.html`, and `screenshot.png`.

---

## 14. Memory & Documentation Update Policy

### 14.1 When to Update Memory and Documentation

**Update ONLY after code changes are VERIFIED:**
- Tests pass (pytest, lint, type-check)
- Manual verification complete
- Code is stable (not during active development that may revert)

**Never update during:**
- Active debugging sessions
- Experimental feature development
- Before changes are committed and tested

### 14.2 Verification Gate

Before updating memory or documentation:

1. **Complete changes** → Code is written and tested
2. **Run verification** → `pytest`, `ruff`, `black --check`, or manual test
3. **Run Sentinel check** → `python utils/memory_sentinel.py --check`
4. **Review drift report** → If drift detected, verify it's intentional
5. **User confirmation** → Explicit "Update memory" approval
6. **Update documentation** → Update relevant docs/*.md files
7. **Update Supermemory** → Add new granular memories via supermemory(mode="add", ...)
8. **Refresh baseline** → `python utils/memory_sentinel.py --update`

### 14.3 Staging Area

Draft memory updates in `docs/_MEMORY_STAGING.md` before promoting to:
- Canonical documentation (docs/*.md)
- Supermemory entries (permanent knowledge)

### 14.4 Automation Hooks (Optional)

For OpenCode with plugin support, sentinel.ts can auto-detect edits:
- Events: `file.edited`, `file.watcher.updated`
- Logic: Check if file matches critical patterns → Run sentinel.py → Prompt user if drift detected

---

## 15. Memory Retrieval Policy (Supermemory vs Serena MCP)

### 15.1 When to Query Supermemory

Query Supermemory **immediately after understanding the task**, before planning implementation:

| Query Type | Example | Why |
|------------|---------|-----|
| Architecture | `fixed_enhanced_state_manager.py` | Get file structure and patterns |
| Error patterns | `PCI hardening resume` | Find known fixes |
| Configuration | `python version batch size` | Check project settings |
| Policies | `main script protection` | Verify constraints |
| Workflows | `RAG index control plane` | Understand flow |

**Supermemory contains**: Architecture, error-solutions, configs, policies, patterns (100+ granular memories).

### 15.2 When to Query Serena MCP

Query Serena MCP **only when you need historical context**:

| Query Type | Example | Why |
|------------|---------|-----|
| Root cause | `category_index_persistence` | Full analysis from past sessions |
| Past implementations | `clearance_king_integration` | See how similar work was done |
| Decision rationale | `surgical_fixes_approval` | Understand why choices were made |
| Test results | `verification_complete_session` | Check prior outcomes |

**Serena MCP contains**: Session transcripts, root-cause analyses, historical context (200+ memories).

### 15.3 Execution Order

```
1. Parse user request
2. Query Supermemory → Get architecture/patterns/policies
3. [If needed] Query Serena MCP → Get historical context
4. Plan and implement
5. Verify
6. Update Supermemory (only after verification + approval)
```

### 15.4 Golden Rule

**"Use Supermemory for implementation. Use Serena MCP for context."**

Supermemory gives you the "what" and "how". Serena gives you the "why".

> **Note**: For detailed comparison and examples, see `docs/SERENA_VS_SUPERMEMORY_COMPARISON.md`.

---

## 16. Antigravity Global Skill Environment

For specialized scraping, strategy, and architecture tasks, the system relies on the optimized Antigravity Agent tools located at `C:\Users\chris\.gemini\antigravity\skills\`.

### 16.1 Skill Manifest
A full index of the 66 kept foundational skills (Research, Analysis, Strategy, FBA Wholesale, and Architecture) is documented at:
`C:\Users\chris\.gemini\antigravity\skills\OPTIMIZED_SKILLS_MANIFEST.md`

### 16.2 API Constraints (Apify & Firecrawl)
Many premium scraping skills (e.g., `apify-ecommerce`, `firecrawl-scraper`) contain internal API logic. 
When executing these tools, establish if they are being used purely for local emulation or as true API calls across environments:
1. **Local Mode (Free)**: Extract the logic from the skill documentation but execute it locally via `playwright-skill` connecting to the local Chrome Instance.
2. **Paid API Mode**: Ensure the user has explicitly confirmed API execution and that keys are tracked via `CRED_OMEGA`.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-** (14502 symbols, 23853 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/clusters` | All functional areas |
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/processes` | All execution flows |
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current

---

## 17. Critical Behavioral Rules

### 17.1 Dual Tracking State Architecture

- `system_progression` section = CANONICAL source for resumption logic
- `supplier_extraction_progress` section = legacy compatibility only
- **ONLY CORRECT METHOD**: `update_progression_unified()` for atomic updates to both sections
- **ARCHITECTURAL VIOLATION**: Direct calls to `update_supplier_extraction_progress()`

### 17.2 State Corruption Indicators

- `total_categories` MUST equal the count from the supplier's `*_categories.json` file
- If `total_categories` diverges from the categories JSON, state corruption has occurred
- Dashboard Health Panel validates this automatically

### 17.3 Never Delete Cache Files

- System uses "reverse gap processing" — acts as if cache clear, starts from first URL, uses cache for skip logic
- Cache files are ESSENTIAL for gap processing and resume functionality
- Deleting cache breaks the entire system architecture

### 17.4 File-Grounded Operations

- All state calculations based on actual files (linking_map.json, processing_state.json, cache files)
- Never rely on in-memory variables for progress tracking
- Dashboard reads directly from output files without database
- Resume data reconstructed from linking_map.json on startup

---

## 18. Forbidden Operations

- No command-line in-place editors (`sed -i`, `perl -pi`, `ed`)
- No "auto-fix" Python/Node scripts that reorder or rewrite large file sections
- No mass search-and-replace across repo without a manifest + manual snippet patches

---

## 19. API Key Preservation Policy

**MANDATORY DIRECTIVE: NEVER REMOVE OR MODIFY EXISTING API KEYS**
- **PRESERVE ALL EXISTING API KEYS** in scripts and environment files (comment out if needed)
- **ADD KEYS WHEN NEEDED** but never remove working configurations
- **MAINTAIN FUNCTIONALITY** - Keep all working API integrations intact

---

## 20. Output Structure

```
OUTPUTS/
├── cached_products/                              # Supplier product cache
│   └── <supplier-normalized>_products_cache.json
├── FBA_ANALYSIS/
│   ├── amazon_cache/                             # Individual Amazon product data
│   │   └── amazon_{ASIN}_{EAN_or_title}.json
│   ├── linking_maps/                             # EAN→ASIN mappings
│   │   └── <supplier.domain>/                    # Dotted folder format
│   │       └── linking_map.json
│   └── financial_reports/                        # Profitability analysis
│       └── fba_financial_report_{timestamp}.csv
├── CACHE/
│   └── processing_states/                        # State management for resumability
│       └── <supplier-normalized>_processing_state.json
├── DIAGNOSTICS/                                  # System diagnostics
│   ├── save_telemetry.log
│   ├── sentinels.log
│   └── monitor_trace.log
└── logs/
    ├── debug/                                    # Detailed execution logs
    │   └── run_custom_<supplier>_{timestamp}.log
    └── health/                                   # System health monitoring
```

---

## 21. Environment Variables

```bash
# Browser Automation
CHROME_REMOTE_PORT=9222
PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

# Output Management
OUTPUTS_BASE_PATH=./OUTPUTS
output_root=./OUTPUTS

# Dashboard Configuration
FBA_BASE_DIR=/path/to/project  # Auto-detected if not set

# Supplier Configuration
SUPPLIER_SESSION_TIMEOUT=3600
AUTHENTICATION_RETRY_ATTEMPTS=3

# Amazon API Configuration
AMAZON_REQUEST_DELAY_MS=1000
AMAZON_CACHE_TTL_HOURS=24

# Financial Analysis (UK Marketplace)
DEFAULT_FBA_FEE_PERCENTAGE=15
VAT_RATE_UK=20
PROFIT_MARGIN_TARGET=25

# System Optimization
MAX_CONCURRENT_EXTRACTIONS=3
CACHE_RETENTION_DAYS=30
```

---

## 22. Troubleshooting

### Chrome Connection Issues
```bash
# Check Chrome v139+ IPv6/IPv4 connectivity
netstat -tuln | grep 9222
curl -6 http://localhost:9222/json/version  # IPv6
curl -4 http://localhost:9222/json/version  # IPv4

# Auto-recovery with dynamic endpoint detection
python utils/browser_manager.py --health-check --auto-restart --ipv6-first
```

### Authentication Failures
```bash
# Clear authentication cache
rm -rf OUTPUTS/CACHE/auth_sessions/*.json
python tools/supplier_authentication_service.py --reset-auth
```

### State Corruption Recovery
```bash
# Validate and rebuild state from files
python utils/fixed_enhanced_state_manager.py --validate-state --supplier=poundwholesale-co-uk
python utils/fixed_enhanced_state_manager.py --rebuild-from-cache --file-grounded
```

### Dashboard Issues
```bash
# Dashboard shows "—" for missing data
# 1. Verify FBA_BASE_DIR environment variable
echo %FBA_BASE_DIR%  # Windows

# 2. Check file structure
dir OUTPUTS\CACHE\processing_states\
dir OUTPUTS\FBA_ANALYSIS\linking_maps\

# 3. Verify files exist with correct supplier naming
# Supports both: poundwholesale.co.uk and poundwholesale_co_uk
```

---

## 23. Windows Compatibility & Performance

- Full Windows 10/11 support with native memory management
- Atomic file operations to prevent permission issues
- Windows Memory Manager with accurate process monitoring
- PowerShell and Command Prompt compatibility
- O(1) hash-based duplicate prevention (20-40% improvement)
- Smart memory clearing (99% reduction in operations)
- URL pre-filtering eliminates duplicate processing
- Configurable batch processing for different system capabilities
- Dashboard with chunked data loading for large datasets

---

## 24. MCP Server Integrations

### Zen MCP - Multi-Model Reasoning & Analysis

When complex reasoning is needed:

- **chat**: General collaborative thinking and brainstorming
- **thinkdeep**: Multi-stage comprehensive investigation and reasoning
- **planner**: Interactive sequential planning with step-by-step breakdown
- **consensus**: Multi-model consensus workflow for decision making
- **codereview**: Step-by-step code review with expert analysis
- **debug**: Root cause analysis and systematic debugging
- **analyze**: Comprehensive code analysis and architectural assessment
- **refactor**: Refactoring analysis with code smell detection
- **tracer**: Code tracing workflow for execution flow analysis
- **docgen**: Documentation generation with complexity analysis

### Context7 MCP - Library Documentation

1. `resolve-library-id` - Find Context7 library ID
2. `get-library-docs` - Retrieve focused documentation

### Chrome DevTools (CDP) MCP - Browser Automation

- `navigate_page`, `click`, `fill`, `take_screenshot`, `evaluate_script`
- Use for browser testing, E2E validation, visual regression testing

### Sequential Thinking MCP - Structured Reasoning

Use when: Breaking down complex problems, planning with room for revision, analysis needing course correction, hypothesis generation and verification.

---

## 25. Sub-Agent Orchestration Protocol

### Orchestration Rules

For multi-step or feature development tasks:
1. **ALWAYS START** by invoking the `tech-lead-orchestrator` agent
2. **WAIT** for its structured routing map (named agents, specified order)
3. **USE ONLY** the agents listed in the routing map, in the sequence provided
4. **NEVER** improvise agent selection or skip the orchestrator step
5. **ALL HANDOFFS** managed by main agent, not sub-agent-to-sub-agent calls

### Available Specialized Agents

**Orchestrators & Planning:**
- `tech-lead-orchestrator` - Strategic planning and agent coordination (REQUIRED for multi-step tasks)
- `project-analyst` - Deep project understanding and stack detection

**Core Development:**
- `code-archaeologist` - Codebase exploration and discovery
- `code-reviewer` - Quality assurance and code review
- `performance-optimizer` - Speed and efficiency improvements
- `documentation-specialist` - Technical documentation creation

**Quality & Testing:**
- `test-automator` - Automated testing strategies
- `debugger` - Error diagnosis and resolution
- `security-auditor` - Security vulnerability analysis

**Infrastructure & DevOps:**
- `cloud-architect` - AWS, Azure, GCP infrastructure
- `deployment-engineer` - CI/CD pipelines and deployment

**Data & AI:**
- `database-optimizer` - Query optimization and schema design
- `ai-engineer` - LLM-powered applications and RAG systems


---

## 26. Serena MCP - READ-ONLY Usage (All CLIs)

**Purpose**: Symbol-based code navigation and discovery - applicable in every CLI/IDE that has Serena MCP configured.

**Capabilities**:
- \ind_symbol\ - Locate classes, methods, functions by name
- \ind_referencing_symbols\ - Discover where code is used
- \search_for_pattern\ - Flexible pattern matching
- \get_symbols_overview\ - File structure understanding

**CRITICAL**: Serena is READ-ONLY. Never use for mutations. Only for discovery and verification.

**Order of use**: Investigate -> hypothesize minimal change -> use Serena to validate coverage -> make edits manually.

---

## 27. GitNexus CLI Skill Table (All CLIs)

The GitNexus skills are installed in multiple locations depending on which CLI you are using.

**Claude Code** (.claude/skills/gitnexus/):

| Task | Skill file |
|------|-----------|
| Understand architecture | .claude/skills/gitnexus/gitnexus-exploring/SKILL.md |
| Blast radius | .claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md |
| Trace bugs | .claude/skills/gitnexus/gitnexus-debugging/SKILL.md |
| Rename / refactor | .claude/skills/gitnexus/gitnexus-refactoring/SKILL.md |
| Tools / schema reference | .claude/skills/gitnexus/gitnexus-guide/SKILL.md |
| Index / status / wiki CLI | .claude/skills/gitnexus/gitnexus-cli/SKILL.md |

**Antigravity / Gemini CLI** (.agents/skills/gitnexus/):

| Task | Skill file |
|------|-----------|
| Understand architecture | .agents/skills/gitnexus/gitnexus-exploring/SKILL.md |
| Blast radius | .agents/skills/gitnexus/gitnexus-impact-analysis/SKILL.md |
| Trace bugs | .agents/skills/gitnexus/gitnexus-debugging/SKILL.md |
| Rename / refactor | .agents/skills/gitnexus/gitnexus-refactoring/SKILL.md |
| CLI commands | .agents/skills/gitnexus/gitnexus-cli/SKILL.md |


---

## 28. OpenCode — Specific Notes (AGENTS.md is the native config file for Codex)

### Codex Global Directory

Codex stores all global state, rules, skills, and memories at: C:\Users\chris\.codex\

`
C:\Users\chris\.codex\
  rules/                     # Global Codex rules
    default.rules            → Default ruleset applied to every session
    .system/                 → System-level rules

  skills/                    # Global Codex skills (empty — skills go via .agents/skills/)
  memories/                  # Persistent Codex memories
  sessions/                  # Session history
  archived_sessions/         # Archived session data
  scripts/                   # Codex scripts
  config.toml                # Global Codex configuration
  AGENTS.md                  # Global AGENTS.md (Codex reads this)
  instructions.md            # Global Codex instructions
  .env                       # Environment variables
`

### OpenCode Global Directories

Custom OpenCode agents and commands at C:\Users\chris\.config\opencode\:

`
C:\Users\chris\.config\opencode\
  agents/                    # Custom agents
    deep-research-agent.md   → Broad external research and source-ranked synthesis
    root-cause-analyst.md    → Failure analysis and root cause investigation
    system-architect.md      → Architecture tradeoffs and design decisions
    business-panel-experts.md → Strategic decision framing
    financial-analyst.md     → Financial analysis and modelling
    spreadsheet-analyst.md   → Spreadsheet and data analysis

  command/                   # Custom slash commands
    /sc-research             → Broad external research and source-ranked synthesis
    /sc-product-brief        → Turn ideas into execution-ready product briefs
    /sc-brainstorm           → Structured ideation and prioritized options
    /handoff                 → Session handoff and state capture
    /handoff-deep            → Deep handoff with full context capture
    /supermemory-init        → Initialize supermemory for a session
`

### Project-Level OpenCode Plugin Directory

.opencode/ — OpenCode plugin configuration for this project (bun-based, 
ode_modules present).
