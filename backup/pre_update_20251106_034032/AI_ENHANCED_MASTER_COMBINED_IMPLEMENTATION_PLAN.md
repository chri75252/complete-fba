# Combined Master Implementation Plan: AI‑Enhanced Supplier Setup (Thin Orchestrator)

This plan consolidates the strongest, feasible elements from both reports into one pragmatic, non‑overengineered implementation that adds a conversational setup layer while preserving the existing deterministic FBA system unchanged.

References (verified sources):
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\AI_Logic_Implementation\AI_ENHANCED_CORRECTED_IMPLEMENTATION_FINAL.md
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\AI_Logic_Implementation\AI_ENHANCED_CORRECTED_IMPLEMENTATION_FINAL - Copy.md

## Executive Overview
- Goal: Add a thin, AI‑assisted chat interface that guides supplier setup via natural language (“Scan/Analyze <supplier or URL>”), auto‑generates required configs, runs the existing workflows unchanged, and summarizes results.
- Philosophy: Value‑focused, conversation‑first, file‑based integration only. Respect your budget acceptance ($2–$4 per supplier when useful). No changes to core system code.
- Outcome: Reduce manual setup time from 45–90 minutes to 5–10 minutes without altering deterministic rules or outputs.

## Non‑Negotiable Constraints (System Integrity)
- Zero modifications to existing 413KB workflow and core components:
  - `tools/passive_extraction_workflow_latest.py` (orchestrator)
  - `tools/configurable_supplier_scraper.py` (deterministic selectors)
  - `tools/amazon_playwright_extractor.py` (EAN‑first, title fallback)
  - `tools/FBA_Financial_calculator.py` (ROI/margin/profit)
  - `utils/browser_manager.py`, `utils/enhanced_state_manager.py`, etc.
