# Master Plan Analysis and Peer Review Synthesis

## Objective
Produce an evidence‑based analysis of the hybrid workflow (default branch), propose surgical fixes for state/filter/resume issues, and compare against the provided Master Plan plus two peer reviews. Highlight agreements, refinements, disagreements, and any items previously missed.

## Methodology
- Searched and inspected key modules and logs in‑repo only (no external sources).
- Anchored findings with file paths and approximate line spans.
- Preferred minimal, reversible changes; preserved interfaces.
- Cross‑checked with peer reports; reconciled where they differ.

## Repository Inventory (relevant)
- Orchestrator: `tools/passive_extraction_workflow_latest.py` (hybrid engine)
- Supplier scraper: `tools/configurable_supplier_scraper.py`
- State manager: `utils/fixed_enhanced_state_manager.py`
- Utilities: `utils/windows_save_guardian.py`, `utils/url_cache_filter.py`, `utils/path_manager.py`
- Local logs: `fba_extraction_*.log` (root)

## Independent Findings (by workstream)
- A. Prefiltered save callback: Present and active.
  - Evidence: `tools/configurable_supplier_scraper.py:983–1041` includes `progress_callback(...)` in prefiltered path; URL path also has callback at `657–906`.
  - Note: When `product_accumulator` is None, code logs a warning—ensure orchestrator passes it to enable periodic saves.
- B. Single writer + phase tracking: Partially compliant.
  - Evidence: Supplier analysis loop writes legacy progress and mis‑tags phase.
    - `tools/passive_extraction_workflow_latest.py:1696–1707`: `extraction_phase="amazon_analysis"` during supplier loop; also calls `update_supplier_extraction_progress(...)`.
  - Unified API exists: `utils/fixed_enhanced_state_manager.py:636–700` (`update_progression_unified`).
  - Recommendation: Correct phase tag to "supplier" and write phase via `update_progression_unified`; keep a temporary mirror to legacy for compatibility (phased removal).
- C. Denominator freeze: Currently correct in main callsites.
  - Evidence: `total_categories=len(category_urls)` at `tools/passive_extraction_workflow_latest.py:1698, 3975–3979`.
  - Helpers log authoritative counts at `1348–1387`. Freeze once at run start and reuse.
- D. Resume fidelity: Uses file‑grounded `resumption_index` (safer).
  - Evidence: `tools/passive_extraction_workflow_latest.py:1438` reads `self.state_manager.get_resumption_index()`.
  - State manager startup policy: `utils/fixed_enhanced_state_manager.py:200–360, 290–333` implements reverse‑gap and resume decisions with reasons.
  - Recommendation: Keep file‑grounded resume; add bounds validation + resume banner; optionally read phase‑specific indices (`supplier_resumption_index`, `amazon_resumption_index`) when resuming mid‑category.
- E. Late de‑dupe gating: Hygiene improvement (not critical) — implement short‑circuit when no new items to reduce log spam.
- F. Serialization hygiene: Strip `__*` keys before persisting products wherever cache writes occur.
- G. Phase write‑through: Ensure all transitions call `update_progression_unified(current_phase=...)` instead of mutating raw state or only legacy structures.

## Concrete Patches (tight diffs)
- B1. Supplier loop phase tag
  - File: `tools/passive_extraction_workflow_latest.py`
  - Around: 1696–1707
  ```diff
  @@
 -                                extraction_phase="amazon_analysis"
 +                                extraction_phase="supplier"
  ```
- B2. Phase write‑through at transitions
  - File: `tools/passive_extraction_workflow_latest.py`
  - Replace raw/legacy phase writes
  ```diff
  - self.state_manager.state_data.setdefault("runtime_settings", {})["current_phase"] = "amazon_analysis"
  + self.state_manager.update_progression_unified(current_phase="amazon_analysis")
  ```
