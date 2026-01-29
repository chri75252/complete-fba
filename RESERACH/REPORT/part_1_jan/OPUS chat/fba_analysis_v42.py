"""
FBA Product Analysis Script - v4.2
Executes the FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md methodology
"""

import os
import re
import math
import pandas as pd
import numpy as np
from datetime import datetime
from difflib import SequenceMatcher

# === CONFIGURATION ===
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\OPUS chat"

# === STAGE 1: Data Loading & Initial Cleaning ===
print("=== STAGE 1: Loading Data ===")
ext = os.path.splitext(INPUT_PATH)[1].lower()
if ext in [".xlsx", ".xls"]:
    df = pd.read_excel(INPUT_PATH)
else:
    df = pd.read_csv(INPUT_PATH)

df["RowID"] = df.index + 1
print(f"Loaded {len(df)} rows")

# Sales column normalization
possible_sales_cols = ["sales_numeric", "bought_in_past_month", "sales", "Sales"]
found_sales_col = None
for col in possible_sales_cols:
    if col in df.columns:
        found_sales_col = col
        break

if found_sales_col:
    df["Sales"] = pd.to_numeric(df[found_sales_col], errors="coerce").fillna(0)
else:
    df["Sales"] = 0

# === EAN Cleaning ===
def _coerce_to_intlike_string(x) -> str:
    if pd.isna(x):
        return ""
    if isinstance(x, float):
        if x == int(x):
            return str(int(round(x)))
        return str(x)
    return str(x)

def clean_to_digits(x) -> str:
    s = _coerce_to_intlike_string(x).strip()
    if not s:
        return ""
    if "e" in s.lower():
        return ""
    return re.sub(r"\D", "", s)

if "EAN" in df.columns:
    df["EAN_digits"] = df["EAN"].apply(clean_to_digits)
else:
    df["EAN_digits"] = ""

if "EAN_OnPage" in df.columns:
    df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(clean_to_digits)
else:
    df["EAN_OnPage_digits"] = ""

# === STAGE 2: Title Similarity ===
print("=== STAGE 2: Computing Title Similarity ===")
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)

