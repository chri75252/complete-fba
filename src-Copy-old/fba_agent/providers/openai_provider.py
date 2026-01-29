"""OpenAI provider implementation."""
from __future__ import annotations

import json
import re
from typing import Any

from fba_agent.providers import BaseProvider, ProviderConfig


class OpenAIProvider(BaseProvider):
    """OpenAI LLM provider."""

    def __init__(self, config: ProviderConfig, trace_path: str | None = None):
        super().__init__(config)
        self.set_trace_path(trace_path)
        self._client = None

    def _get_client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
            
            kwargs = {"api_key": self.config.api_key}
            if self.config.base_url:
                kwargs["base_url"] = self.config.base_url
            
            self._client = OpenAI(**kwargs)
        return self._client

    def chat_json(
        self,
        system: str,
        user: str,
        schema: dict | None = None,
    ) -> dict:
        """
        Send chat request and return parsed JSON.
        
        Uses json_object response format for reliable JSON output.
        """
        client = self._get_client()
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        
        # Add JSON instruction if schema provided
        if schema:
            messages[0]["content"] += f"\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        
        try:
            timestamp = 0
            # Import time locally to avoid circular deps if any, though standard lib is safe
            import time
            start_time = time.time()
            
            response = client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                response_format={"type": "json_object"},
                # Note: temperature removed - gpt-5-mini only supports default (1)
            )
            
            duration = time.time() - start_time
            content = response.choices[0].message.content
            parsed = self._parse_json(content)
            
            # TRACE LOGGING
            if self._trace_path:
                import datetime
                log_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "provider": "openai",
                    "model": self.current_model,
                    "duration_seconds": round(duration, 3),
                    "input": {
                        "system": system,
                        "user": user,
                        "schema": schema
                    },
                    "output": {
                        "raw_content": content,
                        "parsed": parsed
                    }
                }
                try:
                    with open(self._trace_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                except Exception as log_err:
                    print(f"Warning: Failed to write trace log: {log_err}")
            
            return parsed
            
        except Exception as e:
            # Log error before escalating
            if self._trace_path:
                import datetime
                import time
                log_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "provider": "openai",
                    "model": self.current_model,
                    "error": str(e),
                    "input": {
                        "system": system,
                        "user": user
                    }
                }
                try:
                    with open(self._trace_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                except Exception:
                    pass

            # On failure, try escalation
            if self.escalate():
                return self.chat_json(system, user, schema)
            raise

    def _parse_json(self, content: str) -> dict:
        """Parse JSON from response, handling markdown fences."""
        content = content.strip()
        
        # Remove markdown code fences if present
        if content.startswith("```"):
            # Find the end of the opening fence
            first_newline = content.find("\n")
            if first_newline > 0:
                content = content[first_newline + 1:]
            # Remove closing fence
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        
        # Try to extract JSON object
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group())
        
        # If no object found, try the whole content
        return json.loads(content)
