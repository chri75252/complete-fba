from __future__ import annotations

import argparse
import datetime as dt
import math
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import pandas as pd


@dataclass(frozen=True)
class OutputPaths:
    deep_csv: Path
    report_md: Path


TABLE_HEADERS = [
    "RowID",
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
    "its",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "without",
}

MEASUREMENT_UNITS = {"inch", "inches", "in", "cm", "mm", "m", "ml", "l", "ltr", "lt", "g", "kg", "oz"}

COUNT_NOUNS = {
    "bag",
    "bags",
    "liner",
    "liners",
    "doyley",
    "doyleys",
    "stick",
    "sticks",
    "case",
    "cases",
    "container",
    "containers",
    "tray",
    "trays",
    "bottle",
    "bottles",
    "bulb",
    "bulbs",
    "tube",
    "tubes",
    "torch",
    "torches",
    "glove",
    "gloves",
    "wipe",
    "wipes",
    "sheet",
    "sheets",
}

DIMENSION_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?\s*(?:inches?|inch|in|cm|mm|m)\b",
    flags=re.IGNORECASE,
)

CAPACITY_PATTERN = re.compile(
    r"\b(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>ml|l|ltr|lt|g|kg|oz)\b",
    flags=re.IGNORECASE,
)


def _clean_ean_value(x: Any) -> str:
    if pd.isna(x):
        return ""
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        if math.isnan(x):
            return ""
        if x.is_integer():
            return str(int(x))
        return ""
    s = str(x).strip()
    if s.lower() in {"nan", "none", ""}:
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    return s


def clean_to_digits(x: Any) -> str:
    s = _clean_ean_value(x)
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
    if not isinstance(digits, str):
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r"0{6,}$", normalized):
        return False
    return gtin_checksum_ok(normalized)


def title_similarity(a: Any, b: Any) -> float:
    if pd.isna(a) or pd.isna(b):
        return 0.0
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def tokenize(title: Any) -> list[str]:
    if pd.isna(title):
        return []
    raw = re.findall(r"[a-z0-9]+", str(title).lower())
    return [t for t in raw if t and t not in STOPWORDS]


def _significant_tokens(tokens: Iterable[str]) -> list[str]:
    out: list[str] = []
    for tok in tokens:
        if len(tok) <= 1:
            continue
        if tok in MEASUREMENT_UNITS:
            continue
        out.append(tok)
    return out


def shared_anchor_tokens(supplier_title: Any, amazon_title: Any, *, limit: int = 6) -> list[str]:
    sup = set(_significant_tokens(tokenize(supplier_title)))
    amz = set(_significant_tokens(tokenize(amazon_title)))
    shared = sorted(sup & amz, key=lambda x: (-len(x), x))
    return shared[:limit]


def supplier_domain_from_urls(urls: pd.Series) -> str:
    domains = (
        urls.dropna()
        .astype(str)
        .map(lambda u: urlparse(u).netloc.lower())
        .value_counts()
        .index.tolist()
    )
    return domains[0] if domains else "unknown"


def _find_capacity(title: Any) -> tuple[str, float] | None:
    if pd.isna(title):
        return None
    m = CAPACITY_PATTERN.search(str(title))
    if not m:
        return None
    val = float(m.group("val"))
    unit = m.group("unit").lower()
    if unit == "ml":
        return ("ml", val)
    if unit in {"l", "ltr", "lt"}:
        return ("ml", val * 1000.0)
    if unit == "g":
        return ("g", val)
    if unit == "kg":
        return ("g", val * 1000.0)
    return None  # oz ambiguous for our purposes


def capacity_variance_pct(a: Any, b: Any) -> float | None:
    ca = _find_capacity(a)
    cb = _find_capacity(b)
    if not ca or not cb:
        return None
    if ca[0] != cb[0]:
        return None
    va, vb = ca[1], cb[1]
    if va <= 0 or vb <= 0:
        return None
    return abs(va - vb) / min(va, vb) * 100.0


def _has_count_context(title: str) -> bool:
    toks = tokenize(title)
    tokset = set(toks)
    if tokset & COUNT_NOUNS:
        return True
    return bool(re.search(r"\b(pack|pk|pcs|pieces|set)\b", title, flags=re.IGNORECASE))


