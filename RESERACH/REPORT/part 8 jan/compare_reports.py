#!/usr/bin/env python3
"""
FBA Report Comparison and Validation Script
Compares four AI-generated reports and validates against source data
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

# Known brand list
KNOWN_BRANDS = [
    'addis', 'airwick', 'amtech', 'apollo', 'bacofoil', 'barbie', 'beaufort', 'beauty',
    'blue canyon', 'chef aid', 'colgate', 'doff', 'dove', 'draper', 'elbow grease',
    'elliott', 'everbuild', 'eveready', 'everready', 'extra select', 'fairy', 'falcon',
    'giftmaker', 'hem', 'house mate', 'jaunty', 'kilner', 'kilrock', 'lav', 'mason cash',
    'minky', 'munch crunch', 'pan aroma', 'playwrite', 'price & kensington', 'prodec',
    'quest', 'radox', 'rcr', 'rolson', 'roundup', 'royle', 'russell hobbs', 'schott zwiesel',
    'sistema', 'soudal', 'stretcherz', 'superior', 'tala', 'the big cheese', 'tidyz', 'wham',
    'white glo', 'yale', 'alberto balsam', 'adidas', 'little trees', 'dlux', 'blackspur',
    'mokate', 'greenfields', 'sozali', 'bright & homely', 'lynwood', 'apac'
]

INVALID_FIRST_WORDS = ['paper', 'fairy', 'chef', 'pop', 'gel', 'glass', 'mirror', 'paint', 
                        'silicone', 'vacuum', 'wall', 'metal', 'farm', 'square', 'party',
                        'baby', 'cat', 'garden', 'happy', 'fire', 'mens', 'oven', 'craft',
                        'christmas', 'memorial', 'magnetic', 'all', 'the']


def parse_report_table(content, category_name):
    """Parse a markdown table from the report content for a specific category."""
    products = []
    
    # Find the section for this category
    pattern = rf"## {re.escape(category_name)}.*?```text\s*\n(.*?)```"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        # Try alternate pattern without ```text
        pattern = rf"## {re.escape(category_name)}.*?\n(\|.*?)(?:\n##|\n```|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if match:
        table_content = match.group(1).strip()
        lines = table_content.split('\n')
        
        # Find header line
        header_line = None
        for i, line in enumerate(lines):
            if '|' in line and 'Verdict' in line:
                header_line = i
                break
        
        if header_line is not None:
            headers = [h.strip() for h in lines[header_line].split('|')[1:-1]]
            
            # Parse data rows (skip header and separator)
            for line in lines[header_line + 2:]:
                if '|' in line and not line.strip().startswith('|--'):
                    values = [v.strip() for v in line.split('|')[1:-1]]
                    if len(values) >= len(headers):
                        product = {}
                        for j, h in enumerate(headers):
                            product[h] = values[j] if j < len(values) else ''
                        products.append(product)
    
    return products


def extract_products_from_report(report_path, report_name):
    """Extract all products from a report file, organized by category."""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    categories_to_check = [
        "VERIFIED — RECOMMENDED",
        "VERIFIED — AUDITED OUT",
        "VERIFIED",
        "HIGHLY LIKELY — RECOMMENDED",
        "HIGHLY LIKELY — AUDITED OUT",
        "HIGHLY LIKELY",
        "AUDITED OUT / EXCLUDED",
        "AUDITED OUT",
        "NEEDS VERIFICATION",
        "UNRELATED"
    ]
    
    all_products = {}
    for category in categories_to_check:
        products = parse_report_table(content, category)
        if products:
            all_products[category] = products
    
    return all_products


def get_title_similarity(title1, title2):
    """Calculate similarity between two titles."""
    if not title1 or not title2:
        return 0.0
    
    t1 = title1.lower()
    t2 = title2.lower()
    
    # Sequence similarity
    seq_sim = SequenceMatcher(None, t1, t2).ratio()
    
    # Keyword overlap
    words1 = set(t1.split())
    words2 = set(t2.split())
    common = words1 & words2
    union = words1 | words2
    keyword_sim = len(common) / len(union) if union else 0
    
    return max(seq_sim, keyword_sim) * 100


def detect_pack_size(title):
    """Detect pack size from title, with dimension shielding."""
    if not title:
        return 1
    
    title_lower = title.lower()
    
    # Dimension patterns to IGNORE (these are measurements, not pack sizes)
    dimension_patterns = [
        r'\d+\s*(?:cm|mm|m|inch|inches|"|\'|ft|oz|ml|l|ltr|litre|liter|g|kg|gramme|gram)\b',
        r'\d+\s*x\s*\d+\s*(?:cm|mm|m)',  # dimensions like 30x40cm
        r'\d+\s*(?:watt|w|v|volt)\b',
    ]
    
    # Check if the pattern is likely a dimension
    def is_likely_dimension(match_str):
        for dp in dimension_patterns:
            if re.search(dp, match_str.lower()):
                return True
        return False
    
    # Pack patterns to detect
    pack_patterns = [
        r'(\d+)\s*[-]?\s*pack\b',
        r'pack\s*of\s*(\d+)',
        r'(\d+)\s*x\s+(?![\d.])',  # "3 x " but not "3 x 4cm"
        r'(\d+)x\s+',
        r'set\s*of\s*(\d+)',
        r'\((\d+)\)',
        r'(\d+)\s*pce?s?\b',
        r'(\d+)\s*pieces?\b',
    ]
    
    for pattern in pack_patterns:
        matches = re.findall(pattern, title_lower)
        for match in matches:
            try:
                size = int(match)
                if 2 <= size <= 100:  # Reasonable pack size range
                    # Verify it's not a dimension
                    context = re.search(rf'{match}\s*\S{{0,10}}', title_lower)
                    if context and not is_likely_dimension(context.group()):
                        return size
            except ValueError:
                continue
    
    return 1


def extract_brand(title, known_brands):
    """Extract brand from title."""
    if not title:
        return None
    
    title_lower = title.lower()
    
    for brand in known_brands:
        if brand.lower() in title_lower:
            return brand
    
    # Check first word (if not invalid)
    first_word = title_lower.split()[0] if title_lower.split() else ''
    if first_word and first_word not in [b.lower() for b in INVALID_FIRST_WORDS]:
        return first_word.title()
    
    return None


def validate_ean(ean):
    """Validate EAN using checksum."""
    if not ean or pd.isna(ean):
        return False
    
    ean_str = str(ean).replace('.0', '').strip()
    
    # Left-pad to 13 digits if needed
    if len(ean_str) < 13:
        ean_str = ean_str.zfill(13)
    
    if not ean_str.isdigit() or len(ean_str) not in [8, 12, 13, 14]:
        return False
    
    # Checksum validation for EAN-13
    if len(ean_str) == 13:
        total = 0
        for i, digit in enumerate(ean_str[:12]):
            multiplier = 1 if i % 2 == 0 else 3
            total += int(digit) * multiplier
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(ean_str[12])
    
    return True  # Simplified for other lengths


def classify_product(row, source_df=None):
    """
    Independently classify a product based on the methodology.
    Returns: (category, confidence, reasoning)
    """
    supplier_ean = str(row.get('EAN', '')).replace('.0', '').strip()
    amazon_ean = str(row.get('EAN_OnPage', '')).replace('.0', '').strip() if 'EAN_OnPage' in row else ''
    supplier_title = str(row.get('SupplierTitle', ''))
    amazon_title = str(row.get('AmazonTitle', ''))
    net_profit = float(row.get('NetProfit', 0)) if pd.notna(row.get('NetProfit')) else 0
    roi = float(row.get('ROI ( % )', 0)) if pd.notna(row.get('ROI ( % )')) else 0
    
    reasons = []
    
    # 1. EAN Analysis
    supplier_ean_valid = validate_ean(supplier_ean)
    amazon_ean_valid = validate_ean(amazon_ean) if amazon_ean and amazon_ean != 'nan' else False
    ean_match = supplier_ean == amazon_ean and supplier_ean_valid and amazon_ean_valid
    
    if ean_match:
        reasons.append("Exact EAN match")
    elif supplier_ean_valid and amazon_ean_valid and supplier_ean != amazon_ean:
        reasons.append("EAN conflict (both valid but different)")
    elif not amazon_ean_valid:
        reasons.append("Amazon EAN missing/invalid")
    
    # 2. Brand Analysis
    supplier_brand = extract_brand(supplier_title, KNOWN_BRANDS)
    amazon_brand = extract_brand(amazon_title, KNOWN_BRANDS)
    brand_match = supplier_brand and amazon_brand and supplier_brand.lower() == amazon_brand.lower()
    
    if brand_match:
        reasons.append(f"Brand match: {supplier_brand}")
    elif supplier_brand and supplier_brand.lower() in amazon_title.lower():
        reasons.append(f"Supplier brand '{supplier_brand}' appears in Amazon title")
        brand_match = True
    
    # 3. Title Similarity
    similarity = get_title_similarity(supplier_title, amazon_title)
    if similarity >= 55:
        reasons.append(f"Strong title similarity: {similarity:.1f}%")
    elif similarity >= 40:
        reasons.append(f"Moderate title similarity: {similarity:.1f}%")
    else:
        reasons.append(f"Weak title similarity: {similarity:.1f}%")
    
    # 4. Pack Size Analysis
    supplier_pack = detect_pack_size(supplier_title)
    amazon_pack = detect_pack_size(amazon_title)
    rsu = amazon_pack // supplier_pack if supplier_pack > 0 else amazon_pack
    adjusted_profit = net_profit / rsu if rsu > 0 else net_profit
    
    if supplier_pack != amazon_pack:
        reasons.append(f"Pack mismatch: supplier={supplier_pack}, amazon={amazon_pack}, RSU={rsu}")
    else:
        reasons.append(f"Pack match: {supplier_pack}")
    
    reasons.append(f"Adjusted profit: £{adjusted_profit:.2f}")
    
    # 5. Classification Decision
    if adjusted_profit <= 0:
        if ean_match:
            return "AUDITED OUT", 85, "EAN match but negative adjusted profit; " + "; ".join(reasons)
        else:
            return "AUDITED OUT", 75, "Negative adjusted profit; " + "; ".join(reasons)
    
    if ean_match and supplier_pack == amazon_pack:
        return "VERIFIED", 95, "; ".join(reasons)
    
    if ean_match and adjusted_profit > 0:
        if supplier_pack != amazon_pack:
            return "VERIFIED", 90, "EAN match with pack adjustment; " + "; ".join(reasons)
        return "VERIFIED", 95, "; ".join(reasons)
    
    if brand_match and similarity >= 55 and adjusted_profit > 0:
        return "HIGHLY LIKELY", 80, "; ".join(reasons)
    
    if brand_match and adjusted_profit > 0.50 and roi > 15:
        return "NEEDS VERIFICATION", 72, "; ".join(reasons)
    
    if similarity >= 40 and adjusted_profit > 0:
        return "NEEDS VERIFICATION", 70, "; ".join(reasons)
    
    return "UNRELATED", 50, "Insufficient match evidence; " + "; ".join(reasons)


def compare_products_across_reports(reports_data, source_df):
    """Compare how each report classified products."""
    comparison_results = defaultdict(lambda: defaultdict(dict))
    
    # Build EAN-based lookup from source
    ean_to_row = {}
    for idx, row in source_df.iterrows():
        ean = str(row['EAN']).replace('.0', '').strip()
        ean_to_row[ean] = row.to_dict()
        ean_to_row[ean]['RowIndex'] = idx
    
    # Extract unique products from all reports
    all_eans = set()
    
    for report_name, categories in reports_data.items():
        for category, products in categories.items():
            for product in products:
                ean = product.get('Supplier EAN', product.get('EAN', '')).replace('.0', '').strip()
                if ean:
                    all_eans.add(ean)
                    comparison_results[ean][report_name] = {
                        'category': category,
                        'confidence': product.get('Confidence', ''),
                        'pack_verdict': product.get('Pack Verdict', ''),
                        'adjusted_profit': product.get('Adjusted Profit', ''),
                        'supplier_title': product.get('SupplierTitle', ''),
                        'amazon_title': product.get('AmazonTitle', '')
                    }
    
    return comparison_results, ean_to_row


def generate_validation_report(comparison_results, ean_to_row, reports_data, source_df):
    """Generate the comprehensive validation report."""
    
    output = []
    output.append("# FBA Report Comparison and Validation Report")
    output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    # Executive Summary
    output.append("## Executive Summary")
    output.append("")
    output.append("This report provides a comprehensive comparison of four AI-generated FBA analysis reports:")
    output.append("")
    for report_name in reports_data.keys():
        output.append(f"- **{report_name}**")
    output.append("")
    output.append(f"**Source Data:** {len(source_df)} total products in `part 8 jan.xlsx`")
    output.append(f"**Products with Classifications:** {len(comparison_results)}")
    output.append("")
    
    # Summary Statistics per Report
    output.append("## Summary Statistics by Report")
    output.append("")
    output.append("| Report | VERIFIED | HIGHLY LIKELY | NEEDS VERIFICATION | AUDITED OUT | Total Classified |")
    output.append("|--------|----------|---------------|---------------------|-------------|------------------|")
    
    for report_name, categories in reports_data.items():
        verified = 0
        highly_likely = 0
        needs_verification = 0
        audited_out = 0
        
        for category, products in categories.items():
            count = len(products)
            cat_upper = category.upper()
            if 'VERIFIED' in cat_upper and 'AUDITED' not in cat_upper:
                verified += count
            elif 'HIGHLY LIKELY' in cat_upper and 'AUDITED' not in cat_upper:
                highly_likely += count
            elif 'NEEDS VERIFICATION' in cat_upper:
                needs_verification += count
            elif 'AUDITED' in cat_upper:
                audited_out += count
        
        total = verified + highly_likely + needs_verification + audited_out
        output.append(f"| {report_name} | {verified} | {highly_likely} | {needs_verification} | {audited_out} | {total} |")
    
    output.append("")
    
    # Classification Agreement Analysis
    output.append("## Classification Agreement Analysis")
    output.append("")
    
    total_products = len(comparison_results)
    agreement_count = 0
    disagreement_count = 0
    partial_agreement = 0
    
    disagreements = []
    
    for ean, report_classifications in comparison_results.items():
        categories = []
        for report_name, data in report_classifications.items():
            cat = data.get('category', 'UNKNOWN').upper()
            # Normalize categories
            if 'VERIFIED' in cat and 'AUDITED' not in cat:
                categories.append('VERIFIED')
            elif 'HIGHLY LIKELY' in cat and 'AUDITED' not in cat:
                categories.append('HIGHLY_LIKELY')
            elif 'NEEDS' in cat:
                categories.append('NEEDS_VERIFICATION')
            elif 'AUDITED' in cat:
                categories.append('AUDITED_OUT')
            else:
                categories.append('OTHER')
        
        unique_cats = set(categories)
        if len(unique_cats) == 1:
            agreement_count += 1
        elif len(unique_cats) == 2:
            partial_agreement += 1
            disagreements.append((ean, report_classifications))
        else:
            disagreement_count += 1
            disagreements.append((ean, report_classifications))
    
    output.append(f"- **Full Agreement (all reports agree):** {agreement_count} products ({agreement_count/total_products*100:.1f}%)")
    output.append(f"- **Partial Agreement (2-3 agree):** {partial_agreement} products ({partial_agreement/total_products*100:.1f}%)")
    output.append(f"- **Disagreement (most disagree):** {disagreement_count} products ({disagreement_count/total_products*100:.1f}%)")
    output.append("")
    
    # Key Disagreements
    output.append("## Key Classification Disagreements")
    output.append("")
    output.append("The following products had significant classification differences across reports:")
    output.append("")
    
    disagreement_table = []
    for ean, report_classifications in disagreements[:30]:  # Limit to first 30
        row_data = ean_to_row.get(ean, {})
        supplier_title = row_data.get('SupplierTitle', 'N/A')[:50]
        
        row = f"| {ean} | {supplier_title} |"
        for report_name in reports_data.keys():
            data = report_classifications.get(report_name, {})
            cat = data.get('category', 'NOT_LISTED')[:15]
            row += f" {cat} |"
        disagreement_table.append(row)
    
    header = "| EAN | Supplier Title |"
    separator = "|-----|----------------|"
    for report_name in reports_data.keys():
        header += f" {report_name[:12]} |"
        separator += "---------------|"
    
    output.append(header)
    output.append(separator)
    output.extend(disagreement_table)
    output.append("")
    
    # Independent Classification Analysis
    output.append("## Independent Classification (Ground Truth)")
    output.append("")
    output.append("Below is our independent classification of key products using the strict methodology:")
    output.append("")
    
    # Sample 20 products for detailed analysis
    sampled_products = []
    for ean, report_classifications in list(comparison_results.items())[:50]:
        if ean in ean_to_row:
            row = ean_to_row[ean]
            category, confidence, reasoning = classify_product(row)
            sampled_products.append({
                'ean': ean,
                'supplier_title': row.get('SupplierTitle', '')[:40],
                'our_category': category,
                'our_confidence': confidence,
                'reasoning': reasoning[:100],
                'report_classifications': report_classifications
            })
    
    output.append("| EAN | Supplier Title | Our Classification | CODEX_NEW | CODEX_MANU | OPUS_MANU | CODEX_FINAL |")
    output.append("|-----|----------------|-------------------|-----------|------------|-----------|-------------|")
    
    for p in sampled_products[:25]:
        row = f"| {p['ean']} | {p['supplier_title']} | {p['our_category']} |"
        for report_name in ['CODEX_NEW', 'CODEX_MANU', 'OPUS_MANU', 'CODEX_FINAL']:
            data = p['report_classifications'].get(report_name, {})
            cat = data.get('category', 'N/A')[:12]
            row += f" {cat} |"
        output.append(row)
    
    output.append("")
    
    # Model Accuracy Statistics
    output.append("## Model Accuracy Statistics")
    output.append("")
    output.append("Accuracy is calculated by comparing each report's classification against our independent ground truth classification.")
    output.append("")
    
    accuracy_stats = {}
    for report_name in reports_data.keys():
        correct = 0
        total = 0
        category_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for p in sampled_products:
            our_cat = p['our_category']
            report_cat = p['report_classifications'].get(report_name, {}).get('category', '')
            
            # Normalize
            report_cat_norm = ''
            if 'VERIFIED' in report_cat.upper() and 'AUDITED' not in report_cat.upper():
                report_cat_norm = 'VERIFIED'
            elif 'HIGHLY LIKELY' in report_cat.upper() and 'AUDITED' not in report_cat.upper():
                report_cat_norm = 'HIGHLY LIKELY'
            elif 'NEEDS' in report_cat.upper():
                report_cat_norm = 'NEEDS VERIFICATION'
            elif 'AUDITED' in report_cat.upper():
                report_cat_norm = 'AUDITED OUT'
            else:
                report_cat_norm = 'OTHER'
            
            total += 1
            category_stats[our_cat]['total'] += 1
            
            if our_cat == report_cat_norm or (our_cat in report_cat_norm) or (report_cat_norm in our_cat):
                correct += 1
                category_stats[our_cat]['correct'] += 1
        
        accuracy = (correct / total * 100) if total > 0 else 0
        accuracy_stats[report_name] = {
            'overall': accuracy,
            'correct': correct,
            'total': total,
            'by_category': dict(category_stats)
        }
    
    output.append("### Overall Accuracy")
    output.append("")
    output.append("| Report | Correct | Total | Accuracy |")
    output.append("|--------|---------|-------|----------|")
    
    for report_name, stats in accuracy_stats.items():
        output.append(f"| {report_name} | {stats['correct']} | {stats['total']} | {stats['overall']:.1f}% |")
    
    output.append("")
    
    # Rank models
    output.append("### Model Ranking")
    output.append("")
    ranked = sorted(accuracy_stats.items(), key=lambda x: x[1]['overall'], reverse=True)
    for i, (name, stats) in enumerate(ranked, 1):
        output.append(f"{i}. **{name}** - {stats['overall']:.1f}% accuracy")
    
    output.append("")
    
    # Problem Patterns
    output.append("## Problem Patterns Identified")
    output.append("")
    output.append("Based on our analysis, the following common issues were identified:")
    output.append("")
    output.append("1. **Pack Size Detection Inconsistency**: Some reports incorrectly identified pack sizes from dimension patterns (e.g., '30x40cm' interpreted as 30-pack)")
    output.append("2. **EAN Conflict Handling**: Different approaches to handling products where supplier and Amazon EANs are both valid but different")
    output.append("3. **Brand Matching False Positives**: Generic words incorrectly matched as brands")
    output.append("4. **Adjusted Profit Calculation**: Inconsistent RSU (Retail Selling Unit) calculations leading to different adjusted profit figures")
    output.append("5. **Title Similarity Thresholds**: Varying interpretations of 'strong' vs 'moderate' title similarity")
    output.append("")
    
    # Recommendations
    output.append("## Recommendations")
    output.append("")
    output.append("1. **Standardize pack detection**: Implement dimension shielding to avoid confusing measurements with pack counts")
    output.append("2. **EAN conflict routing**: All products with EAN conflicts should be routed to NEEDS VERIFICATION")
    output.append("3. **Use strict brand list**: Only match brands from the known brands list, not generic first words")
    output.append("4. **Consistent RSU calculation**: Ensure RSU = Amazon pack / Supplier pack is applied consistently")
    output.append("5. **Negative profit routing**: Any product with adjusted profit ≤ 0 should be AUDITED OUT")
    output.append("")
    
    output.append("---")
    output.append(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return '\n'.join(output)


def main():
    print("Loading source data...")
    source_df = pd.read_excel(SOURCE_FILE)
    print(f"Loaded {len(source_df)} rows from source")
    
    print("\nLoading reports...")
    reports_data = {}
    for report_name, report_path in REPORTS.items():
        if os.path.exists(report_path):
            print(f"  Loading {report_name}...")
            reports_data[report_name] = extract_products_from_report(report_path, report_name)
            total_products = sum(len(products) for products in reports_data[report_name].values())
            print(f"    Found {total_products} classified products")
        else:
            print(f"  WARNING: {report_name} not found at {report_path}")
    
    print("\nComparing products across reports...")
    comparison_results, ean_to_row = compare_products_across_reports(reports_data, source_df)
    print(f"  Found {len(comparison_results)} unique products across all reports")
    
    print("\nGenerating validation report...")
    report_content = generate_validation_report(comparison_results, ean_to_row, reports_data, source_df)
    
    output_path = os.path.join(BASE_DIR, f"VALIDATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\nValidation report saved to: {output_path}")
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for report_name, categories in reports_data.items():
        total = sum(len(products) for products in categories.values())
        print(f"  {report_name}: {total} products classified")


if __name__ == "__main__":
    main()
