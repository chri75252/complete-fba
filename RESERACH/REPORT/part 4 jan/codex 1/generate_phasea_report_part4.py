from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from difflib import SequenceMatcher


REPO_ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)
INPUT_PATH = REPO_ROOT / r"RESERACH\REPORT\part 4 jan\part 4 jan.xlsx"
OUTPUT_DIR = REPO_ROOT / r"RESERACH\REPORT\part 4 jan\codex 1"
OUTPUT_PATH = OUTPUT_DIR / f"PHASEA_MANUAL_REPORT_{date.today().strftime('%Y%m%d')}.md"


# --- CALIBRATION CONFIGURATION (from part 3 jan preflight; SupplierURL=www.efghousewares.co.uk) ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pack of", "piece", "pieces", "set of"],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": [
        "cm",
        "mm",
        "m",
        "ml",
        "l",
        "ltr",
        "litre",
        "cl",
        "g",
        "kg",
        "oz",
        "inch",
        "in",
        "ft",
    ],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "binocular", "scope", "times"],
    "table_pipe_sanitization": True,
}
# -----------------------------------------------------------------------------------------------


STOPWORDS = {
    "the",
    "and",
    "with",
    "for",
    "of",
    "to",
    "in",
    "on",
    "by",
    "a",
    "an",
    "pack",
    "set",
    "assorted",
    "each",
    "new",
    "sale",
    "uk",
    "christmas",
    "festive",
    "unique",
}

