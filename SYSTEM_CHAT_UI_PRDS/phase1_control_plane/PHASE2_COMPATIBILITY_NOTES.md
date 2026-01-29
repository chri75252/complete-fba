# Phase 2 Compatibility Notes

Phase 1 adds an Operator UI + optional LLM parser, but keeps the core “tool surface” stable for Phase 2.

## What Phase 2 can build on
- job manifests in `OUTPUTS/CONTROL_PLANE/jobs/pending/`
- status files in `OUTPUTS/CONTROL_PLANE/status/`
- per-run logs in `OUTPUTS/CONTROL_PLANE/logs/`
- system index in `OUTPUTS/CONTROL_PLANE/index/system_index.json`

## What Phase 2 should NOT bypass
- direct edits to canonical `config/system_config.json` for per-run changes
- running workflows directly inside Streamlit (use worker)

## LLM roles
- Phase 1 LLM parser: parameter extraction only
- Phase 2 chat agent: tool calling + multi-step orchestration (still gated)
