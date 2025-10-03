# Clearance-King Troubleshooting Guide
**Version**: 1.1 (Corrected)
**Date**: September 29, 2025
**System**: Amazon FBA Agent System v3.7+
**Focus**: Clearance-king.co.uk specific issues

## 🎯 Overview

This guide covers troubleshooting steps specific to the clearance-king.co.uk integration, based on actual implementation experience and resolved issues.

## 🚨 Critical Issues Fixed

### Issue 1: File Corruption During Integration

**Symptoms:**
- Python files contain JSON data instead of Python code
- SyntaxError when importing supplier-specific modules
- "invalid syntax" errors on module import

**Example Error:**
```
SyntaxError: invalid syntax in tools/clearance_king/supplier_authentication_service.py
```

**Diagnosis:**
```bash
# Check file contents
head -5 tools/clearance_king/supplier_authentication_service.py

# Should show Python imports, not JSON:
# from playwright.async_api import Page
# import asyncio
# NOT: {"username": "...", "password": "..."}
```

**Root Cause:** File corruption during copy/paste operations or accidental overwrite with configuration data

**Solution Applied:**
1. **Located correct source**: `tools/clearance_king_authentication_helper.py`
2. **Copied and renamed**: `tools/clearance_king/supplier_authentication_service.py`
3. **Added compatibility alias**: `SupplierAuthenticationService = ClearanceKingAuthenticationHelper`

**Prevention:**
- Always verify file contents after copying
- Use `python -m py_compile` to test syntax before running

### Issue 2: Method Signature Mismatch

**Symptoms:**
- "takes X positional arguments but Y were given" errors
- TypeError on method calls
- Parameter count mismatches

**Example Error:**
```
TypeError: ensure_authenticated_session() takes 2 positional arguments but 3 were given
```

**Root Cause:** Method signatures evolved during refactoring but calling code wasn't updated

**Solution Applied:**
```python
# Updated method signature in supplier_authentication_service.py
async def ensure_authenticated_session(self, page: Page, credentials: Dict[str, str]) -> bool:
    """
    Authenticate with supplier website
    Args:
        page: Playwright page object
        credentials: Dict with username/password
    Returns:
        bool: True if authentication successful
    """
```

### Issue 3: Constructor Parameter Error

**Symptoms:**
- TypeError during object initialization
- "unexpected keyword argument" errors
- Constructor parameter mismatches

**Example Error:**
```
TypeError: SupplierAuthenticationService.__init__() got an unexpected keyword argument 'browser_manager'
```

**Solution Applied:**
```python
# Fixed in run_custom_clearance_king.py
auth_service = SupplierAuthenticationService(page)  # Pass page, not browser_manager
```

### Issue 4: Configuration Format Mismatch

**Symptoms:**
- KeyError when loading categories
- "expected 'category_urls' but got 'categories'" errors
- Configuration parsing failures

**Root Cause:** Different configuration file structures

**Solution Applied:**
```python
# Added flexible parsing in _get_predefined_categories method
def _get_predefined_categories(self, config_path: str) -> List[str]:
    """Load categories with flexible format support"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Support both "category_urls" and "categories" array structures
        category_urls = data.get("category_urls", [])
        if not category_urls and "categories" in data:
            # Handle array of objects with "url" field
            if isinstance(data["categories"], list):
                category_urls = [cat.get("url", cat) if isinstance(cat, dict) else cat
                               for cat in data["categories"]]

        return category_urls

    except Exception as e:
        self.logger.error(f"Failed to load categories from {config_path}: {e}")
        return []
```

### Issue 5: Circuit Breaker Dependencies (Corrected)

**Problem:** Incorrectly added circuit breaker dependencies when they're intentionally disabled

**Solution Applied:**
- Removed `utils/clearance_king` directory
- Circuit breaker is intentionally disabled system-wide
- No circuit breaker dependencies should be copied for any supplier integration

## 🔧 Clearance-King Specific Diagnostics

### Authentication Verification
```bash
# Test authentication manually
python -c "
import asyncio
import sys
sys.path.append('.')

async def test_auth():
    try:
        from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
        print('✅ Authentication service import successful')

        # Check constructor parameters
        import inspect
        init_sig = inspect.signature(SupplierAuthenticationService.__init__)
        print(f'✅ Constructor signature: {init_sig}')

    except Exception as e:
        print(f'❌ Authentication service error: {e}')

asyncio.run(test_auth())
"
```

### Configuration Validation
```bash
# Validate clearance-king configuration
python -c "
import json

# Check system config
try:
    with open('config/system_config.json') as f:
        config = json.load(f)
    if 'clearance-king.co.uk' in config:
        print('✅ Clearance-King credentials configured')
        print(f'   Username: {config[\"clearance-king.co.uk\"].get(\"username\", \"NOT SET\")}')
    else:
        print('❌ Clearance-King credentials not found')
except Exception as e:
    print(f'❌ System config error: {e}')

# Check category config
try:
    with open('config/clearance_king_categories.json') as f:
        categories = json.load(f)
    if 'categories' in categories:
        print(f'✅ Category config loaded: {len(categories[\"categories\"])} categories')
        print(f'   First category: {categories[\"categories\"][0][\"name\"]}')
    else:
        print('❌ No categories found in config')
except Exception as e:
    print(f'❌ Category config error: {e}')
"
```

