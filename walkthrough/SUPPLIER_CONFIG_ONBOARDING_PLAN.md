# Supplier Onboarding: Config-Driven Implementation Plan (Detailed)

Status: Draft for coding agent execution and verification
Last Updated: 2025-09-29

NOTE FOR AGENTS
- Perform your own verification of every file path, timestamp, and content before and after changes.
- Use the MANDATORY_BACKUP_PROTOCOL before any edits. Confirm that no other hardcoded assumptions remain outside the scope listed here.

## Purpose
Provide a precise, file-grounded plan to make supplier onboarding primarily config-driven while retaining manual control for per-site login flows. The goal is to reduce duplicated scripts, eliminate hardcoded supplier values, and make future onboarding largely a matter of adding JSON files and running a generic entry script.

## Current Snapshot (Verified Files)
As of 2025-09-29 (local system time), these files exist and were inspected in this workspace:
- System config: `config/system_config.json` (exists; previously inspected; agent to re-verify).
- CK selector config: `config/supplier_configs/clearance-king.co.uk.json` (exists; EAN selectors include `span.ck-b-code-value`).
- Standalone login helper (hardcoded poundwholesale today):
  - `tools/standalone_playwright_login.py:50` base URL is hardcoded.
  - `tools/standalone_playwright_login.py:112` test product is hardcoded.
- CK auth helper (DOM indicators, no price check): `tools/clearance_king/supplier_authentication_service.py:27, 45, 59`.
- Linking map pathing and atomic save:
  - `tools/passive_extraction_workflow_latest.py:633` initializes `LINKING_MAP_DIR` under output root and creates it.
  - `_save_linking_map(...)` starts around `tools/passive_extraction_workflow_latest.py:1209` (reads/writes via helper and atomic save).
  - `utils/windows_save_guardian.py` ensures `path.parent.mkdir(parents=True, exist_ok=True)` inside `save_json_atomic(...)` before writing.

Agents must re-verify the above lines in their environment.

## What Comes From JSON vs What Stays In Code

JSON (Global; supplier-agnostic)
- File: `config/system_config.json`
- Content examples: pipeline toggles, concurrency, batching, rate limits, output roots, Chrome/CDP, cache/monitoring, global price bounds.

JSON (Per-Supplier; new file)
- File (new, per site): `config/suppliers/<domain>.json`
- Content (keys):
  - `supplier_name`: e.g., "clearance-king.co.uk"
  - `supplier_url`: e.g., "https://www.clearance-king.co.uk"
  - `categories_config_path`: e.g., "config/clearance_king_categories.json"
  - `linking_map_manifest_root`: e.g., "OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/"
  - `login_verification_url`: e.g., "https://www.clearance-king.co.uk/sport-line-aquatic-advanced-swimming-goggles-colours-may-vary-1.html"
  - `credentials`: { "username": "...", "password": "..." } or keyring reference
  - Optional per-supplier overrides (e.g., price bounds, delays)

JSON (Per-Supplier Domain Selectors)
- File: `config/supplier_configs/<domain>.json`
- Content:
  - `field_mappings` (title, price, url, image, ean, barcode, sku, availability)
  - `pagination` (e.g., `next_selector`, `next_url_template`, `page_param`, `max_pages`)
  - `navigation_configuration` hints where applicable
- Example: CK file includes EAN selector `span.ck-b-code-value`; verify `price`, `title`, and pagination/navigation are accurate.

Code (Remains Manual/Hardcoded)
- Import statements in entry scripts (explicit classes to keep import hygiene).
- Per-site login sequence choreography (goto/fill/click/waits) due to variability. Only selectors and `login_verification_url` are config-driven; the steps remain manually coded per site.
- The price verification logic (algorithm) stays in code, but its inputs (base URL, verification URL, selectors) are read from JSON.

## Login Strategy
- Primary success criterion: price-based verification on a known product requiring authentication.
  - Consider "logged in" only when a visible price element contains a numeric currency value (e.g., "£1.20").
  - Reject non-price texts like "login to view price", "sign in", etc.
- Provided CK test product: `https://www.clearance-king.co.uk/sport-line-aquatic-advanced-swimming-goggles-colours-may-vary-1.html`.
- DOM account indicators (e.g., `.customer-welcome`, `.customer-name`) remain secondary signals.

Where it changes:
- Today: `tools/standalone_playwright_login.py:50, 112` hardcode poundwholesale.
- Plan: read `supplier_url` and `login_verification_url` from `config/suppliers/<domain>.json` and feed them into login verification (either directly from runner to a shared helper, or by parameterizing the standalone helper).

