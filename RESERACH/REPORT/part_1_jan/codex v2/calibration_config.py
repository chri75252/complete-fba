# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pcs', 'each'],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ['cm', 'mm', 'ml', 'kg', 'g', 'inch', 'l', 'ft', 'in', 'm', 'x'],
    "brand_position": 'start',
    "sales_column": 'bought_in_past_month',
}
# ---------------------------------

# --- CALIBRATION WARNINGS (sample) ---
# - Row 7: unit keyword without clear qty -> 'STATUS LED G9 2W LED CAPSULE BULB EACH'
