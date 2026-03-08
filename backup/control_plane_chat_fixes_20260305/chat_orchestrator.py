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
    get_run_outputs,
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
    write_output_file,
    validate_run_integrity,
)

from control_plane.tools.tool_param_validation import validate_tool_params


READ_TOOLS = {
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
    "get_run_outputs": "get_run_outputs",
    "validate_run_integrity": "validate_run_integrity",
}


WRITE_TOOLS = {
    "enqueue_run": "enqueue_run",
    "cancel_run": "cancel_run",
    "enqueue_onboarding": "enqueue_onboarding",
    "enqueue_product_list_refresh": "enqueue_product_list_refresh",
    "write_output_file": "write_output_file",
}


TERMINAL_TOOLS = {
    "final_answer": "final_answer",
    "ask_clarify": "ask_clarify",
}


def _sanitize_chat_history(
    history: object,
    *,
    user_text: str | None = None,
    max_messages: int = 50,
    max_content_chars: int = 10000,
    max_total_chars: int = 200000,
) -> list[dict[str, Any]]:
    """Return a small, safe chat history for planner prompt injection.



    Policy:

    - Keep only the last `max_messages` messages.

    - Keep only `role` and a truncated `content` string.

    - Drop large `tool_result` payloads; include only a tiny scalar summary when possible.

    - Enforce `max_total_chars` across all message content.

    """

    if not isinstance(history, list):
        return []

    out: list[dict[str, Any]] = []

    for raw in history[-max_messages:]:
        if not isinstance(raw, dict):
            continue

        role = raw.get("role")

        if not isinstance(role, str) or not role.strip():
            continue

        role = role.strip()

        content = raw.get("content")

        if not isinstance(content, str):
            content = ""

        content = content.strip()

        if len(content) > max_content_chars:
            content = content[:max_content_chars] + "\n...<truncated>"

        msg: dict[str, Any] = {"role": role, "content": content}

        tool_result = raw.get("tool_result")

        if isinstance(tool_result, dict):
            summary: dict[str, Any] = {}

            for key in (
                "ok",
                "error",
                "run_id",
                "sandbox_supplier",
                "message",
                "job_path",
                "log_path",
                "merged_config",
                "categories",
                "report_path",
                "row_count",
                "count",
                "path",
                "hint",
                "questions",
                "missing_params",
            ):
                v = tool_result.get(key)

                if isinstance(v, (bool, int, float, str)):
                    if not isinstance(v, str) or len(v) <= 300:
                        summary[key] = v

                elif key in {"questions", "missing_params"} and isinstance(v, list):
                    items: list[str] = []
                    for item in v[:10]:
                        s = str(item).strip()
                        if s:
                            items.append(s)
                    if items:
                        joined = "; ".join(items)
                        if len(joined) > 300:
                            joined = joined[:300] + "...<truncated>"
                        summary[key] = joined

            if summary:
                msg["tool_result"] = summary

        out.append(msg)

    if user_text and out:
        last = out[-1]

        if (
            str(last.get("role") or "").strip() == "user"
            and str(last.get("content") or "").strip() == user_text.strip()
        ):
            out = out[:-1]

    total = 0

    trimmed: list[dict[str, Any]] = []

    for msg in reversed(out):
        content = str(msg.get("content") or "")

        if total + len(content) > max_total_chars:
            break

        trimmed.append(msg)

        total += len(content)

    return list(reversed(trimmed))


@dataclass(frozen=True)
class ToolCall:
    name: str

    params: dict[str, Any]

    explanation: str | None = None

    expected_outputs: list[str] | None = None


@dataclass(frozen=True)
class AgentStep:
    kind: str  # "tool_call" | "final_answer" | "approval_needed"

    tool_call: ToolCall | None = None

    text: str | None = None

    result: dict[str, Any] | None = None


def _normalize_run_id_for_preview(raw: object) -> str:
    run_id = str(raw or "").strip()

    if not run_id:
        return ""

    if run_id.lower() in {
        "<run-id>",
        "<run_id>",
        "run_id",
        "run-id",
        "{run_id}",
        "{run-id}",
    }:
        return ""

    if any(ch in run_id for ch in '<>:"/\\|?*'):
        return ""

    return run_id


def _ensure_enqueue_preview_run_id(params: dict[str, Any]) -> str:
    run_id = _normalize_run_id_for_preview(params.get("run_id"))

    if run_id:
        params["run_id"] = run_id

        return run_id

    import uuid

    run_id = str(uuid.uuid4())

    params["run_id"] = run_id

    return run_id


