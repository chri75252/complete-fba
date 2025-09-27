Alright — here’s a clean, actionable hand-off you can paste to your coding agent. I split it into (1) the **pre-run fix pack** you asked for (so the system can run correctly across categories), and (2) a **post-run follow-up template** that tells the agent exactly what to do based on what we observe in the next run.

I also include a short **comparison** so you see what my analysis agrees/disagrees with vs the two `.md` reports, and what each of us missed.

---

# Set 1 — Pre-Run Fix Pack (apply these before your next run)

**Goal:** make category runs correct and auditable across categories, stop phase-detection drift, make Amazon queue commits consistent, and harden cache selection. Everything below is surgical, low-risk, and log-proofed.

> **Files:** `tools/passive_extraction_workflow_latest.py`, `utils/fixed_enhanced_state_manager.py`
> **Logs to produce:** keep DEBUG on; we rely on the proof banners listed below.

---

## A. Category index: remove the off-by-one write

**Problem (confirmed):** supplier loop computes `category_index` correctly, then writes **`category_index-1`** into state — that’s why state snapshots keep `"current_category_index": 0` while logs print *Category 1/1*.

**Where (excerpt):**

```
tools/passive_extraction_workflow_latest.py
... "Processing category batch ..."
category_index = resume_cat_idx + (category_batch_start_idx - 1) + subcategory_index
# ❌ wrong — subtracts 1 again at write time:
self.initialize_category_processing(category_index=category_index - 1, ...)
```

**Change (minimal & safe):**

```diff
- self.initialize_category_processing(category_index=category_index - 1, ...)
+ self.initialize_category_processing(category_index=category_index, ...)
```

**Acceptance/grep gates:**

* After fix, state should persist `system_progression.current_category_index == 1` for the first category (was `0`).
* Log still reads “Category 1/…”, but **state** increments beyond zero on the **first** write.

---

## B. Phase detection: compare **file counts** (not session variables)

**Problem (confirmed in latest logs):** divergence warnings like:

```
⚠️ WARNING: supplier_cache_vs_linking_map divergence 521000.0% (session: 10422, global: 2)
🔍 PHASE DETECTION: FRESH_CATEGORIES (reverse gap - linking map: 10422 > cache: 2)
```

The “cache” side comes from a session/global variable, not the **actual cache file** being used. That misclassifies phase and confuses observers.

**Fix:**

1. In the phase-detection decision block (the one that logs `PHASE DETECTION: ...`), **compute counts from disk**:

   * `linking_map_count = len(json.load(open(linking_map_path)))`
   * `cache_path, cache_meta = _find_actual_supplier_cache_file(...)`
   * `cache_count = len(json.load(open(cache_path)))` (guard for non-array/empty)

2. Replace any uses of “session/global cache count” there with `cache_count` loaded **from the chosen file**.

**Acceptance/grep gates:**

* Banners should show: `PHASE DETECTION: ... (linking map: <N> > cache: <M from FILE>)`.
* Divergence percentage recomputes to *(N−M)/max(1,M)*×100 from **file values**.
* No references to `runtime_settings.supplier_cache_count` or other session counts in this decision.

---

## C. Cache selection: add a sanity fallback & pick the largest valid array

**Problem (new and important):** when current cache is tiny (2–3 rows) but you have a larger, valid backup (e.g., `BEFORE RNUpoundwholesale-co-uk_products_cache.json`), the loader never considers it → phase detection keeps “reverse gap”.

**Where (excerpt):**

```
tools/passive_extraction_workflow_latest.py
def _find_actual_supplier_cache_file(self, supplier_name):
    # Pattern 1: exact “poundwholesale-co-uk_products_cache.json”
    # Pattern 2: underscored variant
    # Pattern 3: sanitized variant
    # ❌ no generic scan for other valid backups; no “largest valid array” heuristic
```

**Fix (safe heuristic):**

* After the current 3 patterns, add:

  * Scan `OUTPUTS/cached_products/` for files matching `poundwholesale-co-uk_products_cache*.json` **including** `BEFORE RNUpoundwholesale-co-uk_products_cache.json`.
  * For each candidate: try `json.load`; if top-level is a list, record length.
  * If the “primary” pick has `len < 50` **and** there exists a candidate with `len >= 500` (thresholds configurable), prefer the **largest valid** one.
  * Log:

    * `"[CACHE_PICK] primary={file,len} -> fallback={file,len} reason=implausibly_small"`
* Always return *(path, {count, reason})* so phase detection can log the **file-grounded** `cache_count`.

