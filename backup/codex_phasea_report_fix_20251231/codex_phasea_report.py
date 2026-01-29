from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional
from zoneinfo import ZoneInfo

import pandas as pd


TABLE_COLUMNS = [
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
    "or",
    "with",
    "for",
    "to",
    "a",
    "an",
    "of",
    "in",
    "on",
    "at",
    "by",
    "from",
    "is",
    "are",
    "new",
    "genuine",
    "original",
    "uk",
    "pack",
    "packs",
    "set",
    "sets",
    "piece",
    "pieces",
    "pcs",
    "pce",
    "each",
    "x",
}

LUXURY_IP_RISK_BRANDS = {
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

MEASUREMENT_UNITS = {
    "inch",
    "in",
    "cm",
    "mm",
    "m",
    "ft",
    "ml",
    "l",
    "ltr",
    "litre",
    "liter",
    "g",
    "kg",
    "oz",
}

CAPACITY_UNITS = {"ml", "l", "ltr", "litre", "liter", "g", "kg", "oz"}
DIMENSION_UNITS = {"inch", "in", "cm", "mm", "m", "ft"}


def _is_nan_like(x: object) -> bool:
    if x is None:
        return True
    if isinstance(x, float) and math.isnan(x):
        return True
    s = str(x).strip().lower()
    return s in {"", "nan", "none", "null", "-", "0"}


def _clean_to_digits(raw: object) -> str:
    if _is_nan_like(raw):
        return ""
    if isinstance(raw, int):
        return str(raw)
    if isinstance(raw, float):
        if not math.isfinite(raw):
            return ""
        rounded = round(raw)
        if abs(raw - rounded) > 1e-6:
            return ""
        return str(int(rounded))
    s = str(raw).strip()
    if not s:
        return ""
    if "e" in s.lower():
        try:
            from decimal import Decimal

            d = Decimal(s)
            if d == d.to_integral_value():
                return str(int(d))
            return ""
        except Exception:
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
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check


def normalize_ean(digits: str) -> str:
    if not isinstance(digits, str) or not digits.isdigit():
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


def parse_float(x: object) -> Optional[float]:
    if _is_nan_like(x):
        return None
    if isinstance(x, (int, float)) and math.isfinite(float(x)):
        return float(x)
    s = str(x).strip().replace("£", "").replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None


def parse_int(x: object) -> int:
    v = parse_float(x)
    if v is None:
        return 0
    return int(round(v))


def title_similarity(a: str, b: str) -> float:
    from difflib import SequenceMatcher

    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _tokenize(title: str) -> list[str]:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return [t for t in s.split() if t and t not in STOPWORDS]


def _extract_upper_brand(title: str) -> Optional[str]:
    if not title:
        return None
    upper_tokens = re.findall(r"\b[A-Z]{3,}(?:\s+[A-Z]{3,})?\b", title)
    if not upper_tokens:
        return None
    return upper_tokens[0].strip()


def _brand_match(supplier_title: str, amazon_title: str) -> tuple[bool, Optional[str]]:
    brand = _extract_upper_brand(supplier_title) or _extract_upper_brand(amazon_title)
    if not brand:
        return False, None
    if brand.lower() in amazon_title.lower() and brand.lower() in supplier_title.lower():
        return True, brand
    return False, brand


def _shared_tokens(a: str, b: str) -> list[str]:
    ta = set(_tokenize(a))
    tb = set(_tokenize(b))
    shared = sorted(ta & tb, key=lambda t: (-len(t), t))
    return [t for t in shared if len(t) >= 3][:12]


def _key_match_evidence(
    supplier_title: str,
    amazon_title: str,
    exact_ean: bool,
    brand_hint: Optional[str],
) -> str:
    if exact_ean:
        return "Exact EAN match"
    shared = _shared_tokens(supplier_title, amazon_title)
    picked: list[str] = []
    if brand_hint and brand_hint.lower() in supplier_title.lower() and brand_hint.lower() in amazon_title.lower():
        picked.append(brand_hint.lower())
    for t in shared:
        if t in MEASUREMENT_UNITS:
            continue
        if t not in picked:
            picked.append(t)
        if len(picked) >= 6:
            break
    if not picked:
        return "-"
    return "Shared tokens: " + ", ".join(picked[:6])


def _contains_ip_risk_brand(s: str) -> bool:
    t = (s or "").lower()
    return any(b in t for b in LUXURY_IP_RISK_BRANDS)


def _as_money(x: Optional[float]) -> str:
    return f"{x:.2f}" if x is not None else "-"


_RE_PACK_WORDS = re.compile(r"\b(pack of|pack|pk|bundle|multipack|set of|set)\b", re.I)


def _extract_qty_inside(title: str) -> Optional[int]:
    if not title:
        return None
    s = title.lower()
    patterns = [
        r"\b(\d{1,4})\s*(?:pcs|pc|pce|pieces?)\b",
        r"\b(\d{1,4})\s*(?:cases|case)\b",
        r"\b(\d{1,4})\s*(?:bags|bag)\b",
        r"\b(\d{1,4})\s*(?:wipes|wipe)\b",
        r"\b(\d{1,4})\s*(?:sticks|stick)\b",
        r"\b(\d{1,4})\s*(?:doyleys|doyley)\b",
        r"\b(\d{1,4})\s*(?:containers?|lids?)\b",
        r"\b(\d{1,4})\s*(?:caps?)\b",
    ]
    for pat in patterns:
        m = re.search(pat, s)
        if m:
            try:
                val = int(m.group(1))
            except Exception:
                continue
            if 1 < val <= 5000:
                return val
    return None


def _extract_pack_count(title: str) -> Optional[int]:
    if not title:
        return None
    s = title.lower()
    patterns = [
        r"\bpack of\s*(\d{1,3})\b",
        r"\b(\d{1,3})\s*pack\b",
        r"\b(\d{1,3})-pack\b",
        r"\bset of\s*(\d{1,3})\b",
        r"\b(\d{1,3})\s*pk\b",
    ]
    for pat in patterns:
        m = re.search(pat, s)
        if m:
            try:
                val = int(m.group(1))
            except Exception:
                continue
            if 1 < val <= 200:
                return val
    return None


@dataclass(frozen=True)
class PackAnalysis:
    rsu: float
    verdict: str
    evidence: str
    rsu_confident: bool


def _extract_multipack(title: str) -> Optional[tuple[int, int, Optional[str]]]:
    if not title:
        return None
    s = title.lower()
    m = re.search(r"(\d{1,3})\s*[x×]\s*(\d{1,4})(?:\s*([a-z]{1,5}))?", s)
    if not m:
        return None
    outer = int(m.group(1))
    inner = int(m.group(2))
    unit = (m.group(3) or "").strip(".").lower() or None
    if outer <= 1 or inner <= 0:
        return None
    if outer > 200 or inner > 10000:
        return None
    return outer, inner, unit


def analyze_pack(supplier_title: str, amazon_title: str) -> PackAnalysis:
    sup_qty_inside = _extract_qty_inside(supplier_title)
    amz_qty_inside = _extract_qty_inside(amazon_title)
    sup_pack = _extract_pack_count(supplier_title) or 1
    amz_pack = _extract_pack_count(amazon_title) or 1

    mp = _extract_multipack(amazon_title)
    if mp:
        outer, inner, unit = mp

        # DIMENSION / MEASUREMENT SHIELD:
        # "9 x 9 inch" => dimensions, NOT pack, and NEVER 9*9 units.
        if unit in DIMENSION_UNITS and outer == inner and outer <= 60:
            return PackAnalysis(
                rsu=1.0,
                verdict="1:1 Match (dimension pattern)",
                evidence=f"Amazon has '{outer} x {inner} {unit}' (treated as dimensions)",
                rsu_confident=True,
            )

        # "N x <measurement>" => N-pack, DO NOT multiply by measurement.
        if unit in CAPACITY_UNITS | DIMENSION_UNITS:
            rsu = float(max(1, outer / max(1, sup_pack)))
            evidence = f"Amazon has '{outer} x {inner}{unit}' (outer treated as pack count)"
            if rsu.is_integer():
                return PackAnalysis(
                    rsu=float(int(rsu)),
                    verdict=f"BUNDLE ({int(rsu)}x)",
                    evidence=evidence,
                    rsu_confident=True,
                )
            return PackAnalysis(
                rsu=rsu,
                verdict="Pack uncertain (non-integer RSU)",
                evidence=evidence,
                rsu_confident=False,
            )

        # No unit: likely "(4 x 50)" => 4 packs of 50 => total 200 items.
        if sup_qty_inside and sup_qty_inside == inner:
            return PackAnalysis(
                rsu=float(outer),
                verdict=f"BUNDLE ({outer}x)",
                evidence=f"Amazon has '{outer} x {inner}' and Supplier shows '{sup_qty_inside} pcs' style quantity",
                rsu_confident=True,
            )

        if sup_qty_inside and sup_qty_inside > 0:
            total = outer * inner
            ratio = total / sup_qty_inside
            if abs(ratio - round(ratio)) < 1e-6 and 1 <= ratio <= 50:
                rsu_int = int(round(ratio))
                return PackAnalysis(
                    rsu=float(rsu_int),
                    verdict=f"BUNDLE ({rsu_int}x)",
                    evidence=f"Amazon total {total} from '{outer} x {inner}'; Supplier qty {sup_qty_inside}",
                    rsu_confident=True,
                )

        # Fallback: treat outer as pack count only.
        return PackAnalysis(
            rsu=float(outer),
            verdict=f"BUNDLE ({outer}x) (inner ambiguous)",
            evidence=f"Amazon has '{outer} x {inner}' (inner ambiguous; RSU=outer)",
            rsu_confident=False,
        )

    # Quantity-per-pack shield: if both show same qty-inside => 1:1.
    if sup_qty_inside and amz_qty_inside and sup_qty_inside == amz_qty_inside:
        return PackAnalysis(
            rsu=1.0,
            verdict="1:1 Match (qty-inside aligns)",
            evidence=f"Both titles show {sup_qty_inside} pcs-style quantity",
            rsu_confident=True,
        )

    # Pack words.
    if amz_pack > 1 or sup_pack > 1:
        ratio = amz_pack / max(1, sup_pack)
        if abs(ratio - round(ratio)) < 1e-6 and ratio >= 1:
            rsu_int = int(round(ratio))
            if rsu_int == 1:
                return PackAnalysis(rsu=1.0, verdict="1:1 Match", evidence="Pack counts align", rsu_confident=True)
            return PackAnalysis(
                rsu=float(rsu_int),
                verdict=f"BUNDLE ({rsu_int}x)",
                evidence=f"Pack count from words: Amazon {amz_pack} vs Supplier {sup_pack}",
                rsu_confident=True,
            )
        return PackAnalysis(rsu=1.0, verdict="Pack uncertain", evidence="Pack words present but ratio unclear", rsu_confident=False)

    return PackAnalysis(rsu=1.0, verdict="1:1 Match", evidence="-", rsu_confident=True)


def _capacity_to_base(value: float, unit: str) -> Optional[float]:
    unit = unit.lower()
    if unit == "ml":
        return value
    if unit in {"l", "ltr", "litre", "liter"}:
        return value * 1000.0
    if unit == "g":
        return value
    if unit == "kg":
        return value * 1000.0
    if unit == "oz":
        return value * 28.349523125
    return None


def _extract_capacity(title: str) -> Optional[tuple[float, str]]:
    if not title:
        return None
    s = title.lower()
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|liter|g|kg|oz)\b", s)
    if not m:
        return None
    try:
        value = float(m.group(1))
    except Exception:
        return None
    unit = m.group(2).lower()
    if value <= 0:
        return None
    return value, unit


