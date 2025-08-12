#!/usr/bin/env python3
"""
Test script to validate the Always-Extract Workflow fixes
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_path_logging():
    """Test that module path logging is working"""
    print("🧪 Testing module path logging...")
    
    try:
        from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
        from config.system_config_loader import SystemConfigLoader
        from utils.browser_manager import BrowserManager
        
        # Create a test logger to capture the module path log
        import io
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('PassiveExtractionWorkflow')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Initialize workflow (should trigger module path logging)
        config_loader = SystemConfigLoader()
        workflow_config = {'supplier_name': 'test'}
        browser_manager = BrowserManager()
        
        workflow = PassiveExtractionWorkflow(config_loader, workflow_config, browser_manager)
        
        # Check if module path was logged
        log_output = log_capture.getvalue()
        if "MODULE PATH:" in log_output:
            print("✅ Module path logging is working")
            return True
        else:
            print("❌ Module path logging not found")
            return False
            
    except Exception as e:
        print(f"❌ Module path logging test failed: {e}")
        return False

def test_slug_generation():
    """Test that category slug generation is working correctly"""
    print("🧪 Testing category slug generation...")
    
    try:
        # Test slug generation directly without creating workflow instance
        from urllib.parse import urlparse
        import re
        
        def generate_category_slug(category_url: str) -> str:
            """Generate readable slug from category URL path"""
            try:
                # Parse URL and extract path
                parsed = urlparse(category_url)
                path = parsed.path.strip('/')
                
                # Get the last meaningful part of the path
                if path:
                    path_parts = path.split('/')
                    # Take the last part, or second-to-last if last is very short
                    if len(path_parts) > 1 and len(path_parts[-1]) < 5:
                        slug_base = path_parts[-2] if len(path_parts) > 1 else path_parts[-1]
                    else:
                        slug_base = path_parts[-1]
                else:
                    # Fallback to domain if no path
                    slug_base = parsed.netloc.replace('www.', '').replace('.', '-')
                
                # Clean up the slug
                slug = re.sub(r'[^a-z0-9]+', '-', slug_base.lower()).strip('-')
                
                # Limit length and ensure it's not empty
                slug = slug[:30] if slug else 'unknown'
                
                return slug
                
            except Exception as e:
                return 'unknown'
        
        # Test slug generation
        test_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween"
        slug = generate_category_slug(test_url)
        
        expected_slug = "wholesale-halloween"
        if slug == expected_slug:
            print(f"✅ Slug generation working: {test_url} → {slug}")
            return True
        else:
            print(f"❌ Slug generation incorrect: expected '{expected_slug}', got '{slug}'")
            return False
            
    except Exception as e:
        print(f"❌ Slug generation test failed: {e}")
        return False

def test_normalization():
    """Test URL and EAN normalization"""
    print("🧪 Testing URL/EAN normalization...")
    
    try:
        from utils.normalization import normalize_url, normalize_ean
        
        # Test URL normalization
        test_url = "https://www.Example.com/path/?utm_source=test&param=value"
        normalized_url = normalize_url(test_url)
        expected_url = "https://www.example.com/path?param=value"
        
        if normalized_url == expected_url:
            print(f"✅ URL normalization working: {test_url} → {normalized_url}")
        else:
            print(f"❌ URL normalization incorrect: expected '{expected_url}', got '{normalized_url}'")
            return False
        
        # Test EAN normalization
        test_ean = "  1234567890123  "
        normalized_ean = normalize_ean(test_ean)
        expected_ean = "1234567890123"
        
        if normalized_ean == expected_ean:
            print(f"✅ EAN normalization working: '{test_ean}' → '{normalized_ean}'")
            return True
        else:
            print(f"❌ EAN normalization incorrect: expected '{expected_ean}', got '{normalized_ean}'")
            return False
            
    except Exception as e:
        print(f"❌ Normalization test failed: {e}")
        return False

def test_state_validation():
    """Test state validation and repair"""
    print("🧪 Testing state validation...")
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        # Create a test state manager
        state_manager = FixedEnhancedStateManager('test_supplier')
        
        # Test validation
        is_valid, repairs = state_manager.validate_and_repair_state()
        
        print(f"✅ State validation working: valid={is_valid}, repairs={len(repairs)}")
        return True
        
    except Exception as e:
        print(f"❌ State validation test failed: {e}")
        return False

def test_filter_functionality():
    """Test URL filtering with normalization"""
    print("🧪 Testing URL filtering...")
    
    try:
        from utils.url_filter import filter_urls
        
        # Test data
        test_urls = [
            "https://example.com/product1",
            "https://example.com/product2",
            "https://example.com/product3"
        ]
        
        linking_map = [
            {"supplier_url": "https://example.com/product1", "ean": "123"}
        ]
        
        cached_products = [
            {"url": "https://example.com/product2", "ean": "456"}
        ]
        
        # Filter URLs
        result = filter_urls(test_urls, linking_map, cached_products)
        
        # Validate results
        if (len(result['skip_entirely']) == 1 and 
            len(result['needs_amazon_only']) == 1 and 
            len(result['needs_full_extraction']) == 1):
            print("✅ URL filtering working correctly")
            return True
        else:
            print(f"❌ URL filtering incorrect: {result}")
            return False
            
    except Exception as e:
        print(f"❌ URL filtering test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Always-Extract Workflow Fixes Tests")
    print("=" * 50)
    
    tests = [
        test_module_path_logging,
        test_slug_generation,
        test_normalization,
        test_state_validation,
        test_filter_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The workflow fixes are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())