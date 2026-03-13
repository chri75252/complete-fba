from __future__ import annotations

from typing import Any


def _err(
    *, tool: str, field: str, message: str, error: str = "invalid_tool_params"
) -> dict[str, Any]:
    return {
        "ok": False,
        "error": message,
        "code": error,
        "tool": tool,
        "field": field,
        "message": message,
    }


def _is_number(val: object) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def _parse_int(field: str, val: object) -> tuple[bool, int | None, str | None]:
    if val is None:
        return True, None, None
    if isinstance(val, bool):
        return False, None, f"{field} must be an integer"
    if isinstance(val, int):
        return True, val, None
    if isinstance(val, float):
        if val.is_integer():
            return True, int(val), None
        return False, None, f"{field} must be an integer"
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return True, None, None
        try:
            return True, int(s), None
        except Exception:
            return False, None, f"{field} must be an integer"
    return False, None, f"{field} must be an integer"


def _parse_float(field: str, val: object) -> tuple[bool, float | None, str | None]:
    if val is None:
        return True, None, None
    if isinstance(val, bool):
        return False, None, f"{field} must be a number"
    if isinstance(val, (int, float)):
        return True, float(val), None
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return True, None, None
        try:
            return True, float(s), None
        except Exception:
            return False, None, f"{field} must be a number"
    return False, None, f"{field} must be a number"


def _parse_bool(field: str, val: object) -> tuple[bool, bool | None, str | None]:
    if val is None:
        return True, None, None
    if isinstance(val, bool):
        return True, val, None
    if isinstance(val, str):
        s = val.strip().lower()
        if not s:
            return True, None, None
        if s in {"true", "yes", "1"}:
            return True, True, None
        if s in {"false", "no", "0"}:
            return True, False, None
    return False, None, f"{field} must be a boolean"


def _non_empty_str(field: str, val: object) -> tuple[bool, str | None, str | None]:
    if val is None:
        return False, None, f"{field} is required"
    if not isinstance(val, str):
        return False, None, f"{field} must be a string"
    s = val.strip()
    if not s:
        return False, None, f"{field} is required"
    return True, s, None


def _optional_str(field: str, val: object) -> tuple[bool, str | None, str | None]:
    if val is None:
        return True, None, None
    if not isinstance(val, str):
        return False, None, f"{field} must be a string"
    s = val.strip()
    return True, (s or None), None


def _string_list(field: str, val: object) -> tuple[bool, list[str] | None, str | None]:
    if val is None:
        return True, None, None
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return True, None, None
        return True, [s], None
    if not isinstance(val, list):
        return False, None, f"{field} must be an array of strings"
    out: list[str] = []
    for i, item in enumerate(val):
        if not isinstance(item, str):
            return False, None, f"{field}[{i}] must be a string"
        s = item.strip()
        if s:
            out.append(s)
    return True, out, None


def validate_tool_params(tool: str, params: object) -> dict[str, Any]:
    if not isinstance(tool, str) or not tool.strip():
        return _err(
            tool=str(tool or ""), field="tool", message="tool name must be a non-empty string"
        )

    tool = tool.strip()

    if not isinstance(params, dict):
        return _err(tool=tool, field="params", message="params must be an object")

    if tool == "enqueue_run":
        return _validate_enqueue_run(tool, params)
    if tool == "enqueue_product_list_refresh":
        return _validate_enqueue_product_list_refresh(tool, params)
    if tool == "build_product_list_from_cached":
        return _validate_build_product_list_from_cached(tool, params)
    if tool == "query_financial":
        return _validate_query_financial(tool, params)
    if tool == "enqueue_onboarding":
        return _validate_enqueue_onboarding(tool, params)
    if tool == "cancel_run":
        return _validate_cancel_run(tool, params)

    return {"ok": True, "params": dict(params)}


