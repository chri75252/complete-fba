diff --git a//dev/null b/MASTER_PLAN_COMPARISON_UPDATED.md
index 0000000000000000000000000000000000000000..89d3266d4e5f8fc9cf0cb39963b70a414b369f86 100644
--- a//dev/null
+++ b/MASTER_PLAN_COMPARISON_UPDATED.md
@@ -0,0 +1,73 @@
+### Points Agreed
+- **Single-writer enforcement and phase tracking**: keeping `system_progression` as sole mutable state prevents drift between `supplier_extraction_progress` and resume indices. The shim in `utils/fixed_enhanced_state_manager.py` mirrors updates without breaking legacy callers.
+- **Frozen denominators sourced from config**: using a dedicated `_authoritative_total_categories()` helper ensures `total_categories` never falls back to per-batch counts, avoiding the `1` vs `231` drift seen in `poundwholesale_co_uk_processing_state.json`.
+- **Resume indices read from `system_progression`**: `decide_resume_index()` now looks at `current_product_index`, enabling deterministic restarts.
+- **Deduplication gating and serialization hygiene**: skipping heavy re-scans when no new products exist and filtering `__*` keys before cache writes keep logs concise and caches clean.
+
+### Points Missed
+- **State validation on resume**  
+  *Root cause*: corrupted or out-of-range indices in `system_progression` can restart processing in undefined regions.  
+  *Fix*: validate counts before resuming.
+  ```python
+  # utils/fixed_enhanced_state_manager.py
+  def validate_loaded_state(self):
+      sp = self.state_data.get("system_progression", {})
+      cat_idx = int(sp.get("current_category_index", 0))
+      total = int(sp.get("total_categories", 0))
+      if cat_idx > total:
+          self.log.warning("state drift: category %s > %s", cat_idx, total)
+          sp["current_category_index"] = total
+  ```
+  *Impact*: prevents runaway loops when `total_categories` shrinks after a crash.
+- **Atomic save verification**  
+  *Root cause*: direct `json.dump` calls can leave partial files if interrupted.  
+  *Fix*: use the existing Windows Save Guardian helper.
+  ```python
+  # utils/fixed_enhanced_state_manager.py
+  from utils.windows_save_guardian import WindowsSaveGuardian
+  def save_state(self):
+      path = self._get_state_file_path()
+      WindowsSaveGuardian.save_json_atomic(path, self.state_data)
+  ```
+  *Impact*: avoids state corruption on sudden termination.
+- **Unified progress write inside product callback**  
+  *Root cause*: `_create_product_progress_callback` still back-writes to legacy supplier fields, reintroducing dual writers.  
+  *Fix*: write unified progression directly and drop legacy update.
+  ```python
+  # tools/passive_extraction_workflow_latest.py
+  def _create_product_progress_callback(...):
+      def _cb(...):
+          self.state_manager.update_progression_unified(
+              current_product_index=i,
+              current_phase="supplier",
+          )
+          ...
+  ```
+  *Impact*: guarantees every product-level step honors the single-writer model.
+- **Resume index bounds check**  
+  *Root cause*: `get_resumption_index()` may return an index greater than available products.  
+  *Fix*: cap resume index before slicing.
+  ```python
+  resume = self.state_manager.get_resumption_index()
+  resume = min(resume, len(price_filtered_products))
+  ```
+  *Impact*: prevents index errors when cache shrinks between runs.
+- **Progress callback visibility**  
+  *Root cause*: callback exceptions logged at DEBUG are easy to miss.  
+  *Fix*: raise level to WARNING.
+  ```python
+  except Exception as cb_err:
+      log.warning("progress callback failed: %s", cb_err)
+  ```
+  *Impact*: operational alerts surface in standard log streams.
+
+### Points Disagreed
+- **Immediate removal of the shim**  
+  Report 2 suggests replacing all `update_supplier_extraction_progress` calls with `update_progression_unified`. While desirable long-term, the shim isolates change scope and allows staged deprecation. In a real run where third-party scripts still invoke the legacy API, wholesale removal would break progress tracking; the shim keeps those scripts functional while enforcing single-writer semantics internally.
+- **Mandatory manifest generation before filtering**  
+  For denominator accuracy the plan freezes category totals from configuration. Requiring manifest generation would block quick resumes when the manifest is unavailable (e.g., network outage) without improving denominator stability.
+- **Caching the authoritative category count is risky**  
+  Report 2 warns against caching `self._frozen_total_categories`. In practice, caching is necessary so mid-run category deletions do not shift denominators; a live catalog change in the middle of a 6‑hour scrape would otherwise shrink totals and mis-report progress.
+
+### Summary
+The updated comparison consolidates consensus on single-writer state management, denominator freeze, deterministic resumes, and log hygiene. New recommendations address validation, atomic persistence, and callback robustness, while maintaining a cautious stance on shim removal and mandatory manifest generation.