**Acceptance/grep gates:**

* On a small/truncated current cache, expect one of:
  `"[CACHE_PICK] primary=... -> fallback=... reason=implausibly_small"`
  `"[CACHE_PICK] primary=... (kept) reason=plausible"`
* Phase detection now cites the chosen file and its count.

---

## D. Amazon progress commits: make `total_cats` consistent

**Problem (confirmed in code):** `commit_amazon_progress(...)` is invoked with mixed `total_cats` — sometimes `1`, sometimes `_authoritative_total_categories()` — which makes resume/progress math incoherent.

**Fix (simple rule):**

* **During Amazon phase**, always pass `total_cats=1`. The queue is category-scoped; the “categories” concept shouldn’t fluctuate inside the Amazon queue loop.

**Change (search & replace in `passive_extraction_workflow_latest.py`):**

```diff
- self.state_manager.commit_amazon_progress(... total_cats=self._authoritative_total_categories(), ...)
+ self.state_manager.commit_amazon_progress(... total_cats=1, ...)
```

**Acceptance/grep gates:**

* After fix, **all** `commit_amazon_progress(` call sites show `total_cats=1` inside Amazon analysis paths.

---

## E. Supplier progress display: clamp to denominator

**Problem (observed previously):** display index can exceed the frozen denominator, producing anomalies like `Index updated to 27/6`.

**Fix (display-only guard):**

* Where you log `SUPPLIER STATE UPDATE: Index updated to {display_idx}/{cat_total}`, clamp:

```python
if isinstance(cat_total, int) and display_idx > cat_total:
    self.log.warning(f"[INDEX_CLAMP] display_idx={display_idx}->{cat_total} reason=exceeds_denominator")
    display_idx = cat_total
```

**Acceptance/grep gates:**

* `"[INDEX_CLAMP]"` never appears in normal runs; if it does, you’ve prevented a bad banner.

---

## F. Keep proof banners clear and consistent (no behavior change)

* Keep `✅ RESUME HONORED` lines (they **are** present in your latest logs).
* Optional, but recommended: add `[DENOM_FROZEN] url=… total=… (LOCKED|NEW)` once per category; it helps validate “freeze-once” visually.
  (Do **not** refreeze; just log the existing frozen value with `(LOCKED)`.)

---

## G. OpenAI key check: make it non-fatal when AI is disabled

If there’s a hard exit on missing `OPENAI_API_KEY`, gate it behind your feature flag (e.g., `OPENAI_ENABLED`). This keeps non-AI runs unblocked.

---

# Set 2 — Post-Run Follow-Up Template (fill after next run)

> **You said you’ll run first, then want a second set.** Below is a ready template the agent can execute immediately after the run **based on what the logs & state show**. No guessing.

For each condition, perform the listed action.

---

## 1) Category index in state

* **If** `processing_state.system_progression.current_category_index == 0` after completing category 1:
  → Recheck Set-1 (A). If the code is correct, add an **immediate save** right after `initialize_category_processing(category_index=...)` and log the persisted value:
  `"[STATE_WRITE_PROOF] current_category_index=<val> url=<normalized_url>"`.

* **If** index increments to `1` as expected:
  → No action.

---

## 2) Phase detection banners

* **If** you still see huge divergence with a tiny cache count **and** Set-1 (C) didn’t trigger `[CACHE_PICK]`:
  → Add an **explicit file count log** right before the decision:
  `"[PHASE_COUNTS] lm_file=<path> lm_count=<N> cache_file=<path> cache_count=<M>"`.
  Then verify `_find_actual_supplier_cache_file` returns what phase detection uses.

* **If** divergence now references the selected file with plausible counts:
  → No action.

---

## 3) Amazon resume behavior

* **If** Amazon phase starts and you see **mixed** `total_cats` again in commits:
  → Re-grep for `commit_amazon_progress(` and normalize to `total_cats=1`.

* **If** pointer resumes but skips items after you manually remove a couple from the category cache:
  → Add **fingerprint + last-key remap** (my earlier proposal).
  Proof logs expected: `[RESUME_ENTER]`, `[RESUME_REMAP_CONTIG|RESET]`, `[RESUME_CLAMP]`.

---

## 4) Cache source integrity

* **If** `_find_actual_supplier_cache_file` picked the small file even though a large valid backup exists:
  → Raise fallback threshold (e.g., `small<100` & `fallback>=1000`) and re-run selection. Always log `[CACHE_PICK]`.

---

## 5) Freeze-once proof

