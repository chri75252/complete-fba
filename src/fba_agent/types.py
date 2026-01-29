from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Bucket = Literal["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION", "FILTERED_OUT"]


@dataclass(frozen=True)
class SupplierNamingConvention:
    explicit_units: list[str] = field(default_factory=lambda: ["pce", "pcs", "pk", "pack"])
    allow_trailing_number_as_qty: bool = False
    leading_multiplier_check: bool = True
    dimension_shield_keywords: list[str] = field(
        default_factory=lambda: ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch"]
    )
    brand_position: Literal["start", "mixed"] = "mixed"
    sales_column: str = "sales_numeric"
    capacity_pattern_as_rsu: bool = True
    spec_x_shield_keywords: list[str] = field(
        default_factory=lambda: ["magnification", "zoom", "microscope", "scope", "times"]
    )
    table_pipe_sanitization: bool = True


@dataclass(frozen=True)
class MergedConfig:
    supplier_id: str
    naming: SupplierNamingConvention
    fee_rate: float = 0.30
    title_match_threshold: float = 0.22


@dataclass(frozen=True)
class SchemaInfo:
    input_path: str
    rows: int
    detected_sales_column: str | None
    detected_columns: list[str]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PackParseResult:
    quantity: int | None
    evidence: str
    traps: list[str] = field(default_factory=list)
    ambiguous: bool = False


@dataclass(frozen=True)
class VariantParseResult:
    capacity_value: float | None
    capacity_unit: str | None
    capacity_base: float | None
    color: str | None
    scent: str | None


@dataclass(frozen=True)
class MatchChecks:
    strict_exact_ean: bool
    supplier_ean_valid: bool
    amazon_ean_valid: bool
    amazon_ean_missing: bool
    brand_match: bool
    product_type_match: bool
    variant_within_tolerance: bool
    capacity_delta_pct: float | None
    capacity_gate: Literal["ok_0_10", "nv_10_25", "fo_25_50", "fo_gt_50", "unknown"]


@dataclass(frozen=True)
class RowDecisionRecord:
    row_id: int
    bucket: Bucket
    confidence: int
    track: Literal["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION", "UNKNOWN"]
    include_in_tables: bool

    supplier_title: str
    amazon_title: str
    supplier_ean: str
    amazon_ean: str
    asin: str

    supplier_price: float | None
    selling_price: float | None
    net_profit: float | None
    roi: float | None
    sales: float | None

    supplier_pack_qty: int | None
    amazon_pack_qty: int | None
    pack_ratio: float | None
    pack_verdict: str

    adjusted_profit: float | None
    key_match_evidence: str
    filter_reason: str

    traps: list[str]
    checks: MatchChecks


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# vNext Dataclasses (Phase 2)
# =============================================================================


@dataclass
class AdjudicationResult:
    """Result from AI row adjudication."""

    row_id: int
    stable_key: str
    extracted_signals: dict  # brand, pack, product type extracted by LLM
    trap_detections: list[str]
    recommended_bucket: str  # LLM suggestion (not authoritative)
    confidence_suggestion: int  # LLM signal (not final score)
    reasoning: str


@dataclass
class CritiqueResult:
    """Result from AI report critique."""

    high_severity_issues: list[dict]  # Issues requiring attention
    proposed_changes: list[dict]  # Bounded adjustments to apply
    overall_assessment: str  # Summary text
    recommended_action: str  # "finalize", "apply_and_rerun", "block"


@dataclass
class RegressionDiff:
    """Comparison between iterations or vs historical runs."""

    missing_stable_keys: list[str]  # Keys in history but not current
    bucket_transitions: dict  # {stable_key: {"from": bucket, "to": bucket}}
    good_to_bad_count: int  # Count of VERIFIED/HIGHLY_LIKELY → worse
    bad_to_good_count: int  # Count of improvements
    blocked: bool  # Whether regression guard blocks finalization
    justifications: list[dict]  # Approved exceptions


@dataclass
class IterationResult:
    """Result from a single iteration of the analysis loop."""

    iteration_number: int
    ledger: object  # pd.DataFrame (avoiding import for type hint)
    evidence: list[dict]
    validation_passed: bool
    validation_errors: list[str]
    anomaly_summary: dict
    critique: CritiqueResult | None
    adjudication_results: list[AdjudicationResult]
    config_applied: dict  # Snapshot of config used

