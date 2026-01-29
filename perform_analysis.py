import pandas as pd
import os
from datetime import datetime
import pytz

# Paths
input_file = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\final ver.xlsx"
output_dir = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2"

# Timezone
dubai_tz = pytz.timezone("Asia/Dubai")
now = datetime.now(dubai_tz)
date_str = now.strftime("%Y-%m-%d %H:%M:%S")


def analyze_data():
    df = pd.read_excel(input_file)

    # Clean column names (strip spaces)
    df.columns = [c.strip() for c in df.columns]

    # Mapping
    # Identifier: ASIN
    # Costs: SupplierPrice
    # Price: SellingPrice
    # Profit: NetProfit
    # Sales: Sales

    # Drop rows with missing critical data
    df = df.dropna(subset=["ASIN", "SupplierPrice", "NetProfit", "SellingPrice"])

    # Recalculate ROI% based on prompt formula: (Profit / BuyCost) * 100
    df["ROI_calc"] = (df["NetProfit"] / df["SupplierPrice"]) * 100

    # Velocity Band
    def get_velocity_band(sales):
        try:
            val = float(sales)
            if val >= 100:
                return "High"
            if val >= 30:
                return "Medium"
            return "Low"
        except:
            return "Low"

    df["Velocity"] = df["Sales"].apply(get_velocity_band)

    # Brand Risk Heuristics
    high_risk_brands = ["ADIDAS", "NIKE", "APPLE", "LEGO"]  # Typical gated brands
    med_risk_brands = [
        "MASON CASH",
        "CHEF AID",
        "TALA",
        "FALCON",
    ]  # Common household brands (often need approval)

    def assess_brand_risk(row):
        title = str(row["AmazonTitle"]).upper()
        supp_title = str(row["SupplierTitle"]).upper()

        for brand in high_risk_brands:
            if brand in title or brand in supp_title:
                return "High"
        for brand in med_risk_brands:
            if brand in title or brand in supp_title:
                return "Medium"
        return "Unknown"

    df["BrandRisk"] = df.apply(assess_brand_risk, axis=1)

    # Scoring Logic
    # ROI weight 35%, Profit 25%, Velocity 20%, Competition 10%, Risk 10%

    max_roi = df["ROI_calc"].max() if not df.empty else 1
    max_profit = df["NetProfit"].max() if not df.empty else 1

    def calculate_score(row):
        # ROI Score (0-35)
        roi_score = (min(row["ROI_calc"], 100) / 100) * 35  # Cap at 100% for scoring

        # Profit Score (0-25)
        profit_score = (min(row["NetProfit"], 20) / 20) * 25  # Cap at $20 for scoring

        # Velocity Score (0-20)
        vel_map = {"High": 20, "Medium": 10, "Low": 0}
        velocity_score = vel_map.get(row["Velocity"], 0)

        # Competition Score (0-10) - Default to 5
        comp_score = 5

        # Risk Score (0-10)
        risk_map = {"Low": 10, "Unknown": 7, "Medium": 3, "High": 0}
        risk_score = risk_map.get(row["BrandRisk"], 5)

        return roi_score + profit_score + velocity_score + comp_score + risk_score

    df["Score"] = df.apply(calculate_score, axis=1)

    # Filters
    # Shortlist: Profit > 0 AND ROI >= 20% AND BrandRisk != High
    shortlist = df[
        (df["NetProfit"] > 0) & (df["ROI_calc"] >= 20) & (df["BrandRisk"] != "High")
    ].sort_values(by=["Score", "NetProfit"], ascending=False)

    # Do-Not-Buy: Profit <= 0 OR ROI < 20 OR BrandRisk == High
    do_not_buy = df[
        (df["NetProfit"] <= 0) | (df["ROI_calc"] < 20) | (df["BrandRisk"] == "High")
    ].copy()

    def get_reason(row):
        reasons = []
        if row["NetProfit"] <= 0:
            reasons.append("Negative/Zero Profit")
        if row["ROI_calc"] < 20:
            reasons.append(f"Low ROI ({row['ROI_calc']:.1f}%)")
        if row["BrandRisk"] == "High":
            reasons.append("High Brand Risk")
        return ", ".join(reasons)

    do_not_buy["Reason"] = do_not_buy.apply(get_reason, axis=1)

    # Backlog: BrandRisk == Unknown or Medium or Seasonality keywords
    backlog = df[(df["BrandRisk"].isin(["Unknown", "Medium"]))].copy()
    backlog["Next Action"] = backlog["BrandRisk"].apply(
        lambda x: "Check Brand Approval/IP" if x == "Medium" else "Check IP History & Seasonality"
    )

    # Save to CSVs
    shortlist.to_csv(os.path.join(output_dir, "shortlist.csv"), index=False)
    do_not_buy[["ASIN", "Reason"]].to_csv(os.path.join(output_dir, "do_not_buy.csv"), index=False)
    backlog[["ASIN", "Next Action"]].to_csv(os.path.join(output_dir, "backlog.csv"), index=False)

    return shortlist, do_not_buy, backlog


shortlist, dnb, backlog = analyze_data()

# Print results for the final markdown report
print(f"Shortlist Count: {len(shortlist)}")
print(f"Do-Not-Buy Count: {len(dnb)}")
print(f"Backlog Count: {len(backlog)}")
print("\nShortlist Top 15:")
print(
    shortlist.head(15)[
        [
            "ASIN",
            "AmazonTitle",
            "SupplierPrice",
            "SellingPrice",
            "NetProfit",
            "ROI_calc",
            "Velocity",
            "BrandRisk",
            "Score",
        ]
    ].to_string()
)
print("\nDo-Not-Buy Sample:")
print(dnb.head(10)[["ASIN", "Reason"]].to_string())
print("\nBacklog Sample:")
print(backlog.head(10)[["ASIN", "Next Action"]].to_string())
