from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

# --- Paths (user-provided) ---
INPUT_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx")
OUTDIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Codex 2")

# --- v4.0 Practical Gates (for RECOMMENDED tables) ---
MIN_NET_PROFIT_GBP = 0.50
MIN_ADJUSTED_PROFIT_GBP = 0.50
MIN_ROI_PCT = 15.0

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

LUXURY_IP = [
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


def now_dubai() -> datetime:
    # Asia/Dubai is UTC+4 with no DST.
    return datetime.now(timezone(timedelta(hours=4)))


def long_path(path: Path) -> str:
    # Enable extended-length paths on Windows even if MAX_PATH is enforced.
    s = str(path.resolve())
    if s.startswith("\\\\?\\"):
        return s
    return "\\\\?\\" + s


def safe_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\r", " ").replace("\n", " ")


def sanitize_cell(text: str) -> str:
    return text.replace("|", "¦").replace("\t", " ").strip()


def format_gbp(value: Any) -> str:
    if pd.isna(value):
        return "-"
    try:
        v = float(value)
    except Exception:
        return "-"
    return f"£{v:.2f}"


def format_pct(value: Any) -> str:
    if pd.isna(value):
        return "-"
    try:
        v = float(value)
    except Exception:
        return "-"
    return f"{v:.1f}%"


def parse_sales(value: Any) -> int:
    if pd.isna(value):
        return 0
    m = re.search(r"(\d+)", str(value))
    return int(m.group(1)) if m else 0


def clean_to_digits(value: Any) -> str:
    if pd.isna(value):
        return ""
    s = str(value).strip()
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return re.sub(r"\D", "", s)


def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit() or len(digits) not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = 0
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


def supplier_domain(urls: pd.Series) -> str:
    counts: dict[str, int] = {}
    for u in urls.dropna():
        try:
            dom = urlparse(str(u)).netloc.lower()
        except Exception:
            continue
        if dom:
            counts[dom] = counts.get(dom, 0) + 1
    if not counts:
        return "UNKNOWN"
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[0][0]

@dataclass(frozen=True)
class PackInfo:
    qty: float
    explicit: bool
    note: str
    kind: str  # count|mult_count|capacity_count|each|dimension|none|ambiguous


_COUNT_WORD = r"(?:pack|pk|pcs|pc|pieces?|cases?|bags?|rolls?|sheets?|bottles?|containers?|refills?)"
_CAP_UNIT = r"(?:ml|l|ltr|litre|liter|g|kg|oz)"
_LEN_UNIT = r"(?:mm|cm|m|inch|in|ft)"


def extract_pack_info(title: Any) -> PackInfo:
    t = safe_text(title)
    if not t:
        return PackInfo(1.0, False, "-", "none")

    low = t.lower()

    # Dimension pattern (size), tracked but NOT treated as quantity.
    dim_pat = re.compile(
        rf"(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)(?:\s*[x×]\s*(\d+(?:\.\d+)?))?\s*({_LEN_UNIT})\b"
    )
    dim_m = dim_pat.search(low)
    dim_note = f"; dims={dim_m.group(0)}" if dim_m else ""

    # Explicit single markers
    if re.search(r"\b(sold\s+each|each|single)\b", low):
        return PackInfo(1.0, True, f"each{dim_note}".strip(), "each")

    # pack of N
    m = re.search(r"\bpack\s+of\s+(\d{1,3})\b", low)
    if m:
        return PackInfo(float(m.group(1)), True, f"{m.group(0)}{dim_note}", "count")

    # N-pack / N pack
    m = re.search(r"\b(\d{1,3})\s*[- ]\s*pack\b", low)
    if m:
        return PackInfo(float(m.group(1)), True, f"{m.group(0)}{dim_note}", "count")

    # set of N
    m = re.search(r"\bset\s+of\s+(\d{1,3})\b", low)
    if m:
        return PackInfo(float(m.group(1)), True, f"{m.group(0)}{dim_note}", "count")

    # "200 x <letters>" quantity (NOT dimensions)
    m = re.search(r"\b(\d{1,4})\s*[x×]\s*(?=[a-z])", low)
    if m:
        qty = float(m.group(1))
        if 1 <= qty < 500:
            return PackInfo(qty, True, f"{m.group(0)}{dim_note}".strip(), "count")

    # N x M (count word) => total count
    m = re.search(rf"\b(\d{{1,3}})\s*[x×]\s*(\d{{1,4}})\s*{_COUNT_WORD}\b", low)
    if m:
        a = float(m.group(1))
        b = float(m.group(2))
        if 1 <= a < 500 and 1 <= b < 500:
            return PackInfo(a * b, True, f"{m.group(0)}{dim_note}", "mult_count")

    # N x 500ml/g => count is N
    m = re.search(rf"\b(\d{{1,3}})\s*[x×]\s*(\d+(?:\.\d+)?)\s*({_CAP_UNIT})\b", low)
    if m:
        a = float(m.group(1))
        if 1 <= a < 500:
            return PackInfo(a, True, f"{m.group(0)}{dim_note}", "capacity_count")

    # N pcs/bags/cases/etc (includes "10 containers")
    m = re.search(rf"\b(\d{{1,4}})\s*{_COUNT_WORD}\b", low)
    if m:
        qty = float(m.group(1))
        if 1 <= qty < 500:
            return PackInfo(qty, True, f"{m.group(0)}{dim_note}", "count")

    # PK5 / PK10
    m = re.search(r"\bpk\s*(\d{1,3})\b", low)
    if m:
        qty = float(m.group(1))
        if 1 <= qty < 500:
            return PackInfo(qty, True, f"{m.group(0)}{dim_note}", "count")

    # Dimension-only
    if dim_m:
        return PackInfo(1.0, False, f"dims={dim_m.group(0)}", "dimension")

    # Ambiguous x patterns (no units)
    if re.search(r"\b\d+\s*[x×]\s*\d+\b", low):
        return PackInfo(1.0, False, "ambiguous 'x'", "ambiguous")

    return PackInfo(1.0, False, "-", "none")


@dataclass(frozen=True)
class PackAdj:
    pack_verdict: str
    adjusted_profit: float
    needs_verification: bool


def compute_pack_adjustment(
    supplier_title: str, amazon_title: str, supplier_cost: float, net_profit: float, is_exact: bool
) -> PackAdj:
    sup = extract_pack_info(supplier_title)
    amz = extract_pack_info(amazon_title)

    # Dimension cues => never penalize
    if sup.kind == "dimension" or amz.kind == "dimension":
        return PackAdj(
            pack_verdict=f"1:1 Match (dimensions present; sup={sup.note}; amz={amz.note})",
            adjusted_profit=net_profit,
            needs_verification=False,
        )

    # One-side explicit => verification for non-exact; exact defaults to 1:1
    if sup.explicit != amz.explicit:
        if is_exact:
            return PackAdj(
                pack_verdict=f"1:1 Match (no explicit contradiction; sup={sup.note}; amz={amz.note})",
                adjusted_profit=net_profit,
                needs_verification=False,
            )
        return PackAdj(
            pack_verdict=f"Pack unclear (one-side explicit; sup={sup.note}; amz={amz.note})",
            adjusted_profit=net_profit,
            needs_verification=True,
        )

    # Neither explicit
    if not sup.explicit and not amz.explicit:
        return PackAdj("1:1 Match (no pack info in titles)", net_profit, False)

    # Both explicit
    if sup.qty <= 0 or amz.qty <= 0:
        return PackAdj(f"Pack parse failed (sup={sup.note}; amz={amz.note})", net_profit, True)

    ratio = amz.qty / sup.qty
    if math.isclose(ratio, 1.0, rel_tol=0.01, abs_tol=0.01):
        return PackAdj(f"1:1 Match (sup={sup.note}; amz={amz.note})", net_profit, False)

    # Split case (supplier multipack vs Amazon smaller)
    if ratio < 1.0:
        adj = net_profit + supplier_cost * (1.0 - ratio)
        return PackAdj(
            f"SPLIT required (sup={sup.note}; amz={amz.note}; ratio={ratio:.2f})",
            adj,
            True,
        )

    # Bundle case. Require near-integer ratio.
    nearest = int(round(ratio))
    if not math.isclose(ratio, nearest, rel_tol=0.02, abs_tol=0.02):
        return PackAdj(
            f"Pack mismatch ambiguous (sup={sup.note}; amz={amz.note}; ratio={ratio:.2f})",
            net_profit,
            True,
        )

    required_units = max(nearest, 2)
    adj = net_profit - supplier_cost * float(required_units - 1)
    return PackAdj(
        f"BUNDLE ({required_units}x) (sup={sup.note}; amz={amz.note})",
        adj,
        False,
    )

@dataclass(frozen=True)
class Measure:
    value: float
    unit: str


_MEASURE_PAT = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mm|cm|m|inch|in|ft|ml|l|ltr|litre|liter|g|kg|oz|cup|cups)\b"
)


