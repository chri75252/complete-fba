# FBA Analysis Agent vNext — Phase 2 Implementation Prompt (Self-Contained)

**Purpose:** This prompt is designed to be pasted into a FRESH chat with no prior context. It contains all necessary information for a new agent to implement the vNext upgrade.

---

# ROLE
You are a **Staff Engineer** implementing Phase 2 of the **FBA Product Analysis Agent vNext** upgrade.

**Timezone:** Asia/Dubai (UTC+4)  
**Date:** 2026-01-05

---

# WHAT IS THE FBA ANALYSIS AGENT?

The FBA Product Analysis Agent is a deterministic analysis pipeline that processes supplier product data and identifies profitable Amazon FBA (Fulfillment by Amazon) resale opportunities. It analyzes product listings by comparing supplier data against Amazon listings and categorizes each row into one of these buckets:

- **VERIFIED** — Exact EAN match + brand match + pack match + profit > 0 → Recommended for purchase
- **HIGHLY LIKELY** — Strong brand/product match, no EAN but high confidence → Recommended for purchase
- **NEEDS VERIFICATION** — Moderate match, ambiguous signals → Requires manual review
- **FILTERED OUT** — Confirmed match but excluded for reason (pack mismatch, profit ≤ 0) → Printed in report tables
- **UNRELATED** — Completely different products → Count-only, NOT printed in tables

---

# CURRENT PIPELINE ARCHITECTURE (WHAT EXISTS)

## Existing Workflow (Single-Pass)
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ CURRENT PIPELINE (ONE-SHOT — NO ITERATION)                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: load_report() + normalize_columns()                                     │
│ - Load CSV/XLSX file                                                            │
│ - Generate RowID for each row                                                   │
│ - Normalize column names, parse EANs, clean financial data                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: run_preflight()                                                         │
│ - Sample 50 rows                                                                │
│ - Call LLM to detect supplier-specific patterns (pack keywords, brands, etc.)   │
│ - Fallback to heuristic if no API key                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: load_supplier_memory() + merge_calibration()                            │
│ - Load existing supplier calibration from memory/suppliers/{id}/                │
│ - Merge with preflight output and user overrides                                │
│ - Current precedence: overrides > existing > preflight > defaults               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: analyze_all_rows()                                                      │
│ - For each row: validate EAN, parse titles, detect pack quantities              │
│ - Apply dimension/spec shields (trap detection)                                 │
│ - Calculate adjusted profit (RSU recalculation if pack mismatch)                │
│ - Assign bucket + confidence score                                              │
│ - Output: coverage_ledger DataFrame + evidence list                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: validate_coverage() + validate_profit()                                 │
│ - Coverage gate: every RowID must appear exactly once                           │
│ - Profit gate: no positive bucket with adjusted_profit ≤ 0                      │
│ - If either fails: raise SystemExit (pipeline stops)                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: render_phasea_report() + write artifacts                                │
│ - Generate Markdown report with fixed-width tables                              │
│ - Write coverage_ledger.csv, evidence.jsonl, run_summary.json                   │
│ - Persist supplier calibration                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Existing Files in `src/fba_agent/`

| File | Purpose | Key Functions |
|------|---------|---------------|
| `run.py` | Main orchestrator | `run_analysis()` — calls all steps in sequence |
| `io.py` | Data loading | `load_report()`, `normalize_columns()` |
| `preflight.py` | LLM calibration | `run_preflight()`, `_heuristic_preflight()` |
| `memory_store.py` | Supplier memory | `load_supplier_memory()`, `merge_calibration()`, `persist_calibration()` |
| `analysis.py` | Row analysis | `analyze_row()`, `analyze_all_rows()` |
| `pack.py` | Pack detection | `parse_pack_quantity()`, `pack_ratio()` — includes dimension/spec shields |
| `ean.py` | EAN validation | `normalize_and_validate()`, `validate_gtin()` — GTIN checksum |
| `validate.py` | Validation gates | `validate_coverage()`, `validate_profit()` |
| `render.py` | Report generation | `render_phasea_report()` |
| `cli.py` | CLI interface | `main()` — commands: analyze, top, explain, export, rerun, list-runs, show-memory |
| `types.py` | Dataclasses | `SupplierNamingConvention`, `MergedConfig`, `RowDecisionRecord`, etc. |
| `constants.py` | Constants | `TABLE_COLUMNS`, `STOPWORDS`, default paths |
| `openai_client.py` | OpenAI adapter | `chat_json()`, `load_openai_config()` |
| `moonshot.py` | Moonshot adapter | Moonshot API wrapper |
| `scoring.py` | Confidence scoring | `compute_confidence()` |
| `variant.py` | Variant parsing | `parse_variant()` — capacity/color/scent |
| `text.py` | Text utilities | `sanitize_cell()`, `tokenize()`, `jaccard_similarity()` |

