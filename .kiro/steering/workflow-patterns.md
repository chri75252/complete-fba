# Workflow Patterns & Best Practices

## Core Workflow Architecture

The system follows a configuration-driven, stateful workflow with atomic operations and resumable processing.

### Main Processing Flow
1. **Initialization**: Load configuration and validate state
2. **Category Processing**: Extract products from supplier categories
3. **Filtering Pipeline**: Apply URL-based and cache-based filtering
4. **Amazon Analysis**: Match products and extract Amazon data
5. **Financial Analysis**: Calculate profitability metrics
6. **State Persistence**: Save progress atomically

### Entry Points
- **Primary**: `run_custom_poundwholesale.py`
- **Alternative**: `run_complete_fba_system.py`
- **Core Engine**: `tools/passive_extraction_workflow_latest.py`

## State Management Patterns

### Atomic State Operations
Always use atomic operations for state persistence:

```python
# CORRECT: Atomic state save
self.state_manager.save_state(preserve_interruption_state=True)

# CORRECT: Use WindowsSaveGuardian for file operations
guardian = WindowsSaveGuardian()
success = guardian.save_json_atomic(file_path, data)
```

### Progress Tracking
Update progress through unified state manager:

```python
# Category-level progress
self.unified_state_manager.update_category_progress(
    category_index, category_url, total_products
)

# Product-level progress  
self.unified_state_manager.update_product_progress(
    product_index, phase="supplier"
)

# Phase transitions
self.unified_state_manager.transition_phase("amazon_analysis")
```

### Resume Logic
Always validate state before resuming:

```python
# Get validated resume point
resume_point = self.canonical_resume_provider.get_safe_resume_point()

# Log resume information
self.log.info(f"📊 RESUME POINT: phase={resume_point['phase']} "
              f"cat={resume_point['category_index']}/{resume_point['total_categories']}")
```

## Data Processing Patterns

### Batch Processing
Process data in configurable batches for memory efficiency:

```python
# Supplier extraction batches
batch_size = self.system_config.get("supplier_extraction_batch_size", 100)
for batch in self._chunk_categories(categories, batch_size):
    self._process_category_batch(batch)
```

### Filtering Pipeline
Apply consistent filtering patterns:

```python
# Two-step filtering: linking map first, then cache
urls_after_linking = self._filter_against_linking_map(urls)
urls_after_cache = self._filter_against_cache(urls_after_linking)

# Log filtering transparency
self.log.info(f"🔗 FILTERING: {len(urls)} → {len(urls_after_linking)} → {len(urls_after_cache)}")
```

### Error Handling
Implement comprehensive error handling with recovery:

```python
try:
    result = self._process_category(category_url)
except Exception as e:
    self.log.error(f"❌ Category processing failed: {e}")
    # Attempt recovery or skip
    continue
```

## Memory Management Patterns

### Smart Clearing
Use context-aware memory clearing:

```python
# Check if clearing needed based on context
should_clear, reason = self.context_aware_manager.should_clear_for_context(
    len(self.products_in_memory), current_context
)

if should_clear:
    cleared_count = self._enhanced_smart_memory_clear(current_context)
    self.log.info(f"🧹 MEMORY CLEARED: {cleared_count} products ({reason})")
```

### Memory Monitoring
Continuously monitor memory usage:

```python
# Take memory snapshots at key points
snapshot = self.memory_profiler.take_memory_snapshot("before_processing")

# Monitor for memory leaks
leak_result = self.memory_profiler.detect_memory_leaks()
if leak_result["status"] == "leak_detected":
    self.log.warning(f"⚠️ Memory leak detected: {leak_result['recommendation']}")
```

## Configuration Patterns

### Single Source of Truth
All behavior controlled via `config/system_config.json`:

```python
# Load configuration centrally
self.system_config = self.config_loader.get_system_config()
batch_size = self.system_config.get("financial_report_batch_size", 50)

# Never hardcode configuration values
# WRONG: batch_size = 50
# CORRECT: batch_size = self.system_config.get("financial_report_batch_size", 50)
```

### Environment-Specific Settings
Use environment variables for deployment-specific settings:

```python
# Optional API keys
openai_key = os.getenv("OPENAI_API_KEY")
keepa_key = os.getenv("KEEPA_API_KEY")

# Browser configuration
chrome_port = os.getenv("CHROME_DEBUG_PORT", "9222")
```

## Logging Patterns

### Structured Logging
Use consistent logging patterns with emojis and structured information:

```python
# Progress logging
self.log.info(f"📊 PROGRESS: C{category_index}/{total_categories} P{product_index}/{total_products}")

# Performance logging
self.log.info(f"⚡ PERFORMANCE: {operation} completed in {elapsed:.2f}s")

# Error logging with context
self.log.error(f"❌ OPERATION FAILED: {operation} - {error_details}")

# Warning logging
self.log.warning(f"⚠️ WARNING: {condition} detected - {recommendation}")
```

### Debug Information
Provide detailed debug information for troubleshooting:

```python
# Debug-level detailed information
self.log.debug(f"🔍 DEBUG: Processing {url} with config {config_subset}")

# Include relevant context in error messages
self.log.error(f"❌ Failed to process product {product_id} in category {category_url}: {str(e)}")
```

## Integration Patterns

### Component Integration
Integrate components through well-defined interfaces:

```python
# Initialize managers with dependencies
self.hash_performance_profiler = HashPerformanceProfiler()
self.financial_trigger_manager = FinancialReportTriggerManager(
    self.config_loader, self.log
)

# Use dependency injection pattern
self.enhanced_manifest_generator = EnhancedCategoryManifestGenerator(
    self.log, self.config_loader
)
```

### Event-Driven Processing
Use event-driven patterns for automated triggers:

```python
# Trigger events based on thresholds
if len(self.linking_map) % self.financial_batch_size == 0:
    self._trigger_financial_report()

# Respond to state changes
if self.state_manager.phase_changed():
    self._handle_phase_transition()
```

## Testing Patterns

### Unit Testing
Test individual components in isolation:

```python
def test_hash_performance_benchmarks():
    """Test hash performance meets benchmarks"""
    profiler = HashPerformanceProfiler()
    metrics = profiler.profile_hash_build(test_data)
    assert metrics['build_time'] < 0.5  # Performance requirement
```

### Integration Testing
Test component interactions:

```python
def test_workflow_integration():
    """Test complete workflow integration"""
    workflow = PassiveExtractionWorkflow(config_loader, workflow_config, browser_manager)
    result = await workflow.run()
    assert result['success'] == True
```

### Performance Testing
Validate performance requirements:

```python
def test_memory_stability():
    """Test 24+ hour memory stability"""
    # Run extended processing session
    # Monitor memory usage patterns
    # Validate no memory leaks
```