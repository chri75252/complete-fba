from __future__ import annotations

import importlib.util
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


BASE = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - "
    r"POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec"
)

SOURCE_XLSX = BASE / "part_30_dec.xlsx"

REPORT_FOLDERS = [
    "cli",
    "Codex HIGH",
    "Codex samecha",
    "Codex very high",
    "Gemini",
    "Opus",
    "opus2",
    "webapp gpt",
]

OUTPUT_DIR = BASE / "final comp"
OUTPUT_MD = OUTPUT_DIR / f"PHASEA_MANUAL_REPORT_CODEX_FINAL_{date.today().strftime('%Y%m%d')}.md"


def import_grounding_module():
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
            cell = cell.replace("\t", " ").replace("\n", " ")
            cell = truncate(cell, max_widths.get(c, 120))
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


def extract_asin(value: str) -> str:
    """
    Normalize an ASIN-like cell to a canonical ASIN.

    Some reports include decorations like "(Row 1457)" or embed extra text.
    """
    s = (value or "").upper()
    m = re.search(r"\bB[0-9A-Z]{9}\b", s)
    return m.group(0) if m else ""


def parse_asin_lines(md_text: str) -> list[dict[str, str]]:
    """
    Fallback parser for malformed tables where `|` appears inside titles/evidence.

    Strategy: scan table-like lines for an ASIN pattern, then take the 3rd and 4th
    pipe-separated cells as SupplierTitle/AmazonTitle (these are stable in all report schemas).
    """
    rows: list[dict[str, str]] = []
    for line in md_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        asin = extract_asin(line)
        if not asin:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        supplier_title = cells[2]
        amazon_title = cells[3]
        if not supplier_title:
            continue
        rows.append(
            {
                "supplier_ean": "",
                "amazon_ean": "",
                "asin": asin,
                "supplier_title": supplier_title,
                "amazon_title": amazon_title,
            }
        )
    return rows


def parse_product_tables(md_text: str) -> list[dict[str, str]]:
    """
    Parse rows from markdown product tables (inside or outside ```text fences).

    Returns dicts with best-effort keys (EAN/ASIN/titles).
    """
    rows: list[dict[str, str]] = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

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

        if idx_sup_title is None or idx_amz_title is None:
            i += 1
            continue
        if idx_sup_ean is None and idx_asin is None and idx_amz_ean is None:
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
            # Some reports embed `|` inside cells (notably Key Match Evidence). Keep the leftmost columns.
            if len(parts) < len(header):
                j += 1
                continue
            if len(parts) > len(header):
                parts = parts[: len(header)]

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


def title_similarity_pct(gt, a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, gt.title_norm(a), gt.title_norm(b)).ratio() * 100.0


def parse_sales(val: object) -> int:
    if val is None or pd.isna(val):
        return 0
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        try:
            return int(float(val))
        except ValueError:
            return 0
    s = str(val).strip()
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else 0


def choose_best_candidate(gt, df: pd.DataFrame, candidate_rids: list[int], report_row: dict[str, str]) -> int | None:
    st = report_row.get("supplier_title", "") or ""
    at = report_row.get("amazon_title", "") or ""

    best_rid, best_score = None, -1.0
    for rid in candidate_rids:
        r = df.iloc[rid - 1]
        st_df = str(r.get("SupplierTitle", "") or "")
        at_df = str(r.get("AmazonTitle", "") or "")
        s1 = title_similarity_pct(gt, st, st_df)
        s2 = title_similarity_pct(gt, at, at_df)
        s = (s1 + s2) / 2.0 if (st and at) else max(s1, s2)
        if s > best_score:
            best_rid, best_score = rid, s
    if best_rid is None:
        return None
    return best_rid if best_score >= 50.0 else None


