# AI-Enhanced Orchestrator Integration Plan (Run-Order & Dependencies)

Absolute repo root: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\`

Objective
- Provide a clear, session-by-session plan for integrating the thin conversational orchestrator, config generators, executor, summarizer, and optional dashboard verifier — in a safe order that preserves the existing deterministic system and avoids breaking changes.

Ground Rules
- No edits to core workflow or utilities:
  - `tools/passive_extraction_workflow_latest.py`
  - `tools/configurable_supplier_scraper.py`
  - `tools/amazon_playwright_extractor.py`
  - `tools/FBA_Financial_calculator.py`
  - `utils/browser_manager.py`, `utils/enhanced_state_manager.py`, `utils/path_manager.py`
- File-based integration only (create configs/runners; call via `subprocess`)
- Supplier correctness in examples: `poundwholesale.co.uk` only
- UTF-8 and atomic writes for all new outputs

Key Existing Files (verified)
- Runner: `C:\...\run_custom_poundwholesale.py`
- Workflow: `C:\...\tools\passive_extraction_workflow_latest.py`
- Config Loader: `C:\...\config\system_config.json`

Current Snippets (for reference)
- `C:\...\run_custom_poundwholesale.py` (head):
```python
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.async_api import async_playwright
from config.system_config_loader import SystemConfigLoader
from tools.standalone_playwright_login import StandalonePlaywrightLogin
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from tools.poundwholesale.supplier_authentication_service import PoundwholesaleAuthenticationHelper
from utils.logger import setup_logger
from utils.browser_manager import BrowserManager
```

Why we won’t modify it
- This runner is the stable entry point used by the unchanged system; our orchestrator will call it via `subprocess` and will not import or alter its code.

Session 1 — Create Project Skeleton (no behavior changes)
Safe grouping: Yes (no dependencies on core code)
- Add package and stubs:
  - `ai_enhanced_setup/__init__.py`
  - `ai_enhanced_setup/conversation_orchestrator.py` (stub class + basic CLI helper)
  - `ai_enhanced_setup/config_generator.py` (stub functions returning paths only)
  - `ai_enhanced_setup/workflow_executor.py` (stub that echoes commands, no exec)
  - `ai_enhanced_setup/result_summarizer.py` (stub that prints placeholder summary)
  - `run_ai_setup.py` (prints welcome + dry-run options)
Reasoning: Establish import-safe structure so later sessions can fill behavior incrementally without touching core modules.

Session 2 — Implement Config Generator (deterministic output)
Dependencies: Session 1 package exists
- Implement `config_generator.py` to write UTF-8 JSONs:
  - `config/supplier_configs/{supplier_domain}.json`
  - `config/{supplier_domain}_categories.json`
  - `tools/{supplier_domain}_authentication_helper.py` (only if auth requested)
- Validate keys vs expected schema; include supplier_domain, price range, categories path, output_root
- Atomic write pattern: write to temp then move
Reasoning: Downstream steps (runner and executor) require these files to exist first.

Session 3 — Generate Supplier Runner Scripts
Dependencies: Session 2 outputs paths
- Implement generator for `run_custom_{supplier_domain}.py` that shells through to the existing runner, e.g.:
```python
# run_custom_poundwholesale-co-uk.py (generated)
if __name__ == "__main__":
    import sys, subprocess
    subprocess.run([sys.executable, "run_custom_poundwholesale.py", *sys.argv[1:]], check=False)
```
Reasoning: Keeps the front-door stable while enabling per-supplier entry naming; no behavioral change to core logic.

Session 4 — Implement Workflow Executor (subprocess, sanity-first)
Dependencies: Session 3 runner exists
- Implement `workflow_executor.py` to run:
  - Sanity: `python run_custom_{supplier}.py --test-mode --max-products=25 --debug --log-level=INFO`
  - Full: `python run_custom_{supplier}.py`
- Stream stdout to console and optional log file; return code + timestamps
Reasoning: Executing existing workflow unchanged is central to the thin-orchestrator constraint.

Session 5 — Implement Result Summarizer (file-grounded)
Dependencies: Workflow produces OUTPUTS
- Inspect:
  - `OUTPUTS\FBA_ANALYSIS\amazon_cache\amazon_*.json`
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\{supplier}\linking_map.json`
  - `OUTPUTS\FBA_ANALYSIS\financial_reports\*.csv`
  - `OUTPUTS\CACHE\processing_states\{supplier}_processing_state.json`
- Summaries: product counts, profitable items, top-N by ROI/margin
Reasoning: Provides value without AI cost by reading existing artifacts directly.

Session 6 — Implement Conversation Orchestrator (Claude; no scraping AI)
Dependencies: Sessions 2–5 complete
- `conversation_orchestrator.py` parses intents: scan/analyze/summarize/expand
- Collect slots: domain, categories, price range, modes, budget
- Call generator → executor → summarizer in a guided flow
- Expose `run_ai_setup.py` CLI loop
Reasoning: Adds natural language workflow without touching core code.

Session 7 — Add Dashboard Verifier (optional; when straightforward)
Dependencies: Summarizer in place
- `ai_enhanced_setup/dashboard_verifier.py` (new):
  - Compare dashboard snapshot (JSON) with OUTPUTS-derived metrics
  - Emit compact discrepancy report (JSON/MD)
- Optional AI readout of the small discrepancy report; avoid scanning large raw files unless requested
Reasoning: Early-iteration guardrail to validate dashboard correctness; can be disabled once stable.

Session 8 — Cost Visibility & Controls (lightweight)
Dependencies: Conversation orchestrator
- Track token estimates and show running cost; accept optional cap only if user requests
Reasoning: Aligns with $2–$4 acceptance philosophy; don’t over-engineer enforcement.

Session 9 — Tests & Verification
Dependencies: Core features landed
- Unit tests: generator schema, summarizer parsing, executor return codes
- Integration: end-to-end sanity (max-products=5), presence/timestamp/content checks
- File verification protocol: existence, timestamps, supplier correctness
Reasoning: Prevent regressions; prove the thin layer doesn’t break the core.

Strict Dependency Map
- S1 → S2 → S3 → S4 → S5 → S6 → (S7 optional) → S8 → S9

Safe Groupings (only if needed for speed)
- Group S1+S2 (stubs + config gen) — low risk
- Keep S3 separate (runner script) — depends on S2 values
- Group S4+S5 — executor and summarizer often developed together
- Keep S6 separate (conversation orchestrator) — ties all together

Change Impact & Replacement Notes
- We do not replace or modify `run_custom_poundwholesale.py` or `tools/passive_extraction_workflow_latest.py`.
- New scripts only “add” an orchestration layer and supplier-specific runner shim.

Reasoning Behind the Order
- Configs must exist before runners; runners before executor; executor before summarizer; summarizer before conversational glue; dashboard verifier after summarizer; costs last; tests wrap it up.

Session Hand-off Checklist (per session)
- What to implement
- Files to add/update
- Commands to run (sanity)
- Verification (existence, timestamp, content, supplier correctness)
- Next-session dependencies satisfied?

Appendix — Commands
- Sanity batch: `python run_custom_poundwholesale.py --test-mode --max-products=25 --debug --log-level=INFO`
- AI setup loop: `python run_ai_setup.py`
- Optional verifier: `python -m ai_enhanced_setup.dashboard_verifier --dashboard-json ./.cache/dashboard.json --outputs-root ./OUTPUTS --supplier poundwholesale-co-uk`

