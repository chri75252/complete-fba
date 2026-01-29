from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.audit import append_audit
from control_plane.llm.providers import get_provider
from control_plane.json_io import read_json
from control_plane.paths import get_paths
from control_plane.tools import (
    FinancialQuery,
    RunRequest,
    enqueue_run_job,
    find_cached_products,
    find_linking_entries,
    onboarding_sanity_check,
    query_financial_rows,
    read_amazon_cache_by_asin,
    read_processing_state,
    read_status,
    read_trace_summary,
    run_readiness_check,
    tail_file,
    write_categories_subset,
    write_merged_system_config,
)


READ_TOOLS = {
    "query_financial": "query_financial",
    "show_status": "show_status",
    "tail_logs": "tail_logs",
    "show_trace_summary": "show_trace_summary",
    "read_processing_state": "read_processing_state",
    "find_cached_products": "find_cached_products",
    "find_linking_entries": "find_linking_entries",
    "read_amazon_cache_by_asin": "read_amazon_cache_by_asin",
}

WRITE_TOOLS = {
    "enqueue_run": "enqueue_run",
}


@dataclass(frozen=True)
class ToolCall:
    name: str
    params: dict[str, Any]


def _load_system_index(repo_root: Path) -> dict[str, Any] | None:
    idx_path = repo_root / "OUTPUTS" / "CONTROL_PLANE" / "index" / "system_index.json"
    if not idx_path.exists():
        return None
    return read_json(idx_path)


def build_prompt(user_text: str, system_index: dict[str, Any] | None) -> str:
    tools_desc = {
        "query_financial": {
            "type": "read",
            "params": {
                "supplier_domain": "poundwholesale.co.uk",
                "roi_min": 30,
                "netprofit_min": 5,
                "ean": None,
                "asin": None,
                "limit": 50,
            },
        },
        "show_status": {"type": "read", "params": {"run_id": "..."}},
        "tail_logs": {"type": "read", "params": {"run_id": "...", "lines": 200}},
        "show_trace_summary": {"type": "read", "params": {"limit": 3}},
        "read_processing_state": {"type": "read", "params": {"supplier_domain": "..."}},
        "find_cached_products": {
            "type": "read",
            "params": {
                "supplier_domain": "...",
                "ean": None,
                "url": None,
                "title_contains": None,
                "limit": 50,
            },
        },
        "find_linking_entries": {
            "type": "read",
            "params": {
                "supplier_domain": "...",
                "supplier_ean": None,
                "amazon_asin": None,
                "supplier_url": None,
                "limit": 50,
            },
        },
        "read_amazon_cache_by_asin": {"type": "read", "params": {"asin": "..."}},
        "run_readiness_check": {"type": "read", "params": {"supplier_domain": "..."}},
        "onboarding_sanity_check": {
            "type": "read",
            "params": {"supplier_domain": "...", "run_start_time": 0},
        },
        "enqueue_run": {
            "type": "write",
            "params": {
                "workflow_key": "poundwholesale_workflow",
                "supplier_domain": "poundwholesale.co.uk",
                "runner_script": "run_custom_poundwholesale.py",
                "category_urls": ["https://..."],
                "max_products": 50,
                "max_products_per_category": 50,
                "notes": "user request",
            },
        },
    }

    return (
        "You are a strict JSON generator. Return ONLY valid JSON (no markdown).\n"
        "Choose ONE tool to call that best answers the user.\n"
        "Allowed tools and schemas:\n"
        + json.dumps(tools_desc, indent=2)
        + "\n\nReturn JSON format:\n"
        + json.dumps({"tool": "<tool_name>", "params": {}}, indent=2)
        + "\n\nSystem index (may be null):\n"
        + json.dumps(system_index or {}, indent=2)
        + "\n\nUser: "
        + user_text
    )


def plan_tool_call(user_text: str, repo_root: Path) -> ToolCall:
    provider = get_provider()
    system_index = _load_system_index(repo_root)
    prompt = build_prompt(user_text, system_index)

    data = provider.generate_json(prompt)
    tool = str(data.get("tool") or "").strip()
    params = data.get("params") or {}
    if not isinstance(params, dict):
        params = {}

    return ToolCall(name=tool, params=params)


def is_write_tool(tool: str) -> bool:
    return tool in WRITE_TOOLS


