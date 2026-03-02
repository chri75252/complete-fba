# Chat UI LLM Assistant Upgrade (Dashboard + Control Plane)

## TL;DR

> **Quick Summary**: Upgrade the Streamlit chat UI from a JSON-only “tool picker” into a real assistant: multi-turn memory (within the same chat), natural language responses, safe read access to runtime artifacts, and LLM-driven routing for category URL prompts (no deterministic bypass). Preserve product-list refresh behavior (it already resumes correctly when `run_id` is reused).
>
> **Deliverables**:
> - Chat UI sends conversation context to the LLM (multi-turn memory)
> - Category URL prompts go through LLM planner (no short-circuit)
> - Two-phase LLM: tool selection (safe JSON) + natural language response
> - Safe read access to runtime artifacts (financial reports, linking maps, state, status/logs)
> - Optional: feasibility + guarded integration for supplier onboarding skill
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES (4 waves)
> **Critical Path**: Memory plumbing -> LLM routing refactor -> response generation -> safety hardening -> E2E QA

---

## Context

### Original Request (condensed)
- Make the chat UI LLM behave like a real assistant (like a “proper” LLM chat): understand natural language prompts, remember within-chat context, and generate natural responses.
- Category analysis currently feels robotic and ignores intent (especially `max_products`). Product list refresh is much better and can continue from interruptions when `run_id` is provided.
- You do NOT want deterministic/regex-only behavior for category analysis; you want the model to interpret prompts given a correct system prompt + tools + file access.
- You want safe read access to runtime artifacts (financial reports, linking maps, processing state) so you can ask operational questions.
- You want limited safe operator actions (enqueue, cancel, possibly run runner scripts through controlled pathways).
- You want supplier onboarding skill to be feasible from chat UI (or explicitly assess and defer if heavy).

### File-Grounded Findings

**Why the LLM “forgets” within the same chat**
- The UI keeps history in Streamlit (`st.session_state["chat_messages"]`), but only sends the **latest** message to the planner.
  - `dashboard/chat_panel.py:392-440` appends to chat history, then calls `plan_tool_call(user_input, Path(base_dir))` at `dashboard/chat_panel.py:406`.
- The control-plane planner accepts only a single string turn:
  - `control_plane/chat_orchestrator.py:380` `plan_tool_call(user_text: str, repo_root: Path)`.
- Many providers are single-turn JSON-only by design (temperature=0) for tool selection:
  - `control_plane/llm/providers.py:153-194`.

**Why category URL prompts are robotic**
- Category URL prompts currently bypass the LLM entirely:
  - `control_plane/chat_orchestrator.py:382-417` detects `category_urls` then directly returns `ToolCall(name="enqueue_run", ...)` with a canned note and regex-extracted limits.

**Product list refresh already supports continue/resume**
- Product list refresh preloads prior linking-map rows and dedups by identity before processing:
  - `control_plane/run_product_list_refresh.py` `_load_existing_linking_results()` and `processed_keys`.
  - The job sandbox uses `supplier_domain__sandbox__{run_id[:8]}`.
- Therefore: do NOT “rewrite” product-list refresh; preserve behavior.

**Deterministic bypasses exist in the UI**
- Cancel intent is handled deterministically in the UI without LLM:
  - `dashboard/chat_panel.py:348-371` regex-detects cancel and calls `cancel_run` directly.

**Existing tools already cover many operator tasks**
- Financial rows query tool exists:
  - `control_plane/tools/financial.py:36-88` `query_financial_rows()`.
- Read-only repo file access exists but is blocklist-based:
  - `control_plane/tools/repo_files.py:14-71`, `control_plane/rd2_policy.py:36-99`.
- Enqueue onboarding wizard job exists:
  - `control_plane/tools/repo_files.py:73-104` `enqueue_onboarding_job()`.

---

## How The LLM Will Be “Configured” (the model behavior you asked for)

This plan intentionally keeps **tool execution safe** while making the assistant **feel natural**.

### Two-Phase LLM (Recommended)

1) **Planner phase (Tool JSON, deterministic, safe)**
- Input: conversation context + latest user message + system index/RAG (when relevant)
- Output: a single structured tool call (`tool`, `params`, optional `expected_outputs`)
- LLM settings: `temperature=0` (or equivalent) to avoid malformed tool outputs
- Safety: schema validation + allowlisted tool names

2) **Responder phase (Natural language, grounded, non-robotic)**
- Input: conversation context + selected tool + tool result (or pending confirmation state)
- Output: natural language response like a real assistant (“here’s what I did / what will happen / what I found”)
- LLM settings: `temperature ~0.3-0.5`
- Grounding rule: responder must cite the tool result fields and/or file paths; no hallucinated numbers.

