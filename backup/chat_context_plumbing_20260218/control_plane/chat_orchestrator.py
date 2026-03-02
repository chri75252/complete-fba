from __future__ import annotations

import json
import re
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
    ProductListRefreshRequest,
    RunRequest,
    ask_clarify,
    enqueue_onboarding_job,
    enqueue_product_list_refresh,
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
    "cancel_run": "cancel_run",
    "enqueue_onboarding": "enqueue_onboarding",
    "enqueue_product_list_refresh": "enqueue_product_list_refresh",
}


@dataclass(frozen=True)
class ToolCall:
    name: str
    params: dict[str, Any]
    explanation: str | None = None
    expected_outputs: list[str] | None = None


def _load_system_index(repo_root: Path) -> dict[str, Any] | None:
    idx_path = repo_root / "OUTPUTS" / "CONTROL_PLANE" / "index" / "system_index.json"
    if not idx_path.exists():
        return None
    return read_json(idx_path)


def _load_system_instructions(repo_root: Path | None) -> str:
    """Load system instructions from file if present, else return empty."""
    if not repo_root:
        return ""
    instr_path = get_paths().system_instructions_path
    if not instr_path.exists():
        return ""
    try:
        return instr_path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _infer_supplier_domain_from_url(url: str) -> str:
    """Extract supplier domain from a URL, stripping www. prefix."""
    import re

    m = re.match(r"https?://([^/]+)/", url + "/")
    if not m:
        return ""
    domain = m.group(1).lower()
    # Strip www. prefix for canonical domain matching
    return domain.replace("www.", "")


def _resolve_workflow_params(repo_root: Path, supplier_domain: str) -> tuple[str, str]:
    """
    Resolve workflow parameters for a supplier domain.

    Maps supplier_domain -> workflow_key -> runner_script using three
    matching strategies in order:
    1. Hyphenated domain match (e.g., angelwholesale.co.uk -> angelwholesale-co-uk)
    2. Workflow key base match (e.g., poundwholesale_workflow -> poundwholesale)
    3. Domain base match (e.g., clearance-king.co.uk -> clearance_king)

    Args:
        repo_root: Repository root path
        supplier_domain: Supplier domain (e.g., "angelwholesale.co.uk")

    Returns:
        Tuple of (workflow_key, runner_script)

    Raises:
        ValueError: If supplier not configured or no runner script found
    """
    # Load system config to find workflow key
    sys_cfg = read_json(repo_root / "config" / "system_config.json")
    workflows = sys_cfg.get("workflows", {})

    # Step 1: Map domain -> workflow_key
    workflow_key = next(
        (k for k, v in workflows.items() if v.get("supplier_name") == supplier_domain),
        None,
    )
    if not workflow_key:
        raise ValueError(f"Supplier '{supplier_domain}' is not configured in system_config.json")

    # Step 2: Map workflow_key -> runner_script
    idx_path = repo_root / "OUTPUTS" / "CONTROL_PLANE" / "index" / "system_index.json"
    if not idx_path.exists():
        # Fallback: glob for runner scripts if index missing
        runners = [p.name for p in repo_root.glob("run_custom_*.py")]
    else:
        runners = read_json(idx_path).get("inventory", {}).get("runners", [])

    if not runners:
        raise ValueError(f"No runner scripts found in repository")

    # Matching heuristics (in order of preference)
    # Strategy 1: Hyphenated domain (angelwholesale.co.uk -> angelwholesale-co-uk)
    domain_hyphen = supplier_domain.replace(".", "-")
    runner = next((r for r in runners if domain_hyphen in r), None)

    # Strategy 2: Workflow key base (poundwholesale_workflow -> poundwholesale)
    if not runner:
        key_base = workflow_key.replace("_workflow", "")
        runner = next((r for r in runners if key_base in r), None)

    # Strategy 3: Domain base (clearance-king.co.uk -> clearance_king)
    if not runner:
        domain_base = supplier_domain.split(".")[0]
        runner = next((r for r in runners if domain_base in r), None)

    if not runner:
        raise ValueError(
            f"No runner script found matching '{supplier_domain}' or key '{workflow_key}'. "
            f"Available runners: {', '.join(runners)}"
        )

    return workflow_key, runner


