from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import pandas as pd
from difflib import SequenceMatcher


ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)
INPUT_XLSX = ROOT / r"RESERACH\REPORT\part_30_dec\part_30_dec.xlsx"
OUTPUT_DIR = ROOT / r"RESERACH\REPORT\part_30_dec\Codex 2"

# Time zone pinned by user: Asia/Dubai (UTC+4)
TODAY_DUBAI = "2025-12-30"
PROMPT_VERSION = "4.0"

# Keep source ASCII-only; emit symbols via escapes.
POUND = "\u00a3"


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
    "a",
    "an",
    "and",
    "or",
    "with",
    "for",
    "to",
    "of",
    "in",
    "on",
    "at",
    "by",
    "from",
    "new",
    "genuine",
    "original",
    "replacement",
    "pack",
    "pk",
    "pcs",
    "pieces",
    "piece",
    "set",
    "kit",
    "bundle",
    "x",
}

COLOR_TOKENS = {
    "black",
    "white",
    "red",
    "blue",
    "green",
    "yellow",
    "pink",
    "purple",
    "orange",
    "grey",
    "gray",
    "navy",
    "silver",
    "gold",
    "brown",
    "clear",
    "transparent",
}

IP_RISK_BRANDS = {
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


def _as_str(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x)


def clean_to_digits(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if abs(value - round(value)) > 1e-6:
            return ""
        return str(int(round(value)))
    if isinstance(value, int):
        return str(value)

    s = _as_str(value).strip()
    if not s or s.lower() in {"nan", "none", "null", "-"}:
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
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
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


def title_similarity(a: Any, b: Any) -> float:
    sa = _as_str(a).strip()
    sb = _as_str(b).strip()
    if not sa or not sb:
        return 0.0
    return SequenceMatcher(None, sa.lower(), sb.lower()).ratio()


def tokenize_title(title: Any) -> list[str]:
    s = _as_str(title).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return [t for t in s.split() if len(t) >= 2 and t not in STOPWORDS]


def shared_anchors(supplier_title: Any, amazon_title: Any, limit: int = 8) -> list[str]:
    s_tokens = tokenize_title(supplier_title)
    a_set = set(tokenize_title(amazon_title))
    shared: list[str] = []
    for t in s_tokens:
        if t in a_set and t not in shared:
            if t.isdigit() and len(t) < 3:
                continue
            shared.append(t)
        if len(shared) >= limit:
            break
    return shared


def first_meaningful_word(title: Any) -> str:
    for t in tokenize_title(title):
        if t.isalpha() and len(t) >= 3:
            return t
    return ""


def second_meaningful_word(title: Any) -> str:
    words = [t for t in tokenize_title(title) if t.isalpha() and len(t) >= 3]
    return words[1] if len(words) >= 2 else ""


def parse_sales(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return 0
        return max(0, int(value))
    s = _as_str(value).strip().lower()
    if not s or s in {"nan", "none", "null", "-"}:
        return 0
    m = re.search(r"(\d+)", s)
    return int(m.group(1)) if m else 0


MEASUREMENT_UNITS_RE = re.compile(r"\b(cm|mm|m|inches|inch|in|ft|feet|ml|l|g|kg|oz)\b", re.I)
DIMENSION_RE = re.compile(
    r"\b\d+(\.\d+)?\s*x\s*\d+(\.\d+)?(\s*x\s*\d+(\.\d+)?)?\s*(cm|mm|m|inches|inch|in|ft|feet)\b",
    re.I,
)


@dataclass(frozen=True)
class PackParse:
    qty: int | None
    evidence: str
    has_dimensions: bool


def extract_explicit_pack_qty(title: Any) -> PackParse:
    s = _as_str(title).lower()
    if not s:
        return PackParse(qty=None, evidence="", has_dimensions=False)

    has_dimensions = bool(DIMENSION_RE.search(s))

    patterns: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"\bpack of\s*(\d+)\b"), "pack of N"),
        (re.compile(r"\bset of\s*(\d+)\b"), "set of N"),
        (re.compile(r"\b(\d+)\s*(pack|pk)\b"), "N pack"),
        (re.compile(r"\b(\d+)\s*(pcs|pieces?)\b"), "N pcs"),
        (re.compile(r"\b(\d+)\s*(cases?)\b"), "N cases"),
        (re.compile(r"\b(\d+)\s*(bags?)\b"), "N bags"),
        (re.compile(r"\b(\d+)\s*(rolls?)\b"), "N rolls"),
        (re.compile(r"\b(\d+)\s*(wipes?)\b"), "N wipes"),
        (re.compile(r"\b(\d+)\s*(tablets?)\b"), "N tablets"),
        (re.compile(r"\b(\d+)\s*(capsules?)\b"), "N capsules"),
        (re.compile(r"\b(\d+)\s*(batteries)\b"), "N batteries"),
        (re.compile(r"\b(\d+)\s*(bulbs?)\b"), "N bulbs"),
        (re.compile(r"\b(\d+)\s*(pairs?)\b"), "N pairs"),
    ]

    for pat, label in patterns:
        m = pat.search(s)
        if not m:
            continue
        qty = int(m.group(1))
        if 1 < qty < 500:
            return PackParse(qty=qty, evidence=label, has_dimensions=has_dimensions)

    # "3 x 15 pack" => 45 (only when explicit pack keyword follows)
    m2 = re.search(r"\b(\d+)\s*x\s*(\d+)\s*(pack|pk|pcs|pieces?)\b", s)
    if m2:
        a, b = int(m2.group(1)), int(m2.group(2))
        qty = a * b
        if 1 < qty < 500:
            return PackParse(qty=qty, evidence="A x B pack", has_dimensions=has_dimensions)

    # "3 x <product>" at start (treat as pack ONLY if next token isn't a measurement unit)
    m3 = re.match(r"^\s*(\d+)\s*x\s*([a-z0-9]+)", s)
    if m3:
        a = int(m3.group(1))
        next_tok = m3.group(2)
        if 1 < a < 500 and not MEASUREMENT_UNITS_RE.match(next_tok) and not has_dimensions:
            return PackParse(qty=a, evidence="A x (prefix)", has_dimensions=has_dimensions)

    return PackParse(qty=None, evidence="", has_dimensions=has_dimensions)


