# Data Integrity & Validation Guidelines

## Category Manifest Management

Category manifests serve as the authoritative bridge between product discovery and filtering operations.

### Manifest Structure
```json
{
  "category_url": "https://supplier.com/category/home-kitchen",
  "scraped_at": "2025-01-15T14:30:22Z",
  "product_urls": ["https://supplier.com/product/item-1"],
  "count": 1,
  "supplier_name": "supplier.com",
  "slug": "home-kitchen",
  "manifest_version": "2.0",
  "url_integrity": {
    "integrity_score": 0.98,
    "duplicate_count": 0,
    "invalid_url_count": 0
  }
}
```

### Manifest Validation
Always validate manifests before processing:

```python
# Validate manifest structure
validator = CategoryManifestValidator(self.log)
result = validator.validate_manifest_structure(manifest_path)

if not result["valid"]:
    self.log.error(f"❌ Invalid manifest: {result['errors']}")
    return False

# Validate URL integrity
url_integrity = validator.validate_url_integrity(manifest_data)
if url_integrity["integrity_score"] < 0.95:
    self.log.warning(f"⚠️ Low URL integrity: {url_integrity['integrity_score']:.2f}")
```

### Atomic Manifest Generation
Use atomic operations for manifest creation:

```python
# Generate enhanced manifest with validation
manifest_path = self.enhanced_manifest_generator.generate_enhanced_manifest(
    supplier_name, category_url, urls, scraping_metadata
)

# Always use WindowsSaveGuardian for atomic writes
guardian = WindowsSaveGuardian()
success = guardian.save_json_atomic(manifest_path, manifest_data)
```

## State Consistency Validation

### State Structure Validation
Validate state structure before processing:

```python
# Required system_progression fields
required_fields = [
    "current_phase",
    "current_category_index", 
    "current_product_index_in_category",
    "total_categories"
]

# Validate field presence and types
for field in required_fields:
    if field not in system_progression:
        raise ValueError(f"Missing required field: {field}")
```

### Bounds Validation
Always validate index bounds:

```python
# Category index validation
if category_index < 0:
    raise ValueError("category_index cannot be negative")

if total_categories > 0 and category_index >= total_categories:
    raise ValueError("category_index exceeds total_categories")

# Product index validation  
if product_index < 0:
    raise ValueError("product_index cannot be negative")
```

### State Migration
Handle legacy state migration safely:

```python
# Migrate legacy structures to system_progression
migration_tool = StateMigrationTool(self.state_manager)
success = migration_tool.migrate_legacy_to_system_progression()

if success:
    # Clean up legacy structures after successful migration
    migration_tool.cleanup_legacy_structures()
```

## URL Normalization & Filtering

### Consistent URL Normalization
Use consistent URL normalization across the system:

```python
from utils.normalization import normalize_url

# Always normalize URLs before comparison
normalized_url = normalize_url(raw_url)

# Use normalized URLs in hash sets
self.lm_url_set.add(normalize_url(supplier_url))
```

### Filtering Pipeline Validation
Validate filtering completeness:

```python
# Ensure filtering contract compliance
total_input = len(input_urls)
total_output = len(skip_urls) + len(amazon_only_urls) + len(full_extraction_urls)

if total_input != total_output:
    self.log.error(f"🚨 FILTERING CONTRACT VIOLATION: {total_input} != {total_output}")
    raise RuntimeError("Filtering pipeline integrity check failed")
```

### Duplicate Detection
Implement comprehensive duplicate detection:

```python
# Check for URL duplicates
url_counts = {}
for url in product_urls:
    normalized = normalize_url(url)
    url_counts[normalized] = url_counts.get(normalized, 0) + 1

duplicates = {url: count for url, count in url_counts.items() if count > 1}
if duplicates:
    self.log.warning(f"⚠️ Found {len(duplicates)} duplicate URLs")
```

## Financial Data Validation

### Price Validation
Validate pricing data before calculations:

```python
# Validate price fields
supplier_price = float(entry.get("supplier_price", 0))
amazon_price = float(entry.get("amazon_price", 0))

if supplier_price <= 0:
    self.log.warning(f"⚠️ Invalid supplier price: {supplier_price}")
    return None

if amazon_price <= 0:
    self.log.warning(f"⚠️ Invalid Amazon price: {amazon_price}")
    return None
```

