# FBA Analysis Agent vNext — Phase 1 PRD & Technical Specification

**Version:** vNext Phase 1  
**Date:** 2026-01-04  
**Status:** DRAFT — Awaiting Approval  
**Timezone:** Asia/Dubai (UTC+4)

---

## PART A: AUDIT NOTES (Current State Assessment)

### 1.1 Preflight Persistence — ❌ MISSING

**Current State:**
- `opus_agent/src/fba_agent/agent.py` → `_get_calibration()` (line 260-264) returns a **default static calibration**:
  ```python
  def _get_calibration(self, supplier_id: str, df) -> Dict[str, Any]:
      # For MVP, return default calibration
      # V2 will load from memory and run preflight
      return SupplierCalibration(supplier_id=supplier_id).to_dict()
  ```
- `opus_agent/memory/suppliers/` directory **exists but is empty**.
- **NO code path** currently:
  - Loads prior calibration from disk
  - Runs new preflight via LLM
  - Merges calibration with precedence rules
  - Writes merged calibration back to disk

**Action Required:** Implement full preflight persistence lifecycle.

---

### 1.2 "Filtered Out" Semantics — ⚠️ PARTIALLY CORRECT

**Current State:**
- `categorization.py` correctly distinguishes between FILTERED_OUT and weak-evidence rows.
- The `categorize_row()` function routes negative-profit matches to FILTERED_OUT with explicit reasons.
- **Issue:** There is no explicit `UNRELATED` bucket tracking. Weak-evidence rows are currently routed to `NEEDS_VERIFICATION` with "weak evidence" notes, which conflates two semantically different cases.

**Per Main.txt Spec:**
- **UNRELATED / NOT INCLUDED:** Clear non-matches — MUST NOT be printed in tables.
- **FILTERED OUT:** Confirmed matches excluded for specific reasons — MUST be printed in tables.

**Current Behavior:**
- Weak-evidence rows go to `NEEDS_VERIFICATION`, not silently dropped (good).
- But there's no count/tracking of truly unrelated rows (missing).

**Action Required:** Add explicit `UNRELATED` tracking (count-only, not in tables) and ensure FILTERED_OUT contains only confirmed matches.

---

### 1.3 Row Coverage Contract — ✅ CORRECT

**Current State:**
- `validation.py` → `validate_coverage()` (lines 43-89) correctly:
  - Checks for missing RowIDs
  - Checks for duplicate RowIDs
  - Returns `ValidationResult` with `passed=False` if either condition fails
- `agent.py` → `analyze()` raises `RuntimeError` if coverage or profit gates fail (lines 129-137).

**Contract is enforced:** Every row is accounted for; no silent skipping.

---

### 1.4 Pre-filter Support — ❌ MISSING

**Current State:**
- The pipeline processes whatever file is provided.
- There is **no mechanism** to:
  - Load a "full" report and apply pre-filters internally
  - Report `prefilter_excluded_count` and `prefilter_rules_used`

**Action Required:** Add optional pre-filter logic with explicit tracking.

---

## PART B: PROBLEM STATEMENT

### Why Prompt-Only is Inconsistent
1. **Score Drift:** Same row can score 75 or 85 depending on LLM "mood".
2. **Coverage Gaps:** Rows silently dropped in long chats.
3. **Trap Susceptibility:** "9x9 inch" read as "81-pack" without shields.
4. **No Memory:** Supplier patterns re-learned every run.

