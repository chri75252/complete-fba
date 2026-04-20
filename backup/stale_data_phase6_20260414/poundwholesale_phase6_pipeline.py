from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-")
ANALYSIS_PATH = ROOT / "temp" / "fba_analysis_2026-poundhwolesale-14.csv"
FINANCIAL_PATH = ROOT / "OUTPUTS" / "FBA_ANALYSIS" / "financial_reports" / "poundwholesale-co-uk" / "fba_financial_report_poundwholesale-co-uk_20260414_082856.csv"
CACHE_PATH = ROOT / "OUTPUTS" / "cached_products" / "poundwholesale-co-uk_products_cache.json"
PRODUCTS_DIR = ROOT / "OUTPUTS" / "PRODUCTS_LISTS"
CONTROL_INPUTS_DIR = ROOT / "OUTPUTS" / "CONTROL_PLANE" / "inputs"
BACKUP_DIR = ROOT / "backup" / "stale_data_phase6_20260414"

STOP_WORDS = {"the", "and", "with", "for", "in", "of", "a", "an", "to", "by"}
LUXURY_RE = re.compile(
    r"jo malone|versace|armani|giorgio armani|gucci|chanel|prada|dior|ysl|burberry|"
    r"tom ford|dyson|kenwood|kitchenaid|le creuset|samsung|apple|sony|bose|lego",
    re.I,
)
PACK_PATTERNS = [
    re.compile(r"\bpack\s*(?:of\s*)?(\d+)\b", re.I),
    re.compile(r"\((\d+)\s*pack\)", re.I),
    re.compile(r"\b(\d+)\s*-?\s*pack\b", re.I),
    re.compile(r"\bset\s*of\s*(\d+)\b", re.I),
    re.compile(r"\bbox\s*of\s*(\d+)\b", re.I),
    re.compile(r"\b(\d+)\s*(?:pc|pcs|pieces?|count|ct)\b", re.I),
    re.compile(r"\b(\d+)\s*x\s", re.I),
    re.compile(r"\bx\s*(\d+)\b", re.I),
]
TIER_MAP = {
    "TIER_1_VERIFIED": "T1",
    "TIER_2_LIKELY": "T2",
    "TIER_3_NEEDS_REVIEW": "T3",
}


@dataclass
class OutputPaths:
    ts: str
    snapshot: Path
    summary: Path
    category_targets: Path
    orphan_asins: Path
    validation_candidates: Path
    master_csv: Path
    bucket_a_csv: Path
    bucket_bc_csv: Path
    ranked_json: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def tokens(text: object) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(text).lower())) - STOP_WORDS


def shared_word_count(a: object, b: object) -> int:
    return len(tokens(a) & tokens(b))


def jaccard_similarity(a: object, b: object) -> float:
    ta = tokens(a)
    tb = tokens(b)
    denom = len(ta | tb) or 1
    return round(len(ta & tb) / denom, 4)


def extract_pack_qty(text: object) -> int:
    raw = str(text)
    for pattern in PACK_PATTERNS:
        match = pattern.search(raw)
        if match:
            qty = int(match.group(1))
            if qty > 1:
                return qty
    if "multipack" in raw.lower():
        return 2
    return 1


def confidence_label(tier: str) -> str:
    if tier == "TIER_1_VERIFIED":
        return "HIGH"
    if tier == "TIER_2_LIKELY":
        return "MEDIUM"
    return "LOW"


def priority_label(bucket: str, score: float, sales: float, profit: float, q50: float, q80: float) -> str:
    if bucket == "A" and sales >= 100 and profit >= 1:
        return "HIGH"
    if bucket == "C" and sales >= 200 and profit > -1.5:
        return "HIGH"
    if score >= q80:
        return "HIGH"
    if score >= q50:
        return "MEDIUM"
    return "LOW"


def load_analysis() -> pd.DataFrame:
    return pd.read_csv(ANALYSIS_PATH)


def load_cache() -> pd.DataFrame:
    raw = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    df = pd.DataFrame(raw)
    return df[["url", "source_url", "availability", "scraped_at"]].drop_duplicates("url")


