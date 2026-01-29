from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


# Preflight calibration (efghousewares.co.uk) loaded from:
# RESERACH/REPORT/part_1_jan/codexv1.1/preflight_calibration_part_1_jan_20260102.md
SUPPLIER_NAMING_CONVENTION: dict[str, Any] = {
    "explicit_units": ["pcs", "pk", "pack", "bag", "box", "capsule", "case", "each", "pair", "stick", "tablet"],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "l", "ft", "in", "m", "x"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": False,
}


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "of",
    "to",
    "in",
    "on",
    "at",
    "a",
    "an",
    "new",
    "set",
    "pack",
    "from",
    "by",
    "x",
}

MEASUREMENT_UNITS = {
    "cm",
    "mm",
    "ml",
    "l",
    "ltr",
    "litre",
    "liter",
    "kg",
    "g",
    "oz",
    "inch",
    "in",
    "ft",
    "m",
}

GENERIC_BRAND_TOKENS = {
    "THE",
    "A",
    "AN",
    "AND",
    "FOR",
    "WITH",
    "OF",
    "TO",
    "IN",
    "ON",
    "AT",
    "HOME",
    "HOUSE",
    "EASY",
    "LUXURY",
    "GIANT",
    "UNIQUE",
    "CLASSIC",
    "PREMIUM",
    "SUPER",
    "EXTRA",
    "VALUE",
    "ROUND",
    "SQUARE",
    "SMALL",
    "LARGE",
    "XL",
    "XLARGE",
    "JUMBO",
    "MINI",
    "ASSORTED",
    "FESTIVE",
    "CHRISTMAS",
    "PARTY",
    "MEMORIAL",
}

NON_BRAND_LEADING_TOKENS = {
    "BALLOON",
    "BALLOONS",
    "BANNER",
    "BANNERS",
    "BOWL",
    "BOWLS",
    "CANDLE",
    "CANDLES",
    "CARAFE",
    "GLASS",
    "HAPPY",
    "HOLDER",
    "HOLDERS",
    "JAR",
    "JARS",
    "MICROWAVE",
    "MIRROR",
    "PLATE",
    "PLATES",
    "TRAVEL",
}

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


def _safe_str(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    s = str(x).strip()
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    # Prevent breaking fixed-width markdown tables.
    s = s.replace("|", "/")
    s = re.sub(r"\s+", " ", s)
    return s


_SCINOT_RE = re.compile(r"\d+(\.\d+)?e[+-]?\d+", re.IGNORECASE)


def clean_to_digits(x: Any) -> str:
    s = _safe_str(x)
    if not s or s.lower() in {"nan", "none", "-"}:
        return ""
    if _SCINOT_RE.search(s):
        return ""
    return re.sub(r"\D", "", s)


def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])

    total = 0
    for i, d in enumerate(map(int, body[::-1]), start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check


def normalize_ean(digits: str) -> str:
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
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r"0{6,}$", normalized):
        return False
    return gtin_checksum_ok(normalized)


def format_ean(raw: Any) -> str:
    digits = normalize_ean(clean_to_digits(raw))
    return digits if is_strict_valid_barcode(digits) else "-"


def parse_money_gbp(raw: Any) -> float | None:
    s = _safe_str(raw)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        # Strip currency symbols/commas if present
        s2 = re.sub(r"[^\d.\-]", "", s)
        try:
            return float(s2)
        except ValueError:
            return None


def fmt_gbp(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "-"
    return f"£{value:.2f}"


def fmt_roi(raw: Any) -> str:
    v = parse_money_gbp(raw)
    if v is None:
        return "-"
    return f"{v*100:.1f}%"


def fmt_int(raw: Any) -> str:
    s = _safe_str(raw)
    if not s:
        return "0"
    try:
        return str(int(float(s)))
    except ValueError:
        m = re.search(r"\d+", s)
        return m.group(0) if m else "0"


_DIM_TOKEN_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(cm|mm|ml|l|ltr|litre|liter|kg|g|oz|inch|in|ft|m)\b", re.IGNORECASE
)
_DIM_X_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?(?:\s*[x×]\s*\d+(?:\.\d+)?)?\s*"
    r"(cm|mm|m|inch|in|ft)\b",
    re.IGNORECASE,
)
_CAPACITY_MULTIPACK_RE = re.compile(
    r"\b(\d{1,4})\s*[x×]\s*(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|liter|g|kg|oz)\b",
    re.IGNORECASE,
)