- B3. Legacy→unified mirror (temporary, non‑breaking)
  - File: `utils/fixed_enhanced_state_manager.py`
  - In `update_supplier_extraction_progress(...)`
  ```diff
  @@ def update_supplier_extraction_progress(...):
 -        progress = self.state_data.get("supplier_extraction_progress", {})
 +        progress = self.state_data.get("supplier_extraction_progress", {})
 +        # Mirror critical fields into system_progression (temporary bridge)
 +        sp = self.state_data.setdefault("system_progression", {})
 +        if category_index is not None:
 +            sp["current_category_index"] = int(category_index)
 +        if total_categories is not None:
 +            sp["total_categories"] = int(total_categories)
 +        if extraction_phase is not None:
 +            phase_map = {"fresh_categories": "supplier", "amazon_analysis": "amazon_analysis", "completed": "completed"}
 +            sp["current_phase"] = phase_map.get(str(extraction_phase), str(extraction_phase))
  ```
- E. De‑dupe gating (when no new products)
  - File: `tools/passive_extraction_workflow_latest.py`
  - In `_save_products_to_cache(...)` equivalent path: short‑circuit when `new_products_added == 0` to avoid heavy re‑scan/log spam.
- F. `__*` key stripping on persist
  - Wherever appending to cache: `sanitized = {k: v for k,v in product.items() if not str(k).startswith("__")}` before save.

## Validation Matrix (signals to check)
- Filter invariant per category: LM skip → cache split → extraction needed; sums match (already logged in this branch).
- Resume banner prints phase and category X/Y; indices continue from `resumption_index` with bounds.
- Periodic saves on prefiltered path show “(≥1 new)” once accumulator + callback are active.
- Single‑writer migration: only `system_progression` mutates for core indices/phase; legacy remains stable view until removed.
- No de‑dupe spam when batch adds zero new items.

## Peer Reports — What I Missed or Refine
- Resume index: Use `get_resumption_index()` and validate bounds (I already favored file‑grounded resume; adding explicit bounds + banner is a good refinement).
- Shim phase mapping: Map supplier‑specific `extraction_phase` to unified workflow phases to avoid semantic drift (added phase_map above).
- Atomic saves: Explicitly verify all critical saves use `WindowsSaveGuardian.save_json_atomic`; ensure `save_state()` funnels through atomic path.
- State validation guards on resume: Add a `validate_loaded_state()` pass to cap indices and detect drift to linking map counts; log warnings.
- Callback exception visibility: Elevate progress_callback exceptions to WARNING (from DEBUG) for diagnosability.
- Boundary tests: Add off‑by‑one resume boundary tests for slice safety.

## Peer Reports — Where I Disagree (and why)
- Replace all legacy calls immediately (remove shim): Disagree for immediate rollout. True single‑writer is the goal, but a phased migration avoids breaking any legacy consumers. Plan: Stage 1 mirror (above) + deprecation warnings; Stage 2 remove legacy writes after validation.
- Resume from `system_progression` instead of file‑grounded index: Disagree. Current design intentionally uses file‑grounded `resumption_index` for safety and determinism (ties to persisted artifacts). `system_progression` remains great for telemetry/UX, but should not be the resume authority unless proved equivalent.
- Denominator bug assumed present: In this branch, `total_categories` is already sourced from `len(category_urls)` with authoritative getters; implement a “freeze once” at run start for consistency, but no evidence of active denominator drift here.
- Mandatory manifest generation: Not required to fix denominators in this branch; acceptable as a later enhancement if filters consume an on‑disk manifest.

## Additional Recommendations
- Freeze `total_categories` once at init and store in `runtime_settings.total_categories`; reference the frozen value via a getter for all writes/logs.
- Phase‑specific resume: When resuming mid‑category, prefer `supplier_resumption_index` vs `amazon_resumption_index` based on `current_phase`.
- Memory management: Keep existing sliding‑window/monitor hooks untouched; out of scope for these fixes.

## Test Plan (concise)
- Unit
  - Phase tag write: supplier loop writes `supplier`; unified updater called on transitions.
  - Denominator getter returns the frozen init value.
  - Serialization hygiene drops `__*` keys.
