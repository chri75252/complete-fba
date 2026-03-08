# Chat UI LLM Memory & Resumption Fix Plan

## Objective
Fix the Chat UI "amnesia" bug where the LLM forgets the `run_id` of jobs it just created, and fix the backend execution logic so that when the LLM correctly requests to resume an old sandbox, it isn't forced into a new, empty sandbox.

## Target Files
1. `dashboard/chat_panel.py`
2. `control_plane/chat_orchestrator.py`

---

## Fix 1: Persist Tool Results in Chat History (UI Memory)

### The Problem
Currently, when a write-tool (like `enqueue_run`) is executed and approved, the UI saves the LLM's text explanation to `st.session_state["chat_messages"]`, but completely drops the JSON `result` dictionary (which contains the `run_id`). Because the LLM's context is built purely from `chat_messages`, it becomes instantly blind to the job it just started.

### The Fix
In `dashboard/chat_panel.py`, inside the `if st.button("Confirm execute"):` block, we will extract the exact JSON result of the tool execution and explicitly append it to the assistant's message object under the key `"tool_result"`.

### Code Diff Snippet (`dashboard/chat_panel.py`)
```python
@@ -262,8 +262,11 @@
                 # Append write result to scratchpad and clear pending state
                 scratchpad = st.session_state.get("agent_scratchpad", [])
                 scratchpad.append({"role": "observation", "result": result})
                 
                 # Append the tool result to the actual chat history so the LLM remembers the run_id next turn
-                # (Currently missing)
+                st.session_state["chat_messages"].append({
+                    "role": "assistant",
+                    "content": st.session_state["pending_tool_call"].explanation or "Action executed.",
+                    "tool_result": result
+                })

                 st.session_state["agent_scratchpad"] = scratchpad
                 st.session_state["pending_tool_call"] = None
```
*(Note: We will also do the same for the autonomous loop's `final_answer` block around line 114 to ensure all pathways persist memory).*

---

## Fix 2: Allow LLM to Specify Sandbox for Resumption (Backend Trap)

### The Problem
Even if the LLM remembers the `sandbox_suffix` (e.g., `sandbox_17fd6e1d`) and passes it in the `enqueue_run` parameters to resume a job, `execute_tool_call()` in `chat_orchestrator.py` currently forces the generation of a brand new suffix using the new `run_id` (`sandbox_suffix = f"sandbox__{run_id[:8]}"`). This throws the resume request into a blank sandbox.

### The Fix
Modify `execute_tool_call` and `_fallback_expected_outputs_for_enqueue_tool` in `control_plane/chat_orchestrator.py` to respect the `sandbox_suffix` provided by the LLM. It should only generate a new one if the LLM provided nothing, or if the LLM used the explicit schema placeholder `"<optional_for_resuming>"`.

### Code Diff Snippet (`control_plane/chat_orchestrator.py`)
```python
@@ -1300,8 +1300,8 @@
         if not run_id:
             import uuid
             run_id = str(uuid.uuid4())

-        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
-        if not sandbox_suffix:
+        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
+        if not sandbox_suffix or sandbox_suffix == "<optional_for_resuming>":
             sandbox_suffix = f"sandbox__{run_id[:8]}"

         # Build sandbox_supplier for output paths/polling
         sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}"
```

---

## Fix 3: Fix the Schema Prompt Footgun

### The Problem
The JSON schema definition for `enqueue_run` tells the LLM to use `"sandbox_suffix": "sandbox_20260210_143022"` as an example. When the LLM gets lazy, it blindly copies this exact string into fresh runs, causing bizarre collisions with 3-week-old data.

### The Fix
Update the `tools_desc` schema definition in `control_plane/chat_orchestrator.py` to use a safe placeholder string instead of a real historical timestamp.

### Code Diff Snippet (`control_plane/chat_orchestrator.py`)
```python
@@ -495,3 +495,3 @@
                     "max_products_per_category": 10,
-                    "sandbox_suffix": "sandbox_20260210_143022",
+                    "sandbox_suffix": "<optional_for_resuming>",
                     "notes": "initial run"
                 }
```

---

## Execution Steps
1. Apply the patches to `dashboard/chat_panel.py` and `control_plane/chat_orchestrator.py`.
2. Run the local Streamlit agent test script to simulate enqueueing a run, confirming the JSON output is successfully appended to the `chat_messages` array.
3. Simulate a turn 2 ("now cancel the run") and turn 3 ("now resume the run") to mathematically prove the LLM's prompt context now contains the `run_id` and the `sandbox_supplier`.
