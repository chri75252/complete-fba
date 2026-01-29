"""
Pack Detection Tools for FBA Agent.

Implements deterministic pack size detection with dimension/spec shields.
Based on specifications from Main.txt and Manual guide.
"""

import re
from typing import Tuple, List, Optional
from ..models.schemas import TrapDetection


# Dimension shield patterns - these are NEVER pack counts
DIMENSION_PATTERNS = [
    # Explicit dimensions with units
    r'\b(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*x?\s*(\d+(?:\.\d+)?)?\s*(cm|mm|inch|in|m)\b',  # L x W x H
    r'\b(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(cm|mm|inch|in)\b',  # L x W
    r'\b(\d+(?:\.\d+)?)\s*(cm|mm|inch|in|ft)\b',  # Single dimension
    r'\b(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|liter)\b',  # Capacity
    r'\b(\d+(?:\.\d+)?)\s*(g|gm|kg|oz)\b',  # Weight
    r'\b(\d+(?:\.\d+)?)\s*(w|watt|watts)\b',  # Wattage
    r'\b(\d+)\s*led\b',  # LED count (spec, not pack)
    r'\b(\d+)\s*k\b',  # Color temperature
]

# Spec-X shield patterns - features that look like packs but aren't
SPEC_X_PATTERNS = [
    r'\b(\d+)\s*x\s*(magnification|zoom|microscope|optical|power)\b',
    r'\b(magnification|zoom)\s*(\d+)\s*x\b',
    r'\b(\d+)x\s+(zoom|magnification)\b',
]

# Pack indicator patterns - these ARE pack counts
PACK_PATTERNS = [
    (r'pack\s+of\s+(\d+)', 'pack_of'),
    (r'set\s+of\s+(\d+)', 'set_of'),
    (r'\b(\d+)\s*pack\b', 'n_pack'),
    (r'\b(\d+)\s*pk\b', 'n_pk'),
    (r'(\d+)\s*pcs\b', 'n_pcs'),
    (r'(\d+)\s*pce\b', 'n_pce'),
    (r'(\d+)\s*pieces?\b', 'n_pieces'),
    (r'(\d+)\s*pairs?\b', 'n_pairs'),
    (r'\bx\s*(\d+)\b', 'x_n'),  # "x 10" at end
    (r'\((\d+)\s*pack\)', 'n_pack_parens'),
    (r'\(pack\s+of\s+(\d+)\)', 'pack_of_parens'),
    (r'\b(\d+)\s*rolls?\b', 'n_rolls'),
    (r'\b(\d+)\s*count\b', 'n_count'),
]

# Multipack patterns - "N x M" structure
MULTIPACK_PATTERN = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?'


def detect_dimension_trap(title: str, number: int) -> Optional[TrapDetection]:
    """
    Check if a number in the title is a dimension (not a pack count).
    
    Args:
        title: Product title to analyze
        number: The number to check
        
    Returns:
        TrapDetection if this is a dimension trap, None otherwise
    """
    title_lower = title.lower()
    
    for pattern in DIMENSION_PATTERNS:
        matches = re.findall(pattern, title_lower, re.IGNORECASE)
        for match in matches:
            # Check if our number appears in this dimension match
            if isinstance(match, tuple):
                if str(number) in [str(int(float(m))) for m in match if m and re.match(r'^\d+(?:\.\d+)?$', str(m))]:
                    return TrapDetection(
                        trap_type="dimension_trap",
                        pattern_matched=f"{match}",
                        action_taken="ignored_as_dimension"
                    )
            else:
                if str(number) == str(int(float(match))):
                    return TrapDetection(
                        trap_type="dimension_trap",
                        pattern_matched=match,
                        action_taken="ignored_as_dimension"
                    )
    
    return None


