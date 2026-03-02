# Task 12 - E2E QA and Regression Evidence

## Scope

Validated core chat-planning/runtime behaviors required by the upgrade plan, with deterministic script-level checks plus real enqueue artifact verification.

## Checks Executed

1. Syntax compile checks for changed modules:
   - `control_plane/chat_orchestrator.py`
   - `control_plane/tools/repo_files.py`
   - `control_plane/tools/tool_param_validation.py`
   - `control_plane/llm/providers.py`
   - `dashboard/chat_panel.py`
2. Planner behavior checks (mock provider):
   - Category informational URL prompt is not hard-forced to `enqueue_run`.
   - Expected output placeholders are replaced with concrete `run_id`/sandbox IDs.
3. Runtime safety checks:
   - Strict tool param validation rejects malformed enqueue payloads.
   - Allowlist blocks source-code reads from `read_repo_file`.
4. Real enqueue artifact verification:
   - Enqueued `enqueue_run` with explicit run id: `qa-a525c9ba-328ff280`.
   - Confirmed concrete output paths and file creation.
   - Confirmed status/log files exist for same run id.
   - Cancellation marker created to stop QA run.
5. Product-list refresh regression check:
   - Reused same run id `plr-acb2b193` in dry-run twice.
   - Confirmed deterministic `sandbox_supplier` stability across invocations.

## Command Output Highlights

- Deterministic checks all passed:
  - `PASS :: category_info_not_forced`
  - `PASS :: expected_outputs_concrete_run_id`
  - `PASS :: strict_param_validation_blocks_missing_runner_script`
  - `PASS :: allowlist_blocks_source_reads`
- Enqueue run result included concrete paths:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_qa-a525c9ba-328ff280.json` (later moved to running)
  - `OUTPUTS/CONTROL_PLANE/overrides/qa-a525c9ba-328ff280/system_config.merged.json`
  - `OUTPUTS/CONTROL_PLANE/overrides/qa-a525c9ba-328ff280/categories_subset.json`
- Status/log observed for same run id:
  - `OUTPUTS/CONTROL_PLANE/status/qa-a525c9ba-328ff280.json`
  - `OUTPUTS/CONTROL_PLANE/logs/qa-a525c9ba-328ff280.log`
- Cancel executed:
  - `OUTPUTS/CONTROL_PLANE/status/qa-a525c9ba-328ff280.cancelled`
  - `OUTPUTS/CONTROL_PLANE/lock/cancel_qa-a525c9ba-328ff280.flag`

## Acceptance Mapping

- Product list refresh continuation semantics preserved: **PASS** (run-id reuse keeps same sandbox suffix).
- Category prompts routed through planner path (no deterministic short-circuit in orchestrator): **PASS**.
- Expected output preview uses concrete run-id-based paths: **PASS**.
- Safety hardening (allowlist + strict params) functional: **PASS**.

## Notes

- Full browser/UI conversational walkthroughs remain environment-dependent and are best confirmed in live dashboard usage.
- Script-level and artifact-level checks confirm control-plane logic and output-path grounding behavior.