- File‑based integration only; existing I/O formats and locations remain:
  - `OUTPUTS\FBA_ANALYSIS\amazon_cache\amazon_*.json`
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\<supplier>\linking_map.json`
  - `OUTPUTS\FBA_ANALYSIS\financial_reports\*.csv`
  - `OUTPUTS\CACHE\processing_states\*_processing_state.json`
- Supplier reference correctness: Use `poundwholesale.co.uk` for examples in this phase.

## Architecture (Thin Orchestrator)
New files (chat layer only; no coupling to core code):
1. `run_ai_setup.py` — CLI entry with conversational flow, cost visibility
2. `ai_enhanced_setup/`
   - `__init__.py`
   - `conversation_orchestrator.py` — Intent parsing, Claude Sonnet 3.5 integration
   - `config_generator.py` — Direct Python dict → JSON (UTF‑8), exact schemas
   - `workflow_executor.py` — Launch existing runners via `subprocess`
   - `result_summarizer.py` — Read artifacts from `OUTPUTS/` and summarize

Required artifacts to generate per supplier domain (file‑based integration):
- `config/supplier_configs/{supplier_domain}.json`
- `config/{supplier_domain}_categories.json`
- `run_custom_{supplier_domain}.py` (entry script that loads system config and runs the unchanged workflow)
- `tools/{supplier_domain}_authentication_helper.py` (only if auth is needed)

Notes:
- Use `ai_enhanced_setup/` naming (aligns with current end‑goal). The original report used `ai_setup/`; this plan standardizes to `ai_enhanced_setup/` for clarity.
- All file writes must be atomic and `encoding='utf-8'` (use existing utilities where possible).

## Data Flow
1) User prompt → `run_ai_setup.py` → show budget info
2) Conversation (3‑step loop): gather supplier domain, optional category URLs, price range, sanity/full toggle, AI‑assist level, budget preference
3) `config_generator.py` writes configs (supplier, categories, optional auth helper) and runner script
4) `workflow_executor.py` triggers sanity batch via `subprocess` (25 products), monitors logs
5) On pass, execute full run; otherwise surface issues and options
6) `result_summarizer.py` reads real files in `OUTPUTS/` and presents curated summary (top by ROI/margin, counts, links to artifacts)

## Conversational Modes (Simple, Effective)
- Depth: quick (sanity‑only 25) / standard (default) / thorough (extra checks)
- AI Assist: auto (default) / minimal / off (deterministic‑only prompts)
- Budget: minimal (~$1–$2) / standard (~$2–$4) / generous (>$4)

## Budget Visibility (Value‑Focused)
- Transparent running estimate; no enforcement unless user requests a cap
- Default path should land in ~$2–$4 when AI adds value

## Deterministic Rules To Preserve (No Changes)
- Matching: EAN first; title fallback requires normalized similarity ≥ 0.85
- Profitability thresholds: Net profit ≥ £2.00; ROI ≥ 30%; margin ≥ 25%
- Market sanity: Prime/FBA‑eligible, in‑stock, ≥2 sellers, BSR main ≤ 300k

## Sanity Batch Before Full Run
- Default: 25 products sanity batch with logs + artifact checks
- Proceed to full run only if sanity checks pass (artifacts present, no critical errors)

## Minimal Interfaces To Existing System
- Launch unchanged entry script for supplier: `python run_custom_{supplier_domain}.py`
- Use existing config loader (`config/SystemConfigLoader.py`) and output directories
- Never import or modify `tools/passive_extraction_workflow_latest.py` or other core modules from the chat layer

## Example Prompts
- "Scan Poundwholesale toys under £20; sanity 25 products; then full run if clean."
- "Analyze this category URL; allow title normalization for missing EANs; target ~$3 total."
- "Summarize today’s run; export top 20 by ROI and margin."

## Module Responsibilities
### conversation_orchestrator.py
- Parse intent: scan/analyze/summarize/expand
- Track conversation state, budget visibility, and user preferences
- Call Claude Sonnet 3.5 only for conversation (no scraping AI)

### config_generator.py
- Input: supplier domain, categories/URLs (user‑provided selectors if any), price ranges
- Output files (UTF‑8):
  - `config/supplier_configs/{supplier_domain}.json`
  - `config/{supplier_domain}_categories.json`
  - `run_custom_{supplier_domain}.py`
  - `tools/{supplier_domain}_authentication_helper.py` (if needed)
- Validate schemas to match existing manual format; keep deterministic toggles consistent

### workflow_executor.py
- Start sanity batch: `python run_custom_{supplier_domain}.py --test-mode --max-products=25 --debug --log-level=INFO`
- On success, full run with standard parameters already used in your system
- Stream logs, capture exit status, and timestamps

### result_summarizer.py
- Read real artifacts (file‑grounded):
  - `OUTPUTS\FBA_ANALYSIS\amazon_cache\*.json`
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\{supplier_domain}\linking_map.json`
  - `OUTPUTS\FBA_ANALYSIS\financial_reports\*.csv`
  - `OUTPUTS\CACHE\processing_states\{supplier_domain}_processing_state.json`
- Summaries: product counts, profitable set, top N by ROI/margin, observed match methods, cache hit ratio, links to outputs

## Testing & Verification (File‑Grounded)
Pre‑flight setup:
- Ensure Chrome v139+ CDP: `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug &`
- Verify CDP endpoint: `curl http://localhost:9222/json/version`

Sanity execution:
- `python run_ai_setup.py` → choose sanity (25)
- Expect new files under `config/` and a runner at repo root; outputs under `OUTPUTS/`

Mandatory verification protocol (evidence):
1) Existence: `ls -la` of each generated path
2) Timestamp: confirm recent `LastWriteTime`
3) Content: open files; validate JSON schema and required keys; supplier must be `poundwholesale.co.uk`
4) Outputs: verify caches, linking map, financial CSV, processing state created

Automated tests (non‑destructive):
- `pytest -q`
- Browser‑dependent: `pytest -m "requires_browser" --chrome-port=9222`
- End‑to‑end (light): `python run_custom_poundwholesale.py --test-mode --max-products=5`

