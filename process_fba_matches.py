#!/usr/bin/env python3
"""
MatchSense - Forensic e-commerce sourcing analyst
Processes FBA financial reports to identify true matches and profitable opportunities
"""

import csv
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import sys

def normalize_ean(ean: str) -> str:
    """Normalize EAN by removing whitespace and leading zeros"""
    if not ean or ean.strip() == '':
        return ''
    return ean.strip().lstrip('0')

def titles_match(supplier_title: str, amazon_title: str) -> Tuple[bool, int]:
    """
    Determine if two titles refer to the same product
    Returns: (is_match, confidence_score)
    """
    if not supplier_title or not amazon_title:
        return False, 0

    # Normalize titles
    s_title = supplier_title.lower().strip()
    a_title = amazon_title.lower().strip()

    # Extract key attributes
    s_brand = extract_brand(s_title)
    a_brand = extract_brand(a_title)

    s_product = extract_product_type(s_title)
    a_product = extract_product_type(a_title)

    s_quantity = extract_quantity(s_title)
    a_quantity = extract_quantity(a_title)

    s_color = extract_color(s_title)
    a_color = extract_color(a_title)

    s_size = extract_size(s_title)
    a_size = extract_size(a_title)

    # Calculate confidence score
    score = 0

    # Brand matching (30 points)
    if s_brand and a_brand:
        if s_brand == a_brand:
            score += 30
        elif brands_are_similar(s_brand, a_brand):
            score += 20
    elif s_brand or a_brand:
        # If only one has a brand, be more conservative
        score += 10

    # Product type matching (30 points)
    if s_product == a_product:
        score += 30
    elif product_types_similar(s_product, a_product):
        score += 20

    # Quantity matching (15 points)
    if s_quantity and a_quantity:
        if s_quantity == a_quantity:
            score += 15
        else:
            # Different quantities - likely not the same product
            return False, 0
    elif s_quantity or a_quantity:
        # If quantity mentioned in only one, still possible match
        score += 5

    # Color matching (10 points)
    if s_color and a_color:
        if s_color == a_color:
            score += 10
        else:
            # Different colors - likely different variants
            return False, 0

    # Size matching (10 points)
    if s_size and a_size:
        if s_size == a_size:
            score += 10
        else:
            # Different sizes - different products
            return False, 0

    # Title similarity bonus (5 points)
    similarity = calculate_string_similarity(s_title, a_title)
    if similarity > 0.7:
        score += min(5, int((similarity - 0.7) * 25))

    # Conservative threshold: must be at least 60 to be considered a match
    is_match = score >= 60

    return is_match, min(score, 100)

def extract_brand(title: str) -> str:
    """Extract brand from title"""
    # Common brand patterns
    brand_patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Title Case words
    ]

    words = title.split()
    if words:
        # First word is often the brand
        first_word = words[0]
        if len(first_word) > 2 and not first_word.isdigit():
            return first_word

    return ''

def extract_product_type(title: str) -> str:
    """Extract main product type"""
    # Common product types
    product_keywords = [
        'blanket', 'socks', 'toy', 'ribbon', 'bib', 'basket', 'bowl', 'mug', 'tshirt', 't-shirt',
        'palm pal', 'tissue', 'book', 'tray', 'cushion', 'hat', 'box', 'bag', 'bottle', 'brush',
        'headband', 'teether', 'rattle', 'plush', 'soft toy', 'puppet', 'balloon', 'candle',
        'garland', 'pens', 'pen', 'craft', 'art set', 'puzzle', 'game', 'bowl', 'plate', 'cup'
    ]

    title_lower = title.lower()
    for keyword in product_keywords:
        if keyword in title_lower:
            return keyword

    return 'general'

def extract_quantity(title: str) -> int:
    """Extract pack quantity from title"""
    # Look for patterns like "pack of 6", "3 pack", "6x", "(6)", etc.
    patterns = [
        r'(?:pack\s+of\s+|pack\s+|x\s*)(\d+)',
        r'(\d+)\s*(?:pack|pc|piece|pieces)',
        r'\((\d+)\)',
        r'(\d+)\s*x\s*(?:pack|pcs?|pieces?)',
    ]

    for pattern in patterns:
        match = re.search(pattern, title.lower())
        if match:
            try:
                return int(match.group(1))
            except:
                pass

    return 1  # Default to 1 if not specified

