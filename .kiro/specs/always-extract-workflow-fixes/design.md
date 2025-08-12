# Design Document

## Overview

This design document outlines the critical fixes needed to complete the Always-Extract Workflow implementation. Based on analysis of the current system behavior versus the intended behavior, this design addresses the gaps in logging formats, state management, normalization, and processing flow.

The current system has partial implementations that need to be corrected:
- Pagination logging uses incorrect format and hardcoded category indices
- Breadcrumb logging shows 0/0 denominators due to timing issues
- Manifest generation is completely missing
- Filter summary logging is absent
- URL/EAN normalization is not implemented
- State validation and repair functionality is missing
- Import hygiene logging is not present

## Architecture

### Current System Analysis

From the log file analysis, the current system shows these patterns:

**Current Pagination Format (Incorrect):**
```
PAGINATION[C1 https-www-poundwholesale-co-uk]: pages=5 urls_page=20,20,20,16,0 total=76
```

**Current Breadcrumb Format (Incorrect):**
```
RESUME PTR: phase=supplier_extraction cat_idx=0/1 url=https://... prod_idx=1/0
```

**Missing Patterns:**
- No manifest logging
- No filter summary logging  
- No module path logging
- No state validation logging

### Target System Architecture

The fixed system will implement these corrected patterns:

**Target Pagination Format:**
```
PAGINATION[C5 wholesale-hand-tools]: pages=3 urls_page=166,166,166 total=498
```

**Target Breadcrumb Format:**
```
RESUME PTR: phase=supplier cat_idx=5/119 url=https://...wholesale-hand-tools prod_idx=3/498
```

**New Required Patterns:**
```
MODULE PATH: C:\...\tools\passive_extraction_workflow_latest.py
📝 MANIFEST: 498 URLs → C:\...\OUTPUTS\manifests\poundwholesale.co.uk\wholesale-hand-tools.json
FILTER[C5 wholesale-hand-tools]: in=498 skip=491 needs_amz=0 needs_full=7
State repaired: resumption_index bounds corrected
```

## Components and Interfaces

### 1. Pagination Logging Fix

**Current Issue:** Hardcoded "C1" and incorrect slug generation
**Location:** `tools/passive_extraction_workflow_latest.py`

**Required Changes:**
```python
def _log_pagination_summary(self, category_index: int, category_url: str, pages_scraped: int, urls_per_page: List[int], total_urls: int):
    """Log pagination summary with correct format"""
    slug = self._generate_category_slug(category_url)
    urls_page_str = ','.join(map(str, urls_per_page))
    self.log.info(f"PAGINATION[C{category_index} {slug}]: pages={pages_scraped} urls_page={urls_page_str} total={total_urls}")

def _generate_category_slug(self, category_url: str) -> str:
    """Generate readable slug from category URL"""
    from urllib.parse import urlparse
    path = urlparse(category_url).path.strip('/')
    return path.split('/')[-1] if path else 'unknown'
```

### 2. Breadcrumb Logging Fix

**Current Issue:** Zero denominators and incorrect timing
**Location:** `utils/fixed_enhanced_state_manager.py`

**Required Changes:**
```python
def save_state_atomic(self):
    """Save state with accurate breadcrumbs only when denominators are known"""
    # Only log breadcrumbs if we have valid totals
    if (self.state_data.get('system_progression', {}).get('total_categories', 0) > 0 and
        self.state_data.get('system_progression', {}).get('total_products_in_current_category', 0) > 0):
        breadcrumb = self._generate_resume_breadcrumb()
        self.log.info(f"RESUME PTR: {breadcrumb}")
    
    # Perform atomic save
    self._atomic_save()

def _generate_resume_breadcrumb(self) -> str:
    """Generate accurate resume breadcrumb with non-zero denominators"""
    progression = self.state_data.get('system_progression', {})
    phase = progression.get('current_phase', 'supplier')
    cat_idx = progression.get('current_category_index', 0)
    total_cats = progression.get('total_categories', 0)
    prod_idx = progression.get('current_product_index_in_category', 0)
    total_prods = progression.get('total_products_in_current_category', 0)
    url = progression.get('current_category_url', '')
    
    return f"phase={phase} cat_idx={cat_idx}/{total_cats} url={url} prod_idx={prod_idx}/{total_prods}"
```

### 3. Manifest Generation System

**Current Issue:** Completely missing
**Location:** `tools/passive_extraction_workflow_latest.py`

