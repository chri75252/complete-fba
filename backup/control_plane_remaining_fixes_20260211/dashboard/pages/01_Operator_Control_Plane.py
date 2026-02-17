from __future__ import annotations

import os
import uuid
from pathlib import Path

import streamlit as st

from control_plane.build_index import build_system_index
from control_plane.json_io import read_json
from control_plane.paths import get_paths
from control_plane.tools.financial import FinancialQuery, query_financial_rows
from control_plane.tools.jobs import (
    RunRequest,
    enqueue_run_job,
    write_categories_subset,
    write_merged_system_config,
)
from control_plane.llm.parser import parse_user_text


def load_system_config() -> dict:
    repo_root = get_paths().repo_root
    return read_json(repo_root / "config" / "system_config.json")


def list_workflows(system_config: dict) -> list[tuple[str, dict]]:
    workflows = system_config.get("workflows", {})
    return sorted(workflows.items(), key=lambda kv: kv[0])


def main() -> None:
    st.set_page_config(page_title="Operator Control Plane", layout="wide")
    st.title("Operator Control Plane (Phase 1)")

    paths = get_paths()
    repo_root = paths.repo_root

    st.caption(f"Repo root: {repo_root}")

    with st.expander("LLM Parser (optional)", expanded=False):
        st.write(
            "Type a request in English. The parser will only fill fields; it will NOT run anything."
        )
        st.write("Set env var CONTROL_PLANE_LLM_PROVIDER to enable: none/openai/anthropic/ollama")
        user_text = st.text_input(
            "Request", placeholder="Run poundwholesale on 3 categories, max 50 products"
        )
        if st.button("Parse"):
            res = parse_user_text(user_text)
            if res.ok:
                st.session_state["parsed"] = res.data
                st.success("Parsed")
            else:
                st.error(res.error or "Parse failed")

    parsed = st.session_state.get("parsed", {})

    system_config = load_system_config()
    workflows = list_workflows(system_config)
    workflow_keys = [k for k, _ in workflows]

    st.subheader("Run Builder")

    left, right = st.columns([1, 1])

    with left:
        workflow_key = st.selectbox("Workflow key", workflow_keys, index=0)
        workflow_cfg = dict(workflows)[workflow_key]
        supplier_domain = workflow_cfg.get("supplier_name")

        supplier_domain = st.text_input(
            "Supplier domain", value=parsed.get("supplier_domain") or supplier_domain or ""
        )

        # categories source
        categories_path = workflow_cfg.get("categories_config_path")
        categories_list = []
        if categories_path and Path(categories_path).exists():
            try:
                categories_list = read_json(Path(categories_path)).get("category_urls", [])
            except Exception:
                categories_list = []

        selected = st.multiselect(
            "Select categories (optional)", options=categories_list, default=[]
        )
        pasted = st.text_area("Or paste category URLs (one per line)")

        max_products = int(parsed.get("max_products") or 50)
        max_per_cat = int(parsed.get("max_products_per_category") or max_products)

        max_products = st.number_input("Max products", min_value=0, value=max_products)
        max_per_cat = st.number_input("Max products per category", min_value=0, value=max_per_cat)

        confirm = st.checkbox("I understand this will write override files and enqueue a run")

        if st.button("Create Job"):
            if not confirm:
                st.error("Confirmation required")
            else:
                run_id = str(uuid.uuid4())

                # resolve category urls
                category_urls = []
                if pasted.strip():
                    category_urls = [ln.strip() for ln in pasted.splitlines() if ln.strip()]
                elif parsed.get("category_urls"):
                    category_urls = list(parsed.get("category_urls"))
                else:
                    category_urls = list(selected)

                if not category_urls:
                    st.error("No categories provided")
                else:
                    subset_path = write_categories_subset(run_id, supplier_domain, category_urls)

                    # merged config overrides: set max products and override workflow categories path
                    overrides = {
                        "system": {
                            "max_products": int(max_products),
                            "max_products_per_category": int(max_per_cat),
                        },
                        "workflows": {
                            workflow_key: {
                                "categories_config_path": str(subset_path),
                            }
                        },
                    }
                    merged_path = write_merged_system_config(run_id, system_config, overrides)

                    request = RunRequest(
                        supplier_domain=supplier_domain,
                        workflow_key=workflow_key,
                        runner_script=workflow_cfg.get("runner_script")
                        or f"run_custom_{supplier_domain.replace('.', '-')}.py",
                        category_urls=category_urls,
                        max_products=int(max_products),
                        max_products_per_category=int(max_per_cat),
                        notes="created from Operator UI",
                    )

                    job_path = enqueue_run_job(run_id, request, merged_path, subset_path)
                    st.success(f"Job enqueued: {job_path}")
                    st.session_state["last_run_id"] = run_id

    with right:
        st.subheader("Run Monitor")
        status_files = (
            sorted(paths.status_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
            if paths.status_dir.exists()
            else []
        )
        options = [p.stem for p in status_files]
        default_run = st.session_state.get("last_run_id")
        if default_run and default_run in options:
            idx = options.index(default_run)
        else:
            idx = max(len(options) - 1, 0) if options else 0

        run_id = st.selectbox("Run ID", options=options, index=idx) if options else None
        if run_id:
            status = read_json(paths.status_dir / f"{run_id}.json")
            st.json(status)

        st.subheader("Financial Query")
        roi_min = st.number_input("ROI min", value=float(parsed.get("roi_min") or 30.0))
        net_min = st.number_input("NetProfit min", value=float(parsed.get("netprofit_min") or 5.0))
        limit = st.number_input("Limit", min_value=1, value=int(parsed.get("limit") or 50))

        if st.button("Query Financials"):
            if not supplier_domain:
                st.error("Supplier domain required")
            else:
                result = query_financial_rows(
                    repo_root,
                    FinancialQuery(
                        supplier_domain=supplier_domain,
                        roi_min=roi_min,
                        netprofit_min=net_min,
                        limit=int(limit),
                    ),
                )
                st.json(result)

    with st.expander("System Index", expanded=False):
        if st.button("Rebuild system index"):
            idx = build_system_index()
            st.success(f"Index built; writing to {paths.system_index_path}")
        if paths.system_index_path.exists():
            st.json(read_json(paths.system_index_path))


if __name__ == "__main__":
    main()
