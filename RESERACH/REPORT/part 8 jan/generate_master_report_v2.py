import re
import json
import os

def parse_report_for_rows(filepath, source_name):
    rows = {}
    current_section = 'UNKNOWN'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line_s = line.strip()
        # Flexible Header Detection
        if line_s.startswith('##'):
            upper = line_s.upper()
            if 'VERIFIED' in upper and ('RECOMMENDED' in upper or 'CONFIRMED' in upper):
                current_section = 'VERIFIED'
            elif 'AUDITED' in upper or 'EXCLUDED' in upper:
                current_section = 'AUDITED'
            elif 'HIGHLY LIKELY' in upper or 'LIKELY MATCH' in upper:
                current_section = 'LIKELY'
            elif 'SECTION 5' in upper or 'NEXT BATCH' in upper or 'POTENTIAL' in upper:
                current_section = 'POTENTIAL'
            elif 'NEEDS VERIFICATION' in upper or 'LOWER CONFIDENCE' in upper:
                current_section = 'NEEDS_VERIF'
            else:
                pass # Keep previous section or unknown? Best to reset to UNKNOWN if it's a major header
                # current_section = 'UNKNOWN' 

        # Parse Row
        if line_s.startswith('|'):
            if 'ASIN' in line_s or '---' in line_s or 'Score' in line_s: continue
            
            parts = [p.strip() for p in line_s.split('|')]
            if len(parts) < 3: continue
            
            # Try to find ASIN
            asin = None
            for p in parts:
                if (len(p) == 10 and p.isalnum()) or p.startswith('B0'):
                    asin = p
                    break
            
            if asin:
                # Store if not exists or override based on logic?
                # For now just store.
                if asin not in rows:
                    rows[asin] = {'raw': line_s, 'section': current_section, 'source': source_name}

    return rows

# 1. Parse
my_rows = parse_report_for_rows('FINAL_COMPREHENSIVE_REPORT_20260113.md', 'Mine')
codex_rows = parse_report_for_rows(r'CODEX final\PHASEA_MANUAL_REPORT_FINAL_COMPLETE_20260113_083500.md', 'Codex')

# 2. Merge
all_asins = set(my_rows.keys()) | set(codex_rows.keys())
final_catalog = {}

for asin in all_asins:
    my_entry = my_rows.get(asin)
    cod_entry = codex_rows.get(asin)
    
    final_status = 'NEEDS_VERIF'
    final_row = my_entry if my_entry else cod_entry
    
    my_stat = my_entry['section'] if my_entry else 'MISSING'
    cod_stat = cod_entry['section'] if cod_entry else 'MISSING'
    
    # Priority Logic
    # 1. AUDITED (Safety)
    if 'AUDITED' in my_stat or 'AUDITED' in cod_stat:
        final_status = 'AUDITED'
        if 'AUDITED' in cod_stat: final_row = cod_entry 
        # If I audited it, keep my row (unless Codex audited it too)
        
    # 2. VERIFIED (Gold Standdard)
    elif 'VERIFIED' in my_stat or 'VERIFIED' in cod_stat:
        final_status = 'VERIFIED'
        if 'VERIFIED' in cod_stat and my_stat != 'VERIFIED':
            final_row = cod_entry # Use Codex row if I missed it
            
    # 3. LIKELY
    elif 'LIKELY' in my_stat or 'LIKELY' in cod_stat:
        final_status = 'LIKELY'
        if 'LIKELY' in cod_stat and my_stat != 'LIKELY':
            final_row = cod_entry

    # 4. POTENTIAL (Clean up duplicates)
    elif 'POTENTIAL' in my_stat:
        # If it's not verified/likely/audited elsewhere (already handled by elifs), it stays Potential
        final_status = 'POTENTIAL'
        
    # 5. NEEDS VERIF
    elif 'NEEDS_VERIF' in my_stat or 'NEEDS_VERIF' in cod_stat:
        final_status = 'NEEDS_VERIF'
        
    final_catalog[asin] = {'status': final_status, 'row': final_row}

