from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)

DASHBOARD_EXPORT = ROOT / r"FINAL STALE\fba_analysis_202 efg newst4 (1).csv"
SANDBOX_REPORT = ROOT / (
    r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk__sandbox__4e269fb4"
    r"\fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_RECONCILED_20260410_001500.csv"
)


def normalize_ean(value: str) -> str:
    text = "" if value is None else str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return "".join(ch for ch in text if ch.isdigit() or ch in {"X", "x"}).upper()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


dashboard_rows = load_csv(DASHBOARD_EXPORT)
report_rows = load_csv(SANDBOX_REPORT)

report_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = {}
for row in report_rows:
    key = (
        normalize_ean(row.get("EAN", "")),
        row.get("SupplierURL", "").strip(),
        row.get("SupplierTitle", "").strip(),
    )
    report_by_key.setdefault(key, []).append(row)

metric_fields = [
    "NetProfit",
    "ROI",
    "bought_in_past_month",
    "amazon_sales_badge",
    "SupplierPrice_incVAT",
    "SellingPrice_incVAT",
]

shared_rows = 0
exact_metric_match = 0
ambiguous_multi_report_rows = 0
metric_mismatches: list[dict[str, object]] = []

for dash_row in dashboard_rows:
    key = (
        normalize_ean(dash_row.get("EAN", "")),
        dash_row.get("SupplierURL", "").strip(),
        dash_row.get("SupplierTitle", "").strip(),
    )
    matches = report_by_key.get(key, [])
    if not matches:
        continue
    shared_rows += 1
    if len(matches) > 1:
        same_asin = [row for row in matches if row.get("ASIN", "") == dash_row.get("ASIN", "")]
        if len(same_asin) == 1:
            matches = same_asin
        else:
            ambiguous_multi_report_rows += 1
            continue
    report_row = matches[0]
    diff_fields = [
        field
        for field in metric_fields
        if (dash_row.get(field, "") or "") != (report_row.get(field, "") or "")
    ]
    if not diff_fields:
        exact_metric_match += 1
        continue
    metric_mismatches.append(
        {
            "SupplierTitle": dash_row.get("SupplierTitle", ""),
            "DashboardASIN": dash_row.get("ASIN", ""),
            "ReportASIN": report_row.get("ASIN", ""),
            "DiffFields": ", ".join(diff_fields),
            "DashboardValues": {field: dash_row.get(field, "") for field in diff_fields},
            "ReportValues": {field: report_row.get(field, "") for field in diff_fields},
        }
    )

print(f"dashboard_rows={len(dashboard_rows)}")
print(f"report_rows={len(report_rows)}")
print(f"shared_rows={shared_rows}")
print(f"exact_metric_match={exact_metric_match}")
print(f"ambiguous_multi_report_rows={ambiguous_multi_report_rows}")
print(f"metric_mismatch_count={len(metric_mismatches)}")
for mismatch in metric_mismatches[:10]:
    print(mismatch)
