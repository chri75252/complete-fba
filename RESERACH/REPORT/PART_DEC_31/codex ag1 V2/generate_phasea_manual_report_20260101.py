from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import numpy as np
import pandas as pd


# --- CALIBRATION CONFIGURATION (from preflight) ---
SUPPLIER_NAMING_CONVENTION: dict[str, Any] = {
    "explicit_units": ["pc", "pcs", "pce", "piece", "pieces", "pk", "pack", "case", "cases", "each"],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "m", "kg", "g", "oz", "inch", "in", "w"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
}
# -----------------------------------------------


TABLE_COLUMNS: list[str] = [
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
    "at",
    "by",
    "from",
    "set",
    "kit",
    "new",
    "model",
    "pack",
    "packs",
    "pk",
    "pcs",
    "pc",
    "pce",
    "piece",
    "pieces",
    "case",
    "cases",
    "each",
    "assorted",
}


DIM_UNITS = set(SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"])

COUNT_NOUNS = {
    "bag",
    "bags",
    "balloon",
    "balloons",
    "bottle",
    "bottles",
    "container",
    "containers",
    "cup",
    "cups",
    "doyley",
    "doyleys",
    "glass",
    "glasses",
    "hook",
    "hooks",
    "lid",
    "lids",
    "mat",
    "mats",
    "napkin",
    "napkins",
    "pad",
    "pads",
    "peg",
    "pegs",
    "plate",
    "plates",
    "roller",
    "rollers",
    "stick",
    "sticks",
    "trap",
    "traps",
    "tray",
    "trays",
    "wipe",
    "wipes",
}

COUNT_NOUNS_PATTERN = "|".join(sorted(COUNT_NOUNS, key=len, reverse=True))


@dataclass(frozen=True)
class PackInfo:
    sup_qty: int
    amz_total: int
    rsu: int
    pack_mode: str  # "1:1" | "bundle" | "split"
    pack_verdict: str


def _coerce_to_intlike_string(x: Any) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return ""
    if isinstance(x, (np.integer, int)):
        return str(int(x))
    if isinstance(x, (np.floating, float)):
        if abs(x - round(x)) < 1e-6:
            return str(int(round(x)))
        return str(x)
    return str(x)


def clean_to_digits(x: Any) -> str:
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
    if not norm.isdigit() or len(norm) not in (8, 12, 13, 14):
        return False
    if re.fullmatch(r"0+", norm):
        return False
    if re.search(r"0{6,}$", norm):
        return False
    return gtin_checksum_ok(norm)


def title_similarity(a: Any, b: Any) -> float:
    if a is None or b is None or (isinstance(a, float) and not np.isfinite(a)) or (isinstance(b, float) and not np.isfinite(b)):
        return 0.0
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def _tokenize(title: str) -> list[str]:
    t = str(title).lower()
    t = re.sub(r"[^a-z0-9&×x ]+", " ", t)
    raw = [p for p in t.split() if p]
    out: list[str] = []
    for tok in raw:
        if tok.isdigit():
            continue
        if tok in STOPWORDS:
            continue
        if tok in DIM_UNITS:
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", tok):
            continue
        out.append(tok)
    return out


def _extract_brand_candidate(supplier_title: str) -> str:
    t = str(supplier_title).strip()
    if not t:
        return ""
    first = re.split(r"\s+", t)[0]
    if first.isdigit():
        return ""
    # Handle "BRIGHT & HOMELY ..." style
    m = re.match(r"^([A-Za-z]{2,}(?:\s*&\s*[A-Za-z]{2,}){1,2})\b", t)
    if m:
        return m.group(1).strip()
    # Otherwise, take first token as brand-like if long enough
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9&'\-]{2,}", first):
        return first
    return ""


def _brand_matches(brand: str, amazon_title: str) -> bool:
    if not brand:
        return False
    return re.search(rf"\b{re.escape(brand)}\b", str(amazon_title), re.IGNORECASE) is not None


def _shared_anchor_tokens(supplier_title: str, amazon_title: str, limit: int = 5) -> list[str]:
    s_tokens = set(_tokenize(supplier_title))
    a_tokens = set(_tokenize(amazon_title))
    shared = sorted((s_tokens & a_tokens), key=lambda x: (-len(x), x))
    shared = [t for t in shared if len(t) >= 4]
    return shared[:limit]


def _nxm_is_dimension(title_lower: str, span: tuple[int, int]) -> bool:
    s, e = span
    window = title_lower[max(0, s - 10) : min(len(title_lower), e + 12)]
    # Treat NxM as dimensions only if a real measurement unit is present near the match.
    if re.search(r"\b\d+(?:\.\d+)?\s*(cm|mm|ml|g|kg|ltr|l)\b", window):
        return True
    if re.search(r"\b\d+(?:\.\d+)?\s*(inch|in)\b", window):
        return True
    if re.search(r"\b\d+(?:\.\d+)?\s*w\b", window):
        return True
    return False


def extract_supplier_qty(title: str) -> int:
    t = str(title).lower().strip()

    patterns = [
        r"\b(\d+)\s*(pc|pcs|pce)\b",
        r"\b(\d+)\s*pieces?\b",
        r"\b(\d+)\s*cases?\b",
        r"\bpk\s*(\d+)\b",
        r"\bpk(\d+)\b",
        r"\b(\d+)\s*pack\b",
        r"\b(\d+)pack\b",
    ]
    for pat in patterns:
        m = re.search(pat, t, re.IGNORECASE)
        if m:
            n = int(m.group(1))
            return max(1, n)

    m = re.search(rf"\b(\d{{1,4}})\s*(?:{COUNT_NOUNS_PATTERN})\b", t)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 500:
            return n

    if SUPPLIER_NAMING_CONVENTION.get("allow_trailing_number_as_qty", False):
        m = re.search(r"\b(\d{1,4})\s*$", t)
        if m:
            n = int(m.group(1))
            # Calibration warnings: small trailing numbers often represent variants (e.g., "GIRL 3", "NUMBER ... 6")
            if n <= 12 and re.search(r"\b(number|girl|boy|w/decor|decor)\b", t):
                return 1
            if n <= 12 and re.search(r"\bbadge\b", t):
                return 1
            if n <= 12 and re.search(r"\bcandle\b", t) and re.search(r"\bnumber\b", t):
                return 1
            # Otherwise treat as qty-inside only if it looks like a countable line item
            if re.search(r"\b(balloon|balloons|sticks|straws|plates|cups|napkins|doyleys|bags)\b", t):
                return max(1, n)

    return 1


def extract_amazon_total(title: str) -> int:
    t = str(title).lower().strip()

    # Multipack "(4 x 50)" / "4 x 50" patterns (skip dimensions)
    best_total = 1

    # Multipack count x capacity, e.g. "5 x 30 ml" -> 5 units (NOT 150)
    m = re.search(r"\b(\d{1,3})\s*[x×]\s*(\d+(?:\.\d+)?)\s*(ml|g|kg|l|ltr)\b", t)
    if m:
        best_total = max(best_total, int(m.group(1)))

    for m in re.finditer(r"\b(\d{1,3})\s*[x×]\s*(\d{1,4})\b", t):
        if _nxm_is_dimension(t, m.span()):
            continue
        outer = int(m.group(1))
        inner = int(m.group(2))
        if 1 <= outer <= 100 and 1 <= inner <= 5000:
            best_total = max(best_total, outer * inner)

    # "40 x doyleys" / "200 x bags" patterns (total items)
    m = re.search(rf"\b(\d{{1,4}})\s*[x×]\s*(?:{COUNT_NOUNS_PATTERN})\b", t)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 500:
            best_total = max(best_total, n)

    # "40 x White ... DOYLEYS" (count noun not immediately after 'x')
    m = re.search(r"\b(\d{1,4})\s*[x×]\s+", t)
    if m:
        tail = t[m.end() : m.end() + 80]
        if re.search(rf"\b(?:{COUNT_NOUNS_PATTERN})\b", tail):
            n = int(m.group(1))
            if 1 <= n <= 500:
                best_total = max(best_total, n)

    # "pack of 10" / "10-pack" / "10 pack"
    m = re.search(r"\bpack of\s*(\d{1,3})\b", t)
    if m:
        best_total = max(best_total, int(m.group(1)))
    m = re.search(r"\b(\d{1,3})\s*-\s*pack\b", t)
    if m:
        best_total = max(best_total, int(m.group(1)))
    m = re.search(r"\b(\d{1,3})\s*pack\b", t)
    if m and not re.search(r"\b(\d{1,3})\s*pack(?:et)?\b", t):
        best_total = max(best_total, int(m.group(1)))

    # "42 pcs", "20 pieces", "5 bottles"
    m = re.search(rf"\b(\d{{1,4}})\s*(?:pc|pcs|pce|pieces?|{COUNT_NOUNS_PATTERN})\b", t)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 500:
            best_total = max(best_total, n)

    # "pk6" / "pk 6"
    m = re.search(r"\bpk\s*(\d{1,3})\b", t) or re.search(r"\bpk(\d{1,3})\b", t)
    if m:
        best_total = max(best_total, int(m.group(1)))

    # Leading multiplier "3 x Product" (if enabled; preflight says uncommon, so skip by default)
    if SUPPLIER_NAMING_CONVENTION.get("leading_multiplier_check", False):
        m = re.match(r"^\s*(\d{1,3})\s*[x×]\s+", t)
        if m:
            best_total = max(best_total, int(m.group(1)))

    return max(1, best_total)


def compute_pack_info(supplier_title: str, amazon_title: str) -> PackInfo:
    sup_qty = extract_supplier_qty(supplier_title)
    amz_total = extract_amazon_total(amazon_title)

    if sup_qty <= 0 or amz_total <= 0:
        return PackInfo(sup_qty=1, amz_total=1, rsu=1, pack_mode="1:1", pack_verdict="1:1 Match")

    if sup_qty > 1 and amz_total > 1 and sup_qty == amz_total:
        return PackInfo(
            sup_qty=sup_qty,
            amz_total=amz_total,
            rsu=1,
            pack_mode="1:1",
            pack_verdict="1:1 Match (Qty-inside equality shield)",
        )

    if amz_total > sup_qty:
        ratio = amz_total / sup_qty
        rsu = int(math.ceil(ratio))
        warn = "" if abs(ratio - round(ratio)) < 1e-9 else "; non-divisible bundle (verify)"
        return PackInfo(
            sup_qty=sup_qty,
            amz_total=amz_total,
            rsu=max(1, rsu),
            pack_mode="bundle",
            pack_verdict=f"BUNDLE (RSU={max(1, rsu)}){warn}",
        )

    if sup_qty > amz_total and sup_qty > 1:
        return PackInfo(
            sup_qty=sup_qty,
            amz_total=amz_total,
            rsu=1,
            pack_mode="split",
            pack_verdict="SPLIT (Supplier pack larger) - VERIFY separability",
        )

    return PackInfo(sup_qty=sup_qty, amz_total=amz_total, rsu=1, pack_mode="1:1", pack_verdict="1:1 Match")


def _parse_number_with_unit(title: str) -> dict[str, float]:
    t = str(title).lower()
    out: dict[str, float] = {}

    for m in re.finditer(r"\b(\d+(?:\.\d+)?)\s*(ml|l|ltr)\b", t):
        val = float(m.group(1))
        unit = m.group(2)
        ml = val * 1000.0 if unit in ("l", "ltr") else val
        out["ml"] = ml
        break

    for m in re.finditer(r"\b(\d+(?:\.\d+)?)\s*(g|kg)\b", t):
        val = float(m.group(1))
        unit = m.group(2)
        g = val * 1000.0 if unit == "kg" else val
        out["g"] = g
        break

    return out


def _capacity_verdict(supplier_title: str, amazon_title: str) -> tuple[str, str]:
    s = _parse_number_with_unit(supplier_title)
    a = _parse_number_with_unit(amazon_title)
    for unit in ("ml", "g"):
        if unit in s and unit in a and s[unit] > 0 and a[unit] > 0:
            diff = abs(s[unit] - a[unit]) / max(s[unit], a[unit])
            if diff <= 0.10:
                return ("ok", f"Capacity within 10% ({s[unit]:g}{unit} vs {a[unit]:g}{unit})")
            if diff <= 0.25:
                return ("verify", f"Capacity 10-25% ({s[unit]:g}{unit} vs {a[unit]:g}{unit})")
            if diff <= 0.50:
                return ("filter", f"Capacity 25-50% ({s[unit]:g}{unit} vs {a[unit]:g}{unit})")
            return ("filter", f"Capacity >50% ({s[unit]:g}{unit} vs {a[unit]:g}{unit})")
    return ("unknown", "")


def _fmt_money(x: Any) -> str:
    try:
        v = float(x)
        if not np.isfinite(v):
            return "-"
        return f"£{v:.2f}"
    except Exception:
        return "-"


def _fmt_num(x: Any) -> str:
    try:
        v = float(x)
        if not np.isfinite(v):
            return "-"
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return f"{v:.2f}"
    except Exception:
        return "-"


def _safe_float_from_cell(text: str) -> float:
    try:
        s = str(text).strip().replace("£", "")
        if not s or s == "-":
            return 0.0
        return float(s)
    except Exception:
        return 0.0


def _fixed_width_table(rows: list[dict[str, str]]) -> str:
    cols = TABLE_COLUMNS
    widths = {c: len(c) for c in cols}
    for r in rows:
        for c in cols:
            widths[c] = max(widths[c], len(r.get(c, "")))

    def line(values: Iterable[str]) -> str:
        parts = []
        for c, v in zip(cols, values, strict=True):
            parts.append(f" {v:<{widths[c]}} ")
        return "|" + "|".join(parts) + "|"

    header = line(cols)
    sep = "|" + "|".join("-" * (widths[c] + 2) for c in cols) + "|"
    body = "\n".join(line(r.get(c, "") for c in cols) for r in rows)
    return "\n".join([header, sep, body]) if body else "\n".join([header, sep])


def _domain_from_url(url: Any) -> str:
    try:
        u = str(url)
        if not u or u.lower() == "nan":
            return ""
        netloc = urlparse(u).netloc.lower()
        return netloc.replace("www.", "")
    except Exception:
        return ""


def _confidence(is_exact_ean: bool, brand_match: bool, shared_tokens: list[str], title_match: float) -> int:
    if is_exact_ean:
        return 95
    score = 35
    if brand_match:
        score += 30
    score += min(20, int(round(title_match * 40)))
    score += min(15, 5 * len(shared_tokens))
    return max(0, min(100, score))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx",
    )
    parser.add_argument("--sheet", default="Sheet1")
    parser.add_argument(
        "--output",
        default=r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\codex ag1 V2\PHASEA_MANUAL_REPORT_20260101.md",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    ext = input_path.suffix.lower()
    if ext in {".xlsx", ".xls"}:
        df = pd.read_excel(input_path, sheet_name=args.sheet)
    else:
        df = pd.read_csv(input_path, encoding="utf-8-sig")

    df = df.copy()
    df["RowID"] = df.index + 1

    sales_col = None
    for c in ["sales_numeric", "bought_in_past_month", "sales", "Sales"]:
        if c in df.columns:
            sales_col = c
            break
    df["Sales"] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0) if sales_col else 0

    df["EAN_digits"] = df["EAN"].apply(clean_to_digits) if "EAN" in df.columns else ""
    df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(clean_to_digits) if "EAN_OnPage" in df.columns else ""
    df["EAN_norm"] = df["EAN_digits"].apply(normalize_ean)
    df["EAN_OnPage_norm"] = df["EAN_OnPage_digits"].apply(normalize_ean)
    df["EAN_strict_valid"] = df["EAN_norm"].apply(is_strict_valid_barcode)
    df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_norm"].apply(is_strict_valid_barcode)
    df["is_exact_ean_strict"] = (
        df["EAN_strict_valid"] & df["EAN_OnPage_strict_valid"] & (df["EAN_norm"] == df["EAN_OnPage_norm"])
    )

    df["title_match"] = df.apply(lambda r: title_similarity(r.get("SupplierTitle"), r.get("AmazonTitle")), axis=1)

    # Infer supplier domain (for report header only)
    supplier_domain = ""
    if "SupplierURL" in df.columns:
        domains = df["SupplierURL"].apply(_domain_from_url)
        top = domains.value_counts(dropna=True)
        if not top.empty:
            supplier_domain = str(top.index[0])

    # Per-row derived fields and categorization
    rows_verified_rec: list[dict[str, str]] = []
    rows_verified_filtered: list[dict[str, str]] = []
    rows_hl_rec: list[dict[str, str]] = []
    rows_hl_filtered: list[dict[str, str]] = []
    rows_nv_pool: list[tuple[int, float, float, dict[str, str]]] = []  # (conf, title_match, sales, row)

    for _, r in df.iterrows():
        supplier_title = str(r.get("SupplierTitle") or "")
        amazon_title = str(r.get("AmazonTitle") or "")

        is_exact = bool(r.get("is_exact_ean_strict", False))
        ean_sup = r.get("EAN_norm") if bool(r.get("EAN_strict_valid", False)) else "-"
        ean_amz = r.get("EAN_OnPage_norm") if bool(r.get("EAN_OnPage_strict_valid", False)) else "-"

        brand = _extract_brand_candidate(supplier_title)
        brand_match = _brand_matches(brand, amazon_title)
        shared = _shared_anchor_tokens(supplier_title, amazon_title)
        conf = _confidence(is_exact, brand_match, shared, float(r.get("title_match", 0.0)))

        pack = compute_pack_info(supplier_title, amazon_title)
        supplier_price = r.get("SupplierPrice_incVAT", r.get("SupplierPrice", ""))
        selling_price = r.get("SellingPrice_incVAT", r.get("SellingPrice", ""))
        net_profit = r.get("NetProfit", "")
        roi = r.get("ROI", "")
        sales = float(r.get("Sales", 0) or 0)

        adjusted_profit = None
        try:
            original_profit = float(net_profit)
            cost = float(supplier_price)
            if pack.pack_mode == "bundle" and pack.rsu > 1:
                adjusted_profit = original_profit - cost * (pack.rsu - 1)
            else:
                adjusted_profit = original_profit
        except Exception:
            adjusted_profit = float("nan")

        cap_action, cap_note = _capacity_verdict(supplier_title, amazon_title)

        key_evidence = "Exact EAN match" if is_exact else "; ".join(
            [x for x in ([f"Brand: {brand}"] if brand_match and brand else []) + (shared[:3] if shared else [])]
        )
        if cap_note and key_evidence:
            key_evidence = f"{key_evidence}; {cap_note}"
        elif cap_note:
            key_evidence = cap_note

        profitable = np.isfinite(adjusted_profit) and adjusted_profit > 0 and float(_fmt_num(net_profit)) != "-"
        has_netprofit_pos = False
        try:
            has_netprofit_pos = float(net_profit) > 0
        except Exception:
            has_netprofit_pos = False

        recommended_gate = sales > 0 and has_netprofit_pos and np.isfinite(adjusted_profit) and adjusted_profit > 0

        base_row: dict[str, str] = {
            "Verdict": "",
            "Confidence": str(conf),
            "SupplierTitle": supplier_title,
            "AmazonTitle": amazon_title,
            "Supplier EAN": str(ean_sup),
            "Amazon EAN": str(ean_amz),
            "ASIN": str(r.get("ASIN") or "-"),
            "SupplierPrice": _fmt_money(supplier_price),
            "SellingPrice": _fmt_money(selling_price),
            "NetProfit": _fmt_money(net_profit),
            "ROI": _fmt_num(roi),
            "Sales": _fmt_num(sales),
            "Pack Verdict": pack.pack_verdict,
            "Adjusted Profit": _fmt_money(adjusted_profit),
            "Key Match Evidence": key_evidence or "-",
            "Filter Reason": "-",
        }

        # Exact EAN path
        if is_exact:
            # Exact-EAN downgrades: explicit pack/capacity contradictions + profitability gates
            if cap_action == "filter":
                base_row["Verdict"] = "FILTERED OUT"
                base_row["Filter Reason"] = cap_note or "Capacity mismatch >25%"
                rows_verified_filtered.append(base_row)
                continue

            if pack.pack_mode == "bundle" and adjusted_profit <= 0:
                base_row["Verdict"] = "FILTERED OUT"
                base_row["Filter Reason"] = "Requires multiple units; adjusted profit <= 0"
                rows_verified_filtered.append(base_row)
                continue

            if sales <= 0:
                base_row["Verdict"] = "NEEDS VERIFICATION"
                base_row["Filter Reason"] = "Sales=0 (route to verification, not recommendations)"
                rows_nv_pool.append((conf, float(r.get("title_match", 0.0)), sales, base_row))
                continue

            if not recommended_gate:
                base_row["Verdict"] = "FILTERED OUT"
                if not has_netprofit_pos:
                    base_row["Filter Reason"] = "NetProfit<=0"
                else:
                    base_row["Filter Reason"] = "Adjusted profit<=0"
                rows_verified_filtered.append(base_row)
                continue

            base_row["Verdict"] = "VERIFIED"
            rows_verified_rec.append(base_row)
            continue

        # Non-EAN: determine plausibility/confirmation level
        plausible = False
        if brand_match and shared:
            plausible = True
        elif float(r.get("title_match", 0.0)) >= 0.65 and shared:
            plausible = True

        if not plausible:
            continue

        # Capacity gating for non-EAN
        if cap_action == "filter":
            base_row["Verdict"] = "FILTERED OUT"
            base_row["Filter Reason"] = cap_note or "Capacity mismatch >25%"
            if brand_match and shared:
                rows_hl_filtered.append(base_row)
            continue

        # Pack gating: SPLIT always requires verification (not recommended)
        if pack.pack_mode == "split":
            base_row["Verdict"] = "NEEDS VERIFICATION"
            base_row["Filter Reason"] = "Supplier pack larger; split feasibility required"
            rows_nv_pool.append((conf, float(r.get("title_match", 0.0)), sales, base_row))
            continue

        if brand_match and shared and float(r.get("title_match", 0.0)) >= 0.35:
            # Highly Likely path (subject to profit gate)
            if recommended_gate:
                base_row["Verdict"] = "HIGHLY LIKELY"
                rows_hl_rec.append(base_row)
            else:
                if sales <= 0 and np.isfinite(adjusted_profit) and adjusted_profit > 0 and has_netprofit_pos:
                    base_row["Verdict"] = "NEEDS VERIFICATION"
                    base_row["Filter Reason"] = "Sales=0 (route to verification, not recommendations)"
                    rows_nv_pool.append((conf, float(r.get("title_match", 0.0)), sales, base_row))
                else:
                    base_row["Verdict"] = "FILTERED OUT"
                    if not has_netprofit_pos:
                        base_row["Filter Reason"] = "NetProfit<=0"
                    elif np.isfinite(adjusted_profit) and adjusted_profit <= 0:
                        base_row["Filter Reason"] = "Adjusted profit<=0 (pack mismatch)"
                    else:
                        base_row["Filter Reason"] = "Failed recommendation gates"
                    rows_hl_filtered.append(base_row)
            continue

        # Otherwise: Needs Verification (selective pool)
        if np.isfinite(adjusted_profit) and adjusted_profit > 0:
            base_row["Verdict"] = "NEEDS VERIFICATION"
            reason = "Confirm brand/product-type alignment (1-2 anchors)"
            if cap_action == "verify":
                reason = cap_note or "Capacity 10-25% (verify SKU)"
            base_row["Filter Reason"] = reason
            rows_nv_pool.append((conf, float(r.get("title_match", 0.0)), sales, base_row))

    # Sorting + NV cap (target 40-60)
    rows_verified_rec.sort(key=lambda rr: _safe_float_from_cell(rr.get("Sales", "0")), reverse=True)
    rows_hl_rec.sort(key=lambda rr: _safe_float_from_cell(rr.get("Sales", "0")), reverse=True)
    rows_verified_filtered.sort(key=lambda rr: _safe_float_from_cell(rr.get("Sales", "0")), reverse=True)
    rows_hl_filtered.sort(key=lambda rr: _safe_float_from_cell(rr.get("Sales", "0")), reverse=True)

    rows_nv_pool.sort(key=lambda t: (t[0], t[1], t[2]), reverse=True)
    nv_rows = [t[3] for t in rows_nv_pool[:60]]

    # Compose report
    generated = date(2026, 1, 1).isoformat()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sections: list[str] = []
    sections.append("# PHASEA MANUAL REPORT")
    sections.append(f"**Generated:** {generated}")
    sections.append(f"**Input File:** {str(input_path)}")
    sections.append(f"**Supplier:** {supplier_domain or '-'}")
    sections.append("")
    sections.append("## Summary Counts")
    sections.append(f"- VERIFIED — RECOMMENDED: {len(rows_verified_rec)}")
    sections.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(rows_verified_filtered)}")
    sections.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(rows_hl_rec)}")
    sections.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(rows_hl_filtered)}")
    sections.append(f"- NEEDS VERIFICATION: {len(nv_rows)}")
    sections.append(f"- TOTAL ANALYZED: {len(df)}")
    sections.append("")
    sections.append("## VERIFIED — RECOMMENDED - (count={})".format(len(rows_verified_rec)))
    sections.append("```text")
    sections.append(_fixed_width_table(rows_verified_rec))
    sections.append("```")
    sections.append("")
    sections.append("## VERIFIED — FILTERED OUT / EXCLUDED - (count={})".format(len(rows_verified_filtered)))
    sections.append("```text")
    sections.append(_fixed_width_table(rows_verified_filtered))
    sections.append("```")
    sections.append("")
    sections.append("## HIGHLY LIKELY — RECOMMENDED- (count={})".format(len(rows_hl_rec)))
    sections.append("```text")
    sections.append(_fixed_width_table(rows_hl_rec))
    sections.append("```")
    sections.append("")
    sections.append("## HIGHLY LIKELY — FILTERED OUT / EXCLUDED- (count={})".format(len(rows_hl_filtered)))
    sections.append("```text")
    sections.append(_fixed_width_table(rows_hl_filtered))
    sections.append("```")
    sections.append("")
    sections.append("## NEEDS VERIFICATION (count={})".format(len(nv_rows)))
    sections.append("```text")
    sections.append(_fixed_width_table(nv_rows))
    sections.append("```")
    sections.append("")
    sections.append("## Reconciliation")
    sections.append(f"- VERIFIED — RECOMMENDED: {len(rows_verified_rec)}")
    sections.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(rows_verified_filtered)}")
    sections.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(rows_hl_rec)}")
    sections.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(rows_hl_filtered)}")
    sections.append(f"- NEEDS VERIFICATION: {len(nv_rows)}")
    sections.append(f"- TOTAL ANALYZED: {len(df)}")
    sections.append("")

    output_path.write_text("\n".join(sections), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
