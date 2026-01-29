from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


BASE = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - "
    r"POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec"
)

SOURCE_XLSX = BASE / "part_30_dec.xlsx"
OPUS2_REPORT = BASE / "opus2" / "PHASEA_MANUAL_REPORT_20251230.md"
OUTPUT_MD = BASE / "CODEX_STRICT_VALIDATION_REPORT_20251230.md"


def import_grounding_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("gt_summary", str(BASE / "generate_ground_truth_summary.py"))
    if not spec or not spec.loader:
        raise SystemExit("Could not import generate_ground_truth_summary.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def truncate(s: str, max_len: int) -> str:
    s = (s or "").replace("\t", " ").replace("\n", " ").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3].rstrip() + "..."


def fixed_width_table(rows: list[dict[str, str]], columns: list[str], max_widths: dict[str, int]) -> str:
    prepared: list[dict[str, str]] = []
    for r in rows:
        pr: dict[str, str] = {}
        for c in columns:
            cell = str(r.get(c, "") or "")
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


def hnorm(s: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", (s or "").upper())


def parse_text_tables(md_text: str) -> list[dict[str, str]]:
    """
    Parse all rows from all ```text blocks that contain a markdown table.
    Returns dicts with best-effort keys.
    """
    rows: list[dict[str, str]] = []
    lines = md_text.splitlines()
    in_block = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```text"):
            in_block = True
            i += 1
            continue
        if in_block and line.strip().startswith("```"):
            in_block = False
            i += 1
            continue
        if not in_block:
            i += 1
            continue

        if not line.lstrip().startswith("|"):
            i += 1
            continue

        header = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(header) < 5 or i + 1 >= len(lines):
            i += 1
            continue

        sep = lines[i + 1]
        if "-" not in sep or "|" not in sep:
            i += 1
            continue

        hn = [hnorm(h) for h in header]

        def find_idx(*needles: str) -> int | None:
            for idx, h in enumerate(hn):
                if all(n in h for n in needles):
                    return idx
            return None

        idx_sup_ean = find_idx("SUPPLIER", "EAN")
        idx_amz_ean = find_idx("AMAZON", "EAN")
        idx_asin = find_idx("ASIN")
        idx_sup_title = find_idx("SUPPLIER", "TITLE")
        idx_amz_title = find_idx("AMAZON", "TITLE")

        if idx_sup_ean is None and idx_asin is None:
            i += 1
            continue

        j = i + 2
        while j < len(lines):
            body = lines[j]
            if not body.lstrip().startswith("|"):
                break
            if re.fullmatch(r"[\s\-\|:]+", body.strip()):
                j += 1
                continue

            parts = [c.strip() for c in body.strip().strip("|").split("|")]
            if len(parts) != len(header):
                j += 1
                continue

            rows.append(
                {
                    "supplier_ean": parts[idx_sup_ean] if idx_sup_ean is not None else "",
                    "amazon_ean": parts[idx_amz_ean] if idx_amz_ean is not None else "",
                    "asin": parts[idx_asin] if idx_asin is not None else "",
                    "supplier_title": parts[idx_sup_title] if idx_sup_title is not None else "",
                    "amazon_title": parts[idx_amz_title] if idx_amz_title is not None else "",
                }
            )
            j += 1

        i = j

    return rows


def title_similarity_pct(mod, a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, mod.title_norm(a), mod.title_norm(b)).ratio() * 100.0


@dataclass(frozen=True)
class GroundedRow:
    row_id: int
    category: str
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


def fmt_money(val: float) -> str:
    return f"£{val:.2f}"


def fmt_pct(val: float) -> str:
    try:
        v = float(val)
    except (TypeError, ValueError):
        return "-"
    if not math.isfinite(v):
        return "-"
    pct = v * 100.0 if abs(v) <= 10 else v
    return f"{pct:.1f}%"


def fmt_money(val: float) -> str:
    return f"£{val:.2f}"


def build_pack_verdict(mod, sup_title: str, amz_title: str) -> tuple[str, float]:
    sup_pack, _ = mod.extract_pack_count(sup_title)
    amz_pack, _ = mod.extract_pack_count(amz_title)
    pack_ratio = amz_pack / sup_pack if sup_pack else 1.0
    if sup_pack == amz_pack:
        return "1:1", pack_ratio
    if amz_pack > sup_pack:
        return f"BUNDLE (amz/sup={amz_pack}/{sup_pack})", pack_ratio
    return f"SPLIT (amz/sup={amz_pack}/{sup_pack})", pack_ratio


def resolve_report_row_ids(mod, df: pd.DataFrame, parsed_rows: list[dict[str, str]]) -> list[int]:
    from collections import defaultdict

    ean_to_rids: dict[str, list[int]] = defaultdict(list)
    asin_to_rids: dict[str, list[int]] = defaultdict(list)

    for idx in range(len(df)):
        rid = idx + 1
        ean = mod.norm_digits(df.iloc[idx].get("EAN", ""))
        if ean and ean.lower() != "nan":
            ean_to_rids[ean].append(rid)
        asin = str(df.iloc[idx].get("ASIN", "") or "").strip()
        if asin:
            asin_to_rids[asin].append(rid)

    resolved: list[int] = []
    for r in parsed_rows:
        sup_ean = mod.norm_digits(r.get("supplier_ean", ""))
        asin = (r.get("asin", "") or "").strip()
        rid: int | None = None

        if sup_ean and sup_ean in ean_to_rids:
            rid = ean_to_rids[sup_ean][0]
        elif asin and asin in asin_to_rids:
            cands = asin_to_rids[asin]
            if len(cands) == 1:
                rid = cands[0]
            else:
                # Disambiguate by supplier-title similarity if possible
                st = r.get("supplier_title", "")
                best, best_sim = None, -1.0
                for cand in cands:
                    cand_title = str(df.iloc[cand - 1].get("SupplierTitle", "") or "")
                    s = title_similarity_pct(mod, st, cand_title)
                    if s > best_sim:
                        best, best_sim = cand, s
                if best is not None and best_sim >= 75.0:
                    rid = best

        if rid is None:
            continue
        resolved.append(rid)

    return sorted(set(resolved))


def nv_shortlist(mod, items: list[GroundedRow]) -> list[GroundedRow]:
    """
    Shortlist NV items that are extremely likely matches but need a minor verification.

    We use a score threshold of >=47 (median NV score for opus2), and additionally require:
    - TypeMatch=Y
    - (Brand match OR title similarity >=55%)
    - No EAN mismatch (if both EANs present and different, exclude)
    """
    shortlisted: list[GroundedRow] = []
    for it in items:
        if it.category != "NEEDS VERIFICATION":
            continue
        if it.score < 47:
            continue

        sup_ean = mod.norm_digits(it.supplier_ean)
        amz_ean = mod.norm_digits(it.amazon_ean)
        ean_mismatch = bool(sup_ean) and bool(amz_ean) and sup_ean != amz_ean
        if ean_mismatch:
            continue

        prod_match = mod.product_type_match(it.supplier_title, it.amazon_title)
        if not prod_match:
            continue

        sim = mod.title_similarity_pct(it.supplier_title, it.amazon_title)
        b_sup = mod.detect_brand(it.supplier_title)
        b_amz = mod.detect_brand(it.amazon_title)
        brand_match = bool(b_sup) and b_sup == b_amz
        if not (brand_match or sim >= 55.0):
            continue

        shortlisted.append(it)

    shortlisted.sort(key=lambda x: (x.score, mod.title_similarity_pct(x.supplier_title, x.amazon_title)), reverse=True)
    return shortlisted


def to_table_rows(items: list[GroundedRow]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for it in items:
        out.append(
            {
                "Verdict": it.category,
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
    if not OPUS2_REPORT.exists():
        raise SystemExit(f"Missing: {OPUS2_REPORT}")

    mod = import_grounding_module()
    df = pd.read_excel(SOURCE_XLSX)

    report_text = OPUS2_REPORT.read_text(encoding="utf-8", errors="replace")
    parsed = parse_text_tables(report_text)
    resolved_row_ids = resolve_report_row_ids(mod, df, parsed)

    grounded: list[GroundedRow] = []
    for rid in resolved_row_ids:
        row = df.iloc[rid - 1]

        sup_title = str(row.get("SupplierTitle", "") or "")
        amz_title = str(row.get("AmazonTitle", "") or "")
        sup_ean = mod.norm_digits(row.get("EAN", "")) or "-"
        amz_ean = mod.norm_digits(row.get("EAN_OnPage", "")) or "-"
        asin = str(row.get("ASIN", "") or "").strip()

        sup_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
        sell_price = float(row.get("SellingPrice_incVAT", 0) or 0)
        net_profit = float(row.get("NetProfit", 0) or 0)
        roi = float(row.get("ROI", 0) or 0)
        sales = float(row.get("bought_in_past_month", 0) or 0)

        cat, score, _, _, adj_profit, var_reason = mod.classify_row(
            sup_title,
            amz_title,
            mod.norm_digits(row.get("EAN", "")),
            mod.norm_digits(row.get("EAN_OnPage", "")),
            sup_price,
            net_profit,
            roi,
        )

        pack_verdict, pack_ratio = build_pack_verdict(mod, sup_title, amz_title)

        sim_pct = mod.title_similarity_pct(sup_title, amz_title)
        type_match = mod.product_type_match(sup_title, amz_title)
        b_sup = mod.detect_brand(sup_title)
        b_amz = mod.detect_brand(amz_title)
        if b_sup and b_sup == b_amz:
            brand_txt = f"Brand={b_sup}"
        else:
            brand_txt = "Brand=-"

        # EAN status
        sup_ean_d = mod.norm_digits(row.get("EAN", ""))
        amz_ean_d = mod.norm_digits(row.get("EAN_OnPage", ""))
        if sup_ean_d and amz_ean_d:
            ean_txt = "EAN=Exact" if sup_ean_d == amz_ean_d else "EAN=Mismatch"
        else:
            ean_txt = "EAN=Incomplete"

        evidence_bits = [
            f"RowID={rid}",
            f"Sim={sim_pct:.0f}%",
            brand_txt,
            f"TypeMatch={'Y' if type_match else 'N'}",
            ean_txt,
        ]
        if pack_verdict != "1:1":
            evidence_bits.append(f"Pack={pack_verdict}")
        if var_reason:
            evidence_bits.append(f"Variant={var_reason}")
        key_evidence = "; ".join(evidence_bits)

        filter_reason = "-"
        if cat == "NEEDS VERIFICATION":
            if ean_txt == "EAN=Incomplete":
                filter_reason = "EAN missing/incomplete (confirm listing)"
            elif ean_txt == "EAN=Mismatch":
                filter_reason = "EAN mismatch (verify listing)"
            elif pack_verdict != "1:1":
                filter_reason = "Confirm pack interpretation"
            else:
                filter_reason = "Confirm 1-2 minor details"

        grounded.append(
            GroundedRow(
                row_id=rid,
                category=cat,
                score=score,
                supplier_title=sup_title,
                amazon_title=amz_title,
                supplier_ean=sup_ean,
                amazon_ean=amz_ean,
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

    # Counts
    grounded_counts: dict[str, int] = {}
    for c in ["VERIFIED", "HIGHLY LIKELY", "NEEDS VERIFICATION", "OTHER / LOW PRIORITY"]:
        grounded_counts[c] = sum(1 for g in grounded if g.category == c)

    strict_verified = [g for g in grounded if g.category == "VERIFIED" and "EAN=Exact" in g.key_evidence and "Variant=" not in g.key_evidence]
    strict_hl = [
        g
        for g in grounded
        if g.category == "HIGHLY LIKELY"
        and ("TypeMatch=Y" in g.key_evidence)
        and (mod.title_similarity_pct(g.supplier_title, g.amazon_title) >= 65.0)
        and ("EAN=Mismatch" not in g.key_evidence)
        and ("Variant=" not in g.key_evidence)
    ]

    shortlisted_nv = nv_shortlist(mod, grounded)

    # Build output
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
        "Verdict": 22,
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
        "Key Match Evidence": 80,
        "Filter Reason": 55,
    }

    out: list[str] = []
    out.append("# CODEX STRICT VALIDATION REPORT")
    out.append("")
    out.append(f"**Ground Truth Dataset:** `{SOURCE_XLSX}` ({len(df)} rows)")
    out.append(f"**Validated Report:** `{OPUS2_REPORT}`")
    out.append("")
    out.append("## Grounded Counts (All products listed in opus2 report)")
    out.append("")
    out.append("```text")
    out.append(
        fixed_width_table(
            [
                {"Metric": "Unique products listed (resolved)", "Value": str(len(grounded))},
                {"Metric": "Grounded VERIFIED", "Value": str(grounded_counts["VERIFIED"])},
                {"Metric": "Grounded HIGHLY LIKELY", "Value": str(grounded_counts["HIGHLY LIKELY"])},
                {"Metric": "Grounded NEEDS VERIFICATION", "Value": str(grounded_counts["NEEDS VERIFICATION"])},
                {"Metric": "Grounded OTHER / LOW PRIORITY", "Value": str(grounded_counts["OTHER / LOW PRIORITY"])},
            ],
            ["Metric", "Value"],
            {"Metric": 40, "Value": 10},
        )
    )
    out.append("```")
    out.append("")
    out.append("## Codex Strict Counts")
    out.append("")
    out.append("```text")
    out.append(
        fixed_width_table(
            [
                {"Group": "Strict VERIFIED", "Count": str(len(strict_verified))},
                {"Group": "Strict HIGHLY LIKELY", "Count": str(len(strict_hl))},
                {"Group": "Strict (VERIFIED+HL)", "Count": str(len(strict_verified) + len(strict_hl))},
                {"Group": "Shortlisted NEEDS VERIFICATION", "Count": str(len(shortlisted_nv))},
            ],
            ["Group", "Count"],
            {"Group": 30, "Count": 8},
        )
    )
    out.append("```")
    out.append("")
    out.append("## Shortlisted NEEDS VERIFICATION (Strict)")
    out.append("")
    out.append("Criteria:")
    out.append("- Grounded category is `NEEDS VERIFICATION`")
    out.append("- Score (`Confidence`) >= 47 (median NV score for opus2)")
    out.append("- TypeMatch=Y AND (Brand match OR title similarity >= 55%)")
    out.append("- Excludes EAN mismatches (when both EANs are present and different)")
    out.append("")
    out.append(f"### NV Shortlist (n={len(shortlisted_nv)})")
    out.append("```text")
    out.append(fixed_width_table(to_table_rows(shortlisted_nv), columns, max_widths))
    out.append("```")
    out.append("")

    OUTPUT_MD.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