def extract_color(title: str) -> str:
    """Extract color from title"""
    colors = ['red', 'blue', 'green', 'yellow', 'pink', 'purple', 'orange', 'white', 'black',
              'grey', 'gray', 'brown', 'navy', 'cream', 'beige', 'gold', 'silver', 'rose', 'burgundy',
              'teal', 'turquoise', 'lilac', 'mint', 'coral', 'peach', 'ivory', 'khaki', 'maroon']

    title_lower = title.lower()
    for color in colors:
        if color in title_lower:
            return color

    return ''

def extract_size(title: str) -> str:
    """Extract size/dimensions from title"""
    # Look for patterns like "15cm", "6 inch", "75x100cm", etc.
    patterns = [
        r'\b(\d+(?:\.\d+)?)\s*(?:cm|mm|inch|in|m)\b',
        r'\b(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(?:cm|mm|inch|in|m)?\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, title.lower())
        if match:
            return match.group(0)

    return ''

def brands_are_similar(brand1: str, brand2: str) -> bool:
    """Check if two brands are similar enough to be considered the same"""
    # Handle common variations
    similar_brands = [
        ('aurora', 'aurora world'),
        ('disney', 'disney/marvel'),
        ('lego', 'lego group'),
        ('mattel', 'mattel inc'),
        ('hasbro', 'hasbro toys'),
    ]

    b1, b2 = brand1.lower(), brand2.lower()

    if b1 == b2:
        return True

    for group1, group2 in similar_brands:
        if (b1 == group1 and b2 == group2) or (b1 == group2 and b2 == group1):
            return True

    # Check for substrings
    if b1 in b2 or b2 in b1:
        return True

    return False

def product_types_similar(type1: str, type2: str) -> bool:
    """Check if two product types are similar"""
    if type1 == type2:
        return True

    # Handle synonyms
    similar_pairs = [
        ('socks', 'sock'),
        ('tshirt', 't-shirt'),
        ('blanket', 'throw'),
        ('toy', 'soft toy', 'plush'),
        ('palm pal', 'soft toy', 'plush'),
        ('ribbon', 'satin ribbon'),
        ('bib', 'feeding bib'),
    ]

    for group in similar_pairs:
        if isinstance(group, tuple):
            if type1 in group and type2 in group:
                return True
        else:
            if type1 == group or type2 == group:
                # Single item check
                if type1 in type2 or type2 in type1:
                    return True

    return False

def calculate_string_similarity(s1: str, s2: str) -> float:
    """Calculate Jaccard similarity between two strings"""
    # Simple token-based similarity
    s1_tokens = set(s1.split())
    s2_tokens = set(s2.split())

    if not s1_tokens or not s2_tokens:
        return 0.0

    intersection = s1_tokens.intersection(s2_tokens)
    union = s1_tokens.union(s2_tokens)

    return len(intersection) / len(union)

def process_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single row and determine match type and score"""
    # Extract values
    ean = normalize_ean(row.get('EAN', ''))
    ean_on_page = normalize_ean(row.get('EAN_OnPage', ''))
    net_profit_str = row.get('NetProfit', '').strip()

    # Parse NetProfit
    try:
        net_profit = float(net_profit_str)
    except:
        # Try to compute if components available
        net_proceeds = row.get('NetProceeds', '').strip()
        supplier_price_ex = row.get('SupplierPrice_exVAT', '').strip()

        try:
            net_profit = float(net_proceeds) - float(supplier_price_ex)
        except:
            net_profit = None

    # Skip if NetProfit unavailable
    if net_profit is None:
        return None

    # Skip if NetProfit <= 1
    if net_profit <= 1:
        return None

    # Check for EAN match
    if ean and ean_on_page and ean == ean_on_page:
        # Check for glaring contradictions in titles
        supplier_title = row.get('SupplierTitle', '')
        amazon_title = row.get('AmazonTitle', '')

        # Basic title sanity check
        if supplier_title and amazon_title:
            s_product = extract_product_type(supplier_title.lower())
            a_product = extract_product_type(amazon_title.lower())

            # If completely different product types, might be data error
            if s_product != 'general' and a_product != 'general' and s_product != a_product:
                # Check if they might still match
                if not product_types_similar(s_product, a_product):
                    # Very different products with same EAN - unlikely but include with warning
                    pass

        return {
            'row': row,
            'match_type': 'ean_match',
            'matching_score': 100,
            'net_profit': net_profit
        }

    # Try title-based matching
    supplier_title = row.get('SupplierTitle', '')
    amazon_title = row.get('AmazonTitle', '')

    if supplier_title and amazon_title:
        is_match, score = titles_match(supplier_title, amazon_title)

        if is_match and score >= 60:
            return {
                'row': row,
                'match_type': 'title_match',
                'matching_score': score,
                'net_profit': net_profit
            }

    # Not a match
    return None

def process_csv(input_file: str, output_file: str):
    """Main processing function"""
    ean_matches = []
    title_matches = []

    total_rows = 0
    processed_rows = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_rows += 1
            result = process_row(row)

            if result:
                processed_rows += 1
                if result['match_type'] == 'ean_match':
                    ean_matches.append(result)
                else:
                    title_matches.append(result)

    # Sort title matches by score (descending)
    title_matches.sort(key=lambda x: x['matching_score'], reverse=True)

    # Write output markdown
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("## FBA Product Analysis - MatchSense Report\n\n")

        # Section 1: EAN Matches
        f.write("### 1. Exact matches by EAN (NetProfit > 1)\n\n")

        if ean_matches:
            f.write("| EAN | EAN_OnPage | ASIN | SupplierTitle | AmazonTitle | SupplierPrice_exVAT | NetProfit | ROI | bought_in_past_month | match_type | matching_score |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")

            for match in ean_matches:
                row = match['row']
                f.write(f"| {row.get('EAN', '')} | {row.get('EAN_OnPage', '')} | {row.get('ASIN', '')} | ")
                f.write(f"{row.get('SupplierTitle', '')[:50]} | {row.get('AmazonTitle', '')[:50]} | ")
                f.write(f"{row.get('SupplierPrice_exVAT', '')} | {match['net_profit']:.2f} | ")
                f.write(f"{row.get('ROI', '')} | {row.get('bought_in_past_month', '')} | ")
                f.write(f"{match['match_type']} | {match['matching_score']} |\n")
        else:
            f.write("_No exact EAN matches found with NetProfit > 1_\n\n")

        # Section 2: Title Matches
        f.write("\n### 2. Title-based matches (NetProfit > 1)\n\n")

        if title_matches:
            f.write("| EAN | ASIN | SupplierTitle | AmazonTitle | SupplierPrice_exVAT | NetProfit | ROI | bought_in_past_month | match_type | matching_score |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|\n")

            for match in title_matches:
                row = match['row']
                f.write(f"| {row.get('EAN', '')} | {row.get('ASIN', '')} | ")
                f.write(f"{row.get('SupplierTitle', '')[:50]} | {row.get('AmazonTitle', '')[:50]} | ")
                f.write(f"{row.get('SupplierPrice_exVAT', '')} | {match['net_profit']:.2f} | ")
                f.write(f"{row.get('ROI', '')} | {row.get('bought_in_past_month', '')} | ")
                f.write(f"{match['match_type']} | {match['matching_score']} |\n")
        else:
            f.write("_No title-based matches found with NetProfit > 1_\n\n")

        # Summary
        f.write("\n### Summary\n\n")
        f.write(f"- **Total rows processed**: {total_rows}\n")
        f.write(f"- **Rows with NetProfit > 1**: {processed_rows}\n")
        f.write(f"- **Exact EAN matches**: {len(ean_matches)}\n")
        f.write(f"- **Title-based matches**: {len(title_matches)}\n")

        if title_matches:
            avg_score = sum(m['matching_score'] for m in title_matches) / len(title_matches)
            f.write(f"- **Average title match score**: {avg_score:.1f}\n")

        f.write(f"- **Overall match rate**: {(processed_rows/total_rows)*100:.1f}%\n")

    print(f"Processing complete!")
    print(f"Total rows: {total_rows}")
    print(f"EAN matches: {len(ean_matches)}")
    print(f"Title matches: {len(title_matches)}")

if __name__ == "__main__":
    input_file = "C:\\Users\\chris\\Desktop\\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\\RESERACH\\fba_financial_report_20251205_050200.csv"
    output_file = "C:\\Users\\chris\\Desktop\\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\\RESERACH\\matchsense_analysis.md"

    process_csv(input_file, output_file)
    print(f"\nOutput written to: {output_file}")