---

# AUTHORITATIVE SPECS (CONFLICT RESOLUTION ORDER)

**Order:** Main > Manual > Preflight. If spec conflicts arise, log to `docs/spec_conflicts.md`.

| Spec File | Location | Purpose |
|-----------|----------|---------|
| **Main Spec** | `codex sgent/prompt_specs/FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md` | Report schema, TABLE_SCHEMA, validation checklist, fixed-width table rules |
| **Manual Guide** | `codex sgent/prompt_specs/FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md` | Decision trees, trap patterns, analysis methodology |
| **Preflight Spec** | `codex sgent/prompt_specs/AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md` | Calibration output schema, pattern detection |
| **Authoritative PRD** | `codex sgent/PRD_VNEXT_PHASE1_FBA_AGENT_UPGRADE_20260104.md` | vNext requirements, iteration loop, regression guard |

---

# WHAT vNEXT ADDS (THE UPGRADE)

The vNext upgrade transforms the single-pass pipeline into an **iterative refinement pipeline**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ vNEXT PIPELINE (ITERATIVE — MAX 2 OR 3 ITERATIONS)                              │
└─────────────────────────────────────────────────────────────────────────────────┘

STEP 0: Load + normalize + generate stable_key (collision = HARD FAIL)
STEP 1: Optional prefilter (Sales>0, NetProfit>0)
STEP 2: Memory layers (global traps → supplier calibration → supplier traps → overrides)
                                        │
                ┌───────────────────────┘
                │
                ▼
        ╔═══════════════════════════════════════════════════════════╗
        ║             ITERATION LOOP (max_iterations = 2)            ║
        ╚═══════════════════════════════════════════════════════════╝
                │
                ├──► ITERATION 1 (Baseline)
                │    ├── analyze_all_rows() + detect anomalies
                │    ├── validate_coverage() + validate_profit()
                │    ├── AI Critique (report-level review)
                │    └── AI Adjudication (ambiguous rows, capped)
                │
                ├──► Should run ITERATION 2?
                │    ├── Hard gate failure correctable?
                │    ├── Critique found safe changes?
                │    ├── Regression guard triggered?
                │    └── Large anomaly signals?
                │                │
                │         YES ───┼──► ITERATION 2 (Refined)
                │                │    ├── Apply bounded adjustments
                │                │    ├── Re-analyze with adjustments
                │                │    └── Validate + compare vs iter_1
                │                │
                │          NO ───┼──► Skip to finalize
                │                │
                └────────────────┘
                │
                ▼
STEP 3: Regression Guard
        ├── Compare iter_2 vs iter_1
        ├── Compare vs last K historical runs
        ├── Missing stable keys = HARD FAIL
        └── Good-to-bad transitions > threshold = BLOCK (unless justified)
                │
                ▼
STEP 4: Finalization
        ├── If all gates pass: promote to final/
        └── If blocked: produce DRAFT — NOT PASSED + failure summary
