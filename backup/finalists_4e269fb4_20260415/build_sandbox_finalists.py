from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)
RUN_ID = "4e269fb4"
FULL_RUN_ID = "4e269fb4-8eea-4589-97ad-d76c0a5a1e30"

REPORT_PATH = ROOT / (
    r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk__sandbox__4e269fb4"
    r"\fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_RECONCILED_20260410_001500.csv"
)
LINKING_MAP_PATH = ROOT / (
    r"OUTPUTS\FBA_ANALYSIS\linking_maps\efghousewares.co.uk__sandbox__4e269fb4\linking_map.json"
)
CACHE_PATH = ROOT / (
    r"OUTPUTS\cached_products\efghousewares-co-uk__sandbox__4e269fb4_products_cache.json"
)
AMAZON_OVERRIDE_DIR = ROOT / (
    r"OUTPUTS\CONTROL_PLANE\overrides\4e269fb4-8eea-4589-97ad-d76c0a5a1e30\amazon_cache"
)
PREVIOUS_ANALYSIS_PATH = ROOT / r"FINAL STALE\fba_analysis_202 efg newst4 (1).csv"
OUTPUT_PATH = ROOT / r"FINAL STALE\efg_4e269fb4_sandbox_finalists_verified_20260415.csv"


def normalize_ean(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    if text.endswith(".0"):
        text = text[:-2]
    if "e+" in text.lower():
        try:
            text = str(int(float(text)))
        except ValueError:
            pass
    return "".join(ch for ch in text if ch.isdigit() or ch in {"X", "x"}).upper()


def to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_str(value: Any) -> str:
    return "" if value is None else str(value).strip()


def slug(text: str) -> str:
    lowered = text.lower()
    return "".join(ch if ch.isalnum() else " " for ch in lowered)


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, slug(a), slug(b)).ratio()


def extract_sales_value(cache_data: dict[str, Any]) -> float | None:
    direct = to_float(cache_data.get("amazon_monthly_sales_badge"))
    if direct is not None:
        return direct
    keepa = cache_data.get("keepa", {})
    product_details = keepa.get("product_details_tab_data", {})
    bought = safe_str(product_details.get("Bought in past month"))
    digits = "".join(ch for ch in bought if ch.isdigit())
    if digits:
        return float(digits)
    estimate = to_float(cache_data.get("estimated_monthly_sales_from_bsr"))
    return estimate


@dataclass
class JoinedRow:
    report: dict[str, Any]
    link: dict[str, Any] | None
    cache: dict[str, Any] | None
    previous: dict[str, Any] | None
    verification_status: str
    verification_reason: str


def load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


report_rows = load_csv(REPORT_PATH)
linking_rows = load_json(LINKING_MAP_PATH)
supplier_cache_rows = load_json(CACHE_PATH)
previous_rows = load_csv(PREVIOUS_ANALYSIS_PATH)

link_by_ean: dict[str, dict[str, Any]] = {}
link_by_url: dict[str, dict[str, Any]] = {}
for entry in linking_rows:
    ean = normalize_ean(entry.get("supplier_ean"))
    if ean and ean not in link_by_ean:
        link_by_ean[ean] = entry
    supplier_url = safe_str(entry.get("supplier_url"))
    if supplier_url and supplier_url not in link_by_url:
        link_by_url[supplier_url] = entry

cache_by_asin: dict[str, dict[str, Any]] = {}
for json_path in AMAZON_OVERRIDE_DIR.glob("amazon_*.json"):
    asin = json_path.stem.split("_", 1)[0].replace("amazon_", "", 1)
    if asin not in cache_by_asin:
        cache_by_asin[asin] = load_json(json_path)

previous_by_ean: dict[str, dict[str, Any]] = {}
previous_by_url: dict[str, dict[str, Any]] = {}
for row in previous_rows:
    row_ean = normalize_ean(row.get("EAN"))
    if row_ean and row_ean not in previous_by_ean:
        previous_by_ean[row_ean] = row
    row_url = safe_str(row.get("SupplierURL") or row.get("supplier_url"))
    if row_url and row_url not in previous_by_url:
        previous_by_url[row_url] = row

supplier_cache_by_ean: dict[str, dict[str, Any]] = {}
supplier_cache_by_url: dict[str, dict[str, Any]] = {}
for row in supplier_cache_rows:
    row_ean = normalize_ean(row.get("ean"))
    if row_ean and row_ean not in supplier_cache_by_ean:
        supplier_cache_by_ean[row_ean] = row
    row_url = safe_str(row.get("url"))
    if row_url and row_url not in supplier_cache_by_url:
        supplier_cache_by_url[row_url] = row


def verify_row(report_row: dict[str, Any], link_row: dict[str, Any] | None, cache_row: dict[str, Any] | None) -> tuple[str, str]:
    report_ean = normalize_ean(report_row.get("EAN"))
    report_title = safe_str(report_row.get("SupplierTitle"))
    report_url = safe_str(report_row.get("SupplierURL"))
    if link_row is None:
        return "REJECT", "No sandbox linking-map entry for this profitable+sellable row"
    if cache_row is None:
        return "REVIEW", "Linking map exists but sandbox override Amazon cache entry is missing"

    link_ean = normalize_ean(link_row.get("supplier_ean"))
    cache_ean = normalize_ean(
        cache_row.get("ean_on_page")
        or cache_row.get("keepa", {}).get("product_details_tab_data", {}).get("Product Codes - EAN")
    )
    link_title = safe_str(link_row.get("amazon_title"))
    cache_title = safe_str(cache_row.get("title"))
    method = safe_str(link_row.get("match_method"))
    title_ratio = similarity(report_title, link_row.get("supplier_title") or "")
    if method == "EAN" and report_ean and link_ean == report_ean and cache_ean == report_ean:
        return "CONFIRMED", "EAN exact across report row, linking map, and sandbox Amazon cache"
    if report_url and report_url == safe_str(link_row.get("supplier_url")) and title_ratio >= 0.92:
        return "CONFIRMED", "Supplier URL and supplier title align with sandbox linking map"
    if cache_title and link_title and similarity(cache_title, link_title) >= 0.96 and method == "title":
        return "REVIEW", "Title-based sandbox link only; requires manual review before inclusion"
    return "REJECT", "Sandbox report row conflicts with authoritative linking-map/cache identity"


