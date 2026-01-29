from __future__ import annotations

from typing import Any

import pandas as pd

from fba_agent.moonshot import chat_json, load_moonshot_config
from fba_agent.types import SupplierNamingConvention


def _heuristic_preflight(df_sample: pd.DataFrame) -> tuple[SupplierNamingConvention, list[str]]:
    warnings: list[str] = []

    sales_column = None
    for cand in ("sales_numeric", "bought_in_past_month", "Sales", "sales"):
        if cand in df_sample.columns:
            sales_column = cand
            break

    naming = SupplierNamingConvention(sales_column=sales_column or "sales_numeric")

    if sales_column is None:
        warnings.append("sales_column not detected; defaulting to sales_numeric")

    return naming, warnings


def run_preflight(df_sample: pd.DataFrame) -> tuple[SupplierNamingConvention, list[str], dict[str, Any]]:
    """
    Phase 2 target: LLM-assisted preflight.

    Behavior:
    - If MOONSHOT_API_KEY is not set: heuristic preflight (deterministic).
    - If set: call Moonshot (OpenAI-compatible) and parse JSON config; fallback to heuristic on failure.
    """
    heuristic_naming, warnings = _heuristic_preflight(df_sample)
    config = load_moonshot_config()
    if config is None:
        return heuristic_naming, warnings, {"mode": "heuristic"}

    system = (
        "You are a strict data pattern specialist for FBA supplier reports. "
        "Return ONLY valid JSON, no markdown and no code fences."
    )

    preview_cols = []
    for c in ("SupplierTitle", "AmazonTitle", "Sales", "sales_numeric", "bought_in_past_month"):
        if c in df_sample.columns:
            preview_cols.append(c)
    preview = df_sample[preview_cols].head(50).to_dict(orient="records")

    user = (
        "Analyze these rows and output a JSON object with keys:\n"
        "explicit_units (list of strings), allow_trailing_number_as_qty (bool), "
        "leading_multiplier_check (bool), dimension_shield_keywords (list of strings), "
        "brand_position ('start' or 'mixed'), sales_column (string), "
        "capacity_pattern_as_rsu (bool), spec_x_shield_keywords (list of strings), "
        "table_pipe_sanitization (bool).\n\n"
        f"Rows:\n{preview}\n\n"
        "Return ONLY JSON."
    )

    try:
        obj = chat_json(config=config, system=system, user=user)
        merged = heuristic_naming.__dict__.copy()
        merged.update(obj)
        naming = SupplierNamingConvention(**merged)
        return naming, warnings, {"mode": "moonshot", "model": config.model, "base_url": config.base_url}
    except Exception as e:  # noqa: BLE001
        warnings.append(f"Moonshot preflight failed; falling back to heuristic: {type(e).__name__}")
        return heuristic_naming, warnings, {"mode": "heuristic_fallback"}
