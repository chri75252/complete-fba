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
from control_plane.rag_retriever import load_rag_index, retrieve_rag, format_rag_context
from control_plane.rd2_policy import RagConfig, default_rag_config, should_use_rag
from control_plane.tools import (
    FinancialQuery,
    OnboardingWizardRequest,
    RunRequest,
    ask_clarify,
    enqueue_onboarding_job,
    enqueue_run_job,
    find_cached_products,
    find_linking_entries,
    list_repo_dir,
    onboarding_sanity_check,
    query_financial_rows,
    read_amazon_cache_by_asin,
    read_processing_state,
    read_repo_file,
    read_status,
    read_trace_summary,
    run_readiness_check,
    tail_file,
    write_categories_subset,
    write_merged_system_config,
)


READ_TOOLS = {
    "ask_clarify": "ask_clarify",
    "query_financial": "query_financial",
    "show_status": "show_status",
    "tail_logs": "tail_logs",
    "show_trace_summary": "show_trace_summary",
    "read_processing_state": "read_processing_state",
    "find_cached_products": "find_cached_products",
    "find_linking_entries": "find_linking_entries",
    "read_amazon_cache_by_asin": "read_amazon_cache_by_asin",
    "read_repo_file": "read_repo_file",
    "list_repo_dir": "list_repo_dir",
}