def _substitute_expected_output_placeholders(
    expected_outputs: list[object], *, run_id: str, sandbox_id: str
) -> list[str]:
    out: list[str] = []

    seen: set[str] = set()

    run_tokens = [
        "<run_id>",
        "<run-id>",
        "<RUN_ID>",
        "<RUN-ID>",
        "{run_id}",
        "{run-id}",
        "{RUN_ID}",
        "{RUN-ID}",
    ]

    id_tokens = ["<id>", "<ID>", "{id}", "{ID}"]

    for item in expected_outputs:
        if not isinstance(item, str):
            continue

        s = item.strip()

        if not s:
            continue

        for token in run_tokens:
            s = s.replace(token, run_id)

        for token in id_tokens:
            s = s.replace(token, sandbox_id)

        if s and s not in seen:
            out.append(s)

            seen.add(s)

    return out


def _fallback_expected_outputs_for_enqueue_tool(
    tool: str, params: dict[str, Any], *, run_id: str
) -> list[str]:
    sandbox_id = run_id[:8]
    outputs: list[str] = [
        f"OUTPUTS/CONTROL_PLANE/jobs/pending/job_{run_id}.json",
        f"OUTPUTS/CONTROL_PLANE/status/{run_id}.json",
        f"OUTPUTS/CONTROL_PLANE/logs/{run_id}.log",
    ]

    if tool == "enqueue_run":
        domain = str(params.get("supplier_domain") or "").strip()
        sandbox_suffix = str(params.get("sandbox_suffix") or "").strip()
        has_real_suffix = bool(sandbox_suffix and sandbox_suffix != "<optional_for_resuming>")

        if params.get("category_urls") or has_real_suffix:
            outputs.extend(
                [
                    f"OUTPUTS/CONTROL_PLANE/overrides/{run_id}/system_config.merged.json",
                    f"OUTPUTS/CONTROL_PLANE/overrides/{run_id}/categories_subset.json",
                ]
            )
            if not has_real_suffix:
                sandbox_suffix = f"sandbox__{sandbox_id}"
            sandbox_supplier = f"{domain}__{sandbox_suffix}"
            us_domain = sandbox_supplier.replace(".", "_").replace("-", "_")
            h_domain = sandbox_supplier.replace(".", "-")
            outputs.extend(
                [
                    f"OUTPUTS/CACHE/processing_states/{us_domain}_processing_state.json",
                    f"OUTPUTS/FBA_ANALYSIS/linking_maps/{sandbox_supplier}/linking_map.json",
                    f"OUTPUTS/cached_products/{h_domain}_products_cache.json",
                    f"OUTPUTS/FBA_ANALYSIS/financial_reports/{h_domain}/fba_financial_report_*.csv",
                ]
            )

        else:
            us_domain = domain.replace(".", "_").replace("-", "_")

            h_domain = domain.replace(".", "-")

            outputs.extend(
                [
                    f"OUTPUTS/CACHE/processing_states/{us_domain}_processing_state.json",
                    f"OUTPUTS/FBA_ANALYSIS/linking_maps/{domain}/linking_map.json",
                    f"OUTPUTS/cached_products/{h_domain}_products_cache.json",
                    f"OUTPUTS/FBA_ANALYSIS/financial_reports/{h_domain}/fba_financial_report_*.csv",
                ]
            )

    if tool == "enqueue_product_list_refresh":
        domain = str(params.get("supplier_domain") or "").strip()

        h_domain = domain.replace(".", "-")

        outputs.extend(
            [
                f"OUTPUTS/cached_products/{h_domain}_products_cache.json",
                f"OUTPUTS/FBA_ANALYSIS/financial_reports/{h_domain}/fba_financial_report_*.csv",
                f"OUTPUTS/FBA_ANALYSIS/linking_maps/{domain}/linking_map.json",
            ]
        )

    return outputs


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
    planner_hints: dict[str, Any] | None = None,
    repo_root: Path | None = None,
    chat_history: list[dict[str, Any]] | None = None,
    scratchpad: list[dict[str, Any]] | None = None,
) -> str:
    system_instructions = _load_system_instructions(repo_root) if repo_root else ""

    tools_desc = {
        "final_answer": {
            "type": "terminal",
            "params": {
                "text": "Your complete Markdown response to the user summarizing all actions taken."
            },
        },
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
                "sandbox_suffix": "<optional_for_resuming>",
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
            "params": {"path": "RELATIVE_PATH_IN_REPO", "max_bytes": 1000000},
        },
        "list_repo_dir": {"type": "read", "params": {"path": "RELATIVE_DIR_IN_REPO"}},
        "enqueue_onboarding": {
            "type": "write",
            "params": {
                "run_id": "",
                "supplier_domain": "poundwholesale.co.uk",
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
        "write_output_file": {
            "type": "write",
            "params": {
                "rel_path": "OUTPUTS/CONTROL_PLANE/reports/my_report.md",
                "supplier_domain": "poundwholesale.co.uk",
                "content": "# My Report\n\nContent here",
                "overwrite": False,
            },
        },
        "get_run_outputs": {
            "type": "read",
            "params": {"run_id": "uuid-string"},
        },
        "validate_run_integrity": {
            "type": "read",
            "params": {"run_id": "uuid-string"},
        },
    }

    base_prompt = (
        system_instructions
        + "\n\nYou are an autonomous agent. You may call multiple tools in sequence.\n"
        + "Call read tools to gather data. When ready, call final_answer with your response.\n"
        + "For write actions, call the write tool — the user will confirm.\n"
        + "\n\nReturn JSON format:\n"
        + json.dumps(
            {"tool": "TOOL_NAME", "params": {}, "explanation": "short user-facing prose"},
            indent=2,
        )
        + "\n\nAllowed tools and schemas:\n"
        + json.dumps(tools_desc, indent=2)
        + "\n\nConversation history (most recent last; may be empty):\n"
        + json.dumps(chat_history or [], indent=2)
        + "\n\nSystem index (may be null):\n"
        + json.dumps(system_index or {}, indent=2)
        + "\n\nPlanner hints (may be empty):\n"
        + json.dumps(planner_hints or {}, indent=2)
        + "\n\nRAG metadata (may be null):\n"
        + json.dumps(rag_meta or {}, indent=2)
        + "\n\nRAG context (may be empty):\n"
        + (rag_context or "")
        + "\n\nUser: "
        + user_text
    )

    if scratchpad:
        base_prompt += "\n\n--- Agent scratchpad (your prior actions this turn) ---\n"

        for entry in scratchpad:
            if entry.get("role") == "action":
                base_prompt += f"\nAction: {entry['tool']}({json.dumps(entry['params'])})"

            elif entry.get("role") == "observation":

                def _trunc(v: Any) -> Any:
                    s = str(v)

                    return s if len(s) < 2000 else s[:2000] + "...<truncated>"

                safe_res = {k: _trunc(v) for k, v in entry.get("result", {}).items()}

                base_prompt += f"\nObservation: {json.dumps(safe_res)}"

        base_prompt += "\n\n--- Continue. Call another tool or call final_answer. ---"

    return base_prompt


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


def _compute_planner_hints(user_text: str, repo_root: Path) -> dict[str, Any]:
    system_index = _load_system_index(repo_root)

    category_urls = _extract_category_urls(user_text, system_index)

    planner_hints: dict[str, Any] = {}

    if category_urls:
        safe_urls = [str(u).strip() for u in category_urls if isinstance(u, str) and u.strip()][:10]

        if safe_urls:
            planner_hints["detected_category_urls"] = safe_urls

            supplier_domain = _infer_supplier_domain_from_url(safe_urls[0])

            if supplier_domain:
                planner_hints["inferred_supplier_domain"] = supplier_domain

                try:
                    workflow_key, runner_script = _resolve_workflow_params(
                        repo_root, supplier_domain
                    )

                    planner_hints["suggested_workflow_key"] = workflow_key

                    planner_hints["suggested_runner_script"] = runner_script

                except ValueError as e:
                    planner_hints["resolution_error"] = str(e)[:500]

    planner_hints["parsed_constraints"] = _parse_runtime_constraints(user_text)

    try:
        import streamlit as st

        last_run_id = st.session_state.get("last_run_id")

        if isinstance(last_run_id, str) and last_run_id.strip():
            planner_hints["last_run_id"] = last_run_id.strip()

        last_sandbox = st.session_state.get("last_sandbox_supplier")

        if isinstance(last_sandbox, str) and last_sandbox.strip():
            planner_hints["last_sandbox_supplier"] = last_sandbox.strip()

    except Exception:
        pass

    return planner_hints


def _compute_rag_info(user_text: str) -> tuple[dict[str, Any], str]:
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

    rag_info = {
        "meta": rag_meta,
        "sources_used": rag_sources,
        "scores": rag_scores,
        "context_injected": bool(rag_context),
    }

    return rag_info, rag_context


def agent_plan_step(
    user_text: str,
    repo_root: Path,
    scratchpad: list[dict[str, Any]],
    chat_history: list[dict[str, Any]],
    rag_info_tuple: tuple[dict[str, Any], str],
) -> AgentStep:
    """One iteration of the autonomous agent loop."""

    system_index = _load_system_index(repo_root)

    planner_hints = _compute_planner_hints(user_text, repo_root)

    provider = get_provider()

    rag_info, rag_context = rag_info_tuple

    sanitized_history = _sanitize_chat_history(chat_history, user_text=user_text)

    prompt = build_prompt(
        user_text,
        system_index,
        rag_context,
        rag_info["meta"],
        planner_hints,
        repo_root,
        chat_history=sanitized_history,
        scratchpad=scratchpad,
    )

    explanation: str | None = None

    for attempt in range(3):
        try:
            data = provider.generate_json(prompt)

        except Exception as e:
            if attempt < 2:
                prompt += f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). Return ONLY valid JSON."

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

        expected_outputs = data.get("expected_outputs") or []

        allowed = set(READ_TOOLS) | set(WRITE_TOOLS) | set(TERMINAL_TOOLS)

        if tool not in allowed:
            if attempt < 2:
                prompt += f"\n\nInvalid tool '{tool}'. Choose from: {', '.join(allowed)}"

                continue

            tool = "final_answer"

            params = {
                "text": f"I got confused and tried to use an invalid tool: {tool}. See my scratchpad for what I found."
            }

            break

        if tool == "enqueue_run":
            urls = params.get("category_urls")

            if not isinstance(urls, list) or not [
                u for u in urls if isinstance(u, str) and u.strip()
            ]:
                # If it's a sandbox resume, it might not need urls, but let's assume it does unless it has sandbox_suffix

                if not params.get("sandbox_suffix"):
                    tool = "ask_clarify"

                    params = {"user_text": user_text, "missing_params": ["category_urls"]}

                    explanation = (
                        explanation or "To proceed, I need one or more category URLs to run."
                    )

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

    if tool == "final_answer":
        return AgentStep(
            kind="final_answer",
            text=str(params.get("text") or explanation or "Done."),
        )

    if tool == "ask_clarify":
        tc = ToolCall(
            name=tool,
            params=params,
            explanation=explanation,
        )
        result = execute_tool_call(tc, repo_root)
        text = respond_to_tool_result(user_text, tc, result)
        return AgentStep(kind="final_answer", tool_call=tc, text=text, result=result)

    if tool in {"enqueue_run", "enqueue_product_list_refresh"}:
        run_id = _ensure_enqueue_preview_run_id(params)

        sandbox_id = run_id[:8]

        if not expected_outputs:
            expected_outputs = _fallback_expected_outputs_for_enqueue_tool(
                tool, params, run_id=run_id
            )

        expected_outputs = _substitute_expected_output_placeholders(
            expected_outputs, run_id=run_id, sandbox_id=sandbox_id
        )

    tc = ToolCall(
        name=tool,
        params=params,
        explanation=explanation,
        expected_outputs=expected_outputs if tool in WRITE_TOOLS else None,
    )

    if tool in WRITE_TOOLS:
        return AgentStep(kind="approval_needed", tool_call=tc)

    # Read tool: execute immediately

    result = execute_tool_call(tc, repo_root)

    return AgentStep(kind="tool_call", tool_call=tc, result=result)