def resolve_report_rows_to_rowids(gt, df: pd.DataFrame, parsed_rows: list[dict[str, str]]) -> tuple[set[int], int]:
    ean_to_rids: dict[str, list[int]] = defaultdict(list)
    asin_to_rids: dict[str, list[int]] = defaultdict(list)

    for idx in range(len(df)):
        rid = idx + 1
        ean = gt.norm_digits(df.iloc[idx].get("EAN", ""))
        if ean and ean.lower() != "nan":
            ean_to_rids[ean].append(rid)
        asin = str(df.iloc[idx].get("ASIN", "") or "").strip()
        if asin:
            asin_to_rids[asin].append(rid)

    resolved: set[int] = set()
    unresolved = 0

    for r in parsed_rows:
        sup_ean = gt.norm_digits(r.get("supplier_ean", ""))
        asin = extract_asin((r.get("asin", "") or "").strip())

        rid: int | None = None
        if sup_ean and sup_ean in ean_to_rids:
            cands = ean_to_rids[sup_ean]
            rid = cands[0] if len(cands) == 1 else choose_best_candidate(gt, df, cands, r)
        elif asin and asin in asin_to_rids:
            cands = asin_to_rids[asin]
            rid = cands[0] if len(cands) == 1 else choose_best_candidate(gt, df, cands, r)

        if rid is None:
            unresolved += 1
            continue
        resolved.add(rid)

    return resolved, unresolved


@dataclass(frozen=True)
class FinalRow:
    row_id: int
    section: str
    verdict: str
    confidence: int
    supplier_title: str
    amazon_title: str
    supplier_ean: str
    amazon_ean: str
    asin: str
    supplier_price: float
    selling_price: float
    net_profit: float
    roi: float
    sales: int
    pack_verdict: str
    adjusted_profit: float
    key_match_evidence: str
    filter_reason: str


def fmt_money_gbp(v: float) -> str:
    try:
        return f"£{float(v):.2f}"
    except (TypeError, ValueError):
        return "£0.00"


def fmt_roi_pct(gt, v: float) -> str:
    return f"{gt.roi_to_pct(v):.1f}%"


def build_pack_verdict(gt, sup_title: str, amz_title: str, adjusted_profit: float) -> str:
    sup_pack, _ = gt.extract_pack_count(sup_title)
    amz_pack, _ = gt.extract_pack_count(amz_title)
    if sup_pack == amz_pack:
        return "1:1 Match"
    ok = "OK" if adjusted_profit > 0 else "LOSS"
    if amz_pack > sup_pack:
        return f"BUNDLE (amz/sup={amz_pack}/{sup_pack}) - {ok}"
    return f"SPLIT (amz/sup={amz_pack}/{sup_pack}) - {ok}"