def extract_capacity_ml(title: Any) -> float | None:
    s = _as_str(title).lower()
    if not s:
        return None
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*ml\b", s)
    if m:
        return float(m.group(1))
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*l\b", s)
    if m:
        return float(m.group(1)) * 1000.0
    return None


def capacity_relation(supplier_title: Any, amazon_title: Any) -> tuple[str, str]:
    sup_ml = extract_capacity_ml(supplier_title)
    amz_ml = extract_capacity_ml(amazon_title)
    if sup_ml is None or amz_ml is None or sup_ml <= 0 or amz_ml <= 0:
        return ("-", "-")
    ratio = max(sup_ml, amz_ml) / min(sup_ml, amz_ml)
    pct = (ratio - 1.0) * 100.0
    note = f"{int(round(sup_ml))}ml vs {int(round(amz_ml))}ml (~{pct:.0f}% diff)"
    if pct <= 30.0:
        return ("tolerable_or_minor", note)
    return ("mismatch", note)


def detect_color_mismatch(supplier_title: Any, amazon_title: Any) -> tuple[bool, str]:
    s_tokens = set(tokenize_title(supplier_title))
    a_tokens = set(tokenize_title(amazon_title))
    s_colors = sorted(s_tokens.intersection(COLOR_TOKENS))
    a_colors = sorted(a_tokens.intersection(COLOR_TOKENS))
    if not s_colors or not a_colors:
        return (False, "-")
    if s_colors == a_colors:
        return (False, "-")
    return (True, f"Color differs: supplier={','.join(s_colors)} vs amazon={','.join(a_colors)}")


