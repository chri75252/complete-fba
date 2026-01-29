from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on system env vars


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def load_openai_config() -> OpenAIConfig | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
    # Use MODEL_NAME as primary, fallback to OPENAI_MODEL, then default
    model = os.getenv("MODEL_NAME") or os.getenv("OPENAI_MODEL", "gpt-5-mini")
    model = model.strip()
    timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60"))
    return OpenAIConfig(api_key=api_key, base_url=base_url, model=model, timeout_seconds=timeout)


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


def chat_json(*, config: OpenAIConfig, system: str, user: str) -> dict[str, Any]:
    url = f"{config.base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}
    payload = {
        "model": config.model,
        # "temperature": 0,  # Removed: gpt-5-mini requires default (1)
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    import time
    start_time = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=config.timeout_seconds)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = _extract_json_object(content)
        
        duration = time.time() - start_time
        
        # TRACE LOGGING
        trace_file = os.getenv("FBA_TRACE_FILE")
        if trace_file:
            import datetime
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "provider": "openai_legacy_client",
                "model": config.model,
                "duration_seconds": round(duration, 3),
                "input": {
                    "system": system,
                    "user": user,
                    "url": url
                },
                "output": {
                    "raw_content": content,
                    "parsed": parsed
                }
            }
            try:
                with open(trace_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            except Exception as log_err:
                print(f"Warning: Failed to write trace log: {log_err}")

        return parsed

    except Exception as e:
        # Log detailed error info
        trace_file = os.getenv("FBA_TRACE_FILE")
        if trace_file:
            import datetime
            import time
            error_details = str(e)
            if hasattr(e, "response") and e.response is not None:
                error_details += f" | Body: {e.response.text}"

            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "provider": "openai_legacy_client",
                "model": config.model,
                "error": error_details,
                "input": {
                    "system": system,
                    "user": user,
                    "url": url
                }
            }
            try:
                with open(trace_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            except Exception:
                pass
        raise e

