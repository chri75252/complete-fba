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

log = logging.getLogger(__name__)


class FixedEnhancedStateManager:
    """
    Fixed Enhanced State Manager - Solves critical processing state issues

    Key Fixes:
    1. Separates resumption_index from progress_index to prevent confusion
    2. Only performs reverse gap detection on startup, not every save
    3. Updates category totals with real-time scraping discoveries
    4. Fixes metric placement in processing state
    5. Preserves interruption state correctly
    """

    SCHEMA_VERSION = "1.1_FIXED"

    def __init__(self, supplier_name: str, base_path: Optional[str] = None):
        self.supplier_name = supplier_name

        # Use relative base path if not provided
        if base_path is None:
            self.base_path = Path(__file__).parent.parent  # Go up to project root
        else:
            self.base_path = Path(base_path)

        self.state_file_path = get_processing_state_path(supplier_name)
        self.state_data = self._initialize_state()
        self._startup_completed = False  # Track if startup analysis is done
        self._last_save_time = 0.0
        self._drift_mirrored_once = False  # Mirror legacy from system at most once per run
        # Load system config for toggles (best-effort)
        self.system_config: Dict[str, Any] = {}
        try:
            from config.system_config_loader import SystemConfigLoader

            self.system_config = SystemConfigLoader().get_system_config()
        except Exception:
            self.system_config = {}

    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize state structure with all required fields and FIXED architecture"""
        return {
            "schema_version": self.SCHEMA_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "supplier_name": self.supplier_name,
            # 🚨 CRITICAL FIX 1: Separate resumption from progress tracking
            "last_processed_index": 0,  # Legacy field for backward compatibility
            "resumption_index": 0,  # Where to resume after interruption
            "progress_index": 0,  # Current progress in active session
            "session_products_processed": 0,  # Products processed in current session
            "total_products": 0,
            "processing_status": "initialized",
            "is_fresh_start": True,  # 🚨 FIX 1: Add missing fresh start field (corrected by _detect_actual_fresh_start)
            "category_performance": {},
            "error_log": [],
            "successful_products": 0,
            "profitable_products": 0,
            "total_profit_found": 0.0,
            "processing_statistics": {
                "start_time": None,
                "end_time": None,
                "total_runtime_seconds": 0,
                "average_time_per_product": 0,
                "products_per_hour": 0,
            },
            "metadata": {
                "version": "3.7+_FIXED",
                "config_hash": "",
                "runtime_settings": {},
                "system_info": {},
                "fix_applied": "processing_state_comprehensive_fix_20250730",
            },
            # 🚨 REMOVED: processed_products section - hash search uses linking map + cached products only
            # 🚨 CRITICAL FIX 2: Fixed supplier extraction progress structure
            "supplier_extraction_progress": {
                "current_category_index": 0,
                "total_categories": 0,
                "current_subcategory_index": 0,
                "pages_scraped_in_session": 0,  # 🚨 FIXED: Renamed from total_subcategories_in_batch
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 0,
                "discovered_products_in_current_category": 0,  # 🚨 NEW: Real-time discovery count
                "current_category_url": "",
                "current_batch_number": 0,
                "total_batches": 0,
                "extraction_phase": "not_started",
                "last_completed_category": "",
                "categories_completed": [],
                "products_extracted_total": 0,
            },
            # 🚨 CRITICAL FIX 3: Enhanced gap processing with better tracking
            "gap_processing": {
                "phase": "not_started",
                "gap_products_total": 0,
                "gap_products_processed": 0,
                "gap_start_time": None,
                "gap_end_time": None,
                "gap_profitable_found": 0,
                "gap_last_processed_url": "",
                "category_completion_status": {},
                "reverse_gap_detected": False,  # 🚨 NEW: Track reverse gap state
                "startup_analysis_completed": False,  # 🚨 NEW: Track startup completion
            },
            # ✅ NEW: Separated progression metrics for precise resumption
            "system_progression": {
                "current_phase": "supplier",
                "current_category_index": 0,
                "current_category_url": "",
                "total_categories": 0,
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 0,
                "supplier_extraction_resumption_index": 0,
                "amazon_analysis_resumption_index": 0,
            },
            # ✅ NEW: User-facing metrics (not used for resumption logic)
            "user_display_metrics": {
                "total_products": 0,
                "successful_products": 0,
                "progress_count": 0,
                "session_products_processed": 0,
            },
        }

    def _detect_actual_fresh_start(self):
        """Enhanced fresh start detection with processed product validation"""

        # Original flag-based logic
        flag_fresh_start = self.state_data.get("is_fresh_start", True)

        # NEW: Validate against actual processed data
        successful_products = self.state_data.get("successful_products", 0)
        global_counters = self.state_data.get("global_counters", {})
        total_processed = global_counters.get("total_products_processed", 0)
        system_progression = self.state_data.get("system_progression", {})
        current_category = system_progression.get("current_category_index")

        # True fresh start criteria: No processed products AND no category progress
        actual_fresh_start = (
            successful_products == 0 and total_processed == 0 and current_category is None
        )

        # Detect and log contradictions
        if flag_fresh_start != actual_fresh_start:
            log.warning(
                f"🚨 FRESH START CONTRADICTION DETECTED: "
                f"flag={flag_fresh_start} actual={actual_fresh_start} "
                f"products={successful_products} processed={total_processed} "
                f"category={current_category}"
            )

            # Use actual state rather than flag
            self.state_data["is_fresh_start"] = actual_fresh_start

        return actual_fresh_start

    def load_state(self) -> bool:
        """
        Load existing state from file, with backward compatibility
        Returns True if state was loaded, False if starting fresh
        """
        if not self.state_file_path.exists():
            log.info(f"No existing state file found for {self.supplier_name}, starting fresh")
            return False

        try:
            with open(self.state_file_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)

            # Handle backward compatibility
            if isinstance(loaded_data, dict) and "schema_version" not in loaded_data:
                log.info("Converting legacy state format to fixed enhanced format")
                self._migrate_legacy_state(loaded_data)
            else:
                # Merge loaded data with initialized structure
                self._merge_state_data(loaded_data)

            log.info(
                f"Loaded state for {self.supplier_name} - resumption from index {self.state_data['resumption_index']}"
            )
            return True

        except Exception as e:
            log.warning(f"Failed to load state file: {e}, starting fresh")
            return False

    def _migrate_legacy_state(self, legacy_data: Dict[str, Any]):
        """Migrate legacy state format to fixed enhanced format"""
        # 🚨 CRITICAL FIX: Properly migrate legacy index to resumption_index
        legacy_index = legacy_data.get("last_processed_index", 0)
        self.state_data["last_processed_index"] = legacy_index
        self.state_data["resumption_index"] = legacy_index
        self.state_data["progress_index"] = 0  # Always start fresh progress
        self.state_data["processing_status"] = "migrated_from_legacy"

        # Migrate other legacy fields if they exist
        if "supplier_extraction_progress" in legacy_data:
            legacy_progress = legacy_data["supplier_extraction_progress"]
            # Fix the misplaced metric
            if "total_subcategories_in_batch" in legacy_progress:
                self.state_data["supplier_extraction_progress"][
                    "pages_scraped_in_session"
                ] = legacy_progress["total_subcategories_in_batch"]

        log.info(f"Successfully migrated legacy state format - resumption index: {legacy_index}")

    def _merge_state_data(self, loaded_data: Dict[str, Any]):
        """Merge loaded data with initialized structure"""

        def deep_merge(base: Dict, overlay: Dict) -> Dict:
            result = base.copy()
            for key, value in overlay.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        self.state_data = deep_merge(self.state_data, loaded_data)
        self.state_data["last_updated"] = datetime.now(timezone.utc).isoformat()

        # 🚨 CRITICAL FIX: Ensure new fields exist even in merged data
        if "resumption_index" not in self.state_data:
            self.state_data["resumption_index"] = self.state_data.get("last_processed_index", 0)
        if "progress_index" not in self.state_data:
            self.state_data["progress_index"] = 0
        if "session_products_processed" not in self.state_data:
            self.state_data["session_products_processed"] = 0

    def perform_startup_analysis(self) -> Dict[str, Any]:
        """
        🚨 CRITICAL FIX: Perform reverse gap detection and category analysis ONLY on startup
        This method should be called ONCE at the beginning of a session, not on every save
        """
        if self._startup_completed:
            log.info("Startup analysis already completed for this session")
            return self.state_data.get("gap_processing", {}).get("category_completion_status", {})

        log.info("🔍 STARTUP ANALYSIS: Beginning comprehensive state analysis...")

        # Calculate file-grounded totals
        file_grounded_data = self._calculate_file_grounded_totals()

        # Toggle: allow disabling reverse gap heuristic entirely via config
        use_reverse_gap_heuristic = (
            self.system_config.get("pipeline_toggles", {})
            .get("resume", {})
            .get("use_reverse_gap_heuristic", False)
        )

        if not use_reverse_gap_heuristic:
            # Deterministic resume: use linking map count as resume index
            start_at = int(file_grounded_data.get("linking_map_count", 0))
            self.state_data["resumption_index"] = start_at
            self.state_data["progress_index"] = 0
            self.state_data.setdefault("gap_processing", {})["reverse_gap_detected"] = False
            self.state_data["resume_reason"] = "system_progression"
            log.info(f"RESUME DECISION: START_AT_INDEX={start_at} (reason: system_progression)")
        # 🚨 REVERSE GAP POLICY FIX: Only perform reverse gap detection on startup
        elif file_grounded_data["linking_map_count"] > file_grounded_data["total_products"]:
            log.info(
                f"🔄 REVERSE GAP DETECTED: Linking map ({file_grounded_data['linking_map_count']}) > Cache ({file_grounded_data['total_products']})"
            )

            # Check if we should preserve existing resume index or reset
            current_resumption_index = self.state_data.get("resumption_index", 0)
            explicit_cache_rebuild = self.state_data.get("force_cache_rebuild", False)

            if explicit_cache_rebuild:
                # Only reset to 0 if explicitly rebuilding cache
                self.state_data["resumption_index"] = 0
                self.state_data["resume_reason"] = "reverse_gap_cache_rebuild"
                log.info(
                    f"✅ REVERSE GAP: Reset resumption_index = 0 (explicit cache rebuild requested)"
                )
            elif current_resumption_index == 0:
                # If resumption_index is 0, check if this is truly a fresh start or a restart
                # 🚨 FIX 1: Use enhanced fresh start detection instead of manual logic
                is_actual_fresh_start = self._detect_actual_fresh_start()

                if not is_actual_fresh_start:
                    # This appears to be a restart, not a fresh start - preserve some progress
                    log.warning(
                        f"🔄 REVERSE GAP: Detected restart with resumption_index=0 but previous state exists - preserving index"
                    )
                    self.state_data["resume_reason"] = "reverse_gap_restart_preserved"
                else:
                    # Truly fresh start
                    self.state_data["resumption_index"] = 0
                    self.state_data["resume_reason"] = "reverse_gap_fresh_start"
                    log.info(f"✅ REVERSE GAP: Fresh start confirmed - resumption_index = 0")
            else:
                # Preserve existing resume index to avoid restarting from first category
                log.warning(
                    f"🔄 REVERSE GAP: Preserving existing resumption_index = {current_resumption_index} (no explicit rebuild)"
                )
                self.state_data["resume_reason"] = "reverse_gap_preserved_resume"

            self.state_data["progress_index"] = 0
            self.state_data["processing_status"] = "FRESH_CATEGORIES"
            self.state_data["gap_processing"]["reverse_gap_detected"] = True
        else:
            # Normal gap processing - resume from linking map count
            self.state_data["resumption_index"] = file_grounded_data["linking_map_count"]
            self.state_data["progress_index"] = 0  # Always start fresh progress tracking
            self.state_data["gap_processing"]["reverse_gap_detected"] = False

            # Track normal resume path
            self.state_data["resume_reason"] = "normal_startup"

            log.info(
                f"✅ Normal startup - resumption_index = {file_grounded_data['linking_map_count']}"
            )

        # Log final resume decision for observability (if not already logged)
        if "resume_reason" in self.state_data and "resumption_index" in self.state_data:
            log.info(
                f"RESUME DECISION: START_AT_INDEX={self.state_data['resumption_index']} (reason: {self.state_data['resume_reason']})"
            )

        # Update total products from file-grounded data
        self.state_data["total_products"] = file_grounded_data["total_products"]
        self.state_data["successful_products"] = file_grounded_data["processed_products"]

        # Update category completion status
        if file_grounded_data["category_completion_status"]:
            self.state_data["gap_processing"]["category_completion_status"] = file_grounded_data[
                "category_completion_status"
            ]

        # Update supplier extraction progress with file-grounded metrics
        current_category_analysis = self._calculate_current_category_metrics(file_grounded_data)
        self.state_data["supplier_extraction_progress"].update(current_category_analysis)

        # Mark startup analysis as completed
        self._startup_completed = True
        self.state_data["gap_processing"]["startup_analysis_completed"] = True

        # Save the startup analysis results
        self.save_state(preserve_interruption_state=False)

        log.info("✅ STARTUP ANALYSIS: Completed comprehensive state analysis")
        return self.state_data.get("gap_processing", {}).get("category_completion_status", {})

    def force_cache_rebuild(self, reason: str = "manual_request"):
        """
        🚨 REVERSE GAP POLICY: Explicitly force cache rebuild and reset resume index
        This should only be called when intentionally rebuilding the cache
        """
        log.info(f"🔄 FORCE CACHE REBUILD: {reason}")
        self.state_data["force_cache_rebuild"] = True
        self.state_data["resumption_index"] = 0
        self.state_data["progress_index"] = 0
        self.state_data["resume_reason"] = f"force_rebuild_{reason}"
        self.state_data["processing_status"] = "FRESH_CATEGORIES"

        # Clear startup completion to trigger fresh analysis
        self._startup_completed = False
        self.state_data["gap_processing"]["startup_analysis_completed"] = False

        log.info("✅ Cache rebuild forced - resumption_index reset to 0")

    def validate_and_repair_state(self) -> Tuple[bool, List[str]]:
        """
        🚨 STATE VALIDATION: Validate state consistency and repair issues
        Returns (is_valid, repairs_made)
        """
        repairs_made = []

        # Ensure required keys exist
        required_keys = [
            "resumption_index",
            "progress_index",
            "total_products",
            "processing_status",
        ]
        for key in required_keys:
            if key not in self.state_data:
                self.state_data[key] = (
                    0 if key.endswith("_index") or key == "total_products" else "initialized"
                )
                repairs_made.append(f"Added missing key: {key}")

        # Ensure resumption_index is within bounds and monotonic
        resumption_index = self.state_data.get("resumption_index", 0)
        total_products = self.state_data.get("total_products", 0)

        if resumption_index < 0:
            self.state_data["resumption_index"] = 0
            repairs_made.append("Fixed negative resumption_index")

        if total_products > 0 and resumption_index > total_products:
            self.state_data["resumption_index"] = total_products
            repairs_made.append(
                f"Fixed resumption_index bounds: {resumption_index} -> {total_products}"
            )

        # Ensure gap_processing structure exists
        if "gap_processing" not in self.state_data:
            self.state_data["gap_processing"] = {
                "reverse_gap_detected": False,
                "startup_analysis_completed": False,
            }
            repairs_made.append("Added missing gap_processing structure")

        # Ensure system_progression exists for breadcrumbs
        if "system_progression" not in self.state_data:
            self.state_data["system_progression"] = {
                "current_phase": "supplier",
                "current_category_index": 0,
                "current_category_url": "",
                "total_categories": 0,
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 0,
                "supplier_extraction_resumption_index": resumption_index,
                "amazon_analysis_resumption_index": 0,
            }
            repairs_made.append("Added missing system_progression structure")

        # Log repairs if any were made
        if repairs_made:
            log.info(f"State repaired: {', '.join(repairs_made)}")

        return len(repairs_made) == 0, repairs_made

    def update_discovered_products_in_category(self, category_url: str, discovered_count: int):
        """
        🚨 CRITICAL FIX 4: Update category totals with real-time scraping discoveries
        This method should be called when the scraper discovers more products than expected
        """
        current_total = self.state_data["supplier_extraction_progress"].get(
            "total_products_in_current_category", 0
        )

        if discovered_count > current_total:
            log.info(
                f"🔍 REAL-TIME DISCOVERY: Category {category_url[:50]}... discovered {discovered_count} products (was {current_total})"
            )

            # Update the current category total
            self.state_data["supplier_extraction_progress"][
                "total_products_in_current_category"
            ] = discovered_count
            self.state_data["supplier_extraction_progress"][
                "discovered_products_in_current_category"
            ] = discovered_count
            # Use normalized URL for consistent key comparison
            from utils.normalization import normalize_url

            normalized_category_url = normalize_url(category_url)
            self.state_data["supplier_extraction_progress"][
                "current_category_url"
            ] = normalized_category_url
            self.state_data["supplier_extraction_progress"]["original_category_url"] = category_url

            # Update the category completion status if it exists
            if (
                "gap_processing" in self.state_data
                and "category_completion_status" in self.state_data["gap_processing"]
            ):
                if category_url in self.state_data["gap_processing"]["category_completion_status"]:
                    self.state_data["gap_processing"]["category_completion_status"][category_url][
                        "extracted"
                    ] = discovered_count
                    # Recalculate completion percentage
                    processed = self.state_data["gap_processing"]["category_completion_status"][
                        category_url
                    ].get("processed", 0)
                    completion_pct = (
                        (processed / discovered_count * 100) if discovered_count > 0 else 0
                    )
                    self.state_data["gap_processing"]["category_completion_status"][category_url][
                        "completion_pct"
                    ] = completion_pct

                    # Update status based on new completion
                    if processed >= discovered_count:
                        self.state_data["gap_processing"]["category_completion_status"][
                            category_url
                        ]["status"] = "FULLY_PROCESSED"
                    else:
                        self.state_data["gap_processing"]["category_completion_status"][
                            category_url
                        ]["status"] = "PARTIALLY_PROCESSED"

            # Save the updated discovery using atomic write for safety
            self.save_state_atomic()

            log.info(f"✅ REAL-TIME UPDATE: Category total updated to {discovered_count} products")

    def set_frozen_denominator(self, category_url: str, discovered_count: int):
        """
        🚨 STEP 3 FIX: Set frozen category denominator per run
        This method 'freezes' the category denominator for consistent tracking throughout the run
        """
        # Update the category total to the discovered count
        self.state_data["supplier_extraction_progress"][
            "total_products_in_current_category"
        ] = discovered_count
        self.state_data["supplier_extraction_progress"][
            "discovered_products_in_current_category"
        ] = discovered_count

        # Use normalized URL for consistent key comparison
        from utils.normalization import normalize_url

        normalized_category_url = normalize_url(category_url)
        self.state_data["supplier_extraction_progress"][
            "current_category_url"
        ] = normalized_category_url
        self.state_data["supplier_extraction_progress"]["original_category_url"] = category_url

        # Update system progression with frozen denominator
        sp = self.state_data.setdefault("system_progression", {})
        sp["total_products_in_current_category"] = discovered_count
        sp["current_category_url"] = normalized_category_url
        sp["original_category_url"] = category_url

        # Save the frozen denominator atomically
        self.save_state_atomic()

        log.info(
            f"🔒 FROZEN DENOMINATOR: Set to {discovered_count} products for category {category_url[:50]}..."
        )

    def correct_category_totals_realtime(self, category_url: str, actual_discovered: int):
        """Public wrapper for real-time category total correction.

        This method satisfies the design requirement to expose a
        ``correct_category_totals_realtime`` helper.  It delegates to
        ``update_discovered_products_in_category`` which performs the
        actual update and atomic save.
        """

        self.update_discovered_products_in_category(category_url, actual_discovered)

    def update_processing_progress(self, increment: int = 1, product_url: Optional[str] = None):
        """
        🚨 CRITICAL FIX 5: Update progress tracking AND resumption index for exact recovery
        This method updates both session progress and resumption point for interruption recovery
        """
        # Update progress counters
        # 🚨 CRITICAL FIX: Update ONLY system_progression as single source of truth
        sp = self.state_data.setdefault("system_progression", {})
        sp["current_product_index_in_category"] = (
            sp.get("current_product_index_in_category", 0) + increment
        )

        # Update session metrics for user display
        self.state_data["session_products_processed"] += increment

        # 🚨 CRITICAL FIX: Update resumption_index continuously for exact interruption recovery
        self.state_data["resumption_index"] += increment

        # Legacy compatibility: keep last_processed_index synced with resumption_index
        self.state_data["last_processed_index"] = self.state_data["resumption_index"]

        log.debug(
            f"📊 PROGRESS UPDATE: system_progression.current_product_index_in_category={sp['current_product_index_in_category']}, resumption={self.state_data['resumption_index']}, session={self.state_data['session_products_processed']}"
        )

    # === NEW PROGRESSION METHODS ===
    def initialize_category_processing(
        self, category_index: int, category_url: str, total_categories: int
    ):
        """Initialize tracking for a new category"""
        from utils.normalization import normalize_url

        normalized_category_url = normalize_url(category_url)

        sp = self.state_data.setdefault("system_progression", {})
        sp.update(
            {
                "current_phase": "supplier",
                "current_category_index": category_index,
                "current_category_url": normalized_category_url,
                "original_category_url": category_url,  # Keep original for reference
                "total_categories": total_categories,
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 0,
            }
        )
        self.save_state_atomic()

    def update_supplier_extraction_progress_new(self, product_url: str, increment: int = 1):
        """Update progress during supplier extraction phase"""
        sp = self.state_data.setdefault("system_progression", {})
        sp["current_phase"] = "supplier"
        sp["supplier_extraction_resumption_index"] = (
            sp.get("supplier_extraction_resumption_index", 0) + increment
        )
        sp["current_product_index_in_category"] = (
            sp.get("current_product_index_in_category", 0) + increment
        )

        ud = self.state_data.setdefault("user_display_metrics", {})
        ud["progress_count"] = ud.get("progress_count", 0) + increment

        # 🚨 REMOVED: processed_products tracking - hash search should use linking map + cached products only
        # Supplier extraction is intermediate step, not completion

        self.save_state_atomic()

    def update_amazon_analysis_progress_new(self, product_url: str, increment: int = 1):
        """Update progress during Amazon analysis phase"""
        sp = self.state_data.setdefault("system_progression", {})
        sp["current_phase"] = "amazon_analysis"
        sp["amazon_analysis_resumption_index"] = (
            sp.get("amazon_analysis_resumption_index", 0) + increment
        )

        ud = self.state_data.setdefault("user_display_metrics", {})
        ud["session_products_processed"] = ud.get("session_products_processed", 0) + increment

        # 🚨 REMOVED: processed_products tracking - completion is tracked in linking map only
        # Amazon analysis completion creates linking map entry (source of truth)

        self.save_state_atomic()

    def save_state(self, preserve_interruption_state: bool = True):
        """
        🚨 CRITICAL FIX 6: Save state WITHOUT performing reverse gap detection
        Args:
            preserve_interruption_state: If True, preserves current state for resumption
        """
        try:
            # Update timestamp
            self.state_data["last_updated"] = datetime.now(timezone.utc).isoformat()

            # 🚨 CRITICAL: Do NOT perform file-grounded recalculation here during processing
            # Only update from file-grounded data if this is not preserving interruption state
            if not preserve_interruption_state and not self._startup_completed:
                # This path should only be taken during startup or explicit recalculation
                file_grounded_data = self._calculate_file_grounded_totals()
                self.state_data["total_products"] = file_grounded_data["total_products"]
                self.state_data["successful_products"] = file_grounded_data["processed_products"]

            # Atomic save using the existing windows save guardian
            try:
                from utils.windows_save_guardian import WindowsSaveGuardian

                guardian = WindowsSaveGuardian()
                success = guardian.save_json_atomic(str(self.state_file_path), self.state_data)

                if success:
                    log.debug(f"✅ State saved successfully to {self.state_file_path}")
                else:
                    log.error(f"❌ Failed to save state to {self.state_file_path}")

            except ImportError:
                # Atomic fallback: write to temp then replace
                try:
                    dir_name = os.path.dirname(str(self.state_file_path)) or "."
                    fd, tmp_path = tempfile.mkstemp(
                        prefix="state_", suffix=".tmp", dir=dir_name, text=True
                    )
                    try:
                        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                            json.dump(self.state_data, tmp, indent=2, ensure_ascii=False)
                        os.replace(tmp_path, str(self.state_file_path))
                        log.debug(f"✅ State saved atomically (fallback) to {self.state_file_path}")
                    except Exception as e:
                        log.error(f"❌ Atomic fallback save failed: {e}")
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
                except Exception as e:
                    log.error(f"❌ Could not perform atomic fallback save: {e}")

        except Exception as e:
            log.error(f"❌ Failed to save state: {e}")

        sp = self.state_data.get("system_progression", {})
        phase = sp.get("current_phase", "unknown")
        cci = sp.get("current_category_index", 0)
        tc = sp.get("total_categories", 0)
        cpi = sp.get("current_product_index_in_category", 0)
        tpc = sp.get("total_products_in_current_category", 0)
        ccu = sp.get("current_category_url", "")

        # Emit resume breadcrumbs ONLY after frozen totals are explicitly committed
        frozen_ok = bool(sp.get("frozen_totals_committed", False))
        if not frozen_ok:
            log.debug("RESUME PTR suppressed: frozen_totals_committed=False")
            return
        if tc > 0 and tpc > 0:
            log.info(f"RESUME PTR: phase={phase} cat_idx={cci}/{tc} url={ccu} prod_idx={cpi}/{tpc}")
        elif tc > 0:
            log.info(f"RESUME PTR: phase={phase} cat_idx={cci}/{tc} url={ccu} prod_idx={cpi}/pending")

    def save_state_atomic(self):
        """Atomic save wrapper used by new progression methods"""
        self.save_state(preserve_interruption_state=True)

    @staticmethod
    def compute_supplier_config_hash(category_urls: List[str]) -> str:
        joined = "".join(sorted(category_urls or []))
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()

    def save(self, note: str = "") -> None:
        """Atomically save state with optional note."""
        self.save_state(preserve_interruption_state=True)
        if note:
            log.info(f"💾 ATOMIC SAVE ({note})")
        else:
            log.info("💾 ATOMIC SAVE")

    def save_debounced(self, note: str = "", min_interval: float = 2.0) -> None:
        now = time.time()
        if now - getattr(self, "_last_save_time", 0) < min_interval:
            return
        self._last_save_time = now
        self.save(note=note)

    def set_total_categories(self, n: int, cfg_hash: Optional[str] = None) -> None:
        """Set frozen total categories and optional config hash; mirror into system_progression."""
        try:
            n_int = int(n)
        except Exception:
            n_int = 0
        rs = self.state_data.setdefault("runtime_settings", {})
        rs["total_categories"] = n_int
        if cfg_hash:
            rs["supplier_config_hash"] = cfg_hash
        sp = self.state_data.setdefault("system_progression", {})
        sp["total_categories"] = n_int

    def mark_frozen_totals_committed(self) -> None:
        """Mark frozen totals as committed, enabling RESUME PTR logs."""
        sp = self.state_data.setdefault("system_progression", {})
        sp["frozen_totals_committed"] = True
        self.save_state_atomic()

    def commit_supplier_progress(self, *, cat_idx: int, prod_idx: int,
                                 total_cats: int, cat_url: str, total_prod_in_cat: int) -> None:
        """Atomic supplier-phase commit (category-relative cursor)."""
        sp = self.state_data.setdefault("system_progression", {})
        sp["current_phase"] = "supplier"
        sp["current_category_index"] = int(cat_idx)
        sp["total_categories"] = int(total_cats)
        sp["current_category_url"] = str(cat_url)
        sp["current_product_index_in_category"] = int(prod_idx)           # ✅ category-relative (last completed)
        sp["total_products_in_current_category"] = int(total_prod_in_cat) # ✅ frozen per category
        self.set_resumption_ptr(int(cat_idx), int(prod_idx) + 1)           # Store NEXT to process
        self.save_debounced("supplier-progress")
        self.log_resume_proof_after_commit("SUPPLIER")

    def commit_amazon_progress(self, *, cat_idx: int, queue_idx: int,
                               total_cats: int, cat_url: str, queue_len: int) -> None:
        """Atomic Amazon-phase commit (queue-relative cursor)."""
        sp = self.state_data.setdefault("system_progression", {})
        sp["current_phase"] = "amazon_analysis"
        sp["current_category_index"] = int(cat_idx)
        sp["total_categories"] = int(total_cats)
        sp["current_category_url"] = str(cat_url)
        sp["current_product_index_in_category"] = int(queue_idx)  # ✅ queue-relative
        sp["total_products_in_current_category"] = int(queue_len) # ✅ frozen queue length
        self.save_debounced("amazon-progress")
        self.log_resume_proof_after_commit("AMAZON")

    def commit_phase_switch(self, *, new_phase: str, reset_index: bool = True) -> None:
        """Switch processing phase with optional index reset."""
        sp = self.state_data.setdefault("system_progression", {})
        old = sp.get("current_phase", "supplier")
        sp["current_phase"] = str(new_phase)
        if reset_index:
            sp["current_product_index_in_category"] = 0
        log.info(f"🔄 PHASE TRANSITION: {old} → {new_phase}")
        self.save_state_atomic()
        self.log_resume_proof_after_commit("PHASE_SWITCH")

    def _authoritative_total_categories(self) -> int:
        """Get authoritative total categories count."""
        sp = self.state_data.get("system_progression", {})
        return sp.get("total_categories", 0)

    # (reverted) removed phase-scoped atomic commit helpers and frozen flag gating

    def set_resumption_ptr(self, cat_idx: int, prod_idx: int) -> None:
        """Set monotonic resumption pointer (category, product)."""
        sp = self.state_data.setdefault("system_progression", {})
        prev = sp.get("resumption_ptr", {"cat_idx": 0, "prod_idx": 0})
        prev_cat = int(prev.get("cat_idx", 0))
        prev_prod = int(prev.get("prod_idx", 0))
        inc_cat = int(cat_idx)
        inc_prod = int(prod_idx)
        if inc_cat < prev_cat:
            return
        if inc_cat == prev_cat:
            if inc_prod <= prev_prod:
                return
            sp["resumption_ptr"] = {"cat_idx": prev_cat, "prod_idx": inc_prod}
        else:
            sp["resumption_ptr"] = {"cat_idx": inc_cat, "prod_idx": inc_prod}

    def get_resumption_ptr(self) -> Tuple[int, int]:
        """Return resumption pointer (category, product)."""
        sp = self.state_data.get("system_progression", {})
        ptr = sp.get("resumption_ptr")
        if isinstance(ptr, dict):
            return int(ptr.get("cat_idx", 0)), int(ptr.get("prod_idx", 0))
        return 0, 0

    def update_progression_unified(
        self,
        current_category_index=None,
        current_product_index_in_category=None,
        supplier_resumption_index=None,  # NEW
        amazon_resumption_index=None,  # NEW
        current_phase=None,
        total_products_in_current_category=None,
        current_category_url=None,
        total_categories=None,
        **kwargs,
    ):
        """Extended unified progression with dual phase index tracking"""
        sp = self.state_data.setdefault("system_progression", {})

        # Update provided fields
        if current_category_index is not None:
            sp["current_category_index"] = current_category_index

        if current_product_index_in_category is not None:
            sp["current_product_index_in_category"] = current_product_index_in_category

        if total_products_in_current_category is not None:
            sp["total_products_in_current_category"] = total_products_in_current_category

        if current_phase is not None:
            old_phase = sp.get("current_phase")
            sp["current_phase"] = current_phase
            if old_phase != current_phase:
                log.info(f"🔄 PHASE TRANSITION: {old_phase} → {current_phase}")

        # 🚨 FIX 3: NEW - Phase-specific resumption indices
        if supplier_resumption_index is not None:
            sp["supplier_resumption_index"] = supplier_resumption_index
            log.debug(f"📊 SUPPLIER RESUME INDEX: {supplier_resumption_index}")

        if amazon_resumption_index is not None:
            sp["amazon_resumption_index"] = amazon_resumption_index
            log.debug(f"📊 AMAZON RESUME INDEX: {amazon_resumption_index}")

        if current_category_url is not None:
            # Normalize URL for consistent tracking
            try:
                from utils.normalization import normalize_url

                sp["current_category_url"] = normalize_url(current_category_url)
                sp["original_category_url"] = current_category_url
            except ImportError:
                # Fallback if normalization not available
                sp["current_category_url"] = current_category_url

        if total_categories is not None:
            sp["total_categories"] = total_categories

        # Update timestamp
        sp["last_updated"] = datetime.now(timezone.utc).isoformat()

        # 🚨 FIX 2: Cross-validate and mirror legacy view from system
        drift_magnitude = self._validate_state_synchronization()

        # Log the progression update for observability
        cat_idx = sp.get("current_category_index", 0)
        prod_idx = sp.get("current_product_index_in_category", 0)
        total_cats = sp.get("total_categories", 0)
        total_prods = sp.get("total_products_in_current_category", 0)
        phase = sp.get("current_phase", "unknown")

        log.debug(
            f"📊 PROGRESSION UPDATE: cat={cat_idx}/{total_cats} prod={prod_idx}/{total_prods} phase={phase}"
        )

        return drift_magnitude

    def _validate_state_synchronization(self):
        """Cross-validate system_progression and supplier_extraction_progress consistency"""

        sp = self.state_data.get("system_progression", {})
        legacy = self.state_data.get("supplier_extraction_progress", {})

        # Extract comparison values
        sp_category = sp.get("current_category_index", 0)
        legacy_category = legacy.get("current_category_index", 0)
        sp_product = sp.get("current_product_index_in_category", 0)
        legacy_product = legacy.get("current_product_index_in_category", 0)

        # Calculate drift magnitude
        category_drift = abs(sp_category - legacy_category)
        product_drift = abs(sp_product - legacy_product)
        total_drift = category_drift + product_drift

        # On first discrepancy, mirror legacy from system and suppress further drift noise
        if (category_drift > 0 or product_drift > 0) and not getattr(self, "_drift_mirrored_once", False):
            try:
                self._mirror_legacy_from_system()
                self._drift_mirrored_once = True
                log.info(
                    "🔄 LEGACY MIRRORING: Synchronized supplier_extraction_progress to system_progression"
                )
            except Exception:
                pass

        # Store drift metrics for monitoring
        self.state_data.setdefault("diagnostics", {})["state_drift"] = {
            "category_drift": category_drift,
            "product_drift": product_drift,
            "total_drift": total_drift,
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }

        return total_drift

    def _mirror_legacy_from_system(self) -> None:
        """Mirror key fields from system_progression into supplier_extraction_progress (display only)."""
        sp = self.state_data.setdefault("system_progression", {})
        legacy = self.state_data.setdefault("supplier_extraction_progress", {})
        legacy["current_category_index"] = int(sp.get("current_category_index", 0))
        legacy["total_categories"] = int(sp.get("total_categories", 0))
        legacy["current_product_index_in_category"] = int(
            sp.get("current_product_index_in_category", 0)
        )
        legacy["total_products_in_current_category"] = int(
            sp.get("total_products_in_current_category", 0)
        )
        legacy["current_category_url"] = sp.get("current_category_url", "")
        phase = sp.get("current_phase", "supplier")
        legacy["extraction_phase"] = (
            "products" if phase == "supplier" else ("amazon_analysis" if phase == "amazon_analysis" else str(phase))
        )

    def validate_loaded_state(self) -> None:
        """Clamp out-of-range indices and warn on contradictions; persist once atomically."""
        sp = self.state_data.setdefault("system_progression", {})

        # Clamp category index to max valid (0..total-1)
        try:
            total_cats = int(sp.get("total_categories", 1) or 1)
        except Exception:
            total_cats = 1
        try:
            ci = int(sp.get("current_category_index", 0))
        except Exception:
            ci = 0
        max_cat_index = max(0, total_cats - 1)
        if ci > max_cat_index:
            log.warning(
                f"⚠️ State validation: current_category_index {ci} > max_index {max_cat_index}; capping"
            )
            sp["current_category_index"] = max_cat_index

        # Clamp product index within category (0..tp-1)
        try:
            tp = int(sp.get("total_products_in_current_category", 0))
        except Exception:
            tp = 0
        try:
            pi = int(sp.get("current_product_index_in_category", 0))
        except Exception:
            pi = 0
        max_prod_index = max(0, tp - 1) if tp > 0 else 0
        if pi > max_prod_index:
            log.warning(
                f"⚠️ State validation: product_index {pi} > max_index {max_prod_index}; capping"
            )
            sp["current_product_index_in_category"] = max_prod_index

        # Simple contradiction: fresh-start with non-zero progress
        fs = bool(self.state_data.get("is_fresh_start", False))
        if fs and (
            (sp.get("current_category_index", 0) or 0) > 0
            or (sp.get("current_product_index_in_category", 0) or 0) > 0
        ):
            log.warning(
                "⚠️ Contradiction: is_fresh_start=True with non-zero progress; normalizing is_fresh_start=False"
            )
            self.state_data["is_fresh_start"] = False

        # Optional phase transition sanity (log-only)
        last = sp.get("last_phase")
        cur = sp.get("current_phase")
        allowed = {
            "supplier": {"amazon_analysis", "completed"},
            "amazon_analysis": {"supplier", "completed"},
            "completed": {"supplier"},
        }
        if last and cur and last != cur and last in allowed and cur not in allowed[last]:
            log.warning(f"⚠️ Phase transition {last} → {cur} not in allowed set")
        sp["last_phase"] = cur

        # Persist once
        self.save_state()

    def validate_and_repair_state(self) -> Tuple[bool, List[str]]:
        """
        Validate state consistency and repair issues automatically.

        Returns:
            Tuple[bool, List[str]]: (is_valid, repairs_made)
        """
        repairs_made = []
        is_valid = True

        # Ensure required keys exist
        required_keys = [
            "system_progression",
            "user_display_metrics",
            "supplier_extraction_progress",
        ]
        for key in required_keys:
            if key not in self.state_data:
                self.state_data[key] = {}
                repairs_made.append(f"Added missing key: {key}")
                is_valid = False

        # Validate system_progression structure
        sp = self.state_data.setdefault("system_progression", {})
        required_sp_keys = [
            "current_phase",
            "current_category_index",
            "current_category_url",
            "total_categories",
            "current_product_index_in_category",
            "total_products_in_current_category",
            "supplier_extraction_resumption_index",
            "amazon_analysis_resumption_index",
        ]

        for key in required_sp_keys:
            if key not in sp:
                default_value = "" if "url" in key else 0
                sp[key] = default_value
                repairs_made.append(f"Added missing system_progression key: {key}")
                is_valid = False

        # Validate bounds and monotonic progression
        total_categories = sp.get("total_categories", 0)
        current_category_index = sp.get("current_category_index", 0)

        if current_category_index > total_categories:
            sp["current_category_index"] = max(total_categories - 1, 0)
            repairs_made.append(
                f"Fixed category index bounds: {current_category_index} -> {sp['current_category_index']}"
            )
            is_valid = False

        total_products_in_category = sp.get("total_products_in_current_category", 0)
        current_product_index = sp.get("current_product_index_in_category", 0)

        if current_product_index > total_products_in_category:
            sp["current_product_index_in_category"] = 0
            repairs_made.append(f"Fixed product index bounds: {current_product_index} -> 0")
            is_valid = False

        # Ensure resumption indices are monotonic
        supplier_resumption = sp.get("supplier_extraction_resumption_index", 0)
        amazon_resumption = sp.get("amazon_analysis_resumption_index", 0)

        if supplier_resumption < 0:
            sp["supplier_extraction_resumption_index"] = 0
            repairs_made.append("Fixed negative supplier resumption index")
            is_valid = False

        if amazon_resumption < 0:
            sp["amazon_analysis_resumption_index"] = 0
            repairs_made.append("Fixed negative Amazon resumption index")
            is_valid = False

        # Ensure supplier_extraction_progress keys exist
        sep = self.state_data.setdefault("supplier_extraction_progress", {})
        required_sep_keys = [
            "total_products_in_current_category",
            "discovered_products_in_current_category",
            "current_category_url",
            "current_product_index_in_category",
        ]

        for key in required_sep_keys:
            if key not in sep:
                default_value = "" if "url" in key else 0
                sep[key] = default_value
                repairs_made.append(f"Added missing supplier_extraction_progress key: {key}")
                is_valid = False

        # Sync progress counters if they're inconsistent
        if "resumption_index" not in self.state_data:
            self.state_data["resumption_index"] = supplier_resumption
            repairs_made.append("Synced resumption_index with supplier_extraction_resumption_index")
            is_valid = False

        # Log repairs if any were made
        if repairs_made:
            log.info(f"State repaired: {'; '.join(repairs_made)}")

        return is_valid, repairs_made

    def _calculate_file_grounded_totals(self) -> Dict[str, Any]:
        """
        Calculate all totals by reading actual files on disk
        Returns accurate counts based on real-time file contents
        """
        try:
            # Initialize counters
            file_grounded_data = {
                "total_products": 0,
                "processed_products": 0,
                "category_completion_status": {},
                "linking_map_count": 0,
                "cache_file_exists": False,
                "linking_map_exists": False,
                "total_categories": 0,
                "current_category_analysis": {},
            }

            # Calculate project root path relative to current file location
            current_dir = Path(__file__).parent.parent

            # Path to product cache file - use hyphenated domain format
            hyphenated_supplier = self.supplier_name.replace(".", "-")
            cache_file_path = (
                current_dir
                / "OUTPUTS"
                / "cached_products"
                / f"{hyphenated_supplier}_products_cache.json"
            )

            # Path to linking map file - use dotted domain format
            supplier_domain = self.supplier_name.replace("-", ".")
            linking_map_path = (
                current_dir
                / "OUTPUTS"
                / "FBA_ANALYSIS"
                / "linking_maps"
                / supplier_domain
                / "linking_map.json"
            )

            # 🚨 CRITICAL FIX: Exclude metadata entries from product count
            if cache_file_path.exists():
                file_grounded_data["cache_file_exists"] = True
                try:
                    with open(cache_file_path, "r", encoding="utf-8") as f:
                        product_cache = json.load(f)

                    # Filter out metadata entries
                    actual_products = [
                        p
                        for p in product_cache
                        if isinstance(p, dict) and not p.get("_cache_metadata")
                    ]
                    file_grounded_data["total_products"] = len(actual_products)

                    log.info(
                        f"File-grounded calculation: Found {len(actual_products)} actual products in cache (total entries: {len(product_cache)})"
                    )
                except Exception as e:
                    log.warning(f"Failed to read product cache: {e}")

            # Read linking map to get processed count
            if linking_map_path.exists():
                file_grounded_data["linking_map_exists"] = True
                try:
                    with open(linking_map_path, "r", encoding="utf-8") as f:
                        linking_map = json.load(f)
                    file_grounded_data["linking_map_count"] = len(linking_map)
                    file_grounded_data["processed_products"] = len(linking_map)
                    log.info(
                        f"File-grounded calculation: Found {len(linking_map)} processed products in linking map"
                    )
                except Exception as e:
                    log.warning(f"Failed to read linking map: {e}")

            # Calculate category completion from existing files
            file_grounded_data[
                "category_completion_status"
            ] = self._calculate_startup_category_analysis(
                cache_file_path, linking_map_path, current_dir
            )

            # Load config to get total categories
            config_path = current_dir / "config" / "poundwholesale_categories.json"
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                    if isinstance(config_data, list):
                        file_grounded_data["total_categories"] = len(config_data)
                    elif isinstance(config_data, dict) and "category_urls" in config_data:
                        file_grounded_data["total_categories"] = len(config_data["category_urls"])
                    log.info(
                        f"File-grounded calculation: Found {file_grounded_data['total_categories']} categories in config"
                    )
                except Exception as e:
                    log.warning(f"Failed to read config file: {e}")

            return file_grounded_data

        except Exception as e:
            log.error(f"Failed to calculate file-grounded totals: {e}")
            return {
                "total_products": self.state_data.get("total_products", 0),
                "processed_products": self.state_data.get("last_processed_index", 0),
                "category_completion_status": {},
                "linking_map_count": 0,
                "cache_file_exists": False,
                "linking_map_exists": False,
                "total_categories": 0,
                "current_category_analysis": {},
            }

    def _calculate_startup_category_analysis(
        self, cache_file_path: Path, linking_map_path: Path, current_dir: Path
    ) -> Dict[str, Any]:
        """
        Calculate category completion status from existing cache and linking map files
        """
        try:
            category_completion = {}

            # Load cache data
            cache_data = []
            if cache_file_path.exists():
                with open(cache_file_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

            # Load linking map data
            linking_data = []
            if linking_map_path.exists():
                with open(linking_map_path, "r", encoding="utf-8") as f:
                    linking_data = json.load(f)

            # Build category extraction status from cache
            extracted_categories = defaultdict(list)
            for product in cache_data:
                if (
                    isinstance(product, dict)
                    and "source_url" in product
                    and "url" in product
                    and not product.get("_cache_metadata")
                ):
                    extracted_categories[product["source_url"]].append(product["url"])

            # Build processed product mapping from linking map
            processed_products = set()
            for entry in linking_data:
                if isinstance(entry, dict) and "supplier_url" in entry:
                    processed_products.add(entry["supplier_url"])

            # Calculate category completion status
            for category_url, product_urls in extracted_categories.items():
                extracted_count = len(product_urls)
                processed_count = len([url for url in product_urls if url in processed_products])
                completion_pct = (
                    (processed_count / extracted_count * 100) if extracted_count > 0 else 0
                )

                if processed_count >= extracted_count:
                    status = "FULLY_PROCESSED"
                elif processed_count > 0:
                    status = "PARTIALLY_PROCESSED"
                else:
                    status = "EXTRACTED_ONLY"

                category_completion[category_url] = {
                    "extracted": extracted_count,
                    "processed": processed_count,
                    "completion_pct": completion_pct,
                    "status": status,
                }

            log.info(
                f"Startup category analysis: Calculated completion for {len(category_completion)} categories"
            )
            return category_completion

        except Exception as e:
            log.warning(f"Failed to calculate startup category analysis: {e}")
            return {}

    def _calculate_current_category_metrics(
        self, file_grounded_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🚨 CRITICAL FIX 7: Calculate current category metrics with correct indexing
        Returns metrics for supplier_extraction_progress with proper category index calculation
        """
        try:
            category_completion = file_grounded_data.get("category_completion_status", {})
            total_categories = file_grounded_data.get("total_categories", 0)

            # Find the current category that needs processing
            current_category_url = ""
            current_category_index = 0

            # 🚨 CRITICAL FIX: Load config file to get proper category order and index
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config" / "poundwholesale_categories.json"

            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)

                    # Get category URLs in config order
                    if isinstance(config_data, list):
                        config_urls = config_data
                    elif isinstance(config_data, dict) and "category_urls" in config_data:
                        config_urls = config_data["category_urls"]
                    else:
                        config_urls = []

                    # Find current category based on config order and processing status
                    priority_order = ["EXTRACTED_ONLY", "PARTIALLY_PROCESSED", "FULLY_PROCESSED"]

                    for status in priority_order:
                        for i, config_url in enumerate(config_urls):
                            if (
                                config_url in category_completion
                                and category_completion[config_url].get("status") == status
                            ):
                                current_category_url = config_url
                                current_category_index = (
                                    i  # 🚨 FIXED: Use actual index from config file
                                )
                                break
                        if current_category_url:
                            break

                except Exception as e:
                    log.warning(f"Failed to read config for category indexing: {e}")

            # Calculate current category metrics
            current_category_info = category_completion.get(current_category_url, {})
            total_products_in_current_category = current_category_info.get("extracted", 0)
            current_product_index_in_category = current_category_info.get("processed", 0)

            # Count completed categories
            completed_categories = []
            for url, info in category_completion.items():
                if info.get("status") == "FULLY_PROCESSED":
                    completed_categories.append(url)

            # Determine extraction phase based on state
            if file_grounded_data.get("linking_map_count", 0) > file_grounded_data.get(
                "total_products", 0
            ):
                extraction_phase = "fresh_categories"
            elif current_product_index_in_category < total_products_in_current_category:
                extraction_phase = "amazon_analysis"
            else:
                extraction_phase = "products"

            return {
                "current_category_url": current_category_url,
                "current_category_index": current_category_index,  # 🚨 FIXED: Correct index from config
                "total_categories": total_categories,
                "total_products_in_current_category": total_products_in_current_category,
                "current_product_index_in_category": current_product_index_in_category,
                "extraction_phase": extraction_phase,
                "last_completed_category": completed_categories[-1] if completed_categories else "",
                "categories_completed": completed_categories,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            log.error(f"Failed to calculate current category metrics: {e}")
            return {}

    def mark_category_completed(self, category_url: str):
        """Mark a category as completed - resumption_index now updates continuously"""
        # Update category completion status
        if (
            "gap_processing" in self.state_data
            and "category_completion_status" in self.state_data["gap_processing"]
        ):
            if category_url in self.state_data["gap_processing"]["category_completion_status"]:
                self.state_data["gap_processing"]["category_completion_status"][category_url][
                    "status"
                ] = "FULLY_PROCESSED"
                self.state_data["gap_processing"]["category_completion_status"][category_url][
                    "completion_pct"
                ] = 100.0

        # Add to completed categories
        if (
            category_url
            not in self.state_data["supplier_extraction_progress"]["categories_completed"]
        ):
            self.state_data["supplier_extraction_progress"]["categories_completed"].append(
                category_url
            )

        # Update last completed category
        self.state_data["supplier_extraction_progress"]["last_completed_category"] = category_url

        # Note: resumption_index now updates continuously via update_processing_progress()
        # No need to update it here as it's always current

        log.info(f"✅ Category marked as completed: {category_url[:50]}...")

    def get_resumption_index(self) -> int:
        """Get the index from which to resume processing"""
        return self.state_data.get("resumption_index", 0)

    def get_current_progress(self) -> Dict[str, int]:
        """Get current session progress"""
        return {
            "resumption_index": self.state_data.get("resumption_index", 0),
            "progress_index": self.state_data.get("progress_index", 0),
            "session_products_processed": self.state_data.get("session_products_processed", 0),
            "last_processed_index": self.state_data.get("last_processed_index", 0),
        }

    # === WORKFLOW COMPATIBILITY METHODS ===
    # These methods provide compatibility with the existing workflow

    def update_processing_index(self, current_index: int, total_products: int):
        """Update processing index (compatibility method)"""
        self.state_data["last_processed_index"] = current_index
        self.state_data["progress_index"] = current_index
        self.state_data["total_products"] = total_products

    def start_processing(self, config_hash: str, runtime_settings: Dict[str, Any]):
        """Start processing session"""
        self.state_data["config_hash"] = config_hash
        self.state_data["runtime_settings"] = runtime_settings
        self.state_data["processing_status"] = "active"
        self.state_data["session_start_time"] = datetime.now(timezone.utc).isoformat()

    def complete_processing(self):
        """Mark processing as complete"""
        self.state_data["processing_status"] = "completed"
        self.state_data["session_end_time"] = datetime.now(timezone.utc).isoformat()
        self.save_state()

    def is_product_processed(self, product_url: str) -> bool:
        """
        🚨 DEPRECATED: This method should not be used - linking map is the source of truth
        Hash lookup should check linking map directly, not processing state

        Returns False to ensure products flow through correct filtering workflow
        """
        # 🚨 Always return False - linking map filtering is the correct approach
        return False

    def mark_product_processed(self, product_url: str, status: str):
        """
        🚨 DEPRECATED: This method should not be used - linking map entries are the completion signal
        Processing completion is tracked via linking map entries, not processing state

        This method is now a no-op to prevent incorrect state tracking
        """
        # 🚨 No-op: completion tracking happens in linking map, not processing state
        pass

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state"""
        return {
            "supplier_name": self.supplier_name,
            "processing_status": self.state_data.get("processing_status", "not_started"),
            "resumption_index": self.state_data.get("resumption_index", 0),
            "progress_index": self.state_data.get("progress_index", 0),
            "session_products_processed": self.state_data.get("session_products_processed", 0),
            # 🚨 REMOVED: processed_products count - linking map is source of truth
            "last_update": self.state_data.get("last_update"),
        }

    def start_gap_processing(
        self, gap_size: int, linking_map_count: int, supplier_cache_count: int
    ):
        """Start gap processing session"""
        self.state_data["gap_processing"] = {
            "status": "active",
            "gap_size": gap_size,
            "linking_map_count": linking_map_count,
            "supplier_cache_count": supplier_cache_count,
            "start_time": datetime.now(timezone.utc).isoformat(),
        }

    def complete_gap_processing(self):
        """Complete gap processing session"""
        if "gap_processing" in self.state_data:
            self.state_data["gap_processing"]["status"] = "completed"
            self.state_data["gap_processing"]["end_time"] = datetime.now(timezone.utc).isoformat()

    def update_gap_processing_progress(self, processed_count: int, total_gap: int):
        """Update gap processing progress"""
        if "gap_processing" not in self.state_data:
            self.state_data["gap_processing"] = {}

        self.state_data["gap_processing"]["processed_count"] = processed_count
        self.state_data["gap_processing"]["total_gap"] = total_gap
        self.state_data["gap_processing"]["last_update"] = datetime.now(timezone.utc).isoformat()

    def update_supplier_extraction_progress(
        self,
        category_index: int,
        total_categories: int,
        subcategory_index: int = None,
        total_subcategories: int = None,
        batch_number: int = None,
        total_batches: int = None,
        category_url: str = None,
        extraction_phase: str = None,
    ):
        """Update only system_progression; mirror legacy view and persist (debounced)."""
        sp = self.state_data.setdefault("system_progression", {})
        if category_index is not None:
            try:
                sp["current_category_index"] = max(0, int(category_index))
            except Exception:
                sp["current_category_index"] = 0
        if extraction_phase is not None:
            phase_map = {
                "fresh_categories": "supplier",
                "amazon_analysis": "amazon_analysis",
                "completed": "completed",
            }
            sp["current_phase"] = phase_map.get(str(extraction_phase), str(extraction_phase))
        if category_url is not None:
            try:
                from utils.normalization import normalize_url

                sp["current_category_url"] = normalize_url(category_url)
                sp["original_category_url"] = category_url
            except Exception:
                sp["current_category_url"] = category_url
        if total_categories is not None:
            try:
                sp["total_categories"] = max(1, int(total_categories))
            except Exception:
                sp["total_categories"] = max(1, sp.get("total_categories", 1))
        # Mirror and save (debounced)
        try:
            self._mirror_legacy_from_system()
        except Exception:
            pass
        self.save_debounced(note="progress", min_interval=0.3)

    def update_success_metrics(self, amazon_success: bool, profitable: bool, profit: float = 0):
        """Update success metrics"""
        metrics = self.state_data.get(
            "success_metrics",
            {"amazon_extractions": 0, "profitable_products": 0, "total_profit": 0},
        )

        if amazon_success:
            metrics["amazon_extractions"] += 1

        if profitable:
            metrics["profitable_products"] += 1
            metrics["total_profit"] += profit

        self.state_data["success_metrics"] = metrics

    def log_resume_proof_after_commit(self, commit_type: str) -> None:
        """RESUME PROOF LOG 2: LOG after each atomic commit with current state summary."""
        if hasattr(self, "_log") and self._log:
            sp = self.state_data.setdefault("system_progression", {})
            cat_idx = sp.get("current_category_index", 0)
            prod_idx = sp.get("current_product_index_in_category", 0)
            total_cats = sp.get("total_categories", 0)
            total_prod = sp.get("total_products_in_current_category", 0)
            phase = sp.get("current_phase", "supplier")
            
            self._log.info(f"📋 RESUME PROOF ({commit_type}): cat={cat_idx}/{total_cats} prod={prod_idx}/{total_prod} phase={phase}")
        else:
            # Fallback to module logger if instance logger not available
            import logging
            log = logging.getLogger(__name__)
            log.info(f"📋 RESUME PROOF ({commit_type}): State committed successfully")