_PACK_OF_RE = re.compile(r"\b(pack\s*of|set\s*of)\s*(\d{1,4})\b", re.IGNORECASE)
_N_PACK_RE = re.compile(r"\b(\d{1,4})\s*[- ]?\s*pack\b", re.IGNORECASE)
_PK_PREFIX_RE = re.compile(r"\bpk\s*(\d{1,4})\b|\bpk(\d{1,4})\b", re.IGNORECASE)
_PC_SUFFIX_RE = re.compile(r"\b(\d{1,4})\s*(pcs?|pce|pc|piece|pieces)\b", re.IGNORECASE)
_EACH_RE = re.compile(r"\b(each|sold each|sold separately)\b", re.IGNORECASE)
_RANGE_SUFFIX_RE = re.compile(r"\b\d{1,4}\s*[-–]\s*\d{1,4}\b")
_DATE_CODE_RE = re.compile(r"\b\d{1,2}/\d{1,2}\b")


@dataclass(frozen=True)
class PackInfo:
    supplier_qty_inside: int | None
    amazon_pack_count: int | None
    amazon_total_items: int | None
    evidence: str


def _tokenize(title: str) -> list[str]:
    title = title.lower()
    title = re.sub(r"[^\w\s/.-]", " ", title)
    tokens = [t for t in re.split(r"\s+", title) if t]
    cleaned: list[str] = []
    for t in tokens:
        t = t.strip("()[]{}.,;:/\\-")
        if not t or len(t) < 3:
            continue
        if t.isdigit():
            continue
        if t in MEASUREMENT_UNITS:
            continue
        if t in STOPWORDS:
            continue
        cleaned.append(t)
    return cleaned


def _extract_brand_candidates(supplier_title: str) -> list[str]:
    # Supplier titles in this sheet are often ALLCAPS. Take the first 1-3 ALLCAPS tokens as brand candidates.
    raw_tokens = re.split(r"\s+", supplier_title.strip())
    tokens: list[str] = []
    for t in raw_tokens:
        t2 = t.strip("()[]{}.,;:/\\-")
        if not t2:
            continue
        if any(ch.isdigit() for ch in t2):
            break
        if len(t2) < 3:
            break
        if not t2.isupper():
            break
        tokens.append(t2)
        if len(tokens) >= 3:
            break

    cands: list[str] = []
    if tokens:
        start = 0
        if tokens[0] in GENERIC_BRAND_TOKENS or tokens[0] in NON_BRAND_LEADING_TOKENS:
            start = 1
        if start < len(tokens):
            first = tokens[start]
            if first not in GENERIC_BRAND_TOKENS and first not in NON_BRAND_LEADING_TOKENS:
                cands.append(first)
            if start + 1 < len(tokens):
                cands.append(" ".join(tokens[start : start + 2]))
        if len(tokens) >= 3 and tokens[0] == "THE":
            cands.append(" ".join(tokens[:3]))
    return cands


def _brand_match(supplier_title: str, amazon_title: str) -> str | None:
    at = amazon_title.lower()
    for cand in _extract_brand_candidates(supplier_title):
        if re.search(rf"(?<!\w){re.escape(cand.lower())}(?!\w)", at):
            return cand
    return None


def _looks_like_measurement_context(text: str) -> bool:
    if _DIM_X_RE.search(text):
        return True
    if _DIM_TOKEN_RE.search(text):
        return True
    for kw in SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"]:
        if re.search(rf"\b{re.escape(kw)}\b", text.lower()):
            return True
    return False


