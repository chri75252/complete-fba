# Error Handling & Recovery Guidelines

## Error Classification & Response

### Critical Errors (System Halt)
Errors that require immediate system halt and manual intervention:

```python
# State corruption - halt immediately
if not self._validate_state_integrity():
    self.log.critical("🚨 CRITICAL: State corruption detected - halting system")
    raise SystemExit("State corruption requires manual intervention")

# Configuration errors - halt before processing
if not self._validate_configuration():
    self.log.critical("🚨 CRITICAL: Invalid configuration - cannot proceed")
    raise SystemExit("Configuration validation failed")
```

### Recoverable Errors (Retry Logic)
Errors that can be recovered through retry mechanisms:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def _network_operation_with_retry(self):
    """Network operation with automatic retry"""
    try:
        return self._perform_network_request()
    except (ConnectionError, TimeoutError) as e:
        self.log.warning(f"⚠️ Network error, retrying: {e}")
        raise  # Re-raise for retry mechanism
```

### Degraded Operation (Fallback)
Errors that allow continued operation with reduced functionality:

```python
try:
    # Attempt enhanced operation
    result = self._enhanced_amazon_extraction()
except Exception as e:
    self.log.warning(f"⚠️ Enhanced extraction failed, using fallback: {e}")
    # Fall back to basic extraction
    result = self._basic_amazon_extraction()
```

### Ignorable Errors (Log and Continue)
Errors that can be logged but don't affect core functionality:

```python
try:
    # Optional enhancement
    self._generate_performance_metrics()
except Exception as e:
    self.log.debug(f"🔍 Optional metrics generation failed: {e}")
    # Continue without metrics
```

## Browser Error Handling

### Connection Errors
Handle browser connection failures gracefully:

```python
async def _handle_browser_connection_error(self, error: Exception):
    """Handle browser connection errors with recovery"""
    
    self.log.warning(f"⚠️ Browser connection error: {error}")
    
    try:
        # Attempt browser restart
        await self.browser_manager.restart_browser()
        self.log.info("✅ Browser restarted successfully")
        return True
        
    except Exception as restart_error:
        self.log.error(f"❌ Browser restart failed: {restart_error}")
        
        # Try alternative browser connection
        try:
            await self.browser_manager.connect_alternative_port()
            self.log.info("✅ Connected to alternative browser port")
            return True
        except Exception as alt_error:
            self.log.critical(f"🚨 All browser connection attempts failed: {alt_error}")
            return False
