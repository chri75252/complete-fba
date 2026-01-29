import pandas as pd
import re

df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx')

def extract_pack_count(title):
    if pd.isna(title):
        return 1
    title_lower = str(title).lower()
    pack_patterns = [
        (r'pack\s*of\s*(\d+)', 1),
        (r'set\s*of\s*(\d+)', 1),
        (r'\b(\d+)\s*pack\b', 1),
        (r'\b(\d+)\s*pk\b', 1),
    ]
    for pattern, group in pack_patterns:
        match = re.search(pattern, title_lower)
        if match:
            return int(match.group(group))
    return 1

def extract_multipack_total(title):
    if pd.isna(title):
        return (1, 1, 1)
    title_lower = str(title).lower()
    multipack_patterns = [
        r'\((\d+)\s*x\s*(\d+)\)',
        r'^(\d+)\s*x\s+',
    ]
    for pat in multipack_patterns:
        match = re.search(pat, title_lower)
        if match:
            if len(match.groups()) == 2:
                outer = int(match.group(1))
                inner = int(match.group(2))
                if 2 <= outer <= 20 and inner > outer:
                    return (outer, inner, outer * inner)
            elif len(match.groups()) == 1:
                outer = int(match.group(1))
                if 2 <= outer <= 20:
                    return (outer, 1, outer)
    total_pattern = r'\b(\d+)\s*x\s+(?![\d])'
    match = re.search(total_pattern, title_lower)
    if match:
        total = int(match.group(1))
        if total > 20:
            return (1, total, total)
    pack = extract_pack_count(title)
    return (1, pack, pack)

row = df.iloc[886]
sup_pack = extract_pack_count(row['SupplierTitle'])
amz_multi = extract_multipack_total(row['AmazonTitle'])
amz_total = amz_multi[2]

print(f"SupplierTitle: {row['SupplierTitle']}")
print(f"AmazonTitle: {row['AmazonTitle']}")
print(f"Sup_Pack: {sup_pack}")
print(f"Amz_Multipack: {amz_multi}")
print(f"Amz_Total: {amz_total}")
print()
print(f"Condition check: sup_pack > 0 and amz_total > sup_pack")
print(f"  {sup_pack} > 0 and {amz_total} > {sup_pack}")
print(f"  Result: {sup_pack > 0 and amz_total > sup_pack}")
