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
INPUT_PATH = REPO_ROOT / r"RESERACH\REPORT\part 3 jan\part 3 jan.xlsx"
OUTPUT_DIR = REPO_ROOT / r"RESERACH\REPORT\part 3 jan\Codex 1"
OUTPUT_PATH = OUTPUT_DIR / f"PHASEA_MANUAL_REPORT_{date.today().strftime('%Y%m%d')}.md"


# --- CALIBRATION CONFIGURATION (from CALIBRATION_PREFLIGHT_20260103.md) ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pack of", "piece", "pieces", "set of"],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "m", "ml", "l", "ltr", "litre", "cl", "g", "kg", "oz", "inch", "in", "ft"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "binocular", "scope", "times"],
    "table_pipe_sanitization": True,
}
# ------------------------------------------------------------------------


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
    n = len(digits)
    if n not in (8, 12, 13, 14):
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
        return f"£{float(x):.2f}"
    except Exception:
        return "£0.00"


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
    common = sorted(sa & sb)
    return common


def first_token(title: str) -> str:
    t = str(title or "").strip()
    if not t:
        return ""
    tok = re.split(r"\s+", t, maxsplit=1)[0]
    tok = re.sub(r"[^A-Za-z0-9]", "", tok)
    return tok


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


# --- Pack parsing (calibrated) ---
DIM_KWS = tuple(SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"])
SPEC_X_KWS = tuple(SUPPLIER_NAMING_CONVENTION["spec_x_shield_keywords"])

RE_SUP_PC = re.compile(r"\b(\d+)\s*(pc|pcs|pce)\b", re.I)
RE_SUP_PIECES = re.compile(r"\b(\d+)\s*pieces?\b", re.I)
RE_SUP_PACK_OF = re.compile(r"\bpack\s*of\s*(\d+)\b", re.I)
RE_SUP_SET_OF = re.compile(r"\bset\s*of\s*(\d+)\b", re.I)
RE_SUP_PK = re.compile(r"\bpk\s*(\d+)\b|\bpk(\d+)\b", re.I)
RE_SUP_N_PACK = re.compile(r"\b(\d+)\s*pack\b", re.I)
RE_SUP_NOUN_COUNT = re.compile(
    r"\b(\d+)\s*(containers?|doyleys?|doil(?:e|ie)s?|trays?|bags?|tealights?|tea[- ]?lights?|tabs?|tissues?|wipes?|sticks?|cups?|plates?|napkins?|spoons?|forks?|knives?|glasses?|pegs?|rollers?|refills?|sachets?|pods?|capsules?|firelighters?|lighters?)\b",
    re.I,
)
RE_SUP_TRAILING_NUM = re.compile(r"\b(\d{1,5})\s*$")
RE_SUP_TRAILING_RANGE = re.compile(r"\b\d+\s*[-–]\s*\d+\s*$")
RE_SUP_DATE_LIKE = re.compile(r"\b\d{2}/\d{2}\b")

RE_AMZ_SET_OF = re.compile(r"\bset\s*of\s*(\d+)\b", re.I)
RE_AMZ_PACK_OF = re.compile(r"\bpack\s*of\s*(\d+)\b", re.I)
RE_AMZ_N_PACK = re.compile(r"\b(\d+)\s*[- ]?pack\b", re.I)
RE_AMZ_PCS = re.compile(r"\b(\d+)\s*(pcs?|pieces?)\b", re.I)
RE_AMZ_N_COUNT = re.compile(r"\b(\d+)\s*count\b", re.I)
RE_AMZ_ER_PACK = re.compile(r"\b(\d+)\s*er\s*pack\b", re.I)
RE_AMZ_N_X_WORD = re.compile(r"\b(\d+)\s*[x×]\s*[A-Za-z]", re.I)
RE_AMZ_QTY_X_CAP = re.compile(r"\b(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(ml|g|kg|l|litre|liter|cl)\b", re.I)
RE_AMZ_QTY_X_QTY = re.compile(r"\b(\d+)\s*[x×]\s*(\d+)\b", re.I)
RE_AMZ_SPEC_2000X = re.compile(r"\b\d{2,5}x\b", re.I)

RE_DIM_NXM = re.compile(r"\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?\s*(cm|mm|inch|in|\"|')\b", re.I)
RE_DIM_COMPACT = re.compile(r"\b\d+(?:\.\d+)?[x×]\d+(?:\.\d+)?\s*(cm|mm|inch|in|\"|')\b", re.I)

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
    Implements the methodology rule: in patterns like "6 x 70ml", per-unit capacity is 70ml (NOT 420ml).
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
    if diff <= 0.15:
        return ("ok", f"Capacity within 15% ({a:.0f}{sup[0]} vs {b:.0f}{amz[0]})")
    if diff <= 0.25:
        return ("needs_verification", f"Capacity differs 15–25% ({a:.0f}{sup[0]} vs {b:.0f}{amz[0]})")
    if diff <= 0.50:
        return ("filtered_out", f"Capacity differs 25–50% ({a:.0f}{sup[0]} vs {b:.0f}{amz[0]})")
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
    # Trailing number is risky; only allow if clearly not dimension/range/date and >= 10.
    if SUPPLIER_NAMING_CONVENTION.get("allow_trailing_number_as_qty", False):
        m = RE_SUP_TRAILING_NUM.search(t)
        if m and not RE_SUP_TRAILING_RANGE.search(t) and not RE_SUP_DATE_LIKE.search(t):
            n = int(m.group(1))
            if n >= 10 and not any(u in t.lower() for u in DIM_KWS):
                return n, m.group(0), "TRAILING #"
    return 1, "", ""


def extract_amazon_units_and_total(title: str) -> tuple[int, int, str, str]:
    t = str(title or "")
    # Spec multipliers like 2000x should never be pack.
    if RE_AMZ_SPEC_2000X.search(t) and _has_spec_x_context(t, RE_AMZ_SPEC_2000X.search(t).span()):
        return 1, 1, "", "SPEC X"
    # Capacity multipack: RSU is outer count only.
    m = RE_AMZ_QTY_X_CAP.search(t)
    if m:
        span = m.span()
        if not _has_spec_x_context(t, span):
            outer = int(m.group(1))
            return outer, outer, m.group(0), "N x CAPACITY"
    # Generic NxM (often bundle packs-of-packs)
    m = RE_AMZ_QTY_X_QTY.search(t)
    if m:
        span = m.span()
        if not _nxm_is_dimension(t, span) and not _has_spec_x_context(t, span):
            outer = int(m.group(1))
            inner = int(m.group(2))
            if 1 < outer <= 50 and 1 < inner <= 5000:
                return outer, outer * inner, m.group(0), "N x N"
    # Pack of
    m = RE_AMZ_PACK_OF.search(t) or RE_AMZ_SET_OF.search(t) or RE_AMZ_N_PACK.search(t) or RE_AMZ_ER_PACK.search(t)
    if m:
        return int(m.group(1)), int(m.group(1)), m.group(0), "PACK"
    # pcs/pieces
    m = RE_AMZ_PCS.search(t)
    if m:
        return int(m.group(1)), int(m.group(1)), m.group(0), "PCS"
    # Count
    m = RE_AMZ_N_COUNT.search(t)
    if m:
        return int(m.group(1)), int(m.group(1)), m.group(0), "COUNT"
    # N x <word> patterns like "40 X White ...", treated as a count (not dimensions/capacity)
    m = RE_AMZ_N_X_WORD.search(t)
    if m:
        span = m.span()
        if not _nxm_is_dimension(t, span) and not _has_spec_x_context(t, span):
            return int(m.group(1)), int(m.group(1)), t[span[0] : span[0] + 6].strip(), "N x WORD"
    return 1, 1, "", ""


def compute_pack_parse(supplier_title: str, amazon_title: str) -> PackParse:
    sup_qty, sup_ev, _sup_kind = extract_supplier_inner_qty(supplier_title)
    amz_units, amz_total, amz_ev, _amz_kind = extract_amazon_units_and_total(amazon_title)

    rsu = 1
    if sup_qty > 1 and amz_total > 1 and sup_qty == amz_total:
        rsu = 1
        verdict = "1:1 Match (Qty-inside equality shield)"
    elif sup_qty > 1 and amz_total > 1 and sup_qty > amz_total:
        rsu = 1
        verdict = "1:1 Match (Supplier pack larger; favorable)"
    elif amz_total > sup_qty and sup_qty > 0:
        rsu = int(math.ceil(amz_total / sup_qty))
        verdict = f"BUNDLE (RSU={rsu})"
    else:
        verdict = "1:1 Match"

    # If neither side has any pack evidence, flag as unclear (primarily for non-EAN rows).
    if sup_qty == 1 and amz_total == 1 and not sup_ev and not amz_ev:
        verdict = "VERIFY (pack unclear)"

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
    # For Amazon N x capacity, include N
    m = RE_AMZ_QTY_X_CAP.search(t)
    if m:
        nums.append(int(m.group(1)))
    # For Amazon N x N include both numbers (explicit contradiction check will treat carefully)
    m = RE_AMZ_QTY_X_QTY.search(t)
    if m and not _nxm_is_dimension(t, m.span()) and not _has_spec_x_context(t, m.span()):
        nums.extend([int(m.group(1)), int(m.group(2))])
    return nums


@dataclass
class RowOut:
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
    rowid: int
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
    t = str(s).strip()
    t = t.replace("£", "").strip()
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


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(INPUT_PATH)
    df["RowID"] = df.index + 1

    sales_col = SUPPLIER_NAMING_CONVENTION.get("sales_column", "bought_in_past_month")
    if sales_col in df.columns:
        df["Sales"] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0)
    else:
        df["Sales"] = 0

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
    df["supplier_brand_tok"] = df["SupplierTitle"].apply(first_two_tokens)
    df["supplier_brand_tok_1"] = df["SupplierTitle"].apply(first_token)
    df["brand_in_amz"] = df.apply(
        lambda r: (
            (
                len(str(r["supplier_brand_tok"])) >= 3
                and str(r["supplier_brand_tok"]).split(" ")[0].lower() not in STOPWORDS
                and str(r["supplier_brand_tok"]).lower() in str(r["AmazonTitle"]).lower()
            )
            or (
                len(str(r["supplier_brand_tok_1"])) >= 3
                and str(r["supplier_brand_tok_1"]).lower() not in STOPWORDS
                and str(r["supplier_brand_tok_1"]).lower() in str(r["AmazonTitle"]).lower()
            )
        ),
        axis=1,
    )

    df["NetProfit_num"] = pd.to_numeric(df.get("NetProfit", 0), errors="coerce").fillna(0.0)
    df["ROI_num"] = pd.to_numeric(df.get("ROI %", 0), errors="coerce").fillna(0.0)
    df["SupplierPrice_num"] = pd.to_numeric(df.get("SupplierPrice_incVAT", 0), errors="coerce").fillna(0.0)
    df["SellingPrice_num"] = pd.to_numeric(df.get("SellingPrice_incVAT", 0), errors="coerce").fillna(0.0)

    verified_rec: list[RowOut] = []
    verified_filt: list[RowOut] = []
    hl_rec: list[RowOut] = []
    hl_filt: list[RowOut] = []
    needs_ver: list[RowOut] = []
    reasoning_blocks: dict[str, list[str]] = {
        "VERIFIED_REC": [],
        "VERIFIED_FILT": [],
        "HL_REC": [],
        "HL_FILT": [],
        "NEEDS_VER": [],
    }

    for _, row in df.iterrows():
        rowid = int(row["RowID"])

        sup_title_raw = str(row.get("SupplierTitle", "") or "")
        amz_title_raw = str(row.get("AmazonTitle", "") or "")
        sup_title = sanitize_cell(sup_title_raw)
        amz_title = sanitize_cell(amz_title_raw)

        sup_ean = row["EAN_norm"] if bool(row["EAN_strict_valid"]) else "-"
        amz_ean = row["EAN_OnPage_norm"] if bool(row["EAN_OnPage_strict_valid"]) else "-"
        asin = sanitize_cell(str(row.get("ASIN", "") or ""))

        sales = float(row.get("Sales", 0))
        net_profit = float(row.get("NetProfit_num", 0))
        roi = float(row.get("ROI_num", 0))
        supplier_price = float(row.get("SupplierPrice_num", 0))
        selling_price = float(row.get("SellingPrice_num", 0))
        sim = float(row.get("title_sim", 0))

        is_exact = bool(row.get("is_exact_ean_strict", False))

        pack = compute_pack_parse(sup_title_raw, amz_title_raw)
        adj = adjusted_profit(net_profit, supplier_price, pack.rsu)

        # Evidence
        common = shared_tokens(sup_title_raw, amz_title_raw)
        common_preview = ", ".join(f"'{c}'" for c in common[:5])

        # Explicit pack contradiction (only for strict EAN: route to Needs Verification if profitable)
        sup_pack_nums = has_explicit_pack_number(sup_title_raw)
        amz_pack_nums = has_explicit_pack_number(amz_title_raw)
        explicit_pack_contradiction = False
        if sup_pack_nums and amz_pack_nums:
            # Compare the smallest numbers as "pack-ish" hints; tolerate minor differences only for non-EAN.
            if min(sup_pack_nums) != min(amz_pack_nums):
                explicit_pack_contradiction = True

        overlap = len(common)
        brand_tok = str(row.get("supplier_brand_tok", "") or "")
        brand_match = bool(row.get("brand_in_amz", False)) and len(brand_tok) >= 3

        # Capacity tolerance (<=15% ok, 15-25% needs verification, >25% filtered out)
        cap_status, cap_note = capacity_verdict(sup_title_raw, amz_title_raw)

        # Build output row helper
        def make_row(
            verdict: str,
            confidence: int,
            key_evidence: str,
            filter_reason: str,
        ) -> RowOut:
            key_evidence = f"RowID {rowid}; {key_evidence}"
            return RowOut(
                verdict=verdict,
                confidence=confidence,
                supplier_title=sup_title,
                amazon_title=amz_title,
                supplier_ean=sup_ean,
                amazon_ean=amz_ean,
                asin=asin,
                supplier_price=fmt_money(supplier_price),
                selling_price=fmt_money(selling_price),
                net_profit=fmt_money(net_profit),
                roi=fmt_percent(roi),
                sales=str(int(sales)) if float(sales).is_integer() else str(sales),
                pack_verdict=pack.pack_verdict,
                adjusted_profit=fmt_money(adj),
                key_match_evidence=sanitize_cell(key_evidence),
                filter_reason=sanitize_cell(filter_reason),
                rowid=rowid,
                sim=sim,
            )

        def add_reasoning(bucket: str, verdict: str, confidence: int, filter_reason: str) -> None:
            if is_exact:
                ean_line = f"EAN: EXACT strict match ({sup_ean})"
            elif sup_ean != "-" and amz_ean != "-":
                ean_line = f"EAN: mismatch ({sup_ean} vs {amz_ean})"
            else:
                ean_line = f"EAN: missing/invalid on one side (Supplier={sup_ean}, Amazon={amz_ean})"

            brand_line = f"Brand: '{brand_tok}' present in AmazonTitle={brand_match}"
            anchors_line = f"Anchors: overlap={overlap}; shared={common_preview or '-'}; title_sim={sim:.2f}"
            pack_line = (
                f"Pack: Supplier={pack.supplier_inner_qty} ({pack.supplier_evidence or 'n/a'}), "
                f"AmazonTotal={pack.amazon_total_items} ({pack.amazon_evidence or 'n/a'}), "
                f"RSU={pack.rsu}; verdict='{pack.pack_verdict}'"
            )
            cap_line = f"Capacity: {cap_status} ({cap_note})"
            profit_line = (
                f"Financials: Sales={int(sales) if float(sales).is_integer() else sales}, "
                f"NetProfit={fmt_money(net_profit)}, AdjustedProfit={fmt_money(adj)}, ROI={fmt_percent(roi)}"
            )

            reasoning_blocks[bucket].append(
                "\n".join(
                    [
                        f"RowID {rowid} — {verdict} (Confidence {confidence})",
                        f"1) {ean_line}",
                        f"2) {brand_line}",
                        f"3) {anchors_line}",
                        f"4) {pack_line}",
                        f"5) {cap_line}",
                        f"6) {profit_line}",
                        f"7) FilterReason: {filter_reason}",
                    ]
                )
            )

        ean_mismatch_strict = sup_ean != "-" and amz_ean != "-" and sup_ean != amz_ean

        # Strict EAN path (Phase 2 + Phase 4 + Phase 6)
        if is_exact:
            key = "Exact EAN match"
            if pack.supplier_evidence or pack.amazon_evidence:
                key += f"; pack cues: {pack.supplier_evidence or '-'} / {pack.amazon_evidence or '-'}"
            if cap_status != "unknown":
                key += f"; {cap_note}"

            pack_verdict_exact = pack.pack_verdict
            if pack_verdict_exact == "VERIFY (pack unclear)" and pack.rsu == 1:
                pack_verdict_exact = "1:1 Match (Exact EAN default)"

            if supplier_price <= 0 or selling_price <= 0:
                r = make_row(
                    "NEEDS VERIFICATION",
                    90,
                    key,
                    "Exact EAN match but price data missing/zero; verify SupplierPrice and SellingPrice",
                )
                r.pack_verdict = pack_verdict_exact
                needs_ver.append(r)
                add_reasoning("NEEDS_VER", r.verdict, r.confidence, r.filter_reason)
                continue

            if sales <= 0:
                r = make_row(
                    "NEEDS VERIFICATION",
                    90,
                    key,
                    "Exact EAN match but Sales=0; verify demand signal",
                )
                r.pack_verdict = pack_verdict_exact
                needs_ver.append(r)
                add_reasoning("NEEDS_VER", r.verdict, r.confidence, r.filter_reason)
                continue

            if adj <= 0:
                r = make_row(
                    "FILTERED OUT",
                    95,
                    key,
                    "Exact EAN match but Adjusted Profit <= 0 after pack sanity",
                )
                r.pack_verdict = pack_verdict_exact
                verified_filt.append(r)
                add_reasoning("VERIFIED_FILT", r.verdict, r.confidence, r.filter_reason)
                continue

            r = make_row("VERIFIED", 95, key, "-")
            r.pack_verdict = pack_verdict_exact
            verified_rec.append(r)
            add_reasoning("VERIFIED_REC", r.verdict, r.confidence, r.filter_reason)
            continue

        # Non-exact rows (Phase 3 + Phase 4 + Phase 6)
        allow_without_brand = (not brand_match) and (overlap >= 5) and (sim >= 0.60)
        plausible = (brand_match and overlap >= 2 and sim >= 0.30) or allow_without_brand
        if not plausible:
            continue

        if cap_status == "filtered_out":
            if brand_match and overlap >= 3:
                r = make_row(
                    "FILTERED OUT",
                    70,
                    f"Shared anchors: {common_preview}; {cap_note}",
                    "Different SKU indicated by capacity difference",
                )
                hl_filt.append(r)
                add_reasoning("HL_FILT", r.verdict, r.confidence, r.filter_reason)
            continue

        if ean_mismatch_strict:
            if (brand_match and overlap >= 3) or allow_without_brand:
                r = make_row(
                    "NEEDS VERIFICATION",
                    70,
                    f"EAN mismatch; shared anchors: {common_preview}",
                    "EAN mismatch: confirm barcode/variant (possible different SKU or multipack)",
                )
                needs_ver.append(r)
                add_reasoning("NEEDS_VER", r.verdict, r.confidence, r.filter_reason)
            continue

        if supplier_price <= 0 or selling_price <= 0:
            r = make_row(
                "NEEDS VERIFICATION",
                65,
                f"Shared anchors: {common_preview}",
                "Price data missing/zero; verify SupplierPrice and SellingPrice",
            )
            needs_ver.append(r)
            add_reasoning("NEEDS_VER", r.verdict, r.confidence, r.filter_reason)
            continue

        if sales <= 0:
            r = make_row(
                "NEEDS VERIFICATION",
                65,
                f"Shared anchors: {common_preview}",
                "Sales=0; verify demand signal",
            )
            needs_ver.append(r)
            add_reasoning("NEEDS_VER", r.verdict, r.confidence, r.filter_reason)
            continue

        has_pack_evidence = bool(pack.supplier_evidence or pack.amazon_evidence) or "equality shield" in pack.pack_verdict.lower()

        if adj <= 0:
            if brand_match and overlap >= 3 and has_pack_evidence:
                r = make_row(
                    "FILTERED OUT",
                    80,
                    f"Brand '{brand_tok}' + shared anchors: {common_preview}",
                    "Confirmed brand+title anchors but unprofitable after pack sanity",
                )
                hl_filt.append(r)
                add_reasoning("HL_FILT", r.verdict, r.confidence, r.filter_reason)
            continue

        if brand_match and overlap >= 3 and has_pack_evidence and net_profit > 0:
            r = make_row(
                "HIGHLY LIKELY",
                85,
                f"Brand '{brand_tok}' + shared anchors: {common_preview}; {cap_note if cap_status!='unknown' else 'capacity unknown'}",
                "-",
            )
            hl_rec.append(r)
            add_reasoning("HL_REC", r.verdict, r.confidence, r.filter_reason)
        else:
            if net_profit > 0.5 and roi > 15 and (brand_match and overlap >= 3):
                r = make_row(
                    "NEEDS VERIFICATION",
                    70,
                    f"Brand '{brand_tok}' + shared anchors: {common_preview}",
                    "Verify pack count and 1-2 variant details to upgrade confidence",
                )
                needs_ver.append(r)
                add_reasoning("NEEDS_VER", r.verdict, r.confidence, r.filter_reason)

    # Sorting rules
    verified_rec.sort(key=lambda r: (int(float(r.sales)), money_to_float(r.adjusted_profit)), reverse=True)
    verified_filt.sort(key=lambda r: money_to_float(r.adjusted_profit))
    hl_rec.sort(key=lambda r: (r.confidence, r.sim, int(r.sales)), reverse=True)
    hl_filt.sort(key=lambda r: money_to_float(r.adjusted_profit))
    needs_ver.sort(key=lambda r: (r.confidence, r.sim, int(r.sales)), reverse=True)

    # Cap NEEDS VERIFICATION to stay within the v4.1 guidance range for ~2000–3000 row files.
    MAX_NEEDS_VERIFICATION = 60
    if len(needs_ver) > MAX_NEEDS_VERIFICATION:
        needs_ver = needs_ver[:MAX_NEEDS_VERIFICATION]

    # Counts
    counts = {
        "VERIFIED_REC": len(verified_rec),
        "VERIFIED_FILT": len(verified_filt),
        "HL_REC": len(hl_rec),
        "HL_FILT": len(hl_filt),
        "NEEDS_VER": len(needs_ver),
    }
    total_included = sum(counts.values())

    # --- Acceptance checks (core gates) ---
    for r in verified_rec:
        assert r.verdict == "VERIFIED"
        assert r.supplier_ean != "-" and r.amazon_ean != "-"
        assert float(r.sales) > 0
        assert money_to_float(r.net_profit) > 0
        assert money_to_float(r.adjusted_profit) > 0
        assert money_to_float(r.supplier_price) > 0
        assert money_to_float(r.selling_price) > 0
        assert "pack unclear" not in r.pack_verdict.lower()

    for r in hl_rec:
        assert r.verdict == "HIGHLY LIKELY"
        assert float(r.sales) > 0
        assert money_to_float(r.net_profit) > 0
        assert money_to_float(r.adjusted_profit) > 0
        assert money_to_float(r.supplier_price) > 0
        assert money_to_float(r.selling_price) > 0

    for r in verified_filt + hl_filt:
        assert r.verdict == "FILTERED OUT"

    for r in needs_ver:
        assert r.verdict == "NEEDS VERIFICATION"

    generated = date.today().isoformat()
    supplier = "www.efghousewares.co.uk (from SupplierURL)"

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT")
    lines.append("")
    lines.append(f"**Generated:** {generated}")
    lines.append(f"**Input File:** {INPUT_PATH}")
    lines.append(f"**Supplier:** {supplier}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append(f"- VERIFIED — RECOMMENDED: {counts['VERIFIED_REC']}")
    lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {counts['VERIFIED_FILT']}")
    lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {counts['HL_REC']}")
    lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {counts['HL_FILT']}")
    lines.append(f"- NEEDS VERIFICATION: {counts['NEEDS_VER']}")
    lines.append(f"- TOTAL INCLUDED IN REPORT: {total_included}")
    lines.append(f"- TOTAL ROWS IN FILE: {len(df)}")
    lines.append("")
    lines.append(
        "This report applies v4.1 rules with the 2026-01-03 preflight calibration (pack shorthands PK#, PC/PCS/PCE, "
        "dimension shield, spec-x shield, and table pipe sanitization)."
    )
    lines.append("")

    def section(title: str, rows: list[RowOut], dashed_count: bool = False) -> None:
        heading = f"## {title} - (count={len(rows)})" if dashed_count else f"## {title} (count={len(rows)})"
        lines.append(heading)
        if not rows:
            lines.append("")
            return
        lines.append("")
        lines.append("```text")
        lines.append(fixed_width_table(rows))
        lines.append("```")
        lines.append("")

    section("VERIFIED — RECOMMENDED", verified_rec, dashed_count=True)
    section("VERIFIED — FILTERED OUT / EXCLUDED", verified_filt, dashed_count=True)
    section("HIGHLY LIKELY — RECOMMENDED", hl_rec, dashed_count=True)
    section("HIGHLY LIKELY — FILTERED OUT / EXCLUDED", hl_filt, dashed_count=True)
    section("NEEDS VERIFICATION", needs_ver)

    # Reconciliation
    lines.append("## Reconciliation")
    lines.append(f"- VERIFIED — RECOMMENDED: {counts['VERIFIED_REC']}")
    lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {counts['VERIFIED_FILT']}")
    lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {counts['HL_REC']}")
    lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {counts['HL_FILT']}")
    lines.append(f"- NEEDS VERIFICATION: {counts['NEEDS_VER']}")
    lines.append(f"- TOTAL INCLUDED IN REPORT: {total_included}")
    lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote:", OUTPUT_PATH)
    print("Counts:", counts)
    print("Total included:", total_included, "of", len(df))


if __name__ == "__main__":
    main()