def _validate_enqueue_run(tool: str, p: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}

    ok, supplier_domain, msg = _non_empty_str("supplier_domain", p.get("supplier_domain"))
    if not ok:
        return _err(
            tool=tool, field="supplier_domain", message=msg or "supplier_domain is required"
        )
    cleaned["supplier_domain"] = supplier_domain

    ok, workflow_key, msg = _non_empty_str("workflow_key", p.get("workflow_key"))
    if not ok:
        return _err(tool=tool, field="workflow_key", message=msg or "workflow_key is required")
    cleaned["workflow_key"] = workflow_key

    ok, runner_script, msg = _non_empty_str("runner_script", p.get("runner_script"))
    if not ok:
        return _err(tool=tool, field="runner_script", message=msg or "runner_script is required")
    cleaned["runner_script"] = runner_script

    ok, category_urls, msg = _string_list("category_urls", p.get("category_urls"))
    if not ok:
        return _err(
            tool=tool, field="category_urls", message=msg or "category_urls must be an array"
        )
    category_urls = category_urls or []
    # If resuming a sandbox run, we might not need category URLs directly (the system pulls from previous overrides)
    sandbox_suffix = p.get("sandbox_suffix")
    if not category_urls and not sandbox_suffix:
        return _err(
            tool=tool, field="category_urls", message="category_urls must contain at least one URL"
        )
    cleaned["category_urls"] = category_urls

    ok, max_products, msg = _parse_int("max_products", p.get("max_products"))
    if not ok:
        return _err(
            tool=tool, field="max_products", message=msg or "max_products must be an integer"
        )
    if max_products is not None and max_products < 0:
        return _err(tool=tool, field="max_products", message="max_products must be >= 0")
    cleaned["max_products"] = max_products

    ok, max_per_cat, msg = _parse_int(
        "max_products_per_category", p.get("max_products_per_category")
    )
    if not ok:
        return _err(
            tool=tool,
            field="max_products_per_category",
            message=msg or "max_products_per_category must be an integer",
        )
    if max_per_cat is not None and max_per_cat < 0:
        return _err(
            tool=tool,
            field="max_products_per_category",
            message="max_products_per_category must be >= 0",
        )
    cleaned["max_products_per_category"] = max_per_cat

    ok, run_id, msg = _optional_str("run_id", p.get("run_id"))
    if not ok:
        return _err(tool=tool, field="run_id", message=msg or "run_id must be a string")
    cleaned["run_id"] = run_id

    ok, sandbox_suffix, msg = _optional_str("sandbox_suffix", p.get("sandbox_suffix"))
    if not ok:
        return _err(
            tool=tool, field="sandbox_suffix", message=msg or "sandbox_suffix must be a string"
        )
    cleaned["sandbox_suffix"] = sandbox_suffix

    ok, notes, msg = _optional_str("notes", p.get("notes"))
    if not ok:
        return _err(tool=tool, field="notes", message=msg or "notes must be a string")
    cleaned["notes"] = notes

    return {"ok": True, "params": cleaned}


def _validate_enqueue_product_list_refresh(tool: str, p: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}

    ok, supplier_domain, msg = _non_empty_str("supplier_domain", p.get("supplier_domain"))
    if not ok:
        return _err(
            tool=tool, field="supplier_domain", message=msg or "supplier_domain is required"
        )
    cleaned["supplier_domain"] = supplier_domain

    ok, products_path, msg = _non_empty_str("products_path", p.get("products_path"))
    if not ok:
        return _err(tool=tool, field="products_path", message=msg or "products_path is required")
    cleaned["products_path"] = products_path

    ok, run_id, msg = _optional_str("run_id", p.get("run_id"))
    if not ok:
        return _err(tool=tool, field="run_id", message=msg or "run_id must be a string")
    cleaned["run_id"] = run_id

    ok, notes, msg = _optional_str("notes", p.get("notes"))
    if not ok:
        return _err(tool=tool, field="notes", message=msg or "notes must be a string")
    cleaned["notes"] = notes

    ok, dry_run, msg = _parse_bool("dry_run", p.get("dry_run"))
    if not ok:
        return _err(tool=tool, field="dry_run", message=msg or "dry_run must be a boolean")
    cleaned["dry_run"] = bool(dry_run) if dry_run is not None else False

    return {"ok": True, "params": cleaned}


def _validate_build_product_list_from_cached(tool: str, p: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}

    ok, supplier_domain, msg = _non_empty_str("supplier_domain", p.get("supplier_domain"))
    if not ok:
        return _err(
            tool=tool, field="supplier_domain", message=msg or "supplier_domain is required"
        )
    cleaned["supplier_domain"] = supplier_domain

    ok, output_path, msg = _optional_str("output_path", p.get("output_path"))
    if not ok:
        return _err(tool=tool, field="output_path", message=msg or "output_path must be a string")
    cleaned["output_path"] = output_path

    ok, sample_size, msg = _parse_int("sample_size", p.get("sample_size"))
    if not ok:
        return _err(tool=tool, field="sample_size", message=msg or "sample_size must be an integer")
    sample_size = sample_size if sample_size is not None else 8
    if sample_size <= 0:
        return _err(tool=tool, field="sample_size", message="sample_size must be > 0")
    cleaned["sample_size"] = sample_size

    ok, category_count, msg = _parse_int("category_count", p.get("category_count"))
    if not ok:
        return _err(
            tool=tool, field="category_count", message=msg or "category_count must be an integer"
        )
    category_count = category_count if category_count is not None else 3
    if category_count <= 0:
        return _err(tool=tool, field="category_count", message="category_count must be > 0")
    cleaned["category_count"] = category_count

    ok, overwrite, msg = _parse_bool("overwrite", p.get("overwrite"))
    if not ok:
        return _err(tool=tool, field="overwrite", message=msg or "overwrite must be a boolean")
    cleaned["overwrite"] = bool(overwrite) if overwrite is not None else False

    ok, selection_mode, msg = _optional_str("selection_mode", p.get("selection_mode"))
    if not ok:
        return _err(
            tool=tool,
            field="selection_mode",
            message=msg or "selection_mode must be a string",
        )
    cleaned["selection_mode"] = selection_mode or "random_categories"

    ok, require_ean, msg = _parse_bool("require_ean", p.get("require_ean"))
    if not ok:
        return _err(
            tool=tool, field="require_ean", message=msg or "require_ean must be a boolean"
        )
    cleaned["require_ean"] = bool(require_ean) if require_ean is not None else False

    return {"ok": True, "params": cleaned}


