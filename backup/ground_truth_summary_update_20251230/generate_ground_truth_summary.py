from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


BASE_PATH = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - "
    r"POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec"
)

SOURCE_XLSX = BASE_PATH / "part_30_dec.xlsx"
COMPREHENSIVE_REPORT = BASE_PATH / "COMPREHENSIVE_VALIDATION_REPORT_20251230.md"
OUTPUT_MD = BASE_PATH / "GROUND_TRUTH_SUMMARY_20251230.md"


KNOWN_BRANDS = [
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
    "DENBY",
    "HEAT HOLDERS",
    "KENWOOD",
    "SWAN",
    "TOWER",
    "MORPHY RICHARDS",
    "TEFAL",
    "SABICHI",
    "DUNLOP",
    "JML",
    "BELDRAY",
    "PROGRESS",
    "SALTER",
    "PRESTIGE",
    "STELLAR",
    "JUDGE",
]

VARIANT_SCENTS = {"EUCALYPTUS", "LEMON", "LIME", "LAVENDER", "VANILLA", "ORANGE", "FRESH", "CITRUS"}
VARIANT_COLORS = {"BLACK", "WHITE", "GREY", "GRAY", "NAVY", "CREAM", "RED", "BLUE", "GREEN", "PINK", "BROWN"}
VARIANT_SIZES = {"SMALL", "MEDIUM", "LARGE", "XL", "MINI"}

DIMENSION_UNITS = {"CM", "MM", "IN", "INCH", "M"}


@dataclass(frozen=True)
class ScoredRow:
    row_id: int
    category: str  # VERIFIED / HIGHLY LIKELY / NEEDS VERIFICATION / OTHER
    score: int
    supplier_title: str
    amazon_title: str
    supplier_ean: str
    amazon_ean: str
    asin: str
    supplier_price: float
    selling_price: float
    net_profit: float
    roi: float
    sales: float
    pack_verdict: str
    adjusted_profit: float
    key_evidence: str
    filter_reason: str


def norm_digits(value: object) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    s = re.sub(r"\.0$", "", s)
    return re.sub(r"[^0-9]", "", s)


def title_norm(s: str) -> str:
    s = (s or "").upper()
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_similarity_pct(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, title_norm(a), title_norm(b)).ratio() * 100.0


def detect_brand(title: str) -> str:
    t = " " + title_norm(title) + " "
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        b = " " + title_norm(brand) + " "
        if b in t:
            return brand
    return ""


def tokenize(title: str) -> list[str]:
    return [tok for tok in title_norm(title).split(" ") if tok]


def variant_mismatch(sup_title: str, amz_title: str) -> tuple[bool, str]:
    sup = set(tokenize(sup_title))
    amz = set(tokenize(amz_title))

    sup_sc = VARIANT_SCENTS & sup
    amz_sc = VARIANT_SCENTS & amz
    if sup_sc and amz_sc and sup_sc != amz_sc:
        return True, f"Scent {sorted(sup_sc)} vs {sorted(amz_sc)}"

    sup_co = VARIANT_COLORS & sup
    amz_co = VARIANT_COLORS & amz
    if sup_co and amz_co and sup_co != amz_co:
        return True, f"Color {sorted(sup_co)} vs {sorted(amz_co)}"

    sup_sz = VARIANT_SIZES & sup
    amz_sz = VARIANT_SIZES & amz
    if sup_sz and amz_sz and sup_sz != amz_sz:
        return True, f"Size {sorted(sup_sz)} vs {sorted(amz_sz)}"

    return False, ""


def looks_like_dimension_near(title_upper: str, start: int, end: int) -> bool:
    window = title_upper[max(0, start - 8) : min(len(title_upper), end + 8)]
    return any(u in window for u in DIMENSION_UNITS)


def extract_pack_count(title: str) -> tuple[int, str]:
    t = title_norm(title)
    if not t:
        return 1, "implicit"

    patterns: list[tuple[str, str]] = [
        (r"\bPACK OF (\d+)\b", "PACK OF N"),
        (r"\b(\d+)\s*PACK\b", "N PACK"),
        (r"\b(\d+)\s*(PCS|PC|PIECES|PCE)\b", "N PCS"),
        (r"\bSET OF (\d+)\b", "SET OF N"),
        (r"\bPK\s*(\d+)\b", "PKN"),
        (r"^\s*(\d+)\s*X\s+[A-Z]", "N x <word>"),
        (r"\b(\d+)\s*X\s*(\d+)\b", "N x M"),
    ]

    for pat, reason in patterns:
        for m in re.finditer(pat, t):
            if reason == "N x M":
                if looks_like_dimension_near(t, m.start(), m.end()):
                    continue
                a = int(m.group(1))
                b = int(m.group(2))
                val = a * b
                if 2 <= val <= 500:
                    return val, reason
            else:
                val = int(m.group(1))
                if 2 <= val <= 500:
                    if looks_like_dimension_near(t, m.start(), m.end()):
                        continue
                    return val, reason

    if "TWINPACK" in t or "TWIN PACK" in t:
        return 2, "TWINPACK"

    return 1, "implicit"


