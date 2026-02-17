# Product List Refresh Flawless Sandbox + LLM Behavior Fixes

## TL;DR

> **Quick Summary**: Make product-list refresh **100% sandbox-isolated** and **run-scoped** so it never touches main workflow artifacts. Enforce canonical input path under `OUTPUTS/PRODUCTS_LISTS/`, group products by `source_url`, write linking maps every `system.linking_map_batch_size`, and generate a sandbox processing state using `FixedEnhancedStateManager` (same file type and schema as category runs). Then fix control-plane chat so the LLM always plans (no URL fast-path), receives recent chat history to reduce amnesia, and tool outputs are post-validated so paths/limits can’t be hallucinated.
>
> **Deliverables**:
> - Product refresh: sandbox identity cannot collapse; no main-file overwrites
> - Product refresh: canonical products input allowlist + OS-absolute path stored in job
> - Product refresh: run-scoped Amazon cache JSON + no global `amazon_cache` writes
> - Product refresh: periodic linking map persistence + final flush (cancel-safe)
> - Product refresh: sandbox processing state file generated + updated (EnhancedStateManager-compatible)
> - Worker/status: refresh runs show correct resolved paths + artifact booleans
> - LLM: remove URL fast-path; pass chat history; expand limit parsing; normalize/validate tool calls

**Repo root (authoritative base for absolute paths):**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

---

## Context (Triangulated, File-Grounded)

### Confirmed catastrophic failure modes (must fix first)

#### Finding A (CRITICAL): Sandbox identity collapses to base supplier → overwrites main artifacts
**Current behavior**:
- Refresh jobs correctly set `supplier_domain = <domain>__sandbox__<id8>`.
- Runner reads the product list file; if it contains `supplier_domain = <domain>` and no `sandbox_supplier`, the runner overwrites the sandbox supplier to base domain.
- Result: refresh writes to **main** paths (cached_products, linking maps, financials).

**Evidence (3+ sources of truth):**
1) Job payload sets sandbox supplier:
- `OUTPUTS/CONTROL_PLANE/jobs/done/job_2003c1b4-99f6-4caf-8257-efa851a9923b.json:6`
2) Product list file contains base supplier_domain (no sandbox field):
- `OUTPUTS/PRODUCTS_LISTS/products_subset_angelwholesale.json:3`
3) Runner overwrites sandbox supplier:
- `control_plane/run_product_list_refresh.py:166-169`
4) Run log shows main cached_products was written (proof of leakage):
- `OUTPUTS/CONTROL_PLANE/status/2003c1b4-99f6-4caf-8257-efa851a9923b.json:25-27`

#### Finding B (CRITICAL): Refresh writes to global Amazon cache + triggers financial outputs
**Current behavior**:
- Refresh runner writes Amazon cache JSON under `OUTPUTS/FBA_ANALYSIS/amazon_cache/`.
- Refresh runner calls `tools.FBA_Financial_calculator.run_calculations(...)`, producing financial report outputs.

**Evidence (3+ sources of truth):**
1) Refresh runner writes to global cache dir:
- `control_plane/run_product_list_refresh.py:45-51` and `control_plane/run_product_list_refresh.py:248-261`
2) Control-plane tool `read_amazon_cache_by_asin` reads ONLY global cache:
- `control_plane/tools/amazon_cache.py:9-20` (global cache-only lookup; refresh run-scoped cache will not be visible via this tool unless extended)

**Highest-success choice (no protected-file edits):**
- Keep `read_amazon_cache_by_asin` global-only for now.
- For refresh runs, use the sandbox linking map + run-scoped `overrides/<run_id>/amazon_cache/` directory as the supported inspection surface.
- Add explicit status fields (`amazon_cache_dir`, `amazon_cache_count`) for refresh runs so the operator UI surfaces the run-scoped cache without changing `control_plane/tools/amazon_cache.py`.
3) Refresh run log shows financial calculator invoked:
- `OUTPUTS/CONTROL_PLANE/logs/2003c1b4-99f6-4caf-8257-efa851a9923b.log:168-175`

