"""
EAN Validation Tools for FBA Agent.

Implements strict barcode validation with checksum verification and left-padding.
Based on specifications from Main.txt and Manual guide.
"""

import re
from typing import Tuple, Optional


def clean_to_digits(value) -> str:
    """
    Clean a value to digits only.
    
    Handles:
    - NaN/None values
    - Scientific notation (treated as corrupted)
    - Whitespace and non-digit characters
    
    Args:
        value: Any value to clean
        
    Returns:
        String of digits only, or empty string if invalid
    """
    import pandas as pd
    
    if pd.isna(value):
        return ''
    
    s = str(value).strip()
    
    # Scientific notation indicates corrupted data
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    
    return re.sub(r'\D', '', s)


def gtin_checksum_ok(digits: str) -> bool:
    """
    Validate GTIN checksum for 8, 12, 13, or 14 digit barcodes.
    
    Uses standard GTIN checksum algorithm:
    - Reverse the body (all digits except check digit)
    - Multiply alternating digits by 3 and 1
    - Sum all results
    - Check digit should make total divisible by 10
    
    Args:
        digits: String of digits to validate
        
    Returns:
        True if checksum is valid, False otherwise
    """
    if not digits.isdigit():
        return False
    
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    
    body = digits[:-1]
    check = int(digits[-1])
    
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        # For GTIN: odd positions (from right) get multiplied by 3
        total += d * (3 if i % 2 == 1 else 1)
    
    calc = (10 - (total % 10)) % 10
    return calc == check


def normalize_ean(digits: str) -> str:
    """
    Normalize an EAN by attempting left-padding to valid GTIN length.
    
    If the input is already a valid GTIN, returns it unchanged.
    Otherwise, tries left-padding with zeros to 12, 13, or 14 digits
    and checks if the checksum passes.
    
    Args:
        digits: String of digits to normalize
        
    Returns:
        Normalized EAN string (possibly left-padded)
    """
    if not digits.isdigit():
        return digits
    
    # Already valid?
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    
    # Try left-padding
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    
    return digits


def is_strict_valid_barcode(digits: str) -> bool:
    """
    Check if a barcode is strictly valid.
    
    Criteria:
    - Digits only
    - Valid GTIN length (8, 12, 13, or 14) after normalization
    - Passes checksum validation
    - No suspicious trailing zeros (6+ zeros at end)
    
    Args:
        digits: String to validate
        
    Returns:
        True if barcode is strictly valid
    """
    if not isinstance(digits, str):
        return False
    
    if not digits.isdigit():
        return False
    
    normalized = normalize_ean(digits)
    
    if len(normalized) not in (8, 12, 13, 14):
        return False
    
    # Check for suspicious trailing zeros (likely corrupted data)
    if re.search(r'0{6,}$', normalized):
        return False
    
    return gtin_checksum_ok(normalized)


def check_ean_match(
    supplier_ean: str, 
    amazon_ean: str
) -> Tuple[bool, bool, bool, bool]:
    """
    Check EAN match between supplier and Amazon.
    
    Returns:
        Tuple of (
            supplier_valid: bool - supplier EAN is strictly valid
            amazon_valid: bool - amazon EAN is strictly valid
            is_exact_match: bool - both valid AND identical
            ean_present_amazon: bool - amazon EAN is present (even if invalid)
        )
    """
    # Clean and normalize
    supplier_digits = clean_to_digits(supplier_ean)
    amazon_digits = clean_to_digits(amazon_ean)
    
    # Check validity
    supplier_valid = is_strict_valid_barcode(supplier_digits)
    amazon_valid = is_strict_valid_barcode(amazon_digits)
    
    # Check if Amazon EAN is present (even if invalid)
    amazon_present = bool(amazon_digits and amazon_digits not in ['0', '-', 'nan', 'None'])
    
    # Exact match requires both valid AND identical (after normalization)
    is_exact_match = False
    if supplier_valid and amazon_valid:
        supplier_normalized = normalize_ean(supplier_digits)
        amazon_normalized = normalize_ean(amazon_digits)
        is_exact_match = supplier_normalized == amazon_normalized
    
    return supplier_valid, amazon_valid, is_exact_match, amazon_present


def format_ean_for_display(ean: str) -> str:
    """
    Format an EAN for display in tables.
    
    Args:
        ean: EAN string to format
        
    Returns:
        Formatted EAN or "-" if invalid/empty
    """
    digits = clean_to_digits(ean)
    
    if not digits or digits in ['0', 'nan', 'None']:
        return "-"
    
    if is_strict_valid_barcode(digits):
        return normalize_ean(digits)
    
    # Return as-is if not strictly valid but has content
    return digits if digits else "-"