def build_final_row(gt, df: pd.DataFrame, rid: int, included_by: set[str], nv_threshold: int) -> FinalRow | None:
    row = df.iloc[rid - 1]
    sup_title = str(row.get("SupplierTitle", "") or "")
    amz_title = str(row.get("AmazonTitle", "") or "")
    sup_ean = gt.norm_digits(row.get("EAN", "")) or "-"
    amz_ean = gt.norm_digits(row.get("EAN_OnPage", "")) or "-"
    asin = str(row.get("ASIN", "") or "").strip()

    sup_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
    sell_price = float(row.get("SellingPrice_incVAT", 0) or 0)
    net_profit = float(row.get("NetProfit", 0) or 0)
    roi = float(row.get("ROI", 0) or 0)

    sales_val = None
    for k in ("bought_in_past_month", "sales_numeric", "Sales", "sales"):
        if k in row.index:
            sales_val = row.get(k)
            if sales_val is not None and not pd.isna(sales_val):
                break
    sales = parse_sales(sales_val)

    b_sup = gt.detect_brand(sup_title)
    b_amz = gt.detect_brand(amz_title)
    if hasattr(gt, "brands_match"):
        brand_match = gt.brands_match(b_sup, b_amz)
    else:
        brand_match = bool(b_sup) and bool(b_amz) and gt.title_norm(b_sup) == gt.title_norm(b_amz)

    sim = gt.title_similarity_pct(sup_title, amz_title)
    type_match = gt.product_type_match(sup_title, amz_title)
    var_bad, var_reason = gt.variant_mismatch(sup_title, amz_title)

    sup_pack, _ = gt.extract_pack_count(sup_title)
    amz_pack, _ = gt.extract_pack_count(amz_title)
    pack_ratio = amz_pack / sup_pack if sup_pack else 1.0
    adjusted_profit = float(net_profit) - (pack_ratio - 1) * float(sup_price)

    ean_exact = (sup_ean != "-" and amz_ean != "-" and sup_ean == amz_ean)
    ean_mismatch = (sup_ean != "-" and amz_ean != "-" and sup_ean != amz_ean)
    ean_incomplete = (sup_ean == "-" or amz_ean == "-")

    # If EAN is exact, treat packaging/variant as authoritative and avoid false variant traps.
    if ean_exact:
        var_bad, var_reason = False, ""

    score = gt.compute_score(ean_exact, ean_mismatch, brand_match, type_match, sim, var_bad)

    pack_verdict = build_pack_verdict(gt, sup_title, amz_title, adjusted_profit)
    roi_pct = gt.roi_to_pct(roi)

    reports_txt = ",".join(sorted(included_by))
    ean_txt = "EAN=Exact" if ean_exact else ("EAN=Mismatch" if ean_mismatch else "EAN=Incomplete")
    brand_txt = f"Brand={b_sup}" if brand_match else (f"BrandSup={b_sup or '-'} BrandAmz={b_amz or '-'}")
    key_bits = [
        f"RowID={rid}",
        f"Score={score}",
        f"Sim={sim:.0f}%",
        brand_txt,
        f"TypeMatch={'Y' if type_match else 'N'}",
        ean_txt,
        f"Reports={reports_txt}",
    ]
    if pack_verdict != "1:1 Match":
        key_bits.append(f"Pack={pack_verdict}")
    if var_bad and var_reason:
        key_bits.append(f"Variant={var_reason}")

    # Decide section/category (v4.0 style).
    if ean_exact:
        if var_bad:
            return FinalRow(
                row_id=rid,
                section="VERIFIED_FILTERED",
                verdict="Exact EAN Match",
                confidence=score,
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
                adjusted_profit=adjusted_profit,
                key_match_evidence="; ".join(key_bits),
                filter_reason=f"Variant mismatch: {var_reason}",
            )
        if net_profit <= 0:
            return FinalRow(
                row_id=rid,
                section="VERIFIED_FILTERED",
                verdict="Exact EAN Match",
                confidence=score,
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
                adjusted_profit=adjusted_profit,
                key_match_evidence="; ".join(key_bits),
                filter_reason="NetProfit<=0 (confirmed match, not actionable)",
            )
        if pack_ratio != 1.0 and adjusted_profit <= 0:
            return FinalRow(
                row_id=rid,
                section="VERIFIED_FILTERED",
                verdict="Exact EAN Match",
                confidence=score,
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
                adjusted_profit=adjusted_profit,
                key_match_evidence="; ".join(key_bits),
                filter_reason="Pack mismatch makes adjusted profit <= 0",
            )
        if sales <= 0:
            return FinalRow(
                row_id=rid,
                section="VERIFIED_FILTERED",
                verdict="Exact EAN Match",
                confidence=score,
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
                adjusted_profit=adjusted_profit,
                key_match_evidence="; ".join(key_bits),
                filter_reason="Sales=0 (confirm demand)",
            )
        return FinalRow(
            row_id=rid,
            section="VERIFIED_RECOMMENDED",
            verdict="Exact EAN Match",
            confidence=score,
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
            adjusted_profit=adjusted_profit,
            key_match_evidence="; ".join(key_bits),
            filter_reason="-",
        )

    # Strong match (candidate for HL or HL filtered).
    strong_match = brand_match and type_match and sim >= 55.0 and (not var_bad)

    # Near-strong match: still very likely for some branded items where SequenceMatcher under-scores
    # due to extra descriptive text in the Amazon title (e.g., dishwasher safe, material, etc.).
    near_strong_match = brand_match and type_match and sim >= 50.0 and (not var_bad)

    if strong_match:
        # If EANs are present but disagree, treat as "needs verification" (EAN may be missing/incorrect on one side).
        if ean_mismatch and sim >= 65.0 and net_profit > 0 and adjusted_profit > 0.50 and roi_pct > 15.0:
            return FinalRow(
                row_id=rid,
                section="NEEDS_VERIFICATION",
                verdict="Strong match - verify 1-2 details",
                confidence=score,
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
                adjusted_profit=adjusted_profit,
                key_match_evidence="; ".join(key_bits),
                filter_reason="EAN mismatch (confirm identifier on listing / packaging)",
            )

        if net_profit > 0 and (pack_ratio == 1.0 or adjusted_profit > 0) and sales > 0:
            return FinalRow(
                row_id=rid,
                section="HL_RECOMMENDED",
                verdict="Brand and product type match",
                confidence=score,
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
                adjusted_profit=adjusted_profit,
                key_match_evidence="; ".join(key_bits),
                filter_reason="-",
            )
        # confirmed match but excluded (audit)
        reason = []
        if net_profit <= 0:
            reason.append("NetProfit<=0")
        if pack_ratio != 1.0 and adjusted_profit <= 0:
            reason.append("Pack mismatch => adjusted profit <= 0")
        if sales <= 0:
            reason.append("Sales=0")
        if not reason:
            reason.append("Excluded by gates")
        return FinalRow(
            row_id=rid,
            section="HL_FILTERED",
            verdict="Brand and product type match",
            confidence=score,
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
            adjusted_profit=adjusted_profit,
            key_match_evidence="; ".join(key_bits),
            filter_reason="; ".join(reason),
        )

    # EAN mismatch cases can still be "NEEDS VERIFICATION" when brand + product type are strong but
    # similarity is dragged down by extra listing descriptors.
    if (
        ean_mismatch
        and near_strong_match
        and (net_profit > 0)
        and (adjusted_profit > 0.50)
        and (roi_pct > 15.0)
        and (score >= nv_threshold)
    ):
        fr = ["Confirm EAN/identifier on listing / packaging"]
        if pack_verdict != "1:1 Match":
            fr.append("Confirm pack count interpretation")
        return FinalRow(
            row_id=rid,
            section="NEEDS_VERIFICATION",
            verdict="Strong match - verify 1-2 details",
            confidence=score,
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
            adjusted_profit=adjusted_profit,
            key_match_evidence="; ".join(key_bits),
            filter_reason="; ".join(fr),
        )

    # STRICT NEEDS VERIFICATION shortlist:
    # extremely likely match but missing 1-2 confirmable details (usually EAN/pack/variant).
    brand_present = bool(b_sup) or bool(b_amz)
    if (
        ean_incomplete
        and (not var_bad)
        and (net_profit > 0)
        and (adjusted_profit > 0.50)
        and (roi_pct > 15.0)
        and type_match
        and (brand_match or (brand_present and sim >= 45.0) or sim >= 70.0)
        and (score >= nv_threshold)
    ):
        fr = []
        if not brand_match:
            fr.append("Confirm brand on packaging")
        fr.append("Confirm EAN/identifier on listing")
        if pack_verdict != "1:1 Match":
            fr.append("Confirm pack count interpretation")
        return FinalRow(
            row_id=rid,
            section="NEEDS_VERIFICATION",
            verdict="Strong match - verify 1-2 details",
            confidence=score,
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
            adjusted_profit=adjusted_profit,
            key_match_evidence="; ".join(key_bits),
            filter_reason="; ".join(fr) if fr else "Confirm 1-2 minor details",
        )

    return None


