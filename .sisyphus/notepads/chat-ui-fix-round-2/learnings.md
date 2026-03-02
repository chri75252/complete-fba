# Chat UI Fix Round 2 - Learnings

## 2026-02-25 - Task 1 & Task 2 Execution

### Task 1: Memory Limits - ALREADY COMPLETE
The memory limit increases (50 msgs, 10000 chars, 200000 total) and tool_result keys were already implemented in the current codebase:
- `_sanitize_chat_history` function already had updated defaults
- Tool result summary keys already included: merged_config, categories, report_path, row_count, count, path

### Task 2: Context Injection - COMPLETED
Successfully implemented run resumption via context injection:

1. **chat_orchestrator.py** - Added Streamlit session state extraction in `plan_tool_call`:
   - Extracts `last_run_id` from `st.session_state`
   - Extracts `last_sandbox_supplier` from `st.session_state`
   - Injects both into `planner_hints` dict for LLM to use
   - Wrapped in try/except to handle non-Streamlit contexts gracefully

2. **chat_panel.py** - Added session state persistence:
   - When `enqueue_run` succeeds, now saves `sandbox_supplier` to `st.session_state["last_sandbox_supplier"]`
   - This enables the LLM to know which supplier was last run for "resume that run" requests

### Verification
- `python -c "import control_plane.chat_orchestrator"` passes without error
- Syntax validated successfully

---

## 2026-02-25 - Task 3: Planner Prompt Rewrite

### Task 3: SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md Rewrite - COMPLETED
Successfully rewrote the planner prompt with all required changes:

1. **Removed "Local Ollama" references** - Changed to "MiniMax M2.5 planner calls" throughout
2. **Added Tool Routing Rules section** - Explicit guidance on when to use `query_financial` vs `read_repo_file`:
   - `query_financial`: profitability, ROI, fees, margins
   - `read_repo_file`: viewing, inspecting, reading specific files
   - Added routing table with examples
3. **Added Resuming a Cancelled Run section** - Explained `sandbox_suffix` parameter:
   - How to extract it from original run
   - How to pass it to `enqueue_run` for automatic resume
   - Critical mapping to processing state file
4. **Added Expected Outputs section** - Dynamic output determination:
   - Instructs LLM to read runner scripts and workflow code
   - Lists typical output file paths
   - Emphasizes dynamic vs static templates
5. **Added Writing Output Files section** - Explains `write_output_file` tool:
   - Valid paths: `OUTPUTS/CONTROL_PLANE/reports/` and `OUTPUTS/PRODUCTS_LISTS/`
   - Path validation to prevent directory traversal
6. **Updated Output JSON Contract** - Added optional `expected_outputs` array field
   - Added to JSON schema with example
   - Added note about it being optional

