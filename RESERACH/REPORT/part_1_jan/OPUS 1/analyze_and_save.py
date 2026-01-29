import pandas as pd
import re
import json

# Read the Excel file
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx', nrows=50)

output_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\OPUS 1\analysis_output.txt'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("RAW DATA - FIRST 50 ROWS\n")
    f.write("=" * 100 + "\n\n")

    for idx, row in df.iterrows():
        f.write(f"\n--- Row {idx} ---\n")
        f.write(f"EAN: {row['EAN']}\n")
        f.write(f"SupplierTitle: {row['SupplierTitle']}\n")
        f.write(f"AmazonTitle: {row['AmazonTitle']}\n")
        f.write(f"bought_in_past_month: {row['bought_in_past_month']}\n")
        f.write(f"SupplierPrice_exVAT: {row['SupplierPrice_exVAT']}\n")
        f.write(f"SellingPrice_incVAT: {row['SellingPrice_incVAT']}\n")
        f.write(f"NetProfit: {row['NetProfit']}\n")
    
    # Pattern Analysis
    f.write("\n" + "=" * 100 + "\n")
    f.write("PATTERN DETECTION ANALYSIS\n")
    f.write("=" * 100 + "\n\n")
    
    # Pattern detection for pack quantities
    explicit_units = []
    trailing_numbers = []
    leading_multipliers = []
    dimension_formats = []
    
    unit_pattern = re.compile(r'\b(\d+)\s*(pcs?|pce|pk|pack|unit|set|piece|pieces)\b', re.IGNORECASE)
    trailing_number_pattern = re.compile(r'\s(\d{2,})$')  # Numbers >= 2 digits at end
    leading_multiplier_pattern = re.compile(r'^(\d+)\s*x\s+', re.IGNORECASE)
    dimension_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(cm|mm|ml|ltr|l|kg|g|oz|inch|")\b', re.IGNORECASE)
    
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        amazon_title = str(row['AmazonTitle']) if pd.notna(row['AmazonTitle']) else ""
        
        # Check for explicit units in supplier title
        matches = unit_pattern.findall(supplier_title)
        if matches:
            explicit_units.append((idx, 'supplier', supplier_title, matches))
        
        # Check for explicit units in amazon title
        matches = unit_pattern.findall(amazon_title)
        if matches:
            explicit_units.append((idx, 'amazon', amazon_title, matches))
        
        # Check for trailing numbers in supplier title
        match = trailing_number_pattern.search(supplier_title)
        if match:
            trailing_numbers.append((idx, supplier_title, match.group(1)))
        
        # Check for leading multipliers
        match = leading_multiplier_pattern.search(supplier_title)
        if match:
            leading_multipliers.append((idx, 'supplier', supplier_title, match.group(1)))
        
        match = leading_multiplier_pattern.search(amazon_title)
        if match:
            leading_multipliers.append((idx, 'amazon', amazon_title, match.group(1)))
        
        # Check for dimension formats
        matches = dimension_pattern.findall(supplier_title)
        if matches:
            dimension_formats.append((idx, 'supplier', supplier_title, matches))
        
        matches = dimension_pattern.findall(amazon_title)
        if matches:
            dimension_formats.append((idx, 'amazon', amazon_title, matches))
    
    f.write("=== EXPLICIT UNIT PATTERNS FOUND ===\n")
    for item in explicit_units:
        f.write(f"  Row {item[0]} ({item[1]}): '{item[2]}' -> {item[3]}\n")
    
    f.write("\n=== TRAILING NUMBER PATTERNS FOUND ===\n")
    for item in trailing_numbers:
        f.write(f"  Row {item[0]}: '{item[1]}' -> ends with '{item[2]}'\n")
    
    f.write("\n=== LEADING MULTIPLIER PATTERNS FOUND ===\n")
    for item in leading_multipliers:
        f.write(f"  Row {item[0]} ({item[1]}): '{item[2]}' -> starts with '{item[3]}x'\n")
    
    f.write("\n=== DIMENSION FORMATS FOUND ===\n")
    for item in dimension_formats:
        f.write(f"  Row {item[0]} ({item[1]}): '{item[2]}' -> {item[3]}\n")
    
    # Brand position analysis
    f.write("\n=== BRAND POSITION ANALYSIS ===\n")
    first_words = {}
    for idx, row in df.iterrows():
        supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
        if supplier_title:
            first_word = supplier_title.split()[0] if supplier_title.split() else ""
            if first_word.upper() not in first_words:
                first_words[first_word.upper()] = 0
            first_words[first_word.upper()] += 1
    
    for word, count in sorted(first_words.items(), key=lambda x: -x[1]):
        f.write(f"  '{word}': {count} occurrences\n")
    
    # Sales column analysis
    f.write("\n=== SALES COLUMN ANALYSIS ===\n")
    f.write("bought_in_past_month unique values:\n")
    sales_values = df['bought_in_past_month'].unique()
    for val in sales_values:
        f.write(f"  {repr(val)} (type: {type(val).__name__})\n")
    
    f.write("\nSales data type: " + str(df['bought_in_past_month'].dtype) + "\n")

print(f"Analysis saved to: {output_path}")
