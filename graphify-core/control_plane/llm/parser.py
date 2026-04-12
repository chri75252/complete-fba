from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from control_plane.llm.providers import get_provider


@dataclass(frozen=True)
class ParseResult:
    ok: bool
    data: dict[str, Any]
    error: str | None = None


PARSER_SCHEMA = {
    "type": "object",
    "required": ["intent", "confidence", "missing_fields"],
    "properties": {
        "intent": {"type": "string"},
        "supplier_domain": {"type": ["string", "null"]},
        "max_products": {"type": ["number", "null"]},
        "max_products_per_category": {"type": ["number", "null"]},
        "category_urls": {"type": ["array", "null"], "items": {"type": "string"}},
        "roi_min": {"type": ["number", "null"]},
        "netprofit_min": {"type": ["number", "null"]},
        "ean": {"type": ["string", "null"]},
        "asin": {"type": ["string", "null"]},
        "limit": {"type": ["number", "null"]},
        "confidence": {"type": "number"},
        "missing_fields": {"type": "array", "items": {"type": "string"}},
    },
}


def build_prompt(user_text: str) -> str:
    return (
        "You are a strict JSON generator. Return ONLY valid JSON.\n"
        "Do not include markdown fences, comments, or extra keys.\n"
        "Extract intent + parameters for an Amazon FBA control panel.\n\n"
        "Allowed intents: enqueue_run, query_financial, show_status, tail_logs\n\n"
        "Return this JSON shape exactly:\n"
        + json.dumps(PARSER_SCHEMA["properties"], indent=2)
        + "\n\nUser message:\n"
        + user_text
    )


def parse_user_text(user_text: str) -> ParseResult:
    provider = get_provider()
    prompt = build_prompt(user_text)

    # retries for invalid JSON
    last_err: str | None = None
    for _ in range(2):
        try:
            data = provider.generate_json(prompt)
            if not isinstance(data, dict):
                last_err = "LLM did not return JSON object"
                continue
            # minimal required keys
            for k in ["intent", "confidence", "missing_fields"]:
                if k not in data:
                    last_err = f"Missing required key: {k}"
                    break
            else:
                return ParseResult(ok=True, data=data)
        except Exception as exc:
            last_err = str(exc)

    return ParseResult(ok=False, data={}, error=last_err)
