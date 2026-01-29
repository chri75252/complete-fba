from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import pandas as pd


EXPECTED_TABLE_COLUMNS: list[str] = [
    "Verdict",
    "Confidence",
    "SupplierTitle",
    "AmazonTitle",
    "Supplier EAN",
    "Amazon EAN",
    "ASIN",
    "SupplierPrice",
    "SellingPrice",
    "NetProfit",
    "ROI",
    "Sales",
    "Pack Verdict",
    "Adjusted Profit",
    "Key Match Evidence",
    "Filter Reason",
]


LUXURY_IP_BRANDS = {
    "jo malone",
    "chanel",
    "dior",
    "gucci",
    "louis vuitton",
    "prada",
    "hermès",
    "hermes",
    "apple",
    "samsung",
    "sony",
    "microsoft",
    "nike",
    "adidas",
}


COLOR_WORDS = {
    "black",
    "white",
    "red",
    "blue",
    "green",
    "yellow",
    "orange",
    "pink",
    "purple",
    "grey",
    "gray",
    "brown",
    "navy",
    "silver",
    "gold",
    "beige",
    "cream",
    "clear",
}


BRAND_COLOR_SHIELD_PHRASES = {
    "blue canyon",
    "green flash",
    "red bull",
}


STOPWORDS = {
    "the",
    "and",
    "with",
    "for",
    "to",
    "of",
    "a",
    "an",
    "in",
    "on",
    "by",
    "from",
    "new",
    "pack",
    "set",
    "pcs",
    "pc",
    "piece",
    "pieces",
    "x",
}


MEASUREMENT_UNITS = {
    "cm",
    "mm",
    "m",
    "inch",
    "in",
    "ft",
    "ml",
    "l",
    "ltr",
    "g",
    "kg",
    "oz",
}


DIMENSION_PATTERNS = [
    # 9 x 9 inch, 20x17cm, 15 x 5.5 x 5.5 cm
    r"\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?(?:\s*[x×]\s*\d+(?:\.\d+)?)?\s*(?:cm|mm|inch|in|m|ft)\b",
    # 280X115MM (no spaces)
    r"\b\d{2,4}\s*[x×]\s*\d{2,4}\s*(?:cm|mm)\b",
    # 500ml, 1L, 4ft, 2.5kg
    r"\b\d+(?:\.\d+)?\s*(?:cm|mm|inch|in|m|ft|ml|l|ltr|g|kg|oz)\b",
]


@dataclass(frozen=True)
class PackParse:
    units: float
    evidence: str | None
    used_dimension_shield: bool


def _as_str(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x).strip()


def parse_money_gbp(x: Any) -> float:
    s = _as_str(x)
    if not s:
        return 0.0
    s = s.replace("£", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_sales(x: Any) -> float:
    s = _as_str(x)
    if not s:
        return 0.0
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return 0.0
    try:
        return float(m.group(1))
    except ValueError:
        return 0.0


def clean_to_digits(raw: Any) -> str:
    s = _as_str(raw)
    if not s:
        return ""
    if "e" in s.lower():
        return ""
    s = s.replace(".0", "")
    return re.sub(r"\D", "", s)


def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit():
        return False
    if len(digits) not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])

    total = 0
    for i, ch in enumerate(body[::-1], start=1):
        d = int(ch)
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check


def normalize_gtin(digits: str) -> str:
    if not digits.isdigit():
        return digits
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in (12, 13, 14):
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits


def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_gtin(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r"0{6,}$", normalized):
        return False
    return gtin_checksum_ok(normalized)


def _normalize_title(s: Any) -> str:
    return re.sub(r"\s+", " ", _as_str(s)).strip()


def strip_dimensions(title: str) -> tuple[str, bool]:
    lowered = title.lower()
    cleaned = lowered
    for pat in DIMENSION_PATTERNS:
        cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    used = cleaned != lowered
    return cleaned, used


