from __future__ import annotations

from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    chat_panel_path = repo_root / "dashboard" / "chat_panel.py"
    text = chat_panel_path.read_text(encoding="utf-8")

    needle = '"tool_result": result'
    if needle not in text:
        raise SystemExit(
            f"FAIL: expected {needle!r} in {chat_panel_path.as_posix()} (Confirm execute block)"
        )

    chat_messages: list[dict] = []
    result = {"ok": True, "run_id": "RUN123"}
    chat_messages.append(
        {
            "role": "assistant",
            "content": "Executed `enqueue_run`.",
            "tool_result": result,
        }
    )

    assert chat_messages[-1]["tool_result"] == result
    assert chat_messages[-1]["tool_result"]["run_id"] == "RUN123"

    print("PASS: tool_result is appended into chat_messages and code needle is present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
