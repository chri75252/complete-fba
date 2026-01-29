"""Anomaly detection for iteration loop decision-making.

Anomalies are signals that might indicate:
- Data quality issues
- Pack detection problems
- Rows that need AI adjudication
- Potential regression risks

This module detects:
- Profit outliers (extremely high/low profit)
- ROI outliers
- Weak-match clusters (many rows with similar low confidence)
- Bucket flip candidates (rows near decision boundaries)
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass
class AnomalySummary:
    """Summary of detected anomalies."""

    profit_outliers: list[dict] = field(default_factory=list)
    roi_outliers: list[dict] = field(default_factory=list)
    weak_match_clusters: list[dict] = field(default_factory=list)
    bucket_flip_candidates: list[dict] = field(default_factory=list)
    high_rsu_rows: list[dict] = field(default_factory=list)
    
    @property
    def total_anomalies(self) -> int:
        return (
            len(self.profit_outliers)
            + len(self.roi_outliers)
            + len(self.weak_match_clusters)
            + len(self.bucket_flip_candidates)
            + len(self.high_rsu_rows)
        )
    
    @property
    def has_significant_anomalies(self) -> bool:
        """Check if anomalies are significant enough to warrant another iteration."""
        return (
            len(self.profit_outliers) > 5
            or len(self.weak_match_clusters) > 3
            or len(self.bucket_flip_candidates) > 10
            or len(self.high_rsu_rows) > 5
        )
    
    def to_dict(self) -> dict:
        return {
            "profit_outliers": self.profit_outliers,
            "roi_outliers": self.roi_outliers,
            "weak_match_clusters": self.weak_match_clusters,
            "bucket_flip_candidates": self.bucket_flip_candidates,
            "high_rsu_rows": self.high_rsu_rows,
            "total_anomalies": self.total_anomalies,
            "has_significant_anomalies": self.has_significant_anomalies,
        }


def _detect_profit_outliers(
    ledger: pd.DataFrame,
    threshold_high: float = 20.0,
    threshold_low: float = -10.0,
) -> list[dict]:
    """
    Detect rows with unusually high or low profit.
    
    High profit outliers with low confidence are suspicious.
    Low profit outliers in positive buckets are errors.
    """
    outliers = []
    
    profit = pd.to_numeric(ledger.get("adjusted_profit"), errors="coerce").fillna(0)
    confidence = pd.to_numeric(ledger.get("confidence"), errors="coerce").fillna(50)
    
    # High profit with low confidence — suspicious
    high_profit_low_conf = ledger[(profit > threshold_high) & (confidence < 60)]
    for _, row in high_profit_low_conf.iterrows():
        outliers.append({
            "row_id": int(row.get("row_id", 0)),
            "stable_key": str(row.get("stable_key", "")),
            "type": "high_profit_low_confidence",
            "profit": float(row.get("adjusted_profit", 0)),
            "confidence": int(row.get("confidence", 0)),
            "bucket": str(row.get("bucket", "")),
        })
    
    # Negative profit in analysis (shouldn't happen after validation)
    negative = ledger[profit < threshold_low]
    for _, row in negative.iterrows():
        outliers.append({
            "row_id": int(row.get("row_id", 0)),
            "stable_key": str(row.get("stable_key", "")),
            "type": "very_negative_profit",
            "profit": float(row.get("adjusted_profit", 0)),
            "confidence": int(row.get("confidence", 0)),
            "bucket": str(row.get("bucket", "")),
        })
    
    return outliers


def _detect_roi_outliers(
    ledger: pd.DataFrame,
    threshold_high: float = 500.0,
) -> list[dict]:
    """Detect rows with unusually high ROI (might be data errors)."""
    outliers = []
    
    roi = pd.to_numeric(ledger.get("roi"), errors="coerce").fillna(0)
    
    high_roi = ledger[roi > threshold_high]
    for _, row in high_roi.iterrows():
        outliers.append({
            "row_id": int(row.get("row_id", 0)),
            "stable_key": str(row.get("stable_key", "")),
            "type": "very_high_roi",
            "roi": float(row.get("roi", 0)),
            "bucket": str(row.get("bucket", "")),
        })
    
    return outliers


def _detect_weak_match_clusters(
    ledger: pd.DataFrame,
    confidence_threshold: int = 55,
    min_cluster_size: int = 5,
) -> list[dict]:
    """
    Detect clusters of rows with similar low confidence.
    
    Many rows with confidence in a narrow range might indicate
    a systemic issue (e.g., missing trap pattern).
    """
    clusters = []
    
    confidence = pd.to_numeric(ledger.get("confidence"), errors="coerce").fillna(50)
    weak = ledger[confidence < confidence_threshold]
    
    if len(weak) < min_cluster_size:
        return clusters
    
    # Group by bucket and check cluster sizes
    for bucket in weak["bucket"].unique():
        bucket_rows = weak[weak["bucket"] == bucket]
        if len(bucket_rows) >= min_cluster_size:
            clusters.append({
                "bucket": str(bucket),
                "count": len(bucket_rows),
                "avg_confidence": float(bucket_rows["confidence"].mean()),
                "sample_row_ids": bucket_rows["row_id"].head(5).tolist(),
                "sample_stable_keys": bucket_rows["stable_key"].head(5).tolist() if "stable_key" in bucket_rows.columns else [],
            })
    
    return clusters


def _detect_bucket_flip_candidates(
    ledger: pd.DataFrame,
    confidence_range: tuple[int, int] = (45, 55),
) -> list[dict]:
    """
    Detect rows near decision boundaries.
    
    These are candidates for AI adjudication because small changes
    in scoring could flip their bucket assignment.
    """
    candidates = []
    
    confidence = pd.to_numeric(ledger.get("confidence"), errors="coerce").fillna(50)
    near_boundary = ledger[
        (confidence >= confidence_range[0]) & 
        (confidence <= confidence_range[1])
    ]
    
    for _, row in near_boundary.iterrows():
        candidates.append({
            "row_id": int(row.get("row_id", 0)),
            "stable_key": str(row.get("stable_key", "")),
            "confidence": int(row.get("confidence", 0)),
            "bucket": str(row.get("bucket", "")),
            "pack_verdict": str(row.get("pack_verdict", "")),
        })
    
    return candidates


def _detect_high_rsu_rows(
    ledger: pd.DataFrame,
    rsu_threshold: int = 5,
) -> list[dict]:
    """
    Detect rows with high Required Supplier Units.
    
    High RSU often indicates pack mismatch detection that might
    need verification.
    """
    high_rsu = []
    
    # Check if pack_ratio indicates RSU calculation
    # RSU = ceil(pack_ratio) when pack_ratio > 1
    pack_ratio = pd.to_numeric(ledger.get("pack_ratio"), errors="coerce").fillna(1)
    rsu = np.ceil(pack_ratio)
    
    high = ledger[rsu >= rsu_threshold]
    
    for _, row in high.iterrows():
        high_rsu.append({
            "row_id": int(row.get("row_id", 0)),
            "stable_key": str(row.get("stable_key", "")),
            "pack_ratio": float(row.get("pack_ratio", 1)),
            "rsu": int(np.ceil(float(row.get("pack_ratio", 1)))),
            "bucket": str(row.get("bucket", "")),
            "pack_verdict": str(row.get("pack_verdict", "")),
        })
    
    return high_rsu


def detect_anomalies(
    ledger: pd.DataFrame,
    evidence: list[dict] | None = None,
) -> AnomalySummary:
    """
    Run all anomaly detectors on the ledger.
    
    Args:
        ledger: Analysis ledger DataFrame
        evidence: Optional evidence list (for future expansion)
    
    Returns:
        AnomalySummary with all detected anomalies
    """
    return AnomalySummary(
        profit_outliers=_detect_profit_outliers(ledger),
        roi_outliers=_detect_roi_outliers(ledger),
        weak_match_clusters=_detect_weak_match_clusters(ledger),
        bucket_flip_candidates=_detect_bucket_flip_candidates(ledger),
        high_rsu_rows=_detect_high_rsu_rows(ledger),
    )