def phase2_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    counts: dict[str, int] = {"rows_in": int(len(df))}

    work = df[df["tier"] != "TIER_4_REJECTED"].copy()
    counts["removed_t4"] = int(len(df) - len(work))

    superior_mask = work["SupplierTitle"].str.contains("Superior", case=False, na=False)
    counts["removed_superior"] = int(superior_mask.sum())
    work = work[~superior_mask].copy()

    work["token_overlap"] = [shared_word_count(a, b) for a, b in zip(work["SupplierTitle"], work["AmazonTitle"])]
    work["underpriced_suspicious"] = work["SellingPrice_incVAT"] < (work["SupplierPrice_incVAT"] * 0.5)

    price_remove_mask = (work["SellingPrice_incVAT"] > (20 * work["SupplierPrice_incVAT"])) & (work["token_overlap"] < 2)
    counts["removed_price"] = int(price_remove_mask.sum())
    counts["flagged_underpriced"] = int(work["underpriced_suspicious"].sum())
    work = work[~price_remove_mask].copy()

    brand_mismatch = work["AmazonTitle"].str.contains(LUXURY_RE, na=False) & ~work["SupplierTitle"].str.contains(LUXURY_RE, na=False)
    false_match_mask = brand_mismatch | (work["token_overlap"] < 2)
    counts["removed_false_match"] = int(false_match_mask.sum())
    work = work[~false_match_mask].copy()

    work["supplier_pack_qty"] = work["SupplierTitle"].map(extract_pack_qty)
    work["amazon_pack_qty"] = work["AmazonTitle"].map(extract_pack_qty)
    work["Unit_Qty_Flag"] = np.where(work["amazon_pack_qty"] > work["supplier_pack_qty"], "MISMATCH_CHECK", "MATCH")
    work["Unit_Qty_Note"] = np.where(
        work["Unit_Qty_Flag"] == "MISMATCH_CHECK",
        "Recalculated for Amazon multipack quantity",
        "",
    )
    fees = work["SellingPrice_incVAT"] - work["SupplierPrice_incVAT"] - work["NetProfit"]
    work["Net_Profit"] = np.where(
        work["Unit_Qty_Flag"] == "MISMATCH_CHECK",
        work["SellingPrice_incVAT"] - (work["SupplierPrice_incVAT"] * work["amazon_pack_qty"]) - fees,
        work["NetProfit"],
    )
    qty_remove_mask = (work["Unit_Qty_Flag"] == "MISMATCH_CHECK") & (work["Net_Profit"] < 0)
    counts["removed_qty_mismatch"] = int(qty_remove_mask.sum())
    counts["qty_match_pre_t3"] = int((work["Unit_Qty_Flag"] == "MATCH").sum())
    counts["qty_mismatch_pre_t3"] = int((work["Unit_Qty_Flag"] == "MISMATCH_CHECK").sum() - qty_remove_mask.sum())
    work = work[~qty_remove_mask].copy()

    counts["removed_t3"] = int((work["tier"] == "TIER_3_NEEDS_REVIEW").sum())
    work = work[work["tier"] != "TIER_3_NEEDS_REVIEW"].copy()
    counts["rows_clean"] = int(len(work))
    counts["qty_match_post_t3"] = int((work["Unit_Qty_Flag"] == "MATCH").sum())
    counts["qty_mismatch_post_t3"] = int((work["Unit_Qty_Flag"] == "MISMATCH_CHECK").sum())
    return work, counts