def extract_pack_units(title_raw: Any) -> PackParse:
    title = _normalize_title(title_raw)
    if not title:
        return PackParse(units=1.0, evidence=None, used_dimension_shield=False)

    cleaned, used_dimension_shield = strip_dimensions(title)

    # v4.1 nested pack: (4 x 50) -> 200 total items (only if inner has no measurement unit)
    nested = re.search(r"\((\d+)\s*[x×]\s*(\d+)\s*\)", cleaned, flags=re.IGNORECASE)
    if nested:
        outer = float(nested.group(1))
        inner = float(nested.group(2))
        if 1 < outer < 500 and 1 < inner < 500:
            return PackParse(units=outer * inner, evidence=nested.group(0), used_dimension_shield=used_dimension_shield)

    # 3 x 500ml => pack of 3 (do NOT multiply into 1500)
    cap_pack = re.search(
        r"\b(\d+)\s*[x×]\s*\d+(?:\.\d+)?\s*(ml|l|ltr|g|kg|oz)\b", cleaned, flags=re.IGNORECASE
    )
    if cap_pack:
        qty = float(cap_pack.group(1))
        if 1 < qty < 500:
            return PackParse(units=qty, evidence=cap_pack.group(0), used_dimension_shield=used_dimension_shield)

    patterns: list[tuple[str, str]] = [
        (r"\bpack of (\d+)\b", "pack of"),
        (r"\bset of (\d+)\b", "set of"),
        (r"\b(\d+)\s*pack\b", "pack"),
        (r"\b(\d+)\s*pk\b", "pk"),
        (r"\b(\d+)\s*pcs\b", "pcs"),
        (r"\b(\d+)\s*pieces?\b", "pieces"),
        (r"\b(\d+)\s*pairs?\b", "pairs"),
        (r"\b(\d+)\s*rolls?\b", "rolls"),
        (r"\b(\d+)\s*bags?\b", "bags"),
        (r"\b(\d+)\s*count\b", "count"),
        (r"^\s*(\d+)\s*[x×]\b", "Nx"),
    ]
    for pat, _label in patterns:
        m = re.search(pat, cleaned, flags=re.IGNORECASE)
        if not m:
            continue
        qty = float(m.group(1))
        if 1 < qty < 500:
            return PackParse(units=qty, evidence=m.group(0), used_dimension_shield=used_dimension_shield)

    return PackParse(units=1.0, evidence=None, used_dimension_shield=used_dimension_shield)


def _tokenize(title_raw: Any) -> list[str]:
    title = _normalize_title(title_raw).lower()
    # keep alnum words; split punctuation
    tokens = re.findall(r"[a-z0-9]+", title)
    out: list[str] = []
    for t in tokens:
        if t in STOPWORDS:
            continue
        if t in MEASUREMENT_UNITS:
            continue
        if len(t) <= 2:
            continue
        out.append(t)
    return out


def extract_brand_anchor(supplier_title_raw: Any, amazon_title_raw: Any) -> str | None:
    supplier = _normalize_title(supplier_title_raw)
    amazon = _normalize_title(amazon_title_raw).lower()
    if not supplier or not amazon:
        return None

    supplier_tokens = re.findall(r"[A-Za-z0-9]+", supplier)
    candidates: list[str] = []
    for tok in supplier_tokens[:6]:
        t = tok.lower()
        if t in STOPWORDS or t in COLOR_WORDS or len(t) <= 2:
            continue
        if t.isdigit():
            continue
        candidates.append(t)

    # also consider any ALLCAPS word as potential brand in supplier data
    for tok in supplier_tokens:
        if tok.isupper() and len(tok) >= 3 and tok.lower() not in STOPWORDS:
            candidates.append(tok.lower())

    for cand in candidates:
        if cand in amazon:
            return cand
    return None


def pick_shared_tokens(supplier_title_raw: Any, amazon_title_raw: Any, max_tokens: int = 3) -> list[str]:
    sup = set(_tokenize(supplier_title_raw))
    amz = set(_tokenize(amazon_title_raw))
    shared = list(sup & amz)
    # prefer longer, more distinctive tokens
    shared.sort(key=lambda x: (-len(x), x))
    return shared[:max_tokens]


