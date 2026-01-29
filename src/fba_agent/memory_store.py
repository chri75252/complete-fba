from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fba_agent.atomic import write_json_atomic
from fba_agent.types import SupplierNamingConvention


def supplier_id_from_name(name: str) -> str:
    name = name.strip()
    if not name:
        return "unknown_supplier"
    return (
        name.lower()
        .replace("https://", "")
        .replace("http://", "")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )


def memory_paths(memory_dir: Path, supplier_id: str) -> dict[str, Path]:
    base = memory_dir / "suppliers" / supplier_id
    return {
        "base": base,
        "calibration": base / "calibration.json",
        "trap_library": base / "trap_library.jsonl",
        "overrides": base / "overrides.jsonl",
        "brand_aliases": base / "brand_aliases.json",
        "run_history": base / "run_history.json",
    }


def global_memory_paths(memory_dir: Path) -> dict[str, Path]:
    """Return paths for global memory files."""
    base = memory_dir / "global"
    return {
        "base": base,
        "trap_library": base / "trap_library.jsonl",
        "brand_corrections": base / "brand_corrections.json",
    }


def load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    """Load JSONL file (one JSON object per line)."""
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return items


def load_global_traps(memory_dir: Path) -> list[dict]:
    """
    Load global trap library.
    
    Global traps include universal shields that apply to ALL suppliers:
    - dimension_shield: cm, mm, inch, etc.
    - spec_x_shield: magnification, zoom, led, etc.
    - capacity_multipack: ml, l, g, kg, etc.
    """
    paths = global_memory_paths(memory_dir)
    return load_jsonl(paths["trap_library"])


def load_run_history(memory_dir: Path, supplier_id: str, k: int = 1) -> list[dict]:
    """
    Load last K run history entries for a supplier.
    
    NOTE: Changed default from k=2 to k=1 to compare against only 1 past report.
    This allows for full ledger comparison instead of just bucket count comparison.
    
    Args:
        memory_dir: Memory directory root
        supplier_id: Supplier identifier
        k: Number of recent runs to return (default: 1)
    
    Returns:
        List of run history entries (most recent last)
    """
    paths = memory_paths(memory_dir, supplier_id)
    history = load_json(paths["run_history"]) or []
    if not isinstance(history, list):
        history = []
    return history[-k:] if len(history) > k else history


def persist_run_history(
    memory_dir: Path,
    supplier_id: str,
    run_entry: dict,
    max_entries: int = 10,
) -> None:
    """
    Append run entry to supplier history (keep last N).
    
    Args:
        memory_dir: Memory directory root
        supplier_id: Supplier identifier
        run_entry: Run summary to append
        max_entries: Maximum history entries to keep (default: 10)
    """
    paths = memory_paths(memory_dir, supplier_id)
    paths["base"].mkdir(parents=True, exist_ok=True)
    
    history = load_json(paths["run_history"]) or []
    if not isinstance(history, list):
        history = []
    
    history.append(run_entry)
    if len(history) > max_entries:
        history = history[-max_entries:]
    
    write_json_atomic(paths["run_history"], history)


def load_supplier_memory(memory_dir: Path, supplier_id: str) -> dict[str, Any]:
    paths = memory_paths(memory_dir, supplier_id)
    return {
        "paths": {k: str(v) for k, v in paths.items()},
        "calibration": load_json(paths["calibration"]),
        "brand_aliases": load_json(paths["brand_aliases"]) or {},
        "overrides_path": paths["overrides"],
        "trap_library_path": paths["trap_library"],
        "supplier_traps": load_jsonl(paths["trap_library"]),
        "run_history": load_json(paths["run_history"]) or [],
    }