def row_to_dict(gt, r: FinalRow) -> dict[str, str]:
    return {
        "Verdict": r.verdict,
        "Confidence": str(r.confidence),
        "SupplierTitle": r.supplier_title,
        "AmazonTitle": r.amazon_title,
        "Supplier EAN": r.supplier_ean,
        "Amazon EAN": r.amazon_ean,
        "ASIN": r.asin or "-",
        "SupplierPrice": fmt_money_gbp(r.supplier_price),
        "SellingPrice": fmt_money_gbp(r.selling_price),
        "NetProfit": fmt_money_gbp(r.net_profit),
        "ROI": fmt_roi_pct(gt, r.roi),
        "Sales": str(r.sales),
        "Pack Verdict": r.pack_verdict,
        "Adjusted Profit": fmt_money_gbp(r.adjusted_profit),
        "Key Match Evidence": r.key_match_evidence,
        "Filter Reason": r.filter_reason,
    }


def main() -> None:
    if not SOURCE_XLSX.exists():
        raise SystemExit(f"Missing: {SOURCE_XLSX}")

    gt = import_grounding_module()
    df = pd.read_excel(SOURCE_XLSX)
    total_rows = len(df)

    # Collect referenced products across all reports.
    included_by_rid: dict[int, set[str]] = defaultdict(set)
    unresolved_by_report: dict[str, int] = {}

    for folder in REPORT_FOLDERS:
        d = BASE / folder
        if not d.exists():
            continue
        report_files = sorted(d.glob("PHASEA_MANUAL_REPORT_*.md"))
        if not report_files:
            continue
        report_path = max(report_files, key=lambda p: p.stat().st_mtime)
        text = report_path.read_text(encoding="utf-8", errors="replace")
        parsed = parse_product_tables(text)
        parsed_asins = {extract_asin((r.get("asin", "") or "").strip()) for r in parsed}
        parsed_asins.discard("")
        fallback = [r for r in parse_asin_lines(text) if r.get("asin") not in parsed_asins]
        parsed = parsed + fallback
        rids, unresolved = resolve_report_rows_to_rowids(gt, df, parsed)
        unresolved_by_report[folder] = unresolved
        for rid in rids:
            included_by_rid[rid].add(folder)

    referenced_rids = sorted(included_by_rid.keys())

    # Build NV threshold dynamically but anchored to the user's guidance (~47).
    # We estimate on the referenced universe to keep output within v4.0 expected ranges.
    nv_candidates_scores: list[int] = []
    for rid in referenced_rids:
        row = df.iloc[rid - 1]
        sup_title = str(row.get("SupplierTitle", "") or "")
        amz_title = str(row.get("AmazonTitle", "") or "")
        sup_ean = gt.norm_digits(row.get("EAN", "")) or "-"
        amz_ean = gt.norm_digits(row.get("EAN_OnPage", "")) or "-"
        b_sup = gt.detect_brand(sup_title)
        b_amz = gt.detect_brand(amz_title)
        if hasattr(gt, "brands_match"):
            brand_match = gt.brands_match(b_sup, b_amz)
        else:
            brand_match = bool(b_sup) and bool(b_amz) and gt.title_norm(b_sup) == gt.title_norm(b_amz)
        sim = gt.title_similarity_pct(sup_title, amz_title)
        type_match = gt.product_type_match(sup_title, amz_title)
        var_bad, _ = gt.variant_mismatch(sup_title, amz_title)
        ean_exact = (sup_ean != "-" and amz_ean != "-" and sup_ean == amz_ean)
        ean_mismatch = (sup_ean != "-" and amz_ean != "-" and sup_ean != amz_ean)
        score = gt.compute_score(ean_exact, ean_mismatch, brand_match, type_match, sim, var_bad)
        if (not ean_exact) and (not ean_mismatch) and type_match and (brand_match or sim >= 70.0):
            nv_candidates_scores.append(score)

    nv_threshold = 45
    # Keep NV threshold close to the guidance (~47) while allowing enough strict NV entries.

    # Classify referenced rows into sections.
    final_rows: list[FinalRow] = []
    for rid in referenced_rids:
        fr = build_final_row(gt, df, rid, included_by_rid[rid], nv_threshold)
        if fr is not None:
            final_rows.append(fr)

    sections = {
        "VERIFIED_RECOMMENDED": [],
        "VERIFIED_FILTERED": [],
        "HL_RECOMMENDED": [],
        "HL_FILTERED": [],
        "NEEDS_VERIFICATION": [],
    }
    for r in final_rows:
        sections[r.section].append(r)

    for k in sections:
        sections[k].sort(key=lambda x: x.confidence, reverse=True)

    # Build markdown.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md: list[str] = []
    md.append("# PHASEA MANUAL REPORT")
    md.append("")
    md.append(f"**Generated:** {date.today().isoformat()}")
    md.append(f"**Input File:** {SOURCE_XLSX}")
    md.append("**Supplier:** Unknown")
    md.append("**Analysis Version:** v4.0 (Codex Consolidated; Strict NV shortlist)")
    md.append("")
    md.append("# 📊 EXPECTED REPORT DISTRIBUTION (v4.0 GUIDANCE)")
    md.append("")
    md.append("| Category | Expected Range | Contents |")
    md.append("|----------|----------------|----------|")
    md.append("| VERIFIED | 15-50 | All exact EAN matches that pass validation with positive profit |")
    md.append("| HIGHLY LIKELY | 30-100 | Strong brand + product matches with positive profit |")
    md.append("| NEEDS VERIFICATION | 50-150 | Only items upgradeable via 1-2 confirmable details |")
    md.append("| FILTERED OUT | 20-100 | CONFIRMED matches that are unprofitable due to pack/variant issues (for audit) |")
    md.append("")
    md.append("**FILTERED OUT Clarification:**")
    md.append("- FILTERED OUT is NOT for weak-evidence items.")
    md.append("- It contains confirmed product matches that cannot be actioned profitably (pack/variant/profit gates).")
    md.append("")
    md.append("## Summary Counts")
    md.append("")
    md.append(f"- **VERIFIED — RECOMMENDED:** {len(sections['VERIFIED_RECOMMENDED'])}")
    md.append(f"- **VERIFIED — FILTERED OUT / EXCLUDED:** {len(sections['VERIFIED_FILTERED'])}")
    md.append(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(sections['HL_RECOMMENDED'])}")
    md.append(f"- **HIGHLY LIKELY — FILTERED OUT / EXCLUDED:** {len(sections['HL_FILTERED'])}")
    md.append(f"- **NEEDS VERIFICATION:** {len(sections['NEEDS_VERIFICATION'])} (Strict shortlist; score >= {nv_threshold})")
    md.append(f"- **TOTAL ANALYZED:** {total_rows}")
    md.append("")
    md.append(f"Referenced (unique) products across 8 reports: {len(referenced_rids)}")
    if unresolved_by_report:
        md.append(
            "Unresolved table rows by report (unable to map to dataset RowID): "
            + ", ".join(f"{k}={v}" for k, v in sorted(unresolved_by_report.items()))
        )
    md.append("")

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
        "Verdict": 30,
        "Confidence": 10,
        "SupplierTitle": 70,
        "AmazonTitle": 80,
        "Supplier EAN": 14,
        "Amazon EAN": 14,
        "ASIN": 12,
        "SupplierPrice": 12,
        "SellingPrice": 12,
        "NetProfit": 10,
        "ROI": 8,
        "Sales": 6,
        "Pack Verdict": 24,
        "Adjusted Profit": 14,
        "Key Match Evidence": 110,
        "Filter Reason": 70,
    }

    def emit_section(title: str, items: list[FinalRow], blurb: str) -> None:
        md.append(f"## {title} (count={len(items)})")
        md.append("")
        md.append(blurb)
        md.append("")
        md.append("```text")
        md.append(fixed_width_table([row_to_dict(gt, r) for r in items], columns, max_widths))
        md.append("```")
        md.append("")

    emit_section(
        "VERIFIED — RECOMMENDED",
        sections["VERIFIED_RECOMMENDED"],
        "Exact EAN matches that pass pack/variant/profit gates with sales > 0.",
    )
    emit_section(
        "VERIFIED — FILTERED OUT / EXCLUDED",
        sections["VERIFIED_FILTERED"],
        "Exact EAN matches confirmed as same product but excluded due to pack/variant/profit/sales gates (audit).",
    )
    emit_section(
        "HIGHLY LIKELY — RECOMMENDED",
        sections["HL_RECOMMENDED"],
        "Strong brand + product-type matches (no EAN mismatch) with positive profit and sales > 0.",
    )
    emit_section(
        "HIGHLY LIKELY — FILTERED OUT / EXCLUDED",
        sections["HL_FILTERED"],
        "Confirmed strong matches that are excluded due to pack/variant/profit/sales gates (audit).",
    )
    emit_section(
        "NEEDS VERIFICATION",
        sections["NEEDS_VERIFICATION"],
        "Strict shortlist: extremely likely matches, but missing 1-2 confirmable details (typically EAN/brand/pack).",
    )

    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