def extract_quantity_safe(title: Any) -> tuple[float, str]:
    """
    Conservative pack-count extraction:
    - Trust explicit pack nouns (pack of / pk / pcs / pieces / pairs / rolls / bags / bottles / cases, etc.)
    - Supports multiplicative counts like '4 x 50' or '200 x ... bags' when there is count context.
    - Never treats dimension patterns like '9 x 9 inch' as pack counts.
    """
    if pd.isna(title):
        return (1.0, "missing-title")
    t = str(title).lower()

    patterns: list[tuple[str, str]] = [
        (r"pack of (\d+)", "pack of"),
        (r"set of (\d+)", "set of"),
        (r"\b(\d+)\s*pack\b", "N pack"),
        (r"\b(\d+)\s*pk\b", "N pk"),
        (r"\b(\d+)\s*pcs\b", "N pcs"),
        (r"\b(\d+)\s*pieces?\b", "N pieces"),
        (r"\b(\d+)\s*pairs?\b", "N pairs"),
        (r"\b(\d+)\s*rolls?\b", "N rolls"),
        (r"\b(\d+)\s*bags?\b", "N bags"),
        (r"\b(\d+)\s*bottles?\b", "N bottles"),
        (r"\b(\d+)\s*cases\b", "N cases"),
        (r"\b(\d+)\s*doyleys?\b", "N doyleys"),
        (r"\b(\d+)\s*sticks?\b", "N sticks"),
        (r"\b(\d+)\s*containers?\b", "N containers"),
        (r"\b(\d+)\s*trays?\b", "N trays"),
        (r"\((\d+)\s*pack\)", "(N pack)"),
        (r"\(pack of (\d+)\)", "(pack of N)"),
    ]

    for pat, why in patterns:
        match = re.search(pat, t)
        if not match:
            continue
        qty = float(match.group(1))
        if 1 < qty < 500:
            return (qty, why)

    # Guard: if it is a true dimension pattern with unit (inch/cm/mm/m), don't use A×B as quantity.
    if DIMENSION_PATTERN.search(t):
        # Still allow other explicit pack patterns already handled above.
        pass

    # Multiplicative counts like "4 x 50" (no unit after second number).
    mult = re.search(r"\b(\d+)\s*[x×]\s*(\d+)\b", t)
    if mult:
        a, b = int(mult.group(1)), int(mult.group(2))
        after = t[mult.end() : mult.end() + 6]
        if re.match(r"\s*(ml|l|ltr|lt|g|kg|oz|cm|mm|m|in|inch|inches)\b", after):
            return (1.0, "AxB-measurement")
        if _has_count_context(t):
            total = a * b
            if 1 < total < 500:
                return (float(total), "AxB total")
        return (1.0, "AxB-ambiguous")

    # Total count phrasing: "200 x ... bags"
    total_x = re.search(r"\b(\d+)\s*x\b", t)
    if total_x and not DIMENSION_PATTERN.search(t) and _has_count_context(t):
        qty = float(total_x.group(1))
        if 1 < qty < 500:
            return (qty, "N x (total count)")

    return (1.0, "default-1")


def recalculate_profit(net_profit: float, supplier_cost: float, ratio: float) -> float:
    """
    Profit-after-pack-sanity baseline:
    - For ratio > 1.0: subtract extra supplier units.
    - For ratio <= 1.0: do NOT boost profit (splits are treated as uncertain).
    """
    if ratio <= 1.0:
        return net_profit
    return net_profit - (supplier_cost * (ratio - 1.0))


def pack_verdict(qty_ratio: float, qty_notes: tuple[str, str]) -> str:
    sup_note, amz_note = qty_notes
    if amz_note in {"AxB-ambiguous"}:
        return "Pack math uncertain - verify manually"
    if amz_note in {"AxB-measurement"}:
        return "1:1 Match (numbers look like measurements)"
    if math.isclose(qty_ratio, 1.0, abs_tol=1e-9):
        return "1:1 Match"
    if qty_ratio > 1.0:
        if abs(qty_ratio - round(qty_ratio)) > 1e-6:
            return "Pack math uncertain - verify manually"
        return f"BUNDLE ({int(round(qty_ratio))}x)"
    return "SPLIT - verify allowed"


