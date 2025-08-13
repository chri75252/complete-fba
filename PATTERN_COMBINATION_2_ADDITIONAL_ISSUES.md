diff --git a//dev/null b/PATTERN_COMBINATION_2_ADDITIONAL_ISSUES.md
index 0000000000000000000000000000000000000000..3597f19c708149f5937d60b42bb08b78a1938fa6 100644
--- a//dev/null
+++ b/PATTERN_COMBINATION_2_ADDITIONAL_ISSUES.md
@@ -0,0 +1,63 @@
+# Pattern Combination #2 and Related Anomalies
+
+## Overview
+Pattern Combination #2 describes products flagged for full extraction (`needs_full`)
+but discovered in the supplier cache during processing, resulting in immediate
+"Product already processed" skips and inconsistent linking-map updates.
+This report catalogues additional instances and related anomalies from
+`run_custom_poundwholesale_20250812_140455.log`.
+
+## Logged Instances
+
+| Category | Filter Summary | Runtime Behavior | Linking Map Effect |
+|----------|----------------|------------------|--------------------|
+| C4: Dekton Black Duct Tape | `in=176 skip=175 needs_full=1` | `Product already processed... Skipping.` | `_save_linking_map` with `8074` entries (unchanged) |
+| C17: Marksman Hooks / Prima Tape | `in=137 skip=134 needs_amz=2 needs_full=1` | Two products, both `Product already processed` | `_save_linking_map` with `8074` entries (unchanged) |
+| C23: Toys Wholesale Acti | `in=34 skip=33 needs_full=1` | `Amazon skipped: nothing to analyze` → category completes with **0** processed items | Linking map count remains `8076` |
+| C25: DIY Wholesale Seala | `in=110 skip=105 needs_amz=3 needs_full=2` | Four products logged, each `Product already processed` | Linking map increments from `8074` → `8076` (only 2 new entries) |
+| C33: Wholesale Cleaning | `in=14 skip=1 needs_amz=12 needs_full=1` | 13 products, all `Product already processed` | Linking map rises to `8114` (not equal to 13) |
+
+## Analysis
+- **Expectation:** `needs_full` items should trigger supplier extraction and subsequent
+  Amazon analysis or, at minimum, hydrate a linking-map entry.
+- **Observed:** Products were bypassed due to supplier cache hits, yet linking-map
+  increments are zero or lower than the number of skipped items.
+- **Implications:**
+  - Filter classification ignores `processed_products` state.
+  - Queue construction may discard items between filtering and processing.
+  - Linking-map updates are inconsistent—some skipped products never receive
+    entries, risking future misclassification.
+
+## Root Causes & Fixes
+1. **Missing Processed-State Reconciliation**
+   - *Cause:* `filter_urls` lacks awareness of `processed_products`.
+   - *Fix:* Pass `processed_set` to `filter_urls` and move processed-but-unlinked
+     URLs into `needs_amazon_only`.
+2. **Linking-Map Hydration Omitted**
+   - *Cause:* Startup lacks reconciliation between cache and linking map.
+   - *Fix:* Implement pre-filter reconciliation to hydrate missing entries or
+     enqueue for Amazon analysis.
+3. **Queue Count Mismatch**
+   - *Cause:* Filter result not validated against constructed queues; categories
+     like C23 show `needs_full=1` yet zero products processed.
+   - *Fix:* Validate `skip + needs_amz + needs_full == total_input` and assert
+     queue lengths match expected counts.
+4. **Partial Linking-Map Updates**
+   - *Cause:* `_save_linking_map` called even when all products skipped; linking-map
+     may not include skipped URLs.
+   - *Fix:* On "Product already processed", ensure linking-map entry exists or
+     hydrate from cache before skipping.
+
+## Amazon Cache Consideration
+In all instances above, logs show no Amazon detail extraction or matching with an
+existing Amazon cache file after the skip. The absence of `HASH LOOKUP` or Amazon
+processing logs indicates that Amazon data was neither fetched nor reconciled.
+If Amazon cache existed previously, the linking-map entry should already be present;
+its absence suggests a prior crash or failed persistence.
+
+## Verification Checklist
+- Re-run affected categories after implementing fixes.
+- Confirm filter invariant passes and queue counts match.
+- Verify linking-map increments equal number of processed-or-hydrated products.
+- Ensure restart after interruption does not re-trigger "Product already processed"
+  for these URLs.
