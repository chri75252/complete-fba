
import pandas as pd
import datetime

# CONFIG
CSV_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\deep_analysis_part1.csv"
REPORT_MD_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PHASEA_MANUAL_REPORT_20251223.md"
FINAL_CSV_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\deep_analysis_20251223.csv"

# MANUAL OVERRIDES (Index -> {'action': 'KEEP'|'DROP', 'reason': str, 'pack_verdict': str})
overrides = {
    764: {'action': 'KEEP', 'reason': 'Dimensions 9x9 inch misread as pack 9. 1:1 verified.', 'pack_verdict': '1:1 Match - Dimensions'},
    1078: {'action': 'KEEP', 'reason': '20PCE vs Pack 20. 1:1 verified.', 'pack_verdict': '1:1 Match'},
    298: {'action': 'KEEP', 'reason': '10 Trays vs Pack of 10. 1:1 verified.', 'pack_verdict': '1:1 Match'},
    1069: {'action': 'KEEP', 'reason': 'Values are dimensions. 1:1 verified.', 'pack_verdict': '1:1 Match'},
    920: {'action': 'KEEP', 'reason': 'Dimensions misread as pack. 1:1 verified.', 'pack_verdict': '1:1 Match'},
    
    # Drops / Filtered
    742: {'action': 'DROP', 'reason': 'EXCLUDED: Supplier 50 PCS vs Amazon 200 (4 x 50). RSU=4. Profit Loss.', 'pack_verdict': 'BUNDLE (4x) - LOSS'},
    332: {'action': 'DROP', 'reason': 'EXCLUDED: Sup 5 Bags vs Amz 30 Bags. RSU=6. Profit Loss.', 'pack_verdict': 'BUNDLE (6x) - LOSS'},
    628: {'action': 'DROP', 'reason': 'EXCLUDED: Sup 15m vs Amz 3x15m. RSU=3. Profit Loss.', 'pack_verdict': 'BUNDLE (3x) - LOSS'},
    607: {'action': 'DROP', 'reason': 'EXCLUDED: Sup 15 Pack vs Amz 3x45. RSU=3. Profit Loss.', 'pack_verdict': 'BUNDLE (3x) - LOSS'},
    618: {'action': 'DROP', 'reason': 'EXCLUDED: Amz listing implies (3) pack/gloves. Ambiguous/Loss.', 'pack_verdict': 'Ambiguous Pack'},
    420: {'action': 'DROP', 'reason': 'EXCLUDED: Size mismatch 150ml vs 750ml.', 'pack_verdict': 'Variant Mismatch'},
    752: {'action': 'DROP', 'reason': 'EXCLUDED: Single vs 2x Pack. RSU=2. Loss.', 'pack_verdict': 'BUNDLE (2x) - LOSS'},
    1080: {'action': 'DROP', 'reason': 'EXCLUDED: 3 Way vs 2 Way Socket. Mismatch.', 'pack_verdict': 'Variant Mismatch'},
    850: {'action': 'DROP', 'reason': 'EXCLUDED: Pack 2 vs Pack 6. RSU=3. Loss.', 'pack_verdict': 'BUNDLE (3x) - LOSS'},
}

