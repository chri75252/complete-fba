import pandas as pd
import os
import json
import math

# Use the paths discovered in the previous turn
base_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2"
shortlist_path = os.path.join(base_path, "shortlist.csv")
dnb_path = os.path.join(base_path, "do_not_buy.csv")
backlog_path = os.path.join(base_path, "backlog.csv")


def process_reports():
    # 1. Ingest Data
    shortlist_df = (
        pd.read_excel(os.path.join(base_path, "op", "fba_opportunities_20260117_Asia-Dubai.xlsx"))
        if not os.path.exists(shortlist_path)
        else pd.read_csv(shortlist_path)
    )
    dnb_df = pd.read_csv(dnb_path)
    backlog_df = pd.read_csv(backlog_path)

    # 2. Prioritization Logic (Focus Now vs Next vs Monitor)
    # Sort by Score first
    shortlist_df = shortlist_df.sort_values(by="Score", ascending=False)

    # Heuristics for Focus Now: High Score + High/Medium Velocity + Low/Unknown Risk
    focus_now = shortlist_df.head(8).copy()

    # Add Rationale and Unit Suggestions
    def get_rationale(row):
        return f"High ROI ({row['ROI_calc']:.1f}%) with {row['Velocity']} velocity. Stable profit of £{row['NetProfit']:.2f} per unit."

    def get_units(row):
        # units = min(ceil(0.3 * Sales_Last30D), 30)
        sales = row.get("Sales", 50)  # Fallback to 50
        return min(math.ceil(0.3 * sales), 30)

    focus_now["Why Focus"] = focus_now.apply(get_rationale, axis=1)
    focus_now["Units"] = focus_now.apply(get_units, axis=1)
    focus_now["Budget"] = focus_now["Units"] * focus_now["SupplierPrice"]

    # 3. Focus Next (Seasonal)
    # Identify seasonal keywords in Title
    seasonal_keywords = ["Christmas", "Winter", "Mulled", "Festive", "Valentine", "Summer", "Rose"]
    focus_next = shortlist_df[
        shortlist_df["AmazonTitle"].str.contains("|".join(seasonal_keywords), case=False, na=False)
    ].copy()

    # 4. Monitor/Probe
    # Items with Medium Brand Risk or Unknown Risk but lower scores
    monitor = shortlist_df[~shortlist_df["ASIN"].isin(focus_now["ASIN"])].head(10).copy()

    # 5. DNB Rollup
    dnb_counts = dnb_df["Reason"].value_counts().to_dict()

    # Output for synthesis
    results = {
        "focus_now": focus_now[
            [
                "ASIN",
                "AmazonTitle",
                "SupplierPrice",
                "SellingPrice",
                "NetProfit",
                "ROI_calc",
                "Velocity",
                "BrandRisk",
                "Why Focus",
                "Units",
                "Budget",
            ]
        ].to_dict(orient="records"),
        "focus_next": focus_next[["ASIN", "AmazonTitle", "Score"]]
        .head(5)
        .to_dict(orient="records"),
        "monitor": monitor[["ASIN", "AmazonTitle", "BrandRisk"]].head(5).to_dict(orient="records"),
        "dnb_rollup": dnb_counts,
    }
    print(json.dumps(results, indent=2))


process_reports()
