# Task 11 - Supplier Onboarding via Chat UI Feasibility

## Verdict

Feasible with moderate risk if constrained to a guided, queue-based flow that reuses existing `enqueue_onboarding` job execution and keeps Step-0 preprocessing human-confirmed.

## Current Capability (File-Grounded)

- Chat already supports enqueueing onboarding jobs via `enqueue_onboarding`:
  - `control_plane/chat_orchestrator.py` (tool routing and execution)
  - `control_plane/tools/repo_files.py` (`enqueue_onboarding_job`)
- Worker-side onboarding execution exists as a dedicated job type:
  - `control_plane/worker.py` (job dispatch)
- Supplier onboarding process requirements are detailed in:
  - `.claude/skills/supplier-onboarding/SKILL.md`
  - `NEW_SUPPLIER_WORKFLOW_GUIDE_DEC_29.md`

## Gap Analysis Against Skill Requirements

The skill requires extensive Step-0/Step-6 manual validation and deterministic file generation, including:

- Parsing and validating category URL files
- Parsing selector documents and producing normalized JSON
- Writing onboarding input JSON
- Deep, file-by-file validation and pre-run checks

Current chat tooling does not expose safe write/edit primitives for arbitrary onboarding prep files in `setup/`, `temp/`, and `config/` from natural-language requests. This is the main feasibility gap.

## Recommended Integration Model

1. Keep `enqueue_onboarding` as the only write execution action from chat.
2. Add a guided mode in chat that outputs a validated onboarding input JSON draft (readable by user).
3. User reviews/saves the JSON (or uses a future constrained write tool) and then confirms enqueue.
4. Keep all generated-file verification in read-only tools (`read_repo_file`, `list_repo_dir`) under allowlist and redaction.

## Safety Guardrails

- No arbitrary shell from chat.
- No unrestricted file writes from chat.
- Preserve confirmation gate before enqueue.
- Enforce path allowlist + secret redaction for all readbacks.
- For auth-required onboarding, never surface credentials in chat logs or audit payloads.

## Rollout Plan

1. Phase A: Guided-mode JSON generation + enqueue only.
2. Phase B: Add constrained onboarding-input writer (single destination + strict schema).
3. Phase C: Add optional post-enqueue validation checklist responses based on generated artifacts.

## Recommendation

Proceed with guided mode now (low/medium lift), defer full conversational Step-0 automation until a hardened constrained-write tool is implemented.
