# Learnings - Chat Routing Fix v2

- Added validation to `enqueue_run_job` in `control_plane/tools/jobs.py` to reject empty or missing `runner_script` parameters.
- This serves as the second layer of the fail-fast strategy, catching invalid job requests before they are persisted to disk.
- The validation checks `request.runner_script` and raises a `ValueError` if it is empty or only whitespace.
### Worker Safety Validation (2026-02-01)
- Implemented file existence check for `runner_script` in `control_plane/worker.py`.
- This ensures the worker fails gracefully if a job specifies a non-existent script, preventing subprocess errors.
- The failure flow includes: marking state as failed, recording the error, moving the job to `failed/`, and releasing the active lock.

### Chat Orchestrator Pre-Router Fix (2026-02-01)
- Implemented `_resolve_workflow_params()` helper function in `control_plane/chat_orchestrator.py` to deterministically map supplier_domain → workflow_key → runner_script.
- Added `_infer_supplier_domain_from_url()` helper for consistent domain extraction from URLs.
- Updated the pre-router block in `plan_tool_call()` to use the resolution logic with proper error handling.
- The resolution uses three matching strategies in order:
  1. Hyphenated domain match (e.g., angelwholesale.co.uk → angelwholesale-co-uk)
  2. Workflow key base match (e.g., poundwholesale_workflow → poundwholesale)
  3. Domain base match (e.g., clearance-king.co.uk → clearance_king)
- On resolution failure, the system now returns `ask_clarify` tool call with descriptive error context instead of crashing.
- The pre-router now populates all required parameters: `supplier_domain`, `category_urls`, `workflow_key`, `runner_script`, `max_products`, `max_products_per_category`, and `notes`.
- Rich explanation strings are now included in ToolCall responses for better UX (e.g., "Starting analysis for 3 categories on angelwholesale.co.uk. Using runner 'run_custom_angelwholesale-co-uk.py' with workflow 'angelwholesale_workflow'.")
- The fix prevents the empty runner_script issue that caused run 9575c86c to fail with `python ""` error.
- Verification: `python -m py_compile control_plane/chat_orchestrator.py` passes successfully.