* **If** you do not see a single `[DENOM_FROZEN] … (LOCKED)` per category on second run:
  → Add the banner (read-only); do **not** mutate the frozen value.

---

# What changed my mind (and what I still disagree with)

## Where I now **agree** (based on your latest 3 logs & state)

* **Resume proof exists.** Your logs clearly show the state manager’s resume proof lines:

  * `RESUME PTR: phase=supplier cat_idx=0/231 ...`
  * `✅ RESUME HONORED: phase=supplier cat=0/231 ...`
    That’s sufficient proof of honoring the pointer **inside** the current category. My earlier “missing proof” note was about the extra *runner* tags; it’s not a functional gap.

* **Phase detection must be file-grounded.** The divergence banners must be computed from the **actual file** counts — not session/global placeholders. The current behavior matches your concern.

## Where I still **disagree** with parts of the MD plans

* **Don’t reset `amazon_analysis_resumption_index` at category init.** The state manager already advances these pointers per commit. Resetting at init risks wiping a precise pointer if the process restarts mid-Amazon queue.

* **“Freeze once, read always” is useful.** You’re right to demand persistence; freezing is still valuable **as long as** you don’t refreeze silently. The banner is only proof; it should never change the frozen value on run-2.

## What the MD plans **miss** (and I missed initially)

* **Cache selection fallback.** Neither plan hardens `_find_actual_supplier_cache_file` to choose the **largest valid** JSON when the “current” cache is implausibly small. This is the simplest way to stop repeat reverse-gap noise.

* **Mixed `total_cats` in Amazon commits.** This is in code now and confuses progress math; both reports didn’t call it out. Unify to `total_cats=1` during Amazon analysis.

* **Duplicate/legacy fragments in `passive_extraction_workflow_latest.py`.** Keeping duplicate method bodies makes audits brittle. At minimum, normalize the hot path; if time allows, remove stale duplicates.

---

## Quick checklist the agent can copy/paste

* [ ] **A. Off-by-one**: remove `- 1` when writing `category_index` at initialize time.
* [ ] **B. Phase detection**: compute `linking_map_count` & `cache_count` by reading files actually selected for this run; stop using session/global placeholders.
* [ ] **C. Cache fallback**: in `_find_actual_supplier_cache_file`, add “largest valid array” heuristic and log `[CACHE_PICK] ... reason=implausibly_small` when switching.
* [ ] **D. Amazon commits**: replace any `total_cats=self._authoritative_total_categories()` with `total_cats=1` in Amazon loops.
* [ ] **E. Clamp display index**: add `[INDEX_CLAMP]` safeguard in supplier progress banner logic.
* [ ] **F. Proof logs**: keep `✅ RESUME HONORED`, add optional `[DENOM_FROZEN] ... (LOCKED)` read-only banner.
* [ ] **G. OpenAI key**: make missing key non-fatal when feature flag is off.

**Run expectations right after Set-1:**

* State shows `current_category_index >= 1` after first category is initialized.
* Phase detection cites cache **file** & **count** it actually used.
* No progress math contradictions in Amazon commits.
* If the current cache is tiny and a big backup exists, `[CACHE_PICK] primary->fallback` appears.

---

If you want, I can also package Set-1 as a `.md` you can drop next to the repo and send to the coding agent as the single source of truth.

Below is a **copy-pasteable prompt** you can hand to your coding agent.
It references the two MD reports and clearly marks the **extra items** I’m adding beyond those reports. It includes root causes, diffs/snippets, grep gates, and acceptance tests so integration is surgical and auditable.

---

# 🛠️ Set-1 Pre-Run Fix Pack — Phase/Counts/Indices Hardening (surgical)

**Sources to honor & cite in comments:**

* `/.serena/memories/comprehensive_legacy_processing_and_phase_detection_analysis_report.md`
* `/.serena/memories/surgical_implementation_guide_with_complete_analysis.md`

**Goal:** Make multi-category runs correct and auditable, stop phase-detection drift, unify Amazon progress math, and harden cache selection — **without** altering working resume semantics.

**Target files:**

* `tools/passive_extraction_workflow_latest.py`
* `utils/fixed_enhanced_state_manager.py` (read only unless noted)

---

## ✅ Scope & Non-Negotiables

* Implement exactly the items below.
* Add the **proof banners** so we can grep correctness in logs.
* **Do not** introduce resets for Amazon resume indices. (Rationale at the end.)

---

## 1) Category index write: remove off-by-one

