from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

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

STOPWORDS = {
    "the",
    "and",
    "with",
    "for",
    "of",
    "to",
    "a",
    "an",
    "in",
    "on",
    "by",
    "pack",
    "pk",
    "set",
    "pcs",
    "pieces",
    "piece",
    "x",
    "each",
    "new",
    "original",
}

DIMENSION_RE = re.compile(
    r"(\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?(?:\s*[x×]\s*\d+(?:\.\d+)?)?\s*(?:mm|cm|m|inch|in|\"|ft)\b)"
    r"|(\b\d+(?:\.\d+)?[x×]\d+(?:\.\d+)?(?:[x×]\d+(?:\.\d+)?)?(?:mm|cm|m|inch|in|ft)\b)",
    flags=re.IGNORECASE,
)

COUNT_X_CAPACITY_RE = re.compile(r"\b(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(ml|l|g|kg|oz)\b", re.I)
CAPACITY_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(ml|l|g|kg|oz)\b", re.I)

PACK_PATTERNS = [
    re.compile(r"\bpack\s*of\s*(\d+)\b", re.I),
    re.compile(r"\bset\s*of\s*(\d+)\b", re.I),
    re.compile(r"\bbox\s*of\s*(\d+)\b", re.I),
    re.compile(r"\bcase\s*of\s*(\d+)\b", re.I),
    re.compile(r"\b(\d+)\s*(?:pack|pk)\b", re.I),
    re.compile(r"\bpk\s*-?\s*(\d+)\b", re.I),
    re.compile(r"\bpk(\d+)\b", re.I),
    re.compile(r"\b(\d+)\s*(?:pcs|pieces|pairs|rolls|bottles)\b", re.I),
]

def _safe_str(x: object) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x).replace("\r", " ").replace("\n", " ").strip()


def clean_to_digits(x: object) -> str:
    s = _safe_str(x)
    if not s or s.lower() in {"nan", "none", "-"}:
        return ""
    if "e" in s.lower():
        return ""
    return re.sub(r"\D", "", s)


def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit() or len(digits) not in (8, 12, 13, 14):
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


def has_dimension_pattern(title: str) -> bool:
    return bool(DIMENSION_RE.search(title))


@dataclass(frozen=True)
class PackInfo:
    count: int
    evidence: str
    reliable: bool


def extract_pack_info(title: str) -> PackInfo:
    t = title.strip()
    if not t:
        return PackInfo(1, "-", False)

    m = COUNT_X_CAPACITY_RE.search(t)
    if m:
        n = int(m.group(1))
        if 1 < n < 500:
            return PackInfo(n, f"'{m.group(0)}'", True)

    for pat in PACK_PATTERNS:
        m = pat.search(t)
        if m:
            n = int(m.group(1))
            if 1 < n < 500:
                return PackInfo(n, f"'{m.group(0)}'", True)

    if not has_dimension_pattern(t):
        m = re.search(r"\b(\d+)\s*[x×]\b", t, re.I)
        if m:
            n = int(m.group(1))
            if 1 < n < 200:
                return PackInfo(n, f"'{m.group(0)}'", False)

    return PackInfo(1, "-", False)


def extract_capacity_ml(title: str) -> tuple[float | None, str]:
    t = title.strip()
    if not t:
        return None, "-"
    m = CAPACITY_RE.search(t)
    if not m:
        return None, "-"
    value = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "ml":
        return value, f"'{m.group(0)}'"
    if unit == "l":
        return value * 1000.0, f"'{m.group(0)}'"
    return None, "-"


def title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def tokenize(title: str) -> list[str]:
    t = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    return [tok for tok in t.split() if len(tok) >= 3 and tok not in STOPWORDS]


def pick_brand_candidates(supplier_title: str) -> list[str]:
    toks = tokenize(supplier_title)
    out = []
    for tok in toks[:3]:
        if tok.isdigit() or len(tok) < 4:
            continue
        out.append(tok)
    return out[:2]


