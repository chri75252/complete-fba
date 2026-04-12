#!/usr/bin/env python3
"""
Browser Circuit Breaker Implementation
======================================

Implements circuit breaker pattern for browser operations to prevent cascading 
failures during marathon processing sessions. Based on comprehensive failure 
analysis of 18+ hour browser resource exhaustion patterns.

Key Features:
- 3-failure threshold with 5-minute recovery timeout
- State management (CLOSED/OPEN/HALF_OPEN)
- Automatic failure counting and recovery timing
- Integration with browser health management systems

Usage:
    circuit_breaker = BrowserCircuitBreaker(failure_threshold=3, timeout_seconds=300)
    result = await circuit_breaker.execute_with_breaker(operation, *args, **kwargs)

Author: Amazon FBA Agent System
Date: 2025-07-22
Priority: CRITICAL - Marathon Session Stability
"""

import time
import logging
from typing import Any, Callable, Optional
from functools import wraps

# Configure logging
log = logging.getLogger(__name__)

class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is OPEN"""
    pass

class BrowserCircuitBreaker:
    """
    Circuit breaker implementation for browser operations
    
    Prevents cascading failures by temporarily disabling operations
    after threshold failures are detected. Automatically recovers
    after timeout period with gradual re-enabling.
    
    States:
        CLOSED: Normal operation, operations allowed
        OPEN: Circuit breaker active, operations blocked
        HALF_OPEN: Testing recovery, limited operations allowed
    """
    
    def __init__(self, failure_threshold: int = 3, timeout_seconds: int = 300, recovery_timeout: int = 60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit (default: 3)
            timeout_seconds: Time to keep circuit open before testing recovery (default: 300s/5min)
            recovery_timeout: Time to wait in HALF_OPEN before full recovery (default: 60s)
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.recovery_timeout = recovery_timeout
        
        # Circuit breaker state
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_start: Optional[float] = None
        
        log.info(f"BrowserCircuitBreaker initialized: threshold={failure_threshold}, timeout={timeout_seconds}s")
    
    async def execute_with_breaker(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with circuit breaker protection
        
        Args:
            operation: Async function to execute
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result of operation execution
            
        Raises:
            CircuitBreakerException: If circuit breaker is OPEN
            Exception: Any exception from the wrapped operation
        """
        # Check circuit breaker state
        self._update_state()
        
        if self.state == "OPEN":
            raise CircuitBreakerException(
                f"Circuit breaker is OPEN. Failures: {self.failure_count}/{self.failure_threshold}. "
                f"Will retry in {self._get_time_until_retry():.1f} seconds."
            )
        
        if self.state == "HALF_OPEN":
            log.info("Circuit breaker in HALF_OPEN state - testing recovery")
        
        try:
            # Execute the operation
            result = await operation(*args, **kwargs)
            
            # Record success
            self._record_success()
            return result
            
        except Exception as e:
            # Record failure
            self._record_failure(e)
            raise
    
    def _update_state(self):
        """Update circuit breaker state based on current conditions"""
        current_time = time.time()
        
        if self.state == "OPEN":
            # Check if timeout period has passed
            if self.last_failure_time and (current_time - self.last_failure_time) > self.timeout_seconds:
                self.state = "HALF_OPEN"
                self.half_open_start = current_time
                log.info("Circuit breaker transitioning from OPEN to HALF_OPEN")
        
        elif self.state == "HALF_OPEN":
            # Check if recovery timeout has passed
            if self.half_open_start and (current_time - self.half_open_start) > self.recovery_timeout:
                if self.failure_count == 0:
                    self.state = "CLOSED"
                    log.info("Circuit breaker transitioning from HALF_OPEN to CLOSED - recovery successful")
                else:
                    self.state = "OPEN"
                    self.last_failure_time = current_time
                    log.warning("Circuit breaker transitioning from HALF_OPEN to OPEN - recovery failed")
    
    def _record_success(self):
        """Record successful operation"""
        if self.state == "HALF_OPEN":
            self.failure_count = 0
            self.state = "CLOSED"
            self.half_open_start = None
            log.info("Circuit breaker: Operation successful in HALF_OPEN state - transitioning to CLOSED")
        
        # Reset failure count on success in any state
        if self.failure_count > 0:
            log.debug(f"Circuit breaker: Resetting failure count from {self.failure_count} to 0")
            self.failure_count = 0
    
    def _record_failure(self, error: Exception):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        log.warning(f"Circuit breaker: Operation failed ({self.failure_count}/{self.failure_threshold}): {str(error)}")
        
        # Transition to OPEN state if threshold reached
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            log.error(f"Circuit breaker: OPENING circuit after {self.failure_count} failures. "
                     f"Will retry in {self.timeout_seconds} seconds.")
        
        # If in HALF_OPEN and failure occurs, go back to OPEN
        elif self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.last_failure_time = time.time()
            log.warning("Circuit breaker: Failure in HALF_OPEN state - returning to OPEN")
    
    def _get_time_until_retry(self) -> float:
        """Get time remaining until circuit breaker will allow retry"""
        if not self.last_failure_time or self.state != "OPEN":
            return 0.0
        
        elapsed = time.time() - self.last_failure_time
        return max(0.0, self.timeout_seconds - elapsed)
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "time_until_retry": self._get_time_until_retry() if self.state == "OPEN" else 0.0,
            "half_open_start": self.half_open_start
        }
    
    def reset(self):
        """Reset circuit breaker to CLOSED state"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        self.half_open_start = None
        log.info("Circuit breaker manually reset to CLOSED state")

def circuit_breaker_decorator(failure_threshold: int = 3, timeout_seconds: int = 300):
    """
    Decorator to add circuit breaker functionality to async functions
    
    Usage:
        @circuit_breaker_decorator(failure_threshold=3, timeout_seconds=300)
        async def browser_operation():
            # Your browser operation here
            pass
    """
    def decorator(func: Callable):
        circuit_breaker = BrowserCircuitBreaker(failure_threshold, timeout_seconds)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await circuit_breaker.execute_with_breaker(func, *args, **kwargs)
        
        # Attach circuit breaker to function for external access
        wrapper.circuit_breaker = circuit_breaker
        return wrapper
    
    return decorator