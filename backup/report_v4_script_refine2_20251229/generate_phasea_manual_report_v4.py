from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import pandas as pd


REPO_ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)
INPUT_XLSX = REPO_ROOT / "RESERACH" / "REPORT" / "partdec2812" / "PARTDEC28_1.xlsx"
OUTPUT_DIR = REPO_ROOT / "RESERACH" / "REPORT" / "partdec2812" / "COMP" / "CODEX 4 PRMPT"
TZ = ZoneInfo("Asia/Dubai")


LUXURY_IP_BRANDS = [
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
]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "pack",
    "set",
    "the",
    "to",
    "with",
    "x",
}

MEAS_UNITS = {
    "cm",
    "mm",
    "m",
    "in",
    "inch",
    "inches",
    "ft",
    "feet",
    "ml",
    "l",
    "ltr",
    "litre",
    "litres",
    "g",
    "kg",
    "oz",
}

COLOR_TOKENS = {
    "black",
    "blue",
    "brown",
    "clear",
    "cream",
    "gold",
    "green",
    "grey",
    "orange",
    "pink",
    "purple",
    "red",
    "silver",
    "white",
    "yellow",
}

# Tokens that frequently appear as the first word in SupplierTitle but are not brands.
GENERIC_BRAND_TOKENS = {
    "a",
    "assorted",
    "banner",
    "balloon",
    "birthday",
    "christmas",
    "confetti",
    "decorations",
    "decoration",
    "doormat",
    "fathers",
    "giant",
    "happy",
    "i",
    "indoor",
    "love",
    "memorial",
    "mothers",
    "new",
    "outdoor",
    "party",
    "rose",
    "special",
    "valentines",
    "welcome",
    "wedding",
    "xmas",
}

# Shared tokens that are weak as match evidence for v4 HIGHLY LIKELY without brand confirmation.
LOW_SIGNAL_SHARED_TOKENS = {
    "assorted",
    "available",
    "banner",
    "balloon",
    "birthday",
    "black",
    "blue",
    "case",
    "cases",
    "cm",
    "confetti",
    "decorations",
    "decoration",
    "each",
    "for",
    "ft",
    "gift",
    "gold",
    "green",
    "happy",
    "home",
    "in",
    "inch",
    "inches",
    "large",
    "love",
    "mini",
    "multi",
    "new",
    "outdoor",
    "pack",
    "party",
    "pink",
    "plastic",
    "red",
    "rose",
    "round",
    "set",
    "silver",
    "small",
    "special",
    "strong",
    "uk",
    "welcome",
    "white",
    "x",
}


@dataclass(frozen=True)
class BarcodeResult:
    raw: str
    digits: str
    normalized: str
    strict_valid: bool


def _as_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return ""
    return str(x).strip()


def clean_to_digits(x: Any) -> str:
    s = _as_text(x)
    if not s:
        return ""
    if "e" in s.lower():
        return ""
    s = s.replace(".0", "")
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
    body_rev = list(map(int, body[::-1]))
    for i, d in enumerate(body_rev, start=1):
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


def barcode_result(x: Any) -> BarcodeResult:
    raw = _as_text(x)
    digits = clean_to_digits(raw)
    normalized = normalize_gtin(digits)
    strict_valid = is_strict_valid_barcode(normalized)
    return BarcodeResult(raw=raw, digits=digits, normalized=normalized, strict_valid=strict_valid)


def parse_sales(x: Any) -> int:
    if x is None:
        return 0
    if isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x)):
        return max(0, int(x))
    s = _as_text(x)
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else 0