joined_rows: list[JoinedRow] = []
for report_row in report_rows:
    profit = to_float(report_row.get("NetProfit"))
    bought = to_float(report_row.get("bought_in_past_month"))
    badge = to_float(report_row.get("amazon_sales_badge"))
    sellable = (bought is not None and bought > 0) or (badge is not None and badge > 0)
    if profit is None or profit <= 0 or not sellable:
        continue
    report_ean = normalize_ean(report_row.get("EAN"))
    report_url = safe_str(report_row.get("SupplierURL"))
    link_row = link_by_ean.get(report_ean) or link_by_url.get(report_url)
    cache_row = None
    if link_row is not None:
        cache_row = cache_by_asin.get(safe_str(link_row.get("amazon_asin")))
    previous_row = previous_by_ean.get(report_ean) or previous_by_url.get(report_url)
    status, reason = verify_row(report_row, link_row, cache_row)
    if status != "CONFIRMED":
        continue
    joined_rows.append(
        JoinedRow(
            report=report_row,
            link=link_row,
            cache=cache_row,
            previous=previous_row,
            verification_status=status,
            verification_reason=reason,
        )
    )

joined_rows.sort(
    key=lambda item: (
        -(to_float(item.report.get("NetProfit")) or 0.0),
        -(to_float(item.report.get("amazon_sales_badge")) or 0.0),
        item.report.get("SupplierTitle") or "",
    )
)

fieldnames = [
    "run_id",
    "source_report",
    "linking_map_path",
    "amazon_cache_dir",
    "verification_status",
    "verification_reason",
    "match_method_authoritative",
    "supplier_ean",
    "supplier_title",
    "supplier_url",
    "authoritative_amazon_asin",
    "authoritative_amazon_title",
    "authoritative_amazon_url",
    "previous_sales",
    "previous_net_profit",
    "previous_roi",
    "current_sales_report",
    "current_sales_cache",
    "current_net_profit",
    "current_roi",
    "supplier_price_report_inc_vat",
    "supplier_price_linking_map",
    "amazon_price_report_inc_vat",
    "amazon_price_cache_current",
    "amazon_price_cache_original",
    "fba_fee_report",
    "referral_fee_report",
    "total_offer_count_report",
    "total_offer_count_cache",
    "report_row_asin",
    "report_row_amazon_title",
]

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    for item in joined_rows:
        cache_data = item.cache or {}
        keepa_data = cache_data.get("keepa", {}).get("product_details_tab_data", {})
        report = item.report
        link = item.link or {}
        previous = item.previous or {}
        writer.writerow(
            {
                "run_id": RUN_ID,
                "source_report": str(REPORT_PATH),
                "linking_map_path": str(LINKING_MAP_PATH),
                "amazon_cache_dir": str(AMAZON_OVERRIDE_DIR),
                "verification_status": item.verification_status,
                "verification_reason": item.verification_reason,
                "match_method_authoritative": link.get("match_method", ""),
                "supplier_ean": normalize_ean(report.get("EAN") or link.get("supplier_ean")),
                "supplier_title": report.get("SupplierTitle") or link.get("supplier_title", ""),
                "supplier_url": report.get("SupplierURL") or link.get("supplier_url", ""),
                "authoritative_amazon_asin": link.get("amazon_asin", ""),
                "authoritative_amazon_title": link.get("amazon_title") or cache_data.get("title", ""),
                "authoritative_amazon_url": f"https://www.amazon.co.uk/dp/{link.get('amazon_asin', '')}" if link.get("amazon_asin") else "",
                "previous_sales": previous.get("sales_value") or previous.get("amazon_sales_badge") or previous.get("bought_in_past_month", ""),
                "previous_net_profit": previous.get("NetProfit") or previous.get("Net_Profit", ""),
                "previous_roi": previous.get("ROI", ""),
                "current_sales_report": report.get("bought_in_past_month") or report.get("amazon_sales_badge", ""),
                "current_sales_cache": extract_sales_value(cache_data) or "",
                "current_net_profit": report.get("NetProfit", ""),
                "current_roi": report.get("ROI", ""),
                "supplier_price_report_inc_vat": report.get("SupplierPrice_incVAT", ""),
                "supplier_price_linking_map": link.get("supplier_price", ""),
                "amazon_price_report_inc_vat": report.get("SellingPrice_incVAT", ""),
                "amazon_price_cache_current": cache_data.get("current_price", ""),
                "amazon_price_cache_original": cache_data.get("original_price", ""),
                "fba_fee_report": report.get("FBAFee", ""),
                "referral_fee_report": report.get("ReferralFee", ""),
                "total_offer_count_report": report.get("total_offer_count", ""),
                "total_offer_count_cache": keepa_data.get("Total Offer Count", ""),
                "report_row_asin": report.get("ASIN", ""),
                "report_row_amazon_title": report.get("AmazonTitle", ""),
            }
        )

print(f"Wrote {len(joined_rows)} verified finalists to {OUTPUT_PATH}")
