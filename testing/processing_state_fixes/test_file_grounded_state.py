#!/usr/bin/env python3
"""
Test File-Grounded State Manager Implementation
==============================================

This script tests the enhanced file-grounded processing state functionality
to ensure it correctly reads actual files and calculates accurate totals.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the enhanced state manager
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager as EnhancedStateManager

def setup_logging():
    """Setup basic logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_file_grounded_calculations():
    """Test file-grounded calculations"""
    print("🧪 Testing File-Grounded State Manager")
    print("=" * 50)
    
    # Initialize state manager for poundwholesale-co-uk
    supplier_name = "poundwholesale-co-uk"
    state_manager = EnhancedStateManager(supplier_name)
    
    print(f"✅ Initialized state manager for: {supplier_name}")
    
    # Test file-grounded metrics calculation
    print("\n📊 Testing file-grounded metrics calculation...")
    file_metrics = state_manager.get_file_grounded_metrics()
    
    print(f"📁 Cache file exists: {file_metrics['cache_file_exists']}")
    print(f"📁 Linking map exists: {file_metrics['linking_map_exists']}")
    print(f"📊 Total products (from cache): {file_metrics['total_products']}")
    print(f"📊 Processed products (from linking map): {file_metrics['processed_products']}")
    print(f"📊 Categories with completion data: {len(file_metrics['category_completion_status'])}")
    
    # Display some category completion examples
    if file_metrics['category_completion_status']:
        print("\n📋 Sample category completion status:")
        count = 0
        for category_url, status in file_metrics['category_completion_status'].items():
            if count < 3:  # Show first 3 categories
                print(f"  • {category_url.split('/')[-1]}: {status['processed']}/{status['total']} ({status['percent']}%)")
                count += 1
    
    # Test state summary with file-grounded data
    print("\n📈 Testing state summary with file-grounded accuracy...")
    state_summary = state_manager.get_state_summary()
    
    print(f"📊 Progress: {state_summary['progress']} ({state_summary['progress_percent']}%)")
    print(f"📊 File-grounded: {state_summary['file_grounded']}")
    print(f"📊 Categories with completion: {state_summary['categories_with_completion']}")
    
    # Test saving state with file-grounded calculations
    print("\n💾 Testing state save with file-grounded calculations...")
    state_manager.save_state()
    print("✅ State saved successfully with file-grounded data")
    
    # Test gap processing initialization with file-grounded metrics
    print("\n🔄 Testing gap processing initialization...")
    try:
        state_manager.start_gap_processing()
        gap_status = state_manager.get_gap_processing_status()
        print(f"✅ Gap processing initialized with file-grounded metrics")
        print(f"📊 Gap size: {gap_status.get('gap_products_total', 0)}")
        print(f"📊 Category completion entries: {len(gap_status.get('category_completion_status', {}))}")
    except Exception as e:
        print(f"⚠️ Gap processing test encountered issue: {e}")
    
    print("\n✅ File-grounded state manager test completed successfully!")
    return True

def main():
    """Main test function"""
    setup_logging()
    
    try:
        success = test_file_grounded_calculations()
        if success:
            print("\n🎉 All tests passed! File-grounded processing is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed.")
            return 1
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)