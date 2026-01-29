"""
Title Parsing Tools for FBA Agent.

Extracts brand, product type, and variant information from product titles.
"""

import re
from typing import Optional, List, Set
from ..models.schemas import ParsedAttributes


# Common brand patterns - known FBA-friendly brands (from Main.txt)
KNOWN_BRANDS: Set[str] = {
    # Tool brands
    "amtech", "rolson", "draper", "silverline", "stanley", "dewalt",
    # Household brands
    "fairy", "dettol", "marigold", "febreze", "airwick", "air wick",
    "glade", "sc johnson", "mr muscle", "cillit bang", "vanish",
    # Kitchen brands
    "mason cash", "pyrex", "chef aid", "apollo", "apollo housewares",
    "kitchen craft", "tala", "ravenhead", "price kensington", "price & kensington",
    # DIY brands
    "everbuild", "soudal", "no nonsense", "evo-stik", "unibond",
    "polycell", "ronseal", "hammerite", "rustins",
    # Lighting brands
    "eveready", "everready", "energizer", "duracell", "status", "extrastar",
    # Garden brands
    "roundup", "miracle-gro", "westland", "levington",
    # Food/beverage
    "kilrock", "elbow grease", "little trees",
    # Others from methodology guide
    "tidyz", "superior", "phoods", "blue canyon", "schott zwiesel",
    "ultratape", "prima",
}


def extract_brand(title: str) -> Optional[str]:
    """
    Extract brand name from a product title.
    
    Checks against known brands first, then tries common patterns.
    
    Args:
        title: Product title to parse
        
    Returns:
        Extracted brand name or None
    """
    if not title:
        return None
    
    title_lower = title.lower().strip()
    
    # Check against known brands (anywhere in title)
    for brand in KNOWN_BRANDS:
        if brand in title_lower:
            # Return the properly cased version if found at start
            if title_lower.startswith(brand):
                return title[:len(brand)].strip()
            # Otherwise return as found
            return brand.title()
    
    # Try to extract first word(s) as brand (common pattern)
    # Look for all-caps words at start
    first_words = title.split()[:3]
    caps_brand = []
    for word in first_words:
        if word.isupper() and len(word) > 1 and word.isalpha():
            caps_brand.append(word)
        else:
            break
    
    if caps_brand:
        return " ".join(caps_brand)
    
    # Return first word as fallback
    if first_words:
        first = first_words[0].strip('()[]')
        if len(first) > 1 and first.isalpha():
            return first
    
    return None


def check_brand_match(supplier_brand: Optional[str], amazon_brand: Optional[str]) -> bool:
    """
    Check if two brand names match (case-insensitive).
    
    Args:
        supplier_brand: Brand from supplier title
        amazon_brand: Brand from Amazon title
        
    Returns:
        True if brands match
    """
    if not supplier_brand or not amazon_brand:
        return False
    
    # Normalize for comparison
    sup = supplier_brand.lower().strip()
    amz = amazon_brand.lower().strip()
    
    # Exact match
    if sup == amz:
        return True
    
    # Handle common variations
    variations = [
        ("everready", "eveready"),
        ("air wick", "airwick"),
        ("price kensington", "price & kensington"),
        ("price&kensington", "price & kensington"),
        ("apollo housewares", "apollo"),
    ]
    
    for var1, var2 in variations:
        if (sup == var1 and amz == var2) or (sup == var2 and amz == var1):
            return True
    
    # Check if one contains the other (for "AMTECH" vs "Amtech Tools")
    if sup in amz or amz in sup:
        return True
    
    return False


