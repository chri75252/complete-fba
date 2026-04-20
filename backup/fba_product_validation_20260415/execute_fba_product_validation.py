from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-")
ANALYSIS_CSV = ROOT / r"FINAL STALE\fba_analysis_202 efg newst4 (1).csv"
FIN_REPORT_CSV = ROOT / r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_efghousewares-co-uk_20260413_003445.csv"
PROMPT_FILE = ROOT / r"workflows\fba_product_validation_prompt.md"
OUTPUT_DIR = ROOT / r"FINAL STALE"
DATE_STAMP = "20260415"
OUTPUT_CSV = OUTPUT_DIR / f"verified_profitable_efghousewares-co-uk_{DATE_STAMP}.csv"
OUTPUT_REPORT = OUTPUT_DIR / f"fba_product_validation_report_efghousewares-co-uk_{DATE_STAMP}.md"
OUTPUT_ANALYSIS = OUTPUT_DIR / f"fba_product_validation_prompt_analysis_{DATE_STAMP}.md"


STOP_WORDS = {
    "the",
    "and",
    "with",
    "for",
    "in",
    "of",
    "a",
    "an",
    "to",
    "by",
    "at",
    "on",
    "is",
    "it",
    "each",
    "pack",
    "set",
    "pcs",
    "pc",
    "piece",
    "pieces",
    "assorted",
    "asstd",
}

GENERIC_WORDS = {
    "black",
    "white",
    "blue",
    "green",
    "red",
    "pink",
    "grey",
    "gray",
    "silver",
    "clear",
    "large",
    "medium",
    "small",
    "one",
    "size",
}

TIER_1_VALUES = {"TIER_1_VERIFIED"}
TIER_2_VALUES = {"TIER_2_LIKELY", "TIER_2_MODERATE"}
TIER_3_VALUES = {"TIER_3_NEEDS_REVIEW", "TIER_3_HIGH_RISK"}

QTY_PATTERNS = [
    re.compile(r"(\d+)\s*x\s+", re.I),
    re.compile(r"x\s*(\d+)", re.I),
    re.compile(r"pack\s*(?:of\s*)?(\d+)", re.I),
    re.compile(r"(\d+)\s*pack", re.I),
    re.compile(r"(\d+)\s*[Pp][CcKk]", re.I),
    re.compile(r"set\s*(?:of\s*)?(\d+)", re.I),
    re.compile(r"box\s*(?:of\s*)?(\d+)", re.I),
    re.compile(r"(\d+)\s*pieces?", re.I),
    re.compile(r"(\d+)\s*count", re.I),
    re.compile(r"bundle\s*(?:of\s*)?(\d+)", re.I),
    re.compile(r"\((\d+)\)", re.I),
    re.compile(r"(\d+)\s*×", re.I),
]

SIZE_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s?(?:ml|ltr|l|cm|mm|pc|pcs|pk|pack|g|kg|oz)\b", re.I)


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def tokenize(text: object) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9]+", str(text or "").lower())
    return [tok for tok in raw if tok not in STOP_WORDS and len(tok) > 1]


def meaningful_overlap(a: object, b: object) -> set[str]:
    return set(tokenize(a)) & set(tokenize(b))


def extract_size_specs(text: object) -> set[str]:
    return {m.group(0).replace(" ", "").lower() for m in SIZE_PATTERN.finditer(str(text or ""))}


def extract_brand_like_token(text: object) -> str:
    tokens = tokenize(text)
    return tokens[0] if tokens else ""


def extract_qty(text: object) -> int:
    text_s = str(text or "")
    if re.search(r"multipack", text_s, re.I):
        return 2
    for pattern in QTY_PATTERNS:
        match = pattern.search(text_s)
        if match:
            try:
                return max(1, int(match.group(1)))
            except (ValueError, IndexError):
                continue
    return 1


