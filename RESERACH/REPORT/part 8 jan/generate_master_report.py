import re
import json
import os

def parse_report_for_rows(filepath, source_name):
    """
    Parses report to specific row data objects.
    """
    rows = {}
    current_section = 'UNKNOWN'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        # Detect Section
        if line.startswith('##'):
            upper = line.upper()
            if 'VERIFIED — RECOMMENDED' in upper or 'VERIFIED - RECOMMENDED' in upper:
                current_section = 'VERIFIED'
            elif 'AUDITED OUT' in upper:
                current_section = 'AUDITED'
            elif 'HIGHLY LIKELY' in upper:
                current_section = 'LIKELY'
            elif 'RECOMMENDED (NEW)' in upper:
                current_section = 'POTENTIAL'
            elif 'NEEDS VERIFICATION' in upper:
                current_section = 'NEEDS_VERIF'
        
        # Parse Row
        if line.startswith('|') and 'ASIN' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 5: continue
            
            # Extract basic data
            # Logic depends on source columns
            row_data = {'raw': line, 'section': current_section, 'source': source_name}
            
            # Try to find ASIN
            asin = None
            for p in parts:
                if (len(p) == 10 and p.isalnum()) or p.startswith('B0'):
                    asin = p
                    break
            
            if asin:
                if asin not in rows:
                    rows[asin] = row_data
                else:
                    # Prefer "My" report format if duplicate, unless "Codex" has better info?
                    # Actually, if duplicate, keep the first one found, but we load Mine then Codex.
                    # Wait, if I load Mine first, and Mine has it in 'NEEDS_VERIF', but Codex has it in 'VERIFIED',
                    # I want Codex's version.
                    # So I should store ALL versions and resolve later.
                    pass 
                    
    return rows

# 1. Parse Data
my_rows = parse_report_for_rows('FINAL_COMPREHENSIVE_REPORT_20260113.md', 'Mine')
codex_rows = parse_report_for_rows(r'CODEX final\PHASEA_MANUAL_REPORT_FINAL_COMPLETE_20260113_083500.md', 'Codex')

# 2. Merge Logic
all_asins = set(my_rows.keys()) | set(codex_rows.keys())
final_catalog = {}

for asin in all_asins:
    my_entry = my_rows.get(asin)
    cod_entry = codex_rows.get(asin)
    
    # Determine Winner Entry (for Text/Columns) and Status
    # Default to My Entry if available, else Codex.
    # But if Codex is "Audited" and My is "Verified", use Codex Entry/Status.
    
    final_status = 'NEEDS_VERIF'
    final_row = my_entry if my_entry else cod_entry
    
    my_stat = my_entry['section'] if my_entry else 'MISSING'
    cod_stat = cod_entry['section'] if cod_entry else 'MISSING'
    
    # Logic:
    # 1. AUDITED trumps all (Safety)
    if 'AUDITED' in my_stat or 'AUDITED' in cod_stat:
        final_status = 'AUDITED'
        if 'AUDITED' in cod_stat: final_row = cod_entry # Use the report that audited it
        
    # 2. VERIFIED trumps Likely/Needs
    elif 'VERIFIED' in my_stat or 'VERIFIED' in cod_stat:
        final_status = 'VERIFIED'
        if 'VERIFIED' in cod_stat and my_stat != 'VERIFIED': 
            final_row = cod_entry
            
    # 3. POTENTIAL (My filtered list) trumps Likely? 
    # Actually POTENTIAL is refined Likely. Keep it as POTENTIAL.
    elif 'POTENTIAL' in my_stat:
        final_status = 'POTENTIAL'
        final_row = my_entry
        
    # 4. LIKELY trumps Needs
    elif 'LIKELY' in my_stat or 'LIKELY' in cod_stat:
        final_status = 'LIKELY'
        if 'LIKELY' in cod_stat and my_stat != 'LIKELY':
            final_row = cod_entry
            
    final_catalog[asin] = {'status': final_status, 'row': final_row}

# 3. Generate Report
# Sort ASINs for checking (optional)
sorted_asins = sorted(final_catalog.keys())

# Buckets
buckets = {'VERIFIED': [], 'AUDITED': [], 'LIKELY': [], 'POTENTIAL': [], 'NEEDS_VERIF': []}

for asin in sorted_asins:
    item = final_catalog[asin]
    st = item['status']
    if st in buckets:
        buckets[st].append(item['row'])

