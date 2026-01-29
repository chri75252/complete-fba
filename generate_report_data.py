import pandas as pd
import os
import json
import math

# Paths
shortlist_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2\shortlist.csv"
dnb_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2\do_not_buy.csv"
backlog_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2\backlog.csv"


def generate_report():
    sl_df = pd.read_csv(shortlist_path)
    dnb_df = pd.read_csv(dnb_path)
    bl_df = pd.read_csv(backlog_path) if os.path.exists(backlog_path) else pd.DataFrame()

    # Tiering
    # 1. Focus Now (Top 8)
    focus_now = sl_df.head(8).copy()

    # 2. Focus Next (Seasonal)
    seasonal_keywords = [
        "MULLED WINE",
        "CHRISTMAS",
        "WINTER",
        "FESTIVE",
        "ROBIN",
        "HALLOWEEN",
        "VALENTINE",
    ]

    def is_seasonal(row):
        title = str(row["AmazonTitle"]).upper()
        for kw in seasonal_keywords:
            if kw in title:
                return True
        return False

    seasonal = sl_df[sl_df.apply(is_seasonal, axis=1)].copy()

    # 3. Monitor/Probe
    # Items in shortlist not in top 8 or seasonal, or items in backlog
    focus_now_asins = focus_now["ASIN"].tolist()
    seasonal_asins = seasonal["ASIN"].tolist()

    monitor_probe = sl_df[~sl_df["ASIN"].isin(focus_now_asins + seasonal_asins)].head(10).copy()

    # Rationale Generation for Focus Now
    def get_rationale(row):
        parts = []
        if row["ROI_calc"] > 100:
            parts.append(f"Exceptional ROI ({row['ROI_calc']:.1f}%)")
        elif row["ROI_calc"] > 50:
            parts.append(f"Strong ROI ({row['ROI_calc']:.1f}%)")

        if row["NetProfit"] > 10:
            parts.append(f"High profit per unit (£{row['NetProfit']:.2f})")
        elif row["NetProfit"] > 5:
            parts.append(f"Good profit margin (£{row['NetProfit']:.2f})")

        if row["Velocity"] == "High":
            parts.append("High sales velocity")

        return " | ".join(parts) if parts else "Solid metrics across the board"

    focus_now["Rationale"] = focus_now.apply(get_rationale, axis=1)

    # Next Action
    def get_action(row):
        sales = float(row["Sales"]) if not pd.isna(row["Sales"]) else 0
        units = min(max(math.ceil(0.3 * sales), 5), 30)
        budget = units * row["SupplierPrice"]
        return f"Test {units} units (£{budget:.2f} budget)"

    focus_now["NextAction"] = focus_now.apply(get_action, axis=1)

    # Seasonality Inference
    def infer_seasonality(row):
        title = str(row["AmazonTitle"]).upper()
        if "MULLED WINE" in title or "CHRISTMAS" in title or "WINTER" in title:
            return "Winter/Holiday"
        if "SUMMER" in title:
            return "Summer"
        return "Low/None"

    focus_now["Seasonality"] = focus_now.apply(infer_seasonality, axis=1)

    # Do-Not-Buy Rollup
    dnb_counts = dnb_df["Reason"].value_counts().to_dict()

    return {
        "focus_now": focus_now.to_dict(orient="records"),
        "seasonal": seasonal.to_dict(orient="records"),
        "monitor": monitor_probe.to_dict(orient="records"),
        "dnb_rollup": dnb_counts,
    }


report_data = generate_report()
print(json.dumps(report_data))
