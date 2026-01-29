"""Moonshot provider implementation."""
from __future__ import annotations

import json
import re

from fba_agent.providers import BaseProvider, ProviderConfig


class MoonshotProvider(BaseProvider):
    """Moonshot LLM provider."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = None

    def _get_client(self):
        """Lazy-load the OpenAI client configured for Moonshot."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
            
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url or "https://api.moonshot.cn/v1",
            )
        return self._client

    def chat_json(
        self,
        system: str,
        user: str,
        schema: dict | None = None,
    ) -> dict:
        """Send chat request and return parsed JSON."""
        client = self._get_client()
        
        # Moonshot works well with explicit JSON instructions
        json_system = system + "\n\nRespond ONLY with valid JSON. No markdown fences, no explanations."
        
        if schema:
            json_system += f"\n\nRequired JSON format:\n{json.dumps(schema, indent=2)}"
        
        messages = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": user},
        ]
        
        try:
            response = client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=0.1,
            )
            
            content = response.choices[0].message.content
            return self._parse_json(content)
            
        except Exception as e:
            if self.escalate():
                return self.chat_json(system, user, schema)
            raise

    def _parse_json(self, content: str) -> dict:
        """Parse JSON from response, handling markdown fences."""
        content = content.strip()
        
        if content.startswith("```"):
            first_newline = content.find("\n")
            if first_newline > 0:
                content = content[first_newline + 1:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group())
        
        return json.loads(content)
