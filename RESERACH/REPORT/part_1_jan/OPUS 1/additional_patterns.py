import pandas as pd
import re

# Read the Excel file
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx', nrows=50)

output_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\OPUS 1\additional_patterns.txt'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("ADDITIONAL PATTERN DETECTION\n")
    f.write("=" * 80 + "\n")

    # Look for PK/PK patterns
    pk_pattern = re.compile(r'\bPK\s*(\d+)\b|\b(\d+)\s*PK\b', re.IGNORECASE)

    f.write("\n=== PK (Pack) PATTERNS ===\n")
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        matches = pk_pattern.findall(supplier_title)
        if matches:
            f.write(f"  Row {idx}: '{supplier_title}' -> {matches}\n")

    # Look for X patterns (like 2x, 3x)
    x_pattern = re.compile(r'\b(\d+)\s*[xX]\s*(\d+)\b')

    f.write("\n=== MULTIPLICATION PATTERNS (NxM) ===\n")
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        matches = x_pattern.findall(supplier_title)
        if matches:
            f.write(f"  Row {idx}: '{supplier_title}' -> {matches}\n")

    # Look for patterns that could be misinterpreted
    f.write("\n=== PATTERNS THAT MIGHT LOOK LIKE QUANTITY BUT ARE DIMENSIONS ===\n")
    dimension_with_x = re.compile(r'(\d+)\s*X\s*(\d+)\s*(CM|MM|L|G)', re.IGNORECASE)
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        matches = dimension_with_x.findall(supplier_title)
        if matches:
            f.write(f"  Row {idx}: '{supplier_title}' -> {matches}\n")

    # Look for model numbers that might be confused with quantities
    f.write("\n=== MODEL NUMBERS/CODES THAT MIGHT BE CONFUSED WITH QUANTITIES ===\n")
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        # Check for patterns like "SDB113", "G9", etc.
        model_pattern = re.compile(r'\b([A-Z]+\d+|\d+[A-Z]+)\b')
        matches = model_pattern.findall(supplier_title)
        if matches:
            f.write(f"  Row {idx}: '{supplier_title}' -> {matches}\n")

    # Check for parenthetical packs like (4 x 50)
    f.write("\n=== NESTED/PARENTHETICAL PACK PATTERNS ===\n")
    nested_pattern = re.compile(r'\((\d+)\s*[xX]\s*(\d+)\)')
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        amazon_title = str(row['AmazonTitle']) if pd.notna(row['AmazonTitle']) else ""
        for title in [supplier_title, amazon_title]:
            matches = nested_pattern.findall(title)
            if matches:
                f.write(f"  Row {idx}: '{title[:80]}...' -> {matches}\n")

    # Check for "Cases" pattern (like "100 CASES")
    f.write("\n=== CASE/BOX PATTERNS ===\n")
    case_pattern = re.compile(r'\b(\d+)\s*(CASES?|BOXES?|CTN|CARTONS?)\b', re.IGNORECASE)
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        matches = case_pattern.findall(supplier_title)
        if matches:
            f.write(f"  Row {idx}: '{supplier_title}' -> {matches}\n")

print(f"Output saved to: {output_path}")
