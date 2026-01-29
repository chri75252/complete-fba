"""
Configuration management for FBA Agent.

Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


@dataclass
class Config:
    """Main configuration class for the FBA Agent."""
    
    # API Configuration
    moonshot_api_key: str = field(default_factory=lambda: os.getenv("MOONSHOT_API_KEY", ""))
    moonshot_model: str = field(default_factory=lambda: os.getenv("MOONSHOT_MODEL", "moonshot-v1-128k"))
    moonshot_base_url: str = field(default_factory=lambda: os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"))
    
    # Output Configuration
    default_output_dir: Path = field(default_factory=lambda: Path(os.getenv("DEFAULT_OUTPUT_DIR", "./runs")))
    verbose_logging: bool = field(default_factory=lambda: os.getenv("VERBOSE_LOGGING", "false").lower() == "true")
    
    # Analysis Configuration
    skip_browser_verification: bool = True  # Default per PRD
    preflight_sample_size: int = 50
    
    # Scoring Configuration
    verified_base_score: int = 95
    highly_likely_base_score: int = 80
    needs_verification_base_score: int = 60
    
    # Dimension Shield Keywords (from specifications)
    dimension_shield_keywords: List[str] = field(default_factory=lambda: [
        "cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", 
        "ft", "w", "watt", "led", "magnification", "zoom", "k"
    ])
    
    # Pack Indicator Keywords
    pack_keywords: List[str] = field(default_factory=lambda: [
        "pack", "pk", "pcs", "pce", "pieces", "piece", "pairs", "set", "count"
    ])
    
    # Spec-X Shield Keywords (features, not packs)
    spec_x_shield_keywords: List[str] = field(default_factory=lambda: [
        "magnification", "zoom", "microscope", "scope", "times", "led", "watt"
    ])
    
    # Capacity Tolerance Thresholds (from Main.txt)
    capacity_tolerance_thresholds: dict = field(default_factory=lambda: {
        "verified": 0.10,          # 0-10% → VERIFIED/HIGHLY_LIKELY
        "needs_verification": 0.25, # 10-25% → NEEDS_VERIFICATION
        "filtered_different_sku": 0.50,  # 25-50% → FILTERED OUT (different SKU)
        "filtered_different_product": 1.0  # >50% → FILTERED OUT (different product)
    })
    
    # IP Risk Brands (luxury/trademark only - from Main.txt)
    ip_risk_brands: List[str] = field(default_factory=lambda: [
        "jo malone", "chanel", "dior", "gucci", "louis vuitton", "prada",
        "hermès", "hermes", "apple", "samsung", "sony", "microsoft", "nike", "adidas"
    ])
    
    def validate(self) -> bool:
        """Validate configuration is complete."""
        if not self.moonshot_api_key:
            raise ValueError("MOONSHOT_API_KEY is required. Set it in .env file.")
        return True
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create Config from environment variables."""
        config = cls()
        config.validate()
        return config


@dataclass
class SupplierCalibration:
    """Calibration configuration for a specific supplier."""
    
    supplier_id: str
    explicit_units: List[str] = field(default_factory=lambda: ["pce", "pcs", "pk", "pack"])
    allow_trailing_number_as_qty: bool = True
    leading_multiplier_check: bool = True
    dimension_shield_keywords: List[str] = field(default_factory=lambda: [
        "cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch"
    ])
    brand_position: str = "mixed"  # "start" | "mixed"
    sales_column: str = "sales_numeric"
    capacity_pattern_as_rsu: bool = True  # "3 x 400ml" → RSU=3
    spec_x_shield_keywords: List[str] = field(default_factory=lambda: [
        "magnification", "zoom", "microscope", "scope", "times"
    ])
    table_pipe_sanitization: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "supplier_id": self.supplier_id,
            "explicit_units": self.explicit_units,
            "allow_trailing_number_as_qty": self.allow_trailing_number_as_qty,
            "leading_multiplier_check": self.leading_multiplier_check,
            "dimension_shield_keywords": self.dimension_shield_keywords,
            "brand_position": self.brand_position,
            "sales_column": self.sales_column,
            "capacity_pattern_as_rsu": self.capacity_pattern_as_rsu,
            "spec_x_shield_keywords": self.spec_x_shield_keywords,
            "table_pipe_sanitization": self.table_pipe_sanitization
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SupplierCalibration":
        """Create from dictionary."""
        return cls(**data)