# === STAGE 3: STRICT EAN Matching ===
print("=== STAGE 3: EAN Validation ===")
def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    total = 0
    for i, ch in enumerate(body[::-1], start=1):
        d = int(ch)
        total += d * 3 if i % 2 == 1 else d
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits: str) -> str:
    if not isinstance(digits, str) or not digits.isdigit():
        return ""
    if gtin_checksum_ok(digits):
        return digits
    for target_len in [13, 12, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    norm = normalize_ean(digits)
    if len(norm) not in (8, 12, 13, 14):
        return False
    if re.search(r"0{6,}$", norm):
        return False
    return gtin_checksum_ok(norm)

df["EAN_norm"] = df["EAN_digits"].apply(normalize_ean)
df["EAN_OnPage_norm"] = df["EAN_OnPage_digits"].apply(normalize_ean)

df["EAN_strict_valid"] = df["EAN_norm"].apply(is_strict_valid_barcode)
df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_norm"].apply(is_strict_valid_barcode)

df["is_exact_ean_strict"] = (
    df["EAN_strict_valid"]
    & df["EAN_OnPage_strict_valid"]
    & (df["EAN_norm"] == df["EAN_OnPage_norm"])
    & (df["EAN_norm"] != "")
)

print(f"Exact EAN matches: {df['is_exact_ean_strict'].sum()}")

# === STAGE 4: Pack Size Extraction ===
print("=== STAGE 4: Pack Size Analysis ===")
DEFAULT_DIM_UNITS = ["cm", "mm", "ml", "l", "ltr", "g", "kg", "oz", "inch", "ft"]

def _has_dimension_context(title: str) -> bool:
    t = str(title).lower()
    if re.search(r"\b\d+(\.\d+)?\s*(inch|in)\b", t) and not re.search(r"\b\d+\s*in\s*1\b", t):
        return True
    if re.search(r"\b\d+(\.\d+)?\s*[x×]\s*\d+(\.\d+)?\s*(cm|mm|inch|in)\b", t):
        return True
    return False

def extract_supplier_qty(title) -> int:
    t = str(title).lower().strip()
    m = re.search(r"\b(\d+)\s*(pc|pcs)\b", t)
    if m: return int(m.group(1))
    m = re.search(r"\b(\d+)\s*pack\b", t)
    if m: return int(m.group(1))
    m = re.search(r"\b(\d+)\s*pk\b", t)
    if m: return int(m.group(1))
    return 1

def extract_amazon_total(title) -> int:
    t = str(title).lower().strip()
    m = re.search(r"\b(\d+)\s*[x×]\s*(\d+)\b", t)
    if m:
        if not _has_dimension_context(title):
            outer = int(m.group(1))
            inner = int(m.group(2))
            if outer <= 100:
                return outer * inner
    m = re.search(r"\bpack of\s*(\d+)\b", t) or re.search(r"\b(\d+)\s*-\s*pack\b", t) or re.search(r"\b(\d+)\s*pack\b", t)
    if m:
        val = int(m.group(1))
        if val <= 100:
            return val
    return 1

df["Sup_Qty"] = df["SupplierTitle"].apply(extract_supplier_qty)
df["Amz_Total"] = df["AmazonTitle"].apply(extract_amazon_total)

def compute_pack_fields(row):
    sup_qty = float(row["Sup_Qty"])
    amz_total = float(row["Amz_Total"])
    
    if sup_qty <= 0 or amz_total <= 0:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})
    
    if sup_qty > 1 and amz_total > 1 and abs(sup_qty - amz_total) < 0.1:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": "Qty-inside equality shield"})
    
    ratio = amz_total / sup_qty
    
    if ratio > 1.000001:
        rsu = int(math.ceil(ratio))
        warn = f"Requires {rsu} supplier packs"
        return pd.Series({"RSU": rsu, "Pack_Mode": "bundle", "Pack_Warning": warn})
    
    if sup_qty > amz_total + 1e-6 and sup_qty > 1:
        return pd.Series({"RSU": 1, "Pack_Mode": "split", "Pack_Warning": "Supplier pack larger; split feasibility required"})
    
    return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})

df[["RSU", "Pack_Mode", "Pack_Warning"]] = df.apply(compute_pack_fields, axis=1)

def recalculate_profit_after_pack(row):
    try:
        original_profit = float(row["NetProfit"])
        supplier_cost = float(row["SupplierPrice_incVAT"])
        rsu = float(row["RSU"])
        if rsu > 1:
            adjustment = supplier_cost * (rsu - 1)
            return original_profit - adjustment
        return original_profit
    except:
        return 0.0

df["Adjusted_Profit"] = df.apply(recalculate_profit_after_pack, axis=1)

def pack_verdict(row):
    if row["Pack_Mode"] == "1:1":
        return "1:1 Match"
    if row["Pack_Mode"] == "bundle":
        rsu = int(row["RSU"])
        if row["Adjusted_Profit"] > 0:
            return f"BUNDLE ({rsu}x) - OK"
        else:
            return f"BUNDLE ({rsu}x) - LOSS"
    if row["Pack_Mode"] == "split":
        return "SPLIT (Supplier pack larger) - VERIFY separability"
    return "1:1 Match"

df["Pack_Verdict"] = df.apply(pack_verdict, axis=1)

# === STAGE 5: Product Categorization ===
print("=== STAGE 5: Categorizing Products ===")

# Known brand patterns for matching
KNOWN_BRANDS = [
    "AMTECH", "ROLSON", "DRAPER", "FAIRY", "DETTOL", "DUNLOP", "MASON CASH", "PYREX",
    "EVERBUILD", "HARRIS", "STATUS", "EXTRASTAR", "ROUNDUP", "TIDYZ", "SOUDAL", "KILROCK",
    "CHEF AID", "BLUE CANYON", "PAN AROMA", "VINERS", "WHAM", "CURVER", "BEAUFORT",
    "SCHOTT ZWIESEL", "BACOFOIL", "SPONTEX", "QUEST", "DOFF", "CORAL", "TALA",
    "ELLIOTT", "PRODEC", "APOLLO", "MINKY", "SUPERIOR", "PRIMA", "KINGAVON", "EXTRA SELECT"
]