def _extract_category_urls(user_text: str, system_index: dict | None = None) -> list[str]:
    """Extract category URLs from user text. Returns list of URLs belonging to known suppliers."""
    import re
    from urllib.parse import urlparse

    # Match http/https URLs
    url_pattern = r'https?://[^\s<>"\')\]]+[^\s<>"\')\].,;!?]'
    urls = re.findall(url_pattern, user_text)

    if not system_index:
        # Without index, return all URLs - caller should ensure index is loaded
        return urls

    known_domains = system_index.get("inventory", {}).get("suppliers", [])

    category_urls = []
    for u in urls:
        parsed = urlparse(u)
        domain = parsed.netloc.replace("www.", "").lower()
        if any(d in domain for d in known_domains):
            category_urls.append(u)

    return category_urls


def build_prompt(
    user_text: str,
    system_index: dict[str, Any] | None,
    rag_context: str,
    rag_meta: dict[str, Any],
    repo_root: Path | None = None,
) -> str:
    system_instructions = _load_system_instructions(repo_root) if repo_root else ""

    tools_desc = {
        "ask_clarify": {
            "type": "read",
            "params": {"user_text": "..."},
        },
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
        "show_status": {"type": "read", "params": {"run_id": ""}},
        "tail_logs": {"type": "read", "params": {"run_id": "", "lines": 200}},
        "show_trace_summary": {"type": "read", "params": {"limit": 3}},
        "read_processing_state": {
            "type": "read",
            "params": {"supplier_domain": "poundwholesale.co.uk"},
        },
        "find_cached_products": {
            "type": "read",
            "params": {
                "supplier_domain": "poundwholesale.co.uk",
                "ean": None,
                "url": None,
                "title_contains": None,
                "limit": 50,
            },
        },
        "find_linking_entries": {
            "type": "read",
            "params": {
                "supplier_domain": "poundwholesale.co.uk",
                "supplier_ean": None,
                "amazon_asin": None,
                "supplier_url": None,
                "limit": 50,
            },
        },
        "read_amazon_cache_by_asin": {"type": "read", "params": {"asin": "ASIN"}},
        "run_readiness_check": {
            "type": "read",
            "params": {"supplier_domain": "poundwholesale.co.uk"},
        },
        "onboarding_sanity_check": {
            "type": "read",
            "params": {"supplier_domain": "poundwholesale.co.uk", "run_start_time": 0},
        },
        "enqueue_run": {
            "type": "write",
            "params": {
                "workflow_key": "<workflow_key>",
                "supplier_domain": "poundwholesale.co.uk",
                "runner_script": "<runner-script>",
                "category_urls": ["<category-url>"],
                "max_products": 50,
                "max_products_per_category": 50,
                "notes": "user request",
            },
        },
        "cancel_run": {
            "type": "write",
            "params": {
                "run_id": "",
            },
        },
        "read_repo_file": {
            "type": "read",
            "params": {"path": "RELATIVE_PATH_IN_REPO", "max_bytes": 200000},
        },
        "list_repo_dir": {"type": "read", "params": {"path": "RELATIVE_DIR_IN_REPO"}},
        "enqueue_onboarding": {
            "type": "write",
            "params": {
                "run_id": "",
                "input_path": "ABSOLUTE_PATH_TO_ONBOARDING_INPUT_JSON",
                "output_path": "ABSOLUTE_PATH_TO_ONBOARDING_OUTPUT_JSON",
                "timeout_seconds": 4200,
            },
        },
        "enqueue_product_list_refresh": {
            "type": "write",
            "params": {
                "supplier_domain": "poundwholesale.co.uk",
                "products_path": "OUTPUTS/PRODUCTS_LISTS/products_subset.json",
                "run_id": "",
                "notes": "user request",
                "dry_run": False,
            },
        },
    }

    return (
        system_instructions
        + "\n\nReturn JSON format:\n"
        + json.dumps(
            {"tool": "TOOL_NAME", "params": {}, "explanation": "short user-facing prose"},
            indent=2,
        )
        + "\n\nAllowed tools and schemas:\n"
        + json.dumps(tools_desc, indent=2)
        + "\n\nSystem index (may be null):\n"
        + json.dumps(system_index or {}, indent=2)
        + "\n\nRAG metadata (may be null):\n"
        + json.dumps(rag_meta or {}, indent=2)
        + "\n\nRAG context (may be empty):\n"
        + (rag_context or "")
        + "\n\nUser: "
        + user_text
    )