**Root cause (matches MD reports):** We compute a correct 0-based absolute category index, then write `category_index - 1` into state, leaving `"current_category_index": 0` forever.

**Action:** Where we initialize a category within the supplier loop, stop subtracting 1 at write time.

**Patch (unified-diff style; anchor by `initialize_category_processing(` call):**

```diff
--- a/tools/passive_extraction_workflow_latest.py
+++ b/tools/passive_extraction_workflow_latest.py
@@
- self.initialize_category_processing(category_index=category_index - 1, category_url=normalized_category_url, ...)
+ # Per reports: store the true absolute index; no off-by-one.
+ # Ref: comprehensive_legacy_processing_and_phase_detection_analysis_report.md §Category Indexing
+ self.initialize_category_processing(category_index=category_index, category_url=normalized_category_url, ...)
```

**Grep gates (post-build):**

* `rg -n "initialize_category_processing\\(category_index=.*- 1"` → **no hits**
* `rg -n "initialize_category_processing\\(category_index=" tools/passive_extraction_workflow_latest.py` → hit shows **no subtraction**

**Acceptance log/state:**

* After first category is initialized, state shows
  `system_progression.current_category_index >= 1` (was 0).

---

## 2) Phase detection must compare **file counts** (not session placeholders)

**Problem (matches MD reports & latest logs):**
Warnings like:

```
⚠️ supplier_cache_vs_linking_map divergence 521000.0% (session: 10422, global: 2)
🔍 PHASE DETECTION: FRESH_CATEGORIES (reverse gap - linking map: 10422 > cache: 2)
```

are derived from a “session/global” cache count instead of **the actual cache file** the run is using.

**Action:** In the phase-selection snippet that emits `PHASE DETECTION: ...`, compute both counts from disk.

**Implementation notes:**

* Obtain linking map file path via the same helper the workflow uses; read and `len(...)`.
* Obtain **the cache file actually selected** by `_find_actual_supplier_cache_file()`, then `len(...)`.
* Use those two file-grounded counts to compute divergence and decide reverse-gap vs gap.

**Patch (pseudo-diff w/ anchors):**

```diff
--- a/tools/passive_extraction_workflow_latest.py
+++ b/tools/passive_extraction_workflow_latest.py
@@
- lm_count = runtime_settings.get("linking_map_count_session")  # ❌ remove
- cache_count = runtime_settings.get("supplier_cache_count_global")  # ❌ remove
+ # Read counts from actual files (per MD: compare FILE totals, not session stats)
+ lm_path = self._get_linking_map_path_for_supplier(self.supplier_name)
+ try:
+     with open(lm_path, "r", encoding="utf-8") as _f:
+         _lm = json.load(_f)
+     lm_count = len(_lm) if isinstance(_lm, list) else 0
+ except Exception:
+     lm_count = 0
+
+ cache_file, _meta = self._find_actual_supplier_cache_file(self.supplier_name)
+ try:
+     with open(cache_file, "r", encoding="utf-8") as _f:
+         _cp = json.load(_f)
+     cache_count = len(_cp) if isinstance(_cp, list) else 0
+ except Exception:
+     cache_count = 0
+
+ self.log.info(f"[PHASE_COUNTS] lm_file={lm_path} lm_count={lm_count} cache_file={cache_file} cache_count={cache_count}")
@@
- self.log.warning(f"⚠️ WARNING: supplier_cache_vs_linking_map divergence {divergence_pct}% (session: {lm_count}, global: {cache_count})")
+ self.log.warning(f"⚠️ WARNING: supplier_cache_vs_linking_map divergence {divergence_pct}% (lm_file: {lm_count}, cache_file: {cache_count})")
```

**Grep gates:**

* `rg -n "\\[PHASE_COUNTS\\]" logs/debug/*.log` → at least one line per run.
* No remaining “(session: X, global: Y)” wording.

**Acceptance:**

* `PHASE DETECTION` lines now cite **file-grounded** counts and sane percentages.

---

## 3) **NEW (extra beyond MD reports):** Cache selection fallback — pick largest valid array when “current” is implausibly small

**Why (was missing from MDs):** We’ve seen runs where the “current” cache file has 2–3 rows while a large backup exists (e.g., `BEFORE RNUpoundwholesale-co-uk_products_cache.json`). Phase detection then always screams reverse-gap.

**Action:** Extend `_find_actual_supplier_cache_file` to:

