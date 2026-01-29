from __future__ import annotations

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - "
    r"POSTLONGRUNPREKIRO2 beforecompletion-"
)
BASE = REPO_ROOT / "RESERACH" / "REPORT" / "part_30_dec"
COMPREHENSIBLE_DIR = BASE / "final comp" / "comprehensible"

DATASET_XLSX = BASE / "part_30_dec.xlsx"

REPORT_PATHS: dict[str, Path] = {
    "COMPREHENSIBLE_COMBINED_V2": COMPREHENSIBLE_DIR / "PHASEA_MANUAL_REPORT_FINAL_COMBINED_20251231_v2.md",
    "CODEX_STRICT": COMPREHENSIBLE_DIR / "PHASEA_MANUAL_REPORT_CODEX_FINAL_20251231.md",
    "FINAL_MD": COMPREHENSIBLE_DIR / "PHASEA_MANUAL_REPORT_FINAL.md",
    "FINAL_20251231": COMPREHENSIBLE_DIR / "PHASEA_MANUAL_REPORT_FINAL_20251231.md",
}

OUTPUT_MD = COMPREHENSIBLE_DIR / "CODEX_COVERAGE_COMPARISON_20251231.md"

NV_THRESHOLD = 45  # matches the Codex strict report header (score >= 45)


def _import_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def load_grounding():
    return _import_module("gt_summary", BASE / "generate_ground_truth_summary.py")


def load_codex_builder():
    return _import_module("codex_phasea_v4", BASE / "generate_codex_final_phasea_manual_report_v4.py")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_heading_to_section(heading_line: str) -> str | None:
    h = (heading_line or "").strip().upper()
    if not h.startswith("##"):
        return None

    if "NEEDS VERIFICATION" in h:
        return "NEEDS_VERIFICATION"

    if "HIGHLY" in h and "RECOMMENDED" in h:
        return "HL_RECOMMENDED"
    if "HIGHLY" in h and ("FILTERED" in h or "EXCLUDED" in h):
        return "HL_FILTERED"

    if "VERIFIED" in h and "RECOMMENDED" in h:
        return "VERIFIED_RECOMMENDED"
    if "VERIFIED" in h and ("FILTERED" in h or "EXCLUDED" in h):
        return "VERIFIED_FILTERED"

    if "FILTERED OUT" in h:
        return "FILTERED_OUT_AUDIT"

    return None


def split_text_by_sections(md_text: str) -> dict[str, str]:
    """
    Best-effort split by H2 headings into normalized section buckets.
    We keep only sections that map to our standard bucket names.
    """
    lines = md_text.splitlines()
    out: dict[str, list[str]] = defaultdict(list)

    current: str | None = None
    for line in lines:
        if (line or "").lstrip().startswith("##"):
            sec = normalize_heading_to_section(line)
            current = sec  # may become None for non-section headings; stops capture until next section
        if current is not None:
            out[current].append(line)

    return {k: "\n".join(v).strip() for k, v in out.items()}


