# Run Report: `9a250a20-35a4-4c3b-88b7-203f06175dd8` (angelwholesale sandbox)

## TL;DR (Concise)

- The run **did execute successfully** (`state: done`) and produced sandbox outputs, including a sandbox linking map dir and sandbox supplier cache, but the **Control Plane Run Monitor UI is showing non-sandbox paths** for `processing_state`, `linking_map`, and `financial_dir` because the dashboard resolver (`dashboard/metrics_core.py`) does **not** understand `__sandbox__<runid>` naming for `state_file` and prefers non-sandbox financial directories.
- The workflow **connected to an existing Chrome instance via CDP on port 9222**, which strongly implies a headed browser (extensions require headed Chrome), but because the BrowserManager explicitly **reused an existing page**, you might not visually see navigation if the automation used a background tab/page.
- A sandbox folder is created per run using `__sandbox__{run_id[:8]}`; this will generate a new folder per run unless you intentionally reuse the same `run_id` or provide a stable `sandbox_suffix`.

---

## Scope

You asked for:
1. Explain why Operator Control Plane shows the paths it shows.
2. Determine if the run was headed despite not seeing the browser move.
3. Analyze artifacts/logs/output files and create an evidence-backed report (each claim backed by 2–3 sources).
4. Confirm whether new sandbox folders are created per run, and propose a way to group them under a supplier "sandbox main folder".
5. Prepare for a **product list sandbox workflow test**:
   - confirm whether multiple categories are supported
   - generate ~6 products (2 per category if supported, else 6 from one category)
   - confirm how to input: in chat vs file

---

## Evidence Map (Sources of Truth)

