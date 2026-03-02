# Chat UI Fix Round 2 — Implementation Plan

**Status**: DRAFT — awaiting user approval  
**LLM**: MiniMax M2.5 via OpenCode API (1M context, 128K output, strong reasoning)  
**Priority**: Making the chat UI as best, efficient, useful as possible  

---

## Metis/Momus Gap Analysis & Core Rationale

### 1. Dynamic Expected Outputs (NO Static Templates)
**Metis Review**: The previous plan correctly identified that we must rip out the rigid template in the prompt, but it missed explicit `list_repo_dir` expansion for source exploration.
**Solution**: We are opening up `tools/`, `utils/`, and `control_plane/` for the LLM to read and list. The system instructions explicitly instruct the LLM to *read the runner script and workflow code* before making a prediction for `expected_outputs`. 

### 2. Chat Memory Limits vs. M2.5 Context
**Metis Review**: Truncating memory to 10 messages/12KB is crippling for a 1M token context model.
**Solution**: Expand to 50 messages, 10k chars per message, 200k chars total in `chat_orchestrator.py`. This leaves ~950k tokens free for file reads and reasoning while ensuring robust conversational memory.

### 3. Run Resumption via Context (No New Resume Tool)
**Momus Critique**: Building a redundant `resume_run` tool is bad architecture since `enqueue_run` natively accepts a `sandbox_suffix`.
**Solution**: Inject `last_run_id` and `last_sandbox_supplier` into the hidden `planner_hints`. Update the prompt to instruct the LLM to map a user request of "resume that run" to an `enqueue_run` action with the original `sandbox_suffix`. State management handles the rest naturally.

### 4. File Output Generation (Write Tools)
**User Requirement**: The LLM must be able to generate output files like Markdown reports or JSON lists of products.
**Solution**: Create `write_output_file` (`output_writer.py`). It validates paths to safely allow writes only to `OUTPUTS/CONTROL_PLANE/reports` and `OUTPUTS/PRODUCTS_LISTS`. Path traversal vulnerabilities are handled natively via python's `.resolve().relative_to()`.

### 5. Log Consolidation
**Issue**: Logs were splitting between stdout (`OUTPUTS/CONTROL_PLANE/logs/`) and structured logs (`logs/debug/`), breaking the dashboard view.
**Solution**: Inject `CONTROL_PLANE_LOG_PATH` from `worker.py` into the runner environments so `utils/logger.py` can clone structured output directly to the control plane folder.

---

## Tasks (in priority order)

### P0 — Foundation & Core Intelligence

- [x] Task 1: Increase chat memory limits (M2.5 upgrade)
- [x] Task 2: Inject last_run_id + sandbox_supplier into planner hints
- [x] Task 3: Rewrite planner instructions (`SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`) for routing, resume, and dynamic outputs
- [x] Task 4: Expand `read_repo_file` allowlist to include source directories and cache folders
- [x] Task 5: Raise `DEFAULT_MAX_BYTES` to 1MB

### P1 — Write Capabilities & Data Access

- [x] Task 6: Build `write_output_file` tool in `output_writer.py`
- [x] Task 7: Build `get_run_outputs` tool in `run_outputs.py`
- [x] Task 8: Register new tools in `chat_orchestrator.py` and `tools/__init__.py`

### P2 — Infrastructure

- [x] Task 9: Log consolidation (inject ENV var in `worker.py`, read it in `utils/logger.py`)
- [x] Task 10: Stale jobs cleanup (move 7 orphaned jobs manually)

---

## Technical Diffs (The Implementation)

### Task 1: Memory Limits (`chat_orchestrator.py`)
```diff
 def _sanitize_chat_history(
-    max_messages: int = 10,
-    max_content_chars: int = 2000,
-    max_total_chars: int = 12000,
+    max_messages: int = 50,
+    max_content_chars: int = 10000,
+    max_total_chars: int = 200000,
 ) -> list[dict[str, Any]]:
...
             for key in (
                 "ok",
                 "error",
                 "run_id",
                 "sandbox_supplier",
                 "message",
                 "job_path",
                 "log_path",
+                "merged_config",
+                "categories",
+                "report_path",
+                "row_count",
+                "count",
+                "path",
             ):
```

