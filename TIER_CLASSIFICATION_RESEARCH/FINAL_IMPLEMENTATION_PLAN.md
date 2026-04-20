# FBA Tier Classifier — Final Implementation Plan
**Status:** Locked — ready to execute.
**Decisions confirmed:** D1 = A (direct edit), D2 = A (NEITHER → TIER_1_A), D3 = B (env-overridable thresholds).
**Scope:** Replace rule-based `classify_row` logic with probabilistic matcher (Approach 2) + EAN-first T1 split (T1_A / T1_B) + deterministic pack extraction v2.

**External review applied (2026-04-18):** Six concrete issues raised by external agent review were verified against actual code and addressed below. Each issue is noted in the relevant section.

---

## 0. TL;DR — What changes, what doesn't

| Area | Change | Risk |
|---|---|---|
| `tools/fba_report_filter.py` → `classify_row()` | New EAN-first T1_A/T1_B branch + probabilistic T2/T3/T4 branch + expanded `tiers` dict in `process_report` | Low — same function signature, same return keys (+ sub-tier fields) |
| `tools/fba_report_filter.py` → `process_report()` | Expand hardcoded `tiers` dict to include new tier names; one-time matcher fit before the row loop | Low |
| `dashboard_v2_redesign/api.py` → `get_analysis` | 4-line insert: fit matcher once before the per-row loop; fix variable name to `csv_path` | Minimal |
| `dashboard_v2_redesign/templates/index.html` | Add T1_A and T1_B options to tier filter dropdown (3 lines) | None |
| `dashboard_v2_redesign/static/js/app.js` | tier1Count card sums T1_VERIFIED + T1_A + T1_B (1 line change) | None |
| New files | `tools/_pack_extraction.py`, `tools/_probabilistic_matcher_core.py`, `tools/fba_probabilistic_classifier.py` | None — pure additions |
| Rollback | `FBA_USE_LEGACY_CLASSIFIER=1` → falls back to current code path exactly | None |

**Measured facts (from committed artifacts, not prose):**
- Pack v2 vs v1 on 4,145 EAN-matched rows (`pack_audit_v2.json`): confident buckets 562 (13.6%) → 746 (18.0%), zero regressions.
- Conversation-level review of ~100 newly-extracted rows found 0 errors; 30 NEITHER samples reviewed, all single-unit products. *These are not formal committed benchmarks — they are manual eyeball checks recorded in session.*
- `NEITHER` bucket (2,629 rows = 63.4%) consists of legitimate single-unit products per the 30-sample review. Treated as TIER_1_A per D2.

---

## 1. Locked decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| D1 | Edit `tools/fba_report_filter.py` in place vs. `_v2` sibling | **A — direct edit** | One diff, no duplicate files. Legacy path preserved via env var. |
| D2 | 2,629 `NEITHER` rows (EAN-match, no pack markers) | **A — TIER_1_A_VERIFIED** | 30/30 reviewed samples are single-unit products. Forcing 2,600 rows into audit for ~1-5% edge cases is disproportionate. |
| D3 | Probabilistic matcher thresholds | **B — env-overridable** | `FBA_TIER2_PROB` / `FBA_TIER3_PROB` allow post-live tuning without code changes. |

**On the listing-swap gate (raised by external review):**
The external agent flagged that the earlier comparative report recommended an EAN + title-mismatch gate, and that the final plan removes it. This is correct — the gate was deliberately removed per user's explicit directive: *"product with matching EANs should be treated as tier 1 regardless of title similarities."* The safeguard that remains is GTIN checksum validation (Mod-10). A valid checksum-passing EAN collision between two genuinely different products is not a realistic risk. What the plan adds instead is a non-demoting `SUSPICIOUS_TITLE_MISMATCH` flag on EAN-matched rows where title similarity is below 0.15 AND brand first-words differ — visible in the CSV for manual review, does not change the tier.

**Why the legacy branch stays in the file:** Dead code behind `FBA_USE_LEGACY_CLASSIFIER=1`, invisible to dashboard users. Purpose: (a) instant rollback without code revert, (b) side-by-side comparison on the same CSV. Can be deleted in a follow-up once the new path has seen a few live reports.

---

## 2. Files created (full source)

### 2.1 `tools/_pack_extraction.py` (NEW)

