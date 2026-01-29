# Draft: PRD 03 Natural Language Chat Analysis & Update

## Requirements (confirmed from user request)

1. **Analyze PRD_03_NATURAL_LANGUAGE_CHAT.md** - Deep analysis of current PRD
2. **Reconcile with critique/observations** - Integrate architectural decisions:
   - Sandbox runs (category vs product-list flows)
   - No core script edits constraint
   - Existing control_plane + dashboard chat
3. **Research Qwen3-8B + Ollama** - Best practices for:
   - Tool calling / function calling
   - JSON structured output
   - Thinking mode (`think=True`)
   - Local LLM reliability constraints
4. **Deliverables**:
   - Updated PRD document
   - Comprehensive report

## Technical Decisions (from code analysis)

### Current Implementation State
- **providers.py**: Already has `generate_with_tools()` and `generate_text()` methods implemented
- **chat_orchestrator.py**: Still uses old `plan_tool_call()` with JSON-only output
- **chat_panel.py**: Renders JSON in expanders but lacks natural language flow
- **ToolCall dataclass**: Currently only has `name` and `params` (missing `explanation`, `thinking`)

### Key Constraints (from AGENTS.md and user requirements)
- NO edits to `tools/` or `utils/` directories
- NO modifications to main OUTPUTS artifacts
- Sandbox run isolation via `supplier_domain__sandbox__{run_id}`
- Confirmation gating for write operations already exists
- Single-run lock exists: `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`

### Ollama/Qwen3 Research Findings

1. **Tool Calling API** (from Ollama docs):
   - Endpoint: `POST /api/chat` with `tools` array
   - Response includes: `message.content`, `message.thinking`, `message.tool_calls`
   - Use `think=True` for reasoning trace
   - Tool result goes back as `{"role": "tool", "tool_name": "...", "content": "..."}`

2. **Streaming with Tools** (critical for UX):
   - Ollama supports streaming tool calls since May 2025
   - Accumulate `thinking`, `content`, `tool_calls` from stream chunks
   - Non-streaming is simpler for deterministic execution

3. **Best Practices**:
   - Temperature 0.3 for tool calling (not 0 to allow flexibility)
   - Include tool schema in system prompt for grounding
   - Two-phase: (1) LLM selects tool, (2) Post-execution summarization

## Risk Management Areas (from user requirements)

1. **Zero interference with existing workflow**
   - Mitigation: Sandbox isolation, no core script edits
   - PRD already specifies `control_plane/` and `dashboard/` only

2. **Strict deterministic tool execution**
   - Mitigation: Tools are Python functions, LLM only selects/parameterizes
   - Current `execute_tool_call()` is already deterministic

3. **Confirmation gating**
   - Status: Already implemented in `chat_panel.py` for write tools
   - PRD proposes no changes to this

4. **Schema drift prevention**
   - Risk: LLM may hallucinate tool parameters
   - Mitigation: Pydantic validation, fallback to `ask_clarify`
   - Current code already has this pattern

5. **Local LLM reliability constraints**
   - Risk: Qwen3-8B may fail to call tools correctly
   - Mitigation: Fallback to `ask_clarify`, robust error handling
   - Temperature tuning, explicit tool schemas

## Scope Boundaries

### IN SCOPE
- Analysis of PRD_03 against current implementation
- Reconciliation with architectural decisions
- Qwen3-8B/Ollama best practices research
- Updated PRD with risk mitigations
- Comprehensive report document

### EXPLICITLY OUT OF SCOPE
- Any code implementation
- Any file edits beyond plan/report markdown
- Testing or verification

## Open Questions

1. **Streaming vs Non-streaming**: PRD says "No streaming UI (future enhancement)" - confirm this is still the stance
2. **Model choice**: PRD says Qwen3-8B, but current code defaults to `llama3.1` - which to use?
3. **Thinking mode display**: PRD shows optional thinking expander - is this desired?
4. **Category vs Product-list flows**: How does this affect tool schema?

## Key PRD Gaps Identified

1. **Provider method already exists** - PRD assumes we need to add `generate_with_tools()` but it's already implemented
2. **Missing error handling spec** - What if Ollama is down? What if tool_calls is empty?
3. **Missing schema validation** - No Pydantic models for tool call responses
4. **Missing rate limiting** - No mention of request throttling for LLM calls
5. **Missing token limits** - No discussion of context window management
6. **Missing fallback chain** - What if local LLM fails? Use cloud?