def plan_tool_call(
    user_text: str,
    repo_root: Path,
    chat_history: object | None = None,
) -> tuple[ToolCall, dict[str, Any]]:
    system_index = _load_system_index(repo_root)

    planner_hints = _compute_planner_hints(user_text, repo_root)

    provider = get_provider()

    rag_info, rag_context = _compute_rag_info(user_text)

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

    sanitized_history = _sanitize_chat_history(chat_history, user_text=user_text)

    prompt = build_prompt(
        user_text,
        system_index,
        rag_context,
        rag_meta,
        planner_hints,
        repo_root,
        chat_history=sanitized_history,
    )

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

    if tool in {"enqueue_run", "enqueue_product_list_refresh"}:
        run_id = _ensure_enqueue_preview_run_id(params)

        sandbox_id = run_id[:8]

        if not expected_outputs:
            expected_outputs = _fallback_expected_outputs_for_enqueue_tool(
                tool, params, run_id=run_id
            )

        expected_outputs = _substitute_expected_output_placeholders(
            expected_outputs,
            run_id=run_id,
            sandbox_id=sandbox_id,
        )

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

    if name in {
        "enqueue_run",
        "enqueue_product_list_refresh",
        "query_financial",
        "enqueue_onboarding",
        "cancel_run",
    }:
        validated = validate_tool_params(name, p)

        if validated.get("ok") is not True:
            return validated

        vp = validated.get("params")

        p = vp if isinstance(vp, dict) else {}

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
        if not sandbox_suffix or sandbox_suffix == "<optional_for_resuming>":
            sandbox_suffix = f"sandbox__{run_id[:8]}"

        # Build sandbox_supplier for output paths/polling, but keep supplier_name canonical for credential lookup
        sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}"

        # Resume safety: If user did not provide category URLs, fallback to previous sandbox run

        category_urls = list(req.category_urls)

        if not category_urls:
            overrides_dir = get_paths().overrides_dir

            if overrides_dir.exists():
                candidates = sorted(
                    [
                        d / "categories_subset.json"
                        for d in overrides_dir.iterdir()
                        if d.is_dir()
                        and (d / "categories_subset.json").exists()
                        and d.name != run_id
                    ],
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )

                for subset_path in candidates:
                    try:
                        data = read_json(subset_path)

                        if data.get("supplier_domain") == sandbox_supplier and data.get(
                            "category_urls"
                        ):
                            category_urls = data.get("category_urls")

                            break

                    except Exception:
                        pass

        # Ensure base categories file is copied so state manager doesn't crash on empty manifest

        base_cat_path = (
            repo_root / "config" / f"{req.supplier_domain.replace('.co.uk', '')}_categories.json"
        )

        sandbox_cat_path = (
            repo_root / "config" / f"{sandbox_supplier.replace('.co.uk', '')}_categories.json"
        )

        if base_cat_path.exists() and not sandbox_cat_path.exists():
            import shutil

            shutil.copy2(base_cat_path, sandbox_cat_path)

        elif not base_cat_path.exists() and not sandbox_cat_path.exists():
            return {
                "ok": False,
                "error": f"Base category config not found: {base_cat_path}",
            }

        categories_path = write_categories_subset(run_id, sandbox_supplier, category_urls)

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

        supplier_domain = str(p.get("supplier_domain") or "")

        req = OnboardingWizardRequest(
            input_path=str(p.get("input_path") or ""),
            output_path=str(p.get("output_path") or ""),
            timeout_seconds=int(p.get("timeout_seconds") or 4200),
        )

        return enqueue_onboarding_job(repo_root, run_id, req, supplier_domain=supplier_domain)

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

    if name == "write_output_file":
        rel_path = str(p.get("rel_path") or "")

        content = str(p.get("content") or "")

        overwrite = bool(p.get("overwrite"))

        supplier_domain = str(p.get("supplier_domain") or "")

        return write_output_file(
            repo_root=repo_root,
            rel_path=rel_path,
            content=content,
            overwrite=overwrite,
            supplier_domain=supplier_domain,
        )

    if name == "get_run_outputs":
        run_id = str(p.get("run_id") or "")

        return get_run_outputs(repo_root=repo_root, run_id=run_id)

    if name == "validate_run_integrity":
        run_id = str(p.get("run_id") or "")

        return validate_run_integrity(run_id=run_id)

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


