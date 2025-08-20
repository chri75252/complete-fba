"""
Enhanced State Management Components
===================================

This module provides the foundation for enhanced state management with atomic operations,
invariant validation, and comprehensive monitoring capabilities.

Components:
- AtomicStateUpdater: Provides atomic operations for state updates
- ProductsExtractedCalculator: Implements missing calculation logic
- InvariantValidator: Validates state invariants and provides auto-repair
- StructuredLogger: Provides comprehensive logging for state operations
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod

# Import the existing state manager
try:
    from .fixed_enhanced_state_manager import FixedEnhancedStateManager
except ImportError:
    from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

log = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of an invariant validation check"""
    invariant_name: str
    is_valid: bool
    current_values: Dict[str, Any]
    expected_values: Dict[str, Any]
    severity: str  # "low" | "medium" | "high" | "critical"
    auto_repairable: bool
    repair_action: Optional[str] = None
    details: Optional[str] = None


@dataclass
class RepairResult:
    """Result of an auto-repair operation"""
    success: bool
    repairs_applied: List[str]
    backup_created: Optional[str] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class CalculationMetadata:
    """Metadata for calculation operations"""
    calculation_method: str  # "category_completion" | "processed_products"
    last_calculation_timestamp: datetime
    calculation_source_count: int
    validation_checksum: str