**Required Implementation:**
```python
def _save_category_manifest(self, supplier_name: str, category_url: str, category_index: int, urls: List[str]) -> str:
    """Save category manifest atomically with proper logging"""
    slug = self._generate_category_slug(category_url)
    manifest_dir = Path(self.output_dir) / "manifests" / supplier_name
    manifest_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = manifest_dir / f"{slug}.json"
    
    manifest_data = {
        "category_url": category_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "product_urls": urls,
        "count": len(urls),
        "supplier_name": supplier_name,
        "slug": slug
    }
    
    # Check if manifest exists for overwrite detection
    prev_count = 0
    overwrite = False
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                prev_data = json.load(f)
                prev_count = prev_data.get('count', 0)
                overwrite = True
        except:
            pass
    
    # Atomic save using WindowsSaveGuardian
    self.save_guardian.save_json(manifest_data, str(manifest_path))
    
    # Log appropriate message
    if overwrite:
        self.log.info(f"MANIFEST UPDATE[C{category_index} {slug}]: overwritten=true prev={prev_count} curr={len(urls)}")
    else:
        self.log.info(f"📝 MANIFEST: {len(urls)} URLs → {manifest_path}")
    
    return str(manifest_path)
```

### 4. Filter Summary Logging System

**Current Issue:** Missing clean filter summary
**Location:** `tools/passive_extraction_workflow_latest.py`

**Required Implementation:**
```python
def _log_filter_summary(self, category_index: int, category_url: str, filter_results: Dict[str, List[str]]):
    """Log clean filter summary with invariant validation"""
    slug = self._generate_category_slug(category_url)
    
    input_count = filter_results.get('input_count', 0)
    skip_count = len(filter_results.get('skip_entirely', []))
    needs_amz_count = len(filter_results.get('needs_amazon_only', []))
    needs_full_count = len(filter_results.get('needs_full_extraction', []))
    
    # Validate invariant
    total_classified = skip_count + needs_amz_count + needs_full_count
    if total_classified != input_count:
        self.log.warning(f"FILTER INVARIANT VIOLATION: {skip_count} + {needs_amz_count} + {needs_full_count} = {total_classified} != {input_count}")
    
    self.log.info(f"FILTER[C{category_index} {slug}]: in={input_count} skip={skip_count} needs_amz={needs_amz_count} needs_full={needs_full_count}")
```

### 5. URL/EAN Normalization System

**Current Issue:** Not implemented
**Location:** `utils/url_filter.py` (new file)

**Required Implementation:**
```python
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional

def normalize_url(url: str) -> str:
    """Normalize URL for consistent matching"""
    try:
        parsed = urlparse(url.lower())
        
        # Remove tracking parameters
        tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid', 'gclid'}
        query_params = parse_qs(parsed.query)
        filtered_params = {k: v for k, v in query_params.items() if k not in tracking_params}
        
        # Sort parameters for stable ordering
        sorted_query = urlencode(sorted(filtered_params.items()), doseq=True)
        
        # Normalize path (remove trailing slash unless root)
        path = parsed.path.rstrip('/') if parsed.path != '/' else '/'
        
        # Reconstruct URL
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            sorted_query,
            ''  # Remove fragment
        ))
        
        return normalized
    except Exception as e:
        logging.warning(f"URL normalization failed for {url}: {e}")
        return url

def normalize_ean(ean: str) -> str:
    """Normalize EAN for consistent matching"""
    try:
        # Convert to string and strip whitespace
        normalized = str(ean).strip()
        
        # Preserve leading zeros - don't convert to int
        # Remove any non-digit characters except leading zeros
        normalized = re.sub(r'[^\d]', '', normalized)
        
        return normalized
    except Exception as e:
        logging.warning(f"EAN normalization failed for {ean}: {e}")
        return str(ean)

def filter_urls(urls: List[str], linking_map: List[Dict], cached_products: List[Dict]) -> Dict[str, List[str]]:
    """Filter URLs with normalization and return categorized results"""
    # Build normalized lookup sets
    linking_map_urls = set()
    linking_map_eans = set()
    for entry in linking_map:
        if 'supplier_url' in entry:
            linking_map_urls.add(normalize_url(entry['supplier_url']))
        if 'ean' in entry:
            linking_map_eans.add(normalize_ean(entry['ean']))
    
    cache_urls = set()
    cache_eans = set()
    for product in cached_products:
        if 'url' in product:
            cache_urls.add(normalize_url(product['url']))
        if 'ean' in product:
            cache_eans.add(normalize_ean(product['ean']))
    
    # Categorize URLs
    skip_entirely = []
    needs_amazon_only = []
    needs_full_extraction = []
    
    for url in urls:
        normalized_url = normalize_url(url)
        
        # Check linking map first (highest priority)
        if normalized_url in linking_map_urls:
            skip_entirely.append(url)
        # Check cache second
        elif normalized_url in cache_urls:
            needs_amazon_only.append(url)
        # Not found anywhere - needs full extraction
        else:
            needs_full_extraction.append(url)
    
    return {
        'input_count': len(urls),
        'skip_entirely': skip_entirely,
        'needs_amazon_only': needs_amazon_only,
        'needs_full_extraction': needs_full_extraction
    }
```

