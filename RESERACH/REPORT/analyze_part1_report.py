from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


TZ = ZoneInfo("Asia/Dubai")


INVALID_EAN = {"", "-", "nan", "none", "null", "0", "0.0", "na", "n/a"}


def clean_ean(value: object) -> str:
    if pd.isna(value):
        return "-"
    text = str(value).strip()
    if text.lower() in INVALID_EAN:
        return "-"
    if re.fullmatch(r"\d+(?:\.\d+)?e\+\d+", text, flags=re.I):
        try:
            text = str(int(round(float(text))))
        except Exception:
            return "-"
    if text.endswith(".0"):
        text = text[:-2]
    text = re.sub(r"\s+", "", text)
    digits = re.sub(r"\D", "", text)
    if digits == "" or digits.lower() in INVALID_EAN:
        return "-"
    if not (8 <= len(digits) <= 14):
        return "-"
    return digits


def parse_sales(value: object) -> float:
    if pd.isna(value):
        return 0.0
    match = re.search(r"(\d+)", str(value))
    return float(match.group(1)) if match else 0.0


def title_similarity(title1: object, title2: object) -> float:
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()


def extract_quantity_baseline(title: object) -> float:
    if pd.isna(title):
        return 1.0
    text = str(title).lower()

    patterns = [
        r"pack of (\d+)",
        r"set of (\d+)",
        r"\b(\d+)\s*pack\b",
        r"\b(\d+)\s*pk\b",
        r"(\d+)\s*pcs\b",
        r"(\d+)\s*pieces?\b",
        r"(\d+)\s*pairs?\b",
        r"\bx\s*(\d+)\b",
        r"\((\d+)\s*pack\)",
        r"\(pack of (\d+)\)",
        r"\b(\d+)\s*rolls?\b",
        r"\b(\d+)\s*piece\b",
    ]

    for pat in patterns:
        match = re.search(pat, text)
        if not match:
            continue
        try:
            qty = float(match.group(1))
        except Exception:
            continue
        if 1 < qty < 500:
            return qty
    return 1.0


def recalculate_profit(net_profit: float, supplier_cost: float, qty_ratio: float) -> float:
    return net_profit - supplier_cost * (qty_ratio - 1)


def categorize(is_exact_ean: bool, title_match: float) -> str:
    if is_exact_ean:
        return "EXACT_EAN_MATCH"
    if title_match >= 0.50:
        return "HIGH_LIKELIHOOD"
    if title_match >= 0.30:
        return "MODERATE_CONFIDENCE"
    return "UNCERTAIN"


def pack_verdict_baseline(qty_ratio: float, adjusted_profit: float) -> str:
    if qty_ratio == 1.0:
        return "1:1 Match"
    if qty_ratio > 1.0:
        return f"BUNDLE ({int(round(qty_ratio))}x) - {'OK' if adjusted_profit > 0 else 'LOSS'}"
    inv = 1.0 / qty_ratio if qty_ratio else 0.0
    return f"SPLIT (1/{int(round(inv))}) - {'OK' if adjusted_profit > 0 else 'LOSS'}"


IP_RISK_PATTERNS = [
    r"\bchanel\b",
    r"\bdior\b",
    r"\bjo\s+malone\b",
    r"\btom\s+ford\b",
    r"\bcreed\b",
    r"\brolex\b",
    r"\blouis\s+vuitton\b",
    r"\bgucci\b",
    r"\bprada\b",
    r"\bherm[eè]s\b",
    r"\bcartier\b",
    r"\byves\s+saint\s+laurent\b",
    r"\bysl\b",
    r"\bgivenchy\b",
    r"\bversace\b",
    r"\bdolce\b",
    r"\bgabbana\b",
]


def is_ip_risk_text(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).lower()
    return any(re.search(pat, text) for pat in IP_RISK_PATTERNS)