def _to_base(m: Measure) -> Measure:
    u = m.unit.lower()
    if u == "mm":
        return Measure(m.value, "mm")
    if u == "cm":
        return Measure(m.value * 10.0, "mm")
    if u == "m":
        return Measure(m.value * 1000.0, "mm")
    if u in ("inch", "in"):
        return Measure(m.value * 25.4, "mm")
    if u == "ft":
        return Measure(m.value * 304.8, "mm")
    if u == "ml":
        return Measure(m.value, "ml")
    if u in ("l", "ltr", "litre", "liter"):
        return Measure(m.value * 1000.0, "ml")
    if u == "g":
        return Measure(m.value, "g")
    if u == "kg":
        return Measure(m.value * 1000.0, "g")
    if u == "oz":
        return Measure(m.value * 28.3495, "g")
    if u in ("cup", "cups"):
        return Measure(m.value, "cup")
    return m


def extract_measures(title: str) -> list[Measure]:
    t = safe_text(title).lower()
    out: list[Measure] = []
    for m in _MEASURE_PAT.finditer(t):
        try:
            out.append(_to_base(Measure(float(m.group(1)), m.group(2))))
        except Exception:
            continue
    return out


def _rel_diff(a: float, b: float) -> float:
    denom = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denom


def measure_mismatch_level(supplier_title: str, amazon_title: str) -> tuple[str, str]:
    """Return (level, reason). level in {'none','soft','hard'}."""
    sup = extract_measures(supplier_title)
    amz = extract_measures(amazon_title)
    if not sup or not amz:
        return "none", "-"

    def group(ms: list[Measure]) -> dict[str, list[float]]:
        g: dict[str, list[float]] = {}
        for m in ms:
            g.setdefault(m.unit, []).append(m.value)
        for k in g:
            g[k] = sorted(g[k])
        return g

    sg = group(sup)
    ag = group(amz)
    shared = set(sg) & set(ag)
    if not shared:
        return "hard", "Different measurement units between titles"

    for unit in sorted(shared):
        a = sg[unit][-1]
        b = ag[unit][-1]
        d = _rel_diff(a, b)

        if unit in ("ml", "g"):
            if d <= 0.05:
                continue
            if d <= 0.30:
                return "soft", f"Minor capacity/weight difference: {a:.0f}{unit} vs {b:.0f}{unit}"
            return "hard", f"Different capacity/weight: {a:.0f}{unit} vs {b:.0f}{unit}"

        if unit == "cup":
            if d <= 0.05:
                continue
            if d <= 0.30:
                return "soft", f"Minor size (cups) difference: {a:.0f} vs {b:.0f}"
            return "hard", f"Different size (cups): {a:.0f} vs {b:.0f}"

        if unit == "mm":
            if d <= 0.10:
                continue
            return "hard", f"Different dimensions: {a:.0f}{unit} vs {b:.0f}{unit}"

    return "none", "-"


