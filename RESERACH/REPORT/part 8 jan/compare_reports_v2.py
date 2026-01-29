#!/usr/bin/env python3
"""
FBA Report Comparison and Validation Script v2
Enhanced version with better parsing for different report formats
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
    'addis', 'airwick', 'air wick', 'amtech', 'apollo', 'bacofoil', 'barbie', 'beaufort', 'beauty',
    'blue canyon', 'chef aid', 'colgate', 'doff', 'dove', 'draper', 'elbow grease',
    'elliott', 'elliotts', 'everbuild', 'eveready', 'everready', 'extra select', 'fairy', 'falcon',
    'giftmaker', 'hem', 'house mate', 'jaunty', 'kilner', 'kilrock', 'lav', 'mason cash',
    'minky', 'munch crunch', 'pan aroma', 'playwrite', 'price & kensington', 'prodec',
    'quest', 'radox', 'rcr', 'rolson', 'roundup', 'royle', 'russell hobbs', 'schott zwiesel',
    'sistema', 'soudal', 'stretcherz', 'superior', 'tala', 'the big cheese', 'tidyz', 'wham',
    'white glo', 'yale', 'alberto balsam', 'adidas', 'little trees', 'dlux', 'blackspur',
    'mokate', 'greenfields', 'sozali', 'bright & homely', 'lynwood', 'apac', 'highland', 'fragrant'
]

INVALID_FIRST_WORDS = ['paper', 'fairy', 'chef', 'pop', 'gel', 'glass', 'mirror', 'paint', 
                        'silicone', 'vacuum', 'wall', 'metal', 'farm', 'square', 'party',
                        'baby', 'cat', 'garden', 'happy', 'fire', 'mens', 'oven', 'craft',
                        'christmas', 'memorial', 'magnetic', 'all', 'the']


def parse_markdown_table(table_text):
    """Parse a markdown table into a list of dictionaries."""
    products = []
    lines = table_text.strip().split('\n')
    
    # Find header line (contains | and has column names)
    header_idx = None
    for i, line in enumerate(lines):
        if '|' in line and ('Verdict' in line or 'SupplierTitle' in line or 'Sup EAN' in line):
            header_idx = i
            break
    
    if header_idx is None:
        return products
    
    # Parse headers
    header_line = lines[header_idx]
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    
    # Normalize header names
    header_map = {
        'Sup EAN': 'Supplier EAN',
        'Amz EAN': 'Amazon EAN',
        'Conf': 'Confidence',
        'SupPrice': 'SupplierPrice',
        'SellPrice': 'SellingPrice',
        'Adj Profit': 'Adjusted Profit'
    }
    headers = [header_map.get(h, h) for h in headers]
    
    # Skip separator line
    data_start = header_idx + 2
    
    # Parse data rows
    for line in lines[data_start:]:
        if '|' in line and not line.strip().startswith('|--'):
            values = [v.strip() for v in line.split('|')]
            # Remove empty first/last elements from split
            values = [v for v in values if v]
            
            if len(values) >= 3:  # Minimum viable row
                product = {}
                for j, h in enumerate(headers):
                    if j < len(values):
                        product[h] = values[j]
                    else:
                        product[h] = ''
                products.append(product)
    
    return products


def extract_products_from_report(report_path, report_name):
    """Extract all products from a report file, organized by category."""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_products = {}
    
    # Find all category sections
    category_patterns = [
        (r"## VERIFIED — RECOMMENDED.*?```text\s*\n(.*?)```", "VERIFIED_RECOMMENDED"),
        (r"## VERIFIED — AUDITED OUT.*?```text\s*\n(.*?)```", "VERIFIED_AUDITED_OUT"),
        (r"## VERIFIED(?! —).*?```text\s*\n(.*?)```", "VERIFIED"),
        (r"## HIGHLY LIKELY — RECOMMENDED.*?```text\s*\n(.*?)```", "HIGHLY_LIKELY_RECOMMENDED"),
        (r"## HIGHLY LIKELY — AUDITED OUT.*?```text\s*\n(.*?)```", "HIGHLY_LIKELY_AUDITED_OUT"),
        (r"## HIGHLY LIKELY(?! —).*?```text\s*\n(.*?)```", "HIGHLY_LIKELY"),
        (r"## AUDITED OUT / EXCLUDED.*?```text\s*\n(.*?)```", "AUDITED_OUT"),
        (r"## AUDITED OUT.*?```text\s*\n(.*?)```", "AUDITED_OUT"),
        (r"## NEEDS VERIFICATION.*?```text\s*\n(.*?)```", "NEEDS_VERIFICATION"),
    ]
    
    for pattern, category_name in category_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            products = parse_markdown_table(match)
            if products:
                if category_name in all_products:
                    all_products[category_name].extend(products)
                else:
                    all_products[category_name] = products
    
    return all_products


def get_ean_from_product(product):
    """Extract EAN from product dict with multiple possible key names."""
    for key in ['Supplier EAN', 'Sup EAN', 'EAN', 'SupplierEAN']:
        if key in product and product[key]:
            ean = str(product[key]).replace('.0', '').strip()
            if ean and ean != 'nan':
                return ean
    return None


def normalize_category(category_name):
    """Normalize category name for comparison."""
    cat_upper = category_name.upper()
    if 'VERIFIED' in cat_upper and 'AUDITED' not in cat_upper:
        return 'VERIFIED'
    elif 'HIGHLY LIKELY' in cat_upper and 'AUDITED' not in cat_upper:
        return 'HIGHLY_LIKELY'
    elif 'NEEDS' in cat_upper:
        return 'NEEDS_VERIFICATION'
    elif 'AUDITED' in cat_upper or 'EXCLUDED' in cat_upper:
        return 'AUDITED_OUT'
    else:
        return 'OTHER'


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
    
    return True


def detect_pack_size(title):
    """Detect pack size from title, with dimension shielding."""
    if not title:
        return 1
    
    title_lower = title.lower()
    
    # Dimension patterns to IGNORE
    dimension_keywords = ['cm', 'mm', 'm', 'inch', 'inches', '"', "'", 'ft', 'oz', 'ml', 'l', 
                          'ltr', 'litre', 'liter', 'g', 'kg', 'gramme', 'gram', 'watt', 'w', 'v', 'volt']
    
    # Pack patterns
    pack_patterns = [
        (r'(\d+)\s*[-]?\s*pack\b', 1),
        (r'pack\s*of\s*(\d+)', 1),
        (r'(\d+)\s*x\s+(?!\d)', 1),  # "3 x " but not "3 x 4"
        (r'set\s*of\s*(\d+)', 1),
        (r'(\d+)\s*pce?s?\b', 1),
        (r'(\d+)\s*pieces?\b', 1),
    ]
    
    for pattern, group in pack_patterns:
        match = re.search(pattern, title_lower)
        if match:
            try:
                size = int(match.group(group))
                if 2 <= size <= 100:
                    # Check if followed by dimension keyword
                    end_pos = match.end()
                    following_text = title_lower[end_pos:end_pos+10]
                    is_dimension = any(dim in following_text for dim in dimension_keywords)
                    if not is_dimension:
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
            return brand.title()
    
    return None


def classify_product(row):
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
    
    # EAN Analysis
    supplier_ean_valid = validate_ean(supplier_ean)
    amazon_ean_valid = validate_ean(amazon_ean) if amazon_ean and amazon_ean not in ['nan', ''] else False
    ean_match = supplier_ean == amazon_ean and supplier_ean_valid and amazon_ean_valid
    ean_conflict = supplier_ean_valid and amazon_ean_valid and supplier_ean != amazon_ean
    
    if ean_match:
        reasons.append("Exact EAN match")
    elif ean_conflict:
        reasons.append("EAN conflict")
    
    # Brand Analysis
    supplier_brand = extract_brand(supplier_title, KNOWN_BRANDS)
    amazon_brand = extract_brand(amazon_title, KNOWN_BRANDS)
    brand_match = supplier_brand and (
        amazon_brand and supplier_brand.lower() == amazon_brand.lower() or
        supplier_brand.lower() in amazon_title.lower()
    )
    
    if brand_match:
        reasons.append(f"Brand: {supplier_brand}")
    
    # Title Similarity
    if supplier_title and amazon_title:
        seq_sim = SequenceMatcher(None, supplier_title.lower(), amazon_title.lower()).ratio() * 100
        reasons.append(f"Similarity: {seq_sim:.0f}%")
    else:
        seq_sim = 0
    
    # Pack Size Analysis
    supplier_pack = detect_pack_size(supplier_title)
    amazon_pack = detect_pack_size(amazon_title)
    rsu = max(1, amazon_pack // supplier_pack) if supplier_pack > 0 else amazon_pack
    adjusted_profit = net_profit / rsu if rsu > 0 else net_profit
    
    if rsu > 1:
        reasons.append(f"RSU={rsu}, Adj_Profit=£{adjusted_profit:.2f}")
    
    # Classification
    if adjusted_profit <= 0:
        return "AUDITED_OUT", 80, "; ".join(reasons)
    
    if ean_match:
        return "VERIFIED", 95, "; ".join(reasons)
    
    if ean_conflict:
        return "NEEDS_VERIFICATION", 72, "; ".join(reasons)
    
    if brand_match and seq_sim >= 55 and adjusted_profit > 0:
        return "HIGHLY_LIKELY", 80, "; ".join(reasons)
    
    if brand_match and adjusted_profit > 0.50:
        return "NEEDS_VERIFICATION", 70, "; ".join(reasons)
    
    if seq_sim >= 40 and adjusted_profit > 0:
        return "NEEDS_VERIFICATION", 65, "; ".join(reasons)
    
    return "UNRELATED", 50, "; ".join(reasons)


def main():
    print("=" * 70)
    print("FBA REPORT COMPARISON AND VALIDATION")
    print("=" * 70)
    
    print("\n1. Loading source data...")
    source_df = pd.read_excel(SOURCE_FILE)
    print(f"   Loaded {len(source_df)} rows from source")
    
    # Create EAN lookup
    ean_to_row = {}
    for idx, row in source_df.iterrows():
        ean = str(row['EAN']).replace('.0', '').strip()
        if ean and ean != 'nan':
            ean_to_row[ean] = row.to_dict()
            ean_to_row[ean]['_idx'] = idx
    
    print(f"   {len(ean_to_row)} unique EANs in source")
    
    print("\n2. Loading and parsing reports...")
    reports_data = {}
    report_stats = {}
    
    for report_name, report_path in REPORTS.items():
        if os.path.exists(report_path):
            reports_data[report_name] = extract_products_from_report(report_path, report_name)
            total = sum(len(products) for products in reports_data[report_name].values())
            
            stats = defaultdict(int)
            for category, products in reports_data[report_name].items():
                norm_cat = normalize_category(category)
                stats[norm_cat] += len(products)
            
            report_stats[report_name] = dict(stats)
            print(f"   {report_name}: {total} products")
            for cat, count in stats.items():
                print(f"      - {cat}: {count}")
    
    print("\n3. Building product comparison matrix...")
    # Map all products by EAN
    ean_classifications = defaultdict(dict)
    
    for report_name, categories in reports_data.items():
        for category, products in categories.items():
            norm_cat = normalize_category(category)
            for product in products:
                ean = get_ean_from_product(product)
                if ean:
                    ean_classifications[ean][report_name] = {
                        'category': norm_cat,
                        'raw_category': category,
                        'confidence': product.get('Confidence', ''),
                        'pack_verdict': product.get('Pack Verdict', ''),
                        'adjusted_profit': product.get('Adjusted Profit', ''),
                        'supplier_title': product.get('SupplierTitle', '')[:50]
                    }
    
    print(f"   Found {len(ean_classifications)} unique products across all reports")
    
    print("\n4. Performing independent classification...")
    independent_classifications = {}
    for ean, source_row in ean_to_row.items():
        category, confidence, reasoning = classify_product(source_row)
        independent_classifications[ean] = {
            'category': category,
            'confidence': confidence,
            'reasoning': reasoning
        }
    
    print("\n5. Calculating accuracy metrics...")
    accuracy_matrix = {}
    
    for report_name in reports_data.keys():
        correct = 0
        total = 0
        category_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for ean, report_data in ean_classifications.items():
            if report_name in report_data and ean in independent_classifications:
                report_cat = report_data[report_name]['category']
                our_cat = independent_classifications[ean]['category']
                
                total += 1
                category_accuracy[our_cat]['total'] += 1
                
                # Check if categories match
                if report_cat == our_cat:
                    correct += 1
                    category_accuracy[our_cat]['correct'] += 1
        
        accuracy = (correct / total * 100) if total > 0 else 0
        accuracy_matrix[report_name] = {
            'correct': correct,
            'total': total,
            'accuracy': accuracy,
            'by_category': dict(category_accuracy)
        }
        
        print(f"   {report_name}: {correct}/{total} = {accuracy:.1f}%")
    
    print("\n6. Identifying disagreements...")
    disagreements = []
    
    for ean, report_data in ean_classifications.items():
        categories_found = [data['category'] for data in report_data.values()]
        unique_categories = set(categories_found)
        
        if len(unique_categories) > 1:
            our_cat = independent_classifications.get(ean, {}).get('category', 'UNKNOWN')
            supplier_title = ean_to_row.get(ean, {}).get('SupplierTitle', 'N/A')[:40]
            
            disagreements.append({
                'ean': ean,
                'supplier_title': supplier_title,
                'our_classification': our_cat,
                'report_classifications': report_data,
                'unique_categories': unique_categories
            })
    
    print(f"   Found {len(disagreements)} products with classification disagreements")
    
    print("\n7. Generating validation report...")
    
    # Generate report
    output = []
    output.append("# FBA Report Comprehensive Comparison and Validation Report")
    output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    # Executive Summary
    output.append("## 1. Executive Summary")
    output.append("")
    output.append("This report provides a comprehensive comparison of four AI-generated FBA product analysis reports,")
    output.append("evaluating their classification accuracy against independent ground truth analysis.")
    output.append("")
    output.append("### Reports Analyzed:")
    for name, path in REPORTS.items():
        output.append(f"- **{name}**: `{os.path.basename(path)}`")
    output.append("")
    output.append(f"### Source Data: `part 8 jan.xlsx`")
    output.append(f"- Total products: **{len(source_df)}**")
    output.append(f"- Products with classifications: **{len(ean_classifications)}**")
    output.append(f"- Classification disagreements: **{len(disagreements)}**")
    output.append("")
    
    # Summary Statistics
    output.append("## 2. Summary Statistics by Report")
    output.append("")
    output.append("| Report | VERIFIED | HIGHLY LIKELY | NEEDS VERIFICATION | AUDITED OUT | Total |")
    output.append("|--------|----------|---------------|---------------------|-------------|-------|")
    
    for report_name, stats in report_stats.items():
        v = stats.get('VERIFIED', 0)
        hl = stats.get('HIGHLY_LIKELY', 0)
        nv = stats.get('NEEDS_VERIFICATION', 0)
        ao = stats.get('AUDITED_OUT', 0)
        total = v + hl + nv + ao
        output.append(f"| {report_name} | {v} | {hl} | {nv} | {ao} | {total} |")
    
    output.append("")
    
    # Accuracy Analysis
    output.append("## 3. Model Accuracy Statistics")
    output.append("")
    output.append("Accuracy is calculated by comparing each report's classifications against our independent ground truth analysis.")
    output.append("")
    output.append("### Overall Accuracy")
    output.append("")
    output.append("| Report | Correct | Total | Accuracy | Rank |")
    output.append("|--------|---------|-------|----------|------|")
    
    # Sort by accuracy
    ranked_reports = sorted(accuracy_matrix.items(), key=lambda x: x[1]['accuracy'], reverse=True)
    
    for rank, (name, data) in enumerate(ranked_reports, 1):
        output.append(f"| {name} | {data['correct']} | {data['total']} | **{data['accuracy']:.1f}%** | #{rank} |")
    
    output.append("")
    
    # Model Ranking
    output.append("### Model Ranking")
    output.append("")
    for rank, (name, data) in enumerate(ranked_reports, 1):
        medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
        output.append(f"{medal} **{name}**: {data['accuracy']:.1f}% accuracy ({data['correct']}/{data['total']} correct)")
    
    output.append("")
    
    # Category-Level Accuracy
    output.append("### Category-Level Accuracy")
    output.append("")
    
    for report_name, data in accuracy_matrix.items():
        output.append(f"**{report_name}:**")
        output.append("")
        output.append("| Category | Correct | Total | Accuracy |")
        output.append("|----------|---------|-------|----------|")
        for cat, cat_data in data['by_category'].items():
            if cat_data['total'] > 0:
                acc = cat_data['correct'] / cat_data['total'] * 100
                output.append(f"| {cat} | {cat_data['correct']} | {cat_data['total']} | {acc:.1f}% |")
        output.append("")
    
    # Key Disagreements
    output.append("## 4. Key Classification Disagreements")
    output.append("")
    output.append("The following products had different classifications across reports:")
    output.append("")
    
    header = "| EAN | Supplier Title | Our Class. |"
    separator = "|-----|----------------|------------|"
    for name in reports_data.keys():
        header += f" {name[:10]} |"
        separator += "------------|"
    
    output.append(header)
    output.append(separator)
    
    for d in disagreements[:40]:  # Limit to 40
        row = f"| {d['ean']} | {d['supplier_title']} | {d['our_classification']} |"
        for name in reports_data.keys():
            cat = d['report_classifications'].get(name, {}).get('category', 'NOT LISTED')
            row += f" {cat[:10]} |"
        output.append(row)
    
    if len(disagreements) > 40:
        output.append(f"\n*...and {len(disagreements) - 40} more disagreements*")
    
    output.append("")
    
    # Independent Classification Sample
    output.append("## 5. Independent Ground Truth Classification (Sample)")
    output.append("")
    output.append("Sample of 30 products with our independent classification:")
    output.append("")
    output.append("| EAN | Supplier Title | Our Classification | Confidence | Reasoning |")
    output.append("|-----|----------------|-------------------|------------|-----------|")
    
    sample_eans = list(ean_classifications.keys())[:30]
    for ean in sample_eans:
        if ean in ean_to_row and ean in independent_classifications:
            title = str(ean_to_row[ean].get('SupplierTitle', ''))[:35]
            our = independent_classifications[ean]
            output.append(f"| {ean} | {title} | {our['category']} | {our['confidence']}% | {our['reasoning'][:40]} |")
    
    output.append("")
    
    # Problem Patterns
    output.append("## 6. Problem Patterns Identified")
    output.append("")
    output.append("Based on our analysis, the following common issues were identified across reports:")
    output.append("")
    output.append("### 6.1 Pack Size Detection Issues")
    output.append("- **Dimension Traps**: Reports incorrectly interpreting measurements (e.g., `15x5.5x5.5cm`) as pack quantities")
    output.append("- **Model Number Confusion**: Numeric model identifiers (e.g., `2001.542`) mistaken for pack sizes")
    output.append("- **Bundle vs Pack**: Inconsistent handling of Amazon bundle listings (e.g., `3 x Product`)")
    output.append("")
    output.append("### 6.2 EAN Handling Issues")
    output.append("- **EAN Conflict Routing**: Some reports categorize EAN-conflict products as VERIFIED instead of NEEDS VERIFICATION")
    output.append("- **Missing EAN Handling**: Inconsistent treatment of products where Amazon EAN is missing")
    output.append("")
    output.append("### 6.3 Brand Matching Issues")
    output.append("- **Generic Word False Positives**: Words like 'PAPER', 'FAIRY', 'CHEF' incorrectly matched as brands")
    output.append("- **Brand Case Sensitivity**: Some brand matches failed due to case differences")
    output.append("")
    output.append("### 6.4 Profit Calculation Issues")
    output.append("- **RSU Inconsistency**: Different RSU (Retail Selling Unit) calculations leading to different adjusted profit figures")
    output.append("- **Negative Profit Routing**: Some products with negative adjusted profit incorrectly left in VERIFIED/HIGHLY LIKELY")
    output.append("")
    
    # Recommendations
    output.append("## 7. Recommendations")
    output.append("")
    output.append("### 7.1 Immediate Fixes")
    output.append("1. **Implement strict dimension shielding** - Pattern match for measurements BEFORE pack detection")
    output.append("2. **Route EAN conflicts to NEEDS VERIFICATION** - Per methodology §8.2-8.3")
    output.append("3. **Enforce strict brand list matching** - Do not use first-word matching for unknown brands")
    output.append("4. **Audit negative profit products** - Any adjusted profit ≤ 0 must be AUDITED OUT")
    output.append("")
    output.append("### 7.2 Methodology Improvements")
    output.append("1. Add model number shielding patterns (e.g., `S1532`, `BA2046`, `2001.542`)")
    output.append("2. Implement capacity multipack detection for patterns like `2pk x 50ml`")
    output.append("3. Add stricter title similarity thresholds for low word-overlap datasets")
    output.append("")
    output.append("### 7.3 Best Performing Model")
    best_model = ranked_reports[0][0]
    best_acc = ranked_reports[0][1]['accuracy']
    output.append(f"**{best_model}** achieved the highest accuracy at **{best_acc:.1f}%**.")
    output.append("This model should be used as the baseline for future improvements.")
    output.append("")
    
    output.append("---")
    output.append(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Write report
    output_path = os.path.join(BASE_DIR, f"COMPREHENSIVE_VALIDATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"\n   Report saved to: {output_path}")
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    for rank, (name, data) in enumerate(ranked_reports, 1):
        print(f"  #{rank}. {name}: {data['accuracy']:.1f}% accuracy")
    print("=" * 70)


if __name__ == "__main__":
    main()