* After current patterns, **scan** `OUTPUTS/cached_products/` for `poundwholesale-co-uk_products_cache*.json` (include the “BEFORE RNU…” naming).
* JSON-load each candidate; if top-level is a list, record `len`.
* If the “primary” pick has `len < SMALL_MIN` (default 50) **and** a candidate exists with `len >= LARGE_MIN` (default 500), **prefer the largest valid**.
* Emit proof banner:
  `"[CACHE_PICK] primary={p,len} -> fallback={q,len} reason=implausibly_small"`

**Patch (illustrative block inside `_find_actual_supplier_cache_file`)**:

```diff
@@ def _find_actual_supplier_cache_file(self, supplier_name):
+ # --- Heuristic fallback: prefer largest valid array if primary is implausibly small ---
+ try:
+     SMALL_MIN = int(self.system_config.get("cache_sanity", {}).get("small_min", 50))
+     LARGE_MIN = int(self.system_config.get("cache_sanity", {}).get("large_min", 500))
+ except Exception:
+     SMALL_MIN, LARGE_MIN = 50, 500
+
+ try:
+     primary_len = 0
+     with open(primary_path, "r", encoding="utf-8") as _pf:
+         _pp = json.load(_pf)
+     primary_len = len(_pp) if isinstance(_pp, list) else 0
+ except Exception:
+     primary_len = 0
+
+ # Gather candidates
+ import glob
+ candidates = glob.glob(os.path.join(self.outputs_root, "cached_products", "poundwholesale-co-uk_products_cache*.json"))
+ best_path, best_len = primary_path, primary_len
+ for c in candidates:
+     try:
+         with open(c, "r", encoding="utf-8") as _cf:
+             _cp = json.load(_cf)
+         clen = len(_cp) if isinstance(_cp, list) else 0
+         if clen > best_len:
+             best_path, best_len = c, clen
+     except Exception:
+         continue
+
+ if primary_len < SMALL_MIN and best_len >= LARGE_MIN and best_path != primary_path:
+     self.log.warning(f"[CACHE_PICK] primary={primary_path},{primary_len} -> fallback={best_path},{best_len} reason=implausibly_small")
+     return best_path, {"count": best_len, "reason": "fallback"}
+ else:
+     self.log.info(f"[CACHE_PICK] primary={primary_path},{primary_len} (kept) reason=plausible")
+     return primary_path, {"count": primary_len, "reason": "primary"}
```

**Grep gates:**

* `rg -n "\\[CACHE_PICK\\]" logs/debug/*.log` → shows either **kept** primary or **fallback** with reason.

**Acceptance:**

* If current cache is very small and a big backup exists, the fallback is chosen with a clear banner; phase detection then uses that count.

---

## 4) Amazon progress commits: unify `total_cats=1` inside Amazon analysis

**Why (not covered in MDs):** Mixed values for `total_cats` (sometimes `1`, sometimes `_authoritative_total_categories()`) confuse progress percentages and resume math.

**Action:** In **all** Amazon-phase commit sites, pass `total_cats=1`.

**Search/Replace examples:**

```diff
- self.state_manager.commit_amazon_progress(cat_idx=cat_idx, queue_idx=queue_idx, total_cats=self._authoritative_total_categories(), cat_url=category_url, queue_len=total)
+ self.state_manager.commit_amazon_progress(cat_idx=cat_idx, queue_idx=queue_idx, total_cats=1, cat_url=category_url, queue_len=total)
```

**Grep gates:**

* `rg -n "commit_amazon_progress\\(.*total_cats=" tools/passive_extraction_workflow_latest.py` → every hit shows `total_cats=1` in Amazon loops.

---

## 5) Supplier progress banner: clamp display index to denominator

**Why (observed previously & mentioned in MDs):** Display index can exceed the frozen denominator (e.g., `27/6`). Clamp avoids misleading banners.

**Patch:**

```diff
--- a/tools/passive_extraction_workflow_latest.py
+++ b/tools/passive_extraction_workflow_latest.py
@@
- display_idx = cat_rel_idx + 1
- self.log.info(f"🔍 SUPPLIER STATE UPDATE: Index updated to {display_idx}/{cat_total}")
+ display_idx = cat_rel_idx + 1
+ if isinstance(cat_total, int) and display_idx > cat_total:
+     self.log.warning(f"[INDEX_CLAMP] display_idx={display_idx}->{cat_total} reason=exceeds_denominator")
+     display_idx = cat_total
+ self.log.info(f"🔍 SUPPLIER STATE UPDATE: Index updated to {display_idx}/{cat_total}")
```

