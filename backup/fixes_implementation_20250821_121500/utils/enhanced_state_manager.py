"""
Enhanced State Manager - Comprehensive state management for Amazon FBA Agent System v3.5
RELATIVE PATH VERSION - Uses relative paths instead of hardcoded absolute paths

This module provides superior state management capabilities based on analysis of the deprecated 
script's more comprehensive approach, following claude.md standards.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import hashlib
import logging
from collections import defaultdict

# Use relative imports and paths
try:
    from .path_manager import get_processing_state_path, path_manager
except ImportError:
    try:
        from utils.path_manager import get_processing_state_path, path_manager
    except ImportError:
        # For standalone testing - use relative paths
        import sys
        current_dir = Path(__file__).parent.parent
        sys.path.append(str(current_dir))
        from utils.path_manager import get_processing_state_path, path_manager

# Import category completion tracker for file-grounded calculations
try:
    from tools.category_completion_tracker import get_completion_metrics
except ImportError:
    # Fallback for different import paths - use relative paths
    try:
        import sys
        current_dir = Path(__file__).parent.parent
        sys.path.append(str(current_dir))
        from tools.category_completion_tracker import get_completion_metrics
    except ImportError:
        get_completion_metrics = None

log = logging.getLogger(__name__)


class EnhancedStateManager:
    """Enhanced state management with comprehensive tracking and recovery capabilities"""
    
    SCHEMA_VERSION = "1.0"
    
    def __init__(self, supplier_name: str, base_path: Optional[str] = None):
        self.supplier_name = supplier_name
        
        # Use relative base path if not provided
        if base_path is None:
            self.base_path = Path(__file__).parent.parent  # Go up to project root
        else:
            self.base_path = Path(base_path)
            
        self.state_file_path = get_processing_state_path(supplier_name)
        self.state_data = self._initialize_state()
        
    def _get_relative_path(self, *path_parts) -> Path:
        """Get path relative to project root"""
        return self.base_path / Path(*path_parts)