"""Verify execute_tool_call preserves LLM-provided sandbox_suffix."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _find_workflow_key_for_supplier(repo_root: Path, supplier_domain: str) -> str:
    cfg_path = repo_root / "config" / "system_config.json"
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    workflows = data.get("workflows") or {}
    for k, v in workflows.items():
        if isinstance(v, dict) and v.get("supplier_name") == supplier_domain:
            return str(k)
    raise RuntimeError(f"No workflow_key found for supplier_domain={supplier_domain!r}")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))

    import control_plane.tools as tools

    for name in ("get_run_outputs", "write_output_file", "validate_run_integrity"):
        if not hasattr(tools, name):
            setattr(tools, name, lambda *a, **k: {"ok": False, "error": "stub"})

    from control_plane.chat_orchestrator import ToolCall, execute_tool_call
    import control_plane.chat_orchestrator as orch

    supplier_domain = "poundwholesale.co.uk"
    workflow_key = _find_workflow_key_for_supplier(repo_root, supplier_domain)

    run_id = "11111111-1111-1111-1111-111111111111"
    sandbox_suffix = "sandbox_20260210_143022"

    sandbox_supplier = f"{supplier_domain}__{sandbox_suffix}"
    sandbox_cat_path = (
        repo_root / "config" / f"{sandbox_supplier.replace('.co.uk', '')}_categories.json"
    )
    created = False
    if not sandbox_cat_path.exists():
        sandbox_cat_path.write_text("{}\n", encoding="utf-8")
        created = True

    try:
        setattr(
            orch,
            "write_categories_subset",
            lambda *args, **kwargs: Path("DUMMY/categories_subset.json"),
        )
        setattr(
            orch,
            "write_merged_system_config",
            lambda *args, **kwargs: Path("DUMMY/system_config.merged.json"),
        )

        def _stub_enqueue_run_job(*args, **kwargs):
            return Path("DUMMY/job.json")

        setattr(orch, "enqueue_run_job", _stub_enqueue_run_job)

        tc = ToolCall(
            name="enqueue_run",
            params={
                "workflow_key": workflow_key,
                "supplier_domain": supplier_domain,
                "runner_script": "run_custom_poundwholesale.py",
                "category_urls": ["https://example.invalid/category"],
                "max_products": 1,
                "max_products_per_category": 1,
                "run_id": run_id,
                "sandbox_suffix": sandbox_suffix,
                "notes": "verify sandbox suffix",
            },
        )

        res = execute_tool_call(tc, repo_root)

        assert res.get("ok") is True, f"Expected ok=True, got: {res}"
        assert res.get("run_id") == run_id
        assert res.get("sandbox_supplier") == sandbox_supplier
        assert sandbox_suffix != f"sandbox__{run_id[:8]}"

        print("PASS: execute_tool_call preserved sandbox_suffix")
        return 0

    finally:
        if created:
            try:
                sandbox_cat_path.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
