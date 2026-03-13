import os
import sys
import traceback
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import pandas as pd

# Add the parent directory to sys.path so we can import from dashboard and control_plane
PARENT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PARENT_DIR))

try:
    from dashboard_legacy_streamlit.metrics_core import MetricsLoader, load_metrics
    from control_plane.job_manager import JobManager
except ImportError as e:
    print(f"Error importing metrics/job modules: {e}")

try:
    from control_plane.chat_orchestrator import (
        ToolCall,
        AgentStep,
        agent_plan_step,
        audit_tool_call,
        execute_tool_call,
        _compute_rag_info,
    )
    from control_plane.env_config import ensure_llm_env
    CHAT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Chat modules not available: {e}")
    CHAT_AVAILABLE = False

app = FastAPI(title="Amazon FBA Agent System API")

# ---- In-memory chat session state (mirrors Streamlit session_state) ----
chat_state = {
    "messages": [],
    "scratchpad": [],
    "trace": [],
    "pending_tool_call": None,
    "pending_user_text": None,
    "pending_rag_info": None,
    "last_run_id": None,
    "last_products_path": None,
    "last_supplier_domain": None,
    "last_sandbox_supplier": None,
}


MAX_AGENT_STEPS = 10

class ChatRequest(BaseModel):
    message: str
    supplier: Optional[str] = "poundwholesale.co.uk"

class ApproveRequest(BaseModel):
    approve: bool

# Mount the static directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def get_base_directory():
    """Get the correct base directory for the FBA system"""
    candidates = [
        os.environ.get("FBA_BASE_DIR"),
        str(PARENT_DIR),
        os.getcwd(),
        ".",
    ]
    for candidate in candidates:
        if candidate and os.path.exists(os.path.join(candidate, "OUTPUTS")):
            return candidate
    return os.getcwd()

def validate_supplier_data(base_dir, supplier):
    loader = MetricsLoader(base_dir)
    paths = loader.resolve_paths(supplier)
    issues = []
    if not paths.get("state_file") or not os.path.exists(paths["state_file"]):
        issues.append("State file not found")
    if not paths.get("linking_file") or not os.path.exists(paths["linking_file"]):
        issues.append("Linking map file not found")
    if not paths.get("financial_dir") or not os.path.exists(paths["financial_dir"]):
        issues.append("Financial reports directory not found")
    if not paths.get("logs_dir") or not os.path.exists(paths["logs_dir"]):
        issues.append("Logs directory not found")
    return issues, paths

@app.get("/")
def read_root():
    index_path = Path(__file__).parent / "templates" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "index.html not found"}

@app.get("/api/metrics/{supplier}")
def get_supplier_metrics(supplier: str):
    base_dir = get_base_directory()
    try:
        issues, paths = validate_supplier_data(base_dir, supplier)
        if issues:
            return JSONResponse({
                "error": True,
                "issues": issues,
                "paths": paths,
                "state_metrics": {"state_file_found": False},
                "linking_metrics": {"total_matches": 0},
                "financial_metrics": {"files_scanned": 0},
                "log_data": [[], None]
            })
        
        # We need to serialize paths object cleanly (POSIX paths to str)
        metrics_data = load_metrics(base_dir, supplier)
        
        # Load chart data (sample top 500 for performance)
        chart_data = []
        fin_dir = metrics_data.get("paths", {}).get("financial_dir")
        latest_file = metrics_data.get("financial_metrics", {}).get("latest_file")
        
        if fin_dir and latest_file and os.path.exists(os.path.join(fin_dir, latest_file)):
            try:
                df = pd.read_csv(
                    os.path.join(fin_dir, latest_file),
                    engine='python',
                    on_bad_lines='skip',
                    encoding='utf-8',
                    encoding_errors='replace',
                    nrows=2000  # Cap rows to prevent actual memory exhaustion
                )
                # Send a lightweight version of the data for charts
                if not df.empty:
                    # Clean the data
                    for col in ['SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI',
                                'fba_seller_count', 'fbm_seller_count', 'total_offer_count']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df = df.dropna(subset=['ROI', 'NetProfit']).head(500) # Only up to 500 points
                    
                    # Collect all available columns for charts
                    chart_cols = ['SupplierTitle', 'AmazonTitle', 'SupplierPrice_incVAT',
                                  'SellingPrice_incVAT', 'NetProfit', 'ROI', 'MatchQuality']
                    for extra in ['fba_seller_count', 'fbm_seller_count', 'total_offer_count']:
                        if extra in df.columns:
                            chart_cols.append(extra)
                    chart_cols = [c for c in chart_cols if c in df.columns]
                    chart_data = df[chart_cols].fillna(0).to_dict(orient='records')
            except Exception as e:
                print(f"Error loading CSV for charts: {e}")
                
        metrics_data["chart_data"] = chart_data
        
        # Fix paths types for JSON serialization
        if "paths" in metrics_data:
            for k, v in metrics_data["paths"].items():
                if v is not None:
                    metrics_data["paths"][k] = str(v)
                    
        return metrics_data
    except Exception as e:
        import traceback
        return JSONResponse({"error": True, "issues": [str(e)], "traceback": traceback.format_exc()}, status_code=500)