def classify(clean_df: pd.DataFrame, cache_df: pd.DataFrame) -> pd.DataFrame:
    work = clean_df.merge(cache_df, how="left", left_on="SupplierURL", right_on="url", suffixes=("", "_cache"))
    sales = work["sales_value"].fillna(0)
    profit = work["Net_Profit"]

    bucket_a = (sales > 0) & (profit > 0) & work["tier"].isin(["TIER_1_VERIFIED", "TIER_2_LIKELY"])
    bucket_b = (profit > 0) & ((sales == 0) | work["sales_value"].isna()) & work["tier"].isin(["TIER_1_VERIFIED", "TIER_2_LIKELY"])
    bucket_c = (sales > 50) & (profit >= -3.0) & (profit <= 0.5) & work["tier"].isin(["TIER_1_VERIFIED", "TIER_2_LIKELY"])
    work["Bucket"] = np.select([bucket_a, bucket_b, bucket_c], ["A", "B", "C"], default="")
    work = work[work["Bucket"] != ""].copy()
    sales = work["sales_value"].fillna(0)
    profit = work["Net_Profit"]

    work["Priority_Score"] = np.select(
        [work["Bucket"] == "A", work["Bucket"] == "B", work["Bucket"] == "C"],
        [sales * profit, profit * np.where(work["tier"] == "TIER_1_VERIFIED", 1.15, 1.0), sales / (1 + profit.abs())],
        default=0.0,
    )
    q50 = float(work["Priority_Score"].quantile(0.5))
    q80 = float(work["Priority_Score"].quantile(0.8))
    work["Priority"] = [priority_label(b, sc, sv, pf, q50, q80) for b, sc, sv, pf in zip(work["Bucket"], work["Priority_Score"], sales.loc[work.index], profit.loc[work.index])]
    work["Category_URL"] = work["source_url"].fillna("")
    work["Category_Label"] = work["Category"].fillna("Unknown")
    work["Similarity"] = [jaccard_similarity(a, b) for a, b in zip(work["SupplierTitle"], work["AmazonTitle"])]
    work["Tier_Short"] = work["tier"].map(TIER_MAP).fillna(work["tier"])
    work["Match_Type"] = np.where(work["ean_exact_match"].fillna(False), "EAN", "Title")
    work["Confidence"] = work["tier"].map(confidence_label)
    work["Validation_Required"] = np.where(
        (work["tier"] != "TIER_1_VERIFIED") | (work["Unit_Qty_Flag"] == "MISMATCH_CHECK") | work["underpriced_suspicious"],
        "Yes",
        "No",
    )
    work["Evidence_Status"] = "STALE_SOURCE"
    work["External_Check_Status"] = "NOT_CHECKED"
    work["Dashboard_Flags"] = work["flags"].fillna("")
    work["Inclusion_Reason"] = np.select(
        [work["Bucket"] == "A", work["Bucket"] == "B", work["Bucket"] == "C"],
        [
            "Proven Demand: positive profit + confirmed sales",
            "Opportunity: positive profit with zero/unknown sales",
            "Margin Flip: high sales with near-breakeven economics",
        ],
        default="",
    )
    return work


