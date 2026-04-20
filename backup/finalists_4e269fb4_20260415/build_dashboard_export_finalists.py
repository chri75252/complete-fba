from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)

DASHBOARD_EXPORT = ROOT / r"FINAL STALE\fba_analysis_202 efg newst4 (1).csv"
LINKING_MAP = ROOT / (
    r"OUTPUTS\FBA_ANALYSIS\linking_maps\efghousewares.co.uk__sandbox__4e269fb4\linking_map.json"
)
OUTPUT_PATH = ROOT / r"FINAL STALE\efg_4e269fb4_finalists_complete_20260415_v2.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_ean(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return "".join(ch for ch in text if ch.isdigit() or ch in {"X", "x"}).upper()


def to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


dashboard_rows = load_csv(DASHBOARD_EXPORT)
linking_rows = load_json(LINKING_MAP)

link_by_ean: dict[str, dict[str, Any]] = {}
link_by_url: dict[str, dict[str, Any]] = {}
for row in linking_rows:
    ean = normalize_ean(row.get("supplier_ean"))
    if ean and ean not in link_by_ean:
        link_by_ean[ean] = row
    supplier_url = row.get("supplier_url")
    if supplier_url and supplier_url not in link_by_url:
        link_by_url[supplier_url] = row

MANUAL_OVERRIDES: dict[str, dict[str, str]] = {
    # === Previously reviewed ===
    "B09VPLM7VM": {
        "verdict": "KEEP",
        "reason": "Manual review confirmed product identity aligns; no visible multipack conflict.",
    },
    "1788245415": {
        "verdict": "KEEP",
        "reason": "Manual review confirmed the sticker book row is a valid match.",
    },
    "B0CCJS5GKB": {
        "verdict": "DROP",
        "reason": "Amazon is 3-pack (3x500g) vs supplier single 500g — pack mismatch.",
    },
    "B07L4Y5CBD": {
        "verdict": "DROP",
        "reason": "Amazon is 2-pack vs supplier single unit — pack mismatch.",
    },
    "B0BTMNY9RV": {
        "verdict": "DROP",
        "reason": "Supplier brand SUPER DREAMER vs Amazon GC GAVENO CAVAILIA — different brand.",
    },
    "B0BTMS65BX": {
        "verdict": "DROP",
        "reason": "Supplier brand SUPER DREAMER vs Amazon GC GAVENO CAVAILIA — different brand.",
    },
    "B0CVQP7XXD": {
        "verdict": "DROP",
        "reason": "Amazon is x18 bones pack vs supplier single treat — pack/format mismatch; 21x price ratio confirms.",
    },
    "B00P2R81MU": {
        "verdict": "NEEDS_MANUAL",
        "reason": "EAN exact but Amazon brand 'Dogi Click and Secure' vs supplier 'Kats Romeo' — same product type, different brand.",
    },
    "B093H2DHHF": {
        "verdict": "NEEDS_MANUAL",
        "reason": "EAN exact but Amazon title omits 'Treat and Ease' brand; product type matches (eye mist spray).",
    },
    "B0863MYSTY": {
        "verdict": "KEEP",
        "reason": "EAN exact. Supplier 'RYSONS PLASTIC BOWLS W/STRAW 4PCE' vs Amazon 'Plastic 4 Sippy Bowls with Built in Straw' — same 4-piece product, different brand. EAN confirms identity.",
    },
    "B099X92QGG": {
        "verdict": "KEEP",
        "reason": "EAN exact. Supplier 'ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML' vs Amazon 'Elliott 480ml Brown Glass Spray Bottle' — same brand, same specs, same EAN. Low title sim is cosmetic.",
    },
    # === Newly analyzed — non-Tier-1 profitable+sellable rows ===
    "B0F327VS5G": {
        "verdict": "KEEP",
        "reason": "Supplier 'KINGAVON 2 WAY PLUG ADAPTOR WITH TYPE C & USB' vs Amazon 'Multi Plug Extension Socket with 4 USB (2 Type C)' — same product type (multi-plug adaptor with USB-C), Amazon EAN missing which increases match likelihood. Profit £1.08, 400 sales/mo.",
    },
    "B0D9LXFL9Q": {
        "verdict": "KEEP",
        "reason": "Supplier 'ASHLEY FUNNEL SET 3PC' vs Amazon '3pcs Funnel Set | Stainless Steel Funnels with Handles' — same 3-piece funnel set, Amazon EAN missing. Brand 'Ashley' is a common kitchen brand. Profit £0.03, 50 sales/mo.",
    },
    "B00534860Y": {
        "verdict": "KEEP",
        "reason": "Supplier 'PLASPLUGS P/BOARD SUPER TOGGLE PK5' vs Amazon 'Plasplug SSTC554 Super Toggle Hollow Fixing' — SAME brand (Plasplug), same product type (super toggle), same pack size (PK5). EANs differ by last digits (5010047103058 vs 5010047125548) — likely packaging/SKU variant. Profit £0.88, 50 sales/mo.",
    },
    "B0F4XH7PSR": {
        "verdict": "KEEP",
        "reason": "Supplier 'KINGFISHER PATIO WEED BRUSH 120CM' vs Amazon 'Harbour Housewares Wooden Long Handle Weed Brush 120cm' — same product type, same 120cm length, different brand. EAN mismatch but product identity is clear from title/size. Profit £1.67, 200 sales/mo.",
    },
    "B01IB2SNES": {
        "verdict": "KEEP",
        "reason": "Supplier 'MAGNETIC TRAVEL GAMES' vs Amazon 'JJPRIME - Magnetic Travel Board Games Set of 4 Chess, Draughts, Ludo, Snakes and Ladders' — same product type (magnetic travel games), EAN mismatch but generic product category. Profit £3.19, 600 sales/mo.",
    },
    "B00366NX7C": {
        "verdict": "KEEP",
        "reason": "Supplier 'ALBERO MULTIPURPOSE TRAY NO3' vs Amazon 'Argon Tableware Black Rectangular Serving Tray' — same product type (serving/multipurpose tray), EAN mismatch but generic product. Profit £1.23, 100 sales/mo.",
    },
    "B09DYDR5F2": {
        "verdict": "KEEP",
        "reason": "Supplier 'PRIMA STAINLESS STEEL STRAINER SET 3PK' vs Amazon 'Sieves and Strainers Set – 3 Pack Stainless Steel Fine Mesh Sieve (7cm, 12cm, 18cm)' — same 3-piece stainless steel strainer set, EAN mismatch but product identity clear. Profit £2.29, 600 sales/mo.",
    },
    "B0DRG3DXWF": {
        "verdict": "KEEP",
        "reason": "Supplier 'ISLA BABY DOLL SET 26CM' vs Amazon 'vamei Baby Doll Set, 12 Inches Baby Born Dolls' — same product type (baby doll set), 26cm ≈ 12 inches, EAN missing on Amazon. Profit £10.14, 100 sales/mo.",
    },
    "B00CI6J5JQ": {
        "verdict": "KEEP",
        "reason": "Supplier 'NEON COLOURING SET' vs Amazon 'CRAYOLA Inspiration Art Case - 140 Pieces' — same product type (colouring/art set), EAN missing on Amazon, Crayola is a known brand. Profit £3.15, 900 sales/mo.",
    },
    "B000UXH8KM": {
        "verdict": "DROP",
        "reason": "Supplier 'EVERREADY T8 4FT 36W TUBE LIGHT' vs Amazon 'Osram 4Ft 36w T8 Fluorescent Tube' — different brands (Everready vs Osram), different EANs. Same spec but different manufacturer.",
    },
    "B0BJTS7R9X": {
        "verdict": "DROP",
        "reason": "Supplier 'REDWOOD TELESCOPIC HIKING POLE' vs Amazon 'Underwood-Aggregator Walking Poles - 2 Pack' — different brands, different EANs, Amazon is 2-pack vs supplier likely single. Title sim 0.24.",
    },
}


