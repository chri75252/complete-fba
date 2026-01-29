# FBA Product Analysis Agent

A deterministic, production-grade agent for analyzing supplier financial reports against Amazon listings.

## Features
*   **100% Deterministic Coverage**: No missed rows. Every row is bucketed.
*   **Strict EAN Matching**: Validates checksums and handles padding.
*   **Trap Shields**: Prevents "9x9 inch" from being read as "9-pack".
*   **Preflight Calibration**: Learns supplier patterns (e.g. "pcs", "pk") before analysis.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Copy `.env.example` to `.env` and set your `MOONSHOT_API_KEY`.
    ```bash
    cp .env.example .env
    ```

## Usage

**Run Analysis:**
```bash
python -m src.fba_agent.interface.cli analyze --input "path/to/report.csv" --supplier "my_supplier"
```

**Output:**
Artifacts are generated in `runs/run_YYYYMMDD_HHMMSS_supplier/`:
*   `PHASEA_MANUAL_REPORT_YYYYMMDD.md`: The main human-readable report.
*   `coverage_ledger.csv`: The audit trail for every row.
*   `evidence.jsonl`: Detailed machine-readable decision logs.

## Testing
Run unit tests to verify logic:
```bash
pytest tests/
```