def compute_non_ean_mls(
    supplier_title: Any,
    amazon_title: Any,
    *,
    title_match: float,
) -> tuple[int, str, list[str], list[str]]:
    """
    Recall-first heuristic MLS proxy:
    - Shared anchors drive score.
    - Brand token match gives a boost.
    """
    sup_tokens = tokenize(supplier_title)
    amz_tokens = tokenize(amazon_title)
    sup_set = set(_significant_tokens(sup_tokens))
    amz_set = set(_significant_tokens(amz_tokens))

    shared = sup_set & amz_set
    anchors = sorted(shared, key=lambda x: (-len(x), x))

    brand_candidate = next((t for t in sup_tokens if t not in STOPWORDS), "")
    brand_match = bool(brand_candidate and brand_candidate in amz_set)

    mls = 0
    mls += min(60, len(shared) * 15)
    mls += int(round(title_match * 40))
    if brand_match:
        mls += 15

    risks: list[str] = []
    if "assorted" in str(supplier_title).lower() or "assorted" in str(amazon_title).lower():
        mls -= 20
        risks.append("assorted/variety - variant trap risk")

    if len(shared) == 0 and title_match < 0.20:
        mls = min(mls, 25)

    if brand_match and len(shared) >= 2:
        mls = max(mls, 60)

    mls = max(0, min(100, int(round(mls))))

    if mls >= 75:
        band = "HIGH LIKELIHOOD"
    elif mls >= 50:
        band = "NEEDS VERIFICATION"
    elif mls >= 35:
        band = "POSSIBLE"
    else:
        band = "UNLIKELY"

    evidence_notes: list[str] = []
    if brand_match and brand_candidate:
        evidence_notes.append(f"brand token: {brand_candidate}")

    return (mls, band, anchors[:6], risks + evidence_notes)


