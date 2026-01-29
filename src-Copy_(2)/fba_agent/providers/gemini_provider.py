"""Gemini provider implementation (via OpenAI-compatible endpoint)."""
from __future__ import annotations

import json
import re

from fba_agent.providers import BaseProvider, ProviderConfig


class GeminiProvider(BaseProvider):
    """Gemini LLM provider using OpenAI-compatible API."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = None

    def _get_client(self):
        """Lazy-load the OpenAI client configured for Gemini."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
            
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url or "https://generativelanguage.googleapis.com/v1beta/openai/",
            )
        return self._client

    def chat_json(
        self,
        system: str,
        user: str,
        schema: dict | None = None,
    ) -> dict:
        """
        Send chat request and return parsed JSON.
        
        Note: Gemini's OpenAI-compatible endpoint may not support json_object
        response format, so we rely on prompt engineering.
        """
        client = self._get_client()
        
        # Modify system prompt to emphasize JSON output
        json_system = system + "\n\nIMPORTANT: You MUST respond with valid JSON only. No markdown, no explanations."
        
        if schema:
            json_system += f"\n\nRequired JSON schema:\n{json.dumps(schema, indent=2)}"
        
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
        
        # Remove markdown code fences if present
        if content.startswith("```"):
            first_newline = content.find("\n")
            if first_newline > 0:
                content = content[first_newline + 1:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        
        # Try to extract JSON object
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group())
        
        return json.loads(content)
