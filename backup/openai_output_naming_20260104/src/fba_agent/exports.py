from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fba_agent.atomic import write_text_atomic


def export_run_artifact(runs_dir: Path, run_id: str, fmt: str) -> Path:
    run_dir = runs_dir / run_id
    if not run_dir.exists():
        raise FileNotFoundError(str(run_dir))

    report = next(run_dir.glob("PHASEA_MANUAL_REPORT_*.md"), None)
    ledger_path = run_dir / "coverage_ledger.csv"
    summary_path = run_dir / "run_summary.json"
    evidence_path = run_dir / "evidence.jsonl"

    if fmt == "md":
        if report is None:
            raise FileNotFoundError("Missing PHASEA_MANUAL_REPORT_*.md in run dir")
        return report

    if fmt == "csv":
        if not ledger_path.exists():
            raise FileNotFoundError(str(ledger_path))
        return ledger_path

    if fmt == "json":
        if not ledger_path.exists() or not summary_path.exists():
            raise FileNotFoundError("Missing coverage_ledger.csv or run_summary.json")
        ledger = pd.read_csv(ledger_path).to_dict(orient="records")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        payload = {"summary": summary, "ledger": ledger}
        out_path = run_dir / "export.json"
        write_text_atomic(out_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return out_path

    raise ValueError(f"Unknown format: {fmt}")