def normalize_title(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def strip_dimensions(text: str) -> str:
    # 30cm x 36cm, 9x9in, 24mmx50m, 4ft, 36w, etc.
    text = re.sub(r"\b\d+(?:\.\d+)?\s*(?:cm|mm|ml|l|litre|litres|g|kg|oz|w|wh|inch|in|ft|m)\b", " ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\s*x\s*\d+(?:\.\d+)?\s*(?:cm|mm|inch|in|ft|m)\b", " ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?x\d+(?:\.\d+)?\s*(?:cm|mm|inch|in|ft|m)\b", " ", text)
    text = re.sub(r"\b\d+mm\s*x\s*\d+m\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True)
class PackParse:
    count: int | None
    evidence: list[str]


def extract_pack_count(title: object) -> PackParse:
    raw = normalize_title(title)
    if not raw:
        return PackParse(count=None, evidence=[])

    text = strip_dimensions(raw)
    evidence: list[str] = []
    counts: list[int] = []

    for pat in [
        r"pack of\s*(\d+)",
        r"set of\s*(\d+)",
        r"\b(\d+)\s*pack\b",
        r"\b(\d+)\s*pk\b",
        r"\b(\d+)\s*(?:pcs|pce|pieces?)\b",
        r"\b(\d+)\s*(?:bags?|liners?|tealights?|candles|containers?|trays?|cases?|doyleys?|doileys?|glasses?|cups?|rolls?)\b",
    ]:
        for match in re.finditer(pat, text, flags=re.I):
            n = int(match.group(1))
            if 1 < n < 500:
                counts.append(n)
                evidence.append(match.group(0))

    for match in re.finditer(r"\b(\d+)\s*x\s*(\d+)\b", text, flags=re.I):
        a, b = int(match.group(1)), int(match.group(2))
        prod = a * b
        if 1 < prod < 500:
            counts.append(prod)
            evidence.append(match.group(0))

    for match in re.finditer(r"\b(\d+)\s*x(?!\s*\d)", text, flags=re.I):
        n = int(match.group(1))
        if 1 < n < 500:
            counts.append(n)
            evidence.append(match.group(0).strip())

    # Conservative heuristic: first standalone number + plural count noun somewhere
    match = re.search(r"\b(\d+)\b", text)
    if match:
        n = int(match.group(1))
        if 1 < n < 500 and not re.search(r"\b\d+\s*way\b", text):
            if re.search(r"\b(bags|liners|tealights|candles|containers|trays|cases|doyleys|doileys|glasses|cups|rolls)\b", text):
                counts.append(n)
                evidence.append(f"first number: {n}")

    if not counts:
        return PackParse(count=None, evidence=[])
    return PackParse(count=max(counts), evidence=sorted(set(evidence)))


def extract_size_tokens(title: object) -> list[str]:
    text = normalize_title(title)
    if not text:
        return []

    out: set[str] = set()
    for match in re.finditer(r"\b(\d+(?:\.\d+)?)\s*(ml|l|litre|litres|g|kg|cm|mm|inch|in|ft|m|w)\b", text):
        unit = match.group(2)
        # Heuristic: strings like "150m(6\")" in supplier titles typically mean 150mm (6 inch),
        # not 150 metres. Avoid false variant mismatches by skipping m when directly followed by "(".
        if unit == "m" and text[match.end() : match.end() + 1] == "(":
            continue
        out.add(f"{match.group(1)}{unit}")
    for match in re.finditer(r"\b(\d+)\s*cup\b", text):
        out.add(f"{match.group(1)}cup")
    for match in re.finditer(r"\b(\d+)mm\s*x\s*(\d+)m\b", text):
        out.add(f"{match.group(1)}mmx{match.group(2)}m")
    return sorted(out)


def first_brand_token(title: object) -> str:
    text = normalize_title(title)
    if not text:
        return ""
    return re.split(r"\W+", text)[0]


def fmt_gbp(value: object) -> str:
    try:
        return f"£{float(value):.2f}"
    except Exception:
        return "-"


def fmt_pct(value: object) -> str:
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return "-"


def escape_md(value: object) -> str:
    if pd.isna(value):
        return "-"
    return str(value).replace("\r", " ").replace("\n", " ").replace("|", r"\|")


SCHEMA_COLS = [
    "Verdict",
    "Confidence (0-100)",
    "SupplierTitle",
    "AmazonTitle",
    "Supplier EAN",
    "Amazon EAN",
    "ASIN",
    "SupplierPrice_incVAT",
    "SellingPrice_incVAT",
    "NetProfit",
    "ROI",
    "Sales",
    "Pack Verdict",
    "Adjusted Profit (approx)",
    "Key Match Evidence",
    "Key Risks / Notes",
]


def build_row(
    *,
    verdict: str,
    confidence: int,
    supplier_title: object,
    amazon_title: object,
    supplier_ean: str,
    amazon_ean: str,
    asin: object,
    supplier_price: object,
    selling_price: object,
    net_profit: object,
    roi: object,
    sales: object,
    pack_verdict: str,
    adj_profit: float,
    evidence: str,
    risks: str,
) -> dict[str, object]:
    return {
        "Verdict": verdict,
        "Confidence (0-100)": int(confidence),
        "SupplierTitle": escape_md(supplier_title),
        "AmazonTitle": escape_md(amazon_title),
        "Supplier EAN": supplier_ean or "-",
        "Amazon EAN": amazon_ean or "-",
        "ASIN": escape_md(asin),
        "SupplierPrice_incVAT": fmt_gbp(supplier_price),
        "SellingPrice_incVAT": fmt_gbp(selling_price),
        "NetProfit": fmt_gbp(net_profit),
        "ROI": fmt_pct(roi),
        "Sales": int(float(sales)) if str(sales).strip() not in {"", "-"} else 0,
        "Pack Verdict": escape_md(pack_verdict),
        "Adjusted Profit (approx)": fmt_gbp(adj_profit),
        "Key Match Evidence": escape_md(evidence),
        "Key Risks / Notes": escape_md(risks),
    }


def md_table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "_None._\n"
    lines = [
        "| " + " | ".join(SCHEMA_COLS) + " |",
        "|:--|--:|:--|:--|:--|:--|:--|:--|:--|:--|:--|--:|:--|:--|:--|:--|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(c, "-")) for c in SCHEMA_COLS) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).with_name("part1.xlsx"),
        help="Path to the financial report (xlsx or csv).",
    )
    args = parser.parse_args()

    input_path: Path = args.input
    out_dir = input_path.parent
    stamp = datetime.now(TZ).date().strftime("%Y%m%d")
    out_deep_csv = out_dir / f"deep_analysis_{stamp}.csv"
    out_md = out_dir / f"PHASEA_MANUAL_REPORT_{stamp}.md"
    out_xlsx = out_dir / f"PHASEA_MANUAL_REPORT_{stamp}.xlsx"

    if input_path.suffix.lower() == ".csv":
        df = pd.read_csv(input_path)
    else:
        df = pd.read_excel(input_path, sheet_name=0)

    df["Supplier EAN"] = df.get("EAN", pd.Series([None] * len(df))).map(clean_ean)
    df["Amazon EAN"] = df.get("EAN_OnPage", pd.Series([None] * len(df))).map(clean_ean)

    if "sales_numeric" in df.columns:
        df["sales"] = pd.to_numeric(df["sales_numeric"], errors="coerce").fillna(0)
    elif "bought_in_past_month" in df.columns:
        df["sales"] = pd.to_numeric(df["bought_in_past_month"], errors="coerce").fillna(0)
    else:
        df["sales"] = 0

    df["title_match"] = df.apply(lambda x: title_similarity(x.get("SupplierTitle"), x.get("AmazonTitle")), axis=1)
    df["is_exact_ean"] = (
        (df["Supplier EAN"] != "-") & (df["Amazon EAN"] != "-") & (df["Supplier EAN"] == df["Amazon EAN"])
    )

    df["Sup_Qty"] = df.get("SupplierTitle", pd.Series([None] * len(df))).apply(extract_quantity_baseline)
    df["Amz_Qty"] = df.get("AmazonTitle", pd.Series([None] * len(df))).apply(extract_quantity_baseline)
    df["Qty_Ratio"] = df["Amz_Qty"] / df["Sup_Qty"]

    df["Adjusted_Profit"] = df.apply(
        lambda r: recalculate_profit(
            float(r.get("NetProfit", 0.0)), float(r.get("SupplierPrice_incVAT", 0.0)), float(r.get("Qty_Ratio", 1.0))
        ),
        axis=1,
    )

    df["category"] = df.apply(lambda r: categorize(bool(r.get("is_exact_ean")), float(r.get("title_match", 0.0))), axis=1)
    df["Pack_Verdict"] = df.apply(
        lambda r: pack_verdict_baseline(float(r.get("Qty_Ratio", 1.0)), float(r.get("Adjusted_Profit", 0.0))),
        axis=1,
    )

    df["ip_risk"] = df.apply(
        lambda r: is_ip_risk_text(r.get("SupplierTitle")) or is_ip_risk_text(r.get("AmazonTitle")),
        axis=1,
    )

    # ----------------- Manual verification -----------------
    verified_reco: list[dict[str, object]] = []
    verified_excl: list[dict[str, object]] = []
    high_reco: list[dict[str, object]] = []
    high_excl: list[dict[str, object]] = []
    needs_reco: list[dict[str, object]] = []  # intentionally conservative -> empty

    ip_risk_rows: list[dict[str, object]] = []
    for _, r in df[df["ip_risk"]].sort_values(["sales"], ascending=[False]).head(75).iterrows():
        ip_risk_rows.append(
            build_row(
                verdict="IP RISK",
                confidence=0,
                supplier_title=r.get("SupplierTitle"),
                amazon_title=r.get("AmazonTitle"),
                supplier_ean=r.get("Supplier EAN", "-"),
                amazon_ean=r.get("Amazon EAN", "-"),
                asin=r.get("ASIN"),
                supplier_price=r.get("SupplierPrice_incVAT"),
                selling_price=r.get("SellingPrice_incVAT"),
                net_profit=r.get("NetProfit"),
                roi=r.get("ROI"),
                sales=r.get("sales"),
                pack_verdict=r.get("Pack_Verdict", "-"),
                adj_profit=float(r.get("Adjusted_Profit", 0.0)),
                evidence="Luxury/brand term detected in title text.",
                risks="EXCLUDED: potential IP / brand restriction risk.",
            )
        )

    verified_candidates = df[df["is_exact_ean"] & (df.get("NetProfit", 0) > 0)].copy()
    verified_candidates = verified_candidates.sort_values(["sales", "NetProfit"], ascending=[False, False])

    for _, r in verified_candidates.iterrows():
        ean = r.get("Supplier EAN", "-")
        sup_pack = extract_pack_count(r.get("SupplierTitle"))
        amz_pack = extract_pack_count(r.get("AmazonTitle"))

        net_profit = float(r.get("NetProfit", 0.0))
        supplier_cost = float(r.get("SupplierPrice_incVAT", 0.0))

        evidence_parts = [f"Exact EAN match: {ean}."]
        if sup_pack.count:
            evidence_parts.append(f"Supplier count cue: {sup_pack.count} ({', '.join(sup_pack.evidence[:2])}).")
        if amz_pack.count:
            evidence_parts.append(f"Amazon count cue: {amz_pack.count} ({', '.join(amz_pack.evidence[:2])}).")

        pack_verdict = "1:1 Match"
        adj_profit = net_profit
        exclude_reason = ""

        if sup_pack.count and amz_pack.count and sup_pack.count != amz_pack.count:
            rsu_raw = amz_pack.count / sup_pack.count
            if abs(rsu_raw - round(rsu_raw)) < 1e-9:
                rsu = int(round(rsu_raw))
                pack_verdict = f"BUNDLE ({rsu}x) - LOSS"
                adj_profit = net_profit - supplier_cost * (rsu - 1)
                exclude_reason = (
                    f"EXCLUDED: exact EAN but pack/count contradiction (supplier {sup_pack.count} vs Amazon {amz_pack.count}); "
                    f"if RSU={rsu} then AdjProfit≈{fmt_gbp(adj_profit)}."
                )
            else:
                exclude_reason = (
                    f"EXCLUDED: exact EAN but pack/count contradiction (supplier {sup_pack.count} vs Amazon {amz_pack.count}); "
                    f"RSU={rsu_raw:.2f} not an integer."
                )

        if exclude_reason:
            verified_excl.append(
                build_row(
                    verdict="VERIFIED",
                    confidence=40,
                    supplier_title=r.get("SupplierTitle"),
                    amazon_title=r.get("AmazonTitle"),
                    supplier_ean=r.get("Supplier EAN", "-"),
                    amazon_ean=r.get("Amazon EAN", "-"),
                    asin=r.get("ASIN"),
                    supplier_price=r.get("SupplierPrice_incVAT"),
                    selling_price=r.get("SellingPrice_incVAT"),
                    net_profit=net_profit,
                    roi=r.get("ROI"),
                    sales=r.get("sales"),
                    pack_verdict=pack_verdict,
                    adj_profit=adj_profit,
                    evidence=" ".join(evidence_parts)[:500],
                    risks=exclude_reason,
                )
            )
            continue

        if bool(r.get("ip_risk")):
            continue
        if float(r.get("sales", 0.0)) <= 0 or net_profit <= 0 or adj_profit <= 0:
            continue

        # Confidence tweaks: if only one side mentions pack count, note it.
        confidence = 95
        risks = "Exact EAN match; verify variant/pack from titles/images before buy."
        if (sup_pack.count and not amz_pack.count) or (amz_pack.count and not sup_pack.count):
            confidence = 85
            risks = "Exact EAN match; pack count appears in only one title—verify pack size before buy."

        verified_reco.append(
            build_row(
                verdict="VERIFIED",
                confidence=confidence,
                supplier_title=r.get("SupplierTitle"),
                amazon_title=r.get("AmazonTitle"),
                supplier_ean=r.get("Supplier EAN", "-"),
                amazon_ean=r.get("Amazon EAN", "-"),
                asin=r.get("ASIN"),
                supplier_price=r.get("SupplierPrice_incVAT"),
                selling_price=r.get("SellingPrice_incVAT"),
                net_profit=net_profit,
                roi=r.get("ROI"),
                sales=r.get("sales"),
                pack_verdict=pack_verdict,
                adj_profit=adj_profit,
                evidence=" ".join(evidence_parts)[:500],
                risks=risks,
            )
        )

    high_candidates = df[(~df["is_exact_ean"]) & (df["title_match"] >= 0.50) & (df.get("NetProfit", 0) > 0)].copy()
    high_candidates = high_candidates.sort_values(["sales", "NetProfit"], ascending=[False, False])

    for _, r in high_candidates.iterrows():
        sup_title = r.get("SupplierTitle")
        amz_title = r.get("AmazonTitle")
        net_profit = float(r.get("NetProfit", 0.0))
        supplier_cost = float(r.get("SupplierPrice_incVAT", 0.0))
        sup_ean = str(r.get("Supplier EAN", "-")).strip()
        amz_ean = str(r.get("Amazon EAN", "-")).strip()

        sup_pack = extract_pack_count(sup_title)
        amz_pack = extract_pack_count(amz_title)
        sup_sizes = extract_size_tokens(sup_title)
        amz_sizes = extract_size_tokens(amz_title)

        pack_verdict = "1:1 Match"
        rsu = 1
        manual_adj_profit = net_profit

        exclusion_reason = ""
        if sup_sizes and amz_sizes and set(sup_sizes) != set(amz_sizes):
            mismatch = ", ".join(sorted(set(sup_sizes) ^ set(amz_sizes))[:3])
            exclusion_reason = f"EXCLUDED: variant/size cue mismatch between titles ({mismatch})."

        if not exclusion_reason and sup_pack.count and amz_pack.count and sup_pack.count != amz_pack.count:
            rsu_raw = amz_pack.count / sup_pack.count
            if abs(rsu_raw - round(rsu_raw)) < 1e-9:
                rsu = int(round(rsu_raw))
                manual_adj_profit = net_profit - supplier_cost * (rsu - 1)
                pack_verdict = f"BUNDLE ({rsu}x) - {'OK' if manual_adj_profit > 0 else 'LOSS'}"
                if manual_adj_profit <= 0:
                    exclusion_reason = (
                        f"EXCLUDED: pack mismatch requires RSU={rsu}; AdjProfit≈{fmt_gbp(manual_adj_profit)} (turns non-profitable)."
                    )
                elif float(r.get("title_match", 0.0)) < 0.80:
                    exclusion_reason = (
                        f"EXCLUDED: pack mismatch requires RSU={rsu} (profit stays positive), but EAN mismatch + non-perfect title match."
                    )
            else:
                exclusion_reason = (
                    f"EXCLUDED: pack mismatch (supplier {sup_pack.count} vs Amazon {amz_pack.count}) gives non-integer RSU={rsu_raw:.2f}."
                )

        if not exclusion_reason and ((sup_pack.count and not amz_pack.count) or (amz_pack.count and not sup_pack.count)):
            exclusion_reason = "EXCLUDED: pack/quantity ambiguity (count shown in only one title)."

        if not exclusion_reason:
            brand_sup = first_brand_token(sup_title)
            brand_amz = first_brand_token(amz_title)
            if brand_sup and brand_amz and brand_sup != brand_amz:
                exclusion_reason = f"EXCLUDED: brand token mismatch ('{brand_sup}' vs '{brand_amz}')."

        if not exclusion_reason and float(r.get("title_match", 0.0)) < 0.70:
            exclusion_reason = "EXCLUDED: title similarity >=0.50 but not strong enough after manual review (EAN mismatch/missing)."

        # Aggressive false-positive filter: if Amazon EAN is present and does not match Supplier EAN,
        # treat it as a high-risk mismatch (only allow non-EAN recommendations when Amazon EAN is missing).
        if not exclusion_reason and sup_ean != "-" and amz_ean != "-" and sup_ean != amz_ean:
            exclusion_reason = "EXCLUDED: EAN mismatch present (Supplier EAN != Amazon EAN)."

        if not exclusion_reason:
            if bool(r.get("ip_risk")):
                continue
            if float(r.get("sales", 0.0)) <= 0 or net_profit <= 0 or manual_adj_profit <= 0:
                continue
            high_reco.append(
                build_row(
                    verdict="HIGH LIKELIHOOD",
                    confidence=80,
                    supplier_title=sup_title,
                    amazon_title=amz_title,
                    supplier_ean=r.get("Supplier EAN", "-"),
                    amazon_ean=r.get("Amazon EAN", "-"),
                    asin=r.get("ASIN"),
                    supplier_price=r.get("SupplierPrice_incVAT"),
                    selling_price=r.get("SellingPrice_incVAT"),
                    net_profit=net_profit,
                    roi=r.get("ROI"),
                    sales=r.get("sales"),
                    pack_verdict=pack_verdict,
                    adj_profit=manual_adj_profit,
                    evidence=f"Title match={float(r.get('title_match', 0.0)):.2f}; strong model/keyword alignment in titles.",
                    risks="EAN mismatch/missing; verify barcode + exact variant before buying.",
                )
            )
        else:
            high_excl.append(
                build_row(
                    verdict="HIGH LIKELIHOOD",
                    confidence=30,
                    supplier_title=sup_title,
                    amazon_title=amz_title,
                    supplier_ean=r.get("Supplier EAN", "-"),
                    amazon_ean=r.get("Amazon EAN", "-"),
                    asin=r.get("ASIN"),
                    supplier_price=r.get("SupplierPrice_incVAT"),
                    selling_price=r.get("SellingPrice_incVAT"),
                    net_profit=net_profit,
                    roi=r.get("ROI"),
                    sales=r.get("sales"),
                    pack_verdict=pack_verdict,
                    adj_profit=manual_adj_profit,
                    evidence=(
                        f"Supplier cues: {', '.join(sup_pack.evidence[:2]) or '-'}; "
                        f"Amazon cues: {', '.join(amz_pack.evidence[:2]) or '-'}"
                        + (f"; RSU={rsu}" if rsu != 1 else "")
                    ),
                    risks=exclusion_reason,
                )
            )

    # Sort by sales desc
    verified_reco.sort(key=lambda r: int(r["Sales"]), reverse=True)
    verified_excl.sort(key=lambda r: int(r["Sales"]), reverse=True)
    high_reco.sort(key=lambda r: int(r["Sales"]), reverse=True)
    high_excl.sort(key=lambda r: int(r["Sales"]), reverse=True)

    # ----------------- Save deep_analysis CSV -----------------
    df["manual_group"] = ""
    df["manual_pack_count_supplier"] = df["SupplierTitle"].apply(lambda x: extract_pack_count(x).count)
    df["manual_pack_count_amazon"] = df["AmazonTitle"].apply(lambda x: extract_pack_count(x).count)
    df["manual_size_tokens_supplier"] = df["SupplierTitle"].apply(lambda x: ",".join(extract_size_tokens(x)))
    df["manual_size_tokens_amazon"] = df["AmazonTitle"].apply(lambda x: ",".join(extract_size_tokens(x)))

    reco_asins = {str(r["ASIN"]) for r in verified_reco + high_reco}
    excl_asins_verified = {str(r["ASIN"]) for r in verified_excl}
    excl_asins_high = {str(r["ASIN"]) for r in high_excl}

    df.loc[df["ASIN"].astype(str).isin(reco_asins) & df["is_exact_ean"], "manual_group"] = "VERIFIED_RECOMMENDED"
    df.loc[df["ASIN"].astype(str).isin(reco_asins) & (~df["is_exact_ean"]), "manual_group"] = "HIGH_LIKELIHOOD_RECOMMENDED"
    df.loc[df["ASIN"].astype(str).isin(excl_asins_verified), "manual_group"] = "VERIFIED_FILTERED_OUT"
    df.loc[df["ASIN"].astype(str).isin(excl_asins_high), "manual_group"] = "HIGH_LIKELIHOOD_FILTERED_OUT"

    deep_cols = [
        "category",
        "is_exact_ean",
        "Pack_Verdict",
        "Adjusted_Profit",
        "NetProfit",
        "ROI",
        "Qty_Ratio",
        "Sup_Qty",
        "Amz_Qty",
        "title_match",
        "sales",
        "SupplierTitle",
        "AmazonTitle",
        "Supplier EAN",
        "Amazon EAN",
        "ASIN",
        "SupplierPrice_incVAT",
        "SellingPrice_incVAT",
        "manual_group",
        "manual_pack_count_supplier",
        "manual_pack_count_amazon",
        "manual_size_tokens_supplier",
        "manual_size_tokens_amazon",
        "ip_risk",
    ]
    deep_cols = [c for c in deep_cols if c in df.columns]
    df.to_csv(out_deep_csv, index=False, columns=deep_cols)

    # ----------------- Save Markdown report -----------------
    total_rows = int(len(df))
    rows_sales_gt0 = int((df["sales"] > 0).sum())
    rows_excl_sales0 = int(total_rows - rows_sales_gt0)
    rows_excl_netprofit_le0 = int((df.get("NetProfit", 0) <= 0).sum())
    rows_excl_pack_adj_le0 = int(((df["sales"] > 0) & (df.get("NetProfit", 0) > 0) & (df["Adjusted_Profit"] <= 0)).sum())

    ip_risk_count = int(df["ip_risk"].sum())

    md_parts: list[str] = []
    md_parts.append("# Phase A Manual Match Review (Non-EAN Improvements)\n")
    md_parts.append(f"**Generated:** {datetime.now(TZ).date().isoformat()} (Asia/Dubai)  ")
    md_parts.append(f"**Source:** `{input_path.name}`\n")

    md_parts.append("## Summary counts\n")
    md_parts.append("| Metric | Count |\n|:--|--:|")
    md_parts.append(f"| Total rows | {total_rows} |")
    md_parts.append(f"| Rows with Sales>0 | {rows_sales_gt0} |")
    md_parts.append(f"| Rows excluded (Sales=0) | {rows_excl_sales0} |")
    md_parts.append(f"| Rows excluded (NetProfit<=0) | {rows_excl_netprofit_le0} |")
    md_parts.append(f"| Rows excluded (Pack-adjusted profit<=0) | {rows_excl_pack_adj_le0} |")
    md_parts.append(f"| VERIFIED (exact EAN, recommended) | {len(verified_reco)} |")
    md_parts.append(f"| HIGH LIKELIHOOD (recommended) | {len(high_reco)} |")
    md_parts.append(f"| NEEDS VERIFICATION (recommended) | {len(needs_reco)} |")
    md_parts.append(f"| IP risk rows flagged (excluded) | {ip_risk_count} |")
    md_parts.append(f"| NEW: VERIFIED filtered out (audit) | {len(verified_excl)} |")
    md_parts.append(f"| NEW: HIGH LIKELIHOOD filtered out (audit) | {len(high_excl)} |\n")

    md_parts.append("---\n")

    md_parts.append("## VERIFIED (Exact EAN in report) — RECOMMENDED\n")
    md_parts.append(
        "**Criteria:** Sales>0, NetProfit>0, Profit>0 after sanity (including any Stage 6B overrides), "
        "Supplier EAN == Amazon EAN, and not IP-risk.  \nSorted by Sales desc.\n"
    )
    md_parts.append(md_table(verified_reco))

    md_parts.append("### NEW: VERIFIED (Exact EAN) — FILTERED OUT (Audit)\n")
    md_parts.append("Rows with exact EAN that were excluded after Stage 6B/pack or title contradiction review.\n")
    md_parts.append(md_table(verified_excl))

    md_parts.append("---\n")

    md_parts.append("## HIGH LIKELIHOOD (Top 75 by Sales) — RECOMMENDED\n")
    md_parts.append(
        "**Criteria:** Sales>0, NetProfit>0, Profit>0 after Stage 6 manual pack verification, strong title/variant evidence.  \n"
        "Sorted by Sales desc.\n"
    )
    md_parts.append(md_table(high_reco[:75]))

    md_parts.append("### NEW: HIGH LIKELIHOOD — FILTERED OUT (Audit)\n")
    md_parts.append(
        "Rows initially considered HIGH LIKELIHOOD but excluded primarily due to pack/size mismatch or low confidence. "
        "Sorted by Sales desc.\n"
    )
    md_parts.append(md_table(high_excl[:75]))
    if len(high_excl) > 75:
        md_parts.append(f"Remaining HIGH LIKELIHOOD filtered-out rows not shown: {len(high_excl) - 75}.\n")

    md_parts.append("---\n")

    md_parts.append("## NEEDS VERIFICATION (Top 75 by Sales) — RECOMMENDED\n")
    md_parts.append(
        "**Criteria:** Sales>0, NetProfit>0, Profit>0 after pack sanity, but ambiguous variant/pack evidence.  \n"
        "Sorted by Sales desc.\n"
    )
    md_parts.append(md_table(needs_reco[:75]))

    md_parts.append("## IP RISK (excluded)\n")
    md_parts.append(f"Flagged rows: **{ip_risk_count}** (top 75 shown).\n")
    md_parts.append(md_table(ip_risk_rows))

    out_md.write_text("\n".join(md_parts), encoding="utf-8")

    # ----------------- Optional XLSX -----------------
    try:
        with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
            pd.DataFrame(
                {
                    "Metric": [
                        "Total rows",
                        "Rows with Sales>0",
                        "Rows excluded (Sales=0)",
                        "Rows excluded (NetProfit<=0)",
                        "Rows excluded (Pack-adjusted profit<=0)",
                        "VERIFIED (exact EAN, recommended)",
                        "VERIFIED filtered out (audit)",
                        "HIGH LIKELIHOOD (recommended)",
                        "HIGH LIKELIHOOD filtered out (audit)",
                        "NEEDS VERIFICATION (recommended)",
                        "IP risk rows flagged (excluded)",
                    ],
                    "Count": [
                        total_rows,
                        rows_sales_gt0,
                        rows_excl_sales0,
                        rows_excl_netprofit_le0,
                        rows_excl_pack_adj_le0,
                        len(verified_reco),
                        len(verified_excl),
                        len(high_reco),
                        len(high_excl),
                        len(needs_reco),
                        ip_risk_count,
                    ],
                }
            ).to_excel(writer, sheet_name="SUMMARY", index=False)

            def rows_to_df(rows: list[dict[str, object]]) -> pd.DataFrame:
                return pd.DataFrame(rows, columns=SCHEMA_COLS) if rows else pd.DataFrame(columns=SCHEMA_COLS)

            rows_to_df(verified_reco).to_excel(writer, sheet_name="VERIFIED_RECOMMENDED", index=False)
            rows_to_df(verified_excl).to_excel(writer, sheet_name="VERIFIED_FILTERED_OUT", index=False)
            rows_to_df(high_reco[:75]).to_excel(writer, sheet_name="HIGH_RECO_TOP75", index=False)
            rows_to_df(high_excl[:75]).to_excel(writer, sheet_name="HIGH_FILTERED_OUT_TOP75", index=False)
            rows_to_df(needs_reco[:75]).to_excel(writer, sheet_name="NEEDS_VERIFY_TOP75", index=False)
            rows_to_df(ip_risk_rows).to_excel(writer, sheet_name="IP_RISK_EXCLUDED", index=False)
            df.to_excel(writer, sheet_name="ALL_ROWS_ANNOTATED", index=False)
    except Exception as exc:
        print(f"XLSX export skipped: {exc}")

    print("Wrote:")
    print(out_deep_csv)
    print(out_md)
    print(out_xlsx)
    print("Counts:", {"verified_recommended": len(verified_reco), "high_recommended": len(high_reco)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
