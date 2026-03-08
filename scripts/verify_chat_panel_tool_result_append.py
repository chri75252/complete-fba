"""Verify chat_panel appends tool_result to chat_messages."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any


class _Rerun(Exception):
    pass


class _NullCtx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeStatus(_NullCtx):
    def update(self, *args, **kwargs):
        return None


class _FakeStreamlitModule:
    def __init__(self) -> None:
        self.session_state: dict = {}

    @contextmanager
    def status(self, *args, **kwargs):
        yield _FakeStatus()

    def write(self, *args, **kwargs):
        return None

    @contextmanager
    def expander(self, *args, **kwargs):
        yield _NullCtx()

    def markdown(self, *args, **kwargs):
        return None

    def rerun(self):
        raise _Rerun()


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))

    fake_st = _FakeStreamlitModule()
    sys.modules["streamlit"] = fake_st  # type: ignore[assignment]

    fake_orch = ModuleType("control_plane.chat_orchestrator")

    @dataclass(frozen=True)
    class ToolCall:
        name: str
        params: dict[str, Any]
        explanation: str | None = None
        expected_outputs: list[str] | None = None

    @dataclass(frozen=True)
    class AgentStep:
        kind: str
        tool_call: ToolCall | None = None
        text: str | None = None
        result: dict[str, Any] | None = None

    calls = {"n": 0}

    def _mock_agent_plan_step(user_text, repo_root, scratchpad, chat_history, rag_info_tuple):
        calls["n"] += 1
        if calls["n"] == 1:
            return AgentStep(
                kind="tool_call",
                tool_call=ToolCall(name="show_status", params={"run_id": "abc"}),
                result={"ok": True, "run_id": "abc"},
            )
        return AgentStep(kind="final_answer", text="done")

    fake_orch.ToolCall = ToolCall
    fake_orch.AgentStep = AgentStep
    fake_orch.agent_plan_step = _mock_agent_plan_step
    fake_orch.audit_tool_call = lambda *a, **k: None
    fake_orch.execute_tool_call = lambda *a, **k: {"ok": True}
    fake_orch.plan_tool_call = lambda *a, **k: (ToolCall(name="ask_clarify", params={}), {})
    fake_orch.respond_to_tool_result = lambda *a, **k: ""
    fake_orch._compute_rag_info = lambda _user_text: ({}, "")

    sys.modules["control_plane.chat_orchestrator"] = fake_orch

    import dashboard.chat_panel as chat_panel

    fake_st.session_state["chat_messages"] = []
    fake_st.session_state["agent_trace"] = []
    fake_st.session_state["agent_scratchpad"] = []

    try:
        chat_panel._run_agent_loop("hello", base_dir=".")
    except _Rerun:
        pass

    msgs = fake_st.session_state.get("chat_messages") or []
    tool_msgs = [m for m in msgs if isinstance(m, dict) and m.get("tool_result") is not None]

    assert tool_msgs, "Expected at least one assistant message with tool_result"
    assert tool_msgs[0]["tool_result"] == {"ok": True, "run_id": "abc"}

    print("PASS: tool_result appended to st.session_state['chat_messages']")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
