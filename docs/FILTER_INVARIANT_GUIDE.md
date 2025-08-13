# Filter Invariant Enforcement Guide

## Overview

The Filter Invariant Enforcement system ensures data consistency and processing accuracy by validating that all URLs are properly classified during the filtering process. It implements the critical invariant: `skip + needs_amazon + needs_full == total_input` with automatic repair mechanisms.

## The Filter Invariant

### Mathematical Definition

The filter invariant is a fundamental constraint that ensures no URLs are lost or double-counted during classification:

```
skip_entirely + needs_amazon_only + needs_full_extraction = total_input_urls
```

Where:
- **skip_entirely**: URLs already fully processed (in linking map)
- **needs_amazon_only**: URLs with supplier data, need Amazon analysis
- **needs_full_extraction**: URLs needing complete supplier + Amazon processing
- **total_input_urls**: Total URLs discovered for the category

### Why It Matters

Invariant violations indicate:
- URLs being lost during processing
- Double-counting of products
- Inconsistent state between data sources
- Potential data corruption

## Implementation

### Enhanced URL Filter

The enhanced URL filter (`utils/url_filter.py`) implements mandatory invariant validation:

```python
def filter_urls(
    product_urls: List[str],
    linking_map: List[Dict[str, Any]],
    cached_products: List[Dict[str, Any]],
    processed_urls_set: Optional[Set[str]] = None,
    category_id: Optional[str] = None
) -> Dict[str, List[str]]:
    """
    Classify URLs with mandatory invariant validation.
    """
    # Initial classification
    result = classify_urls(product_urls, linking_map, cached_products)
    
    # Reconciliation for processed-but-unlinked items
    result = reconcile_processed_items(result, processed_urls_set)
    
    # MANDATORY: Validate invariant
    invariant_passed = validate_filter_invariant(result)
    
    if not invariant_passed:
        # Create diagnostic snapshot and attempt repair
        snapshot_filter_failure(result, category_id)
        result = attempt_invariant_repair(result)
    
    return result
```

### Invariant Validation Function

```python
def validate_filter_invariant(result: Dict[str, List[str]]) -> bool:
    """
    Validate the critical filter invariant.
    """
    skip_count = len(result['skip_entirely'])
    amazon_count = len(result['needs_amazon_only'])
    full_count = len(result['needs_full_extraction'])
    total_classified = skip_count + amazon_count + full_count
    
    invariant_passed = total_classified == result['total_input']
    
    # Enhanced logging with breakdown
    log.info(f"INVARIANT CHECK[{result['category_id']}]: "
             f"skip={skip_count} + amazon={amazon_count} + full={full_count} "
             f"= {total_classified} vs input={result['total_input']} "
             f"→ {'PASS' if invariant_passed else 'FAIL'}")
    
    if not invariant_passed:
        # Log detailed failure information
        log.error(f"❌ INVARIANT FAILURE: {total_classified} != {result['total_input']}")
        log.error(f"   Difference: {result['total_input'] - total_classified}")
        
        # Create failure snapshot for debugging
        create_invariant_failure_snapshot(result)
    
    return invariant_passed
```

## Reconciliation Logic

### Processed-But-Unlinked Items

A common cause of invariant violations is products that exist in the processed state but lack linking map entries:

```python
def reconcile_processed_items(result: Dict, processed_urls_set: Set[str]) -> Dict:
    """
    Move processed-but-unlinked items from needs_full to needs_amazon.
    """
    reconciled_full = []
    
    for url in result["needs_full_extraction"]:
        norm_url = normalize_url(url)
        if norm_url in processed_urls_set:
            # Product processed but not in linking map - needs Amazon analysis
            result["needs_amazon_only"].append(url)
            result["reconciled_items"].append(f"moved_to_amazon:{url}")
            log.info(f"🔧 RECONCILED: Moved {url} from needs_full to needs_amazon")
        else:
            reconciled_full.append(url)
    
    result["needs_full_extraction"] = reconciled_full
    return result
```

## Diagnostic Capabilities

### Failure Snapshots

When invariant failures occur, the system creates comprehensive diagnostic snapshots:

