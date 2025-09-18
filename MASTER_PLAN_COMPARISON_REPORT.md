diff --git a//dev/null b/docs/MASTER_PLAN_COMPARISON_REPORT.md
index 0000000000000000000000000000000000000000..dcd3be3a32eb31a3b6f79e94f5f67c2d3458dd40 100644
--- a//dev/null
+++ b/docs/MASTER_PLAN_COMPARISON_REPORT.md
@@ -0,0 +1,142 @@
+# Master Plan Comparison Report
+
+## Objective
+Provide an evidence-backed analysis of the default branch, identify
+surgical fixes for state, filtering and resume issues, and compare our
+findings with the previously supplied "Master Plan".
+
+## Methodology
+1. Scanned repository for workflow, scraper and state manager code.
+2. Reviewed logs where available and inspected processing state files.
+3. Traced callbacks and state writes to locate drift sources.
+4. Proposed minimal patches and validation steps.
+5. Compared findings against the supplied Master Plan for gaps or
+   disagreements.
+
+## Repository Inventory
+| Component | Path | Notes |
+|-----------|------|-------|
+| Passive workflow orchestrator | `tools/passive_extraction_workflow_latest.py` |
+| Supplier scraper | `tools/configurable_supplier_scraper.py` |
+| State manager | `utils/fixed_enhanced_state_manager.py` |
+| Logs | `fba_extraction_*.log` (root) |
+
+## Workstreams & Fixes
+
+### A. Prefiltered path cache-save callback
+- **Evidence**: callback present in prefiltered path
+  (`tools/configurable_supplier_scraper.py` lines 1016‑1035) – already
+  implemented.
+- **Action**: verify periodic saves; no further patch required.
+
+### B. Single writer enforcement & phase tracking
+- **Evidence**: product progress callback writes to
+  `update_supplier_extraction_progress_new` causing dual writers
+  (`tools/passive_extraction_workflow_latest.py` lines 4264‑4282)【F:tools/passive_extraction_workflow_latest.py†L4264-L4282】.
+- **Fix**: remove supplier back-write and rely on unified progression.
+
+```diff
+@@
+-                    if product_url:
+-                        self.state_manager.update_supplier_extraction_progress_new(product_url)
++                    # Single writer: avoid legacy supplier back-write
++                    if product_url:
++                        self.state_manager.update_progression_unified(
++                            current_phase="supplier",
++                            current_product_index_in_category=actual_cache_count,
++                            current_category_url=category_url,
++                        )
+```
+
+### C. Denominator freeze
+- **Evidence**: denominator sourced from `len(category_urls)` which may
+  be local to batch (`tools/passive_extraction_workflow_latest.py` lines
+  7575‑7583) leading to `total_categories` drifting to `1`.
+- **Fix**: introduce `_authoritative_total_categories()` and replace all
+  `total_categories` assignments with this frozen value.
+
+### D. Resume fidelity
+- **Evidence**: resume index chosen from reverse gap logic only, ignoring
+  `system_progression` (`utils/fixed_enhanced_state_manager.py` lines
+  285‑333)【F:utils/fixed_enhanced_state_manager.py†L285-L333】.
+- **Fix**: read `system_progression.current_product_index` first and log
+  the source of resume decision.
+
+### E. Late de-dupe gating
+- **Evidence**: `_save_products_to_cache` performs full dedupe scan even
+  when no new products are added (lines 3520‑3544)【F:tools/passive_extraction_workflow_latest.py†L3520-L3544】.
+- **Fix**: short‑circuit when `new_products` is empty to prevent log
+  spam and unnecessary scans.
+
+### F. `__*` serialization hygiene
+- **Evidence**: products appended without filtering internal keys
+  (`new_products.append(p)` at line 3532).
+- **Fix**: strip keys starting with `__` before appending to the cache.
+
+```diff
+-                    new_products.append(p)
++                    sanitized = {k: v for k, v in p.items()
++                                 if not str(k).startswith("__")}
++                    new_products.append(sanitized)
+```
+
+### G. Phase write-through
+- **Evidence**: multiple calls write phase via legacy structures instead
+  of unified progression (e.g., `update_supplier_extraction_progress` at
+  lines 7575‑7583 uses `extraction_phase="amazon_analysis"`).
+- **Fix**: replace with `update_progression_unified(current_phase=...)`
+  at every transition.
+
+## Validation Plan
+1. **Unit tests**: ensure denominator getter returns frozen count; ensure
+   serialization strips private keys.
+2. **Integration**: run supplier scrape with
+   `update_frequency_products=1` and observe `≥1 new` periodic saves.
+3. **Resume**: interrupt run and verify resume banner reflects stored
+   indices and phase from `system_progression`.
+
+## Comparison with Provided Master Plan
+- **Agreement**: Workstreams B–G match the supplied plan; fixes align.
+- **Already implemented**: Workstream A is already present in current
+  code; no patch needed.
+- **Additional notes**: our analysis highlights existing callback
+  implementation and suggests patch wording that writes directly to
+  unified progression during callback (slightly different from the master
+  plan but same goal).
+
+## Additional Peer Review Insights
+
+### Newly Highlighted Considerations
+- **Resume index retrieval**: peer reports recommend using
+  `get_resumption_index()` instead of direct field access so complex
+  resume policies and bounds remain honored.
+- **State validation and atomic saves**: missing guards for corrupted
+  state and lack of explicit verification that all writes use
+  `WindowsSaveGuardian.save_json_atomic`.
+- **Existing contradiction detection**: ensure the "state
+  contradiction" safeguard mentioned in past audits stays functional
+  when refactoring.
+- **Callback error visibility**: progress callback exceptions should log
+  at `WARNING` level for easier diagnosis.
+- **Boundary tests**: add off-by-one resume boundary tests to catch
+  slice errors.
+
+### Points of Disagreement
+- **Shim-based single writer**: mirroring
+  `update_supplier_extraction_progress` into `system_progression`
+  reintroduces dual-writer complexity. Direct calls to
+  `update_progression_unified` better enforce the single-writer model.
+- **Mandatory manifest generation**: one report advocates generating a
+  manifest before filtering. For the current fix set, denominators come
+  from configuration, so manifest generation remains out of scope.
+
+## Open Questions / Assumptions
+- Audit report referenced in instructions not found; analysis based only
+  on repository files.
+- Logs under `/mnt/data/` absent; validation relies on local logs.
+
+## Minimal Changelog
+- Document recommends removing legacy supplier progress writes, freezing
+  denominators, sourcing resume index from `system_progression`, gating
+  dedupe scans, stripping `__*` keys, and ensuring unified phase writes.
+