- Integration
  - Prefiltered path with `update_frequency_products=1`: first product triggers a save with “≥1 new”.
  - Resume mid‑category: banner shows phase and category X/Y; indices continue from `resumption_index` within bounds.
  - De‑dupe gating produces a single summary when 0 new.
- E2E
  - 2–3 categories mixed cached/new: verify invariant logs, frozen denominators, unified phase logs, no legacy drift.

## Minimal Changelog
- fix(workflow): correct supplier loop phase tag; write phase via unified updater.
- feat(state): temporary mirror legacy progress into `system_progression` with mapped phases; plan staged removal.
- chore(hygiene): strip `__*` keys before persisting; gate dedupe logs when 0 new.
- test: add resume boundary and callback failure visibility tests.

---

Notes
- Evidence anchors (file/line spans) drawn from current files in this branch:
  - `tools/passive_extraction_workflow_latest.py:1348–1387, 1438, 1670–1707, 3966–3983`
  - `tools/configurable_supplier_scraper.py:657–906, 983–1041`
  - `utils/fixed_enhanced_state_manager.py:200–360, 636–700, 1084–1212`
- If you want immediate single‑writer enforcement without a shim, replace all workflow callsites to `update_supplier_extraction_progress` with `update_progression_unified` and delete the legacy method; plan a short hardening run to verify dashboards/consumers.

## Consolidated Misses & Gaps (from peer reports)

The following items were suggested by 2 peer reports (CODX, QWEN). Where both recommended the same fix for the same reason, it is listed once. Where reasons differ, they are captured together.

1) State contradiction detection (missed) — 1 report (CODX)
- Reason: Earlier audits mentioned a "state contradiction" guard; ensure it remains active with new changes.
- Action: Add/keep a validation hook that detects impossible combos (e.g., fresh start flags with non‑zero progress) and logs a clear warning.

2) Resume boundary tests (missed) — 1 report (CODX)
- Reason: Catch off‑by‑one errors at indices 0, 1, n‑1, n, n+1.
- Action: Add explicit unit tests to the test plan and run them in CI.

3) Authoritative total categories lookup precedence (enhancement) — 1 report (CODX)
- Reason: On resume, honor already‑frozen totals in `runtime_settings` or `system_progression` before recomputing from config.
- Action: Update `_authoritative_total_categories()` to check runtime/system values first.

4) Integrity validation on load (missed patch) — 1 report (CODX)
- Reason: Plan mentions capping indices; include a concrete method stub for immediate adoption.
- Action: Add `validate_loaded_state()` with caps and drift warnings.

5) Shim robustness and validation (enhancement) — 1 report (QWEN)
- Reason: Normalizing shim should clamp values, use a robust frozen‑total fallback chain, and avoid negative/zero totals.
- Action: Expand shim parameter validation and fallback chain.

6) Resume index bounds and cross‑validation (enhancement) — 1 report (QWEN)
- Reason: Ensure resume index is within [0, max-1] and optionally validate against linking map count.
- Action: Enhance bounds logic and add optional cross‑checks.

7) Deterministic phase transitions (explicit validation) — 1 report (QWEN)
- Reason: Make allowed transitions explicit; log on invalid hops.
- Action: Add `validate_phase_transition(current_phase, next_phase)` helper.

8) Manifest generation clarification (non‑blocking) — 1 report (QWEN)
- Reason: Manifest useful for audit but should not block the hot path.
- Action: Add optional background manifest writer controlled by config.

9) Backward compatibility validation (enhancement) — 1 report (QWEN)
- Reason: During migration, warn when legacy vs modern indices diverge materially.
- Action: Add `_validate_backward_compatibility()` log‑only checker.

10) Error recovery from state corruption (enhancement) — 1 report (QWEN)
- Reason: Provide a recovery path from a backup file when state load fails.
- Action: Add `recover_from_state_corruption()` routine.

## Points Contradicting the Plan (with counts and reasons)

1) Single‑writer migration approach — 2 reports, differing recommendations
- Count/Reasons:
  - Report favors immediate direct unified writes (remove shim) to avoid dual‑update complexity (1 report).
  - Report supports shim but requests stronger normalization/validation inside shim (1 report).
