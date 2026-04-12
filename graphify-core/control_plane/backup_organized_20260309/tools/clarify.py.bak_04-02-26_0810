from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClarifyResponse:
    questions: list[str]
    hint: str | None = None


def ask_clarify(user_text: str | None = None) -> dict[str, object]:
    text = (user_text or "").strip()
    questions = [
        "What supplier domain should I use (e.g. poundwholesale.co.uk)?",
        "Do you want a read-only query (status/financials/traces), or to enqueue a run?",
        "If enqueuing a run: which workflow_key and runner_script should I use?",
        "If enqueuing a run: paste 1+ category URLs to process.",
    ]
    hint = None
    if text:
        hint = f"Original request: {text}"[:500]

    return {"ok": True, "questions": questions, "hint": hint}
