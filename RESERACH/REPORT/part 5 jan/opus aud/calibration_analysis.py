import pandas as pd
import re
from collections import Counter
import json

# Read the Excel file
file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\part 5 jan.xlsx"
df = pd.read_excel(file_path)

# Analyze first 50 rows
sample_df = df.head(50)

print("=" * 80)
print("FBA CALIBRATION ANALYSIS - PRE-FLIGHT PATTERN DETECTION")
print("=" * 80)
print(f"\nFile: {file_path}")
print(f"Total Rows: {len(df)}")
print(f"Analyzing First: 50 rows")
print(f"\nColumns: {', '.join(df.columns.tolist())}\n")

# ============================================================================
# TASK 1: DETECT PACK QUANTITY PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 1: PACK QUANTITY PATTERN DETECTION")
print("=" * 80)

explicit_units = set()
trailing_number_examples = []
leading_multiplier_examples = []
dimension_examples = []
capacity_multipack_examples = []
spec_x_examples = []

# Common patterns to look for
unit_patterns = [
    r'\b(\d+)\s*(pcs?|pce|pk|pack|unit|piece)s?\b',
    r'\b(pcs?|pce|pk|pack|unit|piece)s?\s*(\d+)\b',
]

dimension_patterns = [
    r'\b(\d+)\s*(cm|mm|ml|ltr?|kg|g|oz|inch|ft|m)\b',
    r'\b(\d+)\s*x\s*(\d+)\s*(cm|mm|ml|ltr?|kg|g|oz|inch)\b',
]

capacity_multipack_pattern = r'\b(\d+)\s*x\s*(\d+)\s*(ml|g|l|kg|oz)\b'
spec_x_pattern = r'\b(\d+)\s*x\s*(magnification|zoom|microscope|scope|times)\b'
leading_multiplier_pattern = r'^(\d+)\s*x\s+'
trailing_number_pattern = r'\s+(\d+)$'