```

### Page Load Failures
Handle page load failures with intelligent retry:

```python
async def _load_page_with_error_handling(self, url: str, max_retries: int = 3):
    """Load page with comprehensive error handling"""
    
    for attempt in range(max_retries):
        try:
            await self.page.goto(url, timeout=30000)
            return True
            
        except TimeoutError:
            self.log.warning(f"⚠️ Page load timeout (attempt {attempt + 1}/{max_retries}): {url}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        except Exception as e:
            self.log.error(f"❌ Page load error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    
    self.log.error(f"❌ Failed to load page after {max_retries} attempts: {url}")
    return False
```

## Authentication Error Handling

### Session Expiration
Handle authentication session expiration:

```python
async def _handle_authentication_failure(self, page, credentials: Dict):
    """Handle authentication failures with re-login"""
    
    self.log.warning("⚠️ Authentication failure detected")
    
    try:
        # Clear existing session
        await page.context.clear_cookies()
        
        # Attempt re-authentication
        success = await self.auth_service.authenticate(page, credentials)
        
        if success:
            self.log.info("✅ Re-authentication successful")
            return True
        else:
            self.log.error("❌ Re-authentication failed")
            return False
            
    except Exception as e:
        self.log.error(f"❌ Authentication error handling failed: {e}")
        return False
```

### Rate Limiting
Handle rate limiting with intelligent backoff:

```python
async def _handle_rate_limiting(self, response_status: int):
    """Handle rate limiting with exponential backoff"""
    
    if response_status == 429:  # Too Many Requests
        # Extract retry-after header if available
        retry_after = getattr(response, 'headers', {}).get('retry-after', '60')
        
        try:
            wait_time = int(retry_after)
        except ValueError:
            wait_time = 60  # Default fallback
        
        self.log.warning(f"⚠️ Rate limited, waiting {wait_time}s before retry")
        await asyncio.sleep(wait_time)
        return True
    
    return False
```

## Data Processing Error Handling

### Malformed Data Recovery
Handle malformed data with validation and recovery:

```python
def _process_product_with_error_handling(self, raw_product_data: Dict):
    """Process product data with comprehensive error handling"""
    
    try:
        # Validate required fields
        if not self._validate_product_data(raw_product_data):
            self.log.warning(f"⚠️ Invalid product data, skipping: {raw_product_data.get('url', 'unknown')}")
            return None
        
        # Process product
        processed_product = self._process_product_data(raw_product_data)
        return processed_product
        
    except KeyError as e:
        self.log.warning(f"⚠️ Missing required field in product data: {e}")
        # Attempt to fill missing data with defaults
        return self._process_with_defaults(raw_product_data)
        
    except ValueError as e:
        self.log.warning(f"⚠️ Invalid data format in product: {e}")
        # Skip this product but continue processing
        return None
        
    except Exception as e:
        self.log.error(f"❌ Unexpected error processing product: {e}")
        # Log full context for debugging
        self.log.debug(f"🔍 Product data: {raw_product_data}")
        return None
```

### File Operation Errors
Handle file operation errors with atomic operations:

```python
def _save_data_with_error_handling(self, file_path: Path, data: Dict):
    """Save data with comprehensive error handling"""
    
    try:
        # Use atomic save operation
        guardian = WindowsSaveGuardian()
        success = guardian.save_json_atomic(file_path, data)
        
        if success:
            self.log.debug(f"✅ Data saved successfully: {file_path}")
            return True
        else:
            raise RuntimeError("Atomic save operation failed")
            
    except PermissionError:
        self.log.error(f"❌ Permission denied saving to: {file_path}")
        # Try alternative location
        alt_path = self._get_alternative_save_path(file_path)
        return self._save_data_with_error_handling(alt_path, data)
        
    except OSError as e:
        self.log.error(f"❌ File system error: {e}")
        # Check disk space and permissions
        if self._check_disk_space(file_path):
            # Retry once if disk space is available
            return self._save_data_with_error_handling(file_path, data)
        else:
            self.log.critical("🚨 Insufficient disk space")
            return False
            
    except Exception as e:
        self.log.error(f"❌ Unexpected file operation error: {e}")
        return False
```

## Memory Error Handling

### Memory Pressure Response
Handle memory pressure with intelligent clearing:

```python
def _handle_memory_pressure(self):
    """Handle memory pressure with escalating responses"""
    
    memory_status = self._get_memory_status()
    
    if memory_status["pressure_level"] == "critical":
        self.log.warning("⚠️ Critical memory pressure - emergency clearing")
        
        # Emergency memory clearing
        cleared = self._emergency_memory_clear()
        self.log.info(f"🧹 Emergency cleared {cleared} items")
        
        # Force garbage collection
        import gc
        gc.collect()
        
    elif memory_status["pressure_level"] == "high":
        self.log.warning("⚠️ High memory pressure - aggressive clearing")
        
        # Aggressive clearing with smaller window
        cleared = self._smart_memory_clear_aggressive()
        self.log.info(f"🧹 Aggressively cleared {cleared} items")
        
    elif memory_status["pressure_level"] == "moderate":
        self.log.info("📊 Moderate memory pressure - standard clearing")
        
        # Standard clearing
        cleared = self._smart_memory_clear()
        self.log.info(f"🧹 Standard cleared {cleared} items")
```

### Out of Memory Recovery
Handle out-of-memory conditions:

```python
def _handle_out_of_memory(self):
    """Handle out-of-memory conditions"""
    
    self.log.critical("🚨 Out of memory condition detected")
    
    try:
        # Emergency data persistence
        self._emergency_save_critical_data()
        
        # Clear all non-essential data
        self._clear_all_caches()
        self._clear_processing_queues()
        
        # Force aggressive garbage collection
        import gc
        gc.collect()
        
        # Check if recovery successful
        if self._check_memory_recovery():
            self.log.info("✅ Memory recovery successful")
            return True
        else:
            self.log.critical("🚨 Memory recovery failed - system halt required")
            return False
            
    except Exception as e:
        self.log.critical(f"🚨 Memory recovery procedure failed: {e}")
        return False
```

## Error Context and Debugging

### Contextual Error Logging
Provide rich context in error messages:

```python
def _log_error_with_context(self, error: Exception, operation: str, context: Dict):
    """Log error with comprehensive context"""
    
    error_context = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
        "system_state": self._get_system_state_summary(),
        "processing_context": context
    }
    
    self.log.error(f"❌ OPERATION FAILED: {operation}")
    self.log.error(f"   Error: {error_context['error_type']}: {error_context['error_message']}")
    self.log.error(f"   Context: {context}")
    
    # Save detailed error context for debugging
    self._save_error_context(error_context)
```

### Error Aggregation
Aggregate similar errors to avoid log spam:

```python
class ErrorAggregator:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.last_logged = {}
        self.log_threshold = 5  # Log every 5th occurrence
    
    def log_error(self, error_key: str, error_message: str, logger):
        """Log error with aggregation"""
        
        self.error_counts[error_key] += 1
        count = self.error_counts[error_key]
        
        # Log first occurrence and every nth occurrence
        if count == 1 or count % self.log_threshold == 0:
            if count > 1:
                logger.error(f"❌ {error_message} (occurred {count} times)")
            else:
                logger.error(f"❌ {error_message}")
            
            self.last_logged[error_key] = datetime.now()
```

## Recovery Procedures

### Automatic Recovery
Implement automatic recovery for common issues:

```python
async def _attempt_automatic_recovery(self, error_type: str):
    """Attempt automatic recovery based on error type"""
    
    recovery_procedures = {
        "browser_connection": self._recover_browser_connection,
        "authentication": self._recover_authentication,
        "network_timeout": self._recover_network_connection,
        "memory_pressure": self._recover_memory_pressure,
        "file_permission": self._recover_file_permissions
    }
    
    recovery_proc = recovery_procedures.get(error_type)
    if recovery_proc:
        try:
            success = await recovery_proc()
            if success:
                self.log.info(f"✅ Automatic recovery successful: {error_type}")
                return True
        except Exception as e:
            self.log.error(f"❌ Automatic recovery failed: {e}")
    
    return False
```

### Manual Recovery Guidance
Provide clear guidance for manual recovery:

```python
def _provide_recovery_guidance(self, error_type: str, error_details: Dict):
    """Provide manual recovery guidance"""
    
    guidance = {
        "state_corruption": [
            "1. Stop the system immediately",
            "2. Check OUTPUTS/CACHE/processing_states/ for backup files",
            "3. Restore from most recent valid backup",
            "4. Restart system with --validate-state flag"
        ],
        "browser_failure": [
            "1. Close all Chrome processes",
            "2. Restart Chrome with debug port: chrome --remote-debugging-port=9222",
            "3. Verify port accessibility at http://localhost:9222",
            "4. Restart the system"
        ],
        "disk_space": [
            "1. Check available disk space",
            "2. Clean up old log files and temporary data",
            "3. Move OUTPUTS directory to larger drive if needed",
            "4. Update configuration with new paths"
        ]
    }
    
    steps = guidance.get(error_type, ["Contact support with error details"])
    
    self.log.error(f"🚨 MANUAL RECOVERY REQUIRED: {error_type}")
    self.log.error("📋 Recovery steps:")
    for step in steps:
        self.log.error(f"   {step}")
```