## Workflow Parameterization (Files/Keys)

Before (hardcoded in supplier workflow files)
- Category config path: e.g., `config/clearance_king_categories.json`.
- Manifest (linking map) root: e.g., `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/`.
- Supplier URL/name: e.g., `https://www.clearance-king.co.uk`, `clearance-king.co.uk`.
- Credential reference keys: hardcoded key names.

After (read from supplier config; no per-site edits)
- The entry script reads `config/suppliers/<domain>.json` and passes into workflow:
  - `categories_config_path`
  - `linking_map_manifest_root` (or rely solely on `utils.path_manager.get_linking_map_path(supplier_name)`)
  - `supplier_url`, `supplier_name`
  - `credentials` and `login_verification_url` for the login helper

Conceptual example (do not apply yet):
```python
# tools/standalone_playwright_login.py
# Before:
# self.base_url = "https://www.poundwholesale.co.uk"
# test_product = f"{self.base_url}/sealapack-turkey-roasting-bags-2-pack"
# After:
self.base_url = supplier_cfg["supplier_url"]
test_product = supplier_cfg["login_verification_url"]

# run_custom_clearance_king.py (or generic runner)
# Before:
# supplier_name = "clearance-king.co.uk"
# supplier_url  = "https://www.clearance-king.co.uk"
# categories_config_path = "config/clearance_king_categories.json"
# After:
supplier_cfg = load_json(f"config/suppliers/{supplier_key}.json")
supplier_name = supplier_cfg["supplier_name"]
supplier_url  = supplier_cfg["supplier_url"]
categories_config_path = supplier_cfg["categories_config_path"]
```

## Configurable Supplier Scraper
- Prefer the generic `tools/configurable_supplier_scraper.py`.
- Drive behavior entirely from `config/supplier_configs/<domain>.json`:
  - `field_mappings.*` selectors for product extraction.
  - `pagination`: support both next-link selectors and URL-parameter pagination (`next_selector` vs `page_param`/`next_url_template`).
  - `navigation_configuration`: category navigation hints if needed.
- Only create a supplier-specific scraper if behavior cannot be expressed via selectors/pagination JSON.

## Entry Script Design (Small Runner)
- Keep a thin entry script (per-supplier file or a generic `run_supplier.py --supplier <domain>`):
  - Reads `config/system_config.json` and `config/suppliers/<domain>.json`.
  - Merges/pass-through config to workflow/auth.
  - Initializes and uses the shared `BrowserManager`.
- On shutdown, call `await browser_manager.close_browser()` (current manager exposes `close_browser`; there is no `cleanup()` method).

Runner verification commands (examples):
```bash
python -c "from pathlib import Path; import json; p=Path('config/suppliers/clearance-king.co.uk.json'); print(json.loads(p.read_text(encoding='utf-8')))"
rg --line-number "close_browser\(|cleanup\(" run_custom_clearance_king.py
```

## Linking Map Directory and File Creation
- Location: `OUTPUTS/FBA_ANALYSIS/linking_maps/<supplier>/linking_map.json` (supplier name dotted canonical form).
- Creation: ensured by atomic writer (`utils/windows_save_guardian.py`) which creates parent directories if missing and then writes the JSON. The file appears on first save when a linking entry is produced.
- Workflow references: `tools/passive_extraction_workflow_latest.py:633`, `_save_linking_map(...)` around `:1209`.

## Side-By-Side: Current vs Proposed (Brief)
- Script Duplication:
  - Current: Duplicate large workflow/scraper scripts per supplier; edit hardcoded values.
  - Proposed: Single generic scraper + tiny entry runner; site specifics from JSON files.
- Login Verification:
  - Current: DOM indicators primary; standalone helper hardcoded to poundwholesale test product.
  - Proposed: Price-based verification via supplier `login_verification_url`; DOM indicators secondary.
- Paths/Names:
  - Current: Hardcoded supplier URL/name and output paths in Python.
  - Proposed: Pull `supplier_name`, `supplier_url`, `categories_config_path`, `linking_map_manifest_root` from `config/suppliers/<domain>.json`.
- Onboarding Steps:
  - Current: Edit multiple Python files per supplier.
  - Proposed: Add 2–3 JSON files (supplier config, categories, selectors) and run the generic runner.

## Detailed Implementation Plan (Agent Tasks)

0) Safety & Backups (MANDATORY_BACKUP_PROTOCOL)
- Create backup folder and copy affected files before editing.

