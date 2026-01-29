# =============================================================================
# SUPPLIER CALIBRATION CONFIGURATION
# Generated from: part_1_jan.xlsx
# Date: 2026-01-01
# 
# Copy this configuration block into your main analysis script.
# =============================================================================

# --- CALIBRATION CONFIGURATION for part_1_jan.xlsx ---
SUPPLIER_NAMING_CONVENTION = {
    # Pack quantity explicit unit keywords found in this supplier file
    # Detected: "2PC", "8PC", "12 PIECES", "5PACK", "PK6", "PK8", "100 CASES"
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces", "piece", "cases"],
    
    # Set FALSE - trailing numbers are rare in this file
    # Only 1 example: Row 18 "PARTY CRAZY BALLOONS ASSORTED 20"
    # Most ending numbers are dimensions (40CM, 30M) or model codes (SDB113)
    "allow_trailing_number_as_qty": False,
    
    # Set FALSE - no leading multiplier patterns (e.g., "10x Product") found
    "leading_multiplier_check": False,
    
    # Dimension/measurement keywords to SHIELD from quantity parsing
    # CRITICAL: These are physical measurements, NOT pack quantities
    # Examples: 70X100CM = bag dimensions, 5X60MM = screw size
    "dimension_shield_keywords": [
        "cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", 
        "inch", "in", "ft", "m", "w"  # meters, watts
    ],
    
    # Enable dimension X pattern shield
    # Patterns like "70X100CM" and "5X60MM" are dimensions, NOT N×M quantities
    "dimension_x_patterns": True,
    
    # Brand position in supplier titles
    # Mixed: Some start with brands (DLUX, PROKLEEN, PANASONIC)
    # Others start with descriptors (LUXURY, EASY, CHRISTMAS)
    "brand_position": "mixed",
    
    # Sales column configuration
    # Column: "bought_in_past_month"
    # Data type: int64 (already numeric)
    # Values: 50, 100, 200, 300, 400, 500
    "sales_column": "bought_in_past_month",
    "sales_requires_parsing": False,
    
    # Model number patterns to exclude from quantity parsing
    # Examples: SDB113, G9, 2W (wattage)
    "model_number_patterns": [
        r'\b[A-Z]+\d{3,}\b',  # SDB113, ABC123
        r'\bG\d+\b',          # G9 (bulb type)
        r'\b\d+W\b',          # 2W (wattage)
    ],
}

# --- HIGH-RISK ROW WARNINGS ---
# These rows have patterns that may cause false positives:
CALIBRATION_WARNINGS = [
    {"row": 1,  "title": "LUXURY CUPCAKE 100 CASES", "warning": "100 CASES may be product name, not quantity"},
    {"row": 10, "title": "EASY STORAGE VACUUM BAG 70X100CM", "warning": "70X100CM are bag dimensions (cm), not 7000 items"},
    {"row": 16, "title": "PANASONIC UPRIGHT SDB113", "warning": "SDB113 is model number, not quantity"},
    {"row": 36, "title": "SECURPAK SCREWS ZP 5X60MM", "warning": "5X60MM is screw spec, not quantity"},
    {"row": 37, "title": "DEKTON DRILL BIT 5MM X 85MM", "warning": "5MM X 85MM is drill size, not quantity"},
    {"row": 5,  "title": "STARWASH CLOTHES LINE 30M", "warning": "30M is length (30 meters), not 30 packs"},
]

# --- DATA QUALITY ALERT ---
# CRITICAL: This file has severe SupplierTitle vs AmazonTitle mismatches
# Example: Row 0 - Supplier="BIRTHDAY BADGE" vs Amazon="Motorola phone"
# Recommendation: Enable strict EAN checksum validation and title similarity checks
DATA_QUALITY_FLAGS = {
    "ean_amazon_mismatch_detected": True,
    "strict_ean_validation_required": True,
    "title_similarity_threshold": 0.30,  # Flag if <30% word overlap
}
# -------------------------------------------------------
