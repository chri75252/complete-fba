"""Critique Tools Module.

This module provides tool functions for AI Critique to access files on-demand
without sending full content upfront.

These tools are designed to be called by the LLM via function calling.
Each tool fetches specific data and returns it in a format suitable for the LLM.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    pass


class CritiqueToolContext:
    """
    Context object that holds references to all data sources.
    This is initialized once and passed to tool functions.
    """
    
    def __init__(
        self,
        ledger: pd.DataFrame,
        evidence: list[dict],
        md_report_path: Path | None = None,
        excel_path: Path | None = None,
        analysis_script_path: Path | None = None,
    ):
        self.ledger = ledger
        self.evidence = evidence
        self.md_report_path = md_report_path
        self.excel_path = excel_path
        self.analysis_script_path = analysis_script_path
        
        # Cache for loaded data
        self._excel_df: pd.DataFrame | None = None
        self._md_content: str | None = None
        self._analysis_script: str | None = None
    
    def get_excel_df(self) -> pd.DataFrame:
        """Load Excel file on first access."""
        if self._excel_df is None and self.excel_path:
            self._excel_df = pd.read_excel(self.excel_path)
        return self._excel_df
    
    def get_md_content(self) -> str:
        """Load MD report on first access."""
        if self._md_content is None and self.md_report_path:
            with open(self.md_report_path, "r", encoding="utf-8") as f:
                self._md_content = f.read()
        return self._md_content or ""
    
    def get_analysis_script(self) -> str:
        """Load analysis.py on first access."""
        if self._analysis_script is None and self.analysis_script_path:
            with open(self.analysis_script_path, "r", encoding="utf-8") as f:
                self._analysis_script = f.read()
        return self._analysis_script or ""


# ============================================================================
# EXCEL ACCESS TOOLS
# ============================================================================

def lookup_excel_rows(
    ctx: CritiqueToolContext,
    row_ids: list[int],
    columns: list[str] | None = None,
) -> list[dict]:
    """
    Fetch specific rows from source Excel by row_id.
    
    Args:
        ctx: Tool context
        row_ids: List of row IDs to retrieve
        columns: Optional list of columns to include
    
    Returns:
        List of row dicts (max 50 rows)
    """
    # Safety limit
    row_ids = row_ids[:50]
    
    # Try ledger first (already in memory)
    results = []
    for row_id in row_ids:
        row = ctx.ledger[ctx.ledger["row_id"] == row_id]
        if not row.empty:
            row_dict = row.iloc[0].to_dict()
            if columns:
                row_dict = {k: v for k, v in row_dict.items() if k in columns}
            # Truncate long strings
            for k, v in row_dict.items():
                if isinstance(v, str) and len(v) > 100:
                    row_dict[k] = v[:100] + "..."
            results.append(row_dict)
    
    return results


def search_excel(
    ctx: CritiqueToolContext,
    column: str,
    contains: str,
    limit: int = 20,
) -> list[dict]:
    """
    Search Excel/ledger for rows matching a criteria.
    
    Args:
        ctx: Tool context
        column: Column to search in
        contains: Search term
        limit: Max rows to return
    
    Returns:
        List of matching row dicts
    """
    if column not in ctx.ledger.columns:
        return []
    
    mask = ctx.ledger[column].astype(str).str.contains(
        contains, case=False, na=False
    )
    matches = ctx.ledger[mask].head(limit)
    
    results = []
    for _, row in matches.iterrows():
        row_dict = {
            "row_id": int(row.get("row_id", 0)),
            column: str(row.get(column, ""))[:80],
            "bucket": str(row.get("bucket", "")),
            "confidence": int(row.get("confidence", 0)),
        }
        results.append(row_dict)
    
    return results


def get_excel_statistics(
    ctx: CritiqueToolContext,
    column: str,
    filter_bucket: str | None = None,
) -> dict:
    """
    Get statistics about a column.
    
    Args:
        ctx: Tool context
        column: Column to analyze
        filter_bucket: Optional bucket filter
    
    Returns:
        Statistics dict
    """
    df = ctx.ledger
    if filter_bucket:
        df = df[df["bucket"] == filter_bucket]
    
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}
    
    col_data = df[column]
    stats = {
        "total_rows": len(df),
        "non_null": int(col_data.notna().sum()),
        "unique_values": int(col_data.nunique()),
    }
    
    # Add top values for string columns
    if col_data.dtype == object:
        value_counts = col_data.value_counts().head(10)
        stats["top_values"] = value_counts.to_dict()
    
    return stats


# ============================================================================
# MD REPORT TOOLS
# ============================================================================

def read_md_section(
    ctx: CritiqueToolContext,
    section: str,
) -> str:
    """
    Read a specific section of the MD report.
    
    Args:
        ctx: Tool context
        section: Section name (VERIFIED, HIGHLY_LIKELY, etc.)
    
    Returns:
        Section content (truncated if too long)
    """
    content = ctx.get_md_content()
    if not content:
        return "MD report not available"
    
    # Map section names to headers
    section_map = {
        "VERIFIED": "## VERIFIED - RECOMMENDED",
        "VERIFIED_AUDITED_OUT": "## VERIFIED - AUDITED OUT",
        "HIGHLY_LIKELY": "## HIGHLY LIKELY - RECOMMENDED",
        "HIGHLY_LIKELY_AUDITED_OUT": "## HIGHLY LIKELY - AUDITED OUT",
        "NEEDS_VERIFICATION": "## NEEDS VERIFICATION",
        "SUMMARY": "## Summary",
    }
    
    header = section_map.get(section, f"## {section}")
    
    # Find section start
    start_idx = content.find(header)
    if start_idx == -1:
        return f"Section '{section}' not found"
    
    # Find section end (next ## header)
    end_idx = content.find("\n## ", start_idx + 1)
    if end_idx == -1:
        end_idx = len(content)
    
    section_content = content[start_idx:end_idx]
    
    # Truncate if too long (>5000 chars)
    if len(section_content) > 5000:
        section_content = section_content[:5000] + "\n... [TRUNCATED]"
    
    return section_content


def search_md_report(
    ctx: CritiqueToolContext,
    search_term: str,
    section: str | None = None,
) -> list[dict]:
    """
    Search MD report for entries containing text.
    
    Args:
        ctx: Tool context
        search_term: Text to search for
        section: Optional section to limit search
    
    Returns:
        List of matching lines with context
    """
    content = ctx.get_md_content()
    if not content:
        return []
    
    if section:
        content = read_md_section(ctx, section)
    
    results = []
    lines = content.split("\n")
    
    for i, line in enumerate(lines):
        if search_term.lower() in line.lower():
            results.append({
                "line_num": i + 1,
                "content": line[:200],
                "context_before": lines[i-1][:100] if i > 0 else "",
            })
            if len(results) >= 20:
                break
    
    return results


# ============================================================================
# LEDGER ACCESS TOOLS
# ============================================================================

def query_ledger(
    ctx: CritiqueToolContext,
    bucket: str | None = None,
    min_confidence: int | None = None,
    max_confidence: int | None = None,
    ean_match: bool | None = None,
    limit: int = 30,
) -> list[dict]:
    """
    Query the analysis ledger with filters.
    
    Args:
        ctx: Tool context
        bucket: Filter by bucket
        min_confidence: Minimum confidence
        max_confidence: Maximum confidence
        ean_match: Filter for EAN matches only
        limit: Max rows to return
    
    Returns:
        List of matching row dicts
    """
    df = ctx.ledger.copy()
    
    if bucket:
        df = df[df["bucket"] == bucket]
    
    if min_confidence is not None and "confidence" in df.columns:
        df = df[df["confidence"] >= min_confidence]
    
    if max_confidence is not None and "confidence" in df.columns:
        df = df[df["confidence"] <= max_confidence]
    
    if ean_match is True:
        if "supplier_ean" in df.columns and "amazon_ean" in df.columns:
            df = df[
                (df["supplier_ean"].notna()) &
                (df["amazon_ean"].notna()) &
                (df["supplier_ean"].astype(str) != "") &
                (df["amazon_ean"].astype(str) != "") &
                (df["supplier_ean"].astype(str) != "-") &
                (df["amazon_ean"].astype(str) != "-") &
                (df["supplier_ean"].astype(str) == df["amazon_ean"].astype(str))
            ]
    
    df = df.head(limit)
    
    results = []
    for _, row in df.iterrows():
        row_dict = {
            "row_id": int(row.get("row_id", 0)),
            "supplier_title": str(row.get("supplier_title", ""))[:60],
            "amazon_title": str(row.get("amazon_title", ""))[:60],
            "bucket": str(row.get("bucket", "")),
            "confidence": int(row.get("confidence", 0)),
            "adjusted_profit": float(row.get("adjusted_profit", 0)),
            "supplier_ean": str(row.get("supplier_ean", "")),
            "amazon_ean": str(row.get("amazon_ean", "")),
        }
        results.append(row_dict)
    
    return results


def get_ledger_row(
    ctx: CritiqueToolContext,
    row_ids: list[int],
) -> list[dict]:
    """
    Get full details for specific ledger rows.
    
    Args:
        ctx: Tool context
        row_ids: Row IDs to fetch
    
    Returns:
        List of full row dicts
    """
    return lookup_excel_rows(ctx, row_ids)


# ============================================================================
# ANALYSIS SCRIPT TOOLS
# ============================================================================

def read_script_function(
    ctx: CritiqueToolContext,
    function_name: str,
) -> str:
    """
    Read a specific function from analysis.py.
    
    Args:
        ctx: Tool context
        function_name: Name of function to read
    
    Returns:
        Function code
    """
    script = ctx.get_analysis_script()
    if not script:
        return "Analysis script not available"
    
    # Simple regex-based extraction (works for most cases)
    import re
    
    # Match function definition
    pattern = rf"^def {function_name}\s*\([^)]*\).*?(?=\n(?:def |class |$))"
    match = re.search(pattern, script, re.MULTILINE | re.DOTALL)
    
    if match:
        return match.group(0)[:3000]  # Truncate long functions
    
    return f"Function '{function_name}' not found"


def search_script(
    ctx: CritiqueToolContext,
    pattern: str,
) -> list[dict]:
    """
    Search analysis.py for code containing pattern.
    
    Args:
        ctx: Tool context
        pattern: Text pattern to search
    
    Returns:
        List of matching lines
    """
    script = ctx.get_analysis_script()
    if not script:
        return []
    
    results = []
    lines = script.split("\n")
    
    for i, line in enumerate(lines):
        if pattern.lower() in line.lower():
            results.append({
                "line_num": i + 1,
                "content": line[:150],
            })
            if len(results) >= 20:
                break
    
    return results


# ============================================================================
# TOOL REGISTRY
# ============================================================================

CRITIQUE_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "lookup_excel_rows",
            "description": "Fetch specific rows from source Excel by row_id. Returns row data for analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "row_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of row IDs to retrieve (max 50)"
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: specific columns to include"
                    }
                },
                "required": ["row_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_excel",
            "description": "Search ledger for rows where a column contains a search term",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {"type": "string", "description": "Column name to search"},
                    "contains": {"type": "string", "description": "Text to search for"},
                    "limit": {"type": "integer", "description": "Max results (default 20)", "default": 20}
                },
                "required": ["column", "contains"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_ledger",
            "description": "Query the analysis ledger with filters (bucket, confidence, EAN match)",
            "parameters": {
                "type": "object",
                "properties": {
                    "bucket": {"type": "string", "description": "Filter by bucket name"},
                    "min_confidence": {"type": "integer", "description": "Minimum confidence score"},
                    "max_confidence": {"type": "integer", "description": "Maximum confidence score"},
                    "ean_match": {"type": "boolean", "description": "Only rows with matching EANs"},
                    "limit": {"type": "integer", "description": "Max results (default 30)", "default": 30}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_md_section",
            "description": "Read a specific section of the MD report",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "description": "Section name",
                        "enum": ["VERIFIED", "VERIFIED_AUDITED_OUT", "HIGHLY_LIKELY", 
                                "HIGHLY_LIKELY_AUDITED_OUT", "NEEDS_VERIFICATION", "SUMMARY"]
                    }
                },
                "required": ["section"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_script_function",
            "description": "Read a specific function from the analysis script",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_name": {"type": "string", "description": "Name of function to read"}
                },
                "required": ["function_name"]
            }
        }
    }
]


def execute_tool(
    ctx: CritiqueToolContext,
    tool_name: str,
    arguments: dict,
) -> Any:
    """
    Execute a tool function by name.
    
    Args:
        ctx: Tool context
        tool_name: Name of tool to execute
        arguments: Tool arguments
    
    Returns:
        Tool result
    """
    tool_map = {
        "lookup_excel_rows": lookup_excel_rows,
        "search_excel": search_excel,
        "get_excel_statistics": get_excel_statistics,
        "read_md_section": read_md_section,
        "search_md_report": search_md_report,
        "query_ledger": query_ledger,
        "get_ledger_row": get_ledger_row,
        "read_script_function": read_script_function,
        "search_script": search_script,
    }
    
    func = tool_map.get(tool_name)
    if not func:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        return func(ctx, **arguments)
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
