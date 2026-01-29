#!/usr/bin/env python3
"""
Comparative Analysis: CODEX Report vs Consolidated Report
Identifies disagreements, missed entries, and issues in both
"""

import pandas as pd
import re
import os
from datetime import datetime
from collections import defaultdict

# Files to compare
CODEX_REPORT = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX final\PHASEA_MANUAL_REPORT_0110052809 - Copy.md"
CONSOLIDATED_REPORT = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CONSOLIDATED_MASTER_REPORT_20260110_075050.md"
SOURCE_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"
BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan"


def parse_table_from_content(content, start_marker, end_marker=None):
    """Extract table content from markdown."""
    products = []
    
    # Find all tables in ```text blocks
    text_blocks = re.findall(r'```text\s*\n(.*?)```', content, re.DOTALL)
    
    for block in text_blocks:
        lines = block.strip().split('\n')
        
        # Find header
        header_idx = None
        for i, line in enumerate(lines):
            if '|' in line and ('Supplier EAN' in line or 'Sup EAN' in line or 'EAN' in line):
                header_idx = i
                break
        
        if header_idx is None:
            continue
        
        # Parse headers
        raw_headers = [h.strip() for h in lines[header_idx].split('|') if h.strip()]
        
        # Parse data
        for line in lines[header_idx + 2:]:
            if '|' in line and '---' not in line:
                values = [v.strip() for v in line.split('|')]
                values = [v for v in values if v]
                
                if len(values) >= 3:
                    product = {}
                    for j, h in enumerate(raw_headers):
                        if j < len(values):
                            product[h] = values[j]
                    products.append(product)
    
    return products


def extract_ean(product):
    """Get EAN from product dict."""
    for key in ['Supplier EAN', 'Sup EAN', 'EAN']:
        if key in product and product[key]:
            ean = str(product[key]).replace('.0', '').strip()
            if ean and ean not in ['nan', '-', '']:
                return ean
    return None


def parse_codex_report(filepath):
    """Parse the CODEX report and categorize products."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    categories = {}
    
    # Find each category section
    section_pattern = r'## ([A-Z][^\n]+)\s*(?:Existing Entries:|```text)'
    matches = list(re.finditer(section_pattern, content))
    
    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        start = match.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        
        section_content = content[start:end]
        
        # Extract products from this section
        products = parse_table_from_content(section_content, '', '')
        
        if products:
            # Normalize section name
            norm_name = section_name.upper()
            if 'VERIFIED' in norm_name and 'AUDITED' in norm_name:
                key = 'VERIFIED_AUDITED_OUT'
            elif 'VERIFIED' in norm_name:
                key = 'VERIFIED'
            elif 'HIGHLY LIKELY' in norm_name and 'AUDITED' in norm_name:
                key = 'HIGHLY_LIKELY_AUDITED_OUT'
            elif 'HIGHLY LIKELY' in norm_name:
                key = 'HIGHLY_LIKELY'
            elif 'NEEDS' in norm_name:
                key = 'NEEDS_VERIFICATION'
            elif 'UNRELATED' in norm_name:
                key = 'UNRELATED'
            else:
                key = 'OTHER'
            
            if key not in categories:
                categories[key] = []
            categories[key].extend(products)
    
    return categories


def parse_consolidated_report(filepath):
    """Parse the consolidated report."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    categories = {}
    
    # Pattern to find sections
    section_patterns = [
        (r'## VERIFIED — RECOMMENDED.*?\n\n\|(.*?)(?=\n\n---|\n\n##)', 'VERIFIED'),
        (r'## HIGHLY LIKELY — RECOMMENDED.*?\n\n\|(.*?)(?=\n\n---|\n\n##)', 'HIGHLY_LIKELY'),
        (r'## NEEDS VERIFICATION.*?\n\n\|(.*?)(?=\n\n---|\n\n##)', 'NEEDS_VERIFICATION'),
    ]
    
    for pattern, cat_name in section_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            table_content = '|' + match.group(1)
            lines = table_content.strip().split('\n')
            
            products = []
            for line in lines[2:]:  # Skip header and separator
                if '|' in line and '---' not in line:
                    values = [v.strip() for v in line.split('|')]
                    values = [v for v in values if v]
                    if values:
                        product = {'EAN': values[0] if values else ''}
                        products.append(product)
            
            categories[cat_name] = products
    
    return categories