### Changes Made
- File: `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- Lines expanded from 85 to 170
- Added 5 new sections with proper markdown formatting
- Maintained existing sections (Category URL Handling, max_products, Product List Refresh, Read-only Rules)

### Verification
- File read back successfully with all sections intact
- JSON contract properly formatted with new optional field
- All routing rules and examples clearly documented

---

## 2026-02-25 - Task 6: write_output_file Tool Creation - COMPLETED

### Task 6: New Output Writer Tool - COMPLETED
Successfully created the new `write_output_file` tool in `control_plane/tools/output_writer.py`:

1. **File Created**: `control_plane/tools/output_writer.py`
2. **Functionality**:
   - Accepts `repo_root`, `rel_path`, `content`, and optional `overwrite` parameter
   - Validates paths against allowed directories: `OUTPUTS/CONTROL_PLANE/reports` and `OUTPUTS/PRODUCTS_LISTS`
   - Prevents directory traversal attacks via path resolution validation
   - Creates parent directories as needed
   - Returns structured dict with `ok`, `path`, `rel_path`, `size` on success
   - Returns appropriate error dict on failure (missing content, path not allowed, file exists)

3. **Verification**
   - Import test passed: `python -c "from control_plane.tools.output_writer import write_output_file"` succeeded

---

## 2026-02-25 - Task 7: Create get_run_outputs Tool

### Task 7: Build get_run_outputs Tool - COMPLETED

Created new tool `control_plane/tools/run_outputs.py` with the `get_run_outputs` function:

1. **Function Purpose**: Scan filesystem for all artifacts produced by a specific run_id
2. **Artifacts Checked**:
   - Status JSON, log, overrides directory
   - Job JSON (done/failed/pending/running)
   - Processing states (OUTPUTS/CACHE/processing_states/)
   - Linking maps (OUTPUTS/FBA_ANALYSIS/linking_maps/)
   - Cached products (OUTPUTS/cached_products/)
   - Financial reports (OUTPUTS/FBA_ANALYSIS/financial_reports/)
3. **Key Features**:
   - Extracts sandbox_id from first 8 chars of run_id
   - Scans for files matching sandbox_id pattern
   - Attempts to get supplier info from status JSON
   - Returns file list with label, path, rel_path, size, type

### Verification
- `python -c "from control_plane.tools.run_outputs import get_run_outputs"` passes without error

---

## 2026-02-25 - Task 9: Log Consolidation

### Task 9: Log Consolidation - COMPLETED

Implemented log consolidation to fix dashboard view by ensuring logs are available in the control plane folder:

1. **control_plane/worker.py** - Added environment variable injection:
   - Line 345: `env["CONTROL_PLANE_LOG_PATH"] = str(log_path)`
   - Placed just after `with open(log_path, "w", encoding="utf-8") as log_file:`
   - Injects the log file path into the runner's environment

2. **utils/logger.py** - Added env var check and FileHandler:
   - Extracted handlers list to variable
   - Added check for `os.environ.get("CONTROL_PLANE_LOG_PATH")`
   - If found, appends FileHandler in mode="a" (append mode)
   - This clones structured output to the control plane folder

### Changes Made
- `worker.py`: +1 line (env injection)
- `logger.py`: Refactored 6-line inline handlers list into 9-line variable with conditional append

### Verification
- `python -m py_compile control_plane/worker.py utils/logger.py` passes without error
- Both files have valid Python syntax

---

## 2026-02-25 - Task 4 & 5: Allowlist and Size Expansion

### Task 4 & 5: repo_files.py Modifications - COMPLETED

Successfully applied all required changes to `control_plane/tools/repo_files.py`:

1. **Raised DEFAULT_MAX_BYTES**: Changed from `200_000` to `1_000_000` (1MB limit)

2. **Expanded _ALLOWED_READ_DIR_PREFIXES** with 7 new directories:
   - OUTPUTS/CONTROL_PLANE/reports/
   - OUTPUTS/CONTROL_PLANE/overrides/
   - OUTPUTS/FBA_ANALYSIS/amazon_cache/
   - OUTPUTS/cached_products/
   - OUTPUTS/PRODUCTS_LISTS/
   - tools/
   - utils/
   - control_plane/

3. **Expanded _ALLOWED_LIST_DIRS** with same 7 directories (without trailing slashes)

4. **Updated _is_allowed_config_json**: Added check for `run_custom_*.py` files

### Verification
- `python -c "import control_plane.tools.repo_files"` passes without error
- All tuple definitions maintain proper trailing commas

---

## 2026-02-25 - Task 8: Tool Registration

### Task 8: Register New Tools in chat_orchestrator.py and tools/__init__.py - COMPLETED

Successfully registered the two new tools (`get_run_outputs` and `write_output_file`) in the orchestrator:

1. **control_plane/tools/__init__.py** - Added imports and exports:
   - Added imports: `from .output_writer import write_output_file`
   - Added imports: `from .run_outputs import get_run_outputs`
   - Added both functions to `_touch_exports()` tuple

2. **control_plane/chat_orchestrator.py** - Complete registration:
   - Added imports for `write_output_file` and `get_run_outputs`
   - Added `get_run_outputs` to `READ_TOOLS` dict
   - Added `write_output_file` to `WRITE_TOOLS` dict
   - Added schemas to `tools_desc` in `build_prompt`:
     - `write_output_file`: params include rel_path, content, overwrite
     - `get_run_outputs`: params include run_id
   - Added execution logic in `execute_tool_call`:
     - `write_output_file`: calls `write_output_file()` with repo_root, rel_path, content, overwrite
     - `get_run_outputs`: calls `get_run_outputs()` with repo_root, run_id
   - Added response formatting in `_fallback_responder`:
     - `write_output_file`: shows path, relative path, size on success
     - `get_run_outputs`: shows run_id, sandbox_id, supplier, file_count, sample files

### Changes Made
- `control_plane/tools/__init__.py`: +4 lines (imports + exports)
- `control_plane/chat_orchestrator.py`: +30 lines (imports, dicts, schemas, execution, responses)

### Verification
- `python -m py_compile control_plane/chat_orchestrator.py` passes
- `python -m py_compile control_plane/tools/__init__.py` passes
- `python -c "import control_plane.chat_orchestrator"` passes
- `python -c "from control_plane.tools import write_output_file, get_run_outputs"` passes
- `'get_run_outputs' in READ_TOOLS` returns True
- `'write_output_file' in WRITE_TOOLS` returns True
