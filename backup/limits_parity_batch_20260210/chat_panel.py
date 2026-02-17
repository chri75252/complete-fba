import os
from pathlib import Path

import streamlit as st

from control_plane.chat_orchestrator import (
    audit_tool_call,
    execute_tool_call,
    is_write_tool,
    plan_tool_call,
    ToolCall,
)
from control_plane.env_config import ensure_llm_env
from control_plane.llm.providers import get_provider
from control_plane.paths import get_paths
from control_plane.rag_index import write_rag_index
from control_plane.rag_retriever import load_rag_index


def _truncate_value(
    value: object,
    *,
    max_str: int = 5000,
    max_list: int = 50,
    max_dict_items: int = 50,
    depth: int = 3,
) -> object:
    if depth <= 0:
        return "<truncated>"

    if value is None:
        return None

    if isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, str):
        if len(value) <= max_str:
            return value
        return value[:max_str] + "\n…<truncated>"

    if isinstance(value, list):
        items = [
            _truncate_value(
                v,
                max_str=max_str,
                max_list=max_list,
                max_dict_items=max_dict_items,
                depth=depth - 1,
            )
            for v in value[:max_list]
        ]
        if len(value) > max_list:
            items.append(f"… ({len(value) - max_list} more)")
        return items

    if isinstance(value, dict):
        out: dict[str, object] = {}
        count = 0
        for k, v in value.items():
            if count >= max_dict_items:
                out["…"] = f"({len(value) - max_dict_items} more keys)"
                break
            out[str(k)] = _truncate_value(
                v,
                max_str=max_str,
                max_list=max_list,
                max_dict_items=max_dict_items,
                depth=depth - 1,
            )
            count += 1
        return out

    text = repr(value)
    if len(text) <= max_str:
        return text
    return text[:max_str] + "\n…<truncated>"


def _ensure_state() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if "pending_tool_call" not in st.session_state:
        st.session_state["pending_tool_call"] = None
        st.session_state["pending_user_text"] = None
        st.session_state["pending_rag_info"] = None


