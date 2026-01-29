# PRD / Tech Spec — FBA Product Analysis Agent (Agents SDK, Kimi/Moonshot) — v1.0

**Status:** Phase 1 (Planning only — no code changes)  
**Timezone:** Asia/Dubai (UTC+4)  
**Primary outcome:** A production-grade, repeatable agent that analyzes supplier↔Amazon matched financial reports and generates a deterministic `CODEX_MANUAL_REPORT_MMDDHHMM.md` with **zero missed RowIDs** and reduced false positives.

---

## 1) Authoritative specs loaded (file-grounded)

These documents are treated as canonical for this build.

**Original locations (absolute paths):**
- Preflight calibration spec:  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md`
- Main report schema + validation checklist spec:  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md`
- Manual methodology (phases/decision trees/pitfalls):  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md`
- Execution wrapper (skip browser Phase 5):  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md`

**Local copies (for this build folder):**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\prompt_specs\MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md`

**Reference output example (format target):**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\codex 1\PHASEA_MANUAL_REPORT_20260104.md` (legacy example)

### 1.1 Conflict resolution order (practical mapping for this repo)

Your build prompt states the conflict order is: Main > Manual guide > Preflight.

In this repository, we map those as:
1. “Main” = `FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md` (schema + validation checklist + fixed-width rules)
2. “Manual guide” = `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md` (phases, traps, decision trees)
3. “Preflight” = `AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md` (supplier-specific calibration config)
4. Wrapper = `MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md` (coverage contract + skip Phase 5)

If any rule conflicts, we will follow (1) → (2) → (3), and record the decision in `calibration_diff.md` for that run.

---

## 2) Problem statement (why prompt-only is inconsistent)

Current manual prompting is inconsistent across chats because:
- “No missed rows” is a *process contract*, not enforced mechanically; rows can be silently skipped or duplicated across buckets.
- Confidence is currently “LLM vibes” and drifts run-to-run; the same evidence can yield different scores.
- Pack/variant traps (dimensions vs pack counts; “2x magnification”; “9 LED”; “N x 400ml” semantics; quantity-inside) are easy to misread without deterministic shields.
- Adjusted Profit can be recomputed inconsistently (NetProfit-based vs SellingPrice-based), changing verdicts.
- There is no durable memory of supplier naming conventions or previously approved overrides.

---

## 3) Goals and non-goals

### 3.1 Goals (hard requirements)

1. **Deterministic coverage:** every input RowID is accounted for exactly once, with a written audit trail.
2. **Deterministic scoring:** confidence is computed by code from explicit signals; LLM only assists extraction and explanation.
3. **Strict gates:** pack/variant/EAN/Adjusted Profit checks are enforced, including dimension/spec shields.
4. **Default skip browser:** Phase 5 (browser verification) is OFF by default; a stub interface exists for later.
5. **Output contract:** produce `CODEX_MANUAL_REPORT_MMDDHHMM.md` with the **exact table schema** and **fixed-width formatting rules** from the Main spec.
6. **Lightweight learning:** store per-supplier calibration/traps/overrides/brand aliases, merged deterministically.

### 3.2 Non-goals (MVP)

- Live web browsing, scraping, Keepa/SellerAmp lookups, or “real-time” verification.
- Model training or embeddings-based retrieval as a hard dependency.
- Automatic repricing or purchasing actions.

---

## 4) User stories (CLI-first)

1. As a user, I run `analyze` on a CSV/XLSX and get a complete PhaseA report + coverage ledger with no missed RowIDs.
2. As a user, I run `top` to see the strongest candidates (by deterministic confidence and upside).
3. As a user, I run `explain --rowid N` to see why a specific RowID landed in its bucket (evidence + gates + traps).
4. As a user, I run `rerun` with an overrides file to update decisions deterministically without losing auditability.
5. As a user, I want learning to persist per supplier so repeated reports become more consistent over time.

---

## 5) Inputs and outputs (contracts)

### 5.1 Input: financial report file

Supported formats:
- CSV (`.csv`)
- Excel (`.xlsx`)

