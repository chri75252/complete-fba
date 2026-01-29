from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fba_agent.run import run_analysis


def test_run_analysis_creates_artifacts(tmp_path: Path) -> None:
    input_path = Path(__file__).parent / "fixtures" / "sample_report.csv"
    runs_dir = tmp_path / "runs"
    memory_dir = tmp_path / "memory"

    run_dir = run_analysis(
        input_path=input_path,
        supplier="auto",
        runs_dir=runs_dir,
        memory_dir=memory_dir,
        skip_browser=True,
        overrides_path=None,
        fee_rate=0.30,
    )

    assert run_dir.exists()
    assert (run_dir / "run_summary.json").exists()
    assert (run_dir / "coverage_ledger.csv").exists()
    assert (run_dir / "evidence.jsonl").exists()
    assert list(run_dir.glob("CODEX_MANUAL_REPORT_*.md"))

    ledger = pd.read_csv(run_dir / "coverage_ledger.csv")
    assert len(ledger) == 6
    assert ledger["row_id"].is_unique

    summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "OK"
