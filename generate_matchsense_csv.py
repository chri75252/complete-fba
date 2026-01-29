#!/usr/bin/env python3
"""
MatchSense CSV Generator
Creates a CSV file with filtered FBA matches (NetProfit > 1)
"""

import csv
import re
import sys

def normalize_ean(ean):
    if not ean or ean.strip() == '':
        return ''
    return ean.strip().lstrip('0')

def extract_brand(title):
    if not title:
        return ''
    words = title.split()
    if words:
        first_word = words[0]
        if len(first_word) > 2 and first_word[0].isupper():
            return first_word
    return ''

def extract_product_type(title):
    if not title:
        return 'general'
    product_keywords = {
        'socks': ['socks', 'sock', 'tights'],
        'toy': ['toy', 'soft toy', 'plush', 'palm pal', 'puppet'],
        'ribbon': ['ribbon', 'satin ribbon'],
        'bib': ['bib', 'feeding bib'],
        'basket': ['basket', 'trug', 'tray'],
        'tissue': ['tissue', 'tissue paper'],
        'blanket': ['blanket', 'throw'],
        'bottle': ['bottle'],
        'mug': ['mug'],
        'book': ['book', 'notebook'],
        'pen': ['pen', 'pens'],
        'garland': ['garland'],
        'candle': ['candle'],
        'balloon': ['balloon'],
        'headband': ['headband'],
        'teether': ['teether', 'rattle'],
        'puzzle': ['puzzle'],
        'game': ['game'],
        'brush': ['brush'],
    }
    title_lower = title.lower()
    for product_type, keywords in product_keywords.items():
        for keyword in keywords:
            if keyword in title_lower:
                return product_type
    return 'general'