Minimum expected columns (names may vary; normalization required):
- Row identity: `RowID` (or create from row index)
- Titles: `SupplierTitle`, `AmazonTitle`
- EANs: `EAN` (supplier), `EAN_OnPage` (Amazon) or equivalent
- `ASIN`
- Financials: `SupplierPrice_incVAT`, `SellingPrice_incVAT`, `NetProfit`, optional `ROI`, optional Sales column (`sales_numeric`, `bought_in_past_month`, or `Sales`)

### 5.2 Output: mandatory run artifacts

Every run writes a directory:
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\AGENT REPORT\<run_id>\`

Mandatory files:
1. `CODEX_MANUAL_REPORT_MMDDHHMM.md`
2. `coverage_ledger.csv` (exactly one row per RowID after normalization)
3. `evidence.jsonl` (one JSON object per RowID)
4. `run_summary.json` (counts, validation results, timing/cost if available)

Optional files:
- `review_queue.csv` (NEEDS_VERIFICATION only; sorted by upside)
- `merged_calibration.json`
- `calibration_diff.md`

### 5.3 PhaseA report structure + table schema (from Main spec)

All tables use the exact schema:
`| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |`

Formatting rules:
- Each table is emitted as **fixed-width, space-padded** rows so `|` aligns in a plain text editor.
- Wrap each table in a fenced code block: start ```text, end ```.
- No tabs; spaces only.
- Table safety: replace literal `|` with `/` and replace embedded newlines with spaces inside any cell before rendering.

---

## 6) System architecture (deterministic spine + agent orchestration)

### 6.1 Components

1. **CLI**: parses args, resolves input path, chooses supplier ID, creates `run_id`.
2. **Agent (Agents SDK)**: coordinates tool calls, composes explanations, and (optionally) proposes overrides.
3. **Deterministic tools** (code): own all parsing, scoring, bucketing, ledger validation, formatting, and file writes.
4. **Supplier memory store**: file-based memory under `memory/suppliers/<supplier_id>/...`.

### 6.2 Provider requirements (Moonshot / Kimi)

- Env var: `MOONSHOT_API_KEY`
- Base URL: `https://api.moonshot.ai/v1`

Implementation approach (Phase 2):
- Use OpenAI Agents SDK for orchestration.
- If direct provider wiring is awkward, route model calls via LiteLLM (Moonshot adapter) while keeping deterministic tools pure-Python.

---

## 7) Pipeline flow (end-to-end)

1. **Load report** (`load_report`)
2. **Normalize schema** (`normalize_columns`)
   - Ensure `RowID` exists and is contiguous/unique
   - Normalize money columns, Sales column, text fields
3. **Sample rows** (`sample_rows`, default 50)
4. **Preflight calibration** (`run_preflight`)
   - Produces `SUPPLIER_NAMING_CONVENTION` config block and warnings
5. **Load supplier memory** (`load_supplier_memory`)
6. **Merge calibration** (`merge_calibration`)
   - Precedence: `overrides` > existing calibration > new preflight > defaults
7. **Analyze all rows deterministically** (`analyze_all_rows`)
   - For each RowID: parse → traps → checks → adjusted profit → bucket + confidence → evidence record
8. **Validate ledger** (`validate_ledger`)
   - Coverage gate, profit gate, trap gates, format gates
9. **Render PhaseA report** (`render_phasea_report`)
10. **Write artifacts atomically** (`write_run_artifacts`)
11. **Persist learning** (`persist_supplier_memory`)

Browser verification tool stub exists but is disabled by default:
- `browser_verify(asin)` (no-op unless explicitly enabled)

---

## 8) Tool contracts and schemas (Phase 2 implementation targets)

All tools are deterministic (no network required) unless explicitly marked as “LLM-assisted”.

### 8.1 `load_report(input_path) -> (df, schema_info)`
- Reads CSV/XLSX.
- `schema_info` includes detected columns, dtype issues, row count, sales column guess, warnings.

### 8.2 `normalize_columns(df) -> (df, normalization_report)`
- Creates/repairs `RowID` if missing.
- Normalizes EAN columns:
  - Strip spaces, remove `.0` artifacts, keep digits only (store original in evidence).
- Normalizes Sales:
  - Parse `"100+ bought"` → numeric (store parsing note).

### 8.3 `sample_rows(df, n=50) -> rows`
- Stable selection strategy: first `n` rows after normalization (deterministic).

