from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Protocol

from control_plane.env_config import ensure_llm_env


class LlmProvider(Protocol):
    def generate_json(self, prompt: str) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class NoneProvider:
    def generate_json(self, prompt: str) -> dict[str, Any]:
        raise RuntimeError("LLM provider disabled")


def _safe_json_loads(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


@dataclass(frozen=True)
class OllamaProvider:
    base_url: str
    model: str

    def generate_json(self, prompt: str) -> dict[str, Any]:
        import requests

        url = self.base_url.rstrip("/") + "/api/generate"
        resp = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data.get("response", "")
        return _safe_json_loads(text)

    def generate_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        think: bool = True,
    ) -> dict[str, Any]:
        """
        Generate response using Ollama's native tool calling with optional thinking.

        Args:
            messages: List of chat messages [{"role": "...", "content": "..."}]
            tools: List of tool schemas in Ollama format
            think: Enable thinking/reasoning mode (default True)

        Returns:
            Dict with keys: content, thinking, tool_calls
        """
        import requests

        url = self.base_url.rstrip("/") + "/api/chat"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.3},
        }

        if tools:
            payload["tools"] = tools

        if think:
            payload["think"] = True

        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        msg = data.get("message", {})

        raw_tool_calls = msg.get("tool_calls", [])
        tool_calls = []
        for tc in raw_tool_calls:
            fn = tc.get("function", {})
            tool_calls.append(
                {
                    "name": fn.get("name", ""),
                    "arguments": fn.get("arguments", "{}"),
                }
            )

        return {
            "content": msg.get("content", ""),
            "thinking": msg.get("thinking", ""),
            "tool_calls": tool_calls,
        }

    def generate_text(self, prompt: str) -> str:
        """
        Generate natural language text without JSON formatting.
        Used for post-tool summarization.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Natural language string response
        """
        import requests

        url = self.base_url.rstrip("/") + "/api/generate"
        resp = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                # NO format="json" - allow natural language
                "options": {"temperature": 0.3},
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")


@dataclass(frozen=True)
class OpenAiProvider:
    api_key: str
    model: str

    def generate_json(self, prompt: str) -> dict[str, Any]:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        temperature = 0
        if self.model == "gpt-5-mini":
            temperature = 1
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        content = resp.choices[0].message.content or "{}"
        return json.loads(content)


@dataclass(frozen=True)
class OpenAiCompatProvider:
    base_url: str
    model: str
    api_key: str | None = None

    def generate_json(self, prompt: str) -> dict[str, Any]:
        import requests

        url = self.base_url.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return _safe_json_loads(text)


@dataclass(frozen=True)
class AnthropicProvider:
    api_key: str
    model: str

    def generate_json(self, prompt: str) -> dict[str, Any]:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        msg = client.messages.create(
            model=self.model,
            max_tokens=800,
            temperature=0,
            system="Return ONLY valid JSON.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join([b.text for b in msg.content if getattr(b, "text", None)])
        return json.loads(text or "{}")


def get_provider() -> LlmProvider:
    ensure_llm_env()
    provider = os.environ.get("CONTROL_PLANE_LLM_PROVIDER", "none").strip().lower()

    if provider == "none":
        return NoneProvider()

    if provider == "ollama":
        base_url = os.environ.get("CONTROL_PLANE_OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.environ.get("CONTROL_PLANE_OLLAMA_MODEL", "llama3.1")
        return OllamaProvider(base_url=base_url, model=model)

    if provider == "lmstudio":
        base_url = os.environ.get("CONTROL_PLANE_LLM_BASE_URL", "http://localhost:1234")
        model = os.environ.get("CONTROL_PLANE_LLM_MODEL") or os.environ.get(
            "LOCAL_LLM_MODEL", "llama3"
        )
        return OpenAiCompatProvider(base_url=base_url, model=model)

    if provider == "opencode":
        base_url = os.environ.get("CONTROL_PLANE_LLM_BASE_URL", "https://opencode.ai/zen")
        model = os.environ.get("OPENCODE_MODEL") or os.environ.get(
            "CONTROL_PLANE_LLM_MODEL", "minimax-m2.5-free"
        )
        api_key = os.environ.get("OPENCODE_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENCODE_API_KEY not set")
        return OpenAiCompatProvider(base_url=base_url, model=model, api_key=api_key)

    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = os.environ.get("CONTROL_PLANE_OPENAI_MODEL", "gpt-4o-mini")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        return OpenAiProvider(api_key=api_key, model=model)

    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        model = os.environ.get("CONTROL_PLANE_ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        return AnthropicProvider(api_key=api_key, model=model)

    raise RuntimeError(f"Unknown CONTROL_PLANE_LLM_PROVIDER: {provider}")
