from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)
METHODOLOGY_GUIDE_PATH = ROOT / r"RESERACH\REPORT\PROMPTS GUIDES\ANTI-GRAVITY\guides\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md"
OPUS_REPORT_PATH = ROOT / r"RESERACH\REPORT\part_1_jan\OPUS chat\PHASEA_MANUAL_REPORT_20260102.md"


# Preflight calibration (detected from part_1_jan.xlsx sample)
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

# These are frequently *product type* words in this supplier dataset, not reliable brands.
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
    s = s.replace("|", "/")
    s = re.sub(r"\s+", " ", s)
    return s


_SCINOT_RE = re.compile(r"\d+(\.\d+)?e[+-]?\d+", re.IGNORECASE)


def clean_to_digits(x: Any) -> str:
    s = _safe_str(x)
    if not s or s.lower() in {"nan", "none", "-", "0"}:
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


def parse_float(raw: Any) -> float | None:
    s = _safe_str(raw)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        s2 = re.sub(r"[^\d.\-]", "", s)
        try:
            return float(s2)
        except ValueError:
            return None


def fmt_money(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "-"
    return f"£{value:.2f}"


def fmt_percent(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "-"
    v = value * 100 if value <= 5 else value
    return f"{v:.1f}%"


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
_PCS_SUFFIX_RE = re.compile(r"\b(\d{1,4})\s*(pcs?|pce|pc|piece|pieces)\b", re.IGNORECASE)
_SOLD_EACH_RE = re.compile(r"\b(sold each|sold separately|each)\b", re.IGNORECASE)
_DATE_CODE_RE = re.compile(r"\b\d{1,2}/\d{1,2}\b")
_QTY_INSIDE_WORD_RE = re.compile(
    r"\b(\d{1,4})\s*(doyleys?|napkins?|bags?|liners?|sticks?|glasses?|cases?|containers?|trays?|"
    r"cards?|pegs?|bells?|pads?)\b",
    re.IGNORECASE,
)
_TOTAL_X_RE = re.compile(r"\b(\d{2,5})\s*[x×]\b", re.IGNORECASE)


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
        if t in STOPWORDS:
            continue
        if t in MEASUREMENT_UNITS:
            continue
        cleaned.append(t)
    return cleaned


def _extract_brand_candidates(supplier_title: str) -> list[str]:
    raw_tokens = [t for t in re.split(r"\s+", supplier_title.strip()) if t]
    caps_tokens: list[str] = []
    for t in raw_tokens:
        t2 = t.strip("()[]{}.,;:/\\-")
        if not t2:
            continue
        if any(ch.isdigit() for ch in t2):
            break
        if len(t2) < 2:
            break
        if not t2.isupper():
            break
        caps_tokens.append(t2)
        if len(caps_tokens) >= 3:
            break

    if not caps_tokens:
        return []

    start = 0
    if caps_tokens[0] in GENERIC_BRAND_TOKENS or caps_tokens[0] in NON_BRAND_LEADING_TOKENS:
        start = 1

    cands: list[str] = []
    if start < len(caps_tokens):
        first = caps_tokens[start]
        if first not in GENERIC_BRAND_TOKENS and first not in NON_BRAND_LEADING_TOKENS:
            cands.append(first)
        if start + 1 < len(caps_tokens):
            cands.append(" ".join(caps_tokens[start : start + 2]))

    if len(caps_tokens) >= 3 and caps_tokens[0] == "THE":
        cands.append(" ".join(caps_tokens[:3]))

    return sorted(set(cands), key=lambda s: (-len(s.split()), -len(s)))


def brand_match(supplier_title: str, amazon_title: str) -> str | None:
    at = amazon_title.lower()
    for cand in _extract_brand_candidates(supplier_title):
        if re.search(rf"(?<!\w){re.escape(cand.lower())}(?!\w)", at):
            return cand
    return None


def ip_risk_note(supplier_title: str, amazon_title: str) -> str | None:
    blob = f"{supplier_title} {amazon_title}".lower()
    for b in LUXURY_IP_BRANDS:
        if b not in blob:
            continue
        if b == "apple":
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
class PackParse:
    supplier_qty: int
    amazon_total: int
    rsu: int
    verdict: str
    evidence: str


def _looks_like_dimension_context(text: str) -> bool:
    return bool(_DIM_X_RE.search(text) or _DIM_TOKEN_RE.search(text))


def _extract_supplier_qty(title: str) -> tuple[int, str]:
    t = title.strip()
    if not t:
        return 1, ""

    if _SOLD_EACH_RE.search(t):
        return 1, "Supplier 'EACH'"

    m = _PACK_OF_RE.search(t)
    if m:
        return int(m.group(2)), f"Supplier '{m.group(0)}'"

    m = _PK_PREFIX_RE.search(t)
    if m:
        qty = int(m.group(1) or m.group(2))
        return qty, f"Supplier '{m.group(0)}'"

    m = _PCS_SUFFIX_RE.search(t)
    if m:
        return int(m.group(1)), f"Supplier '{m.group(0)}'"

    m = _QTY_INSIDE_WORD_RE.search(t)
    if m:
        qty = int(m.group(1))
        return qty, f"Supplier '{m.group(0)}'"

    return 1, ""


def _extract_amazon_total(title: str) -> tuple[int, str]:
    t = title.strip()
    if not t:
        return 1, ""

    m = _CAPACITY_MULTIPACK_RE.search(t)
    if m:
        n = int(m.group(1))
        return n, f"Amazon '{m.group(0)}' (capacity multipack: RSU={n})"

    m = _PACK_OF_RE.search(t)
    if m:
        qty = int(m.group(2))
        return qty, f"Amazon '{m.group(0)}'"

    m = _N_PACK_RE.search(t)
    if m:
        qty = int(m.group(1))
        return qty, f"Amazon '{m.group(0)}'"

    m = re.search(r"\(?\s*(\d{1,4})\s*[x×]\s*(\d{1,4})\s*\)?", t, flags=re.IGNORECASE)
    if m:
        outer = int(m.group(1))
        inner = int(m.group(2))
        window = t[max(0, m.start() - 12) : min(len(t), m.end() + 12)]
        if not _looks_like_dimension_context(window):
            total = outer * inner
            return total, f"Amazon '{m.group(0)}' (total={total})"

    m = _TOTAL_X_RE.search(t)
    if m:
        total = int(m.group(1))
        window = t[max(0, m.start() - 12) : min(len(t), m.end() + 12)]
        if total >= 20 and not _looks_like_dimension_context(window):
            return total, f"Amazon '{m.group(0)}' (total={total})"

    return 1, ""


def parse_pack(supplier_title: str, amazon_title: str) -> PackParse:
    sup_qty, sup_ev = _extract_supplier_qty(supplier_title)
    amz_total, amz_ev = _extract_amazon_total(amazon_title)

    rsu = max(1, math.ceil(amz_total / max(sup_qty, 1)))
    verdict = "1:1 Match"
    if amz_total > sup_qty:
        verdict = f"Bundle: RSU={rsu}"
    elif sup_qty > amz_total and amz_total > 1:
        verdict = "Supplier pack larger (verify ASIN pack)"

    evidence = "; ".join([p for p in (sup_ev, amz_ev) if p])
    if _DATE_CODE_RE.search(supplier_title):
        evidence = "; ".join([evidence, "Supplier has date/code token"]) if evidence else "Supplier has date/code token"

    return PackParse(supplier_qty=sup_qty, amazon_total=amz_total, rsu=rsu, verdict=verdict, evidence=evidence)


def adjusted_profit(net_profit: float | None, supplier_cost: float | None, rsu: int) -> float | None:
    if net_profit is None:
        return None
    if supplier_cost is None:
        return net_profit
    return net_profit - supplier_cost * max(0, rsu - 1)


def capacity_flag(supplier_title: str, amazon_title: str) -> tuple[str | None, str]:
    s = _DIM_TOKEN_RE.search(supplier_title)
    a = _DIM_TOKEN_RE.search(amazon_title)
    if not s or not a:
        return None, ""
    sv = float(s.group(1))
    su = s.group(2).lower()
    av = float(a.group(1))
    au = a.group(2).lower()

    # Normalize to ml/g where possible.
    def norm(val: float, unit: str) -> tuple[float, str]:
        if unit in {"liter", "litre"}:
            unit = "ltr"
        if unit == "l":
            unit = "ltr"
        if unit == "kg":
            return val * 1000, "g"
        if unit == "ltr":
            return val * 1000, "ml"
        return val, unit

    sv, su = norm(sv, su)
    av, au = norm(av, au)
    if su != au:
        return None, ""
    diff = abs(sv - av) / max(sv, av)
    if diff <= 0.15:
        return "capacity<=15%", f"Capacity within 15% ({sv:g}{su} vs {av:g}{au})"
    if diff <= 0.25:
        return "capacity15-25%", f"Capacity 15-25% diff ({sv:g}{su} vs {av:g}{au})"
    if diff <= 0.50:
        return "capacity25-50%", f"Capacity 25-50% diff ({sv:g}{su} vs {av:g}{au})"
    return "capacity>50%", f"Capacity >50% diff ({sv:g}{su} vs {av:g}{au})"


def token_overlap(supplier_title: str, amazon_title: str, brand: str | None) -> tuple[int, float, list[str]]:
    st = set(_tokenize(supplier_title))
    at = set(_tokenize(amazon_title))
    if brand:
        for bt in brand.lower().split():
            st.discard(bt)
            at.discard(bt)
    common = sorted([t for t in (st & at) if len(t) >= 4])[:8]
    union = st | at
    score = (len(st & at) / len(union)) if union else 0.0
    return len(common), score, common


@dataclass(frozen=True)
class RowDecision:
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
    reasoning: list[str]


def decide_rows(df: pd.DataFrame) -> tuple[list[RowDecision], list[RowDecision], list[RowDecision], list[RowDecision], list[RowDecision]]:
    verified_rec: list[RowDecision] = []
    verified_out: list[RowDecision] = []
    likely_rec: list[RowDecision] = []
    likely_out: list[RowDecision] = []
    needs_verification: list[RowDecision] = []

    sup_digits = df["EAN"].map(clean_to_digits).map(normalize_ean)
    amz_digits = df["EAN_OnPage"].map(clean_to_digits).map(normalize_ean)
    sup_valid = sup_digits.map(is_strict_valid_barcode)
    amz_valid = amz_digits.map(is_strict_valid_barcode)
    exact_strict = sup_valid & amz_valid & (sup_digits == amz_digits)

    for idx, row in df.iterrows():
        row_id = int(idx) + 1

        st = _safe_str(row.get("SupplierTitle", ""))
        at = _safe_str(row.get("AmazonTitle", ""))
        asin = _safe_str(row.get("ASIN", ""))

        supplier_ean = format_ean(row.get("EAN"))
        amazon_ean = format_ean(row.get("EAN_OnPage"))
        both_eans_valid = supplier_ean != "-" and amazon_ean != "-"

        supplier_cost = parse_float(row.get("SupplierPrice_incVAT"))
        sell_price = parse_float(row.get("SellingPrice_incVAT"))
        net_profit = parse_float(row.get("NetProfit"))
        roi_val = parse_float(row.get("ROI"))

        sales = int(float(fmt_int(row.get(SUPPLIER_NAMING_CONVENTION["sales_column"], 0))))

        is_exact = bool(exact_strict.iloc[idx])
        assorted = ("assorted" in st.lower()) or ("assorted" in at.lower())

        brand = brand_match(st, at)
        shared_n, overlap, shared_tokens = token_overlap(st, at, brand=brand)

        pack = parse_pack(st, at)
        adj = adjusted_profit(net_profit, supplier_cost, pack.rsu)
        cap_flag, cap_note = capacity_flag(st, at)

        ip_note = ip_risk_note(st, at)

        def mk(verdict: str, confidence: int, filter_reason: str, extra: list[str]) -> RowDecision:
            evidence_parts: list[str] = []
            if is_exact:
                evidence_parts.append("Exact EAN match (strict)")
            if brand:
                evidence_parts.append(f"Brand match: {brand}")
            if shared_tokens:
                evidence_parts.append("Shared tokens: " + ", ".join(repr(t) for t in shared_tokens[:4]))
            if pack.evidence:
                evidence_parts.append(pack.evidence)
            if cap_note:
                evidence_parts.append(cap_note)
            if ip_note:
                evidence_parts.append(ip_note)

            reasoning: list[str] = []
            reasoning.append(f"EAN check: Supplier={supplier_ean}, Amazon={amazon_ean}, strict_exact={is_exact}")
            if both_eans_valid and not is_exact:
                reasoning.append("EAN note: both EANs strict-valid but different -> treat as mismatch unless titles confirm")
            elif supplier_ean == "-" or amazon_ean == "-":
                reasoning.append("EAN note: missing/invalid EAN on one side -> rely on title/brand anchors")
            reasoning.append(f"Brand: {brand or '(none)'}")
            reasoning.append(f"Title anchors: shared_n={shared_n}, overlap={overlap:.2f}, tokens={shared_tokens[:6]}")
            if assorted:
                reasoning.append("Variant risk: 'assorted' present -> verification needed")
            reasoning.append(
                f"Pack: supplier_qty={pack.supplier_qty}, amazon_total={pack.amazon_total}, RSU={pack.rsu}; verdict='{pack.verdict}'"
            )
            if cap_flag:
                reasoning.append(f"Capacity check: {cap_note} -> {cap_flag}")
            reasoning.append(
                f"Profit: NetProfit={fmt_money(net_profit)}, SupplierPrice={fmt_money(supplier_cost)}, AdjustedProfit={fmt_money(adj)}"
            )
            reasoning.extend(extra)

            return RowDecision(
                row_id=row_id,
                verdict=verdict,
                confidence=confidence,
                supplier_title=st,
                amazon_title=at,
                supplier_ean=supplier_ean,
                amazon_ean=amazon_ean,
                asin=asin,
                supplier_price=fmt_money(supplier_cost),
                selling_price=fmt_money(sell_price),
                net_profit=fmt_money(net_profit),
                roi=fmt_percent(roi_val),
                sales=str(sales),
                pack_verdict=pack.verdict + (f" [{pack.evidence}]" if pack.evidence else ""),
                adjusted_profit=fmt_money(adj),
                key_match_evidence="; ".join(evidence_parts) if evidence_parts else "-",
                filter_reason=filter_reason,
                reasoning=reasoning,
            )

        # VERIFIED (strict exact EAN)
        if is_exact:
            if supplier_cost is None or supplier_cost <= 0:
                verified_out.append(mk("FILTERED OUT", 90, "Exact EAN but SupplierPrice missing/0 (report anomaly)", []))
                continue
            if cap_flag == "capacity>50%":
                verified_out.append(mk("FILTERED OUT", 90, "Exact EAN but capacity differs >50% (listing/data issue)", []))
                continue
            if adj is not None and adj <= 0:
                verified_out.append(
                    mk("FILTERED OUT", 95, f"Exact EAN; requires RSU={pack.rsu}; adjusted profit <= 0", [])
                )
                continue
            verified_rec.append(mk("VERIFIED", 95, "-", []))
            continue

        # Non-EAN plausibility gate
        if not brand and overlap < 0.25:
            continue

        # Capacity gating
        if cap_flag == "capacity>50%":
            if brand and shared_n >= 2:
                likely_out.append(mk("FILTERED OUT", 60, "Brand match but capacity differs >50% (different SKU)", []))
            continue

        # If pack adjustment makes it negative and match is otherwise strong -> filtered out
        if adj is not None and adj <= 0 and brand and shared_n >= 2 and pack.rsu > 1:
            likely_out.append(mk("FILTERED OUT", 70, f"Requires RSU={pack.rsu}; adjusted profit <= 0", []))
            continue

        # HIGHLY LIKELY
        if brand and shared_n >= 2 and overlap >= 0.30 and not assorted:
            if both_eans_valid and supplier_ean != amazon_ean:
                needs_verification.append(
                    mk("NEEDS VERIFICATION", 72, "EAN mismatch (both strict-valid); verify packaging/EAN and variant", [])
                )
            elif cap_flag in {"capacity15-25%", "capacity25-50%"}:
                needs_verification.append(mk("NEEDS VERIFICATION", 70, "Capacity variance needs confirmation", []))
            elif pack.verdict == "Supplier pack larger (verify ASIN pack)":
                needs_verification.append(
                    mk("NEEDS VERIFICATION", 70, "Supplier pack appears larger than Amazon listing; verify pack sizes", [])
                )
            else:
                likely_rec.append(mk("HIGHLY LIKELY", 82, "-", []))
            continue

        # NEEDS VERIFICATION (selective)
        if brand and shared_n >= 1 and overlap >= 0.20:
            reason = "Verify pack/variant; title match moderate"
            if assorted:
                reason = "Assorted/variant risk; verify exact variant"
            elif both_eans_valid and supplier_ean != amazon_ean:
                reason = "EAN mismatch (both strict-valid); verify packaging"
            elif pack.rsu > 1 and pack.evidence:
                reason = f"Verify pack calculation (RSU={pack.rsu} inferred)"
            elif cap_flag in {"capacity15-25%", "capacity25-50%"}:
                reason = "Capacity variance needs confirmation"
            needs_verification.append(mk("NEEDS VERIFICATION", 65, reason, []))

    def sort_key(r: RowDecision) -> tuple[int, float]:
        sales_i = int(r.sales) if r.sales.isdigit() else 0
        profit_v = parse_float(r.adjusted_profit) or parse_float(r.net_profit) or 0.0
        return sales_i, profit_v

    verified_rec.sort(key=sort_key, reverse=True)
    verified_out.sort(key=sort_key, reverse=True)
    likely_rec.sort(key=sort_key, reverse=True)
    likely_out.sort(key=sort_key, reverse=True)
    needs_verification.sort(key=sort_key, reverse=True)

    return verified_rec, verified_out, likely_rec, likely_out, needs_verification


def render_table(rows: list[RowDecision]) -> str:
    cols = [
        ("RowID", lambda r: str(r.row_id)),
        ("Verdict", lambda r: r.verdict),
        ("Confidence", lambda r: str(r.confidence)),
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
        "RowID": 6,
        "Verdict": 12,
        "Confidence": 10,
        "SupplierTitle": 50,
        "AmazonTitle": 62,
        "Supplier EAN": 14,
        "Amazon EAN": 14,
        "ASIN": 12,
        "SupplierPrice": 13,
        "SellingPrice": 12,
        "NetProfit": 10,
        "ROI": 8,
        "Sales": 6,
        "Pack Verdict": 30,
        "Adjusted Profit": 14,
        "Key Match Evidence": 60,
        "Filter Reason": 60,
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
        w = max(w, header_len)
        widths.append(w)

    def truncate(s: str, width: int) -> str:
        if len(s) <= width:
            return s
        if width <= 3:
            return s[:width]
        return s[: width - 3] + "..."

    def fmt_row(values: list[str]) -> str:
        parts: list[str] = []
        for v, w in zip(values, widths, strict=True):
            vv = truncate(v, w)
            parts.append(vv.ljust(w))
        return "| " + " | ".join(parts) + " |"

    header = fmt_row([name for name, _ in cols])
    sep = "|-" + "-|-".join("-" * w for w in widths) + "-|"
    body = "\n".join(fmt_row(row) for row in data)
    return "\n".join([header, sep, body]) if body else "\n".join([header, sep])


def render_reasoning(rows: list[RowDecision], title: str) -> str:
    lines: list[str] = []
    lines.append(f"## {title}")
    lines.append("")
    if not rows:
        lines.append("- (none)")
        lines.append("")
        return "\n".join(lines)

    for r in rows:
        lines.append(f"### Row {r.row_id}: {r.supplier_title}")
        lines.append("")
        lines.append(f"- Verdict: {r.verdict} (Confidence {r.confidence})")
        for step in r.reasoning:
            lines.append(f"- {step}")
        lines.append("")
    return "\n".join(lines)


def load_report(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path, dtype=str, engine="openpyxl")
    return pd.read_csv(path, dtype=str, low_memory=False, on_bad_lines="skip")


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

    verified_rec, verified_out, likely_rec, likely_out, needs_verification = decide_rows(df)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    out_lines: list[str] = []
    out_lines.append("# PHASEA MANUAL REPORT")
    out_lines.append("")
    out_lines.append(f"**Generated:** {now}")
    out_lines.append(f"**Input File:** `{args.input}`")
    out_lines.append(f"**Supplier:** `{args.supplier}`")
    out_lines.append(f"**Methodology Guide:** `{METHODOLOGY_GUIDE_PATH}`")
    out_lines.append(f"**Reference Report (OPUS chat):** `{OPUS_REPORT_PATH}`")
    out_lines.append(f"**Total Rows Analyzed:** {len(df)}")
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")
    out_lines.append("## Summary Counts")
    out_lines.append("")
    out_lines.append(f"- VERIFIED — RECOMMENDED: {len(verified_rec)}")
    out_lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(verified_out)}")
    out_lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(likely_rec)}")
    out_lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(likely_out)}")
    out_lines.append(f"- NEEDS VERIFICATION: {len(needs_verification)}")
    out_lines.append(
        f"- TOTAL INCLUDED IN REPORT: {len(verified_rec)+len(verified_out)+len(likely_rec)+len(likely_out)+len(needs_verification)}"
    )
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")

    out_lines.append(f"## VERIFIED — RECOMMENDED - (count={len(verified_rec)})")
    out_lines.append("```text")
    out_lines.append(render_table(verified_rec))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append(f"## VERIFIED — FILTERED OUT / EXCLUDED - (count={len(verified_out)})")
    out_lines.append("```text")
    out_lines.append(render_table(verified_out))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append(f"## HIGHLY LIKELY — RECOMMENDED - (count={len(likely_rec)})")
    out_lines.append("```text")
    out_lines.append(render_table(likely_rec))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED - (count={len(likely_out)})")
    out_lines.append("```text")
    out_lines.append(render_table(likely_out))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append(f"## NEEDS VERIFICATION - (count={len(needs_verification)})")
    out_lines.append("```text")
    out_lines.append(render_table(needs_verification))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append("## Reconciliation")
    out_lines.append(f"- VERIFIED total: {len(verified_rec) + len(verified_out)}")
    out_lines.append(f"- HIGHLY LIKELY total: {len(likely_rec) + len(likely_out)}")
    out_lines.append(f"- NEEDS VERIFICATION total: {len(needs_verification)}")
    out_lines.append("")

    out_lines.append("---")
    out_lines.append("")
    out_lines.append("## Appendix C — Detailed Reasoning (This Run)")
    out_lines.append("")
    out_lines.append("Phases 1–4 and 6–7 reasoning chains (Phase 5 browser verification skipped).")
    out_lines.append("")
    out_lines.append(render_reasoning(verified_rec, "C.1 VERIFIED — RECOMMENDED Reasoning"))
    out_lines.append(render_reasoning(verified_out, "C.1 VERIFIED — FILTERED OUT / EXCLUDED Reasoning"))
    out_lines.append(render_reasoning(likely_rec, "C.2 HIGHLY LIKELY — RECOMMENDED Reasoning"))
    out_lines.append(render_reasoning(likely_out, "C.2 HIGHLY LIKELY — FILTERED OUT / EXCLUDED Reasoning"))
    out_lines.append(render_reasoning(needs_verification, "C.3 NEEDS VERIFICATION Reasoning"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