for idx, row in sample_df.iterrows():
    supplier_title = str(row.get('SupplierTitle', ''))
    amazon_title = str(row.get('AmazonTitle', ''))
    
    # Check for explicit units
    for pattern in unit_patterns:
        matches = re.findall(pattern, supplier_title, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                for part in match:
                    if part.lower() in ['pcs', 'pce', 'pk', 'pack', 'unit', 'piece', 'units', 'pieces', 'packs']:
                        explicit_units.add(part.lower())
    
    # Check for trailing numbers
    trail_match = re.search(trailing_number_pattern, supplier_title)
    if trail_match and len(trailing_number_examples) < 5:
        trailing_number_examples.append({
            'row': idx + 2,  # Excel row (1-indexed + header)
            'supplier': supplier_title,
            'number': trail_match.group(1)
        })
    
    # Check for leading multipliers
    lead_match = re.search(leading_multiplier_pattern, supplier_title)
    if lead_match and len(leading_multiplier_examples) < 5:
        leading_multiplier_examples.append({
            'row': idx + 2,
            'supplier': supplier_title,
            'multiplier': lead_match.group(1)
        })
    
    # Check for dimensions
    for pattern in dimension_patterns:
        dim_matches = re.findall(pattern, supplier_title, re.IGNORECASE)
        if dim_matches and len(dimension_examples) < 5:
            dimension_examples.append({
                'row': idx + 2,
                'supplier': supplier_title,
                'dimension': str(dim_matches[0])
            })
            break
    
    # TASK 1B: Check for capacity multipack patterns in Amazon title
    cap_match = re.search(capacity_multipack_pattern, amazon_title, re.IGNORECASE)
    if cap_match and len(capacity_multipack_examples) < 5:
        capacity_multipack_examples.append({
            'row': idx + 2,
            'amazon': amazon_title,
            'pattern': cap_match.group(0),
            'rsu': cap_match.group(1),
            'capacity': cap_match.group(2) + cap_match.group(3)
        })
    
    # TASK 1C: Check for spec/feature "Nx" patterns
    spec_match = re.search(spec_x_pattern, amazon_title, re.IGNORECASE)
    if spec_match and len(spec_x_examples) < 5:
        spec_x_examples.append({
            'row': idx + 2,
            'amazon': amazon_title,
            'pattern': spec_match.group(0),
            'feature': spec_match.group(2)
        })

print("\n1. EXPLICIT UNITS DETECTED:")
if explicit_units:
    print(f"   Found: {sorted(list(explicit_units))}")
else:
    print("   None detected in sample")

print("\n2. TRAILING NUMBER EXAMPLES:")
if trailing_number_examples:
    for ex in trailing_number_examples[:3]:
        print(f"   Row {ex['row']}: '{ex['supplier']}' → trailing '{ex['number']}'")
else:
    print("   None detected")

print("\n3. LEADING MULTIPLIER EXAMPLES:")
if leading_multiplier_examples:
    for ex in leading_multiplier_examples[:3]:
        print(f"   Row {ex['row']}: '{ex['supplier']}' → starts with '{ex['multiplier']}x'")
else:
    print("   None detected")

print("\n4. DIMENSION EXAMPLES:")
if dimension_examples:
    for ex in dimension_examples[:3]:
        print(f"   Row {ex['row']}: '{ex['supplier']}' → contains dimension '{ex['dimension']}'")
else:
    print("   None detected")

print("\n5. CAPACITY MULTIPACK PATTERNS (Amazon Titles):")
if capacity_multipack_examples:
    for ex in capacity_multipack_examples:
        print(f"   Row {ex['row']}: '{ex['pattern']}' → RSU={ex['rsu']} (NOT {ex['capacity']})")
        print(f"      Full: {ex['amazon'][:80]}...")
else:
    print("   None detected")

print("\n6. SPEC/FEATURE 'Nx' PATTERNS (Non-Pack):")
if spec_x_examples:
    for ex in spec_x_examples:
        print(f"   Row {ex['row']}: '{ex['pattern']}' → feature '{ex['feature']}' (NOT pack count)")
        print(f"      Full: {ex['amazon'][:80]}...")
else:
    print("   None detected")

# ============================================================================
# TASK 2: DETECT SALES SIGNAL
# ============================================================================
print("\n" + "=" * 80)
print("TASK 2: SALES SIGNAL DETECTION")
print("=" * 80)

sales_column = None
sales_needs_parsing = False
sales_sample = []

# Check for common sales column names
sales_candidates = ['sales_numeric', 'bought_in_past_month', 'Sales', 'sales', 'BoughtInPastMonth']
for col in sales_candidates:
    if col in df.columns:
        sales_column = col
        # Check if it needs parsing (contains text like "100+")
        sample_values = df[col].head(10).astype(str).tolist()
        if any('+' in str(v) or 'bought' in str(v).lower() for v in sample_values):
            sales_needs_parsing = True
        sales_sample = sample_values[:5]
        break

print(f"\nSales Column: {sales_column if sales_column else 'NOT DETECTED'}")
if sales_column:
    print(f"Needs Parsing: {sales_needs_parsing}")
    print(f"Sample Values: {sales_sample}")

# ============================================================================
# TASK 3: DETECT BRAND PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 3: BRAND PATTERN DETECTION")
print("=" * 80)

brand_at_start_count = 0
brand_mixed_count = 0
brand_examples = []

# Common brand indicators (all caps at start)
for idx, row in sample_df.head(30).iterrows():
    supplier_title = str(row.get('SupplierTitle', ''))
    
    # Check if starts with uppercase word(s)
    if supplier_title:
        first_word = supplier_title.split()[0] if supplier_title.split() else ''
        if first_word.isupper() and len(first_word) > 2:
            brand_at_start_count += 1
            if len(brand_examples) < 5:
                brand_examples.append({
                    'row': idx + 2,
                    'title': supplier_title,
                    'brand': first_word
                })

brand_position = "start" if brand_at_start_count > 15 else "mixed"

print(f"\nBrand Position: {brand_position}")
print(f"Titles with uppercase start: {brand_at_start_count}/30")
print("\nExamples:")
for ex in brand_examples[:3]:
    print(f"   Row {ex['row']}: '{ex['brand']}' in '{ex['title'][:60]}...'")

# ============================================================================
# TASK 4: CALIBRATION WARNINGS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 4: CALIBRATION WARNINGS")
print("=" * 80)

warnings = []

# Check for potential traps
for idx, row in sample_df.iterrows():
    supplier_title = str(row.get('SupplierTitle', ''))
    amazon_title = str(row.get('AmazonTitle', ''))
    
    # Look for potential model numbers that look like quantities
    model_number_pattern = r'\b(200|300|400|500|1000|2000)\b'
    if re.search(model_number_pattern, supplier_title):
        # Check if it's actually a model number (e.g., "XYZ-2000" or "Model 1000")
        context_pattern = r'(model|type|series|version|mk|v\d|\-\d{3,4}|\d{3,4}\-)'
        if re.search(context_pattern, supplier_title, re.IGNORECASE):
            warnings.append({
                'row': idx + 2,
                'issue': 'Potential model number mistaken for quantity',
                'title': supplier_title
            })
    
    # Check for pipe characters in titles
    if '|' in supplier_title or '|' in amazon_title:
        warnings.append({
            'row': idx + 2,
            'issue': 'Contains pipe character (|) - may break table formatting',
            'title': supplier_title if '|' in supplier_title else amazon_title
        })

print("\nPotential Traps Detected:")
if warnings:
    for warn in warnings[:10]:
        print(f"\n   Row {warn['row']}: {warn['issue']}")
        print(f"      '{warn['title'][:70]}...'")
else:
    print("   No obvious traps detected in sample")

# ============================================================================
# GENERATE CONFIGURATION
# ============================================================================
print("\n\n" + "=" * 80)
print("CALIBRATION CONFIGURATION OUTPUT")
print("=" * 80)

config = f"""
```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {{
    "explicit_units": {sorted(list(explicit_units)) if explicit_units else ["pce", "pcs", "pk", "pack"]},  # Detected units
    "allow_trailing_number_as_qty": {len(trailing_number_examples) > 3},  # {"TRUE - common pattern" if len(trailing_number_examples) > 3 else "FALSE - rare/not detected"}
    "leading_multiplier_check": {len(leading_multiplier_examples) > 2},     # {"TRUE - detected" if len(leading_multiplier_examples) > 2 else "FALSE - rare"}
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "ft", "m"],
    "brand_position": "{brand_position}", # {'start' if brand_at_start_count > 15 else 'mixed'}
    "sales_column": "{sales_column if sales_column else 'NOT_DETECTED'}", # Detected column name
    "capacity_pattern_as_rsu": {len(capacity_multipack_examples) > 0}, # {"TRUE - '3 x 400ml' means RSU=3" if capacity_multipack_examples else "FALSE - not detected"}
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    "table_pipe_sanitization": {any('|' in str(row.get('SupplierTitle', '')) or '|' in str(row.get('AmazonTitle', '')) for _, row in sample_df.iterrows())} # {"TRUE - pipes detected" if any('|' in str(row.get('SupplierTitle', '')) or '|' in str(row.get('AmazonTitle', '')) for _, row in sample_df.iterrows()) else "FALSE"}
}}
# ---------------------------------
```
"""

print(config)

# ============================================================================
# SAVE DETAILED REPORT
# ============================================================================
output_dir = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\opus aud"
report_path = output_dir + r"\CALIBRATION_REPORT_20260106.md"

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# FBA CALIBRATION ANALYSIS REPORT\n")
    f.write(f"**Date:** 2026-01-06\n")
    f.write(f"**File:** part 5 jan.xlsx\n")
    f.write(f"**Total Rows:** {len(df)}\n")
    f.write(f"**Sample Analyzed:** First 50 rows\n\n")
    
    f.write("## EXECUTIVE SUMMARY\n\n")
    f.write(f"- **Explicit Units Detected:** {', '.join(sorted(list(explicit_units))) if explicit_units else 'None'}\n")
    f.write(f"- **Trailing Number Pattern:** {'Common (allow)' if len(trailing_number_examples) > 3 else 'Rare/Not detected'}\n")
    f.write(f"- **Leading Multiplier Pattern:** {'Detected' if len(leading_multiplier_examples) > 2 else 'Rare'}\n")
    f.write(f"- **Capacity Multipack Pattern:** {'Detected ({} examples)'.format(len(capacity_multipack_examples)) if capacity_multipack_examples else 'Not detected'}\n")
    f.write(f"- **Brand Position:** {brand_position.upper()}\n")
    f.write(f"- **Sales Column:** {sales_column if sales_column else 'NOT DETECTED'}\n")
    f.write(f"- **Pipe Character Issues:** {'Yes - sanitization required' if any('|' in str(row.get('SupplierTitle', '')) or '|' in str(row.get('AmazonTitle', '')) for _, row in sample_df.iterrows()) else 'None'}\n\n")
    
    f.write("## DETAILED FINDINGS\n\n")
    
    f.write("### TASK 1: Pack Quantity Patterns\n\n")
    f.write("#### 1.1 Explicit Units\n")
    if explicit_units:
        f.write(f"Detected: `{', '.join(sorted(list(explicit_units)))}`\n\n")
    else:
        f.write("No explicit units detected in sample. Using defaults: `pce, pcs, pk, pack`\n\n")
    
    f.write("#### 1.2 Trailing Numbers\n")
    if trailing_number_examples:
        for ex in trailing_number_examples[:5]:
            f.write(f"- **Row {ex['row']}:** `{ex['supplier']}` → trailing `{ex['number']}`\n")
    else:
        f.write("No trailing number patterns detected.\n")
    f.write("\n")
    
    f.write("#### 1.3 Leading Multipliers\n")
    if leading_multiplier_examples:
        for ex in leading_multiplier_examples[:5]:
            f.write(f"- **Row {ex['row']}:** `{ex['supplier'][:60]}...` → starts with `{ex['multiplier']}x`\n")
    else:
        f.write("No leading multiplier patterns detected.\n")
    f.write("\n")
    
    f.write("#### 1.4 Dimensions\n")
    if dimension_examples:
        for ex in dimension_examples[:5]:
            f.write(f"- **Row {ex['row']}:** Contains `{ex['dimension']}`\n")
    else:
        f.write("No dimension patterns detected.\n")
    f.write("\n")
    
    f.write("### TASK 1B: Capacity Multipack Patterns\n\n")
    if capacity_multipack_examples:
        f.write("**IMPORTANT:** These patterns indicate RSU = first number (NOT capacity multiplication)\n\n")
        for ex in capacity_multipack_examples:
            f.write(f"- **Row {ex['row']}:** `{ex['pattern']}` → **RSU = {ex['rsu']}** (NOT {ex['capacity']})\n")
            f.write(f"  - Full title: {ex['amazon']}\n")
    else:
        f.write("No capacity multipack patterns detected.\n")
    f.write("\n")
    
    f.write("### TASK 1C: Spec/Feature 'Nx' Patterns (Non-Pack)\n\n")
    if spec_x_examples:
        f.write("**WARNING:** These 'Nx' patterns are specifications, NOT pack quantities!\n\n")
        for ex in spec_x_examples:
            f.write(f"- **Row {ex['row']}:** `{ex['pattern']}` → feature `{ex['feature']}` (NOT pack count)\n")
            f.write(f"  - Full title: {ex['amazon']}\n")
    else:
        f.write("No spec/feature 'Nx' patterns detected.\n")
    f.write("\n")
    
    f.write("### TASK 2: Sales Signal\n\n")
    f.write(f"- **Column:** `{sales_column if sales_column else 'NOT DETECTED'}`\n")
    if sales_column:
        f.write(f"- **Needs Parsing:** {sales_needs_parsing}\n")
        f.write(f"- **Sample Values:** {sales_sample}\n\n")
    else:
        f.write("- **Action Required:** Manual identification of sales column\n\n")
    
    f.write("### TASK 3: Brand Patterns\n\n")
    f.write(f"- **Position:** {brand_position.upper()}\n")
    f.write(f"- **Confidence:** {brand_at_start_count}/30 titles start with uppercase word\n\n")
    if brand_examples:
        f.write("**Examples:**\n")
        for ex in brand_examples[:5]:
            f.write(f"- **Row {ex['row']}:** `{ex['brand']}` in title\n")
    f.write("\n")
    
    f.write("### TASK 4: Calibration Warnings\n\n")
    if warnings:
        for warn in warnings[:10]:
            f.write(f"#### Row {warn['row']}: {warn['issue']}\n")
            f.write(f"```\n{warn['title']}\n```\n\n")
    else:
        f.write("No calibration warnings detected in sample.\n\n")
    
    f.write("## CONFIGURATION OUTPUT\n\n")
    f.write(config)
    
    f.write("\n## RECOMMENDATIONS\n\n")
    f.write("1. **Pack Quantity Extraction:**\n")
    if len(trailing_number_examples) > 3:
        f.write("   - Enable trailing number detection (common pattern)\n")
    if len(leading_multiplier_examples) > 2:
        f.write("   - Enable leading multiplier detection (detected pattern)\n")
    if capacity_multipack_examples:
        f.write("   - **CRITICAL:** Implement capacity multipack logic (N x [capacity] → RSU = N)\n")
    
    f.write("\n2. **Brand Detection:**\n")
    if brand_position == "start":
        f.write("   - Consistent brand positioning at start (high confidence)\n")
    else:
        f.write("   - Mixed brand positioning (lower confidence, needs robust matching)\n")
    
    f.write("\n3. **Data Quality:**\n")
    if any('|' in str(row.get('SupplierTitle', '')) or '|' in str(row.get('AmazonTitle', '')) for _, row in sample_df.iterrows()):
        f.write("   - Enable pipe character sanitization for table formatting\n")
    if sales_column:
        if sales_needs_parsing:
            f.write(f"   - Parse `{sales_column}` to extract numeric values ('+' signs detected)\n")
    else:
        f.write("   - **ACTION REQUIRED:** Identify sales column manually\n")
    
    f.write("\n4. **Edge Cases:**\n")
    if warnings:
        f.write(f"   - {len(warnings)} potential traps detected - review warnings section\n")
    if spec_x_examples:
        f.write("   - Implement spec/feature 'Nx' shielding to avoid false positives\n")
    
    f.write("\n---\n")
    f.write("**End of Calibration Report**\n")

print(f"\n\n✅ Detailed report saved to: {report_path}")
print("\nCalibration analysis complete!")
