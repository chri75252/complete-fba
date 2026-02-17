from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from control_plane.json_io import write_json_atomic
from control_plane.paths import get_paths


def build_system_index() -> dict:
    paths = get_paths()
    repo_root = paths.repo_root

    def stat(path: Path) -> dict:
        try:
            st = path.stat()
            return {"exists": True, "mtime": st.st_mtime, "size": st.st_size}
        except FileNotFoundError:
            return {"exists": False}

    runners = sorted([p.name for p in repo_root.glob("run_custom_*.py")])
    supplier_configs = sorted(
        [
            str(p.relative_to(repo_root))
            for p in (repo_root / "config" / "supplier_configs").glob("*.json")
        ]
    )
    category_configs = sorted(
        [str(p.relative_to(repo_root)) for p in (repo_root / "config").glob("*_categories.json")]
    )

    from config.system_config_loader import SystemConfigLoader

    config_loader = SystemConfigLoader()
    full_config = config_loader.get_full_config()

    workflows = full_config.get("workflows", {})
    workflow_keys = sorted(list(workflows.keys()))

    suppliers = []
    for wf_config in workflows.values():
        supplier_name = wf_config.get("supplier_name")
        if supplier_name:
            suppliers.append(supplier_name)

    suppliers = sorted(list(set(suppliers)))

    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    return {
        "schema_version": "1.0",
        "generated_at": now,
        "repo_root": str(repo_root),
        "key_paths": {
            "system_config": str((repo_root / "config" / "system_config.json")),
            "outputs": str((repo_root / "OUTPUTS")),
            "logs": str((repo_root / "logs")),
        },
        "inventory": {
            "runners": runners,
            "supplier_configs": supplier_configs,
            "category_configs": category_configs,
            "workflow_keys": workflow_keys,
            "suppliers": suppliers,
        },
        "stats": {
            "system_config": stat(repo_root / "config" / "system_config.json"),
            "outputs": stat(repo_root / "OUTPUTS"),
        },
    }


def main() -> None:
    paths = get_paths()
    idx = build_system_index()
    write_json_atomic(paths.system_index_path, idx)
    print(f"Wrote system index: {paths.system_index_path}")


if __name__ == "__main__":
    main()
