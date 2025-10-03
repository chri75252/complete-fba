# Troubleshooting Guide Update - New Supplier Integration Fixes
**Date**: September 28, 2025  
**Based on**: Clearance-King integration fixes  
**For inclusion in**: docs/TROUBLESHOOTING.md

## 🔄 NEW SECTION: SUPPLIER INTEGRATION ISSUES

Add this new section after the "🔐 AUTHENTICATION ISSUES" section:

---

## 🏭 **SUPPLIER INTEGRATION ISSUES**

### **Issue: File Corruption During Integration**

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
head -5 tools/{supplier_name}/supplier_authentication_service.py

# Should show Python imports, not JSON:
# from playwright.async_api import Page
# import asyncio
# NOT: {"username": "...", "password": "..."}
```

**Root Cause:** File corruption during copy/paste operations or accidental overwrite with configuration data

**Solutions:**

1. **Verify File Integrity:**
   ```bash
   # Check all Python files in supplier directory
   for file in tools/{supplier_name}/*.py; do
       echo "Checking $file:"
       head -2 "$file"
       echo "---"
   done
   ```

2. **Restore from Known Good Source:**
   ```bash
   # Copy from working source
   cp tools/clearance_king_authentication_helper.py tools/{supplier_name}/supplier_authentication_service.py
   
   # Add compatibility alias
   echo "
   # Compatibility alias
   SupplierAuthenticationService = ClearanceKingAuthenticationHelper
   " >> tools/{supplier_name}/supplier_authentication_service.py
   ```

3. **Validate Python Syntax:**
   ```bash
   # Test syntax before running
   python -m py_compile tools/{supplier_name}/supplier_authentication_service.py
   ```

### **Issue: Missing Supplier-Specific Dependencies**

**Symptoms:**
- ModuleNotFoundError for utils modules
- ImportError for shared components
- Module resolution failures

**Example Error:**
```
ModuleNotFoundError: No module named 'utils.browser_circuit_breaker'
```

**Diagnosis:**
```bash
# Check import statements
grep -n "from utils\." tools/{supplier_name}/*.py

# Check if utils files exist in supplier directory
ls -la utils/{supplier_name}/
```

**Root Cause:** Supplier modules expect shared utils but need isolated copies for proper dependency resolution

**Solutions:**

1. **Copy Required Utils:**
   ```bash
   # Create utils directory for supplier
   mkdir -p utils/{supplier_name}
   
   # Copy browser circuit breaker
   cp utils/browser_circuit_breaker.py utils/{supplier_name}/browser_circuit_breaker.py
   
   # Copy other required utils as needed
   cp utils/windows_save_guardian.py utils/{supplier_name}/windows_save_guardian.py
   ```

2. **Update Import Paths:**
   ```bash
   # Update all imports in supplier modules
   # Change: from utils.browser_circuit_breaker import BrowserCircuitBreaker
   # To: from utils.{supplier_name}.browser_circuit_breaker import BrowserCircuitBreaker
   
   # Use sed for bulk updates (be careful)
   sed -i 's/from utils\./from utils.{supplier_name}./g' tools/{supplier_name}/*.py
   ```

3. **Verify Import Resolution:**
   ```python
   # Test imports
   import sys
   sys.path.append('.')
   
   # Test each import individually
   try:
       from utils.clearance_king.browser_circuit_breaker import BrowserCircuitBreaker
       print("✅ Browser circuit breaker import OK")
   except ImportError as e:
       print(f"❌ Import error: {e}")
   ```

### **Issue: Method Signature Mismatch**

**Symptoms:**
- "takes X positional arguments but Y were given" errors
- TypeError on method calls
- Parameter count mismatches

**Example Error:**
```
TypeError: ensure_authenticated_session() takes 2 positional arguments but 3 were given
```

**Diagnosis:**
```bash
# Check method signature in authentication service
grep -A 5 "def ensure_authenticated_session" tools/{supplier_name}/supplier_authentication_service.py

# Check how method is called
grep -B 2 -A 2 "ensure_authenticated_session" tools/{supplier_name}/*.py
```

**Root Cause:** Method signatures evolved during refactoring but calling code wasn't updated

**Solutions:**

1. **Update Method Signature:**
   ```python
   # Correct signature in supplier_authentication_service.py
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

2. **Verify All Method Calls:**
   ```bash
   # Find all method calls
   grep -rn "ensure_authenticated_session" tools/{supplier_name}/
   
   # Ensure they match the signature
   # Should be: auth_service.ensure_authenticated_session(page, credentials)
   ```

3. **Test Method Call:**
   ```python
   # Test method signature compatibility
   import inspect
   from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
   
   method = SupplierAuthenticationService.ensure_authenticated_session
   sig = inspect.signature(method)
   print(f"Method signature: {sig}")
   print(f"Parameter count: {len(sig.parameters)}")
   ```

### **Issue: Constructor Parameter Error**

**Symptoms:**
- TypeError during object initialization
- "unexpected keyword argument" errors
- Constructor parameter mismatches

**Example Error:**
```
TypeError: SupplierAuthenticationService.__init__() got an unexpected keyword argument 'browser_manager'
```

**Diagnosis:**
```bash
# Check constructor signature
grep -A 10 "def __init__" tools/{supplier_name}/supplier_authentication_service.py

# Check how object is initialized
grep -B 2 -A 2 "SupplierAuthenticationService(" tools/{supplier_name}/*.py run_custom_{supplier_name}.py
```

**Root Cause:** Constructor expects different parameters than what's being passed

**Solutions:**

1. **Fix Constructor Call:**
   ```python
   # In run_custom_{supplier_name}.py
   # Correct initialization
   auth_service = SupplierAuthenticationService(page)  # Pass page, not browser_manager
   
   # Not: auth_service = SupplierAuthenticationService(browser_manager)
   ```

2. **Verify Constructor Parameters:**
   ```python
   # Check constructor signature
   import inspect
   from tools.clearance_king.supplier_authentication_service import SupplierAuthenticationService
   
   init_method = SupplierAuthenticationService.__init__
   sig = inspect.signature(init_method)
   print(f"Constructor signature: {sig}")
   ```

3. **Update Constructor if Needed:**
   ```python
   # In supplier_authentication_service.py
   def __init__(self, page: Page):
       """Initialize with Playwright page object"""
       self.page = page
       # Not: def __init__(self, browser_manager):
   ```

### **Issue: Configuration Format Mismatch**

**Symptoms:**
- KeyError when loading categories
- "expected 'category_urls' but got 'categories'" errors
- Configuration parsing failures

**Example Error:**
```
KeyError: 'category_urls' not found in config file
```

**Diagnosis:**
```bash
# Check category configuration structure
python -c "
import json
with open('config/{supplier_name}_categories.json') as f:
    data = json.load(f)
    print('Keys found:', list(data.keys()))
    if 'categories' in data:
        print('Categories structure:', type(data['categories']))
        if data['categories']:
            print('Sample category:', data['categories'][0])
"
```

**Root Cause:** Different suppliers may use different configuration file structures

**Solutions:**

1. **Add Flexible Configuration Parsing:**
   ```python
   # In _get_predefined_categories method
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

2. **Validate Configuration Format:**
   ```python
   # Test configuration loading
   import json
   
   config_file = "config/clearance_king_categories.json"
   with open(config_file) as f:
       data = json.load(f)
   
   # Check structure
   if "category_urls" in data:
       print(f"✅ Found category_urls: {len(data['category_urls'])} categories")
   elif "categories" in data:
       print(f"✅ Found categories: {len(data['categories'])} categories")
       if data["categories"] and isinstance(data["categories"][0], dict):
           print("✅ Categories are objects with URL field")
       else:
           print("✅ Categories are simple URL strings")
   else:
       print("❌ No recognized category structure found")
   ```

3. **Standardize Configuration Format:**
   ```json
   // Recommended format for new suppliers
   {
     "categories": [
       {
         "name": "Electronics",
         "url": "https://supplier.com/electronics"
       },
       {
         "name": "Home & Garden", 
         "url": "https://supplier.com/home-garden"
       }
     ]
   }
   ```

### **Issue: State File Path Inconsistencies**

**Symptoms:**
- Processing state not saved correctly
- Resume functionality not working
- File path mismatch errors

**Diagnosis:**
```bash
# Check expected vs actual state file paths
ls -la OUTPUTS/CACHE/processing_states/

# Check what path is being used in code
grep -n "processing_state" tools/{supplier_name}/*.py
```

**Solutions:**

1. **Verify State File Paths:**
   ```python
   # Check state file path calculation
   supplier_name = "clearance-king.co.uk"
   expected_path = f"OUTPUTS/CACHE/processing_states/{supplier_name.replace('.', '_')}_processing_state.json"
   print(f"Expected state file: {expected_path}")
   
   # Should be: clearance-king_co_uk_processing_state.json
   # Not: clearance-king.co.uk_processing_state.json
   ```

2. **Test State Management:**
   ```python
   # Test state save/load
   from utils.enhanced_state_manager import EnhancedStateManager
   
   state_manager = EnhancedStateManager("clearance-king.co.uk")
   
   # Test save
   test_state = {"test": "data", "count": 1}
   state_manager.save_state(test_state)
   
   # Test load
   loaded_state = state_manager.load_state()
   print(f"State saved and loaded successfully: {loaded_state}")
   ```

### **General Integration Testing Checklist**

After implementing fixes, verify integration health:

```bash
# 1. File Integrity Check
echo "=== FILE INTEGRITY CHECK ==="
for file in tools/{supplier_name}/*.py; do
    python -m py_compile "$file" && echo "✅ $file" || echo "❌ $file"
done

# 2. Import Resolution Check  
echo "=== IMPORT RESOLUTION CHECK ==="
python -c "
import sys
sys.path.append('.')
try:
    from tools.{supplier_name}.supplier_authentication_service import SupplierAuthenticationService
    print('✅ Authentication service import OK')
except ImportError as e:
    print(f'❌ Authentication service import failed: {e}')

try:
    from utils.{supplier_name}.browser_circuit_breaker import BrowserCircuitBreaker
    print('✅ Browser circuit breaker import OK')
except ImportError as e:
    print(f'❌ Browser circuit breaker import failed: {e}')
"

# 3. Configuration Validation
echo "=== CONFIGURATION VALIDATION ==="
python -c "
import json
try:
    with open('config/{supplier_name}_categories.json') as f:
        data = json.load(f)
    print(f'✅ Category config loaded: {len(data.get(\"categories\", data.get(\"category_urls\", [])))} categories')
except Exception as e:
    print(f'❌ Category config error: {e}')

try:
    with open('config/system_config.json') as f:
        data = json.load(f)
    if '{supplier_name}.com' in data:
        print('✅ Supplier credentials configured')
    else:
        print('❌ Supplier credentials not found')
except Exception as e:
    print(f'❌ System config error: {e}')
"

# 4. Authentication Test
echo "=== AUTHENTICATION TEST ==="
python -c "
import asyncio
import sys
sys.path.append('.')

async def test_auth():
    try:
        from tools.{supplier_name}.supplier_authentication_service import SupplierAuthenticationService
        # Mock page for signature test
        class MockPage:
            pass
        
        auth_service = SupplierAuthenticationService(MockPage())
        print('✅ Authentication service instantiated successfully')
        
    except Exception as e:
        print(f'❌ Authentication service error: {e}')

asyncio.run(test_auth())
"

# 5. State Management Test
echo "=== STATE MANAGEMENT TEST ==="
python -c "
try:
    from utils.enhanced_state_manager import EnhancedStateManager
    state_manager = EnhancedStateManager('{supplier_name}.com')
    
    # Test paths
    expected_path = 'OUTPUTS/CACHE/processing_states/{supplier_name}_co_uk_processing_state.json'
    print(f'✅ State manager initialized for path: {expected_path}')
    
except Exception as e:
    print(f'❌ State manager error: {e}')
"
```

Expected output for successful integration:
```
=== FILE INTEGRITY CHECK ===
✅ tools/clearance_king/supplier_authentication_service.py
✅ tools/clearance_king/passive_extraction_workflow_clearance_king.py
✅ tools/clearance_king/configurable_supplier_scraper_clearance_king.py

=== IMPORT RESOLUTION CHECK ===
✅ Authentication service import OK
✅ Browser circuit breaker import OK

=== CONFIGURATION VALIDATION ===
✅ Category config loaded: 155 categories
✅ Supplier credentials configured

=== AUTHENTICATION TEST ===
✅ Authentication service instantiated successfully

=== STATE MANAGEMENT TEST ===
✅ State manager initialized for path: OUTPUTS/CACHE/processing_states/clearance-king_co_uk_processing_state.json
```

---

## SUMMARY OF NEW TROUBLESHOOTING SECTIONS

The following new troubleshooting sections should be added to docs/TROUBLESHOOTING.md:

1. **🏭 SUPPLIER INTEGRATION ISSUES** - Complete section with 5 major issue types
2. **File Corruption During Integration** - Detection and recovery procedures
3. **Missing Supplier-Specific Dependencies** - Dependency isolation fixes
4. **Method Signature Mismatch** - Parameter count and type fixes
5. **Constructor Parameter Error** - Object initialization fixes
6. **Configuration Format Mismatch** - Flexible config parsing
7. **General Integration Testing Checklist** - Comprehensive verification procedures

These sections are based on the actual fixes implemented during the successful clearance-king.co.uk integration and provide step-by-step resolution procedures for common integration issues.