def extract_quantity(title):
    if not title:
        return 1
    patterns = [
        r'(?:pack\s+of\s+|pack\s+|x\s*|pcs\s*)(\d+)',
        r'(\d+)\s*(?:pack|pc|piece|pieces|pairs|pair)',
        r'\((\d+)\)',
        r'(\d+)\s*x\s*(?:pack|pcs?|pieces?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, title.lower(), re.IGNORECASE)
        if match:
            try:
                qty = int(match.group(1))
                return qty if qty > 0 else 1
            except:
                pass
    return 1

def extract_color(title):
    if not title:
        return ''
    colors = ['red', 'blue', 'green', 'yellow', 'pink', 'purple', 'orange', 'white',
              'black', 'grey', 'gray', 'brown', 'navy', 'cream', 'beige', 'gold',
              'silver', 'rose', 'burgundy', 'teal', 'turquoise', 'lilac', 'coral',
              'peach', 'ivory', 'khaki', 'maroon', 'emerald', 'shocking pink',
              'baby pink', 'sky blue', 'royal blue', 'pale pink', 'light blue']
    title_lower = title.lower()
    for color in colors:
        if color in title_lower:
            return color
    return ''

def extract_size(title):
    if not title:
        return ''
    patterns = [
        r'\b(\d+(?:\.\d+)?)\s*(?:cm|mm|inch|in)(?:\s*x\s*\d+(?:\.\d+)?\s*(?:cm|mm|inch|in)?)?\b',
        r'\((\d+(?:\.\d+)?\s*(?:cm|mm|inch|in))\)',
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1)
    return ''

def brands_are_similar(brand1, brand2):
    if not brand1 or not brand2:
        return False
    b1, b2 = brand1.lower(), brand2.lower()
    if b1 == b2:
        return True
    if b1 in b2 or b2 in b1:
        return True
    similar_mappings = [
        ('aurora', 'aurora world'),
        ('disney', 'disney/marvel'),
        ('lego', 'lego group'),
        ('mattel', 'mattel inc'),
        ('hasbro', 'hasbro toys'),
    ]
    for base, variant in similar_mappings:
        if (b1 == base and b2 == variant) or (b1 == variant and b2 == base):
            return True
    return False

def product_types_similar(type1, type2):
    if type1 == type2:
        return True
    synonym_groups = [
        ['socks', 'sock', 'tights'],
        ['toy', 'soft toy', 'plush', 'palm pal'],
        ['ribbon', 'satin ribbon'],
        ['bib', 'feeding bib'],
        ['basket', 'trug', 'tray', 'basket with handle'],
    ]
    for group in synonym_groups:
        if type1 in group and type2 in group:
            return True
    return False

def calculate_string_similarity(s1, s2):
    if not s1 or not s2:
        return 0.0
    s1_tokens = set(s1.split())
    s2_tokens = set(s2.split())
    if not s1_tokens or not s2_tokens:
        return 0.0
    intersection = s1_tokens.intersection(s2_tokens)
    union = s1_tokens.union(s2_tokens)
    return len(intersection) / len(union)

def titles_match(supplier_title, amazon_title):
    if not supplier_title or not amazon_title:
        return False, 0, "Missing title"
    s_title = supplier_title.lower().strip()
    a_title = amazon_title.lower().strip()
    reasoning_parts = []
    score = 0
    if s_title == a_title:
        return True, 100, "Exact title match"
    s_brand = extract_brand(s_title)
    a_brand = extract_brand(a_title)
    brand_match = False
    if s_brand and a_brand:
        if s_brand == a_brand:
            score += 30
            brand_match = True
            reasoning_parts.append("Brand match")
        elif brands_are_similar(s_brand, a_brand):
            score += 20
            reasoning_parts.append("Similar brands")
    s_product = extract_product_type(s_title)
    a_product = extract_product_type(a_title)
    if s_product == a_product:
        score += 30
        reasoning_parts.append(f"Product type: {s_product}")
    elif product_types_similar(s_product, a_product):
        score += 20
        reasoning_parts.append(f"Similar products: {s_product}/{a_product}")
    else:
        return False, 0, f"Different product types: {s_product} vs {a_product}"
    s_qty = extract_quantity(s_title)
    a_qty = extract_quantity(a_title)
    if s_qty != a_qty:
        return False, 0, f"Different quantities: {s_qty} vs {a_qty}"
    elif s_qty > 1 or a_qty > 1:
        score += 15
        reasoning_parts.append(f"Qty: {s_qty}")
    s_color = extract_color(s_title)
    a_color = extract_color(a_title)
    if s_color and a_color and s_color != a_color:
        return False, 0, f"Different colors: {s_color} vs {a_color}"
    elif s_color or a_color:
        score += 10
        reasoning_parts.append(f"Color: {s_color or a_color}")
    s_size = extract_size(s_title)
    a_size = extract_size(a_title)
    if s_size and a_size and s_size != a_size:
        return False, 0, f"Different sizes: {s_size} vs {a_size}"
    elif s_size or a_size:
        score += 10
        reasoning_parts.append(f"Size: {s_size or a_size}")
    similarity = calculate_string_similarity(s_title, a_title)
    if similarity > 0.6:
        bonus = min(5, int(similarity * 5))
        score += bonus
        if bonus > 0:
            reasoning_parts.append(f"Similarity: {similarity:.2f}")
    is_match = score >= 60
    reasoning = ", ".join(reasoning_parts) if is_match else "Score below threshold"
    return is_match, min(score, 100), reasoning

def process_row(row):
    ean = normalize_ean(row.get('EAN', ''))
    ean_on_page = normalize_ean(row.get('EAN_OnPage', ''))
    net_profit = None
    try:
        net_profit_str = row.get('NetProfit', '').strip()
        if net_profit_str:
            net_profit = float(net_profit_str)
        else:
            net_proceeds = float(row.get('NetProceeds', 0))
            supplier_price_ex = float(row.get('SupplierPrice_exVAT', 0))
            net_profit = net_proceeds - supplier_price_ex
    except (ValueError, TypeError):
        return None
    if net_profit is None or net_profit <= 1:
        return None
    if ean and ean_on_page and ean == ean_on_page:
        supplier_title = row.get('SupplierTitle', '')
        amazon_title = row.get('AmazonTitle', '')
        if supplier_title and amazon_title:
            s_product = extract_product_type(supplier_title.lower())
            a_product = extract_product_type(amazon_title.lower())
            if s_product != 'general' and a_product != 'general' and s_product != a_product:
                if not product_types_similar(s_product, a_product):
                    pass
        return {
            'data': row,
            'match_type': 'EAN Match',
            'matching_score': 100,
            'net_profit': net_profit,
            'reasoning': 'Exact EAN match'
        }
    supplier_title = row.get('SupplierTitle', '')
    amazon_title = row.get('AmazonTitle', '')
    if supplier_title and amazon_title:
        is_match, score, reasoning = titles_match(supplier_title, amazon_title)
        if is_match and score >= 60:
            return {
                'data': row,
                'match_type': 'Title Match',
                'matching_score': score,
                'net_profit': net_profit,
                'reasoning': reasoning
            }
    return None

def main():
    input_file = "C:\\Users\\chris\\Desktop\\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\\RESERACH\\fba_financial_report_20251205_050200.csv"
    output_file = "C:\\Users\\chris\\Desktop\\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\\RESERACH\\matchsense_matches.csv"

    matches = []
    total_rows = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            result = process_row(row)
            if result:
                matches.append(result)

    # Sort: EAN matches first, then title matches by score
    ean_matches = [m for m in matches if m['match_type'] == 'EAN Match']
    title_matches = [m for m in matches if m['match_type'] == 'Title Match']
    title_matches.sort(key=lambda x: x['matching_score'], reverse=True)
    sorted_matches = ean_matches + title_matches

    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if sorted_matches:
            # Get fieldnames from first row
            fieldnames = list(sorted_matches[0]['data'].keys()) + ['match_type', 'matching_score', 'match_reasoning']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for match in sorted_matches:
                row_data = match['data'].copy()
                row_data['match_type'] = match['match_type']
                row_data['matching_score'] = match['matching_score']
                row_data['match_reasoning'] = match['reasoning']
                writer.writerow(row_data)

    print(f"CSV file generated: {output_file}")
    print(f"Total rows processed: {total_rows}")
    print(f"Total matches found: {len(sorted_matches)}")
    print(f"EAN matches: {len(ean_matches)}")
    print(f"Title matches: {len(title_matches)}")

    if title_matches:
        avg_score = sum(m['matching_score'] for m in title_matches) / len(title_matches)
        print(f"Average title match score: {avg_score:.1f}")

    # Top 10 by profit
    print("\nTop 10 opportunities by NetProfit:")
    top_by_profit = sorted(sorted_matches, key=lambda x: x['net_profit'], reverse=True)[:10]
    for i, match in enumerate(top_by_profit, 1):
        title = match['data'].get('SupplierTitle', '')[:60]
        print(f"{i:2d}. NetProfit: £{match['net_profit']:.2f} | Score: {match['matching_score']:2d} | {title}")

    # Top 10 by score
    print("\nTop 10 opportunities by matching score:")
    top_by_score = sorted(sorted_matches, key=lambda x: x['matching_score'], reverse=True)[:10]
    for i, match in enumerate(top_by_score, 1):
        title = match['data'].get('SupplierTitle', '')[:60]
        print(f"{i:2d}. Score: {match['matching_score']:2d} | NetProfit: £{match['net_profit']:.2f} | {title}")

if __name__ == "__main__":
    main()