This is the same core idea modern tool-using assistants implement: keep actions structured, keep conversation natural.

### Files & Data The Assistant Can Read (safe scope)

Default allowlist (read-only):
- `OUTPUTS/CONTROL_PLANE/status/*.json`
- `OUTPUTS/CONTROL_PLANE/logs/*.log` (tail only)
- `OUTPUTS/CONTROL_PLANE/jobs/**/*.json`
- `OUTPUTS/CONTROL_PLANE/audit/*.jsonl`
- `OUTPUTS/CACHE/processing_states/*.json`
- `OUTPUTS/FBA_ANALYSIS/linking_maps/**/*.json`
- `OUTPUTS/FBA_ANALYSIS/financial_reports/**/*.csv`
- `config/system_config.json` (redacted)
- `config/*_categories.json`
- `config/supplier_configs/*.json` (redacted)

Explicitly blocked (even if user requests):
- `.env*`, `credentials.*`, `.git/` (already blocked by `control_plane/rd2_policy.py`)
- Any path outside repo root

### Commands The Assistant Can Execute

No arbitrary shell. All “execution” happens through existing **worker-queued jobs**:
- `enqueue_run` (category workflow)
- `enqueue_product_list_refresh`
- `cancel_run`
- `enqueue_onboarding` (runs onboarding wizard script via worker)

Optional later: “run `python run_custom_{supplier}`” becomes a **safe queued job type** (runner allowlist + tracked status), not direct shell execution.

---

## Work Objectives

### Core Objective
Make chat UI agent behave like a real assistant while keeping execution safe and auditable.

### Must Have
- Multi-turn memory within the same chat without requiring the user to restate run_id or context every turn.
- Category URL prompts must go through LLM planner (no bypass).
- Natural language responses (not JSON-only) for informational queries and tool results.
- Safe read access to runtime artifacts (financial/state/linking maps/status/logs).
- Keep write-tool confirmation gate in the UI.
- Preserve product-list refresh resume behavior; avoid heavy edits there.

### Must NOT Have (Guardrails)
- No unrestricted read access to repo source or secrets.
- No direct shell execution from chat.
- No major refactor of product-list refresh engine.

---

## Verification Strategy (MANDATORY)

All verification is agent-executed. No “user manually checks” acceptance criteria.

### Test Decision
- **Infrastructure exists**: YES (Python modules + lightweight CLI checks)
- **Automated tests**: Tests-after (add targeted tests where feasible)
- **Primary verification**: tool-driven QA scenarios (dashboard + control_plane), plus direct file assertions.

### Evidence Policy
Evidence saved under `.sisyphus/evidence/`.

---

## Execution Strategy (Parallel Waves)

Wave 1 (Start immediately: memory plumbing + response phase scaffolding)
Wave 2 (Routing changes: remove category URL bypass, remove UI cancel bypass)
Wave 3 (Safety hardening + artifact read improvements + onboarding feasibility)
Wave 4 (E2E QA + regression checks: product-list refresh unchanged)

### Dependency Matrix (abbreviated)

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 | — | 2, 5, 6 |
| 2 | 1 | 12 |
| 3 | 1 | 12 |
| 4 | 2 | 12 |
| 5 | 1 | 12 |
| 6 | 1 | 12 |
| 7 | 1 | 12 |
| 8 | — | 12 |
| 9 | — | 12 |
| 10 | — | — |
| 11 | — | — |
| 12 | 1-9 | — |

---

## Proposed Patches (Diff Preview Only)

These are **planning diffs** to communicate intended changes. Executor will implement, run QA, and adjust context lines as needed.

### Patch A: Pass chat history into planner

`dashboard/chat_panel.py`

```diff
@@
-    tool_call, rag_info = plan_tool_call(user_input, Path(base_dir))
+    # Pass recent conversation context so the LLM can handle clarifications.
+    # Do NOT include large tool_result payloads verbatim.
+    history = st.session_state.get("chat_messages", [])
+    tool_call, rag_info = plan_tool_call(user_input, Path(base_dir), history=history)
```

### Patch B: Remove deterministic cancel regex bypass in UI (route through LLM)

`dashboard/chat_panel.py`

```diff
@@
-    cancel_pat = re.compile(...)
-    if cancel_pat.search(user_input):
-        ... execute cancel_run directly ...
-        return
+    # Cancellation intent is handled by the LLM planner so it can use
+    # in-chat context (last run) and ask clarifying questions if needed.
+    # Keep a safe fallback button in the UI (optional).
```

### Patch C: Remove category URL short-circuit (route URLs through LLM planner)

`control_plane/chat_orchestrator.py`

