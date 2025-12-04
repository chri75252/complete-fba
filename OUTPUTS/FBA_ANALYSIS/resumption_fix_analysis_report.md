# Analysis of Resumption Logic Fix Plan

## 1. Executive Summary
The proposed plan to introduce "File-Based Authority" for resumption is **sound, necessary, and surgical**. It directly addresses the user's requirement to prevent index discrepancies after interruptions by verifying the *actual* state of the work queue (via manifest, linking map, and cache) rather than relying solely on the potentially stale `system_progression.json`.

## 2. Triangular Verification (Protocol Check)

### A. The Symptom (Why this is needed)
*   **Logs:** Previous logs showed instances where the system resumed in `amazon_analysis` phase but had "skipped" products that were never actually processed, or where the `supplier_products_completed` count was inconsistent with the actual work done.
*   **Code:** The current `run()` method relies purely on `sp.get("current_phase")` (Line 2016). If the system crashes *after* switching phase but *before* saving the full state (or if the state save is partial), the system might skip the remaining supplier work.
*   **Data:** The `linking_map.json` and `manifests/*.json` are the ground truth. If the manifest has 194 items, and the linking map has 75, and we are in `amazon_analysis`, we *must* ensure the remaining 119 items are accounted for.

### B. The Fix Logic (How it works)
*   **Helper `_compute_resume_evidence_for_category`:** This encapsulates the "Filter Invariant" logic. By moving it to a helper, we can run it *before* committing to a phase in `run()`.
*   **Helper `_re_evaluate_resume_phase_from_files`:** This implements the "File-Based Authority". It explicitly checks: "Do I have supplier work left?" (`full_count > 0`). If yes, it forces the phase back to `supplier`, overriding the stale config.
*   **Integration:** Wiring this into `run()` ensures every resumption is validated against the files.

## 3. Implementation Details & Refinements

I have analyzed the code structure and identified specific implementation details required for the helpers to work correctly in the `run()` context (where the full loop state is not yet initialized).

### Critical Refinements for `_compute_resume_evidence_for_category`:
1.  **Manifest Loading:** The helper must explicitly load the manifest file from disk using `category_url`, as `urls_for_manifest` is not available in `run()`.
    *   *Logic:* Use `path_manager.get_output_path` with the derived filename.
2.  **Lazy Loading:** The helper must check if `self.linking_map` and `self.product_cache` are loaded. In `run()`, this call happens *before* the standard initialization of these maps (Line 2136).
    *   *Fix:* Add `if not hasattr(self, 'linking_map'): self.linking_map = self._load_linking_map(...)` inside the helper.

## 4. Approved Plan with Exact Diffs

I approve the plan. Below are the exact diffs I will apply, including the filled-in logic for the helper.

### Diff 1: Add Helpers (tools/passive_extraction_workflow_latest.py)

```python
    def _compute_resume_evidence_for_category(
        self,
        category_url: str,
        sp: Dict[str, Any],
    ) -> Tuple[int, int, int, int, List[str], List[str]]:
        """
        Compute in/skip/cached/full counts and per-phase worklists for a single category.
        Loads manifest from disk if needed to ensure file-based authority.
        """
        # 1. Ensure dependencies are loaded (Lazy Load for run() context)
        if not hasattr(self, "linking_map") or self.linking_map is None:
            self.linking_map = self._load_linking_map(self.supplier_name)
            
        if not hasattr(self, "product_cache_ean_index"):
            self._ensure_product_cache_indexes(self.supplier_name)

        # 2. Load Manifest (Source of Truth for 'in_count')
        # Replicate manifest path logic from loop
        from urllib.parse import urlparse
        from utils.path_manager import path_manager
        
        category_slug = urlparse(category_url).path.strip('/').replace('/', '_') or 'root'
        manifest_filename = f"{self.supplier_name}_{category_slug}_manifest.json"
        manifest_path = path_manager.get_output_path("manifests", self.supplier_name, manifest_filename)
        
        urls_for_manifest = []
        if manifest_path.exists():
            try:
                import json
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    urls_for_manifest = data.get("product_urls", [])
            except Exception as e:
                self.log.warning(f"Failed to load manifest for evidence calculation: {e}")
        
        # 3. Perform Filtering Logic (Copied & Adapted from Loop)
        # ... (Implementation of the unified filter logic from lines 5441-5536) ...
        # [I will insert the full filtering code here]
        
        return (
            in_count,
            skip_count,
            cached_count,
            full_count,
            needs_amazon_only_urls,
            needs_full_extraction_urls,
        )

    async def _re_evaluate_resume_phase_from_files(
        self,
        start_category_index: int,
        initial_phase: str,
    ) -> str:
        # ... (Implementation as provided in your plan) ...
```

### Diff 2: Wire into `run()` (tools/passive_extraction_workflow_latest.py)

```python
        self._resume_phase = resume_phase
        self.log.info(
            f" RESUMPTION POINT CONFIRMED: Starting from category index {start_category_index} "
            f"at product {product_resume_index} in phase '{resume_phase}'."
        )

        # NEW: File-grounded phase re-evaluation for the resume category.
        resume_phase = await self._re_evaluate_resume_phase_from_files(
            start_category_index=start_category_index,
            initial_phase=resume_phase,
        )
        self._resume_phase = resume_phase

        # Enhanced phase-aware gating logic
        if resume_phase == "amazon_analysis":
```

### Diff 3: Update Loop to Use Helper (tools/passive_extraction_workflow_latest.py)

I will replace the inline calculation block (approx lines 5531-5536) with the call to `self._compute_resume_evidence_for_category`.

```python
                # Calculate counts from filter outputs (already computed above)
                # REPLACED WITH HELPER CALL
                (
                    in_count,
                    skip_count,
                    cached_count,
                    full_count,
                    needs_amazon_only_urls,
                    needs_full_extraction_urls,
                ) = self._compute_resume_evidence_for_category(category_url, sp)
```

## 5. Conclusion
The plan is approved. I am ready to apply these edits upon your confirmation.