- Consolidation: Adopt a phased approach. Land a normalizing shim now (with strong validation) and migrate hot callsites to direct `update_progression_unified(...)`. Remove legacy calls after canary validation.

2) Resume source — 2 reports align against naive `system_progression` read
- Count/Reasons:
  - CODX: Use `get_resumption_index()`; it encapsulates policy and fallbacks.
  - QWEN: Add stronger bounds and optional linking‑map cross‑validation.
- Consolidation: Keep file‑grounded `get_resumption_index()` as authoritative, with enhanced bounds + banner; do not switch to raw `system_progression` fields.

3) Manifest generation — mixed views
- Count/Reasons:
  - Some prior reports wanted manifest‑first to freeze denominators; QWEN suggests optional background generation; CODX did not require it.
- Consolidation: Maintain frozen runtime/config denominator as the primary source; provide optional background manifest generation for audit.

## Ready‑to‑Adopt Snippets (augmentations)

1) Robust normalizing shim (system_progression only)
```python
def update_supplier_extraction_progress(self, **kwargs):
    sys = self.state_data.setdefault("system_progression", {})

    # Category index (clamped >= 0)
    if kwargs.get("category_index") is not None:
        try:
            sys["current_category_index"] = max(0, int(kwargs["category_index"]))
        except Exception:
            sys["current_category_index"] = sys.get("current_category_index", 0)

    # Frozen total: runtime_settings → sys → incoming → authoritative fallback
    frozen_total = (
        self.state_data.get("runtime_settings", {}).get("total_categories")
        or sys.get("total_categories")
        or kwargs.get("total_categories")
    )
    if frozen_total is None:
        try:
            frozen_total = self._authoritative_total_categories()  # or inject via orchestrator
        except Exception:
            frozen_total = 1
    try:
        sys["total_categories"] = max(1, int(frozen_total))
    except Exception:
        sys["total_categories"] = max(1, int(sys.get("total_categories", 1)))

    # Phase normalization: never let supplier path tag as amazon_analysis by mistake
    phase = kwargs.get("extraction_phase")
    if phase is not None:
        phase_map = {"fresh_categories": "supplier", "amazon_analysis": "amazon_analysis", "completed": "completed"}
        sys["current_phase"] = phase_map.get(str(phase), str(phase))

    # URL passthrough (optional normalization)
    if kwargs.get("category_url"):
        try:
            from utils.normalization import normalize_url
            sys["current_category_url"] = normalize_url(kwargs["category_url"])
            sys["original_category_url"] = kwargs["category_url"]
        except Exception:
            sys["current_category_url"] = kwargs["category_url"]

    self.save_state()
```

2) Authoritative totals with precedence (runtime → sys → config)
```python
def _authoritative_total_categories(self) -> int:
    if hasattr(self, "_frozen_total_categories"):
        return int(self._frozen_total_categories)

    rs = self.state_manager.state_data.get("runtime_settings", {})
    sp = self.state_manager.state_data.get("system_progression", {})
    frozen = rs.get("total_categories") or sp.get("total_categories")
    if frozen:
        self._frozen_total_categories = int(frozen)
        return self._frozen_total_categories

    # Fallback to configured categories
    try:
        categories = self._get_predefined_categories(self.supplier_name) or []
        self._frozen_total_categories = len(categories)
    except Exception:
        self._frozen_total_categories = 1

    # Persist for visibility
    rs["total_categories"] = self._frozen_total_categories
    self.state_manager.save_state()
    return int(self._frozen_total_categories)
```

