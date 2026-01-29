from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from control_plane.normalize import supplier_domain_to_underscore


def get_processing_state_path(repo_root: Path, supplier_domain: str) -> Path:
    filename = f"{supplier_domain_to_underscore(supplier_domain)}_processing_state.json"
    return repo_root / "OUTPUTS" / "CACHE" / "processing_states" / filename


def read_processing_state(repo_root: Path, supplier_domain: str) -> dict[str, Any] | None:
    path = get_processing_state_path(repo_root, supplier_domain)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def summarize_processing_state(state: dict[str, Any]) -> dict[str, Any]:
    # Keep this defensive: schema may evolve.
    system_progression = state.get("system_progression", {}) if state else {}

    def get_num(key: str) -> int:
        try:
            return int(system_progression.get(key, 0) or 0)
        except Exception:
            return 0

    return {
        "current_phase": system_progression.get("current_phase"),
        "persistent_category_index": get_num("persistent_category_index"),
        "total_categories": get_num("total_categories"),
        "current_category_url": system_progression.get("current_category_url"),
        "supplier_products_completed": get_num("supplier_products_completed"),
        "supplier_products_needing_extraction": get_num("supplier_products_needing_extraction"),
        "amazon_products_completed": get_num("amazon_products_completed"),
        "amazon_products_needing_analysis": get_num("amazon_products_needing_analysis"),
    }