For every point below, I cite 2–3 independent artifacts among:
- Status file: `OUTPUTS/CONTROL_PLANE/status/9a250a20-35a4-4c3b-88b7-203f06175dd8.json`
- Job file: `OUTPUTS/CONTROL_PLANE/jobs/done/job_9a250a20-35a4-4c3b-88b7-203f06175dd8.json`
- Worker-runner log: `OUTPUTS/CONTROL_PLANE/logs/9a250a20-35a4-4c3b-88b7-203f06175dd8.log`
- Workflow debug log: `logs/debug/run_custom_angelwholesale-co-uk__sandbox__9a250a20_20260201_013612.log`
- Sandbox outputs:
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__9a250a20/linking_map.json`
  - `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__9a250a20_processing_state.json`
  - `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__9a250a20_products_cache.json`
  - `OUTPUTS/FBA_ANALYSIS/financial_reports/angelwholesale-co-uk__sandbox__9a250a20/*`
- Control plane code:
  - `control_plane/worker.py`
  - `control_plane/chat_orchestrator.py`
- Dashboard resolver:
  - `dashboard/metrics_core.py`

---

## 1) Did the run really execute? (Yes)

**Claim:** The run executed and finished successfully.

**Evidence:**
- Status reports completion: `state: "done"` with `ended_at` set in `OUTPUTS/CONTROL_PLANE/status/9a250a20-35a4-4c3b-88b7-203f06175dd8.json`.
- Job payload confirms it was a workflow run: `job_type: "run_workflow"` with `runner_script: "run_custom_angelwholesale-co-uk.py"` in `OUTPUTS/CONTROL_PLANE/jobs/done/job_9a250a20-35a4-4c3b-88b7-203f06175dd8.json`.
- Workflow log shows successful completion: `✅ Workflow completed successfully` in `OUTPUTS/CONTROL_PLANE/logs/9a250a20-35a4-4c3b-88b7-203f06175dd8.log`.

---

## 2) Why does Operator Control Plane show non-sandbox paths?

You saw in the Run Monitor JSON:
- `processing_state` pointing to `...OUTPUTS\CACHE\processing_states\angelwholesale_co_uk_processing_state.json`
- `linking_map` pointing to `...OUTPUTS\FBA_ANALYSIS\linking_maps\angelwholesale.co.uk\linking_map.json`
- `financial_dir` pointing to `...OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk`

**Claim:** Those are coming from the dashboard/metrics resolver and are *not* guaranteed to be sandbox-aware.

**Evidence:**
- The worker Run Monitor populates `resolved_paths` via `MetricsLoader.resolve_paths(supplier_domain)` (see `control_plane/worker.py` where `_read_processing_progress` calls `loader.resolve_paths(supplier_domain)`).
- `MetricsLoader.resolve_paths()` only checks state file patterns like `{normalized}_processing_state.json` and does **not** consider sandbox naming like `{normalized}__sandbox__XXXX_processing_state.json` (see `dashboard/metrics_core.py:34+`, patterns at lines around `53–56`).
- Your sandbox processing state file actually exists at `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__9a250a20_processing_state.json`, but the resolver returned the non-sandbox path in `OUTPUTS/CONTROL_PLANE/status/9a250a20-35a4-4c3b-88b7-203f06175dd8.json`.

**Implication:** The run may have used sandboxed outputs, but the Run Monitor UI is *displaying* canonical outputs due to resolver limitations.

---

## 3) Headed vs headless: was the run headed?

### 3.1 Strong evidence: it connected to an existing Chrome debug session

**Claim:** The workflow used an existing Chrome instance connected via CDP on port 9222, which is typically a **headed** Chrome profile with extensions.

**Evidence:**
- `utils.browser_manager` log lines show: `Connecting to existing Chrome debug instance on port 9222` and `Successfully connected to existing Chrome debug instance` in `logs/debug/run_custom_angelwholesale-co-uk__sandbox__9a250a20_20260201_013612.log`.
- The merged config sets `chrome.headless: false` and `chrome.debug_port: 9222` in `OUTPUTS/CONTROL_PLANE/overrides/9a250a20-.../system_config.merged.json`.

### 3.2 Why you might not have seen the browser move

**Claim:** You might not see visible navigation even with headed Chrome because the BrowserManager reused an existing page/tab and may have navigated in a background tab.

**Evidence:**
- The BrowserManager log: `Using existing context with 4 pages` and `Reusing existing page in persistent context` in `logs/debug/run_custom_angelwholesale-co-uk__sandbox__9a250a20_20260201_013612.log`.
- The workflow did navigate (at least within automation) because it scraped supplier category + extracted Amazon pages (e.g. `Scraping category: https://angelwholesale.co.uk/...` in the debug log, and Amazon extraction lines in `OUTPUTS/CONTROL_PLANE/status/...last_log_lines`).

### 3.3 Extension dependency is acknowledged in logs

**Claim:** The Amazon extractor explicitly waits for Keepa/SellerAmp extensions.

**Evidence:**
- Status last lines include: `Waiting an additional 7s for extensions (Keepa, SellerAmp)...` in `OUTPUTS/CONTROL_PLANE/status/9a250a20-...json`.
- Worker-runner log shows Keepa iframe checks and Keepa AG Grid parsing in `OUTPUTS/CONTROL_PLANE/logs/9a250a20-...log`.

**Open risk:** I do not see explicit evidence of **ad blocker filtering sponsored listings** in this run’s logs. If that’s required, we should add explicit log markers + checks (e.g., count sponsored items filtered) in the Amazon search parsing code.

---

## 4) Sandbox outputs created for this run (what exists)

**Claim:** This run created sandboxed outputs.

**Evidence:**
- Log claims it saved linking map to the sandbox dir: `...\OUTPUTS\FBA_ANALYSIS\linking_maps\angelwholesale.co.uk__sandbox__9a250a20\linking_map.json` in `OUTPUTS/CONTROL_PLANE/logs/9a250a20-...log`.
- The sandbox linking map file exists and contains entries in `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__9a250a20/linking_map.json`.
- The sandbox cache file exists and contains 9 products in `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__9a250a20_products_cache.json`.
- The sandbox financial reports exist under `OUTPUTS/FBA_ANALYSIS/financial_reports/angelwholesale-co-uk__sandbox__9a250a20/`.

**Notes / Issues found:**
- `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__9a250a20_processing_state.json` has internal inconsistencies:
  - `total_products: 9` but `successful_products: 10`, and `supplier_progress_ratio_readable: "9/11"`.
  - This could be expected if the state manager counts multiple events per product, but it’s worth validating.
  - Evidence sources: the processing state file + workflow log lines showing 11 product URLs discovered (manifest says `count: 11`).

---

## 5) Will every run generate a new `__sandbox__...` folder?

**Claim:** Yes, by default each run creates a new sandbox supplier name by appending a sandbox suffix derived from the run id.

**Evidence:**
- `control_plane/chat_orchestrator.py` constructs `sandbox_suffix = f"sandbox__{run_id[:8]}"` and then `sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}"`.
- The resulting job + categories subset use that sandbox supplier:
  - `OUTPUTS/CONTROL_PLANE/overrides/.../categories_subset.json` shows `supplier_domain: "angelwholesale.co.uk__sandbox__9a250a20"`.
  - The workflow debug log uses that session supplier name, and output paths include `...angelwholesale.co.uk__sandbox__9a250a20...`.

### Requested behavior: per-supplier "sandbox main folder"

Right now, sandbox runs already group by supplier name prefix because all dirs start with `angelwholesale...__sandbox__<id>` under each output root.

If you specifically want an additional nesting level like:
`OUTPUTS/FBA_ANALYSIS/linking_maps/sandboxes/angelwholesale.co.uk/<runid>/linking_map.json`
then that requires code changes in the path resolution layer (likely `utils/path_manager.py` and the workflow’s linking map path builder).

I have not implemented this yet, but I can propose a safe migration plan:
- Add new optional base folder `OUTPUTS/FBA_ANALYSIS/linking_maps/__sandbox_runs__/<supplier>/<runid>/...`
- Keep current paths for backward compatibility
- Update dashboard resolver to detect the new pattern

---

## 6) Product List Refresh "Sandboxed Product List" Workflow

### 6.1 Does it support multiple categories?

**Claim:** It does not care about categories; it accepts an arbitrary list of products.

**Evidence:**
- `control_plane/tools/product_list_refresh.py` schema accepts `products: list[dict]` and writes them to `products_subset.json` without any category grouping.
- `control_plane/run_product_list_refresh.py` iterates `for product in products:` and for each product uses only `title`, `url`, `ean`, `price`.

So you can mix products from different categories freely.

### 6.2 Should you input the list in Chat UI or place a file?

There are two supported methods:

1) **Inline list via tool call** (not yet wired from chat UI text parser; would require the LLM to output `enqueue_product_list_refresh` with a `products_path` OR extending it to pass `products` directly).
2) **File path approach** (supported today):
   - You create a JSON file, then ask chat to run `enqueue_product_list_refresh` pointing to it.

**Evidence:**
- Chat tool schema only allows `products_path` (`control_plane/chat_orchestrator.py` tool schema shows `products_path: "C:/path/to/products_subset.json"`).
- `enqueue_product_list_refresh` supports both `products` and `products_path`, but chat currently passes `products=None` and uses `products_path` (see `control_plane/chat_orchestrator.py` `enqueue_product_list_refresh` handling).

### 6.3 Proposed 6-product list for your test

Because category mixing is supported, here is a 6-item list from **3 categories** (2 each), using URLs already seen in your manifest (category = Wholesale Yellow Partyware) plus two more categories you can choose.

I need one small input from you: which other 2 AngelWholesale categories do you want to use besides `Wholesale-Yellow-Partyware`?
- Option A: You paste 2 category URLs.
- Option B: I’ll pick two at random from your existing AngelWholesale categories config once you confirm where it lives.

For now, here are 2 products we already have evidence for (from manifest + cache):
- Yellow Plastic Platters - Pack of 3 (`https://angelwholesale.co.uk/Item/Yellow-Plastic-Platters---Pack-of-3-YEPP890`, EAN `0013051487805`)
- Yellow Rectangle Plastic Table Cover (`https://angelwholesale.co.uk/Item/Yellow-Rectangle-Plastic-Table-Cover-54-X-104-Inch--msc08694`, EAN `5055579191784`)

Evidence: `OUTPUTS/manifests/...manifest.json` + `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__9a250a20_products_cache.json`.

---

## 7) Fixes Still Needed (What I recommend next)

1. **Dashboard resolver should become sandbox-aware**
   - Update `dashboard/metrics_core.py:resolve_paths()` to also look for:
     - `*_processing_state__sandbox__*_processing_state.json` patterns
     - `financial_reports/<supplier>__sandbox__*` directories
     - `linking_maps/<supplier>__sandbox__*` directories
   - Evidence this is needed: Run Monitor shows non-sandbox paths while sandbox files exist.

2. **Run Monitor should display the sandbox supplier**
   - In `control_plane/worker.py`, `supplier_domain` stored in status is the job’s `supplier_domain`.
   - For workflow runs, the job’s `supplier_domain` is the base domain, not the sandbox supplier.
   - Consider adding `sandbox_supplier` into status file explicitly.

3. **Explicit “headed + extensions + adblock active” verification logs**
   - Right now we infer from CDP usage and Keepa parsing.
   - Add explicit checks (e.g. detect Keepa iframe, detect uBlock extension or sponsored listing count filtered) and log a clear “EXTENSIONS_OK” marker.

---

## Questions for You (to finish the product-list test setup)

1) Paste 2 additional AngelWholesale category URLs you want included (so I can pick 2 products from each category), OR confirm you’re fine with 6 products all from `Wholesale-Yellow-Partyware`.

2) Do you want the product list test to be executed via:
- A JSON file you place somewhere (recommended: `OUTPUTS/CONTROL_PLANE/overrides/<runid>/products_subset.json` is already how the tool works), or
- Manual chat paste (would require extending the chat parser to accept raw JSON and pass it as `products`)?

Once you answer (1) and (2), I can generate the exact `products_subset.json` content + the exact chat command/tool invocation you should use.