```python
def snapshot_filter_failure(result: Dict, product_urls: List[str], 
                           linking_map_urls: Set[str], cached_urls: Set[str],
                           processed_urls_set: Set[str]) -> None:
    """
    Create comprehensive diagnostic snapshot for filter failures.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = Path("OUTPUTS/DIAGNOSTICS/filter_failures")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_data = {
        "timestamp": timestamp,
        "category_id": result.get("category_id", "unknown"),
        "invariant_failure": {
            "total_input": result["total_input"],
            "skip_count": len(result["skip_entirely"]),
            "amazon_count": len(result["needs_amazon_only"]),
            "full_count": len(result["needs_full_extraction"]),
            "total_classified": len(result["skip_entirely"]) + 
                              len(result["needs_amazon_only"]) + 
                              len(result["needs_full_extraction"]),
            "difference": result["total_input"] - (
                len(result["skip_entirely"]) + 
                len(result["needs_amazon_only"]) + 
                len(result["needs_full_extraction"])
            )
        },
        "sample_urls": {
            "input_sample": product_urls[:10],
            "skip_sample": result["skip_entirely"][:5],
            "amazon_sample": result["needs_amazon_only"][:5],
            "full_sample": result["needs_full_extraction"][:5]
        },
        "data_source_stats": {
            "linking_map_urls": len(linking_map_urls),
            "cached_urls": len(cached_urls),
            "processed_urls": len(processed_urls_set)
        }
    }
    
    snapshot_file = snapshot_dir / f"filter_failure_{timestamp}.json"
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot_data, f, indent=2)
    
    log.error(f"📸 DIAGNOSTIC SNAPSHOT: {snapshot_file}")
```

## Automatic Repair

### Repair Mechanisms

The system attempts automatic repair of invariant violations:

```python
def attempt_invariant_repair(result: Dict) -> Dict:
    """
    Attempt automatic repair of invariant violations.
    """
    original_result = result.copy()
    
    # Repair Strategy 1: Remove duplicates
    result = remove_duplicate_classifications(result)
    
    # Repair Strategy 2: Reclassify ambiguous items
    result = reclassify_ambiguous_items(result)
    
    # Repair Strategy 3: Handle edge cases
    result = handle_edge_cases(result)
    
    # Validate repair
    if validate_filter_invariant(result):
        log.info(f"✅ INVARIANT REPAIRED: {result['category_id']}")
        return result
    else:
        log.error(f"❌ REPAIR FAILED: {result['category_id']}")
        return original_result  # Return original if repair fails
```

## Integration with Workflow

### Main Workflow Integration

The filter invariant enforcement is integrated into the main workflow:

```python
# In tools/passive_extraction_workflow_latest.py
def process_category(self, category_url, category_index):
    """Process category with invariant enforcement."""
    
    # Extract URLs
    product_urls = self.extract_category_urls(category_url)
    
    # Filter with invariant validation
    filtered_result = filter_urls(
        product_urls=product_urls,
        linking_map=self.linking_map,
        cached_products=self.cached_products,
        processed_urls_set=self.get_processed_urls_set(),
        category_id=f"C{category_index}"
    )
    
    # Check invariant compliance
    if not filtered_result.get('invariant_check', False):
        # Use error handler for invariant failure
        error_handler = ErrorHandler(self.state_manager, self.log)
        recovery_result = error_handler.handle_invariant_failure(
            filtered_result, f"C{category_index}"
        )
        
        if recovery_result['repaired']:
            filtered_result = recovery_result['repaired_filter']
            self.log.info(f"✅ INVARIANT REPAIRED for category {category_index}")
        else:
            self.log.error(f"❌ INVARIANT REPAIR FAILED for category {category_index}")
            # Continue with best effort or halt based on configuration
    
    # Calculate denominator
    denominator = filtered_result['total_input'] - filtered_result['linking_map_hits']
    
    # Update state with denominator
    self.state_manager.update_progression_unified(
        category_index=category_index,
        total_products_in_current_category=denominator
    )
    
    return filtered_result
```

## Monitoring and Alerting

### Key Metrics

Monitor these metrics for filter invariant health:

```bash
# Invariant pass rate (should be 100%)
grep "INVARIANT CHECK" logs/debug/*.log | grep "PASS" | wc -l
grep "INVARIANT CHECK" logs/debug/*.log | wc -l

# Invariant failures
grep "INVARIANT FAILURE" logs/debug/*.log

# Repair success rate
grep "INVARIANT REPAIRED" logs/debug/*.log | wc -l
grep "REPAIR FAILED" logs/debug/*.log | wc -l

# Reconciliation activity
grep "RECONCILED" logs/debug/*.log | wc -l
```

### Log Patterns

```bash
# Monitor invariant checks
tail -f logs/debug/*.log | grep "INVARIANT CHECK"

# Watch for failures
tail -f logs/debug/*.log | grep "INVARIANT FAIL"

# Monitor repairs
tail -f logs/debug/*.log | grep "REPAIRED"

# Check reconciliation
tail -f logs/debug/*.log | grep "RECONCILED"
```

### Diagnostic Files

```bash
# List recent failure snapshots
ls -la OUTPUTS/DIAGNOSTICS/filter_failures/

# Review latest failure
cat OUTPUTS/DIAGNOSTICS/filter_failures/filter_failure_*.json | tail -1

# Check repair attempts
ls -la OUTPUTS/DIAGNOSTICS/repair_attempts/
```

## Configuration

### Environment Variables

```bash
# Invariant enforcement
INVARIANT_ENFORCEMENT=1       # Enable invariant validation
AUTO_REPAIR_ENABLED=1         # Enable automatic repair
DIAGNOSTIC_SNAPSHOTS=1        # Create failure snapshots

# Repair behavior
MAX_REPAIR_ATTEMPTS=3         # Maximum repair attempts
REPAIR_TIMEOUT=30             # Repair timeout in seconds
GRACEFUL_DEGRADATION=1        # Continue on repair failure
```