def _to_float(x: Any) -> float:
    if x is None:
        return float("nan")
    if isinstance(x, (int, float)):
        return float(x)
    s = _as_text(x).replace("£", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def fmt_gbp(x: float) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "-"
    return f"£{x:.2f}"


def fmt_roi(x: float) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "-"
    return f"{x:.1f}%"


def fmt_int(x: int) -> str:
    try:
        return str(int(x))
    except Exception:
        return "0"


def truncate(s: str, max_len: int = 160) -> str:
    s = _as_text(s)
    if len(s) <= max_len:
        return s
    return s[: max_len - 3].rstrip() + "..."


DIMENSION_RE = re.compile(
    r"(?i)\b\d+(?:\.\d+)?\s*(?:x|×)\s*\d+(?:\.\d+)?(?:\s*(?:x|×)\s*\d+(?:\.\d+)?)?\s*(?:cm|mm|m|in|inch|inches|ft)\b"
)
MEASUREMENT_RE = re.compile(r"(?i)\b\d+(?:\.\d+)?\s*(?:cm|mm|m|in|inch|inches|ft|ml|l|ltr|litre|litres|g|kg|oz)\b")


def has_dimension_or_measurement(title: str) -> bool:
    t = _as_text(title)
    return bool(DIMENSION_RE.search(t) or MEASUREMENT_RE.search(t))


PACK_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\bpack of\s*(\d+)\b"),
    re.compile(r"(?i)\bset of\s*(\d+)\b"),
    re.compile(r"(?i)\b(\d+)\s*(?:-|\s*)pack\b"),
    re.compile(r"(?i)\b(\d+)\s*pk\b"),
    re.compile(r"(?i)\b(\d+)\s*(?:pcs|pc|pieces?|pce|pces)\b"),
    re.compile(r"(?i)\b(\d+)\s*pairs?\b"),
    re.compile(r"(?i)\b(\d+)\s*rolls?\b"),
    re.compile(r"(?i)\b(\d+)\s*(?:bags?|cases?|cups?|containers?|doileys?)\b"),
    # Start-of-title multipack indicator (guarded vs dimensions in extract_pack_qty)
    re.compile(r"(?i)^\s*(\d+)\s*(?:x|×)\s+"),
]


def extract_pack_qty(title: str) -> tuple[int, str | None]:
    """
    Returns (qty, evidence_string).
    Evidence_string is a short phrase from the title explaining the qty, or None if defaulted to 1.
    Dimension/measurement patterns never count as pack quantities.
    """
    t = _as_text(title)
    if not t:
        return 1, None

    if DIMENSION_RE.search(t):
        return 1, "dimensions (not pack)"

    for pat in PACK_PATTERNS:
        m = pat.search(t)
        if not m:
            continue
        try:
            qty = int(m.group(1))
        except Exception:
            continue
        if qty <= 1 or qty >= 500:
            continue
        # Guard: only apply dimension/measurement rejection for the "N x ..." prefix pattern.
        if pat.pattern.startswith("(?i)^\\s*(\\d+)\\s*(?:x|×)"):
            window = t[m.start() : min(len(t), m.end() + 25)].lower()
            if any(u in window for u in MEAS_UNITS):
                continue
        return qty, m.group(0).strip()

    return 1, None


TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokenize(title: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(_as_text(title)) if t]


def significant_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for t in tokens:
        if t in STOPWORDS:
            continue
        if t.isdigit():
            continue
        if t in MEAS_UNITS:
            continue
        if len(t) < 3:
            continue
        out.append(t)
    return out


def guess_brand_candidates(supplier_title: str) -> list[str]:
    words = [w for w in _as_text(supplier_title).split() if w]
    if not words:
        return []
    cands: list[str] = []
    if len(words) >= 2:
        cands.append(" ".join(words[:2]))
    cands.append(words[0])
    return list(dict.fromkeys([c.strip() for c in cands if c.strip()]))


def brand_matches(supplier_title: str, amazon_title: str) -> str | None:
    a = _as_text(amazon_title).lower()
    for cand in guess_brand_candidates(supplier_title):
        c = cand.lower().strip()
        if not c or len(c) < 3:
            continue
        c_tokens = [t for t in c.split() if t]
        if not c_tokens:
            continue
        # Reject generic "brands" like HAPPY/MEMORIAL unless a multi-token brand is present.
        if len(c_tokens) == 1 and c_tokens[0] in GENERIC_BRAND_TOKENS:
            continue
        if all(t in COLOR_TOKENS for t in c_tokens):
            continue
        # Prefer word-boundary matches to reduce substring false positives.
        if re.search(rf"(?i)\\b{re.escape(c)}\\b", a):
            return cand
        if len(c_tokens) >= 2 and c in a:
            return cand
    return None