def shared_anchor_tokens(supplier_title: str, amazon_title: str, max_tokens: int = 6) -> list[str]:
    st = supplier_title.lower()
    at = amazon_title.lower()
    shared = list(set(tokenize(supplier_title)) & set(tokenize(amazon_title)))
    shared = [t for t in shared if len(t) >= 4]
    shared.sort(key=lambda x: (-len(x), x))
    grounded = []
    for tok in shared:
        if tok in st and tok in at:
            grounded.append(tok)
        if len(grounded) >= max_tokens:
            break
    return grounded


def fmt_gbp(x: float | None) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"£{x:,.2f}"


def fmt_pct(x: float | None) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{x:.1f}%"


def fmt_int(x: float | int) -> str:
    try:
        return str(int(x))
    except Exception:
        return "0"


def build_fixed_width_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        widths = {c: len(c) for c in TABLE_COLUMNS}
        h = "| " + " | ".join(f"{c:<{widths[c]}}" for c in TABLE_COLUMNS) + " |"
        s = "|" + "|".join("-" * (widths[c] + 2) for c in TABLE_COLUMNS) + "|"
        return "\n".join([h, s])

    widths = {c: len(c) for c in TABLE_COLUMNS}
    for r in rows:
        for c in TABLE_COLUMNS:
            widths[c] = max(widths[c], len(_safe_str(r.get(c, "-"))))

    header = "| " + " | ".join(f"{c:<{widths[c]}}" for c in TABLE_COLUMNS) + " |"
    sep = "|" + "|".join("-" * (widths[c] + 2) for c in TABLE_COLUMNS) + "|"

    lines = [header, sep]
    for r in rows:
        lines.append(
            "| " + " | ".join(f"{_safe_str(r.get(c, '-')):<{widths[c]}}" for c in TABLE_COLUMNS) + " |"
        )
    return "\n".join(lines)


def infer_supplier_name(df: pd.DataFrame) -> str:
    if "SupplierURL" not in df.columns:
        return "-"
    s = df["SupplierURL"].dropna().astype(str)
    if s.empty:
        return "-"
    domains = s.map(lambda u: urlparse(u).netloc.lower().lstrip("www."))
    if domains.empty:
        return "-"
    return str(domains.value_counts().index[0])


def contains_luxury_ip(title: str) -> str | None:
    t = title.lower()
    for b in LUXURY_IP_BRANDS:
        if b in t:
            return b
    return None


def mk_row(
    *,
    verdict: str,
    confidence: int,
    supplier_title: str,
    amazon_title: str,
    supplier_ean: str,
    amazon_ean: str,
    asin: str,
    supplier_price: float,
    selling_price: float,
    net_profit: float,
    roi: float,
    sales: float,
    pack_verdict: str,
    adjusted_profit: float,
    evidence: str,
    filter_reason: str,
) -> dict[str, str]:
    return {
        "Verdict": verdict,
        "Confidence": str(confidence),
        "SupplierTitle": supplier_title,
        "AmazonTitle": amazon_title,
        "Supplier EAN": supplier_ean if supplier_ean else "-",
        "Amazon EAN": amazon_ean if amazon_ean else "-",
        "ASIN": asin or "-",
        "SupplierPrice": fmt_gbp(supplier_price),
        "SellingPrice": fmt_gbp(selling_price),
        "NetProfit": fmt_gbp(net_profit),
        "ROI": fmt_pct(roi),
        "Sales": fmt_int(sales),
        "Pack Verdict": pack_verdict,
        "Adjusted Profit": fmt_gbp(adjusted_profit),
        "Key Match Evidence": evidence,
        "Filter Reason": filter_reason,
    }