def merge_calibration(
    supplier_id: str,
    memory_bundle: dict[str, Any],
    preflight_naming: SupplierNamingConvention,
    overrides_path: Path | None,
    global_traps: list[dict] | None = None,
) -> tuple[SupplierNamingConvention, dict[str, Any]]:
    """
    Merge calibration with strict precedence order.
    
    Precedence (highest to lowest):
    1. User overrides (from overrides.jsonl)
    2. Supplier traps (from supplier trap_library.jsonl)
    3. Supplier calibration (from supplier calibration.json)
    4. Global trap library (from global trap_library.jsonl)
    5. Preflight output (from current run preflight)
    6. Defaults (hardcoded in SupplierNamingConvention)
    
    Args:
        supplier_id: Supplier identifier
        memory_bundle: Output from load_supplier_memory()
        preflight_naming: Current preflight calibration output
        overrides_path: Path to overrides JSONL (optional)
        global_traps: Global trap library entries (optional)
    
    Returns:
        Tuple of (merged SupplierNamingConvention, merge diff for logging)
    """
    # Start with preflight as base (which includes defaults)
    merged = preflight_naming.__dict__.copy()
    
    # Apply global traps (layer 4)
    if global_traps:
        for trap in global_traps:
            trap_type = trap.get("type")
            if trap_type == "dimension_shield":
                keywords = trap.get("keywords", [])
                existing = set(merged.get("dimension_shield_keywords", []))
                merged["dimension_shield_keywords"] = list(existing | set(keywords))
            elif trap_type == "spec_x_shield":
                keywords = trap.get("keywords", [])
                existing = set(merged.get("spec_x_shield_keywords", []))
                merged["spec_x_shield_keywords"] = list(existing | set(keywords))
    
    # Apply existing supplier calibration (layer 3)
    existing_cal = (memory_bundle.get("calibration") or {}).get("config") or {}
    merged.update(existing_cal)
    
    # Apply supplier traps (layer 2)
    supplier_traps = memory_bundle.get("supplier_traps", [])
    for trap in supplier_traps:
        trap_type = trap.get("type")
        if trap_type == "dimension_shield":
            keywords = trap.get("keywords", [])
            existing = set(merged.get("dimension_shield_keywords", []))
            merged["dimension_shield_keywords"] = list(existing | set(keywords))
        elif trap_type == "spec_x_shield":
            keywords = trap.get("keywords", [])
            existing = set(merged.get("spec_x_shield_keywords", []))
            merged["spec_x_shield_keywords"] = list(existing | set(keywords))
        elif trap_type == "pack_keyword":
            keywords = trap.get("keywords", [])
            existing = set(merged.get("explicit_units", []))
            merged["explicit_units"] = list(existing | set(keywords))
    
    # Apply user overrides (layer 1 — highest priority)
    if overrides_path and overrides_path.exists():
        for line in overrides_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "SUPPLIER_NAMING_CONVENTION" in obj:
                naming_overrides = obj["SUPPLIER_NAMING_CONVENTION"]
                if isinstance(naming_overrides, dict):
                    merged.update(naming_overrides)

    naming = SupplierNamingConvention(**merged)
    diff = {
        "supplier_id": supplier_id,
        "preflight": preflight_naming.__dict__,
        "existing_calibration": existing_cal,
        "global_traps_applied": len(global_traps or []),
        "supplier_traps_applied": len(supplier_traps),
        "merged": naming.__dict__,
        "precedence": "overrides > supplier traps > supplier calibration > global traps > preflight > defaults",
    }
    return naming, diff


def persist_calibration(memory_dir: Path, supplier_id: str, naming: SupplierNamingConvention, input_path: Path) -> None:
    paths = memory_paths(memory_dir, supplier_id)
    paths["base"].mkdir(parents=True, exist_ok=True)
    payload = {
        "supplier_id": supplier_id,
        "source_file": str(input_path),
        "config": naming.__dict__,
    }
    write_json_atomic(paths["calibration"], payload)


def show_supplier_memory(memory_dir: Path, supplier: str) -> str:
    supplier_id = supplier_id_from_name(supplier)
    bundle = load_supplier_memory(memory_dir, supplier_id)
    cal = bundle.get("calibration") or {}
    return json.dumps(
        {
            "supplier_id": supplier_id,
            "calibration_present": bool(cal),
            "calibration_config_keys": sorted(list((cal.get("config") or {}).keys())),
            "paths": bundle.get("paths"),
        },
        indent=2,
        ensure_ascii=False,
    )

