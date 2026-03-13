# Plan: High-Fidelity Context & Agent Recall Fix

## TLDR

> **Quick Summary**: Fix the "agent amnesia" issue where the Chat UI LLM fails to remember file paths or run IDs from previous tool outputs. This is achieved by moving from a restrictive whitelist-based stripping model to a structure-preserving recursive pruning model.
> 
> **Deliverables**:
> - Updated `_sanitize_chat_history` in `control_plane/chat_orchestrator.py` with recursive pruning.
> - Updated `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` to allow ID/path recall from history.
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: YES (Wave 1)
> **Critical Path**: Task 1 & 2 -> Task 3

---

## Context

### Original Request
The user noted that the agent behaves "robotically" and forgets identifiers (like `rel_path` or `run_id`) that were just output by a previous tool. Even if the information is visible in the UI, the LLM often asks "Which file?" or "Which run ID?".

### Interview Summary
**Key Discussions**:
- **Amnesia Source**: Identifiers are being deleted by `_sanitize_chat_history` because they aren't in a hardcoded whitelist.
- **Solution Approach**: Instead of deleting non-whitelisted keys, we will keep all keys but prune only large values (long strings, long lists) to save context window space.
- **Planner Constraint**: The "Never guess" rule in system instructions makes the LLM overly cautious about using IDs it sees in the history.

**Research Findings**:
- The current implementation of `_sanitize_chat_history` drops everything except about 15 whitelisted keys.
- `rel_path` (returned by the new product-list builder) was missing from this whitelist.

---

## Work Objectives

### Core Objective
Restore the agent's "Common Sense" by ensuring it can see and use all metadata returned by previous tool executions.

### Concrete Deliverables
- Modified `control_plane/chat_orchestrator.py`
- Modified `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`

### Definition of Done
- [ ] `_sanitize_chat_history` preserves arbitrary tool result keys (e.g., `rel_path`, `report_path`).
- [ ] Large lists in tool results are truncated rather than removed.
- [ ] The planner uses IDs from history without reprompting the user.

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (using ad-hoc verification script)
- **Automated tests**: None
- **QA Policy**: Every task includes Agent-Executed QA Scenarios.

| Deliverable Type | Verification Tool | Method |
|------------------|-------------------|--------|
| Logic Change     | Bash (python -c)  | Verify sanitization preserves keys |
| Prompt Change    | Manual/Playwright | Verify agent recall in chat |

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Implement Pruning Logic [quick]
└── Task 2: Update Planner Instructions [quick]

Wave 2 (After Wave 1):
└── Task 3: Logic Verification [quick]
```

---

## TODOs

- [ ] 1. Implement High-Fidelity Pruning Logic

  **What to do**:
  - In `control_plane/chat_orchestrator.py`, insert a new helper `_prune_value(val, max_list=10, max_str=1000, depth=0)` that:
    - Recursively traverses dicts and lists.
    - Limits recursion depth to 5.
    - Truncates lists to 10 items + a summary string.
    - Truncated strings to 1000 chars + a summary string.
    - Preserves all dictionary keys.
  - Update `_sanitize_chat_history` to remove the whitelist loop and use `_prune_value(tool_result)` instead.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **References**:
  - `control_plane/chat_orchestrator.py:116` - `_sanitize_chat_history` location.

  **Acceptance Criteria**:
  - `python -m py_compile control_plane/chat_orchestrator.py` succeeds.

  **QA Scenarios**:
  \`\`\`
  Scenario: Verify key preservation
    Tool: Bash (python -c)
    Steps:
      1. Run: `python -c "from control_plane.chat_orchestrator import _sanitize_chat_history; h=[{'role':'assistant','tool_result':{'my_new_key':'secret_id','large_list':[1]*100}}]; s=_sanitize_chat_history(h); print(s[0]['tool_result'])"`
    Expected Result: Output contains `'my_new_key': 'secret_id'` and `'large_list'` contains a summary of more items.
    Evidence: .sisyphus/evidence/task-1-key-preservation.txt
  \`\`\`

- [ ] 2. Relax Planner ID Recall Rules

  **What to do**:
  - Update `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`.
  - Modify Rule 13 ("Never guess...") to explicitly state that the planner MUST use IDs and paths found in the chat history or tool results.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **Acceptance Criteria**:
  - File updated with the new wording.

- [ ] 3. Final Verification

  **What to do**:
  - Run a comprehensive check of the sanitization logic.

  **QA Scenarios**:
  \`\`\`
  Scenario: Full History Sanitization Test
    Tool: Bash (python -c)
    Steps:
      1. Run a script that feeds a multi-turn history with various tool result shapes into `_sanitize_chat_history`.
      2. Verify the output size remains reasonable but IDs are preserved.
    Expected Result: IDs are visible in the resulting prompt context.
    Evidence: .sisyphus/evidence/task-3-final-verification.txt
  \`\`\`

---

## Success Criteria

- [ ] All "amnesia" points identified in the report are addressed.
- [ ] No regressions in context window limit handling.
- [ ] Agent can recall `rel_path` from turn N in turn N+1.
