#!/usr/bin/env python3
"""
Identify MISSED and INCORRECTLY ADDED products in CODEX report
Cross-references against all 4 AI reports and source Excel
"""

import pandas as pd
import re
import os
from datetime import datetime
from collections import defaultdict

BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan"

# Target report to analyze
TARGET_REPORT = os.path.join(BASE_DIR, "CODEX final", "PHASEA_MANUAL_REPORT_0110052809 - Copy.md")

# Other reports for cross-reference
OTHER_REPORTS = {
    "CODEX_NEW": os.path.join(BASE_DIR, "CODEX NEW", "PHASEA_MANUAL_REPORT_VALIDATED_2601090352.md"),
    "CODEX_MANU": os.path.join(BASE_DIR, "CODEX manu", "PHASEA_MANUAL_REPORT_2601090949.md"),
    "OPUS_MANU": os.path.join(BASE_DIR, "OPUS manu", "PHASEA_MANUAL_REPORT_2601100043_CORRECTED.md"),
}

SOURCE_FILE = os.path.join(BASE_DIR, "part 8 jan.xlsx")


def extract_all_eans_from_report(filepath):
    """Extract ALL EANs from a report, categorized."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all EANs in the content (13-14 digit numbers)
    ean_pattern = r'\b(\d{12,14})\b'
    all_eans = set(re.findall(ean_pattern, content))
    
    # Now categorize by section
    categories = {
        'VERIFIED': set(),
        'HIGHLY_LIKELY': set(),
        'NEEDS_VERIFICATION': set(),
        'AUDITED_OUT': set(),
        'ALL': set()
    }
    
    # Split content by sections and find EANs in each
    sections = [
        (r'## VERIFIED — RECOMMENDED.*?(?=## |$)', 'VERIFIED'),
        (r'## VERIFIED — AUDITED OUT.*?(?=## |$)', 'AUDITED_OUT'),
        (r'## HIGHLY LIKELY — RECOMMENDED.*?(?=## |$)', 'HIGHLY_LIKELY'),
        (r'## HIGHLY LIKELY — AUDITED OUT.*?(?=## |$)', 'AUDITED_OUT'),
        (r'## NEEDS VERIFICATION.*?(?=## |$)', 'NEEDS_VERIFICATION'),
    ]
    
    for pattern, cat_name in sections:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section_content = match.group(0)
            section_eans = set(re.findall(ean_pattern, section_content))
            categories[cat_name].update(section_eans)
            categories['ALL'].update(section_eans)
    
    return categories


def validate_ean_checksum(ean_str):
    """Validate EAN-13 checksum."""
    if not ean_str or len(ean_str) < 8:
        return False
    
    ean_str = ean_str.zfill(13)
    
    if not ean_str.isdigit():
        return False
    
    if len(ean_str) == 13:
        total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(ean_str[:12]))
        check = (10 - (total % 10)) % 10
        return check == int(ean_str[12])
    
    return True


def main():
    print("=" * 80)
    print("MISSED & INCORRECTLY ADDED PRODUCT ANALYSIS")
    print("=" * 80)
    print(f"Target Report: {os.path.basename(TARGET_REPORT)}")
    print("")
    
    # 1. Load source data
    print("[1] Loading source Excel data...")
    source_df = pd.read_excel(SOURCE_FILE)
    
    source_eans = set()
    source_by_ean = {}
    for idx, row in source_df.iterrows():
        ean = str(row['EAN']).replace('.0', '').strip()
        if ean and ean != 'nan' and len(ean) >= 8:
            source_eans.add(ean)
            source_by_ean[ean] = row.to_dict()
    
    print(f"   Source contains {len(source_eans)} unique EANs")
    
    # 2. Extract EANs from target report
    print("\n[2] Parsing TARGET report (CODEX final)...")
    target_data = extract_all_eans_from_report(TARGET_REPORT)
    
    target_verified = target_data['VERIFIED']
    target_highly_likely = target_data['HIGHLY_LIKELY']
    target_needs_verification = target_data['NEEDS_VERIFICATION']
    target_audited_out = target_data['AUDITED_OUT']
    target_all = target_data['ALL']
    
    print(f"   VERIFIED: {len(target_verified)}")
    print(f"   HIGHLY LIKELY: {len(target_highly_likely)}")
    print(f"   NEEDS VERIFICATION: {len(target_needs_verification)}")
    print(f"   AUDITED OUT: {len(target_audited_out)}")
    print(f"   TOTAL UNIQUE: {len(target_all)}")
    
    # 3. Extract EANs from other reports
    print("\n[3] Parsing OTHER reports for cross-reference...")
    other_reports_data = {}
    
    for report_name, report_path in OTHER_REPORTS.items():
        if os.path.exists(report_path):
            data = extract_all_eans_from_report(report_path)
            other_reports_data[report_name] = data
            print(f"   {report_name}:")
            print(f"     - VERIFIED: {len(data['VERIFIED'])}")
            print(f"     - HIGHLY LIKELY: {len(data['HIGHLY_LIKELY'])}")
            print(f"     - TOTAL: {len(data['ALL'])}")
    
    # 4. Find AGREED VERIFIED products across ALL reports
    print("\n[4] Finding products VERIFIED in OTHER reports but MISSING in TARGET...")
    
    # Get union of VERIFIED from all other reports
    other_verified_union = set()
    other_verified_all = {}  # Which reports have this as VERIFIED
    
    for report_name, data in other_reports_data.items():
        for ean in data['VERIFIED']:
            other_verified_union.add(ean)
            if ean not in other_verified_all:
                other_verified_all[ean] = []
            other_verified_all[ean].append(report_name)
    
    # VERIFIED in multiple other reports but NOT in target VERIFIED
    missed_verified = []
    for ean in other_verified_union:
        if ean not in target_verified and ean not in target_highly_likely:
            reports_with = other_verified_all.get(ean, [])
            if len(reports_with) >= 2:  # At least 2 other reports agree
                source_data = source_by_ean.get(ean, {})
                missed_verified.append({
                    'ean': ean,
                    'title': source_data.get('SupplierTitle', 'N/A')[:50],
                    'net_profit': source_data.get('NetProfit', 0),
                    'agreed_by': reports_with,
                    'in_target_as': 'NEEDS_VERIFICATION' if ean in target_needs_verification else 
                                   ('AUDITED_OUT' if ean in target_audited_out else 'NOT_FOUND')
                })
    
    print(f"   Found {len(missed_verified)} VERIFIED products MISSING from target (agreed by 2+ reports)")
    
    # 5. Find HIGHLY LIKELY that are missing
    print("\n[5] Finding HIGHLY LIKELY products in OTHER reports but MISSING in TARGET...")
    
    other_highly_likely_union = set()
    other_hl_all = {}
    
    for report_name, data in other_reports_data.items():
        for ean in data['HIGHLY_LIKELY']:
            other_highly_likely_union.add(ean)
            if ean not in other_hl_all:
                other_hl_all[ean] = []
            other_hl_all[ean].append(report_name)
    
    missed_highly_likely = []
    for ean in other_highly_likely_union:
        if ean not in target_verified and ean not in target_highly_likely:
            reports_with = other_hl_all.get(ean, [])
            if len(reports_with) >= 2:
                source_data = source_by_ean.get(ean, {})
                missed_highly_likely.append({
                    'ean': ean,
                    'title': source_data.get('SupplierTitle', 'N/A')[:50],
                    'net_profit': source_data.get('NetProfit', 0),
                    'agreed_by': reports_with,
                    'in_target_as': 'NEEDS_VERIFICATION' if ean in target_needs_verification else 
                                   ('AUDITED_OUT' if ean in target_audited_out else 'NOT_FOUND')
                })
    
    print(f"   Found {len(missed_highly_likely)} HIGHLY LIKELY products MISSING from target (agreed by 2+ reports)")
    
    # 6. Find INCORRECTLY ADDED products
    print("\n[6] Finding INCORRECTLY ADDED products (in TARGET but NOT in any other report)...")
    
    # Get products that are in target's recommended sections but NOT in any other report
    all_other_recommended = set()
    for data in other_reports_data.values():
        all_other_recommended.update(data['VERIFIED'])
        all_other_recommended.update(data['HIGHLY_LIKELY'])
    
    possibly_incorrect = []
    
    for ean in (target_verified | target_highly_likely):
        if ean not in all_other_recommended:
            # Check if it exists in source
            if ean in source_eans:
                source_data = source_by_ean.get(ean, {})
                # Check EAN validity
                ean_valid = validate_ean_checksum(ean)
                
                possibly_incorrect.append({
                    'ean': ean,
                    'title': source_data.get('SupplierTitle', 'N/A')[:50],
                    'net_profit': source_data.get('NetProfit', 0),
                    'in_target_as': 'VERIFIED' if ean in target_verified else 'HIGHLY_LIKELY',
                    'in_source': True,
                    'ean_valid': ean_valid,
                    'in_other_reports': 'NO'
                })
            else:
                # Not even in source!
                possibly_incorrect.append({
                    'ean': ean,
                    'title': 'NOT IN SOURCE',
                    'net_profit': 0,
                    'in_target_as': 'VERIFIED' if ean in target_verified else 'HIGHLY_LIKELY',
                    'in_source': False,
                    'ean_valid': validate_ean_checksum(ean),
                    'in_other_reports': 'NO'
                })
    
    print(f"   Found {len(possibly_incorrect)} products in TARGET recommended but NOT in any other report")
    
    # 7. Find products with EAN conflicts (different classification across reports)
    print("\n[7] Finding products with CLASSIFICATION CONFLICTS...")
    
    conflicts = []
    all_eans_across_reports = set()
    for data in other_reports_data.values():
        all_eans_across_reports.update(data['ALL'])
    all_eans_across_reports.update(target_all)
    
    for ean in all_eans_across_reports:
        classifications = {}
        
        # Check target
        if ean in target_verified:
            classifications['TARGET'] = 'VERIFIED'
        elif ean in target_highly_likely:
            classifications['TARGET'] = 'HIGHLY_LIKELY'
        elif ean in target_audited_out:
            classifications['TARGET'] = 'AUDITED_OUT'
        elif ean in target_needs_verification:
            classifications['TARGET'] = 'NEEDS_VERIFICATION'
        
        # Check other reports
        for rname, data in other_reports_data.items():
            if ean in data['VERIFIED']:
                classifications[rname] = 'VERIFIED'
            elif ean in data['HIGHLY_LIKELY']:
                classifications[rname] = 'HIGHLY_LIKELY'
            elif ean in data['AUDITED_OUT']:
                classifications[rname] = 'AUDITED_OUT'
            elif ean in data['NEEDS_VERIFICATION']:
                classifications[rname] = 'NEEDS_VERIFICATION'
        
        if len(classifications) >= 2:
            unique_cats = set(classifications.values())
            # Only flag if there's a disagreement between VERIFIED/HIGHLY_LIKELY vs AUDITED_OUT/NOT_IN
            recommended_cats = {'VERIFIED', 'HIGHLY_LIKELY'}
            excluded_cats = {'AUDITED_OUT', 'NEEDS_VERIFICATION'}
            
            cats_found = unique_cats
            if cats_found & recommended_cats and cats_found & excluded_cats:
                source_data = source_by_ean.get(ean, {})
                conflicts.append({
                    'ean': ean,
                    'title': source_data.get('SupplierTitle', 'N/A')[:45],
                    'classifications': classifications
                })
    
    print(f"   Found {len(conflicts)} products with MAJOR classification conflicts")
    
    # 8. Generate Output Report
    print("\n" + "=" * 80)
    print("GENERATING OUTPUT REPORT")
    print("=" * 80)
    
    output = []
    output.append("# MISSED & INCORRECTLY ADDED PRODUCTS ANALYSIS")
    output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"**Target Report:** `{os.path.basename(TARGET_REPORT)}`")
    output.append("")
    output.append("---")
    output.append("")
    
    # Summary
    output.append("## EXECUTIVE SUMMARY")
    output.append("")
    output.append("| Issue Type | Count |")
    output.append("|------------|-------|")
    output.append(f"| VERIFIED products MISSED (agreed by 2+ other reports) | **{len(missed_verified)}** |")
    output.append(f"| HIGHLY LIKELY products MISSED (agreed by 2+ other reports) | **{len(missed_highly_likely)}** |")
    output.append(f"| Products in TARGET but NOT in any other report | **{len(possibly_incorrect)}** |")
    output.append(f"| Products with major classification conflicts | **{len(conflicts)}** |")
    output.append("")
    
    # MISSED VERIFIED
    output.append("---")
    output.append("")
    output.append(f"## 1. MISSED VERIFIED PRODUCTS ({len(missed_verified)})")
    output.append("")
    output.append("These products are classified as VERIFIED in 2+ other reports but are NOT in the target's VERIFIED or HIGHLY LIKELY sections:")
    output.append("")
    
    if missed_verified:
        output.append("| EAN | Supplier Title | Net Profit | Agreed By | In Target As |")
        output.append("|-----|----------------|------------|-----------|--------------|")
        for m in missed_verified:
            agreed = ', '.join(m['agreed_by'])
            profit = f"£{float(m['net_profit']):.2f}" if m['net_profit'] else 'N/A'
            output.append(f"| {m['ean']} | {m['title']} | {profit} | {agreed} | {m['in_target_as']} |")
    else:
        output.append("✅ No VERIFIED products missed")
    output.append("")
    
    # MISSED HIGHLY LIKELY
    output.append("---")
    output.append("")
    output.append(f"## 2. MISSED HIGHLY LIKELY PRODUCTS ({len(missed_highly_likely)})")
    output.append("")
    output.append("These products are classified as HIGHLY LIKELY in 2+ other reports but are NOT in the target's recommended sections:")
    output.append("")
    
    if missed_highly_likely:
        output.append("| EAN | Supplier Title | Net Profit | Agreed By | In Target As |")
        output.append("|-----|----------------|------------|-----------|--------------|")
        for m in missed_highly_likely[:50]:
            agreed = ', '.join(m['agreed_by'])
            profit = f"£{float(m['net_profit']):.2f}" if m['net_profit'] else 'N/A'
            output.append(f"| {m['ean']} | {m['title']} | {profit} | {agreed} | {m['in_target_as']} |")
        if len(missed_highly_likely) > 50:
            output.append(f"\n*...and {len(missed_highly_likely) - 50} more*")
    else:
        output.append("✅ No HIGHLY LIKELY products missed")
    output.append("")
    
    # POSSIBLY INCORRECTLY ADDED
    output.append("---")
    output.append("")
    output.append(f"## 3. POSSIBLY INCORRECTLY ADDED PRODUCTS ({len(possibly_incorrect)})")
    output.append("")
    output.append("These products are in target's VERIFIED/HIGHLY LIKELY but do NOT appear in ANY other report's recommended sections:")
    output.append("")
    
    if possibly_incorrect:
        output.append("| EAN | Supplier Title | In Target As | In Source? | EAN Valid? |")
        output.append("|-----|----------------|--------------|------------|------------|")
        for p in possibly_incorrect[:50]:
            in_source = '✅' if p['in_source'] else '❌'
            ean_valid = '✅' if p['ean_valid'] else '❌'
            output.append(f"| {p['ean']} | {p['title']} | {p['in_target_as']} | {in_source} | {ean_valid} |")
        if len(possibly_incorrect) > 50:
            output.append(f"\n*...and {len(possibly_incorrect) - 50} more*")
    else:
        output.append("✅ No possibly incorrect additions found")
    output.append("")
    
    # CLASSIFICATION CONFLICTS
    output.append("---")
    output.append("")
    output.append(f"## 4. MAJOR CLASSIFICATION CONFLICTS ({len(conflicts)})")
    output.append("")
    output.append("These products have conflicting classifications across reports (some say VERIFIED/HIGHLY LIKELY, others say AUDITED_OUT):")
    output.append("")
    
    if conflicts:
        output.append("| EAN | Title | TARGET | CODEX_NEW | CODEX_MANU | OPUS_MANU |")
        output.append("|-----|-------|--------|-----------|------------|-----------|")
        for c in conflicts[:40]:
            target_cat = c['classifications'].get('TARGET', '-')
            codex_new = c['classifications'].get('CODEX_NEW', '-')
            codex_manu = c['classifications'].get('CODEX_MANU', '-')
            opus_manu = c['classifications'].get('OPUS_MANU', '-')
            output.append(f"| {c['ean']} | {c['title']} | {target_cat} | {codex_new} | {codex_manu} | {opus_manu} |")
        if len(conflicts) > 40:
            output.append(f"\n*...and {len(conflicts) - 40} more*")
    else:
        output.append("✅ No major classification conflicts found")
    output.append("")
    
    # Conclusions
    output.append("---")
    output.append("")
    output.append("## CONCLUSIONS")
    output.append("")
    output.append(f"### Products MISSED in Target Report: {len(missed_verified) + len(missed_highly_likely)}")
    if missed_verified:
        output.append(f"- **{len(missed_verified)} VERIFIED products** that 2+ other reports agree on are NOT in target's recommended sections")
    if missed_highly_likely:
        output.append(f"- **{len(missed_highly_likely)} HIGHLY LIKELY products** that 2+ other reports agree on are NOT in target's recommended sections")
    output.append("")
    
    output.append(f"### Products POSSIBLY INCORRECTLY ADDED: {len(possibly_incorrect)}")
    not_in_source = len([p for p in possibly_incorrect if not p['in_source']])
    if not_in_source > 0:
        output.append(f"- **{not_in_source} products** are NOT even in the source Excel file!")
    output.append("")
    
    output.append("---")
    output.append(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Save report
    output_path = os.path.join(BASE_DIR, f"MISSED_AND_INCORRECT_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"\n   Report saved to: {output_path}")
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"   MISSED VERIFIED: {len(missed_verified)}")
    print(f"   MISSED HIGHLY LIKELY: {len(missed_highly_likely)}")
    print(f"   POSSIBLY INCORRECT: {len(possibly_incorrect)}")
    print(f"   CLASSIFICATION CONFLICTS: {len(conflicts)}")
    print("=" * 80)
    
    if missed_verified:
        print("\n   TOP MISSED VERIFIED:")
        for m in missed_verified[:5]:
            print(f"   - {m['ean']}: {m['title']} (agreed: {', '.join(m['agreed_by'])})")
    
    if missed_highly_likely:
        print("\n   TOP MISSED HIGHLY LIKELY:")
        for m in missed_highly_likely[:5]:
            print(f"   - {m['ean']}: {m['title']} (agreed: {', '.join(m['agreed_by'])})")
    
    if possibly_incorrect:
        print("\n   TOP POSSIBLY INCORRECT:")
        for p in possibly_incorrect[:5]:
            print(f"   - {p['ean']}: {p['title']} ({p['in_target_as']}, in source: {p['in_source']})")


if __name__ == "__main__":
    main()
