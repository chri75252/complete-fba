from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class BarcodeResult:
    raw: str
    cleaned: str
    normalized: str | None
    is_valid: bool
    notes: str


KNOWN_BRANDS: list[str] = [
    "AMTECH",
    "MASON CASH",
    "ROLSON",
    "KILNER",
    "DRAPER",
    "PYREX",
    "CHEF AID",
    "BLUE CANYON",
    "ELLIOTT",
    "FALCON",
    "BAKER & SALT",
    "BAKER AND SALT",
    "SCHOTT ZWIESEL",
    "MARIGOLD",
    "FAIRY",
    "DETTOL",
    "EVERBUILD",
    "SOUDAL",
    "TIDYZ",
    "BACOFOIL",
    "HARRIS",
    "EXTRASTAR",
    "GIFTMAKER",
    "PRIMA",
    "APOLLO",
    "KILROCK",
    "PRODEC",
    "HOUSE MATE",
    "TALA",
    "LITTLE TREES",
    "ELBOW GREASE",
    "PRICE & KENSINGTON",
    "ULTRATAPE",
    "FIRE UP",
    "DOFF",
    "GEEPAS",
    "STATUS",
    "ROUNDUP",
    "SUPERIOR",
    "FIRST STEPS",
    "MINKY",
    "RUSSELL HOBBS",
    "QUEST",
    "YALE",
    "VINERS",
    "MASTERCLASS",
    "HEM",
    "AIRWICK",
    "AIR WICK",
    "SPONTEX",
    "PASABAHCE",
    "RCR",
    "SCHOTT",
    "DENBY",
    "HEAT HOLDERS",
    "KORKEN",
    "ZEAL",
    "OXO",
    "JOSEPH JOSEPH",
    "BRABANTIA",
    "KENWOOD",
    "SWAN",
    "TOWER",
    "MORPHY RICHARDS",
    "TEFAL",
    "WILTON",
    "SABICHI",
    "DUNLOP",
    "JML",
    "BELDRAY",
    "PROGRESS",
    "SALTER",
    "PRESTIGE",
    "STELLAR",
    "HORWOOD",
    "RAVENHEAD",
    "DURALEX",
    "LUMINARC",
    "ARC",
    "ARCOROC",
    "PYREX ESSENTIALS",
    "MASTER CLASS",
    "JUDGE",
]

INVALID_FIRST_WORDS: set[str] = {
    "MONEY",
    "HAPPY",
    "SALT",
    "LED",
    "BBQ",
    "DOOR",
    "PET",
    "CAT",
    "DOG",
    "CANDLE",
    "MIRROR",
    "BOTTLE",
    "BASKET",
    "GLOVES",
    "WATCH",
    "LARGE",
    "SMALL",
    "PREMIUM",
    "DELUXE",
    "CLASSIC",
    "MODERN",
    "WOODEN",
    "METAL",
    "PLASTIC",
    "STEEL",
    "GLASS",
    "CHRISTMAS",
    "BIRTHDAY",
    "GARDEN",
    "KITCHEN",
    "BATHROOM",
    "BEDROOM",
    "OUTDOOR",
    "INDOOR",
    "BLACK",
    "WHITE",
    "BLUE",
    "RED",
}

VARIANT_SCENTS: set[str] = {
    "EUCALYPTUS",
    "LEMON",
    "LIME",
    "LAVENDER",
    "VANILLA",
    "ORANGE",
    "FRESH",
    "CITRUS",
    "MINT",
    "ROSE",
    "OCEAN",
    "APPLE",
    "CHERRY",
    "PINE",
}
VARIANT_COLORS: set[str] = {
    "BLACK",
    "WHITE",
    "GREY",
    "GRAY",
    "NAVY",
    "CREAM",
    "RED",
    "BLUE",
    "GREEN",
    "PINK",
    "BROWN",
    "SILVER",
    "GOLD",
    "YELLOW",
    "PURPLE",
    "ORANGE",
}
VARIANT_SIZES: set[str] = {
    "SMALL",
    "MEDIUM",
    "LARGE",
    "XL",
    "XXL",
    "MINI",
    "GIANT",
    "JUMBO",
}
VARIANT_MATERIALS: set[str] = {
    "ENAMEL",
    "STAINLESS",
    "STEEL",
    "WOOD",
    "PLASTIC",
    "CERAMIC",
    "GLASS",
    "SILICONE",
    "ALUMINIUM",
    "ALUMINUM",
    "IRON",
}


