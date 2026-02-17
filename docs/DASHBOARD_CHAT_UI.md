# Dashboard & Chat UI Architecture

This document describes the architecture, layout, and workflows of the FBA Analytics Dashboard, focusing on the Chat UI and Operator Control Plane.

## UI Layout

The main entry point is `dashboard/app_fixed.py`. The interface is organized into three primary tabs:

1.  **Dashboard**: Real-time monitoring of system health, matching performance, and financial metrics.
2.  **Operator**: Control plane for creating and monitoring processing jobs.
3.  **Chat**: Natural language interface for system interaction and automated task execution.

The sidebar contains global configuration settings, including the **Base Directory** (auto-detected), **Supplier** selection, and **Auto Refresh** interval (with safety controls to prevent rapid refresh loops).

## Chat UI Architecture

The Chat UI (`dashboard/chat_panel.py`) provides a conversational interface to the FBA system.

### Persistence
- **Session-Only Persistence**: Messages are stored in `st.session_state["chat_messages"]`. They persist during the current browser session but are not saved permanently to disk.

### Execution Workflow & Gating
- **Confirmation Gating**: Actions that modify the system state or initiate long-running jobs (e.g., `enqueue_product_list_refresh`) require explicit user confirmation.
- **Pending Tool Calls**: When the LLM plans a "write" action, it is stored in `st.session_state["pending_tool_call"]`. The UI displays a confirmation dialog with tool parameters and expected outputs.
- **Natural Language Parameter Updates**: Users can update parameters of a pending tool call (e.g., "set max products to 10") before confirming. The system uses regex and re-parsing to update the `pending_tool_call` object.

### Integration
- **LLM Providers**: Configurable via `CONTROL_PLANE_LLM_PROVIDER` (OpenAI, Anthropic, Ollama, etc.).
- **RAG Index**: Integrates with a RAG index (`system_index.json`) for context-aware responses regarding codebase and status.

## Operator Tab Workflow

The Operator Control Plane (`dashboard/operator_control_plane.py` or `dashboard/pages/01_Operator_Control_Plane.py`) allows manual job orchestration.

### Run Job Creation
1.  **Workflow Selection**: Select from available supplier workflows defined in `config/system_config.json`.
2.  **Category Configuration**:
    - **Selection**: Multiselect from predefined category lists.
    - **Manual Entry**: Paste custom category URLs directly into a text area.
3.  **Limits**: Set `max_products` and `max_products_per_category`.
4.  **Job Dispatch**: Uses `JobManager` to create a `run_id`, write override configuration files, and enqueue the job for the worker.

### Monitoring & Financials
- **Run Monitor**: Select a `run_id` to view its current status (JSON) and a live tail of the execution log.
- **Financial Query**: Interface for querying profitability data (ROI, Net Profit) for specific suppliers or EANs.

## Debugging UI Issues

### Common Data Issues
- **Missing Data Files**: If the dashboard shows "—" or error panels, use the `validate_supplier_data` helper in `app_fixed.py` to check for missing state files, linking maps, or financial directories.
- **Path Resolution**: Ensure the `Base Directory` in the sidebar correctly points to the root of the FBA system.

### Browser & Refresh Issues
- **Refresh Loops**: `app_fixed.py` includes logic to disable auto-refresh if data loading errors occur, preventing infinite reloading.
- **UI Lag**: The log panel is limited to the last 50 lines to prevent performance degradation with large log files.

### LLM & Chat Issues
- **Provider Errors**: Check sidebar and chat panel for LLM provider connection status.
- **RAG Drift**: If chat responses are inaccurate, use the "Refresh system index" or "Build RAG index" buttons in the Chat tab.