def _extract_supplier_qty_inside(title: str) -> tuple[int | None, str]:
    t = title.strip()
    if not t:
        return None, ""

    m = _PACK_OF_RE.search(t)
    if m:
        qty = int(m.group(2))
        return qty, f"Supplier '{m.group(0)}'"

    m = _PK_PREFIX_RE.search(t)
    if m:
        qty = int(m.group(1) or m.group(2))
        return qty, f"Supplier '{m.group(0)}'"

    m = _PC_SUFFIX_RE.search(t)
    if m:
        qty = int(m.group(1))
        return qty, f"Supplier '{m.group(0)}'"

    if _EACH_RE.search(t):
        return 1, "Supplier 'EACH'"

    # Trailing bare numbers are unreliable for this supplier (per calibration) — ignore by default.
    return None, ""


def _extract_amazon_pack_and_total(title: str) -> tuple[int | None, int | None, str]:
    t = title.strip()
    if not t:
        return None, None, ""

    # Capacity multipack: "3 x 400ml" -> RSU = 3 (units), not 1200.
    m = _CAPACITY_MULTIPACK_RE.search(t)
    if m:
        outer = int(m.group(1))
        return outer, outer, f"Amazon '{m.group(0)}'"

    m = _PACK_OF_RE.search(t)
    if m:
        qty = int(m.group(2))
        return qty, qty, f"Amazon '{m.group(0)}'"

    m = _N_PACK_RE.search(t)
    if m:
        qty = int(m.group(1))
        return qty, qty, f"Amazon '{m.group(0)}'"

    # Generic "(N x M)" multipack. If M looks like measurement => treat as units=N.
    m = re.search(r"\(?\s*(\d{1,4})\s*[x×]\s*(\d{1,4})\s*\)?", t, flags=re.IGNORECASE)
    if m:
        outer = int(m.group(1))
        inner = int(m.group(2))

        # Avoid dimension traps: if near a measurement token or dimension pattern, do not treat as item count.
        window = t[max(0, m.start() - 10) : min(len(t), m.end() + 10)]
        if _looks_like_measurement_context(window):
            return None, None, ""

        # Avoid obvious ranges/codes.
        if _RANGE_SUFFIX_RE.search(window) or _DATE_CODE_RE.search(window):
            return None, None, ""

        total = outer * inner
        return outer, total, f"Amazon '{m.group(0)}'"

    # No explicit pack found.
    return None, None, ""


def extract_pack_info(supplier_title: str, amazon_title: str) -> PackInfo:
    sup_qty, sup_ev = _extract_supplier_qty_inside(supplier_title)
    amz_pack, amz_total, amz_ev = _extract_amazon_pack_and_total(amazon_title)

    evidence_parts = [p for p in (sup_ev, amz_ev) if p]
    return PackInfo(
        supplier_qty_inside=sup_qty,
        amazon_pack_count=amz_pack,
        amazon_total_items=amz_total,
        evidence="; ".join(evidence_parts),
    )


def compute_rsu(pack: PackInfo) -> tuple[int, str]:
    """
    Returns (required_supplier_units, pack_verdict).
    Conservative: only compute RSU>1 when Amazon explicitly indicates a multipack/bundle.
    """
    if pack.amazon_total_items is None and pack.amazon_pack_count is None:
        return 1, "1:1 Match (no Amazon multipack signal)"

    if pack.supplier_qty_inside is None or pack.supplier_qty_inside <= 0:
        rsu = int(pack.amazon_pack_count or pack.amazon_total_items or 1)
        rsu = max(1, rsu)
        return rsu, f"BUNDLE (RSU={rsu})"

    # If we have an Amazon total and supplier qty, compute packs needed.
    if pack.amazon_total_items is not None:
        rsu = max(1, math.ceil(pack.amazon_total_items / pack.supplier_qty_inside))
        if rsu == 1:
            return 1, "1:1 Match (qty-inside aligns)"
        return rsu, f"BUNDLE (RSU={rsu})"

    # Fallback: Amazon pack count only.
    rsu = max(1, int(pack.amazon_pack_count))
    if rsu == 1:
        return 1, "1:1 Match"
    return rsu, f"BUNDLE (RSU={rsu})"