### Task 2: Context Injection (`chat_orchestrator.py` & `dashboard/chat_panel.py`)
`chat_orchestrator.py`:
```diff
         planner_hints["parsed_constraints"] = _parse_runtime_constraints(user_text)
 
+    try:
+        import streamlit as st
+        last_run_id = st.session_state.get("last_run_id")
+        if isinstance(last_run_id, str) and last_run_id.strip():
+            planner_hints["last_run_id"] = last_run_id.strip()
+        last_sandbox = st.session_state.get("last_sandbox_supplier")
+        if isinstance(last_sandbox, str) and last_sandbox.strip():
+            planner_hints["last_sandbox_supplier"] = last_sandbox.strip()
+    except Exception:
+        pass
```

`dashboard/chat_panel.py`:
```diff
                     st.session_state["last_run_id"] = result["run_id"]
+                    if isinstance(result.get("sandbox_supplier"), str):
+                        st.session_state["last_sandbox_supplier"] = result["sandbox_supplier"]
```

### Task 3: Planner Prompt Rewrite (`SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`)
*(Will completely rewrite to include explicit tool routing tables, dynamic expected output instructions via source reading, and resume instructions via suffix reuse. Removing all Ollama references.)*

### Task 4 & 5: Allowlist and Size Expansion (`control_plane/tools/repo_files.py`)
```diff
-DEFAULT_MAX_BYTES = 200_000
+DEFAULT_MAX_BYTES = 1_000_000
...
 _ALLOWED_READ_DIR_PREFIXES: tuple[str, ...] = (
+    "OUTPUTS/CONTROL_PLANE/reports/",
+    "OUTPUTS/FBA_ANALYSIS/amazon_cache/",
+    "OUTPUTS/cached_products/",
+    "OUTPUTS/PRODUCTS_LISTS/",
+    "tools/",
+    "utils/",
+    "control_plane/",
...
+    if rpl.startswith("run_custom_") and rpl.endswith(".py"):
+        return True
```

### Task 6: `write_output_file` Tool
Will create `control_plane/tools/output_writer.py` strictly gating writes to `OUTPUTS/CONTROL_PLANE/reports` and `OUTPUTS/PRODUCTS_LISTS` via python `.resolve().relative_to(repo_root)`.

### Task 7: `get_run_outputs` Tool
Will create `control_plane/tools/run_outputs.py` to scan `OUTPUTS/` subdirectories and aggregate all files associated with a single run's ID for dynamic verification.

### Task 8: Tool Registration
Will import both new functions into `__init__.py`, update `READ_TOOLS` and `WRITE_TOOLS` in `chat_orchestrator.py`, add them to the `build_prompt` JSON schema list, and implement their caller pathways in `execute_tool_call()`.

### Task 9: Log Consolidation
`worker.py`:
```diff
                 with open(log_path, "w", encoding="utf-8") as log_file:
+                    env["CONTROL_PLANE_LOG_PATH"] = str(log_path)
```
`utils/logger.py`:
```diff
         # Configure logging
+        handlers = [
+            logging.StreamHandler(),
+            logging.FileHandler(debug_log_file, mode="w", encoding="utf-8"),
+        ]
+        cp_log_path = os.environ.get("CONTROL_PLANE_LOG_PATH")
+        if cp_log_path:
+            handlers.append(logging.FileHandler(cp_log_path, mode="a", encoding="utf-8"))
+
         logging.basicConfig(
             level=log_level,
             format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
-            handlers=[
-                logging.StreamHandler(),
-                logging.FileHandler(debug_log_file, mode="w", encoding="utf-8"),
-            ],
+            handlers=handlers,
             force=True,
         )
```