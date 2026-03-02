from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from control_plane.json_io import read_json
from control_plane.normalize import supplier_domain_to_hyphen, supplier_domain_to_underscore
from control_plane.paths import get_paths


_MAX_LOG_SCAN_LINES = 5000
_MAX_ERROR_ITEMS = 12
_LOG_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("http_404", re.compile(r"\b404\b", re.IGNORECASE)),
    ("empty_category", re.compile(r"EMPTY CATEGORY", re.IGNORECASE)),
    ("exception", re.compile(r"\bexception\b|\btraceback\b", re.IGNORECASE)),
)
_PRICE_LIKE_PATTERN = re.compile(r"^\s*[£$]?\d+(?:\.\d+)?\s*$")


def validate_run_integrity(run_id: str) -> dict[str, Any]:
    """
    Deterministically validate a completed run.
    Handles both standard FBA workflows and supplier onboarding wizard jobs.
    """
    normalized_run_id = str(run_id or "").strip()
    if not normalized_run_id:
        return {
            "status": "error",
            "errors_found": ["missing_run_id"],
        }

    paths = get_paths()
    repo_root = paths.repo_root

    # Load job payload to determine mode
    job_payload = _load_run_job_payload(paths, normalized_run_id)
    if not job_payload:
        return {"status": "error", "errors_found": ["job_json_not_found"]}

    job_type = str(job_payload.get("job_type", ""))

    if job_type == "run_onboarding_wizard":
        return _validate_onboarding_run(repo_root, job_payload)
    else:
        return _validate_standard_workflow(repo_root, paths, normalized_run_id, job_payload)


def _validate_onboarding_run(repo_root: Path, job_payload: dict[str, Any]) -> dict[str, Any]:
    """Validates the output of a supplier_onboarding_wizard execution."""
    supplier_domain = str(job_payload.get("supplier_domain", "")).strip()
    if not supplier_domain:
        return {"status": "error", "errors_found": ["missing_supplier_domain_in_job"]}

    domain_hyphen = supplier_domain.replace(".", "-")
    domain_underscore = supplier_domain.replace(".", "_")

    errors: list[str] = []
    checks: dict[str, bool] = {}

    # 1. Check Filesystem Artifacts
    runner_script = repo_root / f"run_custom_{domain_hyphen}.py"
    checks["runner_script_exists"] = runner_script.exists()
    if not runner_script.exists():
        errors.append(f"missing_file: {runner_script.name}")

    categories_file = repo_root / "config" / f"{domain_underscore}_categories.json"
    checks["categories_json_exists"] = categories_file.exists()
    if not categories_file.exists():
        errors.append(f"missing_file: {categories_file.name}")

    selectors_file = repo_root / "config" / "supplier_configs" / f"{supplier_domain}.json"
    checks["selectors_json_exists"] = selectors_file.exists()
    if not selectors_file.exists():
        errors.append(f"missing_file: {selectors_file.name}")

    # Determine if auth was required from the wizard payload
    wizard_payload = job_payload.get("wizard", {})
    input_path = repo_root / str(wizard_payload.get("input", ""))
    auth_required = False
    workflow_key = f"{domain_underscore}_workflow"

    if input_path.exists():
        try:
            wizard_input = read_json(input_path)
            auth_required = bool(wizard_input.get("authentication_required"))
            workflow_key = str(wizard_input.get("workflow_key") or workflow_key)
        except Exception:
            pass

    if auth_required:
        auth_script = repo_root / "tools" / domain_hyphen / "supplier_authentication_service.py"
        checks["auth_script_exists"] = auth_script.exists()
        if not auth_script.exists():
            errors.append(f"missing_file: {auth_script.name}")

    # 2. Check System Config Injection
    system_config_path = repo_root / "config" / "system_config.json"
    try:
        sys_config = read_json(system_config_path)

        # Check Workflow Key
        workflows = sys_config.get("workflows", {})
        if workflow_key in workflows:
            checks["workflow_injected"] = True
            wf = workflows[workflow_key]
            if not wf.get("test_product_url"):
                errors.append("system_config: missing test_product_url in workflow")
        else:
            checks["workflow_injected"] = False
            errors.append(f"system_config: missing workflow key {workflow_key}")

        # Check Credentials if auth required
        if auth_required:
            creds = sys_config.get("credentials", {})
            if supplier_domain in creds:
                checks["credentials_injected"] = True
            else:
                checks["credentials_injected"] = False
                errors.append(f"system_config: missing credentials for {supplier_domain}")

    except Exception as e:
        errors.append(f"system_config_read_error: {str(e)}")

    return {
        "status": "success" if not errors else "failed",
        "mode": "onboarding_validation",
        "supplier_domain": supplier_domain,
        "checks_passed": checks,
        "errors_found": errors,
    }