```

---

# NON-NEGOTIABLES (HARD RULES — MUST NOT VIOLATE)

1. **Deterministic spine remains authoritative.**
   - LLM outputs (adjudication, critique) are **bounded suggestions only**.
   - The deterministic scoring formula always produces the final confidence score.
   - AI CANNOT directly rewrite the final report.

2. **Memory layer precedence (strict order):**
   ```
   1. User overrides (highest priority)
   2. Supplier traps (supplier-specific trap patterns)
   3. Supplier calibration (persisted merged preflight per supplier)
   4. Global trap library (universal dimension/spec shields)
   5. Defaults (lowest priority)
   ```
   - "Supplier calibration" = persisted merged preflight output **per supplier** (NOT global).
   - "Global trap library" = universal traps at `memory/global/trap_library.jsonl`.

3. **Stable key + collision rule:**
   - Generate stable_key deterministically for each row.
   - Primary strategy: `sha256(SupplierURL|ASIN)[:16]`
   - Fallback (no SupplierURL): `sha256(EAN_norm|ASIN|SupplierTitle[:50]|AmazonTitle[:50])[:16]`
   - **Collision = HARD FAIL.** Emit `stable_key_collisions.json` + block finalization.
   - Do NOT disambiguate via RowID (breaks cross-run comparability).

4. **Canonical report filename:**
   - Must be: `PHASEA_MANUAL_REPORT_YYYYMMDD.md` (per Main spec).
   - Also generate timestamped archive: `PHASEA_MANUAL_REPORT_YYYYMMDD_HHMM.md`.
   - Do NOT use `CODEX_MANUAL_REPORT_*`.

5. **Promotion gating:**
   - Never produce "final" artifacts unless:
     - All hard gates pass (coverage, profit, stable_key)
     - Regression guard says "not worse"
     - Critique has no unresolved high-severity issues
   - If blocked: produce `DRAFT — NOT PASSED` artifacts + explicit "what to verify manually" section.

6. **FILTERED OUT vs UNRELATED:**
   - FILTERED OUT = confirmed matches excluded for reason (pack/profit) → **print in tables**
   - UNRELATED = completely different products → **count-only, NOT in tables**

---

# TARGET CODEBASE

**Location:** `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\src\fba_agent`

**Memory directory:** `memory/` (create if missing)

**Output directory:** `codex sgent/AGENT REPORT/` (existing)

---

# IMPLEMENTATION PHASES

## PHASE 2a — FOUNDATION (stable_key, memory layers, types)

Implement in this exact order:

### 1. `types.py` — Add new dataclasses

Add these to `src/fba_agent/types.py`:

```python
@dataclass(frozen=True)
class IterationResult:
    iteration_number: int
    ledger: pd.DataFrame
    evidence: list[dict]
    validation_passed: bool
    validation_errors: list[str]
    anomaly_summary: dict
    critique: "CritiqueResult | None"
    adjudication_results: list["AdjudicationResult"]

@dataclass(frozen=True)
class RegressionDiff:
    missing_stable_keys: list[str]
    bucket_transitions: dict[str, dict[str, int]]  # {stable_key: {"from": bucket, "to": bucket}}
    good_to_bad_count: int
    blocked: bool
    justifications: list[dict]

@dataclass(frozen=True)
class AdjudicationResult:
    row_id: int
    stable_key: str
    extracted_signals: dict
    trap_detections: list[str]
    recommended_bucket: str
    confidence_suggestion: int
    reasoning: str

@dataclass(frozen=True)
class CritiqueResult:
    high_severity_issues: list[dict]
    proposed_changes: list[dict]
    overall_assessment: str
    recommended_action: str  # "finalize", "apply_and_rerun", "block"
```

### 2. `stable_key.py` — Create new file

Create `src/fba_agent/stable_key.py`:

```python
"""Stable key generation for cross-run comparison."""
from __future__ import annotations

import hashlib
import pandas as pd

class StableKeyCollisionError(Exception):
    """Raised when stable_key collisions are detected."""
    def __init__(self, collisions: list[dict]):
        self.collisions = collisions
        super().__init__(f"Stable key collisions detected: {len(collisions)} collisions")