WRITE_TOOLS = {
    "enqueue_run": "enqueue_run",
    "enqueue_onboarding": "enqueue_onboarding",
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


def build_prompt(
    user_text: str,
    system_index: dict[str, Any] | None,
    rag_context: str,
    rag_meta: dict[str, Any],
) -> str:
    tools_desc = {
        "ask_clarify": {
            "type": "read",
            "params": {"user_text": "..."},
        },
        "query_financial": {
            "type": "read",
            "params": {
                "supplier_domain": "<supplier-domain>",
                "roi_min": 30,
                "netprofit_min": 5,
                "ean": None,
                "asin": None,
                "limit": 50,
            },
        },
        "show_status": {"type": "read", "params": {"run_id": "<run-id>"}},
        "tail_logs": {"type": "read", "params": {"run_id": "<run-id>", "lines": 200}},
        "show_trace_summary": {"type": "read", "params": {"limit": 3}},
        "read_processing_state": {
            "type": "read",
            "params": {"supplier_domain": "<supplier-domain>"},
        },
        "find_cached_products": {
            "type": "read",
            "params": {
                "supplier_domain": "<supplier-domain>",
                "ean": None,
                "url": None,
                "title_contains": None,
                "limit": 50,
            },
        },
        "find_linking_entries": {
            "type": "read",
            "params": {
                "supplier_domain": "<supplier-domain>",
                "supplier_ean": None,
                "amazon_asin": None,
                "supplier_url": None,
                "limit": 50,
            },
        },
        "read_amazon_cache_by_asin": {"type": "read", "params": {"asin": "<asin>"}},
        "run_readiness_check": {"type": "read", "params": {"supplier_domain": "<supplier-domain>"}},
        "onboarding_sanity_check": {
            "type": "read",
            "params": {"supplier_domain": "<supplier-domain>", "run_start_time": 0},
        },
        "enqueue_run": {
            "type": "write",
            "params": {
                "workflow_key": "<workflow_key>",
                "supplier_domain": "<supplier-domain>",
                "runner_script": "<runner-script>",
                "category_urls": ["<category-url>"],
                "max_products": 50,
                "max_products_per_category": 50,
                "notes": "user request",
            },
        },
        "read_repo_file": {
            "type": "read",
            "params": {"path": "<repo-relative-path>", "max_bytes": 200000},
        },
        "list_repo_dir": {"type": "read", "params": {"path": "<repo-relative-dir>"}},
        "enqueue_onboarding": {
            "type": "write",
            "params": {
                "run_id": "<run-id>",
                "input_path": "C:/path/to/onboarding_input.json",
                "output_path": "C:/path/to/onboarding_output.json",
                "timeout_seconds": 4200,
            },
        },
    }

    return (
        "You are a strict JSON generator. Return ONLY valid JSON (no markdown).\n"
        "Choose ONE tool to call that best answers the user.\n"
        "If the request is ambiguous or missing required info, choose tool `ask_clarify`.\n"
        "IMPORTANT: Never choose `enqueue_run` unless `category_urls` is a non-empty list.\n"
        "Allowed tools and schemas:\n"
        + json.dumps(tools_desc, indent=2)
        + "\n\nReturn JSON format:\n"
        + json.dumps({"tool": "<tool_name>", "params": {}}, indent=2)
        + "\n\nSystem index (may be null):\n"
        + json.dumps(system_index or {}, indent=2)
        + "\n\nRAG metadata (may be null):\n"
        + json.dumps(rag_meta or {}, indent=2)
        + "\n\nRAG context (may be empty):\n"
        + (rag_context or "")
        + "\n\nUser: "
        + user_text
    )


def plan_tool_call(user_text: str, repo_root: Path) -> tuple[ToolCall, dict[str, Any]]:
    provider = get_provider()
    system_index = _load_system_index(repo_root)

    rag_cfg: RagConfig = default_rag_config()
    rag_enabled = bool(rag_cfg.enabled) and should_use_rag(user_text)

    rag_index = load_rag_index(get_paths().rag_index_path)
    rag_meta: dict[str, Any] = {
        "enabled": rag_enabled,
        "ok": bool(rag_index) if rag_enabled else False,
    }

    rag_context = ""
    rag_sources: list[str] = []
    rag_scores: list[float] = []

    if rag_enabled and rag_index:
        rag_meta.update(
            {
                "doc_count": rag_index.get("doc_count", 0),
                "generated_at": rag_index.get("generated_at"),
                "top_k": rag_cfg.top_k,
            }
        )

        res = retrieve_rag(rag_index=rag_index, query=user_text, config=rag_cfg)
        chunks = res.get("chunks") or []
        rag_sources = list(res.get("sources") or [])
        rag_scores = [float(x) for x in (res.get("scores") or [])]
        rag_context = format_rag_context(chunks)

    prompt = build_prompt(user_text, system_index, rag_context, rag_meta)

    data = provider.generate_json(prompt)
    tool = str(data.get("tool") or "").strip()
    params = data.get("params") or {}
    if not isinstance(params, dict):
        params = {}

    if tool == "enqueue_run":
        urls = params.get("category_urls")
        if not isinstance(urls, list) or not [u for u in urls if isinstance(u, str) and u.strip()]:
            tool = "ask_clarify"
            params = {"user_text": user_text}

    rag_info = {
        "meta": rag_meta,
        "sources_used": rag_sources,
        "scores": rag_scores,
        "context_injected": bool(rag_context),
    }

    return ToolCall(name=tool, params=params), rag_info


def is_write_tool(tool: str) -> bool:
    return tool in WRITE_TOOLS


def execute_tool_call(tool_call: ToolCall, repo_root: Path) -> dict[str, Any]:
    name = tool_call.name
    p = tool_call.params

    if isinstance(p, dict):
        inferred_supplier_domain = None
        for key in ("supplier_domain", "supplier"):
            v = p.get(key)
            if isinstance(v, str) and v.strip():
                inferred_supplier_domain = v.strip()
                break

        url_candidates: list[str] = []
        raw_url = p.get("url")
        if isinstance(raw_url, str) and raw_url.strip():
            url_candidates.append(raw_url.strip())
        elif isinstance(raw_url, list):
            url_candidates.extend([str(u).strip() for u in raw_url if str(u).strip()])

        raw_urls = p.get("category_urls")
        if isinstance(raw_urls, list):
            url_candidates.extend([str(u).strip() for u in raw_urls if str(u).strip()])

        if inferred_supplier_domain is None and url_candidates:
            import re

            m = re.match(r"https?://([^/]+)/", url_candidates[0] + "/")
            if m:
                inferred_supplier_domain = m.group(1).lower()

        if inferred_supplier_domain is None:
            try:
                import streamlit as st

                sidebar_supplier = st.session_state.get("supplier")
                if isinstance(sidebar_supplier, str) and sidebar_supplier.strip():
                    inferred_supplier_domain = sidebar_supplier.strip()
            except Exception:
                pass

        if inferred_supplier_domain:
            p.setdefault("supplier_domain", inferred_supplier_domain)

        if "url" in p and isinstance(p.get("url"), list):
            items = [str(u).strip() for u in p.get("url") or [] if str(u).strip()]
            p["url"] = items[0] if items else ""

    if name == "ask_clarify":
        return ask_clarify(user_text=str(p.get("user_text") or "").strip() or None)

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

    if name == "read_repo_file":
        rel_path = str(p.get("path") or "")
        max_bytes = int(p.get("max_bytes") or 200000)
        return read_repo_file(repo_root, rel_path, max_bytes=max_bytes)

    if name == "list_repo_dir":
        rel_path = str(p.get("path") or "")
        return list_repo_dir(repo_root, rel_path)

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
        run_id = str(p.get("run_id") or "").strip()
        if not run_id:
            import uuid

            run_id = str(uuid.uuid4())

        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
        if not sandbox_suffix:
            sandbox_suffix = f"sandbox__{run_id[:8]}"

        sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}"

        categories_path = write_categories_subset(run_id, sandbox_supplier, req.category_urls)

        overrides = {
            "system": {
                "max_products": req.max_products,
                "max_products_per_category": req.max_products_per_category,
            },
            "workflows": {
                req.workflow_key: {
                    "supplier_name": sandbox_supplier,
                    "categories_config_path": str(categories_path),
                }
            },
        }

        merged_cfg_path = write_merged_system_config(run_id, base_cfg, overrides)
        job_path = enqueue_run_job(run_id, req, merged_cfg_path, categories_path)

        return {
            "ok": True,
            "run_id": run_id,
            "sandbox_supplier": sandbox_supplier,
            "job_path": str(job_path),
            "merged_config": str(merged_cfg_path),
            "categories": str(categories_path),
        }

    if name == "enqueue_onboarding":
        import uuid

        run_id = str(p.get("run_id") or "").strip() or str(uuid.uuid4())
        req = OnboardingWizardRequest(
            input_path=str(p.get("input_path") or ""),
            output_path=str(p.get("output_path") or ""),
            timeout_seconds=int(p.get("timeout_seconds") or 4200),
        )
        return enqueue_onboarding_job(repo_root, run_id, req)

    return {"ok": False, "error": f"Unknown tool: {name}"}


def audit_tool_call(
    user_text: str,
    tool_call: ToolCall,
    result: dict[str, Any],
    rag_info: dict[str, Any] | None = None,
) -> None:
    event = {
        "user_text": user_text,
        "tool": tool_call.name,
        "params": tool_call.params,
        "result_ok": result.get("ok"),
    }
    if rag_info:
        event["rag"] = rag_info
    append_audit(event)