def adjusted_profit(net_profit: float | None, supplier_cost: float | None, rsu: int) -> float | None:
    if net_profit is None:
        return None
    if supplier_cost is None:
        return net_profit
    return net_profit - supplier_cost * max(0, rsu - 1)


def capacity_value(title: str) -> tuple[float, str] | None:
    m = _DIM_TOKEN_RE.search(title)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit in {"liter", "litre"}:
        unit = "ltr"
    if unit == "l":
        unit = "ltr"
    if unit == "kg":
        unit = "g"
        val *= 1000
    if unit == "ltr":
        unit = "ml"
        val *= 1000
    return val, unit


def capacity_diff_flag(supplier_title: str, amazon_title: str) -> str | None:
    s = capacity_value(supplier_title)
    a = capacity_value(amazon_title)
    if not s or not a:
        return None
    sv, su = s
    av, au = a
    if su != au:
        return None
    if sv <= 0 or av <= 0:
        return None
    diff = abs(sv - av) / max(sv, av)
    if diff <= 0.10:
        return "capacity<=10%"
    if diff <= 0.25:
        return "capacity10-25%"
    if diff <= 0.50:
        return "capacity25-50%"
    return "capacity>50%"


def title_similarity(a: str, b: str) -> float:
    # Lightweight similarity; avoid SequenceMatcher cost across all 2402 rows.
    at = set(_tokenize(a))
    bt = set(_tokenize(b))
    if not at or not bt:
        return 0.0
    return len(at & bt) / len(at | bt)


def shared_evidence(supplier_title: str, amazon_title: str, brand: str | None) -> str:
    st = set(_tokenize(supplier_title))
    at = set(_tokenize(amazon_title))
    common = [t for t in (st & at) if len(t) >= 4 and t not in STOPWORDS and t not in MEASUREMENT_UNITS]
    common_sorted = sorted(common)[:4]

    parts: list[str] = []
    if brand:
        parts.append(f"Brand '{brand}'")
    if common_sorted:
        parts.append("Shared: " + ", ".join(repr(t) for t in common_sorted))
    return "; ".join(parts) if parts else "-"


def ip_risk_note(supplier_title: str, amazon_title: str) -> str | None:
    blob = f"{supplier_title} {amazon_title}".lower()
    for b in LUXURY_IP_BRANDS:
        if b in blob:
            if b == "apple":
                # Avoid false positives like "Apple & Cinnamon" (fragrance/food), only flag likely Apple Inc contexts.
                if not re.search(r"\b(iphone|ipad|mac|airpods|watch|magsafe|lightning)\b", blob):
                    continue
            if b == "samsung" and not re.search(r"\b(galaxy|s\d{1,2}|note|tab)\b", blob):
                continue
            if b == "sony" and not re.search(r"\b(playstation|ps5|ps4|bravia)\b", blob):
                continue
            if b == "microsoft" and not re.search(r"\b(xbox|surface)\b", blob):
                continue
            return f"IP risk: {b.title()}"
    return None


@dataclass(frozen=True)
class ReportRow:
    row_id: int
    verdict: str
    confidence: int
    supplier_title: str
    amazon_title: str
    supplier_ean: str
    amazon_ean: str
    asin: str
    supplier_price: str
    selling_price: str
    net_profit: str
    roi: str
    sales: str
    pack_verdict: str
    adjusted_profit: str
    key_match_evidence: str
    filter_reason: str
    score: float


def truncate(s: str, width: int) -> str:
    if len(s) <= width:
        return s
    if width <= 3:
        return s[:width]
    return s[: width - 3] + "..."


