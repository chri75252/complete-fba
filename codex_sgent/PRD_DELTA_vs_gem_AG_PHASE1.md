# PRD Delta: `gem_AG/PHASE1_PRD_TECH_SPEC.md` vs `codex sgent/PRD_TECH_SPEC_FBA_PRODUCT_ANALYSIS_AGENT_v1.0.md`

**Compared files (absolute paths):**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\gem_AG\PHASE1_PRD_TECH_SPEC.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\codex sgent\PRD_TECH_SPEC_FBA_PRODUCT_ANALYSIS_AGENT_v1.0.md`

## Items present in `gem_AG` PRD but missing or divergent in `codex sgent` PRD

1. **Internal 5-bucket model**
   - `gem_AG` explicitly models UNRELATED as a 5th internal bucket.
   - `codex sgent` uses a 4-bucket contract + `include_in_tables` flag (UNRELATED as count-only).

2. **Fail-fast API key gate**
   - `gem_AG` requires missing `MOONSHOT_API_KEY` to hard-fail.
   - `codex sgent` supports heuristic preflight fallback when no key is set.

3. **Memory updates for traps**
   - `gem_AG` indicates auto-updating trap memory when new patterns are detected.
   - `codex sgent` stores calibration and brand aliases, but does not auto-append trap patterns.

4. **CLI command naming**
   - `gem_AG` uses `fba analyze ...` shorthand.
   - `codex sgent` uses `python -m fba_agent ...` (no installed console script).

5. **Directory structure**
   - `gem_AG` proposes nested `core/`, `tools/`, `interface/` structure.
   - `codex sgent` uses a flat module layout under `src/fba_agent/` for MVP simplicity.

6. **Python version**
   - `gem_AG` says Python 3.10+; repo standard is 3.12+.

## Recommendations / decision points

- **Bucket model:** keep current 4-bucket + `include_in_tables` flag unless you explicitly want a 5th internal bucket.
- **API key gate:** keep heuristic fallback unless you require hard-fail when Moonshot key is missing.
- **Trap memory:** can add a minimal trap append step (requires defined pattern capture) if you want it in MVP.
- **CLI naming:** can add a `fba` wrapper script later; low priority.
- **Structure:** keep flat module layout for speed; reorganize only if you prefer the `core/tools/interface` split.

