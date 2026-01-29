"""
Export all categorized data to a comprehensive CSV for user reference
"""

import pandas as pd
from pathlib import Path

INPUT_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Opus\intermediate_analysis.csv")
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Opus")

# Load the categorized data
df = pd.read_csv(INPUT_PATH)

# Filter to only categorized items (where category is assigned)
# Re-apply categorization logic to get the categories
from analyze_fba_v4_stage2 import categorize_row, get_key_evidence

# Since we can't import directly, let's re-do the categorization
# Load the report data JSON instead
import json
with open(OUTPUT_DIR / 'report_data.json', 'r', encoding='utf-8') as f:
    report_data = json.load(f)

# Combine all categories into a single export
all_items = []

for item in report_data['verified_recommended']:
    item['Category'] = 'VERIFIED_RECOMMENDED'
    all_items.append(item)

for item in report_data['verified_filtered']:
    item['Category'] = 'VERIFIED_FILTERED'
    all_items.append(item)

for item in report_data['highly_likely_recommended']:
    item['Category'] = 'HIGHLY_LIKELY_RECOMMENDED'
    all_items.append(item)

for item in report_data['highly_likely_filtered']:
    item['Category'] = 'HIGHLY_LIKELY_FILTERED'
    all_items.append(item)

for item in report_data['needs_verification']:
    item['Category'] = 'NEEDS_VERIFICATION'
    all_items.append(item)

# Convert to DataFrame
export_df = pd.DataFrame(all_items)

# Reorder columns
column_order = [
    'Category', 'RowID', 'Verdict', 'Confidence', 
    'SupplierTitle', 'AmazonTitle', 
    'Supplier EAN', 'Amazon EAN', 'ASIN',
    'SupplierPrice', 'SellingPrice', 'NetProfit', 'ROI', 'Sales',
    'Pack Verdict', 'Adjusted Profit',
    'Key Match Evidence', 'Filter Reason'
]

export_df = export_df[[c for c in column_order if c in export_df.columns]]

# Save to CSV
export_path = OUTPUT_DIR / 'CATEGORIZED_ITEMS_EXPORT.csv'
export_df.to_csv(export_path, index=False, encoding='utf-8-sig')
print(f"Exported {len(export_df)} categorized items to: {export_path}")

# Also create a summary by category
print("\n===== EXPORT SUMMARY =====")
print(export_df['Category'].value_counts())