```python
"""Deterministic pack-size extraction — v2. No integer-fallback rule."""
from __future__ import annotations
import re, math
from typing import Optional, Any

PACK_PATTERNS = [
    # existing (v1)
    r"pack of (\d+)",
    r"(\d+)\s*pack\b",
    r"(\d+)\s*pk\b",
    r"(\d+)\s*pcs?\b",
    r"set of (\d+)",
    r"\b(\d+)x\b",
    r"\bx(\d+)\b",
    # new (v2) — deterministic only, no integer-fallback
    r"(\d+)\s*piece[s]?\b",
    r"\bpk\s*(\d+)\b",
    r"(\d+)\s*count\b",
    r"(\d+)\s*ct\b",
    r"\bpack\s+(\d+)\b",
    r"\b(\d+)\s*-\s*pack\b",
]

def _clean(value: Any) -> str:
    s = "" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value).lower()
    s = s.replace("\u00d7", "x").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"[^a-z0-9\.\-\+ ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def extract_pack(value: Any) -> Optional[int]:
    s = _clean(value)
    for pattern in PACK_PATTERNS:
        m = re.search(pattern, s)
        if m:
            try:
                n = int(m.group(1))
                if 1 <= n <= 999:
                    return n
            except ValueError:
                continue
    return None
```

**Evidence (from `TIER_CLASSIFICATION_RESEARCH/rerun/pack_audit_v2.json`):**

| Bucket | v1 | v2 | Δ |
|---|---|---|---|
| BOTH_EQUAL | 495 | 663 | +168 |
| BOTH_DIFFERENT | 67 | 83 | +16 |
| ONLY_SUP | 456 | 355 | −101 |
| ONLY_AMZ | 359 | 415 | +56 |
| NEITHER | 2,768 | 2,629 | −139 |
| **Confident (EQUAL + DIFFERENT)** | **562 (13.6%)** | **746 (18.0%)** | **+184** |
| Regressions (EQUAL → DIFFERENT) | — | **0** | — |

### 2.2 `tools/_probabilistic_matcher_core.py` (NEW)

Byte-for-byte copy of `FINAL STALE/agent analyses/initial_probabilistic_implementation_package/probabilistic_matcher_prototype.py`. No code changes. Pinned copy so prod code does not import from `FINAL STALE/`.

**Wording note (raised by external review):** The prototype uses plain `LogisticRegression`, not `CalibratedClassifierCV`. The probability output is a logistic regression probability estimate, not an explicitly calibrated posterior. All references in this plan use "probability estimate" accordingly.

### 2.3 `tools/fba_probabilistic_classifier.py` (NEW)

*Fix applied: replaced single global `_matcher` with a `dict` keyed by `report_id` + thread-local to track which report is active per thread. This eliminates the race condition raised by external review where two concurrent API requests for different reports could overwrite each other's matcher.*