def pack_and_profit(
    *,
    is_exact_ean: bool,
    supplier_title: str,
    amazon_title: str,
    supplier_pack: PackInfo,
    amazon_pack: PackInfo,
    has_dimensions_flag: bool,
    supplier_price: float,
    net_profit: float,
) -> tuple[str, int | None, float]:
    explicit = (
        supplier_pack.evidence != "-" or amazon_pack.evidence != "-" or "pack" in supplier_title.lower() or "pack" in amazon_title.lower()
    )

    rsu: int | None = 1

    if has_dimensions_flag and not explicit:
        rsu = 1
        pack_v = "1:1 Match (dimensions)"
    else:
        if supplier_pack.count > 1 and amazon_pack.count > 1 and supplier_pack.count != amazon_pack.count:
            ratio = amazon_pack.count / supplier_pack.count
            if ratio > 1 and abs(ratio - round(ratio)) < 0.05:
                rsu = int(round(ratio))
                pack_v = f"BUNDLE ({rsu}x); Supplier {supplier_pack.evidence}; Amazon {amazon_pack.evidence}"
            else:
                rsu = None
                pack_v = f"Pack uncertain; Supplier {supplier_pack.evidence}; Amazon {amazon_pack.evidence}"
        elif supplier_pack.count == 1 and amazon_pack.count > 1:
            rsu = amazon_pack.count
            pack_v = f"BUNDLE ({rsu}x); Amazon {amazon_pack.evidence}"
        elif supplier_pack.count > 1 and amazon_pack.count == 1:
            rsu = None
            pack_v = f"Pack uncertain; Supplier {supplier_pack.evidence}; Amazon {amazon_pack.evidence}"
        else:
            rsu = 1
            pack_v = "1:1 Match"
            ev = []
            if supplier_pack.evidence != "-":
                ev.append(f"Supplier {supplier_pack.evidence}")
            if amazon_pack.evidence != "-":
                ev.append(f"Amazon {amazon_pack.evidence}")
            if ev:
                pack_v += "; " + "; ".join(ev)

    if rsu is None:
        adjusted = net_profit
    else:
        adjusted = net_profit - supplier_price * (rsu - 1)

    if is_exact_ean and rsu not in (None, 1):
        pack_v += "; exact EAN, explicit pack mismatch"

    return pack_v, rsu, adjusted


