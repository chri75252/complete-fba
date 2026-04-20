import pandas as pd
import sys

csv_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\FINAL STALE\fba_analysis_202 efg newst4 (1).csv"
df = pd.read_csv(csv_path, dtype=str)
df['NetProfit_num'] = pd.to_numeric(df['NetProfit'], errors='coerce')
df['ROI_num'] = pd.to_numeric(df['ROI'], errors='coerce')
df['SupplierPrice_num'] = pd.to_numeric(df['SupplierPrice_incVAT'], errors='coerce')

mask = (df['NetProfit_num'] > 0) & (df['ROI_num'] < 0)
print(f"Rows with NetProfit>0 AND ROI<0: {mask.sum()}")
print(f"Total rows: {len(df)}")
print(f"NetProfit>0 count: {(df['NetProfit_num'] > 0).sum()}")
print(f"ROI<0 count: {(df['ROI_num'] < 0).sum()}")
print(f"ROI_num sample: {df['ROI_num'].head(10).tolist()}")
print(f"NetProfit_num sample: {df['NetProfit_num'].head(10).tolist()}")

if mask.sum() > 0:
    subset = df[mask][['SupplierTitle', 'SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI', 'tier', 'flags']].head(20)
    for _, r in subset.iterrows():
        sp = float(r['SupplierPrice_incVAT']) if pd.notna(pd.to_numeric(r['SupplierPrice_incVAT'], errors='coerce')) else None
        np_val = float(r['NetProfit']) if pd.notna(pd.to_numeric(r['NetProfit'], errors='coerce')) else None
        roi_val = float(r['ROI']) if pd.notna(pd.to_numeric(r['ROI'], errors='coerce')) else None
        expected_roi = (np_val / sp * 100) if sp and np_val else None
        print(f"  {r['SupplierTitle'][:50]} | SP={sp} | NP={np_val} | ROI={roi_val} | expected_ROI={expected_roi:.1f} | tier={r['tier']} | flags={r['flags']}")