@app.get("/api/workflows")
def list_workflows():
    import json
    cfg_path = PARENT_DIR / "config" / "system_config.json"
    if not cfg_path.exists():
        return []
    try:
        cfg = json.load(open(cfg_path, "r", encoding="utf-8"))
        workflows = cfg.get("workflows", {})
        out = []
        for key, wf in workflows.items():
            supplier = str(wf.get("supplier_name") or "")
            out.append({"key": key, "supplier": supplier})
        out.sort(key=lambda t: t["key"])
        return out
    except Exception:
        return []

# ---- Chat API Endpoints ----

@app.post("/api/chat")
def chat_send(req: ChatRequest):
    """Run the agent loop for a user message. Returns trace steps and final answer or pending approval."""
    if not CHAT_AVAILABLE:
        return JSONResponse({"error": True, "message": "Chat modules not available. Check LLM provider env vars."}, status_code=503)

    base_dir = get_base_directory()
    repo_root = Path(base_dir)
    user_text = req.message.strip()

    if not user_text:
        return JSONResponse({"error": True, "message": "Empty message"}, status_code=400)

    # If there's a pending approval, tell the user
    if chat_state["pending_tool_call"] is not None:
        return JSONResponse({
            "type": "approval_pending",
            "message": "A pending action is waiting for your approval. Please approve or reject it before sending a new message.",
            "pending_tool": {
                "name": chat_state["pending_tool_call"].name,
                "params": chat_state["pending_tool_call"].params,
                "explanation": chat_state["pending_tool_call"].explanation,
                "expected_outputs": chat_state["pending_tool_call"].expected_outputs,
            }
        })

    try:
        ensure_llm_env()
    except Exception as e:
        return JSONResponse({"error": True, "message": f"LLM environment error: {e}"}, status_code=503)

    # Add user message to history
    chat_state["messages"].append({"role": "user", "content": user_text})
    chat_state["scratchpad"] = []
    chat_state["trace"] = []

    try:
        rag_info, rag_context = _compute_rag_info(user_text)
    except Exception:
        rag_info = {"meta": {}, "chunks": []}
        rag_context = ""

    def event_stream():
        import json as _json
        local_trace = []
        try:
            for step_num in range(MAX_AGENT_STEPS):
                step = agent_plan_step(
                    user_text,
                    repo_root,
                    chat_state["scratchpad"],
                    chat_state["messages"],
                    (rag_info, rag_context),
                    session_state=chat_state,
                )

                if step.kind == "final_answer":
                    chat_state["messages"].append({"role": "assistant", "content": step.text})
                    chat_state["scratchpad"] = []
                    chat_state["trace"] = []
                    yield "data: " + _json.dumps({"type": "final_answer", "text": step.text, "trace": local_trace}) + "\n\n"
                    return

                if step.kind == "approval_needed":
                    tc = step.tool_call
                    chat_state["pending_tool_call"] = tc
                    chat_state["pending_user_text"] = user_text
                    chat_state["pending_rag_info"] = rag_info
                    yield "data: " + _json.dumps({
                        "type": "approval_needed",
                        "trace": local_trace,
                        "pending_tool": {
                            "name": tc.name,
                            "params": tc.params,
                            "explanation": tc.explanation,
                            "expected_outputs": tc.expected_outputs,
                        }
                    }) + "\n\n"
                    return

                # State tracking for context injection
                if step.result and step.result.get("ok"):
                    if isinstance(step.result.get("run_id"), str) and step.result.get("run_id"):
                        chat_state["last_run_id"] = step.result["run_id"]
                    if isinstance(step.result.get("sandbox_supplier"), str):
                        chat_state["last_sandbox_supplier"] = step.result["sandbox_supplier"]
                    supplier_domain = step.tool_call.params.get("supplier_domain")
                    if isinstance(supplier_domain, str) and supplier_domain.strip():
                        chat_state["last_supplier_domain"] = supplier_domain.strip()
                    products_path = step.tool_call.params.get("products_path")
                    if isinstance(products_path, str) and products_path.strip():
                        chat_state["last_products_path"] = products_path.strip()
                    elif step.tool_call.name == "build_product_list_from_cached":
                        rel_path = step.result.get("rel_path")
                        if isinstance(rel_path, str) and rel_path.strip():
                            chat_state["last_products_path"] = rel_path.strip()

                # Yield trace step IMMEDIATELY as it completes (the key SSE behaviour)
                trace_entry = {
                    "step": step_num + 1,
                    "tool": step.tool_call.name if step.tool_call else "unknown",
                    "explanation": step.tool_call.explanation if step.tool_call else None,
                    "result": _safe_serialize(step.result) if step.result else None,
                }
                local_trace.append(trace_entry)
                yield "data: " + _json.dumps({"type": "trace_update", "step": trace_entry}) + "\n\n"

                chat_state["scratchpad"].append({"role": "action", "tool": step.tool_call.name, "params": step.tool_call.params})
                chat_state["scratchpad"].append({"role": "observation", "result": step.result})

            # Step limit reached
            fallback_msg = "I reached the maximum number of reasoning steps. See the trace for what I found."
            chat_state["messages"].append({"role": "assistant", "content": fallback_msg})
            chat_state["scratchpad"] = []
            yield "data: " + _json.dumps({"type": "final_answer", "text": fallback_msg, "trace": local_trace}) + "\n\n"

        except Exception as e:
            yield "data: " + _json.dumps({"type": "error", "message": f"Agent error: {str(e)}", "traceback": traceback.format_exc()}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")



@app.post("/api/chat/approve")
def chat_approve(req: ApproveRequest):
    """Approve or reject the pending write-tool action."""
    if not CHAT_AVAILABLE:
        return JSONResponse({"error": True, "message": "Chat modules not available."}, status_code=503)

    tc = chat_state["pending_tool_call"]
    if tc is None:
        return JSONResponse({"error": True, "message": "No pending action to approve."}, status_code=400)

    user_text = chat_state["pending_user_text"] or ""
    rag_info = chat_state["pending_rag_info"] or {}
    base_dir = get_base_directory()
    repo_root = Path(base_dir)

    if not req.approve:
        # User rejected
        chat_state["pending_tool_call"] = None
        chat_state["pending_user_text"] = None
        chat_state["pending_rag_info"] = None
        chat_state["scratchpad"] = []
        chat_state["trace"] = []
        chat_state["messages"].append({"role": "assistant", "content": "Action cancelled by user."})
        return {"type": "cancelled", "text": "Action cancelled by user."}

    # Execute the approved tool
    try:
        result = execute_tool_call(tc, repo_root)
        audit_tool_call(user_text, tc, result, rag_info)

        if result.get("ok"):
            if isinstance(result.get("run_id"), str) and result.get("run_id"):
                chat_state["last_run_id"] = result["run_id"]
            if isinstance(result.get("sandbox_supplier"), str):
                chat_state["last_sandbox_supplier"] = result["sandbox_supplier"]

            supplier_domain = tc.params.get("supplier_domain")
            if isinstance(supplier_domain, str) and supplier_domain.strip():
                chat_state["last_supplier_domain"] = supplier_domain.strip()

            products_path = tc.params.get("products_path")
            if isinstance(products_path, str) and products_path.strip():
                chat_state["last_products_path"] = products_path.strip()
            elif tc.name == "build_product_list_from_cached":
                rel_path = result.get("rel_path")
                if isinstance(rel_path, str) and rel_path.strip():
                    chat_state["last_products_path"] = rel_path.strip()


        chat_state["pending_tool_call"] = None
        chat_state["pending_user_text"] = None
        chat_state["pending_rag_info"] = None
        chat_state["scratchpad"] = []
        chat_state["trace"] = []

        chat_state["messages"].append({
            "role": "assistant",
            "content": f"Action `{tc.name}` executed successfully.",
        })

        return {
            "type": "executed",
            "tool": tc.name,
            "result": _safe_serialize(result),
        }
    except Exception as e:
        return JSONResponse({
            "error": True,
            "message": f"Execution error: {str(e)}",
            "traceback": traceback.format_exc(),
        }, status_code=500)


@app.get("/api/chat/history")
def chat_history():
    """Return the current chat message history."""
    return {"messages": chat_state["messages"]}


@app.post("/api/chat/reset")
def chat_reset():
    """Clear all chat context to start a fresh session. Prevents token accumulation."""
    msg_count = len(chat_state["messages"])
    chat_state["messages"] = []
    chat_state["scratchpad"] = []
    chat_state["trace"] = []
    chat_state["pending_tool_call"] = None
    chat_state["pending_user_text"] = None
    chat_state["pending_rag_info"] = None
    return {"ok": True, "cleared_messages": msg_count}


def _safe_serialize(obj, depth=3):
    """Recursively make an object JSON-safe."""
    if depth <= 0:
        return "<truncated>"
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, str):
        return obj[:5000] if len(obj) > 5000 else obj
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, list):
        return [_safe_serialize(v, depth - 1) for v in obj[:50]]
    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v, depth - 1) for k, v in list(obj.items())[:50]}
    return str(obj)[:2000]
