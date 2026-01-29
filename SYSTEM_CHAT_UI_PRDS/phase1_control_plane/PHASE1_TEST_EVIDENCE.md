# Phase 1 Test Evidence (2026-01-25)

## 1) Syntax/Import
- `python -m py_compile control_plane/*.py control_plane/internal/*.py dashboard/operator_control_plane.py dashboard/app_fixed.py config/system_config_loader.py tools/passive_extraction_workflow_latest.py`
  - Result: exit code 0

## 2) Ollama connectivity
- URL: `http://localhost:11434/api/tags`
- Result: HTTP 200
- Models: `deepseek-r1:7b`

## 3) LLM parser (Ollama)
Env:
- `CONTROL_PLANE_LLM_PROVIDER=ollama`
- `CONTROL_PLANE_LLM_MODEL=deepseek-r1:7b`

Command:
- `python -c "import os; from control_plane.llm_parser import parse; os.environ['CONTROL_PLANE_LLM_PROVIDER']='ollama'; os.environ['CONTROL_PLANE_LLM_MODEL']='deepseek-r1:7b'; print(parse('Run poundwholesale_workflow on 2 categories, max 10 products'))"`

Result:
- Parser returned `ok=True` with missing fields list (expected; user didn't provide supplier_domain/workflow_key/etc).

## 4) Job creation (no worker)
Command created a run job and wrote:
- `OUTPUTS/CONTROL_PLANE/jobs/pending/job_04d79978-b2cd-400b-8362-6a8e5e745764.json`
- `OUTPUTS/CONTROL_PLANE/overrides/04d79978-b2cd-400b-8362-6a8e5e745764/system_config.merged.json`
- `OUTPUTS/CONTROL_PLANE/overrides/04d79978-b2cd-400b-8362-6a8e5e745764/categories_subset.json`

## 5) Worker smoke
- Worker processed the job and produced:
  - `OUTPUTS/CONTROL_PLANE/status/04d79978-b2cd-400b-8362-6a8e5e745764.json`
  - `OUTPUTS/CONTROL_PLANE/logs/04d79978-b2cd-400b-8362-6a8e5e745764.log`

Note: underlying workflow process exited due to Chrome CDP not running on port 9222; status JSON captured traceback.

## 6) FinancialQuery
Command:
- `python -c "from control_plane.financial_query import FinancialQuery; fq=FinancialQuery('.'); print(fq.query_financial_rows(supplier_domain='poundwholesale.co.uk', filters={'roi_min':30,'netprofit_min':5}, limit=5)['matched_rows'])"`

Result:
- `matched_rows=5`
- `latest_report=OUTPUTS/FBA_ANALYSIS/financial_reports/poundwholesale-co-uk/combined_reports.csv`
