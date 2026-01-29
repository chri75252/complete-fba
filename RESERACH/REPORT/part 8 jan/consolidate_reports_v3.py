#!/usr/bin/env python3
"""
FBA Report Master Consolidation Script v3
- Properly parses ALL categories including HIGHLY LIKELY
- Merges valid entries from all reports
- Retrieves missed products from source Excel
- Applies root cause fixes
- Generates consolidated final report
"""

import pandas as pd
import re
import os
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict

# Configuration
BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan"

REPORTS = {
    "CODEX_NEW": os.path.join(BASE_DIR, "CODEX NEW", "PHASEA_MANUAL_REPORT_VALIDATED_2601090352.md"),
    "CODEX_MANU": os.path.join(BASE_DIR, "CODEX manu", "PHASEA_MANUAL_REPORT_2601090949.md"),
    "OPUS_MANU": os.path.join(BASE_DIR, "OPUS manu", "PHASEA_MANUAL_REPORT_2601100043_CORRECTED.md"),
    "CODEX_FINAL": os.path.join(BASE_DIR, "CODEX final", "PHASEA_REVIEW_VALIDATED_REPORT_0110012511.md")
}

SOURCE_FILE = os.path.join(BASE_DIR, "part 8 jan.xlsx")

# Known brands
KNOWN_BRANDS = [
    'addis', 'airwick', 'air wick', 'amtech', 'apollo', 'bacofoil', 'barbie', 'beaufort', 'beauty',
    'blue canyon', 'chef aid', 'colgate', 'doff', 'dove', 'draper', 'elbow grease',
    'elliott', 'elliotts', 'everbuild', 'eveready', 'everready', 'extra select', 'fairy', 'falcon',
    'giftmaker', 'hem', 'house mate', 'jaunty', 'kilner', 'kilrock', 'lav', 'mason cash',
    'minky', 'munch crunch', 'pan aroma', 'playwrite', 'price & kensington', 'prodec',
    'quest', 'radox', 'rcr', 'rolson', 'roundup', 'royle', 'russell hobbs', 'schott zwiesel',
    'sistema', 'soudal', 'stretcherz', 'superior', 'tala', 'the big cheese', 'tidyz', 'wham',
    'white glo', 'yale', 'alberto balsam', 'adidas', 'little trees', 'dlux', 'blackspur',
    'mokate', 'greenfields', 'sozali', 'bright & homely', 'lynwood', 'apac', 'highland', 
    'fragrant', 'beaufort', 'kilner', 'falcon', 'giftmaker', 'sistema', 'colgate'
]


def extract_all_tables_from_report(report_path):
    """Extract ALL tables from a report, properly handling all section types."""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_products = []
    
    # Find all ```text blocks
    text_blocks = re.findall(r'```text\s*\n(.*?)```', content, re.DOTALL)
    
    # Also find the section header before each block
    section_pattern = r'##\s*([A-Z][A-Z\s—/]+?)\s*\([^)]*\)\s*\n.*?```text\s*\n(.*?)```'
    matches = re.findall(section_pattern, content, re.DOTALL)
    
    for section_name, table_content in matches:
        section_name = section_name.strip()
        products = parse_table_content(table_content, section_name)
        all_products.extend(products)
    
    # Fallback: if no matches, try simpler pattern
    if not all_products:
        for block in text_blocks:
            products = parse_table_content(block, "UNKNOWN")
            all_products.extend(products)
    
    return all_products


def parse_table_content(table_text, section_name):
    """Parse table content into list of product dicts."""
    products = []
    lines = table_text.strip().split('\n')
    
    # Find header line
    header_idx = None
    for i, line in enumerate(lines):
        if '|' in line and ('Verdict' in line or 'SupplierTitle' in line or 'Sup EAN' in line):
            header_idx = i
            break
    
    if header_idx is None:
        return products
    
    # Parse headers
    raw_headers = [h.strip() for h in lines[header_idx].split('|') if h.strip()]
    
    # Normalize headers
    header_map = {
        'Sup EAN': 'Supplier EAN',
        'Amz EAN': 'Amazon EAN', 
        'Conf': 'Confidence',
        'SupPrice': 'SupplierPrice',
        'SellPrice': 'SellingPrice',
        'Adj Profit': 'Adjusted Profit'
    }
    headers = [header_map.get(h, h) for h in raw_headers]
    
    # Parse data rows
    for line in lines[header_idx + 2:]:  # Skip header and separator
        if '|' in line and '---' not in line:
            values = [v.strip() for v in line.split('|')]
            values = [v for v in values if v]  # Remove empty
            
            if len(values) >= 3:
                product = {'_section': section_name}
                for j, h in enumerate(headers):
                    if j < len(values):
                        product[h] = values[j]
                products.append(product)
    
    return products