# 3. Output
buckets = {'VERIFIED': [], 'AUDITED': [], 'LIKELY': [], 'POTENTIAL': [], 'NEEDS_VERIF': []}
sorted_asins = sorted(final_catalog.keys())

for asin in sorted_asins:
    item = final_catalog[asin]
    if item['status'] in buckets:
        buckets[item['status']].append(item['row'])

def convert_codex_row(raw_line):
    parts = [p.strip() for p in raw_line.split('|')]
    if len(parts) < 9: return raw_line
    # Map Codex to Mine format roughly
    try:
         # Clean empty strings
        p = [x for x in parts if x]
        # p[0]=Ver, p[1]=Conf, p[2]=SupTitle, p[3]=AmzTitle, p[6]=ASIN, p[7]=SupPrice, p[8]=AmzPrice, p[9]=Profit
        if len(p) < 9: return raw_line
        return f"| - | {p[2]} | {p[3]} | {p[6]} | {p[7]} | {p[8]} | {p[9]} | - | Imported Codex |"
    except:
        return raw_line

with open('FINAL_CONSOLIDATED_MASTER_REPORT.md', 'w', encoding='utf-8') as f:
    f.write("# FINAL CONSOLIDATED MASTER REPORT\n")
    f.write("**Generated:** 2026-01-13\n")
    f.write("**Sources:** Validated Agent Report + Codex Final Report\n\n")

    f.write("## EXECUTIVE SUMMARY\n")
    f.write(f"- **VERIFIED - RECOMMENDED:** {len(buckets['VERIFIED'])}\n")
    f.write(f"- **VERIFIED - AUDITED OUT:** {len(buckets['AUDITED'])}\n")
    f.write(f"- **HIGHLY LIKELY:** {len(buckets['LIKELY'])}\n")
    f.write(f"- **HIGH POTENTIAL (NEW):** {len(buckets['POTENTIAL'])}\n")
    f.write(f"- **NEEDS VERIFICATION:** {len(buckets['NEEDS_VERIF'])}\n")
    f.write(f"- **TOTAL PROCESSED:** {len(final_catalog)}\n\n")
    f.write("---\n\n")

    f.write(f"## 1. VERIFIED - RECOMMENDED ({len(buckets['VERIFIED'])})\n")
    f.write("| # | Supplier Title | Amazon Title | ASIN | Sup Price | Amz Price | Profit | Sales | Evidence |\n")
    f.write("|---|---|---|---|---|---|---|---|---| \n")
    for item in buckets['VERIFIED']:
        line = item['raw']
        if item['source'] == 'Codex': line = convert_codex_row(line)
        f.write(line + "\n")
    f.write("\n")

    f.write(f"## 2. AUDITED OUT / EXCLUDED ({len(buckets['AUDITED'])})\n")
    f.write("| # | Supplier Title | Amazon Title | ASIN | Sup Price | Amz Price | Profit | Sales | Reason |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for item in buckets['AUDITED']:
        line = item['raw']
        if item['source'] == 'Codex': line = convert_codex_row(line)
        f.write(line + "\n")
    f.write("\n")

    f.write(f"## 3. HIGHLY LIKELY ({len(buckets['LIKELY'])})\n")
    f.write("| # | Supplier Title | Amazon Title | ASIN | Sup Price | Amz Price | Profit | Sales | Evidence |\n")
    f.write("|---|---|---|---|---|---|---|---|---| \n")
    for item in buckets['LIKELY']:
        line = item['raw']
        if item['source'] == 'Codex': line = convert_codex_row(line)
        f.write(line + "\n")
    f.write("\n")
    
    f.write(f"## 4. HIGH POTENTIAL CANDIDATES ({len(buckets['POTENTIAL'])})\n")
    f.write("*Filtered candidates not yet in Master Verification Lists*\n")
    f.write("| Score | ASIN | Profit | Supplier Title | Amazon Title | Reason |\n")
    f.write("|---|---|---|---|---|---|\n")
    for item in buckets['POTENTIAL']:
        f.write(item['raw'] + "\n")
    f.write("\n")
    
print("Master Report v2 Generated.")