def generate_report():
    df = pd.read_csv(CSV_PATH)
    
    # Process Overrides
    def apply_override(row):
        idx = row.name
        if idx in overrides:
            ov = overrides[idx]
            if ov['action'] == 'KEEP':
                # Force profit > 0 if it was negative due to bad math
                return True
            elif ov['action'] == 'DROP':
                return False
        return None 
        
    df['manual_override_keep'] = df.apply(apply_override, axis=1)
    
    # Buckets
    verified_recs = []
    verified_filtered = []
    high_recs = []
    high_filtered = []
    
    # Sort by Sales
    df = df.sort_values(by='sales', ascending=False)
    
    for idx, row in df.iterrows():
        keep = row['manual_override_keep']
        
        # Determine Status
        is_exact = row['is_exact_ean']
        category = row['category']
        sales_ok = row['sales'] > 0
        
        # Profit Check (Baseline)
        net_profit_ok = row['NetProfit'] > 0
        adj_profit_ok = row['Adjusted_Profit'] > 0
        
        # Override Logic
        if keep is True:
            # Manually Kept
            final_status = 'REC'
            risk_note = overrides[idx]['reason']
            pack_verdict = overrides[idx]['pack_verdict']
            # Fix Adjusted Profit if needed (set to NetProfit)
            adj_profit = row['NetProfit'] 
        elif keep is False:
            # Manually Dropped
            final_status = 'FILTERED'
            risk_note = overrides[idx]['reason']
            pack_verdict = overrides[idx]['pack_verdict']
            adj_profit = row['Adjusted_Profit']
        else:
            # Automatic Logic
            pack_verdict = row['Pack_Verdict']
            adj_profit = row['Adjusted_Profit']
            risk_note = "EAN Match." if is_exact else "High likelihood."
            
            if sales_ok and net_profit_ok and adj_profit_ok:
                final_status = 'REC'
            else:
                final_status = 'FILTERED'
                if not sales_ok: risk_note = "No Sales."
                elif not net_profit_ok: risk_note = "Net Profit Negative."
                elif not adj_profit_ok: risk_note = "Pack Adjustment Loss."

        # Add to buckets
        item = {
            'Verdict': 'VERIFIED' if is_exact else 'HIGH LIKELIHOOD',
            'Confidence': 100 if is_exact else int(row['title_match']*100),
            'SupplierTitle': row['SupplierTitle'],
            'AmazonTitle': row['AmazonTitle'],
            'Supplier EAN': row['EAN'],
            'Amazon EAN': row['EAN_OnPage'],
            'ASIN': row['ASIN'],
            'SupplierPrice_incVAT': row['SupplierPrice_incVAT'],
            'SellingPrice_incVAT': row['SellingPrice_incVAT'],
            'NetProfit': row['NetProfit'],
            'ROI': row['ROI'],
            'Sales': row['sales'],
            'Pack Verdict': pack_verdict,
            'Adjusted Profit (approx)': adj_profit,
            'Key Match Evidence': f"Match {row['title_match']:.2f}",
            'Key Risks / Notes': risk_note,
            'is_exact_ean': is_exact
        }
        
        if is_exact:
            if final_status == 'REC': verified_recs.append(item)
            else: verified_filtered.append(item)
        elif category == 'HIGH_LIKELIHOOD':
            if final_status == 'REC': high_recs.append(item)
            else: high_filtered.append(item)

    # WRITE MARKDOWN
    with open(REPORT_MD_PATH, 'w', encoding='utf-8') as f:
        f.write(f"# Phase A Manual Match Review\n\n**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d')} (Asia/Dubai)\n\n")
        
        # Summary
        f.write("## Summary counts\n\n")
        f.write(f"| Metric | Count |\n|:--|--:|\n")
        f.write(f"| VERIFIED (Exact EAN, Recommended) | {len(verified_recs)} |\n")
        f.write(f"| HIGH LIKELIHOOD (Recommended) | {len(high_recs)} |\n")
        f.write(f"| VERIFIED (Filtered Out) | {len(verified_filtered)} |\n")
        f.write(f"| HIGH LIKELIHOOD (Filtered Out) | {len(high_filtered)} |\n\n")
        
        def write_table(items, title, limit=75):
            f.write(f"## {title}\n")
            if not items:
                f.write("No items.\n\n")
                return
            
            # Header
            cols = ["Verdict", "Confidence", "SupplierTitle", "AmazonTitle", "Supplier EAN", "Amazon EAN", "ASIN", 
                    "SupplierPrice_incVAT", "SellingPrice_incVAT", "NetProfit", "ROI", "Sales", "Pack Verdict", 
                    "Adjusted Profit (approx)", "Key Match Evidence", "Key Risks / Notes"]
            
            f.write("| " + " | ".join(cols) + " |\n")
            f.write("|" + "|".join([":---"] * len(cols)) + "|\n")
            
            count = 0
            for item in items:
                if count >= limit:
                    break
                
                row_str = "|"
                for k in cols:
                    val = item.get(k, "")
                    if k in ["NetProfit", "Adjusted Profit (approx)"]:
                        try: val = f"£{float(val):.2f}"
                        except: pass
                    elif k in ["SupplierPrice_incVAT", "SellingPrice_incVAT"]:
                        try: val = f"£{str(val).replace('£','')}"
                        except: pass
                    row_str += f" {val} |"
                f.write(row_str + "\n")
                count += 1
            
            if len(items) > limit:
                f.write(f"\n*...and {len(items) - limit} more items.*\n")
            f.write("\n")

        write_table(verified_recs, "VERIFIED (Exact EAN) — RECOMMENDED")
        write_table(verified_filtered, "VERIFIED (Exact EAN) — FILTERED OUT (Audit)", limit=50)
        write_table(high_recs, "HIGH LIKELIHOOD — RECOMMENDED")
        write_table(high_filtered, "HIGH LIKELIHOOD — FILTERED OUT (Audit)", limit=50)

    # Save CSV
    final_df = pd.DataFrame(verified_recs + high_recs + verified_filtered + high_filtered)
    final_df.to_csv(FINAL_CSV_PATH, index=False)
    print("Completed.")

if __name__ == "__main__":
    generate_report()
