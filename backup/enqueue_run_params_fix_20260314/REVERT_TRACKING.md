# Revert Tracking

- Backup dir: C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\enqueue_run_params_fix_20260314
- Created (UTC): 2026-03-14T06:35:12Z

## Planned changes
- control_plane/tools/tool_param_validation.py: Normalize enqueue_run max_products when equal to max_products_per_category across multiple category URLs; align recorded tool params with effective merged config.

## Validation plan
- lsp_diagnostics on control_plane/tools/tool_param_validation.py
- python -m py_compile control_plane/tools/tool_param_validation.py
- (If available) pytest -q (or targeted tests)

## Validation results
- lsp_diagnostics: clean (no diagnostics)
- py_compile: ok
- smoke test: validate_tool_params('enqueue_run', max_products=4, max_products_per_category=4, 3 urls) -> max_products=12
- pytest: fails due to pre-existing import/collection issues in unrelated paths (plugin autoload disabled)