def _truncate_for_prompt(
    value: object,
    *,
    max_str: int = 3000,
    max_list: int = 30,
    max_dict_items: int = 50,
    depth: int = 3,
) -> object:
    if depth <= 0:
        return "<truncated>"

    if value is None:
        return None

    if isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, str):
        if len(value) <= max_str:
            return value

        return value[:max_str] + "\n...<truncated>"

    if isinstance(value, list):
        items = [
            _truncate_for_prompt(
                v,
                max_str=max_str,
                max_list=max_list,
                max_dict_items=max_dict_items,
                depth=depth - 1,
            )
            for v in value[:max_list]
        ]

        if len(value) > max_list:
            items.append(f"... ({len(value) - max_list} more)")

        return items

    if isinstance(value, dict):
        out: dict[str, object] = {}

        count = 0

        for k, v in value.items():
            if count >= max_dict_items:
                out["..."] = f"({len(value) - max_dict_items} more keys)"

                break

            out[str(k)] = _truncate_for_prompt(
                v,
                max_str=max_str,
                max_list=max_list,
                max_dict_items=max_dict_items,
                depth=depth - 1,
            )

            count += 1

        return out

    text = repr(value)

    if len(text) <= max_str:
        return text

    return text[:max_str] + "\n...<truncated>"


