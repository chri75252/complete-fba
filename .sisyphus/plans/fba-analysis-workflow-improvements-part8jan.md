# FBA Analysis Workflow Improvements (Part 8 Jan)

## TL;DR

This report proposes workflow + prompt + agent-skill improvements to reduce **false positives** in `HIGHLY LIKELY` and `NEEDS VERIFICATION`, while preserving recall.

Core fix: introduce a **two-pass gate**:
1) **Automated structural gates** (pack/size/variant sanity, profit sanity, measurement shield) 
2) **Manual reasoning gate** only for survivors, with strict evidence rules.

This directly addresses observed issues where other agents “found more” by being overly permissive, while our pipeline still let some invalid rows through.

---

## Context (What we observed)

### Inputs used
- Preflight prompt: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\finale\AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2_patched (1).md`
- Analysis prompt: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\finale\FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2_AUDITED_OUT_v5 (1).md`
- Manual guide: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\finale\MANUAL_GUIDE_UPDATED_v1.1.5_PATCHED.md`
- Our execution artifacts:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\OC\finan ana\financial_analysis.py`
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\OC\finan ana\PHASEA_MANUAL_REPORT_2601310829_VALIDATED.md`

### User feedback to incorporate
- “Most of the Highly Likely + Needs Verification rows were not valid anyway.”
- “Other agents found more rows, but they may be just additional rows, not valid matches.”

So improvements must prioritize **precision** and **reducing junk**, not just increasing counts.

---

## Failure Modes (Root Causes)

### FM1 — HIGHLY LIKELY inflation due to weak brand/token logic
In `financial_analysis.py`, brand matching defaults to “first token” and treats many generic first tokens as “brands” (e.g., `HAPPY`, `WORLD`, `DOG`, `FIRST`). This is a major false-positive driver.

**Impact:** Many rows qualify as “brand match” when it’s just a generic descriptor.

### FM2 — Variant/size mismatch not aggressively gated
The analysis prompt requires careful treatment of:
- Capacity/size mismatch thresholds
- Variant traps (size/color/version)

In practice, “strong anchors” were over-weighted, and mismatched sizes slipped into `HIGHLY LIKELY`.

Example pattern:
- Supplier: `3KG`
- Amazon: `6KG`

Even when both appear, some reports still classify as `HIGHLY LIKELY`.

### FM3 — Pack parsing / measurement shield errors (dimension trap)
Even with shield keywords, “N x M” patterns are still error-prone:
- Dimensions like `15 x 5.5 x 5.5 cm` must never become RSU.
- Our tooling uses keyword presence; but context windowing can still misclassify.

### FM4 — Profit sanity not used as a hard gate early enough
The analysis prompt explicitly states:
- Items with `Adjusted Profit ≤ 0` must be audited out.

But we still saw cases where negative adjusted profit or absurd RSU behavior can appear in actionable buckets when the parsing fails upstream.

### FM5 — Step 3 “Review Mode” cannot scale to 249 rows honestly
The Manual Guide says “manually adjudicate row-by-row.” This is costly and prone to “claimed review” vs “actual review”.

We need a hybrid approach:
- automated spot-check sampling + anomaly detection
- targeted human review on the highest-risk rows

---

## Improvement Goals (Measurable)

1) Reduce `HIGHLY LIKELY` false positives by **50%+** (measured by manual audit sample).
2) Reduce `NEEDS VERIFICATION` junk by **50%+** by improving gating.
3) Preserve recall on truly good matches (don’t lose clear brand+model matches).
4) Make Step 3 verification **verifiable** (audit log + sampling protocol).

---

## Proposed Workflow Changes (High Impact)

### W1 — Introduce explicit “JUNK” gate before categorization
Add an intermediate bucket (internal only): `REJECTED_WEAK_MATCH`.

Rules to reject (before HL/NV):
- Brand token is generic/stopword-like (see W2)
- No unique anchor (model/series token) AND title similarity below threshold
- Product-type noun mismatch (simple noun whitelist per domain)
- Size/capacity conflict > 25% (route to NV or reject depending on severity)

### W2 — Brand extraction overhaul (critical)
Replace “first token” as brand with a calibrated brand extractor:

**Brand extraction rules:**
- Maintain a `KNOWN_BRANDS` set learned from supplier catalog (top-N tokens that repeat as first token AND also appear in Amazon titles)
- Maintain a `GENERIC_FIRST_TOKENS` denylist (e.g., HAPPY, WORLD, DOG, FIRST, KITCHEN, HOME, ROUND, WHITE, BLACK, RED)
- Only treat brand match as positive evidence if:
  - supplier brand ∈ KNOWN_BRANDS AND
  - supplier brand appears in Amazon title (any position)

If supplier brand is unknown → treat as “brand missing/unknown”, not “brand match”.

### W3 — Size/capacity/quantity consistency gate
Before labeling HL:
- Parse **all numeric+unit tokens** (kg/g/ml/l/cm/mm/inch) from both titles
- Apply the prompt’s tolerance rules:
  - 0–10% → OK
  - 10–25% → NV
  - 25–50% → audit out / excluded
  - >50% → audit out / excluded

If units differ (kg vs ml) → reject.

### W4 — Pack parsing hardening
Split pack parsing into:
1) `explicit_pack_count` (pack of N / N pack / Npk / Npcs)
2) `multipack_structure` (N x M)
3) `dimension_structure` (A x B x C with units)

Hard rule:
- If 3 numbers exist in close proximity with `cm/mm/inch` → treat as dimensions, RSU=1.

### W5 — Profit sanity hard gate
Enforce early and late:
- If `Adjusted Profit ≤ 0` → cannot be in VERIFIED/HIGHLY LIKELY.
- If RSU is absurd (e.g., RSU>20) and no explicit pack evidence → route to NV with “RSU anomaly” reason.

### W6 — Step 3 verification becomes sampling-based + anomaly-driven
Instead of claiming full row-by-row review:
- Run stratified sample audit:
  - 10 VERIFIED, 20 HL, 20 NV (random)
- Run anomaly audit:
  - all rows where size conflict detected
  - all rows where RSU>3
  - all rows where brand is generic/unknown

Report output must include:
- sample size
- error rate
- list of corrected rows

---

## Prompt Improvements

### P1 — Update HIGHLY LIKELY definition to disallow “generic brand tokens”
In the analysis prompt, add:
- “Do not treat generic adjectives/nouns as brand evidence.”
- Provide examples: HAPPY, WORLD, DOG, FIRST, KITCHEN.

### P2 — Add mandatory size/weight conflict checklist row field
Add output column (optional) for internal QA:
- `Size Verdict`: OK / NV / AUDIT OUT

Or require it in “Filter Reason” when numeric units appear.

### P3 — Clarify that “more rows” is not better
Add an explicit instruction:
- “Do not maximize counts. Prefer rejecting weak matches to keep NV clean.”

### P4 — Strengthen “unique anchor” requirement
Currently “unique anchor” is underspecified.
Add examples of what counts:
- model codes (S1532)
- MPNs
- series codes

And what does NOT count:
- generic numerals with units (26cm, 3L, 500ml)

---

## Agent / Skill-Level Improvements

### A1 — Force `@financial-analyst` + `xlsx-intake-qc` to output machine-readable intermediate artifacts
Add mandatory outputs:
- `analysis_decisions.csv` with per-row reason codes and extracted features:
  - `brand_sup`, `brand_amz`, `brand_confidence`
  - `units_sup`, `units_amz`, `size_conflict_pct`
  - `pack_sup`, `pack_amz`, `rsu`, `rsu_reason`
  - `verdict`

This makes downstream validation possible.

### A2 — Constrain subagents from “claiming full manual review”
In Step 3 instructions:
- require explicit audit evidence:
  - “List RowIDs reviewed” OR
  - “Provide sampling evidence”

### A3 — Dedicated “validator” pass
After Step 2, run a validator agent that only checks:
- negative adjusted profit in actionable buckets
- RSU anomalies
- size conflicts

This can be `@financial-analyst` again, but with a different prompt emphasizing QA.

---

## Implementation Plan (for ATLAS /start-work)

### Wave 1 — Prompt edits (fast)
1. Update Analysis prompt HIGHLY LIKELY rule re: generic brand tokens.
2. Update Analysis prompt: require size/weight consistency reasoning.
3. Update Manual Guide: replace “must manually adjudicate all rows” with sampling+anomaly approach.

### Wave 2 — Script improvements (financial_analysis.py)
1. Replace brand extraction with calibrated brand list + denylist.
2. Add size/capacity parser and conflict thresholds.
3. Harden pack vs dimension detection (3-number dimension pattern).
4. Add hard gates for adjusted profit and RSU anomalies.

### Wave 3 — QA + reporting
1. Add a validator report step that outputs error rate and corrected rows.
2. Add machine-readable `analysis_decisions.csv` for traceability.

---

## Acceptance Criteria (Agent-executable)

1. Running Step 2 produces:
- a Markdown report
- `analysis_decisions.csv`

2. Validator step reports:
- 0 rows with `Adjusted Profit ≤ 0` in VERIFIED/HIGHLY LIKELY
- 0 rows with dimension-multiplication RSU artifacts

3. Manual review step produces:
- sampling log
- quantified error rate

---

## Notes / Defaults

- Default goal is **precision-first** (reduce junk in HL/NV). If you prefer recall-first, we can tune thresholds upward.