def extract_product_type(title: str) -> Optional[str]:
    """
    Extract core product type from title.
    
    Args:
        title: Product title
        
    Returns:
        Product type string or None
    """
    if not title:
        return None
    
    title_lower = title.lower()
    
    # Common product types to detect
    product_types = [
        # Tools
        "hammer", "trowel", "screwdriver", "pliers", "wrench", "spanner",
        "saw", "drill", "chisel", "level", "tape measure", "torch", "flashlight",
        # Kitchen
        "bowl", "dish", "plate", "cup", "mug", "glass", "jar", "bottle",
        "pot", "pan", "tray", "container", "lid", "brush", "sponge",
        "shaker", "grinder", "mill", "timer", "scale",
        # Cleaning
        "cleaner", "spray", "wipes", "mop", "bucket", "gloves",
        "detergent", "powder", "liquid", "gel",
        # Home
        "candle", "air freshener", "diffuser", "plug-in",
        "light", "bulb", "lamp", "tube", "led",
        "tape", "adhesive", "glue", "sealant", "foam",
        # Food storage
        "bags", "doyleys", "foil", "cling film", "food wrap",
    ]
    
    for ptype in product_types:
        if ptype in title_lower:
            return ptype
    
    # Try to extract noun after brand
    words = title_lower.split()
    if len(words) >= 2:
        # Skip known brands, return next significant word
        for i, word in enumerate(words):
            if word not in KNOWN_BRANDS and len(word) > 3:
                return word
    
    return None


def check_product_type_match(supplier_type: Optional[str], amazon_type: Optional[str]) -> bool:
    """
    Check if product types match.
    
    Args:
        supplier_type: Product type from supplier title
        amazon_type: Product type from Amazon title
        
    Returns:
        True if product types match
    """
    if not supplier_type or not amazon_type:
        return False
    
    sup = supplier_type.lower().strip()
    amz = amazon_type.lower().strip()
    
    # Exact match
    if sup == amz:
        return True
    
    # Handle pluralization
    if sup.rstrip('s') == amz.rstrip('s'):
        return True
    
    # Handle synonyms
    synonyms = [
        ("torch", "flashlight"),
        ("light", "lamp"),
        ("dish", "bowl"),
        ("container", "tray"),
        ("bags", "bag"),
    ]
    
    for s1, s2 in synonyms:
        if (sup == s1 and amz == s2) or (sup == s2 and amz == s1):
            return True
    
    # Check containment
    if sup in amz or amz in sup:
        return True
    
    return False


def parse_title_attributes(title: str) -> ParsedAttributes:
    """
    Parse a product title into structured attributes.
    
    Args:
        title: Product title to parse
        
    Returns:
        ParsedAttributes with extracted information
    """
    from .pack_detection import extract_pack_count
    
    if not title:
        return ParsedAttributes(raw_title=title or "")
    
    brand = extract_brand(title)
    product_type = extract_product_type(title)
    pack_count, _ = extract_pack_count(title)
    
    # Extract size/capacity
    size_capacity = _extract_size_capacity(title)
    
    # Extract variant (color, scent, etc.)
    variant = _extract_variant(title)
    
    return ParsedAttributes(
        brand=brand,
        product_type=product_type,
        variant=variant,
        size_capacity=size_capacity,
        pack_count=pack_count,
        raw_title=title
    )


def _extract_size_capacity(title: str) -> Optional[str]:
    """Extract size/capacity information from title."""
    if not title:
        return None
    
    patterns = [
        r'(\d+(?:\.\d+)?\s*(?:ml|l|ltr|litre|liter))',  # Volume
        r'(\d+(?:\.\d+)?\s*(?:g|gm|kg|oz))',  # Weight
        r'(\d+(?:\.\d+)?\s*(?:cm|mm|m|inch|in|ft))',  # Length
        r'(\d+(?:\.\d+)?\s*(?:w|watt))',  # Wattage
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title.lower())
        if match:
            return match.group(1).strip()
    
    return None


def _extract_variant(title: str) -> Optional[str]:
    """Extract variant information (color, scent, model) from title."""
    if not title:
        return None
    
    title_lower = title.lower()
    
    # Colors
    colors = ["white", "black", "red", "blue", "green", "yellow", "cream",
              "chrome", "silver", "gold", "bronze", "navy", "clear", "transparent"]
    for color in colors:
        if color in title_lower:
            return color
    
    # Scents
    scents = ["lavender", "lemon", "eucalyptus", "fresh", "vanilla", 
              "ocean", "pine", "citrus", "floral"]
    for scent in scents:
        if scent in title_lower:
            return scent
    
    return None


def calculate_title_similarity(title1: str, title2: str) -> float:
    """
    Calculate similarity between two titles.
    
    Args:
        title1: First title
        title2: Second title
        
    Returns:
        Similarity score 0.0 to 1.0
    """
    from difflib import SequenceMatcher
    
    if not title1 or not title2:
        return 0.0
    
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
