# New Supplier Integration Walkthrough Guide
**Version**: 1.0  
**Date**: September 28, 2025  
**Based on**: Successful clearance-king.co.uk integration  
**System**: Amazon FBA Agent System v3.7+

## 🎯 Purpose

This guide provides a complete step-by-step walkthrough for integrating new suppliers into the Amazon FBA Agent System, based on the successful clearance-king.co.uk integration that extracted 48+ products and achieved complete system isolation.

## ⚠️ Prerequisites

### Required Knowledge
- Basic understanding of Python async/await patterns
- Familiarity with Playwright browser automation
- Understanding of JSON configuration files
- Basic command line usage

### System Requirements
- Chrome browser with debug port capability
- Python 3.8+ with required dependencies
- Sufficient disk space for product caches (1GB+ recommended)
- Stable internet connection for supplier authentication

### Existing System Status
- Existing supplier systems (e.g., poundwholesale.co.uk) must be functioning
- Amazon extraction components must be operational
- Browser automation infrastructure must be stable

## 🚀 Phase 1: Pre-Integration Analysis

### Step 1.1: Supplier Website Analysis
Before starting integration, analyze the target supplier website:

```bash
# Document the following information:
- Supplier URL: https://www.{supplier}.com
- Authentication method: Login form, OAuth, etc.
- Category structure: How products are organized
- Product data format: What information is available
- Anti-bot measures: Rate limits, CAPTCHA, etc.
```

### Step 1.2: Credential Preparation
Obtain valid credentials for the supplier:
- Username/email
- Password
- Any additional authentication tokens
- Test credentials manually in browser first

### Step 1.3: Category URL Collection
Create a list of category URLs to scrape:
- Identify all product categories
- Document category URLs
- Estimate total product count per category
- Plan processing order (start with smaller categories for testing)

## 🏗️ Phase 2: Infrastructure Setup

### Step 2.1: Core Script Duplication
Create supplier-specific versions of core scripts:

```bash
# 1. Create supplier directory
mkdir tools/{supplier_name}
mkdir utils/{supplier_name}

# 2. Copy core workflow script
cp passive_extraction_workflow_latest.py tools/{supplier_name}/passive_extraction_workflow_{supplier_name}.py

# 3. Copy supplier scraper
cp tools/configurable_supplier_scraper.py tools/{supplier_name}/configurable_supplier_scraper_{supplier_name}.py

# 4. Create entry point
cp run_custom_poundwholesale.py run_custom_{supplier_name}.py
```

### Step 2.2: Entry Point Configuration
Edit `run_custom_{supplier_name}.py`:

```python
# Update these key lines:
supplier_name = "{supplier_name}.com"  # Line ~15
config_key = "{supplier_name}_workflow"  # Line ~20

# Import supplier-specific modules
from tools.{supplier_name}.passive_extraction_workflow_{supplier_name} import PassiveExtractionWorkflow
```

### Step 2.3: Workflow Script Parameterization
Edit `tools/{supplier_name}/passive_extraction_workflow_{supplier_name}.py`:

**Critical Lines to Update** (based on clearance-king implementation):
- Line ~1834: Category config path
- Line ~7334: Manifest path
- Line ~11727: Supplier URL
- Line ~11732: Supplier name
- All credential reference keys

```python
# Example updates:
# Line 1834: Category config path
category_config_path = f"config/{supplier_name}_categories.json"

# Line 7334: Manifest path  
manifest_path = f"OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/"

# Line 11727: Supplier URL
supplier_url = f"https://www.{supplier_name}.com"

# Line 11732: Supplier name
supplier_name = f"{supplier_name}.com"
```

### Step 2.4: Configuration Files Setup

**A. System Configuration**
Add to `config/system_config.json`:

```json
{
  "{supplier_name}.com": {
    "username": "your_username",
    "password": "your_password"
  },
  "{supplier_name}_workflow": {
    "supplier_name": "{supplier_name}.com",
    "supplier_url": "https://www.{supplier_name}.com",
    "use_predefined_categories": true,
    "max_price_gbp": 50,
    "min_price_gbp": 0.01
  }
}
```

**B. Category Configuration**
Create `config/{supplier_name}_categories.json`:

```json
{
  "categories": [
    {
      "name": "Category 1",
      "url": "https://www.{supplier_name}.com/category1"
    },
    {
      "name": "Category 2", 
      "url": "https://www.{supplier_name}.com/category2"
    }
  ]
}
```

## 🔧 Phase 3: Authentication Service Implementation

### Step 3.1: Authentication Service Creation
Create `tools/{supplier_name}/supplier_authentication_service.py`:

```python
from playwright.async_api import Page
from typing import Dict
import asyncio

class SupplierAuthenticationService:
    def __init__(self, page: Page):
        self.page = page
        
    async def ensure_authenticated_session(self, page: Page, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with supplier website
        Returns True if authentication successful
        """
        try:
            # Navigate to login page
            await page.goto(f"https://www.{supplier_name}.com/login")
            
            # Fill login form (customize selectors)
            await page.fill('input[name="username"]', credentials["username"])
            await page.fill('input[name="password"]', credentials["password"])
            
            # Submit login
            await page.click('button[type="submit"]')
            
            # Wait for authentication confirmation
            await page.wait_for_selector('.user-dashboard', timeout=30000)
            
            return True
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
```

### Step 3.2: Dependency Resolution
Copy required utilities to supplier directory:

