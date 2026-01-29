"""
Data schemas for FBA Agent pipeline.

These dataclasses define the structure of data flowing through the pipeline.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum


class Bucket(str, Enum):
    """Final categorization buckets for products."""
    VERIFIED = "VERIFIED"
    HIGHLY_LIKELY = "HIGHLY_LIKELY"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    FILTERED_OUT = "FILTERED_OUT"


class TrapType(str, Enum):
    """Types of trap patterns detected during analysis."""
    DIMENSION_TRAP = "dimension_trap"
    QUANTITY_INSIDE = "quantity_inside"
    SPEC_X = "spec_x"
    CAPACITY_MULTIPACK = "capacity_multipack"
    MODEL_NUMBER = "model_number"


@dataclass
class SchemaInfo:
    """Information about the input file schema."""
    detected_columns: List[str]
    ean_column: str
    ean_onpage_column: str
    sales_column: Optional[str]
    has_rowid: bool
    row_count: int
    file_format: str  # "csv" | "xlsx"
    
    def to_dict(self) -> dict:
        return {
            "detected_columns": self.detected_columns,
            "ean_column": self.ean_column,
            "ean_onpage_column": self.ean_onpage_column,
            "sales_column": self.sales_column,
            "has_rowid": self.has_rowid,
            "row_count": self.row_count,
            "file_format": self.file_format
        }


@dataclass
class ParsedAttributes:
    """Attributes parsed from a product title."""
    brand: Optional[str] = None
    product_type: Optional[str] = None
    variant: Optional[str] = None
    size_capacity: Optional[str] = None
    pack_count: int = 1
    raw_title: str = ""
    
    def to_dict(self) -> dict:
        return {
            "brand": self.brand,
            "product_type": self.product_type,
            "variant": self.variant,
            "size_capacity": self.size_capacity,
            "pack_count": self.pack_count,
            "raw_title": self.raw_title
        }


@dataclass
class TrapDetection:
    """Record of a trap pattern detected during analysis."""
    trap_type: str  # TrapType value
    pattern_matched: str
    action_taken: str  # "ignored_as_dimension" | "treated_as_pack" | etc.
    
    def to_dict(self) -> dict:
        return {
            "trap_type": self.trap_type,
            "pattern_matched": self.pattern_matched,
            "action_taken": self.action_taken
        }


@dataclass
class MatchChecks:
    """Results of all match verification checks."""
    ean_strict_valid_supplier: bool = False
    ean_strict_valid_amazon: bool = False
    is_exact_ean_strict: bool = False
    brand_match: bool = False
    product_type_match: bool = False
    variant_match: str = "unknown"  # "true" | "false" | "ambiguous" | "unknown"
    pack_match: bool = False
    capacity_delta_percent: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "ean_strict_valid_supplier": self.ean_strict_valid_supplier,
            "ean_strict_valid_amazon": self.ean_strict_valid_amazon,
            "is_exact_ean_strict": self.is_exact_ean_strict,
            "brand_match": self.brand_match,
            "product_type_match": self.product_type_match,
            "variant_match": self.variant_match,
            "pack_match": self.pack_match,
            "capacity_delta_percent": self.capacity_delta_percent
        }


@dataclass
class RowDecisionRecord:
    """Complete decision record for a single row."""
    row_id: int
    bucket: str  # Bucket value
    confidence: int  # 0-100
    pack_verdict: str  # "1:1 Match" | "BUNDLE (4x) - OK" | etc.
    adjusted_profit: float
    rsu: float  # Required Supplier Units
    
    # Parsed attributes
    supplier_attributes: ParsedAttributes = field(default_factory=ParsedAttributes)
    amazon_attributes: ParsedAttributes = field(default_factory=ParsedAttributes)
    
    # Detection records
    trap_detections: List[TrapDetection] = field(default_factory=list)
    match_checks: MatchChecks = field(default_factory=MatchChecks)
    
    # Evidence and reasons
    key_match_evidence: str = ""
    filter_reason: str = "-"
    required_next_action: Optional[str] = None
    
    # Original row data for reference
    raw_row: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "row_id": self.row_id,
            "bucket": self.bucket,
            "confidence": self.confidence,
            "pack_verdict": self.pack_verdict,
            "adjusted_profit": self.adjusted_profit,
            "rsu": self.rsu,
            "supplier_attributes": self.supplier_attributes.to_dict(),
            "amazon_attributes": self.amazon_attributes.to_dict(),
            "trap_detections": [t.to_dict() for t in self.trap_detections],
            "match_checks": self.match_checks.to_dict(),
            "key_match_evidence": self.key_match_evidence,
            "filter_reason": self.filter_reason,
            "required_next_action": self.required_next_action
        }
    
    def to_ledger_row(self) -> dict:
        """Convert to coverage ledger row format."""
        return {
            "row_id": self.row_id,
            "bucket": self.bucket,
            "confidence": self.confidence,
            "pack_ratio": self.rsu,
            "adjusted_profit": self.adjusted_profit,
            "is_exact_ean_strict": self.match_checks.is_exact_ean_strict,
            "brand_match": self.match_checks.brand_match,
            "product_match": self.match_checks.product_type_match,
            "trap_flags": ",".join([t.trap_type for t in self.trap_detections]),
            "evidence_pointer": f"evidence.jsonl:row_{self.row_id}"
        }


@dataclass
class ValidationResult:
    """Result of a validation gate check."""
    passed: bool
    gate_name: str = ""
    error: str = ""
    violation_rows: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "gate_name": self.gate_name,
            "error": self.error,
            "violation_rows": self.violation_rows,
            "warnings": self.warnings
        }


@dataclass
class RunSummary:
    """Summary of an analysis run."""
    run_id: str
    input_file: str
    supplier_id: str
    row_count: int
    bucket_counts: Dict[str, int] = field(default_factory=dict)
    validation_passed: bool = True
    validation_details: Dict[str, Any] = field(default_factory=dict)
    timing_ms: int = 0
    model_calls: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "input_file": self.input_file,
            "supplier_id": self.supplier_id,
            "row_count": self.row_count,
            "bucket_counts": self.bucket_counts,
            "validation_passed": self.validation_passed,
            "validation_details": self.validation_details,
            "timing_ms": self.timing_ms,
            "model_calls": self.model_calls,
            "created_at": self.created_at
        }


@dataclass
class PreflightWarning:
    """Warning generated during preflight calibration."""
    row_id: int
    description: str
    pattern: str = ""
    severity: str = "warning"  # "warning" | "error"
    
    def to_dict(self) -> dict:
        return {
            "row_id": self.row_id,
            "description": self.description,
            "pattern": self.pattern,
            "severity": self.severity
        }