def render_table(rows: list[ReportRow]) -> str:
    cols = [
        ("Verdict", lambda r: r.verdict),
        ("Confidence", lambda r: str(r.confidence)),
        ("RowID", lambda r: str(r.row_id)),
        ("SupplierTitle", lambda r: r.supplier_title),
        ("AmazonTitle", lambda r: r.amazon_title),
        ("Supplier EAN", lambda r: r.supplier_ean),
        ("Amazon EAN", lambda r: r.amazon_ean),
        ("ASIN", lambda r: r.asin),
        ("SupplierPrice", lambda r: r.supplier_price),
        ("SellingPrice", lambda r: r.selling_price),
        ("NetProfit", lambda r: r.net_profit),
        ("ROI", lambda r: r.roi),
        ("Sales", lambda r: r.sales),
        ("Pack Verdict", lambda r: r.pack_verdict),
        ("Adjusted Profit", lambda r: r.adjusted_profit),
        ("Key Match Evidence", lambda r: r.key_match_evidence),
        ("Filter Reason", lambda r: r.filter_reason),
    ]

    max_width = {
        "Verdict": 12,
        "Confidence": 10,
        "RowID": 6,
        "SupplierTitle": 48,
        "AmazonTitle": 58,
        "Supplier EAN": 14,
        "Amazon EAN": 14,
        "ASIN": 12,
        "SupplierPrice": 13,
        "SellingPrice": 12,
        "NetProfit": 10,
        "ROI": 8,
        "Sales": 6,
        "Pack Verdict": 26,
        "Adjusted Profit": 14,
        "Key Match Evidence": 46,
        "Filter Reason": 46,
    }

    data: list[list[str]] = []
    for r in rows:
        data.append([_safe_str(getter(r)) for _, getter in cols])

    widths: list[int] = []
    for idx, (name, _) in enumerate(cols):
        header_len = len(name)
        data_len = max((len(row[idx]) for row in data), default=0)
        w = max(header_len, data_len)
        w = min(w, max_width.get(name, w))
        w = max(w, header_len)  # never truncate headers
        widths.append(w)

    def fmt_row(values: list[str]) -> str:
        parts = []
        for v, w in zip(values, widths, strict=True):
            vv = truncate(v, w)
            parts.append(vv.ljust(w))
        return "| " + " | ".join(parts) + " |"

    header = fmt_row([name for name, _ in cols])
    sep = "|-" + "-|-".join("-" * w for w in widths) + "-|"
    body = "\n".join(fmt_row([cell for cell in row]) for row in data)
    return "\n".join([header, sep, body]) if body else "\n".join([header, sep])


