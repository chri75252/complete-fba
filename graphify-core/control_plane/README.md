# Control Plane (Phase 1)

This package provides deterministic orchestration and querying capabilities that Phase 2 chat UI will drive.

## Key concepts
- Jobs are JSON files written to `OUTPUTS/CONTROL_PLANE/jobs/pending/`.
- The worker executes jobs and writes status to `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`.

## Run worker
- `python -m control_plane worker`

## Build system index
- `python -m control_plane build-index`

## Safety
- Single-run lock file prevents concurrent runs.
- Per-run merged config uses `FBA_SYSTEM_CONFIG_PATH` env var (requires small core hook).