```python
"""Probabilistic FBA row classifier. Wraps A2 matcher + pack-aware T1 split."""
from __future__ import annotations
import os, threading
from typing import Optional, Dict, Any, List
import pandas as pd

from tools._pack_extraction import extract_pack
from tools._probabilistic_matcher_core import ProbabilisticPairMatcher

_DEFAULT_T2_PROB = float(os.getenv("FBA_TIER2_PROB", "0.95"))
_DEFAULT_T3_PROB = float(os.getenv("FBA_TIER3_PROB", "0.10"))

_matchers: Dict[str, ProbabilisticPairMatcher] = {}
_matchers_lock = threading.Lock()
_current_report = threading.local()  # per-thread active report_id


def prepare_matcher(report_rows: List[Dict[str, Any]], report_id: str) -> None:
    """Fit matcher for this report. Idempotent — no-op if already fitted."""
    with _matchers_lock:
        if report_id not in _matchers:
            df = pd.DataFrame(report_rows)
            m = ProbabilisticPairMatcher(
                tier2_prob=_DEFAULT_T2_PROB,
                tier3_prob=_DEFAULT_T3_PROB,
            )
            m.fit(df)
            _matchers[report_id] = m
    _current_report.id = report_id


def reset_matcher(report_id: Optional[str] = None) -> None:
    with _matchers_lock:
        if report_id:
            _matchers.pop(report_id, None)
        else:
            _matchers.clear()


def classify_row_probabilistic(row: Dict[str, Any]) -> Dict[str, Any]:
    report_id = getattr(_current_report, "id", None)
    matcher = _matchers.get(report_id) if report_id else None
    if matcher is None:
        raise RuntimeError("prepare_matcher() must be called before classify_row_probabilistic()")

    sup_title = row.get("SupplierTitle", "") or ""
    amz_title = row.get("AmazonTitle", "") or ""
    sup_ean = str(row.get("EAN", "") or "").strip()
    amz_ean = str(row.get("EAN_OnPage", "") or "").strip()

    # Pack extraction
    p_sup = extract_pack(sup_title)
    p_amz = extract_pack(amz_title)
    if p_sup is not None and p_amz is not None:
        pack_bucket = "BOTH_EQUAL" if p_sup == p_amz else "BOTH_DIFFERENT"
    elif p_sup is not None:
        pack_bucket = "ONLY_SUP"
    elif p_amz is not None:
        pack_bucket = "ONLY_AMZ"
    else:
        pack_bucket = "NEITHER"

    # Probability estimate from A2 matcher
    score = matcher.score_pair(sup_title, amz_title)
    prob_estimate = float(score.get("posterior", 0.0))
    reasons: List[str] = list(score.get("reasons", []))
    flags: List[str] = []

    # Financial sanity
    try:
        roi = float(row.get("ROI", 0) or 0)
        net_profit = float(row.get("NetProfit", 0) or 0)
        supplier_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
        sell_price = float(row.get("SellingPrice_incVAT", 0) or 0)
    except (ValueError, TypeError):
        roi = net_profit = supplier_price = sell_price = 0.0

    if roi > 1000:
        flags.append("EXTREME_ROI")
        reasons.append(f"Suspiciously high ROI: {roi:.0f}%")
    if sell_price > 0 and supplier_price > 0 and (sell_price / supplier_price) > 20:
        flags.append("EXTREME_PRICE_RATIO")
        reasons.append(f"Price ratio {sell_price/supplier_price:.1f}x")
    if net_profit <= 0:
        flags.append("UNPROFITABLE")

    # Category mismatch
    category_keywords = {
        "electronics": ["trimmer", "charger", "battery", "headphone", "speaker", "phone", "tablet", "laptop"],
        "food": ["chocolate", "biscuit", "cereal", "snack", "sweet", "candy"],
        "health": ["cream", "soap", "shampoo", "wash", "lotion", "gel", "wipe"],
        "cleaning": ["bleach", "detergent", "cloth", "mop", "brush"],
        "toys": ["toy", "game", "puzzle", "doll", "figure"],
    }
    sup_l, amz_l = sup_title.lower(), amz_title.lower()
    sup_cats, amz_cats = set(), set()
    for cat, kws in category_keywords.items():
        if any(k in sup_l for k in kws): sup_cats.add(cat)
        if any(k in amz_l for k in kws): amz_cats.add(cat)
    if sup_cats and amz_cats and not (sup_cats & amz_cats):
        flags.append("CATEGORY_MISMATCH")
        reasons.append(f"Category mismatch: {sup_cats} vs {amz_cats}")

    # Brand mismatch (first-token heuristic; low-weight signal only)
    sup_brand = sup_title.strip().split()[0].lower() if sup_title.strip() else ""
    amz_brand = amz_title.strip().split()[0].lower() if amz_title.strip() else ""
    if sup_brand and amz_brand and sup_brand != amz_brand:
        flags.append("BRAND_MISMATCH")

    # EAN exact match (checksum-validated)
    from tools.fba_report_filter import normalize_ean, gtin_checksum_valid, title_similarity as _sim
    nsup, namz = normalize_ean(sup_ean), normalize_ean(amz_ean)
    ean_exact_match = bool(
        nsup and namz and nsup == namz
        and gtin_checksum_valid(nsup) and gtin_checksum_valid(namz)
    )

    # ---- TIER DECISION ----

    if ean_exact_match:
        # Suspicious-title audit flag — does NOT change tier (user directive: EAN = always T1)
        sim = _sim(sup_title, amz_title)
        if sim < 0.15 and "BRAND_MISMATCH" in flags:
            flags.append("SUSPICIOUS_TITLE_MISMATCH")
            reasons.append(f"EAN match but titles very dissimilar (sim={sim:.2f}) — manual check advised")

        if pack_bucket == "BOTH_EQUAL":
            tier = "TIER_1_A_VERIFIED"
            reasons.append("EAN match + pack sizes equal")
        elif pack_bucket == "BOTH_DIFFERENT":
            tier = "TIER_1_B_AUDIT_OUT"
            reasons.append(f"EAN match but pack differs (sup={p_sup}, amz={p_amz}) — audit NetProfit")
        elif pack_bucket in ("ONLY_SUP", "ONLY_AMZ"):
            tier = "TIER_1_B_AUDIT_OUT"
            reasons.append(f"EAN match, pack visible on one side only ({pack_bucket})")
        else:  # NEITHER — D2 = A
            tier = "TIER_1_A_VERIFIED"
            reasons.append("EAN match, no pack markers in either title (assumed single-unit)")

        return {
            "tier": tier,
            "confidence_score": int(round(prob_estimate * 100)),
            "prob_estimate": round(prob_estimate, 4),
            "reasons": reasons,
            "flags": flags,
            "ean_exact_match": True,
            "sup_pack": p_sup,
            "amz_pack": p_amz,
            "pack_bucket": pack_bucket,
        }

    # No EAN match — probabilistic tier + post-layer
    if prob_estimate >= _DEFAULT_T2_PROB:
        tier = "TIER_2_LIKELY"
    elif prob_estimate >= _DEFAULT_T3_PROB:
        tier = "TIER_3_NEEDS_REVIEW"
    else:
        tier = "TIER_4_REJECTED"

    if tier == "TIER_2_LIKELY" and "BRAND_MISMATCH" in flags:
        tier = "TIER_3_NEEDS_REVIEW"
        reasons.append("Demoted T2→T3: brand mismatch on non-EAN match")

    if "CATEGORY_MISMATCH" in flags and tier in ("TIER_2_LIKELY", "TIER_3_NEEDS_REVIEW"):
        tier = "TIER_4_REJECTED"
        reasons.append("Rejected: category mismatch")

    if "EXTREME_PRICE_RATIO" in flags and tier == "TIER_2_LIKELY":
        tier = "TIER_3_NEEDS_REVIEW"

    return {
        "tier": tier,
        "confidence_score": int(round(prob_estimate * 100)),
        "prob_estimate": round(prob_estimate, 4),
        "reasons": reasons,
        "flags": flags,
        "ean_exact_match": False,
        "sup_pack": p_sup,
        "amz_pack": p_amz,
        "pack_bucket": pack_bucket,
    }
```