def build_report_rows(
    df: pd.DataFrame,
) -> tuple[list[ReportRow], list[ReportRow], list[ReportRow], list[ReportRow], list[ReportRow]]:
    verified_rec: list[ReportRow] = []
    verified_out: list[ReportRow] = []
    likely_rec: list[ReportRow] = []
    likely_out: list[ReportRow] = []
    needs_verification: list[ReportRow] = []

    # Compute strict EAN match flags
    sup_digits = df["EAN"].map(clean_to_digits).map(normalize_ean)
    amz_digits = df["EAN_OnPage"].map(clean_to_digits).map(normalize_ean)
    sup_valid = sup_digits.map(is_strict_valid_barcode)
    amz_valid = amz_digits.map(is_strict_valid_barcode)
    is_exact_ean_strict = sup_valid & amz_valid & (sup_digits == amz_digits)

    # Derive a conservative "known brands" set from strict-exact rows to avoid false brand positives
    # (e.g., titles that start with product-type words like "BALLOONS", "BOWL", "CANDLE").
    known_brands: set[str] = set()
    for i in df.index[is_exact_ean_strict]:
        st_i = _safe_str(df.at[i, "SupplierTitle"])
        at_i = _safe_str(df.at[i, "AmazonTitle"])
        b = _brand_match(st_i, at_i)
        if b:
            known_brands.add(b)

    for idx, row in df.iterrows():
        row_id = int(idx) + 1
        st = _safe_str(row.get("SupplierTitle", ""))
        at = _safe_str(row.get("AmazonTitle", ""))
        asin = _safe_str(row.get("ASIN", ""))

        supplier_cost = parse_money_gbp(row.get("SupplierPrice_incVAT"))
        sell_price = parse_money_gbp(row.get("SellingPrice_incVAT"))
        net_profit = parse_money_gbp(row.get("NetProfit"))

        sales = int(float(fmt_int(row.get(SUPPLIER_NAMING_CONVENTION["sales_column"], 0))))

        strict_ean = bool(is_exact_ean_strict.iloc[idx])
        supplier_ean = format_ean(row.get("EAN"))
        amazon_ean = format_ean(row.get("EAN_OnPage"))

        overlap = title_similarity(st, at)
        brand = _brand_match(st, at)
        if not strict_ean and brand:
            brand_tokens = brand.split()
            allow_unknown_multiword = (
                " " in brand
                and all(t not in GENERIC_BRAND_TOKENS and t not in NON_BRAND_LEADING_TOKENS for t in brand_tokens)
            )
            if brand not in known_brands and not allow_unknown_multiword and overlap < 0.60:
                brand = None

        pack = extract_pack_info(st, at)
        rsu, pack_verdict = compute_rsu(pack)

        # For strict EAN matches: default to 1:1 unless Amazon explicitly shows multipack/bundle.
        if strict_ean and rsu == 1:
            pack_verdict = "1:1 Match (Exact EAN)"

        adj = adjusted_profit(net_profit, supplier_cost, rsu)

        # Capacity mismatch gating for strong matches only.
        cap_flag = capacity_diff_flag(st, at)

        base_evidence = shared_evidence(st, at, brand=brand)
        pack_evidence = pack.evidence
        ip_note = ip_risk_note(st, at)

        key_parts = [p for p in (("Exact EAN" if strict_ean else None), base_evidence, pack_evidence, ip_note) if p]
        key_match = "; ".join(p for p in key_parts if p and p != "-") or "-"

        # Candidate scoring for ordering (not shown).
        score = (0.8 if strict_ean else 0.0) + (0.6 if brand else 0.0) + overlap

        def make_row(verdict: str, confidence: int, filter_reason: str) -> ReportRow:
            return ReportRow(
                row_id=row_id,
                verdict=verdict,
                confidence=confidence,
                supplier_title=st,
                amazon_title=at,
                supplier_ean=supplier_ean,
                amazon_ean=amazon_ean,
                asin=asin,
                supplier_price=fmt_gbp(supplier_cost),
                selling_price=fmt_gbp(sell_price),
                net_profit=fmt_gbp(net_profit),
                roi=fmt_roi(row.get("ROI")),
                sales=str(sales),
                pack_verdict=pack_verdict + (f" [{pack.evidence}]" if pack.evidence else ""),
                adjusted_profit=fmt_gbp(adj),
                key_match_evidence=key_match,
                filter_reason=filter_reason,
                score=score,
            )

        # Strict EAN path
        if strict_ean:
            confidence = 95
            filter_reason = "-"

            if supplier_cost is None or supplier_cost <= 0:
                filter_reason = "Exact EAN but SupplierPrice is missing/0 (report anomaly)"
                verified_out.append(make_row("FILTERED OUT", 90, filter_reason))
                continue

            # Explicit multipack contradiction => adjust and potentially filter out if unprofitable.
            if rsu > 1 and adj is not None and adj <= 0:
                filter_reason = f"Exact EAN; requires RSU={rsu}; adjusted profit <= 0"
                verified_out.append(make_row("FILTERED OUT", confidence, filter_reason))
                continue

            # Large capacity mismatch on exact EAN should not auto-exclude within 25%, but >50% is a red flag.
            if cap_flag == "capacity>50%":
                filter_reason = "Exact EAN but capacity differs >50% (possible data error / different listing)"
                verified_out.append(make_row("FILTERED OUT", 90, filter_reason))
                continue

            verified_rec.append(make_row("VERIFIED", confidence, filter_reason))
            continue

        # Non-EAN: choose conservative candidate set
        # Exclude obvious non-matches unless they have strong overlap.
        if overlap < 0.25:
            continue

        assorted = "assorted" in st.lower() or "assorted" in at.lower()
        both_eans_strict_valid = supplier_ean != "-" and amazon_ean != "-"
        strict_ean_mismatch = both_eans_strict_valid and supplier_ean != amazon_ean

        # Capacity mismatch >50% => exclude even for strong brand matches.
        if cap_flag == "capacity>50%" and brand and overlap >= 0.45:
            likely_out.append(make_row("FILTERED OUT", 65, "Brand match but capacity differs >50% (different SKU)"))
            continue

        if brand and overlap >= 0.45 and not assorted and not strict_ean_mismatch:
            # Strong brand + product overlap => HIGHLY LIKELY
            confidence = min(92, max(80, int(round(70 + overlap * 60))))
            if rsu > 1 and adj is not None and adj <= 0:
                likely_out.append(
                    make_row("FILTERED OUT", confidence, f"Requires RSU={rsu}; adjusted profit <= 0")
                )
            else:
                likely_rec.append(make_row("HIGHLY LIKELY", confidence, "-"))
            continue

        # Otherwise: NEEDS VERIFICATION only if upgradeable and still plausible.
        st_tokens = set(_tokenize(st))
        at_tokens = set(_tokenize(at))
        shared = [t for t in (st_tokens & at_tokens) if len(t) >= 5]
        upgradeable = (brand and overlap >= 0.30) or (overlap >= 0.55 and len(shared) >= 3)
        if upgradeable:
            confidence = min(
                79,
                max(55, int(round(45 + overlap * 70 + (10 if brand else 0) - (8 if assorted else 0)))),
            )
            reason_parts: list[str] = []
            if strict_ean_mismatch:
                reason_parts.append("EAN mismatch (both strict-valid); verify packaging")
            elif not brand:
                reason_parts.append("Verify brand/model on listing")
            if rsu > 1:
                reason_parts.append(f"Verify pack count (RSU={rsu} inferred)")
            if cap_flag == "capacity10-25%":
                reason_parts.append("Verify capacity (10-25% diff)")
            if cap_flag == "capacity25-50%":
                reason_parts.append("Likely different size (25-50% diff)")
            if assorted:
                reason_parts.append("Assorted/variant risk; verify exact variant")
            if not reason_parts:
                reason_parts.append("Verify variant/attributes")
            # Enforce A4: if adjusted profit is non-positive after a clear RSU recalculation, exclude.
            if rsu > 1 and adj is not None and adj <= 0 and brand and overlap >= 0.30:
                likely_out.append(make_row("FILTERED OUT", confidence, f"Requires RSU={rsu}; adjusted profit <= 0"))
            else:
                needs_verification.append(make_row("NEEDS VERIFICATION", confidence, "; ".join(reason_parts)))

    # Sorting per spec
    verified_rec.sort(key=lambda r: (int(r.sales), (parse_money_gbp(r.net_profit) or 0.0)), reverse=True)
    verified_out.sort(key=lambda r: int(r.sales), reverse=True)
    likely_rec.sort(key=lambda r: (r.score, int(r.sales)), reverse=True)
    likely_out.sort(key=lambda r: int(r.sales), reverse=True)
    needs_verification.sort(key=lambda r: (r.confidence, r.score, int(r.sales)), reverse=True)

    return verified_rec, verified_out, likely_rec, likely_out, needs_verification


