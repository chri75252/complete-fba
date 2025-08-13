diff --git a//dev/null b/ALWAYS_EXTRACT_WORKFLOW_AUDIT.md
index 0000000000000000000000000000000000000000..da299278d4de98da2b2c670b85d50e1553bd5287 100644
--- a//dev/null
+++ b/ALWAYS_EXTRACT_WORKFLOW_AUDIT.md
@@ -0,0 +1,91 @@
+# Always-Extract Workflow Audit Findings
+
+## 1. Critical System-Level Issues
+
+### 1.1 Resume Pointer Regression & State Drift
+- **Specification Expectation**: Resume breadcrumbs must show the true category/product indices and monotonically increase.
+- **Log Evidence**: `RESUME PTR: phase=supplier cat_idx=0/1 ... prod_idx=1/pending` repeats for categories processed later in the run.
+- **State Snapshot Evidence**:
+  - `poundwholesale_co_uk_processing_state_PRERUN.json` – `resumption_index=0`, `total_products=7597`.
+  - `processing_state_during_longrun.json` – `resumption_index=0`, `total_products=8`.
+  - `poundwholesale_co_uk_processing_state.json` (post rerun) – `resumption_index=8378`, `total_products=9030`, `system_progression.current_category_index=0`.
+- **Root Cause**: `state_manager.save_state()` logs breadcrumbs from `system_progression`, but callers save before updating `system_progression`, leaving totals at default values. Dual progress structures (`supplier_extraction_progress` vs `system_progression`) drift, causing resume regression.
+- **Suggested Fix**: Update `system_progression` prior to each save and enforce monotonic checks in `load_state()`.
+
+### 1.2 Linking-Map ↔ Cache Precedence Violations (Pattern Combination #2)
+- **Spec Requirement**: Filtering order is linking-map → supplier cache → extraction; processed-but-unlinked items must be reclassified to Amazon analysis.
+- **Log Evidence**:
+  - Category 4: `FILTER[C4]: in=176 skip=175 needs_full=1`; soon after, `Product already processed... Skipping.` and linking-map count stays 8074.
+  - Category 17: `FILTER[C17]: in=137 skip=134 needs_amz=2 needs_full=1`; both items skipped, linking-map unchanged.
+  - Category 25: `FILTER[C25]: in=110 skip=105 needs_amz=3 needs_full=2`; four products skipped, linking-map only increments from 8074 → 8076.
+- **Root Cause**: `filter_urls()` ignores `processed_products` state. Items existing in supplier cache but absent from linking-map are flagged `needs_full_extraction`; later, execution sees them as processed and skips without creating linking-map entries or Amazon cache.
+- **Suggested Fix**: On startup, reconcile `processed_products` against linking-map; extend `filter_urls` to accept a `processed_set` and reclassify such URLs into `needs_amazon_only` before queue creation.
+
+### 1.3 Progression Denominator Collapse
+- **Spec Requirement**: `denominator = |discovered_urls − linking_map_hits|` persisted after filtering.
+- **Evidence**: `total_products` in state collapses from 7597 → 8 during run, then jumps to 9030 after rerun, despite filter logs (e.g., `in=176` for Category 4) indicating many items.
+- **Root Cause**: Denominator saved before `system_progression.total_products_in_current_category` is populated. State writes capture zeros or manifest-length values, not the filtered queue size.
+- **Suggested Fix**: Recompute denominator immediately after filtering and persist via `update_progression_unified`.
+
+### 1.4 Category Isolation & Accumulator Leakage
+- **Evidence**: `categories_completed` increases while `system_progression.total_categories` resets to 1; manifests and queues persist across categories, causing spillover.
+- **Root Cause**: Per-category accumulators are not cleared after completion or on resume. Two tracking structures fall out of sync.
+- **Suggested Fix**: Provide `reset_category_accumulators(category_index)` and call on entry/exit. Consolidate progression tracking.
+
+## 2. Secondary Issues
+
+### 2.1 Breadcrumb Logging with Unknown Totals
+- **Observation**: Breadcrumbs emit with `prod_idx=1/pending` because denominators unset when logging occurs.
+- **Fix**: Delay `log_breadcrumb_guarded()` until `total_products_in_current_category` and `total_categories` have valid values.
+
+### 2.2 Missing Linking-Map Entries After Cache Hits
+- **Observation**: "CACHE FOUND" lines do not guarantee linking-map entries; subsequent runs misclassify these URLs, leading to Pattern Combination #2.
+- **Fix**: Startup reconciliation must ensure every cached product has a corresponding linking-map entry or is queued for Amazon analysis.
+
+## 3. Mapping to Specification Steps
+
+| Spec Step | Implementation (file:function) | Divergence |
+|-----------|--------------------------------|------------|
+| Load & validate state | `utils/fixed_enhanced_state_manager.py: load_state` (~54-98) | No regression guard for `system_progression` |
+| URL filtering (LM→cache→extract) | `utils/url_filter.py: filter_urls` (1-38) | Does not handle `processed_products` |
+| Progress update & save | `utils/fixed_enhanced_state_manager.py: save_state` (~576-593) | Called before `system_progression` populated |
+| Category processing loop | `tools/passive_extraction_workflow_latest.py` (4424-4468) | Doesn't reset per-category accumulators |
+
+## 4. Proposed Minimal Code Changes
+
+1. **utils/url_filter.py**
+   - Add `processed_set` parameter.
+   - Move processed-but-unlinked URLs from `needs_full_extraction` to `needs_amazon_only`.
+   - Return `denominator` and `linking_map_hits`.
+
+2. **utils/fixed_enhanced_state_manager.py**
+   - `update_progression_unified` to populate `system_progression` before calling `save_state`.
+   - `load_state` to assert non-regressing `resumption_index` and `current_category_index`.
+   - `reset_category_accumulators` invoked on category entry/exit.
+
+3. **tools/passive_extraction_workflow_latest.py**
+   - After filtering, compute denominator and persist via state manager.
+   - On "Product already processed", ensure linking-map entry exists (hydrate or schedule Amazon extraction).
+   - Call `reset_category_accumulators` after each category completes.
+
+## 5. Verification Plan
+
+1. **Test Scenario**: Two categories:
+   - Cat A: 3 URLs (1 in linking-map, 1 in supplier cache only, 1 new).
+   - Cat B: same pattern; interrupt after supplier phase.
+2. **Expected Counters**:
+   - Filter A: `in=3 skip=1 needs_amz=1 needs_full=1`; denominator=2.
+   - Resume after interruption: starts at Cat B with preserved `current_product_index`.
+3. **Golden Log Snippets**:
+   - `FILTER[C1]: in=3 skip=1 needs_amz=1 needs_full=1`
+   - `RESUME PTR: phase=supplier cat_idx=2/2 ... prod_idx=1/40`
+   - After restart: identical breadcrumb line.
+4. **Tests**:
+   - Unit tests for `filter_urls` invariant and reconciliation paths.
+   - Integration test for interrupt → resume with cache/linking-map mismatches.
+
+## 6. Risks & Rollback
+- Startup reconciliation may extend boot time; guard via `STATE_STRICT_MODE` env flag.
+- Denominator recalculation may alter progress dashboards; provide `LEGACY_DENOMINATOR=1` fallback.
+- Resume regression assertion could block recovery; enable `ALLOW_STATE_REGRESSION` override.
+