def product_type_match(sup_title: str, amz_title: str) -> bool:
    sup = set(tokenize(sup_title))
    amz = set(tokenize(amz_title))

    # Remove pure numbers and obvious units.
    def filt(tokens: set[str]) -> set[str]:
        out = set()
        for tok in tokens:
            if tok.isdigit():
                continue
            if tok in {"CM", "MM", "ML", "L", "G", "KG", "IN", "INCH", "M"}:
                continue
            out.add(tok)
        return out

    sup = filt(sup)
    amz = filt(amz)
    inter = sup & amz
    return len(inter) >= 2


def compute_score(
    ean_exact: bool,
    ean_mismatch: bool,
    brand_match: bool,
    prod_match: bool,
    sim_pct: float,
    variant_bad: bool,
) -> int:
    score = int(round(sim_pct))
    if brand_match:
        score += 10
    if prod_match:
        score += 10
    if ean_mismatch:
        score -= 20
    if variant_bad:
        score -= 25
    if ean_exact:
        score = max(score, 95)
    if score < 0:
        score = 0
    if score > 99:
        score = 99
    return score


def classify_row(
    sup_title: str,
    amz_title: str,
    sup_ean: str,
    amz_ean: str,
    sup_price: float,
    net_profit: float,
    roi: float,
) -> tuple[str, int, str, str, float, str]:
    brand_sup = detect_brand(sup_title)
    brand_amz = detect_brand(amz_title)
    brand_match = bool(brand_sup) and brand_sup == brand_amz
    sim = title_similarity_pct(sup_title, amz_title)
    prod_match = product_type_match(sup_title, amz_title)

    var_bad, var_reason = variant_mismatch(sup_title, amz_title)

    sup_pack, _ = extract_pack_count(sup_title)
    amz_pack, _ = extract_pack_count(amz_title)
    pack_ratio = amz_pack / sup_pack if sup_pack else 1.0
    adjusted_profit = float(net_profit) - (pack_ratio - 1) * float(sup_price)

    ean_exact = bool(sup_ean) and bool(amz_ean) and sup_ean == amz_ean
    ean_mismatch = bool(sup_ean) and bool(amz_ean) and sup_ean != amz_ean

    score = compute_score(ean_exact, ean_mismatch, brand_match, prod_match, sim, var_bad)

    if net_profit <= 0:
        return "OTHER / LOW PRIORITY", score, "NetProfit<=0", f"ratio={pack_ratio:.2f}", adjusted_profit, var_reason

    # VERIFIED
    if ean_exact and (pack_ratio == 1.0 or adjusted_profit > 0) and not var_bad:
        return "VERIFIED", score, "Exact EAN match", f"1:{int(pack_ratio)}" if pack_ratio != 1 else "1:1", adjusted_profit, var_reason

    # HIGHLY LIKELY
    if brand_match and prod_match and sim >= 55.0 and (pack_ratio == 1.0 or adjusted_profit > 0) and not var_bad:
        return "HIGHLY LIKELY", score, f"Brand match ({brand_sup}) + type match", f"1:{int(pack_ratio)}" if pack_ratio != 1 else "1:1", adjusted_profit, var_reason

    # NEEDS VERIFICATION (baseline)
    partial = brand_match or sim >= 55.0 or prod_match
    if partial and adjusted_profit > 0.50 and roi > 15 and not var_bad:
        return "NEEDS VERIFICATION", score, "Partial evidence; needs 1-2 confirmations", f"1:{int(pack_ratio)}" if pack_ratio != 1 else "1:1", adjusted_profit, var_reason

    return "OTHER / LOW PRIORITY", score, "Weak match evidence", f"1:{int(pack_ratio)}" if pack_ratio != 1 else "1:1", adjusted_profit, var_reason


