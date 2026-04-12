from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

from dashboard_legacy_streamlit.metrics_core import MetricsLoader


def _normalize_col(name: str) -> str:
    return name.lower().replace("_", "").replace(" ", "")


def _find_column(columns: list[str], candidates: list[str]) -> str | None:
    normalized = [_normalize_col(c) for c in columns]
    for cand in candidates:
        c_norm = _normalize_col(cand)
        if c_norm in normalized:
            return columns[normalized.index(c_norm)]
    return None


def _latest_csv(financial_dir: str) -> str | None:
    if not financial_dir or not os.path.exists(financial_dir):
        return None

    csv_files = [
        f
        for f in os.listdir(financial_dir)
        if f.endswith(".csv") and os.path.isfile(os.path.join(financial_dir, f))
    ]
    if not csv_files:
        return None

    latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(financial_dir, f)))
    return os.path.join(financial_dir, latest_file)


class FinancialQuery:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or os.getcwd()
        self._loader = MetricsLoader(self.base_dir)

    def query_financial_rows(
        self, *, supplier_domain: str, filters: dict[str, Any], limit: int = 50
    ) -> dict[str, Any]:
        paths = self._loader.resolve_paths(supplier_domain)
        financial_dir = paths.get("financial_dir")
        latest_path = _latest_csv(financial_dir) if financial_dir else None

        if not latest_path:
            return {
                "ok": False,
                "reason": "No financial report CSV found",
                "supplier_domain": supplier_domain,
                "rows": [],
            }

        df = pd.read_csv(latest_path, dtype=str)
        cols = list(df.columns)

        roi_col = _find_column(cols, MetricsLoader.ROI_COLUMNS) or _find_column(cols, ["ROI"])
        profit_col = _find_column(cols, MetricsLoader.PROFIT_COLUMNS) or _find_column(
            cols, ["NetProfit"]
        )
        ean_col = _find_column(cols, ["EAN", "supplier_ean", "supplierEAN"])

        work = df.copy()

        if roi_col and filters.get("roi_min") is not None:
            roi_min = float(filters["roi_min"])
            roi_vals = pd.to_numeric(
                work[roi_col].astype(str).str.replace("%", ""), errors="coerce"
            )
            work = work[roi_vals >= roi_min]

        if profit_col and filters.get("netprofit_min") is not None:
            np_min = float(filters["netprofit_min"])
            profit_vals = pd.to_numeric(
                work[profit_col].astype(str).str.replace("£", ""), errors="coerce"
            )
            work = work[profit_vals >= np_min]

        if ean_col and filters.get("ean"):
            needle = str(filters["ean"]).strip()
            work = work[work[ean_col].astype(str).str.strip() == needle]

        if limit > 0:
            work = work.head(int(limit))

        return {
            "ok": True,
            "supplier_domain": supplier_domain,
            "latest_report": latest_path,
            "matched_rows": int(len(work)),
            "columns": cols,
            "rows": work.to_dict(orient="records"),
        }