1) Add Supplier Config (new file)
- Path: `config/suppliers/clearance-king.co.uk.json`
- Contents (example):
```json
{
  "supplier_name": "clearance-king.co.uk",
  "supplier_url": "https://www.clearance-king.co.uk",
  "categories_config_path": "config/clearance_king_categories.json",
  "linking_map_manifest_root": "OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/",
  "login_verification_url": "https://www.clearance-king.co.uk/sport-line-aquatic-advanced-swimming-goggles-colours-may-vary-1.html",
  "credentials": { "username": "<redacted>", "password": "<redacted>" }
}
```

2) Parameterize Standalone Login Helper
- File: `tools/standalone_playwright_login.py`
- Replace hardcoded `base_url` (around line 50) and test product (around line 112) to read from supplier config.
- Keep acceptance rule: visible numeric currency price → success; ignore non-price texts.

3) Use Supplier Config in Runner
- File: `run_custom_clearance_king.py` (or a new generic `run_supplier.py`)
- Load `config/suppliers/<domain>.json` and pass into workflow and login helper; remove hardcoded supplier strings.
- On shutdown, call `await browser_manager.close_browser()`.

4) Keep Selectors in Domain JSON
- File: `config/supplier_configs/clearance-king.co.uk.json` already includes EAN selectors; re-verify `price`, `title`, and `pagination`/`navigation_configuration` keys.

5) Optional: Generic Runner
- Create `run_supplier.py` that takes `--supplier <domain>` and implements steps in (3). Tiny per-supplier scripts may wrap it if desired.

## Verification Checklist (Agent Must Check)
- Existence and timestamps (absolute paths; verify recent writes):
  - `config/suppliers/clearance-king.co.uk.json`
  - `config/supplier_configs/clearance-king.co.uk.json`
  - `tools/standalone_playwright_login.py`
  - `run_custom_clearance_king.py` or `run_supplier.py`
- Content verification:
  - Supplier config keys present and correct; URLs reachable.
  - Selector JSON contains working selectors (`field_mappings`, `pagination` if used).
  - Runner reads supplier config (add a log line dumping resolved paths).
- Runtime verification:
  - Login flow completes; price verification passes on the CK test product URL.
  - Linking map directory and `linking_map.json` auto-created under `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/`.
  - No hardcoded poundwholesale strings remain in login helper or runner.

## Non-Obvious Observations & Risks
- Standalone login helper currently hardcodes poundwholesale; forgetting to parameterize will cause login verification to hit the wrong site/product.
- Auth helper’s negative check (any `a[href*='login']` means not authenticated) can be a false negative if the site keeps a dormant login link after authentication. Keep it as secondary only.
- `BrowserManager` exposes `close_browser` (not `cleanup`); calling `cleanup()` will raise an attribute error.
- Ensure selector JSON supplies robust price selectors for the login verification phase.
- Ensure `pagination` is explicitly defined per site to avoid hidden hardcoded traversal behavior.

## COMPARING PREVIOUS WITH NEW IMPLEMENTATION SYSTEM BEHAVIOR
- Script duplication: many large per site → one generic + tiny wrappers.
- Hardcoded values: many in code → values in `config/suppliers/<domain>.json`.
- Login verdict: DOM indicators / wrong-site test product → price verification on correct supplier product + DOM secondaries.
- Outputs: created ad hoc → ensured by atomic save and verified via explicit checks.
- Onboarding: code edits per supplier → add JSONs and run generic script.

## Agent Notes
- Always re-verify file presence, last write times, and content before and after changes.
- Search for any remaining hardcoded supplier strings (domains, product slugs, output paths) and migrate to JSON where feasible.
- If a site’s login flow or pagination cannot be described in JSON, isolate custom logic in the smallest possible supplier-specific helper to avoid re-introducing duplication elsewhere.


## Deep-Dive References & Snippets (For Agent Analysis)

### Repository Ground Truth: File & Symbol Map
- `tools/configurable_supplier_scraper.py`
  - `_get_selectors_for_domain(domain_or_url)` near ~1677: resolves `config/supplier_configs/<domain>.json`.
  - `extract_ean(...)` near ~3241–3267 (generic); CK-specific copy under `tools/clearance_king/` includes `span.ck-b-code-value`.
- `config/supplier_config_loader.py`
  - `load_supplier_selectors(domain)` cleans domain and loads selector JSON.
- `tools/standalone_playwright_login.py`
  - Hardcoded `base_url` (~50) and test product (~112) → must read from supplier config.
  - Price verification loops multiple selectors; looks for currency + digits.
- `tools/clearance_king/supplier_authentication_service.py`
  - `is_authenticated()` uses DOM indicators + negative login-link check. Keep as secondary after refactor.
