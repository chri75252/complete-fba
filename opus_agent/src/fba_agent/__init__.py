"""
FBA Product Analysis Agent

A deterministic, tool-driven agent for analyzing FBA arbitrage opportunities.
Built with OpenAI Agents SDK + Kimi/Moonshot.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Agent System Architect"

from .config import Config
from .agent import FBAAgent

__all__ = ["Config", "FBAAgent", "__version__"]
