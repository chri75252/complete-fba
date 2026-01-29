from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

from control_plane.json_io import read_json
from control_plane.normalize import supplier_domain_to_underscore
from control_plane.tools.logs import tail_file


def check_cdp_running(host: str = "127.0.0.1", port: int = 9222, timeout: float = 1.0) -> bool:
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def onboarding_sanity_check(
    repo_root: Path, supplier_domain: str, run_start_time: float
) -> dict[str, Any]:
    checks: dict[str, bool] = {}

    state_file = (
        repo_root
        / "OUTPUTS"
        / "CACHE"
        / "processing_states"
        / f"{supplier_domain_to_underscore(supplier_domain)}_processing_state.json"
    )

    if state_file.exists():
        try:
            state = read_json(state_file)
            sp = state.get("system_progression", {})
            completed = sp.get("supplier_products_completed")
            if completed is None:
                completed = state.get("supplier_products_completed", 0)
            checks["scraping_rate"] = int(completed) >= 20
        except Exception:
            checks["scraping_rate"] = False
    else:
        checks["scraping_rate"] = False

    amazon_cache_dir = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "amazon_cache"
    if amazon_cache_dir.exists():
        recent_files = [
            f for f in amazon_cache_dir.glob("amazon_*.json") if f.stat().st_mtime >= run_start_time
        ]
        checks["amazon_cache"] = len(recent_files) > 0
    else:
        checks["amazon_cache"] = False

    dotted = supplier_domain
    underscored = supplier_domain_to_underscore(supplier_domain)
    linking_candidates = [
        repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / dotted / "linking_map.json",
        repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / underscored / "linking_map.json",
    ]

    linking_map = None
    for c in linking_candidates:
        if c.exists():
            linking_map = c
            break

    if linking_map and linking_map.exists():
        checks["linking_map"] = (
            linking_map.stat().st_mtime >= run_start_time and linking_map.stat().st_size > 100
        )
    else:
        checks["linking_map"] = False

    financial_dir = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "financial_reports"
    if financial_dir.exists():
        recent_csvs = [
            f
            for f in financial_dir.glob("fba_financial_report_*.csv")
            if f.stat().st_mtime >= run_start_time and f.stat().st_size > 1024
        ]
        checks["financial_csv"] = len(recent_csvs) > 0
    else:
        checks["financial_csv"] = False

    checks["processing_state"] = (
        state_file.exists() and state_file.stat().st_mtime >= run_start_time
    )

    checks["no_critical_errors"] = check_logs_for_errors(repo_root, run_start_time)

    return {
        "ok": True,
        "overall": all(checks.values()),
        "checks": checks,
        "state_file": str(state_file),
    }


def check_logs_for_errors(repo_root: Path, run_start_time: float) -> bool:
    logs_dir = repo_root / "logs" / "debug"
    if not logs_dir.exists():
        return True

    recent_logs = [
        f for f in logs_dir.glob("run_custom_*.log") if f.stat().st_mtime >= run_start_time
    ]

    critical_patterns = [
        r"ERROR:",
        r"CRITICAL:",
        r"Exception:",
        r"Traceback \(most recent call last\):",
    ]

    for log_file in recent_logs:
        try:
            content = log_file.read_text(errors="ignore")
            for pattern in critical_patterns:
                if re.search(pattern, content):
                    return False
        except Exception:
            pass

    return True


def run_readiness_check(repo_root: Path, supplier_domain: str) -> dict[str, Any]:
    checks: dict[str, Any] = {}

    checks["cdp_running_9222"] = check_cdp_running(port=9222)

    categories_file_ok = False
    try:
        import json

        cfg = json.load(open(repo_root / "config" / "system_config.json", "r", encoding="utf-8"))
        wf = None
        for key, v in (cfg.get("workflows") or {}).items():
            if v.get("supplier_name") == supplier_domain:
                wf = v
                break
        if wf and wf.get("categories_config_path"):
            p = repo_root / wf["categories_config_path"]
            categories_file_ok = p.exists() and p.stat().st_size > 0
    except Exception:
        categories_file_ok = False

    checks["categories_file_present"] = categories_file_ok

    state_file = (
        repo_root
        / "OUTPUTS"
        / "CACHE"
        / "processing_states"
        / f"{supplier_domain_to_underscore(supplier_domain)}_processing_state.json"
    )
    checks["processing_state_exists"] = state_file.exists()

    return {"ok": True, "checks": checks}