### 8.4 `run_preflight(rows) -> (preflight_config, warnings)` (LLM-assisted)
- Produces the config format defined in the preflight spec (`SUPPLIER_NAMING_CONVENTION`).
- Outputs concrete examples of traps found in sample.

### 8.5 `load_supplier_memory(supplier_id) -> memory_bundle`
File-based memory:
- `memory/suppliers/<supplier_id>/calibration.json`
- `memory/suppliers/<supplier_id>/trap_library.jsonl`
- `memory/suppliers/<supplier_id>/overrides.jsonl`
- `memory/suppliers/<supplier_id>/brand_aliases.json`

### 8.6 `merge_calibration(memory_bundle, preflight_config) -> (merged_config, diff_report)`
- Deterministic merge with precedence:
  - overrides > existing calibration > preflight > defaults
- Diff report written as Markdown (`calibration_diff.md`).

### 8.7 `analyze_row(row, merged_config) -> decision_record`
Deterministic outputs:
- `bucket`: one of `VERIFIED`, `HIGHLY_LIKELY`, `NEEDS_VERIFICATION`, `FILTERED_OUT`
- `unrelated_not_included`: boolean (for “UNRELATED / NOT INCLUDED” count and table exclusion)
- `confidence`: 0–100 integer (computed by code)
- `pack`: parsed supplier pack, amazon pack, pack ratio, RSU, pack verdict + trap flags
- `ean`: normalized supplier EAN, amazon EAN, strict validity, strict exact match
- `checks`: brand/product/variant/capacity/pack matches + deltas
- `adjusted_profit`: numeric (see §9.4), plus `profit_gate_pass`
- `key_match_evidence`: row-grounded tokens or strict exact EAN statement
- `filter_reason`: explicit, single-line reason (or `-`)

### 8.8 `analyze_all_rows(df, merged_config) -> (coverage_ledger_df, evidence_jsonl_iter)`
- Must not skip rows; must not duplicate RowIDs.

### 8.9 `validate_ledger(coverage_ledger_df, df) -> validation_result`
Hard failures if:
- Missing/duplicate RowIDs
- Any `adjusted_profit <= 0` row is in `VERIFIED/HIGHLY_LIKELY/NEEDS_VERIFICATION`
- Evidence integrity fails (evidence cites tokens not present in the row titles when not using strict EAN)
- Format constraints violated (pipes/newlines not sanitized; tables not fixed-width)

