#!/usr/bin/env python3
"""
Supplier Circuit Breaker Implementation
======================================

Comprehensive circuit breaker system specifically designed for supplier scraping operations.
Prevents cascading failures during zero-result scenarios, quality validation issues,
and repeated failed extractions that waste processing time.

Key Features:
- Zero-result detection with consecutive failure tracking
- Quality validation for scraped product data
- Category-level retry logic with progressive backoff
- Integration with existing supplier scraping workflows

Author: Amazon FBA Agent System  
Date: 2025-07-22
Priority: HIGH - Prevents supplier scraping efficiency issues
"""

import time
import logging
from typing import Any, Callable, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
log = logging.getLogger(__name__)

class SupplierCircuitState(Enum):
    """Circuit breaker states for supplier operations"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit breaker active, operations blocked
    HALF_OPEN = "HALF_OPEN"  # Testing recovery

@dataclass
class SupplierExtractionResult:
    """Result of supplier extraction operation"""
    success: bool
    products_count: int
    valid_products_count: int  
    category_url: str
    error_message: Optional[str] = None
    quality_issues: List[str] = None
    
    def __post_init__(self):
        if self.quality_issues is None:
            self.quality_issues = []

class SupplierQualityValidator:
    """
    Validates quality of supplier extraction results
    """
    
    def __init__(self):
        self.min_products_threshold = 1
        self.max_products_threshold = 200  # Sanity check
        self.valid_price_ratio_threshold = 0.5  # At least 50% should have valid prices
        self.valid_name_ratio_threshold = 0.8   # At least 80% should have valid names
    
    def validate_extraction_quality(self, products: List[Dict[str, Any]], category_url: str) -> SupplierExtractionResult:
        """
        Validate quality of extracted products from supplier category
        
        Args:
            products: List of extracted product dictionaries
            category_url: URL of the category that was scraped
            
        Returns:
            SupplierExtractionResult with validation details
        """
        if not isinstance(products, list):
            return SupplierExtractionResult(
                success=False,
                products_count=0,
                valid_products_count=0,
                category_url=category_url,
                error_message="Products is not a list",
                quality_issues=["invalid_data_type"]
            )
        
        products_count = len(products)
        quality_issues = []
        
        # Check 1: Zero products
        if products_count == 0:
            return SupplierExtractionResult(
                success=False,
                products_count=0,
                valid_products_count=0,
                category_url=category_url,
                error_message="No products extracted",
                quality_issues=["zero_products"]
            )
        
        # Check 2: Sanity check for too many products
        if products_count > self.max_products_threshold:
            quality_issues.append(f"suspiciously_high_count_{products_count}")
            log.warning(f"⚠️ Unusually high product count: {products_count} from {category_url}")
        
        # Check 3: Validate individual product quality
        valid_products = 0
        products_with_prices = 0
        products_with_names = 0
        products_with_urls = 0
        
        for i, product in enumerate(products):
            if not isinstance(product, dict):
                continue
                
            has_valid_price = False
            has_valid_name = False  
            has_valid_url = False
            
            # Price validation
            price = product.get('price')
            if price is not None:
                try:
                    price_float = float(price)
                    if 0.01 <= price_float <= 1000.0:  # Reasonable price range
                        has_valid_price = True
                        products_with_prices += 1
                except (ValueError, TypeError):
                    pass
            
            # Name validation  
            title = product.get('title', '').strip()
            if title and len(title) >= 3 and not title.lower() in ['n/a', 'none', 'null']:
                has_valid_name = True
                products_with_names += 1
            
            # URL validation
            url = product.get('url', '').strip()
            if url and url.startswith('http') and len(url) >= 10:
                has_valid_url = True
                products_with_urls += 1
            
            # Count as valid if has name and either price or URL
            if has_valid_name and (has_valid_price or has_valid_url):
                valid_products += 1
        
        # Calculate quality ratios
        price_ratio = products_with_prices / products_count if products_count > 0 else 0
        name_ratio = products_with_names / products_count if products_count > 0 else 0
        url_ratio = products_with_urls / products_count if products_count > 0 else 0
        valid_ratio = valid_products / products_count if products_count > 0 else 0
        
        # Quality checks
        if price_ratio < self.valid_price_ratio_threshold:
            quality_issues.append(f"low_price_ratio_{price_ratio:.2f}")
        
        if name_ratio < self.valid_name_ratio_threshold:
            quality_issues.append(f"low_name_ratio_{name_ratio:.2f}")
        
        if url_ratio < 0.9:  # Almost all should have URLs
            quality_issues.append(f"low_url_ratio_{url_ratio:.2f}")
        
        if valid_ratio < 0.3:  # At least 30% should be valid
            quality_issues.append(f"low_valid_ratio_{valid_ratio:.2f}")
        
        # Determine success
        success = (
            valid_products >= self.min_products_threshold and 
            len(quality_issues) == 0 and
            valid_ratio >= 0.5
        )
        
        log.debug(f"🔍 Quality validation: {products_count} products, {valid_products} valid, "
                 f"ratios: price={price_ratio:.2f}, name={name_ratio:.2f}, success={success}")
        
        return SupplierExtractionResult(
            success=success,
            products_count=products_count,
            valid_products_count=valid_products,
            category_url=category_url,
            error_message=None if success else f"Quality validation failed: {', '.join(quality_issues)}",
            quality_issues=quality_issues
        )

class SupplierCircuitBreakerException(Exception):
    """Exception raised when supplier circuit breaker is OPEN"""
    pass

class SupplierCircuitBreaker:
    """
    Circuit breaker specifically designed for supplier scraping operations
    
    Prevents cascading failures by detecting:
    - Consecutive zero-result extractions
    - Poor quality extraction results  
    - Repeated category failures
    - System-wide supplier connectivity issues
    """
    
    def __init__(self, 
                 failure_threshold: int = 2,
                 timeout_seconds: int = 180,
                 consecutive_zero_results_threshold: int = 3):
        """
        Initialize supplier circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit (default: 2)
            timeout_seconds: Time to keep circuit open before testing recovery (default: 180s/3min)
            consecutive_zero_results_threshold: Consecutive zero results before opening (default: 3)
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.consecutive_zero_results_threshold = consecutive_zero_results_threshold
        
        # Circuit breaker state
        self.state = SupplierCircuitState.CLOSED
        self.failure_count = 0
        self.consecutive_zero_results = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_start: Optional[float] = None
        
        # Quality tracking
        self.quality_validator = SupplierQualityValidator()
        self.recent_results: List[SupplierExtractionResult] = []
        self.category_failure_counts: Dict[str, int] = {}
        
        log.info(f"🛡️ SupplierCircuitBreaker initialized: failure_threshold={failure_threshold}, "
                f"timeout={timeout_seconds}s, zero_results_threshold={consecutive_zero_results_threshold}")
    
    async def execute_with_breaker(self, 
                                   operation: Callable, 
                                   category_url: str, 
                                   *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute supplier scraping operation with circuit breaker protection
        
        Args:
            operation: Async function to execute (should return list of products)
            category_url: URL of category being scraped
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            List of extracted products
            
        Raises:
            SupplierCircuitBreakerException: If circuit breaker is OPEN
        """
        # Check circuit breaker state
        self._update_state()
        
        if self.state == SupplierCircuitState.OPEN:
            raise SupplierCircuitBreakerException(
                f"Supplier circuit breaker is OPEN for category scraping. "
                f"Failures: {self.failure_count}/{self.failure_threshold}, "
                f"Zero results: {self.consecutive_zero_results}/{self.consecutive_zero_results_threshold}. "
                f"Will retry in {self._get_time_until_retry():.1f} seconds."
            )
        
        if self.state == SupplierCircuitState.HALF_OPEN:
            log.info(f"🔍 Supplier circuit breaker in HALF_OPEN state - testing recovery for {category_url}")
        
        try:
            # Execute the operation
            log.debug(f"🔧 Executing supplier operation for {category_url}")
            products = await operation(*args, **kwargs)
            
            # Validate results
            validation_result = self.quality_validator.validate_extraction_quality(products, category_url)
            
            # Record result
            self._record_result(validation_result)
            
            if validation_result.success:
                log.debug(f"✅ Supplier operation successful: {validation_result.valid_products_count} valid products")
                return products
            else:
                log.warning(f"⚠️ Supplier operation quality issues: {validation_result.error_message}")
                # Still return products but record as quality failure
                return products
                
        except Exception as e:
            # Record failure  
            error_result = SupplierExtractionResult(
                success=False,
                products_count=0,
                valid_products_count=0,
                category_url=category_url,
                error_message=str(e),
                quality_issues=["operation_exception"]
            )
            self._record_result(error_result)
            raise
    
    def _update_state(self):
        """Update circuit breaker state based on current conditions"""
        current_time = time.time()
        
        if self.state == SupplierCircuitState.OPEN:
            # Check if timeout period has passed
            if self.last_failure_time and (current_time - self.last_failure_time) > self.timeout_seconds:
                self.state = SupplierCircuitState.HALF_OPEN
                self.half_open_start = current_time
                log.info("🔄 Supplier circuit breaker transitioning from OPEN to HALF_OPEN")
        
        elif self.state == SupplierCircuitState.HALF_OPEN:
            # Check if recovery timeout has passed
            if self.half_open_start and (current_time - self.half_open_start) > 60:  # 1 minute test period
                if self.failure_count == 0:
                    self.state = SupplierCircuitState.CLOSED
                    log.info("✅ Supplier circuit breaker transitioning from HALF_OPEN to CLOSED - recovery successful")
                else:
                    self.state = SupplierCircuitState.OPEN
                    self.last_failure_time = current_time
                    log.warning("❌ Supplier circuit breaker transitioning from HALF_OPEN to OPEN - recovery failed")
    
    def _record_result(self, result: SupplierExtractionResult):
        """Record supplier extraction result and update circuit breaker state"""
        # Add to recent results
        self.recent_results.append(result)
        
        # Keep only last 10 results
        if len(self.recent_results) > 10:
            self.recent_results = self.recent_results[-10:]
        
        # Update category failure tracking
        if not result.success:
            self.category_failure_counts[result.category_url] = \
                self.category_failure_counts.get(result.category_url, 0) + 1
        else:
            # Reset category failure count on success
            if result.category_url in self.category_failure_counts:
                self.category_failure_counts[result.category_url] = 0
        
        if result.success and result.products_count > 0:
            # Success with products
            self._record_success()
        elif result.products_count == 0:
            # Zero results - track separately
            self.consecutive_zero_results += 1
            log.warning(f"📉 Zero results from {result.category_url} "
                       f"(consecutive: {self.consecutive_zero_results}/{self.consecutive_zero_results_threshold})")
            
            if self.consecutive_zero_results >= self.consecutive_zero_results_threshold:
                self._trigger_circuit_breaker("consecutive_zero_results")
        else:
            # Quality issues but some products
            self.consecutive_zero_results = 0  # Reset zero results counter
            if len(result.quality_issues) > 2:  # Multiple quality issues
                self._record_failure("quality_issues", result.error_message)
            else:
                # Minor quality issues - don't count as full failure
                log.debug(f"⚠️ Minor quality issues for {result.category_url}: {result.quality_issues}")
    
    def _record_success(self):
        """Record successful operation"""
        if self.state == SupplierCircuitState.HALF_OPEN:
            self.failure_count = 0
            self.consecutive_zero_results = 0
            self.state = SupplierCircuitState.CLOSED
            self.half_open_start = None
            log.info("✅ Supplier circuit breaker: Operation successful in HALF_OPEN state - transitioning to CLOSED")
        
        # Reset counters on success
        if self.failure_count > 0:
            log.debug(f"🔄 Resetting supplier failure count from {self.failure_count} to 0")
            self.failure_count = 0
            self.consecutive_zero_results = 0
    
    def _record_failure(self, failure_type: str, error_message: str):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        log.warning(f"⚠️ Supplier operation failed ({failure_type}): {error_message} "
                   f"[{self.failure_count}/{self.failure_threshold}]")
        
        # Check if we should trigger circuit breaker
        if self.failure_count >= self.failure_threshold:
            self._trigger_circuit_breaker(failure_type)
        elif self.state == SupplierCircuitState.HALF_OPEN:
            # Any failure in HALF_OPEN goes back to OPEN
            self.state = SupplierCircuitState.OPEN
            self.last_failure_time = time.time()
            log.warning("🔄 Supplier circuit breaker: Failure in HALF_OPEN state - returning to OPEN")
    
    def _trigger_circuit_breaker(self, reason: str):
        """Trigger circuit breaker to OPEN state"""
        self.state = SupplierCircuitState.OPEN
        self.last_failure_time = time.time()
        
        log.error(f"🚨 SUPPLIER CIRCUIT BREAKER OPENED: {reason}. "
                 f"Failures: {self.failure_count}, Zero results: {self.consecutive_zero_results}. "
                 f"Will retry in {self.timeout_seconds} seconds.")
    
    def _get_time_until_retry(self) -> float:
        """Get time remaining until circuit breaker will allow retry"""
        if not self.last_failure_time or self.state != SupplierCircuitState.OPEN:
            return 0.0
        
        elapsed = time.time() - self.last_failure_time
        return max(0.0, self.timeout_seconds - elapsed)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current supplier circuit breaker status"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "consecutive_zero_results": self.consecutive_zero_results,
            "zero_results_threshold": self.consecutive_zero_results_threshold,
            "last_failure_time": self.last_failure_time,
            "time_until_retry": self._get_time_until_retry() if self.state == SupplierCircuitState.OPEN else 0.0,
            "half_open_start": self.half_open_start,
            "recent_results_count": len(self.recent_results),
            "category_failures": dict(self.category_failure_counts)
        }
    
    def reset(self):
        """Reset supplier circuit breaker to CLOSED state"""
        self.failure_count = 0
        self.consecutive_zero_results = 0
        self.last_failure_time = None
        self.state = SupplierCircuitState.CLOSED
        self.half_open_start = None
        self.recent_results.clear()
        self.category_failure_counts.clear()
        log.info("🔄 Supplier circuit breaker manually reset to CLOSED state")
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quality analysis of recent extractions"""
        if not self.recent_results:
            return {"status": "no_data"}
        
        recent = self.recent_results[-5:]  # Last 5 results
        
        total_products = sum(r.products_count for r in recent)
        total_valid = sum(r.valid_products_count for r in recent)
        success_count = sum(1 for r in recent if r.success)
        
        quality_issues = []
        for result in recent:
            quality_issues.extend(result.quality_issues)
        
        return {
            "recent_extractions": len(recent),
            "success_rate": success_count / len(recent) if recent else 0,
            "total_products": total_products,
            "total_valid_products": total_valid,
            "valid_product_ratio": total_valid / total_products if total_products > 0 else 0,
            "common_quality_issues": list(set(quality_issues)),
            "zero_result_categories": [r.category_url for r in recent if r.products_count == 0]
        }

# Global instance for easy access
_supplier_circuit_breaker = None

def get_supplier_circuit_breaker() -> SupplierCircuitBreaker:
    """Get global supplier circuit breaker instance"""
    global _supplier_circuit_breaker
    if _supplier_circuit_breaker is None:
        _supplier_circuit_breaker = SupplierCircuitBreaker()
    return _supplier_circuit_breaker

async def scrape_category_with_safeguards(scraping_function: Callable, 
                                          category_url: str, 
                                          max_retries: int = 2,
                                          *args, **kwargs) -> List[Dict[str, Any]]:
    """
    Wrapper function to scrape category with supplier safeguards
    
    Args:
        scraping_function: The actual scraping function to call
        category_url: URL of category to scrape
        max_retries: Maximum number of retry attempts
        *args, **kwargs: Arguments to pass to scraping function
        
    Returns:
        List of extracted products
    """
    circuit_breaker = get_supplier_circuit_breaker()
    
    for attempt in range(max_retries + 1):
        try:
            log.info(f"🔧 Scraping category {category_url} (attempt {attempt + 1}/{max_retries + 1})")
            
            products = await circuit_breaker.execute_with_breaker(
                scraping_function, category_url, *args, **kwargs
            )
            
            log.info(f"✅ Successfully scraped {len(products)} products from {category_url}")
            return products
            
        except SupplierCircuitBreakerException as e:
            log.error(f"🚨 Circuit breaker blocked scraping: {e}")
            if attempt == max_retries:
                raise
            
            # Wait for circuit breaker to allow retry
            wait_time = circuit_breaker._get_time_until_retry()
            if wait_time > 0:
                log.info(f"⏳ Waiting {wait_time:.1f} seconds for circuit breaker...")
                import asyncio
                await asyncio.sleep(wait_time)
        
        except Exception as e:
            log.error(f"❌ Scraping attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                raise
            
            # Progressive backoff
            backoff_time = 10 * (attempt + 1)
            log.info(f"⏳ Retrying in {backoff_time} seconds...")
            import asyncio
            await asyncio.sleep(backoff_time)
    
    return []  # Should not reach here

if __name__ == "__main__":
    # Test the supplier circuit breaker
    import asyncio
    
    async def test_supplier_circuit_breaker():
        print("🧪 Testing Supplier Circuit Breaker...")
        
        circuit_breaker = SupplierCircuitBreaker()
        
        # Test quality validator
        validator = SupplierQualityValidator()
        
        # Test with good products
        good_products = [
            {"title": "Product 1", "price": 10.99, "url": "http://example.com/1"},
            {"title": "Product 2", "price": 15.50, "url": "http://example.com/2"},
        ]
        result = validator.validate_extraction_quality(good_products, "http://test.com/category1")
        print(f"Good products validation: {result.success}, issues: {result.quality_issues}")
        
        # Test with poor quality products
        poor_products = [
            {"title": "", "price": None, "url": ""},
            {"title": "Product", "price": "invalid", "url": "not_url"},
        ]
        result = validator.validate_extraction_quality(poor_products, "http://test.com/category2")
        print(f"Poor products validation: {result.success}, issues: {result.quality_issues}")
        
        # Test circuit breaker status
        status = circuit_breaker.get_status()
        print(f"Circuit breaker status: {status}")
        
        print("✅ Supplier Circuit Breaker test complete")
    
    asyncio.run(test_supplier_circuit_breaker())