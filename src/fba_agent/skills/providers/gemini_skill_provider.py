"""
Gemini Skill Provider implementation (via OpenAI-compatible endpoint).
This provider is isolated for the FBA Skill and supports Function Calling.
"""
from __future__ import annotations
import json
import re
from fba_agent.providers import BaseProvider, ProviderConfig

class GeminiSkillProvider(BaseProvider):
    """Gemini LLM provider using OpenAI-compatible API, with Tool/Function Calling support."""

    def __init__(self, config: ProviderConfig, trace_path: str | None = None):
        super().__init__(config)
        self.set_trace_path(trace_path)
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
        Send chat request and return parsed JSON (Legacy/Standard method).
        Satisfies BaseProvider interface.
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
            # Basic cleanup if needed
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("\n", 1)[0]
                
            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                return json.loads(match.group())
            return json.loads(content)
            
        except Exception as e:
            if self.escalate():
                return self.chat_json(system, user, schema)
            raise

    def chat_with_tools(
        self,
        system: str,
        user: str,
        tools: list[dict],
    ) -> dict:
        """
        Send chat request and return parsed JSON from a tool call.
        """
        client = self._get_client()
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        try:
            response = client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=0.1,
                tools=tools,
                tool_choice="auto",
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                # Assuming one tool call per "skill" interaction
                tool_call = message.tool_calls[0]
                return json.loads(tool_call.function.arguments)
            
            # Fallback or error if no tool was called
            raise ValueError("Expected a tool call from the model, but none was received.")
            
        except Exception as e:
            if self.escalate():
                return self.chat_with_tools(system, user, tools)
            raise