### ROI Calculation Validation
Validate financial calculations:

```python
# Calculate ROI with validation
if supplier_price > 0:
    roi_percent = (net_profit / supplier_price) * 100
else:
    self.log.warning("⚠️ Cannot calculate ROI: supplier_price is zero")
    roi_percent = 0

# Validate reasonable ROI ranges
if roi_percent > 1000:  # 1000% ROI seems unrealistic
    self.log.warning(f"⚠️ Unusually high ROI: {roi_percent:.1f}%")
```

### Financial Report Integrity
Ensure financial report completeness:

```python
# Validate report data completeness
if not results["profitable_products"]:
    self.log.warning("⚠️ No profitable products found in analysis")

# Validate category analysis
for category, data in results["category_analysis"].items():
    if data["product_count"] <= 0:
        self.log.warning(f"⚠️ Empty category analysis: {category}")
```

## Cache Integrity Management

### Cache Validation
Validate cache integrity before use:

```python
# Validate cache file structure
try:
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
except json.JSONDecodeError as e:
    self.log.error(f"❌ Corrupted cache file: {e}")
    return None

# Validate cache data structure
if not isinstance(cache_data, list):
    self.log.error("❌ Invalid cache structure: expected list")
    return None
```

### Hash Index Integrity
Validate hash index consistency:

```python
# Validate hash index counts
if len(self.lm_ean_set) != len(set(e.get("ean") for e in self.linking_map if e.get("ean"))):
    self.log.warning("⚠️ EAN hash index inconsistency detected")
    self._rebuild_hash_indices_with_timing()

# Detect hash collisions
collision_detector = HashCollisionDetector()
collision_result = collision_detector.detect_url_collisions(urls)
if collision_result["collision_rate"] > 0.001:  # 0.1% threshold
    self.log.warning(f"⚠️ High URL collision rate: {collision_result['collision_rate']:.3f}")
```

## Error Recovery Patterns

### Graceful Degradation
Implement graceful degradation for non-critical failures:

```python
try:
    # Attempt enhanced operation
    result = self._enhanced_operation()
except Exception as e:
    self.log.warning(f"⚠️ Enhanced operation failed, falling back: {e}")
    # Fall back to basic operation
    result = self._basic_operation()
```

### Data Recovery
Implement data recovery mechanisms:

```python
# Attempt to recover corrupted state
try:
    state_data = self._load_state()
except Exception as e:
    self.log.warning(f"⚠️ State corruption detected, attempting recovery: {e}")
    
    # Try backup state
    backup_path = self._get_backup_state_path()
    if backup_path.exists():
        state_data = self._load_state_from_backup(backup_path)
    else:
        # Initialize fresh state
        state_data = self._initialize_fresh_state()
```

### Validation Checkpoints
Implement validation checkpoints throughout processing:

```python
# Validate at key processing points
def _validate_processing_checkpoint(self, checkpoint_name: str):
    """Validate system state at processing checkpoint"""
    
    # Validate state consistency
    if not self._validate_state_consistency():
        raise RuntimeError(f"State inconsistency at checkpoint: {checkpoint_name}")
    
    # Validate data integrity
    if not self._validate_data_integrity():
        raise RuntimeError(f"Data integrity failure at checkpoint: {checkpoint_name}")
    
    self.log.debug(f"✅ Checkpoint validation passed: {checkpoint_name}")
```

## Backup and Recovery

### Automatic Backups
Create automatic backups before critical operations:

```python
# Backup before major state changes
backup_path = self._create_state_backup()
self.log.info(f"💾 State backup created: {backup_path}")

try:
    # Perform critical operation
    self._critical_state_operation()
except Exception as e:
    # Restore from backup on failure
    self.log.error(f"❌ Critical operation failed, restoring backup: {e}")
    self._restore_state_from_backup(backup_path)
    raise
```

### Data Verification
Verify data integrity after operations:

```python
# Verify data after save operations
def _verify_saved_data(self, file_path: Path, expected_data: Dict):
    """Verify saved data matches expected data"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # Compare critical fields
        if saved_data.get("count") != expected_data.get("count"):
            raise ValueError("Data verification failed: count mismatch")
        
        self.log.debug(f"✅ Data verification passed: {file_path}")
        
    except Exception as e:
        self.log.error(f"❌ Data verification failed: {e}")
        raise
```