- `utils/windows_save_guardian.py`
  - `save_json_atomic(...)` ensures parent directories exist before writing (auto-creates linking_maps folder).
- `tools/passive_extraction_workflow_latest.py`
  - Declares linking map dir around ~633; `_save_linking_map(...)` starts around ~1209.

Suggested ripgrep checks:
```bash
rg -n "_get_selectors_for_domain\(|extract_ean\(|verify_price_access\(|save_json_atomic\(" tools utils config | rg -v "backup|archive|OUTPUTS"
rg -n "poundwholesale|sealapack|login to view price|cleanup\(" tools run_* utils | rg -v "backup|archive|tests|OUTPUTS"
```

### Price-Based Login Acceptance Snippet (Illustrative)
```python
text = await element.text_content()
normalized = (text or "").strip().lower()
is_price = any(c in normalized for c in ["£", "gbp"]) and any(ch.isdigit() for ch in normalized)
contains_login_words = any(w in normalized for w in ["login", "log in", "sign in", "view price", "please login"])
if is_price and not contains_login_words:
    return True
```

### Parameterization Examples (Illustrative)
```python
# Standalone login helper parameters
self.base_url = supplier_cfg["supplier_url"]
test_product = supplier_cfg["login_verification_url"]

# Workflow construction with supplier config
workflow = PassiveExtractionWorkflow(
    config_loader=config_loader,
    workflow_config={
        "supplier_name": supplier_cfg["supplier_name"],
        "supplier_url": supplier_cfg["supplier_url"],
        "categories_config_path": supplier_cfg["categories_config_path"],
        "manifest_root": supplier_cfg.get("linking_map_manifest_root"),
        "use_predefined_categories": True,
    },
    browser_manager=browser_manager,
)
```

### Selector JSON Skeleton (Guide)
```json
{
  "field_mappings": {
    "product_item": ["li.item.product.product-item"],
    "title": ["a.product-item-link"],
    "price": [".price-box .price", "span.price"],
    "url": ["a.product-item-link"],
    "image": ["img.product-image-photo"],
    "ean": ["span.ck-b-code-value", "meta[itemprop='gtin13']"],
    "sku": ["[data-product-sku]"],
    "availability": [".stock span", ".availability"]
  },
  "pagination": {
    "mode": "next_selector",
    "next_selector": "a.action.next",
    "max_pages": 50
  },
  "navigation_configuration": {
    "category_link_selector": "a.category-link"
  }
}
```

### Runner Verification Commands
```bash
python -c "from pathlib import Path; import json; p=Path('config/suppliers/clearance-king.co.uk.json'); print(json.loads(p.read_text(encoding='utf-8')))" 
rg --line-number "close_browser\(|cleanup\(" run_custom_clearance_king.py
```

### Linking Map Sanity Checks
```bash
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/ || echo "dir not yet created"
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk/linking_map.json || echo "file not yet created"
```

### Guided Diff Hints (Do Not Apply Blindly)
```diff
--- a/tools/standalone_playwright_login.py
+++ b/tools/standalone_playwright_login.py
@@
-    self.base_url = "https://www.poundwholesale.co.uk"
+    self.base_url = supplier_cfg["supplier_url"]
@@
-    test_product = f"{self.base_url}/sealapack-turkey-roasting-bags-2-pack"
+    test_product = supplier_cfg["login_verification_url"]
```

```python
# Runner wiring (illustrative)
from pathlib import Path
import json

supplier_key = "clearance-king.co.uk"  # or from --supplier
cfg_path = Path(f"config/suppliers/{supplier_key}.json")
supplier_cfg = json.loads(cfg_path.read_text(encoding='utf-8'))

credentials = supplier_cfg["credentials"]
verification_url = supplier_cfg["login_verification_url"]
# pass to auth / login helper accordingly
```

## Authentication Modules: Roles, Differences, Integration Points

This section clarifies the two auth-related scripts, their intended use, and how they interact after the config-driven changes.

- Standalone Playwright Login
  - File: `tools/standalone_playwright_login.py`
  - Purpose:
    - A self-contained utility for authentication verification, runnable independently or called as a fallback inside workflows.
    - Strongly oriented around price-based verification on a single, known product page.
  - Inputs:
    - `supplier_url` (base) and `login_verification_url` (test product) – read from `config/suppliers/<domain>.json` after parameterization.
    - Optional: CDP port or `BrowserManager` instance for shared Chrome.
  - Behavior:
    - Navigates to login page, fills credentials (selectors may be generic or site-tuned), submits.
    - Loads the test product page and searches for a visible numeric currency price across multiple selectors (e.g., `.price-box .price`, `span.price`, etc.).
    - Declares success if price is found and text does not include login prompts (e.g., "login to view price").
  - Outputs:
    - A structured result (e.g., `LoginResult`) with booleans `success`, `login_detected`, `price_access_verified`, duration, and error text when applicable.
  - When to use:
    - Manual, quick verification when testing credentials/config.
    - Workflow fallback if mid-run authentication appears lost.

