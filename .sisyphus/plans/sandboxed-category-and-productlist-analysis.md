# Sandboxed Category Analysis + Sandboxed Product-List Analysis

## TL;DR

> **Quick Summary**: Make chat reliably start **sandbox runs** for (A) supplier **category URL** input and (B) **product list** input, instead of accidentally returning production linking-map lookups.
>
> **Deliverables**:
> - Deterministic routing: category URL(s) → `enqueue_run` (sandboxed workflow run)
> - Deterministic routing: product list (path or inline JSON) → `enqueue_product_list_refresh` (sandboxed)
> - Deterministic param resolution: domain → `workflow_key` + `runner_script`
> - Tests that lock the routing and prevent regressions
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES (2 waves)
> **Critical Path**: URL/product-list detection → deterministic mapping → tests

---

## Context

### Original Failure (Observed)
- User prompt: `analyze this category: https://angelwholesale.co.uk/Category/Baby-Clothing/Baby-Clothing-Sets`
- Returned: ~50 rows from existing linking map (read-only)

### Grounded Evidence
- The response envelope `{ ok, count, rows, path }` matches `find_linking_entries`:
  - `control_plane/tools/linking_map.py:33`
- Production linking map file exists and contains `created_at` and `confidence`:
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk/linking_map.json:1`
- Planner prompt contains: “Never choose `enqueue_run` unless `category_urls` is a non-empty list.”
  - `control_plane/chat_orchestrator.py:169`
- The tool dispatcher builds sandbox supplier names for `enqueue_run`:
  - `control_plane/chat_orchestrator.py:423` creates `sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}"`
- Workflow mapping exists in config:
  - `config/system_config.json:265` includes `angelwholesale_workflow`.
- Runner exists and uses that workflow key:
  - `run_custom_angelwholesale-co-uk.py:68`

### Confirmed Requirements (User)

**Cache/linking semantics clarification (important):**
- In the current full workflow, having cached products does **not** mean “skip supplier scraping entirely”. The workflow can use cache for progress/backfill, but it still performs fresh extraction to detect updates.
- The “amazon-only backfill” logic is a safety net: it adds cached products to the Amazon analysis queue **only if** they are not in the linking map.
  - The snippet checks `not self.hash_optimizer.check_product_in_linking_map(supplier_url=url)[0]` before adding.
  - So it does **not** reprocess items already present in the linking map.
  - Grounded at `tools/passive_extraction_workflow_latest - Copy (2).py:6117`.

- User may input **one or multiple category URLs**.
- Category analysis must run **sandboxed**: produce new sandbox `linking_map`, `processing_state`, `financial_report`.
- Product list analysis (if product list provided) must run **sandboxed**.
- Existing production files must not be treated as “analysis results”.
- For category analysis, use **Option A (full workflow run)**: scrape supplier category → supplier product extraction → Amazon extraction, but sandboxed.
- Cached products should be leveraged as much as the workflow supports, but we will not invent a new “amazon-only from cache” mode in this plan.

---

## Scope Lock (to avoid ambiguity)

### IN SCOPE
1) Fix chat/tool routing so category URLs enqueue sandbox runs.
2) Fix chat/tool routing so product lists enqueue sandbox product-list refresh.
3) Deterministically fill required enqueue params:
   - `supplier_domain`, `workflow_key`, `runner_script`, `category_urls`.
4) Add tests that run without a browser.
5) Update PRDs/report docs to reflect the routing contract.

### OUT OF SCOPE (explicit)
- Changing core workflow behavior in `tools/passive_extraction_workflow_latest.py` to “supplier-scrape skip / amazon-only mode”.
  - Note: the full workflow already uses cached products for progress/backfill, and cached products contain `source_url` (category URL) per product (example: `OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json:1`), but the workflow still performs supplier scraping.
  - If we later want true “amazon-only from cache” category runs, that is a separate feature.

This plan’s category analysis mechanism is: **enqueue_run → sandboxed full workflow run**.

---

## LLM File Access + RAG (runtime reality)