def _validate_standard_workflow(
    repo_root: Path, paths: Any, normalized_run_id: str, job_payload: dict[str, Any]
) -> dict[str, Any]:
    """Validates standard FBA Extraction and Product List Refresh jobs."""
    sandbox_id = normalized_run_id[:8]
    status_payload = _safe_read_json(paths.status_dir / f"{normalized_run_id}.json")
    status_state = str((status_payload or {}).get("state") or "unknown")
    supplier_hint = _extract_supplier_hint(status_payload, job_payload)

    log_path = _resolve_log_path(paths, normalized_run_id, status_payload)
    linking_map_path = _resolve_linking_map_path(
        repo_root=repo_root,
        run_id=normalized_run_id,
        sandbox_id=sandbox_id,
        status_payload=status_payload,
        supplier_hint=supplier_hint,
    )
    cached_products_path = _resolve_cached_products_path(
        repo_root=repo_root,
        run_id=normalized_run_id,
        sandbox_id=sandbox_id,
        status_payload=status_payload,
        supplier_hint=supplier_hint,
    )

    linking_map_rows = _extract_linking_map_rows(_safe_read_json(linking_map_path))
    cached_product_rows = _extract_cached_product_rows(_safe_read_json(cached_products_path))

    errors_found: list[str] = []
    linking_schema_errors: list[str] = []

    if not linking_map_rows:
        linking_schema_errors.append("linking_map_empty")
    else:
        sampled_linking_rows = _sample_rows(linking_map_rows, normalized_run_id)
        for idx, row in sampled_linking_rows:
            linking_schema_errors.extend(_validate_linking_map_row(row, idx))

    errors_found.extend(linking_schema_errors)

    sampled_cached_rows = _sample_rows(cached_product_rows, normalized_run_id)
    for idx, row in sampled_cached_rows:
        errors_found.extend(_validate_full_product_dict(row, idx))

    should_run_triangulation = bool(linking_schema_errors)
    triangulation_diagnosis = ""
    if should_run_triangulation:
        triangulation_diagnosis = _execute_triangulation_fallback(
            repo_root=repo_root,
            run_id=normalized_run_id,
            sandbox_id=sandbox_id,
            supplier_hint=supplier_hint,
            linking_map_path=linking_map_path,
            linking_map_rows=linking_map_rows,
            cached_product_rows=cached_product_rows,
            log_path=log_path,
            linking_schema_errors=linking_schema_errors,
        )

    schema_ok = len(errors_found) == 0

    return {
        "status": "success" if schema_ok and status_state != "failed" else "failed",
        "mode": "standard_workflow",
        "run_id": normalized_run_id,
        "entries_generated": {
            "cached_products": len(cached_product_rows),
            "linking_map": len(linking_map_rows),
        },
        "schema_ok": schema_ok,
        "errors_found": errors_found[:_MAX_ERROR_ITEMS],
        "triangulation_diagnosis": triangulation_diagnosis,
    }