def parse_referenced_row_ids(report_text: str) -> set[int]:
    """
    Extract Row IDs from the comprehensive validation report's tables.
    We look for table rows that begin with `| <digits> |` (first column is Row ID).
    """
    row_ids: set[int] = set()
    for line in report_text.splitlines():
        m = re.match(r"^\|\s*(\d{1,5})\s*\|", line)
        if not m:
            continue
        row_ids.add(int(m.group(1)))
    return row_ids


def fmt_money(val: float) -> str:
    return f"£{val:.2f}"


def fmt_pct(val: float) -> str:
    return f"{val:.1f}%"


def truncate(s: str, max_len: int) -> str:
    s = (s or "").replace("\n", " ").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3].rstrip() + "..."


def fixed_width_table(rows: list[dict[str, str]], columns: list[str], max_widths: dict[str, int]) -> str:
    """
    Returns a fixed-width, space-padded markdown table as plain text.
    Pipes align vertically. No tabs.
    """
    prepared: list[dict[str, str]] = []
    for r in rows:
        pr = {}
        for c in columns:
            cell = str(r.get(c, "") or "")
            cell = cell.replace("\t", " ")
            cell = cell.replace("\n", " ")
            cell = truncate(cell, max_widths.get(c, 80))
            pr[c] = cell
        prepared.append(pr)

    widths: dict[str, int] = {}
    for c in columns:
        widths[c] = max(len(c), *(len(r[c]) for r in prepared)) if prepared else len(c)

    def _row(values: list[str]) -> str:
        parts = []
        for c, v in zip(columns, values, strict=True):
            parts.append(" " + v.ljust(widths[c]) + " ")
        return "|" + "|".join(parts) + "|"

    header = _row(columns)
    sep = "|" + "|".join("-" * (widths[c] + 2) for c in columns) + "|"
    body = "\n".join(_row([r[c] for c in columns]) for r in prepared)
    return "\n".join([header, sep, body]) if body else "\n".join([header, sep])


def build_scored_rows(df: pd.DataFrame, row_ids: set[int]) -> list[ScoredRow]:
    out: list[ScoredRow] = []
    for row_id in sorted(row_ids):
        if row_id < 1 or row_id > len(df):
            continue
        row = df.iloc[row_id - 1]

        sup_title = str(row.get("SupplierTitle", "") or "")
        amz_title = str(row.get("AmazonTitle", "") or "")
        sup_ean = norm_digits(row.get("EAN", ""))
        amz_ean = norm_digits(row.get("EAN_OnPage", ""))
        asin = str(row.get("ASIN", "") or "")
        sup_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
        sell_price = float(row.get("SellingPrice_incVAT", 0) or 0)
        net_profit = float(row.get("NetProfit", 0) or 0)
        roi = float(row.get("ROI", 0) or 0)
        sales = float(row.get("bought_in_past_month", 0) or 0)

        cat, score, reason, pack_short, adj_profit, var_reason = classify_row(
            sup_title, amz_title, sup_ean, amz_ean, sup_price, net_profit, roi
        )

        sup_pack, _ = extract_pack_count(sup_title)
        amz_pack, _ = extract_pack_count(amz_title)
        if sup_pack == amz_pack:
            pack_verdict = "1:1"
        elif amz_pack > sup_pack:
            pack_verdict = f"BUNDLE (amz/sup={amz_pack}/{sup_pack})"
        else:
            pack_verdict = f"SPLIT (amz/sup={amz_pack}/{sup_pack})"

        evidence_bits = [
            f"RowID={row_id}",
            f"Sim={title_similarity_pct(sup_title, amz_title):.0f}%",
        ]
        b = detect_brand(sup_title)
        if b and b == detect_brand(amz_title):
            evidence_bits.append(f"Brand={b}")
        if product_type_match(sup_title, amz_title):
            evidence_bits.append("TypeMatch=Y")
        if sup_ean and amz_ean:
            evidence_bits.append("EAN=Exact" if sup_ean == amz_ean else "EAN=Mismatch")
        elif sup_ean or amz_ean:
            evidence_bits.append("EAN=Incomplete")
        if var_reason:
            evidence_bits.append(f"Variant={var_reason}")

        key_evidence = "; ".join(evidence_bits)

        filter_reason = "-"
        if cat == "NEEDS VERIFICATION":
            # What is missing?
            if not (sup_ean and amz_ean):
                filter_reason = "EAN missing/incomplete"
            elif sup_ean != amz_ean:
                filter_reason = "EAN mismatch (verify listing)"
            elif pack_verdict != "1:1":
                filter_reason = "Confirm pack interpretation"
            else:
                filter_reason = "Confirm 1-2 minor details"

        out.append(
            ScoredRow(
                row_id=row_id,
                category=cat,
                score=score,
                supplier_title=sup_title,
                amazon_title=amz_title,
                supplier_ean=sup_ean or "-",
                amazon_ean=amz_ean or "-",
                asin=asin,
                supplier_price=sup_price,
                selling_price=sell_price,
                net_profit=net_profit,
                roi=roi,
                sales=sales,
                pack_verdict=pack_verdict,
                adjusted_profit=adj_profit,
                key_evidence=key_evidence,
                filter_reason=filter_reason,
            )
        )
    return out


