from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
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

GENERIC_TOKENS = {
    "stainless",
    "steel",
    "chrome",
    "metal",
    "plastic",
    "glass",
    "white",
    "black",
    "grey",
    "gray",
    "red",
    "blue",
    "green",
    "orange",
    "pink",
    "silver",
    "gold",
    "large",
    "small",
    "medium",
    "pack",
    "set",
    "holder",
    "brush",
    "toilet",
    "bath",
    "door",
    "mat",
    "world",
    "scented",
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
    "litre",
    "litres",
    "g",
    "kg",
    "oz",
    "w",
}


DIMENSION_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?(?:\s*[x×]\s*\d+(?:\.\d+)?)?\s*(?:cm|mm|inch|in|m|ft)\b",
    r"\b\d{2,4}\s*[x×]\s*\d{2,4}\s*(?:cm|mm)\b",
    r"\b\d+(?:\.\d+)?\s*(?:cm|mm|inch|in|m|ft|ml|l|ltr|litre|litres|g|kg|oz|w)\b",
]


MULTIWORD_BRANDS = {
    "mason cash",
    "chef aid",
    "blue canyon",
    "pan aroma",
    "house mate",
    "big cheese",
    "the big cheese",
    "world of pets",
    "bright & homely",
    "bright and homely",
    "extra select",
    "special occasions",
}

NON_BRAND_FIRST_TOKENS = {
    "salt",
    "pepper",
    "shakers",
    "door",
    "mat",
    "rubber",
    "duck",
    "family",
    "basket",
    "hanger",
    "hangers",
}


@dataclass(frozen=True)
class PackParse:
    total: int
    evidence: str | None
    confidence: str  # "explicit" | "assumed" | "unclear"


def _as_str(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x).strip()


def sanitize_cell_text(s: str) -> str:
    return s.replace("|", "¦").replace("\n", " ").replace("\r", " ").strip()


