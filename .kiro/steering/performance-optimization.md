# Performance Optimization Guidelines

## Hash-Based Duplicate Prevention

The system implements O(1) hash-based duplicate prevention with 20-40% performance improvements through intelligent indexing.

### Hash Index Management
- **EAN Hash**: Product matching by barcode (`linking_map[].ean`)
- **URL Hash**: Supplier URL deduplication (`linking_map[].supplier_url`) 
- **ASIN Hash**: Amazon product lookup (`linking_map[].amazon_asin`)

### Performance Standards
- Hash build time: <0.5s for 50K entries
- Lookup performance: >100K operations/sec
- Memory usage: <50MB for 100K entries
- Collision rate: <0.1%

### Implementation Patterns
```python
# Always use hash-based lookups for duplicate detection
if url in self.lm_url_set:  # O(1) lookup
    # Skip processing
    
# Rebuild hash indices intelligently
if self.smart_rebuild_manager.should_rebuild_hash_indices(len(self.linking_map)):
    self._rebuild_hash_indices_with_timing()
```

### Logging Requirements
```python
# Required hash index logging format
self.log.info(f"🔥 HASH INDEX BUILT: {ean_count} EANs, {url_count} URLs, {asin_count} ASINs in {elapsed:.2f}s")
```

## Memory Management Optimization

### Smart Memory Clearing
- **Sliding Window**: Clear every 500 products, keep recent 100 for continuity
- **Context-Aware**: Adjust thresholds based on processing phase
- **Predictive**: Use memory trends to prevent pressure buildup

### Memory Thresholds
- **Low Memory**: Clear every 300 products, keep 50
- **Normal**: Clear every 500 products, keep 100  
- **High Memory**: Clear every 800 products, keep 200

### Platform-Specific Optimizations
- **Windows**: Use native memory trimming APIs
- **WSL**: Monitor VmmemWSL accumulation
- **Cross-platform**: psutil for accurate monitoring

## State Management Consistency

### Single Source of Truth
Always use `system_progression` as the authoritative state source:

```python
# CORRECT: Use system_progression exclusively
sp = self.state_manager.state_data.setdefault("system_progression", {})
sp["current_product_index_in_category"] = product_index

# WRONG: Dual updates to legacy structures
self.state_data["supplier_extraction_progress"]["resumption_index"] = index
```

### Required State Fields
- `current_phase`: "supplier" | "amazon_analysis"
- `current_category_index`: Integer >= 0
- `current_product_index_in_category`: Integer >= 0
- `total_categories`: Total category count
- `last_updated`: ISO timestamp

### Resume Point Validation
Always validate resume points before processing:
```python
resume_point = self.canonical_resume_provider.get_safe_resume_point()
is_valid, errors = self.validate_resume_point(resume_point)
if not is_valid:
    # Handle validation errors
```

## Financial Report Automation

### Automated Triggering
- Monitor linking map entry count continuously
- Trigger reports at configurable thresholds (`financial_report_batch_size`)
- Generate comprehensive profitability analysis automatically

### Integration Points
```python
# Check for financial report trigger after linking map updates
current_count = len(self.linking_map)
if self.financial_trigger_manager.should_trigger_report(current_count):
    self._trigger_financial_report(supplier_name)
```

### Report Requirements
- Real-time profitability tracking
- Category-wise financial metrics
- ROI distribution analysis
- Actionable recommendations

## Performance Monitoring

### Key Metrics to Track
- Hash build/lookup performance
- Memory usage patterns and trends
- State consistency validation results
- Financial analysis completion times

### Logging Standards
- Use consistent emoji prefixes (🔥 for hash, 🧹 for memory, 📊 for progress)
- Include timing information for performance operations
- Log warnings for performance degradation
- Provide actionable error messages

### Regression Prevention
- Establish performance baselines
- Monitor for >10% performance degradation
- Alert on memory leak detection
- Validate state consistency on resume