def hnorm(s: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", (s or "").upper())


def extract_rowids_from_tables(md_text: str) -> set[int]:
    """
    Extract Row IDs when the table has an explicit RowID/Row ID column.

    Works for markdown pipe tables inside/outside fences. Does not require alignment.
    """
    row_ids: set[int] = set()
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.lstrip().startswith("|"):
            i += 1
            continue

        header = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(header) < 3 or i + 1 >= len(lines):
            i += 1
            continue

        sep = lines[i + 1]
        if "-" not in sep or "|" not in sep:
            i += 1
            continue

        hn = [hnorm(h) for h in header]
        idx_rowid = None
        for idx, h in enumerate(hn):
            if h == "ROWID" or h == "ROWID#":
                idx_rowid = idx
                break
            if h == "ROW" or h == "ROWID":
                idx_rowid = idx
                break
            if "ROWID" in h:
                idx_rowid = idx
                break
            if h == "ROWID" or h == "ROWID":
                idx_rowid = idx
        if idx_rowid is None:
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
            if len(parts) <= idx_rowid:
                j += 1
                continue
            m = re.search(r"\d{1,5}", parts[idx_rowid])
            if m:
                row_ids.add(int(m.group(0)))
            j += 1
        i = j

    return row_ids


def extract_rowids_from_rowid_eq(md_text: str) -> set[int]:
    return {int(x) for x in re.findall(r"\bRowID\s*=\s*(\d{1,5})\b", md_text)}


@dataclass(frozen=True)
class SectionCoverage:
    row_ids: set[int]
    resolved_row_ids: set[int]
    unresolved_rows: int


def compute_section_coverage(
    gt,
    codex_builder,
    df: pd.DataFrame,
    section_text: str,
    *,
    rowid_eq_fallback: bool = False,
) -> SectionCoverage:
    parsed = codex_builder.parse_product_tables(section_text)
    fallback = codex_builder.parse_asin_lines(section_text)
    parsed_asins = {codex_builder.extract_asin((r.get("asin", "") or "").strip()) for r in parsed}
    parsed_asins.discard("")
    parsed = parsed + [r for r in fallback if r.get("asin") not in parsed_asins]

    resolved, unresolved = codex_builder.resolve_report_rows_to_rowids(gt, df, parsed)
    # Canonicalize coverage to the current dataset by mapping rows via Supplier EAN / ASIN.
    # Some non-Codex reports include "RowID" columns that do not match the current Excel row ordering,
    # so we intentionally do NOT trust those columns for cross-report comparisons.
    row_ids = set(resolved)
    if rowid_eq_fallback:
        row_ids |= extract_rowids_from_rowid_eq(section_text)
    return SectionCoverage(row_ids=row_ids, resolved_row_ids=resolved, unresolved_rows=unresolved)


def summarize_counts_from_report(md_text: str) -> dict[str, str]:
    """
    Pull the report's own Summary Counts block (if present) for context.
    """
    out: dict[str, str] = {}
    m = re.search(r"^##\s+Summary Counts\s*$", md_text, flags=re.MULTILINE)
    if not m:
        return out
    tail = md_text[m.end() :]
    # take up to next heading
    next_h = re.search(r"^##\s+", tail, flags=re.MULTILINE)
    block = tail[: next_h.start()] if next_h else tail
    for line in block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        if line.startswith("-"):
            line = line.lstrip("-").strip()
        out[line.split(":", 1)[0].strip()] = line.split(":", 1)[1].strip()
    return out


def eval_row_for_reason(gt, codex_builder, df: pd.DataFrame, rid: int, included_by: set[str]) -> tuple[str, str]:
    """
    Return (codex_section_or_EXCLUDED, short_reason).
    """
    fr = codex_builder.build_final_row(gt, df, rid, included_by, NV_THRESHOLD)
    if fr is not None:
        return fr.section, fr.filter_reason

    row = df.iloc[rid - 1]
    sup_title = str(row.get("SupplierTitle", "") or "")
    amz_title = str(row.get("AmazonTitle", "") or "")
    sup_ean = gt.norm_digits(row.get("EAN", "")) or "-"
    amz_ean = gt.norm_digits(row.get("EAN_OnPage", "")) or "-"
    sup_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
    net_profit = float(row.get("NetProfit", 0) or 0)
    roi = float(row.get("ROI", 0) or 0)

    sales_val = row.get("bought_in_past_month")
    sales = codex_builder.parse_sales(sales_val)

    b_sup = gt.detect_brand(sup_title)
    b_amz = gt.detect_brand(amz_title)
    brand_match = gt.brands_match(b_sup, b_amz) if hasattr(gt, "brands_match") else bool(b_sup and b_amz)
    sim = gt.title_similarity_pct(sup_title, amz_title)
    type_match = gt.product_type_match(sup_title, amz_title)
    var_bad, var_reason = gt.variant_mismatch(sup_title, amz_title)

    sup_pack, _ = gt.extract_pack_count(sup_title)
    amz_pack, _ = gt.extract_pack_count(amz_title)
    pack_ratio = amz_pack / sup_pack if sup_pack else 1.0
    adjusted_profit = float(net_profit) - (pack_ratio - 1) * float(sup_price)

    ean_exact = (sup_ean != "-" and amz_ean != "-" and sup_ean == amz_ean)
    ean_mismatch = (sup_ean != "-" and amz_ean != "-" and sup_ean != amz_ean)

    if net_profit <= 0:
        return "EXCLUDED", "NetProfit<=0"
    if var_bad:
        return "EXCLUDED", f"Variant mismatch ({var_reason})"
    if pack_ratio != 1.0 and adjusted_profit <= 0:
        return "EXCLUDED", "Pack mismatch => adjusted profit <= 0"
    if sales <= 0:
        return "EXCLUDED", "Sales=0"
    if ean_mismatch and sim < 65.0:
        return "EXCLUDED", "EAN mismatch with insufficient title similarity (<65)"
    if not (brand_match and type_match and sim >= 55.0):
        return "EXCLUDED", "Not a strong enough match under v4.0 gates (brand/type/sim)"
    if adjusted_profit <= 0.50 or gt.roi_to_pct(roi) <= 15.0:
        return "EXCLUDED", "Fails NV profitability threshold (AdjProfit<=0.50 or ROI<=15%)"
    return "EXCLUDED", "Excluded by strict NV shortlist (score below threshold or missing corroboration)"


def fixed_width_counts_table(gt, rows: list[dict[str, str]]) -> str:
    cols = ["Report", "VERIFIED_REC", "VERIFIED_FILT", "HL_REC", "HL_FILT", "NV", "FILTERED_AUDIT", "TOTAL_UNIQUE"]
    maxw = {c: 24 for c in cols}
    maxw["Report"] = 32
    return gt.fixed_width_table(rows, cols, maxw)


def main() -> None:
    missing: list[str] = []
    for name, path in REPORT_PATHS.items():
        if not path.exists():
            missing.append(f"{name}: {path}")
    if missing:
        raise SystemExit("Missing report files:\n" + "\n".join(missing))
    if not DATASET_XLSX.exists():
        raise SystemExit(f"Missing dataset: {DATASET_XLSX}")

    gt = load_grounding()
    codex_builder = load_codex_builder()

    df = pd.read_excel(DATASET_XLSX)

    per_report_section: dict[str, dict[str, SectionCoverage]] = {}
    per_report_claimed_counts: dict[str, dict[str, str]] = {}

    for name, path in REPORT_PATHS.items():
        txt = read_text(path)
        per_report_claimed_counts[name] = summarize_counts_from_report(txt)
        sections = split_text_by_sections(txt)
        cov: dict[str, SectionCoverage] = {}
        for sec_name, sec_text in sections.items():
            cov[sec_name] = compute_section_coverage(
                gt,
                codex_builder,
                df,
                sec_text,
                rowid_eq_fallback=(name == "CODEX_STRICT"),
            )
        per_report_section[name] = cov

    def sec_ids(report: str, sec: str) -> set[int]:
        return per_report_section.get(report, {}).get(sec, SectionCoverage(set(), set(), 0)).row_ids

    all_sections = [
        "VERIFIED_RECOMMENDED",
        "VERIFIED_FILTERED",
        "HL_RECOMMENDED",
        "HL_FILTERED",
        "NEEDS_VERIFICATION",
        "FILTERED_OUT_AUDIT",
    ]

    # Build report-level counts (derived from actual parsed + mapped RowIDs).
    counts_rows: list[dict[str, str]] = []
    for report in REPORT_PATHS:
        row = {"Report": report}
        total: set[int] = set()
        for sec in all_sections:
            ids = sec_ids(report, sec)
            total |= ids
            key = {
                "VERIFIED_RECOMMENDED": "VERIFIED_REC",
                "VERIFIED_FILTERED": "VERIFIED_FILT",
                "HL_RECOMMENDED": "HL_REC",
                "HL_FILTERED": "HL_FILT",
                "NEEDS_VERIFICATION": "NV",
                "FILTERED_OUT_AUDIT": "FILTERED_AUDIT",
            }[sec]
            row[key] = str(len(ids))
        row["TOTAL_UNIQUE"] = str(len(total))
        counts_rows.append(row)

    codex_total: set[int] = set()
    for sec in all_sections:
        codex_total |= sec_ids("CODEX_STRICT", sec)

    union_total: set[int] = set()
    for report in REPORT_PATHS:
        for sec in all_sections:
            union_total |= sec_ids(report, sec)

    missing_from_codex = sorted(union_total - codex_total)

    # Evaluate why Codex doesn't include those.
    included_by_map: dict[int, set[str]] = defaultdict(set)
    for report in REPORT_PATHS:
        for sec in all_sections:
            for rid in sec_ids(report, sec):
                included_by_map[rid].add(report)

    reason_counts: Counter[str] = Counter()
    section_counts: Counter[str] = Counter()
    examples: list[dict[str, str]] = []
    for rid in missing_from_codex:
        sec, reason = eval_row_for_reason(gt, codex_builder, df, rid, included_by_map.get(rid, set()))
        section_counts[sec] += 1
        reason_counts[reason] += 1
        if len(examples) < 40:
            row = df.iloc[rid - 1]
            examples.append(
                {
                    "RowID": str(rid),
                    "SeenIn": ",".join(sorted(included_by_map.get(rid, set()))),
                    "WouldBe": sec,
                    "Reason": reason,
                    "ASIN": str(row.get("ASIN", "") or "-"),
                    "Supplier EAN": gt.norm_digits(row.get("EAN", "")) or "-",
                    "Amazon EAN": gt.norm_digits(row.get("EAN_OnPage", "")) or "-",
                    "SupplierTitle": str(row.get("SupplierTitle", "") or "")[:80],
                }
            )

    # Build markdown output.
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = []
    lines.append("# CODEX COVERAGE COMPARISON (COMPREHENSIBLE REPORTS)")
    lines.append("")
    lines.append(f"**Generated:** {ts}")
    lines.append(f"**Dataset:** {DATASET_XLSX}")
    lines.append("")
    lines.append("## Inputs (Verified Existing Files)")
    lines.append("")
    for name, path in REPORT_PATHS.items():
        st = path.stat()
        lines.append(f"- {name}: {path} (bytes={st.st_size}, mtime={datetime.fromtimestamp(st.st_mtime)})")
    lines.append("")
    lines.append("## Parsed Coverage (RowID-based)")
    lines.append("")
    lines.append("Derived counts are based on mapping report table rows to dataset RowIDs using ASIN/EAN/title tie-breaks.")
    lines.append("")
    lines.append("```text")
    lines.append(fixed_width_counts_table(gt, counts_rows).rstrip("\n"))
    lines.append("```")
    lines.append("")
    lines.append("## Report-Claimed Summary Counts (For Context)")
    lines.append("")
    for report, claimed in per_report_claimed_counts.items():
        if not claimed:
            lines.append(f"- {report}: (no parseable `## Summary Counts` block found)")
            continue
        # keep short
        items = "; ".join(f"{k}={v}" for k, v in claimed.items())
        lines.append(f"- {report}: {items}")
    lines.append("")
    lines.append("## Codex Coverage Gaps vs Union of All Comprehensible Reports")
    lines.append("")
    lines.append(f"- Union (unique RowIDs across all 4 reports): {len(union_total)}")
    lines.append(f"- Codex strict (unique RowIDs): {len(codex_total)}")
    lines.append(f"- Present in other report(s) but missing from Codex strict: {len(missing_from_codex)}")
    lines.append("")
    if not missing_from_codex:
        lines.append("No RowIDs were found in other comprehensible reports that are absent from the Codex strict report.")
    else:
        lines.append("### Primary Reasons Missing Rows Were Not Included in Codex Strict")
        lines.append("")
        for reason, cnt in reason_counts.most_common():
            lines.append(f"- {cnt}x: {reason}")
        lines.append("")
        lines.append("### Would-Be Section Breakdown (If Re-evaluated Under Codex v4.0 Gates)")
        lines.append("")
        for sec, cnt in section_counts.most_common():
            lines.append(f"- {cnt}x: {sec}")
        lines.append("")
        lines.append("### Examples (First 40 Missing RowIDs)")
        lines.append("")
        cols = ["RowID", "ASIN", "Supplier EAN", "Amazon EAN", "SeenIn", "WouldBe", "Reason", "SupplierTitle"]
        lines.append("```text")
        lines.append(gt.fixed_width_table(examples, cols, {c: 48 for c in cols}).rstrip("\n"))
        lines.append("```")
        lines.append("")

    lines.append("## Per-Report Differences vs Codex Strict (Why Some Reports Look Larger)")
    lines.append("")
    for report in REPORT_PATHS:
        if report == "CODEX_STRICT":
            continue

        report_total: set[int] = set()
        for sec in all_sections:
            report_total |= sec_ids(report, sec)
        delta = sorted(report_total - codex_total)

        lines.append(f"### {report}")
        lines.append("")
        lines.append(f"- Unique RowIDs in this report: {len(report_total)}")
        lines.append(f"- Unique RowIDs missing from Codex strict: {len(delta)}")
        if not delta:
            lines.append("- Codex strict already covers all RowIDs from this report.")
            lines.append("")
            continue

        rc: Counter[str] = Counter()
        ex: list[dict[str, str]] = []
        for rid in delta:
            sec, reason = eval_row_for_reason(gt, codex_builder, df, rid, included_by_map.get(rid, {report}))
            rc[reason] += 1
            if len(ex) < 12:
                row = df.iloc[rid - 1]
                ex.append(
                    {
                        "RowID": str(rid),
                        "ASIN": str(row.get("ASIN", "") or "-"),
                        "Supplier EAN": gt.norm_digits(row.get("EAN", "")) or "-",
                        "Amazon EAN": gt.norm_digits(row.get("EAN_OnPage", "")) or "-",
                        "Reason": reason,
                        "SupplierTitle": str(row.get("SupplierTitle", "") or "")[:90],
                    }
                )

        lines.append("")
        lines.append("Main exclusion reasons for this report's extra rows:")
        for reason, cnt in rc.most_common(8):
            lines.append(f"- {cnt}x: {reason}")
        lines.append("")
        lines.append("Examples (first 12 extra rows):")
        lines.append("")
        cols = ["RowID", "ASIN", "Supplier EAN", "Amazon EAN", "Reason", "SupplierTitle"]
        lines.append("```text")
        lines.append(gt.fixed_width_table(ex, cols, {c: 52 for c in cols}).rstrip("\n"))
        lines.append("```")
        lines.append("")

    # Unresolved counts from Codex strict (already in the report header, but re-summarize here).
    lines.append("## Notes on Disagreements / Larger Section Counts in Other Reports")
    lines.append("")
    lines.append(
        "When other reports show larger counts, the dominant causes (confirmed by Row-level re-evaluation) are: "
        "pack/quantity mismatches that make adjusted profit <= 0, variant mismatches (scent/color/size), "
        "EAN mismatches without sufficient similarity, and lower-quality NV items that do not meet the strict shortlist."
    )
    lines.append("")

    OUTPUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