class TransactionManager:
    """Manages transactional state updates with rollback capability"""
    
    def __init__(self):
        self._transaction_stack = []
        self._lock = threading.Lock()
    
    def begin_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Begin a new transaction and return a snapshot for rollback"""
        with self._lock:
            snapshot = {
                'transaction_id': transaction_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {}
            }
            self._transaction_stack.append(snapshot)
            return snapshot
    
    def commit_transaction(self, transaction_id: str) -> bool:
        """Commit a transaction and remove it from the stack"""
        with self._lock:
            for i, transaction in enumerate(self._transaction_stack):
                if transaction['transaction_id'] == transaction_id:
                    self._transaction_stack.pop(i)
                    return True
            return False
    
    def rollback_transaction(self, transaction_id: str, state_data: Dict[str, Any]) -> bool:
        """Rollback a transaction using the stored snapshot"""
        with self._lock:
            for transaction in self._transaction_stack:
                if transaction['transaction_id'] == transaction_id:
                    # Restore data from snapshot
                    for key, value in transaction['data'].items():
                        state_data[key] = value
                    return True
            return False


class AtomicStateUpdater:
    """Provides atomic operations for related state field updates"""
    
    def __init__(self, state_manager: FixedEnhancedStateManager):
        self.state_manager = state_manager
        self.transaction_manager = TransactionManager()
        self.log = logging.getLogger(f"{__name__}.AtomicStateUpdater")
        
        # Performance and reliability settings
        self._max_retry_attempts = 3
        self._retry_delay_seconds = 0.1
        self._operation_timeout_seconds = 30
        self._metrics = {
            'successful_operations': 0,
            'failed_operations': 0,
            'rollback_operations': 0,
            'retry_operations': 0
        }
    
    def update_category_atomic(self, url: str, index: int, products_total: int) -> bool:
        """Atomically update all category-related fields with retry logic"""
        return self._execute_with_retry(
            self._update_category_atomic_impl,
            "category_update",
            url=url, index=index, products_total=products_total
        )
    
    def _update_category_atomic_impl(self, url: str, index: int, products_total: int) -> bool:
        """Implementation of atomic category update"""
        transaction_id = f"category_update_{int(time.time() * 1000)}"
        
        try:
            # Validate inputs
            if not url or not isinstance(url, str):
                raise ValueError(f"Invalid URL: {url}")
            if not isinstance(index, int) or index < 0:
                raise ValueError(f"Invalid index: {index}")
            if not isinstance(products_total, int) or products_total < 0:
                raise ValueError(f"Invalid products_total: {products_total}")
            
            # Begin transaction
            snapshot = self.transaction_manager.begin_transaction(transaction_id)
            
            # Store current values for rollback
            with self.state_manager._state_lock:
                snapshot['data'] = {
                    'supplier_extraction_progress': self.state_manager.state_data['supplier_extraction_progress'].copy(),
                    'system_progression': self.state_manager.state_data.get('system_progression', {}).copy(),
                    'last_updated': self.state_manager.state_data.get('last_updated')
                }
                
                # Update all related fields atomically
                sep = self.state_manager.state_data['supplier_extraction_progress']
                sep['current_category_url'] = url
                sep['current_category_index'] = index
                sep['products_extracted_total'] = products_total
                
                # Also update category-specific totals if this is a discovery update
                if products_total > 0:
                    sep['total_products_in_current_category'] = products_total
                    sep['discovered_products_in_current_category'] = products_total
                
                self.state_manager.state_data['last_updated'] = datetime.now(timezone.utc).isoformat()
                
                # Update system progression if it exists
                if 'system_progression' in self.state_manager.state_data:
                    sp = self.state_manager.state_data['system_progression']
                    sp['current_category_url'] = url
                    sp['current_category_index'] = index
                    sp['last_sync'] = datetime.now(timezone.utc).isoformat()
            
            # Commit transaction
            self.transaction_manager.commit_transaction(transaction_id)
            self._metrics['successful_operations'] += 1
            self.log.info(f"✅ Atomic category update: url={url[:50]}..., index={index}, total={products_total}")
            return True
            
        except Exception as e:
            # Rollback on error
            self.transaction_manager.rollback_transaction(transaction_id, self.state_manager.state_data)
            self._metrics['rollback_operations'] += 1
            self.log.error(f"❌ Atomic category update failed, rolled back: {e}")
            raise
    
    def update_progress_atomic(self, **kwargs) -> bool:
        """Atomically update progress-related fields with retry logic"""
        return self._execute_with_retry(
            self._update_progress_atomic_impl,
            "progress_update",
            **kwargs
        )
    
    def _update_progress_atomic_impl(self, **kwargs) -> bool:
        """Implementation of atomic progress update"""
        transaction_id = f"progress_update_{int(time.time() * 1000)}"
        
        try:
            # Validate inputs
            valid_fields = ['successful_products', 'profitable_products', 'total_profit_found']
            for key, value in kwargs.items():
                if key not in valid_fields:
                    raise ValueError(f"Invalid field: {key}")
                if key in ['successful_products', 'profitable_products'] and (not isinstance(value, int) or value < 0):
                    raise ValueError(f"Invalid value for {key}: {value}")
                if key == 'total_profit_found' and not isinstance(value, (int, float)):
                    raise ValueError(f"Invalid value for {key}: {value}")
            
            # Begin transaction
            snapshot = self.transaction_manager.begin_transaction(transaction_id)
            
            with self.state_manager._state_lock:
                # Store current values for rollback
                snapshot['data'] = {
                    'successful_products': self.state_manager.state_data.get('successful_products', 0),
                    'profitable_products': self.state_manager.state_data.get('profitable_products', 0),
                    'total_profit_found': self.state_manager.state_data.get('total_profit_found', 0.0),
                    'last_updated': self.state_manager.state_data.get('last_updated')
                }
                
                # Update fields atomically
                for key, value in kwargs.items():
                    if key in valid_fields:
                        self.state_manager.state_data[key] = value
                
                self.state_manager.state_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Commit transaction
            self.transaction_manager.commit_transaction(transaction_id)
            self._metrics['successful_operations'] += 1
            self.log.info(f"✅ Atomic progress update: {kwargs}")
            return True
            
        except Exception as e:
            # Rollback on error
            self.transaction_manager.rollback_transaction(transaction_id, self.state_manager.state_data)
            self._metrics['rollback_operations'] += 1
            self.log.error(f"❌ Atomic progress update failed, rolled back: {e}")
            raise
    
    def synchronize_sections_atomic(self) -> bool:
        """Atomically synchronize supplier_extraction_progress and system_progression with retry logic"""
        return self._execute_with_retry(
            self._synchronize_sections_atomic_impl,
            "section_sync"
        )
    
    def _synchronize_sections_atomic_impl(self) -> bool:
        """Implementation of atomic section synchronization"""
        transaction_id = f"sync_sections_{int(time.time() * 1000)}"
        
        try:
            # Begin transaction
            snapshot = self.transaction_manager.begin_transaction(transaction_id)
            
            with self.state_manager._state_lock:
                # Store current values for rollback
                snapshot['data'] = {
                    'supplier_extraction_progress': self.state_manager.state_data['supplier_extraction_progress'].copy(),
                    'system_progression': self.state_manager.state_data.get('system_progression', {}).copy()
                }
                
                # Get source values from supplier_extraction_progress
                source = self.state_manager.state_data['supplier_extraction_progress']
                
                # Ensure system_progression exists
                if 'system_progression' not in self.state_manager.state_data:
                    self.state_manager.state_data['system_progression'] = {}
                
                target = self.state_manager.state_data['system_progression']
                
                # Synchronize key fields
                sync_fields = [
                    'current_category_url',
                    'current_category_index',
                    'total_categories',
                    'current_product_index_in_category',
                    'total_products_in_current_category'
                ]
                
                for field in sync_fields:
                    if field in source:
                        target[field] = source[field]
                
                target['phase'] = 'supplier_extraction'
                target['last_sync'] = datetime.now(timezone.utc).isoformat()
            
            # Commit transaction
            self.transaction_manager.commit_transaction(transaction_id)
            self._metrics['successful_operations'] += 1
            self.log.info("✅ Atomic section synchronization completed")
            return True
            
        except Exception as e:
            # Rollback on error
            self.transaction_manager.rollback_transaction(transaction_id, self.state_manager.state_data)
            self._metrics['rollback_operations'] += 1
            self.log.error(f"❌ Atomic section synchronization failed, rolled back: {e}")
            raise
    
    def _execute_with_retry(self, operation_func, operation_name: str, *args, **kwargs) -> bool:
        """Execute an operation with retry logic"""
        last_exception = None
        
        for attempt in range(self._max_retry_attempts):
            try:
                result = operation_func(*args, **kwargs)
                # Only count as successful if this is not the first attempt (meaning we recovered from failure)
                if attempt > 0:
                    self.log.info(f"✅ {operation_name} succeeded after {attempt + 1} attempts")
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < self._max_retry_attempts - 1:
                    self._metrics['retry_operations'] += 1
                    self.log.warning(f"⚠️ {operation_name} attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(self._retry_delay_seconds * (attempt + 1))  # Exponential backoff
                else:
                    self.log.error(f"❌ {operation_name} failed after {self._max_retry_attempts} attempts: {e}")
        
        # All retries failed
        self._metrics['failed_operations'] += 1
        return False
    
    def update_progress_incremental_atomic(self, progress_index_inc: int = 0, session_products_processed_inc: int = 0,
                                         resumption_index_inc: int = 0, current_product_index_in_category_inc: int = 0,
                                         **kwargs) -> bool:
        """Atomically update progress-related fields with incremental updates"""
        return self._execute_with_retry(
            self._update_progress_incremental_impl,
            "progress_incremental_update",
            progress_index_inc=progress_index_inc,
            session_products_processed_inc=session_products_processed_inc,
            resumption_index_inc=resumption_index_inc,
            current_product_index_in_category_inc=current_product_index_in_category_inc,
            **kwargs
        )
    
    def _update_progress_incremental_impl(self, progress_index_inc: int = 0, session_products_processed_inc: int = 0,
                                        resumption_index_inc: int = 0, current_product_index_in_category_inc: int = 0,
                                        **kwargs) -> bool:
        """Implementation of atomic incremental progress update"""
        transaction_id = f"progress_incremental_{int(time.time() * 1000)}"
        
        try:
            # Begin transaction
            snapshot = self.transaction_manager.begin_transaction(transaction_id)
            
            with self.state_manager._state_lock:
                # Store current values for rollback
                snapshot['data'] = {
                    'progress_index': self.state_manager.state_data.get('progress_index', 0),
                    'session_products_processed': self.state_manager.state_data.get('session_products_processed', 0),
                    'resumption_index': self.state_manager.state_data.get('resumption_index', 0),
                    'supplier_extraction_progress': self.state_manager.state_data['supplier_extraction_progress'].copy(),
                    'last_updated': self.state_manager.state_data.get('last_updated')
                }
                
                # Apply incremental updates atomically
                if progress_index_inc != 0:
                    self.state_manager.state_data['progress_index'] = self.state_manager.state_data.get('progress_index', 0) + progress_index_inc
                
                if session_products_processed_inc != 0:
                    self.state_manager.state_data['session_products_processed'] = self.state_manager.state_data.get('session_products_processed', 0) + session_products_processed_inc
                
                if resumption_index_inc != 0:
                    self.state_manager.state_data['resumption_index'] = self.state_manager.state_data.get('resumption_index', 0) + resumption_index_inc
                
                if current_product_index_in_category_inc != 0:
                    sep = self.state_manager.state_data['supplier_extraction_progress']
                    sep['current_product_index_in_category'] = sep.get('current_product_index_in_category', 0) + current_product_index_in_category_inc
                
                # Apply any other field updates
                for key, value in kwargs.items():
                    if key in ['successful_products', 'profitable_products', 'total_profit_found']:
                        self.state_manager.state_data[key] = value
                
                self.state_manager.state_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Commit transaction
            self.transaction_manager.commit_transaction(transaction_id)
            self._metrics['successful_operations'] += 1
            self.log.debug(f"✅ Atomic incremental progress update: progress+{progress_index_inc}, session+{session_products_processed_inc}, resumption+{resumption_index_inc}")
            return True
            
        except Exception as e:
            # Rollback on error
            self.transaction_manager.rollback_transaction(transaction_id, self.state_manager.state_data)
            self._metrics['rollback_operations'] += 1
            self.log.error(f"❌ Atomic incremental progress update failed, rolled back: {e}")
            raise

    def update_product_status_atomic(self, product_url: str, status: str, 
                                   source_category: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Atomically update product processing status"""
        return self._execute_with_retry(
            self._update_product_status_atomic_impl,
            "product_status_update",
            product_url=product_url, status=status, 
            source_category=source_category, metadata=metadata
        )
    
    def _update_product_status_atomic_impl(self, product_url: str, status: str,
                                         source_category: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Implementation of atomic product status update"""
        transaction_id = f"product_status_{int(time.time() * 1000)}"
        
        try:
            # Validate inputs
            if not product_url or not isinstance(product_url, str):
                raise ValueError(f"Invalid product_url: {product_url}")
            if not status or not isinstance(status, str):
                raise ValueError(f"Invalid status: {status}")
            
            # Begin transaction
            snapshot = self.transaction_manager.begin_transaction(transaction_id)
            
            with self.state_manager._state_lock:
                # Store current values for rollback
                processed_products = self.state_manager.state_data.setdefault('processed_products', {})
                snapshot['data'] = {
                    'processed_products': processed_products.copy(),
                    'last_updated': self.state_manager.state_data.get('last_updated')
                }
                
                # Update product status
                product_data = {
                    'status': status,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                if source_category:
                    product_data['source_category'] = source_category
                
                if metadata:
                    product_data['metadata'] = metadata
                
                processed_products[product_url] = product_data
                self.state_manager.state_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Commit transaction
            self.transaction_manager.commit_transaction(transaction_id)
            self._metrics['successful_operations'] += 1
            self.log.debug(f"✅ Atomic product status update: {product_url[:50]}... → {status}")
            return True
            
        except Exception as e:
            # Rollback on error
            self.transaction_manager.rollback_transaction(transaction_id, self.state_manager.state_data)
            self._metrics['rollback_operations'] += 1
            self.log.error(f"❌ Atomic product status update failed, rolled back: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get atomic operations metrics"""
        total_operations = self._metrics['successful_operations'] + self._metrics['failed_operations']
        
        return {
            'metrics': self._metrics.copy(),
            'success_rate': (
                self._metrics['successful_operations'] / max(1, total_operations)
            ),
            'settings': {
                'max_retry_attempts': self._max_retry_attempts,
                'retry_delay_seconds': self._retry_delay_seconds,
                'operation_timeout_seconds': self._operation_timeout_seconds
            }
        }
    
    def reset_metrics(self):
        """Reset operation metrics"""
        self._metrics = {
            'successful_operations': 0,
            'failed_operations': 0,
            'rollback_operations': 0,
            'retry_operations': 0
        }
        self.log.info("🔄 Atomic operations metrics reset")


class ProductsExtractedCalculator:
    """Implements missing calculation logic for products_extracted_total"""
    
    def __init__(self, state_manager: FixedEnhancedStateManager):
        self.state_manager = state_manager
        self.log = logging.getLogger(f"{__name__}.ProductsExtractedCalculator")
        self._calculation_cache = {}
        self._cache_timestamp = None
        self._calculation_metadata = {}
        
        # Performance optimization settings
        self._cache_ttl_seconds = 60  # 1 minute cache TTL
        self._lazy_calculation_threshold = 1000  # Only use lazy calculation for large datasets
        self._performance_metrics = {
            'calculation_count': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_calculation_time': 0.0,
            'average_calculation_time': 0.0
        }
    
    def calculate_from_category_completion(self) -> Tuple[int, CalculationMetadata]:
        """Calculate products_extracted_total from category completion data"""
        try:
            total = 0
            categories_completed = self.state_manager.state_data['supplier_extraction_progress'].get('categories_completed', [])
            category_details = {}
            
            # Sum products from completed categories
            for category_url in categories_completed:
                # Try to get count from processed_products
                category_count = 0
                for url, status in self.state_manager.state_data.get('processed_products', {}).items():
                    if isinstance(status, dict) and status.get('source_category') == category_url:
                        category_count += 1
                
                total += category_count
                category_details[category_url] = category_count
            
            # Create metadata
            metadata = CalculationMetadata(
                calculation_method="category_completion",
                last_calculation_timestamp=datetime.now(timezone.utc),
                calculation_source_count=len(categories_completed),
                validation_checksum=self._generate_checksum(category_details)
            )
            
            self.log.debug(f"Calculated from category completion: {total} products across {len(categories_completed)} categories")
            return total, metadata
            
        except Exception as e:
            self.log.error(f"Error calculating from category completion: {e}")
            metadata = CalculationMetadata(
                calculation_method="category_completion_error",
                last_calculation_timestamp=datetime.now(timezone.utc),
                calculation_source_count=0,
                validation_checksum=""
            )
            return 0, metadata
    
    def calculate_from_processed_products(self) -> Tuple[int, CalculationMetadata]:
        """Calculate from processed_products dictionary"""
        try:
            processed_products = self.state_manager.state_data.get('processed_products', {})
            count = len(processed_products)
            
            # Analyze product status distribution
            status_distribution = {}
            for url, status in processed_products.items():
                if isinstance(status, dict):
                    status_key = status.get('status', 'unknown')
                else:
                    status_key = str(status)
                status_distribution[status_key] = status_distribution.get(status_key, 0) + 1
            
            # Create metadata
            metadata = CalculationMetadata(
                calculation_method="processed_products",
                last_calculation_timestamp=datetime.now(timezone.utc),
                calculation_source_count=count,
                validation_checksum=self._generate_checksum(status_distribution)
            )
            
            self.log.debug(f"Calculated from processed products: {count} products with status distribution: {status_distribution}")
            return count, metadata
            
        except Exception as e:
            self.log.error(f"Error calculating from processed products: {e}")
            metadata = CalculationMetadata(
                calculation_method="processed_products_error",
                last_calculation_timestamp=datetime.now(timezone.utc),
                calculation_source_count=0,
                validation_checksum=""
            )
            return 0, metadata
    
    def calculate_from_successful_products(self) -> Tuple[int, CalculationMetadata]:
        """Calculate from successful_products field for cross-validation"""
        try:
            successful_count = self.state_manager.state_data.get('successful_products', 0)
            
            # Create metadata
            metadata = CalculationMetadata(
                calculation_method="successful_products",
                last_calculation_timestamp=datetime.now(timezone.utc),
                calculation_source_count=1,
                validation_checksum=self._generate_checksum({'successful_products': successful_count})
            )
            
            self.log.debug(f"Calculated from successful products: {successful_count}")
            return successful_count, metadata
            
        except Exception as e:
            self.log.error(f"Error calculating from successful products: {e}")
            metadata = CalculationMetadata(
                calculation_method="successful_products_error",
                last_calculation_timestamp=datetime.now(timezone.utc),
                calculation_source_count=0,
                validation_checksum=""
            )
            return 0, metadata
    
    def get_canonical_count(self) -> Tuple[int, Dict[str, Any]]:
        """Get the canonical products_extracted_total using best available source with detailed analysis"""
        start_time = time.time()
        
        # Check cache first
        current_time = datetime.now(timezone.utc)
        if self._is_cache_valid(current_time):
            self._performance_metrics['cache_hits'] += 1
            self.log.debug(f"Cache hit: returning cached canonical count")
            return self._calculation_cache['canonical_count'], self._calculation_cache['analysis']
        
        self._performance_metrics['cache_misses'] += 1
        self._performance_metrics['calculation_count'] += 1
        
        # Determine if we should use lazy calculation
        processed_products_count = len(self.state_manager.state_data.get('processed_products', {}))
        use_lazy_calculation = processed_products_count > self._lazy_calculation_threshold
        
        if use_lazy_calculation:
            self.log.debug(f"Using lazy calculation for {processed_products_count} products")
            canonical_count, analysis = self._calculate_canonical_count_lazy()
        else:
            canonical_count, analysis = self._calculate_canonical_count_full()
        
        # Update performance metrics
        calculation_time = time.time() - start_time
        self._performance_metrics['total_calculation_time'] += calculation_time
        self._performance_metrics['average_calculation_time'] = (
            self._performance_metrics['total_calculation_time'] / 
            self._performance_metrics['calculation_count']
        )
        
        # Update cache
        self._update_cache(canonical_count, analysis, current_time, calculation_time)
        
        self.log.info(f"Canonical count: {canonical_count} (method: {analysis['best_method']}, "
                     f"confidence: {analysis['consistency_check']['confidence']}, "
                     f"time: {calculation_time:.3f}s)")
        
        if analysis['consistency_check']['max_deviation'] > 0:
            self.log.warning(f"Count inconsistency detected: {analysis['all_counts']}")
        
        return canonical_count, analysis
    
    def _is_cache_valid(self, current_time: datetime) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp or 'canonical_count' not in self._calculation_cache:
            return False
        
        cache_age = (current_time - self._cache_timestamp).total_seconds()
        return cache_age < self._cache_ttl_seconds
    
    def _calculate_canonical_count_full(self) -> Tuple[int, Dict[str, Any]]:
        """Full calculation using all methods"""
        # Calculate using multiple methods
        category_count, category_metadata = self.calculate_from_category_completion()
        processed_count, processed_metadata = self.calculate_from_processed_products()
        successful_count, successful_metadata = self.calculate_from_successful_products()
        
        # Determine the most reliable count
        counts = {
            'category_completion': category_count,
            'processed_products': processed_count,
            'successful_products': successful_count
        }
        
        # Use the highest count as it's most likely to be accurate
        canonical_count = max(counts.values())
        best_method = max(counts, key=counts.get)
        
        # Create detailed analysis
        analysis = {
            'canonical_count': canonical_count,
            'best_method': best_method,
            'all_counts': counts,
            'calculation_method': 'full',
            'metadata': {
                'category_completion': category_metadata,
                'processed_products': processed_metadata,
                'successful_products': successful_metadata
            },
            'consistency_check': {
                'all_equal': len(set(counts.values())) == 1,
                'max_deviation': max(counts.values()) - min(counts.values()),
                'confidence': 'high' if max(counts.values()) - min(counts.values()) <= 1 else 'medium'
            }
        }
        
        return canonical_count, analysis
    
    def _calculate_canonical_count_lazy(self) -> Tuple[int, Dict[str, Any]]:
        """Lazy calculation using only the most efficient method"""
        # For large datasets, use only processed_products count as it's most efficient
        processed_count, processed_metadata = self.calculate_from_processed_products()
        
        # Quick validation with successful_products if available
        successful_count = self.state_manager.state_data.get('successful_products', 0)
        
        # Use the higher count
        canonical_count = max(processed_count, successful_count)
        best_method = 'processed_products' if processed_count >= successful_count else 'successful_products'
        
        # Create simplified analysis
        analysis = {
            'canonical_count': canonical_count,
            'best_method': best_method,
            'all_counts': {
                'processed_products': processed_count,
                'successful_products': successful_count
            },
            'calculation_method': 'lazy',
            'metadata': {
                'processed_products': processed_metadata
            },
            'consistency_check': {
                'all_equal': processed_count == successful_count,
                'max_deviation': abs(processed_count - successful_count),
                'confidence': 'medium'  # Lower confidence for lazy calculation
            }
        }
        
        return canonical_count, analysis
    
    def _update_cache(self, canonical_count: int, analysis: Dict[str, Any], 
                     current_time: datetime, calculation_time: float):
        """Update calculation cache with performance data"""
        self._calculation_cache = {
            'canonical_count': canonical_count,
            'analysis': analysis,
            'timestamp': current_time,
            'calculation_time': calculation_time,
            'cache_generation': self._performance_metrics['calculation_count']
        }
        self._cache_timestamp = current_time
    
    def update_products_extracted_total(self) -> bool:
        """Update the products_extracted_total field with calculated value"""
        try:
            canonical_count, analysis = self.get_canonical_count()
            
            with self.state_manager._state_lock:
                old_value = self.state_manager.state_data['supplier_extraction_progress'].get('products_extracted_total', 0)
                self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = canonical_count
                
                # Store calculation metadata
                if 'calculation_metadata' not in self.state_manager.state_data:
                    self.state_manager.state_data['calculation_metadata'] = {}
                
                self.state_manager.state_data['calculation_metadata']['products_extracted_total'] = {
                    'last_update': datetime.now(timezone.utc).isoformat(),
                    'method_used': analysis['best_method'],
                    'confidence': analysis['consistency_check']['confidence'],
                    'all_counts': analysis['all_counts'],
                    'old_value': old_value,
                    'new_value': canonical_count
                }
                
                if old_value != canonical_count:
                    self.log.info(f"Updated products_extracted_total: {old_value} → {canonical_count} (method: {analysis['best_method']})")
                
            return True
            
        except Exception as e:
            self.log.error(f"Error updating products_extracted_total: {e}")
            return False
    
    def validate_calculation_consistency(self) -> ValidationResult:
        """Validate that all calculation methods produce consistent results"""
        try:
            canonical_count, analysis = self.get_canonical_count()
            
            # Check consistency
            max_deviation = analysis['consistency_check']['max_deviation']
            all_equal = analysis['consistency_check']['all_equal']
            
            if all_equal:
                return ValidationResult(
                    invariant_name="calculation_consistency",
                    is_valid=True,
                    current_values=analysis['all_counts'],
                    expected_values=analysis['all_counts'],
                    severity="low",
                    auto_repairable=False,
                    details="All calculation methods produce identical results"
                )
            elif max_deviation <= 5:  # Allow small deviations
                return ValidationResult(
                    invariant_name="calculation_consistency",
                    is_valid=True,
                    current_values=analysis['all_counts'],
                    expected_values={'deviation_threshold': 5},
                    severity="medium",
                    auto_repairable=True,
                    repair_action="use_canonical_count",
                    details=f"Small deviation detected: {max_deviation} products"
                )
            else:
                return ValidationResult(
                    invariant_name="calculation_consistency",
                    is_valid=False,
                    current_values=analysis['all_counts'],
                    expected_values={'max_allowed_deviation': 5},
                    severity="high",
                    auto_repairable=True,
                    repair_action="recalculate_and_reconcile",
                    details=f"Large deviation detected: {max_deviation} products"
                )
                
        except Exception as e:
            return ValidationResult(
                invariant_name="calculation_consistency",
                is_valid=False,
                current_values={},
                expected_values={},
                severity="critical",
                auto_repairable=False,
                details=f"Calculation validation failed: {e}"
            )
    
    def _generate_checksum(self, data: Dict[str, Any]) -> str:
        """Generate a checksum for validation data"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()[:8]
    
    def get_calculation_report(self) -> Dict[str, Any]:
        """Get a comprehensive calculation report with performance metrics"""
        canonical_count, analysis = self.get_canonical_count()
        validation = self.validate_calculation_consistency()
        
        return {
            'canonical_count': canonical_count,
            'calculation_analysis': analysis,
            'validation_result': {
                'is_valid': validation.is_valid,
                'severity': validation.severity,
                'details': validation.details
            },
            'cache_info': {
                'cached': self._cache_timestamp is not None,
                'cache_age_seconds': (datetime.now(timezone.utc) - self._cache_timestamp).total_seconds() if self._cache_timestamp else None,
                'cache_ttl_seconds': self._cache_ttl_seconds,
                'cache_generation': self._calculation_cache.get('cache_generation', 0)
            },
            'performance_metrics': self._performance_metrics.copy(),
            'optimization_settings': {
                'cache_ttl_seconds': self._cache_ttl_seconds,
                'lazy_calculation_threshold': self._lazy_calculation_threshold
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            'metrics': self._performance_metrics.copy(),
            'cache_hit_rate': (
                self._performance_metrics['cache_hits'] / 
                max(1, self._performance_metrics['cache_hits'] + self._performance_metrics['cache_misses'])
            ),
            'optimization_settings': {
                'cache_ttl_seconds': self._cache_ttl_seconds,
                'lazy_calculation_threshold': self._lazy_calculation_threshold
            },
            'recommendations': self._get_performance_recommendations()
        }
    
    def _get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        # Cache hit rate recommendations
        cache_hit_rate = (
            self._performance_metrics['cache_hits'] / 
            max(1, self._performance_metrics['cache_hits'] + self._performance_metrics['cache_misses'])
        )
        
        if cache_hit_rate < 0.5:
            recommendations.append("Consider increasing cache TTL - low cache hit rate detected")
        
        # Calculation time recommendations
        if self._performance_metrics['average_calculation_time'] > 0.1:
            recommendations.append("Consider lowering lazy calculation threshold - slow calculations detected")
        
        # Calculation frequency recommendations
        if self._performance_metrics['calculation_count'] > 100:
            recommendations.append("High calculation frequency - consider increasing cache TTL")
        
        return recommendations
    
    def optimize_performance_settings(self, dataset_size: int = None) -> Dict[str, Any]:
        """Automatically optimize performance settings based on usage patterns"""
        old_settings = {
            'cache_ttl_seconds': self._cache_ttl_seconds,
            'lazy_calculation_threshold': self._lazy_calculation_threshold
        }
        
        # Adjust cache TTL based on calculation frequency
        if self._performance_metrics['calculation_count'] > 50:
            self._cache_ttl_seconds = min(300, self._cache_ttl_seconds * 2)  # Max 5 minutes
        
        # Adjust lazy calculation threshold based on dataset size
        if dataset_size:
            if dataset_size > 10000:
                self._lazy_calculation_threshold = 500  # More aggressive lazy calculation
            elif dataset_size < 100:
                self._lazy_calculation_threshold = 10000  # Less lazy calculation for small datasets
        
        new_settings = {
            'cache_ttl_seconds': self._cache_ttl_seconds,
            'lazy_calculation_threshold': self._lazy_calculation_threshold
        }
        
        self.log.info(f"Performance settings optimized: {old_settings} → {new_settings}")
        
        return {
            'old_settings': old_settings,
            'new_settings': new_settings,
            'optimization_applied': old_settings != new_settings
        }
    
    def clear_cache(self, reason: str = "manual"):
        """Clear calculation cache"""
        self._calculation_cache.clear()
        self._cache_timestamp = None
        self.log.info(f"Calculation cache cleared: {reason}")
    
    def warm_cache(self) -> bool:
        """Pre-warm the calculation cache"""
        try:
            start_time = time.time()
            canonical_count, analysis = self.get_canonical_count()
            warm_time = time.time() - start_time
            
            self.log.info(f"Cache warmed: {canonical_count} products calculated in {warm_time:.3f}s")
            return True
        except Exception as e:
            self.log.error(f"Cache warm-up failed: {e}")
            return False


class StructuredLogger:
    """Provides comprehensive logging for state operations"""
    
    def __init__(self, logger_name: str = "StateOperations"):
        self.log = logging.getLogger(logger_name)
        self.metrics = {
            'state_updates': 0,
            'invariant_checks': 0,
            'reconciliations': 0,
            'errors': 0
        }
    
    def log_state_update(self, operation: str, fields: Dict[str, Any], success: bool, duration_ms: float = 0):
        """Log structured state update events"""
        self.metrics['state_updates'] += 1
        
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "state_update",
            "operation": operation,
            "fields_updated": list(fields.keys()),
            "success": success,
            "duration_ms": duration_ms
        }
        
        if success:
            self.log.info(f"✅ State Update: {operation} - {len(fields)} fields updated in {duration_ms:.1f}ms")
        else:
            self.log.error(f"❌ State Update Failed: {operation}")
            self.metrics['errors'] += 1
        
        self.log.debug(f"State update details: {json.dumps(log_data, indent=2)}")
    
    def log_invariant_check(self, invariant: str, status: str, details: Dict[str, Any]):
        """Log invariant validation results"""
        self.metrics['invariant_checks'] += 1
        
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "invariant_check",
            "invariant": invariant,
            "status": status,
            "details": details
        }
        
        if status == "valid":
            self.log.debug(f"✅ Invariant Valid: {invariant}")
        else:
            self.log.warning(f"⚠️ Invariant Violation: {invariant} - {details}")
        
        self.log.debug(f"Invariant check details: {json.dumps(log_data, indent=2)}")
    
    def log_reconciliation(self, operation: str, changes: List[str], success: bool):
        """Log reconciliation operations"""
        self.metrics['reconciliations'] += 1
        
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "reconciliation",
            "operation": operation,
            "changes_applied": changes,
            "success": success
        }
        
        if success:
            self.log.info(f"✅ Reconciliation: {operation} - {len(changes)} changes applied")
        else:
            self.log.error(f"❌ Reconciliation Failed: {operation}")
            self.metrics['errors'] += 1
        
        self.log.debug(f"Reconciliation details: {json.dumps(log_data, indent=2)}")
    
    def get_metrics(self) -> Dict[str, int]:
        """Get current metrics"""
        return self.metrics.copy()


class AutoRepairEngine:
    """Provides deterministic repair rules for state inconsistencies"""
    
    def __init__(self, state_manager: FixedEnhancedStateManager):
        self.state_manager = state_manager
        self.log = logging.getLogger(f"{__name__}.AutoRepairEngine")
    
    def repair_product_count_inconsistency(self, violation: ValidationResult) -> RepairResult:
        """Repair products_extracted_total != successful_products inconsistency"""
        try:
            # Use the higher count as it's more likely to be accurate
            current_extracted = violation.current_values.get('products_extracted_total', 0)
            current_successful = violation.current_values.get('successful_products', 0)
            
            # Determine canonical count
            canonical_count = max(current_extracted, current_successful)
            
            # Apply repair
            with self.state_manager._state_lock:
                self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = canonical_count
                self.state_manager.state_data['successful_products'] = canonical_count
            
            self.log.info(f"✅ Repaired product count inconsistency: {current_extracted}, {current_successful} → {canonical_count}")
            
            return RepairResult(
                success=True,
                repairs_applied=[f"products_extracted_total: {current_extracted} → {canonical_count}",
                               f"successful_products: {current_successful} → {canonical_count}"]
            )
            
        except Exception as e:
            self.log.error(f"❌ Failed to repair product count inconsistency: {e}")
            return RepairResult(
                success=False,
                repairs_applied=[],
                errors=[str(e)]
            )
    
    def repair_cross_section_inconsistency(self, violation: ValidationResult) -> RepairResult:
        """Repair supplier_extraction_progress and system_progression inconsistency"""
        try:
            repairs_applied = []
            
            with self.state_manager._state_lock:
                sep = self.state_manager.state_data['supplier_extraction_progress']
                
                # Ensure system_progression exists
                if 'system_progression' not in self.state_manager.state_data:
                    self.state_manager.state_data['system_progression'] = {}
                
                sp = self.state_manager.state_data['system_progression']
                
                # Synchronize key fields from supplier_extraction_progress (source of truth)
                sync_fields = [
                    'current_category_url',
                    'current_category_index',
                    'total_categories'
                ]
                
                for field in sync_fields:
                    if field in sep and sep[field] is not None:
                        old_value = sp.get(field)
                        sp[field] = sep[field]
                        if old_value != sep[field]:
                            repairs_applied.append(f"system_progression.{field}: {old_value} → {sep[field]}")
                
                sp['last_sync'] = datetime.now(timezone.utc).isoformat()
            
            self.log.info(f"✅ Repaired cross-section inconsistency: {len(repairs_applied)} fields synchronized")
            
            return RepairResult(
                success=True,
                repairs_applied=repairs_applied
            )
            
        except Exception as e:
            self.log.error(f"❌ Failed to repair cross-section inconsistency: {e}")
            return RepairResult(
                success=False,
                repairs_applied=[],
                errors=[str(e)]
            )


class InvariantValidator:
    """Validates state invariants and provides auto-repair capabilities"""
    
    def __init__(self, state_manager: FixedEnhancedStateManager):
        self.state_manager = state_manager
        self.repair_engine = AutoRepairEngine(state_manager)
        self.log = logging.getLogger(f"{__name__}.InvariantValidator")
    
    def validate_product_count_consistency(self) -> ValidationResult:
        """Validate products_extracted_total == successful_products"""
        try:
            current_extracted = self.state_manager.state_data.get('supplier_extraction_progress', {}).get('products_extracted_total', 0)
            current_successful = self.state_manager.state_data.get('successful_products', 0)
            
            is_valid = (current_extracted == current_successful)
            severity = "low" if is_valid else ("critical" if abs(current_extracted - current_successful) > 10 else "high")
            
            return ValidationResult(
                invariant_name="product_count_consistency",
                is_valid=is_valid,
                current_values={
                    "products_extracted_total": current_extracted,
                    "successful_products": current_successful
                },
                expected_values={
                    "products_extracted_total": current_successful,
                    "successful_products": current_extracted
                },
                severity=severity,
                auto_repairable=True,
                repair_action="synchronize_product_counts" if not is_valid else None,
                details=f"products_extracted_total ({current_extracted}) vs successful_products ({current_successful})"
            )
            
        except Exception as e:
            return ValidationResult(
                invariant_name="product_count_consistency",
                is_valid=False,
                current_values={},
                expected_values={},
                severity="critical",
                auto_repairable=False,
                details=f"Validation failed: {e}"
            )
    
    def validate_cross_section_consistency(self) -> ValidationResult:
        """Validate supplier_extraction_progress and system_progression consistency"""
        try:
            sep = self.state_manager.state_data.get('supplier_extraction_progress', {})
            sp = self.state_manager.state_data.get('system_progression', {})
            
            # Check key fields for consistency
            inconsistencies = []
            check_fields = ['current_category_url', 'current_category_index']
            
            for field in check_fields:
                sep_value = sep.get(field)
                sp_value = sp.get(field)
                
                if sep_value is not None and sp_value is not None and sep_value != sp_value:
                    inconsistencies.append(f"{field}: sep={sep_value} vs sp={sp_value}")
            
            is_valid = len(inconsistencies) == 0
            severity = "low" if is_valid else "medium"
            
            return ValidationResult(
                invariant_name="cross_section_consistency",
                is_valid=is_valid,
                current_values={"inconsistencies": inconsistencies},
                expected_values={"inconsistencies": []},
                severity=severity,
                auto_repairable=True,
                repair_action="synchronize_sections" if not is_valid else None,
                details=f"Found {len(inconsistencies)} inconsistencies: {inconsistencies}"
            )
            
        except Exception as e:
            return ValidationResult(
                invariant_name="cross_section_consistency",
                is_valid=False,
                current_values={},
                expected_values={},
                severity="critical",
                auto_repairable=False,
                details=f"Validation failed: {e}"
            )
    
    def validate_all_invariants(self) -> List[ValidationResult]:
        """Run all invariant validations"""
        validations = []
        
        try:
            validations.append(self.validate_product_count_consistency())
            validations.append(self.validate_cross_section_consistency())
            
            # Log validation results
            violations = [v for v in validations if not v.is_valid]
            if violations:
                self.log.warning(f"⚠️ INVARIANT VIOLATIONS: {len(violations)} detected")
                for violation in violations:
                    self.log.warning(f"  - {violation.invariant_name}: {violation.details}")
            else:
                self.log.debug("✅ All invariants valid")
                
        except Exception as e:
            self.log.error(f"❌ Invariant validation failed: {e}")
            validations.append(ValidationResult(
                invariant_name="validation_system",
                is_valid=False,
                current_values={},
                expected_values={},
                severity="critical",
                auto_repairable=False,
                details=f"Validation system error: {e}"
            ))
        
        return validations
    
    def auto_repair_violations(self, violations: List[ValidationResult]) -> RepairResult:
        """Automatically repair detected violations"""
        all_repairs = []
        all_errors = []
        backup_created = None
        
        try:
            # Create backup before repairs
            backup_dir = f"artifacts/backups/invariant_repair_{int(time.time())}"
            import os
            os.makedirs(backup_dir, exist_ok=True)
            
            # Save current state as backup
            backup_file = f"{backup_dir}/state_before_repair.json"
            with open(backup_file, 'w') as f:
                json.dump(self.state_manager.state_data, f, indent=2)
            backup_created = backup_file
            
            # Apply repairs
            for violation in violations:
                if not violation.auto_repairable:
                    all_errors.append(f"Cannot auto-repair {violation.invariant_name}: not auto-repairable")
                    continue
                
                if violation.repair_action == "synchronize_product_counts":
                    repair_result = self.repair_engine.repair_product_count_inconsistency(violation)
                elif violation.repair_action == "synchronize_sections":
                    repair_result = self.repair_engine.repair_cross_section_inconsistency(violation)
                else:
                    all_errors.append(f"Unknown repair action: {violation.repair_action}")
                    continue
                
                if repair_result.success:
                    all_repairs.extend(repair_result.repairs_applied)
                else:
                    all_errors.extend(repair_result.errors)
            
            success = len(all_errors) == 0
            self.log.info(f"✅ Auto-repair completed: {len(all_repairs)} repairs, {len(all_errors)} errors")
            
            return RepairResult(
                success=success,
                repairs_applied=all_repairs,
                backup_created=backup_created,
                errors=all_errors
            )
            
        except Exception as e:
            self.log.error(f"❌ Auto-repair failed: {e}")
            return RepairResult(
                success=False,
                repairs_applied=all_repairs,
                backup_created=backup_created,
                errors=all_errors + [str(e)]
            )


# Factory function to create enhanced state components
def create_enhanced_state_components(state_manager: FixedEnhancedStateManager) -> Dict[str, Any]:
    """Factory function to create all enhanced state management components"""
    
    components = {
        'atomic_updater': AtomicStateUpdater(state_manager),
        'calculator': ProductsExtractedCalculator(state_manager),
        'logger': StructuredLogger(f"StateOps.{state_manager.supplier_name}"),
        'invariant_validator': InvariantValidator(state_manager)
    }
    
    log.info(f"✅ Enhanced state components created for {state_manager.supplier_name}")
    return components