### 8.10 `render_phasea_report(coverage_ledger_df, metadata) -> markdown_str`
- Uses fixed-width tables in fenced ```text blocks.
- Never prints UNRELATED rows in tables (only as counts).

### 8.11 `write_run_artifacts(run_id, outputs) -> file_paths`
- Uses atomic write patterns (temp → replace).

### 8.12 `persist_supplier_memory(...)`
- Appends new traps and approved overrides.

---

## 9) Deterministic analysis rules

### 9.1 EAN normalization + strict validity

From Main spec acceptance tests:
- Only claim “Exact EAN match” when both are:
  - digits-only
  - plausible GTIN length (8/12/13/14)
  - checksum-valid where applicable
- If shorter than expected, attempt **left-padding** to 12/13/14 and re-validate checksum.
- If missing/invalid, output `-` in tables.

Deterministic implementation (Phase 2):
- `normalize_ean(raw) -> normalized_digits | None`
- `validate_gtin(normalized_digits) -> (is_valid, gtin_type, checksum_ok)`
- `strict_exact_ean = supplier_valid && amazon_valid && supplier_digits == amazon_digits`

### 9.2 Pack parsing + trap shields (must be code-driven)

Pack signals (from preflight + manual guide):
- Explicit units: `pcs/pce/pk/pack/unit`
- Trailing raw number quantity-inside (supplier-dependent)
- `N x <capacity>` means RSU = N (pack count), *not* `N*capacity`

Trap shields (never treat as pack counts):
- Dimension patterns: `9 x 9 inch`, `15 x 5.5 x 5.5 cm`, `280x115mm`
- Spec-x patterns: `2x magnification`, `3x zoom`, other feature multipliers
- Specification counts: `9 LED`

Quantity-inside logic:
- `(4 x 50)` may indicate total count 200 *if* it is quantity-inside (no measurement unit).

### 9.3 Capacity tolerance gates (from Main spec)

Capacity delta tiers (when comparing parsed capacities like `407ml` vs `408ml`):
- 0–10%: allow (note in evidence)
- 10–25%: NEEDS_VERIFICATION
- 25–50%: FILTERED_OUT (different SKU)
- >50%: FILTERED_OUT (completely different product)

### 9.4 Adjusted Profit (deterministic)

Preferred method (if `NetProfit` exists in input):
- If `amazon_pack > supplier_pack`:
  - `pack_ratio = amazon_pack / supplier_pack`
  - `adjusted_profit = net_profit - supplier_price * (pack_ratio - 1)`
- If `amazon_pack == supplier_pack`: `adjusted_profit = net_profit`
- If `supplier_pack > amazon_pack`: treat as split-candidate; do not auto-adjust profit; route to NEEDS_VERIFICATION unless override.

Fallback method (if `NetProfit` missing):
- Estimate fees as `selling_price * fee_rate` (default `0.30`, configurable).
- `adjusted_profit = selling_price - (supplier_price * pack_ratio) - estimated_fees`

Profit gate (hard):
- If `adjusted_profit <= 0`, bucket must be `FILTERED_OUT` (and included in FILTERED OUT table if match is confirmed).

### 9.5 Bucket decision policy (deterministic)

We will preserve both the “4-bucket contract” (for tooling) and the “UNRELATED / NOT INCLUDED” reporting semantics (for the PhaseA report):

- `bucket` is always one of:
  - `VERIFIED`, `HIGHLY_LIKELY`, `NEEDS_VERIFICATION`, `FILTERED_OUT`
- Additionally:
  - `unrelated_not_included = true` indicates “UNRELATED / NOT INCLUDED” (not printed in tables, count-only)
  - `filtered_out_kind` distinguishes:
    - `CONFIRMED_UNPROFITABLE` / `CONFIRMED_VARIANT_MISMATCH` / `CONFIRMED_PACK_MISMATCH` / `UNRELATED_NOT_INCLUDED`

Decision logic (high level):
- **VERIFIED**
  - `strict_exact_ean == true`
  - no confirmed pack/variant contradiction (dimension/spec shields applied)
  - `adjusted_profit > 0`
- **HIGHLY_LIKELY**
  - strict EAN not available/mismatch
  - strong brand + product-type anchors match
  - variant within tolerance (capacity gates applied)
  - pack not contradicted (or pack evidence supports)
  - `adjusted_profit > 0`
- **NEEDS_VERIFICATION**
  - strong match potential but 1–2 blockers:
    - pack ambiguity, possible variant mismatch, EAN mismatch needing confirmation, or split-candidate (supplier pack > amazon pack)
  - `adjusted_profit > 0` (or “profit unknown” if missing data; configurable)
- **FILTERED_OUT**
  - confirmed mismatch (variant/product-type), or adjusted profit <= 0 after required pack adjustment, or other explicit contradiction
  - if the row is weak/contradictory such that it’s not a confirmed match: set `unrelated_not_included = true` and exclude from tables.

---

## 10) Deterministic confidence scoring rubric (code-driven)

### 10.1 Core principles

From Main spec:
- Exact-EAN rows: default `Confidence = 95`, downgrade only on meaningful ambiguity/contradiction.
- Non-EAN rows: confidence reflects match likelihood from title analysis and pack/variant evidence.

### 10.2 Base scores by bucket (defaults)

These base scores are consistent with the Main spec’s “Exact-EAN defaults to 95” policy and keep scoring stable run-to-run.

| Bucket | Base score | Typical range intent |
|--------|------------|----------------------|
| VERIFIED (exact EAN) | 95 | 85–95 (downgrade only) |
| HIGHLY_LIKELY | 80 | 70–90 |
| NEEDS_VERIFICATION | 60 | 40–79 |
| FILTERED_OUT | (computed) | “would-have-been” score |

### 10.3 Evidence weighting (deterministic features)

These weights are used by the scoring function (LLM does not set the score).

| Evidence type | Effect (default) |
|---------------|------------------|
| Strict exact EAN match | VERIFIED track (score starts at 95) |
| Brand match (case-insensitive / alias) | +35 (non-EAN path) |
| Product-type anchors match | +25 (non-EAN path) |
| Variant match within tolerance | +15 |
| Pack match evidence (1:1 or resolved) | +10 |
| Capacity within 0–10% | +5 |
| Missing Amazon EAN (not different) | +2 |

### 10.4 Proposed scoring (MVP)

Confidence is computed deterministically as an integer 0–100 from explicit signals:

**Exact-EAN base path**
- Start: `95`
- Penalties:
  - `-10` if pack parsing indicates mismatch and is not resolved by dimension/spec shields
  - `-10` if capacity delta is 10-25% (route likely to NEEDS_VERIFICATION anyway)
  - `-20` if any confirmed variant contradiction exists (route to FILTERED_OUT)
- Floor/ceiling:
  - Clamp to `[0, 100]`

**Non-EAN base path**
- Start: `0`
- Additive points:
  - `+35` strong brand match (exact or alias match)
  - `+25` product-type anchor match
  - `+15` variant match within tolerance (capacity/color/scent/model)
  - `+10` pack match evidence (or `N x capacity` resolved correctly)
  - `+5` sales signal present (non-zero)
- Penalties:
  - `-20` pack ambiguity (route to NEEDS_VERIFICATION)
  - `-30` capacity delta 10–25% (route to NEEDS_VERIFICATION)
  - `-60` capacity delta >25% (route to FILTERED_OUT)
  - `-60` confirmed product-type mismatch (route to FILTERED_OUT)
- Clamp to `[0, 100]`

Confidence-to-bucket thresholds (deterministic defaults; adjustable per supplier):
- VERIFIED: must satisfy VERIFIED gates (score is informational; typical ≥85)
- HIGHLY_LIKELY: score ≥80 and gates pass
- NEEDS_VERIFICATION: score 50–79 and gates pass
- FILTERED_OUT: otherwise, or profit gate fails, or mismatch confirmed

### 10.5 Scoring pseudocode (implementation reference)

```python
def compute_confidence(record) -> int:
    if record.strict_exact_ean:
        score = 95
        if record.traps_applied:
            score -= 1
        if record.capacity_delta_pct is not None and record.capacity_delta_pct > 5:
            score -= 2
        if record.pack_ratio is not None and record.pack_ratio > 1 and record.adjusted_profit < 5:
            score -= 2
        return clamp(score, 85, 95)

    score = 0
    score += 35 if record.brand_match else 0
    score += 25 if record.product_type_match else 0
    score += 15 if record.variant_within_tolerance else 0
    score += 10 if record.pack_match_evidence else 0
    score += 5 if record.sales_numeric and record.sales_numeric > 0 else 0
    score += 2 if record.amazon_ean_missing else 0

    if record.pack_ambiguous:
        score -= 20
    if record.capacity_gate == "10_25":
        score -= 30
    if record.capacity_gate in {"25_50", "gt_50"}:
        score -= 60
    if record.confirmed_product_type_mismatch:
        score -= 60
    return clamp(score, 0, 100)
