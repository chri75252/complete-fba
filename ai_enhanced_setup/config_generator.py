#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Generator - Full Implementation

Generates JSON configuration files for new suppliers with validation and atomic writes.

Features:
- Direct Python dict → JSON conversion
- Schema validation against SystemConfigLoader
- Atomic writes using WindowsSaveGuardian pattern
- Additive system_config.json merging
- UTF-8 encoding at all file boundaries

Session 2 Implementation
"""

import json
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, Any, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigGenerator:
    """
    Generates supplier configuration files from collected data.
    
    Full implementation:
    - Generate supplier_config JSON
    - Generate categories_config JSON
    - Merge into system_config.json (additive)
    - Validate schemas
    - Use atomic writes (WindowsSaveGuardian pattern)
    """
    
    def __init__(self, workspace_root: str = "."):
        """
        Initialize config generator.
        
        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root)
        self.config_dir = self.workspace_root / "config"
        self.supplier_configs_dir = self.config_dir / "supplier_configs"
        logger.info(f"ConfigGenerator initialized with workspace: {workspace_root}")
    
    def generate_supplier_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate supplier configuration from collected data.
        
        Args:
            data: Collected supplier data including:
                - supplier_domain: str (e.g., 'poundwholesale.co.uk')
                - field_mappings: Dict with title, price, ean, url, image selectors
                - price_range: Dict with min, max
                - target_roi: int (optional, default 25)
                
        Returns:
            Supplier configuration dict
        """
        domain = data.get("supplier_domain", "")
        supplier_id = domain.replace(".", "-")
        
        config = {
            "supplier_id": supplier_id,
            "supplier_name": domain,
            "base_url": f"https://{domain}",
            "enabled": True,
            "field_mappings": data.get("field_mappings", {
                "title": [],
                "price": [],
                "ean": [],
                "url": [],
                "image": []
            }),
            "authentication": {
                "enabled": False,
                "note": "Configure manually using existing StandalonePlaywrightLogin pattern"
            },
            "price_range": data.get("price_range", {"min": 1.0, "max": 20.0}),
            "target_roi_pct": data.get("target_roi", 25),
            "created_at": datetime.now().isoformat(),
            "created_by": "ai_enhanced_setup"
        }
        
        logger.info(f"Generated supplier config for: {supplier_id}")
        return config
    
    def generate_categories_config(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate categories configuration from collected data.
        
        Args:
            data: Collected category data including:
                - categories: List[Dict] with name, url
                
        Returns:
            List of category configs
        """
        categories = data.get("categories", [])
        
        config = []
        for idx, cat in enumerate(categories):
            config.append({
                "name": cat.get("name", f"Category {idx+1}"),
                "url": cat.get("url", ""),
                "enabled": True,
                "priority": idx + 1
            })
        
        logger.info(f"Generated categories config: {len(config)} categories")
        return config
    
    def merge_system_config(self, supplier_config: Dict[str, Any]) -> None:
        """
        Merge new supplier into system_config.json using additive strategy.
        
        Args:
            supplier_config: Supplier configuration to merge
            
        Raises:
            ValueError: If supplier_id already exists
            FileNotFoundError: If system_config.json not found
        """
        system_config_path = self.config_dir / "system_config.json"
        
        if not system_config_path.exists():
            logger.warning(f"system_config.json not found at: {system_config_path}")
            logger.info("Creating new system_config.json")
            system_config = {"suppliers": []}
        else:
            # Read existing config with UTF-8 encoding
            with open(system_config_path, 'r', encoding='utf-8') as f:
                system_config = json.load(f)
        
        # Ensure suppliers array exists
        if "suppliers" not in system_config:
            system_config["suppliers"] = []
        
        # Check for duplicate supplier_id
        supplier_id = supplier_config["supplier_id"]
        existing_ids = [s.get("supplier_id") for s in system_config["suppliers"]]
        
        if supplier_id in existing_ids:
            raise ValueError(
                f"Supplier '{supplier_id}' already exists in system_config.json. "
                f"Remove or rename the existing entry first."
            )
        
        # Append new supplier
        system_config["suppliers"].append(supplier_config)
        
        # Write atomically with UTF-8 encoding
        self._atomic_write_json(system_config_path, system_config)
        logger.info(f"Merged supplier '{supplier_id}' into system_config.json")
    
    def write_configs_atomic(self, 
                            supplier_config: Dict[str, Any],
                            categories_config: List[Dict[str, Any]],
                            supplier_id: str) -> bool:
        """
        Write all configuration files atomically.
        
        Args:
            supplier_config: Supplier configuration dict
            categories_config: Categories configuration list
            supplier_id: Supplier identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directories exist
            self.supplier_configs_dir.mkdir(parents=True, exist_ok=True)
            
            # Define file paths
            supplier_config_path = self.supplier_configs_dir / f"{supplier_id}.json"
            categories_config_path = self.config_dir / f"{supplier_id}_categories.json"
            
            # Write supplier config
            self._atomic_write_json(supplier_config_path, supplier_config)
            logger.info(f"✅ Written: {supplier_config_path}")
            
            # Write categories config
            self._atomic_write_json(categories_config_path, categories_config)
            logger.info(f"✅ Written: {categories_config_path}")
            
            # Merge into system_config.json
            self.merge_system_config(supplier_config)
            logger.info(f"✅ Updated: config/system_config.json")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write configs: {e}")
            return False
    
    def _atomic_write_json(self, file_path: Path, data: Any) -> None:
        """
        Write JSON file atomically using WindowsSaveGuardian pattern.
        
        Pattern:
        1. Write to temp file
        2. Validate temp file
        3. Move to final destination (atomic on Windows)
        
        Args:
            file_path: Target file path
            data: Data to write (will be JSON serialized)
        """
        # Create temp file in same directory for atomic move
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.json',
            dir=file_path.parent,
            text=True
        )
        
        try:
            # Write to temp file with UTF-8 encoding
            with open(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Validate temp file is readable
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)  # Will raise if invalid
            
            # Atomic move (on Windows, this is atomic at filesystem level)
            shutil.move(temp_path, str(file_path))
            logger.debug(f"Atomic write successful: {file_path}")
            
        except Exception as e:
            # Clean up temp file on error
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
            raise RuntimeError(f"Atomic write failed for {file_path}: {e}")


class ConfigValidator:
    """
    Validates generated configurations against system schema.
    """
    
    @staticmethod
    def validate_supplier_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate supplier configuration against required schema.
        
        Args:
            config: Supplier configuration dict
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required top-level keys
        required_keys = ["supplier_id", "supplier_name", "base_url", "field_mappings"]
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")
        
        # Validate field_mappings structure
        if "field_mappings" in config:
            field_mappings = config["field_mappings"]
            required_fields = ["title", "price", "ean", "url"]
            
            for field in required_fields:
                if field not in field_mappings:
                    errors.append(f"Missing field_mapping: {field}")
                elif not isinstance(field_mappings[field], list):
                    errors.append(f"field_mapping '{field}' must be a list of selectors")
        
        # Validate price_range if present
        if "price_range" in config:
            price_range = config["price_range"]
            if "min" not in price_range or "max" not in price_range:
                errors.append("price_range must have 'min' and 'max' keys")
            elif price_range.get("min", 0) > price_range.get("max", 0):
                errors.append("price_range min must be <= max")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def validate_categories_config(config: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate categories configuration.
        
        Args:
            config: Categories configuration list
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not isinstance(config, list):
            errors.append("Categories config must be a list")
            return False, errors
        
        if len(config) == 0:
            errors.append("Categories config must have at least one category")
        
        for idx, cat in enumerate(config):
            if "name" not in cat:
                errors.append(f"Category {idx} missing 'name' field")
            if "url" not in cat:
                errors.append(f"Category {idx} missing 'url' field")
            elif not cat["url"].startswith(("http://", "https://")):
                errors.append(f"Category {idx} URL must start with http:// or https://")
        
        is_valid = len(errors) == 0
        return is_valid, errors


if __name__ == "__main__":
    # Test implementation
    logging.basicConfig(level=logging.INFO)
    
    generator = ConfigGenerator()
    
    # Test data
    test_data = {
        "supplier_domain": "poundwholesale.co.uk",
        "categories": [
            {"name": "Toys", "url": "https://poundwholesale.co.uk/toys"},
            {"name": "Electronics", "url": "https://poundwholesale.co.uk/electronics"}
        ],
        "field_mappings": {
            "title": [".product-title"],
            "price": [".price .amount"],
            "ean": ["[data-ean]"],
            "url": [".product-link"],
            "image": [".product-image img"]
        },
        "price_range": {"min": 1.0, "max": 20.0},
        "target_roi": 30
    }
    
    # Generate configs
    supplier_config = generator.generate_supplier_config(test_data)
    categories_config = generator.generate_categories_config(test_data)
    
    # Validate
    validator = ConfigValidator()
    is_valid, errors = validator.validate_supplier_config(supplier_config)
    
    if is_valid:
        print("✅ Supplier config valid")
        print(json.dumps(supplier_config, indent=2))
    else:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    is_valid, errors = validator.validate_categories_config(categories_config)
    
    if is_valid:
        print("✅ Categories config valid")
        print(json.dumps(categories_config, indent=2))
    else:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  - {error}")