def _validate_query_financial(tool: str, p: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}

    ok, supplier_domain, msg = _non_empty_str("supplier_domain", p.get("supplier_domain"))
    if not ok:
        return _err(
            tool=tool, field="supplier_domain", message=msg or "supplier_domain is required"
        )
    cleaned["supplier_domain"] = supplier_domain

    for f in ("roi_min", "roi_max", "netprofit_min", "netprofit_max"):
        ok, num, msg = _parse_float(f, p.get(f))
        if not ok:
            return _err(tool=tool, field=f, message=msg or f"{f} must be a number")
        cleaned[f] = num

    if cleaned.get("roi_min") is not None and cleaned.get("roi_max") is not None:
        if float(cleaned["roi_min"]) > float(cleaned["roi_max"]):
            return _err(tool=tool, field="roi_min", message="roi_min must be <= roi_max")

    if cleaned.get("netprofit_min") is not None and cleaned.get("netprofit_max") is not None:
        if float(cleaned["netprofit_min"]) > float(cleaned["netprofit_max"]):
            return _err(
                tool=tool, field="netprofit_min", message="netprofit_min must be <= netprofit_max"
            )

    for f in ("ean", "asin"):
        v = p.get(f)
        if v is None:
            cleaned[f] = None
            continue
        if isinstance(v, str):
            cleaned[f] = v.strip() or None
            continue
        if _is_number(v):
            if isinstance(v, float):
                if not v.is_integer():
                    return _err(tool=tool, field=f, message=f"{f} must be a string")
                cleaned[f] = str(int(v))
            else:
                cleaned[f] = str(v)
            continue
        return _err(tool=tool, field=f, message=f"{f} must be a string")

    ok, limit, msg = _parse_int("limit", p.get("limit"))
    if not ok:
        return _err(tool=tool, field="limit", message=msg or "limit must be an integer")
    if limit is None:
        limit = 50
    if limit <= 0:
        return _err(tool=tool, field="limit", message="limit must be >= 1")
    if limit > 10000:
        return _err(tool=tool, field="limit", message="limit must be <= 10000")
    cleaned["limit"] = limit

    return {"ok": True, "params": cleaned}


def _validate_enqueue_onboarding(tool: str, p: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}

    ok, run_id, msg = _optional_str("run_id", p.get("run_id"))
    if not ok:
        return _err(tool=tool, field="run_id", message=msg or "run_id must be a string")
    cleaned["run_id"] = run_id

    ok, supplier_domain, msg = _optional_str("supplier_domain", p.get("supplier_domain"))
    if not ok:
        return _err(
            tool=tool, field="supplier_domain", message=msg or "supplier_domain must be a string"
        )
    cleaned["supplier_domain"] = supplier_domain

    ok, input_path, msg = _non_empty_str("input_path", p.get("input_path"))
    if not ok:
        return _err(tool=tool, field="input_path", message=msg or "input_path is required")
    cleaned["input_path"] = input_path

    ok, output_path, msg = _non_empty_str("output_path", p.get("output_path"))
    if not ok:
        return _err(tool=tool, field="output_path", message=msg or "output_path is required")
    cleaned["output_path"] = output_path

    ok, timeout_seconds, msg = _parse_int("timeout_seconds", p.get("timeout_seconds"))
    if not ok:
        return _err(
            tool=tool, field="timeout_seconds", message=msg or "timeout_seconds must be an integer"
        )
    if timeout_seconds is None:
        timeout_seconds = 4200
    if timeout_seconds <= 0:
        return _err(tool=tool, field="timeout_seconds", message="timeout_seconds must be >= 1")
    cleaned["timeout_seconds"] = timeout_seconds

    return {"ok": True, "params": cleaned}


def _validate_cancel_run(tool: str, p: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    ok, run_id, msg = _optional_str("run_id", p.get("run_id"))
    if not ok:
        return _err(tool=tool, field="run_id", message=msg or "run_id must be a string")
    cleaned["run_id"] = run_id or ""
    return {"ok": True, "params": cleaned}