def capacity_mismatch_bucket(supplier_title: str, amazon_title: str) -> Optional[tuple[float, str]]:
    cap_sup = _extract_capacity(supplier_title)
    cap_amz = _extract_capacity(amazon_title)
    if not cap_sup or not cap_amz:
        return None
    v1 = _capacity_to_base(cap_sup[0], cap_sup[1])
    v2 = _capacity_to_base(cap_amz[0], cap_amz[1])
    if v1 is None or v2 is None or v1 <= 0 or v2 <= 0:
        return None
    rel = abs(v1 - v2) / max(v1, v2)
    if rel <= 0.10:
        return rel, "0-10%"
    if rel <= 0.25:
        return rel, "10-25%"
    if rel <= 0.50:
        return rel, "25-50%"
    return rel, ">50%"


def adjusted_profit(net_profit: Optional[float], supplier_cost: Optional[float], rsu: float) -> Optional[float]:
    if net_profit is None or supplier_cost is None:
        return None
    return float(net_profit) - float(supplier_cost) * (float(rsu) - 1.0)


def _format_fixed_width_table(rows: list[dict[str, object]]) -> str:
    widths: dict[str, int] = {c: len(c) for c in TABLE_COLUMNS}
    for r in rows:
        for c in TABLE_COLUMNS:
            s = str(r.get(c, ""))
            widths[c] = max(widths[c], len(s))

    def fmt_row(vals: Iterable[str]) -> str:
        out = []
        for c, v in zip(TABLE_COLUMNS, vals, strict=True):
            out.append(v.ljust(widths[c]))
        return "| " + " | ".join(out) + " |"

    header = fmt_row(TABLE_COLUMNS)
    sep = "| " + " | ".join(("-" * widths[c]) for c in TABLE_COLUMNS) + " |"
    body = "\n".join(fmt_row([str(r.get(c, "")) for c in TABLE_COLUMNS]) for r in rows)
    return "\n".join([header, sep, body]).rstrip()