def load_report(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path, dtype=str, engine="openpyxl")
    return pd.read_csv(path, dtype=str, low_memory=False, on_bad_lines="skip")


def write_report(
    output_path: Path,
    input_path: Path,
    supplier: str,
    verified_rec: list[ReportRow],
    verified_out: list[ReportRow],
    likely_rec: list[ReportRow],
    likely_out: list[ReportRow],
    needs_verification: list[ReportRow],
    total_analyzed: int,
) -> None:
    today = date.today().isoformat()

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT")
    lines.append(f"**Generated:** {today}")
    lines.append(f"**Input File:** `{input_path}`")
    lines.append(f"**Supplier:** `{supplier}`")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append(f"- VERIFIED — RECOMMENDED: {len(verified_rec)}")
    lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(verified_out)}")
    lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(likely_rec)}")
    lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(likely_out)}")
    lines.append(f"- NEEDS VERIFICATION: {len(needs_verification)}")
    lines.append(f"- TOTAL ANALYZED: {total_analyzed}")
    lines.append("")
    lines.append(
        "This report applies v4.1.1 manual gating: strict EAN validation, dimension/measurement shielding, "
        "and conservative pack recalculation (RSU only when Amazon explicitly signals a bundle)."
    )
    lines.append(
        "Most extreme ROI rows are treated as false positives unless supported by strict exact EAN or strong "
        "brand+product anchors in both titles."
    )
    lines.append("")

    lines.append(f"## VERIFIED — RECOMMENDED - (count={len(verified_rec)})")
    lines.append("```text")
    lines.append(render_table(verified_rec))
    lines.append("```")
    lines.append("")

    lines.append(f"## VERIFIED — FILTERED OUT / EXCLUDED - (count={len(verified_out)})")
    lines.append("```text")
    lines.append(render_table(verified_out))
    lines.append("```")
    lines.append("")

    lines.append(f"## HIGHLY LIKELY — RECOMMENDED - (count={len(likely_rec)})")
    lines.append("```text")
    lines.append(render_table(likely_rec))
    lines.append("```")
    lines.append("")

    lines.append(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED - (count={len(likely_out)})")
    lines.append("```text")
    lines.append(render_table(likely_out))
    lines.append("```")
    lines.append("")

    lines.append(f"## NEEDS VERIFICATION - (count={len(needs_verification)})")
    lines.append("```text")
    lines.append(render_table(needs_verification))
    lines.append("```")
    lines.append("")

    lines.append("## Reconciliation")
    lines.append(
        f"- VERIFIED total: {len(verified_rec) + len(verified_out)} (recommended={len(verified_rec)}, excluded={len(verified_out)})"
    )
    lines.append(
        f"- HIGHLY LIKELY total: {len(likely_rec) + len(likely_out)} (recommended={len(likely_rec)}, excluded={len(likely_out)})"
    )
    lines.append(f"- NEEDS VERIFICATION total: {len(needs_verification)}")
    lines.append(
        f"- TOTAL INCLUDED IN REPORT: {len(verified_rec) + len(verified_out) + len(likely_rec) + len(likely_out) + len(needs_verification)}"
    )
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Path to financial report (.xlsx/.csv)")
    parser.add_argument("--output", type=Path, required=True, help="Path to output markdown report")
    parser.add_argument("--supplier", default="efghousewares.co.uk", help="Supplier name/domain for report header")
    args = parser.parse_args()

    df = load_report(args.input)
    required = {
        "EAN",
        "EAN_OnPage",
        "ASIN",
        "SupplierTitle",
        "AmazonTitle",
        "SupplierPrice_incVAT",
        "SellingPrice_incVAT",
        "NetProfit",
        "ROI",
        SUPPLIER_NAMING_CONVENTION["sales_column"],
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")

    verified_rec, verified_out, likely_rec, likely_out, needs_verification = build_report_rows(df)
    write_report(
        output_path=args.output,
        input_path=args.input,
        supplier=args.supplier,
        verified_rec=verified_rec,
        verified_out=verified_out,
        likely_rec=likely_rec,
        likely_out=likely_out,
        needs_verification=needs_verification,
        total_analyzed=len(df),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
