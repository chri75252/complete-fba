import os
from pathlib import Path

import streamlit as st

from control_plane.env_config import ensure_llm_env
from control_plane.financial_query import FinancialQuery
from control_plane.job_manager import JobManager
from control_plane.llm_parser import parse as llm_parse
from control_plane.status_reader import StatusReader


def _list_workflows() -> list[tuple[str, str]]:
    import json

    cfg = json.load(open("config/system_config.json", "r", encoding="utf-8"))
    workflows = cfg.get("workflows", {})
    out: list[tuple[str, str]] = []
    for key, wf in workflows.items():
        supplier = str(wf.get("supplier_name") or "")
        out.append((key, supplier))
    out.sort(key=lambda t: t[0])
    return out


def _load_categories_for_workflow(workflow_key: str) -> list[str]:
    import json

    cfg = json.load(open("config/system_config.json", "r", encoding="utf-8"))
    wf = (cfg.get("workflows", {}) or {}).get(workflow_key, {})
    path = wf.get("categories_config_path")
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []
    data = json.load(open(p, "r", encoding="utf-8"))
    return list(data.get("category_urls", []) or [])


def render_operator_panel(base_dir: str, supplier_hint: str) -> None:
    ensure_llm_env()
    st.subheader("Operator Control Plane")

    workflows = _list_workflows()
    workflow_labels = [f"{k} ({s})" for k, s in workflows]

    default_idx = 0
    for i, (k, s) in enumerate(workflows):
        if supplier_hint and supplier_hint.lower() in {k.lower(), s.lower()}:
            default_idx = i
            break

    col_a, col_b = st.columns([2, 1])

    with col_a:
        natural = st.text_area(
            "Optional: natural request (fills form only)",
            value="",
            placeholder="Run poundwholesale_workflow on 3 categories, max 50 products",
            height=80,
        )

    parsed = None
    if natural.strip():
        if st.button("Parse"):
            res = llm_parse(natural)
            if res.ok:
                parsed = res.data
                st.session_state["cp_last_parse"] = parsed
            else:
                st.error(res.error or "parse_failed")

    parsed = parsed or st.session_state.get("cp_last_parse")

    with col_b:
        st.write("LLM provider:")
        st.code(os.environ.get("CONTROL_PLANE_LLM_PROVIDER", "none"), language="text")

    selected = st.selectbox("Workflow", options=workflow_labels, index=default_idx)
    workflow_key = workflows[workflow_labels.index(selected)][0]
    supplier_domain = workflows[workflow_labels.index(selected)][1]

    all_categories = _load_categories_for_workflow(workflow_key)

    st.write("Categories")
    selected_cats = st.multiselect("Select categories", options=all_categories, default=[])
    pasted_urls = st.text_area("Or paste category URLs (one per line)", value="", height=120)

    max_products = st.number_input("Max products", min_value=0, value=50, step=10)
    max_products_per_category = st.number_input(
        "Max products per category", min_value=0, value=50, step=10
    )

    if parsed and parsed.get("intent") == "enqueue_run":
        if parsed.get("max_products") is not None:
            max_products = int(parsed["max_products"])
        if parsed.get("max_products_per_category") is not None:
            max_products_per_category = int(parsed["max_products_per_category"])

        urls = parsed.get("category_urls") or []
        if urls:
            pasted_urls = "\n".join(urls)

    confirm = st.checkbox("I confirm: create job + write override files", value=False)

    if st.button("Create Job"):
        if not confirm:
            st.error("Confirmation required")
        else:
            urls = [u.strip() for u in pasted_urls.splitlines() if u.strip()]
            if not urls:
                urls = list(selected_cats)

            runner_script = f"run_custom_{supplier_domain.split('.')[0]}.py"
            jm = JobManager(repo_root=Path(base_dir))
            jp = jm.create_run_workflow_job(
                supplier_domain=supplier_domain,
                workflow_key=workflow_key,
                runner_script=runner_script,
                category_urls=urls,
                max_products=int(max_products),
                max_products_per_category=int(max_products_per_category),
            )
            st.success(f"Created job {jp.run_id}")
            st.code(str(jp.job_path), language="text")

    st.markdown("---")

    st.subheader("Monitor")
    sr = StatusReader(repo_root=Path(base_dir))
    run_ids = sr.list_run_ids()
    run_id = st.selectbox("Run ID", options=[""] + run_ids)
    if run_id:
        status = sr.get_status(run_id)
        st.json(status)
        lines = sr.tail_run_log(run_id, lines=50)
        if lines:
            st.code("\n".join(lines[-50:]), language="text")

    st.markdown("---")

    st.subheader("Query Financial")
    roi_min = st.number_input("ROI min", min_value=0.0, value=30.0, step=1.0)
    netprofit_min = st.number_input("NetProfit min", min_value=0.0, value=5.0, step=0.5)
    ean = st.text_input("EAN (optional)", value="")

    if parsed and parsed.get("intent") == "query_financial":
        if parsed.get("roi_min") is not None:
            roi_min = float(parsed["roi_min"])
        if parsed.get("netprofit_min") is not None:
            netprofit_min = float(parsed["netprofit_min"])
        if parsed.get("ean"):
            ean = str(parsed["ean"])

    if st.button("Run Financial Query"):
        fq = FinancialQuery(base_dir)
        res = fq.query_financial_rows(
            supplier_domain=supplier_domain,
            filters={"roi_min": roi_min, "netprofit_min": netprofit_min, "ean": ean or None},
            limit=50,
        )
        if not res.get("ok"):
            st.error(res.get("reason"))
        else:
            st.write(f"Latest report: `{res.get('latest_report')}`")
            st.write(f"Matched rows: {res.get('matched_rows')}")
            st.dataframe(res.get("rows", []))