def _safe_title_with_rowid(rowid: int, title: str) -> str:
    title = (title or "").strip()
    return f"RowID:{rowid} - {title}" if title else f"RowID:{rowid} -"


def main() -> int:
    repo_root = Path.cwd()
    default_input = repo_root / "RESERACH" / "REPORT" / "PART_DEC_31" / "PART_DEC_31.xlsx"
    default_out_dir = repo_root / "RESERACH" / "REPORT" / "PART_DEC_31" / "CODEX 1"

    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=default_input)
    ap.add_argument("--output-dir", type=Path, default=default_out_dir)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--needs-verification-max", type=int, default=60)
    ap.add_argument("--filtered-out-max", type=int, default=50)
    args = ap.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(args.input, sheet_name=args.sheet)
    df = df.copy()
    df["RowID"] = df.index + 1

    # Sales proxy: sales_numeric > bought_in_past_month > 0.
    if "sales_numeric" in df.columns:
        df["Sales"] = df["sales_numeric"].apply(parse_int)
    elif "bought_in_past_month" in df.columns:
        df["Sales"] = df["bought_in_past_month"].apply(parse_int)
    else:
        df["Sales"] = 0

    # Strict EAN: digits-only + GTIN length + checksum, with left-padding attempt.
    df["EAN_digits"] = df["EAN"].apply(_clean_to_digits) if "EAN" in df.columns else ""
    df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(_clean_to_digits) if "EAN_OnPage" in df.columns else ""
    df["EAN_digits_norm"] = df["EAN_digits"].apply(normalize_ean)
    df["EAN_OnPage_digits_norm"] = df["EAN_OnPage_digits"].apply(normalize_ean)
    df["EAN_strict_valid"] = df["EAN_digits_norm"].apply(is_strict_valid_barcode)
    df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_digits_norm"].apply(is_strict_valid_barcode)
    df["is_exact_ean_strict"] = (
        df["EAN_strict_valid"]
        & df["EAN_OnPage_strict_valid"]
        & (df["EAN_digits_norm"] == df["EAN_OnPage_digits_norm"])
    )

    # Numeric fields used in gating.
    df["SupplierPrice_f"] = (
        df["SupplierPrice_incVAT"].apply(parse_float) if "SupplierPrice_incVAT" in df.columns else None
    )
    df["SellingPrice_f"] = df["SellingPrice_incVAT"].apply(parse_float) if "SellingPrice_incVAT" in df.columns else None
    df["NetProfit_f"] = df["NetProfit"].apply(parse_float) if "NetProfit" in df.columns else None
    df["ROI_f"] = df["ROI"].apply(parse_float) if "ROI" in df.columns else None

    # Title similarity baseline.
    df["title_match"] = df.apply(
        lambda r: title_similarity(str(r.get("SupplierTitle", "") or ""), str(r.get("AmazonTitle", "") or "")),
        axis=1,
    )

    # Pack adjustment baseline.
    pack_results: list[PackAnalysis] = []
    for _, r in df.iterrows():
        pack_results.append(analyze_pack(str(r.get("SupplierTitle", "") or ""), str(r.get("AmazonTitle", "") or "")))
    df["RSU"] = [p.rsu for p in pack_results]
    df["PackVerdict"] = [p.verdict for p in pack_results]
    df["PackEvidence"] = [p.evidence for p in pack_results]
    df["RSU_confident"] = [p.rsu_confident for p in pack_results]
    df["AdjustedProfit_f"] = df.apply(
        lambda r: adjusted_profit(r.get("NetProfit_f"), r.get("SupplierPrice_f"), float(r.get("RSU", 1.0) or 1.0)),
        axis=1,
    )

    # Capacity mismatch buckets (used for strong exclusions only).
    df["capacity_bucket"] = df.apply(
        lambda r: capacity_mismatch_bucket(str(r.get("SupplierTitle", "") or ""), str(r.get("AmazonTitle", "") or "")),
        axis=1,
    )

    verified_rec: list[dict[str, object]] = []
    verified_fo: list[dict[str, object]] = []
    hl_rec: list[dict[str, object]] = []
    hl_fo: list[dict[str, object]] = []
    needs_verification: list[dict[str, object]] = []
    filtered_out: list[dict[str, object]] = []

    for _, r in df.iterrows():
        rowid = int(r["RowID"])
        sup_title = str(r.get("SupplierTitle", "") or "")
        amz_title = str(r.get("AmazonTitle", "") or "")
        asin = str(r.get("ASIN", "") or "").strip()

        sales = int(r.get("Sales", 0) or 0)
        supplier_price = r.get("SupplierPrice_f")
        selling_price = r.get("SellingPrice_f")
        net_profit = r.get("NetProfit_f")
        roi = r.get("ROI_f")
        adj_profit = r.get("AdjustedProfit_f")

        rsu = float(r.get("RSU", 1.0) or 1.0)
        rsu_confident = bool(r.get("RSU_confident"))
        title_match = float(r.get("title_match", 0.0) or 0.0)
        is_exact = bool(r.get("is_exact_ean_strict"))

        pack_verdict = str(r.get("PackVerdict", "") or "-")
        pack_evidence = str(r.get("PackEvidence", "") or "-")

        brand_ok, brand_hint = _brand_match(sup_title, amz_title)
        shared_count = len(_shared_tokens(sup_title, amz_title))

        sup_ean_norm = r.get("EAN_digits_norm") if r.get("EAN_strict_valid") else ""
        amz_ean_norm = r.get("EAN_OnPage_digits_norm") if r.get("EAN_OnPage_strict_valid") else ""
        sup_ean_out = sup_ean_norm if sup_ean_norm else "-"
        amz_ean_out = amz_ean_norm if amz_ean_norm else "-"

        key_evidence = _key_match_evidence(sup_title, amz_title, exact_ean=is_exact, brand_hint=brand_hint)

        # Confidence (A9) + IP risk soft-flagging (A15).
        if is_exact:
            confidence = 95
        else:
            confidence = int(round(40 + 40 * min(1.0, title_match) + 5 * min(6, shared_count)))
            if brand_ok:
                confidence = min(95, confidence + 10)
            if _contains_ip_risk_brand(sup_title) or _contains_ip_risk_brand(amz_title):
                confidence = min(confidence, 70)

        adj_profit_val = float(adj_profit) if adj_profit is not None else -9999.0
        net_profit_val = float(net_profit) if net_profit is not None else -9999.0

        # Capacity tolerance: for non-EAN, >50% or 25-50% is different SKU => FILTERED OUT.
        cap_bucket = r.get("capacity_bucket")
        cap_reason = None
        if cap_bucket:
            rel, bucket = cap_bucket
            if bucket in {"10-25%", "25-50%", ">50%"}:
                cap_reason = f"Capacity mismatch {bucket} (rel={rel:.2f})"

        if cap_reason and not is_exact and ("25-50%" in cap_reason or ">50%" in cap_reason):
            if len(filtered_out) < args.filtered_out_max:
                filtered_out.append(
                    {
                        "Verdict": "FILTERED OUT",
                        "Confidence": confidence,
                        "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                        "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                        "Supplier EAN": sup_ean_out,
                        "Amazon EAN": amz_ean_out,
                        "ASIN": asin,
                        "SupplierPrice": _as_money(supplier_price),
                        "SellingPrice": _as_money(selling_price),
                        "NetProfit": _as_money(net_profit),
                        "ROI": f"{roi:.1f}" if roi is not None else "-",
                        "Sales": sales,
                        "Pack Verdict": pack_verdict,
                        "Adjusted Profit": _as_money(adj_profit),
                        "Key Match Evidence": key_evidence,
                        "Filter Reason": cap_reason,
                    }
                )
            continue

        # Category mismatch trap guard (sample output only; avoids huge report).
        obvious_mismatch = (
            not is_exact
            and title_match < 0.18
            and shared_count < 2
            and (selling_price or 0) >= 80
            and (supplier_price or 0) <= 10
        )
        if obvious_mismatch:
            if len(filtered_out) < args.filtered_out_max:
                filtered_out.append(
                    {
                        "Verdict": "FILTERED OUT",
                        "Confidence": 5,
                        "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                        "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                        "Supplier EAN": sup_ean_out,
                        "Amazon EAN": amz_ean_out,
                        "ASIN": asin,
                        "SupplierPrice": _as_money(supplier_price),
                        "SellingPrice": _as_money(selling_price),
                        "NetProfit": _as_money(net_profit),
                        "ROI": f"{roi:.1f}" if roi is not None else "-",
                        "Sales": sales,
                        "Pack Verdict": pack_verdict,
                        "Adjusted Profit": _as_money(adj_profit),
                        "Key Match Evidence": key_evidence,
                        "Filter Reason": "Category/title mismatch trap (low overlap; implausible pairing)",
                    }
                )
            continue

        # VERIFIED (Exact EAN).
        if is_exact:
            # Capacity tolerance for Exact EAN: only exclude if mismatch is big (>=25%).
            if cap_reason and ("25-50%" in cap_reason or ">50%" in cap_reason):
                verified_fo.append(
                    {
                        "Verdict": "VERIFIED (Exact EAN) - FILTERED OUT",
                        "Confidence": confidence,
                        "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                        "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                        "Supplier EAN": sup_ean_out,
                        "Amazon EAN": amz_ean_out,
                        "ASIN": asin,
                        "SupplierPrice": _as_money(supplier_price),
                        "SellingPrice": _as_money(selling_price),
                        "NetProfit": _as_money(net_profit),
                        "ROI": f"{roi:.1f}" if roi is not None else "-",
                        "Sales": sales,
                        "Pack Verdict": pack_verdict,
                        "Adjusted Profit": _as_money(adj_profit),
                        "Key Match Evidence": key_evidence,
                        "Filter Reason": cap_reason,
                    }
                )
                continue

            # Explicit pack mismatch that flips profit negative => FILTERED OUT.
            if rsu_confident and rsu > 1 and adj_profit_val <= 0:
                verified_fo.append(
                    {
                        "Verdict": "VERIFIED (Exact EAN) - FILTERED OUT",
                        "Confidence": confidence,
                        "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                        "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                        "Supplier EAN": sup_ean_out,
                        "Amazon EAN": amz_ean_out,
                        "ASIN": asin,
                        "SupplierPrice": _as_money(supplier_price),
                        "SellingPrice": _as_money(selling_price),
                        "NetProfit": _as_money(net_profit),
                        "ROI": f"{roi:.1f}" if roi is not None else "-",
                        "Sales": sales,
                        "Pack Verdict": f"{pack_verdict} ({pack_evidence})",
                        "Adjusted Profit": _as_money(adj_profit),
                        "Key Match Evidence": key_evidence,
                        "Filter Reason": "Pack mismatch makes adjusted profit ≤ 0",
                    }
                )
                continue

            # Recommendation gating (A3/A4).
            if sales > 0 and net_profit_val > 0 and adj_profit_val > 0:
                verified_rec.append(
                    {
                        "Verdict": "VERIFIED (Exact EAN) - RECOMMENDED",
                        "Confidence": confidence,
                        "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                        "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                        "Supplier EAN": sup_ean_out,
                        "Amazon EAN": amz_ean_out,
                        "ASIN": asin,
                        "SupplierPrice": _as_money(supplier_price),
                        "SellingPrice": _as_money(selling_price),
                        "NetProfit": _as_money(net_profit),
                        "ROI": f"{roi:.1f}" if roi is not None else "-",
                        "Sales": sales,
                        "Pack Verdict": pack_verdict,
                        "Adjusted Profit": _as_money(adj_profit),
                        "Key Match Evidence": key_evidence,
                        "Filter Reason": "-",
                    }
                )
            else:
                if net_profit_val > 0 and adj_profit_val > 0 and len(needs_verification) < args.needs_verification_max:
                    needs_verification.append(
                        {
                            "Verdict": "NEEDS VERIFICATION",
                            "Confidence": confidence,
                            "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                            "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                            "Supplier EAN": sup_ean_out,
                            "Amazon EAN": amz_ean_out,
                            "ASIN": asin,
                            "SupplierPrice": _as_money(supplier_price),
                            "SellingPrice": _as_money(selling_price),
                            "NetProfit": _as_money(net_profit),
                            "ROI": f"{roi:.1f}" if roi is not None else "-",
                            "Sales": sales,
                            "Pack Verdict": pack_verdict,
                            "Adjusted Profit": _as_money(adj_profit),
                            "Key Match Evidence": key_evidence,
                            "Filter Reason": "Sales=0; verify demand and confirm no pack-word contradiction",
                        }
                    )
            continue

        # Non-EAN path: HIGHLY LIKELY / NEEDS VERIFICATION / FILTERED OUT.
        plausible = title_match >= 0.35 and shared_count >= 2
        strong = title_match >= 0.48 and shared_count >= 3
        roi_val = float(roi) if roi is not None else 0.0

        if brand_ok and strong and net_profit_val > 0 and adj_profit_val > 0 and rsu_confident:
            if sales > 0:
                hl_rec.append(
                    {
                        "Verdict": "HIGHLY LIKELY - RECOMMENDED",
                        "Confidence": min(90, max(80, confidence)),
                        "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                        "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                        "Supplier EAN": sup_ean_out,
                        "Amazon EAN": amz_ean_out,
                        "ASIN": asin,
                        "SupplierPrice": _as_money(supplier_price),
                        "SellingPrice": _as_money(selling_price),
                        "NetProfit": _as_money(net_profit),
                        "ROI": f"{roi_val:.1f}" if roi is not None else "-",
                        "Sales": sales,
                        "Pack Verdict": f"{pack_verdict} ({pack_evidence})" if "BUNDLE" in pack_verdict else pack_verdict,
                        "Adjusted Profit": _as_money(adj_profit),
                        "Key Match Evidence": key_evidence,
                        "Filter Reason": "-",
                    }
                )
            else:
                if len(needs_verification) < args.needs_verification_max:
                    needs_verification.append(
                        {
                            "Verdict": "NEEDS VERIFICATION",
                            "Confidence": min(85, max(70, confidence)),
                            "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                            "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                            "Supplier EAN": sup_ean_out,
                            "Amazon EAN": amz_ean_out,
                            "ASIN": asin,
                            "SupplierPrice": _as_money(supplier_price),
                            "SellingPrice": _as_money(selling_price),
                            "NetProfit": _as_money(net_profit),
                            "ROI": f"{roi_val:.1f}" if roi is not None else "-",
                            "Sales": sales,
                            "Pack Verdict": f"{pack_verdict} ({pack_evidence})" if "BUNDLE" in pack_verdict else pack_verdict,
                            "Adjusted Profit": _as_money(adj_profit),
                            "Key Match Evidence": key_evidence,
                            "Filter Reason": "Sales=0; verify demand + confirm pack evidence",
                        }
                    )
            continue

        # Pack mismatch makes adjusted profit negative (but match is otherwise plausible) => HIGHLY LIKELY - FILTERED OUT.
        if rsu_confident and rsu > 1 and adj_profit_val <= 0 and brand_ok and plausible:
            hl_fo.append(
                {
                    "Verdict": "HIGHLY LIKELY - FILTERED OUT",
                    "Confidence": min(85, max(70, confidence)),
                    "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                    "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                    "Supplier EAN": sup_ean_out,
                    "Amazon EAN": amz_ean_out,
                    "ASIN": asin,
                    "SupplierPrice": _as_money(supplier_price),
                    "SellingPrice": _as_money(selling_price),
                    "NetProfit": _as_money(net_profit),
                    "ROI": f"{roi_val:.1f}" if roi is not None else "-",
                    "Sales": sales,
                    "Pack Verdict": f"{pack_verdict} ({pack_evidence})",
                    "Adjusted Profit": _as_money(adj_profit),
                    "Key Match Evidence": key_evidence,
                    "Filter Reason": "Pack mismatch makes adjusted profit ≤ 0",
                }
            )
            continue

        # NEEDS VERIFICATION (selective).
        if plausible and net_profit_val > 0.5 and roi_val > 15 and len(needs_verification) < args.needs_verification_max:
            if cap_reason and "10-25%" in cap_reason:
                filter_reason = f"{cap_reason}; verify size/variant"
            elif not rsu_confident and _RE_PACK_WORDS.search(amz_title):
                filter_reason = "Pack words present; verify exact pack count then re-check profit"
            elif brand_ok:
                filter_reason = "Verify 1 detail: exact variant/pack count (titles mostly align)"
            else:
                filter_reason = "Verify 1 detail: brand on listing/packaging (brand not clearly anchored)"

            needs_verification.append(
                {
                    "Verdict": "NEEDS VERIFICATION",
                    "Confidence": min(79, max(55, confidence)),
                    "SupplierTitle": _safe_title_with_rowid(rowid, sup_title),
                    "AmazonTitle": _safe_title_with_rowid(rowid, amz_title),
                    "Supplier EAN": sup_ean_out,
                    "Amazon EAN": amz_ean_out,
                    "ASIN": asin,
                    "SupplierPrice": _as_money(supplier_price),
                    "SellingPrice": _as_money(selling_price),
                    "NetProfit": _as_money(net_profit),
                    "ROI": f"{roi_val:.1f}" if roi is not None else "-",
                    "Sales": sales,
                    "Pack Verdict": f"{pack_verdict} ({pack_evidence})" if pack_evidence != "-" else pack_verdict,
                    "Adjusted Profit": _as_money(adj_profit),
                    "Key Match Evidence": key_evidence,
                    "Filter Reason": filter_reason,
                }
            )

    # Ordering per spec.
    verified_rec.sort(key=lambda x: (int(x["Sales"]), float(x["Adjusted Profit"])), reverse=True)
    verified_fo.sort(key=lambda x: (int(x["Sales"]), float(x["Adjusted Profit"])), reverse=True)
    hl_rec.sort(key=lambda x: (int(x["Confidence"]), int(x["Sales"])), reverse=True)
    hl_fo.sort(key=lambda x: (int(x["Confidence"]), int(x["Sales"])), reverse=True)
    needs_verification.sort(key=lambda x: (int(x["Confidence"]), int(x["Sales"])), reverse=True)

    needs_verification = needs_verification[: args.needs_verification_max]
    filtered_out = filtered_out[: args.filtered_out_max]

    now = datetime.now(ZoneInfo("Asia/Dubai"))
    out_md = args.output_dir / f"PHASEA_MANUAL_REPORT_{now:%Y%m%d}.md"

    summary_lines = [
        f"- Source file: `{args.input}`",
        f"- Generated: {now:%Y-%m-%d} (Asia/Dubai)",
        f"- Total rows in sheet: {len(df)}",
        f"- VERIFIED — RECOMMENDED: {len(verified_rec)}",
        f"- VERIFIED — FILTERED OUT: {len(verified_fo)}",
        f"- HIGHLY LIKELY — RECOMMENDED: {len(hl_rec)}",
        f"- HIGHLY LIKELY — FILTERED OUT: {len(hl_fo)}",
        f"- NEEDS VERIFICATION: {len(needs_verification)}",
        f"- FILTERED OUT (sample): {len(filtered_out)}",
    ]

    def section(title: str, rows: list[dict[str, object]]) -> str:
        if not rows:
            return f"## {title}\n\n_No rows_\n"
        return f"## {title}\n\n```text\n{_format_fixed_width_table(rows)}\n```\n"

    md_parts: list[str] = []
    md_parts.append("# PHASEA Manual Report\n")
    md_parts.append("## Summary Counts\n")
    md_parts.extend([*summary_lines, ""])
    md_parts.append(
        "This report enforces strict EAN validity (checksum + left-padding) and blocks dimension traps (e.g., '9 x 9 inch' ≠ 81 units).\n"
        "VERIFIED and HIGHLY LIKELY recommendations require Sales>0, NetProfit>0, and Adjusted Profit>0.\n"
        "Rows with Sales=0 but strong match signals are routed to NEEDS VERIFICATION instead of being recommended.\n"
        "FILTERED OUT is intentionally capped to a sample to keep the report readable; the underlying sheet contains many obvious mismatch traps.\n"
    )
    md_parts.append(section(f"VERIFIED — RECOMMENDED (count={len(verified_rec)})", verified_rec))
    md_parts.append(section(f"VERIFIED — FILTERED OUT (count={len(verified_fo)})", verified_fo))
    md_parts.append(section(f"HIGHLY LIKELY — RECOMMENDED (count={len(hl_rec)})", hl_rec))
    md_parts.append(section(f"HIGHLY LIKELY — FILTERED OUT (count={len(hl_fo)})", hl_fo))
    md_parts.append(section(f"NEEDS VERIFICATION (count={len(needs_verification)})", needs_verification))
    md_parts.append(section(f"FILTERED OUT (count={len(filtered_out)})", filtered_out))
    md_parts.append("## Reconciliation\n")
    md_parts.append(
        f"- VERIFIED — RECOMMENDED: {len(verified_rec)}\n"
        f"- VERIFIED — FILTERED OUT: {len(verified_fo)}\n"
        f"- HIGHLY LIKELY — RECOMMENDED: {len(hl_rec)}\n"
        f"- HIGHLY LIKELY — FILTERED OUT: {len(hl_fo)}\n"
        f"- NEEDS VERIFICATION: {len(needs_verification)}\n"
        f"- FILTERED OUT: {len(filtered_out)}\n"
    )

    out_md.write_text("\n".join(md_parts).rstrip() + "\n", encoding="utf-8")
    print(out_md)
    print("\n".join(summary_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