### Processing State Check
```bash
# Check current processing status
python -c "
import json
import os

state_file = 'OUTPUTS/CACHE/processing_states/clearance-king_co_uk_processing_state.json'

if os.path.exists(state_file):
    with open(state_file) as f:
        state = json.load(f)

    print('=== CLEARANCE-KING PROCESSING STATUS ===')
    print(f'Status: {state.get(\"processing_status\", \"unknown\")}')
    print(f'Supplier Products Completed: {state.get(\"system_progression\", {}).get(\"supplier_products_completed\", 0)}')
    print(f'Supplier Products Total: {state.get(\"system_progression\", {}).get(\"supplier_products_needing_extraction\", 0)}')
    print(f'Current Category: {state.get(\"system_progression\", {}).get(\"current_category_url\", \"none\")}')
    print(f'Categories Progress: {state.get(\"system_progression\", {}).get(\"current_category_index\", 0) + 1}/{state.get(\"system_progression\", {}).get(\"total_categories\", 0)}')
else:
    print('❌ Processing state file not found')
"
```

### Product Cache Verification
```bash
# Check extracted products
python -c "
import json
import os

cache_file = 'OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json'

if os.path.exists(cache_file):
    with open(cache_file) as f:
        products = json.load(f)

    print('=== CLEARANCE-KING PRODUCT CACHE ===')
    print(f'Total Products: {len(products)}')

    if products:
        latest = products[-1]
        print(f'Latest Product: {latest.get(\"title\", \"No title\")}')
        print(f'Price: £{latest.get(\"price\", \"No price\")}')
        print(f'SKU: {latest.get(\"sku\", \"No SKU\")}')
        print(f'URL: {latest.get(\"url\", \"No URL\")}')
        print(f'Scraped: {latest.get(\"scraped_at\", \"No timestamp\")}')
    else:
        print('No products in cache yet')
else:
    print('❌ Product cache file not found')
"
```

## 🚨 Common Runtime Issues

### Issue: Authentication Failures
**Symptoms:**
- "Authentication failed" messages
- Unable to access product pages
- Repeated login attempts

**Diagnosis:**
```bash
# Check credentials in system config
grep -A 3 "clearance-king.co.uk" config/system_config.json

# Check recent authentication attempts in logs
grep -i "auth" logs/debug/run_custom_poundwholesale_*.log | tail -5
```

**Solutions:**
1. **Verify credentials manually** in browser
2. **Check for website changes** in login process
3. **Update credentials** if expired

### Issue: No Products Found
**Symptoms:**
- Categories process but no products extracted
- Empty product cache file
- "No products found" messages

**Diagnosis:**
```bash
# Check category URLs are still valid
python -c "
import json
with open('config/clearance_king_categories.json') as f:
    categories = json.load(f)
first_category = categories['categories'][0]['url']
print(f'Testing first category: {first_category}')
"

# Test category URL manually in browser
```

**Solutions:**
1. **Verify category URLs** are still valid
2. **Check for website structure changes**
3. **Update scraping selectors** if needed

### Issue: Processing Stalled
**Symptoms:**
- Processing state shows no progress
- Last updated timestamp is old
- No new products being added

**Diagnosis:**
```bash
# Check if process is running
ps aux | grep "run_custom_clearance_king" || echo "No clearance-king process running"

# Check last processing timestamp
python -c "
import json
from datetime import datetime
with open('OUTPUTS/CACHE/processing_states/clearance-king_co_uk_processing_state.json') as f:
    state = json.load(f)
last_update = state.get('last_updated', 'unknown')
print(f'Last updated: {last_update}')
"
```

**Solutions:**
1. **Restart the process** if stalled
2. **Check Chrome debug port** accessibility
3. **Verify system resources** (memory, CPU)

## 📋 Integration Health Check

Run this comprehensive health check for clearance-king integration:

```bash
echo "=== CLEARANCE-KING INTEGRATION HEALTH CHECK ==="

# 1. File Integrity
echo "1. File Integrity Check:"
python -m py_compile tools/clearance_king/supplier_authentication_service.py && echo "✅ Authentication service syntax OK" || echo "❌ Authentication service syntax error"

# 2. Import Resolution
echo "2. Import Resolution Check:"
python -c "
try:
    from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
    print('✅ Authentication service import OK')
except ImportError as e:
    print(f'❌ Import failed: {e}')
"

# 3. Configuration Validation
echo "3. Configuration Validation:"
python -c "
import json
try:
    with open('config/system_config.json') as f:
        config = json.load(f)
    assert 'clearance-king.co.uk' in config
    print('✅ System config OK')
except Exception as e:
    print(f'❌ System config error: {e}')

try:
    with open('config/clearance_king_categories.json') as f:
        categories = json.load(f)
    assert 'categories' in categories
    print('✅ Category config OK')
except Exception as e:
    print(f'❌ Category config error: {e}')
"

# 4. Output Files Check
echo "4. Output Files Check:"
ls -la OUTPUTS/cached_products/clearance-king-co-uk_products_cache.json 2>/dev/null && echo "✅ Product cache exists" || echo "❌ Product cache missing"
ls -la OUTPUTS/CACHE/processing_states/clearance-king_co_uk_processing_state.json 2>/dev/null && echo "✅ Processing state exists" || echo "❌ Processing state missing"

# 5. System Isolation Check
echo "5. System Isolation Check:"
ls -la OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json 2>/dev/null && echo "✅ Poundwholesale cache protected" || echo "❌ Poundwholesale cache missing"

echo "=== HEALTH CHECK COMPLETE ==="
```

## 📞 Support Quick Reference

When reporting clearance-king specific issues, include:

1. **Error Messages**: Exact error text and stack traces
2. **Configuration**: Contents of clearance-king specific configs
3. **Processing State**: Current processing state file contents
4. **Product Cache**: Number of products currently cached
5. **Logs**: Recent entries from debug logs related to clearance-king
6. **Health Check**: Output from the integration health check above

---

**Last Updated**: September 29, 2025
**Integration Status**: ✅ OPERATIONAL
**Products Extracted**: 1 product successfully (KIDS TOOTHBRUSHES)
**Contact**: Amazon FBA Agent System Team