---

## 3. Diffs to existing files

### 3.1 `tools/fba_report_filter.py` — two separate hunks

**Hunk A — top of file, after existing imports:**

```diff
 from difflib import SequenceMatcher
+
+# Probabilistic classifier — opt-out via FBA_USE_LEGACY_CLASSIFIER=1
+_USE_LEGACY = os.getenv("FBA_USE_LEGACY_CLASSIFIER", "0") == "1"
+if not _USE_LEGACY:
+    try:
+        from tools.fba_probabilistic_classifier import (
+            classify_row_probabilistic,
+            prepare_matcher,
+        )
+    except Exception as _e:
+        _USE_LEGACY = True
+        print(f"[fba_report_filter] probabilistic import failed ({_e}); using legacy")
```

**Hunk B — inside `classify_row`, at the very top of the function body (before any existing logic):**

```diff
 def classify_row(row: dict) -> dict:
     """
-    Returns dict with: tier, confidence_score, reasons[], flags[]
+    Returns dict with: tier, confidence_score, reasons[], flags[], ean_exact_match,
+    title_similarity, shared_tokens. Probabilistic path also returns: prob_estimate,
+    sup_pack, amz_pack, pack_bucket.
     """
+    if not _USE_LEGACY:
+        try:
+            res = classify_row_probabilistic(row)
+            res.setdefault("title_similarity", round(
+                title_similarity(row.get("SupplierTitle", ""), row.get("AmazonTitle", "")), 3))
+            res.setdefault("shared_tokens", shared_token_count(
+                row.get("SupplierTitle", ""), row.get("AmazonTitle", "")))
+            return res
+        except RuntimeError:
+            pass  # prepare_matcher not yet called — fall through to legacy
+
     supplier_ean = normalize_ean(row.get("EAN", ""))
     # ... rest of legacy logic unchanged ...
```

**Hunk C — inside `process_report`, two changes:**

*Fix 1 — read rows once and fit matcher before the classify loop:*

```diff
-    # existing: open file, iterate rows, call classify_row per row
+    # Read all rows upfront so matcher can be fitted before classification
+    fieldnames = None
+    all_rows = []
+    with open(csv_path, "r", encoding="utf-8-sig") as f:
+        reader = csv.DictReader(f)
+        fieldnames = reader.fieldnames or []
+        for i, row in enumerate(reader, start=2):
+            row["_row_id"] = i
+            all_rows.append(row)
+
+    if not _USE_LEGACY:
+        try:
+            prepare_matcher(all_rows, report_id=str(csv_path.resolve()))
+        except Exception as e:
+            print(f"[fba_report_filter] matcher fit failed ({e}); using legacy")
+            globals()["_USE_LEGACY"] = True
+
+    rows = []
+    for row in all_rows:
+        classification = classify_row(row)
+        row.update(classification)
+        rows.append(row)
```

