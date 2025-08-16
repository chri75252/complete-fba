#!/usr/bin/env python3
"""
Test script to verify both missing sections are restored
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
import json

def test_sections_restoration():
    """Test that both missing sections are restored"""
    
    print("🔧 Testing sections restoration...")
    
    # Initialize state manager
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    
    # Load existing state
    state_loaded = state_manager.load_state()
    print(f"✅ State loaded: {state_loaded}")
    
    # Check category_completion_status section
    gap_processing = state_manager.state_data.get("gap_processing", {})
    category_completion_status = gap_processing.get("category_completion_status", {})
    
    print(f"📊 Category completion status: {len(category_completion_status)} categories")
    if len(category_completion_status) > 0:
        # Show first few categories
        for i, (url, status) in enumerate(list(category_completion_status.items())[:3]):
            print(f"   • {url}: {status['processed']}/{status['extracted']} ({status['completion_pct']}%) - {status['status']}")
        if len(category_completion_status) > 3:
            print(f"   • ... and {len(category_completion_status) - 3} more categories")
    
    # Check categories_completed array
    sep = state_manager.state_data.get("supplier_extraction_progress", {})
    categories_completed = sep.get("categories_completed", [])
    print(f"📋 Categories completed array: {len(categories_completed)} entries")
    
    if len(categories_completed) > 0:
        print(f"   • First completed: {categories_completed[0]}")
        print(f"   • Last completed: {categories_completed[-1]}")
    
    # Save state to ensure sections are persisted
    state_manager.save_state()
    print("✅ State saved with restored sections")
    
    return len(category_completion_status) > 0 and len(categories_completed) > 0

if __name__ == "__main__":
    success = test_sections_restoration()
    if success:
        print("🎉 Both sections successfully restored!")
    else:
        print("❌ Sections restoration failed")