def classify_row(row: dict[str, str]) -> tuple[str, str, dict[str, Any] | None]:
    ean = normalize_ean(row.get("EAN"))
    supplier_url = row.get("SupplierURL", "")
    link = link_by_ean.get(ean) or link_by_url.get(supplier_url)
    override = MANUAL_OVERRIDES.get(row.get("ASIN", ""))
    if override is not None:
        return override["verdict"], override["reason"], link
    if str(row.get("ean_exact_match", "")).strip().lower() == "true" and row.get("tier") == "TIER_1_VERIFIED":
        if link is None:
            return "KEEP", "Auto-kept from dashboard export exact-EAN verified row; sandbox linking-map grounding missing for this shortlisted row.", None
        return "KEEP", "Auto-kept from dashboard export exact-EAN verified row.", link
    return "NEEDS_MANUAL", "Not an exact-EAN Tier-1 row and no manual override exists.", link


filtered_rows = []
review_rows = []
for row in dashboard_rows:
    profit = to_float(row.get("NetProfit"))
    sales_value = to_float(row.get("sales_value"))
    bought = to_float(row.get("bought_in_past_month"))
    badge = to_float(row.get("amazon_sales_badge"))
    sellable = any(value is not None and value > 0 for value in (sales_value, bought, badge))
    if profit is None or profit <= 0 or not sellable:
        continue
    verdict, reason, link = classify_row(row)
    output = {
        "SupplierTitle": row.get("SupplierTitle", ""),
        "SupplierURL": row.get("SupplierURL", ""),
        "SupplierEAN": normalize_ean(row.get("EAN")),
        "Dashboard_ASIN": row.get("ASIN", ""),
        "Dashboard_AmazonTitle": row.get("AmazonTitle", ""),
        "Dashboard_NetProfit": row.get("NetProfit", ""),
        "Dashboard_ROI": row.get("ROI", ""),
        "Dashboard_SalesValue": row.get("sales_value", ""),
        "Dashboard_BoughtInPastMonth": row.get("bought_in_past_month", ""),
        "Dashboard_AmazonSalesBadge": row.get("amazon_sales_badge", ""),
        "Dashboard_Tier": row.get("tier", ""),
        "Dashboard_Confidence": row.get("confidence_score", ""),
        "Dashboard_Flags": row.get("flags", ""),
        "Dashboard_Reasons": row.get("reasons", ""),
        "Authoritative_ASIN": "" if not link else link.get("amazon_asin", ""),
        "Authoritative_AmazonTitle": "" if not link else link.get("amazon_title", ""),
        "Authoritative_MatchMethod": "" if not link else link.get("match_method", ""),
        "Authoritative_AmazonPrice": "" if not link else link.get("amazon_price", ""),
        "VerificationDecision": verdict,
        "VerificationReason": reason,
        "ArtifactGrounding": "Missing in sandbox linking map" if link is None else "Present in sandbox linking map",
    }
    if verdict == "KEEP":
        filtered_rows.append(output)
    else:
        review_rows.append(output)

filtered_rows.sort(key=lambda row: float(row["Dashboard_NetProfit"]), reverse=True)

fieldnames = list(filtered_rows[0].keys()) if filtered_rows else [
    "SupplierTitle",
    "SupplierURL",
    "SupplierEAN",
    "Dashboard_ASIN",
    "Dashboard_AmazonTitle",
    "Dashboard_NetProfit",
    "Dashboard_ROI",
    "Dashboard_SalesValue",
    "Dashboard_BoughtInPastMonth",
    "Dashboard_AmazonSalesBadge",
    "Dashboard_Tier",
    "Dashboard_Confidence",
    "Dashboard_Flags",
    "Dashboard_Reasons",
    "Authoritative_ASIN",
    "Authoritative_AmazonTitle",
    "Authoritative_MatchMethod",
    "Authoritative_AmazonPrice",
    "VerificationDecision",
    "VerificationReason",
    "ArtifactGrounding",
]

with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)

print(f"profitable_sellable_rows={len(filtered_rows) + len(review_rows)}")
print(f"final_keep_rows={len(filtered_rows)}")
print(f"rejected_or_manual_rows={len(review_rows)}")
for row in review_rows[:20]:
    print(row)
print(f"output={OUTPUT_PATH}")
