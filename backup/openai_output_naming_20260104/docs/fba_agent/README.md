# FBA Product Analysis Agent (deterministic PhaseA)

This is a standalone, deterministic “PhaseA manual report” generator that reads a supplier↔Amazon matched financial report (CSV/XLSX) and produces:
- `PHASEA_MANUAL_REPORT_YYYYMMDD.md` (fixed-width tables)
- `coverage_ledger.csv` (one row per RowID)
- `evidence.jsonl` (one JSON object per RowID)
- `run_summary.json` (validation + run metadata)

## Quickstart (Windows / PowerShell)

From repo root:

```powershell
python -m fba_agent analyze --input "C:\path\report.xlsx" --supplier auto --skip-browser true
```

List runs:
```powershell
python -m fba_agent list-runs
```

Top candidates:
```powershell
python -m fba_agent top --run-id 20260104_153000 --min-confidence 80 --limit 30
```

Explain one row:
```powershell
python -m fba_agent explain --run-id 20260104_153000 --rowid 626
```

## Environment variables

Add to `.env` (optional):

```bash
MOONSHOT_API_KEY=...
MOONSHOT_BASE_URL=https://api.moonshot.ai/v1
MOONSHOT_MODEL=moonshot-v1-8k
```

Note: MVP preflight currently runs in deterministic heuristic mode even if the key is set (LLM wiring is stubbed).
If `MOONSHOT_API_KEY` is set, the agent will attempt a Moonshot preflight call and fall back to heuristic mode on failure.