### 6. State Validation and Repair System

**Current Issue:** Not implemented
**Location:** `utils/fixed_enhanced_state_manager.py`

**Required Implementation:**
```python
def validate_and_repair_state(self) -> Tuple[bool, List[str]]:
    """Validate state consistency and repair common issues"""
    repairs = []
    
    # Ensure system_progression exists
    if 'system_progression' not in self.state_data:
        self.state_data['system_progression'] = {}
        repairs.append("added missing system_progression")
    
    progression = self.state_data['system_progression']
    
    # Validate and repair resumption_index bounds
    resumption_index = self.state_data.get('resumption_index', 0)
    total_categories = progression.get('total_categories', 0)
    
    if resumption_index < 0:
        self.state_data['resumption_index'] = 0
        repairs.append("corrected negative resumption_index")
    elif total_categories > 0 and resumption_index >= total_categories:
        self.state_data['resumption_index'] = max(0, total_categories - 1)
        repairs.append("corrected resumption_index bounds")
    
    # Ensure monotonic progression
    last_processed = self.state_data.get('last_processed_index', 0)
    if last_processed > resumption_index:
        self.state_data['resumption_index'] = last_processed
        repairs.append("aligned resumption_index with last_processed_index")
    
    # Validate category indices
    cat_index = progression.get('current_category_index', 0)
    if cat_index < 0:
        progression['current_category_index'] = 0
        repairs.append("corrected negative category_index")
    
    # Ensure required fields exist with defaults
    required_fields = {
        'current_phase': 'supplier',
        'current_category_index': 0,
        'current_category_url': '',
        'total_categories': 0,
        'current_product_index_in_category': 0,
        'total_products_in_current_category': 0
    }
    
    for field, default in required_fields.items():
        if field not in progression:
            progression[field] = default
            repairs.append(f"added missing field {field}")
    
    # Log repairs if any were made
    if repairs:
        self.log.info(f"State repaired: {', '.join(repairs)}")
        self._atomic_save()
    
    return len(repairs) == 0, repairs
```

### 7. Module Path Logging System

**Current Issue:** Not implemented
**Location:** `tools/passive_extraction_workflow_latest.py`

**Required Implementation:**
```python
def __init__(self, supplier_name: str, use_predefined_categories: bool = False, **kwargs):
    """Initialize workflow with module path logging"""
    # Log module path for import hygiene
    self.log.info(f"MODULE PATH: {__file__}")
    
    # Check for duplicate workflow modules
    self._check_import_hygiene()
    
    # Continue with existing initialization...

def _check_import_hygiene(self):
    """Check for potential import conflicts with duplicate workflow files"""
    import glob
    import os
    
    # Look for other workflow files that might cause conflicts
    project_root = Path(__file__).parent.parent
    workflow_patterns = [
        "passive_extraction_workflow*.py",
        "*workflow*.py"
    ]
    
    potential_conflicts = []
    for pattern in workflow_patterns:
        matches = list(project_root.rglob(pattern))
        for match in matches:
            if match != Path(__file__) and 'archive' not in str(match) and 'backup' not in str(match):
                potential_conflicts.append(str(match))
    
    if potential_conflicts:
        self.log.warning(f"Potential workflow import conflicts detected: {potential_conflicts}")
        self.log.warning("Ensure you're importing from the canonical tools/ directory")
```

## Data Models

### CategoryManifest
```python
@dataclass
class CategoryManifest:
    category_url: str
    scraped_at: str  # ISO timestamp
    product_urls: List[str]
    count: int
    supplier_name: str
    slug: str
```

### FilterResults
```python
@dataclass
class FilterResults:
    input_count: int
    skip_entirely: List[str]
    needs_amazon_only: List[str]
    needs_full_extraction: List[str]
    
    def validate_invariant(self) -> bool:
        """Validate that all inputs are accounted for"""
        total = len(self.skip_entirely) + len(self.needs_amazon_only) + len(self.needs_full_extraction)
        return total == self.input_count
```

### StateValidationResult
```python
@dataclass
class StateValidationResult:
    is_valid: bool
    repairs_made: List[str]
    resumption_index: int
    category_index: int
```

## Error Handling

### Pagination Logging Failures
- **Detection**: Monitor for missing category index or invalid URL parsing
- **Recovery**: Use fallback values (index=0, slug="unknown")
- **Logging**: Log parsing failures with original URL

### Manifest Generation Failures
- **Detection**: File system errors, permission issues, JSON serialization failures
- **Recovery**: Retry with temporary directory, fallback to non-atomic writes
- **Logging**: Clear error messages with suggested actions