- The local LLM does not read arbitrary files by itself; it can only see what the control-plane prompt provides and what the orchestrator returns via tools.
- Chat provides broad repo access via read tools:
  - `read_repo_file` can read any repo-relative file up to `max_bytes` (schema shown in `control_plane/chat_orchestrator.py:143`).
  - `list_repo_dir` can list any repo directory.
  - There are also specific read tools for outputs: linking map, cached products, processing state, status, logs.
- Serena MCP is **not** wired into the running chat orchestrator (it is a dev-time navigation/index tool).
- A RAG system **does exist** in chat:
  - `control_plane/chat_orchestrator.py:13` imports `rag_retriever`, and `plan_tool_call` loads `OUTPUTS/CONTROL_PLANE/index/rag_index.json` and injects RAG context.

## Design: Deterministic Routing (no LLM guesswork)

### Why deterministic routing is required
- LLM-only routing can choose read tools that “work” (like `find_linking_entries`) even when the user asked to *run* analysis.
- We must guarantee “category URL input → sandbox job” regardless of the LLM’s JSON output.

### Where to implement routing
- Implement a **pre-router** inside `control_plane/chat_orchestrator.py` BEFORE calling `plan_tool_call()`.
- The pre-router inspects raw user text and, when it finds category URLs or product list inputs, it directly constructs a `ToolCall` and calls `dispatch_tool_call()`.

This ensures:
- Category URLs never fall through to “linking-map lookup” as the primary action.
- Tests can validate behavior without calling the LLM.

---

## Algorithms (must be implemented exactly)

### A) Extract URLs from user text
1) Regex extract all substrings matching `https?://\S+`.
2) Strip trailing punctuation `).,]}` from each URL.
3) Deduplicate while preserving order.

### B) Classify URLs
For each URL:
- Parse netloc as `supplier_domain_candidate` (strip leading `www.`).
- Classify as:
  - **Category URL** if path contains `/Category/` (case-sensitive match on the site’s pattern).
  - **Non-category URL** otherwise.

Then:
- Group category URLs by supplier domain.
- If category URLs exist → route to sandbox `enqueue_run` (one job per supplier).

### C) Resolve `workflow_key` deterministically (supplier_domain → workflow_key)
Input: `supplier_domain` (e.g., `angelwholesale.co.uk`).

Algorithm:
1) Load `config/system_config.json`.
2) Inspect `workflows` mapping.
3) Find the first `workflow_key` where `workflows[workflow_key].supplier_name == supplier_domain`.
   - Example: `config/system_config.json:285` maps `angelwholesale_workflow → supplier_name: angelwholesale.co.uk`.
4) If none found → return `ask_clarify` with `missing_fields=["workflow_key"]` and a message: supplier not configured.

### D) Resolve `runner_script` deterministically (supplier_domain → runner_script)
Algorithm:
1) If `OUTPUTS/CONTROL_PLANE/index/system_index.json` exists, use it:
   - `control_plane/chat_orchestrator.py:69` loads it; inventory.runners list is at `OUTPUTS/CONTROL_PLANE/index/system_index.json:10`.
2) Build expected runner name by convention:
   - `expected = f"run_custom_{supplier_domain.replace('.', '-')}.py"`
   - Example: `angelwholesale.co.uk → run_custom_angelwholesale-co-uk.py`.
3) If system_index has an exact match in `inventory.runners`, use it.
4) Else if a file with that name exists at repo root, use it.
5) Else → return `ask_clarify` with `missing_fields=["runner_script"]`.

### E) Default runtime limits (no ambiguous “choose one”)
- For sandbox category runs, default:
  - `max_products_per_category = 2000` (from `config/system_config.json` system+limits conventions)
  - `max_products = len(category_urls) * max_products_per_category`
- Users can override by explicitly stating limits in chat.

### F) Product list input contract (routing)
The system recognizes “product list analysis” if user text includes either:

1) A JSON file path ending in `.json` (Windows absolute path) AND user says “product list”, “products file”, “refresh these products”.
   - Route to `enqueue_product_list_refresh`.

2) Inline JSON that parses to a list of objects with minimum fields:
   - `url` (string)
   - `title` (string)
   - `price` (number)
   - optional: `ean`, `source_url`

If product list is detected but required params are missing:
- If `supplier_domain` is not known, ask clarify (do not guess).

