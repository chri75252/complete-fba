from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from fba_agent.constants import TABLE_COLUMNS
from fba_agent.text import sanitize_cell


def _fmt_money(value: object) -> str:
    if value is None:
        return "-"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "-"
    return f"£{f:.2f}"


def _fmt_pct(value: object) -> str:
    if value is None:
        return "-"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "-"
    return f"{f:.1f}%"


def _fmt_int(value: object) -> str:
    if value is None:
        return "-"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "-"
    # Check for NaN - cannot convert to int
    import math
    if math.isnan(f):
        return "-"
    if f.is_integer():
        return str(int(f))
    return str(int(round(f)))


def _fixed_width_table(rows: list[dict[str, str]]) -> str:
    cols = TABLE_COLUMNS
    widths: dict[str, int] = {c: len(c) for c in cols}

    for row in rows:
        for c in cols:
            widths[c] = max(widths[c], len(row.get(c, "")))

    def fmt_row(values: dict[str, str]) -> str:
        parts = []
        for c in cols:
            v = values.get(c, "")
            parts.append(v.ljust(widths[c]))
        return "| " + " | ".join(parts) + " |"

    header = fmt_row({c: c for c in cols})
    sep = "|-" + "-|-".join("-" * widths[c] for c in cols) + "-|"
    lines = [header, sep]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def _ledger_to_table_rows(ledger: pd.DataFrame, verdict_override: str | None = None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for _, r in ledger.iterrows():
        verdict = verdict_override or str(r.get("bucket") or "")
        out.append(
            {
                "Verdict": sanitize_cell(verdict),
                "Confidence": sanitize_cell(str(int(r.get("confidence") or 0))),
                "SupplierTitle": sanitize_cell(str(r.get("supplier_title") or "")),
                "AmazonTitle": sanitize_cell(str(r.get("amazon_title") or "")),
                "Supplier EAN": sanitize_cell(str(r.get("supplier_ean") or "-")),
                "Amazon EAN": sanitize_cell(str(r.get("amazon_ean") or "-")),
                "ASIN": sanitize_cell(str(r.get("asin") or "")),
                "SupplierPrice": sanitize_cell(_fmt_money(r.get("supplier_price"))),
                "SellingPrice": sanitize_cell(_fmt_money(r.get("selling_price"))),
                "NetProfit": sanitize_cell(_fmt_money(r.get("net_profit"))),
                "ROI": sanitize_cell(_fmt_pct(r.get("roi"))),
                "Sales": sanitize_cell(_fmt_int(r.get("sales"))),
                "Pack Verdict": sanitize_cell(str(r.get("pack_verdict") or "")),
                "Adjusted Profit": sanitize_cell(_fmt_money(r.get("adjusted_profit"))),
                "Key Match Evidence": sanitize_cell(str(r.get("key_match_evidence") or "-")),
                "Filter Reason": sanitize_cell(str(r.get("filter_reason") or "-")),
            }
        )
    return out


def render_phasea_report(
    ledger: pd.DataFrame,
    *,
    input_file: str,
    supplier: str,
    generated_date: str | None = None,
) -> str:
    generated_date = generated_date or date.today().isoformat()

    include_mask = ledger["include_in_tables"].astype(bool)
    included = ledger[include_mask]
    unrelated_count = int((~include_mask).sum())

    verified_rec = included[(included["track"] == "VERIFIED") & (included["bucket"] == "VERIFIED")]
    verified_fo = included[(included["track"] == "VERIFIED") & (included["bucket"] == "FILTERED_OUT")]
    hl_rec = included[(included["track"] == "HIGHLY_LIKELY") & (included["bucket"] == "HIGHLY_LIKELY")]
    hl_fo = included[(included["track"] == "HIGHLY_LIKELY") & (included["bucket"] == "FILTERED_OUT")]
    needs_ver = included[included["bucket"].isin(["NEEDS_VERIFICATION", "NEEDS VERIFICATION"])]  # FIX #3: Handle both variants

    total = int(len(ledger))

    lines: list[str] = []
    lines.append("# PHASEA MANUAL REPORT")
    lines.append("")
    lines.append(f"**Generated:** {generated_date}")
    lines.append(f"**Input File:** {input_file}")
    lines.append(f"**Supplier:** {supplier}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append("")
    lines.append(f"- VERIFIED - RECOMMENDED: {len(verified_rec)}")
    lines.append(f"- VERIFIED - AUDITED OUT: {len(verified_fo)}")
    lines.append(f"- HIGHLY LIKELY - RECOMMENDED: {len(hl_rec)}")
    lines.append(f"- HIGHLY LIKELY - AUDITED OUT: {len(hl_fo)}")
    lines.append(f"- NEEDS VERIFICATION: {len(needs_ver)}")
    lines.append(f"- UNRELATED / NOT INCLUDED: {unrelated_count}")
    lines.append(f"- **TOTAL ANALYZED: {total}**")
    lines.append("")

    def section(title: str, df: pd.DataFrame) -> None:
        lines.append(f"## {title} (count={len(df)})")
        if len(df) == 0:
            lines.append("")
            return
        # SORT BY CONFIDENCE DESCENDING (highest score first)
        if "confidence" in df.columns:
            df = df.sort_values("confidence", ascending=False)
        rows = _ledger_to_table_rows(df)
        lines.append("```text")
        lines.append(_fixed_width_table(rows))
        lines.append("```")
        lines.append("")

    section("VERIFIED - RECOMMENDED", verified_rec)
    section("VERIFIED - AUDITED OUT", verified_fo)
    section("HIGHLY LIKELY - RECOMMENDED", hl_rec)
    section("HIGHLY LIKELY - AUDITED OUT", hl_fo)
    section("NEEDS VERIFICATION", needs_ver)

    # Reconciliation (no duplicates, no missing) is enforced by validation gates; still display summary.
    lines.append("## Reconciliation")
    lines.append("")
    lines.append(
        f"- VERIFIED({len(verified_rec) + len(verified_fo)}) + HIGHLY_LIKELY({len(hl_rec) + len(hl_fo)}) + "
        f"NEEDS_VERIFICATION({len(needs_ver)}) + UNRELATED({unrelated_count}) = TOTAL({total})"
    )
    lines.append("")

    return "\n".join(lines)