### What vNext Solves
- **Deterministic spine** for obvious cases (EAN Match → VERIFIED).
- **Bounded AI** for ambiguous cases (Adjudication Queue).
- **Iterative Refinement** with regression guard (don't make it worse).
- **Historical Comparison** (detect drift vs previous runs).

---

## PART C: TECHNICAL SPECIFICATION

---

### 3.1 Iteration Loop Design

```
┌─────────────────────────────────────────────────────────────┐
│                      RUN ORCHESTRATOR                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐  fail/incomplete  ┌──────────────┐      │
│   │  ITERATION 1 │ ──────────────────▶│  ITERATION 2 │      │
│   │  (Baseline)  │                    │  (Refined)   │      │
│   └──────────────┘                    └──────────────┘      │
│          │                                   │              │
│          ▼                                   ▼              │
│   ┌──────────────┐                    ┌──────────────┐      │
│   │   VALIDATE   │                    │   VALIDATE   │      │
│   │   + CRITIQUE │                    │   + COMPARE  │      │
│   └──────────────┘                    └──────────────┘      │
│          │                                   │              │
│          └───────────┐   ┌───────────────────┘              │
│                      ▼   ▼                                  │
│              ┌───────────────────┐                          │
│              │  REGRESSION GUARD │                          │
│              │  (Historical Diff)│                          │
│              └───────────────────┘                          │
│                      │                                      │
│                      ▼                                      │
│              ┌───────────────────┐                          │
│              │   FINALIZE BEST   │                          │
│              │   ITERATION       │                          │
│              └───────────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Iteration Trigger Rules:**
- Iteration 2 runs if Iteration 1 has:
  - Any hard gate failure that is correctable
  - Large anomaly signals (>10 outliers, >5% bucket flip)
  - Regression guard detects >10% "good-to-bad" transitions vs history
  - Critique identifies safe rule additions

**Stop Conditions:**
- All hard gates pass
- Regression guard says "not worse"
- Critique has no high-severity unresolved issues
- Max iterations (default 2) reached

---

### 3.2 Stable Key Strategy

**Problem:** `RowID` is not stable across file regenerations.

**Solution:** Generate a hash-based stable key:

```python
import hashlib

def compute_stable_key(row: Dict) -> str:
    """Generate stable key for cross-run comparison."""
    # Prefer SupplierURL if available (unique per product)
    if row.get("SupplierURL"):
        base = f"{row['SupplierURL']}|{row.get('ASIN', '')}"
    else:
        # Fallback to content hash
        base = "|".join([
            str(row.get("EAN", "")).strip(),
            str(row.get("ASIN", "")).strip(),
            str(row.get("SupplierTitle", ""))[:50].lower(),
            str(row.get("AmazonTitle", ""))[:50].lower()
        ])
    return hashlib.sha256(base.encode()).hexdigest()[:16]
```

**Storage:** Add `stable_key` column to `coverage_ledger.csv`.

---

### 3.3 AI Logic Integration Points

#### AI Step A: Targeted Row Adjudication

**Selector Logic:**
```python
def select_adjudication_candidates(records: List[RowDecisionRecord], cap: int = 200) -> List[RowDecisionRecord]:
    """Select rows that need AI adjudication."""
    candidates = []
    for r in records:
        if should_adjudicate(r):
            candidates.append(r)
        if len(candidates) >= cap:
            break
    return candidates

def should_adjudicate(r: RowDecisionRecord) -> bool:
    """Determine if row needs AI review."""
    # Pack ambiguity
    if r.pack_verdict and "uncertain" in r.pack_verdict.lower():
        return True
    # Variant ambiguity
    if r.match_checks.variant_match == "ambiguous":
        return True
    # EAN missing but strong title
    if not r.match_checks.is_exact_ean_strict and r.confidence > 60:
        return True
    # High profit outlier with weak match
    if r.adjusted_profit > 50 and r.confidence < 70:
        return True
    return False
```

**AI Output Schema:**
```json
{
  "row_id": 123,
  "extracted_signals": {
    "supplier_brand": "AMTECH",
    "amazon_brand": "Amtech",
    "supplier_product_type": "trowel",
    "amazon_product_type": "trowel",
    "supplier_pack": 1,
    "amazon_pack": 1,
    "supplier_capacity": "N/A",
    "amazon_capacity": "N/A"
  },
  "trap_detections": [
    {"type": "dimension_shield", "pattern": "9x9 inch", "action": "ignored as dimension"}
  ],
  "recommended_bucket": "HIGHLY_LIKELY",
  "confidence_suggestion": 85,
  "reasoning": "Brand match (case-insensitive), product type match, no pack contradiction."
}
```

**Constraint:** AI confidence is a SUGGESTION. Deterministic scoring is final.

---

#### AI Step B: Report Critique

**Input to Critique:**
- Bucket counts
- Validation results
- Top 20 anomalies (profit outliers, title mismatches)
- Sample rows (20 per bucket)
- Regression diff summary

**Critique Output Schema:**
```json
{
  "high_severity_issues": [
    {
      "issue_id": "HSI_001",
      "description": "5 rows with RSU>10 but no dimension trap detected",
      "affected_rows": [123, 456, 789],
      "suggested_resolution": "Add trap pattern for 'LED' as spec keyword"
    }
  ],
  "proposed_changes": [
    {
      "change_type": "add_shield_token",
      "target": "spec_x_shield_keywords",
      "value": "LED",
      "safe_to_apply": true
    },
    {
      "change_type": "adjust_threshold",
      "target": "capacity_tolerance_verified",
      "current": 0.10,
      "proposed": 0.12,
      "safe_to_apply": false
    }
  ],
  "overall_assessment": "Minor issues detected. Safe to finalize after applying 1 shield token."
}
```

**Constraint:** Only `safe_to_apply: true` changes are auto-applied. Others require manual approval.

---

### 3.4 Regression Guard

**Comparison Matrix:**
```
                    CURRENT RUN
                    VER  HL   NV   FO   UNR
HISTORICAL  VER     ✓    ⚠️   ⚠️   ❌   ❌
RUN         HL      ✓    ✓    ⚠️   ⚠️   ❌
            NV      ✓    ✓    ✓    ⚠️   ⚠️
            FO      ⚠️   ⚠️   ⚠️   ✓    ⚠️
            UNR     ⚠️   ⚠️   ⚠️   ⚠️   ✓

✓ = Good (same or better)
⚠️ = Warning (may need justification)
❌ = Blocked (requires explicit justification)
```

**Blocking Thresholds (default):**
- Missing stable keys: > 0 (HARD BLOCK)
- Good-to-bad transitions: > 10% of previously-good OR > 30 rows
- Unexplained bucket changes: > 5% of total

**Justification File:** `regression_justifications.jsonl`
```jsonl
{"stable_key": "a1b2c3d4", "from": "VERIFIED", "to": "FILTERED_OUT", "reason": "RSU=4 makes profit negative after pack correction", "justified": true}
```

---

### 3.5 Memory Layout

```
memory/
├── global/
│   └── trap_library.jsonl          # Universal traps
└── suppliers/
    └── {supplier_id}/
        ├── calibration.json        # Merged preflight config
        ├── trap_library.jsonl      # Supplier-specific traps
        ├── overrides.jsonl         # User-approved overrides
        ├── brand_aliases.json      # Known brand aliases
        └── run_history.json        # Last K run pointers
```

**Merge Precedence:**
1. User overrides (highest)
2. Supplier-specific traps/calibration
3. Global traps
4. Defaults (lowest)

---

### 3.6 Provider Configuration

**Environment Variables:**
```bash
# OpenAI (default)
OPENAI_API_KEY=sk-...

# Gemini (OpenAI-compatible endpoint)
GEMINI_API_KEY=...
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# Moonshot/Kimi
MOONSHOT_API_KEY=...
MOONSHOT_BASE_URL=https://api.moonshot.ai/v1
```

**CLI Flags:**
```bash
--provider {openai|gemini|moonshot}
--model-small <name>        # Default: gpt-4o-mini / gemini-2.0-flash
--model-large <name>        # Default: gpt-4o / gemini-2.0-pro
--max-escalations 2         # Max model escalations per run
```

---

### 3.7 Output Artifacts

```
runs/
└── {run_id}/
    ├── iter_1/
    │   ├── coverage_ledger.csv
    │   ├── evidence.jsonl
    │   ├── run_summary.json
    │   ├── config_applied.json
    │   └── critique.json
    ├── iter_2/
    │   ├── coverage_ledger.csv
    │   ├── evidence.jsonl
    │   ├── run_summary.json
    │   ├── config_applied.json
    │   ├── critique.json
    │   └── regression_diff.json
    └── final/
        ├── CODEX_MANUAL_REPORT_{MMDDHHMM}.md
        ├── coverage_ledger.csv
        ├── evidence.jsonl
        ├── run_summary.json
        ├── FINAL_SUMMARY.md
        └── REGRESSION_JUSTIFICATIONS.jsonl
```

---

### 3.8 CLI Interface

```bash
# Basic run
python -m fba_agent analyze \
  --input "path/to/report.xlsx" \
  --supplier "efghousewares" \
  --max-iterations 2

# With provider selection
python -m fba_agent analyze \
  --input "path/to/report.xlsx" \
  --supplier "efghousewares" \
  --provider openai \
  --model-small gpt-4o-mini \
  --model-large gpt-4o

# With historical comparison
python -m fba_agent analyze \
  --input "path/to/report.xlsx" \
  --supplier "efghousewares" \
  --history-k 2

# Explain a specific row
python -m fba_agent explain \
  --run-id "20260104_153045" \
  --rowid 626
```

---

## PART D: IMPLEMENTATION CHECKLIST

### Phase 2a — Core Framework (Must Do First)

| # | File | Change |
|---|------|--------|
| 1 | `tools/stable_key.py` | **NEW** — Implement `compute_stable_key()` |
| 2 | `tools/data_loading.py` | Add `stable_key` column generation |
| 3 | `models/schemas.py` | Add `stable_key` field to `RowDecisionRecord` |
| 4 | `core/memory.py` | **NEW** — Implement full memory manager (load/save/merge) |
| 5 | `core/preflight.py` | **NEW** — Implement LLM-assisted preflight with persistence |
| 6 | `agent.py` | Integrate memory + preflight lifecycle |

### Phase 2b — Iteration Engine

| # | File | Change |
|---|------|--------|
| 7 | `core/iteration.py` | **NEW** — Implement iteration loop controller |
| 8 | `core/regression.py` | **NEW** — Implement regression guard + diff logic |
| 9 | `tools/validation.py` | Add iteration-aware validation (soft vs hard) |
| 10 | `agent.py` | Integrate iteration loop |

### Phase 2c — AI Logic

| # | File | Change |
|---|------|--------|
| 11 | `tools/adjudication.py` | **NEW** — Implement row adjudication selector + LLM call |
| 12 | `tools/critique.py` | **NEW** — Implement report critique step |
| 13 | `core/provider.py` | **NEW** — Implement multi-provider support (OpenAI/Gemini/Moonshot) |
| 14 | `core/escalation.py` | **NEW** — Implement model escalation logic |

### Phase 2d — Output & CLI

| # | File | Change |
|---|------|--------|
| 15 | `tools/output.py` | Update for iteration-based folder structure |
| 16 | `cli.py` | Add new flags: `--max-iterations`, `--history-k`, `--provider`, etc. |
| 17 | `tools/reporting.py` | Add `FINAL_SUMMARY.md` generation |

### Phase 2e — Testing

| # | File | Change |
|---|------|--------|
| 18 | `tests/test_stable_key.py` | **NEW** — Stable key generation tests |
| 19 | `tests/test_regression.py` | **NEW** — Regression guard tests |
| 20 | `tests/golden_dataset.csv` | **NEW** — 50-100 row curated test set |
| 21 | `tests/test_iteration.py` | **NEW** — Iteration selection tests |

---

## PART E: ACCEPTANCE CRITERIA

| Gate | Description | Pass Condition |
|------|-------------|----------------|
| G1 | Coverage | 100% rows accounted (no missing/duplicates) |
| G2 | Profit | No positive bucket with AdjustedProfit ≤ 0 |
| G3 | Stable Keys | All rows have stable_key; no collisions |
| G4 | Iteration | Final iteration is not worse than iter_1 |
| G5 | Regression | Good-to-bad transitions < threshold |
| G6 | Format | Report matches Main.txt schema exactly |

---

## APPROVAL REQUEST

**Phase 1 is complete.**

I have:
1. Audited the current codebase
2. Identified gaps (preflight persistence, UNRELATED tracking, pre-filter support)
3. Designed the iteration loop, regression guard, and AI integration
4. Specified memory layout and provider support
5. Created a detailed implementation checklist

**Please review and approve to proceed to Phase 2 (Implementation).**

If you have questions or want changes to the spec, let me know.