*Fix 2 — expand `tiers` dict to include new tier names (prevents KeyError):*

```diff
-    tiers = {
-        "TIER_1_VERIFIED": [],
-        "TIER_2_LIKELY": [],
-        "TIER_3_NEEDS_REVIEW": [],
-        "TIER_4_REJECTED": [],
-    }
-    for row in rows:
-        tiers[row["tier"]].append(row)
+    tiers = {
+        "TIER_1_A_VERIFIED": [],
+        "TIER_1_B_AUDIT_OUT": [],
+        "TIER_1_VERIFIED": [],       # legacy key — populated when FBA_USE_LEGACY_CLASSIFIER=1
+        "TIER_2_LIKELY": [],
+        "TIER_3_NEEDS_REVIEW": [],
+        "TIER_4_REJECTED": [],
+    }
+    for row in rows:
+        t = row.get("tier", "TIER_4_REJECTED")
+        if t not in tiers:
+            tiers[t] = []            # defensive catch-all for any future tier names
+        tiers[t].append(row)
```

### 3.2 `dashboard_v2_redesign/api.py` — single hunk

*Fix applied: `report_path` in the previous draft was wrong. Actual variable in scope is `csv_path` (confirmed at api.py:564-575).*

```diff
@@ after csv_path is resolved (around line 584) and rows list is populated @@
         rows.append(row)
+
+    # Fit probabilistic matcher once per report before any classify_row calls
+    if filter_mod is not None:
+        try:
+            from tools.fba_probabilistic_classifier import prepare_matcher
+            prepare_matcher(rows, report_id=str(csv_path))
+        except Exception as e:
+            print(f"[api.get_analysis] matcher prep failed ({e}); legacy path active")

     # existing: tier_counts computation
     tier_counts = {}
```

*Note: `prepare_matcher` is idempotent — calling it after rows are already built is fine because the matcher fits on the full dataset before classify_row is called per row. In the api path, classify_row is not called here — it was called inside the reader loop above. This means the api.py fit call needs to go BEFORE the reader loop, not after. See corrected placement below:*

```diff
@@ after csv_path is resolved, before the reader loop (around line 582) @@
         filter_mod = _get_filter_module()
         if filter_mod is None:
             return JSONResponse({"error": True, "message": "fba_report_filter.py not found in tools/"})

+        # Pre-read rows for matcher fitting, then classify
         import csv as csv_mod
-        rows = []
-        with open(csv_path, "r", encoding="utf-8-sig") as f:
-            reader = csv_mod.DictReader(f)
-            ...
-            for i, row in enumerate(reader, start=2):
-                ...
-                classification = filter_mod.classify_row(row, **classify_kwargs)
-                row.update(classification)
-                rows.append(row)
+        raw_rows = []
+        with open(csv_path, "r", encoding="utf-8-sig") as f:
+            reader = csv_mod.DictReader(f)
+            selected_sales_field = sales_field if sales_field in {"bought_in_past_month", "amazon_sales_badge"} else "bought_in_past_month"
+            for i, row in enumerate(reader, start=2):
+                row["_row_id"] = i
+                sales_source = selected_sales_field if selected_sales_field in row else (
+                    "bought_in_past_month" if "bought_in_past_month" in row else (
+                        "amazon_sales_badge" if "amazon_sales_badge" in row else ""
+                    )
+                )
+                row["sales_value"] = _parse_sales_value(row.get(sales_source)) if sales_source else 0.0
+                raw_rows.append(row)
+
+        try:
+            from tools.fba_probabilistic_classifier import prepare_matcher
+            prepare_matcher(raw_rows, report_id=str(csv_path))
+        except Exception as e:
+            print(f"[api.get_analysis] matcher prep failed ({e}); legacy path active")
+
+        rows = []
+        for row in raw_rows:
+            classify_kwargs = {}
+            try:
+                if "loose_mode" in inspect.signature(filter_mod.classify_row).parameters:
+                    classify_kwargs["loose_mode"] = loose_mode
+            except (TypeError, ValueError):
+                pass
+            classification = filter_mod.classify_row(row, **classify_kwargs)
+            row.update(classification)
+            rows.append(row)
```

### 3.3 `dashboard_v2_redesign/templates/index.html` — tier filter dropdown