def extract_brand(title):
    """Extract brand from title"""
    if pd.isna(title):
        return None
    t = str(title).upper()
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if brand.upper() in t:
            return brand
    # First word might be brand
    words = t.split()
    if words:
        return words[0]
    return None

def brands_match(sup_title, amz_title):
    """Check if brands match between titles"""
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    
    if sup_brand and amz_brand:
        return sup_brand.upper() == amz_brand.upper()
    return False

def categorize_product(row):
    """Categorize product according to v4.2 methodology"""
    
    sup_title = str(row.get("SupplierTitle", "")).upper()
    amz_title = str(row.get("AmazonTitle", "")).upper()
    title_sim = row.get("title_match", 0)
    adjusted_profit = row.get("Adjusted_Profit", 0)
    is_exact_ean = row.get("is_exact_ean_strict", False)
    rsu = row.get("RSU", 1)
    
    # Determine EAN status
    ean_sup = str(row.get("EAN_norm", ""))
    ean_amz = str(row.get("EAN_OnPage_norm", ""))
    ean_status = "both_missing"
    if ean_sup and ean_amz:
        if ean_sup == ean_amz:
            ean_status = "exact_match"
        else:
            ean_status = "different"
    elif ean_sup or ean_amz:
        ean_status = "one_missing"
    
    # Check brand match
    brand_matches = brands_match(sup_title, amz_title)
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    
    # === VERIFIED: Exact EAN match ===
    if is_exact_ean:
        if adjusted_profit <= 0:
            return "VERIFIED_FILTERED", 95, f"Exact EAN match; {sup_brand}", f"Requires {int(rsu)} units; adjusted profit is negative"
        else:
            return "VERIFIED", 95, f"Exact EAN match; {sup_brand}", "-"
    
    # === HIGHLY LIKELY: Brand + Product match ===
    if brand_matches and adjusted_profit > 0:
        # Strong brand match with good title similarity
        if title_sim >= 0.5:
            evidence = f"{sup_brand}; {int(title_sim*100)}% title"
            return "HIGHLY_LIKELY", 85, evidence, "-"
        elif title_sim >= 0.35:
            # Moderate similarity but brand matches
            evidence = f"{sup_brand}; {int(title_sim*100)}% title"
            return "HIGHLY_LIKELY", 80, evidence, "-"
    
    # Brand matches but unprofitable
    if brand_matches and adjusted_profit <= 0:
        evidence = f"{sup_brand}; {int(title_sim*100)}% title"
        return "HIGHLY_LIKELY_FILTERED", 80, evidence, f"Requires {int(rsu)} units; adjusted profit is negative"
    
    # === NEEDS VERIFICATION scenarios ===
    
    # Scenario A/B: Brand absent or different
    if not brand_matches and title_sim >= 0.4 and adjusted_profit > 0:
        # One brand missing or different brands - but titles align
        if ean_status == "one_missing":
            # Missing EAN is more favorable
            return "NEEDS_VERIFICATION", 70, f"{int(title_sim*100)}% title; EAN missing", "Verify brand on packaging"
        elif ean_status == "different":
            # Different EANs - needs more scrutiny
            return "NEEDS_VERIFICATION", 65, f"{int(title_sim*100)}% title; EANs differ", "Different EANs - verify if rebrand"
        else:
            return "NEEDS_VERIFICATION", 70, f"{int(title_sim*100)}% title", "Verify brand"
    
    # Scenario C/D/E: Pack ambiguous, variant uncertain, capacity tolerance
    if brand_matches and title_sim >= 0.3 and adjusted_profit > 0:
        # Brand matches but something else is uncertain
        if rsu > 1:
            return "NEEDS_VERIFICATION", 72, f"{sup_brand}; Pack ambiguous", "Verify pack count"
        else:
            return "NEEDS_VERIFICATION", 75, f"{sup_brand}; {int(title_sim*100)}% title", "Verify variant"
    
    # Too weak - don't include
    return None, 0, "", ""

