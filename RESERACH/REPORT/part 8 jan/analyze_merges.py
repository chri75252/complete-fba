import re

# Parse the comparison result text file I generated earlier (or I could re-parse the reports, but I'll use the result if possible. 
# Actually, re-parsing is safer to get the full list of titles/data).

# Let's re-parse both reports to get the full dictionaries again.
def parse_report(filepath):
    data = {}
    current_status = None
    
    status_map = {
        'VERIFIED — RECOMMENDED': 'VERIFIED_OK',
        'VERIFIED - RECOMMENDED': 'VERIFIED_OK',
        'VERIFIED — AUDITED OUT': 'VERIFIED_OUT',
        'VERIFIED - AUDITED OUT': 'VERIFIED_OUT',
        'VERIFIED - AUDITED OUT / EXCLUDED': 'VERIFIED_OUT',
        'HIGHLY LIKELY — PENDING VERIFICATION': 'LIKELY_OK',
        'HIGHLY LIKELY - RECOMMENDED': 'LIKELY_OK',
        'HIGHLY LIKELY - AUDITED OUT / EXCLUDED': 'LIKELY_OUT',
        'NEEDS VERIFICATION': 'NEEDS_VERIF',
        'RECOMMENDED (NEW)': 'RECOMMENDED_NEW'
    }

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('##'):
            upper = line.upper()
            for k, v in status_map.items():
                if k in upper:
                    current_status = v
                    break
        
        if line.startswith('|') and 'ASIN' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 4:
                # Find ASIN
                asin = None
                title = "Unknown"
                # Simple heuristic for ASIN column (usually index 4 or 3)
                for p in parts:
                    if (len(p) == 10 and p.isalnum()) or p.startswith('B0'):
                        asin = p
                        break
                
                if asin:
                    if len(parts) > 2: title = parts[2]
                    # Capture full line for reconstruction if needed, or just data
                    # We store the cleaned Status
                    data[asin] = {'status': current_status, 'title': title, 'raw_line': line}

    return data

my_report = parse_report('FINAL_COMPREHENSIVE_REPORT_20260113.md')
codex_report = parse_report(r'CODEX final\PHASEA_MANUAL_REPORT_FINAL_COMPLETE_20260113_083500.md')

# LOGIC FOR MERGE
# We want the UNION of best statuses.
# Hierarchy: VERIFIED_OK > LIKELY_OK > NEEDS_VERIF
# BUT: If either says AUDITED_OUT (VERIFIED_OUT/LIKELY_OUT), that trumps OK (safety first).
# Exception: If I verified it and they audited it, I should check why. 
# (In previous step I decided to trust Codex Audit for safety).

final_list = {}
all_asins = set(my_report.keys()) | set(codex_report.keys())

move_to_audited = []
add_to_likely = []
add_to_verified = []

for asin in all_asins:
    my_stat = my_report.get(asin, {}).get('status', 'MISSING')
    cod_stat = codex_report.get(asin, {}).get('status', 'MISSING')
    
    # 1. Resolve Status
    final_status = 'NEEDS_VERIF'
    source_line = my_report.get(asin, {}).get('raw_line') or codex_report.get(asin, {}).get('raw_line')
    
    # Check for Audited Out in EITHER
    if 'OUT' in my_stat or 'OUT' in cod_stat:
        final_status = 'AUDITED_OUT'
        if my_stat == 'VERIFIED_OK' and 'OUT' in cod_stat:
            move_to_audited.append(asin)
        elif my_stat == 'LIKELY_OK' and 'OUT' in cod_stat:
            move_to_audited.append(asin)
            
    # Check for Verified OK
    elif 'VERIFIED_OK' in my_stat or 'VERIFIED_OK' in cod_stat:
        final_status = 'VERIFIED_OK'
        # If I missed it, log it
        if my_stat != 'VERIFIED_OK' and cod_stat == 'VERIFIED_OK':
            add_to_verified.append(asin)
            
    # Check for Likely OK
    elif 'LIKELY_OK' in my_stat or 'LIKELY_OK' in cod_stat:
        final_status = 'LIKELY_OK'
        if my_stat != 'LIKELY_OK' and cod_stat == 'LIKELY_OK':
            add_to_likely.append(asin)
            
    elif 'RECOMMENDED_NEW' in my_stat:
        final_status = 'LIKELY_OK' # Map my new findings to Likely
        
    final_list[asin] = {
        'status': final_status, 
        'title': my_report.get(asin, {}).get('title') or codex_report.get(asin, {}).get('title'),
        'line': source_line
    }

print(f"MOVED_TO_AUDITED: {len(move_to_audited)}")
for a in move_to_audited: print(f" - {a}: {final_list[a]['title']}")

print(f"ADDED_TO_VERIFIED: {len(add_to_verified)}")
for a in add_to_verified: print(f" - {a}: {final_list[a]['title']}")

print(f"ADDED_TO_LIKELY: {len(add_to_likely)}")
for a in add_to_likely[:20]: print(f" - {a}: {final_list[a]['title']}")

# Save Conflict/Merge Data for report generation
import json
with open('merge_decisions.json', 'w') as f:
    json.dump({'audited': move_to_audited, 'verified': add_to_verified, 'likely': add_to_likely}, f)