def _extract_references_for_validation(text: str) -> dict[str, set[str]]:
    uuids = set(
        re.findall(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    win_paths = set(re.findall(r"\b[A-Za-z]:\\[^\s`\"]+", text))

    repo_paths = set(
        re.findall(r"\b(?:OUTPUTS|logs|config|control_plane|dashboard)/[^\s`\"]+", text)
    )

    return {"uuids": uuids, "paths": win_paths | repo_paths}


def _fallback_responder(tool_call: ToolCall, result: dict[str, Any]) -> str:
    tool = str(tool_call.name or "").strip() or "<unknown>"

    ok = result.get("ok")

    run_id = result.get("run_id") if isinstance(result.get("run_id"), str) else ""

    sandbox_supplier = (
        result.get("sandbox_supplier") if isinstance(result.get("sandbox_supplier"), str) else ""
    )

    if tool == "validate_run_integrity" and ok is True:
        mode = result.get("mode", "unknown")

        status = result.get("status", "unknown")

        lines = [f"Validation Status: **{status.upper()}**", f"Mode: `{mode}`"]

        if mode == "onboarding_validation":
            checks = result.get("checks_passed", {})

            for k, v in checks.items():
                lines.append(f"- {k}: {'✅' if v else '❌'}")

        else:
            entries = result.get("entries_generated", {})

            for k, v in entries.items():
                lines.append(f"- {k} generated: `{v}`")

        errors = result.get("errors_found", [])

        if errors:
            lines.append("\n**Errors Detected:**")

            for e in errors:
                lines.append(f"- `{e}`")

        return "\n".join(lines)

    if tool == "run_readiness_check":
        missing = result.get("missing_requirements")

        expected = result.get("expected_outputs")

        miss_n = len(missing) if isinstance(missing, list) else 0

        exp_n = len(expected) if isinstance(expected, list) else 0

        lines = [f"Readiness check: ok=`{bool(result.get('ok'))}`."]

        lines.append(f"Missing requirements: `{miss_n}`")

        if miss_n and isinstance(missing, list):
            preview: list[str] = []

            for m in missing[:3]:
                if not isinstance(m, dict):
                    continue

                req = str(m.get("requirement") or "").strip()

                fix = str(m.get("fix") or "").strip()

                if req and fix:
                    preview.append(f"- {req}: `{fix}`")

                elif req:
                    preview.append(f"- {req}")

            if preview:
                lines.append("\nTop fixes:\n" + "\n".join(preview))

        lines.append(f"Expected outputs listed: `{exp_n}`")

        lines.append("\nSee the Tool output expander for full details.")

        return "\n".join(lines)

    if ok is False:
        err = ""

        if isinstance(result.get("error"), str) and result.get("error"):
            err = result.get("error")

        elif isinstance(result.get("message"), str) and result.get("message"):
            err = result.get("message")

        else:
            err = "unknown_error"

        lines = [f"Tool `{tool}` failed.", "", f"Error: `{err}`"]

        if run_id:
            lines.append(f"Run ID: `{run_id}`")

        return "\n".join(lines)

    if tool == "ask_clarify":
        questions = result.get("questions")

        hint = result.get("hint")

        if isinstance(questions, list) and questions:
            text = "I need a bit more information:\n\n" + "\n".join(
                [f"- {str(q)}" for q in questions if str(q).strip()]
            )

        else:
            text = "I need a bit more information to help with that."

        if isinstance(hint, str) and hint.strip():
            text += "\n\n" + hint.strip()

        return text

    if tool == "enqueue_run" and ok is True:
        job_path = result.get("job_path") if isinstance(result.get("job_path"), str) else ""

        merged_cfg = (
            result.get("merged_config") if isinstance(result.get("merged_config"), str) else ""
        )

        cats_path = result.get("categories") if isinstance(result.get("categories"), str) else ""

        lines = ["Job queued successfully."]

        if run_id:
            lines.append(f"\nRun ID: `{run_id}`")

        if sandbox_supplier:
            lines.append(f"Supplier: `{sandbox_supplier}`")

        if job_path:
            lines.append(f"Job file: `{job_path}`")

        if merged_cfg:
            lines.append(f"Merged config: `{merged_cfg}`")

        if cats_path:
            lines.append(f"Categories subset: `{cats_path}`")

        if run_id:
            lines.append("\nStart the worker to execute:\n```\npython -m control_plane worker\n```")

            lines.append(
                "Monitor progress:\n"
                + f"- Status: `OUTPUTS/CONTROL_PLANE/status/{run_id}.json`\n"
                + f"- Log: `OUTPUTS/CONTROL_PLANE/logs/{run_id}.log`"
            )

        return "\n".join(lines)

    if tool == "enqueue_product_list_refresh" and ok is True:
        rid = run_id or "unknown"

        ss = sandbox_supplier or "unknown"

        return (
            "✅ Job queued successfully!\n\n"
            + f"**Run ID:** `{rid}`\n"
            + f"**Supplier:** `{ss}`\n\n"
            + "⚠️ **ACTION REQUIRED:** Start the worker to execute:\n"
            + "```\npython -m control_plane worker\n```\n\n"
            + "**Monitor progress:**\n"
            + f"- Status: `OUTPUTS/CONTROL_PLANE/status/{rid}.json`\n"
            + f"- Log: `OUTPUTS/CONTROL_PLANE/logs/{rid}.log`\n"
            + "- Pending jobs: Check `OUTPUTS/CONTROL_PLANE/jobs/pending/`\n\n"
            + "The worker will pick up the job and move it to running, then done/failed."
        )

    if tool == "cancel_run" and ok is True:
        cancel_marker = (
            result.get("cancel_marker") if isinstance(result.get("cancel_marker"), str) else ""
        )

        lines = ["Cancellation marker written."]

        if run_id:
            lines.append(f"Run ID: `{run_id}`")

        if cancel_marker:
            lines.append(f"Cancel marker: `{cancel_marker}`")

        return "\n".join(lines)

    if tool == "show_status" and ok is True:
        status = result.get("status")

        if isinstance(status, dict):
            st_status = status.get("status")

            st_progress = status.get("progress")

            st_msg = status.get("message")

            rid = status.get("run_id") if isinstance(status.get("run_id"), str) else run_id

            lines = ["Status loaded."]

            if isinstance(rid, str) and rid:
                lines.append(f"Run ID: `{rid}`")

            if isinstance(st_status, str) and st_status.strip():
                lines.append(f"State: `{st_status.strip()}`")

            if isinstance(st_progress, (int, float)):
                lines.append(f"Progress: `{st_progress}`")

            if isinstance(st_msg, str) and st_msg.strip():
                lines.append(f"Message: {st_msg.strip()}")

            lines.append("\nSee the Tool output expander for full status JSON.")

            return "\n".join(lines)

        return "Status loaded. See the Tool output expander for details."

    if tool == "tail_logs" and ok is True:
        log_path = result.get("log_path") if isinstance(result.get("log_path"), str) else ""

        raw_lines = result.get("lines")

        n = len(raw_lines) if isinstance(raw_lines, list) else 0

        lines = ["Fetched recent log lines."]

        if log_path:
            lines.append(f"Log: `{log_path}`")

        if n:
            lines.append(f"Lines returned: `{n}`")

        lines.append("\nSee the Tool output expander for the log content.")

        return "\n".join(lines)

    if tool == "query_financial" and ok is True:
        report_path = (
            result.get("report_path") if isinstance(result.get("report_path"), str) else ""
        )

        row_count = result.get("row_count")

        n = int(row_count) if isinstance(row_count, (int, float)) else 0

        lines = ["Financial report query completed."]

        if report_path:
            lines.append(f"Report: `{report_path}`")

        lines.append(f"Rows returned: `{n}`")

        lines.append("\nSee the Tool output expander for the row data.")

        return "\n".join(lines)

    if tool == "find_cached_products" and ok is True:
        path = result.get("path") if isinstance(result.get("path"), str) else ""

        count = result.get("count")

        n = int(count) if isinstance(count, (int, float)) else 0

        lines = ["Cached products lookup completed."]

        if path:
            lines.append(f"Cache file: `{path}`")

        lines.append(f"Matches: `{n}`")

        lines.append("\nSee the Tool output expander for the matched rows.")

        return "\n".join(lines)

    if tool == "find_linking_entries" and ok is True:
        path = result.get("path") if isinstance(result.get("path"), str) else ""

        count = result.get("count")

        n = int(count) if isinstance(count, (int, float)) else 0

        lines = ["Linking map lookup completed."]

        if path:
            lines.append(f"Linking map: `{path}`")

        lines.append(f"Matches: `{n}`")

        lines.append("\nSee the Tool output expander for the matched entries.")

        return "\n".join(lines)

    if tool == "read_repo_file" and ok is True:
        path = result.get("path") if isinstance(result.get("path"), str) else ""

        content = result.get("content")

        size = len(content) if isinstance(content, str) else 0

        lines = ["File read completed."]

        if path:
            lines.append(f"Path: `{path}`")

        if size:
            lines.append(f"Chars returned: `{size}`")

        lines.append("\nSee the Tool output expander for the file contents.")

        return "\n".join(lines)

    if tool == "list_repo_dir" and ok is True:
        path = result.get("path") if isinstance(result.get("path"), str) else ""

        items = result.get("items")

        n = len(items) if isinstance(items, list) else 0

        lines = ["Directory listing completed."]

        if path:
            lines.append(f"Path: `{path}`")

        lines.append(f"Items: `{n}`")

        lines.append("\nSee the Tool output expander for the full listing.")

        return "\n".join(lines)

    if tool == "read_processing_state" and ok is True:
        state = result.get("state")

        if not isinstance(state, dict) or not state:
            return "No processing state found for that supplier (state file missing or empty)."

        try:
            from control_plane.tools.state import summarize_processing_state

            summary = summarize_processing_state(state)

        except Exception:
            summary = {}

        if isinstance(summary, dict) and summary:
            phase = summary.get("current_phase")

            pci = summary.get("persistent_category_index")

            tot = summary.get("total_categories")

            lines = ["Processing state loaded."]

            if phase:
                lines.append(f"Phase: `{phase}`")

            if isinstance(pci, int) and isinstance(tot, int) and tot > 0:
                lines.append(f"Category index: `{pci}` / `{tot}`")

            lines.append("\nSee the Tool output expander for the full state JSON.")

            return "\n".join(lines)

        return "Processing state loaded. See the Tool output expander for details."

    if tool == "read_amazon_cache_by_asin" and ok is True:
        res = result.get("result")

        if res is None:
            return "No Amazon cache entry found for that ASIN (no matching cache file)."

        if not isinstance(res, dict):
            return "Amazon cache result has unexpected shape. See the Tool output expander for details."

        path = res.get("path") if isinstance(res.get("path"), str) else ""

        data = res.get("data")

        keys = list(data.keys()) if isinstance(data, dict) else []

        lines = ["Amazon cache entry loaded."]

        if path:
            lines.append(f"Cache file: `{path}`")

        if keys:
            show = ", ".join([str(k) for k in keys[:12]])

            if len(keys) > 12:
                show += ", ..."

            lines.append(f"Top-level keys: {show}")

        lines.append("\nSee the Tool output expander for the full cached JSON.")

        return "\n".join(lines)

    if tool == "onboarding_sanity_check" and ok is True:
        overall = result.get("overall")

        state_file = result.get("state_file") if isinstance(result.get("state_file"), str) else ""

        checks = result.get("checks")

        checks_n = len(checks) if isinstance(checks, dict) else 0

        lines = [f"Onboarding sanity check: overall=`{bool(overall)}`."]

        if state_file:
            lines.append(f"State file: `{state_file}`")

        lines.append(f"Checks evaluated: `{checks_n}`")

        lines.append("\nSee the Tool output expander for the detailed checklist results.")

        return "\n".join(lines)

    if tool == "enqueue_onboarding" and ok is True:
        job_path = result.get("job_path") if isinstance(result.get("job_path"), str) else ""

        lines = ["Onboarding job queued."]

        if run_id:
            lines.append(f"Run ID: `{run_id}`")

        if job_path:
            lines.append(f"Job file: `{job_path}`")

        if run_id:
            lines.append("\nStart the worker to execute:\n```\npython -m control_plane worker\n```")

        return "\n".join(lines)

    if tool == "show_trace_summary" and ok is True:
        count = result.get("count")

        traces = result.get("traces")

        n = (
            int(count)
            if isinstance(count, (int, float))
            else (len(traces) if isinstance(traces, list) else 0)
        )

        return f"Loaded `{n}` recent trace(s).\n\nSee the Tool output expander for the full trace summary."

    if tool == "write_output_file" and ok is True:
        path = result.get("path") if isinstance(result.get("path"), str) else ""

        rel_path = result.get("rel_path") if isinstance(result.get("rel_path"), str) else ""

        size = result.get("size")

        n = int(size) if isinstance(size, (int, float)) else 0

        lines = ["File written successfully."]

        if path:
            lines.append(f"Path: `{path}`")

        if rel_path:
            lines.append(f"Relative path: `{rel_path}`")

        lines.append(f"Size: `{n}` bytes")

        lines.append("\nSee the Tool output expander for confirmation.")

        return "\n".join(lines)

    if tool == "get_run_outputs" and ok is True:
        rid = result.get("run_id") if isinstance(result.get("run_id"), str) else ""

        sid = result.get("sandbox_id") if isinstance(result.get("sandbox_id"), str) else ""

        supplier = result.get("supplier") if isinstance(result.get("supplier"), str) else ""

        file_count = result.get("file_count")

        n = int(file_count) if isinstance(file_count, (int, float)) else 0

        files = result.get("files") if isinstance(result.get("files"), list) else []

        lines = ["Run outputs retrieved."]

        if rid:
            lines.append(f"Run ID: `{rid}`")

        if sid:
            lines.append(f"Sandbox ID: `{sid}`")

        if supplier:
            lines.append(f"Supplier: `{supplier}`")

        lines.append(f"Files found: `{n}`")

        if files:
            labels = [f.get("label") for f in files[:5] if isinstance(f, dict)]

            if labels:
                lines.append(f"Sample files: {', '.join(labels)}")

        lines.append("\nSee the Tool output expander for the full file list.")

        return "\n".join(lines)

    msg = result.get("message") if isinstance(result.get("message"), str) else ""

    if msg.strip():
        return msg.strip()

    return f"Executed `{tool}`. Result ok=`{bool(ok)}`. See Tool output for details."


def respond_to_tool_result(
    user_text: str | None,
    tool_call: ToolCall,
    result: dict[str, Any],
) -> str:
    base = _fallback_responder(tool_call, result)

    try:
        provider = get_provider()

    except Exception:
        return base

    gen = getattr(provider, "generate_text", None)

    if not callable(gen):
        return base

    tool = str(tool_call.name or "").strip()

    compact = {
        "tool": tool,
        "user_text": (user_text or "").strip()[:800],
        "tool_result": _truncate_for_prompt(
            result, max_str=1000, max_list=10, max_dict_items=30, depth=2
        ),
        "base_response": base,
    }

    prompt = (
        "Rewrite the BASE_RESPONSE into a clear, natural assistant message.\n"
        "Rules:\n"
        "- Do NOT add new facts, numbers, run ids, or paths not already present in BASE_RESPONSE.\n"
        "- Keep any backticked literals (like `run_id` or file paths) exactly unchanged.\n"
        "- Keep it concise (max 12 lines).\n"
        "- Use Markdown.\n\n" + json.dumps(compact, indent=2)
    )

    try:
        rewritten = str(gen(prompt) or "").strip()

    except Exception:
        return base

    if not rewritten:
        return base

    base_refs = _extract_references_for_validation(base)

    new_refs = _extract_references_for_validation(rewritten)

    if not new_refs["uuids"].issubset(base_refs["uuids"]):
        return base

    if not new_refs["paths"].issubset(base_refs["paths"]):
        return base

    base_ticks = set(re.findall(r"`([^`]+)`", base))

    if base_ticks:
        rewritten_ticks = set(re.findall(r"`([^`]+)`", rewritten))

        if not base_ticks.issubset(rewritten_ticks):
            return base

    return rewritten
