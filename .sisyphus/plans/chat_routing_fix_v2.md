# Implementation Plan: Chat Routing Fixes & Safety Improvements

**Status**: Ready for Implementation
**Trigger**: Critical failure in run `9575c86c` (empty runner script execution)
**Reviewer**: Momus (Approved with amendments)

## 1. Executive Summary

We are fixing a critical regression where the chat system's "pre-router" (which detects category URLs) bypassed necessary parameter resolution, causing it to enqueue jobs with empty `workflow_key` and `runner_script`. This caused the worker to crash (`python ""`).

**Goal**: Ensure `analyze category <url>` commands reliably trigger a **sandboxed workflow run** with the correct runner script and workflow configuration, while providing a rich natural language response.

---

## 2. Technical Specification

### 2.1 Resolution Algorithm (`control_plane/chat_orchestrator.py`)

We will implement a helper `_resolve_workflow_params` to deterministically map `supplier_domain` → `workflow_key` → `runner_script`.

**Logic Flow:**
1.  **Inputs**: `supplier_domain` (e.g., `angelwholesale.co.uk`), `repo_root`.
2.  **Step 1: Find Workflow Key**
    *   Load `config/system_config.json`.
    *   Iterate `workflows` values.
    *   Find entry where `entry["supplier_name"] == supplier_domain`.
    *   Result: `workflow_key` (e.g., `angelwholesale_workflow`).
    *   *Error handling*: If not found, raise `ValueError("Supplier not configured")`.
3.  **Step 2: Find Runner Script**
    *   Load `OUTPUTS/CONTROL_PLANE/index/system_index.json`.
    *   Get list `inventory.runners`.
    *   **Matching Strategy** (in order):
        1.  **Exact Domain Match (Hyphenated)**: Does runner contain `supplier_domain.replace(".", "-")`? (Matches `angelwholesale-co-uk`)
        2.  **Workflow Key Base Match**: Does runner contain `workflow_key.replace("_workflow", "")`? (Matches `poundwholesale` from `poundwholesale_workflow`)
        3.  **Domain Base Match**: Does runner contain `supplier_domain.split(".")[0]`? (Matches `clearance_king`)
    *   *Selection*: Pick the first match.
    *   *Error handling*: If no match, raise `ValueError("No runner script found")`.

### 2.2 Validation Layers (Fail Fast)

| Layer | File | Action |
| :--- | :--- | :--- |
| **1. Pre-Router** | `chat_orchestrator.py` | Catch `ValueError` from resolution. Return `ask_clarify` tool instead of `enqueue_run`. |
| **2. Enqueue** | `control_plane/tools/jobs.py` | In `enqueue_run_job`, raise `ValueError` if `runner_script` is empty/None. |
| **3. Worker** | `control_plane/worker.py` | Before `subprocess.Popen`, check `if not os.path.exists(runner_script)`. If missing, write `state="failed"` to status and return. |

### 2.3 UX Improvements

*   **Pre-router**: Construct a detailed `explanation` string for the `ToolCall`.
    *   *Template*: "I'm starting a sandboxed analysis for [Supplier]. I've identified [N] category URLs. This will run [Runner Script] with workflow [Key]."

---

## 3. Implementation Steps (Diffs)

### Step 1: Update `control_plane/chat_orchestrator.py`

**Add Helper:**
```python
def _resolve_workflow_params(repo_root: Path, supplier_domain: str) -> tuple[str, str]:
    # Load config
    sys_cfg = read_json(repo_root / "config" / "system_config.json")
    workflows = sys_cfg.get("workflows", {})
    
    # 1. Map domain -> workflow_key
    workflow_key = next((k for k, v in workflows.items() if v.get("supplier_name") == supplier_domain), None)
    if not workflow_key:
        raise ValueError(f"Supplier '{supplier_domain}' is not configured in system_config.json")

    # 2. Map workflow_key -> runner_script
    idx_path = repo_root / "OUTPUTS" / "CONTROL_PLANE" / "index" / "system_index.json"
    if not idx_path.exists():
        # Fallback globbing if index missing
        runners = [p.name for p in repo_root.glob("run_custom_*.py")]
    else:
        runners = read_json(idx_path).get("inventory", {}).get("runners", [])

    # Matching heuristics
    # A: angelwholesale.co.uk -> angelwholesale-co-uk
    domain_hyphen = supplier_domain.replace(".", "-")
    # B: poundwholesale_workflow -> poundwholesale
    key_base = workflow_key.replace("_workflow", "")
    
    runner = next((r for r in runners if domain_hyphen in r), None)
    if not runner:
        runner = next((r for r in runners if key_base in r), None)
    
    if not runner:
        raise ValueError(f"No runner script found matching '{supplier_domain}' or key '{workflow_key}'")
        
    return workflow_key, runner
```

**Update `plan_tool_call` Pre-router block:**
```python
    # Inside plan_tool_call, before LLM...
    category_urls = _extract_category_urls(user_text)
    if category_urls:
        # Infer domain...
        supplier_domain = _infer_supplier_domain_from_url(category_urls[0]) # Implementation needed
        
        try:
            workflow_key, runner_script = _resolve_workflow_params(repo_root, supplier_domain)
            
            # Success - Enqueue
            return ToolCall(
                name="enqueue_run",
                params={
                    "supplier_domain": supplier_domain,
                    "category_urls": category_urls,
                    "workflow_key": workflow_key,
                    "runner_script": runner_script,
                    "max_products": 0, # Default
                    "max_products_per_category": 2000, # Default
                    "notes": "User requested category analysis via chat"
                },
                explanation=f"Starting analysis for {len(category_urls)} categories on {supplier_domain}. Using runner '{runner_script}'."
            ), {}
            
        except ValueError as e:
            # Failure - Ask Clarify
            return ToolCall(
                name="ask_clarify",
                params={
                    "user_text": user_text,
                    "error_context": str(e)
                },
                explanation=f"I found category URLs, but I can't start the run: {str(e)}. Please verify the supplier configuration."
            ), {}
```

### Step 2: Update `control_plane/tools/jobs.py`

**Add Assertion in `enqueue_run_job`:**
```python
def enqueue_run_job(..., runner_script: str, ...):
    if not runner_script or not runner_script.strip():
        raise ValueError("Cannot enqueue job: runner_script is empty")
    # ... existing code ...
```

### Step 3: Update `control_plane/worker.py`

**Add Check in Execution Loop:**
```python
            if job.get("job_type") == job_types.JOB_TYPE_RUN_WORKFLOW:
                runner_script = str(job.get("runner_script") or "")
                
                # SAFETY CHECK
                if not runner_script or not (paths.repo_root / runner_script).exists():
                     status["state"] = "failed"
                     status["error"]["summary"] = f"Runner script missing: {runner_script}"
                     write_json_atomic(status_path, status)
                     _move_job(running_job_path, paths.jobs_failed)
                     _release_lock(paths.active_lock_file)
                     continue
                     
                # ... proceed to cmd setup ...
```

---

## 4. Verification Plan

1.  **Static**: Run `python -m py_compile ...` on modified files.
2.  **Unit Logic**: Create a small script `debug_resolve.py` to test `_resolve_workflow_params` against your actual config files.
3.  **End-to-End**:
    *   Input: `analyze this category: https://angelwholesale.co.uk/Category/Baby-Clothing`
    *   Verify UI: Shows "Starting analysis... Using runner 'run_custom_angelwholesale-co-uk.py'"
    *   Verify Job: JSON contains `runner_script: "run_custom_angelwholesale-co-uk.py"`
    *   Verify Worker: Log shows Python execution starting (no `__main__` error).