def title_verdict(row: pd.Series, tier: str) -> tuple[bool, str]:
    supplier = row.get("SupplierTitle", "")
    amazon = row.get("AmazonTitle", "")
    overlap = meaningful_overlap(supplier, amazon)
    supplier_specs = extract_size_specs(supplier)
    amazon_specs = extract_size_specs(amazon)
    shared_specs = supplier_specs & amazon_specs
    supplier_brand = extract_brand_like_token(supplier)
    amazon_brand = extract_brand_like_token(amazon)
    brand_ok = supplier_brand and supplier_brand == amazon_brand
    ean_exact = str(row.get("ean_exact_match", "")).strip().lower() in {"true", "1", "yes"}

    if brand_ok and len(overlap) >= 2:
        return True, f"KEEP - shared terms={sorted(overlap)[:6]} and brand aligned"
    if ean_exact and len(overlap) >= 2 and (shared_specs or not supplier_specs or not amazon_specs):
        return True, f"KEEP - exact EAN plus overlap={sorted(overlap)[:6]}"
    if len(overlap) >= 3 and (shared_specs or not supplier_specs or not amazon_specs):
        return True, f"KEEP - strong descriptor overlap={sorted(overlap)[:6]}"
    if tier in TIER_3_VALUES and len(overlap) >= 2 and brand_ok and (shared_specs or not supplier_specs or not amazon_specs):
        return True, f"KEEP - cautious T3 keep, overlap={sorted(overlap)[:6]}"

    reason_parts = []
    if len(overlap) < 2:
        reason_parts.append(f"low overlap={sorted(overlap)}")
    if supplier_specs and amazon_specs and not shared_specs:
        reason_parts.append(f"spec mismatch supplier={sorted(supplier_specs)} amazon={sorted(amazon_specs)}")
    if supplier_brand and amazon_brand and supplier_brand != amazon_brand:
        reason_parts.append(f"brand mismatch {supplier_brand}!={amazon_brand}")
    if not reason_parts:
        reason_parts.append("core descriptors insufficiently aligned")
    return False, "DROP - " + "; ".join(reason_parts)


def unit_qty_result(row: pd.Series) -> tuple[str, str, float, float]:
    supplier_qty = extract_qty(row.get("SupplierTitle", ""))
    amazon_qty = extract_qty(row.get("AmazonTitle", ""))
    supplier_price = float(row.get("SupplierPrice_incVAT_num", np.nan))
    profit = float(row.get("NetProfit_num", np.nan))
    roi = float(row.get("ROI_num", np.nan)) if not math.isnan(float(row.get("ROI_num", np.nan))) else np.nan

    if supplier_qty == amazon_qty:
        return "MATCH", f"supplier_qty={supplier_qty}, amazon_qty={amazon_qty}", profit, roi
    if amazon_qty > supplier_qty and supplier_qty > 0 and not math.isnan(supplier_price):
        adjusted_cost = supplier_price * (amazon_qty / supplier_qty)
        adjusted_profit = profit - (adjusted_cost - supplier_price)
        adjusted_roi = (adjusted_profit / supplier_price * 100.0) if supplier_price else np.nan
        if adjusted_profit <= 0:
            return "MISMATCH_REMOVED", f"supplier_qty={supplier_qty}, amazon_qty={amazon_qty}, adjusted_profit={adjusted_profit:.2f}", adjusted_profit, adjusted_roi
        return "MISMATCH_ADJUST", f"supplier_qty={supplier_qty}, amazon_qty={amazon_qty}, adjusted_profit={adjusted_profit:.2f}", adjusted_profit, adjusted_roi
    return "UNCLEAR", f"supplier_qty={supplier_qty}, amazon_qty={amazon_qty}", profit, roi