### State Validation Failures
- **Detection**: Missing required fields, invalid indices, corrupted data
- **Recovery**: Apply default values, correct bounds, rebuild missing sections
- **Logging**: Detailed repair log with before/after values

### Normalization Failures
- **Detection**: URL parsing errors, invalid EAN formats
- **Recovery**: Use original values as fallback
- **Logging**: Log normalization failures with input values

## Testing Strategy

### Unit Tests
1. **Pagination Format Tests**
   - Test category index calculation
   - Test slug generation from various URL formats
   - Test pagination summary with edge cases (0 pages, 1 page, many pages)

2. **Breadcrumb Generation Tests**
   - Test breadcrumb format with various phase/index combinations
   - Test handling of zero denominators
   - Test breadcrumb generation timing

3. **Manifest Generation Tests**
   - Test atomic manifest saving
   - Test overwrite detection and logging
   - Test manifest structure validation

4. **Filter Summary Tests**
   - Test invariant validation (skip + needs_amz + needs_full = in)
   - Test edge cases with empty results
   - Test filter summary format

5. **Normalization Tests**
   - Test URL normalization with tracking parameters
   - Test EAN normalization with leading zeros
   - Test normalization failure handling

6. **State Validation Tests**
   - Test repair of missing fields
   - Test bounds correction
   - Test monotonic progression validation

### Integration Tests
1. **End-to-End Category Processing**
   - Test complete category workflow with all logging
   - Verify manifest generation and filter summary
   - Check breadcrumb accuracy throughout processing

2. **Resume Functionality**
   - Test state validation on startup
   - Test resume from various interruption points
   - Verify breadcrumb accuracy after resume

3. **Multi-Category Processing**
   - Test category index progression
   - Test manifest generation for multiple categories
   - Verify filter summaries for each category

## Implementation Phases

### Phase 1: Logging Format Fixes (High Priority)
1. Fix pagination logging format with correct category indices and slugs
2. Fix breadcrumb logging with accurate denominators and timing
3. Add module path logging for import hygiene
4. Remove cache hit spam logging

### Phase 2: Manifest Generation (High Priority)
1. Implement atomic manifest saving with WindowsSaveGuardian
2. Add manifest logging with correct format
3. Implement overwrite detection and logging
4. Create manifest directory structure

### Phase 3: Filter Summary and Normalization (High Priority)
1. Implement clean filter summary logging
2. Add URL/EAN normalization utilities
3. Apply normalization consistently in filtering
4. Validate filter summary invariants

### Phase 4: State Management Enhancement (Medium Priority)
1. Implement validate_and_repair_state() functionality
2. Add state validation on startup
3. Implement automatic repair of common issues
4. Add detailed repair logging

### Phase 5: Category-Local Processing (Medium Priority)
1. Implement category-local queue building
2. Add sequential category processing (supplier → Amazon per category)
3. Add Amazon phase skipping when queue is empty
4. Implement proper phase transition logging

### Phase 6: Testing and Validation (Medium Priority)
1. Create comprehensive test suite for all fixes
2. Add log format validation
3. Implement invariant checking
4. Add performance monitoring

## Monitoring and Observability

### Key Metrics
- **Log Format Compliance**: Monitor for correct pagination, breadcrumb, and filter formats
- **Manifest Generation Rate**: Track successful manifest saves per category
- **State Validation Success**: Monitor state repair frequency and types
- **Filter Invariant Compliance**: Track filter summary mathematical accuracy
- **Normalization Success Rate**: Monitor URL/EAN normalization failures

### Alerting Thresholds
- Log format violations > 5%
- Manifest generation failures > 2%
- State validation failures > 1%
- Filter invariant violations > 1%
- Normalization failures > 10%

### Performance Targets
- Pagination logging: < 100ms per category
- Manifest generation: < 2 seconds per category
- State validation: < 5 seconds on startup
- Filter summary: < 1 second per category
- Normalization: < 10ms per URL/EAN

## Deployment Strategy

### Feature Flags
- **CORRECT_LOG_FORMATS=ON**: Enable corrected logging formats (default ON)
- **MANIFEST_GENERATION=ON**: Enable manifest generation (default ON)
- **STATE_VALIDATION=ON**: Enable state validation and repair (default ON)
- **URL_NORMALIZATION=ON**: Enable URL/EAN normalization (default ON)

### Rollout Plan
1. **Development Testing**: Test all fixes with sample categories
2. **Canary Deployment**: Deploy to 2-3 categories with monitoring
3. **Staged Rollout**: Deploy to 10-20 categories with validation
4. **Full Production**: Deploy to all categories with monitoring

### Success Criteria
- All required log formats appear correctly
- Manifest files generated for all processed categories
- State validation completes without errors
- Filter invariants hold for all categories
- No cache hit spam in logs
- Breadcrumbs show accurate denominators