_STOP = {"the", "and", "with", "for", "pack", "of", "set", "in", "on", "a", "an", "to"}


def token_set(s: str) -> set[str]:
    toks = set(re.findall(r"[a-z0-9]+", s.lower()))
    return {t for t in toks if len(t) >= 3 and t not in _STOP}


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def token_jaccard(a: str, b: str) -> float:
    sa = token_set(a)
    sb = token_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def shared_tokens_for_evidence(supplier_title: str, amazon_title: str, limit: int = 4) -> list[str]:
    shared = token_set(supplier_title) & token_set(amazon_title)
    return sorted(shared, key=lambda t: (len(t), t), reverse=True)[:limit]


def money_val(s: str) -> float:
    if not s.startswith("£"):
        return float("nan")
    try:
        return float(s[1:])
    except Exception:
        return float("nan")


def fixed_width_table(rows: list[dict[str, str]]) -> str:
    widths: dict[str, int] = {c: len(c) for c in TABLE_COLUMNS}
    for r in rows:
        for c in TABLE_COLUMNS:
            widths[c] = max(widths[c], len(r[c]))

    def fmt_row(values: dict[str, str]) -> str:
        parts = [f" {values[c].ljust(widths[c])} " for c in TABLE_COLUMNS]
        return "|" + "|".join(parts) + "|"

    header = fmt_row({c: c for c in TABLE_COLUMNS})
    sep = "|" + "|".join(["-" * (widths[c] + 2) for c in TABLE_COLUMNS]) + "|"
    body = "\n".join(fmt_row(r) for r in rows)
    return "\n".join([header, sep, body])


