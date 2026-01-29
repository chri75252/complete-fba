"""Internal pre-filtering before analysis.

Prefilter removes rows that are obviously unprofitable BEFORE they go through
the full analysis pipeline. This is different from FILTERED_OUT, which happens
AFTER analysis confirms a match but with profit issues.

Prefilter tracking:
- prefilter_excluded_count: How many rows were removed
- prefilter_rules_applied: Which rules triggered
- Excluded rows are NOT in the main ledger but are tracked separately
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd


@dataclass
class PrefilterResult:
    """Result of applying prefilter rules to a DataFrame."""

    filtered_df: pd.DataFrame
    excluded_df: pd.DataFrame
    excluded_count: int
    rules_applied: list[dict]
    total_original: int


@dataclass
class PrefilterRule:
    """A single prefilter rule."""

    name: str
    description: str
    condition: Callable[[pd.DataFrame], pd.Series]  # Returns boolean mask of rows to KEEP
    enabled: bool = True


def _rule_sales_positive(df: pd.DataFrame) -> pd.Series:
    """Keep rows where Sales > 0 (or Sales is null)."""
    sales = pd.to_numeric(df.get("Sales"), errors="coerce")
    # Keep if Sales > 0 OR Sales is null (don't exclude missing data)
    return (sales > 0) | sales.isna()


def _rule_net_profit_positive(df: pd.DataFrame) -> pd.Series:
    """Keep rows where NetProfit > 0 (or NetProfit is null)."""
    profit = pd.to_numeric(df.get("NetProfit"), errors="coerce")
    # Keep if NetProfit > 0 OR null
    return (profit > 0) | profit.isna()


def _rule_has_asin(df: pd.DataFrame) -> pd.Series:
    """Keep rows where ASIN is present and non-empty."""
    asin = df.get("ASIN", pd.Series([""] * len(df)))
    return asin.astype(str).str.strip().str.len() > 0


def _rule_has_title(df: pd.DataFrame) -> pd.Series:
    """Keep rows where at least one of SupplierTitle or AmazonTitle exists."""
    s_title = df.get("SupplierTitle", pd.Series([""] * len(df))).astype(str).str.strip()
    a_title = df.get("AmazonTitle", pd.Series([""] * len(df))).astype(str).str.strip()
    return (s_title.str.len() > 0) | (a_title.str.len() > 0)


# Default rules (can be customized via config)
DEFAULT_RULES = [
    PrefilterRule(
        name="sales_positive",
        description="Exclude rows with Sales <= 0",
        condition=_rule_sales_positive,
        enabled=True,
    ),
    PrefilterRule(
        name="net_profit_positive",
        description="Exclude rows with NetProfit <= 0",
        condition=_rule_net_profit_positive,
        enabled=True,
    ),
    PrefilterRule(
        name="has_asin",
        description="Exclude rows without ASIN",
        condition=_rule_has_asin,
        enabled=False,  # Disabled by default — we handle missing ASIN in analysis
    ),
    PrefilterRule(
        name="has_title",
        description="Exclude rows without any title",
        condition=_rule_has_title,
        enabled=False,  # Disabled by default
    ),
]


def get_default_rules() -> list[PrefilterRule]:
    """Get a copy of default prefilter rules."""
    return [
        PrefilterRule(
            name=r.name,
            description=r.description,
            condition=r.condition,
            enabled=r.enabled,
        )
        for r in DEFAULT_RULES
    ]


def apply_prefilter(
    df: pd.DataFrame,
    rules: list[PrefilterRule] | None = None,
    custom_rules: dict | None = None,
) -> PrefilterResult:
    """
    Apply prefilter rules to exclude obviously unprofitable rows.
    
    Args:
        df: DataFrame to filter
        rules: List of PrefilterRule objects (default: DEFAULT_RULES)
        custom_rules: Dict of rule_name -> enabled (True/False) to customize defaults
    
    Returns:
        PrefilterResult with filtered_df, excluded_df, and statistics
    
    Example:
        result = apply_prefilter(df, custom_rules={"sales_positive": False})
        # This disables the sales_positive rule
    """
    if rules is None:
        rules = get_default_rules()
    
    # Apply custom overrides
    if custom_rules:
        for rule in rules:
            if rule.name in custom_rules:
                rule.enabled = custom_rules[rule.name]
    
    total_original = len(df)
    keep_mask = pd.Series([True] * len(df), index=df.index)
    rules_applied = []
    
    for rule in rules:
        if not rule.enabled:
            continue
        
        rule_mask = rule.condition(df)
        excluded_by_rule = (~rule_mask).sum()
        
        rules_applied.append({
            "name": rule.name,
            "description": rule.description,
            "excluded_count": int(excluded_by_rule),
        })
        
        keep_mask = keep_mask & rule_mask
    
    filtered_df = df[keep_mask].copy()
    excluded_df = df[~keep_mask].copy()
    
    return PrefilterResult(
        filtered_df=filtered_df,
        excluded_df=excluded_df,
        excluded_count=len(excluded_df),
        rules_applied=rules_applied,
        total_original=total_original,
    )


def prefilter_summary(result: PrefilterResult) -> dict:
    """Generate a summary dict for logging/reporting."""
    return {
        "total_original": result.total_original,
        "excluded_count": result.excluded_count,
        "remaining_count": len(result.filtered_df),
        "exclusion_rate": round(result.excluded_count / result.total_original * 100, 2) if result.total_original > 0 else 0,
        "rules_applied": result.rules_applied,
    }
