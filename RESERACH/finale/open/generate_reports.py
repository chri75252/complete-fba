import pandas as pd
import json
from datetime import datetime

# Load the enriched data
csv_path = "RESERACH/finale/open/final_ver_sheet1_enriched.csv"
df = pd.read_csv(csv_path)

# Mock verification results (in a real scenario, this would be loaded from a database or log)
# I am incorporating the "Human Verification" I just performed.
verification_data = {
    "B07WDRQ4J7": {  # Air Wick
        "status": "TEST",
        "notes": "Verified. Price dropped to £29.60 (was £46). Profit reduced to ~£3.30. Returnable. Hazmat warning present but FBA eligible.",
        "verified_price": 29.60,
        "verified_date": datetime.now().strftime("%Y-%m-%d"),
    },
    "B005XKFN0O": {  # Eveready
        "status": "BUY",
        "notes": "Verified. Price £18.99 stable. Breakage risk (Glass). Requires bubble wrap. High profit.",
        "verified_price": 18.99,
        "verified_date": datetime.now().strftime("%Y-%m-%d"),
    },
    "B01IFIJ91Y": {  # Mason Cash
        "status": "BUY",
        "notes": "Verified. Price £26.76. Consistent profit. Fragile (Earthenware).",
        "verified_price": 26.76,
        "verified_date": datetime.now().strftime("%Y-%m-%d"),
    },
    "B07DCXX17M": {  # Adidas
        "status": "AVOID",
        "notes": "HAZMAT (Aerosol). Price dropped to £19.99 (was £25). Loss maker at current price.",
        "verified_price": 19.99,
        "verified_date": datetime.now().strftime("%Y-%m-%d"),
    },
    "B09KCMWXQX": {  # Pan Aroma Red
        "status": "TEST",
        "notes": "Verified. Price £8.99. Huge ROI (300%+) but low absolute profit (£2.77). Meltable risk in summer.",
        "verified_price": 8.99,
        "verified_date": datetime.now().strftime("%Y-%m-%d"),
    },
}


# Apply verification to DataFrame
def apply_verification(row):
    asin = row["ASIN"]
    if asin in verification_data:
        v = verification_data[asin]
        return pd.Series([v["status"], v["notes"], v["verified_price"], v["verified_date"]])
    else:
        return pd.Series(
            ["Pending Verification", "Not manually checked yet", row["SellingPrice"], ""]
        )


df[["Verification_Verdict", "Verification_Notes", "Verified_Price", "Date_Checked"]] = df.apply(
    apply_verification, axis=1
)

# Generate Output A: Top 10 Shortlist (Filtered for BUY/TEST)
top_shortlist = df[df["Verification_Verdict"].isin(["BUY", "TEST"])].copy()
# Add high profit pending ones
pending_high_profit = df[
    (df["Verification_Verdict"] == "Pending Verification") & (df["NetProfit"] > 3)
].head(5)
output_a = pd.concat([top_shortlist, pending_high_profit])

# Save Output A (Markdown)
with open("RESERACH/finale/open/OUTPUT_A_Shortlist.md", "w", encoding="utf-8") as f:
    f.write("# Output A: Top Amazon Wholesale Candidates\n\n")
    f.write(
        "| Status | Product | ASIN | Supplier Price | Amz Price | Exp. Profit | ROI | Notes |\n"
    )
    f.write("|---|---|---|---|---|---|---|---|\n")
    for _, row in output_a.iterrows():
        title = (
            (row["AmazonTitle"][:40] + "...")
            if len(str(row["AmazonTitle"])) > 40
            else row["AmazonTitle"]
        )
        amz_url = f"https://www.amazon.co.uk/dp/{row['ASIN']}"
        supp_url = (
            row["Website(s)"].split("/")[0] if isinstance(row["Website(s)"], str) else "Supplier"
        )
        f.write(
            f"| **{row['Verification_Verdict']}** | [{title}]({amz_url}) | {row['ASIN']} | £{row['SupplierPrice']} | £{row['Verified_Price']} | £{row['NetProfit']} | {row['ROI']} | {row['Verification_Notes']} |\n"
        )

# Save Output B: Full Decision Table
df.to_csv("RESERACH/finale/open/OUTPUT_B_Full_Decision_Table.csv", index=False)

# Save Output C: Missing Verifications
missing = df[df["Verification_Verdict"] == "Pending Verification"][
    ["ASIN", "SupplierTitle", "NetProfit", "ROI"]
].head(20)
with open("RESERACH/finale/open/OUTPUT_C_Missing_Verifications.md", "w", encoding="utf-8") as f:
    f.write("# Output C: Priority Candidates Pending Verification\n\n")
    f.write(
        "These items have high potential profit but were not manually verified in this session.\n\n"
    )
    f.write(missing.to_markdown(index=False))

print("Reports generated successfully.")