def _normalize_for_hash(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower()[:50]

def generate_stable_key(
    row: pd.Series,
    has_supplier_url: bool = False,
) -> str:
    """
    Generate deterministic stable key for a row.
    
    Primary: sha256(SupplierURL|ASIN)[:16]
    Fallback: sha256(EAN_norm|ASIN|SupplierTitle[:50]|AmazonTitle[:50])[:16]
    """
    if has_supplier_url and "SupplierURL" in row.index and row.get("SupplierURL"):
        key_input = f"{_normalize_for_hash(row['SupplierURL'])}|{_normalize_for_hash(row.get('ASIN', ''))}"
    else:
        ean = _normalize_for_hash(str(row.get("SupplierEAN_raw", "")))
        asin = _normalize_for_hash(str(row.get("ASIN", "")))
        supplier_title = _normalize_for_hash(str(row.get("SupplierTitle", "")))
        amazon_title = _normalize_for_hash(str(row.get("AmazonTitle", "")))
        key_input = f"{ean}|{asin}|{supplier_title}|{amazon_title}"
    
    return hashlib.sha256(key_input.encode("utf-8")).hexdigest()[:16]

def check_collisions(df: pd.DataFrame) -> tuple[bool, list[dict]]:
    """
    Check for stable_key collisions.
    
    Returns (has_collisions, collision_details).
    If has_collisions=True, this is a HARD FAIL.
    """
    if "stable_key" not in df.columns:
        return False, []
    
    duplicated = df[df["stable_key"].duplicated(keep=False)]
    if len(duplicated) == 0:
        return False, []
    
    collisions = []
    for key in duplicated["stable_key"].unique():
        rows = duplicated[duplicated["stable_key"] == key]
        collisions.append({
            "stable_key": key,
            "row_ids": rows["RowID"].tolist(),
            "count": len(rows),
        })
    
    return True, collisions
```

### 3. `io.py` — Modify normalize_columns()

In `src/fba_agent/io.py`, modify `normalize_columns()` to:
- Add `stable_key` column using `generate_stable_key()`
- Check for collisions at the end
- Raise `StableKeyCollisionError` if collisions found

Add after generating RowID:
```python
from fba_agent.stable_key import generate_stable_key, check_collisions, StableKeyCollisionError

# Inside normalize_columns(), after normalized DataFrame is created:
has_supplier_url = "SupplierURL" in df.columns
normalized["stable_key"] = normalized.apply(
    lambda row: generate_stable_key(row, has_supplier_url=has_supplier_url),
    axis=1
)

# Before returning:
has_collisions, collision_details = check_collisions(normalized)
if has_collisions:
    raise StableKeyCollisionError(collision_details)
```

### 4. `memory_store.py` — Expand with global traps + run_history

Add to `src/fba_agent/memory_store.py`:

```python
def load_global_traps(memory_dir: Path) -> list[dict]:
    """Load global trap library."""
    trap_path = memory_dir / "global" / "trap_library.jsonl"
    if not trap_path.exists():
        return []
    traps = []
    for line in trap_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            traps.append(json.loads(line))
    return traps

def load_run_history(memory_dir: Path, supplier_id: str, k: int = 2) -> list[dict]:
    """Load last K run history entries for a supplier."""
    history_path = memory_paths(memory_dir, supplier_id)["base"] / "run_history.json"
    if not history_path.exists():
        return []
    history = json.loads(history_path.read_text(encoding="utf-8"))
    return history[-k:] if len(history) > k else history

def persist_run_history(
    memory_dir: Path,
    supplier_id: str,
    run_entry: dict,
    max_entries: int = 10,
) -> None:
    """Append run entry to supplier history (keep last N)."""
    paths = memory_paths(memory_dir, supplier_id)
    paths["base"].mkdir(parents=True, exist_ok=True)
    history_path = paths["base"] / "run_history.json"
    
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = []
    
    history.append(run_entry)
    if len(history) > max_entries:
        history = history[-max_entries:]
    
    write_json_atomic(history_path, history)
```

Update `merge_calibration()` to implement correct precedence:
```python
def merge_calibration(
    supplier_id: str,
    memory_bundle: dict[str, Any],
    preflight_naming: SupplierNamingConvention,
    overrides_path: Path | None,
    global_traps: list[dict] | None = None,
) -> tuple[SupplierNamingConvention, dict[str, Any]]:
    """
    Merge calibration with strict precedence:
    1. defaults
    2. global traps (apply shield keywords)
    3. supplier calibration
    4. supplier traps
    5. user overrides (highest priority)
    """
    # Start with preflight as base (includes defaults)
    merged = preflight_naming.__dict__.copy()
    
    # Apply global traps (dimension/spec shields)
    if global_traps:
        for trap in global_traps:
            if trap.get("type") == "dimension_shield":
                existing = set(merged.get("dimension_shield_keywords", []))
                merged["dimension_shield_keywords"] = list(existing | set(trap.get("keywords", [])))
            elif trap.get("type") == "spec_x_shield":
                existing = set(merged.get("spec_x_shield_keywords", []))
                merged["spec_x_shield_keywords"] = list(existing | set(trap.get("keywords", [])))
    
    # Apply existing supplier calibration
    existing = (memory_bundle.get("calibration") or {}).get("config") or {}
    merged.update(existing)
    
    # Apply user overrides (from file)
    if overrides_path and overrides_path.exists():
        for line in overrides_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "SUPPLIER_NAMING_CONVENTION" in obj:
                naming_overrides = obj["SUPPLIER_NAMING_CONVENTION"]
                if isinstance(naming_overrides, dict):
                    merged.update(naming_overrides)
    
    naming = SupplierNamingConvention(**merged)
    diff = {
        "supplier_id": supplier_id,
        "preflight": preflight_naming.__dict__,
        "existing_calibration": existing,
        "global_traps_applied": len(global_traps or []),
        "merged": naming.__dict__,
        "precedence": "overrides > supplier traps > supplier calibration > global traps > defaults",
    }
    return naming, diff
```

### 5. `memory/global/trap_library.jsonl` — Create with defaults

Create `memory/global/trap_library.jsonl`:
```jsonl
{"type": "dimension_shield", "keywords": ["cm", "mm", "inch", "in", "m", "ft", "feet"]}
{"type": "spec_x_shield", "keywords": ["magnification", "zoom", "times", "led", "microscope", "scope"]}
{"type": "capacity_multipack", "units": ["ml", "l", "ltr", "g", "kg", "oz", "cl"]}
```

---

**⏹️ STOP CHECKPOINT 2a**

After completing Phase 2a:
1. Run existing tests: `pytest tests/` (should still pass)
2. Test stable_key generation on sample data
3. Verify no collisions on `part 4 jan.xlsx`
4. Verify global traps are loaded from `memory/global/trap_library.jsonl`

Report completion and any issues before proceeding to Phase 2b.

---

## PHASE 2b — VALIDATION + ANALYSIS ENHANCEMENTS

(Continue after Phase 2a checkpoint passes)

### 6. `validate.py` — Add stable_key coverage gate

### 7. `prefilter.py` — Create internal prefilter module

### 8. `anomalies.py` — Create outlier/cluster detection

### 9. `analysis.py` — Integrate stable_key + anomalies

---

## PHASE 2c — PROVIDERS + AI MODULES

(Continue after Phase 2b checkpoint passes)

### 10-13. `providers/` — Create unified provider interface

### 14. `adjudication.py` — AI row adjudication

### 15. `critique.py` — AI report critique

### 16. `adjustments.py` — Bounded adjustment application

---

## PHASE 2d — ITERATION + REGRESSION

(Continue after Phase 2c checkpoint passes)

### 17. `regression.py` — Regression guard

### 18. `iteration.py` — Iteration loop controller

### 19. `run.py` — Refactor to use iteration loop

### 20. `render.py` — DRAFT vs FINAL stamping + fix filename

---

## PHASE 2e — CLI + TESTS + DOCS

(Continue after Phase 2d checkpoint passes)

### 21. `cli.py` — Add vNext CLI flags

### 22. Tests — Create all vNext tests + golden dataset

### 23. Docs — spec_conflicts.md + README updates

---

# SAFETY RAILS

- **No schema drift:** Ledger columns must remain backward-compatible
- **No unbounded LLM rewrites:** AI outputs are suggestions only, never final
- **Hard gates must block:** Coverage/profit/stable_key failures = no finalization
- **Always emit justifications:** Any regression exception must be documented

---

# TEST PLAN

After each phase:
1. Run `pytest tests/` to verify no regressions
2. Run sample analysis: `python -m fba_agent analyze --input "path/to/part 4 jan.xlsx"`
3. Verify output artifacts match expected structure

---

# NEXT STEPS

**You are now ready to implement Phase 2a.**

1. Begin with step 1 (`types.py`) and proceed through step 5
2. After completing all 5 files, report completion
3. Run checkpoint tests
4. Wait for confirmation before proceeding to Phase 2b

**Begin implementation now with Phase 2a, Step 1: types.py**