def _parse_runtime_constraints(user_text: str) -> dict[str, int | None]:
    """Extract max_products and max_products_per_category from user text."""
    constraints: dict[str, int | None] = {"max_products": None, "max_products_per_category": None}

    mpc_match = re.search(
        r"(?:max[_ ]?products[_ ]?per[_ ]?category|products?\s+per\s+category)\s*(?:from\s+\d+\s+)?(?:should\s+be|set\s+to|to|=|:)?\s*(\d+)",
        user_text,
        re.IGNORECASE,
    )
    if mpc_match:
        constraints["max_products_per_category"] = int(mpc_match.group(1))

    mp_match = re.search(
        r"max[_ ]?products(?![_ ]?per[_ ]?category)\s*(?:from\s+\d+\s+)?(?:should\s+be|set\s+to|to|=|:)?\s*(\d+)",
        user_text,
        re.IGNORECASE,
    )
    if mp_match:
        constraints["max_products"] = int(mp_match.group(1))

    if constraints["max_products"] is None:
        natural_match = re.search(
            r"(?:first|only|just|limit(?:ed)?\s+to|top|up\s*to|at\s*most|no\s+more\s+than)\s+(\d+)\s+products?",
            user_text,
            re.IGNORECASE,
        )
        if natural_match:
            constraints["max_products"] = int(natural_match.group(1))

    if constraints["max_products"] is None:
        analyze_match = re.search(
            r"(?:analy[sz]e|process|run|check)\s+(?:only\s+)?(?:the\s+)?(?:first\s+)?(\d+)\s+products?",
            user_text,
            re.IGNORECASE,
        )
        if analyze_match:
            constraints["max_products"] = int(analyze_match.group(1))

    if constraints["max_products"] is None:
        reversed_match = re.search(
            r"\b(\d+)\s+products?\s+(?:max(?:imum)?|limit(?:ed)?)\b",
            user_text,
            re.IGNORECASE,
        )
        if reversed_match:
            constraints["max_products"] = int(reversed_match.group(1))

    if constraints["max_products"] is None:
        unlimited_match = re.search(
            r"\b(?:unlimited|no\s+limit|all\s+products?)\b",
            user_text,
            re.IGNORECASE,
        )
        if unlimited_match:
            constraints["max_products"] = 0

    return constraints


def plan_tool_call(user_text: str, repo_root: Path) -> tuple[ToolCall, dict[str, Any]]:
    system_index = _load_system_index(repo_root)
    category_urls = _extract_category_urls(user_text, system_index)

    if category_urls:
        supplier_domain = _infer_supplier_domain_from_url(category_urls[0])
        constraints = _parse_runtime_constraints(user_text)

        try:
            workflow_key, runner_script = _resolve_workflow_params(repo_root, supplier_domain)

            tool_call = ToolCall(
                name="enqueue_run",
                params={
                    "supplier_domain": supplier_domain,
                    "category_urls": category_urls,
                    "workflow_key": workflow_key,
                    "runner_script": runner_script,
                    "max_products": constraints["max_products"],
                    "max_products_per_category": constraints["max_products_per_category"],
                    "notes": "User requested category analysis via chat",
                },
                explanation=f"Starting analysis for {len(category_urls)} categories on {supplier_domain}. Using runner '{runner_script}' with workflow '{workflow_key}'.",
                expected_outputs=[
                    f"OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json",
                    f"OUTPUTS/CONTROL_PLANE/status/<run_id>.json",
                    f"OUTPUTS/CONTROL_PLANE/logs/<run_id>.log",
                    f"OUTPUTS/CACHE/processing_states/{supplier_domain.replace('.', '_')}__sandbox_<id>_processing_state.json",
                    f"OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_domain}__sandbox_<id>/linking_map.json",
                    f"OUTPUTS/FBA_ANALYSIS/financial_reports/{supplier_domain.replace('.', '-')}__sandbox_<id>/fba_financial_report_*.csv",
                ],
            )
            return tool_call, {
                "meta": {},
                "sources_used": [],
                "scores": [],
                "context_injected": False,
            }

        except ValueError as e:
            # Resolution failed - return ask_clarify with error context
            tool_call = ToolCall(
                name="ask_clarify",
                params={
                    "user_text": user_text,
                    "error_context": str(e),
                },
                explanation=f"I found {len(category_urls)} category URL(s), but I can't start the run: {str(e)}. Please verify the supplier is properly configured.",
            )
            return tool_call, {
                "meta": {},
                "sources_used": [],
                "scores": [],
                "context_injected": False,
            }

    provider = get_provider()

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

    prompt = build_prompt(user_text, system_index, rag_context, rag_meta, repo_root)

    explanation: str | None = None

    for attempt in range(3):
        try:
            data = provider.generate_json(prompt)
        except Exception as e:
            if attempt < 2:
                prompt = (
                    prompt
                    + f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). "
                    + "Return ONLY a single valid JSON object with keys: tool, params, explanation."
                )
                continue
            data = {
                "tool": "ask_clarify",
                "params": {"user_text": user_text, "error_context": str(e)},
            }

        tool = str(data.get("tool") or "").strip()
        params = data.get("params") or {}
        if not isinstance(params, dict):
            params = {}

        explanation_raw = data.get("explanation")
        if isinstance(explanation_raw, str) and explanation_raw.strip():
            explanation = explanation_raw.strip()

        expected_outputs = data.get("expected_outputs")
        if not isinstance(expected_outputs, list):
            expected_outputs = []

        allowed = set(READ_TOOLS) | set(WRITE_TOOLS)
        if tool not in allowed:
            if attempt < 2:
                prompt = (
                    prompt
                    + "\n\nYour last response used an invalid tool name. Choose ONLY from the allowed tools."
                )
                continue
            tool = "ask_clarify"
            params = {"user_text": user_text}
            explanation = explanation or "I need a bit more information to help with that."
            expected_outputs = []
            break

        if tool == "enqueue_run":
            urls = params.get("category_urls")
            if not isinstance(urls, list) or not [
                u for u in urls if isinstance(u, str) and u.strip()
            ]:
                tool = "ask_clarify"
                params = {"user_text": user_text, "missing_params": ["category_urls"]}
                explanation = explanation or "To proceed, I need one or more category URLs to run."
                expected_outputs = []
            else:
                constraints = _parse_runtime_constraints(user_text)
                if constraints.get("max_products") is not None:
                    params["max_products"] = constraints["max_products"]
                if constraints.get("max_products_per_category") is not None:
                    params["max_products_per_category"] = constraints["max_products_per_category"]
                if (
                    constraints.get("max_products") is not None
                    and constraints.get("max_products_per_category") is None
                ):
                    params["max_products_per_category"] = constraints["max_products"]

        break

    rag_info = {
        "meta": rag_meta,
        "sources_used": rag_sources,
        "scores": rag_scores,
        "context_injected": bool(rag_context),
    }

    return (
        ToolCall(
            name=tool,
            params=params,
            explanation=explanation,
            expected_outputs=expected_outputs,
        ),
        rag_info,
    )


