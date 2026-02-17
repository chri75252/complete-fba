# Doc/Code Drift Ledger (UltraWork)

**Generated**: 2026-02-03

This ledger lists high-impact mismatches between markdown documentation and current code reality.

---

## 1) Dashboard is not “monitoring only” anymore

**Doc pattern (common)**: Dashboard docs describe metrics/monitoring panels but omit operator + chat.

**Code reality**:
- Tabs include Operator and Chat:
  - `dashboard/app_fixed.py#L523`
- Chat panel exists and is wired to control plane:
  - `dashboard/chat_panel.py#L88`
- Operator control plane page exists:
  - `dashboard/pages/01_Operator_Control_Plane.py#L32`

**Impact**: Anyone reading old docs will not know chat-driven run creation and write-confirmation flow exists.

---

## 2) Control plane job system exists and is a first-class execution path

**Doc pattern**: Many workflow docs talk only about “run the runner script” and omit queued jobs and override configs.

**Code reality**:
- Worker CLI exists:
  - `control_plane/__main__.py#L9`
- Worker uses `OUTPUTS/CONTROL_PLANE/jobs/*` and writes `status/*.json` and `logs/*.log`:
  - `control_plane/paths.py#L32`
  - `control_plane/worker.py#L161`

**Impact**: Operations and automation can be driven via a queue, not only by manual script runs.

---

## 3) `FBA_SYSTEM_CONFIG_PATH` is now actually wired (override configs are real)

**Doc drift**: Some older docs imply changing `config/system_config.json` is required for runtime changes.

**Code reality**:
- Config loader reads env override:
  - `config/system_config_loader.py#L16`
- Worker sets it for run jobs:
  - `control_plane/worker.py#L186`

**Impact**: Operator/chat runs can be sandboxed by using per-run merged configs without modifying the base config.

---

## 4) Product list refresh (PRD_04) docs may be stale vs current implementation

**Doc claim** (from PRD_04 gaps report): product refresh writes minimal Amazon payload and does not use core extractor.

**Code reality**:
- `control_plane/run_product_list_refresh.py` imports `FixedAmazonExtractor` from `tools/amazon_playwright_extractor.py`:
  - `control_plane/run_product_list_refresh.py#L12`

**Impact**: The actual behavior depends on `tools/amazon_playwright_extractor.py`, including its OpenAI env gating.

---

## 5) `tools/amazon_playwright_extractor.py` hard-exits if `OPENAI_API_KEY` missing

**Doc expectation**: “AI optional / disabled by default” is commonly stated.

**Code reality**:
- The module exits the process if API key missing:
  - `tools/amazon_playwright_extractor.py#L43`

**Impact**: Any script importing this module in a non-OpenAI environment can crash immediately.

---

## 6) Supplier onboarding templates referenced in docs vs code

**Doc pattern**: Templates referenced under `utils/*_template.py.txt`.

**Code reality**:
- Wizard uses templates under `.claude/skills/supplier-onboarding/templates/*` (per earlier exploration).
- `utils/runner_template.py.txt` and `utils/auth_helper_template.py.txt` exist but are not the ones used by the wizard.

**Impact**: Editing the wrong template won’t affect generated runners.

---

## 7) Onboarding wizard category config naming is internally inconsistent

**Docs** generally propose one naming convention.

**Code reality**:
- Wizard has logic that can default to `config/{workflow_key}_categories.json`:
  - `utils/supplier_onboarding_wizard.py#L199`
- Other wizard logic writes `config/{domain_first_label}_categories.json` during generation (confirmed by exploration).

**Impact**: Automation can create “extra” category config files and/or mismatch the workflow’s configured `categories_config_path`.

---

## 8) Separate `fba_agent` subsystem exists (often omitted)

**Docs** focus on scraping workflow.

**Code reality**:
- `fba_agent/__main__.py#L7` bootstraps `src/` and runs `src/fba_agent/cli.py`.
- This subsystem has its own pipeline and tests.

**Impact**: The repo is not a single pipeline; it’s at least two.

(End)