
# --- CALIBRATION CONFIGURATION (part 8 jan.xlsx) ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['PIECES', 'PK', 'PCS', 'PC', 'PACK'],
    "allow_trailing_number_as_qty": False,  # DANGEROUS - trailing numbers are often variant codes (e.g., "GIRL 3")
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "m"],
    "brand_position": "start",  # Brands like MINKY, CHEF AID, TALA appear at start
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": False,
    "brand_format_patterns": ["ALL_CAPS_AT_START"],
    "brand_sparse_supplier_mode": True,  # Amazon titles rarely have matching brand
    "strong_similarity_threshold": 0.20,  # LOW due to high mismatch rate
    "strong_shared_tokens_threshold": 2,  # LOW due to high mismatch rate
    "very_strong_similarity_threshold": 0.30,
    "very_strong_shared_tokens_threshold": 3,
    "gate_mode": "C_brand_sparse",  # Use sparse mode due to title mismatches
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,  # "3 x 400ml" means RSU=3
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True,
    
    # CRITICAL WARNING FLAGS
    "high_mismatch_rate": True,  # 39/50 rows have no title overlap
    "mismatch_percentage": 78.0,
    "require_strict_ean_validation": True,  # EAN validity is the only reliable link
}
# ---------------------------------
