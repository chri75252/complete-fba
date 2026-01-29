import os
from pathlib import Path

import streamlit as st

from control_plane.chat_orchestrator import (
    audit_tool_call,
    execute_tool_call,
    is_write_tool,
    plan_tool_call,
)
from control_plane.env_config import ensure_llm_env
from control_plane.llm.providers import get_provider
from control_plane.rag_index import write_rag_index
from control_plane.rag_retrieval import load_rag_index, summarize_rag_index


def _ensure_state() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if "pending_tool_call" not in st.session_state:
        st.session_state["pending_tool_call"] = None
    if "pending_user_text" not in st.session_state:
        st.session_state["pending_user_text"] = None


def render_chat_panel(base_dir: str) -> None:
    _ensure_state()
    ensure_llm_env()

    st.subheader("Chat")

    col_a, col_b = st.columns([3, 1])
    with col_b:
        st.write("LLM provider:")
        st.code(repr(os.environ.get("CONTROL_PLANE_LLM_PROVIDER", "none")), language="text")

        rag_summary = summarize_rag_index(load_rag_index())
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

    if st.session_state["pending_tool_call"] is not None:
        tool_call = st.session_state["pending_tool_call"]
        user_text = st.session_state["pending_user_text"]
        with st.chat_message("assistant"):
            st.markdown("Proposed action requires confirmation:")
            st.json({"tool": tool_call.name, "params": tool_call.params})

            if st.button("Confirm execute"):
                result = execute_tool_call(tool_call, Path(base_dir))
                audit_tool_call(user_text, tool_call, result, rag_info)

                st.session_state["chat_messages"].append(
                    {
                        "role": "assistant",
                        "content": f"Executed tool: `{tool_call.name}`\n\nResult: `{result.get('ok')}`",
                    }
                )
                st.session_state["chat_messages"].append(
                    {"role": "assistant", "content": f"{result}"}
                )

                st.session_state["pending_tool_call"] = None
                st.session_state["pending_user_text"] = None

            if st.button("Cancel"):
                st.session_state["pending_tool_call"] = None
                st.session_state["pending_user_text"] = None

    user_input = st.chat_input("Ask about status, financials, traces, or request a run...")
    if not user_input:
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

    if not tool_call.name:
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": "I couldn't select a tool for that request."}
        )
        return

    if is_write_tool(tool_call.name):
        st.session_state["pending_tool_call"] = tool_call
        st.session_state["pending_user_text"] = user_input
        st.rerun()

    result = execute_tool_call(tool_call, Path(base_dir))
    audit_tool_call(user_input, tool_call, result, rag_info)

    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": f"Tool: `{tool_call.name}`\n\n{result}"}
    )

    st.rerun()