def render_chat_panel(base_dir: str) -> None:
    _ensure_state()
    ensure_llm_env()

    st.subheader("Chat")

    col_a, col_b = st.columns([3, 1])
    with col_b:
        st.write("LLM provider:")
        st.code(repr(os.environ.get("CONTROL_PLANE_LLM_PROVIDER", "none")), language="text")

        rag_index = load_rag_index(get_paths().rag_index_path)
        rag_summary = {
            "ok": bool(rag_index),
            "doc_count": (rag_index or {}).get("doc_count", 0),
            "generated_at": (rag_index or {}).get("generated_at"),
        }
        st.write("RAG index:")
        st.json(rag_summary)

        if st.button("Refresh system index"):
            try:
                import subprocess

                subprocess.run(["python", "-m", "control_plane", "build-index"], check=False)
                st.success("system_index.json refreshed")
            except Exception as e:
                st.error(str(e))

        if st.button("Build RAG index"):
            try:
                p = write_rag_index()
                st.success(f"RAG index written: {p}")
            except Exception as e:
                st.error(str(e))

    with col_a:
        st.write("Use natural language. Write/exec actions require confirmation.")

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            tool_result = msg.get("tool_result")
            if tool_result is not None:
                with st.expander("Tool output", expanded=False):
                    st.json(_truncate_value(tool_result))

    if st.session_state["pending_tool_call"] is not None:
        tool_call = st.session_state["pending_tool_call"]
        user_text = st.session_state["pending_user_text"]
        rag_info = st.session_state.get("pending_rag_info") or {}
        with st.chat_message("assistant"):
            st.markdown("Proposed action requires confirmation:")
            st.json({"tool": tool_call.name, "params": tool_call.params})

            if getattr(tool_call, "explanation", None):
                st.info(tool_call.explanation)

            if getattr(tool_call, "expected_outputs", None):
                st.markdown("**Expected Output Files:**")
                for path in tool_call.expected_outputs:
                    st.code(path, language=None)

            if st.button("Confirm execute"):
                result = execute_tool_call(tool_call, Path(base_dir))
                audit_tool_call(user_text, tool_call, result, rag_info)

                # Enhanced messaging for product list refresh
                if tool_call.name == "enqueue_product_list_refresh" and result.get("ok"):
                    run_id = result.get("run_id", "unknown")
                    sandbox_supplier = result.get("sandbox_supplier", "unknown")
                    assistant_content = f"""✅ Job queued successfully!

**Run ID:** `{run_id}`
**Supplier:** `{sandbox_supplier}`

⚠️ **ACTION REQUIRED:** Start the worker to execute:
```
python -m control_plane worker
```

**Monitor progress:**
- Status: `OUTPUTS/CONTROL_PLANE/status/{run_id}.json`
- Log: `OUTPUTS/CONTROL_PLANE/logs/{run_id}.log`
- Pending jobs: Check `OUTPUTS/CONTROL_PLANE/jobs/pending/`

The worker will pick up the job and move it to running, then done/failed."""
                else:
                    assistant_content = (
                        tool_call.explanation
                        if isinstance(getattr(tool_call, "explanation", None), str)
                        and tool_call.explanation
                        else str(result.get("message"))
                        if isinstance(result.get("message"), str) and result.get("message")
                        else f"Executed tool: `{tool_call.name}`\n\nResult: `{result.get('ok')}`"
                    )
                st.session_state["chat_messages"].append(
                    {
                        "role": "assistant",
                        "content": assistant_content,
                        "tool_result": result,
                    }
                )

                st.session_state["pending_tool_call"] = None
                st.session_state["pending_user_text"] = None
                st.session_state["pending_rag_info"] = None
                st.rerun()

            if st.button("Cancel"):
                st.session_state["pending_tool_call"] = None
                st.session_state["pending_user_text"] = None
                st.session_state["pending_rag_info"] = None
                st.rerun()

    user_input = st.chat_input("Ask about status, financials, traces, or request a run...")
    if not user_input:
        return

    if st.session_state["pending_tool_call"] is not None:
        import re

        updated_params = False
        current_tool = st.session_state["pending_tool_call"]
        new_params = current_tool.params.copy()

        # Parse max_products_per_category (accepts: "to 10", "= 10", ": 10", or just "10")
        mpc_match = re.search(
            r"max[_ ]?products[_ ]?per[_ ]?category\s*(?:from\s+\d+\s+)?(?:to|=|:)?\s*(\d+)",
            user_input,
            re.IGNORECASE,
        )
        if mpc_match:
            new_params["max_products_per_category"] = int(mpc_match.group(1))
            updated_params = True

        # Parse max_products (accepts: "to 10", "= 10", ": 10", or just "10")
        mp_match = re.search(
            r"max[_ ]?products(?![_ ]?per[_ ]?category)\s*(?:from\s+\d+\s+)?(?:to|=|:)?\s*(\d+)",
            user_input,
            re.IGNORECASE,
        )
        if mp_match:
            new_params["max_products"] = int(mp_match.group(1))
            updated_params = True

        if updated_params:
            st.session_state["pending_tool_call"] = ToolCall(
                name=current_tool.name,
                params=new_params,
                explanation=current_tool.explanation,
                expected_outputs=current_tool.expected_outputs,
            )
            changes = []
            if mpc_match:
                changes.append(
                    f"max_products_per_category={new_params['max_products_per_category']}"
                )
            if mp_match:
                changes.append(f"max_products={new_params['max_products']}")

            st.session_state["chat_messages"].append({"role": "user", "content": user_input})
            st.session_state["chat_messages"].append(
                {
                    "role": "assistant",
                    "content": f"Updated pending run: {', '.join(changes)}",
                }
            )
            st.rerun()
            return

        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        st.session_state["chat_messages"].append(
            {
                "role": "assistant",
                "content": "⚠️ A pending action is waiting for confirmation. Please **Confirm** or **Cancel** above, or type 'set max products to X' to edit parameters.",
            }
        )
        st.rerun()
        return

    st.session_state["chat_messages"].append({"role": "user", "content": user_input})

    provider_ok = True
    try:
        _ = get_provider()
    except Exception as e:
        provider_ok = False
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": f"LLM provider error: {e}"}
        )

    if not provider_ok:
        return

    tool_call, rag_info = plan_tool_call(user_input, Path(base_dir))

    if tool_call.explanation:
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": tool_call.explanation, "tool_result": None}
        )

    if not tool_call.name:
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": "I couldn't select a tool for that request."}
        )
        return

    if is_write_tool(tool_call.name):
        st.session_state["pending_tool_call"] = tool_call
        st.session_state["pending_user_text"] = user_input
        st.session_state["pending_rag_info"] = rag_info
        st.rerun()

    result = execute_tool_call(tool_call, Path(base_dir))
    audit_tool_call(user_input, tool_call, result, rag_info)

    assistant_content = (
        tool_call.explanation
        if isinstance(getattr(tool_call, "explanation", None), str) and tool_call.explanation
        else str(result.get("message"))
        if isinstance(result.get("message"), str) and result.get("message")
        else f"Tool: `{tool_call.name}`\n\nResult: `{result.get('ok')}`"
    )
    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": assistant_content, "tool_result": result}
    )

    st.rerun()