STOPWORDS: set[str] = {
    "THE",
    "AND",
    "OR",
    "WITH",
    "FOR",
    "OF",
    "A",
    "AN",
    "TO",
    "IN",
    "ON",
    "BY",
    "PACK",
    "SET",
    "PCS",
    "PC",
    "PIECE",
    "PIECES",
    "ASSORTED",
    "ASST",
    "LTD",
    "LIMITED",
    "NEW",
    "UK",
}


def _safe_str(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def _digits_only(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)


def _compute_gs1_check_digit(digits_without_check: str) -> int:
    total = 0
    reversed_digits = list(reversed([int(d) for d in digits_without_check]))
    for idx, digit in enumerate(reversed_digits):
        total += digit * (3 if idx % 2 == 0 else 1)
    return (10 - (total % 10)) % 10


def _is_valid_gtin(candidate: str) -> bool:
    if not candidate.isdigit():
        return False
    if len(candidate) not in (8, 12, 13, 14):
        return False
    body, check = candidate[:-1], int(candidate[-1])
    return _compute_gs1_check_digit(body) == check


def normalize_barcode(raw: object) -> BarcodeResult:
    raw_s = _safe_str(raw)
    cleaned = raw_s.replace(".0", "").strip()
    digits = _digits_only(cleaned)
    if not digits:
        return BarcodeResult(raw=raw_s, cleaned=cleaned, normalized=None, is_valid=False, notes="missing")

    if _is_valid_gtin(digits):
        return BarcodeResult(raw=raw_s, cleaned=digits, normalized=digits, is_valid=True, notes="valid")

    padded_attempts: list[str] = []
    if len(digits) < 8:
        targets = (13, 12, 14)
    elif len(digits) not in (8, 12, 13, 14) and len(digits) < 14:
        targets = (13, 12, 14)
    else:
        targets = ()

    for target in targets:
        if len(digits) >= target:
            continue
        padded = digits.zfill(target)
        padded_attempts.append(padded)
        if _is_valid_gtin(padded):
            return BarcodeResult(
                raw=raw_s,
                cleaned=digits,
                normalized=padded,
                is_valid=True,
                notes=f"valid (left-padded to {target})",
            )

    if len(digits) in (8, 12, 13, 14):
        return BarcodeResult(
            raw=raw_s,
            cleaned=digits,
            normalized=None,
            is_valid=False,
            notes="checksum-fail",
        )

    attempts = ", ".join(str(len(a)) for a in padded_attempts) if padded_attempts else "none"
    return BarcodeResult(
        raw=raw_s,
        cleaned=digits,
        normalized=None,
        is_valid=False,
        notes=f"invalid length ({len(digits)}); pad attempts: {attempts}",
    )


def extract_known_brand(title: object) -> str:
    t = _safe_str(title).upper()
    if not t:
        return ""
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if brand in t:
            return brand
    return ""


def starts_with_invalid_word(title: object) -> bool:
    t = _safe_str(title)
    if not t:
        return False
    first = re.split(r"\s+", t.strip(), maxsplit=1)[0]
    first = re.sub(r"[^A-Za-z0-9&]+", "", first).upper()
    return first in INVALID_FIRST_WORDS


def _title_tokens(title: object) -> set[str]:
    t = _safe_str(title).upper()
    t = re.sub(r"[^A-Z0-9&]+", " ", t)
    tokens = {tok for tok in t.split() if tok and tok not in STOPWORDS and not tok.isdigit()}
    return tokens


def shared_anchor_tokens(supplier_title: object, amazon_title: object, supplier_brand: str) -> list[str]:
    sup_tokens = _title_tokens(supplier_title)
    amz_tokens = _title_tokens(amazon_title)
    if supplier_brand:
        for part in _title_tokens(supplier_brand):
            sup_tokens.discard(part)
            amz_tokens.discard(part)
    shared = sorted(sup_tokens.intersection(amz_tokens))
    return shared[:8]


def title_similarity(a: object, b: object) -> float:
    from difflib import SequenceMatcher

    a_s = _safe_str(a).lower()
    b_s = _safe_str(b).lower()
    if not a_s or not b_s:
        return 0.0
    seq = SequenceMatcher(None, a_s, b_s).ratio()
    a_tok = {t for t in re.findall(r"[a-z0-9]+", a_s) if t not in {w.lower() for w in STOPWORDS}}
    b_tok = {t for t in re.findall(r"[a-z0-9]+", b_s) if t not in {w.lower() for w in STOPWORDS}}
    if not a_tok or not b_tok:
        jacc = 0.0
    else:
        jacc = len(a_tok & b_tok) / len(a_tok | b_tok)
    return 0.7 * seq + 0.3 * jacc


_DIMENSION_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(cm|mm|inch|in|m)\b", re.I)
_DIMENSION_RE2 = re.compile(r"\b\d+\s*x\s*\d+\s*(mm|cm|m|in|inch)\b", re.I)
_HARD_DIMENSION_TOKEN = re.compile(r"\b\d{2,4}\s*x\s*\d{2,4}\s*(mm|cm)\b", re.I)  # e.g., 280x115mm


def extract_pack_quantity(title: object) -> float:
    t = _safe_str(title).lower()
    if not t:
        return 1.0

    # If title looks like pure dimension data, avoid treating it as quantity.
    if _HARD_DIMENSION_TOKEN.search(t):
        return 1.0

    patterns: list[re.Pattern[str]] = [
        re.compile(r"\bpack of\s*(\d+)\b", re.I),
        re.compile(r"\bset of\s*(\d+)\b", re.I),
        re.compile(r"\b(\d+)\s*-\s*pack\b", re.I),
        re.compile(r"\b(\d+)\s*pack\b", re.I),
        re.compile(r"\b(\d+)\s*pk\b", re.I),
        re.compile(r"\b(\d+)\s*pcs\b", re.I),
        re.compile(r"\b(\d+)\s*pieces?\b", re.I),
        re.compile(r"\b(\d+)\s*pairs?\b", re.I),
        re.compile(r"\b(\d+)\s*rolls?\b", re.I),
        re.compile(r"\b(\d+)\s*bags?\b", re.I),
        re.compile(r"\b(\d+)\s*containers?\b", re.I),
        # Common shorthand: 40x, 50 x, etc. (avoid "9 x 9 inch" etc)
        re.compile(r"\b(\d+)\s*x\b(?!\s*\d+\s*(cm|mm|inch|in|m)\b)", re.I),
        # Pack-of-N with capacity: "2 x 25ml" means pack 2, not 25.
        re.compile(r"\b(\d+)\s*x\s*\d+(?:\.\d+)?\s*(ml|l|ltr|litre|liter|g|kg|oz)\b", re.I),
    ]

    for pat in patterns:
        m = pat.search(t)
        if not m:
            continue

        if pat is patterns[-2]:
            # If the token sequence is actually dimensions, ignore.
            if _DIMENSION_RE.search(t) or _DIMENSION_RE2.search(t):
                continue

        try:
            qty = float(m.group(1))
        except Exception:
            continue
        if 1 < qty < 500:
            return qty
    return 1.0


def extract_capacity_ml(title: object) -> float | None:
    t = _safe_str(title).lower()
    if not t:
        return None

    matches: list[tuple[float, str]] = []
    for num, unit in re.findall(r"\b(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|liter)\b", t, flags=re.I):
        try:
            val = float(num)
        except ValueError:
            continue
        u = unit.lower()
        ml = val * 1000.0 if u in ("l", "ltr", "litre", "liter") else val
        if ml > 0:
            matches.append((ml, "ml"))

    if not matches:
        return None
    # Use the largest capacity mentioned (more stable for multi-size marketing phrases)
    return max(v for v, _ in matches)


def extract_weight_g(title: object) -> float | None:
    t = _safe_str(title).lower()
    if not t:
        return None

    matches: list[float] = []
    for num, unit in re.findall(r"\b(\d+(?:\.\d+)?)\s*(g|kg|oz)\b", t, flags=re.I):
        try:
            val = float(num)
        except ValueError:
            continue
        u = unit.lower()
        if u == "kg":
            g = val * 1000.0
        elif u == "oz":
            g = val * 28.3495
        else:
            g = val
        if g > 0:
            matches.append(g)
    return max(matches) if matches else None


def detect_variant_mismatch(sup_title: object, amz_title: object) -> tuple[bool, str]:
    sup = _safe_str(sup_title).upper()
    amz = _safe_str(amz_title).upper()
    if not sup or not amz:
        return False, ""

    def _find(group: set[str], text: str) -> set[str]:
        return {w for w in group if w in text}

    sup_sc = _find(VARIANT_SCENTS, sup)
    amz_sc = _find(VARIANT_SCENTS, amz)
    if sup_sc and amz_sc and sup_sc.isdisjoint(amz_sc):
        return True, f"Scent mismatch: {sorted(sup_sc)} vs {sorted(amz_sc)}"

    sup_col = _find(VARIANT_COLORS, sup)
    amz_col = _find(VARIANT_COLORS, amz)
    if sup_col and amz_col and sup_col.isdisjoint(amz_col):
        return True, f"Color mismatch: {sorted(sup_col)} vs {sorted(amz_col)}"

    sup_sz = _find(VARIANT_SIZES, sup)
    amz_sz = _find(VARIANT_SIZES, amz)
    if sup_sz and amz_sz and sup_sz.isdisjoint(amz_sz):
        return True, f"Size mismatch: {sorted(sup_sz)} vs {sorted(amz_sz)}"

    sup_mat = _find(VARIANT_MATERIALS, sup)
    amz_mat = _find(VARIANT_MATERIALS, amz)
    if sup_mat and amz_mat and sup_mat.isdisjoint(amz_mat):
        return True, f"Material mismatch: {sorted(sup_mat)} vs {sorted(amz_mat)}"

    return False, ""


def _capacity_assessment(sup_title: object, amz_title: object) -> tuple[bool, str, float | None]:
    sup_ml = extract_capacity_ml(sup_title)
    amz_ml = extract_capacity_ml(amz_title)
    if sup_ml and amz_ml:
        rel = abs(sup_ml - amz_ml) / max(sup_ml, amz_ml)
        if rel > 0.50:
            return True, f"Capacity mismatch (>50%): {sup_ml:.0f}ml vs {amz_ml:.0f}ml", rel
        if rel > 0.30:
            return False, f"Capacity variance (30–50%): {sup_ml:.0f}ml vs {amz_ml:.0f}ml", rel
        if rel > 0.0:
            return False, f"Capacity variance (<=30%): {sup_ml:.0f}ml vs {amz_ml:.0f}ml", rel

    sup_g = extract_weight_g(sup_title)
    amz_g = extract_weight_g(amz_title)
    if sup_g and amz_g:
        rel = abs(sup_g - amz_g) / max(sup_g, amz_g)
        if rel > 0.50:
            return True, f"Weight mismatch (>50%): {sup_g:.0f}g vs {amz_g:.0f}g", rel
        if rel > 0.30:
            return False, f"Weight variance (30–50%): {sup_g:.0f}g vs {amz_g:.0f}g", rel
        if rel > 0.0:
            return False, f"Weight variance (<=30%): {sup_g:.0f}g vs {amz_g:.0f}g", rel

    return False, "", None


def _to_float(value: object) -> float:
    s = _safe_str(value)
    if not s:
        return 0.0
    try:
        return float(s)
    except Exception:
        return 0.0


def choose_sales_column(df: pd.DataFrame) -> str | None:
    for col in ("sales_numeric", "bought_in_past_month", "Sales"):
        if col in df.columns:
            return col
    return None


def choose_selling_price_column(df: pd.DataFrame) -> str | None:
    for col in ("SellingPrice_incVAT", "SellingPrice"):
        if col in df.columns:
            return col
    return None


def assign_category_v41(row: dict) -> tuple[str, str]:
    is_exact_ean = row["is_exact_ean_strict"]
    net_profit = row["NetProfit"]
    adjusted_profit = row["Adjusted_Profit"]
    sales = row["Sales"]
    brand_match = row["brand_match"]
    starts_invalid = row["starts_invalid"]
    title_sim = row["title_similarity"]
    variant_mismatch = row["variant_mismatch"]
    variant_reason = row["variant_reason"]
    cap_hard_mismatch = row["capacity_hard_mismatch"]
    cap_note = row["capacity_note"]
    qty_ratio = row["Qty_Ratio"]
    qty_note = row["Pack_Verdict"]

    # FILTERED OUT first: confirmed match + contradiction (variant mismatch)
    if (variant_mismatch or cap_hard_mismatch) and (brand_match or is_exact_ean):
        reason = variant_reason if variant_mismatch else cap_note
        return "FILTERED OUT", f"Confirmed match; {reason}"

    # Exact-EAN path: pack sanity before VERIFIED
    if is_exact_ean:
        if adjusted_profit <= 0:
            return "FILTERED OUT", f"Exact EAN; pack ratio {qty_ratio:.2f}x makes profit <= 0"
        if sales <= 0:
            return "NEEDS VERIFICATION", "Exact EAN but Sales=0; verify demand"
        if cap_note and not cap_hard_mismatch:
            return "NEEDS VERIFICATION", f"Exact EAN but {cap_note}; verify variant"
        if net_profit > 0 and adjusted_profit > 0:
            if qty_note:
                return "VERIFIED", "Exact EAN match; pack check applied"
            return "VERIFIED", "Exact EAN match"
        return "FILTERED OUT", "Exact EAN but profit negative"

    # HIGHLY LIKELY: strict brand rules + profit + sales + similarity
    if brand_match and not starts_invalid and not variant_mismatch and not cap_hard_mismatch:
        if adjusted_profit <= 0:
            return "FILTERED OUT", "Brand match; adjusted profit <= 0 due to pack"
        if sales <= 0:
            return "NEEDS VERIFICATION", "Brand match but Sales=0; verify demand"
        if title_sim >= 0.55 and net_profit > 0.10 and adjusted_profit > 0.10:
            if cap_note:
                return "NEEDS VERIFICATION", f"Brand match but {cap_note}; verify variant"
            if qty_note:
                return "NEEDS VERIFICATION", "Brand match but pack size needs verification"
            return "HIGHLY LIKELY", f"Brand match: {row['supplier_brand']}"

    # NEEDS VERIFICATION: brand visible OR similarity; selective; positive profit thresholds
    if (brand_match or title_sim >= 0.55) and adjusted_profit > 0.50 and row["ROI"] > 15:
        if net_profit > 0:
            needs = []
            if qty_note:
                needs.append("pack size")
            if cap_note:
                needs.append("capacity/variant")
            if not needs:
                needs.append("match details")
            return "NEEDS VERIFICATION", f"Verify {', '.join(needs)}"

    # FILTERED OUT: evidence but negative after pack
    if adjusted_profit <= 0 and (brand_match or title_sim >= 0.50):
        return "FILTERED OUT", "Match evidence but profit <= 0 after pack sanity"

    return "OTHER", "Insufficient match evidence"


def compute_confidence(row: dict) -> int:
    if row["is_exact_ean_strict"]:
        conf = 95
        if row["Pack_Verdict"]:
            conf = min(conf, 90)
        if row["variant_mismatch"] or row["capacity_hard_mismatch"]:
            conf = min(conf, 85)
        if row["Sales"] <= 0:
            conf = min(conf, 90)
        return conf

    base = int(round(row["title_similarity"] * 100))
    if row["brand_match"]:
        base = min(90, base + 10)
    if row["starts_invalid"]:
        base = max(0, base - 10)
    if row["Pack_Verdict"]:
        base = max(0, base - 5)
    if row["capacity_note"]:
        base = max(0, base - 3)
    return max(0, min(100, base))


def format_fixed_width_table(headers: list[str], rows: list[list[str]], max_widths: dict[str, int]) -> str:
    widths: list[int] = []
    for idx, h in enumerate(headers):
        max_len = max([len(h)] + [len(r[idx]) for r in rows]) if rows else len(h)
        cap = max_widths.get(h)
        if cap is not None:
            max_len = min(max_len, cap)
        widths.append(max_len)

    def _cell(text: str, width: int) -> str:
        if len(text) > width:
            if width <= 1:
                return text[:width]
            return text[: width - 1] + "…"
        return text.ljust(width)

    lines = []
    lines.append("| " + " | ".join(_cell(h, widths[i]) for i, h in enumerate(headers)) + " |")
    lines.append("|-" + "-|-".join("-" * widths[i] for i in range(len(headers))) + "-|")
    for r in rows:
        lines.append("| " + " | ".join(_cell(r[i], widths[i]) for i in range(len(headers))) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to the financial report XLSX/CSV")
    parser.add_argument("--outdir", required=True, help="Directory to write the markdown report + artifacts")
    parser.add_argument("--supplier", default="poundwholesale.co.uk", help="Supplier name (for report header)")
    parser.add_argument("--prompt-version", default="v4.1", help="Prompt version label")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    if input_path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(input_path, dtype={"EAN": "string", "EAN_OnPage": "string"})
    else:
        df = pd.read_csv(input_path, dtype={"EAN": "string", "EAN_OnPage": "string"})

    sales_col = choose_sales_column(df)
    selling_price_col = choose_selling_price_column(df)
    if sales_col is None:
        df["sales__v41"] = 0.0
        sales_col = "sales__v41"
    if selling_price_col is None:
        df["selling_price__v41"] = 0.0
        selling_price_col = "selling_price__v41"

    rows: list[dict] = []
    for idx, r in df.iterrows():
        supplier_title = r.get("SupplierTitle", "")
        amazon_title = r.get("AmazonTitle", "")

        sup_bc = normalize_barcode(r.get("EAN", ""))
        amz_bc = normalize_barcode(r.get("EAN_OnPage", ""))
        sup_ean = sup_bc.normalized if sup_bc.is_valid else None
        amz_ean = amz_bc.normalized if amz_bc.is_valid else None
        is_exact_ean = bool(sup_ean and amz_ean and sup_ean == amz_ean)

        supplier_brand = extract_known_brand(supplier_title)
        amazon_brand = extract_known_brand(amazon_title)
        brand_match = bool(supplier_brand and supplier_brand == amazon_brand)

        starts_invalid = starts_with_invalid_word(supplier_title)
        sim = title_similarity(supplier_title, amazon_title)

        sup_qty = extract_pack_quantity(supplier_title)
        amz_qty = extract_pack_quantity(amazon_title)
        qty_ratio = amz_qty / sup_qty if sup_qty else 1.0

        supplier_price = _to_float(r.get("SupplierPrice_incVAT", 0))
        selling_price = _to_float(r.get(selling_price_col, 0))
        net_profit = _to_float(r.get("NetProfit", 0))
        roi = _to_float(r.get("ROI", 0))
        sales = _to_float(r.get(sales_col, 0))

        adjusted_profit = net_profit
        pack_verdict = ""
        if amz_qty > sup_qty and sup_qty > 0:
            rsu = amz_qty / sup_qty
            adjusted_profit = net_profit - (rsu - 1) * supplier_price
            pack_verdict = f"Amz {amz_qty:g} vs Sup {sup_qty:g} (RSU={rsu:.2f})"
        elif sup_qty > amz_qty and amz_qty > 0:
            # Supplier multipack vs Amazon smaller pack/single. Can't assume break-down/repack is allowed.
            pack_verdict = f"Sup {sup_qty:g} vs Amz {amz_qty:g} (repack risk)"

        variant_mismatch, variant_reason = detect_variant_mismatch(supplier_title, amazon_title)
        cap_hard_mismatch, cap_note, _ = _capacity_assessment(supplier_title, amazon_title)

        shared_tokens = shared_anchor_tokens(supplier_title, amazon_title, supplier_brand)

        row = {
            "RowID": int(idx) + 1,
            "ASIN": _safe_str(r.get("ASIN", "")),
            "SupplierTitle": _safe_str(supplier_title),
            "AmazonTitle": _safe_str(amazon_title),
            "SupplierEAN": sup_ean or "-",
            "AmazonEAN": amz_ean or "-",
            "SupplierPrice": supplier_price,
            "SellingPrice": selling_price,
            "NetProfit": net_profit,
            "ROI": roi,
            "Sales": sales,
            "Sup_Qty": sup_qty,
            "Amz_Qty": amz_qty,
            "Qty_Ratio": qty_ratio,
            "Adjusted_Profit": adjusted_profit,
            "Pack_Verdict": pack_verdict,
            "supplier_brand": supplier_brand,
            "amazon_brand": amazon_brand,
            "brand_match": brand_match,
            "starts_invalid": starts_invalid,
            "title_similarity": sim,
            "variant_mismatch": variant_mismatch,
            "variant_reason": variant_reason,
            "capacity_hard_mismatch": cap_hard_mismatch,
            "capacity_note": cap_note,
            "shared_tokens": shared_tokens,
            "is_exact_ean_strict": is_exact_ean,
            "barcode_notes": f"Sup:{sup_bc.notes} Amz:{amz_bc.notes}",
        }

        verdict, filter_reason = assign_category_v41(row)
        row["Verdict"] = verdict
        row["FilterReason"] = filter_reason
        row["Confidence"] = compute_confidence(row)

        # Enforce acceptance tests: no Sales<=0 in VERIFIED/HIGHLY LIKELY
        if row["Verdict"] in ("VERIFIED", "HIGHLY LIKELY") and row["Sales"] <= 0:
            row["Verdict"] = "NEEDS VERIFICATION"
            row["FilterReason"] = "Sales=0; moved out of recommendations"

        # Enforce profitability in recommendations
        if row["Verdict"] in ("VERIFIED", "HIGHLY LIKELY") and (
            row["NetProfit"] <= 0 or row["Adjusted_Profit"] <= 0
        ):
            row["Verdict"] = "FILTERED OUT"
            row["FilterReason"] = "Non-profitable after pack sanity"

        rows.append(row)

    out_df = pd.DataFrame(rows)

    verified = out_df[out_df["Verdict"] == "VERIFIED"].sort_values(by="NetProfit", ascending=False)
    highly = out_df[out_df["Verdict"] == "HIGHLY LIKELY"].sort_values(by="Confidence", ascending=False)
    needs = out_df[out_df["Verdict"] == "NEEDS VERIFICATION"].sort_values(by="Confidence", ascending=False)
    filtered = out_df[out_df["Verdict"] == "FILTERED OUT"].sort_values(by="NetProfit", ascending=False)

    counts = {
        "VERIFIED": int(len(verified)),
        "HIGHLY LIKELY": int(len(highly)),
        "NEEDS VERIFICATION": int(len(needs)),
        "FILTERED OUT": int(len(filtered)),
        "TOTAL_ANALYZED": int(len(out_df)),
    }

    def _build_rows(frame: pd.DataFrame, limit: int | None = None) -> list[list[str]]:
        if limit is not None:
            frame = frame.head(limit)

        table_rows: list[list[str]] = []
        for _, rr in frame.iterrows():
            def _clean_cell(text: object) -> str:
                s = _safe_str(text)
                s = s.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                s = re.sub(r"\s+", " ", s).strip()
                s = s.replace("|", "¦")
                return s

            evidence_bits: list[str] = [f"RowID={int(rr['RowID'])}"]
            if rr["is_exact_ean_strict"]:
                evidence_bits.append("Exact EAN")
            if rr["brand_match"]:
                evidence_bits.append(f"Brand={rr['supplier_brand']}")
            if rr["shared_tokens"]:
                evidence_bits.append("Shared=" + ",".join(rr["shared_tokens"]))
            evidence_bits.append(f"Sim={rr['title_similarity']*100:.0f}%")
            if rr["barcode_notes"]:
                evidence_bits.append(rr["barcode_notes"])

            pack_verdict = rr["Pack_Verdict"] or "-"
            if rr["Pack_Verdict"] and rr["Adjusted_Profit"] != rr["NetProfit"]:
                pack_verdict = f"{rr['Pack_Verdict']}; AdjProfit={rr['Adjusted_Profit']:.2f}"

            filter_reason = rr["FilterReason"] if rr["Verdict"] == "FILTERED OUT" else "-"

            table_rows.append(
                [
                    _clean_cell(rr["Verdict"]),
                    str(int(rr["Confidence"])),
                    _clean_cell(rr["SupplierTitle"]),
                    _clean_cell(rr["AmazonTitle"]),
                    _clean_cell(rr["SupplierEAN"]),
                    _clean_cell(rr["AmazonEAN"]),
                    _clean_cell(rr["ASIN"] or "-"),
                    f"{rr['SupplierPrice']:.3f}",
                    f"{rr['SellingPrice']:.2f}",
                    f"{rr['NetProfit']:.2f}",
                    f"{rr['ROI']:.2f}",
                    f"{rr['Sales']:.0f}",
                    _clean_cell(pack_verdict),
                    f"{rr['Adjusted_Profit']:.2f}",
                    _clean_cell("; ".join(evidence_bits)),
                    _clean_cell(filter_reason),
                ]
            )
        return table_rows

    headers = [
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

    max_widths = {
        "SupplierTitle": 80,
        "AmazonTitle": 90,
        "Key Match Evidence": 120,
        "Pack Verdict": 60,
        "Filter Reason": 80,
    }

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_tag = datetime.now().strftime("%Y%m%d")
    report_path = outdir / f"PHASEA_MANUAL_REPORT_{date_tag}_v41.md"
    debug_csv_path = outdir / f"PHASEA_MANUAL_REPORT_{date_tag}_v41_debug.csv"

    out_df.to_csv(debug_csv_path, index=False, encoding="utf-8-sig")

    def _section(title: str, frame: pd.DataFrame, sorted_note: str) -> str:
        row_list = _build_rows(frame)
        table = format_fixed_width_table(headers, row_list, max_widths=max_widths)
        return (
            f"## {title} (count={len(frame)})\n"
            f"*{sorted_note}*\n\n"
            "```text\n" + table + "\n```\n"
        )

    md = []
    md.append("# PHASEA MANUAL REPORT")
    md.append("")
    md.append(f"**Generated:** {now}")
    md.append(f"**Input File:** {input_path}")
    md.append(f"**Supplier:** {args.supplier}")
    md.append(f"**Prompt Version:** {args.prompt_version}")
    md.append("")
    md.append("## Summary Counts")
    md.append(f"- VERIFIED: {counts['VERIFIED']}")
    md.append(f"- HIGHLY LIKELY: {counts['HIGHLY LIKELY']}")
    md.append(f"- NEEDS VERIFICATION: {counts['NEEDS VERIFICATION']}")
    md.append(f"- FILTERED OUT: {counts['FILTERED OUT']}")
    md.append(f"- TOTAL ANALYZED: {counts['TOTAL_ANALYZED']}")
    md.append("")
    md.append(
        "Note: `RowID` is embedded at the start of `Key Match Evidence` for traceability while preserving the v4.1 table schema."
    )
    md.append("")

    md.append(_section("VERIFIED", verified, "Sorted by NetProfit descending"))
    md.append(_section("HIGHLY LIKELY", highly, "Sorted by Confidence descending"))
    md.append(_section("NEEDS VERIFICATION", needs, "Sorted by Confidence descending"))
    md.append(_section("FILTERED OUT", filtered, "Sorted by NetProfit descending"))

    other_counts = out_df["Verdict"].value_counts().to_dict()
    md.append("## Reconciliation")
    md.append(f"- Total rows in input: {len(df)}")
    md.append(
        "- Rows categorized (VERIFIED+HIGHLY LIKELY+NEEDS VERIFICATION+FILTERED OUT): "
        f"{counts['VERIFIED'] + counts['HIGHLY LIKELY'] + counts['NEEDS VERIFICATION'] + counts['FILTERED OUT']}"
    )
    md.append(f"- Other/uncategorized (e.g., OTHER): {other_counts.get('OTHER', 0)}")
    md.append("")
    md.append("## Output Files")
    md.append(f"- Markdown report: `{report_path}`")
    md.append(f"- Debug CSV (all rows + computed fields): `{debug_csv_path}`")
    md.append("")

    report_path.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote: {report_path}")
    print(f"Wrote: {debug_csv_path}")
    print("Counts:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