### System Configuration

```json
{
  "filter_invariant": {
    "enforcement_enabled": true,
    "auto_repair_enabled": true,
    "diagnostic_snapshots": true,
    "max_repair_attempts": 3,
    "repair_timeout": 30,
    "graceful_degradation": true
  },
  "reconciliation": {
    "enabled": true,
    "batch_size": 100,
    "timeout": 60
  }
}
```

## Troubleshooting

### Common Issues

#### Persistent Invariant Failures

```bash
# Check failure patterns
grep "INVARIANT FAILURE" logs/debug/*.log | tail -10

# Review diagnostic snapshots
ls -la OUTPUTS/DIAGNOSTICS/filter_failures/ | tail -5

# Analyze failure data
python -c "
import json
with open('OUTPUTS/DIAGNOSTICS/filter_failures/latest.json') as f:
    data = json.load(f)
    print(f'Difference: {data[\"invariant_failure\"][\"difference\"]}')
    print(f'Input: {data[\"invariant_failure\"][\"total_input\"]}')
    print(f'Classified: {data[\"invariant_failure\"][\"total_classified\"]}')
"
```

#### Repair Failures

```bash
# Check repair attempts
grep "REPAIR FAILED" logs/debug/*.log

# Review repair diagnostics
cat OUTPUTS/DIAGNOSTICS/repair_attempts/latest.json

# Test repair manually
python -c "
from utils.url_filter import attempt_invariant_repair
# Test repair logic with sample data
"
```

#### Reconciliation Issues

```bash
# Check reconciliation activity
grep "RECONCILED" logs/debug/*.log | tail -10

# Review processed URLs set
python -c "
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
mgr = FixedEnhancedStateManager('test')
processed_urls = mgr.get_processed_urls_set()
print(f'Processed URLs: {len(processed_urls)}')
"
```

## Best Practices

### Development

1. **Always validate invariants** in filter operations
2. **Create diagnostic snapshots** for debugging
3. **Test repair mechanisms** with edge cases
4. **Monitor invariant compliance** continuously
5. **Handle graceful degradation** appropriately

### Production

1. **Enable automatic repair** for common issues
2. **Monitor failure rates** and investigate patterns
3. **Review diagnostic snapshots** regularly
4. **Set up alerting** for persistent failures
5. **Maintain repair mechanism** effectiveness

### Debugging

1. **Use diagnostic snapshots** to understand failures
2. **Analyze URL classification** patterns
3. **Check data source consistency**
4. **Validate reconciliation logic**
5. **Test with known problematic data**

## Testing

### Unit Tests

```python
def test_filter_invariant_validation():
    """Test invariant validation logic."""
    result = {
        'skip_entirely': ['url1', 'url2'],
        'needs_amazon_only': ['url3'],
        'needs_full_extraction': ['url4', 'url5'],
        'total_input': 5
    }
    
    assert validate_filter_invariant(result) == True

def test_invariant_failure_detection():
    """Test invariant failure detection."""
    result = {
        'skip_entirely': ['url1'],
        'needs_amazon_only': ['url2'],
        'needs_full_extraction': ['url3'],
        'total_input': 5  # Should be 3
    }
    
    assert validate_filter_invariant(result) == False

def test_reconciliation_logic():
    """Test processed item reconciliation."""
    result = {
        'needs_full_extraction': ['url1', 'url2'],
        'needs_amazon_only': []
    }
    processed_urls = {'url1'}
    
    reconciled = reconcile_processed_items(result, processed_urls)
    assert 'url1' in reconciled['needs_amazon_only']
    assert 'url1' not in reconciled['needs_full_extraction']
```

### Integration Tests

```python
def test_end_to_end_filtering():
    """Test complete filtering with invariant validation."""
    # Test with real data
    product_urls = get_test_urls()
    linking_map = get_test_linking_map()
    cached_products = get_test_cached_products()
    
    result = filter_urls(product_urls, linking_map, cached_products)
    
    # Verify invariant
    assert result['invariant_check'] == True
    
    # Verify classification
    total_classified = (len(result['skip_entirely']) + 
                       len(result['needs_amazon_only']) + 
                       len(result['needs_full_extraction']))
    assert total_classified == len(product_urls)
```

## Conclusion

The Filter Invariant Enforcement system provides:

1. **Data Integrity**: Ensures no URLs are lost during classification
2. **Automatic Repair**: Fixes common invariant violations automatically
3. **Comprehensive Diagnostics**: Detailed failure analysis and debugging
4. **Production Reliability**: Graceful handling of edge cases
5. **Monitoring Capabilities**: Real-time invariant compliance tracking

This system is critical for maintaining data consistency and processing accuracy in the FBA extraction workflow.