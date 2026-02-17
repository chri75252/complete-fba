from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClarifyResponse:
    questions: list[str]
    hint: str | None = None


def ask_clarify(
    user_text: str | None = None,
    missing_params: list[str] | None = None,
    error_context: str | None = None,
) -> dict[str, object]:
    """Generate dynamic clarification questions based on context."""
    text = (user_text or "").strip()

    if missing_params:
        param_questions = {
            "supplier_domain": "Which supplier domain should I use (e.g. poundwholesale.co.uk)?",
            "category_urls": "Please provide one or more category URLs to process.",
            "workflow_key": "Which workflow key should I use (e.g. poundwholesale_workflow)?",
            "runner_script": "Which runner script should I use (e.g. run_custom_poundwholesale.py)?",
            "max_products": "How many products should I process in total?",
            "run_id": "Which run ID should I check?",
        }
        questions = [param_questions.get(p, f"Please provide: {p}") for p in missing_params]
    else:
        questions = [
            "What would you like me to do? (e.g., analyze categories, check status, query financials)",
        ]

    hint = None
    if text:
        hint = f"Original request: {text}"[:500]

    if error_context and isinstance(error_context, str) and error_context.strip():
        hint = (hint + "\n" if hint else "") + f"Error context: {error_context.strip()}"[:500]

    return {"ok": True, "questions": questions, "hint": hint}
