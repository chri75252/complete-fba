from __future__ import annotations

from pathlib import Path

import pandas as pd


def print_top_candidates(*, runs_dir: Path, run_id: str, min_confidence: int, limit: int) -> None:
    run_dir = runs_dir / run_id
    ledger_path = run_dir / "coverage_ledger.csv"
    if not ledger_path.exists():
        raise FileNotFoundError(str(ledger_path))

    ledger = pd.read_csv(ledger_path)
    ledger["confidence"] = pd.to_numeric(ledger["confidence"], errors="coerce").fillna(0).astype(int)

    pool = ledger[(ledger["bucket"].isin(["VERIFIED", "HIGHLY_LIKELY"])) & (ledger["confidence"] >= min_confidence)]
    pool = pool.sort_values(["confidence", "sales", "adjusted_profit"], ascending=[False, False, False])
    show = pool.head(limit)

    cols = ["row_id", "bucket", "confidence", "asin", "supplier_title", "amazon_title", "adjusted_profit"]
    for _, r in show.iterrows():
        row_id = int(r.get("row_id"))
        bucket = str(r.get("bucket"))
        conf = int(r.get("confidence"))
        asin = str(r.get("asin") or "")
        adj = r.get("adjusted_profit")
        print(f"{row_id}\t{bucket}\t{conf}\t{asin}\tadj_profit={adj}")

