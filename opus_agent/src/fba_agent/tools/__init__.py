"""
FBA Agent Tools Package.

Contains all deterministic tools used by the agent pipeline.
"""

from .data_loading import load_report, normalize_columns, sample_rows
from .ean_validation import (
    clean_to_digits,
    gtin_checksum_ok,
    normalize_ean,
    is_strict_valid_barcode,
    check_ean_match
)
from .pack_detection import (
    extract_pack_count,
    extract_multipack_total,
    detect_dimension_trap,
    detect_spec_x_trap,
    calculate_rsu
)
from .title_parsing import (
    parse_title_attributes,
    extract_brand,
    check_brand_match,
    check_product_type_match
)
from .scoring import compute_confidence, compute_pack_verdict
from .profit_calculation import calculate_adjusted_profit
from .categorization import categorize_row, analyze_row, analyze_all_rows
from .validation import validate_ledger, validate_coverage, validate_profit
from .output import render_phasea_report, write_run_artifacts

__all__ = [
    # Data loading
    "load_report",
    "normalize_columns", 
    "sample_rows",
    # EAN validation
    "clean_to_digits",
    "gtin_checksum_ok",
    "normalize_ean",
    "is_strict_valid_barcode",
    "check_ean_match",
    # Pack detection
    "extract_pack_count",
    "extract_multipack_total",
    "detect_dimension_trap",
    "detect_spec_x_trap",
    "calculate_rsu",
    # Title parsing
    "parse_title_attributes",
    "extract_brand",
    "check_brand_match",
    "check_product_type_match",
    # Scoring
    "compute_confidence",
    "compute_pack_verdict",
    # Profit
    "calculate_adjusted_profit",
    # Categorization
    "categorize_row",
    "analyze_row",
    "analyze_all_rows",
    # Validation
    "validate_ledger",
    "validate_coverage",
    "validate_profit",
    # Output
    "render_phasea_report",
    "write_run_artifacts"
]
