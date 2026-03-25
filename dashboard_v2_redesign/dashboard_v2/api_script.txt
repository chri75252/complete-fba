import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Any, Optional
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
    from control_plane.audit import write_session_transcript
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _new_session_id() -> str:
    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"

# ---- In-memory chat session state (mirrors Streamlit session_state) ----
chat_state = {
    "messages": [],
    "scratchpad": [],
    "trace": [],
    "tool_executions": [],
    "turn_history": [],
    "pending_tool_call": None,
    "pending_user_text": None,
    "pending_rag_info": None,
    "last_run_id": None,
    "last_products_path": None,
    "last_supplier_domain": None,
    "last_sandbox_supplier": None,
    "session_id": _new_session_id(),
    "session_started_at": _now_iso(),
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
def get_supplier_metrics(supplier: str, lineage: str = "base"):
    base_dir = get_base_directory()
    try:
        effective_supplier = supplier
        if lineage == "latest_sandbox":
            loader = MetricsLoader(base_dir)
            latest = loader.discover_latest_sandbox_supplier(supplier)
            if latest:
                effective_supplier = latest

        issues, paths = validate_supplier_data(base_dir, effective_supplier)
        if issues:
            return JSONResponse({
                "error": True,
                "issues": issues,
                "paths": paths,
                "state_metrics": {"state_file_found": False},
                "linking_metrics": {"total_matches": 0},
                "financial_metrics": {"files_scanned": 0},
                "log_data": [[], None],
                "meta": {
                    "requested_supplier": supplier,
                    "lineage": lineage,
                    "effective_supplier": effective_supplier,
                },
            })

        # We need to serialize paths object cleanly (POSIX paths to str)
        metrics_data = load_metrics(base_dir, effective_supplier)
        metrics_data["meta"] = {
            "requested_supplier": supplier,
            "lineage": lineage,
            "effective_supplier": effective_supplier,
        }
        metrics_data.setdefault("paths", {})["base_dir"] = base_dir
        
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


@app.get("/api/validate/{supplier}")
def run_validation(supplier: str, lineage: str = "base"):
    base_dir = get_base_directory()
    effective_supplier = supplier
    if lineage == "latest_sandbox":
        loader = MetricsLoader(base_dir)
        latest = loader.discover_latest_sandbox_supplier(supplier)
        if latest:
            effective_supplier = latest

    issues, paths = validate_supplier_data(base_dir, effective_supplier)
    checks: dict[str, Any] = {}

    state_file = paths.get("state_file")
    if state_file and os.path.exists(state_file):
        try:
            state = json.loads(Path(state_file).read_text(encoding="utf-8"))
            checks["state_total_categories"] = (
                state.get("system_progression", {}).get("total_categories")
            )
            checks["state_has_resume_pointer"] = (
                "resume_pointer" in state.get("system_progression", {})
            )
            checks["state_readable"] = True
        except Exception:
            checks["state_readable"] = False

    linking_file = paths.get("linking_file")
    if linking_file and os.path.exists(linking_file):
        try:
            linking_map = json.loads(Path(linking_file).read_text(encoding="utf-8"))
            checks["linking_map_entries"] = len(linking_map) if isinstance(linking_map, list) else 0
            checks["linking_map_readable"] = True
        except Exception:
            checks["linking_map_readable"] = False

    return JSONResponse(
        {
            "requested_supplier": supplier,
            "effective_supplier": effective_supplier,
            "lineage": lineage,
            "issues": issues,
            "checks": checks,
            "paths": {k: str(v) if v else None for k, v in paths.items()},
            "valid": len(issues) == 0,
        }
    )

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
    chat_state["tool_executions"] = []

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
                    chat_state["trace"] = list(local_trace)
                    _archive_current_turn("final_answer", final_answer=step.text)
                    _clear_turn_buffers()
                    _persist_chat_session("final_answer")
                    yield "data: " + _json.dumps({"type": "final_answer", "text": step.text, "trace": local_trace}) + "\n\n"
                    return

                if step.kind == "approval_needed":
                    tc = step.tool_call
                    chat_state["pending_tool_call"] = tc
                    chat_state["pending_user_text"] = user_text
                    chat_state["pending_rag_info"] = rag_info
                    _persist_chat_session("approval_needed")
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
                chat_state["trace"] = list(local_trace)
                yield "data: " + _json.dumps({"type": "trace_update", "step": trace_entry}) + "\n\n"

                chat_state["scratchpad"].append({"role": "action", "tool": step.tool_call.name, "params": step.tool_call.params})
                chat_state["scratchpad"].append({"role": "observation", "result": step.result})

            # Step limit reached
            fallback_msg = "I reached the maximum number of reasoning steps. See the trace for what I found."
            chat_state["messages"].append({"role": "assistant", "content": fallback_msg})
            chat_state["trace"] = list(local_trace)
            _archive_current_turn("step_limit_final_answer", final_answer=fallback_msg)
            _clear_turn_buffers()
            _persist_chat_session("step_limit_final_answer")
            yield "data: " + _json.dumps({"type": "final_answer", "text": fallback_msg, "trace": local_trace}) + "\n\n"

        except Exception as e:
            _archive_current_turn(
                "agent_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
            )
            _clear_turn_buffers()
            _persist_chat_session("agent_error")
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
        rejected_snapshot = _pending_tool_snapshot()
        pending_user_text = _safe_serialize(chat_state.get("pending_user_text"), depth=2)
        pending_rag_info = _safe_serialize(chat_state.get("pending_rag_info"), depth=4)
        # User rejected
        chat_state["messages"].append({"role": "assistant", "content": "Action cancelled by user."})
        _archive_current_turn(
            "approval_rejected",
            pending_tool_call=rejected_snapshot,
            pending_user_text=pending_user_text,
            pending_rag_info=pending_rag_info,
        )
        chat_state["pending_tool_call"] = None
        chat_state["pending_user_text"] = None
        chat_state["pending_rag_info"] = None
        _clear_turn_buffers()
        _persist_chat_session("approval_rejected")
        return {"type": "cancelled", "text": "Action cancelled by user."}

    # Execute the approved tool
    try:
        result = execute_tool_call(tc, repo_root)
        audit_tool_call(user_text, tc, result, rag_info)
        _record_tool_execution(tc, result)

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

        chat_state["messages"].append({
            "role": "assistant",
            "content": f"Action `{tc.name}` executed successfully.",
        })
        _archive_current_turn(
            "approval_executed",
            executed_tool=tc.name,
            executed_result=_safe_serialize(result, depth=4),
        )
        _clear_turn_buffers()
        _persist_chat_session("approval_executed")

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
    _archive_current_turn("chat_reset")
    _persist_chat_session("chat_reset")
    msg_count = len(chat_state["messages"])
    chat_state["messages"] = []
    chat_state["scratchpad"] = []
    chat_state["trace"] = []
    chat_state["tool_executions"] = []
    chat_state["turn_history"] = []
    chat_state["pending_tool_call"] = None
    chat_state["pending_user_text"] = None
    chat_state["pending_rag_info"] = None
    chat_state["last_run_id"] = None
    chat_state["last_products_path"] = None
    chat_state["last_supplier_domain"] = None
    chat_state["last_sandbox_supplier"] = None
    _begin_new_chat_session()
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


def _record_tool_execution(tc, result: dict) -> None:
    chat_state["tool_executions"].append(
        {
            "tool": tc.name,
            "params": _safe_serialize(tc.params, depth=4),
            "expected_outputs": _safe_serialize(
                getattr(tc, "expected_outputs", None), depth=4
            ),
            "result": _safe_serialize(result, depth=4),
            "executed_at": _now_iso(),
        }
    )
    chat_state["tool_executions"] = chat_state["tool_executions"][-50:]


def _clear_turn_buffers() -> None:
    chat_state["scratchpad"] = []
    chat_state["trace"] = []
    chat_state["tool_executions"] = []


def _archive_current_turn(reason: str, **extra: Any) -> None:
    has_turn_data = bool(
        chat_state["scratchpad"]
        or chat_state["trace"]
        or chat_state["tool_executions"]
        or extra
    )
    if not has_turn_data:
        return

    chat_state["turn_history"].append(
        _safe_serialize(
            {
                "reason": reason,
                "archived_at": _now_iso(),
                "messages": chat_state["messages"][-3:],
                "scratchpad": chat_state["scratchpad"],
                "trace": chat_state["trace"],
                "tool_executions": chat_state["tool_executions"],
                **extra,
            },
            depth=6,
        )
    )
    chat_state["turn_history"] = chat_state["turn_history"][-50:]


def _pending_tool_snapshot() -> dict[str, Any] | None:
    tc = chat_state.get("pending_tool_call")
    if tc is None:
        return None
    return {
        "name": getattr(tc, "name", None),
        "params": _safe_serialize(getattr(tc, "params", None), depth=5),
        "explanation": getattr(tc, "explanation", None),
        "expected_outputs": _safe_serialize(getattr(tc, "expected_outputs", None), depth=5),
    }


def _has_persistable_session_data() -> bool:
    return bool(
        chat_state["messages"]
        or chat_state["scratchpad"]
        or chat_state["trace"]
        or chat_state["tool_executions"]
        or chat_state["turn_history"]
        or chat_state["pending_tool_call"]
        or chat_state["last_run_id"]
        or chat_state["last_products_path"]
        or chat_state["last_supplier_domain"]
        or chat_state["last_sandbox_supplier"]
    )


def _persist_chat_session(reason: str) -> None:
    if not _has_persistable_session_data():
        return

    payload = {
        "session_id": chat_state["session_id"],
        "session_started_at": chat_state["session_started_at"],
        "reason": reason,
        "messages": _safe_serialize(chat_state["messages"], depth=6),
        "scratchpad": _safe_serialize(chat_state["scratchpad"], depth=6),
        "trace": _safe_serialize(chat_state["trace"], depth=6),
        "tool_executions": _safe_serialize(chat_state["tool_executions"], depth=6),
        "turn_history": _safe_serialize(chat_state["turn_history"], depth=6),
        "pending_tool_call": _pending_tool_snapshot(),
        "pending_user_text": _safe_serialize(chat_state["pending_user_text"], depth=2),
        "pending_rag_info": _safe_serialize(chat_state["pending_rag_info"], depth=4),
        "last_run_id": chat_state["last_run_id"],
        "last_products_path": chat_state["last_products_path"],
        "last_supplier_domain": chat_state["last_supplier_domain"],
        "last_sandbox_supplier": chat_state["last_sandbox_supplier"],
    }

    try:
        write_session_transcript(chat_state["session_id"], payload)
    except Exception as e:
        print(f"Transcript persistence failed: {e}")


def _begin_new_chat_session() -> None:
    chat_state["session_id"] = _new_session_id()
    chat_state["session_started_at"] = _now_iso()
