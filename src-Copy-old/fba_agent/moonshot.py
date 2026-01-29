from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class MoonshotConfig:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def load_moonshot_config() -> MoonshotConfig | None:
    api_key = os.getenv("MOONSHOT_API_KEY", "").strip()
    if not api_key:
        return None
    base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1").strip().rstrip("/")
    model = os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k").strip()
    timeout = float(os.getenv("MOONSHOT_TIMEOUT_SECONDS", "60"))
    return MoonshotConfig(api_key=api_key, base_url=base_url, model=model, timeout_seconds=timeout)


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = _JSON_OBJECT_RE.search(text)
    if not match:
        raise ValueError("No JSON object found in model output")
    return json.loads(match.group(0))


def chat_json(*, config: MoonshotConfig, system: str, user: str) -> dict[str, Any]:
    url = f"{config.base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}
    payload = {
        "model": config.model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=config.timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return _extract_json_object(content)