```bash
# Copy browser circuit breaker
cp utils/browser_circuit_breaker.py utils/{supplier_name}/browser_circuit_breaker.py

# Update import paths in all supplier scripts
# Change: from utils.browser_circuit_breaker import BrowserCircuitBreaker
# To: from utils.{supplier_name}.browser_circuit_breaker import BrowserCircuitBreaker
```

## 🧪 Phase 4: Testing and Verification

### Step 4.1: Initial Connection Test
Test basic connectivity:

```bash
# Run entry point script
python run_custom_{supplier_name}.py

# Expected outputs:
# 1. Authentication success message
# 2. Category loading confirmation
# 3. First product extraction
```

### Step 4.2: Critical Error Resolution

**Common Error Patterns** (based on clearance-king fixes):

**Error 1: File Corruption**
```
Symptom: SyntaxError when importing modules
Solution: Verify all .py files contain Python code, not JSON
Action: Re-copy from source if corrupted
```

**Error 2: Missing Dependencies**
```
Symptom: ModuleNotFoundError for utils modules
Solution: Copy required utils to supplier-specific directories
Action: Update import paths in all modules
```

**Error 3: Method Signature Mismatch**
```
Symptom: "takes X arguments but Y were given"
Solution: Update method signatures to match calling code
Action: Check constructor parameters and method calls
```

**Error 4: Configuration Format Issues**
```
Symptom: KeyError when loading categories
Solution: Support multiple configuration formats
Action: Add flexible parsing logic
```

### Step 4.3: Output Verification
Verify all expected files are created:

```bash
# Check product cache
ls -la "OUTPUTS/cached_products/{supplier_name}_products_cache.json"

# Check processing state
ls -la "OUTPUTS/CACHE/processing_states/{supplier_name}_processing_state.json"

# Check Amazon cache files
ls -la "OUTPUTS/FBA_ANALYSIS/amazon_cache/" | head -10

# Check debug logs
ls -la "logs/debug/run_custom_poundwholesale_*.log" | tail -1
```

### Step 4.4: System Isolation Verification
Ensure existing systems are unaffected:

```bash
# Check poundwholesale files haven't changed
ls -la "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"

# Verify timestamps are unchanged
stat "OUTPUTS/CACHE/processing_states/poundwholesale-co-uk_processing_state.json"

# Test poundwholesale system still works
python run_custom_poundwholesale.py --test-mode
```

## 📊 Phase 5: Production Deployment

### Step 5.1: Performance Monitoring
Monitor key metrics during initial run:

```bash
# Product extraction rate (target: 3-5 products/minute)
# Memory usage (should remain stable)
# Authentication success rate (target: 100%)
# Error rate (target: <1%)
```

### Step 5.2: Scaling Considerations
For high-volume suppliers:

- Implement batch processing for large categories
- Add memory management for long-running sessions
- Configure appropriate rate limiting
- Set up monitoring for extended runs

### Step 5.3: Documentation Update
Document the new integration:

```bash
# Update system documentation
# Add supplier-specific troubleshooting guide
# Document any unique authentication requirements
# Record performance benchmarks
```

## 🚨 Critical Success Factors

### 1. File Integrity Verification
**Always verify** that copied files contain expected content:
```bash
# Check first few lines of Python files
head -5 tools/{supplier_name}/supplier_authentication_service.py
# Should show Python imports, not JSON data
```

### 2. Dependency Isolation
**Never assume** shared utils will work:
- Copy all required utils to supplier directories
- Update all import paths consistently
- Test import resolution before running

### 3. Method Signature Consistency
**Always verify** method signatures match usage:
- Check constructor parameters match initialization code
- Verify async method signatures are consistent
- Test all method calls have correct parameter counts

### 4. Configuration Format Flexibility
**Build robust** configuration parsers:
- Support multiple JSON structures
- Provide clear error messages for invalid configs
- Default to safe fallback values when possible

### 5. Authentication Validation
**Test authentication** independently:
- Verify credentials work in browser first
- Test authentication service in isolation
- Monitor authentication success rates in production

## 📋 Troubleshooting Checklist

### Pre-Flight Checklist
- [ ] Supplier credentials tested manually in browser
- [ ] All required files copied to supplier directories
- [ ] Configuration files created with correct format
- [ ] Import paths updated in all modules
- [ ] Entry point script configured for new supplier

### Runtime Verification
- [ ] Authentication succeeds on first attempt
- [ ] Categories load without errors
- [ ] First product extracts successfully
- [ ] Output files created in expected locations
- [ ] Processing state updates correctly

### Post-Integration Validation
- [ ] No impact on existing supplier systems
- [ ] All expected output files contain valid data
- [ ] System can resume from interruption
- [ ] Performance metrics meet expectations
- [ ] Error rates within acceptable limits

## 🎯 Success Metrics

A successful integration should achieve:

- **Authentication Success**: 100% on first attempt
- **Product Extraction**: At least 1 product extracted
- **Output Files**: All expected files created with valid data
- **System Isolation**: Zero impact on existing suppliers
- **Performance**: 3-5 products extracted per minute
- **Resumability**: System can restart and continue from interruption

## 🔄 Maintenance and Updates

### Regular Monitoring
- Check authentication success rates weekly
- Monitor product extraction rates
- Verify output file integrity
- Watch for supplier website changes

### Update Procedures
- Test authentication changes in staging first
- Update category configurations quarterly
- Monitor for new anti-bot measures
- Keep documentation synchronized with changes

---

**Generated**: September 28, 2025  
**Based on**: Clearance-King successful integration (48+ products extracted)  
**Next Update**: Upon completion of next supplier integration  
**Contact**: Amazon FBA Agent System Team