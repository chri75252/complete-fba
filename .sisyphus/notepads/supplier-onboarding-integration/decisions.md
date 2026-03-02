## 2026-02-26

- Use a compatibility-first fix for onboarding enqueue: derive `supplier_domain` from onboarding input JSON when not provided, and reject enqueue with a clear error if it cannot be resolved.
- Preserve existing `enqueue_onboarding` interface but support explicit `supplier_domain` passthrough for deterministic behavior.
- Keep planner behavior single-tool-per-turn; implement onboarding as a multi-turn stateful sequence rather than introducing multi-tool planning changes.
- Extend allowlists minimally to required onboarding paths only (`.claude/skills`, `setup`, `temp`, selected `config` JSON patterns, and `OUTPUTS/CONTROL_PLANE/jobs/pending`) to limit security blast radius.
- Chosen remediation: support optional supplier_domain in enqueue_onboarding, then resolve fallback from onboarding input JSON key domain before writing pending job payload.
- Chosen prompt strategy: append a dedicated "Supplier Onboarding Skill Execution (Steps 0-7)" section in SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md that preserves single-tool routing while encoding stage transitions.
- Chosen safety control: if write access is extended to OUTPUTS/CONTROL_PLANE/jobs/pending, enforce .json extension for that subtree to prevent arbitrary artifact writes.

## 2026-02-27

- Treat Chat onboarding execution as deterministic multi-turn state machine, not autonomous multi-tool chain.
- Update test plan wording to require explicit turn transitions (read SKILL -> next prompt read setup file -> next prompt write staged JSON -> next prompt enqueue).
- If autonomous chaining is required, implement a bounded planner-executor loop in `chat_orchestrator` and invoke it from `chat_panel` as a separate mode.
- Applied strict supplier-domain lock for code writes via `write_output_file`: code edit paths now require a non-empty `supplier_domain` and domain substring match; no fallback to permissive behavior.
- Kept existing `OUTPUTS/` report/product-list write logic unchanged to avoid widening blast radius while adding script-tailoring protection.
