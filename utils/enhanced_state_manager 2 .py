"""
Enhanced State Manager - Comprehensive state management for Amazon FBA Agent System v3.5

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
try:
    from .path_manager import get_processing_state_path, path_manager
except ImportError:
    try:
        from utils.path_manager import get_processing_state_path, path_manager
    except ImportError:
        # For standalone testing
        import sys
        sys.path.append('.')
        from utils.path_manager import get_processing_state_path, path_manager

# Import category completion tracker for file-grounded calculations
try:
    from tools.category_completion_tracker import get_completion_metrics
except ImportError:
    # Fallback for different import paths
    try:
        import sys
        sys.path.append('.')
        from tools.category_completion_tracker import get_completion_metrics
    except ImportError:
        get_completion_metrics = None

log = logging.getLogger(__name__)


class EnhancedStateManager:
    """Enhanced state management with comprehensive tracking and recovery capabilities"""
    
    SCHEMA_VERSION = "1.0"
    
    def __init__(self, supplier_name: str):
        self.supplier_name = supplier_name
        self.state_file_path = get_processing_state_path(supplier_name)
        self.state_data = self._initialize_state()
        
    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize state structure with all required fields"""
        return {
            "schema_version": self.SCHEMA_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "supplier_name": self.supplier_name,
            "last_processed_index": 0,
            "total_products": 0,
            "processing_status": "initialized",  # initialized, in_progress, completed, error, paused
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
                "products_per_hour": 0
            },
            "metadata": {
                "version": "3.5",
                "config_hash": "",
                "runtime_settings": {},
                "system_info": {}
            },
            "processed_products": {},  # URL -> status mapping for product-level tracking
            "supplier_extraction_progress": {
                "current_category_index": 0,
                "total_categories": 0,
                "current_subcategory_index": 0,
                "total_subcategories_in_batch": 0,
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 0,
                "current_category_url": "",
                "current_batch_number": 0,
                "total_batches": 0,
                "extraction_phase": "not_started",  # not_started, categories, products, completed
                "last_completed_category": "",
                "categories_completed": [],
                "products_extracted_total": 0
            },
            "gap_processing": {
                "phase": "not_started",  # not_started, gap_processing, gap_completed
                "gap_products_total": 0,
                "gap_products_processed": 0,
                "gap_start_time": None,
                "gap_end_time": None,
                "gap_profitable_found": 0,
                "gap_last_processed_url": "",
                "category_completion_status": {}
            }
        }
    
    def load_state(self) -> bool:
        """
        Load existing state from file, with backward compatibility
        Returns True if state was loaded, False if starting fresh
        """
        if not self.state_file_path.exists():
            log.info(f"No existing state file found for {self.supplier_name}, starting fresh")
            return False
        
        try:
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            # Handle backward compatibility with simple state format
            if isinstance(loaded_data, dict) and "schema_version" not in loaded_data:
                log.info("Converting legacy state format to enhanced format")
                self._migrate_legacy_state(loaded_data)
            else:
                # Merge loaded data with initialized structure to handle missing fields
                self._merge_state_data(loaded_data)
            
            log.info(f"Loaded state for {self.supplier_name} - resuming from index {self.state_data['last_processed_index']}")
            return True
            
        except Exception as e:
            log.warning(f"Failed to load state file: {e}, starting fresh")
            return False
    
    def _migrate_legacy_state(self, legacy_data: Dict[str, Any]):
        """Migrate legacy state format to enhanced format"""
        self.state_data["last_processed_index"] = legacy_data.get("last_processed_index", 0)
        self.state_data["processing_status"] = "migrated_from_legacy"
        log.info("Successfully migrated legacy state format")
    
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
    
    def _calculate_file_grounded_totals(self) -> Dict[str, Any]:
        """
        Calculate all totals by reading actual files on disk
        Returns accurate counts based on real-time file contents
        ENHANCED: Now includes startup category analysis
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
                "current_category_analysis": {}
            }
            
            # Calculate project root path relative to current file location
            current_dir = Path(__file__).parent.parent
            
            # Path to product cache file - use hyphenated domain format
            hyphenated_supplier = self.supplier_name.replace('.', '-')
            cache_file_path = current_dir / "OUTPUTS" / "cached_products" / f"{hyphenated_supplier}_products_cache.json"
            
            # Path to linking map file
            supplier_domain = self.supplier_name.replace('-', '.')
            linking_map_path = current_dir / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / supplier_domain / "linking_map.json"
            
            # Read product cache to get total products
            if cache_file_path.exists():
                file_grounded_data["cache_file_exists"] = True
                try:
                    with open(cache_file_path, 'r', encoding='utf-8') as f:
                        product_cache = json.load(f)
                    file_grounded_data["total_products"] = len(product_cache)
                    log.info(f"File-grounded calculation: Found {len(product_cache)} products in cache")
                except Exception as e:
                    log.warning(f"Failed to read product cache: {e}")
            else:
                log.warning(f"Product cache file not found: {cache_file_path}")
            
            # Read linking map to get processed count
            if linking_map_path.exists():
                file_grounded_data["linking_map_exists"] = True
                try:
                    with open(linking_map_path, 'r', encoding='utf-8') as f:
                        linking_map = json.load(f)
                    file_grounded_data["linking_map_count"] = len(linking_map)
                    file_grounded_data["processed_products"] = len(linking_map)
                    log.info(f"File-grounded calculation: Found {len(linking_map)} processed products in linking map")
                except Exception as e:
                    log.warning(f"Failed to read linking map: {e}")
            else:
                log.warning(f"Linking map file not found: {linking_map_path}")
            
            # ENHANCED: Calculate category completion from existing files
            file_grounded_data["category_completion_status"] = self._calculate_startup_category_analysis(
                cache_file_path, linking_map_path, current_dir
            )
            
            # Load config to get total categories
            config_path = current_dir / "config" / "poundwholesale_categories.json"
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    if isinstance(config_data, list):
                        file_grounded_data["total_categories"] = len(config_data)
                    elif isinstance(config_data, dict) and "category_urls" in config_data:
                        file_grounded_data["total_categories"] = len(config_data["category_urls"])
                    log.info(f"File-grounded calculation: Found {file_grounded_data['total_categories']} categories in config")
                except Exception as e:
                    log.warning(f"Failed to read config file: {e}")
            
            # Get category completion status using the category_completion_tracker (fallback)
            if get_completion_metrics and not file_grounded_data["category_completion_status"]:
                try:
                    completion_metrics = get_completion_metrics(str(current_dir))
                    if completion_metrics and completion_metrics.get('category_completion_status'):
                        # Convert the detailed completion status to the format expected by state
                        for category_url, metrics in completion_metrics['category_completion_status'].items():
                            file_grounded_data["category_completion_status"][category_url] = {
                                "processed": metrics.get('processed_products', 0),
                                "total": metrics.get('total_products', 0),
                                "percent": metrics.get('completion_percentage', 0.0)
                            }
                        log.info(f"File-grounded calculation: Retrieved category completion for {len(file_grounded_data['category_completion_status'])} categories")
                    else:
                        log.warning("Category completion metrics returned empty or invalid data")
                except Exception as e:
                    log.warning(f"Failed to get category completion metrics: {e}")
            else:
                log.info(f"Using enhanced startup category analysis: {len(file_grounded_data['category_completion_status'])} categories")
            
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
                "current_category_analysis": {}
            }

    def _calculate_startup_category_analysis(self, cache_file_path: Path, linking_map_path: Path, current_dir: Path) -> Dict[str, Any]:
        """
        Calculate category completion status from existing cache and linking map files
        This provides immediate category progression visibility on system startup
        """
        try:
            category_completion = {}
            
            # Load cache data
            cache_data = []
            if cache_file_path.exists():
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
            # Load linking map data  
            linking_data = []
            if linking_map_path.exists():
                with open(linking_map_path, 'r', encoding='utf-8') as f:
                    linking_data = json.load(f)
                    
            # Build category extraction status from cache
            extracted_categories = defaultdict(list)
            for product in cache_data:
                if isinstance(product, dict) and 'source_url' in product and 'url' in product:
                    extracted_categories[product['source_url']].append(product['url'])
                    
            # Build processed product mapping from linking map
            processed_products = set()
            for entry in linking_data:
                if isinstance(entry, dict) and 'supplier_url' in entry:
                    processed_products.add(entry['supplier_url'])
                    
            # Calculate category completion status
            for category_url, product_urls in extracted_categories.items():
                extracted_count = len(product_urls)
                processed_count = sum(1 for url in product_urls if url in processed_products)
                completion_pct = (processed_count / extracted_count * 100) if extracted_count > 0 else 0
                
                if processed_count == 0:
                    status = "EXTRACTED_ONLY"
                elif processed_count == extracted_count:
                    status = "FULLY_PROCESSED"
                else:
                    status = "PARTIALLY_PROCESSED"
                    
                category_completion[category_url] = {
                    'extracted': extracted_count,
                    'processed': processed_count,
                    'completion_pct': round(completion_pct, 1),
                    'status': status
                }
                
            log.info(f"Startup category analysis: Calculated completion for {len(category_completion)} categories")
            return category_completion
            
        except Exception as e:
            log.error(f"Failed to calculate startup category analysis: {e}")
            return {}

    def _calculate_current_category_metrics(self, file_grounded_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate current category metrics from file-grounded data
        Returns metrics for supplier_extraction_progress
        """
        try:
            category_completion = file_grounded_data.get("category_completion_status", {})
            total_categories = file_grounded_data.get("total_categories", 0)
            
            # Find the category that needs processing (for current_category_url)
            current_category_url = ""
            current_category_index = 0
            
            # Priority: EXTRACTED_ONLY > PARTIALLY_PROCESSED > FULLY_PROCESSED
            priority_order = ["EXTRACTED_ONLY", "PARTIALLY_PROCESSED", "FULLY_PROCESSED"]
            
            for status in priority_order:
                for category_url, info in category_completion.items():
                    if info.get('status') == status:
                        current_category_url = category_url
                        break
                if current_category_url:
                    break
                    
            # Calculate current category metrics
            current_category_info = category_completion.get(current_category_url, {})
            total_products_in_current_category = current_category_info.get('extracted', 0)
            current_product_index_in_category = current_category_info.get('processed', 0)
            
            # Determine extraction phase based on reverse gap status
            if file_grounded_data.get("linking_map_count", 0) > file_grounded_data.get("total_products", 0):
                extraction_phase = "fresh_categories"
            elif current_product_index_in_category < total_products_in_current_category:
                extraction_phase = "amazon_analysis"
            else:
                extraction_phase = "products"
                
            return {
                "current_category_url": current_category_url,
                "current_category_index": current_category_index,
                "total_products_in_current_category": total_products_in_current_category,
                "current_product_index_in_category": current_product_index_in_category,
                "extraction_phase": extraction_phase,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            log.error(f"Failed to calculate current category metrics: {e}")
            return {}

    def update_category_progression(self, product_url: str, category_url: str, processed: bool = True):
        """
        Update category progression in real-time (every 1-5 entries as requested)
        This method is called from the main processing loop
        """
        try:
            # Ensure gap_processing structure exists
            if "gap_processing" not in self.state_data:
                self.state_data["gap_processing"] = {}
            if "category_completion_status" not in self.state_data["gap_processing"]:
                self.state_data["gap_processing"]["category_completion_status"] = {}
                
            # Update category completion status
            category_status = self.state_data["gap_processing"]["category_completion_status"]
            
            if category_url not in category_status:
                # Initialize new category
                category_status[category_url] = {
                    'extracted': 1,
                    'processed': 1 if processed else 0,
                    'completion_pct': 100.0 if processed else 0.0,
                    'status': 'FULLY_PROCESSED' if processed else 'EXTRACTED_ONLY'
                }
            else:
                # Update existing category
                if processed:
                    category_status[category_url]['processed'] += 1
                    
                # Recalculate completion percentage
                extracted = category_status[category_url]['extracted']
                processed_count = category_status[category_url]['processed']
                completion_pct = (processed_count / extracted * 100) if extracted > 0 else 0
                category_status[category_url]['completion_pct'] = round(completion_pct, 1)
                
                # Update status
                if processed_count == 0:
                    category_status[category_url]['status'] = "EXTRACTED_ONLY"
                elif processed_count == extracted:
                    category_status[category_url]['status'] = "FULLY_PROCESSED"
                else:
                    category_status[category_url]['status'] = "PARTIALLY_PROCESSED"
                    
            # Update supplier extraction progress
            if "supplier_extraction_progress" in self.state_data:
                progress = self.state_data["supplier_extraction_progress"]
                if progress.get("current_category_url") == category_url:
                    progress["current_product_index_in_category"] = category_status[category_url]['processed']
                    progress["total_products_in_current_category"] = category_status[category_url]['extracted']
                    
            log.debug(f"Updated category progression: {category_url} - {category_status[category_url]['processed']}/{category_status[category_url]['extracted']} ({category_status[category_url]['completion_pct']}%)")
            
        except Exception as e:
            log.error(f"Failed to update category progression: {e}")

    def save_state(self, force: bool = False):
        """
        Save state to file with atomic write operation and file-grounded calculations
        Args:
            force: Force save even if no changes detected
        """
        try:
            # STEP 1: Calculate file-grounded totals from actual files on disk
            file_grounded_data = self._calculate_file_grounded_totals()
            
            # STEP 2: Update state with accurate file-based totals
            self.state_data["total_products"] = file_grounded_data["total_products"]
            
            # Update processed index with reverse gap handling
            if file_grounded_data["linking_map_exists"]:
                # CRITICAL FIX: Handle reverse gap scenario correctly
                if file_grounded_data["linking_map_count"] > file_grounded_data["total_products"]:
                    # REVERSE GAP: More linking map entries than cache entries
                    # Set index to 0 for fresh category processing
                    self.state_data["last_processed_index"] = 0
                    self.state_data["processing_phase"] = "FRESH_CATEGORIES"
                    log.info(f"🔄 REVERSE GAP DETECTED: Linking map ({file_grounded_data['linking_map_count']}) > Cache ({file_grounded_data['total_products']})")
                    log.info(f"✅ Set last_processed_index = 0 for fresh category processing")
                else:
                    # NORMAL GAP: Set index to linking map count for gap processing
                    self.state_data["last_processed_index"] = file_grounded_data["linking_map_count"]
                    
                self.state_data["successful_products"] = file_grounded_data["processed_products"]
            
            # STEP 3: Update category completion status and file-grounded category metrics
            if file_grounded_data["category_completion_status"]:
                if "gap_processing" not in self.state_data:
                    self.state_data["gap_processing"] = {}
                self.state_data["gap_processing"]["category_completion_status"] = file_grounded_data["category_completion_status"]
            
            # ENHANCED: Update supplier extraction progress with file-grounded metrics
            if "supplier_extraction_progress" not in self.state_data:
                self.state_data["supplier_extraction_progress"] = {}
                
            # Update total categories from config file
            if file_grounded_data.get("total_categories", 0) > 0:
                self.state_data["supplier_extraction_progress"]["total_categories"] = file_grounded_data["total_categories"]
                
            # Calculate current category metrics from file-grounded data
            current_category_analysis = self._calculate_current_category_metrics(file_grounded_data)
            self.state_data["supplier_extraction_progress"].update(current_category_analysis)
            
            # STEP 4: Update metadata with file existence status
            if "metadata" not in self.state_data:
                self.state_data["metadata"] = {}
            self.state_data["metadata"]["file_grounded_stats"] = {
                "cache_file_exists": file_grounded_data["cache_file_exists"],
                "linking_map_exists": file_grounded_data["linking_map_exists"],
                "last_file_check": datetime.now(timezone.utc).isoformat()
            }
            
            # STEP 5: Update timestamp
            self.state_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # STEP 6: Log the file-grounded calculations for verification
            log.info(f"File-grounded state update - Total: {file_grounded_data['total_products']}, "
                    f"Processed: {file_grounded_data['processed_products']}, "
                    f"Categories: {len(file_grounded_data['category_completion_status'])}")
            
            # STEP 7: Ensure directory exists
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # STEP 8: Atomic write using temporary file
            temp_path = self.state_file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.state_data, f, indent=2, ensure_ascii=False)
            
            # STEP 9: Atomic replace
            os.replace(temp_path, self.state_file_path)
            
        except Exception as e:
            log.error(f"Failed to save state: {e}")
            # Cleanup temp file if it exists
            if 'temp_path' in locals() and temp_path.exists():
                temp_path.unlink()
    
    def update_processing_index(self, index: int, total_products: int = None):
        """Update the current processing index"""
        self.state_data["last_processed_index"] = index
        if total_products is not None:
            self.state_data["total_products"] = total_products
        self.state_data["processing_status"] = "in_progress"
        self.save_state()
    
    def add_category_performance(self, category_url: str, products_found: int, 
                               profitable_products: int = 0, avg_roi: float = 0.0):
        """Add or update category performance metrics"""
        self.state_data["category_performance"][category_url] = {
            "products_found": products_found,
            "profitable_products": profitable_products,
            "avg_roi_percent": avg_roi,
            "last_processed": datetime.now(timezone.utc).isoformat()
        }
        self.save_state()
    
    def log_error(self, error_type: str, error_message: str, product_index: int = None, 
                  context: Dict[str, Any] = None):
        """Log an error with context"""
        error_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "product_index": product_index,
            "context": context or {}
        }
        self.state_data["error_log"].append(error_entry)
        
        # Keep only last 100 errors to prevent file bloat
        if len(self.state_data["error_log"]) > 100:
            self.state_data["error_log"] = self.state_data["error_log"][-100:]
        
        self.save_state()
    
    def update_success_metrics(self, successful: bool, profitable: bool = False, 
                             profit_amount: float = 0.0):
        """Update success and profitability metrics"""
        if successful:
            self.state_data["successful_products"] += 1
        if profitable:
            self.state_data["profitable_products"] += 1
            self.state_data["total_profit_found"] += profit_amount
        self.save_state()
    
    def start_processing(self, config_hash: str = "", runtime_settings: Dict[str, Any] = None):
        """Mark processing as started with metadata"""
        self.state_data["processing_status"] = "in_progress"
        self.state_data["processing_statistics"]["start_time"] = datetime.now(timezone.utc).isoformat()
        self.state_data["metadata"]["config_hash"] = config_hash
        self.state_data["metadata"]["runtime_settings"] = runtime_settings or {}
        self.save_state()
    
    def complete_processing(self):
        """Mark processing as completed and calculate final statistics"""
        self.state_data["processing_status"] = "completed"
        end_time = datetime.now(timezone.utc)
        self.state_data["processing_statistics"]["end_time"] = end_time.isoformat()
        
        # Calculate runtime statistics
        if self.state_data["processing_statistics"]["start_time"]:
            start_time = datetime.fromisoformat(self.state_data["processing_statistics"]["start_time"].replace('Z', '+00:00'))
            runtime_seconds = (end_time - start_time).total_seconds()
            self.state_data["processing_statistics"]["total_runtime_seconds"] = runtime_seconds
            
            if self.state_data["successful_products"] > 0:
                self.state_data["processing_statistics"]["average_time_per_product"] = runtime_seconds / self.state_data["successful_products"]
                self.state_data["processing_statistics"]["products_per_hour"] = (self.state_data["successful_products"] * 3600) / runtime_seconds
        
        self.save_state()
    
    def mark_error_state(self, error_message: str):
        """Mark processing as failed due to error"""
        self.state_data["processing_status"] = "error"
        self.log_error("system_error", error_message)
    
    def get_category_performance_summary(self) -> str:
        """Generate category performance summary for AI re-ordering (like deprecated script)"""
        if not self.state_data["category_performance"]:
            return "CATEGORY PERFORMANCE: No previous performance data available."
        
        summary_lines = ["CATEGORY PERFORMANCE SUMMARY:"]
        sorted_categories = sorted(
            self.state_data["category_performance"].items(),
            key=lambda x: x[1].get('products_found', 0),
            reverse=True
        )[:5]
        
        for url, metrics in sorted_categories:
            products_found = metrics.get('products_found', 0)
            profitable_count = metrics.get('profitable_products', 0)
            avg_roi = metrics.get('avg_roi_percent', 0)
            summary_lines.append(
                f"- {url.split('/')[-1]}: {products_found} products, "
                f"{profitable_count} profitable, {avg_roi:.1f}% avg ROI"
            )
        
        return "\n".join(summary_lines)
    
    def should_resume(self) -> bool:
        """Check if processing should be resumed"""
        return (self.state_data["processing_status"] in ["in_progress", "paused"] and 
                self.state_data["last_processed_index"] > 0)
    
    def update_supplier_extraction_progress(self, category_index: int, total_categories: int,
                                          subcategory_index: int, total_subcategories: int,
                                          batch_number: int, total_batches: int,
                                          category_url: str, extraction_phase: str = "categories"):
        """Update detailed supplier extraction progress"""
        progress = self.state_data["supplier_extraction_progress"]
        progress.update({
            "current_category_index": category_index,
            "total_categories": total_categories,
            "current_subcategory_index": subcategory_index,
            "total_subcategories_in_batch": total_subcategories,
            "current_batch_number": batch_number,
            "total_batches": total_batches,
            "current_category_url": category_url,
            "extraction_phase": extraction_phase,
            "last_updated": datetime.now(timezone.utc).isoformat()
        })
        self.save_state()
    
    def update_product_extraction_progress(self, product_index: int, total_products_in_category: int,
                                         product_url: str = "", products_extracted_total: int = None):
        """Update product-level extraction progress within current category"""
        progress = self.state_data["supplier_extraction_progress"]
        progress.update({
            "current_product_index_in_category": product_index,
            "total_products_in_current_category": total_products_in_category,
            "extraction_phase": "products",
            "last_updated": datetime.now(timezone.utc).isoformat()
        })
        
        if products_extracted_total is not None:
            progress["products_extracted_total"] = products_extracted_total
            
        self.save_state()
    
    # 🚨 REMOVED: hard_reset method removed per user request
    # This method was causing inappropriate data loss by detecting non-empty cache files as empty
    # and clearing processing state when resumption should have occurred
    
    def complete_category_extraction(self, category_url: str, products_found: int):
        """Mark a category as completed during extraction"""
        progress = self.state_data["supplier_extraction_progress"]
        progress["last_completed_category"] = category_url
        progress["categories_completed"].append({
            "url": category_url,
            "products_found": products_found,
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Also update category performance for historical tracking
        self.add_category_performance(category_url, products_found)
        self.save_state()
    
    def get_extraction_resume_point(self) -> Dict[str, Any]:
        """Get detailed resume point for supplier extraction"""
        progress = self.state_data["supplier_extraction_progress"]
        return {
            "should_resume_extraction": progress.get("extraction_phase") in ["categories", "products"],
            "last_category_index": progress.get("current_category_index", 0),
            "last_subcategory_index": progress.get("current_subcategory_index", 0),
            "last_batch_number": progress.get("current_batch_number", 0),
            "completed_categories": progress.get("categories_completed", []),
            "extraction_phase": progress.get("extraction_phase", "not_started")
        }
    
    def get_resume_index(self) -> int:
        """Get the index to resume from"""
        return self.state_data["last_processed_index"]
    
    def get_file_grounded_metrics(self) -> Dict[str, Any]:
        """
        Get file-grounded metrics without saving state
        Useful for real-time progress monitoring
        """
        return self._calculate_file_grounded_totals()

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state for logging with file-grounded accuracy"""
        # Get real-time file-grounded metrics
        file_metrics = self._calculate_file_grounded_totals()
        
        return {
            "supplier": self.supplier_name,
            "status": self.state_data["processing_status"],
            "progress": f"{file_metrics['processed_products']}/{file_metrics['total_products']}",
            "progress_percent": round((file_metrics['processed_products'] / file_metrics['total_products'] * 100), 2) if file_metrics['total_products'] > 0 else 0,
            "successful": file_metrics["processed_products"],  # Use file-grounded count
            "profitable": self.state_data["profitable_products"],
            "total_profit": self.state_data["total_profit_found"],
            "categories_processed": len(self.state_data["category_performance"]),
            "categories_with_completion": len(file_metrics["category_completion_status"]),
            "errors": len(self.state_data["error_log"]),
            "file_grounded": True,  # Flag to indicate this uses real file data
            "cache_exists": file_metrics["cache_file_exists"],
            "linking_map_exists": file_metrics["linking_map_exists"]
        }
    
    def is_product_processed(self, url: str) -> bool:
        """Check if a product URL has been previously processed"""
        if not url:
            return False
        return url in self.state_data.get("processed_products", {})
    
    def is_all_products_failed(self) -> bool:
        """Check if all processed products have failed status"""
        processed_products = self.state_data.get("processed_products", {})
        if not processed_products:
            return False
        
        # Check if all products have failed status
        failed_statuses = ["failed_financial_calculation", "failed_amazon_extraction", "failed_supplier_extraction"]
        
        # CRITICAL FIX: Consider success statuses - these are NOT failures!
        success_statuses = ["completed_profitable", "completed_not_profitable", "completed"]
        
        all_failed = all(
            product_data.get("status", "") in failed_statuses 
            for product_data in processed_products.values()
        )
        
        # ADDITIONAL CHECK: If any products have success status, then NOT all failed
        any_successful = any(
            product_data.get("status", "") in success_statuses
            for product_data in processed_products.values()
        )
        
        return all_failed and len(processed_products) > 0 and not any_successful
    
    def auto_reset_failed_state(self) -> bool:
        """Automatically reset state if all products failed and no successful processing occurred"""
        if self.is_all_products_failed() and self.state_data.get("successful_products", 0) == 0:
            log.warning(f"🔄 AUTO-RESET: All {len(self.state_data.get('processed_products', {}))} products failed processing - resetting state for fresh run")
            # Reset critical state fields
            self.state_data["processing_status"] = "initialized"
            self.state_data["last_processed_index"] = 0
            self.state_data["processed_products"] = {}
            self.state_data["error_log"] = []
            self.state_data["processing_statistics"]["start_time"] = None
            self.state_data["processing_statistics"]["end_time"] = None
            self.save_state()
            return True
        return False
    
    def mark_product_processed(self, url: str, status: str, category_url: str = None) -> None:
        """
        Mark a product URL as processed with the given status
        ENHANCED: Now updates category progression in real-time
        """
        if not url:
            return
        if "processed_products" not in self.state_data:
            self.state_data["processed_products"] = {}
        
        self.state_data["processed_products"][url] = {
            "status": status,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # ENHANCED: Update category progression if category_url provided
        if category_url:
            self.update_category_progression(url, category_url, processed=True)
        else:
            # Try to determine category from existing data
            category_url = self._determine_category_from_product_url(url)
            if category_url:
                self.update_category_progression(url, category_url, processed=True)
        
        # Auto-save after marking product as processed
        self.save_state()

    def _determine_category_from_product_url(self, product_url: str) -> str:
        """
        Determine category URL from product URL by checking cache data
        """
        try:
            # Load cache to find category mapping
            current_dir = Path(__file__).parent.parent
            hyphenated_supplier = self.supplier_name.replace('.', '-')
            cache_file_path = current_dir / "OUTPUTS" / "cached_products" / f"{hyphenated_supplier}_products_cache.json"
            
            if cache_file_path.exists():
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                for product in cache_data:
                    if isinstance(product, dict) and product.get('url') == product_url:
                        return product.get('source_url', '')
                        
        except Exception as e:
            log.error(f"Failed to determine category from product URL: {e}")
            
        return ""

    def get_category_progression_for_url_reorganization(self) -> Dict[str, Any]:
        """
        Get category progression status for URL reorganization
        Returns data needed to reorganize config URLs
        """
        try:
            # Force recalculation of file-grounded data
            file_grounded_data = self._calculate_file_grounded_totals()
            category_completion = file_grounded_data.get("category_completion_status", {})
            
            # Organize categories by priority for URL reorganization
            reorganization_plan = {
                'top_priority': [],      # EXTRACTED_ONLY - need immediate processing
                'medium_priority': [],   # PARTIALLY_PROCESSED - finish these
                'move_to_bottom': [],    # FULLY_PROCESSED - final check later
                'summary': {
                    'total_categories': len(category_completion),
                    'extracted_only': 0,
                    'partially_processed': 0,
                    'fully_processed': 0
                }
            }
            
            for category_url, info in category_completion.items():
                category_data = {
                    'url': category_url,
                    'extracted': info.get('extracted', 0),
                    'processed': info.get('processed', 0),
                    'completion_pct': info.get('completion_pct', 0.0),
                    'status': info.get('status', 'UNKNOWN')
                }
                
                if info.get('status') == 'EXTRACTED_ONLY':
                    reorganization_plan['top_priority'].append(category_data)
                    reorganization_plan['summary']['extracted_only'] += 1
                elif info.get('status') == 'PARTIALLY_PROCESSED':
                    reorganization_plan['medium_priority'].append(category_data)
                    reorganization_plan['summary']['partially_processed'] += 1
                else:  # FULLY_PROCESSED
                    reorganization_plan['move_to_bottom'].append(category_data)
                    reorganization_plan['summary']['fully_processed'] += 1
                    
            # Sort by priority within each group
            reorganization_plan['top_priority'].sort(key=lambda x: -x['extracted'])  # Most products first
            reorganization_plan['medium_priority'].sort(key=lambda x: x['completion_pct'])  # Least complete first
            reorganization_plan['move_to_bottom'].sort(key=lambda x: -x['extracted'])  # Most products first
            
            log.info(f"Category progression for URL reorganization: {reorganization_plan['summary']}")
            return reorganization_plan
            
        except Exception as e:
            log.error(f"Failed to get category progression for URL reorganization: {e}")
            return {'top_priority': [], 'medium_priority': [], 'move_to_bottom': [], 'summary': {}}
    
    def start_gap_processing(self, gap_size: int = None, linking_map_count: int = None, cache_count: int = None):
        """Initialize gap processing phase with file-grounded calculations"""
        # Get file-grounded metrics if parameters not provided
        file_metrics = self._calculate_file_grounded_totals()
        
        # Use file-grounded values if parameters not explicitly provided
        actual_gap_size = gap_size if gap_size is not None else max(0, file_metrics["total_products"] - file_metrics["processed_products"])
        actual_linking_count = linking_map_count if linking_map_count is not None else file_metrics["linking_map_count"]
        actual_cache_count = cache_count if cache_count is not None else file_metrics["total_products"]
        
        self.state_data["gap_processing"].update({
            "phase": "gap_processing",
            "gap_products_total": actual_gap_size,
            "gap_products_processed": 0,
            "gap_start_time": datetime.now(timezone.utc).isoformat(),
            "gap_end_time": None,
            "gap_profitable_found": 0,
            "gap_last_processed_url": "",
            "category_completion_status": file_metrics["category_completion_status"]  # Use file-grounded status
        })
        
        # Update supplier extraction progress for gap processing
        self.state_data["supplier_extraction_progress"].update({
            "current_category_index": 0,  # Gap processing = category 0
            "total_categories": 0,  # Will be updated when fresh categories start
            "current_subcategory_index": 1,  # Gap processing = 1 batch
            "total_subcategories_in_batch": 1,  # All gap products in 1 batch
            "current_product_index_in_category": 0,  # Starting gap product
            "total_products_in_current_category": actual_gap_size,  # File-grounded gap size
            "current_category_url": "",  # No specific category during gap
            "current_batch_number": 1,  # Single gap batch
            "total_batches": 1,  # Single gap batch
            "extraction_phase": "amazon_analysis",  # Processing existing products
            "last_completed_category": "",  # None yet
            "categories_completed": [],  # None yet
            "products_extracted_total": actual_cache_count  # File-grounded total in cache
        })
        
        # Set initial processing index to file-grounded linking map count
        self.state_data["last_processed_index"] = actual_linking_count
        self.state_data["total_products"] = actual_cache_count
        
        log.info(f"Gap processing initialized with file-grounded metrics - Gap size: {actual_gap_size}, "
                f"Linking count: {actual_linking_count}, Cache count: {actual_cache_count}")
        
        self.save_state()
    
    def update_gap_processing_progress(self, processed_count: int, profitable_found: int = 0, 
                                     last_processed_url: str = ""):
        """Update gap processing progress"""
        gap_data = self.state_data["gap_processing"]
        gap_data["gap_products_processed"] = processed_count
        gap_data["gap_profitable_found"] = profitable_found
        gap_data["gap_last_processed_url"] = last_processed_url
        
        # Update supplier extraction progress
        progress = self.state_data["supplier_extraction_progress"]
        progress["current_product_index_in_category"] = processed_count
        
        # Update overall processing index
        linking_map_base = self.state_data["last_processed_index"] - gap_data["gap_products_total"]
        self.state_data["last_processed_index"] = linking_map_base + processed_count
        
        self.save_state()
    
    def complete_gap_processing(self):
        """Mark gap processing as completed"""
        gap_data = self.state_data["gap_processing"]
        gap_data["phase"] = "gap_completed"
        gap_data["gap_end_time"] = datetime.now(timezone.utc).isoformat()
        
        # Update supplier extraction progress to prepare for fresh categories
        progress = self.state_data["supplier_extraction_progress"]
        progress["extraction_phase"] = "products"  # Ready for fresh category processing
        progress["categories_completed"].append("gap_processing")  # Mark gap as completed
        progress["last_completed_category"] = "gap_processing"
        
        # Set processing index to total products (end of gap)
        self.state_data["last_processed_index"] = self.state_data["total_products"]
        
        self.save_state()
    
    def update_category_completion_status(self, category_url: str, processed: int, total: int):
        """Update category completion status in gap processing"""
        if "gap_processing" not in self.state_data:
            return
            
        percent = (processed / total * 100) if total > 0 else 0
        self.state_data["gap_processing"]["category_completion_status"][category_url] = {
            "processed": processed,
            "total": total,
            "percent": round(percent, 1)
        }
        self.save_state()
    
    def is_gap_processing_active(self) -> bool:
        """Check if gap processing is currently active"""
        return self.state_data.get("gap_processing", {}).get("phase") == "gap_processing"
    
    def get_gap_processing_status(self) -> Dict[str, Any]:
        """Get current gap processing status"""
        return self.state_data.get("gap_processing", {})


def migrate_legacy_state_files():
    """Migrate any legacy state files to new format"""
    log.info("Checking for legacy state files to migrate...")
    
    # Find legacy state files in old locations
    legacy_patterns = [
        "OUTPUTS/*_processing_state.json",
        "tools/OUTPUTS/*_processing_state.json", 
        "*_processing_state.json"
    ]
    
    migrated_count = 0
    for pattern in legacy_patterns:
        for legacy_file in Path(".").glob(pattern):
            try:
                # Extract supplier name from filename
                supplier_name = legacy_file.stem.replace("_processing_state", "")
                
                # Create enhanced state manager
                state_manager = EnhancedStateManager(supplier_name)
                
                # Load and migrate legacy data
                with open(legacy_file, 'r', encoding='utf-8') as f:
                    legacy_data = json.load(f)
                
                state_manager._migrate_legacy_state(legacy_data)
                state_manager.save_state()
                
                # Archive the old file
                archive_dir = Path("archive/migrated_states")
                archive_dir.mkdir(parents=True, exist_ok=True)
                archive_file = archive_dir / legacy_file.name
                legacy_file.rename(archive_file)
                
                log.info(f"Migrated {legacy_file} → {state_manager.state_file_path}")
                migrated_count += 1
                
            except Exception as e:
                log.error(f"Failed to migrate {legacy_file}: {e}")
    
    log.info(f"Migration complete: {migrated_count} files migrated")


if __name__ == "__main__":
    # Test the enhanced state manager
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test basic functionality
    state_manager = EnhancedStateManager("test-supplier")
    state_manager.start_processing("test_hash", {"test_mode": True})
    state_manager.update_processing_index(10, 100)
    state_manager.add_category_performance("/test-category", 25, 5, 45.2)
    state_manager.log_error("test_error", "This is a test error", 5)
    state_manager.update_success_metrics(True, True, 15.50)
    
    print("State Summary:", state_manager.get_state_summary())
    print("Category Performance:", state_manager.get_category_performance_summary())
    
    state_manager.complete_processing()
    print("✅ Enhanced state manager test completed")