def build_row(
    *,
    verdict: str,
    confidence: int,
    row_id: int,
    supplier_title: str,
    amazon_title: str,
    supplier_ean: str,
    amazon_ean: str,
    asin: str,
    supplier_price: float,
    selling_price: float,
    net_profit: float,
    roi: float,
    sales: int,
    pack_verdict: str,
    adjusted_profit: float,
    evidence: str,
    filter_reason: str,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    d: dict[str, Any] = {
        "Verdict": verdict,
        "Confidence": str(int(confidence)),
        "SupplierTitle": sanitize_cell(f"#{row_id} {supplier_title}".strip()),
        "AmazonTitle": sanitize_cell(amazon_title),
        "Supplier EAN": sanitize_cell(supplier_ean) if supplier_ean else "-",
        "Amazon EAN": sanitize_cell(amazon_ean) if amazon_ean else "-",
        "ASIN": sanitize_cell(asin) if asin else "-",
        "SupplierPrice": format_gbp(supplier_price),
        "SellingPrice": format_gbp(selling_price),
        "NetProfit": format_gbp(net_profit),
        "ROI": format_pct(roi),
        "Sales": str(int(sales)),
        "Pack Verdict": sanitize_cell(pack_verdict),
        "Adjusted Profit": format_gbp(adjusted_profit),
        "Key Match Evidence": sanitize_cell(evidence),
        "Filter Reason": sanitize_cell(filter_reason) if filter_reason else "-",
    }
    if meta:
        d.update(meta)
    return d


def strip_meta(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{c: str(r[c]) for c in TABLE_COLUMNS} for r in rows]


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_PATH.exists():
        raise FileNotFoundError(str(INPUT_PATH))

    # Load with EAN columns as strings to preserve digits.
    df = pd.read_excel(INPUT_PATH, dtype={"EAN": str, "EAN_OnPage": str, "ASIN": str})
    df["RowID"] = df.index + 1

    # Numeric normalization
    for col in ("SupplierPrice_incVAT", "SellingPrice_incVAT", "NetProfit", "ROI"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sales
    if "sales_numeric" in df.columns:
        df["Sales"] = pd.to_numeric(df["sales_numeric"], errors="coerce").fillna(0).astype(int)
    elif "bought_in_past_month" in df.columns:
        df["Sales"] = df["bought_in_past_month"].apply(parse_sales).astype(int)
    else:
        df["Sales"] = 0

    sup_dom = supplier_domain(df.get("SupplierURL", pd.Series([], dtype=object)))

    # Strict EAN matching
    sup_digits = df["EAN"].apply(clean_to_digits).apply(normalize_gtin)
    amz_digits = df["EAN_OnPage"].apply(clean_to_digits).apply(normalize_gtin)

    sup_ok = sup_digits.apply(is_strict_valid_barcode)
    amz_ok = amz_digits.apply(is_strict_valid_barcode)

    df["SupplierEAN_norm"] = sup_digits.where(sup_ok, "-")
    df["AmazonEAN_norm"] = amz_digits.where(amz_ok, "-")
    df["is_exact_ean_strict"] = sup_ok & amz_ok & (sup_digits == amz_digits)

    # Similarity signals for candidate pool
    sup_t = df["SupplierTitle"].apply(safe_text)
    amz_t = df["AmazonTitle"].apply(safe_text)
    df["title_sim"] = [title_similarity(a, b) for a, b in zip(sup_t, amz_t)]
    df["token_jacc"] = [token_jaccard(a, b) for a, b in zip(sup_t, amz_t)]

    exact_pool = df[df["is_exact_ean_strict"]].copy()
    non_exact_pool = df[(~df["is_exact_ean_strict"]) & (df["title_sim"] >= 0.55) & (df["token_jacc"] >= 0.25)].copy()
    analyzed_df = pd.concat([exact_pool, non_exact_pool], ignore_index=True)

    verified_rec: list[dict[str, Any]] = []
    verified_filt: list[dict[str, Any]] = []
    highly_rec: list[dict[str, Any]] = []
    highly_filt: list[dict[str, Any]] = []
    needs_ver: list[dict[str, Any]] = []

    for _, r in analyzed_df.iterrows():
        row_id = int(r["RowID"])
        supplier_title = safe_text(r.get("SupplierTitle"))
        amazon_title = safe_text(r.get("AmazonTitle"))
        asin = safe_text(r.get("ASIN"))

        supplier_ean = safe_text(r.get("SupplierEAN_norm")) or "-"
        amazon_ean = safe_text(r.get("AmazonEAN_norm")) or "-"

        supplier_cost = float(r.get("SupplierPrice_incVAT")) if not pd.isna(r.get("SupplierPrice_incVAT")) else float("nan")
        selling_price = float(r.get("SellingPrice_incVAT")) if not pd.isna(r.get("SellingPrice_incVAT")) else float("nan")
        net_profit = float(r.get("NetProfit")) if not pd.isna(r.get("NetProfit")) else float("nan")
        roi = float(r.get("ROI")) if not pd.isna(r.get("ROI")) else float("nan")
        sales = int(r.get("Sales", 0))

        is_exact = bool(r.get("is_exact_ean_strict"))
        ts = float(r.get("title_sim", 0.0))
        tj = float(r.get("token_jacc", 0.0))

        shared = shared_tokens_for_evidence(supplier_title, amazon_title, limit=4)
        shared_str = ", ".join(shared) if shared else "-"

        mm_level, mm_reason = measure_mismatch_level(supplier_title, amazon_title)

        supplier_cost_for_math = 0.0 if math.isnan(supplier_cost) else supplier_cost
        net_profit_for_math = 0.0 if math.isnan(net_profit) else net_profit
        pack_adj = compute_pack_adjustment(
            supplier_title, amazon_title, supplier_cost_for_math, net_profit_for_math, is_exact
        )

        if is_exact:
            evidence = f"Exact EAN match: {supplier_ean}" if supplier_ean != "-" else "Exact EAN match"

            # Exact-EAN rows: default VERIFIED unless explicit contradictions need verification.
            if pack_adj.needs_verification:
                needs_ver.append(
                    build_row(
                        verdict="NEEDS VERIFICATION",
                        confidence=90,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=supplier_ean,
                        amazon_ean=amazon_ean,
                        asin=asin,
                        supplier_price=supplier_cost,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_adj.pack_verdict,
                        adjusted_profit=pack_adj.adjusted_profit,
                        evidence=evidence,
                        filter_reason="Confirm pack from title cues (explicit on one side / ambiguous ratio)",
                        meta={"_title_sim": ts, "_sales": sales},
                    )
                )
                continue

            if mm_level == "hard":
                needs_ver.append(
                    build_row(
                        verdict="NEEDS VERIFICATION",
                        confidence=90,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=supplier_ean,
                        amazon_ean=amazon_ean,
                        asin=asin,
                        supplier_price=supplier_cost,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_adj.pack_verdict,
                        adjusted_profit=pack_adj.adjusted_profit,
                        evidence=evidence,
                        filter_reason=f"Exact EAN match but title measurements disagree: {mm_reason}",
                        meta={"_title_sim": ts, "_sales": sales},
                    )
                )
                continue

            if (
                sales <= 0
                or math.isnan(net_profit)
                or math.isnan(roi)
                or net_profit < MIN_NET_PROFIT_GBP
                or roi < MIN_ROI_PCT
                or pack_adj.adjusted_profit < MIN_ADJUSTED_PROFIT_GBP
            ):
                reasons: list[str] = []
                if sales <= 0:
                    reasons.append("Sales=0")
                if math.isnan(net_profit) or net_profit < MIN_NET_PROFIT_GBP:
                    reasons.append(f"NetProfit<{MIN_NET_PROFIT_GBP:.2f}")
                if math.isnan(roi) or roi < MIN_ROI_PCT:
                    reasons.append(f"ROI<{MIN_ROI_PCT:.0f}%")
                if pack_adj.adjusted_profit < MIN_ADJUSTED_PROFIT_GBP:
                    reasons.append(f"AdjustedProfit<{MIN_ADJUSTED_PROFIT_GBP:.2f}")

                verified_filt.append(
                    build_row(
                        verdict="FILTERED OUT",
                        confidence=95,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=supplier_ean,
                        amazon_ean=amazon_ean,
                        asin=asin,
                        supplier_price=supplier_cost,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_adj.pack_verdict,
                        adjusted_profit=pack_adj.adjusted_profit,
                        evidence=evidence,
                        filter_reason="; ".join(reasons) if reasons else "Excluded by gates",
                        meta={"_sales": sales, "_adj": pack_adj.adjusted_profit},
                    )
                )
                continue

            verified_rec.append(
                build_row(
                    verdict="VERIFIED",
                    confidence=95,
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean=supplier_ean,
                    amazon_ean=amazon_ean,
                    asin=asin,
                    supplier_price=supplier_cost,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_adj.pack_verdict,
                    adjusted_profit=pack_adj.adjusted_profit,
                    evidence=evidence,
                    filter_reason="-",
                    meta={"_sales": sales, "_adj": pack_adj.adjusted_profit},
                )
            )
            continue

        # ---- Non-exact rows (title based) ----
        if len(shared) < 2:
            continue

        confidence = int(round(55 + 30 * ts + 25 * tj))
        confidence = max(55, min(confidence, 90))
        evidence = f"Shared tokens: {shared_str}"

        # Hard variant mismatch (different size/capacity)
        if mm_level == "hard":
            highly_filt.append(
                build_row(
                    verdict="FILTERED OUT",
                    confidence=min(confidence, 80),
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean=supplier_ean,
                    amazon_ean=amazon_ean,
                    asin=asin,
                    supplier_price=supplier_cost,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_adj.pack_verdict,
                    adjusted_profit=pack_adj.adjusted_profit,
                    evidence=evidence,
                    filter_reason=mm_reason,
                    meta={"_sales": sales, "_conf": confidence},
                )
            )
            continue

        # Financial gates for inclusion
        if (
            sales <= 0
            or math.isnan(net_profit)
            or math.isnan(roi)
            or net_profit < MIN_NET_PROFIT_GBP
            or roi < MIN_ROI_PCT
            or pack_adj.adjusted_profit < MIN_ADJUSTED_PROFIT_GBP
        ):
            reasons: list[str] = []
            if sales <= 0:
                reasons.append("Sales=0")
            if math.isnan(net_profit) or net_profit < MIN_NET_PROFIT_GBP:
                reasons.append(f"NetProfit<{MIN_NET_PROFIT_GBP:.2f}")
            if math.isnan(roi) or roi < MIN_ROI_PCT:
                reasons.append(f"ROI<{MIN_ROI_PCT:.0f}%")
            if pack_adj.adjusted_profit < MIN_ADJUSTED_PROFIT_GBP:
                reasons.append(f"AdjustedProfit<{MIN_ADJUSTED_PROFIT_GBP:.2f}")

            highly_filt.append(
                build_row(
                    verdict="FILTERED OUT",
                    confidence=min(confidence, 80),
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean=supplier_ean,
                    amazon_ean=amazon_ean,
                    asin=asin,
                    supplier_price=supplier_cost,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_adj.pack_verdict,
                    adjusted_profit=pack_adj.adjusted_profit,
                    evidence=evidence,
                    filter_reason="; ".join(reasons) if reasons else "Excluded by gates",
                    meta={"_sales": sales, "_conf": confidence},
                )
            )
            continue

        # Capacity tolerance => NEEDS VERIFICATION, not filtered out
        if mm_level == "soft":
            needs_ver.append(
                build_row(
                    verdict="NEEDS VERIFICATION",
                    confidence=min(confidence, 79),
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean=supplier_ean,
                    amazon_ean=amazon_ean,
                    asin=asin,
                    supplier_price=supplier_cost,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_adj.pack_verdict,
                    adjusted_profit=pack_adj.adjusted_profit,
                    evidence=evidence,
                    filter_reason=mm_reason,
                    meta={"_title_sim": ts, "_sales": sales},
                )
            )
            continue

        if pack_adj.needs_verification:
            needs_ver.append(
                build_row(
                    verdict="NEEDS VERIFICATION",
                    confidence=min(confidence, 79),
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean=supplier_ean,
                    amazon_ean=amazon_ean,
                    asin=asin,
                    supplier_price=supplier_cost,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_adj.pack_verdict,
                    adjusted_profit=pack_adj.adjusted_profit,
                    evidence=evidence,
                    filter_reason="Confirm pack interpretation (one-side pack info / split / ambiguous ratio)",
                    meta={"_title_sim": ts, "_sales": sales},
                )
            )
            continue

        # Strong match => HIGHLY LIKELY
        strong = (ts >= 0.65) and (tj >= 0.35) and (confidence >= 80)
        if strong:
            highly_rec.append(
                build_row(
                    verdict="HIGHLY LIKELY",
                    confidence=confidence,
                    row_id=row_id,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean=supplier_ean,
                    amazon_ean=amazon_ean,
                    asin=asin,
                    supplier_price=supplier_cost,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_adj.pack_verdict,
                    adjusted_profit=pack_adj.adjusted_profit,
                    evidence=evidence,
                    filter_reason="-",
                    meta={"_sales": sales},
                )
            )
        else:
            # Selective: only include if upgradeable
            if confidence >= 70:
                needs_ver.append(
                    build_row(
                        verdict="NEEDS VERIFICATION",
                        confidence=confidence,
                        row_id=row_id,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=supplier_ean,
                        amazon_ean=amazon_ean,
                        asin=asin,
                        supplier_price=supplier_cost,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_adj.pack_verdict,
                        adjusted_profit=pack_adj.adjusted_profit,
                        evidence=evidence,
                        filter_reason="Confirm 1–2 details (brand/variant/pack) to upgrade",
                        meta={"_title_sim": ts, "_sales": sales},
                    )
                )

    # Sorting rules
    verified_rec = sorted(
        verified_rec, key=lambda r: (int(r.get("_sales", 0)), money_val(r["Adjusted Profit"])), reverse=True
    )
    verified_filt = sorted(
        verified_filt, key=lambda r: (int(r.get("_sales", 0)), money_val(r["Adjusted Profit"])), reverse=True
    )
    highly_rec = sorted(highly_rec, key=lambda r: (int(r["Confidence"]), int(r["Sales"])), reverse=True)
    highly_filt = sorted(highly_filt, key=lambda r: (int(r["Confidence"]), int(r["Sales"])), reverse=True)
    needs_ver = sorted(
        needs_ver,
        key=lambda r: (int(r["Confidence"]), float(r.get("_title_sim", 0.0)), int(r["Sales"])),
        reverse=True,
    )

    vrec = strip_meta(verified_rec)
    vfilt = strip_meta(verified_filt)
    hrec = strip_meta(highly_rec)
    hfilt = strip_meta(highly_filt)
    need = strip_meta(needs_ver)

    dt = now_dubai()
    date_md = dt.strftime("%Y-%m-%d")
    date_compact = dt.strftime("%Y%m%d")
    report_path = OUTDIR / f"PHASEA_MANUAL_REPORT_{date_compact}.md"

    total_analyzed = len(vrec) + len(vfilt) + len(hrec) + len(hfilt) + len(need)

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT")
    lines.append("")
    lines.append(f"**Generated:** {date_md}")
    lines.append(f"**Input File:** {INPUT_PATH}")
    lines.append(f"**Supplier:** {sup_dom}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append(f"- VERIFIED — RECOMMENDED: {len(vrec)}")
    lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(vfilt)}")
    lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(hrec)}")
    lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(hfilt)}")
    lines.append(f"- NEEDS VERIFICATION: {len(need)}")
    lines.append(f"- TOTAL ANALYZED: {total_analyzed}")
    lines.append("")
    lines.append(
        "This report applies v4.0 Thorough Manual Analysis with strict EAN checksum validation + left-padding, "
        "dimension/measurement shield, and pack/profit gating."
    )
    lines.append("RowID is prefixed in the SupplierTitle column as `#<RowID>` for traceability.")
    lines.append("")

    def emit_section(title: str, rows: list[dict[str, str]]) -> None:
        lines.append(title)
        lines.append("")
        if not rows:
            lines.append("_None._")
            lines.append("")
            return
        lines.append("```text")
        lines.append(fixed_width_table(rows))
        lines.append("```")
        lines.append("")

    emit_section(f"## VERIFIED — RECOMMENDED (count={len(vrec)})", vrec)
    emit_section(f"## VERIFIED — FILTERED OUT / EXCLUDED (count={len(vfilt)})", vfilt)
    emit_section(f"## HIGHLY LIKELY — RECOMMENDED (count={len(hrec)})", hrec)
    emit_section(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(hfilt)})", hfilt)
    emit_section(f"## NEEDS VERIFICATION (count={len(need)})", need)

    included_text = " ".join(
        (r["SupplierTitle"] + " " + r["AmazonTitle"]).lower() for r in (vrec + vfilt + hrec + hfilt + need)
    )
    ip_found = sorted({b for b in LUXURY_IP if b in included_text})
    if ip_found:
        lines.append("## Additional Notes")
        lines.append(f"- Possible IP/trademark sensitivity in included rows: {', '.join(ip_found)}")
        lines.append("")

    lines.append("## Reconciliation")
    lines.append(f"- Total rows in input: {len(df)}")
    lines.append(f"- Rows analyzed and categorized: {total_analyzed}")
    lines.append("")

    content = "\n".join(lines)

    # Write using long-path support.
    with open(long_path(report_path), "w", encoding="utf-8") as f:
        f.write(content)

    # Acceptance checks (recommended sections)
    for row in vrec:
        assert row["Supplier EAN"] != "-" and row["Amazon EAN"] != "-"
        assert row["Supplier EAN"] == row["Amazon EAN"]
        assert int(row["Sales"]) > 0
        assert money_val(row["NetProfit"]) > 0
        assert money_val(row["Adjusted Profit"]) > 0

    for row in hrec:
        assert int(row["Sales"]) > 0
        assert money_val(row["NetProfit"]) > 0
        assert money_val(row["Adjusted Profit"]) > 0

    size = os.path.getsize(long_path(report_path))
    print(f"WROTE {report_path} ({size} bytes)")
    print(
        f"COUNTS verified_rec={len(vrec)} verified_filt={len(vfilt)} highly_rec={len(hrec)} highly_filt={len(hfilt)} needs_ver={len(need)} total={total_analyzed}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