- Supplier Authentication Service (per-site helper)
  - Example File: `tools/clearance_king/supplier_authentication_service.py`
  - Purpose:
    - Encapsulate the site-specific login choreography (selectors, timing, multi-step flows) inside the supplier workflow context.
    - Historically used DOM indicators (e.g., `.customer-welcome`) to determine success; moving to price-based confirmation as primary.
  - Inputs:
    - `Page` (from Playwright via shared `BrowserManager`), `credentials`, `login_verification_url` (from supplier config after parameterization).
    - Site-specific selectors for email, password, submit, and optional account indicators.
  - Behavior:
    - Performs the exact sequence the site requires (goto -> fill -> click -> wait), then calls a shared price-verification step.
    - Uses DOM indicators as secondary confirmation to support sites that expose prices pre-login.
  - Outputs:
    - Boolean `True/False` indicating whether session is authenticated.
  - When to use:
    - Primary authentication mechanism in the supplier workflow (at start, and on re-auth attempts during long runs).

- Practical differences
  - Scope: Standalone is a general verifier (can be run by itself), Supplier Auth Service is embedded in workflow logic.
  - Responsibility: Standalone emphasizes verification and resilience; Supplier Auth performs the site’s actual login steps.
  - Integration: The workflow calls Supplier Auth; Supplier Auth may delegate to a shared price verifier (common function or reuse the standalone helper’s logic) for a definitive check.

- Failure and retry
  - Both should tolerate intermittent timeouts and re-attempt a configurable number of times.
  - The workflow should detect session loss and call Supplier Auth again, not the standalone tool directly (unless designed as a fallback).

Textual sequence (happy path)
- Runner loads configs -> Workflow starts -> Supplier Auth runs login -> Price verification passes -> Workflow continues category/product processing.
- If price verification fails -> Supplier Auth returns False -> Workflow logs and either retries or aborts based on policy.

## Hardcoded Audit & Remediation Checklist
- Search and remediate before parameterization:
  - Domain strings (e.g., `poundwholesale`, `clearance-king`) outside of selectors/config loaders.
  - Product slugs used for login verification (e.g., `sealapack-turkey-roasting-bags-2-pack`).
  - Output path fragments hardcoded in code (prefer `utils.path_manager` or config keys).
  - Any lingering `cleanup()` calls on `BrowserManager` (should be `close_browser()`).
- Suggested commands:
  - `rg -n "poundwholesale|sealapack|cleanup\(" tools run_* utils | rg -v "backup|archive|tests|OUTPUTS"`
  - `rg -n "OUTPUTS/FBA_ANALYSIS/linking_maps/" tools | rg -v "backup|archive|tests"`

## Pagination & Navigation Patterns (Config Examples)
- Next-link pagination
  - `pagination.mode: next_selector`, `pagination.next_selector: "a.action.next"`
- URL-parameter pagination
  - `pagination.mode: url_param`, `pagination.page_param: "p"`, `pagination.start: 1`, `pagination.max_pages: 50`
  - Optional `next_url_template`: e.g., `"{base_url}?p={page}"`
- Category navigation hints
  - `navigation_configuration.category_link_selector`: CSS to pick subcategory links.
  - `navigation_configuration.exclude_patterns`: substrings to avoid (e.g., `"/search"`, `"/login"`).

## Supplier Config Template (Inline)
```json
{
  "supplier_name": "<domain>",
  "supplier_url": "https://<domain>",
  "categories_config_path": "config/<supplier>_categories.json",
  "linking_map_manifest_root": "OUTPUTS/FBA_ANALYSIS/linking_maps/<domain>/",
  "login_verification_url": "https://<domain>/<known-product-path>",
  "credentials": { "username": "<user>", "password": "<pass>" },
  "overrides": { "min_price_gbp": 0.01, "max_price_gbp": 50 }
}
```

### Additional Gotchas
- Domain selector JSON filename must exactly match `clean_domain` (e.g., `clearance-king.co.uk.json`), not variants like `-updated.json`.
- Prefer `utils.path_manager` helpers for canonical output paths.
- Ensure console and file logging handle UTF-8 (currency symbols) to avoid misinterpretation during verification.