# Apply categorization
results = df.apply(categorize_product, axis=1, result_type='expand')
df["Category"] = results[0]
df["Confidence"] = results[1]
df["Evidence"] = results[2]
df["Filter_Reason"] = results[3]

# === Count categories ===
verified_rec = df[df["Category"] == "VERIFIED"]
verified_filt = df[df["Category"] == "VERIFIED_FILTERED"]
highly_likely_rec = df[df["Category"] == "HIGHLY_LIKELY"]
highly_likely_filt = df[df["Category"] == "HIGHLY_LIKELY_FILTERED"]
needs_ver = df[df["Category"] == "NEEDS_VERIFICATION"]

print(f"\n=== CATEGORIZATION RESULTS ===")
print(f"VERIFIED - RECOMMENDED: {len(verified_rec)}")
print(f"VERIFIED - FILTERED OUT: {len(verified_filt)}")
print(f"HIGHLY LIKELY - RECOMMENDED: {len(highly_likely_rec)}")
print(f"HIGHLY LIKELY - FILTERED OUT: {len(highly_likely_filt)}")
print(f"NEEDS VERIFICATION: {len(needs_ver)}")

# === STAGE 6: Generate Report ===
print("\n=== STAGE 6: Generating Report ===")

def format_price(val):
    try:
        return f"£{float(val):.2f}"
    except:
        return str(val)

def truncate(s, max_len=42):
    s = str(s) if not pd.isna(s) else "-"
    return s[:max_len] if len(s) > max_len else s

def format_ean(val):
    if pd.isna(val) or str(val).strip() == "" or str(val) == "nan":
        return "-"
    return str(val)

report_date = datetime.now().strftime("%Y%m%d")
report_lines = []