3) Integrity validation on load (caps + drift warnings)
```python
def validate_loaded_state(self):
    sp = self.state_manager.state_data.get("system_progression", {})
    total_cats = sp.get("total_categories") or self._authoritative_total_categories()
    if total_cats is None:
        total_cats = 1

    # Cap category index
    cat_idx = int(sp.get("current_category_index", 0))
    if cat_idx > total_cats:
        self.log.warning(f"⚠️ State validation: current_category_index {cat_idx} > total_categories {total_cats}; capping")
        sp["current_category_index"] = total_cats

    # Optional: cross-check product indices (if available)
    prod_total = int(sp.get("total_products_in_current_category", 0))
    prod_idx = int(sp.get("current_product_index_in_category", 0))
    if prod_total > 0 and prod_idx > prod_total:
        self.log.warning(f"⚠️ State validation: product_index {prod_idx} > total_products {prod_total}; capping")
        sp["current_product_index_in_category"] = prod_total
```

4) Resume bounds and banner (with optional linking‑map check)
```python
resume_idx = getattr(self.state_manager, "get_resumption_index", lambda: 0)()
# Bound to [0, max(0, n-1)]
n = len(price_filtered_products)
upper = max(0, n - 1)
resume_idx = max(0, min(int(resume_idx), upper))

# Optional cross-check with linking-map count if available
try:
    lm_count = self._file_grounded_linking_map_count()
    if lm_count is not None and abs(lm_count - resume_idx) > 100:
        self.log.warning(f"⚠️ Linking map drift: {lm_count} entries vs resume {resume_idx}")
except Exception:
    pass

sp = self.state_manager.state_data.get("system_progression", {})
total_cats = sp.get("total_categories") or self._authoritative_total_categories()
self.log.info(f"▶ RESUME {sp.get('current_phase','supplier')}: category {sp.get('current_category_index',0)+1}/{total_cats} (system_progression)")
```

5) Deterministic phase transition validation
```python
def validate_phase_transition(self, current_phase: str, next_phase: str) -> bool:
    valid_transitions = {
        "supplier": ["amazon_analysis", "completed"],
        "amazon_analysis": ["supplier", "completed"],
        "completed": ["supplier"],  # next run
    }
    ok = next_phase in valid_transitions.get(current_phase, [])
    if not ok:
        self.log.warning(f"⚠️ Invalid phase transition: {current_phase} → {next_phase}")
    return ok
```

6) Optional background manifest generation (non‑blocking)
```python
def _generate_category_manifest(self, category_url: str, product_urls: list):
    if not self.system_config.get("audit", {}).get("generate_manifests", False):
        return
    import threading
    threading.Thread(target=self._save_manifest_async, args=(category_url, product_urls), daemon=True).start()
```

7) Backward compatibility validation
```python
def _validate_backward_compatibility(self):
    legacy = self.state_manager.state_data.get("supplier_extraction_progress", {})
    modern = self.state_manager.state_data.get("system_progression", {})
    if legacy.get("current_category_index", 0) != modern.get("current_category_index", 0):
        self.log.warning("Legacy/Modern category index mismatch detected")
```

8) Error recovery from state corruption
```python
def recover_from_state_corruption(self):
    try:
        backup_path = str(self.state_manager.state_file_path) + ".backup"
        import os, shutil
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, self.state_manager.state_file_path)
            self.state_manager.load_state()
            self.log.info("Recovered state from backup")
    except Exception as e:
        self.log.error(f"Failed to recover state: {e}")
        # Fallback policy could reset to a safe fresh state here
```

9) Callback exception visibility (WARN)
```python
try:
    self.progress_callback("supplier_extraction", i + 1, len(filtered_urls), product_url, product)
except Exception as cb_err:
    log.warning(f"⚠️ progress_callback failed at {i+1}: {cb_err}")
```

## Final Recommendations (merged)
- Keep file‑grounded `get_resumption_index()` as the resume authority; add bounds + optional linking‑map cross‑check and a clear resume banner.
- Land a robust normalizing shim now; migrate hot callsites to direct unified writes; remove the legacy API after canary validation.
- Freeze denominators once; read from runtime/system first on resume; fall back to config only when necessary.
- Add explicit phase transition validation and WARN when an invalid hop is attempted.
- Make manifest generation optional and asynchronous for audit; keep it off the hot path.
- Add backward compatibility and contradiction validation, plus an error recovery routine.
