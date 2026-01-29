from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from control_plane.normalize import supplier_domain_to_hyphen


@dataclass(frozen=True)
class FinancialQuery:
    supplier_domain: str
    roi_min: float | None = None
    roi_max: float | None = None
    netprofit_min: float | None = None
    netprofit_max: float | None = None
    ean: str | None = None
    asin: str | None = None
    limit: int = 50


def find_latest_financial_report(repo_root: Path, supplier_domain: str) -> Path | None:
    supplier_folder = supplier_domain_to_hyphen(supplier_domain)
    reports_dir = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "financial_reports" / supplier_folder
    if not reports_dir.exists():
        return None

    candidates = sorted(
        reports_dir.glob("fba_financial_report_*.csv"), key=lambda p: p.stat().st_mtime
    )
    return candidates[-1] if candidates else None


def query_financial_rows(repo_root: Path, query: FinancialQuery) -> dict[str, Any]:
    report_path = find_latest_financial_report(repo_root, query.supplier_domain)
    if not report_path:
        return {
            "ok": False,
            "error": "No financial report found",
            "report_path": None,
            "rows": [],
            "row_count": 0,
        }

    df = pd.read_csv(report_path)

    # Column naming varies across versions; attempt common variants.
    def first_col(*names: str) -> str | None:
        for n in names:
            if n in df.columns:
                return n
        return None

    roi_col = first_col("ROI", "roi", "roi_percent", "roi_percent_value")
    net_col = first_col("NetProfit", "net_profit", "net_profit_gbp", "net_profit_per_unit")
    ean_col = first_col("EAN", "ean")
    asin_col = first_col("ASIN", "asin")

    filtered = df

    if query.ean and ean_col:
        filtered = filtered[filtered[ean_col].astype(str) == str(query.ean)]
    if query.asin and asin_col:
        filtered = filtered[filtered[asin_col].astype(str) == str(query.asin)]

    if roi_col and query.roi_min is not None:
        filtered = filtered[filtered[roi_col] >= query.roi_min]
    if roi_col and query.roi_max is not None:
        filtered = filtered[filtered[roi_col] <= query.roi_max]

    if net_col and query.netprofit_min is not None:
        filtered = filtered[filtered[net_col] >= query.netprofit_min]
    if net_col and query.netprofit_max is not None:
        filtered = filtered[filtered[net_col] <= query.netprofit_max]

    if query.limit > 0:
        filtered = filtered.head(query.limit)

    return {
        "ok": True,
        "report_path": str(report_path),
        "row_count": int(len(filtered)),
        "columns": list(filtered.columns),
        "rows": filtered.to_dict(orient="records"),
    }
