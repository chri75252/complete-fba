# PRD Delta: `opus_agent/PHASE1_PRD_TECH_SPEC.md` vs `codex sgent/PRD_TECH_SPEC_FBA_PRODUCT_ANALYSIS_AGENT_v1.0.md`

**Compared files (absolute paths):**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\opus_agent\PHASE1_PRD_TECH_SPEC.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\PRD_TECH_SPEC_FBA_PRODUCT_ANALYSIS_AGENT_v1.0.md`

## High-value items present in `opus_agent` PRD but missing/under-specified in `codex sgent` PRD

1. **Scoring rubric detail**
   - Base scores by bucket (e.g., VERIFIED=95, HIGHLY_LIKELY=80, NEEDS_VERIFICATION=60).
   - Concrete deterministic `compute_confidence()` pseudocode.
   - Evidence weighting table (EAN/brand/product/variant/pack/capacity).

2. **Validation severity model**
   - Explicit “Hard fail vs Soft fail” handling and what artifacts may still be written.

3. **Evaluation metrics**
   - Targets for coverage, stability, false positives, miss rate.

4. **CLI surface area**
   - Extra operational commands like `list-runs` and `show-memory`.

5. **Schema concreteness**
   - Stronger typed schemas (e.g., `SchemaInfo`, decision record fields, trap record fields) and sample JSON examples for memory files.

6. **Conflict resolution log**
   - A section that records specific spec conflicts and the resolution (even if “none yet”).

## Decisions / alignment actions

These items should be pulled into the canonical plan used for implementation:
- Expand scoring section to include base-scores + evidence weighting + deterministic scoring pseudocode.
- Add “Hard vs Soft fail” semantics (note: coverage/profit/format remain hard fails).
- Add evaluation metrics targets to guide regression testing.
- Add `list-runs` and `show-memory` as CLI commands (low complexity, helpful for ops).
- Add explicit schema notes + example JSON payloads for memory files.
- Add a short conflict-resolution log section and keep it updated during build.

