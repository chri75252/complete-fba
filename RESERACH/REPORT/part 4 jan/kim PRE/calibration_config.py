# -*- coding: utf-8 -*-
# FBA Calibration Configuration
# Generated: 2026-01-05T03:35:10.915913
# Source: part 4 jan.xlsx (2696 products)
# ============================================================

# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pce', 'pc', 'pcs', 'pk', 'pack', 'piece', 'pieces', 'set', 'assorted'],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ['cm', 'mm', 'ml', 'ml', 'ltr', 'l', 'lt', 'kg', 'g', 'oz', 'inch', "'", '"'],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ['magnification', 'zoom', 'microscope', 'scope', 'times', 'processor'],
    "table_pipe_sanitization": False,
    "single_item_keywords": ['each', 'sold each', 'per each'],
    "model_number_patterns": [r'SDB\d+', r'V\d+', r'F\d+', r'MK\d+'],
    "trailing_number_threshold": 100,
}
# ---------------------------------
