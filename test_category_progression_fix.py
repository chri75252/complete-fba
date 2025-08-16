#!/usr/bin/env python3
"""
Test script to verify category progression section is restored
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
import json

def test_category_progression_fix():
    """Test that category progression section is generated"""
    
    print("🔧 Testing category progression fix...")
    
    # Initialize state manager
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    
    # Load existing state
    state_loaded = state_manager.load_state()
    print(f"✅ State loaded: {state_loaded}")
    
    # Check if category_progression section exists
    if "category_progression" in state_manager.state_data:
        progression = state_manager.state_data["category_progression"]
        print(f"✅ Category progression section found:")
        print(f"   • Total categories: {progression.get('total_categories', 0)}")
        print(f"   • Completed categories: {progression.get('completed_categories', 0)}")
        print(f"   • Completion percentage: {progression.get('completion_percentage', 0)}%")
        print(f"   • Last updated: {progression.get('last_updated', 'N/A')}")
    else:
        print("❌ Category progression section missing")
    
    # Check categories_completed array
    sep = state_manager.state_data.get("supplier_extraction_progress", {})
    categories_completed = sep.get("categories_completed", [])
    print(f"📊 Categories completed array: {len(categories_completed)} entries")
    
    if len(categories_completed) > 0:
        print(f"   • First completed: {categories_completed[0]}")
        print(f"   • Last completed: {categories_completed[-1]}")
    
    # Save state to ensure progression is persisted
    state_manager.save_state()
    print("✅ State saved with category progression")
    
    return len(categories_completed) > 0

if __name__ == "__main__":
    test_category_progression_fix()