## Phased Delivery (Fast, Practical)
### Phase A (1–2 days)
- Skeleton: `run_ai_setup.py`, `ai_enhanced_setup/` modules with no‑op stubs
- Implement conversation flow (intent → config → sanity run → summarize)
- Cost visibility (running tally; optional cap by user request)
- Generate supplier config + categories + runner; optional auth helper
- Sanity batch execution; read artifacts; show summary

### Phase B (2–3 days)
- Refine conversation UX; add preset prompts; improve summarization (top N, CSV export)
- Robust schema validation, UTF‑8 enforcement, atomic writes
- Better logging with clear file links to `OUTPUTS/`

### Phase C (1 day)
- Polish: quick links to outputs, saved profiles, cost recap, helpful errors
- Hardening: edge cases (missing EANs → title fallback flag), safe retries

## Acceptance Criteria
- Conversational interface collects all supplier inputs naturally
- Generates all required config files with correct schemas and encoding
- Executes unchanged workflows via `subprocess`; preserves outputs/paths
- Shows cost estimates and final tally (value‑focused, no enforcement)
- Sanity batch (25) precedes full run; summaries are file‑grounded
- No changes to core system files; all functionality preserved

## Risk & Mitigation
- Chrome/CDP instability → use existing `utils/browser_manager.py` health checks
- State issues → file‑grounded verification; never rely on memory state alone
- Over‑engineering → keep chat layer thin; avoid templates and complex budgets
- Supplier specificity → keep examples to `poundwholesale.co.uk` during this phase

## Out of Scope
- Modifying core workflow, browser manager, state manager, or scraping logic
- Fixing system‑level issues (auth failures, CDP problems) beyond surfacing guidance

## Implementation Checklist
- [ ] Create `ai_enhanced_setup/` package and modules
- [ ] Implement minimal `run_ai_setup.py` CLI
- [ ] Generate per‑supplier configs and runner scripts
- [ ] Execute sanity → full run sequence via `subprocess`
- [ ] Summarize from real `OUTPUTS/` artifacts
- [ ] Add light tests; document usage and verification steps

---

Appendix A — Key Paths (Absolute)
- Repo root (example):
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\` (this repository)
  - Reports used in this plan:
    - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\AI_Logic_Implementation\AI_ENHANCED_CORRECTED_IMPLEMENTATION_FINAL.md`
    - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\AI_Logic_Implementation\AI_ENHANCED_CORRECTED_IMPLEMENTATION_FINAL - Copy.md`

Appendix B — Env Vars (suggested)
- `CHROME_REMOTE_PORT=9222`
- `OUTPUTS_BASE_PATH=./OUTPUTS`
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` (do not commit)

Appendix C — Sample Supplier Config Fields (illustrative)
```json
{
  "supplier_domain": "poundwholesale.co.uk",
  "price_range_gbp": {"min": 1.0, "max": 20.0},
  "categories_config_path": "config/poundwholesale-co-uk_categories.json",
  "output_root": "./OUTPUTS",
  "ai_assist": "auto",
  "notes": "Generated by run_ai_setup.py"
}
```

----------------------------------------
SECTION 19 — Extended Technical Specification (Deep Dive)
----------------------------------------

19.1 Data Models (Authoritative)
- ConversationState
  - `supplier_domain: str`
  - `category_urls: List[str]`
  - `price_min: float`
  - `price_max: float`
  - `run_mode: Literal['quick','standard','thorough']`
  - `ai_assist: Literal['auto','minimal','off']`
  - `budget_target: Literal['minimal','standard','generous']`
  - `sanity_batch_size: int` (default=25)
  - `notes: Optional[str]`

- GenerationOutputs
  - `supplier_config_path: str`
  - `categories_config_path: str`
  - `runner_script_path: str`
  - `auth_helper_path: Optional[str]`
  - `created_at_utc: str`

- ExecutionResult
  - `sanity_passed: bool`
  - `return_code: int`
  - `log_path: Optional[str]`
  - `artifacts: Dict[str, str]` (key: artifact type, value: absolute path)
  - `started_at_utc: str`
  - `finished_at_utc: str`

