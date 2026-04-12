# Control Plane Tool Surface (Phase 1)

This is the deterministic tool surface that Phase 2 chat will call.

## Read-only
- `control_plane.tools.state.read_processing_state`
- `control_plane.tools.state.summarize_processing_state`
- `control_plane.tools.financial.query_financial_rows`
- `control_plane.tools.financial.find_latest_financial_report`
- `control_plane.tools.logs.tail_file`
- `control_plane.tools.status.read_status`

## Write/exec
- `control_plane.tools.jobs.write_categories_subset`
- `control_plane.tools.jobs.write_merged_system_config`
- `control_plane.tools.jobs.enqueue_run_job`

## Execution
- `control_plane.worker` (job executor)