def fmt_gbp(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "-"
    return f"{POUND}{v:.2f}"


def fmt_pct(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "-"
    return f"{v:.1f}%"

def sanitize_cell(value: Any) -> str:
    s = _as_str(value)
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = s.replace("|", " / ")
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def build_fixed_width_table(rows: list[dict[str, str]]) -> str:
    widths: dict[str, int] = {c: len(c) for c in TABLE_COLUMNS}
    for r in rows:
        for col in TABLE_COLUMNS:
            widths[col] = max(widths[col], len(r.get(col, "")))

    def fmt_row(values: Iterable[str]) -> str:
        parts = [f" {v:<{widths[col]}} " for col, v in zip(TABLE_COLUMNS, values, strict=True)]
        return "|" + "|".join(parts) + "|"

    header = fmt_row(TABLE_COLUMNS)
    sep = "|" + "|".join(["-" * (widths[c] + 2) for c in TABLE_COLUMNS]) + "|"
    body = "\n".join(fmt_row([r.get(c, "") for c in TABLE_COLUMNS]) for r in rows)
    return "\n".join([header, sep, body]) if body else "\n".join([header, sep])


def infer_supplier_from_urls(urls: pd.Series) -> str:
    domains: dict[str, int] = {}
    for u in urls.dropna().astype(str).tolist():
        try:
            netloc = urlparse(u).netloc.lower().replace("www.", "")
        except Exception:
            continue
        if not netloc:
            continue
        domains[netloc] = domains.get(netloc, 0) + 1
    return max(domains.items(), key=lambda kv: kv[1])[0] if domains else "poundwholesale.co.uk"


def confidence_score(
    *,
    is_exact_ean: bool,
    title_match: float,
    brand_match: bool,
    product_type_match: bool,
    shared_count: int,
    has_assorted: bool,
    has_conflict: bool,
) -> int:
    if is_exact_ean:
        base = 95
        if has_conflict:
            base -= 10
        if has_assorted:
            base -= 5
        return max(0, min(100, base))

    base = int(round(title_match * 100))
    if brand_match:
        base += 12
    if product_type_match:
        base += 10
    base += min(12, shared_count * 4)
    if has_assorted:
        base -= 12
    if has_conflict:
        base -= 10
    return max(0, min(94, base))


def make_row_dict(
    *,
    verdict: str,
    confidence: int,
    supplier_title: str,
    amazon_title: str,
    supplier_ean_disp: str,
    amazon_ean_disp: str,
    asin: str,
    supplier_price: Any,
    selling_price: Any,
    net_profit: Any,
    roi: Any,
    sales: int,
    pack_verdict: str,
    adjusted_profit: float,
    evidence: str,
    filter_reason: str,
) -> dict[str, str]:
    return {
        "Verdict": verdict,
        "Confidence": str(confidence),
        "SupplierTitle": sanitize_cell(supplier_title),
        "AmazonTitle": sanitize_cell(amazon_title),
        "Supplier EAN": supplier_ean_disp,
        "Amazon EAN": amazon_ean_disp,
        "ASIN": asin or "-",
        "SupplierPrice": fmt_gbp(supplier_price),
        "SellingPrice": fmt_gbp(selling_price),
        "NetProfit": fmt_gbp(net_profit),
        "ROI": fmt_pct(roi),
        "Sales": str(int(sales)),
        "Pack Verdict": sanitize_cell(pack_verdict),
        "Adjusted Profit": fmt_gbp(adjusted_profit),
        "Key Match Evidence": sanitize_cell(evidence),
        "Filter Reason": sanitize_cell(filter_reason),
    }


def _money_to_float(s: str) -> float:
    try:
        cleaned = re.sub(r"^[^0-9\\-\\.]+", "", s.strip())
        return float(cleaned)
    except Exception:
        return 0.0


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(INPUT_XLSX, sheet_name=0, engine="openpyxl").copy()
    df["RowID"] = df.index + 1

    supplier_domain = infer_supplier_from_urls(df.get("SupplierURL", pd.Series(dtype=str)))

    df["sales"] = df.get("bought_in_past_month", 0).apply(parse_sales)
    df["title_match"] = df.apply(lambda r: title_similarity(r.get("SupplierTitle"), r.get("AmazonTitle")), axis=1)

    df["EAN_digits"] = df.get("EAN", "").apply(clean_to_digits)
    df["EAN_OnPage_digits"] = df.get("EAN_OnPage", "").apply(clean_to_digits)
    df["EAN_digits_normalized"] = df["EAN_digits"].apply(normalize_ean)
    df["EAN_OnPage_digits_normalized"] = df["EAN_OnPage_digits"].apply(normalize_ean)
    df["EAN_strict_valid"] = df["EAN_digits_normalized"].apply(is_strict_valid_barcode)
    df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_digits_normalized"].apply(is_strict_valid_barcode)
    df["is_exact_ean_strict"] = (
        df["EAN_strict_valid"]
        & df["EAN_OnPage_strict_valid"]
        & (df["EAN_digits_normalized"] == df["EAN_OnPage_digits_normalized"])
    )

    rows_verified_rec: list[dict[str, str]] = []
    rows_verified_filtered: list[dict[str, str]] = []
    rows_hl_rec: list[dict[str, str]] = []
    rows_hl_filtered: list[dict[str, str]] = []
    rows_needs_ver: list[dict[str, str]] = []

    for _, r in df.iterrows():
        rowid = int(r.get("RowID", 0) or 0)
        supplier_title = _as_str(r.get("SupplierTitle")).strip()
        amazon_title = _as_str(r.get("AmazonTitle")).strip()
        if not supplier_title or not amazon_title:
            continue

        asin = _as_str(r.get("ASIN")).strip()
        sales = int(r.get("sales", 0) or 0)
        net_profit = float(r.get("NetProfit", 0) or 0)
        roi = r.get("ROI", 0)
        supplier_price = float(r.get("SupplierPrice_incVAT", 0) or 0)
        selling_price = r.get("SellingPrice_incVAT", 0)

        sup_digits = r.get("EAN_digits_normalized", "")
        amz_digits = r.get("EAN_OnPage_digits_normalized", "")
        sup_ok = bool(r.get("EAN_strict_valid"))
        amz_ok = bool(r.get("EAN_OnPage_strict_valid"))
        supplier_ean_disp = sup_digits if sup_ok else "-"
        amazon_ean_disp = amz_digits if amz_ok else "-"

        exact_ean = bool(r.get("is_exact_ean_strict"))

        sup_pack = extract_explicit_pack_qty(supplier_title)
        amz_pack = extract_explicit_pack_qty(amazon_title)

        explicit_pack_mismatch = False
        required_units = 1
        pack_verdict = "1:1 Match"

        if sup_pack.qty is not None or amz_pack.qty is not None:
            if sup_pack.qty is None and amz_pack.qty is not None:
                explicit_pack_mismatch = True
                required_units = amz_pack.qty
                pack_verdict = f"Amazon {amz_pack.qty}-pack; supplier pack unclear"
            elif sup_pack.qty is not None and amz_pack.qty is None:
                explicit_pack_mismatch = True
                pack_verdict = f"Supplier {sup_pack.qty}-pack; Amazon pack unclear"
            else:
                assert sup_pack.qty is not None and amz_pack.qty is not None
                if sup_pack.qty == amz_pack.qty:
                    pack_verdict = f"1:1 Match ({sup_pack.qty}-pack)"
                else:
                    explicit_pack_mismatch = True
                    if amz_pack.qty > sup_pack.qty:
                        required_units = int(math.ceil(amz_pack.qty / sup_pack.qty))
                        pack_verdict = (
                            f"Amazon {amz_pack.qty}-pack vs supplier {sup_pack.qty}-pack; RSU={required_units}"
                        )
                    else:
                        pack_verdict = (
                            f"Supplier {sup_pack.qty}-pack vs Amazon {amz_pack.qty}-pack; verify split/units"
                        )

        adjusted_profit = net_profit
        if required_units > 1:
            adjusted_profit = net_profit - supplier_price * (required_units - 1)

        profit_after_pack = adjusted_profit

        cap_status, cap_note = capacity_relation(supplier_title, amazon_title)
        color_mismatch, color_note = detect_color_mismatch(supplier_title, amazon_title)

        assorted = ("assorted" in supplier_title.lower()) or ("assorted" in amazon_title.lower())

        anchors = shared_anchors(supplier_title, amazon_title)
        base_evidence = "Exact EAN match" if exact_ean else ("Shared: " + ", ".join(anchors[:6]) if anchors else "-")
        evidence = f"RowID={rowid}; {base_evidence}" if rowid else base_evidence

        sup_brand = first_meaningful_word(supplier_title)
        sup_type = second_meaningful_word(supplier_title)
        a_tokens = set(tokenize_title(amazon_title))
        brand_match = bool(sup_brand) and (sup_brand in a_tokens)
        product_type_match = bool(sup_type) and (sup_type in a_tokens)

        has_conflict = cap_status == "mismatch"
        conf = confidence_score(
            is_exact_ean=exact_ean,
            title_match=float(r.get("title_match", 0) or 0),
            brand_match=brand_match,
            product_type_match=product_type_match,
            shared_count=len(anchors),
            has_assorted=assorted,
            has_conflict=has_conflict,
        )

        is_highly_likely_match = (
            (not exact_ean)
            and brand_match
            and product_type_match
            and float(r.get("title_match", 0) or 0) >= 0.55
            and len(anchors) >= 3
            and not assorted
        )

        sellable = sales > 0
        profitable = net_profit > 0 and profit_after_pack > 0

        supplier_multipack_vs_amz_smaller = (
            sup_pack.qty is not None and amz_pack.qty is not None and sup_pack.qty > amz_pack.qty
        )
        recommendable_pack = (not explicit_pack_mismatch) or (required_units > 1 and not supplier_multipack_vs_amz_smaller)

        if exact_ean:
            if cap_status == "mismatch":
                pack_verdict = f"{pack_verdict}; note: {cap_note}"
            if color_mismatch:
                pack_verdict = f"{pack_verdict}; note: {color_note}"

            if profitable and sellable and recommendable_pack:
                rows_verified_rec.append(
                    make_row_dict(
                        verdict="VERIFIED",
                        confidence=conf,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=profit_after_pack,
                        evidence=evidence,
                        filter_reason="-",
                    )
                )
                continue

            if not sellable and profitable:
                rows_needs_ver.append(
                    make_row_dict(
                        verdict="NEEDS VERIFICATION",
                        confidence=max(85, min(94, conf)),
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=profit_after_pack,
                        evidence=evidence,
                        filter_reason="Sales=0 (exact EAN); verify demand before buying",
                    )
                )
                continue

            filter_reason = "Adjusted profit <= 0 (or NetProfit <= 0)" if not profitable else "Excluded by pack gate"
            if explicit_pack_mismatch and required_units > 1 and adjusted_profit <= 0:
                filter_reason = f"Requires {required_units} units; adjusted profit is negative"
            rows_verified_filtered.append(
                make_row_dict(
                    verdict="FILTERED OUT",
                    confidence=conf,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean_disp=supplier_ean_disp,
                    amazon_ean_disp=amazon_ean_disp,
                    asin=asin,
                    supplier_price=supplier_price,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_verdict,
                    adjusted_profit=profit_after_pack,
                    evidence=evidence,
                    filter_reason=filter_reason,
                )
            )
            continue

        if is_highly_likely_match:
            if profitable and sellable and recommendable_pack and cap_status != "mismatch":
                rows_hl_rec.append(
                    make_row_dict(
                        verdict="HIGHLY LIKELY",
                        confidence=conf,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean_disp=supplier_ean_disp,
                        amazon_ean_disp=amazon_ean_disp,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_verdict,
                        adjusted_profit=profit_after_pack,
                        evidence=evidence,
                        filter_reason="-",
                    )
                )
                continue

            filter_reason = "Excluded by gates (sales/pack/capacity)"
            if cap_status == "mismatch":
                filter_reason = f"Different SKU likely: {cap_note}"
            if supplier_multipack_vs_amz_smaller:
                filter_reason = "Supplier multipack vs Amazon smaller; confirm split/units"
            if explicit_pack_mismatch and required_units > 1 and adjusted_profit <= 0:
                filter_reason = f"Requires {required_units} units; adjusted profit is negative"
            if not profitable:
                filter_reason = "Adjusted profit <= 0 (or NetProfit <= 0)"
            if color_mismatch and filter_reason.startswith("Excluded by"):
                filter_reason = color_note

            rows_hl_filtered.append(
                make_row_dict(
                    verdict="FILTERED OUT",
                    confidence=conf,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean_disp=supplier_ean_disp,
                    amazon_ean_disp=amazon_ean_disp,
                    asin=asin,
                    supplier_price=supplier_price,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_verdict,
                    adjusted_profit=profit_after_pack,
                    evidence=evidence,
                    filter_reason=filter_reason,
                )
            )
            continue

        plausible = float(r.get("title_match", 0) or 0) >= 0.45 and len(anchors) >= 2
        worth_it = net_profit > 0.50 and float(roi or 0) >= 15.0
        joined_lower = (supplier_title.lower() + " " + amazon_title.lower())
        ip_risk = any(b in joined_lower for b in IP_RISK_BRANDS)
        if plausible and worth_it and (sales > 0 or conf >= 80):
            reasons: list[str] = []
            if not brand_match:
                reasons.append("Brand not clearly shared; confirm packaging/brand on listing")
            if not product_type_match:
                reasons.append("Product type token not clearly shared; confirm same item")
            if explicit_pack_mismatch:
                reasons.append("Confirm pack count (explicit pack words present/missing)")
            if cap_status == "tolerable_or_minor":
                reasons.append(f"Minor capacity difference: {cap_note}")
            if color_mismatch:
                reasons.append(color_note)
            if ip_risk:
                reasons.append("Potential IP risk brand; confirm sourcing/listing safety")
            if not reasons:
                reasons.append("Confirm 1-2 details (pack/variant) to upgrade confidence")
            rows_needs_ver.append(
                make_row_dict(
                    verdict="NEEDS VERIFICATION",
                    confidence=conf,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean_disp=supplier_ean_disp,
                    amazon_ean_disp=amazon_ean_disp,
                    asin=asin,
                    supplier_price=supplier_price,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_verdict,
                    adjusted_profit=profit_after_pack,
                    evidence=evidence,
                    filter_reason="; ".join(reasons[:2]),
                )
            )

    rows_verified_rec.sort(key=lambda rr: (-int(rr["Sales"]), -_money_to_float(rr["Adjusted Profit"])))
    rows_verified_filtered.sort(key=lambda rr: (-int(rr["Sales"]), -_money_to_float(rr["Adjusted Profit"])))
    rows_hl_rec.sort(key=lambda rr: (-int(rr["Confidence"]), -int(rr["Sales"])))
    rows_hl_filtered.sort(key=lambda rr: (-int(rr["Confidence"]), -int(rr["Sales"])))
    rows_needs_ver.sort(key=lambda rr: (-int(rr["Confidence"]), -int(rr["Sales"])))

    out_md = OUTPUT_DIR / f"PHASEA_MANUAL_REPORT_{TODAY_DUBAI.replace('-', '')}.md"

    def section(title: str, rows: list[dict[str, str]]) -> str:
        return "\n".join(
            [
                f"## {title} (count={len(rows)})",
                "",
                "```text",
                build_fixed_width_table(rows),
                "```",
                "",
            ]
        )

    summary = "\n".join(
        [
            "# PHASEA MANUAL REPORT",
            "",
            f"**Generated:** {TODAY_DUBAI}",
            f"**Input File:** {INPUT_XLSX}",
            f"**Supplier:** {supplier_domain}",
            "",
            "## Summary Counts",
            f"- VERIFIED - RECOMMENDED: {len(rows_verified_rec)}",
            f"- VERIFIED - FILTERED OUT / EXCLUDED: {len(rows_verified_filtered)}",
            f"- HIGHLY LIKELY - RECOMMENDED: {len(rows_hl_rec)}",
            f"- HIGHLY LIKELY - FILTERED OUT / EXCLUDED: {len(rows_hl_filtered)}",
            f"- NEEDS VERIFICATION: {len(rows_needs_ver)}",
            f"- TOTAL ANALYZED: {len(df)}",
            "",
            f"This report applies v{PROMPT_VERSION} Thorough Manual Analysis:",
            "- VERIFIED requires strict-valid, exact EAN (checksum + normalization).",
            "- HIGHLY LIKELY requires brand + product-type anchors from both titles.",
            "- NEEDS VERIFICATION is selective: 1-2 confirmable details should upgrade confidence.",
            "",
        ]
    )

    reconciliation = "\n".join(
        [
            "## Reconciliation",
            f"- Total rows in input: {len(df)}",
            (
                "- Rows analyzed and categorized: "
                f"{len(rows_verified_rec) + len(rows_verified_filtered) + len(rows_hl_rec) + len(rows_hl_filtered) + len(rows_needs_ver)}"
            ),
            "",
        ]
    )

    content = "\n".join(
        [
            summary,
            section("VERIFIED - RECOMMENDED", rows_verified_rec),
            section("VERIFIED - FILTERED OUT / EXCLUDED", rows_verified_filtered),
            section("HIGHLY LIKELY - RECOMMENDED", rows_hl_rec),
            section("HIGHLY LIKELY - FILTERED OUT / EXCLUDED", rows_hl_filtered),
            section("NEEDS VERIFICATION", rows_needs_ver),
            reconciliation,
            f"---\n\n*Prompt Version {PROMPT_VERSION} (Dubai time: {TODAY_DUBAI}).*",
            "",
        ]
    )

    out_md.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
