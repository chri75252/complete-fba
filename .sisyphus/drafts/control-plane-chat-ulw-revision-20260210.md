# Draft: Control Plane Chat ULW Plan Revision (2026-02-10)

## Requirements (confirmed)
- Revert **all edits** made to **main/original workflow scripts**, including `tools/*` core scripts and `run_custom_*.py` runners.
- Future/new `run_custom_*.py` scripts are generated via supplier-onboarding skill (`.claude/skills/supplier-onboarding/`) and should be treated as the canonical template baseline; do not patch existing runners for control-plane needs.
- Prefer fixes in the **new workflows layer** (`control_plane/*`, `dashboard/*`) over core workflow changes.
- If core instrumentation is ever required:
  - Must be explicitly pre-announced (file list + intended diff + risks + rollback plan).
  - Must be gated behind an explicit toggle (default OFF).
  - Must be **removed/reverted** after diagnosing root cause (explicit plan step).
- Add this policy as durable guidance in BOTH:
  - Persistent memory (Supermemory)
  - Human-facing docs (`AGENTS.md`, plus agent-facing `CLAUDE.md` / `CLAUDE_STANDARDS.md`)

## Technical Decisions
- Replace the prior plan’s Task 5 (instrument `tools/configurable_supplier_scraper.py`) with a **control-plane diagnostics probe** approach:
  - Collect selector evidence, HTML snapshots, screenshots, optional Playwright trace/HAR, without editing `tools/*`.
- Cancellation markers: canonical marker is `OUTPUTS/CONTROL_PLANE/status/<run_id>.cancelled`; allow backward compatibility with `OUTPUTS/CONTROL_PLANE/lock/cancel_<run_id>.flag`.

## Research Findings
- Existing repo snapshot patterns:
  - `page.screenshot(...)` already used in `tools/efghousewares/supplier_authentication_service.py`.
  - `page.content()` + screenshot used in historical supplier login scripts.
- Control-plane has a non-Playwright “trace” concept: `OUTPUTS/DIAGNOSTICS/trace_*.json` surfaced via `control_plane/tools/trace.py` and indexed by `control_plane/rag_index.py`.
- Playwright built-in tracing/HAR is not currently implemented in the repo, but supported by Playwright Python and can be added in control-plane diagnostics layer.
- AngelWholesale debugging assets exist without touching core code:
  - `extract_angelwholesale_urls.py`, `angelwholesale_category_snapshot.txt`, `ANGELWHOLESALE_PAGINATION_AMAZON_INVESTIGATION_REPORT_20251115.md`, Angel sandbox logs.

## Scope Boundaries
- INCLUDE: control-plane chat reliability, sandbox run correctness, cancellation, clarify context, run_id follow-ups, low-risk AngelWholesale pagination diagnosis.
- EXCLUDE: structural refactors of core workflow engine; changes to `tools/*` unless explicitly justified and gated; edits to existing runner scripts.

## Open Questions
- Whether diagnostics probe should connect via existing `BrowserManager` vs standalone `chromium.connect_over_cdp`.
- Whether to store probe artifacts under `OUTPUTS/CONTROL_PLANE/diagnostics/<run_id>/` or `OUTPUTS/DIAGNOSTICS/` (needs consistency decision).