report_lines.append("# PHASEA MANUAL REPORT")
report_lines.append("")
report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report_lines.append(f"**Input File:** part_1_jan.xlsx")
report_lines.append(f"**Methodology:** AG1 v4.2 (OPUS chat)")
report_lines.append(f"**Total Rows Analyzed:** {len(df)}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## Summary Counts")
report_lines.append("")
report_lines.append(f"- **VERIFIED — RECOMMENDED:** {len(verified_rec)}")
report_lines.append(f"- **VERIFIED — FILTERED OUT:** {len(verified_filt)}")
report_lines.append(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(highly_likely_rec)}")
report_lines.append(f"- **HIGHLY LIKELY — FILTERED OUT:** {len(highly_likely_filt)}")
report_lines.append(f"- **NEEDS VERIFICATION:** {len(needs_ver)}")
report_lines.append(f"- **TOTAL ACTIONABLE:** {len(verified_rec) + len(highly_likely_rec)}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

def build_table(df_subset, show_filter_reason=False):
    """Build a fixed-width table from dataframe subset"""
    lines = []
    
    # Header
    if show_filter_reason:
        header = "| Row | SupplierTitle                            | AmazonTitle                                   |   Profit |  AdjProfit | Sales | Pack Verdict              | Filter Reason                        |"
        sep    = "|-----|------------------------------------------|-----------------------------------------------|----------|------------|-------|---------------------------|--------------------------------------|"
    else:
        header = "| Row | SupplierTitle                            | AmazonTitle                                   |   Profit |  AdjProfit | Sales | Pack Verdict              | Evidence                             |"
        sep    = "|-----|------------------------------------------|-----------------------------------------------|----------|------------|-------|---------------------------|--------------------------------------|"
    
    lines.append("```text")
    lines.append(header)
    lines.append(sep)
    
    for _, row in df_subset.sort_values("Sales", ascending=False).head(60).iterrows():
        row_id = str(int(row.get("RowID", 0))).rjust(4)
        sup = truncate(row.get("SupplierTitle", ""), 40).ljust(40)
        amz = truncate(row.get("AmazonTitle", ""), 45).ljust(45)
        profit = format_price(row.get("NetProfit", 0)).rjust(8)
        adj_profit = format_price(row.get("Adjusted_Profit", 0)).rjust(10)
        sales = str(int(row.get("Sales", 0))).rjust(5)
        pack_v = truncate(row.get("Pack_Verdict", "1:1 Match"), 25).ljust(25)
        
        if show_filter_reason:
            reason = truncate(row.get("Filter_Reason", "-"), 36).ljust(36)
            line = f"|{row_id} | {sup} | {amz} | {profit} | {adj_profit} | {sales} | {pack_v} | {reason} |"
        else:
            evidence = truncate(row.get("Evidence", "-"), 36).ljust(36)
            line = f"|{row_id} | {sup} | {amz} | {profit} | {adj_profit} | {sales} | {pack_v} | {evidence} |"
        
        lines.append(line)
    
    lines.append("```")
    return lines

# VERIFIED - RECOMMENDED
report_lines.append(f"## VERIFIED — RECOMMENDED (count={len(verified_rec)})")
report_lines.append("")
if len(verified_rec) > 0:
    report_lines.extend(build_table(verified_rec, show_filter_reason=False))
else:
    report_lines.append("*No exact EAN matches found in this dataset.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# VERIFIED - FILTERED OUT
report_lines.append(f"## VERIFIED — FILTERED OUT (count={len(verified_filt)})")
report_lines.append("")
if len(verified_filt) > 0:
    report_lines.extend(build_table(verified_filt, show_filter_reason=True))
else:
    report_lines.append("*No filtered exact EAN matches.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# HIGHLY LIKELY - RECOMMENDED
report_lines.append(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_rec)})")
report_lines.append("")
if len(highly_likely_rec) > 0:
    report_lines.extend(build_table(highly_likely_rec, show_filter_reason=False))
else:
    report_lines.append("*No highly likely matches found.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# HIGHLY LIKELY - FILTERED OUT
report_lines.append(f"## HIGHLY LIKELY — FILTERED OUT (count={len(highly_likely_filt)})")
report_lines.append("")
if len(highly_likely_filt) > 0:
    report_lines.extend(build_table(highly_likely_filt, show_filter_reason=True))
else:
    report_lines.append("*No filtered highly likely matches.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# NEEDS VERIFICATION
report_lines.append(f"## NEEDS VERIFICATION (count={len(needs_ver)})")
report_lines.append("")
if len(needs_ver) > 0:
    report_lines.extend(build_table(needs_ver, show_filter_reason=True))
else:
    report_lines.append("*No items requiring verification.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Reconciliation
report_lines.append("## Reconciliation")
report_lines.append("")
report_lines.append(f"- Total rows in input: {len(df)}")
report_lines.append(f"- VERIFIED (total): {len(verified_rec) + len(verified_filt)}")
report_lines.append(f"- HIGHLY LIKELY (total): {len(highly_likely_rec) + len(highly_likely_filt)}")
report_lines.append(f"- NEEDS VERIFICATION: {len(needs_ver)}")
total_categorized = len(verified_rec) + len(verified_filt) + len(highly_likely_rec) + len(highly_likely_filt) + len(needs_ver)
report_lines.append(f"- Rows categorized: {total_categorized}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("*Report generated by AG1 v4.2 FBA Analysis System (OPUS chat)*")
report_lines.append(f"*Date: {datetime.now().strftime('%Y-%m-%d')}*")

# === Save Report ===
report_content = "\n".join(report_lines)
output_path = os.path.join(OUTPUT_DIR, f"PHASEA_MANUAL_REPORT_{report_date}.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"\n=== REPORT SAVED ===")
print(f"Output: {output_path}")

# Also save a CSV for reference
csv_path = os.path.join(OUTPUT_DIR, f"analysis_results_{report_date}.csv")
export_cols = ["RowID", "ASIN", "SupplierTitle", "AmazonTitle", "EAN_norm", "EAN_OnPage_norm", 
               "NetProfit", "Adjusted_Profit", "Sales", "Pack_Verdict", "Category", "Confidence", "Evidence", "Filter_Reason"]
df[df["Category"].notna()][export_cols].to_csv(csv_path, index=False)
print(f"CSV: {csv_path}")