def main() -> int:
    repo_root = Path(
        r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
    )
    input_path = repo_root / "RESERACH" / "REPORT" / "part_30_dec" / "part_30_dec.xlsx"
    out_dir = repo_root / "RESERACH" / "REPORT" / "part_30_dec" / "cli"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(input_path, dtype={"EAN": str, "EAN_OnPage": str}).copy()
    df["RowID"] = df.index + 1

    supplier_name = infer_supplier_name(df)

    df["SupplierTitle"] = df["SupplierTitle"].fillna("").astype(str)
    df["AmazonTitle"] = df["AmazonTitle"].fillna("").astype(str)

    df["sales"] = pd.to_numeric(df.get("sales_numeric", df.get("bought_in_past_month", 0)), errors="coerce").fillna(0)

    df["SupplierPrice_incVAT_num"] = pd.to_numeric(df.get("SupplierPrice_incVAT", 0), errors="coerce").fillna(0.0)
    df["SellingPrice_incVAT_num"] = pd.to_numeric(df.get("SellingPrice_incVAT", 0), errors="coerce").fillna(0.0)
    df["NetProfit_num"] = pd.to_numeric(df.get("NetProfit", 0), errors="coerce").fillna(0.0)
    df["ROI_num"] = pd.to_numeric(df.get("ROI", 0), errors="coerce").fillna(0.0)

    df["EAN_digits"] = df["EAN"].map(clean_to_digits)
    df["EAN_OnPage_digits"] = df["EAN_OnPage"].map(clean_to_digits)

    df["EAN_norm"] = df["EAN_digits"].map(normalize_ean)
    df["EAN_OnPage_norm"] = df["EAN_OnPage_digits"].map(normalize_ean)

    df["EAN_valid"] = df["EAN_norm"].map(is_strict_valid_barcode)
    df["EAN_OnPage_valid"] = df["EAN_OnPage_norm"].map(is_strict_valid_barcode)

    df["is_exact_ean_strict"] = df["EAN_valid"] & df["EAN_OnPage_valid"] & (df["EAN_norm"] == df["EAN_OnPage_norm"])

    df["title_match"] = df.apply(lambda r: title_similarity(r["SupplierTitle"], r["AmazonTitle"]), axis=1)

    df["sup_pack"] = df["SupplierTitle"].map(extract_pack_info)
    df["amz_pack"] = df["AmazonTitle"].map(extract_pack_info)
    df["has_dimensions"] = df.apply(lambda r: has_dimension_pattern(r["SupplierTitle"]) or has_dimension_pattern(r["AmazonTitle"]), axis=1)

    sup_cap = df["SupplierTitle"].map(extract_capacity_ml)
    amz_cap = df["AmazonTitle"].map(extract_capacity_ml)
    df["sup_cap_ml"] = [c[0] for c in sup_cap]
    df["sup_cap_ev"] = [c[1] for c in sup_cap]
    df["amz_cap_ml"] = [c[0] for c in amz_cap]
    df["amz_cap_ev"] = [c[1] for c in amz_cap]

    verified_rec: list[dict[str, str]] = []
    verified_filt: list[dict[str, str]] = []
    hl_rec: list[dict[str, str]] = []
    hl_filt: list[dict[str, str]] = []
    needs_ver: list[dict[str, str]] = []

    for _, r in df.iterrows():
        row_id = int(r["RowID"])
        supplier_title = _safe_str(r["SupplierTitle"])
        amazon_title = _safe_str(r["AmazonTitle"])
        asin = _safe_str(r.get("ASIN", ""))

        supplier_price = float(r["SupplierPrice_incVAT_num"])
        selling_price = float(r["SellingPrice_incVAT_num"])
        net_profit = float(r["NetProfit_num"])
        roi = float(r["ROI_num"])
        sales = float(r["sales"])

        sup_ean = r["EAN_norm"] if bool(r["EAN_valid"]) else ""
        amz_ean = r["EAN_OnPage_norm"] if bool(r["EAN_OnPage_valid"]) else ""

        exact = bool(r["is_exact_ean_strict"])
        tm = float(r["title_match"])

        anchors = shared_anchor_tokens(supplier_title, amazon_title)
        brand_candidates = pick_brand_candidates(supplier_title)
        brand_match = any(b in amazon_title.lower() for b in brand_candidates)

        assorted = ("assorted" in supplier_title.lower()) or ("assorted" in amazon_title.lower())

        pack_v, rsu, adj_profit = pack_and_profit(
            is_exact_ean=exact,
            supplier_title=supplier_title,
            amazon_title=amazon_title,
            supplier_pack=r["sup_pack"],
            amazon_pack=r["amz_pack"],
            has_dimensions_flag=bool(r["has_dimensions"]),
            supplier_price=supplier_price,
            net_profit=net_profit,
        )

        cap_reason = ""
        if r["sup_cap_ml"] is not None and r["amz_cap_ml"] is not None and r["sup_cap_ml"] and r["amz_cap_ml"]:
            rel = abs(float(r["sup_cap_ml"]) - float(r["amz_cap_ml"])) / max(float(r["sup_cap_ml"]), float(r["amz_cap_ml"]))
            if rel <= 0.30:
                cap_reason = f"Minor capacity difference: {r['sup_cap_ev']} vs {r['amz_cap_ev']}"
            else:
                cap_reason = f"Different capacity (likely different SKU): {r['sup_cap_ev']} vs {r['amz_cap_ev']}"

        ip = contains_luxury_ip(supplier_title) or contains_luxury_ip(amazon_title)

        # Evidence (row-grounded)
        ev = []
        if exact:
            ev.append("Exact EAN match")
        if brand_match and brand_candidates:
            ev.append(f"Brand anchor: '{brand_candidates[0]}'")
        if anchors:
            ev.append("Shared tokens: " + ", ".join(f"'{a}'" for a in anchors[:4]))
        if r["sup_pack"].evidence != "-" or r["amz_pack"].evidence != "-":
            ev.append(f"Pack evidence: {pack_v}")
        ev.append(f"RowID={row_id}")
        evidence = "; ".join(ev)

        # Confidence
        if exact:
            conf = 95
            if rsu not in (None, 1):
                conf = 90
            if not anchors and not brand_match:
                conf = min(conf, 90)
        else:
            s_tokens = set(tokenize(supplier_title))
            a_tokens = set(tokenize(amazon_title))
            jacc = (len(s_tokens & a_tokens) / max(1, len(s_tokens | a_tokens))) if (s_tokens and a_tokens) else 0.0
            score = 40 * tm + 25 * jacc + (20 if brand_match else 0) + (10 if len(anchors) >= 3 else 0) - (10 if assorted else 0)
            conf = int(max(0, min(94, round(score))))

        profitable = net_profit > 0 and adj_profit > 0
        sellable = sales > 0

        if exact:
            if rsu is None:
                needs_ver.append(
                    mk_row(
                        verdict="NEEDS VERIFICATION",
                        confidence=max(80, conf),
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=sup_ean,
                        amazon_ean=amz_ean,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_v,
                        adjusted_profit=adj_profit,
                        evidence=evidence,
                        filter_reason="Exact EAN match but explicit pack contradiction; confirm pack count",
                    )
                )
            elif not profitable:
                verified_filt.append(
                    mk_row(
                        verdict="FILTERED OUT",
                        confidence=conf,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=sup_ean,
                        amazon_ean=amz_ean,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_v,
                        adjusted_profit=adj_profit,
                        evidence=evidence,
                        filter_reason="Adjusted profit ≤ 0 after pack sanity",
                    )
                )
            elif not sellable:
                needs_ver.append(
                    mk_row(
                        verdict="NEEDS VERIFICATION",
                        confidence=conf,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=sup_ean,
                        amazon_ean=amz_ean,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_v,
                        adjusted_profit=adj_profit,
                        evidence=evidence,
                        filter_reason="Sales=0; exact EAN match but demand unclear",
                    )
                )
            else:
                verified_rec.append(
                    mk_row(
                        verdict="VERIFIED",
                        confidence=conf,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=sup_ean,
                        amazon_ean=amz_ean,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=(pack_v + ("; " + cap_reason if cap_reason else "")),
                        adjusted_profit=adj_profit,
                        evidence=evidence,
                        filter_reason="-",
                    )
                )
            continue

        strong = brand_match and tm >= 0.62 and len(anchors) >= 3
        plausible = tm >= 0.52 and len(anchors) >= 2 and (brand_match or len(anchors) >= 4)

        if strong:
            if cap_reason.startswith("Different capacity"):
                hl_filt.append(
                    mk_row(
                        verdict="FILTERED OUT",
                        confidence=conf,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=sup_ean,
                        amazon_ean=amz_ean,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_v,
                        adjusted_profit=adj_profit,
                        evidence=evidence,
                        filter_reason=cap_reason,
                    )
                )
            elif rsu is not None and adj_profit <= 0:
                hl_filt.append(
                    mk_row(
                        verdict="FILTERED OUT",
                        confidence=conf,
                        supplier_title=supplier_title,
                        amazon_title=amazon_title,
                        supplier_ean=sup_ean,
                        amazon_ean=amz_ean,
                        asin=asin,
                        supplier_price=supplier_price,
                        selling_price=selling_price,
                        net_profit=net_profit,
                        roi=roi,
                        sales=sales,
                        pack_verdict=pack_v,
                        adjusted_profit=adj_profit,
                        evidence=evidence,
                        filter_reason=(f"Requires {rsu} units; adjusted profit is negative" if rsu and rsu > 1 else "Adjusted profit ≤ 0"),
                    )
                )
            elif rsu is None:
                if net_profit > 0.50 and roi >= 15:
                    needs_ver.append(
                        mk_row(
                            verdict="NEEDS VERIFICATION",
                            confidence=max(70, conf),
                            supplier_title=supplier_title,
                            amazon_title=amazon_title,
                            supplier_ean=sup_ean,
                            amazon_ean=amz_ean,
                            asin=asin,
                            supplier_price=supplier_price,
                            selling_price=selling_price,
                            net_profit=net_profit,
                            roi=roi,
                            sales=sales,
                            pack_verdict=pack_v,
                            adjusted_profit=adj_profit,
                            evidence=evidence,
                            filter_reason="Confirm pack size interpretation",
                        )
                    )
            elif cap_reason and not cap_reason.startswith("Different capacity"):
                if net_profit > 0.50 and roi >= 15:
                    needs_ver.append(
                        mk_row(
                            verdict="NEEDS VERIFICATION",
                            confidence=max(65, conf),
                            supplier_title=supplier_title,
                            amazon_title=amazon_title,
                            supplier_ean=sup_ean,
                            amazon_ean=amz_ean,
                            asin=asin,
                            supplier_price=supplier_price,
                            selling_price=selling_price,
                            net_profit=net_profit,
                            roi=roi,
                            sales=sales,
                            pack_verdict=pack_v,
                            adjusted_profit=adj_profit,
                            evidence=evidence,
                            filter_reason=cap_reason,
                        )
                    )
            elif assorted:
                if net_profit > 0.50 and roi >= 15:
                    needs_ver.append(
                        mk_row(
                            verdict="NEEDS VERIFICATION",
                            confidence=max(65, conf),
                            supplier_title=supplier_title,
                            amazon_title=amazon_title,
                            supplier_ean=sup_ean,
                            amazon_ean=amz_ean,
                            asin=asin,
                            supplier_price=supplier_price,
                            selling_price=selling_price,
                            net_profit=net_profit,
                            roi=roi,
                            sales=sales,
                            pack_verdict=pack_v,
                            adjusted_profit=adj_profit,
                            evidence=evidence,
                            filter_reason="Contains 'assorted'; confirm exact variant",
                        )
                    )
            else:
                if profitable and sellable:
                    fr = "-" if not ip else f"IP risk check: '{ip}' (verify restrictions)"
                    hl_rec.append(
                        mk_row(
                            verdict="HIGHLY LIKELY",
                            confidence=conf,
                            supplier_title=supplier_title,
                            amazon_title=amazon_title,
                            supplier_ean=sup_ean,
                            amazon_ean=amz_ean,
                            asin=asin,
                            supplier_price=supplier_price,
                            selling_price=selling_price,
                            net_profit=net_profit,
                            roi=roi,
                            sales=sales,
                            pack_verdict=pack_v,
                            adjusted_profit=adj_profit,
                            evidence=evidence,
                            filter_reason=fr,
                        )
                    )
                else:
                    hl_filt.append(
                        mk_row(
                            verdict="FILTERED OUT",
                            confidence=conf,
                            supplier_title=supplier_title,
                            amazon_title=amazon_title,
                            supplier_ean=sup_ean,
                            amazon_ean=amz_ean,
                            asin=asin,
                            supplier_price=supplier_price,
                            selling_price=selling_price,
                            net_profit=net_profit,
                            roi=roi,
                            sales=sales,
                            pack_verdict=pack_v,
                            adjusted_profit=adj_profit,
                            evidence=evidence,
                            filter_reason="Sales=0 or profit≤0 after pack sanity",
                        )
                    )
            continue

        if plausible:
            if net_profit <= 0.50 or roi < 15:
                continue
            if rsu is not None and adj_profit <= 0:
                continue
            reason = "Confirm 1 detail to upgrade"
            if not brand_match:
                reason = "Brand not explicit in Amazon title; confirm packaging/brand"
            elif rsu is None:
                reason = "Confirm pack size interpretation"
            elif cap_reason:
                reason = cap_reason
            elif assorted:
                reason = "Contains 'assorted'; confirm exact variant"

            needs_ver.append(
                mk_row(
                    verdict="NEEDS VERIFICATION",
                    confidence=conf,
                    supplier_title=supplier_title,
                    amazon_title=amazon_title,
                    supplier_ean=sup_ean,
                    amazon_ean=amz_ean,
                    asin=asin,
                    supplier_price=supplier_price,
                    selling_price=selling_price,
                    net_profit=net_profit,
                    roi=roi,
                    sales=sales,
                    pack_verdict=pack_v,
                    adjusted_profit=adj_profit,
                    evidence=evidence,
                    filter_reason=reason,
                )
            )

    verified_rec.sort(key=lambda x: int(x["Sales"].replace(",", "")), reverse=True)
    verified_filt.sort(key=lambda x: int(x["Sales"].replace(",", "")), reverse=True)
    hl_rec.sort(key=lambda x: (int(x["Confidence"]), int(x["Sales"].replace(",", ""))), reverse=True)
    hl_filt.sort(key=lambda x: (int(x["Confidence"]), int(x["Sales"].replace(",", ""))), reverse=True)
    needs_ver.sort(key=lambda x: (int(x["Confidence"]), int(x["Sales"].replace(",", ""))), reverse=True)

    now_dubai = datetime.now(timezone(timedelta(hours=4)))
    date_str = now_dubai.strftime("%Y-%m-%d")
    fname = f"PHASEA_MANUAL_REPORT_{now_dubai.strftime('%Y%m%d')}.md"
    out_path = out_dir / fname

    total_categorized = len(verified_rec) + len(verified_filt) + len(hl_rec) + len(hl_filt) + len(needs_ver)

    md = []
    md.append("# PHASEA MANUAL REPORT")
    md.append("")
    md.append(f"**Generated:** {date_str}")
    md.append(f"**Input File:** {input_path}")
    md.append(f"**Supplier:** {supplier_name}")
    md.append("")

    md.append("## Summary Counts")
    md.append(f"- VERIFIED — RECOMMENDED: {len(verified_rec)}")
    md.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(verified_filt)}")
    md.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(hl_rec)}")
    md.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(hl_filt)}")
    md.append(f"- NEEDS VERIFICATION: {len(needs_ver)}")
    md.append(f"- TOTAL ANALYZED: {total_categorized}")
    md.append("")

    md.append("This report applies v4.0 Thorough Manual Analysis:")
    md.append("- VERIFIED uses strict-valid exact EAN (checksum + left-padding) and avoids dimension traps.")
    md.append("- HIGHLY LIKELY requires shared brand/product anchors; pack sanity must keep profit positive.")
    md.append("- NEEDS VERIFICATION is selective (1–2 specific checks would upgrade confidence).")
    md.append("")

    md.append(f"## VERIFIED — RECOMMENDED (count={len(verified_rec)})")
    md.append("```text")
    md.append(build_fixed_width_table(verified_rec))
    md.append("```")
    md.append("")

    md.append(f"## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_filt)})")
    md.append("```text")
    md.append(build_fixed_width_table(verified_filt))
    md.append("```")
    md.append("")

    md.append(f"## HIGHLY LIKELY — RECOMMENDED (count={len(hl_rec)})")
    md.append("```text")
    md.append(build_fixed_width_table(hl_rec))
    md.append("```")
    md.append("")

    md.append(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(hl_filt)})")
    md.append("```text")
    md.append(build_fixed_width_table(hl_filt))
    md.append("```")
    md.append("")

    md.append(f"## NEEDS VERIFICATION (count={len(needs_ver)})")
    md.append("```text")
    md.append(build_fixed_width_table(needs_ver))
    md.append("```")
    md.append("")

    md.append("## Reconciliation")
    md.append(f"- Total rows in input: {len(df)}")
    md.append(f"- Rows analyzed and categorized: {total_categorized}")

    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote: {out_path}")

    # Hard gates for recommended tables
    for row in verified_rec:
        assert row["Sales"] != "0"
        assert row["Supplier EAN"] != "-" and row["Amazon EAN"] != "-" and row["Supplier EAN"] == row["Amazon EAN"]
        assert float(row["Adjusted Profit"].replace("£", "").replace(",", "")) > 0

    for row in hl_rec:
        assert row["Sales"] != "0"
        assert float(row["Adjusted Profit"].replace("£", "").replace(",", "")) > 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