def detect_spec_x_trap(title: str, number: int) -> Optional[TrapDetection]:
    """
    Check if a number is a specification (like "2x magnification") not a pack count.
    
    Args:
        title: Product title to analyze
        number: The number to check
        
    Returns:
        TrapDetection if this is a spec-x trap, None otherwise
    """
    title_lower = title.lower()
    
    for pattern in SPEC_X_PATTERNS:
        matches = re.findall(pattern, title_lower, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                if str(number) in match:
                    return TrapDetection(
                        trap_type="spec_x",
                        pattern_matched=f"{match}",
                        action_taken="ignored_as_specification"
                    )
            else:
                if str(number) == match:
                    return TrapDetection(
                        trap_type="spec_x",
                        pattern_matched=match,
                        action_taken="ignored_as_specification"
                    )
    
    return None


def extract_pack_count(title: str) -> Tuple[int, List[TrapDetection]]:
    """
    Extract pack count from a product title.
    
    Implements dimension shield and spec-x shield to avoid false positives.
    
    Args:
        title: Product title to analyze
        
    Returns:
        Tuple of (pack_count, list of trap detections)
    """
    if not title:
        return 1, []
    
    title_lower = title.lower()
    traps_detected: List[TrapDetection] = []
    
    # Try each pack pattern
    for pattern, pattern_name in PACK_PATTERNS:
        match = re.search(pattern, title_lower)
        if match:
            number = int(match.group(1))
            
            # Sanity check: reject unrealistic pack counts
            if number < 1 or number > 500:
                continue
            
            # Check if this number is actually a dimension
            dim_trap = detect_dimension_trap(title, number)
            if dim_trap:
                traps_detected.append(dim_trap)
                continue
            
            # Check if this number is a specification
            spec_trap = detect_spec_x_trap(title, number)
            if spec_trap:
                traps_detected.append(spec_trap)
                continue
            
            # Valid pack count found
            return number, traps_detected
    
    # Default: single unit
    return 1, traps_detected


def extract_multipack_total(title: str) -> Tuple[int, int, int, List[TrapDetection]]:
    """
    Extract total items from multipack patterns like '(4 x 50)' or '3 x 500ml'.
    
    Per Main.txt: "(4 x 50)" means 4 packs of 50 = 200 total items
    Per Main.txt: "3 x 400ml" means 3 bottles of 400ml each (RSU = 3)
    
    Args:
        title: Product title to analyze
        
    Returns:
        Tuple of (outer_count, inner_count, total, trap_detections)
        - If no multipack: (1, pack_count, pack_count, traps)
        - If multipack with capacity: (N, 1, N, traps) - "3 x 400ml" means RSU=3
        - If multipack with quantity: (N, M, N*M, traps) - "(4 x 50)" means total=200
    """
    if not title:
        return 1, 1, 1, []
    
    title_lower = title.lower()
    traps_detected: List[TrapDetection] = []
    
    # First check for capacity multipack: "N x [capacity]ml/g/l"
    capacity_pattern = r'\b(\d+)\s*x\s*(\d+)\s*(ml|g|l|ltr|litre|oz|kg)\b'
    cap_match = re.search(capacity_pattern, title_lower)
    if cap_match:
        outer = int(cap_match.group(1))
        # This is NOT a quantity multiplication - outer is the RSU
        # "3 x 400ml" means 3 bottles, each 400ml
        if outer > 1 and outer <= 20:  # Reasonable multipack count
            traps_detected.append(TrapDetection(
                trap_type="capacity_multipack",
                pattern_matched=cap_match.group(0),
                action_taken="outer_is_rsu"
            ))
            return outer, 1, outer, traps_detected
    
    # Check for dimension patterns (should NOT trigger multipack)
    dim_pattern = r'\b(\d+)\s*x\s*(\d+)\s*(cm|mm|inch|in|m)\b'
    dim_match = re.search(dim_pattern, title_lower)
    if dim_match:
        traps_detected.append(TrapDetection(
            trap_type="dimension_trap",
            pattern_matched=dim_match.group(0),
            action_taken="ignored_as_dimension"
        ))
        # Fall through to standard pack extraction
    
    # Check for quantity multipack: "(N x M)" where M is quantity-inside
    qty_multipack = re.search(r'\((\d+)\s*x\s*(\d+)\)', title_lower)
    if qty_multipack:
        outer = int(qty_multipack.group(1))
        inner = int(qty_multipack.group(2))
        # "(4 x 50)" = 4 packs of 50 = 200 total
        if outer > 0 and inner > 0 and outer * inner <= 10000:
            total = outer * inner
            return outer, inner, total, traps_detected
    
    # Check for leading "N x" pattern: "3 x Product Name"
    leading_pattern = r'^(\d+)\s*x\s+\w'
    lead_match = re.search(leading_pattern, title_lower)
    if lead_match:
        outer = int(lead_match.group(1))
        if outer > 1 and outer <= 20:
            return outer, 1, outer, traps_detected
    
    # Check for "N x Product" pattern mid-title
    mid_pattern = r'\b(\d+)\s*x\s+(?!magnification|zoom|power|optical)'
    mid_match = re.search(mid_pattern, title_lower)
    if mid_match:
        outer = int(mid_match.group(1))
        # Verify this isn't a dimension
        dim_trap = detect_dimension_trap(title, outer)
        if dim_trap:
            traps_detected.append(dim_trap)
        elif outer > 1 and outer <= 20:
            return outer, 1, outer, traps_detected
    
    # Fallback to standard pack extraction
    pack_count, pack_traps = extract_pack_count(title)
    traps_detected.extend(pack_traps)
    
    return 1, pack_count, pack_count, traps_detected


def calculate_rsu(
    supplier_pack: int, 
    amazon_total: int
) -> float:
    """
    Calculate Required Supplier Units.
    
    RSU = How many supplier packs needed to fulfill one Amazon listing
    
    Args:
        supplier_pack: Pack count from supplier title
        amazon_total: Total items in Amazon listing
        
    Returns:
        RSU (float, minimum 1.0)
    """
    if supplier_pack <= 0:
        supplier_pack = 1
    
    rsu = amazon_total / supplier_pack
    return max(1.0, rsu)


def detect_quantity_inside_trap(title: str) -> Optional[TrapDetection]:
    """
    Detect "quantity inside" patterns like "STICKS 200" or "50 PCS".
    
    These describe items PER PACK, not number of packs.
    
    Args:
        title: Product title to analyze
        
    Returns:
        TrapDetection if quantity-inside pattern found
    """
    title_lower = title.lower()
    
    # Patterns where trailing numbers are quantity-inside
    qty_inside_patterns = [
        r'(sticks?|straws?|bags?|sheets?|wipes?|tabs?|tablets?|capsules?)\s+(\d+)\b',
        r'\b(\d+)\s+(sticks?|straws?|bags?|sheets?|wipes?|tabs?|tablets?|capsules?)\b',
    ]
    
    for pattern in qty_inside_patterns:
        match = re.search(pattern, title_lower)
        if match:
            return TrapDetection(
                trap_type="quantity_inside",
                pattern_matched=match.group(0),
                action_taken="treated_as_items_per_pack"
            )
    
    return None
