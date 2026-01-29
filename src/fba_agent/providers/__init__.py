"""Unified provider interface for LLM providers.

This module provides a consistent interface for different LLM providers:
- OpenAI (GPT-4o, GPT-4o-mini)
- Gemini (via OpenAI-compatible endpoint)
- Moonshot

Features:
- Common interface for chat_json()
- Model escalation (small → large on failure)
- Structured JSON output with schema validation
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on system env vars


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""

    name: str
    api_key: str | None = None
    base_url: str | None = None
    model_small: str = "gpt-4o-mini"
    model_large: str = "gpt-4o"
    current_model: str | None = None  # Set at runtime
    max_escalations: int = 2
    escalations_used: int = 0


class ProviderInterface(Protocol):
    """Protocol for LLM providers."""

    def chat_json(
        self,
        system: str,
        user: str,
        schema: dict | None = None,
    ) -> dict:
        """
        Send a chat request expecting JSON response.
        
        Args:
            system: System prompt
            user: User message
            schema: Optional JSON schema for validation
        
        Returns:
            Parsed JSON response as dict
        """
        ...

    def escalate(self) -> bool:
        """
        Escalate to a larger model.
        
        Returns:
            True if escalation succeeded, False if at max
        """
        ...

    @property
    def current_model(self) -> str:
        """Return the current model being used."""
        ...


class BaseProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.config.current_model = config.model_small
        self._trace_path: str | None = None

    def set_trace_path(self, trace_path: str | None) -> None:
        """Set the trace log file path."""
        self._trace_path = trace_path
    
    @property
    def current_model(self) -> str:
        return self.config.current_model or self.config.model_small

    def escalate(self) -> bool:
        """Escalate to larger model."""
        if self.config.escalations_used >= self.config.max_escalations:
            return False
        if self.config.current_model == self.config.model_large:
            return False
        self.config.current_model = self.config.model_large
        self.config.escalations_used += 1
        return True

    @abstractmethod
    def chat_json(
        self,
        system: str,
        user: str,
        schema: dict | None = None,
    ) -> dict:
        """Send chat request and return parsed JSON."""
        ...


def get_provider(
    name: str,
    api_key: str | None = None,
    model_small: str | None = None,
    model_large: str | None = None,
    base_url: str | None = None,
    trace_path: str | None = None,
) -> BaseProvider:
    """
    Get a provider instance by name.
    
    Args:
        name: Provider name ("openai", "gemini", "moonshot")
        api_key: API key (defaults to env var)
        model_small: Small model name (for initial requests)
        model_large: Large model name (for escalation)
        base_url: Custom base URL (for proxies/compatible endpoints)
        trace_path: Path to LLM trace log file (optional)
    
    Returns:
        Provider instance
    
    Raises:
        ValueError: If provider name not recognized
    """
    name = name.lower()
    
    if name == "openai":
        from fba_agent.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(
            config=ProviderConfig(
                name="openai",
                api_key=api_key or os.getenv("OPENAI_API_KEY"),
                base_url=base_url,
                model_small=model_small or os.getenv("MODEL_NAME", "gpt-5-mini"),
                model_large=model_large or os.getenv("MODEL_NAME", "gpt-5-mini"),
            ),
            trace_path=trace_path,
        )
    
    if name == "gemini":
        from fba_agent.providers.gemini_provider import GeminiProvider
        return GeminiProvider(
            config=ProviderConfig(
                name="gemini",
                api_key=api_key or os.getenv("GEMINI_API_KEY"),
                base_url=base_url or "https://generativelanguage.googleapis.com/v1beta/openai/",
                model_small=model_small or "gemini-2.0-flash-exp",
                model_large=model_large or "gemini-2.0-flash-thinking-exp-01-21",
            ),
            trace_path=trace_path,
        )
    
    if name == "moonshot":
        from fba_agent.providers.moonshot_provider import MoonshotProvider
        return MoonshotProvider(
            config=ProviderConfig(
                name="moonshot",
                api_key=api_key or os.getenv("MOONSHOT_API_KEY"),
                base_url=base_url or "https://api.moonshot.cn/v1",
                model_small=model_small or "moonshot-v1-8k",
                model_large=model_large or "moonshot-v1-32k",
            ),
            trace_path=trace_path,
        )
    
    raise ValueError(f"Unknown provider: {name}. Supported: openai, gemini, moonshot")


def load_provider_from_env(trace_path: str | None = None) -> BaseProvider | None:
    """
    Load a provider from environment variables.
    
    Checks in order: OPENAI_API_KEY, GEMINI_API_KEY, MOONSHOT_API_KEY
    
    Args:
        trace_path: Path to LLM trace log file (optional)
    
    Returns:
        Provider instance or None if no API key found
    """
    if os.getenv("OPENAI_API_KEY"):
        return get_provider("openai", trace_path=trace_path)
    if os.getenv("GEMINI_API_KEY"):
        return get_provider("gemini", trace_path=trace_path)
    if os.getenv("MOONSHOT_API_KEY"):
        return get_provider("moonshot", trace_path=trace_path)
    return None