def shared_anchor_tokens(supplier_title: str, amazon_title: str, limit: int = 6) -> list[str]:
    sup = set(significant_tokens(tokenize(supplier_title)))
    amz = set(significant_tokens(tokenize(amazon_title)))
    shared = sorted(sup & amz)
    return shared[:limit]


def strong_shared_tokens(shared: Iterable[str], brand_hit: str | None) -> list[str]:
    brand_tokens = set()
    if brand_hit:
        brand_tokens = {t.lower() for t in tokenize(brand_hit)}
    out: list[str] = []
    for t in shared:
        if t in LOW_SIGNAL_SHARED_TOKENS:
            continue
        if t in brand_tokens:
            continue
        out.append(t)
    return out


def capacity_ml(title: str) -> float | None:
    t = _as_text(title).lower()
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|litres)\b", t)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2)
    if unit == "ml":
        return val
    return val * 1000.0


def within_capacity_tolerance(supplier_title: str, amazon_title: str, tol: float = 0.30) -> bool:
    s = capacity_ml(supplier_title)
    a = capacity_ml(amazon_title)
    if s is None or a is None:
        return False
    if s <= 0 or a <= 0:
        return False
    return abs(a - s) / max(s, a) <= tol


@dataclass(frozen=True)
class PackAnalysis:
    supplier_qty: int
    amazon_qty: int
    rsu: int
    verdict: str
    adjusted_profit: float
    ratio_known: bool


def analyze_pack(
    supplier_title: str, amazon_title: str, supplier_price: float, net_profit: float
) -> PackAnalysis:
    sup_qty, sup_ev = extract_pack_qty(supplier_title)
    amz_qty, amz_ev = extract_pack_qty(amazon_title)

    ratio_known = True
    rsu = 1

    if sup_qty <= 0:
        sup_qty = 1
    if amz_qty <= 0:
        amz_qty = 1

    if amz_qty == sup_qty:
        verdict = "1:1 Match"
    elif amz_qty > sup_qty:
        if amz_qty % sup_qty == 0:
            rsu = amz_qty // sup_qty
            verdict = f"BUNDLE (Amazon {amz_qty} vs Supplier {sup_qty}); RSU={rsu}"
        else:
            ratio_known = False
            verdict = f"Pack ratio unclear (Amazon {amz_qty} vs Supplier {sup_qty})"
    else:
        # Supplier pack bigger than Amazon unit; splitting is operationally possible but risky/ambiguous.
        ratio_known = False
        verdict = f"SPLIT risk (Supplier {sup_qty} vs Amazon {amz_qty})"

    dim_note = None
    if has_dimension_or_measurement(supplier_title) or has_dimension_or_measurement(amazon_title):
        dim_note = "Dimension Shield"

    # Dimension shield: never penalize based on dimension-like patterns.
    if dim_note and (sup_ev == "dimensions (not pack)" or amz_ev == "dimensions (not pack)"):
        rsu = 1
        ratio_known = True
        verdict = "1:1 Match (Dimension Shield)"

    adjusted_profit = net_profit
    if ratio_known and rsu > 1 and not (math.isnan(supplier_price) or math.isnan(net_profit)):
        adjusted_profit = net_profit - (supplier_price * (rsu - 1))

    return PackAnalysis(
        supplier_qty=sup_qty,
        amazon_qty=amz_qty,
        rsu=rsu,
        verdict=verdict,
        adjusted_profit=adjusted_profit,
        ratio_known=ratio_known,
    )


def detect_supplier_domain(df: pd.DataFrame) -> str:
    if "SupplierURL" not in df.columns:
        return "-"
    for v in df["SupplierURL"].dropna().astype(str).tolist():
        v = v.strip()
        if not v:
            continue
        try:
            host = urlparse(v).netloc
        except Exception:
            host = ""
        if host:
            return host
    return "-"