19.2 JSON Schema (Supplier Config, Illustrative)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["supplier_domain", "output_root", "price_range_gbp", "categories_config_path"],
  "properties": {
    "supplier_domain": {"type": "string", "pattern": "^([a-z0-9\.-]+)\.co\.uk$"},
    "output_root": {"type": "string"},
    "price_range_gbp": {
      "type": "object",
      "required": ["min", "max"],
      "properties": {"min": {"type": "number"}, "max": {"type": "number"}}
    },
    "categories_config_path": {"type": "string"},
    "ai_assist": {"type": "string", "enum": ["auto", "minimal", "off"]},
    "notes": {"type": "string"},
    "auth_required": {"type": "boolean"},
    "auth_helper_path": {"type": "string"}
  }
}
```

19.3 Categories JSON (Illustrative Schema)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["categories"],
  "properties": {
    "categories": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "url"],
        "properties": {
          "name": {"type": "string"},
          "url": {"type": "string"},
          "selectors": {"type": ["object", "null"]}
        }
      }
    }
  }
}
```

19.4 Sequence Flows (ASCII)
```
User ──▶ run_ai_setup.py ──▶ ConversationOrchestrator ──▶ ConfigGenerator ──▶ Files on disk
   │                                     │                          │
   │                                     ▼                          ▼
   │                               WorkflowExecutor ──▶ subprocess(run_custom_{domain}.py)
   │                                     │                          │
   │                                     ▼                          ▼
   │                               ResultSummarizer ◀────────── OUTPUTS/* artifacts
   ▼
 Console summaries + links
```

19.5 Pseudocode (Key Components)
```python
# run_ai_setup.py
def main():
    state = ConversationOrchestrator().run()
    outputs = ConfigGenerator().generate(state)
    sanity = WorkflowExecutor().run_sanity(outputs.runner_script_path, batch_size=state.sanity_batch_size)
    if sanity.sanity_passed:
        full = WorkflowExecutor().run_full(outputs.runner_script_path)
    summary = ResultSummarizer().summarize()
    print(summary)
```

```python
# conversation_orchestrator.py (sketch)
class ConversationOrchestrator:
    def run(self) -> ConversationState:
        # greet, collect supplier, categories, price, modes, budget
        # confirm and return a filled ConversationState
        ...
```

```python
# config_generator.py (sketch)
class ConfigGenerator:
    def generate(self, state: ConversationState) -> GenerationOutputs:
        # write supplier config, categories config, runner, optional auth helper
        # validate and return paths with timestamps
        ...
```

```python
# workflow_executor.py (sketch)
class WorkflowExecutor:
    def run_sanity(self, runner: str, batch_size: int) -> ExecutionResult:
        # subprocess: python runner --test-mode --max-products=batch_size --debug --log-level=INFO
        ...
    def run_full(self, runner: str) -> ExecutionResult:
        # subprocess: python runner
        ...
```

```python
# result_summarizer.py (sketch)
class ResultSummarizer:
    def summarize(self) -> dict:
        # read OUTPUTS artifacts, compute top-N, return dict/markdown
        ...
```

19.6 Error Catalog and Remedies
- CDP Unreachable
  - Verify `netstat -tuln | grep 9222` (or Windows equivalent)
  - `curl http://localhost:9222/json/version`
  - Run `python utils/browser_manager.py --health-check --auto-restart`
- Auth Failures
  - `python tools/supplier_authentication_service.py --reset-auth`
  - Confirm `OUTPUTS/CACHE/auth_sessions/*.json` is rotated
- Selector Breaks
  - User provides corrected selectors; regenerate categories JSON; rerun sanity
- Schema Mismatch
  - Validate JSON with schema checker; fix missing/extra fields; rewrite

19.7 Logging and Observability
- Stream subprocess stdout to console and a log file under `OUTPUTS/logs/` with timestamps
- Record generation actions and produced paths
- Capture return codes and durations for sanity/full runs

19.8 Windows‑First Details
- Use `sys.executable` for Python path
- Ensure paths use `PathManager` conventions where reading/writing
- Prefer explicit UTF‑8 for all open() calls

----------------------------------------
SECTION 20 — Test Suites and Scenarios
----------------------------------------

