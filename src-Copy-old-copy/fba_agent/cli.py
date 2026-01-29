from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

from fba_agent.constants import DEFAULT_MEMORY_DIRNAME, DEFAULT_RUNS_DIRNAME
from fba_agent.exports import export_run_artifact
from fba_agent.memory_store import show_supplier_memory
from fba_agent.run import run_analysis
from fba_agent.runs import list_runs
from fba_agent.top import print_top_candidates


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fba_agent", add_help=True)
    sub = parser.add_subparsers(dest="cmd", required=True)

    analyze = sub.add_parser("analyze", help="Analyze a CSV/XLSX and write run artifacts")
    analyze.add_argument("--input", required=True, help="Path to input CSV/XLSX")
    analyze.add_argument("--supplier", default="auto", help="Supplier name/id or 'auto'")
    analyze.add_argument("--skip-browser", default="true", help="Browser verification stub (default true)")
    analyze.add_argument(
        "--runs-dir",
        default=DEFAULT_RUNS_DIRNAME,
        help=f"Runs output directory (default ./{DEFAULT_RUNS_DIRNAME})",
    )
    analyze.add_argument(
        "--memory-dir",
        default=DEFAULT_MEMORY_DIRNAME,
        help=f"Memory directory (default ./{DEFAULT_MEMORY_DIRNAME})",
    )
    analyze.add_argument("--overrides", default=None, help="Overrides JSONL path (optional)")
    analyze.add_argument("--fee-rate", type=float, default=0.30, help="Fee rate fallback (default 0.30)")
    analyze.add_argument("--max-iterations", type=int, default=2, help="Max iterations (default 2)")
    analyze.add_argument("--enable-ai", default="true", help="Enable AI features (default true)")
    analyze.add_argument("--provider", default=None, help="LLM provider: openai, gemini, moonshot (auto-detect if not specified)")

    top = sub.add_parser("top", help="Show top candidates from a run")
    top.add_argument("--run-id", required=True, help="Run id (folder name under runs)")
    top.add_argument(
        "--runs-dir",
        default=DEFAULT_RUNS_DIRNAME,
        help=f"Runs output directory (default ./{DEFAULT_RUNS_DIRNAME})",
    )
    top.add_argument("--min-confidence", type=int, default=80, help="Minimum confidence (default 80)")
    top.add_argument("--limit", type=int, default=30, help="Max rows to display (default 30)")

    explain = sub.add_parser("explain", help="Explain a RowID from a run (prints evidence JSON)")
    explain.add_argument("--run-id", required=True)
    explain.add_argument("--rowid", required=True, type=int)
    explain.add_argument("--runs-dir", default=DEFAULT_RUNS_DIRNAME)

    export = sub.add_parser("export", help="Export run output in md|csv|json")
    export.add_argument("--run-id", required=True)
    export.add_argument("--format", required=True, choices=["md", "csv", "json"])
    export.add_argument("--runs-dir", default=DEFAULT_RUNS_DIRNAME)

    rerun = sub.add_parser("rerun", help="Rerun a previous run (same input) with overrides")
    rerun.add_argument("--run-id", required=True)
    rerun.add_argument("--runs-dir", default=DEFAULT_RUNS_DIRNAME)
    rerun.add_argument("--memory-dir", default=DEFAULT_MEMORY_DIRNAME)
    rerun.add_argument("--apply-overrides", required=True, help="Overrides JSONL path")
    rerun.add_argument("--fee-rate", type=float, default=0.30)

    list_runs_parser = sub.add_parser("list-runs", help="List runs under runs dir")
    list_runs_parser.add_argument("--runs-dir", default=DEFAULT_RUNS_DIRNAME)

    show_memory = sub.add_parser("show-memory", help="Show supplier memory summary")
    show_memory.add_argument("--supplier", required=True)
    show_memory.add_argument("--memory-dir", default=DEFAULT_MEMORY_DIRNAME)

    return parser


def _read_evidence_jsonl(evidence_path: Path, row_id: int) -> dict | None:
    if not evidence_path.exists():
        return None
    with evidence_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("row_id") == row_id:
                return obj
    return None


def main(argv: list[str] | None = None) -> int:
    if load_dotenv is not None:
        load_dotenv()
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "analyze":
        skip_browser = str(args.skip_browser).lower() in {"1", "true", "yes", "y"}
        enable_ai = str(args.enable_ai).lower() in {"1", "true", "yes", "y"}
        run_analysis(
            input_path=Path(args.input),
            supplier=args.supplier,
            runs_dir=Path(args.runs_dir),
            memory_dir=Path(args.memory_dir),
            skip_browser=skip_browser,
            overrides_path=Path(args.overrides) if args.overrides else None,
            fee_rate=args.fee_rate,
            max_iterations=args.max_iterations,
            enable_ai=enable_ai,
            provider_name=args.provider,
        )
        return 0

    if args.cmd == "top":
        print_top_candidates(
            runs_dir=Path(args.runs_dir),
            run_id=args.run_id,
            min_confidence=args.min_confidence,
            limit=args.limit,
        )
        return 0

    if args.cmd == "explain":
        run_dir = Path(args.runs_dir) / args.run_id
        evidence_path = run_dir / "evidence.jsonl"
        obj = _read_evidence_jsonl(evidence_path, args.rowid)
        if obj is None:
            raise SystemExit(f"RowID {args.rowid} not found in {evidence_path}")
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "export":
        out_path = export_run_artifact(Path(args.runs_dir), args.run_id, args.format)
        print(str(out_path))
        return 0

    if args.cmd == "rerun":
        run_dir = Path(args.runs_dir) / args.run_id
        summary_path = run_dir / "run_summary.json"
        if not summary_path.exists():
            raise SystemExit(f"Missing {summary_path}")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        input_path = Path(summary["input_file"])
        supplier = summary.get("supplier", "auto")
        run_analysis(
            input_path=input_path,
            supplier=supplier,
            runs_dir=Path(args.runs_dir),
            memory_dir=Path(args.memory_dir),
            skip_browser=True,
            overrides_path=Path(args.apply_overrides),
            fee_rate=args.fee_rate,
            max_iterations=2,  # Default for reruns
            enable_ai=True,    # Enable AI for reruns
            provider_name=None,  # Auto-detect provider
        )
        return 0

    if args.cmd == "list-runs":
        for run_id in list_runs(Path(args.runs_dir)):
            print(run_id)
        return 0

    if args.cmd == "show-memory":
        print(show_supplier_memory(Path(args.memory_dir), args.supplier))
        return 0

    raise SystemExit(f"Unknown command: {args.cmd}")
