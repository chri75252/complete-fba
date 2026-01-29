"""
Data models for FBA Agent.

Contains all dataclasses and schemas used across the pipeline.
"""

from .schemas import (
    SchemaInfo,
    ParsedAttributes,
    TrapDetection,
    MatchChecks,
    RowDecisionRecord,
    ValidationResult,
    RunSummary,
    PreflightWarning
)

__all__ = [
    "SchemaInfo",
    "ParsedAttributes", 
    "TrapDetection",
    "MatchChecks",
    "RowDecisionRecord",
    "ValidationResult",
    "RunSummary",
    "PreflightWarning"
]
