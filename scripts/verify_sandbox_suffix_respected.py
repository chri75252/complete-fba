from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


def _pick_poundwholesale_workflow_key(repo_root: Path) -> str:
    cfg_path = repo_root / "config" / "system_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    workflows = cfg.get("workflows") or {}
    for key, data in workflows.items():
        if isinstance(data, dict) and data.get("supplier_name") == "poundwholesale.co.uk":
            return str(key)
    raise RuntimeError("Could not find a workflow_key for supplier_name=poundwholesale.co.uk")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

    import control_plane.tools as tools

    if not hasattr(tools, "get_run_outputs"):
        tools.get_run_outputs = lambda *a, **k: {"ok": False, "error": "stub"}
    if not hasattr(tools, "validate_run_integrity"):
        tools.validate_run_integrity = lambda *a, **k: {"ok": False, "error": "stub"}
    if not hasattr(tools, "write_output_file"):
        tools.write_output_file = lambda *a, **k: {"ok": False, "error": "stub"}

    from control_plane.chat_orchestrator import ToolCall, execute_tool_call

    workflow_key = _pick_poundwholesale_workflow_key(repo_root)
    supplier_domain = "poundwholesale.co.uk"
    runner_script = "run_custom_poundwholesale.py"
    run_id = "11111111-1111-1111-1111-111111111111"
    category_urls = ["https://www.poundwholesale.co.uk/test-category"]

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        merged_cfg_path = tmp / "system_config.merged.json"
        categories_path = tmp / "categories_subset.json"
        job_path = tmp / f"job_{run_id}.json"

        merged_cfg_path.write_text("{}", encoding="utf-8")
        categories_path.write_text("{}", encoding="utf-8")
        job_path.write_text("{}", encoding="utf-8")

        def _fake_write_categories_subset(*_args, **_kwargs) -> Path:
            return categories_path

        def _fake_write_merged_system_config(*_args, **_kwargs) -> Path:
            return merged_cfg_path

        def _fake_enqueue_run_job(*_args, **_kwargs) -> Path:
            return job_path

        with (
            patch(
                "control_plane.chat_orchestrator.write_categories_subset",
                _fake_write_categories_subset,
            ),
            patch(
                "control_plane.chat_orchestrator.write_merged_system_config",
                _fake_write_merged_system_config,
            ),
            patch("control_plane.chat_orchestrator.enqueue_run_job", _fake_enqueue_run_job),
            patch("shutil.copy2", lambda *_a, **_k: None),
        ):
            tool_call = ToolCall(
                name="enqueue_run",
                params={
                    "workflow_key": workflow_key,
                    "supplier_domain": supplier_domain,
                    "runner_script": runner_script,
                    "category_urls": category_urls,
                    "run_id": run_id,
                    "sandbox_suffix": "my_sandbox_suffix",
                    "max_products": 1,
                    "max_products_per_category": 1,
                    "notes": "verification",
                },
            )
            res = execute_tool_call(tool_call, repo_root)
            assert res.get("ok") is True, res
            assert res.get("sandbox_supplier") == f"{supplier_domain}__my_sandbox_suffix", res

            tool_call_placeholder = ToolCall(
                name="enqueue_run",
                params={
                    "workflow_key": workflow_key,
                    "supplier_domain": supplier_domain,
                    "runner_script": runner_script,
                    "category_urls": category_urls,
                    "run_id": run_id,
                    "sandbox_suffix": "<optional_for_resuming>",
                    "max_products": 1,
                    "max_products_per_category": 1,
                    "notes": "verification",
                },
            )
            res2 = execute_tool_call(tool_call_placeholder, repo_root)
            assert res2.get("ok") is True, res2
            assert res2.get("sandbox_supplier") == f"{supplier_domain}__sandbox__{run_id[:8]}", res2

    print("PASS: execute_tool_call respects sandbox_suffix; placeholder does not overwrite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