def to_table_rows(items: list[ScoredRow], verdict_override: str | None = None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for it in items:
        verdict = verdict_override or it.category
        out.append(
            {
                "Verdict": verdict,
                "Confidence": str(it.score),
                "SupplierTitle": it.supplier_title,
                "AmazonTitle": it.amazon_title,
                "Supplier EAN": it.supplier_ean,
                "Amazon EAN": it.amazon_ean,
                "ASIN": it.asin,
                "SupplierPrice": fmt_money(it.supplier_price),
                "SellingPrice": fmt_money(it.selling_price),
                "NetProfit": fmt_money(it.net_profit),
                "ROI": fmt_pct(it.roi),
                "Sales": str(int(it.sales)) if it.sales == int(it.sales) else f"{it.sales:.0f}",
                "Pack Verdict": it.pack_verdict,
                "Adjusted Profit": fmt_money(it.adjusted_profit),
                "Key Match Evidence": it.key_evidence,
                "Filter Reason": it.filter_reason,
            }
        )
    return out


def main() -> None:
    if not SOURCE_XLSX.exists():
        raise SystemExit(f"Missing: {SOURCE_XLSX}")
    if not COMPREHENSIVE_REPORT.exists():
        raise SystemExit(f"Missing: {COMPREHENSIVE_REPORT}")

    df = pd.read_excel(SOURCE_XLSX)

    report_text = COMPREHENSIVE_REPORT.read_text(encoding="utf-8", errors="replace")
    referenced = parse_referenced_row_ids(report_text)

    scored = build_scored_rows(df, referenced)

    # Unique products referenced across all reports (dedupe by RowID).
    # `scored` already unique by RowID due to set.
    verified = [s for s in scored if s.category == "VERIFIED"]
    highly = [s for s in scored if s.category == "HIGHLY LIKELY"]
    needs = [s for s in scored if s.category == "NEEDS VERIFICATION"]

    # Rank by score for HL and NV (and VERIFIED too for consistency).
    verified.sort(key=lambda x: x.score, reverse=True)
    highly.sort(key=lambda x: x.score, reverse=True)
    needs.sort(key=lambda x: x.score, reverse=True)

    # Prune "very unlikely" NEEDS VERIFICATION:
    # keep only stronger candidates (stricter than the prompt baseline).
    pruned_needs = [
        s
        for s in needs
        if (s.score >= 65)
        and (s.net_profit > 0.50)
        and (s.roi > 15)
        and (s.adjusted_profit > 0.50)
    ]

    # Missed by all reports:
    # Evaluate all dataset rows and select those not referenced.
    missed_verified: list[ScoredRow] = []
    missed_strict_hl: list[ScoredRow] = []

    for rid in range(1, len(df) + 1):
        if rid in referenced:
            continue
        row = df.iloc[rid - 1]
        sup_title = str(row.get("SupplierTitle", "") or "")
        amz_title = str(row.get("AmazonTitle", "") or "")
        sup_ean = norm_digits(row.get("EAN", ""))
        amz_ean = norm_digits(row.get("EAN_OnPage", ""))
        asin = str(row.get("ASIN", "") or "")
        sup_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
        sell_price = float(row.get("SellingPrice_incVAT", 0) or 0)
        net_profit = float(row.get("NetProfit", 0) or 0)
        roi = float(row.get("ROI", 0) or 0)
        sales = float(row.get("bought_in_past_month", 0) or 0)

        cat, score, _, _, adj_profit, _ = classify_row(sup_title, amz_title, sup_ean, amz_ean, sup_price, net_profit, roi)

        sup_pack, _ = extract_pack_count(sup_title)
        amz_pack, _ = extract_pack_count(amz_title)
        if sup_pack == amz_pack:
            pack_verdict = "1:1"
        elif amz_pack > sup_pack:
            pack_verdict = f"BUNDLE (amz/sup={amz_pack}/{sup_pack})"
        else:
            pack_verdict = f"SPLIT (amz/sup={amz_pack}/{sup_pack})"

        item = ScoredRow(
            row_id=rid,
            category=cat,
            score=score,
            supplier_title=sup_title,
            amazon_title=amz_title,
            supplier_ean=sup_ean or "-",
            amazon_ean=amz_ean or "-",
            asin=asin,
            supplier_price=sup_price,
            selling_price=sell_price,
            net_profit=net_profit,
            roi=roi,
            sales=sales,
            pack_verdict=pack_verdict,
            adjusted_profit=adj_profit,
            key_evidence=f"RowID={rid}; Sim={title_similarity_pct(sup_title, amz_title):.0f}%",
            filter_reason="Missed by all reports",
        )

        if cat == "VERIFIED" and sales > 0:
            missed_verified.append(item)
        else:
            # Strict "missed highly likely": stricter than report HL.
            brand_sup = detect_brand(sup_title)
            brand_amz = detect_brand(amz_title)
            brand_match = bool(brand_sup) and brand_sup == brand_amz
            sim = title_similarity_pct(sup_title, amz_title)
            prod_match = product_type_match(sup_title, amz_title)
            var_bad, _ = variant_mismatch(sup_title, amz_title)
            ean_exact = bool(sup_ean) and bool(amz_ean) and sup_ean == amz_ean

            if (
                (not ean_exact)
                and (sales > 0)
                and (net_profit > 0)
                and (adj_profit > 0)
                and brand_match
                and prod_match
                and (sim >= 70.0)
                and (not var_bad)
                and (roi >= 20.0)
            ):
                missed_strict_hl.append(item.__class__(**{**item.__dict__, "category": "HIGHLY LIKELY"}))

    missed_verified.sort(key=lambda x: x.score, reverse=True)
    missed_strict_hl.sort(key=lambda x: x.score, reverse=True)

    columns = [
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
        "Verdict": 14,
        "Confidence": 10,
        "SupplierTitle": 60,
        "AmazonTitle": 70,
        "Supplier EAN": 14,
        "Amazon EAN": 14,
        "ASIN": 10,
        "SupplierPrice": 12,
        "SellingPrice": 12,
        "NetProfit": 12,
        "ROI": 10,
        "Sales": 8,
        "Pack Verdict": 26,
        "Adjusted Profit": 14,
        "Key Match Evidence": 70,
        "Filter Reason": 50,
    }

    out_lines: list[str] = []
    out_lines.append("# GROUND TRUTH SUMMARY (UNIQUE PRODUCTS)")
    out_lines.append("")
    out_lines.append(f"**Source Dataset:** `{SOURCE_XLSX}` ({len(df)} rows)")
    out_lines.append(f"**Referenced RowIDs (unique across all reports):** {len(referenced)}")
    out_lines.append(f"**Source of references:** `{COMPREHENSIVE_REPORT}`")
    out_lines.append("")

    out_lines.append("## Your Ground Truth Classification (Unique Products referenced across all reports)")
    out_lines.append("")

    out_lines.append(f"### VERIFIED (n={len(verified)})")
    out_lines.append("```text")
    out_lines.append(fixed_width_table(to_table_rows(verified), columns, max_widths))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append(f"### HIGHLY LIKELY (n={len(highly)})")
    out_lines.append("```text")
    out_lines.append(fixed_width_table(to_table_rows(highly), columns, max_widths))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append(f"### NEEDS VERIFICATION (PRUNED, n={len(pruned_needs)})")
    out_lines.append("```text")
    out_lines.append(fixed_width_table(to_table_rows(pruned_needs), columns, max_widths))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append("## Missed By All Reports (Not referenced in any model output)")
    out_lines.append("")

    out_lines.append(f"### MISSED VERIFIED (n={len(missed_verified)})")
    out_lines.append("```text")
    out_lines.append(fixed_width_table(to_table_rows(missed_verified), columns, max_widths))
    out_lines.append("```")
    out_lines.append("")

    out_lines.append(f"### MISSED HIGHLY LIKELY (STRICT, n={len(missed_strict_hl)})")
    out_lines.append("```text")
    out_lines.append(fixed_width_table(to_table_rows(missed_strict_hl), columns, max_widths))
    out_lines.append("```")
    out_lines.append("")

    OUTPUT_MD.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Wrote: {OUTPUT_MD}")


if __name__ == "__main__":
    main()