**Acceptance:** `[INDEX_CLAMP]` should **not** appear in normal runs; if it does, the banner is still accurate.

---

## 6) Proof banners (keep / add)

* **Keep** the existing state-manager banners (they **are** present in latest logs):

  * `RESUME PTR: ...`
  * `✅ RESUME HONORED: ...`
  * `📋 RESUME PROOF (...): ...`

* **Optional, read-only banner (matches MD intent “freeze-once, read-always”):**
  Where we **read** the frozen denominator for a category (not setting it), log:

  ```python
  frozen = self.state_manager.get_frozen_denominator(category_url)
  nurl = normalize_url(category_url)
  self.log.info(f"[DENOM_FROZEN] url={nurl} total={int(frozen) if frozen else 0} (LOCKED)")
  ```

  Do **not** refreeze or change stored value here.

**Grep gates:** `rg -n "\\[DENOM_FROZEN\\]" logs/debug/*.log` → one line per category per run.

---

## 7) OpenAI key check: make non-fatal when AI is disabled

If any path hard-exits when `OPENAI_API_KEY` is missing, guard it with a feature toggle (e.g., `OPENAI_ENABLED` / `use_ai_features`), so non-AI runs are not blocked.

**Patch sketch:**

```diff
-if not os.getenv("OPENAI_API_KEY"):
-    sys.exit(1)
+if self.system_config.get("use_ai_features") and not os.getenv("OPENAI_API_KEY"):
+    self.log.error("OPENAI_API_KEY missing and AI features enabled; aborting.")
+    sys.exit(1)
```

---

# 🔎 Commentary: What’s **new** here vs the MD reports, and any disagreements

## Additions (not in the MDs)

1. **Cache selection fallback** (`[CACHE_PICK]` + “largest valid array” heuristic).
   *Reason:* prevents endless reverse-gap noise when the “current” cache is truncated but a large valid backup exists.

2. **Unify Amazon `total_cats=1`** for commit calls.
   *Reason:* avoids mixed semantics that distort progress math.

3. **OpenAI key non-fatal gating.**
   *Reason:* operational robustness on non-AI runs.

## Points I **do not** agree with (if present in your Set-1 tasks or MDs)

* **Do NOT reset `amazon_analysis_resumption_index` (or any resume pointer) at category init.**
  *Why:* The state manager already advances pointers **per commit** (your latest logs show `✅ RESUME HONORED`). A reset here can **wipe a precise pointer** on restart mid-queue and cause skips/duplication. Keep category init free of resume-index mutation; let the commit API own those pointers.

---

# ✅ Post-merge Validation (what I expect to see)

1. **Category index**

   * State: `current_category_index` increments to `1` after category-1 init.
   * No `- 1` write remains.

2. **Phase detection**

   * Logs contain `[PHASE_COUNTS] lm_file=… lm_count=N cache_file=… cache_count=M`.
   * Divergence warning now uses `(lm_file: N, cache_file: M)` wording.

3. **Cache fallback**

   * If “current” is tiny and a big backup exists:
     `[CACHE_PICK] primary=... -> fallback=... reason=implausibly_small`.

4. **Amazon commits**

   * All Amazon commit sites use `total_cats=1`.

5. **Supplier progress**

   * No more `Index updated to X/Y` with `X>Y`; clamp triggers `[INDEX_CLAMP]` if needed.

6. **Proof banners**

   * Existing resume banners still present.
   * Optional `[DENOM_FROZEN] ... (LOCKED)` appears once per category read.

---

## 📋 Quick Grep Pack (run after changes)

```
# no off-by-one
rg -n "initialize_category_processing\\(category_index=.*- 1" tools/passive_extraction_workflow_latest.py

# phase counts + wording
rg -n "\\[PHASE_COUNTS\\]" logs/debug/
rg -n "supplier_cache_vs_linking_map divergence .*\\(lm_file: .* cache_file: " logs/debug/

# cache chooser
rg -n "\\[CACHE_PICK\\]" logs/debug/

# amazon total_cats unified
rg -n "commit_amazon_progress\\(.*total_cats=" tools/passive_extraction_workflow_latest.py

# clamp
rg -n "\\[INDEX_CLAMP\\]" logs/debug/

# denom banner (optional)
rg -n "\\[DENOM_FROZEN\\]" logs/debug/
```

---

**That’s it.** Apply exactly these, keep comments referencing the two MDs where noted, and don’t add any resume-index resets. After I run a multi-category pass on your changes, I’ll send you Set-2 (post-run prompts) keyed to whatever the logs/state show.