def parse_float(x: Any) -> float:
    s = _as_str(x)
    if not s:
        return 0.0
    s = s.replace("£", "").replace("Ł", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def format_money(x: float) -> str:
    return f"£{x:.2f}"


def format_roi(roi_raw: Any) -> str:
    try:
        roi = float(roi_raw)
    except Exception:
        return "-"
    return f"{roi * 100:.1f}%"


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


def strip_dimensions(title: str) -> str:
    lowered = title.lower()
    cleaned = lowered
    for pat in DIMENSION_PATTERNS:
        cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def parse_pack_total(title_raw: Any, *, side: str) -> PackParse:
    title = _normalize_title(title_raw)
    if not title:
        return PackParse(total=1, evidence=None, confidence="assumed")

    lowered = title.lower()

    # 6 * 200ml / 3 x 500ml => pack of 6/3 (do NOT multiply into capacity)
    cap_pack = re.search(
        r"\b(\d+)\s*[*x×]\s*\d+(?:\.\d+)?\s*(ml|l|ltr|litre|litres|g|kg|oz)\b",
        lowered,
        flags=re.IGNORECASE,
    )
    if cap_pack:
        n = int(cap_pack.group(1))
        if 1 < n < 500:
            return PackParse(total=n, evidence=cap_pack.group(0), confidence="explicit")

    cleaned = strip_dimensions(title)

    # v4.1 nested pack pattern: (4 x 50) => 200 TOTAL
    nested = re.search(r"\((\d+)\s*[x×]\s*(\d+)\s*\)", cleaned, flags=re.IGNORECASE)
    if nested:
        outer = int(nested.group(1))
        inner = int(nested.group(2))
        if 1 < outer < 500 and 1 < inner < 500:
            return PackParse(total=outer * inner, evidence=nested.group(0), confidence="explicit")

    # PK5 / PK 5
    pk = re.search(r"\bpk\s*([0-9]{1,3})\b", cleaned, flags=re.IGNORECASE)
    if pk:
        n = int(pk.group(1))
        if 1 < n < 500:
            return PackParse(total=n, evidence=pk.group(0), confidence="explicit")

    patterns: list[str] = [
        r"\bpack of\s+(\d+)\b",
        r"\bset of\s+(\d+)\b",
        r"\b(\d+)\s*[-]?\s*pack\b",
        r"\b(\d+)\s*[-]?\s*pk\b",
        r"\b(\d+)\s*[-]?\s*pcs\b",
        r"\b(\d+)\s*[-]?\s*pce\b",
        r"\b(\d+)\s*[-]?\s*pces\b",
        r"\b(\d+)\s*[-]?\s*pieces?\b",
        r"\b(\d+)\s*[-]?\s*piece\b",
        r"\b(\d+)\s*[-]?\s*pc\b",
        r"\b(\d+)\s*doyleys?\b",
        r"\b(\d+)\s*bottles?\b",
        r"\b(\d+)\s*cans?\b",
        r"\b(\d+)\s*trays?\b",
        r"\b(\d+)\s*tea\s*lights?\b",
        r"\b(\d+)\s*tealights?\b",
        r"\b(\d+)\s*count\b",
    ]
    for pat in patterns:
        m = re.search(pat, cleaned, flags=re.IGNORECASE)
        if m:
            n = int(m.group(1))
            if 1 < n < 500:
                return PackParse(total=n, evidence=m.group(0), confidence="explicit")

    # Leading "3 x ..."
    lead_x = re.search(r"^\s*(\d+)\s*[x×]\b", cleaned, flags=re.IGNORECASE)
    if lead_x:
        n = int(lead_x.group(1))
        if 1 < n < 500:
            return PackParse(total=n, evidence=lead_x.group(0), confidence="explicit")

    # Trailing "... x 100" common listing pattern
    tail_x = re.search(r"\b[x×]\s*(\d{1,3})\b", cleaned, flags=re.IGNORECASE)
    if tail_x:
        n = int(tail_x.group(1))
        if 1 < n < 500:
            return PackParse(total=n, evidence=tail_x.group(0), confidence="explicit")

    # Amazon-only heuristic: leading count like "50 Non Slip Velvet Hangers ..." implies pack/count.
    if side == "amazon":
        tokens = re.findall(r"[a-z0-9]+", cleaned.lower())
        if tokens and tokens[0].isdigit():
            n = int(tokens[0])
            if 1 < n < 500:
                countable_nouns = {
                    "hangers",
                    "pcs",
                    "pieces",
                    "bags",
                    "bottles",
                    "cans",
                    "trays",
                    "pads",
                    "glasses",
                    "clips",
                    "lights",
                    "tealights",
                    "tea",
                }
                window = set(tokens[1:8])
                if window & countable_nouns:
                    return PackParse(total=n, evidence=f"leading {n}", confidence="explicit")

    # If Amazon side mentions pack-ish words but we didn't parse a number, flag unclear
    if side == "amazon" and re.search(r"\b(pack|set|pcs|pce|pieces|bottles|cans)\b", cleaned, flags=re.IGNORECASE):
        return PackParse(total=1, evidence=None, confidence="unclear")

    # "double pack" / "triple pack"
    if re.search(r"\bdouble\s+pack\b", cleaned, flags=re.IGNORECASE):
        return PackParse(total=2, evidence="double pack", confidence="explicit")
    if re.search(r"\btriple\s+pack\b", cleaned, flags=re.IGNORECASE):
        return PackParse(total=3, evidence="triple pack", confidence="explicit")

    return PackParse(total=1, evidence=None, confidence="assumed")


def required_supplier_units(supplier_total: int, amazon_total: int) -> int | None:
    if supplier_total <= 0 or amazon_total <= 0:
        return None
    if amazon_total <= supplier_total:
        return 1
    ratio = amazon_total / supplier_total
    if abs(ratio - round(ratio)) <= 0.01:
        return int(round(ratio))
    return None


def extract_brand(supplier_title_raw: Any) -> str | None:
    title = _normalize_title(supplier_title_raw)
    if not title:
        return None
    lowered = title.lower()
    for b in sorted(MULTIWORD_BRANDS, key=len, reverse=True):
        if lowered.startswith(b):
            return b

    tokens = re.findall(r"[A-Za-z0-9&]+", title)
    if not tokens:
        return None
    # Brand is usually first token. Keep numeric brands like "151". Avoid guessing brands for non-ALLCAPS titles.
    first_raw = tokens[0]
    first = first_raw.lower()
    if first in NON_BRAND_FIRST_TOKENS:
        return None
    if first_raw.isdigit():
        return first
    if first_raw.isupper() and len(first_raw) >= 3:
        return first
    return None


def brand_in_amazon(brand: str | None, amazon_title_raw: Any) -> bool:
    if not brand:
        return False
    amz = _normalize_title(amazon_title_raw).lower()
    if not amz:
        return False
    # ignore spaces/punct for robust matching (AIRWICK vs AIR WICK)
    b_norm = re.sub(r"[^a-z0-9]+", "", brand.lower())
    a_norm = re.sub(r"[^a-z0-9]+", "", amz)
    return b_norm and b_norm in a_norm


def shared_tokens(a: Any, b: Any, *, limit: int = 4) -> list[str]:
    ta = {t for t in re.findall(r"[a-z0-9]+", _normalize_title(a).lower()) if t not in STOPWORDS}
    tb = {t for t in re.findall(r"[a-z0-9]+", _normalize_title(b).lower()) if t not in STOPWORDS}
    shared = [t for t in (ta & tb) if len(t) >= 4 and t not in MEASUREMENT_UNITS]
    shared.sort(key=lambda x: (-len(x), x))
    return shared[:limit]


def has_distinctive_shared(shared: list[str]) -> bool:
    return any(t not in GENERIC_TOKENS for t in shared)


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


def build_row(
    *,
    verdict: str,
    confidence: int,
    row_id: int,
    supplier_title: str,
    amazon_title: str,
    supplier_ean_disp: str,
    amazon_ean_disp: str,
    asin: str,
    supplier_price: float,
    selling_price: float,
    net_profit: float,
    roi_raw: Any,
    sales: float,
    pack_verdict: str,
    adjusted_profit: float,
    key_evidence: str,
    filter_reason: str,
) -> dict[str, str]:
    return {
        "Verdict": verdict,
        "Confidence": str(confidence),
        "SupplierTitle": sanitize_cell_text(f"Row {row_id}: {supplier_title}"),
        "AmazonTitle": sanitize_cell_text(amazon_title),
        "Supplier EAN": supplier_ean_disp or "-",
        "Amazon EAN": amazon_ean_disp or "-",
        "ASIN": asin or "-",
        "SupplierPrice": format_money(supplier_price),
        "SellingPrice": format_money(selling_price),
        "NetProfit": format_money(net_profit),
        "ROI": format_roi(roi_raw),
        "Sales": str(int(sales)) if float(sales).is_integer() else f"{sales:g}",
        "Pack Verdict": sanitize_cell_text(pack_verdict),
        "Adjusted Profit": format_money(adjusted_profit),
        "Key Match Evidence": sanitize_cell_text(key_evidence),
        "Filter Reason": sanitize_cell_text(filter_reason),
    }


def parse_row_ids_from_codex_report(path: Path) -> list[int]:
    text = path.read_text(encoding="utf-8")
    row_ids: list[int] = []
    for m in re.finditer(r"\bRow\s+(\d+):", text):
        row_ids.append(int(m.group(1)))
    return sorted(set(row_ids))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-xlsx", required=True)
    ap.add_argument("--codex-report-md", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    input_xlsx = Path(args.input_xlsx)
    codex_report_md = Path(args.codex_report_md)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(input_xlsx, sheet_name=0, dtype=object).fillna("")
    df["RowID"] = range(1, len(df) + 1)
    df = df.set_index("RowID", drop=False)

    wanted_row_ids = parse_row_ids_from_codex_report(codex_report_md)

    verified_reco: list[dict[str, str]] = []
    verified_filtered: list[dict[str, str]] = []
    high_reco: list[dict[str, str]] = []
    high_filtered: list[dict[str, str]] = []
    needs_verif: list[dict[str, str]] = []

    for row_id in wanted_row_ids:
        if row_id not in df.index:
            continue
        r = df.loc[row_id]

        supplier_title = _normalize_title(r.get("SupplierTitle", ""))
        amazon_title = _normalize_title(r.get("AmazonTitle", ""))
        asin = _as_str(r.get("ASIN", "")) or "-"

        supplier_price = parse_float(r.get("SupplierPrice_incVAT", ""))
        selling_price = parse_float(r.get("SellingPrice_incVAT", ""))
        net_profit = parse_float(r.get("NetProfit", ""))
        roi_raw = r.get("ROI", "")
        sales = parse_float(r.get("sales_numeric", "")) if "sales_numeric" in r.index else parse_float(
            r.get("bought_in_past_month", "")
        )

        sup_digits = clean_to_digits(r.get("EAN", ""))
        amz_digits = clean_to_digits(r.get("EAN_OnPage", ""))
        sup_norm = normalize_gtin(sup_digits) if sup_digits else ""
        amz_norm = normalize_gtin(amz_digits) if amz_digits else ""
        sup_ok = is_strict_valid_barcode(sup_norm) if sup_norm else False
        amz_ok = is_strict_valid_barcode(amz_norm) if amz_norm else False
        exact_ean = bool(sup_ok and amz_ok and sup_norm == amz_norm)

        supplier_ean_disp = sup_norm if sup_ok else "-"
        amazon_ean_disp = amz_norm if amz_ok else "-"

        sup_pack = parse_pack_total(supplier_title, side="supplier")
        amz_pack = parse_pack_total(amazon_title, side="amazon")
        rsu = required_supplier_units(sup_pack.total, amz_pack.total)
        adjusted_profit = net_profit
        if rsu and rsu > 1:
            adjusted_profit = net_profit - (supplier_price * (rsu - 1))

        pack_bits: list[str] = []
        if rsu is None:
            pack_bits.append("Pack unclear; verify unit count")
        elif rsu == 1:
            if sup_pack.total == amz_pack.total and (sup_pack.total != 1 or amz_pack.total != 1):
                pack_bits.append(f"1:1 Match ({sup_pack.total}:{amz_pack.total})")
            else:
                pack_bits.append("1:1 Match")
        else:
            pack_bits.append(f"Amazon pack={amz_pack.total}; Supplier pack={sup_pack.total}; RSU={rsu}")
            if amz_pack.evidence:
                pack_bits.append(f"Amazon evidence: {amz_pack.evidence}")
            if sup_pack.evidence:
                pack_bits.append(f"Supplier evidence: {sup_pack.evidence}")
        pack_verdict = "; ".join(pack_bits)

        brand = extract_brand(supplier_title)
        brand_match = brand_in_amazon(brand, amazon_title)
        shared = shared_tokens(supplier_title, amazon_title, limit=4)
        distinctive = has_distinctive_shared(shared)

        recommended_gate = sales > 0 and net_profit > 0 and adjusted_profit > 0

        # Evidence must be row-grounded
        if exact_ean:
            key_evidence = "Exact EAN match"
        else:
            key_evidence = "Shared tokens: " + ", ".join(shared) if shared else "-"

        # Decide verdict
        verdict: str
        filter_reason = "-"
        confidence: int

        if exact_ean:
            confidence = 95
            if rsu and rsu > 1 and adjusted_profit <= 0:
                verdict = "FILTERED OUT"
                filter_reason = (
                    f"Exact EAN match but Amazon appears larger pack; RSU={rsu}; "
                    f"AdjProfit={format_money(adjusted_profit)} (<=0)"
                )
                verified_filtered.append(
                    build_row(
                        verdict=verdict,
                        confidence=confidence,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi_raw=roi_raw,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=adjusted_profit,
                        key_evidence=key_evidence,
                        filter_reason=filter_reason,
                    )
                )
                continue

            if rsu is None and amz_pack.confidence == "explicit" and sup_pack.confidence != "explicit":
                verdict = "NEEDS VERIFICATION"
                confidence = 85
                filter_reason = "Exact EAN match but supplier pack unclear vs Amazon explicit pack; confirm supplier unit"
                needs_verif.append(
                    build_row(
                        verdict=verdict,
                        confidence=confidence,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi_raw=roi_raw,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=adjusted_profit,
                        key_evidence=key_evidence,
                        filter_reason=filter_reason,
                    )
                )
                continue

            if recommended_gate:
                verdict = "VERIFIED"
                verified_reco.append(
                    build_row(
                        verdict=verdict,
                        confidence=confidence,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi_raw=roi_raw,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=adjusted_profit,
                        key_evidence=key_evidence,
                        filter_reason="-",
                    )
                )
            else:
                verdict = "NEEDS VERIFICATION"
                confidence = 85
                filter_reason = "Exact EAN match but fails sales/profit gate; verify demand/fees"
                needs_verif.append(
                    build_row(
                        verdict=verdict,
                        confidence=confidence,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi_raw=roi_raw,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=adjusted_profit,
                        key_evidence=key_evidence,
                        filter_reason=filter_reason,
                    )
                )
            continue

        # Non-EAN rows (manual title-based)
        confidence = 55
        if brand_match and len(shared) >= 2 and distinctive:
            confidence = 90
        elif brand_match and len(shared) >= 2:
            confidence = 84
        elif len(shared) >= 4 and distinctive:
            confidence = 80
        elif len(shared) >= 3 and distinctive:
            confidence = 75
        elif len(shared) >= 2 and distinctive:
            confidence = 68

        # Manual guardrail: if supplier appears to specify a brand and it is not present in the Amazon title,
        # treat as mismatch (avoid brand/IP/false-positive traps).
        if brand and not brand_match:
            verdict = "FILTERED OUT"
            filter_reason = f"Brand mismatch: supplier '{brand}' not present in Amazon title"
            high_filtered.append(
                build_row(
                    verdict=verdict,
                    confidence=confidence,
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean_disp=supplier_ean_disp,
                    amazon_ean_disp=amazon_ean_disp,
                    asin=asin,
                    supplier_price=supplier_price,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi_raw=roi_raw,
                    sales=sales,
                    pack_verdict=pack_verdict,
                    adjusted_profit=adjusted_profit,
                    key_evidence=key_evidence,
                    filter_reason=filter_reason,
                )
            )
            continue

        if rsu and rsu > 1 and adjusted_profit <= 0:
            verdict = "FILTERED OUT"
            filter_reason = (
                f"Pack mismatch makes unprofitable; RSU={rsu}; AdjProfit={format_money(adjusted_profit)} (<=0)"
            )
            high_filtered.append(
                build_row(
                    verdict=verdict,
                    confidence=confidence,
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean_disp=supplier_ean_disp,
                    amazon_ean_disp=amazon_ean_disp,
                    asin=asin,
                    supplier_price=supplier_price,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi_raw=roi_raw,
                    sales=sales,
                    pack_verdict=pack_verdict,
                    adjusted_profit=adjusted_profit,
                    key_evidence=key_evidence,
                    filter_reason=filter_reason,
                )
            )
            continue

        if brand_match and len(shared) >= 2 and distinctive and recommended_gate and rsu != 0:
            if rsu is None or amz_pack.confidence == "unclear" or sup_pack.confidence == "unclear":
                verdict = "NEEDS VERIFICATION"
                filter_reason = "Brand/product match but pack unclear; confirm unit count on Amazon page"
                needs_verif.append(
                    build_row(
                        verdict=verdict,
                        confidence=max(confidence, 75),
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi_raw=roi_raw,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=adjusted_profit,
                        key_evidence=key_evidence,
                        filter_reason=filter_reason,
                    )
                )
            else:
                verdict = "HIGHLY LIKELY"
                high_reco.append(
                    build_row(
                        verdict=verdict,
                        confidence=confidence,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi_raw=roi_raw,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=adjusted_profit,
                        key_evidence=key_evidence,
                        filter_reason="-",
                    )
                )
            continue

        # Selective NEEDS VERIFICATION: only if upgradeable and financially worthwhile
        roi_val = parse_float(roi_raw)
        if (
            (brand_match and len(shared) >= 2 and distinctive)
            or (len(shared) >= 3 and distinctive)
        ) and adjusted_profit > 0 and net_profit > 0.5 and sales > 0:
            verdict = "NEEDS VERIFICATION"
            if brand_match:
                filter_reason = "Plausible match; confirm variant/model and (if shown) EAN on Amazon page"
            else:
                filter_reason = "Plausible product-type match but brand unclear; confirm brand/EAN on Amazon page"
            needs_verif.append(
                build_row(
                    verdict=verdict,
                    confidence=min(84, max(confidence, 68)),
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean_disp=supplier_ean_disp,
                    amazon_ean_disp=amazon_ean_disp,
                    asin=asin,
                    supplier_price=supplier_price,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi_raw=roi_raw,
                    sales=sales,
                    pack_verdict=pack_verdict,
                    adjusted_profit=adjusted_profit,
                    key_evidence=key_evidence,
                    filter_reason=filter_reason,
                )
                )
            continue

        verdict = "FILTERED OUT"
        filter_reason = "Insufficient distinctive shared evidence for safe match"
        high_filtered.append(
            build_row(
                verdict=verdict,
                confidence=confidence,
                row_id=row_id,
                supplier_title=supplier_title,
                amazon_title=amazon_title,
                supplier_ean_disp=supplier_ean_disp,
                amazon_ean_disp=amazon_ean_disp,
                asin=asin,
                supplier_price=supplier_price,
                selling_price=selling_price,
                net_profit=net_profit,
                roi_raw=roi_raw,
                sales=sales,
                pack_verdict=pack_verdict,
                adjusted_profit=adjusted_profit,
                key_evidence=key_evidence,
                filter_reason=filter_reason,
            )
        )

    # Sorting rules (guide-inspired)
    verified_reco.sort(key=lambda r: (-parse_float(r["Sales"]), -parse_float(r["Adjusted Profit"]), -int(r["Confidence"])))
    high_reco.sort(key=lambda r: (-int(r["Confidence"]), -parse_float(r["Sales"]), -parse_float(r["Adjusted Profit"])))
    needs_verif.sort(key=lambda r: (-int(r["Confidence"]), -parse_float(r["Sales"]), -parse_float(r["Adjusted Profit"])))
    verified_filtered.sort(key=lambda r: (-int(r["Confidence"]), parse_float(r["Adjusted Profit"])))
    high_filtered.sort(key=lambda r: (-int(r["Confidence"]), parse_float(r["Adjusted Profit"])))

    tz = ZoneInfo("Asia/Dubai")
    now = datetime.now(tz=tz)
    stamp = now.strftime("%Y%m%d")
    date_str = now.strftime("%Y-%m-%d")
    out_path = output_dir / f"PHASEA_MANUAL_REPORT_{stamp}_MANUAL_AUDIT.md"

    n_total = len(df)
    counts = {
        "VERIFIED_RECO": len(verified_reco),
        "VERIFIED_FILTERED": len(verified_filtered),
        "HIGH_RECO": len(high_reco),
        "HIGH_FILTERED": len(high_filtered),
        "NEEDS_VERIFICATION": len(needs_verif),
    }
    n_categorized = sum(counts.values())

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT — MANUAL AUDIT (v4.1 rules)")
    lines.append("")
    lines.append(f"**Generated:** {date_str}")
    lines.append(f"**Input File:** {str(input_xlsx)}")
    lines.append(f"**Source Report Reviewed:** {str(codex_report_md)}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append(f"- VERIFIED — RECOMMENDED: {counts['VERIFIED_RECO']}")
    lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {counts['VERIFIED_FILTERED']}")
    lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {counts['HIGH_RECO']}")
    lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {counts['HIGH_FILTERED']}")
    lines.append(f"- NEEDS VERIFICATION: {counts['NEEDS_VERIFICATION']}")
    lines.append(f"- TOTAL ANALYZED (input): {n_total}")
    lines.append(f"- TOTAL REVIEWED ROWS (from source report): {len(wanted_row_ids)}")
    lines.append("")
    lines.append(
        "Manual-audit rules applied (no browsing): strict-valid EAN + exact match for VERIFIED; "
        "dimension/measurement shield; nested pack handling `(4 x 50)=200`; "
        "pack/RSU profitability adjustment; selective NEEDS VERIFICATION."
    )
    lines.append("")

    def _section(title: str, rows: list[dict[str, str]]) -> None:
        lines.append(f"## {title} (count={len(rows)})")
        lines.append("")
        lines.append("```text")
        lines.append(render_fixed_width_table(rows))
        lines.append("```")
        lines.append("")

    _section("VERIFIED — RECOMMENDED", verified_reco)
    _section("VERIFIED — FILTERED OUT / EXCLUDED", verified_filtered)
    _section("HIGHLY LIKELY — RECOMMENDED", high_reco)
    _section("HIGHLY LIKELY — FILTERED OUT / EXCLUDED", high_filtered)
    _section("NEEDS VERIFICATION", needs_verif)

    lines.append("## Reconciliation")
    lines.append(f"- Total rows in input: {n_total}")
    lines.append(f"- Rows reviewed (rows present in source report tables): {len(wanted_row_ids)}")
    lines.append(f"- Rows output in this audited report: {n_categorized}")
    lines.append(
        f"- Breakdown check: {(counts['VERIFIED_RECO'] + counts['VERIFIED_FILTERED'])}"
        f" + {(counts['HIGH_RECO'] + counts['HIGH_FILTERED'])}"
        f" + {counts['NEEDS_VERIFICATION']} = {n_categorized}"
    )
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