def _validate_full_product_dict(product: dict[str, Any], index: int) -> list[str]:
    """Validates an entire product dictionary comprehensively."""
    errors = []

    # 1. Check Title
    title = product.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append(f"product[{index}].title_invalid_or_empty")

    # 2. Check URL
    url = product.get("url")
    if not _looks_like_http_url(url):
        errors.append(f"product[{index}].url_invalid")
    if _looks_like_price_string(url):
        errors.append(f"product[{index}].url_looks_like_price")

    # 3. Check Price
    price = product.get("price")
    if not isinstance(price, int | float) or isinstance(price, bool):
        errors.append(f"product[{index}].price_not_numeric")

    # 4. Check Source URL
    source_url = product.get("source_url")
    if source_url and not _looks_like_http_url(source_url):
        errors.append(f"product[{index}].source_url_invalid")

    # 5. Check EAN (if present)
    ean = product.get("ean")
    if ean is not None:
        if not isinstance(ean, str):
            errors.append(f"product[{index}].ean_must_be_string")
        elif ean.strip() and not ean.strip().isdigit():
            errors.append(f"product[{index}].ean_contains_non_digits")

    return errors


def _validate_linking_map_row(row: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []

    ean = _pick_first(row, ("supplier_ean", "ean"))
    if not isinstance(ean, str) or not ean.strip() or not ean.strip().isdigit():
        errors.append(f"linking_map[{index}].ean_must_be_digits")

    supplier_url = _pick_first(row, ("supplier_url", "source_url", "url", "product_url"))
    if not _looks_like_http_url(supplier_url):
        errors.append(f"linking_map[{index}].supplier_url_invalid")

    amazon_url = _pick_first(row, ("amazon_url", "amazon_product_url"))
    if amazon_url is not None and str(amazon_url).strip() and not _looks_like_http_url(amazon_url):
        errors.append(f"linking_map[{index}].amazon_url_invalid")

    asin = _pick_first(row, ("amazon_asin", "asin"))
    if not isinstance(asin, str) or not re.fullmatch(r"[A-Za-z0-9]{10}", asin.strip()):
        errors.append(f"linking_map[{index}].asin_invalid")

    supplier_price = _coerce_float(_pick_first(row, ("supplier_price", "price")))
    if supplier_price is None:
        errors.append(f"linking_map[{index}].supplier_price_not_float")

    amazon_price = _coerce_float(_pick_first(row, ("amazon_price",)))
    if amazon_price is None:
        errors.append(f"linking_map[{index}].amazon_price_not_float")

    return errors


def _execute_triangulation_fallback(
    *,
    repo_root: Path,
    run_id: str,
    sandbox_id: str,
    supplier_hint: str,
    linking_map_path: Path | None,
    linking_map_rows: list[dict[str, Any]],
    cached_product_rows: list[dict[str, Any]],
    log_path: Path | None,
    linking_schema_errors: list[str],
) -> str:
    system_config_path = repo_root / "config" / "system_config.json"
    system_config = _safe_read_json(system_config_path)

    batch_size = 1
    if isinstance(system_config, dict):
        system_block = system_config.get("system")
        if isinstance(system_block, dict):
            batch_size = _coerce_int(system_block.get("financial_report_batch_size"), default=1)
    if batch_size < 1:
        batch_size = 1

    linking_count = len(linking_map_rows)
    cached_count = len(cached_product_rows)

    extraction_worked = cached_count > 0
    matching_likely_failed = extraction_worked and linking_count == 0

    log_signals = _scan_log_for_errors(log_path)
    log_404_or_empty = [
        signal
        for signal in log_signals
        if signal.startswith("http_404:") or signal.startswith("empty_category:")
    ]

    financial_report_expected = linking_count >= batch_size
    report_exists, report_example = _financial_report_exists_for_run(
        repo_root=repo_root,
        run_id=run_id,
        sandbox_id=sandbox_id,
        supplier_hint=supplier_hint,
        linking_map_path=linking_map_path,
    )

    schema_excerpt = ", ".join(linking_schema_errors[:3]) if linking_schema_errors else "none"
    log_excerpt = "; ".join(log_404_or_empty[:2]) if log_404_or_empty else "none"
    report_label = report_example.name if report_example is not None else "none"

    return (
        "Cascade Triangulation: "
        f"linking_entries={linking_count}; cached_products={cached_count}; "
        f"schema_signals={schema_excerpt}; "
        f"extraction_worked={str(extraction_worked).lower()}; "
        f"matching_likely_failed={str(matching_likely_failed).lower()}; "
        f"log_404_or_empty={log_excerpt}; "
        f"financial_report_batch_size={batch_size}; "
        f"financial_report_expected={str(financial_report_expected).lower()}; "
        f"financial_report_exists={str(report_exists).lower()}; "
        f"financial_report_example={report_label}"
    )


def _financial_report_exists_for_run(
    *,
    repo_root: Path,
    run_id: str,
    sandbox_id: str,
    supplier_hint: str,
    linking_map_path: Path | None,
) -> tuple[bool, Path | None]:
    reports_root = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "financial_reports"
    if not reports_root.exists() or not reports_root.is_dir():
        return False, None

    all_reports = sorted(reports_root.rglob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not all_reports:
        return False, None

    tokens: list[str] = [run_id.lower(), sandbox_id.lower()]
    if supplier_hint:
        dotted = supplier_hint.strip().lower()
        tokens.extend(
            [
                dotted,
                supplier_domain_to_hyphen(dotted),
                supplier_domain_to_underscore(dotted),
            ]
        )
    if linking_map_path is not None:
        tokens.append(linking_map_path.parent.name.lower())

    normalized_tokens = [re.sub(r"[^a-z0-9]", "", token) for token in tokens if token]
    for report in all_reports:
        report_text = str(report).lower()
        report_text_normalized = re.sub(r"[^a-z0-9]", "", report_text)
        for token in tokens:
            if token and token in report_text:
                return True, report
        for token in normalized_tokens:
            if token and token in report_text_normalized:
                return True, report

    return False, None


def _pick_first(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in row:
            return row.get(key)
    return None


def _coerce_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        cleaned = re.sub(r"^[£$€]\s*", "", cleaned)
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _coerce_int(value: Any, default: int) -> int:
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        try:
            return int(float(text))
        except ValueError:
            return default
    return default


# --- Helper Functions below remain unchanged from standard Oracle architecture ---


def _safe_read_json(path: Path | None) -> Any:
    if path is None or not path.exists() or not path.is_file():
        return None
    try:
        return read_json(path)
    except Exception:
        return None


def _load_run_job_payload(paths: Any, run_id: str) -> dict[str, Any] | None:
    job_name = f"job_{run_id}.json"
    for directory in (paths.jobs_running, paths.jobs_done, paths.jobs_failed, paths.jobs_pending):
        payload = _safe_read_json(directory / job_name)
        if isinstance(payload, dict):
            return payload
    return None


def _extract_supplier_hint(
    status_payload: dict[str, Any] | None, job_payload: dict[str, Any] | None
) -> str:
    if isinstance(job_payload, dict):
        sandbox_supplier = job_payload.get("sandbox_supplier")
        if isinstance(sandbox_supplier, str) and sandbox_supplier.strip():
            return sandbox_supplier.strip()
    if isinstance(status_payload, dict):
        supplier_domain = status_payload.get("supplier_domain")
        if isinstance(supplier_domain, str) and supplier_domain.strip():
            return supplier_domain.strip()
    return ""


def _resolve_log_path(
    paths: Any, run_id: str, status_payload: dict[str, Any] | None
) -> Path | None:
    candidates: list[Path] = []
    if isinstance(status_payload, dict):
        resolved = status_payload.get("resolved_paths")
        if isinstance(resolved, dict):
            candidate = _to_path(resolved.get("runner_log"))
            if candidate is not None:
                candidates.append(candidate)
    candidates.append(paths.logs_dir / f"{run_id}.log")
    return _first_existing_path(candidates)


def _resolve_linking_map_path(
    *,
    repo_root: Path,
    run_id: str,
    sandbox_id: str,
    status_payload: dict[str, Any] | None,
    supplier_hint: str,
) -> Path | None:
    linking_maps_dir = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps"
    candidates: list[Path] = []
    if linking_maps_dir.exists():
        candidates.extend(
            sorted(
                linking_maps_dir.glob(f"*{sandbox_id}*/linking_map.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        )
    if supplier_hint:
        candidates.extend(_supplier_linking_map_candidates(linking_maps_dir, supplier_hint))
    candidates.append(linking_maps_dir / run_id / "linking_map.json")
    return _first_existing_path(candidates)


def _resolve_cached_products_path(
    *,
    repo_root: Path,
    run_id: str,
    sandbox_id: str,
    status_payload: dict[str, Any] | None,
    supplier_hint: str,
) -> Path | None:
    cached_dir = repo_root / "OUTPUTS" / "cached_products"
    candidates: list[Path] = []
    if cached_dir.exists():
        candidates.extend(
            sorted(
                cached_dir.glob(f"*{sandbox_id}*_products_cache.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        )
    if supplier_hint:
        candidates.extend(_supplier_cached_products_candidates(cached_dir, supplier_hint))
    candidates.append(cached_dir / f"{run_id}_products_cache.json")
    return _first_existing_path(candidates)


def _supplier_linking_map_candidates(linking_maps_dir: Path, supplier_hint: str) -> list[Path]:
    dotted = supplier_hint.strip()
    return [
        linking_maps_dir / dotted / "linking_map.json",
        linking_maps_dir / supplier_domain_to_underscore(dotted) / "linking_map.json",
        linking_maps_dir / supplier_domain_to_hyphen(dotted) / "linking_map.json",
    ]


def _supplier_cached_products_candidates(cached_dir: Path, supplier_hint: str) -> list[Path]:
    dotted = supplier_hint.strip()
    return [
        cached_dir / f"{supplier_domain_to_hyphen(dotted)}_products_cache.json",
        cached_dir / f"{supplier_domain_to_underscore(dotted)}_products_cache.json",
        cached_dir / f"{dotted}_products_cache.json",
    ]


def _to_path(value: Any) -> Path | None:
    if not isinstance(value, str):
        return None
    if not value.strip():
        return None
    return Path(value.strip())


def _first_existing_path(candidates: list[Path]) -> Path | None:
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _scan_log_for_errors(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except Exception:
        return ["log_read_error"]
    found: list[str] = []
    for line in lines[-_MAX_LOG_SCAN_LINES:]:
        text = line.strip()
        if not text:
            continue
        for label, pattern in _LOG_PATTERNS:
            if pattern.search(text):
                found.append(f"{label}: {text[:180]}")
    return found[:_MAX_ERROR_ITEMS]


def _extract_linking_map_rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [row for row in data.values() if isinstance(row, dict)]
    return []


def _extract_cached_product_rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        products = data.get("products")
        if isinstance(products, list):
            return [row for row in products if isinstance(row, dict)]
    return []


def _sample_rows(rows: list[dict[str, Any]], run_id: str) -> list[tuple[int, dict[str, Any]]]:
    if not rows:
        return []
    sample_size = min(3, len(rows))
    if len(rows) <= sample_size:
        return list(enumerate(rows))
    rng = random.Random(f"{run_id}:{len(rows)}")
    indices = sorted(rng.sample(range(len(rows)), sample_size))
    return [(idx, rows[idx]) for idx in indices]


def _looks_like_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _looks_like_price_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(_PRICE_LIKE_PATTERN.match(value.strip()))
