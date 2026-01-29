import pandas as pd
import re

# Load confirmed entries from my analysis
confirmed_ean = pd.read_csv('confirmed_exact_ean.csv')
confirmed_non_ean = pd.read_csv('confirmed_non_ean.csv')
excluded_ean = pd.read_csv('excluded_exact_ean.csv')

confirmed_ean_asins = set(confirmed_ean['ASIN'].tolist())
confirmed_non_ean_asins = set(confirmed_non_ean['ASIN'].tolist())
all_confirmed_asins = confirmed_ean_asins | confirmed_non_ean_asins

print("="*80)
print("GROUND TRUTH FROM MY ANALYSIS")
print("="*80)
print(f"Confirmed Exact EAN ASINs: {len(confirmed_ean_asins)}")
print(f"Confirmed Non-EAN ASINs: {len(confirmed_non_ean_asins)}")
print(f"TOTAL CONFIRMED ASINs: {len(all_confirmed_asins)}")
print()

# Function to extract ASINs from MD file
def extract_asins_from_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all ASIN patterns (B followed by 9 alphanumerics)
    asins = re.findall(r'\b(B[A-Z0-9]{9})\b', content)
    
    # Also find ASINs in table format (may have extra chars)
    asins2 = re.findall(r'B[0-9A-Z]{9,10}', content)
    
    return set(asins) | set([a[:10] for a in asins2 if len(a) >= 10])

# Function to extract ASINs from specific sections
def extract_section_asins(filepath, section_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the section
    pattern = rf'#{1,3}\s*.*?{section_name}.*?\n(.*?)(?=\n#{1,3}\s|\Z)'
    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
    
    asins = []
    for match in matches:
        found = re.findall(r'\b(B[A-Z0-9]{9})\b', match)
        asins.extend(found)
    
    return set(asins)

# Parse each report
reports = [
    ("Report 2.4", "prompt 2.4 PHASEA_MANUAL_REPORT_20251224 (1).md"),
    ("Report 2.5", "prompt 2.5 PHASEA_MANUAL_REPORT_2512241822.md"),
    ("Report 2.7", "prompt 2.7 PHASEA_MANUAL_REPORT_2512241836.md"),
    ("Report 2.8", "prompt 2.8PHASEA_MANUAL_REPORT_20251224 (2).md"),
]

report_results = {}

for name, filepath in reports:
    try:
        all_asins = extract_asins_from_md(filepath)
        verified_asins = extract_section_asins(filepath, "VERIFIED")
        high_likelihood_asins = extract_section_asins(filepath, "HIGH LIKELIHOOD")
        
        # Count confirmed matches
        confirmed_in_report = all_asins & all_confirmed_asins
        confirmed_verified = verified_asins & all_confirmed_asins
        confirmed_hl = high_likelihood_asins & all_confirmed_asins
        
        # Also check for confirmed EAN matches specifically
        confirmed_ean_in_report = all_asins & confirmed_ean_asins
        confirmed_non_ean_in_report = all_asins & confirmed_non_ean_asins
        
        report_results[name] = {
            'total_asins': len(all_asins),
            'verified_asins': len(verified_asins),
            'high_likelihood_asins': len(high_likelihood_asins),
            'confirmed_total': len(confirmed_in_report),
            'confirmed_ean': len(confirmed_ean_in_report),
            'confirmed_non_ean': len(confirmed_non_ean_in_report),
            'confirmed_in_verified': len(confirmed_verified),
            'confirmed_in_hl': len(confirmed_hl),
            'asins': all_asins,
            'verified': verified_asins,
            'confirmed_set': confirmed_in_report
        }
        
        print(f"\n{name}:")
        print(f"  Total ASINs found in report: {len(all_asins)}")
        print(f"  ASINs in VERIFIED section: {len(verified_asins)}")
        print(f"  ASINs in HIGH LIKELIHOOD section: {len(high_likelihood_asins)}")
        print(f"  ---")
        print(f"  Confirmed ASINs matching my analysis: {len(confirmed_in_report)}")
        print(f"    - Confirmed via Exact EAN: {len(confirmed_ean_in_report)}")
        print(f"    - Confirmed via Title Analysis: {len(confirmed_non_ean_in_report)}")
        
    except Exception as e:
        print(f"Error parsing {name}: {e}")

# Determine winner
print()
print("="*80)
print("WINNER DETERMINATION")
print("="*80)

winner = max(report_results.items(), key=lambda x: x[1]['confirmed_total'])
print(f"\n*** WINNER: {winner[0]} with {winner[1]['confirmed_total']} confirmed matches ***")
print()

# Show scoring
print("SCORECARD:")
print("-"*80)
for name, data in sorted(report_results.items(), key=lambda x: -x[1]['confirmed_total']):
    print(f"{name}: {data['confirmed_total']} confirmed | {data['confirmed_ean']} EAN | {data['confirmed_non_ean']} Title")

# Find what was missed by the winner
winner_asins = winner[1]['asins']
missed_by_winner = all_confirmed_asins - winner_asins

print()
print("="*80)
print(f"CONFIRMED PRODUCTS MISSED BY WINNER ({winner[0]})")
print("="*80)
print(f"Total missed: {len(missed_by_winner)}")

# Check which other reports have these missed items
missed_details = []
for asin in missed_by_winner:
    found_in = []
    for name, data in report_results.items():
        if name != winner[0]:
            if asin in data['asins']:
                found_in.append(name)
    
    # Get details from confirmed csvs
    ean_row = confirmed_ean[confirmed_ean['ASIN'] == asin]
    non_ean_row = confirmed_non_ean[confirmed_non_ean['ASIN'] == asin]
    
    if len(ean_row) > 0:
        row = ean_row.iloc[0]
        match_type = "Exact EAN"
    elif len(non_ean_row) > 0:
        row = non_ean_row.iloc[0]
        match_type = "Title Analysis"
    else:
        continue
    
    missed_details.append({
        'ASIN': asin,
        'SupplierTitle': row.get('SupplierTitle', 'N/A'),
        'MatchType': match_type,
        'NetProfit': row.get('NetProfit', 0),
        'FoundIn': found_in if found_in else ['Not in any report']
    })

print()
for item in sorted(missed_details, key=lambda x: -x['NetProfit']):
    print(f"{item['ASIN']} | {item['MatchType']} | £{item['NetProfit']:.2f}")
    print(f"  Title: {str(item['SupplierTitle'])[:60]}")
    print(f"  Found in: {', '.join(item['FoundIn'])}")
    print()

# Generate the final confirmed list from winner + missed items
print()
print("="*80)
print(f"COMPLETE CONFIRMED LIST (Winner + Missed)")
print("="*80)

# Winner's confirmed entries
winner_confirmed = winner[1]['confirmed_set']
all_final_confirmed = winner_confirmed | missed_by_winner

print(f"Winner's confirmed entries: {len(winner_confirmed)}")
print(f"Additional entries from other sources: {len(missed_by_winner)}")
print(f"TOTAL FINAL CONFIRMED: {len(all_final_confirmed)}")