def title_similarity(a: Any, b: Any) -> float:
    sa = _normalize_title(a).lower()
    sb = _normalize_title(b).lower()
    if not sa or not sb:
        return 0.0
    # token-based Jaccard (fast + stable)
    ta = set(_tokenize(sa))
    tb = set(_tokenize(sb))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def extract_primary_capacity(title_raw: Any) -> tuple[float, str] | None:
    title = _normalize_title(title_raw).lower()
    if not title:
        return None

    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(ml|l|ltr)\b", title, flags=re.IGNORECASE)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit in {"l", "ltr"}:
            return val * 1000.0, "ml"
        return val, "ml"

    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(g|kg)\b", title, flags=re.IGNORECASE)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit == "kg":
            return val * 1000.0, "g"
        return val, "g"

    return None


def capacity_relation(
    supplier_title_raw: Any, amazon_title_raw: Any, *, is_exact_ean_strict: bool
) -> tuple[str, str | None]:
    sup = extract_primary_capacity(supplier_title_raw)
    amz = extract_primary_capacity(amazon_title_raw)
    if not sup or not amz:
        return "unknown", None
    if sup[1] != amz[1]:
        return "unknown", None

    sup_val, unit = sup
    amz_val, _ = amz
    if sup_val <= 0 or amz_val <= 0:
        return "unknown", None
    diff = abs(sup_val - amz_val) / max(sup_val, amz_val)

    if diff <= 0.15:
        return "match", f"Capacity within 15% ({sup_val:g}{unit} vs {amz_val:g}{unit})"
    if diff <= 0.30:
        return "needs_verification", f"Capacity 16–30% variance ({sup_val:g}{unit} vs {amz_val:g}{unit})"

    # >30% is a clear variant mismatch, except exact-EAN rows are treated as listing-title inconsistency risk
    if is_exact_ean_strict:
        return "needs_verification", f"Exact EAN but capacity differs >30% ({sup_val:g}{unit} vs {amz_val:g}{unit})"
    return "mismatch", f"Capacity differs >30% ({sup_val:g}{unit} vs {amz_val:g}{unit})"


def detect_color_mismatch(supplier_title_raw: Any, amazon_title_raw: Any) -> bool:
    sup_title = _normalize_title(supplier_title_raw).lower()
    amz_title = _normalize_title(amazon_title_raw).lower()
    if not sup_title or not amz_title:
        return False

    for phrase in BRAND_COLOR_SHIELD_PHRASES:
        if phrase in sup_title or phrase in amz_title:
            return False

    sup_colors = {c for c in COLOR_WORDS if re.search(rf"\b{re.escape(c)}\b", sup_title)}
    amz_colors = {c for c in COLOR_WORDS if re.search(rf"\b{re.escape(c)}\b", amz_title)}
    if not sup_colors or not amz_colors:
        return False
    return sup_colors.isdisjoint(amz_colors)


def ip_risk_brand(title_raw: Any) -> str | None:
    title = _normalize_title(title_raw).lower()
    if not title:
        return None
    for brand in sorted(LUXURY_IP_BRANDS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(brand)}\b", title):
            return brand
    return None


def compute_required_supplier_units(supplier_units: float, amazon_units: float) -> int | None:
    if supplier_units <= 0 or amazon_units <= 0:
        return None
    if amazon_units <= supplier_units:
        return 1
    ratio = amazon_units / supplier_units
    if abs(ratio - round(ratio)) <= 0.01:
        return int(round(ratio))
    # ambiguous ratio (could be dimensions or messy title); do not guess
    return None


def format_money(x: float) -> str:
    return f"£{x:.2f}"


def format_roi(roi_raw: Any) -> str:
    try:
        roi = float(roi_raw)
    except Exception:
        return "-"
    return f"{roi * 100:.1f}%"


