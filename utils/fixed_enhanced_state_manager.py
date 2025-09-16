"""
Fixed Enhanced State Manager - Comprehensive solution for processing state issues
================================================================================

This module provides a complete fix for the critical processing state issues identified:
1. last_processed_index constantly resetting to 0
2. Category product count mismatches (36 vs 100+ products)
3. Metrics appearing in wrong sections  
4. System skipping products due to incorrect totals

Key Architectural Changes:
- Separated resumption index from progress tracking
- Prevented automatic index resets during processing
- Added real-time category product count updates
- Fixed metric placement and calculation
- Enhanced state preservation during interruptions

Author: Claude Code Processing State Fix Implementation
Date: July 30, 2025
Version: v3.7+ Critical Fix
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import hashlib
import logging
import time
from collections import defaultdict
import threading
from dataclasses import dataclass
import uuid

# Import atomic file operations
try:
    from .atomic_file_operations import ThreadSafeStateWriter, save_json
