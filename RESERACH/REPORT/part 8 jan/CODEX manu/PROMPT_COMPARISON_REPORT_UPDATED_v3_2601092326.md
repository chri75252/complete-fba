# Prompt Comparison & Recommendation Report (Updated v3)
**Generated:** 2026-01-09 (Asia/Dubai)

## 1) Direct Answer: Did I include the v1.2_v5 prompt in the earlier comparison?
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\PROMPT_COMPARISON_REPORT_2601092235.md` included `FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2_AUDITED_OUT_v5 (1).md`: `True`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\PROMPT_COMPARISON_REPORT_2601092235.md` included `FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_OG.md`: `False`
- So: I DID take the v1.2_v5 prompt into account in that earlier recommendation (it was not excluded).

## 2) After-calibration generation prompt: OG vs v1.2_v5
- OG: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_OG.md`
- v1.2_v5: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2_AUDITED_OUT_v5 (1).md`
- Normalized similarity: `0.625`

### Feature matrix
| Feature | OG | v1.2_v5 |
|---|---:|---:|
| Preflight calibration integration | T | T |
| Strict EAN checksum+leftpad | T | T |
| EAN normalization order explicitly stated | F | T |
| Reject scientific notation EANs | T | T |
| Dimension/measurement shield | T | T |
| Capacity tolerance thresholds | T | T |
| EAN conflict default -> NEEDS VERIFICATION | T | T |
| Unique-anchor gate present | T | T |
| UNRELATED count-only (not listed) | T | T |
| AUDITED OUT confirmed-only constraint | T | T |
| Fixed-width table contract | T | T |

- Score: OG=28, v1.2_v5=31
- Recommendation: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2_AUDITED_OUT_v5 (1).md`

### Practical difference that matters
- v1.2_v5 is the safer default because it makes the EAN normalization pipeline more explicit (including the `.0` artifact and scientific notation rejection). That reduces false EAN mismatches and improves consistency across runs.
- v1.2_v5 excerpt: ive only** and must not be used to override a gate. **Routing invariants (must hold everywhere in this prompt):** 1) **EAN normalization is mandatory** before any comparison: strip whitespace \u2192 remove trailing \u201c.0\u201d \u2192 reject scientific no...

## 3) Manual guide selection: v1.1.4 (chat) vs v1.1.5 patched vs v4
- Chat manual guide: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\MANUAL_GUIDE_UPDATED_v1.1.4 (1).md`
- Option: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\MANUAL_GUIDE_UPDATED_v1.1.5_PATCHED.md`
- Option: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE_AUDITED_OUT_v4.md`

### Feature matrix
| Feature | v1.1.4 | v1.1.5 | v4 |
|---|---:|---:|---:|
| Execution mode selection (review vs fresh) | T | T | F |
| Review mode boundary (no re-run pipeline) | T | T | F |
| Raw+normalized EAN evidence rule | T | T | F |
| Normalization order includes .0 + scientific notation | T | T | T |
| Pre-submission anomaly gate | T | T | F |
| Corrections log requirement (REMOVE/MOVE/EDIT) | T | T | F |
| UNRELATED count-only (not listed) | T | T | T |
| AUDITED OUT confirmed-only constraint | T | T | T |
| Anti-noise / unique-anchor gate section | T | T | T |
| Consistency/formatting invariants section | F | T | F |

- Score: v1.1.4=26, v1.1.5=28, v4=10
- Recommendation: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\MANUAL_GUIDE_UPDATED_v1.1.5_PATCHED.md`

## 4) Additional thorough comparison (required): v1.1.4 vs selected manual guide
- Selected manual guide: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\MANUAL_GUIDE_UPDATED_v1.1.5_PATCHED.md`

### Concrete diffs (headings)
- Only in v1.1.4: `5`
  - ### Step 8.2: HIGHLY LIKELY Criteria
  - ### Step 8.3: NEEDS VERIFICATION Criteria
  - ### Step 8.4: AUDITED OUT Criteria
  - #### Part A \u2014 Confirmed match via VERIFIED-path (EAN-confirmed)
  - #### Part B \u2014 Confirmed match via HIGHLY-LIKELY-path (non\u2011EAN confirmed)
- Only in v1.1.5: `10`
  - ### Consistency invariants (MANDATORY)
  - ### Output formatting hard rules (MANDATORY)
  - ### Step 8.2: HIGHLY LIKELY Criteria (Non\u2011Exact EAN)
  - ### Step 8.3: NEEDS VERIFICATION Criteria (Anti\u2011Noise)
  - ### Step 8.4: AUDITED OUT Criteria (Confirmed Match, Not Actionable)
  - #### Brand status gate (MANDATORY)
  - #### Eligibility gate (ANTI\u2011NOISE) \u2014 MANDATORY
  - #### Product-type anchor strength (MANDATORY)
  - #### Routing (when gates pass)
  - #### Unique-anchor gate (ANTI\u2011NOISE) \u2014 MANDATORY

### Why the switch helps
- v1.1.5 adds explicit “Consistency invariants” + “Output formatting hard rules” + clearer anti-noise gating. That reduces drift in REVIEW MODE and makes the correction trail more reproducible.

## 5) Final recommended future workflow
- Step 1: Calibration prompt.
- Step 2: Use `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2_AUDITED_OUT_v5 (1).md` to generate the PhaseA report.
- Step 3: Use `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX manu\MANUAL_GUIDE_UPDATED_v1.1.5_PATCHED.md` (REVIEW MODE) to adjudicate and produce the final corrected list.