def ip_risk_flag(supplier_title: str, amazon_title: str) -> str | None:
    t = f"{_as_text(supplier_title)} {_as_text(amazon_title)}".lower()
    for b in LUXURY_IP_BRANDS:
        if b in t:
            return b
    return None


def confidence_score(
    is_exact_ean_strict: bool,
    brand_hit: str | None,
    shared: list[str],
    title_similarity: float,
    has_assorted: bool,
) -> int:
    if is_exact_ean_strict:
        base = 95
        if has_assorted:
            base -= 5
        return max(60, min(95, base))

    score = 40
    if brand_hit:
        score += 25
    score += min(20, 5 * len(shared))
    score += int(round(title_similarity * 10))
    if has_assorted:
        score -= 10
    return max(0, min(90, score))


def title_similarity_ratio(a: str, b: str) -> float:
    # Lightweight similarity; avoids importing difflib for speed/verbosity in this script.
    a_tokens = significant_tokens(tokenize(a))
    b_tokens = significant_tokens(tokenize(b))
    if not a_tokens or not b_tokens:
        return 0.0
    a_set = set(a_tokens)
    b_set = set(b_tokens)
    inter = len(a_set & b_set)
    union = len(a_set | b_set)
    return inter / union if union else 0.0


def build_row_record(row: pd.Series, row_id: int) -> dict[str, Any]:
    supplier_title = _as_text(row.get("SupplierTitle"))
    amazon_title = _as_text(row.get("AmazonTitle"))
    asin = _as_text(row.get("ASIN"))

    sup_e = barcode_result(row.get("EAN"))
    amz_e = barcode_result(row.get("EAN_OnPage"))

    supplier_price = _to_float(row.get("SupplierPrice_incVAT"))
    selling_price = _to_float(row.get("SellingPrice_incVAT"))
    net_profit = _to_float(row.get("NetProfit"))
    roi = _to_float(row.get("ROI"))

    sales = parse_sales(row.get("sales"))

    is_exact_ean_strict = (
        sup_e.strict_valid
        and amz_e.strict_valid
        and sup_e.normalized
        and sup_e.normalized == amz_e.normalized
    )

    shared = shared_anchor_tokens(supplier_title, amazon_title)
    shared_strong = strong_shared_tokens(shared, brand_hit)
    brand_hit = brand_matches(supplier_title, amazon_title)
    assorted = ("assorted" in supplier_title.lower()) or ("assorted" in amazon_title.lower())
    sim = title_similarity_ratio(supplier_title, amazon_title)

    pack = analyze_pack(supplier_title, amazon_title, supplier_price, net_profit)
    cap_tol = within_capacity_tolerance(supplier_title, amazon_title)
    ip_risk = ip_risk_flag(supplier_title, amazon_title)

    supplier_ean_out = sup_e.normalized if sup_e.strict_valid else "-"
    amazon_ean_out = amz_e.normalized if amz_e.strict_valid else "-"

    # Output schema fields
    supplier_title_out = f"[{row_id}] {truncate(supplier_title)}"
    amazon_title_out = truncate(amazon_title)

    confidence = confidence_score(
        is_exact_ean_strict=is_exact_ean_strict,
        brand_hit=brand_hit,
        shared=shared,
        title_similarity=sim,
        has_assorted=assorted,
    )

    return {
        "RowID": row_id,
        "SupplierTitleFull": supplier_title,
        "AmazonTitleFull": amazon_title,
        "SupplierTitle": supplier_title_out,
        "AmazonTitle": amazon_title_out,
        "SupplierEAN": supplier_ean_out,
        "AmazonEAN": amazon_ean_out,
        "ASIN": asin if asin else "-",
        "SupplierPrice": fmt_gbp(supplier_price),
        "SellingPrice": fmt_gbp(selling_price),
        "NetProfitValue": net_profit,
        "NetProfit": fmt_gbp(net_profit),
        "ROIValue": roi,
        "ROI": fmt_roi(roi),
        "SalesValue": sales,
        "Sales": fmt_int(sales),
        "PackVerdict": pack.verdict,
        "AdjustedProfitValue": pack.adjusted_profit,
        "AdjustedProfit": fmt_gbp(pack.adjusted_profit),
        "Confidence": confidence,
        "is_exact_ean_strict": is_exact_ean_strict,
        "brand_hit": brand_hit,
        "shared": shared,
        "shared_strong": shared_strong,
        "sim": sim,
        "assorted": assorted,
        "cap_tol": cap_tol,
        "ip_risk": ip_risk,
        "pack_ratio_known": pack.ratio_known,
        "rsu": pack.rsu,
    }