# Normalize Rows for Output
# My rows are one format, Codex rows are another.
# It is hard to reformat Codex rows accurately without complex parsing.
# I will output them as is, but maybe group them by source? 
# Or just dump the raw line. The markdown table might look messy if columns don't align.
# My report: | # | SupTitle | AmzTitle | ASIN | ...
# Codex: | Verdict | Conf | SupTitle | ...
# I should try to format Codex rows to match Mine if possible, or just print them.
# Given time constraints, I will preserve the source formatting but note it.
# Actually, mixed columns in one table breaks Markdown rendering.
# I will create sub-sections: "From Analysis A" and "From Analysis B" if needed?
# No, consolidated means merged.
# I will convert Codex rows to My format.
# Codex: | Ver | Conf | SupTitle | AmzTitle | ... | ASIN | ... | Profit | ...
# My:    | # | SupTitle | AmzTitle | ASIN | Price | Price | Profit | ...

def convert_codex_row(raw_line):
    parts = [p.strip() for p in raw_line.split('|')]
    if len(parts) < 10: return raw_line # Fallback
    try:
        # Map
        sup_title = parts[3] # Index might vary, splitting by pipe gives empty first element usually
        # | Verdict | Conf | Title | ...
        # 0 ("") | 1 (Verdict) | 2 (Conf) | 3 (SupTitle) | 4 (AmzTitle) | 5 (SupEAN) | 6 (AmzEAN) | 7 (ASIN) | 8 (SupPrice) | 9 (SellPrice) | 10 (Profit) ...
        
        # Let's handle the split robustly
        clean_parts = [p.strip() for p in parts if p.strip() != '']
        # clean_parts[0]=Verdict, [1]=Conf, [2]=SupTitle, [3]=AmzTitle, [6]=ASIN, [7]=SupPrice, [8]=SellPrice, [9]=Profit
        
        if len(clean_parts) < 9: return raw_line
        
        new_row = f"| - | {clean_parts[2]} | {clean_parts[3]} | {clean_parts[6]} | {clean_parts[7]} | {clean_parts[8]} | {clean_parts[9]} | - | Imported from Codex |"
        return new_row
    except:
        return raw_line

# Write File
with open('FINAL_CONSOLIDATED_MASTER_REPORT.md', 'w', encoding='utf-8') as f:
    f.write("# FINAL CONSOLIDATED MASTER REPORT\n")
    f.write("**Generated:** 2026-01-13\n")
    f.write("**Merges:** Analysis A (My Report) + Analysis B (Codex Report) + Conflict Resolution\n\n")
    
    # SUMMARY
    f.write("## EXECUTIVE SUMMARY\n")
    f.write(f"- **VERIFIED - RECOMMENDED:** {len(buckets['VERIFIED'])}\n")
    f.write(f"- **VERIFIED - AUDITED OUT:** {len(buckets['AUDITED'])}\n")
    f.write(f"- **HIGHLY LIKELY:** {len(buckets['LIKELY'])}\n")
    f.write(f"- **HIGH POTENTIAL (NEW):** {len(buckets['POTENTIAL'])}\n")
    f.write(f"- **NEEDS VERIFICATION:** {len(buckets['NEEDS_VERIF'])}\n\n")
    
    f.write("---\n\n")
    
    # VERIFIED
    f.write(f"## 1. VERIFIED - RECOMMENDED ({len(buckets['VERIFIED'])})\n")
    f.write("| # | Supplier Title | Amazon Title | ASIN | Sup Price | Amz Price | Profit | Sales | Evidence |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for i, item in enumerate(buckets['VERIFIED']):
        line = item['raw']
        if item['source'] == 'Codex':
            line = convert_codex_row(line)
        f.write(line + "\n")
    f.write("\n")
    
    # AUDITED
    f.write(f"## 2. AUDITED OUT / EXCLUDED ({len(buckets['AUDITED'])})\n")
    f.write("| # | Supplier Title | Amazon Title | ASIN | Sup Price | Amz Price | Profit | Sales | Evidence |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for item in buckets['AUDITED']:
        line = item['raw']
        if item['source'] == 'Codex':
            line = convert_codex_row(line)
        f.write(line + "\n")
    f.write("\n")

    # HIGHLY LIKELY
    f.write(f"## 3. HIGHLY LIKELY ({len(buckets['LIKELY'])})\n")
    f.write("| # | Supplier Title | Amazon Title | ASIN | Sup Price | Amz Price | Profit | Sales | Evidence |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for item in buckets['LIKELY']:
        line = item['raw']
        if item['source'] == 'Codex':
            line = convert_codex_row(line)
        f.write(line + "\n")
    f.write("\n")

    # POTENTIAL
    f.write(f"## 4. HIGH POTENTIAL CANDIDATES ({len(buckets['POTENTIAL'])})\n")
    f.write("| Score | ASIN | Profit | Supplier Title | Amazon Title | Reason |\n")
    f.write("|---|---|---|---|---|---|\n")
    for item in buckets['POTENTIAL']:
        # These are from my report Section 5, which has specific columns.
        # Just write raw.
        f.write(item['raw'] + "\n")
    f.write("\n")
    
print("Consolidated Report Generated.")
