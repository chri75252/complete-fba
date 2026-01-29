# FBA Product Analysis Agent (deterministic PhaseA)

This is a standalone, deterministic -PhaseA manual report- generator that reads a supplier-Amazon matched financial report (CSV/XLSX) and produces:
- `CODEX_MANUAL_REPORT_MMDDHHMM.md` (fixed-width tables)
- `coverage_ledger.csv` (one row per RowID)
- `evidence.jsonl` (one JSON object per RowID)
- `run_summary.json` (validation + run metadata)

## Quickstart (Windows / PowerShell)

From repo root (outputs default to `./AGENT REPORT/<run_id>/`):

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
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5-mini
```

Preflight uses OpenAI Chat Completions when `OPENAI_API_KEY` is set, and falls back to deterministic heuristic mode on failure.
