# Chat UI Autonomous ReAct Agent: System Architecture & Guardrails

You asked two incredibly important questions:
1.  **Where exactly does the current chat agent live in the codebase?** (Where is the prompt, the tools, the guardrails?)
2.  **Why did earlier AI agents avoid building an autonomous ReAct agent from the start?** (What makes it so hard to build from scratch?)

Here is the exact, file-grounded breakdown of the system we just built, answering both questions.

---

## 1. Where the Agent Lives (The Architecture Map)

The Chat UI LLM is not a single script. It is a sophisticated multi-layer state machine spread across 4 key files.

### A. The Brain (System Prompt & Logic)
**File**: `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
*   **What it is**: The literal text prompt fed to MiniMax M2.5.
*   **What it does**: Tells the LLM it is an autonomous agent, defines its persona, gives it the rules for onboarding suppliers, and provides the exact JSON output format it must use.

### B. The Engine (Tool Registration & Dispatch)
**File**: `control_plane/chat_orchestrator.py`
*   **Registration**: Lines ~45-56 define the `READ_TOOLS`, `WRITE_TOOLS`, and `TERMINAL_TOOLS` allowlists. 
*   **Tool Menu (`tools_desc`)**: Lines ~400+ define the exact JSON schemas that the LLM is allowed to see and use (this is where we fixed the `sandbox_suffix` and `max_bytes` bugs).
*   **The Loop Engine (`agent_plan_step`)**: Lines ~710+. This is the core logic that feeds the "scratchpad" (memory) back to the LLM so it knows what it just did 2 seconds ago. It executes Read tools instantly, but pauses and returns `approval_needed` if the LLM picks a Write tool.

### C. The Brawn (The Actual Tools & Guardrails)
**Folder**: `control_plane/tools/`
*   `repo_files.py`: Houses `read_repo_file` and `list_repo_dir`. Contains the strict `_ALLOWED_READ_DIR_PREFIXES` array that blocks the LLM from reading arbitrary system files (like `.env`).
*   `output_writer.py`: Houses `write_output_file`. Contains `_ALLOWED_WRITE_DIRS` and the `_is_allowed_code_edit` "Prompt Lock" logic that dynamically prevents the LLM from overwriting existing supplier scripts.
*   `tool_param_validation.py`: The final security gate. Even if the LLM hallucinates a valid tool, this script explicitly checks the data types (e.g., verifying `supplier_domain` is a string and not malicious code) before handing it to the system.

### D. The Face (The UI Loop)
**File**: `dashboard/chat_panel.py`
*   **The Autonomous Loop (`_run_agent_loop`)**: Lines ~97+. This is the literal `while` loop that allows the LLM to run up to 10 steps (`MAX_AGENT_STEPS = 10`) consecutively.
*   **The Safety Gate**: Lines ~250+. The code that literally pauses the entire application, renders the "Approve & Execute" button on your screen if the LLM tries to write a file, and resumes the loop when you click it.

---

## 2. Why Earlier Agents Refused to Build This From Scratch

You noted that earlier AI agents aggressively avoided building this autonomous loop when you asked them to, despite you asking for guardrails.

**Why did they refuse?**
Because building an autonomous ReAct loop from scratch inside **Streamlit** is one of the hardest problems in UI engineering.

### The Streamlit Problem
Streamlit is not a normal app framework. It is "rerun-driven." Every time you click a button or type a letter, Streamlit wipes its entire memory and re-runs the entire python script from top to bottom.
*   A naive AI would just write: `while True: agent.think()`
*   In Streamlit, doing this causes the UI to completely freeze. The page locks up, the spinner hangs forever, and the backend duplicates executions until your API credits run out.

### The Finite-State Machine Requirement
To make an autonomous agent work in Streamlit, you cannot just write a prompt. You must build a highly complex **Finite-State Machine** using `st.session_state`.
1.  The agent needs a `scratchpad` to remember its loop across UI refreshes.
2.  The loop needs a `pending_tool_call` memory bank so that when it pauses to ask for your permission ("Approve & Execute"), it doesn't forget what it was trying to do when you finally click the button 30 seconds later.
3.  The agent needs defense-in-depth security (Prompt rules + Validation layer + Hardcoded path allowlists) because autonomous loops hallucinate exponentially faster than single-turn chats.

### Why "Retrofitting" Worked So Well Today
Earlier agents refused to build it because inventing that entire 4-layer architecture simultaneously (Prompt + Orchestrator + Tools + Streamlit Loop) from scratch overwhelms LLM context and guarantees failure.

The reason we successfully built it today is because we **retrofitted** your existing, highly robust backend. Your `worker.py`, `tool_param_validation.py`, and base tools were already rock-solid. We just had to surgically wrap them in the `_run_agent_loop` state machine.

Building it from scratch is chaos. Retrofitting it onto your well-architected base was precise engineering.

---

## 3. Tool Arsenal, JSON Visibility, and Guardrail Tiers

### A. Tool Arsenal (Autonomous Planner)

**Read tools (9):**
1. `ask_clarify`
2. `query_financial`
3. `show_status`
4. `tail_logs`
5. `show_trace_summary`
6. `read_processing_state`
7. `find_cached_products`
8. `find_linking_entries`
9. `read_amazon_cache_by_asin`

**Write tools (5):**
1. `enqueue_run`
2. `cancel_run`
3. `enqueue_onboarding`
4. `enqueue_product_list_refresh`
5. `write_output_file`

### B. JSON Visibility in the Approve Flow

When the UI shows JSON before execution, that is expected behavior, not a formatting bug. The JSON is the raw structured tool payload (tool name + params) that the chat panel intercepts and renders so the user can explicitly approve the exact write action.

### C. Guardrails (3 Tiers)

**Tier 1 - Path Locking**
- **Read boundaries (`control_plane/tools/repo_files.py`)**:
  - `DEFAULT_MAX_BYTES = 1_000_000` enforces the 1 MB read cap.
  - `_ALLOWED_READ_DIR_PREFIXES` is the hard allowlist that constrains what `read_repo_file` and `list_repo_dir` can access.
- **Write boundaries (`control_plane/tools/output_writer.py`)**:
  - `_ALLOWED_WRITE_DIRS` restricts writes to approved output locations.
  - `_is_allowed_code_edit(...)` is the dynamic prompt lock that only permits narrowly-scoped supplier script edits tied to the active supplier domain.

**Tier 2 - Parameter Validation**
- `control_plane/tools/tool_param_validation.py` enforces schema/type safety on tool params before execution, so malformed or hallucinated payloads are rejected before they can run.

**Tier 3 - Loop Limits (Hard Kill Switch)**
- `dashboard/chat_panel.py` sets `MAX_AGENT_STEPS = 10` and runs `for step_num in range(MAX_AGENT_STEPS)`, which is the hard stop preventing infinite autonomous loops.

## 3. The Tools, Capabilities, and Guardrails

The autonomous LLM is strictly boxed in by three layers of security. Here is exactly what it can do and how it is restricted:

### A. Read Capabilities (The "Eyes")
*   **Tools:** `read_repo_file`, `list_repo_dir`, `find_cached_products`, `find_linking_entries`, `show_status`, `tail_logs`, `read_processing_state`, `get_run_outputs`, `query_financial`.
*   **What it can read:** Logs, financial CSVs (via pandas to bypass size limits), cached product JSONs, linking maps, processing states, generated python runner scripts, and markdown skill files.
*   **The Guardrail:** `control_plane/tools/repo_files.py`. The `_ALLOWED_READ_DIR_PREFIXES` tuple hard-blocks the LLM from reading arbitrary system files (like your API keys in `.env` or root system files).
*   **The Size Guardrail:** A hard `max_bytes` limit of 1MB ensures the LLM cannot crash the UI by attempting to ingest a massive cache file directly into its context window.

### B. Write Capabilities (The "Hands")
*   **Tools:** `write_output_file`, `enqueue_run`, `enqueue_onboarding`, `enqueue_product_list_refresh`, `cancel_run`.
*   **What it can write:** Markdown reports, product list JSONs, and configuration staging files.
*   **The Guardrail (Path Locking):** `control_plane/tools/output_writer.py`. The `_ALLOWED_WRITE_DIRS` strictly confines outputs to `OUTPUTS/CONTROL_PLANE/reports`, `OUTPUTS/PRODUCTS_LISTS`, and the `OUTPUTS/CONTROL_PLANE/jobs/onboarding_staging` directory. 
*   **The Guardrail (Dynamic Prompt Lock):** The `_is_allowed_code_edit` function mathematically prohibits the LLM from overwriting python files (like `run_custom_clearance_king.py`) *unless* the user explicitly passes the matching `supplier_domain`.

### C. The Loop Guardrail (The "Kill Switch")
*   In `dashboard/chat_panel.py`, the `while` loop has a hardcoded `MAX_AGENT_STEPS = 10`. If the LLM gets confused and tries to read the same file 11 times, the UI kills the loop to prevent it from draining your token balance.

---

## 4. UI Rendering: Why JSON is Visible

Even though the Chat UI agent uses a multi-step loop, it still prints JSON when it wants to do something like enqueue a run. 

**Is the JSON actually used?**
Yes. The LLM does not interact with the Python backend via normal conversation. When the LLM decides to trigger a tool, its "thought" is actually a JSON dictionary containing the tool name, the parameters, and its explanation.

**Why does the UI show it to you?**
The Streamlit UI intentionally intercepts this JSON specifically for **Write Tools**. When the LLM decides to perform a dangerous action, the UI pauses the loop, parses that JSON, and displays it inside the `st.markdown("Proposed action requires confirmation:")` block. It shows you the JSON so you can see *exactly* what parameters the LLM is attempting to pass to the FBA backend before you click "Confirm Execute." It is a vital transparency feature.