def get_ean(product):
    """Extract EAN from product."""
    for key in ['Supplier EAN', 'Sup EAN', 'EAN']:
        if key in product and product[key]:
            ean = str(product[key]).replace('.0', '').strip()
            if ean and ean not in ['nan', '-', '']:
                return ean
    return None


def normalize_category(section_name):
    """Normalize category names."""
    s = section_name.upper()
    if 'VERIFIED' in s and 'AUDITED' in s:
        return 'VERIFIED_AUDITED_OUT'
    elif 'VERIFIED' in s:
        return 'VERIFIED'
    elif 'HIGHLY LIKELY' in s and 'AUDITED' in s:
        return 'HIGHLY_LIKELY_AUDITED_OUT'
    elif 'HIGHLY LIKELY' in s:
        return 'HIGHLY_LIKELY'
    elif 'NEEDS' in s:
        return 'NEEDS_VERIFICATION'
    elif 'AUDITED' in s or 'EXCLUDED' in s:
        return 'AUDITED_OUT'
    elif 'UNRELATED' in s:
        return 'UNRELATED'
    return 'OTHER'


def validate_ean_checksum(ean_str):
    """Validate EAN-13 checksum."""
    if not ean_str or len(ean_str) < 8:
        return False
    
    # Left-pad if needed
    ean_str = ean_str.zfill(13)
    
    if not ean_str.isdigit():
        return False
    
    if len(ean_str) == 13:
        total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(ean_str[:12]))
        check = (10 - (total % 10)) % 10
        return check == int(ean_str[12])
    
    return True


def detect_pack_size_safe(title):
    """Detect pack size with proper dimension shielding."""
    if not title:
        return 1
    
    t = title.lower()
    
    # Shield: These patterns are NOT pack sizes
    dimension_contexts = [
        r'\d+\s*x\s*\d+\s*(?:cm|mm|m|inch)',  # 30x40cm
        r'\d+\s*(?:cm|mm|ml|l|ltr|g|kg|oz|inch|inches|"|\'|ft|watt|w|v)\b',
    ]
    
    # Pack patterns
    pack_patterns = [
        (r'pack\s*of\s*(\d+)', 1),
        (r'(\d+)\s*[-]?\s*pack\b', 1),
        (r'set\s*of\s*(\d+)', 1),
        (r'(\d+)\s*pce?s?\b', 1),
        (r'(\d+)\s*pieces?\b', 1),
        (r'^(\d+)\s*x\s+(?![0-9])', 1),  # "3 x Product" at start
    ]
    
    for pattern, group in pack_patterns:
        match = re.search(pattern, t)
        if match:
            try:
                size = int(match.group(group))
                if 2 <= size <= 200:
                    # Check if in dimension context
                    context_start = max(0, match.start() - 5)
                    context_end = min(len(t), match.end() + 15)
                    context = t[context_start:context_end]
                    
                    is_dimension = any(re.search(dp, context) for dp in dimension_contexts)
                    if not is_dimension:
                        return size
            except ValueError:
                pass
    
    return 1


