from __future__ import annotations

from typing import Any

import pandas as pd

from fba_agent.openai_client import chat_json, load_openai_config
from fba_agent.types import SupplierNamingConvention


def validate_and_fix_calibration(ai_response: dict) -> tuple[dict, list[str]]:
    """
    Validate AI calibration response and auto-fix common issues.
    
    Fixes:
    1. Remove pack keywords from dimension/spec shield lists
    2. Remove overly broad shields like 'X', 'x', 'BY'
    3. Move measurement units from explicit_units to shields
    4. Add defaults for missing fields
    
    Returns:
        (fixed_response, warnings)
    """
    warnings = []
    
    explicit_units = set(ai_response.get("explicit_units", []))
    dim_shields = set(ai_response.get("dimension_shield_keywords", []))
    spec_shields = set(ai_response.get("spec_x_shield_keywords", []))
    
    # FIX #1: Remove pack keywords from shield lists
    pack_keywords = {"PK", "PACK", "PC", "PCS", "PIECES", "PIECE", "pk", "pack", "pc", "pcs", "pieces", "piece"}
    
    duplicates_in_dim = explicit_units & dim_shields & pack_keywords
    if duplicates_in_dim:
        warnings.append(f"AI put pack keywords in dimension_shield: {duplicates_in_dim}. Auto-fixing.")
        dim_shields -= pack_keywords
    
    duplicates_in_spec = explicit_units & spec_shields & pack_keywords
    if duplicates_in_spec:
        warnings.append(f"AI put pack keywords in spec_x_shield: {duplicates_in_spec}. Auto-fixing.")
        spec_shields -= pack_keywords
    
    # FIX #2: Don't shield generic multipliers
    overly_broad_shields = {"X", "x", "BY", "/", "-"}
    removed_broad = spec_shields & overly_broad_shields
    if removed_broad:
        warnings.append(f"Removed overly broad spec shields: {removed_broad}")
        spec_shields -= overly_broad_shields
    
    # FIX #3: Move measurement units from explicit_units to shields
    measurement_units = {"CM", "MM", "ML", "KG", "G", "L", "cm", "mm", "ml", "kg", "g", "l", "oz", "OZ", "inch", "INCH"}
    meas_in_explicit = explicit_units & measurement_units
    if meas_in_explicit:
        warnings.append(f"Measurements in explicit_units: {meas_in_explicit}. Moving to shields.")
        explicit_units -= measurement_units
        dim_shields |= (meas_in_explicit & measurement_units)
    
    # FIX #4: Add capacity multipack pattern support
    if "capacity_pattern_as_rsu" not in ai_response:
        ai_response["capacity_pattern_as_rsu"] = True
        warnings.append("Added default capacity_pattern_as_rsu=True (treats '3 x 400ml' as RSU=3)")
    
    # FIX #5: Add spec-x shield defaults if empty
    if not spec_shields:
        spec_shields = {"magnification", "zoom", "microscope", "scope", "times"}
        warnings.append("Added default spec_x_shield_keywords for feature multipliers")
    
    # Update response with fixed values
    ai_response["explicit_units"] = sorted(list(explicit_units))
    ai_response["dimension_shield_keywords"] = sorted(list(dim_shields))
    ai_response["spec_x_shield_keywords"] = sorted(list(spec_shields))
    
    return ai_response, warnings


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
    - If OPENAI_API_KEY is not set: heuristic preflight (deterministic).
    - If set: call OpenAI Chat Completions and parse JSON config; fallback to heuristic on failure.
    """
    heuristic_naming, warnings = _heuristic_preflight(df_sample)
    config = load_openai_config()
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

    # Improved prompt with detailed explanations and multi-supplier context
    user = (
        "You are analyzing product title patterns from a specific supplier's catalog. "
        "Each supplier may use different naming conventions.\n\n"
        
        "**CRITICAL: These lists must be MUTUALLY EXCLUSIVE!**\n\n"
        
        "**explicit_units** (Pack quantity keywords that ENABLE pack detection):\n"
        "- Words that indicate MULTIPACKS or QUANTITIES\n"
        "- Examples: 'pk', 'pack', 'pc', 'pcs', 'pieces', 'ct', 'count'\n"
        "- As in: '6 PK', 'PACK OF 12', '24 PC SET'\n"
        "- These trigger pack quantity detection\n\n"
        
        "**dimension_shield_keywords** (Measurement words that PREVENT pack detection):\n"
        "- Words that indicate PHYSICAL MEASUREMENTS or SIZES\n"
        "- Examples: 'cm', 'mm', 'inch', 'ml', 'kg', 'g', 'l', 'oz'\n"
        "- As in: '30CM x 40CM', '500ML BOTTLE', '2KG WEIGHT'\n"
        "- These are dimensions, NOT pack quantities\n"
        "- **DO NOT include pack keywords here!**\n\n"
        
        "**spec_x_shield_keywords** (Non-pack multipliers in specifications):\n"
        "- Words that appear with 'X' but DON'T mean packs\n"
        "- Examples: 'zoom', 'magnification', 'times' → as in '10X ZOOM', '2000X MICROSCOPE'\n"
        "- **AVOID generic words:** Don't include 'X', 'x', 'BY', '/', '-' (too broad)\n\n"
        
        f"Sample rows from THIS SUPPLIER:\n{preview}\n\n"
        
        "Return ONLY valid JSON with these keys:\n"
        "explicit_units, dimension_shield_keywords, spec_x_shield_keywords, "
        "brand_position, sales_column, allow_trailing_number_as_qty, "
        "leading_multiplier_check, capacity_pattern_as_rsu, table_pipe_sanitization"
    )

    try:
        obj = chat_json(config=config, system=system, user=user)
        
        # VALIDATE AND FIX AI RESPONSE
        obj, validation_warnings = validate_and_fix_calibration(obj)
        warnings.extend(validation_warnings)
        
        merged = heuristic_naming.__dict__.copy()
        merged.update(obj)
        naming = SupplierNamingConvention(**merged)
        return naming, warnings, {"mode": "openai_validated", "model": config.model, "base_url": config.base_url}
    except Exception as e:  # noqa: BLE001
        warnings.append(f"OpenAI preflight failed; falling back to heuristic: {type(e).__name__}")
        return heuristic_naming, warnings, {"mode": "heuristic_fallback"}