MEASUREMENT_UNITS = {
    "cm",
    "mm",
    "m",
    "ml",
    "l",
    "ltr",
    "litre",
    "liter",
    "cl",
    "g",
    "kg",
    "oz",
    "inch",
    "in",
    "ft",
    "w",
    "kw",
    "led",
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


def _coerce_to_intlike_string(x) -> str:
    if pd.isna(x):
        return ""
    if isinstance(x, (np.integer, int)):
        return str(int(x))
    if isinstance(x, (np.floating, float)):
        if not np.isfinite(x):
            return ""
        if abs(x - round(x)) < 1e-6:
            return str(int(round(x)))
        return str(x)
    return str(x)


def clean_to_digits(x) -> str:
    s = _coerce_to_intlike_string(x).strip()
    if not s:
        return ""
    if "e" in s.lower():
        return ""
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


def normalize_ean(digits: str) -> str:
    if not isinstance(digits, str) or not digits.isdigit():
        return ""
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
    norm = normalize_ean(digits)
    if not isinstance(norm, str) or not norm.isdigit():
        return False
    if len(norm) not in (8, 12, 13, 14):
        return False
    if re.search(r"0{6,}$", norm):
        return False
    return gtin_checksum_ok(norm)


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def sanitize_cell(text: str) -> str:
    s = str(text or "").replace("\n", " ").replace("\r", " ").strip()
    if SUPPLIER_NAMING_CONVENTION.get("table_pipe_sanitization", True):
        s = s.replace("|", "/")
    return re.sub(r"\s+", " ", s)


def fmt_money(x: float) -> str:
    try:
        return f"\u00a3{float(x):.2f}"
    except Exception:
        return "\u00a30.00"


def fmt_percent(x: float) -> str:
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return "0.0%"


def tokenize(title: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", str(title).lower())
    out: list[str] = []
    for w in words:
        if len(w) < 3:
            continue
        if w in STOPWORDS:
            continue
        if w in MEASUREMENT_UNITS:
            continue
        out.append(w)
    return out


def shared_tokens(a: str, b: str) -> list[str]:
    sa = set(tokenize(a))
    sb = set(tokenize(b))
    return sorted(sa & sb)


def first_token(title: str) -> str:
    t = str(title or "").strip()
    if not t:
        return ""
    tok = re.split(r"\s+", t, maxsplit=1)[0]
    return re.sub(r"[^A-Za-z0-9]", "", tok)


def first_two_tokens(title: str) -> str:
    t = str(title or "").strip()
    if not t:
        return ""
    parts = re.findall(r"[A-Za-z0-9]+", t)
    if len(parts) < 2:
        return first_token(title)
    a = re.sub(r"[^A-Za-z0-9]", "", parts[0])
    b = re.sub(r"[^A-Za-z0-9]", "", parts[1])
    if len(a) < 3 or len(b) < 3:
        return first_token(title)
    return f"{a} {b}"


def brand_candidates(title: str) -> list[str]:
    """
    Best-effort brand candidates from the start of SupplierTitle (per calibration brand_position='start').
    Skips numeric-only tokens, stopwords, and measurement/spec tokens.
    """
    parts = re.findall(r"[A-Za-z0-9]+", str(title or ""))
    cleaned: list[str] = []
    for p in parts:
        pl = p.lower()
        if pl.isdigit():
            continue
        if len(pl) < 3:
            continue
        if pl in STOPWORDS:
            continue
        if pl in MEASUREMENT_UNITS:
            continue
        cleaned.append(p)
        if len(cleaned) >= 2:
            break
    if not cleaned:
        return []
    out = [cleaned[0]]
    if len(cleaned) >= 2:
        out.insert(0, f"{cleaned[0]} {cleaned[1]}")
    return out


def brand_match_token(supplier_title: str, amazon_title: str) -> str:
    """
    Returns the matched brand token/phrase (from SupplierTitle candidates) if found in AmazonTitle; else "".
    """
    amz = str(amazon_title or "").lower()
    for cand in brand_candidates(supplier_title):
        c = cand.lower()
        if " " in c:
            if c in amz:
                return cand
        else:
            if re.search(rf"\\b{re.escape(c)}\\b", amz):
                return cand
    return ""


# --- Pack parsing (calibrated) ---
DIM_KWS = tuple(SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"])
SPEC_X_KWS = tuple(SUPPLIER_NAMING_CONVENTION["spec_x_shield_keywords"])

RE_SUP_PACK_OF = re.compile(r"\bpack\s*of\s*(\d+)\b", re.I)
RE_SUP_SET_OF = re.compile(r"\bset\s*of\s*(\d+)\b", re.I)
RE_SUP_PC = re.compile(r"\b(\d+)\s*(?:pc|pcs|pce)\b", re.I)
RE_SUP_PIECES = re.compile(r"\b(\d+)\s*pieces?\b", re.I)
RE_SUP_PK = re.compile(r"\bpk\s*(\d+)\b", re.I)
RE_SUP_N_PACK = re.compile(r"\b(\d+)\s*pack\b", re.I)
RE_SUP_TRAILING_NUM = re.compile(r"\b(\d+)\s*$", re.I)
RE_SUP_TRAILING_RANGE = re.compile(r"\b\d+\s*-\s*\d+\b", re.I)
RE_SUP_DATE_LIKE = re.compile(r"\b\d{1,2}\s*/\s*\d{1,2}\b", re.I)

RE_SUP_NOUN_COUNT = re.compile(
    r"\b(\d+)\s*(?:bags|gloves|balloons|sticks|doil(?:y|ies)|towels|wipes|capsules|tablets|bulbs)\b",
    re.I,
)

RE_AMZ_PACK_OF = re.compile(r"\bpack\s*of\s*(\d+)\b", re.I)
RE_AMZ_N_PACK = re.compile(r"\b(\d+)\s*pack\b", re.I)
RE_AMZ_PCS = re.compile(r"\b(\d+)\s*(?:pcs|pieces|count)\b", re.I)
RE_AMZ_ER_PACK = re.compile(r"\b(\d+)\s*er\s*pack\b", re.I)
RE_AMZ_N_X_WORD = re.compile(r"\b(\d+)\s*[xx]\s*[A-Za-z]", re.I)
RE_AMZ_QTY_X_CAP = re.compile(r"\b(\d+)\s*[xx]\s*(\d+(?:\.\d+)?)\s*(ml|g|kg|l|litre|liter|cl)\b", re.I)
RE_AMZ_QTY_X_QTY = re.compile(r"\b(\d+)\s*[xx]\s*(\d+)\b", re.I)
RE_AMZ_SPEC_2000X = re.compile(r"\b\d{2,5}x\b", re.I)

RE_DIM_NXM = re.compile(r"\b\d+(?:\.\d+)?\s*[xx]\s*\d+(?:\.\d+)?\s*(cm|mm|inch|in|\"|')\b", re.I)
RE_DIM_COMPACT = re.compile(r"\b\d+(?:\.\d+)?[xx]\d+(?:\.\d+)?\s*(cm|mm|inch|in|\"|')\b", re.I)

RE_CAP_SINGLE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|liter|cl|g|kg)\b", re.I)


def _has_spec_x_context(title: str, span: tuple[int, int]) -> bool:
    t = str(title or "").lower()
    s, e = span
    window = t[max(0, s - 24) : min(len(t), e + 24)]
    return any(k in window for k in SPEC_X_KWS)


def _nxm_is_dimension(title: str, span: tuple[int, int]) -> bool:
    t = str(title or "").lower()
    s, e = span
    window = t[max(0, s - 16) : min(len(t), e + 20)]
    if RE_DIM_NXM.search(window) or RE_DIM_COMPACT.search(window):
        return True
    return any(k in window for k in DIM_KWS)


def parse_capacity_per_unit_ml_or_g(title: str) -> tuple[str, float] | None:
    """
    Returns ("ml", value_ml) or ("g", value_g) if a plausible per-unit capacity/weight is found.
    In patterns like "6 x 70ml", per-unit capacity is 70ml (NOT 420ml).
    """
    t = str(title or "")

    m = RE_AMZ_QTY_X_CAP.search(t)
    if m:
        value = float(m.group(2))
        unit = m.group(3).lower()
        if unit in ("l", "ltr", "litre", "liter"):
            return ("ml", value * 1000.0)
        if unit == "cl":
            return ("ml", value * 10.0)
        if unit == "ml":
            return ("ml", value)
        if unit == "kg":
            return ("g", value * 1000.0)
        if unit == "g":
            return ("g", value)

    m = RE_CAP_SINGLE.search(t)
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2).lower()
    if unit in ("l", "ltr", "litre", "liter"):
        return ("ml", value * 1000.0)
    if unit == "cl":
        return ("ml", value * 10.0)
    if unit == "ml":
        return ("ml", value)
    if unit == "kg":
        return ("g", value * 1000.0)
    if unit == "g":
        return ("g", value)
    return None


def capacity_verdict(supplier_title: str, amazon_title: str) -> tuple[str, str]:
    """
    Returns (status, note):
    - status in {"unknown","ok","needs_verification","filtered_out"}

    v4.1.1 tolerance:
    - 0-10%: ok
    - 10-25%: needs_verification
    - >25%: filtered_out
    """
    sup = parse_capacity_per_unit_ml_or_g(supplier_title)
    amz = parse_capacity_per_unit_ml_or_g(amazon_title)
    if not sup or not amz:
        return ("unknown", "No comparable capacity tokens found in both titles")
    if sup[0] != amz[0]:
        return ("needs_verification", f"Capacity units differ ({sup[0]} vs {amz[0]})")
    a = sup[1]
    b = amz[1]
    if a <= 0 or b <= 0:
        return ("unknown", "Non-positive capacity tokens")
    diff = abs(a - b) / max(a, b)
    if diff <= 0.10:
        return ("ok", f"Capacity within 10% ({a:.0f}{sup[0]} vs {b:.0f}{amz[0]})")
    if diff <= 0.25:
        return ("needs_verification", f"Capacity differs 10-25% ({a:.0f}{sup[0]} vs {b:.0f}{amz[0]})")
    if diff <= 0.50:
        return ("filtered_out", f"Capacity differs 25-50% ({a:.0f}{sup[0]} vs {b:.0f}{amz[0]})")
    return ("filtered_out", f"Capacity differs >50% ({a:.0f}{sup[0]} vs {b:.0f}{amz[0]})")


@dataclass(frozen=True)
class PackParse:
    supplier_inner_qty: int
    supplier_evidence: str
    amazon_units: int
    amazon_total_items: int
    amazon_evidence: str
    rsu: int
    pack_verdict: str


def extract_supplier_inner_qty(title: str) -> tuple[int, str, str]:
    t = str(title or "")
    for rg, kind in (
        (RE_SUP_PACK_OF, "PACK OF"),
        (RE_SUP_SET_OF, "SET OF"),
        (RE_SUP_PC, "PC/PCS/PCE"),
        (RE_SUP_PIECES, "PIECES"),
        (RE_SUP_PK, "PK#"),
        (RE_SUP_N_PACK, "N PACK"),
        (RE_SUP_NOUN_COUNT, "N NOUN"),
    ):
        m = rg.search(t)
        if m:
            nums = [g for g in m.groups() if g]
            if nums:
                return int(nums[0]), m.group(0), kind
    if SUPPLIER_NAMING_CONVENTION.get("allow_trailing_number_as_qty", False):
        m = RE_SUP_TRAILING_NUM.search(t)
        if m and not RE_SUP_TRAILING_RANGE.search(t) and not RE_SUP_DATE_LIKE.search(t):
            n = int(m.group(1))
            if n >= 10 and not any(u in t.lower() for u in DIM_KWS):
                return n, m.group(0), "TRAILING #"
    return 1, "", ""


def extract_amazon_units_and_total(title: str) -> tuple[int, int, str, str]:
    t = str(title or "")
    m_spec = RE_AMZ_SPEC_2000X.search(t)
    if m_spec and _has_spec_x_context(t, m_spec.span()):
        return 1, 1, "", "SPEC X"

    m = RE_AMZ_QTY_X_CAP.search(t)
    if m and not _has_spec_x_context(t, m.span()):
        outer = int(m.group(1))
        if outer > 1:
            return outer, outer, m.group(0), "N x CAP"

    m = RE_AMZ_QTY_X_QTY.search(t)
    if m and not _nxm_is_dimension(t, m.span()) and not _has_spec_x_context(t, m.span()):
        outer = int(m.group(1))
        inner = int(m.group(2))
        if 1 < outer < 500 and 1 < inner < 500:
            return outer, outer * inner, m.group(0), "N x N"

    for rg, kind in ((RE_AMZ_PACK_OF, "PACK OF"), (RE_AMZ_N_PACK, "N PACK"), (RE_AMZ_ER_PACK, "ER PACK"), (RE_AMZ_PCS, "PCS/COUNT")):
        m = rg.search(t)
        if m:
            nums = [g for g in m.groups() if g]
            if nums:
                n = int(nums[0])
                if 1 < n < 500:
                    return n, n, m.group(0), kind

    m = RE_AMZ_N_X_WORD.search(t)
    if m and not _nxm_is_dimension(t, m.span()) and not _has_spec_x_context(t, m.span()):
        n = int(m.group(1))
        if 1 < n < 500:
            return n, n, m.group(0), "N x WORD"

    return 1, 1, "", ""


def parse_pack(supplier_title: str, amazon_title: str) -> PackParse:
    sup_qty, sup_ev, _sup_kind = extract_supplier_inner_qty(supplier_title)
    amz_units, amz_total, amz_ev, _amz_kind = extract_amazon_units_and_total(amazon_title)

    rsu = 1
    if sup_qty > 0:
        rsu = int(math.ceil(amz_total / sup_qty))
        rsu = max(1, rsu)

    ratio = (amz_total / sup_qty) if sup_qty > 0 else 1.0
    if ratio < 0.85 and sup_qty > 1 and amz_total >= 1:
        verdict = f"SPLIT CANDIDATE (Amazon {amz_total} < Supplier {sup_qty})"
        rsu = 1
    elif rsu == 1:
        verdict = "1:1 Match"
    else:
        verdict = f"BUNDLE (RSU={rsu})"
    return PackParse(
        supplier_inner_qty=sup_qty,
        supplier_evidence=sup_ev,
        amazon_units=amz_units,
        amazon_total_items=amz_total,
        amazon_evidence=amz_ev,
        rsu=rsu,
        pack_verdict=verdict,
    )


def adjusted_profit(net_profit: float, supplier_cost: float, rsu: int) -> float:
    if rsu <= 1:
        return net_profit
    return net_profit - supplier_cost * (rsu - 1)


def has_explicit_pack_number(title: str) -> list[int]:
    t = str(title or "")
    nums: list[int] = []
    for rg in (RE_SUP_PACK_OF, RE_SUP_SET_OF, RE_SUP_PC, RE_SUP_PIECES, RE_SUP_PK, RE_AMZ_PACK_OF, RE_AMZ_N_PACK, RE_AMZ_PCS):
        for m in rg.finditer(t):
            for g in m.groups():
                if g and g.isdigit():
                    nums.append(int(g))
    m = RE_AMZ_QTY_X_CAP.search(t)
    if m:
        nums.append(int(m.group(1)))
    m = RE_AMZ_QTY_X_QTY.search(t)
    if m and not _nxm_is_dimension(t, m.span()) and not _has_spec_x_context(t, m.span()):
        nums.extend([int(m.group(1)), int(m.group(2))])
    return nums


@dataclass
class RowOut:
    verdict: str
    confidence: int
    rowid: int
    supplier_title_raw: str
    amazon_title_raw: str
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
    sim: float


HEADERS = [
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


def money_to_float(s: str) -> float:
    t = str(s).strip().replace("\u00a3", "").replace("£", "").replace("ś", "").strip()
    try:
        return float(t)
    except Exception:
        return 0.0


def fixed_width_table(rows: list[RowOut]) -> str:
    matrix: list[list[str]] = []
    for r in rows:
        matrix.append(
            [
                r.verdict,
                str(r.confidence),
                r.supplier_title,
                r.amazon_title,
                r.supplier_ean,
                r.amazon_ean,
                r.asin,
                r.supplier_price,
                r.selling_price,
                r.net_profit,
                r.roi,
                r.sales,
                r.pack_verdict,
                r.adjusted_profit,
                r.key_match_evidence,
                r.filter_reason,
            ]
        )
    widths = [len(h) for h in HEADERS]
    for row in matrix:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells: Iterable[str]) -> str:
        parts = []
        for i, c in enumerate(cells):
            parts.append(c.ljust(widths[i]))
        return "| " + " | ".join(parts) + " |"

    sep = "|-" + "-|-".join("-" * w for w in widths) + "-|"
    out = [fmt_row(HEADERS), sep]
    out.extend(fmt_row(r) for r in matrix)
    return "\n".join(out)


def _pick_column(df: pd.DataFrame, preferred_names: list[str]) -> str | None:
    cols = {str(c).strip().lower(): str(c) for c in df.columns}
    for name in preferred_names:
        key = name.strip().lower()
        if key in cols:
            return cols[key]
    return None


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(INPUT_PATH)
    df["RowID"] = df.index + 1

    sales_col = SUPPLIER_NAMING_CONVENTION.get("sales_column", "bought_in_past_month")
    df["Sales"] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0) if sales_col in df.columns else 0

    roi_col = _pick_column(df, ["ROI", "ROI %", "ROI % ", "ROI ( % )", "ROI ( % ) "])
    if not roi_col:
        roi_col = next((c for c in df.columns if str(c).strip().lower().startswith("roi")), None)
    df["ROI_num"] = pd.to_numeric(df.get(roi_col, 0), errors="coerce").fillna(0.0)

    df["EAN_digits"] = df["EAN"].apply(clean_to_digits) if "EAN" in df.columns else ""
    df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(clean_to_digits) if "EAN_OnPage" in df.columns else ""
    df["EAN_norm"] = df["EAN_digits"].apply(normalize_ean)
    df["EAN_OnPage_norm"] = df["EAN_OnPage_digits"].apply(normalize_ean)
    df["EAN_strict_valid"] = df["EAN_norm"].apply(is_strict_valid_barcode)
    df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_norm"].apply(is_strict_valid_barcode)
    df["is_exact_ean_strict"] = (
        df["EAN_strict_valid"] & df["EAN_OnPage_strict_valid"] & (df["EAN_norm"] == df["EAN_OnPage_norm"])
    )

    df["title_sim"] = [
        title_similarity(a, b) for a, b in df[["SupplierTitle", "AmazonTitle"]].fillna("").astype(str).values
    ]
    df["brand_tok_match"] = df.apply(lambda r: brand_match_token(r.get("SupplierTitle", ""), r.get("AmazonTitle", "")), axis=1)
    df["brand_in_amz"] = df["brand_tok_match"].astype(str).str.len() > 0

    verified_rec: list[RowOut] = []
    verified_filt: list[RowOut] = []
    hl_rec: list[RowOut] = []
    hl_filt: list[RowOut] = []
    needs_ver: list[RowOut] = []
    unrelated_candidates: list[dict[str, object]] = []

    def fnum(x: object) -> float:
        try:
            v = float(x)  # type: ignore[arg-type]
        except Exception:
            return 0.0
        return v if math.isfinite(v) else 0.0

    for row in df.to_dict(orient="records"):
        rowid = int(row.get("RowID", 0) or 0)
        sup_title_raw = str(row.get("SupplierTitle", "") or "")
        amz_title_raw = str(row.get("AmazonTitle", "") or "")

        sup_title = sanitize_cell(f"(RowID {rowid}) {sup_title_raw}")
        amz_title = sanitize_cell(amz_title_raw)

        supplier_price = fnum(row.get("SupplierPrice_incVAT", 0))
        selling_price = fnum(row.get("SellingPrice_incVAT", 0))
        net_profit = fnum(row.get("NetProfit", 0))
        roi = fnum(row.get("ROI_num", 0))
        sales = fnum(row.get("Sales", 0))

        sup_ean = row.get("EAN_norm", "") if bool(row.get("EAN_strict_valid", False)) else "-"
        amz_ean = row.get("EAN_OnPage_norm", "") if bool(row.get("EAN_OnPage_strict_valid", False)) else "-"
        asin = sanitize_cell(str(row.get("ASIN", "") or ""))

        sim = float(row.get("title_sim", 0) or 0)
        common = shared_tokens(sup_title_raw, amz_title_raw)
        overlap = len(common)
        common_preview = ", ".join(common[:8]) if common else "-"

        pack = parse_pack(sup_title_raw, amz_title_raw)
        adj = adjusted_profit(net_profit, supplier_price, pack.rsu)
        pack_evidence = f"Pack cues: {pack.supplier_evidence or '-'} / {pack.amazon_evidence or '-'}"

        cap_status, cap_note = capacity_verdict(sup_title_raw, amz_title_raw)

        supplier_price_s = fmt_money(supplier_price)
        selling_price_s = fmt_money(selling_price)
        net_profit_s = fmt_money(net_profit)
        adj_s = fmt_money(adj)
        roi_s = fmt_percent(roi)
        sales_s = str(int(round(sales)))

        is_exact = bool(row.get("is_exact_ean_strict", False))
        strict_mismatch = (sup_ean != "-" and amz_ean != "-" and sup_ean != amz_ean)

        def make_row(verdict: str, confidence: int, evidence: str, filter_reason: str) -> RowOut:
            return RowOut(
                verdict=verdict,
                confidence=confidence,
                rowid=rowid,
                supplier_title_raw=sup_title_raw,
                amazon_title_raw=amz_title_raw,
                supplier_title=sup_title,
                amazon_title=amz_title,
                supplier_ean=sanitize_cell(sup_ean) if sup_ean != "-" else "-",
                amazon_ean=sanitize_cell(amz_ean) if amz_ean != "-" else "-",
                asin=asin,
                supplier_price=supplier_price_s,
                selling_price=selling_price_s,
                net_profit=net_profit_s,
                roi=roi_s,
                sales=sales_s,
                pack_verdict=sanitize_cell(pack.pack_verdict),
                adjusted_profit=adj_s,
                key_match_evidence=sanitize_cell(evidence),
                filter_reason=sanitize_cell(filter_reason),
                sim=sim,
            )

        if is_exact:
            pack_verdict_exact = pack.pack_verdict
            if pack_verdict_exact.startswith("SPLIT CANDIDATE") and not pack.amazon_evidence:
                pack_verdict_exact = "1:1 Match (Exact EAN default; Amazon pack not explicit)"
            if pack_verdict_exact == "1:1 Match" and pack.rsu == 1 and not pack.supplier_evidence and not pack.amazon_evidence:
                pack_verdict_exact = "1:1 Match (Exact EAN default)"

            evidence = f"Exact EAN match; {pack_evidence}"
            if common_preview != "-":
                evidence += f"; Shared anchors: {common_preview}"
            if cap_status != "unknown":
                evidence += f"; {cap_note}"

            if adj <= 0:
                r = make_row("FILTERED OUT", 95, evidence, "Exact EAN match but Adjusted Profit <= 0 after pack recalculation")
                r.pack_verdict = sanitize_cell(pack_verdict_exact)
                verified_filt.append(r)
                continue

            if pack.pack_verdict.startswith("SPLIT CANDIDATE") and pack.amazon_evidence:
                r = make_row(
                    "NEEDS VERIFICATION",
                    90,
                    evidence,
                    "Exact EAN match but pack mismatch suggests split candidate; verify Amazon unit count/pack wording",
                )
                r.pack_verdict = sanitize_cell(pack_verdict_exact)
                needs_ver.append(r)
                continue

            r = make_row("VERIFIED", 95, evidence, "-")
            r.pack_verdict = sanitize_cell(pack_verdict_exact)
            verified_rec.append(r)
            continue

        brand_match = bool(row.get("brand_in_amz", False))
        brand_tok = str(row.get("brand_tok_match", "") or "").strip()
        allow_without_brand = (not brand_match) and (overlap >= 6) and (sim >= 0.65)
        allow_high_sim = (not brand_match) and (sim >= 0.75) and (overlap >= 3)
        plausible = (brand_match and overlap >= 2 and sim >= 0.25) or allow_without_brand or allow_high_sim
        if not plausible:
            unrelated_candidates.append(
                {
                    "rowid": rowid,
                    "supplier_title_raw": sup_title_raw,
                    "amazon_title_raw": amz_title_raw,
                    "supplier_ean": sup_ean,
                    "amazon_ean": amz_ean,
                    "asin": asin,
                    "supplier_price": supplier_price,
                    "selling_price": selling_price,
                    "net_profit": net_profit,
                    "roi": roi,
                    "sales": sales,
                    "sim": sim,
                    "common_preview": common_preview,
                    "overlap": overlap,
                    "pack_evidence": pack_evidence,
                    "cap_status": cap_status,
                    "cap_note": cap_note,
                    "strict_mismatch": strict_mismatch,
                    "brand_match": brand_match,
                }
            )
            continue

        ip_risk = any(b in (sup_title_raw + " " + amz_title_raw).lower() for b in LUXURY_IP_BRANDS)
        anchors = [t for t in common if t.lower() not in {first_token(sup_title_raw).lower()} and not t.isdigit()]
        has_product_anchor = len(anchors) >= 1

        if cap_status == "filtered_out" and brand_match and has_product_anchor:
            hl_filt.append(
                make_row(
                    "FILTERED OUT",
                    80,
                    (
                        f"Brand '{brand_tok}' + anchors: {common_preview}; {cap_note}; {pack_evidence}"
                        if brand_tok
                        else f"Brand + anchors: {common_preview}; {cap_note}; {pack_evidence}"
                    ),
                    "Different SKU indicated by capacity difference (>25%)",
                )
            )
            continue

        if cap_status == "needs_verification":
            needs_ver.append(
                make_row(
                    "NEEDS VERIFICATION",
                    70,
                    f"Shared anchors: {common_preview}; {cap_note}; {pack_evidence}",
                    "Capacity variance needs verification (10-25% tolerance rule)",
                )
            )
            continue

        if strict_mismatch:
            needs_ver.append(
                make_row(
                    "NEEDS VERIFICATION",
                    70,
                    f"EAN mismatch; shared anchors: {common_preview}; {pack_evidence}",
                    "EAN mismatch: confirm barcode/variant/pack",
                )
            )
            continue

        if pack.pack_verdict.startswith("SPLIT CANDIDATE"):
            needs_ver.append(
                make_row(
                    "NEEDS VERIFICATION",
                    70,
                    f"Split candidate; shared anchors: {common_preview}; {pack_evidence}",
                    "Supplier pack appears larger than Amazon pack (split candidate); verify pack counts/compliance",
                )
            )
            continue

        if brand_match and has_product_anchor:
            confidence = 88 if overlap >= 4 and sim >= 0.35 else 85
            evidence = (
                f"Brand '{brand_tok}' match + anchors: {common_preview}; {pack_evidence}"
                if brand_tok
                else f"Brand match + anchors: {common_preview}; {pack_evidence}"
            )
            if cap_status != "unknown":
                evidence += f"; {cap_note}"
            if ip_risk:
                needs_ver.append(make_row("NEEDS VERIFICATION", 75, evidence, "Potential IP risk brand: verify authenticity/eligibility"))
                continue

            if adj <= 0:
                hl_filt.append(make_row("FILTERED OUT", confidence, evidence, "Confirmed match cues but Adjusted Profit <= 0 after pack recalculation"))
                continue

            hl_rec.append(make_row("HIGHLY LIKELY", confidence, evidence, "-"))
            continue

        confidence = 75 if allow_high_sim else 68
        evidence = f"Shared anchors: {common_preview}; {pack_evidence}"
        if ip_risk:
            needs_ver.append(make_row("NEEDS VERIFICATION", max(65, confidence - 5), evidence, "Potential IP risk brand: verify authenticity/eligibility"))
            continue

        needs_ver.append(make_row("NEEDS VERIFICATION", confidence, evidence, "Verify brand/product type and pack size; match is plausible from shared anchors"))

    # Enforce A4/A3 gating: anything with Adjusted Profit <= 0 cannot remain recommended.
    for r in list(verified_rec):
        if money_to_float(r.adjusted_profit) <= 0:
            verified_rec.remove(r)
            r.verdict = "FILTERED OUT"
            r.filter_reason = "Exact EAN match but Adjusted Profit <= 0 after pack recalculation"
            verified_filt.append(r)

    for r in list(hl_rec):
        if money_to_float(r.adjusted_profit) <= 0:
            hl_rec.remove(r)
            r.verdict = "FILTERED OUT"
            r.filter_reason = "Confirmed match cues but Adjusted Profit <= 0 after pack recalculation"
            hl_filt.append(r)

    # A4: Adjusted Profit <= 0 must NOT appear in NEEDS VERIFICATION.
    # If evidence indicates a strong match (brand/anchors), keep as FILTERED OUT audit; otherwise treat as NOT INCLUDED.
    for r in list(needs_ver):
        if money_to_float(r.adjusted_profit) <= 0:
            needs_ver.remove(r)
            overlap = len(shared_tokens(r.supplier_title_raw, r.amazon_title_raw))
            brand_tok = brand_match_token(r.supplier_title_raw, r.amazon_title_raw).strip()
            strong_match = bool(brand_tok) or overlap >= 4
            if strong_match:
                r.verdict = "FILTERED OUT"
                r.confidence = max(70, r.confidence)
                r.filter_reason = "Adjusted Profit <= 0 after pack recalculation; excluded per A4"
                hl_filt.append(r)
            # else: implicitly becomes UNRELATED / NOT INCLUDED via reconciliation

    # Miss sweep: recheck initially-unrelated rows for brand/shared-anchor signals that were too strict.
    included_ids = {r.rowid for r in (verified_rec + verified_filt + hl_rec + hl_filt + needs_ver)}
    promoted = 0
    for c in unrelated_candidates:
        rowid = int(c["rowid"])
        if rowid in included_ids:
            continue

        sup_title_raw = str(c["supplier_title_raw"] or "")
        amz_title_raw = str(c["amazon_title_raw"] or "")
        brand_tok = brand_match_token(sup_title_raw, amz_title_raw).strip()
        brand_match = bool(brand_tok)

        sim = float(c.get("sim", 0) or 0)
        overlap = int(c.get("overlap", 0) or 0)

        promote = (brand_match and overlap >= 1) or (overlap >= 8 and sim >= 0.70)
        if not promote:
            continue

        supplier_price = float(c.get("supplier_price", 0) or 0)
        selling_price = float(c.get("selling_price", 0) or 0)
        net_profit = float(c.get("net_profit", 0) or 0)
        roi = float(c.get("roi", 0) or 0)
        sales = float(c.get("sales", 0) or 0)
        sup_ean = str(c.get("supplier_ean", "-") or "-")
        amz_ean = str(c.get("amazon_ean", "-") or "-")
        asin = str(c.get("asin", "") or "")

        pack = parse_pack(sup_title_raw, amz_title_raw)
        adj = adjusted_profit(net_profit, supplier_price, pack.rsu)
        cap_status, cap_note = capacity_verdict(sup_title_raw, amz_title_raw)

        sup_title = sanitize_cell(f"(RowID {rowid}) {sup_title_raw}")
        amz_title = sanitize_cell(amz_title_raw)

        supplier_price_s = fmt_money(supplier_price)
        selling_price_s = fmt_money(selling_price)
        net_profit_s = fmt_money(net_profit)
        adj_s = fmt_money(adj)
        roi_s = fmt_percent(roi)
        sales_s = str(int(round(sales)))

        strict_mismatch = (sup_ean != "-" and amz_ean != "-" and sup_ean != amz_ean)
        ip_risk = any(b in (sup_title_raw + " " + amz_title_raw).lower() for b in LUXURY_IP_BRANDS)
        common_preview = str(c.get("common_preview", "-") or "-")
        pack_evidence = f"Pack cues: {pack.supplier_evidence or '-'} / {pack.amazon_evidence or '-'}"

        evidence = (
            f"Miss sweep: brand '{brand_tok}' + anchors: {common_preview}; {pack_evidence}"
            if brand_tok
            else f"Miss sweep: shared anchors: {common_preview}; {pack_evidence}"
        )
        if cap_status != "unknown":
            evidence += f"; {cap_note}"

        r = RowOut(
            verdict="NEEDS VERIFICATION",
            confidence=65 if brand_match else 60,
            rowid=rowid,
            supplier_title_raw=sup_title_raw,
            amazon_title_raw=amz_title_raw,
            supplier_title=sup_title,
            amazon_title=amz_title,
            supplier_ean=sanitize_cell(sup_ean) if sup_ean != "-" else "-",
            amazon_ean=sanitize_cell(amz_ean) if amz_ean != "-" else "-",
            asin=sanitize_cell(asin),
            supplier_price=supplier_price_s,
            selling_price=selling_price_s,
            net_profit=net_profit_s,
            roi=roi_s,
            sales=sales_s,
            pack_verdict=sanitize_cell(pack.pack_verdict),
            adjusted_profit=adj_s,
            key_match_evidence=sanitize_cell(evidence),
            filter_reason="Miss sweep: verify brand/product type and pack/variant; previously excluded by strict gates",
            sim=sim,
        )

        # Apply gates for promoted rows (respect A4: no non-positive Adjusted Profit in NEEDS VERIFICATION).
        strong_match = brand_match and overlap >= 1

        if cap_status == "filtered_out" and strong_match:
            r.verdict = "FILTERED OUT"
            r.confidence = 75
            r.filter_reason = "Different SKU indicated by capacity difference (>25%)"
            hl_filt.append(r)
            included_ids.add(rowid)
            promoted += 1
            continue

        if money_to_float(r.adjusted_profit) <= 0:
            if strong_match:
                r.verdict = "FILTERED OUT"
                r.confidence = 75
                r.filter_reason = "Adjusted Profit <= 0 after pack recalculation; excluded per A4"
                hl_filt.append(r)
                included_ids.add(rowid)
                promoted += 1
            # else: keep UNRELATED / NOT INCLUDED
            continue

        if ip_risk:
            r.filter_reason = "Potential IP risk brand: verify authenticity/eligibility"
            needs_ver.append(r)
            included_ids.add(rowid)
            promoted += 1
            continue

        if strict_mismatch:
            r.confidence = 70
            r.filter_reason = "EAN mismatch: confirm barcode/variant/pack"
            needs_ver.append(r)
            included_ids.add(rowid)
            promoted += 1
            continue

        needs_ver.append(r)
        included_ids.add(rowid)
        promoted += 1

    verified_rec.sort(key=lambda r: (int(float(r.sales)), money_to_float(r.adjusted_profit)), reverse=True)
    verified_filt.sort(key=lambda r: money_to_float(r.adjusted_profit))
    hl_rec.sort(key=lambda r: (r.confidence, r.sim, int(r.sales)), reverse=True)
    hl_filt.sort(key=lambda r: money_to_float(r.adjusted_profit))
    needs_ver.sort(key=lambda r: (r.confidence, r.sim, int(r.sales)), reverse=True)

    total_included = len(verified_rec) + len(verified_filt) + len(hl_rec) + len(hl_filt) + len(needs_ver)
    unrelated_count = len(df) - total_included
    assert unrelated_count >= 0

    counts = {
        "VERIFIED_REC": len(verified_rec),
        "VERIFIED_FILT": len(verified_filt),
        "HL_REC": len(hl_rec),
        "HL_FILT": len(hl_filt),
        "NEEDS_VER": len(needs_ver),
        "UNRELATED": unrelated_count,
        "MISS_SWEEP_PROMOTED": promoted,
    }

    # Coverage contract: each RowID in exactly one bucket; UNRELATED is count-only.
    all_ids = [r.rowid for r in (verified_rec + verified_filt + hl_rec + hl_filt + needs_ver)]
    assert len(all_ids) == len(set(all_ids)), "Duplicate RowIDs across included buckets"
    assert total_included + counts["UNRELATED"] == len(df), "Reconciliation failed"

    for r in verified_rec:
        assert r.verdict == "VERIFIED"
        assert r.supplier_ean != "-" and r.amazon_ean != "-"
        assert float(r.sales) > 0
        assert money_to_float(r.adjusted_profit) > 0

    for r in hl_rec:
        assert r.verdict == "HIGHLY LIKELY"
        assert float(r.sales) > 0
        assert money_to_float(r.adjusted_profit) > 0

    for r in verified_filt + hl_filt:
        assert r.verdict == "FILTERED OUT"

    for r in needs_ver:
        assert r.verdict == "NEEDS VERIFICATION"

    generated = date.today().isoformat()
    supplier = "www.efghousewares.co.uk (from SupplierURL)"

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT")
    lines.append(f"**Generated:** {generated}")
    lines.append(f"**Input File:** {INPUT_PATH}")
    lines.append(f"**Supplier:** {supplier}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append(f"- VERIFIED - RECOMMENDED: {counts['VERIFIED_REC']}")
    lines.append(f"- VERIFIED - FILTERED OUT / EXCLUDED: {counts['VERIFIED_FILT']}")
    lines.append(f"- HIGHLY LIKELY - RECOMMENDED: {counts['HL_REC']}")
    lines.append(f"- HIGHLY LIKELY - FILTERED OUT / EXCLUDED: {counts['HL_FILT']}")
    lines.append(f"- NEEDS VERIFICATION: {counts['NEEDS_VER']}")
    lines.append(f"- UNRELATED / NOT INCLUDED: {counts['UNRELATED']}")
    lines.append(f"- TOTAL ANALYZED: {len(df)}")
    lines.append("")
    lines.append(
        "Executed Phases 1-4 and 6-7 from FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md (skipped Phase 5 browser verification). "
        "Input is pre-filtered (NetProfit>0, Sales>0); focus is match quality + pack/variant sanity. "
        f"Miss sweep promoted {counts['MISS_SWEEP_PROMOTED']} initially-excluded rows for review."
    )
    lines.append("")

    def section(title: str, rows: list[RowOut]) -> None:
        lines.append(f"## {title} - (count={len(rows)})")
        lines.append("")
        if not rows:
            return
        lines.append("```text")
        lines.append(fixed_width_table(rows))
        lines.append("```")
        lines.append("")

    section("VERIFIED - RECOMMENDED", verified_rec)
    section("VERIFIED - FILTERED OUT / EXCLUDED", verified_filt)
    section("HIGHLY LIKELY - RECOMMENDED", hl_rec)
    section("HIGHLY LIKELY - FILTERED OUT / EXCLUDED", hl_filt)
    section("NEEDS VERIFICATION", needs_ver)

    # Appendix-C style reasoning for every row included in tables.
    def reasoning_block(r: RowOut) -> str:
        sup_raw = r.supplier_title_raw
        amz_raw = r.amazon_title_raw
        sup_clean = sanitize_cell(sup_raw)
        amz_clean = sanitize_cell(amz_raw)
        common = shared_tokens(sup_raw, amz_raw)
        common_preview = ", ".join(common[:12]) if common else "-"

        ean_sup = r.supplier_ean
        ean_amz = r.amazon_ean
        if ean_sup != "-" and ean_amz != "-" and ean_sup == ean_amz:
            ean_status = "EXACT MATCH (strict-valid in VERIFIED)"
        elif ean_sup == "-" or ean_amz == "-":
            ean_status = "MISSING/INVALID on one side"
        else:
            ean_status = "MISMATCH (both present/valid)"

        brand_tok = brand_match_token(sup_raw, amz_raw).strip() or "-"
        pack = parse_pack(sup_raw, amz_raw)
        cap_status, cap_note = capacity_verdict(sup_raw, amz_raw)

        meas_notes: list[str] = []
        if (
            RE_DIM_NXM.search(sup_raw)
            or RE_DIM_COMPACT.search(sup_raw)
            or RE_DIM_NXM.search(amz_raw)
            or RE_DIM_COMPACT.search(amz_raw)
        ):
            meas_notes.append("NxM + unit detected -> DIMENSION (not pack)")
        if RE_AMZ_QTY_X_CAP.search(amz_raw):
            meas_notes.append("N x capacity detected -> RSU=N (do NOT multiply by ml/g)")
        spec_m = RE_AMZ_SPEC_2000X.search(amz_raw)
        if spec_m and _has_spec_x_context(amz_raw, spec_m.span()):
            meas_notes.append("Spec '####x' near scope/microscope keywords -> NOT pack")
        if not meas_notes:
            meas_notes.append("No dimension/spec traps detected")

        sup_pack_ev = pack.supplier_evidence or "-"
        amz_pack_ev = pack.amazon_evidence or "-"

        lines_block: list[str] = []
        lines_block.append(f"RowID: {r.rowid}")
        lines_block.append(f"Verdict: {r.verdict} (Confidence {r.confidence})")
        lines_block.append("")
        lines_block.append("Raw Data:")
        lines_block.append(f"- Supplier EAN: {ean_sup}")
        lines_block.append(f"- Amazon EAN: {ean_amz}")
        lines_block.append(f"- SupplierTitle: {sup_clean}")
        lines_block.append(f"- AmazonTitle: {amz_clean}")
        lines_block.append(f"- SupplierPrice: {r.supplier_price} | SellingPrice: {r.selling_price}")
        lines_block.append(
            f"- NetProfit: {r.net_profit} | Adjusted Profit: {r.adjusted_profit} | ROI: {r.roi} | Sales: {r.sales}"
        )
        lines_block.append("")
        lines_block.append("Step-by-Step Reasoning:")
        lines_block.append(f"1) EAN Check: {ean_status}")
        lines_block.append(f"2) Brand Anchor: {brand_tok} (Supplier-start heuristic)")
        lines_block.append(f"3) Shared Anchors: {common_preview}")
        lines_block.append(
            f"4) Pack Detection: Supplier='{sup_pack_ev}' vs Amazon='{amz_pack_ev}' -> RSU={pack.rsu}; Pack Verdict='{r.pack_verdict}'"
        )
        lines_block.append(f"5) Number Interpretation Shield: {', '.join(meas_notes)}")
        lines_block.append(f"6) Capacity Check: {cap_status} ({cap_note})")
        lines_block.append(f"7) Evidence (row-grounded): {r.key_match_evidence}")
        lines_block.append(
            f"8) Decision: {r.filter_reason if r.filter_reason != '-' else 'Included as actionable (profit>0 after pack sanity)'}"
        )
        return "\n".join(lines_block)

    def reasoning_section(title: str, rows: list[RowOut]) -> None:
        lines.append(f"### {title} (count={len(rows)})")
        lines.append("")
        if not rows:
            return
        lines.append("```text")
        lines.append("\n\n---\n\n".join(reasoning_block(r) for r in rows))
        lines.append("```")
        lines.append("")

    lines.append("## Reasoning Chains (Appendix C style)")
    lines.append("")
    reasoning_section("VERIFIED - RECOMMENDED", verified_rec)
    reasoning_section("VERIFIED - FILTERED OUT / EXCLUDED", verified_filt)
    reasoning_section("HIGHLY LIKELY - RECOMMENDED", hl_rec)
    reasoning_section("HIGHLY LIKELY - FILTERED OUT / EXCLUDED", hl_filt)
    reasoning_section("NEEDS VERIFICATION", needs_ver)

    lines.append("## Reconciliation")
    lines.append(f"- VERIFIED - RECOMMENDED: {counts['VERIFIED_REC']}")
    lines.append(f"- VERIFIED - FILTERED OUT / EXCLUDED: {counts['VERIFIED_FILT']}")
    lines.append(f"- HIGHLY LIKELY - RECOMMENDED: {counts['HL_REC']}")
    lines.append(f"- HIGHLY LIKELY - FILTERED OUT / EXCLUDED: {counts['HL_FILT']}")
    lines.append(f"- NEEDS VERIFICATION: {counts['NEEDS_VER']}")
    lines.append(f"- UNRELATED / NOT INCLUDED: {counts['UNRELATED']}")
    lines.append(f"- TOTAL ANALYZED: {len(df)}")
    lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8-sig")
    print("Wrote:", OUTPUT_PATH)
    print("Counts:", counts)


if __name__ == "__main__":
    main()
