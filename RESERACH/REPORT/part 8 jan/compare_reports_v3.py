import re
import os

def parse_report(filepath):
    """
    Parses the report to extract ASINs and their status.
    Returns a dict: {ASIN: {'status': STATUS, 'title': TITLE, 'line': LINE_NUM}}
    """
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

    for i, line in enumerate(lines):
        line = line.strip()
        
        # Detect Section Headers
        # Flexible matching for ## Headers
        if line.startswith('##'):
            upper_line = line.upper()
            found_status = None
            for key, val in status_map.items():
                if key in upper_line:
                    found_status = val
                    break
            if found_status:
                current_status = found_status
                continue
        
        # Parse Table Rows
        if line.startswith('|') and 'ASIN' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 4:
                # Try to find ASIN. Usually in column 4 or similar.
                # Regex for ASIN: B0... or 10 digits
                asin_candidate = None
                title_candidate = "Unknown Title"
                
                # Scan parts for ASIN-like string
                for part in parts:
                    if (len(part) == 10 and part.isalnum()) or (part.startswith('B0') and len(part) == 10):
                        asin_candidate = part
                        break
                
                if asin_candidate:
                    # Capture title (usually 2nd or 3rd column)
                    if len(parts) > 2:
                        title_candidate = parts[2] 
                        
                    if asin_candidate not in data:
                        data[asin_candidate] = {
                            'status': current_status,
                            'title': title_candidate,
                            'line': i + 1
                        }

    return data

my_report_path = 'FINAL_COMPREHENSIVE_REPORT_20260113.md'
target_report_path = r'CODEX final\PHASEA_MANUAL_REPORT_FINAL_COMPLETE_20260113_083500.md'

print(f"Parsing My Report: {my_report_path}")
my_data = parse_report(my_report_path)
print(f"Found {len(my_data)} items in My Report.")

print(f"Parsing Target Report: {target_report_path}")
target_data = parse_report(target_report_path)
print(f"Found {len(target_data)} items in Target Report.")

# Comparison Logic
disagreements = []
missed_by_me = []
missed_by_target = []

all_asins = set(my_data.keys()) | set(target_data.keys())

for asin in all_asins:
    my_status = my_data.get(asin, {}).get('status', 'MISSING')
    target_status = target_data.get(asin, {}).get('status', 'MISSING')
    
    title = my_data.get(asin, {}).get('title') or target_data.get(asin, {}).get('title')
    
    if my_status == 'MISSING':
        missed_by_me.append((asin, title, target_status))
    elif target_status == 'MISSING':
        missed_by_target.append((asin, title, my_status))
    elif my_status != target_status:
        # Ignore loose mappings like RECOMMENDED_NEW vs LIKELY
        if my_status == 'RECOMMENDED_NEW' and target_status in ['LIKELY_OK', 'NEEDS_VERIF']:
            continue
        disagreements.append((asin, title, my_status, target_status))

print("\n=== DISAGREEMENTS IN STATUS ===")
print(f"Total: {len(disagreements)}")
for item in disagreements[:20]:
    print(f"ASIN: {item[0]} | Title: {item[1][:30]}... | Me: {item[2]} | Target: {item[3]}")

print("\n=== MISSED BY ME (In Target but not Mine) ===")
print(f"Total: {len(missed_by_me)}")
for item in missed_by_me[:20]:
    print(f"ASIN: {item[0]} | Title: {item[1][:30]}... | Target Status: {item[2]}")

print("\n=== MISSED BY TARGET (In Mine but not Target) ===")
print(f"Total: {len(missed_by_target)}")
for item in missed_by_target[:20]:
    print(f"ASIN: {item[0]} | Title: {item[1][:30]}... | My Status: {item[2]}")

# Summary Stats
print("\n=== SUMMARY STATISTICS ===")
print(f"My Total Verified (OK): {sum(1 for x in my_data.values() if x['status'] == 'VERIFIED_OK')}")
print(f"Target Total Verified (OK): {sum(1 for x in target_data.values() if x['status'] == 'VERIFIED_OK')}")
print(f"My Total Audited Out: {sum(1 for x in my_data.values() if x['status'] == 'VERIFIED_OUT')}")
print(f"Target Total Audited Out: {sum(1 for x in target_data.values() if x['status'] == 'VERIFIED_OUT')}")