def execute_tool_call(tool_call: ToolCall, repo_root: Path) -> dict[str, Any]:
    name = tool_call.name
    p = tool_call.params

    if name == "query_financial":
        q = FinancialQuery(
            supplier_domain=str(p.get("supplier_domain") or ""),
            roi_min=p.get("roi_min"),
            roi_max=p.get("roi_max"),
            netprofit_min=p.get("netprofit_min"),
            netprofit_max=p.get("netprofit_max"),
            ean=p.get("ean"),
            asin=p.get("asin"),
            limit=int(p.get("limit") or 50),
        )
        return query_financial_rows(repo_root, q)

    if name == "show_status":
        run_id = str(p.get("run_id") or "").strip()
        return {"ok": True, "status": read_status(run_id)}

    if name == "tail_logs":
        run_id = str(p.get("run_id") or "").strip()
        lines = int(p.get("lines") or 200)
        paths = get_paths()
        log_path = paths.logs_dir / f"{run_id}.log"
        return {"ok": True, "lines": tail_file(log_path, lines=lines), "log_path": str(log_path)}

    if name == "show_trace_summary":
        limit = int(p.get("limit") or 5)
        return read_trace_summary(repo_root, limit=limit)

    if name == "read_processing_state":
        supplier_domain = str(p.get("supplier_domain") or "")
        return {"ok": True, "state": read_processing_state(repo_root, supplier_domain)}

    if name == "find_cached_products":
        supplier_domain = str(p.get("supplier_domain") or "")
        return find_cached_products(
            repo_root,
            supplier_domain,
            ean=p.get("ean"),
            url=p.get("url"),
            title_contains=p.get("title_contains"),
            limit=int(p.get("limit") or 50),
        )

    if name == "find_linking_entries":
        supplier_domain = str(p.get("supplier_domain") or "")
        return find_linking_entries(
            repo_root,
            supplier_domain,
            supplier_ean=p.get("supplier_ean"),
            amazon_asin=p.get("amazon_asin"),
            supplier_url=p.get("supplier_url"),
            limit=int(p.get("limit") or 50),
        )

    if name == "read_amazon_cache_by_asin":
        asin = str(p.get("asin") or "")
        return {"ok": True, "result": read_amazon_cache_by_asin(repo_root, asin)}

    if name == "run_readiness_check":
        supplier_domain = str(p.get("supplier_domain") or "")
        return run_readiness_check(repo_root, supplier_domain)

    if name == "onboarding_sanity_check":
        supplier_domain = str(p.get("supplier_domain") or "")
        run_start_time = float(p.get("run_start_time") or 0)
        if run_start_time <= 0:
            run_start_time = time.time() - 3600
        return onboarding_sanity_check(repo_root, supplier_domain, run_start_time)

    if name == "enqueue_run":
        req = RunRequest(
            supplier_domain=str(p.get("supplier_domain") or ""),
            workflow_key=str(p.get("workflow_key") or ""),
            runner_script=str(p.get("runner_script") or ""),
            category_urls=list(p.get("category_urls") or []),
            max_products=int(p.get("max_products") or 0),
            max_products_per_category=int(p.get("max_products_per_category") or 0),
            notes=p.get("notes"),
        )

        base_cfg = read_json(repo_root / "config" / "system_config.json")
        run_id = p.get("run_id") or ""
        if not run_id:
            import uuid

            run_id = str(uuid.uuid4())

        categories_path = write_categories_subset(run_id, req.supplier_domain, req.category_urls)

        overrides = {
            "system": {
                "max_products": req.max_products,
                "max_products_per_category": req.max_products_per_category,
            },
            "workflows": {
                req.workflow_key: {
                    "categories_config_path": str(categories_path),
                }
            },
        }

        merged_cfg_path = write_merged_system_config(run_id, base_cfg, overrides)
        job_path = enqueue_run_job(run_id, req, merged_cfg_path, categories_path)

        return {
            "ok": True,
            "run_id": run_id,
            "job_path": str(job_path),
            "merged_config": str(merged_cfg_path),
            "categories": str(categories_path),
        }

    return {"ok": False, "error": f"Unknown tool: {name}"}


def audit_tool_call(user_text: str, tool_call: ToolCall, result: dict[str, Any]) -> None:
    append_audit(
        {
            "user_text": user_text,
            "tool": tool_call.name,
            "params": tool_call.params,
            "result_ok": result.get("ok"),
        }
    )