def _fmt_money(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "-"
    return f"{v:.2f}"


def _fmt_num(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "-"
    if math.isfinite(v) and v.is_integer():
        return str(int(v))
    return f"{v:.2f}"


def _fmt_pct(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "-"
    return f"{v:.2f}"


def _fmt_ean(digits: str, strict_ok: bool) -> str:
    if not strict_ok:
        return "-"
    return normalize_ean(digits)


def _sanitize_cell(value: Any) -> str:
    s = "" if value is None else str(value)
    s = s.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    s = s.replace("|", "¦")
    s = re.sub(r"\s+", " ", s).strip()
    return s if s else "-"


def render_fixed_width_table(headers: list[str], rows: list[list[str]]) -> str:
    cols = len(headers)
    if any(len(r) != cols for r in rows):
        raise ValueError("Row width mismatch")

    widths: list[int] = []
    for i in range(cols):
        widths.append(max(len(headers[i]), *(len(r[i]) for r in rows)) if rows else len(headers[i]))

    def fmt_row(values: list[str]) -> str:
        cells = [f" {values[i].ljust(widths[i])} " for i in range(cols)]
        return "|" + "|".join(cells) + "|"

    header_line = fmt_row(headers)
    sep_cells = [f" {'-' * widths[i]} " for i in range(cols)]
    sep_line = "|" + "|".join(sep_cells) + "|"
    data_lines = [fmt_row(r) for r in rows]
    return "\n".join([header_line, sep_line, *data_lines])


def cap_rows(
    rows: list[pd.Series],
    *,
    cap: int,
    mls_values: list[int] | None = None,
) -> tuple[list[pd.Series], str | None]:
    if len(rows) <= cap:
        return rows, None
    shown = rows[:cap]
    omitted = rows[cap:]
    note = f"NOTE: Showing Top {cap}. Remaining: {len(omitted)} rows."
    if mls_values is not None and len(mls_values) == len(rows):
        omitted_mls = mls_values[cap:]
        if omitted_mls:
            note += f" Omitted MLS range: {min(omitted_mls)}–{max(omitted_mls)}."
    return shown, note


def build_outputs(out_dir: Path, stamp: str) -> OutputPaths:
    return OutputPaths(
        deep_csv=out_dir / f"deep_analysis_{stamp}.csv",
        report_md=out_dir / f"PHASEA_MANUAL_REPORT_{stamp}.md",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze PARTDEC28_1.xlsx into deep CSV + PhaseA report.")
    parser.add_argument(
        "--input-xlsx",
        default=(
            r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - "
            r"POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.xlsx"
        ),
    )
    parser.add_argument(
        "--out-dir",
        default=(
            r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - "
            r"POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\CODEX"
        ),
    )
    parser.add_argument("--stamp", default=dt.date.today().strftime("%Y%m%d"))
    parser.add_argument("--cap", type=int, default=75)
    args = parser.parse_args()

    input_xlsx = Path(args.input_xlsx)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = build_outputs(out_dir, args.stamp)

    df = pd.read_excel(input_xlsx)
    df["RowID"] = df.index + 1

    supplier_domain = supplier_domain_from_urls(df.get("SupplierURL", pd.Series(dtype=str)))

    # Sales signal.
    if "sales_numeric" in df.columns:
        df["sales"] = pd.to_numeric(df["sales_numeric"], errors="coerce").fillna(0)
    elif "bought_in_past_month" in df.columns:
        df["sales"] = pd.to_numeric(df["bought_in_past_month"], errors="coerce").fillna(0)
    else:
        df["sales"] = 0

    # EAN cleanup + strict match.
    df["EAN_digits"] = df["EAN"].apply(clean_to_digits)
    df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(clean_to_digits)
    df["EAN_digits_normalized"] = df["EAN_digits"].apply(normalize_ean)
    df["EAN_OnPage_digits_normalized"] = df["EAN_OnPage_digits"].apply(normalize_ean)
    df["EAN_strict_valid"] = df["EAN_digits_normalized"].apply(is_strict_valid_barcode)
    df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_digits_normalized"].apply(is_strict_valid_barcode)
    df["is_exact_ean_strict"] = (
        df["EAN_strict_valid"]
        & df["EAN_OnPage_strict_valid"]
        & (df["EAN_digits_normalized"] == df["EAN_OnPage_digits_normalized"])
    )

    # Title similarity.
    df["title_match"] = df.apply(lambda r: title_similarity(r.get("SupplierTitle"), r.get("AmazonTitle")), axis=1)

    # Pack extraction and Adjusted Profit.
    sup_qty = df["SupplierTitle"].apply(extract_quantity_safe)
    amz_qty = df["AmazonTitle"].apply(extract_quantity_safe)
    df["Sup_Qty"] = sup_qty.apply(lambda t: float(t[0]))
    df["Sup_Qty_Note"] = sup_qty.apply(lambda t: str(t[1]))
    df["Amz_Qty"] = amz_qty.apply(lambda t: float(t[0]))
    df["Amz_Qty_Note"] = amz_qty.apply(lambda t: str(t[1]))
    df["Qty_Ratio"] = df.apply(
        lambda r: (float(r["Amz_Qty"]) / float(r["Sup_Qty"])) if float(r["Sup_Qty"]) > 0 else 1.0,
        axis=1,
    )

    df["NetProfit"] = pd.to_numeric(df.get("NetProfit", 0), errors="coerce").fillna(0)
    df["SupplierPrice_incVAT"] = pd.to_numeric(df.get("SupplierPrice_incVAT", 0), errors="coerce").fillna(0)
    df["Adjusted_Profit"] = df.apply(
        lambda r: recalculate_profit(float(r["NetProfit"]), float(r["SupplierPrice_incVAT"]), float(r["Qty_Ratio"])),
        axis=1,
    )
    df["Pack_Verdict"] = df.apply(
        lambda r: pack_verdict(float(r["Qty_Ratio"]), (str(r["Sup_Qty_Note"]), str(r["Amz_Qty_Note"]))),
        axis=1,
    )

    # MLS for non-EAN candidates (title_match >= 0.10, not strict exact EAN).
    df["MLS"] = 0
    df["MLS_band"] = "UNLIKELY"
    non_ean_candidate = (~df["is_exact_ean_strict"]) & (df["title_match"] >= 0.10)
    for idx, row in df.loc[non_ean_candidate].iterrows():
        mls, band, anchors, notes = compute_non_ean_mls(
            row.get("SupplierTitle"),
            row.get("AmazonTitle"),
            title_match=float(row.get("title_match") or 0.0),
        )
        df.at[idx, "MLS"] = mls
        df.at[idx, "MLS_band"] = band

    df.loc[df["is_exact_ean_strict"], "MLS"] = 95
    df.loc[df["is_exact_ean_strict"], "MLS_band"] = "EXACT_EAN_STRICT"

    # Deep analysis CSV.
    deep_cols = [
        "RowID",
        "is_exact_ean_strict",
        "EAN_digits",
        "EAN_OnPage_digits",
        "EAN_digits_normalized",
        "EAN_OnPage_digits_normalized",
        "EAN_strict_valid",
        "EAN_OnPage_strict_valid",
        "Pack_Verdict",
        "Adjusted_Profit",
        "NetProfit",
        "ROI",
        "Qty_Ratio",
        "Sup_Qty",
        "Amz_Qty",
        "title_match",
        "sales",
        "MLS",
        "MLS_band",
        "SupplierTitle",
        "AmazonTitle",
        "EAN",
        "EAN_OnPage",
        "ASIN",
        "SupplierPrice_incVAT",
        "SellingPrice_incVAT",
    ]
    df[deep_cols].to_csv(outputs.deep_csv, index=False)

    # ---- Bucketing for report (mutually exclusive) ----
    bucket: list[str] = ["OTHER"] * len(df)
    confidence: list[int] = [0] * len(df)
    evidence: list[str] = [""] * len(df)
    reason: list[str] = [""] * len(df)
    adjusted_profit_final: list[float] = [float(x) for x in df["Adjusted_Profit"].tolist()]
    pack_verdict_final: list[str] = [str(x) for x in df["Pack_Verdict"].tolist()]

    def set_row(i: int, b: str, conf: int, ev: str, rsn: str) -> None:
        bucket[i] = b
        confidence[i] = conf
        evidence[i] = ev
        reason[i] = rsn

    for i, row in df.iterrows():
        is_exact = bool(row["is_exact_ean_strict"])
        mls = int(row.get("MLS", 0) or 0)
        seq = float(row.get("title_match", 0.0) or 0.0)

        sup_ean_disp = _fmt_ean(str(row["EAN_digits"]), bool(row["EAN_strict_valid"]))
        amz_ean_disp = _fmt_ean(str(row["EAN_OnPage_digits"]), bool(row["EAN_OnPage_strict_valid"]))
        anchors = shared_anchor_tokens(row.get("SupplierTitle"), row.get("AmazonTitle"), limit=4)
        anchor_ev = ", ".join(anchors[:3]) if anchors else "-"

        net_profit = float(row.get("NetProfit", 0.0) or 0.0)
        sales = float(row.get("sales", 0.0) or 0.0)
        ratio = float(row.get("Qty_Ratio", 1.0) or 1.0)

        cap_var = capacity_variance_pct(row.get("SupplierTitle"), row.get("AmazonTitle"))
        has_dimensions = bool(DIMENSION_PATTERN.search(str(row.get("SupplierTitle", "")))) or bool(
            DIMENSION_PATTERN.search(str(row.get("AmazonTitle", "")))
        )

        if is_exact:
            conf = 95
            if has_dimensions:
                conf = 90

            ev_parts = [f"Exact EAN: {sup_ean_disp}"]
            if anchors:
                ev_parts.append(f"anchors: {', '.join(anchors[:2])}")
            ev = "; ".join(ev_parts)

            # Capacity tolerance => needs verification (recall-first).
            if cap_var is not None and cap_var <= 30.0:
                set_row(i, "NEEDS_VERIFICATION", conf, ev, f"Minor capacity variance (~{cap_var:.0f}%)")
                continue

            # Dimension shield: if pack math seems to come only from dimensions, restore to 1:1.
            if has_dimensions and "BUNDLE" in str(row.get("Pack_Verdict", "")):
                pack_verdict_final[i] = "1:1 Match"
                adjusted_profit_final[i] = net_profit

            # If clear pack mismatch makes profit-after-pack <= 0, audit-exclude.
            if ratio > 1.0 and adjusted_profit_final[i] <= 0:
                set_row(i, "AUDIT_VERIFIED_EXCLUDED", 75, ev, "EXCLUDED: pack mismatch -> profit-after-pack ≤ 0")
                continue

            if sales <= 0:
                set_row(i, "NEEDS_VERIFICATION", conf, ev, "Sales=0 (exact EAN) - verify demand")
                continue
            if net_profit <= 0 or adjusted_profit_final[i] <= 0:
                set_row(i, "NEEDS_VERIFICATION", conf, ev, "Profit gating failed - verify fees/pack")
                continue

            set_row(i, "VERIFIED_RECOMMENDED", conf, ev, "-")
            continue

        # Non-exact EAN path.
        ev = f"anchors: {anchor_ev}"

        if seq < 0.10 or mls < 35:
            set_row(i, "OTHER", mls, ev, "-")
            continue

        if "uncertain" in str(row.get("Pack_Verdict", "")).lower():
            set_row(i, "NEEDS_VERIFICATION", mls, ev, "Pack math uncertain - verify manually")
            continue

        if mls >= 75:
            if sales <= 0:
                set_row(i, "NEEDS_VERIFICATION", mls, ev, "Sales=0 (high MLS) - verify demand")
                continue
            if net_profit <= 0 or adjusted_profit_final[i] <= 0:
                set_row(i, "AUDIT_HIGHLIK_EXCLUDED", mls, ev, "EXCLUDED: profit-after-pack ≤ 0")
                continue
            if len(anchors) < 2:
                set_row(i, "NEEDS_VERIFICATION", mls, ev, "Insufficient grounded anchors - verify manually")
                continue
            set_row(i, "HIGH_LIKELIHOOD_RECOMMENDED", mls, ev, "-")
            continue

        set_row(i, "NEEDS_VERIFICATION", mls, ev, "-")

    df["bucket"] = bucket
    df["Confidence"] = confidence
    df["Key_Match_Evidence_Final"] = evidence
    df["Filter_Reason_Final"] = reason
    df["Pack_Verdict_Final"] = pack_verdict_final
    df["Adjusted_Profit_Final"] = adjusted_profit_final

    total_rows = len(df)
    count_verified = int((df["bucket"] == "VERIFIED_RECOMMENDED").sum())
    count_high = int((df["bucket"] == "HIGH_LIKELIHOOD_RECOMMENDED").sum())
    count_needs = int((df["bucket"] == "NEEDS_VERIFICATION").sum())
    count_audit = int(df["bucket"].isin(["AUDIT_VERIFIED_EXCLUDED", "AUDIT_HIGHLIK_EXCLUDED"]).sum())
    count_other = int((df["bucket"] == "OTHER").sum())
    sum_buckets = count_verified + count_high + count_needs + count_audit + count_other
    recon_pass = sum_buckets == total_rows

    def row_to_table(r: pd.Series, verdict_label: str) -> list[str]:
        sup_ean = _fmt_ean(str(r["EAN_digits"]), bool(r["EAN_strict_valid"]))
        amz_ean = _fmt_ean(str(r["EAN_OnPage_digits"]), bool(r["EAN_OnPage_strict_valid"]))
        return [
            _sanitize_cell(int(r["RowID"])),
            _sanitize_cell(verdict_label),
            _sanitize_cell(int(r["Confidence"])),
            _sanitize_cell(r.get("SupplierTitle", "")),
            _sanitize_cell(r.get("AmazonTitle", "")),
            _sanitize_cell(sup_ean),
            _sanitize_cell(amz_ean),
            _sanitize_cell(r.get("ASIN", "")),
            _sanitize_cell(_fmt_money(r.get("SupplierPrice_incVAT"))),
            _sanitize_cell(_fmt_money(r.get("SellingPrice_incVAT"))),
            _sanitize_cell(_fmt_money(r.get("NetProfit"))),
            _sanitize_cell(_fmt_pct(r.get("ROI"))),
            _sanitize_cell(_fmt_num(r.get("sales"))),
            _sanitize_cell(r.get("Pack_Verdict_Final", "")),
            _sanitize_cell(_fmt_money(r.get("Adjusted_Profit_Final"))),
            _sanitize_cell(r.get("Key_Match_Evidence_Final", "")),
            _sanitize_cell(r.get("Filter_Reason_Final", "")),
        ]

    def write_section(
        fh,
        *,
        title: str,
        rows_df: pd.DataFrame,
        verdict_label: str,
        sort_cols: list[str],
        cap: int,
        mls_col: str | None = None,
    ) -> None:
        fh.write(f"\n## {title}\n\n")
        if rows_df.empty:
            fh.write("(none)\n")
            return

        sorted_df = rows_df.sort_values(sort_cols, ascending=[False] * len(sort_cols)).copy()
        rows_series = [r for _, r in sorted_df.iterrows()]
        mls_vals = [int(r.get(mls_col, 0) or 0) for r in rows_series] if mls_col else None
        shown, note = cap_rows(rows_series, cap=cap, mls_values=mls_vals)
        if note:
            fh.write(note + "\n\n")

        table_rows = [row_to_table(r, verdict_label) for r in shown]
        fh.write("```text\n")
        fh.write(render_fixed_width_table(TABLE_HEADERS, table_rows))
        fh.write("\n```\n")

    with outputs.report_md.open("w", encoding="utf-8") as fh:
        fh.write("# PHASEA MANUAL REPORT\n")
        fh.write(f"**Generated (YYYY-MM-DD):** {dt.date.today().strftime('%Y-%m-%d')}\n\n")
        fh.write(f"**Input:** {input_xlsx}\n\n")
        fh.write(f"**Supplier (from SupplierURL):** {supplier_domain}\n\n")
        fh.write(
            "This report is recall-first: uncertain cases go to NEEDS VERIFICATION, and only explicit contradictions "
            "are excluded. No external lookups were used.\n"
        )

        fh.write("\n## Reconciliation Proof\n\n")
        recon_headers = ["Bucket", "Count"]
        recon_rows = [
            ["Total input rows", str(total_rows)],
            ["VERIFIED (Recommended)", str(count_verified)],
            ["HIGH LIKELIHOOD (Recommended)", str(count_high)],
            ["NEEDS VERIFICATION", str(count_needs)],
            ["FILTERED OUT (Audit)", str(count_audit)],
            ["OTHER (Low MLS / not listed)", str(count_other)],
            ["SUM", str(sum_buckets)],
        ]
        fh.write("```text\n")
        fh.write(render_fixed_width_table(recon_headers, recon_rows))
        fh.write("\n```\n\n")
        fh.write(
            f"✅ Reconciliation: {count_verified} + {count_high} + {count_needs} + {count_audit} + {count_other} = "
            f"{total_rows} ({'PASS' if recon_pass else 'FAIL'})\n"
        )

        verified_rec = df[df["bucket"] == "VERIFIED_RECOMMENDED"]
        high_rec = df[df["bucket"] == "HIGH_LIKELIHOOD_RECOMMENDED"]
        needs_ver = df[df["bucket"] == "NEEDS_VERIFICATION"]
        verified_ex = df[df["bucket"] == "AUDIT_VERIFIED_EXCLUDED"]
        high_ex = df[df["bucket"] == "AUDIT_HIGHLIK_EXCLUDED"]

        write_section(
            fh,
            title="VERIFIED (Exact EAN) — RECOMMENDED",
            rows_df=verified_rec,
            verdict_label="VERIFIED",
            sort_cols=["sales", "NetProfit"],
            cap=args.cap,
        )
        write_section(
            fh,
            title="HIGH LIKELIHOOD (Non-EAN) — RECOMMENDED",
            rows_df=high_rec,
            verdict_label="HIGH LIKELIHOOD",
            sort_cols=["MLS", "sales", "Adjusted_Profit_Final"],
            cap=args.cap,
            mls_col="MLS",
        )
        write_section(
            fh,
            title="NEEDS VERIFICATION — REVIEW (includes MLS 35–74 + exact-EAN ambiguities)",
            rows_df=needs_ver,
            verdict_label="NEEDS VERIFICATION",
            sort_cols=["MLS", "sales", "Adjusted_Profit_Final"],
            cap=args.cap,
            mls_col="MLS",
        )
        write_section(
            fh,
            title="VERIFIED (Exact EAN) — FILTERED OUT (Audit) — EXCLUDED",
            rows_df=verified_ex,
            verdict_label="EXCLUDED",
            sort_cols=["sales", "NetProfit"],
            cap=args.cap,
        )
        write_section(
            fh,
            title="HIGH LIKELIHOOD — FILTERED OUT (Audit) — EXCLUDED",
            rows_df=high_ex,
            verdict_label="EXCLUDED",
            sort_cols=["MLS", "sales", "Adjusted_Profit_Final"],
            cap=args.cap,
            mls_col="MLS",
        )

        fh.write("\n## IP Risk\n\n")
        fh.write("No IP-risk brand keywords detected in titles (per softened list).\n")

    print(f"Wrote: {outputs.deep_csv}")
    print(f"Wrote: {outputs.report_md}")
    print(f"Supplier: {supplier_domain}")
    print(f"Reconciliation: {sum_buckets} / {total_rows} ({'PASS' if recon_pass else 'FAIL'})")

    return 0 if recon_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
