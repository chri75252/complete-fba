from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from control_plane.llm_provider import generate_json


ALLOWED_INTENTS = {"enqueue_run", "query_financial", "show_status", "tail_logs"}


@dataclass(frozen=True)
class ParseResult:
    ok: bool
    data: dict[str, Any]
    error: str | None = None


def _coerce_list(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if str(x).strip()]
    return [str(val)]


def validate_payload(payload: dict[str, Any]) -> ParseResult:
    intent = str(payload.get("intent") or "").strip()
    if intent not in ALLOWED_INTENTS:
        return ParseResult(ok=False, data={}, error="invalid_intent")

    out: dict[str, Any] = {
        "intent": intent,
        "supplier_domain": payload.get("supplier_domain"),
        "workflow_key": payload.get("workflow_key"),
        "runner_script": payload.get("runner_script"),
        "category_urls": _coerce_list(payload.get("category_urls")),
        "max_products": payload.get("max_products"),
        "max_products_per_category": payload.get("max_products_per_category"),
        "roi_min": payload.get("roi_min"),
        "netprofit_min": payload.get("netprofit_min"),
        "ean": payload.get("ean"),
        "limit": payload.get("limit"),
        "confidence": payload.get("confidence"),
        "missing_fields": _coerce_list(payload.get("missing_fields")),
    }

    return ParseResult(ok=True, data=out)


def build_prompt(text: str) -> str:
    return (
        "Return ONLY valid JSON. No markdown. No prose.\n"
        "Schema:\n"
        "{\n"
        '  "intent": one of [enqueue_run, query_financial, show_status, tail_logs],\n'
        '  "supplier_domain": string or null,\n'
        '  "workflow_key": string or null,\n'
        '  "runner_script": string or null,\n'
        '  "category_urls": array of strings,\n'
        '  "max_products": number or null,\n'
        '  "max_products_per_category": number or null,\n'
        '  "roi_min": number or null,\n'
        '  "netprofit_min": number or null,\n'
        '  "ean": string or null,\n'
        '  "limit": number or null,\n'
        '  "confidence": number between 0 and 1,\n'
        '  "missing_fields": array of strings\n'
        "}\n\n"
        f"User text: {text}"
    )


def parse(text: str) -> ParseResult:
    try:
        raw = generate_json(build_prompt(text))
    except Exception as e:
        return ParseResult(ok=False, data={}, error=str(e))

    if not isinstance(raw, dict):
        return ParseResult(ok=False, data={}, error="provider_returned_non_object")

    return validate_payload(raw)