20.1 Unit Tests
- Conversation parsing (intent detection, slot extraction)
- Config writing (schema validation, UTF‑8 enforcement, atomicity)
- Summary parsers (robust to empty outputs)

20.2 Integration Tests
- Generate configs → verify presence, timestamps, content
- Subprocess execution (sanity mode) with mock/safe parameters

20.3 Workflow Validation (Light)
- `python run_custom_poundwholesale.py --test-mode --max-products=5` and verify outputs exist

20.4 Snapshot Tests
- Maintain Markdown/CSV summary snapshots for consistency

20.5 File‑Grounded Checks (Mandatory)
- Existence, timestamp, content, supplier correctness (no stray domains)

----------------------------------------
SECTION 21 — Conversation Templates and Utterances
----------------------------------------

21.1 System Prompt (Claude Sonnet 3.5 — Outline)
- Role: configuration orchestrator for an existing deterministic FBA system
- Rules: preserve architecture; file‑based only; budget visibility; sanity first
- Safety: do not invent selectors; ask user for missing specifics

21.2 Example Utterances
- “Scan poundwholesale.co.uk toys under £20; quick mode; then full if clean.”
- “Analyze this URL and allow title fallback when EAN missing; target ~£3 cost.”
- “Summarize today; export top 20 by ROI and margin.”

21.3 Disambiguation Questions
- “Do you want AI‑assist ‘auto’, ‘minimal’, or ‘off’?”
- “Confirm sanity batch size (default 25)?”
- “Provide category URLs or proceed with predefined categories?”

----------------------------------------
SECTION 22 — Performance Budgets
----------------------------------------

22.1 Memory and Files
- Limit in‑memory aggregation; rely on on‑disk artifacts
- Periodic cleanup of transient caches (never delete outputs)

22.2 Timing
- Sanity batch target: minutes, not hours, for 25 products

22.3 Browser Lifecycle
- Restart schedule via `utils/browser_manager.py --restart-schedule --interval=9000`

----------------------------------------
SECTION 23 — Rollout and Change Management
----------------------------------------

23.1 Branching/Commits
- Follow conventional commits; update docs when paths change

23.2 Documentation Sync
- Update `docs/README.md` usage examples for new chat layer
- Reference this plan file in `AI_Logic_Implementation/`

23.3 Backups (MANDATORY_BACKUP_PROTOCOL)
- Before significant changes: copy affected dirs to `backup/<timestamp>/`

----------------------------------------
SECTION 24 — Comprehensive Checklists
----------------------------------------

24.1 Pre‑Run Checklist
- [ ] Chrome CDP is reachable
- [ ] Supplier and categories configs present
- [ ] Runner script present and executable

24.2 Sanity Run Checklist
- [ ] Logs stream without critical errors
- [ ] OUTPUTS artifacts created (cache, linking map, CSV, state)
- [ ] Gate decision recorded

24.3 Full Run Checklist
- [ ] Completed without non‑recoverable errors
- [ ] Summaries generated and exported as requested

24.4 Post‑Run Verification
- [ ] Timestamps are recent
- [ ] Supplier references correct (`poundwholesale.co.uk`)
- [ ] CSV encodes as UTF‑8; schemas intact

----------------------------------------
SECTION 25 — Frequently Asked Questions (Operational)
----------------------------------------

Q: Can this layer modify the core workflow?
A: No. It only generates files and calls existing scripts.

Q: How are costs controlled?
A: Costs are surfaced; caps are applied only if users request them.

Q: What if EANs are missing?
A: Title fallback can be enabled; similarity threshold remains ≥ 0.85.

Q: Can it guess selectors?
A: No. The user provides selectors; the system stores them.

----------------------------------------
SECTION 26 — Future Enhancements (Optional)
----------------------------------------

- Saved profiles and recent runs menu in `run_ai_setup.py`
- Optional HTML summary dashboard reading from OUTPUTS/
- Cross‑supplier comparison reports (still file‑grounded)

----------------------------------------
END OF MASTER COMBINED IMPLEMENTATION PLAN
----------------------------------------