```

---

## 11) Learning / memory design (lightweight, file-based)

### 11.1 What is stored

Per supplier:
- `calibration.json`: merged `SUPPLIER_NAMING_CONVENTION` plus derived defaults
- `trap_library.jsonl`: appended trap examples with correct interpretation
- `overrides.jsonl`: user-approved overrides (pack rules, split allowances, known safe brands)
- `brand_aliases.json`: alias mappings seen repeatedly

### 11.2 Merge precedence (hard rule)

`overrides` > `existing calibration` > `new preflight inference` > defaults

### 11.3 Lifecycle

On each run:
1. Load memory (if any)
2. Run preflight (always)
3. Merge deterministically + record diff
4. During analysis, collect “candidate traps” (not auto-trusted)
5. Only persist to overrides when explicitly approved (via `rerun --apply-overrides`)

---

## 12) Validation gates & failure handling

Hard-fail gates:
1. **Coverage gate:** ledger has exactly N rows (N = normalized input rows), no missing, no duplicates.
2. **Profit gate:** any row with `adjusted_profit <= 0` must not be in VERIFIED/HIGHLY_LIKELY/NEEDS_VERIFICATION.
3. **Trap gates:** dimension/spec shields must prevent RSU inflation from size/spec numbers.
4. **Evidence integrity gate:** evidence cites only tokens present in the row titles (or strict exact EAN).
5. **Output formatting gate:** fixed-width tables, sanitized pipes/newlines, correct schema.

Failure handling:
- Fail fast with a clear error message and write `run_summary.json` with `status="FAILED"` + gate details.
- Never output a partial report that silently omits rows.

### 12.1 Severity model (hard vs soft fail)

- **Hard fail:** coverage gate, profit gate, strict format/schema gate, fatal I/O errors.
  - Action: stop; write `run_summary.json` with failure detail; do not write a partial PhaseA report.
- **Soft fail (warning):** “quality” gates that indicate drift but not corruption (e.g., trap-rate spikes, unusual distribution, low evidence density).
  - Action: still write artifacts, but include warnings in `run_summary.json` and optionally a short “Warnings” section in the report header.

---

## 13) Test plan (mandatory for Phase 2)

### 13.1 Unit tests (deterministic)

- EAN normalization + checksum validation + left-padding
- Pack parsing:
  - `N x capacity` RSU rule
  - dimension shield patterns
  - spec-x shield patterns (e.g., magnification)
  - `X LED` shield
  - quantity-inside patterns `(4 x 50)`
- Adjusted profit computation:
  - NetProfit-based adjustment
  - selling-price fallback

### 13.2 Regression tests (golden dataset)

- A small curated CSV/XLSX with known outcomes (buckets + confidence + adjusted profit).
- Tests assert stable outputs across runs (no drift unless overrides changed).

### 13.3 Evaluation metrics (targets)

| Metric | Target |
|--------|--------|
| Coverage | 100% (no missing/duplicate RowIDs) |
| Bucket stability (same input, no overrides) | 0 bucket changes |
| Score stability (same input, no overrides) | ±2 points max |
| False positives (VERIFIED/HIGHLY_LIKELY later overturned) | <5% |
| Miss rate (valid matches that should have been higher bucket) | <10% |

---

## 14) Implementation milestones (Phase 2 plan)

MVP (Phase 2):
1. Repo scaffold: `src/fba_agent/`, `tests/`, `AGENT REPORT/`, `memory/`, `docs/`
2. Deterministic core tools (load/normalize/parse/score/bucket/validate/render/write)
3. Agents SDK orchestration + Moonshot provider wiring (LiteLLM if needed)
4. CLI commands: `analyze`, `top`, `explain`, `export`, `rerun`, `list-runs`, `show-memory`
5. Unit tests + golden dataset regression tests
6. Docs: `README.md`, `.env.example`, `docs/examples/`

V2:
- Optional Streamlit UI or CLI REPL mode
- Browser verify tool implementation (Phase 5) behind a feature flag
- Better supplier auto-detection (domain inference + heuristics)

---

## 15) Risks and mitigations

- **Model/provider quirks (Moonshot):** mitigate by keeping logic deterministic; LLM only for preflight + explanations.
- **Input schema variance:** mitigate with robust column normalization + schema warnings.
- **Pack parsing edge cases:** mitigate with trap library + conservative “NEEDS_VERIFICATION” routing.
- **Performance on large files:** mitigate with streaming JSONL evidence writing + vector-free matching.
- **Bucket semantics drift (UNRELATED vs FILTERED OUT):** mitigate by representing "unrelated" as `unrelated_not_included=true` (count-only) while keeping 4-bucket contract.

---

## 16) Conflict resolution log (Phase 1)

| Topic | Options observed | Resolution | Rationale |
|-------|------------------|------------|-----------|
| UNRELATED vs 4-bucket contract | Wrapper/methodology includes “UNRELATED / NOT INCLUDED” as count-only; build prompt lists 4 buckets | Keep 4 buckets for tools + `unrelated_not_included=true` flag | Satisfies deterministic tool contract while preserving the PhaseA report’s “don’t print unrelated rows” rule |

---

## Approval request (end of Phase 1)

If this PRD/Tech Spec matches your intended workflow and the canonical prompt specs, approve Phase 2 and tell me:
1. Which input files you want as the initial golden dataset (paths), and
2. Whether you want `UNRELATED / NOT INCLUDED` represented as a separate bucket internally (5 buckets) or as `unrelated_not_included=true` under the 4-bucket contract (as specified above).