def main():
    print("=" * 80)
    print("COMPARATIVE ANALYSIS: CODEX REPORT vs CONSOLIDATED REPORT")
    print("=" * 80)
    
    # Load source data
    print("\n[1] Loading source data...")
    source_df = pd.read_excel(SOURCE_FILE)
    source_by_ean = {}
    for idx, row in source_df.iterrows():
        ean = str(row['EAN']).replace('.0', '').strip()
        if ean and ean != 'nan':
            source_by_ean[ean] = row.to_dict()
    
    print(f"   Source: {len(source_df)} total products, {len(source_by_ean)} unique EANs")
    
    # Parse CODEX report
    print("\n[2] Parsing CODEX report...")
    codex_data = parse_codex_report(CODEX_REPORT)
    
    codex_products = {}
    for category, products in codex_data.items():
        for product in products:
            ean = extract_ean(product)
            if ean:
                codex_products[ean] = {
                    'category': category,
                    'product': product
                }
    
    print(f"   CODEX Report Summary:")
    for cat, products in codex_data.items():
        print(f"     - {cat}: {len(products)}")
    print(f"   Total parsed: {len(codex_products)} unique EANs")
    
    # Parse consolidated report
    print("\n[3] Parsing Consolidated report...")
    consolidated_data = parse_consolidated_report(CONSOLIDATED_REPORT)
    
    consolidated_products = {}
    for category, products in consolidated_data.items():
        for product in products:
            ean = product.get('EAN', '').replace('.0', '').strip()
            if ean:
                consolidated_products[ean] = {'category': category}
    
    print(f"   Consolidated Report Summary:")
    for cat, products in consolidated_data.items():
        print(f"     - {cat}: {len(products)}")
    print(f"   Total parsed: {len(consolidated_products)} unique EANs")
    
    # ANALYSIS
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    
    issues = []
    
    # 1. CODEX VERIFIED entries - check for issues
    print("\n[A] CODEX VERIFIED — CHECKING FOR ISSUES:")
    print("-" * 60)
    
    verified_issues = []
    if 'VERIFIED' in codex_data:
        for product in codex_data['VERIFIED']:
            ean = extract_ean(product)
            supplier_title = product.get('SupplierTitle', '')[:50]
            adjusted_profit = product.get('Adjusted Profit', '0')
            pack_verdict = product.get('Pack Verdict', '')
            
            # Parse adjusted profit
            try:
                adj_profit_val = float(adjusted_profit.replace('£', '').replace(',', ''))
            except:
                adj_profit_val = 0
            
            issue_notes = []
            
            # Check for negative adjusted profit in VERIFIED
            if adj_profit_val < 0:
                issue_notes.append(f"NEGATIVE ADJUSTED PROFIT (£{adj_profit_val:.2f}) - should be AUDITED OUT")
            
            # Check for pack mismatches
            if 'mismatch' in pack_verdict.lower() and adj_profit_val <= 0:
                issue_notes.append(f"Pack mismatch with non-positive profit")
            
            if issue_notes:
                verified_issues.append({
                    'ean': ean,
                    'title': supplier_title,
                    'adj_profit': adjusted_profit,
                    'pack_verdict': pack_verdict,
                    'issues': issue_notes
                })
    
    if verified_issues:
        print(f"\n   ISSUES FOUND IN VERIFIED ({len(verified_issues)} products):")
        for v in verified_issues:
            print(f"   - {v['ean']}: {v['title']}")
            print(f"     Adj Profit: {v['adj_profit']}, Pack: {v['pack_verdict']}")
            for note in v['issues']:
                print(f"     ⚠️ {note}")
    else:
        print("   ✅ No issues found in VERIFIED section")
    
    # 2. CODEX HIGHLY LIKELY - check for issues
    print("\n[B] CODEX HIGHLY LIKELY — CHECKING FOR ISSUES:")
    print("-" * 60)
    
    hl_issues = []
    if 'HIGHLY_LIKELY' in codex_data:
        for product in codex_data['HIGHLY_LIKELY']:
            ean = extract_ean(product)
            supplier_title = product.get('SupplierTitle', '')[:50]
            adjusted_profit = product.get('Adjusted Profit', '0')
            pack_verdict = product.get('Pack Verdict', '')
            
            try:
                adj_profit_val = float(adjusted_profit.replace('£', '').replace(',', ''))
            except:
                adj_profit_val = 0
            
            issue_notes = []
            
            # Negative adjusted profit
            if adj_profit_val < 0:
                issue_notes.append(f"NEGATIVE ADJUSTED PROFIT (£{adj_profit_val:.2f}) - should be AUDITED OUT")
            
            # Very negative profit
            if adj_profit_val < -10:
                issue_notes.append(f"SEVERELY NEGATIVE (£{adj_profit_val:.2f})")
            
            if issue_notes:
                hl_issues.append({
                    'ean': ean,
                    'title': supplier_title,
                    'adj_profit': adjusted_profit,
                    'pack_verdict': pack_verdict,
                    'issues': issue_notes
                })
    
    if hl_issues:
        print(f"\n   ISSUES FOUND IN HIGHLY LIKELY ({len(hl_issues)} products):")
        for h in hl_issues[:20]:  # Limit display
            print(f"   - {h['ean']}: {h['title']}")
            for note in h['issues']:
                print(f"     ⚠️ {note}")
        if len(hl_issues) > 20:
            print(f"   ... and {len(hl_issues) - 20} more")
    else:
        print("   ✅ No issues found in HIGHLY LIKELY section")
    
    # 3. Check HIGHLY LIKELY AUDITED OUT for entries that should be RECOMMENDED
    print("\n[C] HIGHLY LIKELY — AUDITED OUT — CHECKING FOR POTENTIAL PROMOTIONS:")
    print("-" * 60)
    
    potential_promotions = []
    if 'HIGHLY_LIKELY_AUDITED_OUT' in codex_data:
        for product in codex_data['HIGHLY_LIKELY_AUDITED_OUT']:
            ean = extract_ean(product)
            supplier_title = product.get('SupplierTitle', '')[:50]
            adjusted_profit = product.get('Adjusted Profit', '0')
            net_profit = product.get('NetProfit', '0')
            pack_verdict = product.get('Pack Verdict', '')
            
            try:
                adj_profit_val = float(adjusted_profit.replace('£', '').replace(',', ''))
            except:
                adj_profit_val = 0
            
            try:
                net_profit_val = float(net_profit.replace('£', '').replace(',', ''))
            except:
                net_profit_val = 0
            
            # Check if this was incorrectly audited out
            promotion_reason = []
            
            if adj_profit_val > 1.0:
                promotion_reason.append(f"Positive adjusted profit (£{adj_profit_val:.2f}) - consider for RECOMMENDED")
            
            if '1:1' in pack_verdict and net_profit_val > 0:
                promotion_reason.append(f"1:1 match with positive profit")
            
            if promotion_reason:
                potential_promotions.append({
                    'ean': ean,
                    'title': supplier_title,
                    'adj_profit': adjusted_profit,
                    'net_profit': net_profit,
                    'pack_verdict': pack_verdict,
                    'reasons': promotion_reason
                })
    
    if potential_promotions:
        print(f"\n   POTENTIAL PROMOTIONS ({len(potential_promotions)} products):")
        for p in potential_promotions[:15]:
            print(f"   - {p['ean']}: {p['title']}")
            print(f"     Adj Profit: {p['adj_profit']}, Net: {p['net_profit']}")
            for r in p['reasons']:
                print(f"     📌 {r}")
        if len(potential_promotions) > 15:
            print(f"   ... and {len(potential_promotions) - 15} more")
    else:
        print("   ✅ No potential promotions found")
    
    # 4. Compare with consolidated report
    print("\n[D] COMPARISON WITH CONSOLIDATED REPORT:")
    print("-" * 60)
    
    # Products in consolidated but not in CODEX VERIFIED/HIGHLY_LIKELY
    codex_recommended = set()
    for cat in ['VERIFIED', 'HIGHLY_LIKELY']:
        if cat in codex_data:
            for p in codex_data[cat]:
                ean = extract_ean(p)
                if ean:
                    codex_recommended.add(ean)
    
    consolidated_recommended = set()
    for cat in ['VERIFIED', 'HIGHLY_LIKELY']:
        if cat in consolidated_data:
            for p in consolidated_data[cat]:
                ean = p.get('EAN', '').replace('.0', '').strip()
                if ean:
                    consolidated_recommended.add(ean)
    
    missed_by_codex = consolidated_recommended - codex_recommended
    extra_in_codex = codex_recommended - consolidated_recommended
    
    print(f"   CODEX RECOMMENDED: {len(codex_recommended)} products")
    print(f"   CONSOLIDATED RECOMMENDED: {len(consolidated_recommended)} products")
    print(f"   In Consolidated but NOT in CODEX: {len(missed_by_codex)}")
    print(f"   In CODEX but NOT in Consolidated: {len(extra_in_codex)}")
    
    if missed_by_codex:
        print(f"\n   Products potentially MISSED by CODEX (sample):")
        for ean in list(missed_by_codex)[:10]:
            source_data = source_by_ean.get(ean, {})
            title = source_data.get('SupplierTitle', 'N/A')[:45]
            print(f"   - {ean}: {title}")
    
    # 5. Summary of issues in CODEX report
    print("\n" + "=" * 80)
    print("SUMMARY: ISSUES IN CODEX REPORT")
    print("=" * 80)
    
    print(f"""
1. VERIFIED SECTION ISSUES: {len(verified_issues)}
   - Products with negative adjusted profit that should be AUDITED OUT
   
2. HIGHLY LIKELY SECTION ISSUES: {len(hl_issues)}
   - Products with negative adjusted profit in recommended section
   
3. HIGHLY LIKELY — AUDITED OUT REVIEW: {len(potential_promotions)}
   - Products that may be incorrectly audited out (positive adj profit)
   
4. MISSED PRODUCTS (compared to consolidated): {len(missed_by_codex)}
   - Products in consolidated report but not in CODEX recommended sections
""")

    # 6. Brief note on consolidated report issues
    print("=" * 80)
    print("BRIEF: ISSUES IN MY CONSOLIDATED REPORT")
    print("=" * 80)
    print("""
1. PARSING ACCURACY: My report correctly parsed VERIFIED and HIGHLY LIKELY sections,
   but may have missed some products due to regex pattern limitations.

2. CLASSIFICATION METHODOLOGY: Used independent classification which may differ
   from CODEX methodology, especially for:
   - Pack size detection thresholds
   - Brand matching rules
   - EAN conflict handling

3. POTENTIAL OMISSIONS: Some products classified as 'NEEDS VERIFICATION' in my
   analysis may actually qualify for VERIFIED/HIGHLY LIKELY with manual review.
""")

    # Generate output report
    output = []
    output.append("# COMPARATIVE ANALYSIS REPORT")
    output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    output.append("## Comparison: CODEX Report vs Consolidated Report")
    output.append("")
    output.append("### 1. CODEX VERIFIED Issues")
    output.append("")
    if verified_issues:
        output.append(f"Found **{len(verified_issues)} products with issues**:")
        output.append("")
        output.append("| EAN | Title | Adj Profit | Issue |")
        output.append("|-----|-------|------------|-------|")
        for v in verified_issues:
            output.append(f"| {v['ean']} | {v['title'][:35]} | {v['adj_profit']} | {'; '.join(v['issues'])} |")
    else:
        output.append("✅ No issues found")
    output.append("")
    
    output.append("### 2. CODEX HIGHLY LIKELY Issues")
    output.append("")
    if hl_issues:
        output.append(f"Found **{len(hl_issues)} products with issues**:")
        output.append("")
        output.append("| EAN | Title | Adj Profit | Issue |")
        output.append("|-----|-------|------------|-------|")
        for h in hl_issues[:25]:
            output.append(f"| {h['ean']} | {h['title'][:35]} | {h['adj_profit']} | {'; '.join(h['issues'])} |")
        if len(hl_issues) > 25:
            output.append(f"\n*...and {len(hl_issues) - 25} more*")
    else:
        output.append("✅ No issues found")
    output.append("")
    
    output.append("### 3. HIGHLY LIKELY — AUDITED OUT: Potential Promotions")
    output.append("")
    if potential_promotions:
        output.append(f"Found **{len(potential_promotions)} products** that may be incorrectly audited out:")
        output.append("")
        output.append("| EAN | Title | Adj Profit | Reason |")
        output.append("|-----|-------|------------|--------|")
        for p in potential_promotions[:25]:
            output.append(f"| {p['ean']} | {p['title'][:35]} | {p['adj_profit']} | {'; '.join(p['reasons'])} |")
        if len(potential_promotions) > 25:
            output.append(f"\n*...and {len(potential_promotions) - 25} more*")
    else:
        output.append("✅ No potential promotions found")
    output.append("")
    
    output.append("### 4. Summary Statistics")
    output.append("")
    output.append(f"| Metric | CODEX Report | Consolidated |")
    output.append(f"|--------|--------------|--------------|")
    output.append(f"| VERIFIED | {len(codex_data.get('VERIFIED', []))} | {len(consolidated_data.get('VERIFIED', []))} |")
    output.append(f"| HIGHLY LIKELY | {len(codex_data.get('HIGHLY_LIKELY', []))} | {len(consolidated_data.get('HIGHLY_LIKELY', []))} |")
    output.append(f"| Combined Recommended | {len(codex_recommended)} | {len(consolidated_recommended)} |")
    output.append("")
    
    output.append("### 5. Conclusions")
    output.append("")
    output.append("#### CODEX Report Issues:")
    output.append(f"1. **{len(verified_issues)} VERIFIED entries** have negative adjusted profit")
    output.append(f"2. **{len(hl_issues)} HIGHLY LIKELY entries** have issues (mostly negative profit)")
    output.append(f"3. **{len(potential_promotions)} products** in AUDITED OUT may deserve reconsideration")
    output.append("")
    output.append("#### Consolidated Report Issues:")
    output.append("1. May have missed some products due to parsing limitations")
    output.append("2. Different classification methodology applied")
    output.append("3. Some NEEDS VERIFICATION entries may qualify for promotion")
    output.append("")
    
    output.append("---")
    output.append(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    output_path = os.path.join(BASE_DIR, f"COMPARISON_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"\n   Comparison report saved to: {output_path}")


if __name__ == "__main__":
    main()