```diff
@@
-    category_urls = _extract_category_urls(user_text, system_index)
-
-    if category_urls:
-        supplier_domain = _infer_supplier_domain_from_url(category_urls[0])
-        constraints = _parse_runtime_constraints(user_text)
-        ... return ToolCall(name="enqueue_run", ...) ...
+    # NOTE: Do NOT short-circuit on category URLs.
+    # The LLM planner must see the user intent and decide whether to enqueue
+    # a run or ask clarifying questions.
+    category_urls = _extract_category_urls(user_text, system_index)
+    # Pass category_urls as hints into the prompt/RAG context instead.
```

### Patch D: Stop overriding max_products with regex after LLM selection

`control_plane/chat_orchestrator.py`

```diff
@@
-        if tool == "enqueue_run":
-            ... constraints = _parse_runtime_constraints(user_text)
-            params["max_products"] = constraints["max_products"] ...
+        if tool == "enqueue_run":
+            # Prefer the model's interpreted params.
+            # Only apply regex constraints as a fallback when the model left
+            # the value unset AND the user explicitly wrote a number.
+            ...
```

### Patch E: Add responder phase (natural language)

`control_plane/chat_orchestrator.py` and `control_plane/llm/providers.py`

```diff
@@
 class LlmProvider(Protocol):
     def generate_json(self, prompt: str) -> dict[str, Any]:
         ...
+    def generate_text(self, messages: list[dict[str, Any]]) -> str:
+        ...
```

Then in chat execution flow: after `execute_tool_call()`, call responder LLM to turn tool result into natural language.

---

## TODOs

Each task includes: recommended agent profile, references, acceptance criteria, and QA scenarios.

### Wave 1 — Memory + Two-Phase Response (Foundation)

- [x] 1. Add conversation context plumbing (UI -> planner)

  **What to do**:
  - Extend `plan_tool_call` to accept `history` (list of prior messages).
  - In `dashboard/chat_panel.py`, pass `st.session_state["chat_messages"]` into planner.
  - Define truncation policy: include last N messages; exclude/trim large `tool_result` blobs.

  **Must NOT do**:
  - Do not persist across browser refresh in this task.
  - Do not change product-list refresh runner.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: (none)

  **Parallelization**:
  - Can Run In Parallel: YES (with Tasks 2-4)
  - Parallel Group: Wave 1

  **References**:
  - `dashboard/chat_panel.py:392-440` - current single-turn planner call
  - `control_plane/chat_orchestrator.py:380` - planner signature

  **Acceptance Criteria**:
  - [ ] In a single chat session, ask a clarifying question then answer it; planner uses prior context and does not treat it as a brand new request.

  **QA Scenarios**:
  ```
  Scenario: Clarification retains context
    Tool: Playwright (or manual via scripted steps if Playwright not wired)
    Steps:
      1. Send message: "Analyze category X with max_products 10"
      2. If assistant asks: "Which supplier?" reply: "efghousewares.co.uk"
      3. Verify assistant enqueues run for efghousewares and uses max_products=10
    Evidence: .sisyphus/evidence/task-1-clarification-context.txt
  ```

- [x] 2. Implement responder phase (natural language) while keeping planner JSON-safe

  **What to do**:
  - Keep planner as JSON-only tool selection.
  - Add second LLM call to generate conversational response using tool result.
  - Ensure responder includes citations (file paths/tool outputs).

  **References**:
  - `control_plane/llm/providers.py` - providers (add text generation capability)
  - `dashboard/chat_panel.py:428-437` - current assistant_content fallback logic

  **Acceptance Criteria**:
  - [ ] For `query_financial` results, assistant responds with a natural paragraph + cites report_path.
  - [ ] No raw JSON is printed to the chat unless user explicitly asks.

  **QA Scenarios**:
  ```
  Scenario: Natural language response grounded in tool result
    Tool: Bash (python)
    Steps:
      1. Invoke query tool through chat: "Show me 5 rows with ROI > 30 for supplier X"
      2. Verify assistant reply contains count/summary and includes report path.
    Evidence: .sisyphus/evidence/task-2-nl-response.txt
  ```

- [x] 3. Token budget + truncation rules for history and tool results

  **What to do**:
  - Implement history window default (e.g., last 10 messages).
  - Summarize or omit large tool_result payloads.

  **Acceptance Criteria**:
  - [ ] Large tool result does not blow up prompt size; assistant remains responsive.

- [x] 4. Provider capability parity for your API model (OpenAI-compatible)

  **What to do**:
  - Ensure OpenAI-compat provider can do: JSON tool planning + text response.
  - Keep tool planning deterministic (temperature 0); responder warmer.

  **References**:
  - `control_plane/llm/providers.py:169-194` - OpenAiCompatProvider