TABLE_COLS = [
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


def format_table(rows: list[dict[str, str]]) -> str:
    widths: dict[str, int] = {c: len(c) for c in TABLE_COLS}
    for r in rows:
        for c in TABLE_COLS:
            widths[c] = max(widths[c], len(_as_text(r.get(c, ""))))

    def fmt_row(vals: dict[str, str]) -> str:
        parts = []
        for c in TABLE_COLS:
            parts.append(_as_text(vals.get(c, "")).ljust(widths[c]))
        return "| " + " | ".join(parts) + " |"

    header = fmt_row({c: c for c in TABLE_COLS})
    sep = "|-" + "-|-".join("-" * widths[c] for c in TABLE_COLS) + "-|"
    body = "\n".join(fmt_row(r) for r in rows)
    return "\n".join([header, sep, body]) if body else "\n".join([header, sep])


def should_include_as_candidate(rec: dict[str, Any]) -> bool:
    # Reject obvious mismatches: no usable shared anchors, no brand hit, and no strict EAN.
    if rec["is_exact_ean_strict"]:
        return True
    if rec["brand_hit"] and len(rec["shared_strong"]) >= 1:
        return True
    if len(rec["shared_strong"]) >= 2:
        return True
    return False


def categorize(rec: dict[str, Any]) -> tuple[str | None, dict[str, str] | None]:
    sales = rec["SalesValue"]
    net_profit = rec["NetProfitValue"]
    adj_profit = rec["AdjustedProfitValue"]
    roi = rec["ROIValue"]

    if not should_include_as_candidate(rec):
        return None, None

    supplier_ean = rec["SupplierEAN"]
    amazon_ean = rec["AmazonEAN"]
    is_exact = rec["is_exact_ean_strict"]
    shared = rec["shared"]
    shared_strong = rec["shared_strong"]
    brand_hit = rec["brand_hit"]
    assorted = rec["assorted"]
    cap_tol = rec["cap_tol"]
    ip_risk = rec["ip_risk"]
    pack_ratio_known = rec["pack_ratio_known"]

    def evidence_tokens() -> str:
        if is_exact:
            extras = "; ".join(shared[:4]) if shared else "-"
            if extras != "-":
                return f"Exact EAN match ({supplier_ean}); shared: {extras}"
            return f"Exact EAN match ({supplier_ean})"
        tokens = ", ".join(shared[:5]) if shared else "-"
        if brand_hit and tokens != "-":
            return f"shared: {tokens}; brand: {brand_hit}"
        if brand_hit:
            return f"brand: {brand_hit}"
        return f"shared: {tokens}"

    # Profit gating for recommended tables
    profitable = (
        not (math.isnan(net_profit) or math.isnan(adj_profit)) and net_profit > 0 and adj_profit > 0
    )

    has_sales = sales > 0

    # For v4 non-EAN recommendations, apply a finance floor to reduce false positives.
    meets_finance_floor = (
        not (math.isnan(net_profit) or math.isnan(roi)) and net_profit > 0.50 and roi > 15.0
    )

    # Pack sanity gating: if ratio is unknown and not exact EAN, do not recommend.
    pack_ok_for_recommend = is_exact or pack_ratio_known

    confidence = rec["Confidence"]

    # VERIFIED: strict exact EAN, default to VERIFIED unless explicit pack contradiction makes adjusted profit <= 0.
    if is_exact:
        if adj_profit <= 0 or net_profit <= 0:
            row = {
                "Verdict": "FILTERED OUT",
                "Confidence": str(confidence),
                "SupplierTitle": rec["SupplierTitle"],
                "AmazonTitle": rec["AmazonTitle"],
                "Supplier EAN": supplier_ean,
                "Amazon EAN": amazon_ean,
                "ASIN": rec["ASIN"],
                "SupplierPrice": rec["SupplierPrice"],
                "SellingPrice": rec["SellingPrice"],
                "NetProfit": rec["NetProfit"],
                "ROI": rec["ROI"],
                "Sales": rec["Sales"],
                "Pack Verdict": rec["PackVerdict"],
                "Adjusted Profit": rec["AdjustedProfit"],
                "Key Match Evidence": evidence_tokens(),
                "Filter Reason": "Adjusted profit ≤ 0 (pack/profit gating)",
            }
            return "FILTERED_OUT", row

        if not has_sales:
            row = {
                "Verdict": "NEEDS VERIFICATION",
                "Confidence": str(confidence),
                "SupplierTitle": rec["SupplierTitle"],
                "AmazonTitle": rec["AmazonTitle"],
                "Supplier EAN": supplier_ean,
                "Amazon EAN": amazon_ean,
                "ASIN": rec["ASIN"],
                "SupplierPrice": rec["SupplierPrice"],
                "SellingPrice": rec["SellingPrice"],
                "NetProfit": rec["NetProfit"],
                "ROI": rec["ROI"],
                "Sales": rec["Sales"],
                "Pack Verdict": rec["PackVerdict"],
                "Adjusted Profit": rec["AdjustedProfit"],
                "Key Match Evidence": evidence_tokens(),
                "Filter Reason": "Sales=0: confirm demand; EAN match otherwise strong",
            }
            return "NEEDS_VERIFICATION", row

        row = {
            "Verdict": "VERIFIED",
            "Confidence": "95" if confidence >= 95 else str(confidence),
            "SupplierTitle": rec["SupplierTitle"],
            "AmazonTitle": rec["AmazonTitle"],
            "Supplier EAN": supplier_ean,
            "Amazon EAN": amazon_ean,
            "ASIN": rec["ASIN"],
            "SupplierPrice": rec["SupplierPrice"],
            "SellingPrice": rec["SellingPrice"],
            "NetProfit": rec["NetProfit"],
            "ROI": rec["ROI"],
            "Sales": rec["Sales"],
            "Pack Verdict": rec["PackVerdict"],
            "Adjusted Profit": rec["AdjustedProfit"],
            "Key Match Evidence": evidence_tokens(),
            "Filter Reason": "-",
        }
        return "VERIFIED", row

    # Non-EAN candidates:
    strong_title = bool(brand_hit) and len(shared_strong) >= 2
    plausible_title = (len(shared_strong) >= 2) or (brand_hit is not None and len(shared_strong) >= 1)

    if assorted:
        strong_title = False

    # FILTERED OUT: confirmed (strong_title) but unprofitable after pack.
    if plausible_title and (math.isnan(adj_profit) or adj_profit <= 0):
        row = {
            "Verdict": "FILTERED OUT",
            "Confidence": str(confidence),
            "SupplierTitle": rec["SupplierTitle"],
            "AmazonTitle": rec["AmazonTitle"],
            "Supplier EAN": supplier_ean,
            "Amazon EAN": amazon_ean,
            "ASIN": rec["ASIN"],
            "SupplierPrice": rec["SupplierPrice"],
            "SellingPrice": rec["SellingPrice"],
            "NetProfit": rec["NetProfit"],
            "ROI": rec["ROI"],
            "Sales": rec["Sales"],
            "Pack Verdict": rec["PackVerdict"],
            "Adjusted Profit": rec["AdjustedProfit"],
            "Key Match Evidence": evidence_tokens(),
            "Filter Reason": "Adjusted profit ≤ 0 after pack sanity",
        }
        return "FILTERED_OUT", row

    # HIGHLY LIKELY: strong brand+product anchors, profitable, pack verified, and sales>0.
    if strong_title and profitable and meets_finance_floor and pack_ok_for_recommend and has_sales:
        row = {
            "Verdict": "HIGHLY LIKELY",
            "Confidence": str(max(70, min(90, confidence))),
            "SupplierTitle": rec["SupplierTitle"],
            "AmazonTitle": rec["AmazonTitle"],
            "Supplier EAN": supplier_ean,
            "Amazon EAN": amazon_ean,
            "ASIN": rec["ASIN"],
            "SupplierPrice": rec["SupplierPrice"],
            "SellingPrice": rec["SellingPrice"],
            "NetProfit": rec["NetProfit"],
            "ROI": rec["ROI"],
            "Sales": rec["Sales"],
            "Pack Verdict": rec["PackVerdict"],
            "Adjusted Profit": rec["AdjustedProfit"],
            "Key Match Evidence": evidence_tokens(),
            "Filter Reason": "-",
        }
        return "HIGHLY_LIKELY", row

    # NEEDS VERIFICATION: selective and upgradeable by 1–2 details; must be profitable after pack sanity.
    if not profitable:
        return None, None

    if ip_risk:
        # Softened: route to Needs Verification if uncertain.
        filter_reason = f"IP risk check: brand '{ip_risk}' appears; confirm listing safety"
    else:
        filter_reason = "-"

    # High-level eligibility for Needs Verification.
    if not meets_finance_floor:
        return None, None

    if not (plausible_title or cap_tol):
        return None, None

    if not has_sales and not strong_title:
        # Sales=0 only kept when match is very strong.
        return None, None

    if not pack_ratio_known:
        need_reason = "Confirm pack: ratio unclear from titles"
    elif cap_tol:
        need_reason = "Minor capacity variance (≤30%): confirm same SKU"
    elif brand_hit is None:
        need_reason = "Brand not visible in Amazon title: confirm packaging/brand"
    else:
        need_reason = "Confirm 1 detail: variant/model/pack matches"

    if filter_reason != "-":
        need_reason = f"{need_reason}; {filter_reason}"

    row = {
        "Verdict": "NEEDS VERIFICATION",
        "Confidence": str(max(50, min(85, confidence))),
        "SupplierTitle": rec["SupplierTitle"],
        "AmazonTitle": rec["AmazonTitle"],
        "Supplier EAN": supplier_ean,
        "Amazon EAN": amazon_ean,
        "ASIN": rec["ASIN"],
        "SupplierPrice": rec["SupplierPrice"],
        "SellingPrice": rec["SellingPrice"],
        "NetProfit": rec["NetProfit"],
        "ROI": rec["ROI"],
        "Sales": rec["Sales"],
        "Pack Verdict": rec["PackVerdict"],
        "Adjusted Profit": rec["AdjustedProfit"],
        "Key Match Evidence": evidence_tokens(),
        "Filter Reason": need_reason,
    }
    return "NEEDS_VERIFICATION", row


def sort_key_for_bucket(bucket: str, r: dict[str, str]) -> tuple:
    def parse_int_field(v: str) -> int:
        m = re.search(r"-?\d+", _as_text(v))
        return int(m.group(0)) if m else 0

    def parse_money(v: str) -> float:
        s = _as_text(v).replace("£", "").strip()
        try:
            return float(s)
        except ValueError:
            return -1e9

    if bucket == "VERIFIED":
        return (-parse_int_field(r["Sales"]), -parse_money(r["Adjusted Profit"]))
    if bucket == "HIGHLY_LIKELY":
        return (-int(_as_text(r["Confidence"]) or "0"), -parse_int_field(r["Sales"]))
    if bucket == "NEEDS_VERIFICATION":
        return (-parse_int_field(r["Sales"]), -parse_money(r["Adjusted Profit"]))
    if bucket == "FILTERED_OUT":
        return (parse_money(r["Adjusted Profit"]), -parse_int_field(r["Sales"]))
    return (0,)


def main() -> Path:
    if not INPUT_XLSX.exists():
        raise FileNotFoundError(str(INPUT_XLSX))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read with dtype=str to reduce Excel scientific-notation corruption for barcodes; we still apply strict validity.
    df = pd.read_excel(INPUT_XLSX, dtype=str)

    # Sales normalization
    if "sales_numeric" in df.columns:
        df["sales"] = df["sales_numeric"]
    elif "bought_in_past_month" in df.columns:
        df["sales"] = df["bought_in_past_month"]
    else:
        df["sales"] = 0

    supplier = detect_supplier_domain(df)
    total_rows = len(df)

    buckets: dict[str, list[dict[str, str]]] = {
        "VERIFIED": [],
        "HIGHLY_LIKELY": [],
        "NEEDS_VERIFICATION": [],
        "FILTERED_OUT": [],
    }

    categorized_count = 0
    for idx, row in df.iterrows():
        row_id = int(idx) + 1
        rec = build_row_record(row, row_id=row_id)
        bucket, out_row = categorize(rec)
        if bucket is None or out_row is None:
            continue
        categorized_count += 1
        buckets[bucket].append(out_row)

    for b in buckets:
        buckets[b].sort(key=lambda r, bb=b: sort_key_for_bucket(bb, r))

    not_listed = total_rows - categorized_count

    generated = datetime.now(TZ).date().isoformat()
    yyyymmdd = generated.replace("-", "")
    out_path = OUTPUT_DIR / f"PHASEA_MANUAL_REPORT_{yyyymmdd}.md"

    summary = {
        "VERIFIED": len(buckets["VERIFIED"]),
        "HIGHLY LIKELY": len(buckets["HIGHLY_LIKELY"]),
        "NEEDS VERIFICATION": len(buckets["NEEDS_VERIFICATION"]),
        "FILTERED OUT": len(buckets["FILTERED_OUT"]),
    }

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT")
    lines.append("")
    lines.append(f"**Generated:** {generated}")
    lines.append(f"**Input File:** {INPUT_XLSX}")
    lines.append(f"**Supplier:** {supplier}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append(f"- VERIFIED: {summary['VERIFIED']}")
    lines.append(f"- HIGHLY LIKELY: {summary['HIGHLY LIKELY']}")
    lines.append(f"- NEEDS VERIFICATION: {summary['NEEDS VERIFICATION']}")
    lines.append(f"- FILTERED OUT: {summary['FILTERED OUT']}")
    lines.append(f"- TOTAL ANALYZED: {categorized_count}")
    lines.append("")
    lines.append(
        "This report applies v4.0 Thorough Manual Analysis: strict EAN validity (checksum + left-padding), "
        "dimension/measurement shielding for pack parsing, and selective NEEDS VERIFICATION."
    )
    lines.append(
        "Long titles are truncated inside tables for readability; the `[RowID]` prefix in `SupplierTitle` preserves traceability."
    )
    lines.append(
        "VERIFIED and HIGHLY LIKELY enforce Sales>0, NetProfit>0, and Adjusted Profit>0; unprofitable confirmed cases go to FILTERED OUT."
    )
    lines.append("")

    def section(title: str, bucket_key: str) -> None:
        rows = buckets[bucket_key]
        lines.append(f"## {title} (count={len(rows)})")
        lines.append("")
        lines.append("```text")
        lines.append(format_table(rows))
        lines.append("```")
        lines.append("")

    section("VERIFIED", "VERIFIED")
    section("HIGHLY LIKELY", "HIGHLY_LIKELY")
    section("NEEDS VERIFICATION", "NEEDS_VERIFICATION")
    section("FILTERED OUT", "FILTERED_OUT")

    lines.append("## Reconciliation")
    lines.append(f"- Total rows in input: {total_rows}")
    lines.append(
        f"- Rows analyzed and categorized: {summary['VERIFIED']} + {summary['HIGHLY LIKELY']} + {summary['NEEDS VERIFICATION']} + {summary['FILTERED OUT']} = {categorized_count}"
    )
    lines.append(f"- Not listed (weak evidence / category mismatch): {not_listed}")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    p = main()
    print(str(p))