def build_category_targets(classified: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ac = classified[classified["Bucket"].isin(["A", "C"])].copy()
    ac["Value_Contribution"] = ac["sales_value"].fillna(0) * ac["Net_Profit"].abs()
    grouped = (
        ac.groupby(["Category_URL", "Category_Label"], dropna=False)
        .agg(
            products=("ASIN", "size"),
            value_score=("Value_Contribution", "sum"),
            t1_count=("tier", lambda s: int((s == "TIER_1_VERIFIED").sum())),
            t2_count=("tier", lambda s: int((s == "TIER_2_LIKELY").sum())),
            avg_sales=("sales_value", "mean"),
        )
        .reset_index()
    )
    grouped["identifier_quality"] = ((grouped["t1_count"] + 0.5 * grouped["t2_count"]) / grouped["products"]).round(3)
    grouped["rank_score"] = (grouped["products"] * grouped["value_score"] * grouped["identifier_quality"]).round(2)
    grouped = grouped.sort_values(["rank_score", "products", "value_score"], ascending=[False, False, False]).reset_index(drop=True)
    top = grouped[grouped["Category_URL"].astype(str).str.strip() != ""].head(min(5, len(grouped))).copy().reset_index(drop=True)
    return grouped, top


def clean_json_value(value):
    if pd.isna(value):
        return None
    return value


def product_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for row in df.itertuples(index=False):
        records.append(
            {
                "title": row.Supplier_Title,
                "amazon_title": row.Amazon_Title,
                "price": row.Supplier_Price,
                "amazon_price": row.Amazon_Price,
                "url": row.Supplier_URL,
                "normalized_url": row.Supplier_URL,
                "amazon_url": row.Amazon_URL,
                "ean": row.EAN,
                "asin": row.ASIN,
                "availability": clean_json_value(getattr(row, "Availability", "Unknown")),
                "source_url": clean_json_value(getattr(row, "Category_URL", "")),
                "scraped_at": clean_json_value(getattr(row, "Scraped_At", "")),
                "net_profit": clean_json_value(row.Net_Profit),
                "sales": clean_json_value(row.Sales),
                "roi": clean_json_value(row.ROI),
                "bucket": row.Bucket,
                "priority": row.Priority,
                "confidence": row.Confidence,
                "unit_qty_flag": row.Unit_Qty_Flag,
                "tier": row.Tier,
                "external_check_status": getattr(row, "External_Check_Status", "NOT_CHECKED"),
            }
        )
    return records


def output_paths(ts: str) -> OutputPaths:
    return OutputPaths(
        ts=ts,
        snapshot=BACKUP_DIR / f"poundwholesale-co-uk_clean_snapshot_{ts}.csv",
        summary=PRODUCTS_DIR / f"poundwholesale-co-uk_phase4_summary_{ts}.json",
        category_targets=PRODUCTS_DIR / f"poundwholesale-co-uk_category_sandbox_targets_{ts}.json",
        orphan_asins=CONTROL_INPUTS_DIR / f"poundwholesale-co-uk_orphan_asins_{ts}.json",
        validation_candidates=PRODUCTS_DIR / f"poundwholesale-co-uk_phase5_validation_candidates_{ts}.json",
        master_csv=PRODUCTS_DIR / f"poundwholesale-co-uk_VALIDATED_master_{ts}.csv",
        bucket_a_csv=PRODUCTS_DIR / f"poundwholesale-co-uk_VALIDATED_bucketA_{ts}.csv",
        bucket_bc_csv=PRODUCTS_DIR / f"poundwholesale-co-uk_VALIDATED_bucketBC_{ts}.csv",
        ranked_json=PRODUCTS_DIR / f"poundwholesale-co-uk_validated_ranked_products_{ts}.json",
    )


def main() -> None:
    PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
    CONTROL_INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    ts = now_stamp()
    paths = output_paths(ts)
    raw_df = load_analysis()
    _ = pd.read_csv(FINANCIAL_PATH)
    cache_df = load_cache()

    clean_df, counts = phase2_clean(raw_df)
    clean_df.sort_values(["tier", "confidence_score"], ascending=[True, False]).to_csv(paths.snapshot, index=False)

    classified = classify(clean_df, cache_df)
    ranked_all = classified.sort_values(["Bucket", "Priority_Score"], ascending=[True, False]).copy()

    _grouped, top_categories = build_category_targets(classified)
    top_urls = set(top_categories["Category_URL"].tolist())
    orphan_df = classified[classified["Bucket"].isin(["A", "C"]) & ~classified["Category_URL"].isin(top_urls)].copy()
    orphan_asins = [x for x in orphan_df["ASIN"].dropna().astype(str).unique().tolist() if x]

    bucket_a = classified[classified["Bucket"] == "A"].sort_values(["Priority_Score", "sales_value", "Net_Profit"], ascending=[False, False, False]).head(10)
    bucket_b = classified[classified["Bucket"] == "B"].sort_values(["Priority_Score", "Net_Profit"], ascending=[False, False]).head(5)
    bucket_c = classified[classified["Bucket"] == "C"].assign(abs_profit=classified.loc[classified["Bucket"] == "C", "Net_Profit"].abs()).sort_values(["abs_profit", "sales_value"], ascending=[True, False]).head(10)
    validation_df = pd.concat([bucket_a, bucket_b, bucket_c], ignore_index=True)

    final_cols = {
        "SupplierTitle": "Supplier_Title",
        "AmazonTitle": "Amazon_Title",
        "ASIN": "ASIN",
        "EAN": "EAN",
        "Match_Type": "Match_Type",
        "Tier_Short": "Tier",
        "confidence_score": "Confidence_Score",
        "ean_exact_match": "EAN_Exact_Match",
        "sales_value": "Sales",
        "Net_Profit": "Net_Profit",
        "ROI": "ROI",
        "SupplierPrice_incVAT": "Supplier_Price",
        "SellingPrice_incVAT": "Amazon_Price",
        "Bucket": "Bucket",
        "Inclusion_Reason": "Inclusion_Reason",
        "Confidence": "Confidence",
        "Validation_Required": "Validation_Required",
        "Priority": "Priority",
        "Similarity": "Similarity",
        "Unit_Qty_Flag": "Unit_Qty_Flag",
        "Unit_Qty_Note": "Unit_Qty_Note",
        "Category_Label": "Category",
        "SupplierURL": "Supplier_URL",
        "AmazonURL": "Amazon_URL",
        "fba_seller_count": "FBA_Sellers",
        "Dashboard_Flags": "Dashboard_Flags",
        "Evidence_Status": "Evidence_Status",
        "External_Check_Status": "External_Check_Status",
        "availability": "Availability",
        "scraped_at": "Scraped_At",
        "Category_URL": "Category_URL",
        "Priority_Score": "Priority_Score",
    }
    final_df = ranked_all[list(final_cols.keys())].rename(columns=final_cols)
    final_df.to_csv(paths.master_csv, index=False)
    final_df[final_df["Bucket"] == "A"].to_csv(paths.bucket_a_csv, index=False)
    final_df[final_df["Bucket"].isin(["B", "C"])].to_csv(paths.bucket_bc_csv, index=False)

    ranked_payload = {
        "supplier_domain": "poundwholesale.co.uk",
        "generated_at": utc_now(),
        "source_cached_file": str(paths.master_csv.relative_to(ROOT)),
        "selection": {
            "mode": "ranked_validated",
            "sample_size": int(len(final_df)),
            "category_count": int(len(top_categories)),
            "selected_categories": top_categories["Category_URL"].tolist(),
        },
        "products": product_records(final_df),
    }
    paths.ranked_json.write_text(json.dumps(ranked_payload, indent=2), encoding="utf-8")

    category_payload = {
        "supplier_domain": "poundwholesale.co.uk",
        "generated_at": utc_now(),
        "source_snapshot": str(paths.snapshot.relative_to(ROOT)),
        "top_categories": [
            {
                "rank": int(i + 1),
                "category_url": row.Category_URL,
                "category_label": row.Category_Label,
                "products": int(row.products),
                "value_score": round(float(row.value_score), 2),
                "identifier_quality": float(row.identifier_quality),
                "rank_score": round(float(row.rank_score), 2),
                "trigger_command": f"run sandbox analysis for category {row.Category_URL} on poundwholesale-co-uk",
            }
            for i, row in top_categories.iterrows()
        ],
        "orphan_product_count": int(len(orphan_asins)),
    }
    paths.category_targets.write_text(json.dumps(category_payload, indent=2), encoding="utf-8")
    paths.orphan_asins.write_text(json.dumps(orphan_asins, indent=2), encoding="utf-8")

    validation_payload = {
        "supplier_domain": "poundwholesale.co.uk",
        "generated_at": utc_now(),
        "source_snapshot": str(paths.snapshot.relative_to(ROOT)),
        "selection": {
            "bucket_a": int(len(bucket_a)),
            "bucket_b": int(len(bucket_b)),
            "bucket_c": int(len(bucket_c)),
            "total": int(len(validation_df)),
        },
        "products": product_records(validation_df.rename(columns=final_cols)),
    }
    paths.validation_candidates.write_text(json.dumps(validation_payload, indent=2), encoding="utf-8")

    summary = {
        "analysis_source": str(ANALYSIS_PATH),
        "financial_source": str(FINANCIAL_PATH),
        "snapshot": str(paths.snapshot),
        "rows_clean": counts["rows_clean"],
        "classified_rows": int(len(final_df)),
        "bucket_counts": final_df["Bucket"].value_counts().to_dict(),
        "top_categories": category_payload["top_categories"],
        "orphan_count": int(len(orphan_asins)),
        "validation_candidate_count": int(len(validation_df)),
        "files": {
            "master_csv": str(paths.master_csv),
            "bucket_a_csv": str(paths.bucket_a_csv),
            "bucket_bc_csv": str(paths.bucket_bc_csv),
            "ranked_json": str(paths.ranked_json),
            "category_targets": str(paths.category_targets),
            "orphan_asins": str(paths.orphan_asins),
            "validation_candidates": str(paths.validation_candidates),
        },
    }
    paths.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    for path in [paths.master_csv, paths.bucket_a_csv, paths.bucket_bc_csv, paths.ranked_json, paths.category_targets, paths.orphan_asins, paths.validation_candidates, paths.summary]:
        shutil.copy2(path, BACKUP_DIR / path.name)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