### Wave 2 — Route Category Prompts Through LLM (Remove Bypasses)

- [x] 5. Route category URL prompts through the LLM planner (remove short-circuit)

  **What to do**:
  - Delete or feature-flag `if category_urls:` block at `control_plane/chat_orchestrator.py:382-417`.
  - Provide category_urls as hint context to the LLM planner instead of bypass.

  **Acceptance Criteria**:
  - [ ] Category URL prompts produce non-robotic, context-aware behavior (clarify when ambiguous, enqueue when explicit).

- [x] 6. Remove deterministic cancel regex bypass from dashboard UI (route cancel intent through planner)

- [x] 7. Update planner instructions to support multi-turn + “assistant-like” behavior

  **What to do**:
  - Keep planner JSON-only, but update instructions to:
    - prefer asking clarifying questions when ambiguous
    - treat category URLs as inputs, not auto-run triggers
    - avoid defaulting max_products to 0/2000 unless user asks

  **References**:
  - `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md:7-24` - current hard rules (URL => enqueue_run)

  **Acceptance Criteria**:
  - [ ] Category URL prompt that is informational ("what is this URL?") does not auto-enqueue.

  **QA Scenarios**:
  ```
  Scenario: Informational category URL does not auto-run
    Tool: Bash (python)
    Steps:
      1. Call planner with user_text: "What is https://angelwholesale.co.uk/Category/Wholesale-Yellow-Partyware?"
      2. Assert tool == ask_clarify OR a read-only tool, not enqueue_run
    Evidence: .sisyphus/evidence/task-7-category-informational.txt
  ```

  **What to do**:
  - Remove `cancel_pat` branch in `dashboard/chat_panel.py:348-371`.
  - Ensure planner can resolve contextual run_id (already exists in `control_plane/chat_orchestrator.py` contextual resolution).

  **References**:
  - `control_plane/chat_orchestrator.py:558+` - `_resolve_contextual_run_id()`

### Wave 3 — Safety Hardening + Read Access + Onboarding Feasibility

- [x] 8. Implement allowlist-based file reads for the assistant

  **What to do**:
  - Keep `control_plane/rd2_policy.py` blocklist.
  - Add allowlist enforcement for chat assistant reads (runtime artifacts + configs).

  **References**:
  - `control_plane/tools/repo_files.py:14-71`
  - `control_plane/rd2_policy.py:77-99`

- [x] 9. Tight schema validation for tool params

  **What to do**:
  - Add strict validation for each tool request type (RunRequest, ProductListRefreshRequest, FinancialQuery, OnboardingWizardRequest).
  - Reject malformed tool calls before execution.

- [x] 10. Serena MCP (read-only) feasibility + safe integration design (optional)

  **What to do**:
  - Document how a read-only MCP could be used to implement file retrieval/search.
  - Guardrail: still enforce path allowlist + redaction before returning content.

- [x] 11. Supplier onboarding via chat UI feasibility assessment

  **What to do**:
  - Use existing `enqueue_onboarding` job type for wizard execution.
  - Determine what additional write tools are required for Step-0 preprocessing in `.claude/skills/supplier-onboarding/SKILL.md`.
  - If too risky, propose "guided mode": assistant outputs a validated wizard input JSON for the user to save manually, then enqueues wizard.

  **References**:
  - `.claude/skills/supplier-onboarding/SKILL.md`
  - `control_plane/tools/repo_files.py:73-104` - onboarding job enqueue
  - `NEW_SUPPLIER_WORKFLOW_GUIDE_DEC_29.md`

### Wave 4 — End-to-End QA + Regression

- [x] 12. E2E QA for category + product list + financial queries

  **What to do**:
  - Run the chat scenarios end-to-end with worker running.
  - Confirm category prompts now behave like product list prompts (LLM planned).
  - Confirm product list refresh still resumes correctly when `run_id` is reused.

  **Acceptance Criteria**:
  - [ ] Product list refresh continuation still works; no regressions.
  - [ ] Category prompt understands `max_products` and respects it (no silent default to 0/2000 unless user asked).
  - [ ] Clarifying Q/A works without treating each reply as a new chat.

---

## Decisions Needed (if you want to override defaults)

Defaults applied unless you override:
- Memory window: last 10 messages (exclude large tool results)
- Persistence across browser refresh: NO (within-session memory only)
- File read scope: allowlist for runtime artifacts + configs (no `*.py` reading)
- Execution: no arbitrary shell; queue-only via worker

---

## Success Criteria

- Category URL prompts are LLM-planned and non-robotic.
- Within the same chat, the assistant remembers context and handles clarifications naturally.
- Assistant can answer informational questions grounded in runtime artifacts.
- All write actions still require confirmation.
- Product list refresh behavior is preserved.