def render_fixed_width_table(rows: list[dict[str, str]]) -> str:
    cols = EXPECTED_TABLE_COLUMNS
    widths: dict[str, int] = {c: len(c) for c in cols}
    for r in rows:
        for c in cols:
            widths[c] = max(widths[c], len(r.get(c, "")))

    def _row(values: Iterable[str]) -> str:
        parts = []
        for c, v in zip(cols, values, strict=True):
            parts.append(f" {v:<{widths[c]}} ")
        return "|" + "|".join(parts) + "|"

    header = _row(cols)
    sep = "|" + "|".join(f" {'-' * widths[c]} " for c in cols) + "|"
    body = "\n".join(_row(r.get(c, "") for c in cols) for r in rows)
    return "\n".join([header, sep, body]) if body else "\n".join([header, sep])


def infer_supplier_from_urls(df: pd.DataFrame) -> str:
    if "SupplierURL" not in df.columns:
        return "-"
    hosts: list[str] = []
    for x in df["SupplierURL"].dropna().astype(str).head(2000):
        try:
            host = urlparse(x).netloc.lower()
        except Exception:
            continue
        if host:
            hosts.append(host)
    if not hosts:
        return "-"
    return max(set(hosts), key=hosts.count)


def build_row_output(
    *,
    verdict: str,
    confidence: int,
    row_id: int,
    supplier_title: str,
    amazon_title: str,
    supplier_ean_display: str,
    amazon_ean_display: str,
    asin: str,
    supplier_price: float,
    selling_price: float,
    net_profit: float,
    roi_raw: Any,
    sales: float,
    pack_verdict: str,
    adjusted_profit: float,
    key_match_evidence: str,
    filter_reason: str,
) -> dict[str, str]:
    return {
        "Verdict": verdict,
        "Confidence": str(confidence),
        "SupplierTitle": f"Row {row_id}: {supplier_title}",
        "AmazonTitle": amazon_title,
        "Supplier EAN": supplier_ean_display or "-",
        "Amazon EAN": amazon_ean_display or "-",
        "ASIN": asin or "-",
        "SupplierPrice": format_money(supplier_price),
        "SellingPrice": format_money(selling_price),
        "NetProfit": format_money(net_profit),
        "ROI": format_roi(roi_raw),
        "Sales": str(int(sales)) if sales.is_integer() else f"{sales:g}",
        "Pack Verdict": pack_verdict,
        "Adjusted Profit": format_money(adjusted_profit),
        "Key Match Evidence": key_match_evidence,
        "Filter Reason": filter_reason,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        required=True,
        help="Path to Excel or CSV financial report",
    )
    ap.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write PHASEA_MANUAL_REPORT_YYYYMMDD.md",
    )
    args = ap.parse_args()

    input_path = args.input
    output_dir = args.output_dir

    if input_path.lower().endswith(".csv"):
        df = pd.read_csv(input_path, dtype=str)
    else:
        df = pd.read_excel(input_path, sheet_name=0, dtype=str)

    df = df.fillna("")
    df["RowID"] = range(1, len(df) + 1)

    supplier_name = infer_supplier_from_urls(df)

    out_verified_reco: list[dict[str, str]] = []
    out_verified_filtered: list[dict[str, str]] = []
    out_high_reco: list[dict[str, str]] = []
    out_high_filtered: list[dict[str, str]] = []
    out_needs_verif: list[dict[str, str]] = []

    sort_keys: dict[int, tuple[float, float, float]] = {}

    for _idx, r in df.iterrows():
        row_id = int(r["RowID"])
        supplier_title = _normalize_title(r.get("SupplierTitle", ""))
        amazon_title = _normalize_title(r.get("AmazonTitle", ""))
        asin = _as_str(r.get("ASIN", "")) or "-"

        supplier_price = parse_money_gbp(r.get("SupplierPrice_incVAT", ""))
        selling_price = parse_money_gbp(r.get("SellingPrice_incVAT", ""))
        net_profit = parse_money_gbp(r.get("NetProfit", ""))
        sales = parse_sales(r.get("sales_numeric", "")) if "sales_numeric" in df.columns else parse_sales(
            r.get("bought_in_past_month", "")
        )
        roi_raw = r.get("ROI", "")

        sup_digits = clean_to_digits(r.get("EAN", ""))
        amz_digits = clean_to_digits(r.get("EAN_OnPage", ""))
        sup_norm = normalize_gtin(sup_digits) if sup_digits else ""
        amz_norm = normalize_gtin(amz_digits) if amz_digits else ""
        sup_strict = is_strict_valid_barcode(sup_norm) if sup_norm else False
        amz_strict = is_strict_valid_barcode(amz_norm) if amz_norm else False
        is_exact_ean_strict = bool(sup_strict and amz_strict and sup_norm == amz_norm)

        supplier_ean_display = sup_norm if sup_strict else "-"
        amazon_ean_display = amz_norm if amz_strict else "-"

        sup_pack = extract_pack_units(supplier_title)
        amz_pack = extract_pack_units(amazon_title)
        rsu = compute_required_supplier_units(sup_pack.units, amz_pack.units)
        if rsu is None and (sup_pack.used_dimension_shield or amz_pack.used_dimension_shield):
            rsu = 1

        adjusted_profit = net_profit
        if rsu and rsu > 1:
            adjusted_profit = net_profit - (supplier_price * (rsu - 1))

        pack_bits: list[str] = []
        if rsu == 1:
            pack_bits.append("1:1 Match")
            if sup_pack.used_dimension_shield or amz_pack.used_dimension_shield:
                pack_bits[-1] += " (dimensions/measurements ignored)"
        elif rsu and rsu > 1:
            pack_bits.append(f"Amazon appears larger pack; RSU={rsu}")
            if amz_pack.evidence:
                pack_bits.append(f"Amazon evidence: {amz_pack.evidence}")
            if sup_pack.evidence:
                pack_bits.append(f"Supplier evidence: {sup_pack.evidence}")
        else:
            pack_bits.append("Pack unclear from titles; do not assume")
        pack_verdict = "; ".join(pack_bits)

        cap_rel, cap_note = capacity_relation(
            supplier_title, amazon_title, is_exact_ean_strict=is_exact_ean_strict
        )

        brand_anchor = extract_brand_anchor(supplier_title, amazon_title)
        shared = pick_shared_tokens(supplier_title, amazon_title, max_tokens=3)
        product_token_match = len([t for t in shared if (brand_anchor is None or t != brand_anchor)]) >= 1
        brand_match = brand_anchor is not None
        strong_title = title_similarity(supplier_title, amazon_title)
        confirmed_non_ean = bool(brand_match and product_token_match and strong_title >= 0.25)
        confirmed_match = bool(is_exact_ean_strict or confirmed_non_ean)

        if detect_color_mismatch(supplier_title, amazon_title):
            color_flag = True
        else:
            color_flag = False

        ip_brand = ip_risk_brand(supplier_title) or ip_risk_brand(amazon_title)

        profit_gate_ok = net_profit > 0 and adjusted_profit > 0
        sellable_gate_ok = sales > 0

        # evidence is row-grounded: exact EAN or shared tokens present in both titles
        if is_exact_ean_strict:
            key_evidence = "Exact EAN match"
        else:
            if brand_anchor and shared:
                key_evidence = "Shared tokens: " + ", ".join(shared)
            elif shared:
                key_evidence = "Shared tokens: " + ", ".join(shared)
            else:
                key_evidence = "-"

        # Confidence
        if is_exact_ean_strict:
            confidence = 95
        else:
            base = 55 + int(min(40, strong_title * 80))
            if confirmed_non_ean:
                base = max(base, 82)
            confidence = max(0, min(94, base))

        # Categorization
        filter_reason = "-"
        verdict = "IGNORE"

        if is_exact_ean_strict:
            if adjusted_profit <= 0 or net_profit <= 0:
                verdict = "FILTERED OUT"
                filter_reason = (
                    f"Exact EAN match but unprofitable after pack sanity (AdjProfit {format_money(adjusted_profit)})"
                )
            elif not sellable_gate_ok:
                verdict = "NEEDS VERIFICATION"
                filter_reason = "Exact EAN match but Sales=0 (verify demand signal)"
            elif cap_rel == "mismatch":
                verdict = "NEEDS VERIFICATION"
                filter_reason = cap_note or "Exact EAN match but capacity mismatch"
            elif rsu and rsu > 1:
                verdict = "NEEDS VERIFICATION"
                filter_reason = "Exact EAN match but titles suggest multipack; confirm pack size"
            else:
                verdict = "VERIFIED"
        else:
            if not confirmed_match:
                # Skip weak/likely-wrong matches entirely (avoid giant tables of obvious mismatches)
                continue

            if cap_rel == "mismatch":
                verdict = "FILTERED OUT"
                filter_reason = cap_note or "Capacity mismatch >30% (different SKU)"
            elif adjusted_profit <= 0 or net_profit <= 0:
                verdict = "FILTERED OUT"
                if rsu and rsu > 1:
                    filter_reason = (
                        f"Requires {rsu} units; adjusted profit is {format_money(adjusted_profit)} (<=0)"
                    )
                else:
                    filter_reason = f"Unprofitable (AdjProfit {format_money(adjusted_profit)})"
            else:
                if color_flag:
                    verdict = "NEEDS VERIFICATION"
                    filter_reason = "Possible color/variant mismatch; confirm variant"
                elif cap_rel == "needs_verification":
                    verdict = "NEEDS VERIFICATION"
                    filter_reason = cap_note or "Minor capacity variance; confirm same variant"
                elif rsu is None:
                    verdict = "NEEDS VERIFICATION"
                    filter_reason = "Pack unclear from titles; confirm pack count"
                elif brand_match and product_token_match:
                    verdict = "HIGHLY LIKELY"
                else:
                    verdict = "NEEDS VERIFICATION"
                    filter_reason = "Missing brand or product-type anchor; confirm packaging/title details"

        # Needs-verification selectivity gates
        if verdict == "NEEDS VERIFICATION":
            try:
                roi = float(roi_raw)
            except Exception:
                roi = 0.0
            if not ((net_profit > 0.50) and (roi > 0.15) and (adjusted_profit > 0)):
                continue
            if ip_brand:
                filter_reason = f"{filter_reason}; IP risk brand present: {ip_brand}"

        if verdict == "VERIFIED":
            if not (profit_gate_ok and sellable_gate_ok):
                verdict = "FILTERED OUT"
                filter_reason = "Failed profit/sales gate"

        if verdict == "HIGHLY LIKELY":
            if not (profit_gate_ok and sellable_gate_ok):
                verdict = "FILTERED OUT"
                filter_reason = "Failed profit/sales gate"

        out = build_row_output(
            verdict=verdict,
            confidence=confidence,
            row_id=row_id,
            supplier_title=supplier_title,
            amazon_title=amazon_title,
            supplier_ean_display=supplier_ean_display,
            amazon_ean_display=amazon_ean_display,
            asin=asin,
            supplier_price=supplier_price,
            selling_price=selling_price,
            net_profit=net_profit,
            roi_raw=roi_raw,
            sales=sales,
            pack_verdict=pack_verdict,
            adjusted_profit=adjusted_profit,
            key_match_evidence=key_evidence,
            filter_reason=filter_reason,
        )

        # for sorting: (confidence, sales, adjusted_profit)
        sort_keys[row_id] = (float(confidence), float(sales), float(adjusted_profit))

        if is_exact_ean_strict and verdict == "VERIFIED":
            out_verified_reco.append(out)
        elif is_exact_ean_strict and verdict == "FILTERED OUT":
            out_verified_filtered.append(out)
        elif (not is_exact_ean_strict) and verdict == "HIGHLY LIKELY":
            out_high_reco.append(out)
        elif (not is_exact_ean_strict) and verdict == "FILTERED OUT":
            out_high_filtered.append(out)
        elif verdict == "NEEDS VERIFICATION":
            out_needs_verif.append(out)

    def _sort(rows: list[dict[str, str]], key: str) -> list[dict[str, str]]:
        if key == "verified":
            return sorted(
                rows,
                key=lambda rr: (-float(rr["Sales"]), -parse_money_gbp(rr["Adjusted Profit"]), -int(rr["Confidence"])),
            )
        if key == "high":
            return sorted(rows, key=lambda rr: (-int(rr["Confidence"]), -float(rr["Sales"])))
        if key == "needs":
            return sorted(rows, key=lambda rr: (-int(rr["Confidence"]), -float(rr["Sales"])))
        if key == "filtered":
            return sorted(rows, key=lambda rr: (-int(rr["Confidence"]), float(rr["Adjusted Profit"].replace("£", ""))))
        return rows

    out_verified_reco = _sort(out_verified_reco, "verified")
    out_verified_filtered = _sort(out_verified_filtered, "filtered")
    out_high_reco = _sort(out_high_reco, "high")
    out_high_filtered = _sort(out_high_filtered, "filtered")
    out_needs_verif = _sort(out_needs_verif, "needs")

    tz = ZoneInfo("Asia/Dubai")
    now = datetime.now(tz=tz)
    date_str = now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y%m%d")
    out_path = f"{output_dir.rstrip('\\\\/')}/PHASEA_MANUAL_REPORT_{stamp}.md"

    n_total = len(df)
    counts = {
        "VERIFIED_RECO": len(out_verified_reco),
        "VERIFIED_FILTERED": len(out_verified_filtered),
        "HIGH_RECO": len(out_high_reco),
        "HIGH_FILTERED": len(out_high_filtered),
        "NEEDS_VERIFICATION": len(out_needs_verif),
    }
    n_categorized = sum(counts.values())

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT")
    lines.append("")
    lines.append(f"**Generated:** {date_str}")
    lines.append(f"**Input File:** {input_path}")
    lines.append(f"**Supplier:** {supplier_name}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append(f"- VERIFIED — RECOMMENDED: {counts['VERIFIED_RECO']}")
    lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {counts['VERIFIED_FILTERED']}")
    lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {counts['HIGH_RECO']}")
    lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {counts['HIGH_FILTERED']}")
    lines.append(f"- NEEDS VERIFICATION: {counts['NEEDS_VERIFICATION']}")
    lines.append(f"- TOTAL ANALYZED: {n_total}")
    lines.append("")
    lines.append(
        "This report enforces: strict EAN validity + exact match for VERIFIED, Sales>0/Profit>0 for recommendations, "
        "dimension/measurement shield, v4.1 nested pack handling, and capacity tolerance."
    )
    lines.append("")

    def _section(title: str, rows: list[dict[str, str]]) -> None:
        lines.append(f"## {title} (count={len(rows)})")
        lines.append("")
        lines.append("```text")
        lines.append(render_fixed_width_table(rows))
        lines.append("```")
        lines.append("")

    _section("VERIFIED — RECOMMENDED", out_verified_reco)
    _section("VERIFIED — FILTERED OUT / EXCLUDED", out_verified_filtered)
    _section("HIGHLY LIKELY — RECOMMENDED", out_high_reco)
    _section("HIGHLY LIKELY — FILTERED OUT / EXCLUDED", out_high_filtered)
    _section("NEEDS VERIFICATION", out_needs_verif)

    lines.append("## Reconciliation")
    lines.append(f"- Total rows in input: {n_total}")
    lines.append(f"- Rows analyzed and categorized: {n_categorized}")
    lines.append(
        f"- Breakdown check: {(counts['VERIFIED_RECO'] + counts['VERIFIED_FILTERED'])}"
        f" + {(counts['HIGH_RECO'] + counts['HIGH_FILTERED'])}"
        f" + {counts['NEEDS_VERIFICATION']} = {n_categorized}"
    )
    lines.append("")

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