Reference tool contract:
- `control_plane/tools/product_list_refresh.py:34` (expects `supplier_domain` + `products_path` or inline list)

---

## Concrete TODOs

- [ ] 1. Implement pre-router in chat orchestrator

  **What to do**:
  - Add a deterministic “pre-routing” phase in `control_plane/chat_orchestrator.py` before LLM planning.
  - If category URLs found → bypass LLM → dispatch `enqueue_run` with fully resolved params.
  - If product list found → bypass LLM → dispatch `enqueue_product_list_refresh` or `ask_clarify`.

  **References**:
  - `control_plane/chat_orchestrator.py:76` (`build_prompt` and overall orchestration)
  - `control_plane/chat_orchestrator.py:405` (`dispatch_tool_call` implements `enqueue_run` sandboxing)

  **Acceptance Criteria**:
  - [ ] A category URL in user text never results in `find_linking_entries` as the primary action.


- [ ] 2. Implement deterministic mapping helpers

  **What to do**:
  - Implement the exact algorithms C and D above to resolve:
    - `workflow_key` from `config/system_config.json`
    - `runner_script` from system index or naming convention

  **References**:
  - `config/system_config.json:265` (`workflows` mapping)
  - `OUTPUTS/CONTROL_PLANE/index/system_index.json:10` (runner inventory)
  - `run_custom_angelwholesale-co-uk.py:68` (workflow key example)

  **Acceptance Criteria**:
  - [ ] For `angelwholesale.co.uk`, resolved `workflow_key=angelwholesale_workflow` and `runner_script=run_custom_angelwholesale-co-uk.py`.


- [ ] 3. Implement category URL grouping policy

  **What to do**:
  - Support one or multiple category URLs.
  - Enqueue one job per supplier with `category_urls=[...]` (deduped).

  **Acceptance Criteria**:
  - [ ] Two Angel category URLs in one prompt → one `enqueue_run` call with 2 URLs.


- [ ] 4. Add deterministic tests (no LLM, no browser)

  **What to do**:
  - Add tests under `tests/unit/`.
  - Use `monkeypatch` to patch `control_plane.paths.get_repo_root()` so writes go to a temp repo root.
  - In that temp repo root, create minimal required files:
    - `config/system_config.json` (minimal workflows section containing Angel)
    - `run_custom_angelwholesale-co-uk.py` (empty stub file, since tests don’t execute it)
    - optionally `OUTPUTS/CONTROL_PLANE/index/system_index.json` for runner inventory coverage

  **Tests to implement** (exact names):
  - `tests/unit/test_chat_routing_sandbox.py::test_category_url_enqueues_run`
  - `tests/unit/test_chat_routing_sandbox.py::test_multiple_category_urls_grouped_by_supplier`
  - `tests/unit/test_chat_routing_sandbox.py::test_unknown_supplier_domain_returns_ask_clarify`

  **Acceptance Criteria**:
  - [ ] `pytest -q tests/unit/test_chat_routing_sandbox.py` → PASS


- [ ] 5. Update docs to reflect the routing contract

  **What to do**:
  - Update these docs to explicitly state:
    - “Category URL means sandbox run”
    - “Linking-map lookup is only for explicit ‘show linking map’ requests”

  **References**:
  - `SYSTEM_CHAT_UI_PRDS/PRD_03_CHAT_UX_ONLY_v1_1.md`
  - `SYSTEM_CHAT_UI_PRDS/PRD_04_CHAT_PLUS_PRODUCT_LIST_REFRESH_v1_1.md`
  - `SYSTEM_CHAT_UI_PRDS/PRODUCT_LIST_REFRESH_GAPS_REPORT_AND_AGENT_PROMPT.md`

  **Acceptance Criteria**:
  - [ ] Docs mention the deterministic pre-router behavior.

---

## Automated Verification Commands

- `pytest -q tests/unit/test_chat_routing_sandbox.py`

---

## Handoff Notes

- Category URL analysis uses the existing sandboxing in `dispatch_tool_call` for `enqueue_run`.
- This produces sandbox outputs because the merged config overrides `workflows[workflow_key].supplier_name` to the sandbox supplier.