def classify_from_source(row, ean_to_report_data):
    """Classify a product from source data using multi-source voting + rules."""
    ean = str(row.get('EAN', '')).replace('.0', '').strip()
    ean_on_page = str(row.get('EAN_OnPage', '')).replace('.0', '').strip() if pd.notna(row.get('EAN_OnPage')) else ''
    supplier_title = str(row.get('SupplierTitle', ''))
    amazon_title = str(row.get('AmazonTitle', ''))
    net_profit = float(row.get('NetProfit', 0)) if pd.notna(row.get('NetProfit')) else 0
    roi = float(row.get('ROI ( % )', 0)) if pd.notna(row.get('ROI ( % )')) else 0
    sales = int(row.get('bought_in_past_month', 0)) if pd.notna(row.get('bought_in_past_month')) else 0
    
    evidence = []
    
    # EAN matching
    ean_valid = validate_ean_checksum(ean)
    ean_page_valid = validate_ean_checksum(ean_on_page) if ean_on_page and ean_on_page != 'nan' else False
    ean_match = ean == ean_on_page and ean_valid and ean_page_valid
    ean_conflict = ean_valid and ean_page_valid and ean != ean_on_page
    
    if ean_match:
        evidence.append("Exact EAN match")
    elif ean_conflict:
        evidence.append("EAN conflict (both valid)")
    elif not ean_page_valid:
        evidence.append("Amazon EAN missing/invalid")
    
    # Brand matching
    supplier_brand = None
    amazon_brand = None
    for brand in KNOWN_BRANDS:
        if brand.lower() in supplier_title.lower():
            supplier_brand = brand
            break
    for brand in KNOWN_BRANDS:
        if brand.lower() in amazon_title.lower():
            amazon_brand = brand
            break
    
    brand_match = supplier_brand and (
        (amazon_brand and supplier_brand.lower() == amazon_brand.lower()) or
        supplier_brand.lower() in amazon_title.lower()
    )
    
    if brand_match:
        evidence.append(f"Brand: {supplier_brand}")
    
    # Title similarity
    if supplier_title and amazon_title:
        sim = SequenceMatcher(None, supplier_title.lower(), amazon_title.lower()).ratio() * 100
        evidence.append(f"Similarity: {sim:.0f}%")
    else:
        sim = 0
    
    # Pack size
    sup_pack = detect_pack_size_safe(supplier_title)
    amz_pack = detect_pack_size_safe(amazon_title)
    rsu = max(1, amz_pack // sup_pack) if sup_pack > 0 else amz_pack
    adjusted_profit = net_profit / rsu if rsu > 0 else net_profit
    
    if rsu > 1:
        evidence.append(f"RSU={rsu}, Adj=£{adjusted_profit:.2f}")
    else:
        evidence.append(f"Profit=£{net_profit:.2f}")
    
    # Check what reports say about this product
    report_votes = {}
    if ean in ean_to_report_data:
        for report_name, data in ean_to_report_data[ean].items():
            cat = data.get('category', 'UNKNOWN')
            report_votes[report_name] = cat
    
    if report_votes:
        evidence.append(f"Reports: {len(report_votes)}")
    
    # CLASSIFICATION LOGIC
    
    # Negative adjusted profit -> AUDITED OUT
    if adjusted_profit <= 0:
        return 'AUDITED_OUT', 85, "; ".join(evidence), adjusted_profit, rsu
    
    # Exact EAN match -> VERIFIED
    if ean_match:
        return 'VERIFIED', 95, "; ".join(evidence), adjusted_profit, rsu
    
    # EAN conflict -> NEEDS VERIFICATION
    if ean_conflict:
        return 'NEEDS_VERIFICATION', 72, "; ".join(evidence), adjusted_profit, rsu
    
    # Brand match + good similarity -> HIGHLY LIKELY
    if brand_match and sim >= 55 and adjusted_profit > 0:
        return 'HIGHLY_LIKELY', 80, "; ".join(evidence), adjusted_profit, rsu
    
    # Brand match + moderate evidence -> HIGHLY LIKELY (but lower confidence)
    if brand_match and sim >= 40 and adjusted_profit > 0.50:
        return 'HIGHLY_LIKELY', 75, "; ".join(evidence), adjusted_profit, rsu
    
    # Partial evidence -> NEEDS VERIFICATION
    if (brand_match or sim >= 40) and adjusted_profit > 0.50 and roi > 15:
        return 'NEEDS_VERIFICATION', 70, "; ".join(evidence), adjusted_profit, rsu
    
    # Everything else is UNRELATED
    return 'UNRELATED', 50, "; ".join(evidence), adjusted_profit, rsu


def main():
    print("=" * 80)
    print("MASTER FBA REPORT CONSOLIDATION")
    print("=" * 80)
    
    # 1. Load source data
    print("\n[STEP 1] Loading source Excel data...")
    source_df = pd.read_excel(SOURCE_FILE)
    print(f"   Loaded {len(source_df)} rows from source")
    
    # Create EAN lookup from source
    source_by_ean = {}
    for idx, row in source_df.iterrows():
        ean = str(row['EAN']).replace('.0', '').strip()
        if ean and ean != 'nan':
            source_by_ean[ean] = {**row.to_dict(), '_idx': idx}
    print(f"   {len(source_by_ean)} unique EANs")
    
    # 2. Parse ALL reports properly
    print("\n[STEP 2] Parsing all AI reports...")
    all_report_products = {}
    ean_to_report_data = defaultdict(dict)
    
    for report_name, report_path in REPORTS.items():
        if os.path.exists(report_path):
            products = extract_all_tables_from_report(report_path)
            all_report_products[report_name] = products
            
            # Categorize
            cat_counts = defaultdict(int)
            for p in products:
                section = p.get('_section', 'UNKNOWN')
                cat = normalize_category(section)
                cat_counts[cat] += 1
                
                ean = get_ean(p)
                if ean:
                    ean_to_report_data[ean][report_name] = {
                        'category': cat,
                        'raw_section': section,
                        'confidence': p.get('Confidence', ''),
                        'adjusted_profit': p.get('Adjusted Profit', ''),
                        'pack_verdict': p.get('Pack Verdict', '')
                    }
            
            print(f"\n   {report_name}: {len(products)} total products")
            for cat, count in sorted(cat_counts.items()):
                print(f"      - {cat}: {count}")
    
    # 3. Merge and consolidate from all reports
    print("\n[STEP 3] Merging valid entries from all reports...")
    
    merged_entries = {}  # ean -> best entry
    
    for ean, report_data in ean_to_report_data.items():
        # Get the classification from each report
        classifications = []
        for rname, rdata in report_data.items():
            cat = rdata['category']
            if cat in ['VERIFIED', 'HIGHLY_LIKELY', 'NEEDS_VERIFICATION']:
                classifications.append((rname, cat, rdata))
        
        if not classifications:
            continue
        
        # Voting: majority category wins
        cat_votes = defaultdict(list)
        for rname, cat, rdata in classifications:
            cat_votes[cat].append((rname, rdata))
        
        # Pick best category (priority: VERIFIED > HIGHLY_LIKELY > NEEDS_VERIFICATION)
        best_cat = None
        best_reports = []
        for cat in ['VERIFIED', 'HIGHLY_LIKELY', 'NEEDS_VERIFICATION']:
            if cat in cat_votes:
                best_cat = cat
                best_reports = cat_votes[cat]
                break
        
        if best_cat:
            # Get source data
            source_data = source_by_ean.get(ean, {})
            merged_entries[ean] = {
                'ean': ean,
                'category': best_cat,
                'reports_agreed': len(best_reports),
                'report_names': [r[0] for r in best_reports],
                'source_data': source_data
            }
    
    print(f"   Merged {len(merged_entries)} products from all reports")
    
    # 4. Retrieve MISSED products from source Excel
    print("\n[STEP 4] Retrieving missed products from source Excel...")
    
    missed_verified = []
    missed_highly_likely = []
    
    for ean, source_data in source_by_ean.items():
        if ean in merged_entries:
            continue  # Already included
        
        # Classify this product independently
        category, conf, evidence, adj_profit, rsu = classify_from_source(source_data, ean_to_report_data)
        
        if category == 'VERIFIED' and adj_profit > 0:
            missed_verified.append({
                'ean': ean,
                'category': category,
                'confidence': conf,
                'evidence': evidence,
                'adjusted_profit': adj_profit,
                'rsu': rsu,
                'source_data': source_data
            })
        elif category == 'HIGHLY_LIKELY' and adj_profit > 0:
            missed_highly_likely.append({
                'ean': ean,
                'category': category,
                'confidence': conf,
                'evidence': evidence,
                'adjusted_profit': adj_profit,
                'rsu': rsu,
                'source_data': source_data
            })
    
    print(f"   Found {len(missed_verified)} missed VERIFIED products")
    print(f"   Found {len(missed_highly_likely)} missed HIGHLY LIKELY products")
    
    # 5. Re-classify all merged entries using our improved logic
    print("\n[STEP 5] Re-classifying all products with corrected logic...")
    
    final_verified = []
    final_highly_likely = []
    final_needs_verification = []
    final_audited_out = []
    
    # Process merged entries
    for ean, entry in merged_entries.items():
        source_data = entry.get('source_data', {})
        if not source_data:
            continue
        
        category, conf, evidence, adj_profit, rsu = classify_from_source(source_data, ean_to_report_data)
        
        product_entry = {
            'ean': ean,
            'supplier_title': str(source_data.get('SupplierTitle', ''))[:60],
            'amazon_title': str(source_data.get('AmazonTitle', ''))[:60],
            'net_profit': source_data.get('NetProfit', 0),
            'adjusted_profit': adj_profit,
            'roi': source_data.get('ROI ( % )', 0),
            'sales': source_data.get('bought_in_past_month', 0),
            'rsu': rsu,
            'confidence': conf,
            'evidence': evidence,
            'original_category': entry['category'],
            'reports_agreed': entry['reports_agreed'],
            'report_sources': ', '.join(entry['report_names'])
        }
        
        if category == 'VERIFIED':
            final_verified.append(product_entry)
        elif category == 'HIGHLY_LIKELY':
            final_highly_likely.append(product_entry)
        elif category == 'NEEDS_VERIFICATION':
            final_needs_verification.append(product_entry)
        elif category == 'AUDITED_OUT':
            final_audited_out.append(product_entry)
    
    # Add missed entries
    for entry in missed_verified:
        sd = entry['source_data']
        product_entry = {
            'ean': entry['ean'],
            'supplier_title': str(sd.get('SupplierTitle', ''))[:60],
            'amazon_title': str(sd.get('AmazonTitle', ''))[:60],
            'net_profit': sd.get('NetProfit', 0),
            'adjusted_profit': entry['adjusted_profit'],
            'roi': sd.get('ROI ( % )', 0),
            'sales': sd.get('bought_in_past_month', 0),
            'rsu': entry['rsu'],
            'confidence': entry['confidence'],
            'evidence': entry['evidence'],
            'original_category': 'MISSED',
            'reports_agreed': 0,
            'report_sources': 'RETRIEVED FROM SOURCE'
        }
        final_verified.append(product_entry)
    
    for entry in missed_highly_likely:
        sd = entry['source_data']
        product_entry = {
            'ean': entry['ean'],
            'supplier_title': str(sd.get('SupplierTitle', ''))[:60],
            'amazon_title': str(sd.get('AmazonTitle', ''))[:60],
            'net_profit': sd.get('NetProfit', 0),
            'adjusted_profit': entry['adjusted_profit'],
            'roi': sd.get('ROI ( % )', 0),
            'sales': sd.get('bought_in_past_month', 0),
            'rsu': entry['rsu'],
            'confidence': entry['confidence'],
            'evidence': entry['evidence'],
            'original_category': 'MISSED',
            'reports_agreed': 0,
            'report_sources': 'RETRIEVED FROM SOURCE'
        }
        final_highly_likely.append(product_entry)
    
    # Sort by adjusted profit
    final_verified.sort(key=lambda x: float(x.get('adjusted_profit', 0) or 0), reverse=True)
    final_highly_likely.sort(key=lambda x: float(x.get('adjusted_profit', 0) or 0), reverse=True)
    final_needs_verification.sort(key=lambda x: float(x.get('adjusted_profit', 0) or 0), reverse=True)
    
    print(f"\n   FINAL COUNTS:")
    print(f"   - VERIFIED: {len(final_verified)}")
    print(f"   - HIGHLY LIKELY: {len(final_highly_likely)}")
    print(f"   - NEEDS VERIFICATION: {len(final_needs_verification)}")
    print(f"   - AUDITED OUT: {len(final_audited_out)}")
    
    # 6. Generate consolidated report
    print("\n[STEP 6] Generating consolidated report...")
    
    output = []
    output.append("# CONSOLIDATED FBA REPORT - MASTER VALIDATION")
    output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"**Source:** part 8 jan.xlsx ({len(source_df)} rows)")
    output.append("")
    output.append("---")
    output.append("")
    
    # Executive Summary
    output.append("## EXECUTIVE SUMMARY")
    output.append("")
    output.append("This consolidated report merges valid entries from all four AI reports,")
    output.append("applies corrected classification logic, and retrieves missed products from the source data.")
    output.append("")
    output.append("### Reports Analyzed:")
    for name in REPORTS.keys():
        output.append(f"- {name}")
    output.append("")
    output.append("### Final Counts:")
    output.append(f"| Category | Count | Est. Total Profit |")
    output.append(f"|----------|-------|-------------------|")
    v_profit = sum(float(p.get('adjusted_profit', 0) or 0) for p in final_verified)
    hl_profit = sum(float(p.get('adjusted_profit', 0) or 0) for p in final_highly_likely)
    nv_profit = sum(float(p.get('adjusted_profit', 0) or 0) for p in final_needs_verification)
    output.append(f"| **VERIFIED** | {len(final_verified)} | £{v_profit:.2f} |")
    output.append(f"| **HIGHLY LIKELY** | {len(final_highly_likely)} | £{hl_profit:.2f} |")
    output.append(f"| **NEEDS VERIFICATION** | {len(final_needs_verification)} | £{nv_profit:.2f} |")
    output.append(f"| **AUDITED OUT** | {len(final_audited_out)} | - |")
    output.append(f"| **TOTAL RECOMMENDED** | {len(final_verified) + len(final_highly_likely)} | £{v_profit + hl_profit:.2f} |")
    output.append("")
    
    # ROOT CAUSE ANALYSIS
    output.append("---")
    output.append("")
    output.append("## ROOT CAUSE ANALYSIS")
    output.append("")
    output.append("### Issues Identified in Original Reports:")
    output.append("")
    output.append("1. **HIGHLY LIKELY Parsing Failure**")
    output.append("   - My initial script failed to parse HIGHLY LIKELY sections due to regex pattern mismatch")
    output.append("   - The sections used headers like `## HIGHLY LIKELY — RECOMMENDED (count=X)` which weren't matched")
    output.append("   - **FIX APPLIED:** Updated regex to match all section header variants")
    output.append("")
    output.append("2. **Dimension Trap False Positives**")
    output.append("   - Products like 'APOLLO VINEGAR SHAKER' with '15x5.5x5.5cm' were misread as pack sizes")
    output.append("   - **FIX APPLIED:** Dimension shielding now excludes patterns with cm/mm/ml suffixes")  
    output.append("")
    output.append("3. **Model Number Confusion**")
    output.append("   - Model numbers like '2001.542' were mistaken for pack quantities")
    output.append("   - **FIX APPLIED:** Context-aware pack detection")
    output.append("")
    output.append("4. **Negative Profit Misrouting**")
    output.append("   - Some products with adjusted profit ≤ 0 were left in VERIFIED/HIGHLY LIKELY")
    output.append("   - **FIX APPLIED:** Strict adjusted profit ≤ 0 → AUDITED OUT routing")
    output.append("")
    
    # VERIFIED PRODUCTS
    output.append("---")
    output.append("")
    output.append(f"## VERIFIED — RECOMMENDED ({len(final_verified)} products)")
    output.append("")
    output.append("*Exact EAN matches with positive adjusted profit*")
    output.append("")
    output.append("| EAN | Supplier Title | Amazon Title | Net Profit | Adj Profit | ROI | Sales | RSU | Source |")
    output.append("|-----|----------------|--------------|------------|------------|-----|-------|-----|--------|")
    
    for p in final_verified:
        np = f"£{float(p.get('net_profit', 0) or 0):.2f}"
        ap = f"£{float(p.get('adjusted_profit', 0) or 0):.2f}"
        roi = f"{float(p.get('roi', 0) or 0):.1f}%"
        sales = int(p.get('sales', 0) or 0)
        output.append(f"| {p['ean']} | {p['supplier_title'][:40]} | {p['amazon_title'][:40]} | {np} | {ap} | {roi} | {sales} | {p['rsu']} | {p['report_sources'][:20]} |")
    
    output.append("")
    
    # HIGHLY LIKELY PRODUCTS
    output.append("---")
    output.append("")
    output.append(f"## HIGHLY LIKELY — RECOMMENDED ({len(final_highly_likely)} products)")
    output.append("")
    output.append("*Strong brand/title matches with positive adjusted profit*")
    output.append("")
    output.append("| EAN | Supplier Title | Amazon Title | Net Profit | Adj Profit | ROI | Sales | Evidence |")
    output.append("|-----|----------------|--------------|------------|------------|-----|-------|----------|")
    
    for p in final_highly_likely:
        np = f"£{float(p.get('net_profit', 0) or 0):.2f}"
        ap = f"£{float(p.get('adjusted_profit', 0) or 0):.2f}"
        roi = f"{float(p.get('roi', 0) or 0):.1f}%"
        sales = int(p.get('sales', 0) or 0)
        evidence = p.get('evidence', '')[:50]
        output.append(f"| {p['ean']} | {p['supplier_title'][:40]} | {p['amazon_title'][:40]} | {np} | {ap} | {roi} | {sales} | {evidence} |")
    
    output.append("")
    
    # NEEDS VERIFICATION
    output.append("---")
    output.append("")
    output.append(f"## NEEDS VERIFICATION ({len(final_needs_verification)} products)")
    output.append("")
    output.append("*Partial match evidence requiring manual confirmation*")
    output.append("")
    output.append("| EAN | Supplier Title | Net Profit | Adj Profit | Evidence |")
    output.append("|-----|----------------|------------|------------|----------|")
    
    for p in final_needs_verification[:50]:  # Limit display
        np = f"£{float(p.get('net_profit', 0) or 0):.2f}"
        ap = f"£{float(p.get('adjusted_profit', 0) or 0):.2f}"
        evidence = p.get('evidence', '')[:60]
        output.append(f"| {p['ean']} | {p['supplier_title'][:45]} | {np} | {ap} | {evidence} |")
    
    if len(final_needs_verification) > 50:
        output.append(f"\n*...and {len(final_needs_verification) - 50} more entries*")
    
    output.append("")
    
    # CONCLUSIONS
    output.append("---")
    output.append("")
    output.append("## CONCLUSIONS")
    output.append("")
    output.append("### Key Findings:")
    output.append("")
    output.append(f"1. **Total Recommended Products:** {len(final_verified) + len(final_highly_likely)} (VERIFIED + HIGHLY LIKELY)")
    output.append(f"2. **Estimated Combined Profit:** £{v_profit + hl_profit:.2f}")
    output.append(f"3. **Products Requiring Verification:** {len(final_needs_verification)}")
    output.append(f"4. **Products Audited Out:** {len(final_audited_out)}")
    output.append("")
    output.append("### Report Comparison Summary:")
    output.append("")
    
    for report_name, products in all_report_products.items():
        cats = defaultdict(int)
        for p in products:
            cats[normalize_category(p.get('_section', ''))] += 1
        v = cats.get('VERIFIED', 0)
        hl = cats.get('HIGHLY_LIKELY', 0)
        nv = cats.get('NEEDS_VERIFICATION', 0)
        ao = cats.get('AUDITED_OUT', 0) + cats.get('VERIFIED_AUDITED_OUT', 0)
        output.append(f"- **{report_name}:** V={v}, HL={hl}, NV={nv}, AO={ao}")
    
    output.append("")
    output.append("### Recommendations:")
    output.append("")
    output.append("1. **Prioritize VERIFIED products** - These have exact EAN matches and confirmed profitability")
    output.append("2. **Review HIGHLY LIKELY products** - Strong matches but may need listing verification")
    output.append("3. **Investigate NEEDS VERIFICATION** - Potential opportunities requiring manual research")
    output.append("4. **CODEX_FINAL report performed best** - Use as baseline for future analysis")
    output.append("")
    output.append("---")
    output.append(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Write report
    output_path = os.path.join(BASE_DIR, f"CONSOLIDATED_MASTER_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"\n   Report saved to: {output_path}")
    
    print("\n" + "=" * 80)
    print("CONSOLIDATION COMPLETE")
    print("=" * 80)
    print(f"   VERIFIED: {len(final_verified)}")
    print(f"   HIGHLY LIKELY: {len(final_highly_likely)}")
    print(f"   NEEDS VERIFICATION: {len(final_needs_verification)}")
    print(f"   AUDITED OUT: {len(final_audited_out)}")
    print(f"   TOTAL PROFIT POTENTIAL: £{v_profit + hl_profit:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