*Fix applied: filter dropdown hardcoded `TIER_1_VERIFIED` only. New tier names would make the T1 filter show nothing.*

```diff
                 <select id="analysisTierFilter" class="glass-input">
                   <option value="all">All Tiers</option>
                   <option value="TIER_1_VERIFIED">T1: Verified</option>
+                  <option value="TIER_1_A_VERIFIED">T1-A: Verified (exact pack)</option>
+                  <option value="TIER_1_B_AUDIT_OUT">T1-B: Audit (pack diff)</option>
                   <option value="TIER_2_LIKELY">T2: Likely</option>
                   <option value="TIER_3_NEEDS_REVIEW">T3: Review</option>
                   <option value="TIER_4_REJECTED">T4: Rejected</option>
                 </select>
```

### 3.4 `dashboard_v2_redesign/static/js/app.js` — tier 1 count card

*Fix applied: `tier1Count` read `tc.TIER_1_VERIFIED` only — would show 0 once new tier names are in use.*

```diff
-            document.getElementById('tier1Count').textContent = (tc.TIER_1_VERIFIED || 0).toLocaleString();
+            document.getElementById('tier1Count').textContent = (
+                (tc.TIER_1_VERIFIED || 0) + (tc.TIER_1_A_VERIFIED || 0) + (tc.TIER_1_B_AUDIT_OUT || 0)
+            ).toLocaleString();
```

---

## 4. Validation checklist (run BEFORE merging)

| # | Command | Expected outcome |
|---|---|---|
| 1 | `python TIER_CLASSIFICATION_RESEARCH/rerun/pack_audit_v2.py` | Already run. Confident 13.6% → 18.0%, 0 regressions. Artifact: `pack_audit_v2.json`. |
| 2 | `FBA_USE_LEGACY_CLASSIFIER=1 python tools/fba_report_filter.py <csv>` then compare `tier` column to current prod output on the same CSV | **Tier assignments must be identical row-for-row** (not byte-identical — timestamps differ). Check: `python -c "import csv; ..."` diff on the tier column only. |
| 3 | `python tools/fba_report_filter.py <csv>` (EFG) | T1_A + T1_B row count equals legacy T1_VERIFIED count. No KeyError on tiers dict. |
| 4 | `python tools/fba_report_filter.py <csv>` (PoundWholesale) | Same. Spot-check ≥ 20 T1_B rows for legitimate pack differences. |
| 5 | `python tools/fba_report_filter.py <csv>` (Angel) | Same — confirms generalization across naming conventions. |
| 6 | Hit dashboard `GET /api/analysis?...` on each report | T1 card count = T1_A + T1_B combined. T1-A and T1-B appear as selectable filter options. No JS errors. |
| 7 | Pipe filtered CSV to downstream operator agent | No schema errors on new fields. |

**Abort criteria:** If step 2 shows any row where the new path assigns a different tier than legacy on the same input, stop and investigate. If T1_B false-positive rate on step 3-5 spot-check exceeds 5%, stop.

---

## 5. Rollback

```bash
export FBA_USE_LEGACY_CLASSIFIER=1
```

All new imports are wrapped in try/except — a broken scikit-learn install or missing new file will not crash the tool, it will fall back to legacy silently.

---

## 6. Out of scope

- Listing-swap demotion gate — removed per user directive (EAN match = always T1; SUSPICIOUS_TITLE_MISMATCH flag added as non-demoting audit signal instead).
- Common-integer fallback for pack extraction — removed per past-inconsistency constraint.
- Manual source-of-truth labels — was only for the rejected Approach 4.
- Changes to upstream scrapers, Keepa calls, financial calculator.

---

## 7. Execution order

1. Create `tools/_pack_extraction.py` (§2.1).
2. Copy prototype → `tools/_probabilistic_matcher_core.py` (§2.2).
3. Create `tools/fba_probabilistic_classifier.py` (§2.3).
4. Apply all three hunks to `tools/fba_report_filter.py` (§3.1).
5. Apply the expanded diff to `dashboard_v2_redesign/api.py` (§3.2).
6. Apply 3-line diff to `dashboard_v2_redesign/templates/index.html` (§3.3).
7. Apply 1-line diff to `dashboard_v2_redesign/static/js/app.js` (§3.4).
8. Run validation steps 2-5. Report tier-column equivalence result + T1_A/T1_B counts per supplier.
9. Spot-check ≥ 20 T1_B rows per supplier. Report findings before sign-off.

Say "go" and I'll execute steps 1-9.