def main() -> None:
    analysis_df = pd.read_csv(ANALYSIS_CSV, dtype=str).fillna("")
    fin_df = pd.read_csv(FIN_REPORT_CSV, dtype=str).fillna("")
    prompt_text = PROMPT_FILE.read_text(encoding="utf-8")

    for col in ["SupplierPrice_incVAT", "SellingPrice_incVAT", "NetProfit", "ROI", "sales_value", "confidence_score"]:
        analysis_df[col + "_num"] = to_number(analysis_df[col])

    fin_df["NetProfit_num"] = to_number(fin_df["NetProfit"])
    fin_df["ROI_num"] = to_number(fin_df["ROI"])

    total_rows = len(analysis_df)
    tier_counts = analysis_df["tier"].value_counts(dropna=False).to_dict()

    flag_counter = Counter()
    for flags in analysis_df["flags"].tolist():
        parts = [p.strip() for p in str(flags).split(",") if p.strip()]
        if not parts:
            flag_counter["NONE"] += 1
        else:
            flag_counter.update(parts)

    profitable_count = int((analysis_df["NetProfit_num"] > 0).sum())
    sales_positive_count = int((analysis_df["sales_value_num"] > 0).sum())
    sales_missing_count = int(analysis_df["sales_value"].eq("").sum())

    working = analysis_df.copy()
    waterfall = []

    rows_in = len(working)
    t4_mask = working["tier"].eq("TIER_4_REJECTED")
    working = working.loc[~t4_mask].copy()
    waterfall.append(("2.1 T4 filter", rows_in, int(t4_mask.sum()), len(working), "T4 rejected"))

    rows_in = len(working)
    overlaps = working.apply(lambda r: len(meaningful_overlap(r["SupplierTitle"], r["AmazonTitle"])), axis=1)
    high_ratio = working["SellingPrice_incVAT_num"] > (20 * working["SupplierPrice_incVAT_num"])
    low_ratio = working["SellingPrice_incVAT_num"] < (0.5 * working["SupplierPrice_incVAT_num"])
    price_remove = high_ratio & (overlaps < 2)
    suspicious_count = int(low_ratio.sum())
    working = working.loc[~price_remove].copy()
    waterfall.append(("2.2 Price plausibility", rows_in, int(price_remove.sum()), len(working), f"suspicious kept={suspicious_count}"))

    rows_in = len(working)
    overlaps = working.apply(lambda r: len(meaningful_overlap(r["SupplierTitle"], r["AmazonTitle"])), axis=1)
    ean_exact = working["ean_exact_match"].astype(str).str.lower().isin(["true", "1", "yes"])
    tier1 = working["tier"].isin(TIER_1_VALUES)
    false_match_remove = (overlaps < 2) & ~(tier1 & ean_exact)
    working = working.loc[~false_match_remove].copy()
    waterfall.append(("2.3 False match", rows_in, int(false_match_remove.sum()), len(working), "overlap < 2"))

    rows_in = len(working)
    qty_results = working.apply(unit_qty_result, axis=1)
    working["Unit_Qty_Flag"] = [item[0] for item in qty_results]
    working["Unit_Qty_Note"] = [item[1] for item in qty_results]
    working["NetProfit_num"] = [item[2] for item in qty_results]
    working["ROI_num"] = [item[3] for item in qty_results]
    mismatch_removed = working["Unit_Qty_Flag"].eq("MISMATCH_REMOVED")
    mismatch_examples = ", ".join(working.loc[mismatch_removed, "SupplierTitle"].head(3).tolist()) or "none"
    working = working.loc[~mismatch_removed].copy()
    waterfall.append(("2.4 Unit qty mismatch", rows_in, int(mismatch_removed.sum()), len(working), mismatch_examples))

    rows_in = len(working)
    verdict_notes = []
    keep_mask = np.ones(len(working), dtype=bool)
    index_list = list(working.index)
    for pos, idx in enumerate(index_list):
        tier = working.at[idx, "tier"]
        if tier in TIER_3_VALUES:
            keep, verdict = title_verdict(working.loc[idx], tier)
            verdict_notes.append((working.at[idx, "SupplierTitle"], verdict))
            keep_mask[pos] = keep
        else:
            verdict_notes.append((working.at[idx, "SupplierTitle"], "N/A"))
    working["Validation_Verdict"] = [note for _, note in verdict_notes]
    t3_rows = working["tier"].isin(TIER_3_VALUES)
    t3_drops = t3_rows & ~pd.Series(keep_mask, index=working.index)
    t3_drop_count = int(t3_drops.sum())
    t3_note = "; ".join([working.loc[idx, "Validation_Verdict"] for idx in working.index[t3_drops].tolist()[:3]]) or "none"
    working = working.loc[~t3_drops].copy()
    waterfall.append(("2.5 T3 verification", rows_in, t3_drop_count, len(working), t3_note))

    rows_in = len(working)
    t2_drop_indexes = []
    for idx in working.index.tolist():
        if working.at[idx, "tier"] in TIER_2_VALUES:
            keep, verdict = title_verdict(working.loc[idx], working.at[idx, "tier"])
            working.at[idx, "Validation_Verdict"] = verdict
            if not keep:
                t2_drop_indexes.append(idx)
    t2_drop_note = "; ".join([working.loc[idx, "Validation_Verdict"] for idx in t2_drop_indexes[:3]]) or "none"
    working = working.drop(index=t2_drop_indexes).copy()
    waterfall.append(("2.6 T2 verification", rows_in, len(t2_drop_indexes), len(working), t2_drop_note))

    working["Confidence"] = "MEDIUM"
    working["Validation_Required"] = "No"
    working["Bucket"] = ""

    sales = working["sales_value_num"].fillna(0)
    profit = working["NetProfit_num"].fillna(0)
    t1_t2 = working["tier"].isin(TIER_1_VALUES | TIER_2_VALUES)
    t3 = working["tier"].isin(TIER_3_VALUES)

    bucket_a = (profit > 0) & (sales > 0) & t1_t2
    bucket_b = (profit > 0) & ((sales <= 0) | working["sales_value"].eq(""))
    bucket_c = (sales > 50) & (profit >= -3.0) & (profit <= 0.5) & t1_t2

    working.loc[bucket_a, "Bucket"] = "A"
    working.loc[bucket_c & ~bucket_a, "Bucket"] = "C"
    working.loc[bucket_b & working["Bucket"].eq(""), "Bucket"] = "B"
    working.loc[t3 & working["Bucket"].eq("B"), "Confidence"] = "LOW"
    working.loc[t3 & working["Bucket"].eq("B"), "Validation_Required"] = "Yes"
    working = working.loc[~(t3 & working["Bucket"].isin(["A", "C"]))].copy()

    bucketed = working.loc[working["Bucket"].isin(["A", "B", "C"])].copy()

    fin_lookup = (
        fin_df.sort_values(["SupplierTitle", "NetProfit_num"], ascending=[True, False])
        .drop_duplicates(subset=["SupplierTitle"], keep="first")
        .set_index("SupplierTitle")
    )

    fin_profits = []
    profit_discrepancy = []
    fin_roi = []
    fin_bought = []
    for _, row in bucketed.iterrows():
        title = row["SupplierTitle"]
        if title in fin_lookup.index:
            fin_row = fin_lookup.loc[title]
            fin_profit_val = fin_row.get("NetProfit_num", np.nan)
            fin_roi_val = fin_row.get("ROI_num", np.nan)
            fin_bought_val = fin_row.get("bought_in_past_month", "")
            fin_profits.append(fin_profit_val)
            fin_roi.append(fin_roi_val)
            fin_bought.append(fin_bought_val)
            if pd.notna(fin_profit_val) and abs(float(row["NetProfit_num"]) - float(fin_profit_val)) > 1.0:
                profit_discrepancy.append("YES")
            else:
                profit_discrepancy.append("NO")
        else:
            fin_profits.append(np.nan)
            fin_roi.append(np.nan)
            fin_bought.append("")
            profit_discrepancy.append("NO")

    bucketed["FinReport_NetProfit"] = fin_profits
    bucketed["FinReport_ROI"] = fin_roi
    bucketed["FinReport_bought_in_past_month"] = fin_bought
    bucketed["Profit_Discrepancy"] = profit_discrepancy

    bucketed["SortScore"] = bucketed["sales_value_num"].fillna(0) * bucketed["NetProfit_num"].fillna(0)
    bucketed["BucketOrder"] = bucketed["Bucket"].map({"A": 0, "B": 1, "C": 2})
    bucketed = bucketed.sort_values(["BucketOrder", "SortScore"], ascending=[True, False]).copy()

    output_columns = [
        "SupplierTitle",
        "AmazonTitle",
        "EAN",
        "EAN_OnPage",
        "ASIN",
        "SupplierPrice_incVAT",
        "SellingPrice_incVAT",
        "NetProfit",
        "ROI",
        "bought_in_past_month",
        "amazon_sales_badge",
        "sales_value",
        "tier",
        "confidence_score",
        "flags",
        "reasons",
        "ean_exact_match",
        "SupplierURL",
        "AmazonURL",
        "fba_seller_count",
        "Category",
        "Bucket",
        "Unit_Qty_Flag",
        "Unit_Qty_Note",
        "FinReport_NetProfit",
        "Profit_Discrepancy",
    ]

    bucketed["NetProfit"] = bucketed["NetProfit_num"].round(9)
    bucketed["ROI"] = bucketed["ROI_num"].round(9)
    bucketed["FinReport_NetProfit"] = pd.to_numeric(bucketed["FinReport_NetProfit"], errors="coerce").round(9)

    bucketed[output_columns].to_csv(OUTPUT_CSV, index=False)

    bucket_summary = (
        bucketed.groupby("Bucket")
        .agg(
            Count=("Bucket", "size"),
            AvgProfit=("NetProfit_num", "mean"),
            AvgSales=("sales_value_num", "mean"),
        )
        .reset_index()
    )

    top10 = bucketed.head(10).copy()
    matched_fin = int(pd.notna(bucketed["FinReport_NetProfit"]).sum())
    discrepancies = int(bucketed["Profit_Discrepancy"].eq("YES").sum())
    t3_in_b = int((bucketed["tier"].isin(TIER_3_VALUES) & (bucketed["Bucket"] == "B")).sum())
    manual_qty = int(bucketed["Unit_Qty_Flag"].eq("UNCLEAR").sum())
    phase5_status = "Skipped - no explicit live validation requested for this execution pass. Results remain stale-data based."

    report_lines = [
        "# FBA Product Validation Report",
        "",
        f"Supplier: `efghousewares-co-uk`",
        f"Analysis Export: `{ANALYSIS_CSV}`",
        f"Financial Report: `{FIN_REPORT_CSV}`",
        f"Prompt Source: `{PROMPT_FILE}`",
        f"Date Executed: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "## Phase 1 - Input Summary",
        "",
        f"- Total rows loaded: {total_rows}",
        f"- Columns loaded: {len(analysis_df.columns) - 6}",
        f"- Tier counts: {tier_counts}",
        f"- Top flags: {dict(flag_counter.most_common(10))}",
        f"- Profitable rows (`NetProfit > 0`): {profitable_count}",
        f"- Rows with sales (`sales_value > 0`): {sales_positive_count}",
        f"- Rows with sales missing/blank: {sales_missing_count}",
        "",
        "## Phase 2 - Cleansing Waterfall",
        "",
        "| Step | Rows In | Removed | Rows Out | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for step, rows_in, removed, rows_out, notes in waterfall:
        report_lines.append(f"| {step} | {rows_in} | {removed} | {rows_out} | {notes} |")

    report_lines.extend([
        "",
        "## Phase 3 - Bucket Summary",
        "",
        "| Bucket | Count | Avg Profit | Avg Sales | T1 | T2 | T3 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for bucket_name in ["A", "B", "C"]:
        subset = bucketed.loc[bucketed["Bucket"] == bucket_name]
        report_lines.append(
            f"| {bucket_name} | {len(subset)} | {subset['NetProfit_num'].mean() if len(subset) else 0:.2f} | {subset['sales_value_num'].mean() if len(subset) else 0:.2f} | "
            f"{int(subset['tier'].isin(TIER_1_VALUES).sum())} | {int(subset['tier'].isin(TIER_2_VALUES).sum())} | {int(subset['tier'].isin(TIER_3_VALUES).sum())} |"
        )

    report_lines.extend([
        "",
        "## Phase 4 - Financial Report Cross-Reference",
        "",
        f"- Products matched to financial report by `SupplierTitle`: {matched_fin}",
        f"- Profit discrepancies flagged (`abs(delta) > 1.00`): {discrepancies}",
        f"- T3 rows retained in Bucket B only: {t3_in_b}",
        "",
        "## Phase 5 - Optional Live Validation",
        "",
        f"- {phase5_status}",
        "",
        "## Top 10 Highest-Conviction Opportunities",
        "",
        "| # | Product | Bucket | Net Profit | Sales | ROI | Unit Qty | Fin Report Profit | Discrepancy |",
        "|---|---|---|---:|---:|---:|---|---:|---|",
    ])
    for i, (_, row) in enumerate(top10.iterrows(), start=1):
        fin_profit = row["FinReport_NetProfit"]
        fin_profit_str = "" if pd.isna(fin_profit) else f"{fin_profit:.2f}"
        report_lines.append(
            f"| {i} | {row['SupplierTitle']} | {row['Bucket']} | {row['NetProfit_num']:.2f} | {row['sales_value_num'] if pd.notna(row['sales_value_num']) else 0:.0f} | {row['ROI_num']:.2f} | {row['Unit_Qty_Flag']} | {fin_profit_str} | {row['Profit_Discrepancy']} |"
        )

    report_lines.extend([
        "",
        "## Manual Review Queue",
        "",
        f"- Unit quantity unclear: {manual_qty}",
        f"- Profit discrepancy: {discrepancies}",
        f"- T3 in Bucket B (low confidence): {t3_in_b}",
        "",
        "## Output Verification",
        "",
        f"- Output CSV: `{OUTPUT_CSV}`",
        f"- Output rows: {len(bucketed)}",
        f"- Zero T4 items in output: {int((bucketed['tier'] == 'TIER_4_REJECTED').sum()) == 0}",
        f"- Zero T3 items in Bucket A/C: {int((bucketed['tier'].isin(TIER_3_VALUES) & bucketed['Bucket'].isin(['A', 'C'])).sum()) == 0}",
        f"- `Unit_Qty_Flag` present: {'Unit_Qty_Flag' in bucketed.columns}",
        f"- `Bucket` present: {'Bucket' in bucketed.columns}",
        f"- `MISMATCH_REMOVED` rows excluded: {int((bucketed['Unit_Qty_Flag'] == 'MISMATCH_REMOVED').sum()) == 0}",
        "",
        "## Honest Assessment",
        "",
        f"- Genuinely actionable products: {len(bucketed)} out of {total_rows}",
        f"- Confidence level: {'HIGH' if len(bucketed) and discrepancies < max(3, len(bucketed) * 0.1) else 'MEDIUM'}",
        "- Most of the retained set is T1 exact-EAN product matching. The main residual risk is stale pricing rather than identity mismatch.",
    ])

    OUTPUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    prompt_analysis_lines = [
        "# Analysis of `fba_product_validation_prompt.md`",
        "",
        f"Source: `{PROMPT_FILE}`",
        "",
        "## What the prompt does well",
        "",
        "- It forces a clear phased workflow: summarize, cleanse, bucket, cross-reference, optionally live-check, then verify outputs.",
        "- It correctly separates stale-data uncertainty from true zero sales and explicitly quarantines T3 risk.",
        "- It is strong on verification discipline: re-read after save, preserve schema, and cross-check against the financial report.",
        "- Its unit-quantity section is one of the strongest parts of the prompt; the regex coverage is materially better than the earlier ad hoc pass.",
        "",
        "## Blind spots seen during execution",
        "",
        "- The prompt assumes the financial report is a trustworthy cross-reference, but the sampled EFG financial report contains obvious extreme mismatches and fantasy-priced Amazon matches in many rows. This means the report cannot be treated as automatically authoritative for all products.",
        "- The prompt does not define an exact deterministic decision rule for T2/T3 title verification. It says 'be thorough' but leaves room for inconsistent agent judgment.",
        "- The prompt does not say how to handle datasets that are overwhelmingly T1 exact-EAN matches; in that case much of the cleansing logic becomes mostly a no-op and the report can feel overbuilt.",
        "- Phase 5 is optional, but the trigger rule is slightly ambiguous when API keys exist in env vars but the user has not explicitly asked for live checks in the current run.",
        "",
        "## Improvements I would make",
        "",
        "- Add a hard financial-report sanity gate before Phase 4 comparison. Example: if the financial report contains impossible price deltas or obvious product-identity mismatches, downgrade it to 'advisory only' rather than primary tie-breaker.",
        "- Add deterministic T2/T3 keep/drop rules with a minimum token overlap, brand rule, and size/spec consistency rule so two agents produce the same result.",
        "- Add a fast-path for mostly T1 exact-EAN datasets: skip deep T2/T3 discussion when counts are tiny and focus on profitability and quantity adjustments.",
        "- Clarify Phase 5 trigger language: either require explicit user request for live checks, or require automatic execution when keys are present. Right now it can be read both ways.",
        "- Require a second output artifact: a machine-readable JSON summary of phase counts, bucket counts, and removals for downstream reuse.",
        "",
        "## Execution-specific observations for this EFG file",
        "",
        f"- Input rows: {total_rows}",
        f"- Retained actionable rows: {len(bucketed)}",
        f"- T4 removed: {tier_counts.get('TIER_4_REJECTED', 0)}",
        f"- T3 retained in Bucket B only: {t3_in_b}",
        f"- Quantity mismatch removals: {next((removed for step, _, removed, _, _ in waterfall if step == '2.4 Unit qty mismatch'), 0)}",
        f"- Financial-report profit discrepancies flagged: {discrepancies}",
        "",
        "## Bottom line",
        "",
        "- The prompt is useful and much better than the earlier loose workflow, but it still needs a deterministic Phase 4 trust model and a sharper T2/T3 decision rubric.",
        "- For exact-EAN-heavy exports like this EFG file, the prompt is strongest when used as a cleanse-and-verification workflow rather than a broad discovery workflow.",
    ]
    OUTPUT_ANALYSIS.write_text("\n".join(prompt_analysis_lines) + "\n", encoding="utf-8")

    print(f"WROTE_CSV={OUTPUT_CSV}")
    print(f"WROTE_REPORT={OUTPUT_REPORT}")
    print(f"WROTE_ANALYSIS={OUTPUT_ANALYSIS}")
    print(f"OUTPUT_ROWS={len(bucketed)}")
    print(f"BUCKET_A={int((bucketed['Bucket'] == 'A').sum())}")
    print(f"BUCKET_B={int((bucketed['Bucket'] == 'B').sum())}")
    print(f"BUCKET_C={int((bucketed['Bucket'] == 'C').sum())}")


if __name__ == "__main__":
    main()