#### Finding C (HIGH): Enqueue resolves `OUTPUTS/...` paths against CONTROL_PLANE root (wrong)
**Current behavior**:
- `enqueue_product_list_refresh` resolves non-absolute paths as `paths.control_plane_root / products_path`, which breaks repo-relative `OUTPUTS/PRODUCTS_LISTS/...`.

**Evidence (3 sources):**
1) Enqueue path resolution:
- `control_plane/tools/product_list_refresh.py:70-83`
2) Runner resolves relative paths against repo root:
- `control_plane/run_product_list_refresh.py:129-132`
3) Product list file exists in repo root outputs:
- `OUTPUTS/PRODUCTS_LISTS/products_subset_angelwholesale.json`

---

## Non-Negotiable Guardrails

- **No secrets touched**: never modify credentials/API keys anywhere.
- **No protected files**: no edits to `tools/*` or `run_custom_*.py` without explicit approval.
- **No git commands**.
- **No main-file overwrites** from product refresh. The refresh workflow must not modify:
  - `OUTPUTS/cached_products/<base_supplier>_products_cache.json`
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/<base_supplier>/linking_map.json`
  - `OUTPUTS/CACHE/processing_states/<base_supplier>_processing_state.json`
  - `OUTPUTS/FBA_ANALYSIS/amazon_cache/*`
  - `OUTPUTS/FBA_ANALYSIS/financial_reports/<base_supplier>/*`

---

## Scope

### IN
- `control_plane/run_product_list_refresh.py`
- `control_plane/tools/product_list_refresh.py`
- `control_plane/chat_orchestrator.py`
- `dashboard/chat_panel.py`
- `control_plane/worker.py`
- `docs/CONCISE_LAUNCH_GUIDE.md` (update canonical path examples; make `OUTPUTS\\PRODUCTS_LISTS\\` canonical; mark `OUTPUTS\\CONTROL_PLANE\\inputs\\` legacy)

### OUT
- Any changes to protected `tools/*` or `run_custom_*.py`.
- Any credential changes.

---

## Verification Strategy (Agent-Executable)

### Baseline safety snapshot (must run before/after any refresh verification run)
Capture mtimes of main artifacts and assert unchanged after refresh run:
```bash
python -c "import pathlib; f=pathlib.Path('OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json'); print('cached_products main:', f.exists(), f.stat().st_mtime if f.exists() else None)"
python -c "import pathlib; f=pathlib.Path('OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk/linking_map.json'); print('linking_map main:', f.exists(), f.stat().st_mtime if f.exists() else None)"
python -c "import pathlib; f=pathlib.Path('OUTPUTS/CACHE/processing_states/angelwholesale_co_uk_processing_state.json'); print('processing_state main:', f.exists(), f.stat().st_mtime if f.exists() else None)"
python -c "import pathlib; d=pathlib.Path('OUTPUTS/FBA_ANALYSIS/amazon_cache'); print('global_amazon_cache_files:', len(list(d.glob('amazon_*.json'))) if d.exists() else 0)"
```

### Cancellation test (periodic persistence)
- Cancel by creating `OUTPUTS/CONTROL_PLANE/status/<run_id>.cancelled` (worker checks this):
  - `control_plane/worker.py:47-56`
- Assert sandbox linking map exists and contains partial entries.

---

## Execution Strategy (Waves)

### Wave 1 (CRITICAL): Sandbox isolation + canonical input path
- Fix sandbox identity override.
- Disable cached_products writes.
- Fix enqueue products_path resolution; enforce allowlist to `OUTPUTS/PRODUCTS_LISTS`.
- Disable financial calculator for refresh until sandbox-safe.

### Wave 2 (CRITICAL): Run-scoped outputs + periodic persistence
- Run-scoped Amazon cache JSON writes under `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/amazon_cache/`.
- Linking map written every `system.linking_map_batch_size` products + final flush.

### Wave 3 (HIGH): EnhancedStateManager processing state + grouping
- Group products by `source_url` (stable order; missing -> `__unknown__`).
- Initialize `FixedEnhancedStateManager` with sandbox supplier; call `initialize_workflow_session()`.
- Call `set_total_categories(...)` and then **call `enter_runtime_phase()` early** so saves are not blocked by startup gating.
- For each group/category: `initialize_category_processing(...)` then `set_frozen_denominator(...)`, then process products.
- Update Amazon progress via `update_amazon_analysis_progress_new(...)` (auto-saves).

### Wave 4 (HIGH): Worker/status truth + LLM behavior
- Worker: refresh-specific resolved_paths/artifacts computed deterministically.
- Chat: remove URL fast-path; pass recent chat history into LLM prompt; expand limit parsing; normalize tool calls.

---

## TODOs (Complete, Single Plan)

> Each task includes: what to do, suggested diff, references, and acceptance criteria.

### 0) Backup protocol (MANDATORY)

### D) Update docs + schema hints (canonical paths)
**Fix addresses**: path hallucinations and operator expectations.

**What to change**:
- In `docs/CONCISE_LAUNCH_GUIDE.md`, make `OUTPUTS\\PRODUCTS_LISTS\\` the canonical product-list refresh input location and mark `OUTPUTS\\CONTROL_PLANE\\inputs\\` as legacy.
- In `control_plane/chat_orchestrator.py` tool schema for `enqueue_product_list_refresh`, update the example `products_path` to `OUTPUTS/PRODUCTS_LISTS/products_subset_<supplier>.json`.

**Acceptance Criteria**:
- The docs no longer instruct placing product-list refresh inputs under `OUTPUTS\\CONTROL_PLANE\\inputs\\`.
- The LLM tool schema hint no longer mentions `OUTPUTS/CONTROL_PLANE/inputs/products_subset.json`.

---

### 0) Backup protocol (MANDATORY)
**What to do**:
- Create `backup/product_refresh_flawless_<YYYYMMDD>/`.
- Copy all files that will be edited into it.

**Files to back up (expected):**
- `control_plane/run_product_list_refresh.py`
- `control_plane/tools/product_list_refresh.py`
- `control_plane/worker.py`
- `control_plane/chat_orchestrator.py`
- `dashboard/chat_panel.py`
- `docs/CONCISE_LAUNCH_GUIDE.md`

**Acceptance Criteria**:
- Backup files exist and have non-zero length.

---

### 1) Fix sandbox identity override (job sandbox is authoritative)
**Fix addresses**: Finding A

**Pre-fix**: product file’s `supplier_domain` can replace sandbox supplier.
**Post-fix**: runner never changes sandbox supplier from job.

**Suggested diff** (`control_plane/run_product_list_refresh.py`):
```diff
@@
-    sandbox_from_file, products = _load_products_from_subset(repo_root, products_path)
-    if sandbox_from_file and sandbox_from_file != sandbox_supplier:
-        sandbox_supplier = sandbox_from_file
+    sandbox_from_file, products = _load_products_from_subset(repo_root, products_path)
+    if sandbox_from_file and sandbox_from_file != sandbox_supplier:
+        log.warning(
+            "Ignoring supplier identity from products file; job sandbox is authoritative. job=%s file=%s",
+            sandbox_supplier,
+            sandbox_from_file,
+        )
```

**Acceptance Criteria**:
- A run with job sandbox supplier and product file base supplier produces outputs under `OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/`.
- Baseline safety snapshot shows main mtimes unchanged.

---

### 2) Disable cached_products writes for product refresh
**Fix addresses**: user requirement + prevents catastrophic overwrite.

**Pre-fix**: refresh writes `OUTPUTS/cached_products/<something>_products_cache.json`.
**Post-fix**: refresh does not write cached_products at all.

**Suggested diff** (`control_plane/run_product_list_refresh.py`):
```diff
@@
-    _write_supplier_cache(repo_root, sandbox_supplier, products)
+    # Guardrail: do not write cached_products during product-list refresh.
+    # The input products list is treated as the supplier cache for this run.
```

**Acceptance Criteria**:
- Baseline mtimes show `OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json` unchanged.

---

### 3) Canonicalize + allowlist products_path under `OUTPUTS/PRODUCTS_LISTS/` and store OS-absolute path
**Fix addresses**: Finding C + user requirement.

**Rules (explicit):**
- If user passes bare filename, resolve to `<repo_root>\OUTPUTS\PRODUCTS_LISTS\<filename>`.
- If user passes repo-relative `OUTPUTS/PRODUCTS_LISTS/<file>`, resolve to `<repo_root>\OUTPUTS\PRODUCTS_LISTS\<file>`.
- If user passes OS-absolute, it must still be under `<repo_root>\OUTPUTS\PRODUCTS_LISTS\`.
- Exception: inline-products flow already produces an OS-absolute file under `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/products_subset.json` (allowed).

**Suggested diff** (`control_plane/tools/product_list_refresh.py`):
```diff
@@
-    candidate_path = Path(products_path)
-    if not candidate_path.is_absolute():
-        candidate_path = paths.control_plane_root / products_path
+    products_lists_dir = (paths.repo_root / "OUTPUTS" / "PRODUCTS_LISTS").resolve()
+    p = Path(products_path)
+    if p.is_absolute():
+        candidate_path = p.resolve()
+    else:
+        norm = str(products_path).replace("\\", "/")
+        if norm.startswith("OUTPUTS/PRODUCTS_LISTS/"):
+            candidate_path = (paths.repo_root / products_path).resolve()
+        else:
+            candidate_path = (products_lists_dir / products_path).resolve()
+
+    # Allow inline-products file under overrides (already OS-absolute)
+    overrides_root = paths.overrides_dir.resolve()
+    allowed = (
+        (products_lists_dir in [candidate_path] + list(candidate_path.parents))
+        or (overrides_root in [candidate_path] + list(candidate_path.parents))
+    )
+    if not allowed:
+        return {"ok": False, "error": "products_path_not_allowed", "products_path": str(candidate_path)}
@@
-    products_path = str(candidate_path)
+    products_path = str(candidate_path)  # Persist absolute into job payload
```

**Acceptance Criteria**:
- Passing `products_path="products_subset_angelwholesale.json"` yields OS-absolute in job.
- Passing `products_path="OUTPUTS/CONTROL_PLANE/inputs/products_subset_angelwholesale.json"` yields `products_path_not_allowed`.

---

### 4) Disable financial calculator for refresh runs until sandbox-safe
**Fix addresses**: Finding B + leakage risk.

**Pre-fix**: refresh calls `run_calculations(sandbox_supplier)`.
**Post-fix**: refresh logs match count only; no financial writes.

**Suggested diff** (`control_plane/run_product_list_refresh.py`):
```diff
@@
-    if not dry_run:
-        successful_matches = sum(1 for r in results if r.get("amazon_asin"))
-        if successful_matches > 0:
-            from tools.FBA_Financial_calculator import run_calculations
-
-            run_calculations(sandbox_supplier)
-            log.info(
-                f"✅ Financial calculations completed for {successful_matches} matched products"
-            )
-        else:
-            log.warning("⚠️  No successful ASIN matches - skipping financial calculations")
+    successful_matches = sum(1 for r in results if r.get("amazon_asin"))
+    log.info("Product list refresh complete: %d/%d matched", successful_matches, len(results))
+    # Financial calculator disabled for refresh runs until sandbox-safe output dirs are implemented.
```

**Acceptance Criteria**:
- Refresh run log does not contain `FBA_Financial_calculator` lines.
- No new files under `OUTPUTS/FBA_ANALYSIS/financial_reports/<base_supplier>/`.

---

### 5) Run-scope Amazon cache JSON writes (no global `OUTPUTS/FBA_ANALYSIS/amazon_cache` writes)
**Fix addresses**: Finding B.

**Pre-fix**: refresh writes `amazon_<asin>_<ean>.json` to global amazon_cache.
**Post-fix**: refresh writes to `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/amazon_cache/`.

**Suggested diff** (`control_plane/run_product_list_refresh.py`):
```diff
@@
-def _amazon_cache_dir(repo_root: Path) -> Path:
-    return repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "amazon_cache"
+def _amazon_cache_dir(repo_root: Path, run_id: str) -> Path:
+    return repo_root / "OUTPUTS" / "CONTROL_PLANE" / "overrides" / run_id / "amazon_cache"
@@
-def _amazon_cache_path(repo_root: Path, asin: str, ean: str) -> Path:
+def _amazon_cache_path(repo_root: Path, run_id: str, asin: str, ean: str) -> Path:
     ean_safe = _sanitize_ean(ean) or "N"
-    return _amazon_cache_dir(repo_root) / f"amazon_{asin}_{ean_safe}.json"
+    return _amazon_cache_dir(repo_root, run_id) / f"amazon_{asin}_{ean_safe}.json"
@@
-    sandbox_supplier = str(job.get("supplier_domain") or "")
+    sandbox_supplier = str(job.get("supplier_domain") or "")
+    run_id = str(job.get("run_id") or "")
@@
-                    out_path = _amazon_cache_path(repo_root, asin, ean)
+                    out_path = _amazon_cache_path(repo_root, run_id, asin, ean)
-                    backups_dir = (... / "amazon_cache_backups")
-                    _backup_existing(out_path, backups_dir)
+                    # Optional: backup no longer needed once cache is run-scoped
```

**Acceptance Criteria**:
- Baseline count of `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_*.json` unchanged.
- New files appear under `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/amazon_cache/`.
- Known limitation: `read_amazon_cache_by_asin` will not find run-scoped cache without a future enhancement.

**Known limitation (must disclose)**:
- `tools/amazon_playwright_extractor.py` may still create `OUTPUTS/CACHE/amazon_data/` (extractor output_dir) because it uses `utils/file_manager.py:39-40` (`cache_amazon` → `CACHE/amazon_data`). This directory creation is tolerated; the critical guardrail is that no **main workflow artifacts** are overwritten. (No screenshot env toggle is assumed here because `DEBUG_SCREENSHOTS` is not referenced in the extractor.)

---

### 6) Periodic linking map persistence + final flush (cancel-safe)
**Fix addresses**: partial-progress loss.

**Pre-fix**: `_write_linking_map` runs once at end (`control_plane/run_product_list_refresh.py:294-296`).
**Post-fix**: write every N products + `finally` flush.

**Implementation details**:
- Load `N` from `config/system_config.json` (`system.linking_map_batch_size`, currently `1`).

**Suggested diff** (`control_plane/run_product_list_refresh.py`):
```diff
@@
+def _get_linking_map_batch_size(repo_root: Path) -> int:
+    try:
+        from config.system_config_loader import SystemConfigLoader
+        cfg = SystemConfigLoader().get_system_config()
+        return max(1, int(cfg.get("linking_map_batch_size") or 1))
+    except Exception:
+        return 1
@@
     async def run() -> None:
         await extractor.connect()
         page = await _ensure_playwright_page(cdp_port=9222)
-        for product in products:
+        batch_n = _get_linking_map_batch_size(repo_root)
+        for idx, product in enumerate(products, start=1):
             ...
             results.append(...)
+            if not dry_run and results and (idx % batch_n == 0):
+                _write_linking_map(repo_root, sandbox_supplier, results)
@@
-    asyncio.run(run())
-
-    _write_linking_map(repo_root, sandbox_supplier, results)
+    try:
+        asyncio.run(run())
+    finally:
+        if results:
+            _write_linking_map(repo_root, sandbox_supplier, results)
```

**Acceptance Criteria**:
- Cancel mid-run using `OUTPUTS/CONTROL_PLANE/status/<run_id>.cancelled`; verify sandbox linking map exists with partial entries.

---

### 7) Group products by `source_url` (stable order) and dedupe
**Fix addresses**: agreed grouping step to emulate category-run semantics.

**Rules**:
- Group by `source_url` (string). Missing → `__unknown__`.
- Preserve category order by first appearance.
- Optional dedupe: if same supplier `url`+`ean` repeats under multiple categories, process once and attribute to first category.

**Suggested diff** (`control_plane/run_product_list_refresh.py`):
```diff
+def _group_products_by_source_url(products: list[dict[str, Any]]):
+    seen: dict[str, list[dict[str, Any]]] = {}
+    order: list[str] = []
+    used: set[tuple[str, str]] = set()
+    for p in products:
+        key = str(p.get("source_url") or "").strip() or "__unknown__"
+        sku = (str(p.get("url") or ""), _sanitize_ean(str(p.get("ean") or "")))
+        if sku in used:
+            continue
+        used.add(sku)
+        if key not in seen:
+            seen[key] = []
+            order.append(key)
+        seen[key].append(p)
+    return [(k, seen[k]) for k in order]
```

**Acceptance Criteria**:
- A list interleaving categories X,Y,X processes X then Y (single pass per category).

---

### 8) Generate sandbox processing state (EnhancedStateManager-compatible)
**Fix addresses**: user requirement for refresh runs to generate sandbox processing state like category runs.

**How sandbox filename is derived (important):**
- Sandbox supplier string is passed into `FixedEnhancedStateManager`, which uses `utils.path_manager.get_processing_state_path(supplier_name)`.

**References:**
- `utils/path_manager.py:211-223` (`get_processing_state_path` naming)
- `utils/fixed_enhanced_state_manager.py:247` (`initialize_workflow_session`)
- `utils/fixed_enhanced_state_manager.py:148` (`enter_runtime_phase`)
- `utils/fixed_enhanced_state_manager.py:1055` (`initialize_category_processing`)
- `utils/fixed_enhanced_state_manager.py:818` (`set_frozen_denominator`)
- `utils/fixed_enhanced_state_manager.py:1154` (`update_amazon_analysis_progress_new`)
- `utils/fixed_enhanced_state_manager.py:1458` (`save_state_atomic`)

**Minimal integration recipe** (public methods only):
1) `sm = FixedEnhancedStateManager(sandbox_supplier)`
2) `sm.initialize_workflow_session()`
3) `sm.set_total_categories(total=<distinct_categories>, manifest_hash=sm.compute_supplier_config_hash(category_urls))`
4) Call `sm.enter_runtime_phase()` **before** relying on any saves performed by progression helpers (save gating):
   - `utils/fixed_enhanced_state_manager.py:148-157` sets `_startup_completed=True`
   - `utils/fixed_enhanced_state_manager.py:1202-1207` blocks saves when `_startup_completed` is false
5) For each category group:
   - `sm.initialize_category_processing(category_index=i, category_url=source_url, total_categories=total)`
   - `sm.set_frozen_denominator(category_url=source_url, discovered_count=len(group), amazon_total=len(group), manifest_urls=[p['url']...])`
   - For each product processed:
     - `sm.update_amazon_analysis_progress_new(product_url=p['url'], increment=1)` (auto-saves via `utils/fixed_enhanced_state_manager.py:1168`)

**Semantics** (explicit and consistent):
- Supplier stage is pre-completed for refresh runs:
  - `supplier_products_needing_extraction = 0`
  - `supplier_products_completed = 0`
- Amazon stage drives progress:
  - `amazon_products_needing_analysis = total_products`
  - `amazon_products_completed` increments via `update_amazon_analysis_progress_new`

**Acceptance Criteria**:
- File exists: `OUTPUTS/CACHE/processing_states/<sandbox_underscored>_processing_state.json`.
- `system_progression.total_categories == distinct(source_url)`.
- `system_progression.amazon_products_completed` increments during run.

---

### 9) Worker/status truthfulness for refresh runs
**Fix addresses**: status JSON currently relies on MetricsLoader heuristics and can show false negatives.

**Change**:
- In `control_plane/worker.py`, if job_type is refresh, compute resolved paths deterministically:
  - processing state path for sandbox supplier
  - linking map path for sandbox supplier
  - run-scoped amazon cache dir

**References:**
- Worker polling loop: `control_plane/worker.py:267-277`

**Acceptance Criteria**:
- Status JSON shows non-null `resolved_paths.processing_state` and `resolved_paths.linking_map` for refresh runs.
- `artifacts.linking_map_exists=true` when sandbox linking map exists.

---

### 10) LLM behavior fixes (after product refresh is airtight)
**User requirement**: LLM must process every prompt (category runs, product list runs, status/log queries). No URL fast-path.

**Fixes**:
1) Remove URL fast-path in `control_plane/chat_orchestrator.py` (category_urls branch at `control_plane/chat_orchestrator.py:362-400`).
2) Add chat history injection:
   - Extend `build_prompt(...)` to accept `chat_history`.
   - Extend `plan_tool_call(...)` to accept `chat_history` and pass through.
   - Pass `st.session_state['chat_messages']` from `dashboard/chat_panel.py`.
3) Expand `_parse_runtime_constraints`:
   - Support “both should be 10”, “set to 10”, tolerate `12products` missing-space.
   - Always enforce parity: if `max_products` set but per-category missing, set equal.
4) Post-validate tool calls:
   - `enqueue_product_list_refresh`: strip hallucinated directories; enforce canonical allowlist and store absolute.
   - `enqueue_run`: enforce max_products parity.
   - `cancel_run`/`show_status`/`tail_logs`: use last_run_id when missing.

**Acceptance Criteria**:
- Prompt: “analyze 12 products from <category url>” produces tool call with `max_products=12` and `max_products_per_category=12`.
- Prompt: “analyze this product list products_subset_angelwholesale.json” produces tool call with `products_path` OS-absolute under `OUTPUTS/PRODUCTS_LISTS`.

---

## Comparison vs the other agent’s merged plan (alignment + misses)

### Misalignments with our agreed requirements
- They propose **keeping URL fast-path**; we agreed to **remove** it so LLM always processes prompts.
- They propose **dropping category grouping** and **dropping processing state generation**; we agreed to include both.

### Good suggestions from their plan that are incorporated here
- Fix sandbox identity override, disable cached_products writes, run-scope amazon cache JSON, disable financial calculator, fix enqueue path resolution, periodic linking map persistence.
- Add chat history injection (“amnesia fix”).
- Expand regex/constraints parsing.

### What *I* missed in the earlier plan (now included)
- Correct product list reference path (must be `OUTPUTS/PRODUCTS_LISTS/...`, not `OUTPUTS/PRODUCTS/...`).
- Concrete, file-grounded `FixedEnhancedStateManager` integration recipe with real method names + line refs.
- Explicit disclosure of extractor side effects: `OUTPUTS/CACHE/amazon_data` directory creation and potential screenshot writes (mitigated via env).

---

## Handoff
- Plan file: `.sisyphus/plans/product-refresh-flawless-and-llm.md`
- Draft notes: `.sisyphus/drafts/product-refresh-flawless-and-llm.md`

Run `/start-work` to execute this plan once approved.
