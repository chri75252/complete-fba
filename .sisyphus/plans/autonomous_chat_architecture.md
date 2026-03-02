# Autonomous Chat UI Re-architecture Plan
**Status**: DRAFT
**Model Target**: MiniMax M2.5

---

## 1. Goal
Convert the existing 1-to-1 Streamlit Chat UI into an autonomous ReAct (Reason + Act) loop. The LLM must be able to automatically chain multiple tools together (e.g., read a file, process it, write a report, and read the output) without requiring the user to prompt it at every step, while preserving the strict "Approve & Execute" safety gate for write operations.

---

## 2. Core Architectural Pattern (@Oracle)

We will implement a **Step-Function + Synchronous While-Loop** pattern. 
*   **No Async/Generators:** Streamlit crashes with background threads and generators. The loop must run synchronously inside a Streamlit `st.status()` block to show live updates.
*   **The Scratchpad:** All inter-step memory (the tools called and their results during the loop) will be stored in `st.session_state["agent_scratchpad"]`.
*   **The Exit Condition:** A new pseudo-tool called `final_answer` will be introduced. The loop continues until the LLM explicitly calls `final_answer`.

---

## 3. Required Modifications (The Diffs)

### Phase 1: Engine Updates (`control_plane/chat_orchestrator.py`)

**1. Define the Agent State**
We must add a dataclass to manage the loop state.
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentStep:
    kind: str  # "tool_call" | "final_answer" | "approval_needed"
    tool_call: ToolCall | None = None
    text: str | None = None          
    result: dict[str, Any] | None = None
```

**2. Add `final_answer` to the Tool Registry**
In `build_prompt`, we add the termination tool:
```python
        "final_answer": {
            "type": "terminal",
            "params": {"text": "Your complete Markdown response to the user summarizing all actions taken."},
        },
```

**3. Build the `agent_plan_step` function**
This replaces `plan_tool_call` as the primary engine for the loop. It injects the `scratchpad` into the prompt so the LLM remembers what it did 5 seconds ago.
```python
def agent_plan_step(
    user_text: str,
    repo_root: Path,
    scratchpad: list[dict[str, Any]],
    chat_history: list[dict[str, Any]],
    rag_info: dict[str, Any] | None = None,
) -> AgentStep:
    prompt = build_agent_prompt(user_text, repo_root, scratchpad, chat_history, rag_info)
    provider = get_provider()
    data = provider.generate_json(prompt)
    
    tool = str(data.get("tool", "")).strip()
    params = data.get("params") or {}
    
    if tool == "final_answer":
        return AgentStep(kind="final_answer", text=str(params.get("text", "")))
        
    if tool in WRITE_TOOLS:
        tc = ToolCall(name=tool, params=params)
        return AgentStep(kind="approval_needed", tool_call=tc)
        
    tc = ToolCall(name=tool, params=params)
    result = execute_tool_call(tc, repo_root)
    return AgentStep(kind="tool_call", tool_call=tc, result=result)
```

**4. Update Prompt Instructions**
The `SYSTEM_INSTRUCTIONS` must be rewritten from "Pick ONE tool" to:
*"You are an autonomous agent. Use as many read tools as you need sequentially to gather data. When you have achieved the user's goal, you MUST call `final_answer` to output your text to the user."*

---

### Phase 2: UI Updates (`dashboard/chat_panel.py`)

**1. Build the Autonomous Loop**
We must build a loop that limits the LLM to a maximum of 10 steps to prevent infinite token-draining loops (Momus Critique).
```python
MAX_AGENT_STEPS = 10

def _run_agent_loop(user_text: str, base_dir: str) -> None:
    scratchpad = st.session_state.get("agent_scratchpad", [])
    
    with st.status("Agent is thinking...", expanded=True) as status:
        for step_num in range(MAX_AGENT_STEPS):
            step = agent_plan_step(user_text, Path(base_dir), scratchpad, ...)
            
            if step.kind == "final_answer":
                status.update(label="Done", state="complete")
                st.session_state["chat_messages"].append({"role": "assistant", "content": step.text})
                st.session_state["agent_scratchpad"] = [] 
                return
                
            if step.kind == "approval_needed":
                status.update(label="Waiting for approval...", state="running")
                st.session_state["pending_tool_call"] = step.tool_call
                st.session_state["agent_scratchpad"] = scratchpad 
                st.rerun() # Pauses the UI for user click
                return
                
            # Read tool executed
            st.write(f"Step {step_num + 1}: Executed `{step.tool_call.name}`")
            scratchpad.append({"role": "action", "tool": step.tool_call.name})
            scratchpad.append({"role": "observation", "result": step.result})
            
        status.update(label="Step limit reached", state="error")
```

**2. Handle Resumption After Write Approval**
When you click "Confirm Execute", the UI must execute the write tool, append the result to the scratchpad, and immediately resume the loop.
```python
if st.button("Confirm execute"):
    result = execute_tool_call(tool_call, Path(base_dir))
    
    scratchpad = st.session_state.get("agent_scratchpad", [])
    scratchpad.append({"role": "observation", "result": result})
    st.session_state["agent_scratchpad"] = scratchpad
    
    st.session_state["pending_tool_call"] = None
    st.rerun() # Triggers the loop to pick up where it left off
```

---

## 4. Impact on Existing Capabilities

1. **Safety**: **NO CHANGE.** Because `WRITE_TOOLS` trigger `AgentStep(kind="approval_needed")`, the system will STILL pause and throw up the big "Confirm Execute" button before doing anything dangerous. The agent loop cleanly suspends itself and waits for your click.
2. **Standard Workflows (Category/PLR)**: **IMPROVED.** You can now type *"Read setup.txt and trigger the wizard"*, and it will do both steps automatically.
3. **Data Retrieval**: **IMPROVED.** The `respond_to_tool_result` LLM call is completely removed. It is replaced by `final_answer`. The LLM now has full context of *all* tools it ran before responding to you.
4. **Main Scripts**: **PROTECTED.** Zero changes are required to the python FBA scrapers or background workers. All changes are strictly confined to the Streamlit UI and the Orchestrator parser.

---
## Summary of Work
- Edit `control_plane/chat_orchestrator.py` (Add `AgentStep`, `agent_plan_step`, `final_answer`)
- Edit `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` (Update rules for looping)
- Edit `dashboard/chat_panel.py` (Implement `_run_agent_loop` and write-tool resumption)