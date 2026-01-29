from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from fba_agent.analysis import analyze_all_rows
from fba_agent.atomic import write_json_atomic, write_text_atomic
from fba_agent.io import load_report, normalize_columns
from fba_agent.memory_store import (
    load_supplier_memory,
    merge_calibration,
    persist_calibration,
    supplier_id_from_name,
)
from fba_agent.preflight import run_preflight
from fba_agent.render import render_phasea_report
from fba_agent.types import MergedConfig
from fba_agent.validate import validate_coverage, validate_profit


def _now_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _write_evidence_jsonl(path: Path, evidence: list[dict[str, Any]]) -> None:
    lines = [json.dumps(obj, ensure_ascii=False) for obj in evidence]
    write_text_atomic(path, "\n".join(lines) + "\n")


def _write_csv_atomic(path: Path, df: pd.DataFrame) -> None:
    write_text_atomic(path, df.to_csv(index=False))


def run_analysis(
    *,
    input_path: Path,
    supplier: str,
    runs_dir: Path,
    memory_dir: Path,
    skip_browser: bool,
    overrides_path: Path | None,
    fee_rate: float,
) -> Path:
    df_raw, schema = load_report(input_path)
    df, normalization_report = normalize_columns(df_raw)

    supplier_id = supplier_id_from_name(supplier if supplier != "auto" else input_path.stem)
    memory_bundle = load_supplier_memory(memory_dir, supplier_id)

    sample = df.head(50).copy()
    preflight_naming, preflight_warnings, preflight_diag = run_preflight(sample)

    naming, calibration_diff = merge_calibration(
        supplier_id=supplier_id,
        memory_bundle=memory_bundle,
        preflight_naming=preflight_naming,
        overrides_path=overrides_path,
    )

    merged_config = MergedConfig(supplier_id=supplier_id, naming=naming, fee_rate=fee_rate)

    brand_aliases = memory_bundle.get("brand_aliases") or {}

    ledger, evidence = analyze_all_rows(df, merged_config, brand_aliases=brand_aliases)

    cov = validate_coverage(ledger, df)
    prof = validate_profit(ledger)

    validation_errors = cov.errors + prof.errors
    validation_passed = cov.passed and prof.passed

    run_id = _now_run_id()
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "run_id": run_id,
        "status": "OK" if validation_passed else "FAILED",
        "input_file": str(input_path),
        "supplier": supplier_id,
        "skip_browser": bool(skip_browser),
        "preflight": {"warnings": preflight_warnings, "diagnostics": preflight_diag},
        "normalization_report": normalization_report,
        "schema": {
            "input_path": schema.input_path,
            "rows": schema.rows,
            "detected_columns": schema.detected_columns,
            "warnings": schema.warnings,
        },
        "validation": {"passed": validation_passed, "errors": validation_errors},
    }

    # Always write run_summary.json for debugging (even if gates fail).
    write_json_atomic(run_dir / "run_summary.json", summary)
    write_json_atomic(run_dir / "merged_calibration.json", naming.__dict__)
    write_json_atomic(run_dir / "calibration_diff.json", calibration_diff)

    if not validation_passed:
        raise SystemExit("Validation gates failed. See run_summary.json for details.")

    _write_csv_atomic(run_dir / "coverage_ledger.csv", ledger)
    _write_evidence_jsonl(run_dir / "evidence.jsonl", evidence)

    report_md = render_phasea_report(
        ledger,
        input_file=str(input_path),
        supplier=supplier_id,
        generated_date=datetime.now().date().isoformat(),
    )
    report_path = run_dir / f"PHASEA_MANUAL_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
    write_text_atomic(report_path, report_md)

    persist_calibration(memory_dir, supplier_id, naming, input_path)

    return run_dir