def is_write_tool(tool: str) -> bool:
    return tool in WRITE_TOOLS


def execute_tool_call(tool_call: ToolCall, repo_root: Path) -> dict[str, Any]:
    name = tool_call.name
    p = tool_call.params

    def _normalize_run_id(raw: object) -> str:
        run_id = str(raw or "").strip()
        if run_id.lower() in {"<run-id>", "<run_id>", "run_id", "run-id"}:
            return ""
        if any(ch in run_id for ch in '<>:"/\\|?*'):
            return ""
        return run_id

    def _resolve_contextual_run_id(repo_root: Path, raw: object) -> str:
        normalized = _normalize_run_id(raw)
        if normalized:
            return normalized
        paths = get_paths()
        running_dir = paths.jobs_running
        if running_dir.exists():
            candidates = sorted(
                [
                    f
                    for f in running_dir.iterdir()
                    if f.name.startswith("job_") and f.suffix == ".json"
                ],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                return candidates[0].stem.replace("job_", "", 1)
        pending_dir = paths.jobs_pending
        if pending_dir.exists():
            candidates = sorted(
                [
                    f
                    for f in pending_dir.iterdir()
                    if f.name.startswith("job_") and f.suffix == ".json"
                ],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                return candidates[0].stem.replace("job_", "", 1)
        status_dir = paths.status_dir
        if status_dir.exists():
            candidates = sorted(
                [
                    f
                    for f in status_dir.iterdir()
                    if f.suffix == ".json" and not f.stem.endswith(".cancelled")
                ],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                return candidates[0].stem
        return ""

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
        return ask_clarify(
            user_text=str(p.get("user_text") or "").strip() or None,
            missing_params=p.get("missing_params"),
            error_context=str(p.get("error_context") or "").strip() or None,
        )

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
        run_id = _resolve_contextual_run_id(repo_root, p.get("run_id"))
        if not run_id:
            return {
                "ok": False,
                "error": "run_id could not be resolved. No active, pending, or recent job found.",
            }
        return {"ok": True, "status": read_status(run_id)}

    if name == "tail_logs":
        run_id = _resolve_contextual_run_id(repo_root, p.get("run_id"))
        if not run_id:
            return {
                "ok": False,
                "error": "run_id could not be resolved. No active, pending, or recent job found.",
            }
        lines = int(p.get("lines") or 200)
        paths = get_paths()
        log_path = paths.logs_dir / f"{run_id}.log"
        return {"ok": True, "lines": tail_file(log_path, lines=lines), "log_path": str(log_path)}

    if name == "show_trace_summary":
        limit = int(p.get("limit") or 5)
        return read_trace_summary(repo_root, limit=limit)

    if name == "read_processing_state":
        supplier_domain = str(p.get("supplier_domain") or "")
        if not supplier_domain:
            try:
                import streamlit as st

                supplier_domain = str(st.session_state.get("supplier") or "")
            except Exception:
                supplier_domain = ""
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
        workflow_key = str(p.get("workflow_key") or "")

        from config.system_config_loader import SystemConfigLoader

        config_loader = SystemConfigLoader()
        full_config = config_loader.get_full_config()
        valid_keys = list(full_config.get("workflows", {}).keys())

        if workflow_key not in valid_keys:
            supplier_domain = str(p.get("supplier_domain") or "")
            for key in valid_keys:
                domain_clean = supplier_domain.replace(".", "_").replace("-", "_")
                if domain_clean in key.lower():
                    p["workflow_key"] = key
                    workflow_key = key
                    break
            else:
                return {
                    "ok": False,
                    "error": f"Invalid workflow_key: {workflow_key}. Valid: {valid_keys}",
                }

        try:
            base_cfg = read_json(repo_root / "config" / "system_config.json")
        except Exception as e:
            return {
                "ok": False,
                "error": f"Failed to parse config/system_config.json: {e}",
            }

        system_defaults = base_cfg.get("system") or {}

        raw_max_products = p.get("max_products")
        raw_max_products_per_category = p.get("max_products_per_category")

        def _coerce_or_default(raw: object, default_val: int) -> int:
            if raw is None:
                return default_val
            if isinstance(raw, str) and not raw.strip():
                return default_val
            return int(raw)

        per_cat_default = int(system_defaults.get("max_products_per_category") or 0)
        try:
            if (
                raw_max_products_per_category is None
                and raw_max_products is not None
                and int(raw_max_products) > 0
            ):
                per_cat_default = int(raw_max_products)
        except Exception:
            pass

        req = RunRequest(
            supplier_domain=str(p.get("supplier_domain") or ""),
            workflow_key=workflow_key,
            runner_script=str(p.get("runner_script") or ""),
            category_urls=list(p.get("category_urls") or []),
            max_products=_coerce_or_default(
                raw_max_products,
                int(system_defaults.get("max_products") or 0),
            ),
            max_products_per_category=_coerce_or_default(
                raw_max_products_per_category,
                per_cat_default,
            ),
            notes=p.get("notes"),
        )
        run_id = str(p.get("run_id") or "").strip()
        if not run_id:
            import uuid

            run_id = str(uuid.uuid4())

        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
        if not sandbox_suffix:
            sandbox_suffix = f"sandbox__{run_id[:8]}"

        # Build sandbox_supplier for output paths/polling, but keep supplier_name canonical for credential lookup
        sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}"

        categories_path = write_categories_subset(run_id, sandbox_supplier, req.category_urls)

        overrides: dict[str, Any] = {
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

        base_creds = (base_cfg.get("credentials") or {}).get(req.supplier_domain)
        if isinstance(base_creds, dict) and base_creds:
            overrides["credentials"] = {sandbox_supplier: base_creds}

        merged_cfg_path = write_merged_system_config(run_id, base_cfg, overrides)
        job_path = enqueue_run_job(
            run_id, req, merged_cfg_path, categories_path, sandbox_supplier=sandbox_supplier
        )

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

    if name == "enqueue_product_list_refresh":
        req = ProductListRefreshRequest(
            supplier_domain=str(p.get("supplier_domain") or ""),
            products=None,
            products_path=str(p.get("products_path") or "") or None,
            run_id=str(p.get("run_id") or "") or None,
            notes=str(p.get("notes") or "") or None,
            dry_run=bool(p.get("dry_run")),
        )
        return enqueue_product_list_refresh(repo_root, req)

    if name == "cancel_run":
        run_id = _resolve_contextual_run_id(repo_root, p.get("run_id"))
        if not run_id:
            return {
                "ok": False,
                "error": "run_id could not be resolved. No active, pending, or recent job found.",
            }

        paths = get_paths()

        cancel_path = paths.status_dir / f"{run_id}.cancelled"
        cancel_path.parent.mkdir(parents=True, exist_ok=True)
        cancel_path.write_text("cancelled", encoding="utf-8")

        legacy_path = paths.lock_dir / f"cancel_{run_id}.flag"
        legacy_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_path.write_text("cancelled", encoding="utf-8")

        return {
            "ok": True,
            "run_id": run_id,
            "cancel_marker": str(cancel_path),
            "cancel_marker_legacy": str(legacy_path),
        }

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
