#!/usr/bin/env python3
"""
Resume Functionality Test - Validate State Consistency for Resume
Tests that the state can be properly loaded and resume points calculated
"""

import json
import sys
from pathlib import Path

def test_state_loading():
    """Test that state can be loaded without errors"""
    try:
        with open("OUTPUTS/processing_state.json", 'r') as f:
            state = json.load(f)
        print("✅ State file loads successfully")
        return True, state
    except Exception as e:
        print(f"❌ Failed to load state: {e}")
        return False, None

def test_resume_point_calculation(state):
    """Test resume point calculation logic"""
    try:
        # Extract key resume indicators
        last_processed = state.get("last_processed_index", 0)
        resumption_index = state.get("resumption_index", 0)
        progress_index = state.get("progress_index", 0)
        
        supplier_progress = state.get("supplier_extraction_progress", {})
        current_category_index = supplier_progress.get("current_category_index", 0)
        current_category_url = supplier_progress.get("current_category_url", "")
        
        print(f"📊 Resume Point Analysis:")
        print(f"   - Last Processed Index: {last_processed}")
        print(f"   - Resumption Index: {resumption_index}")
        print(f"   - Progress Index: {progress_index}")
        print(f"   - Current Category Index: {current_category_index}")
        print(f"   - Current Category URL: {current_category_url}")
        
        # Validate resume point consistency
        if last_processed == resumption_index == progress_index:
            print("✅ Resume indices are consistent")
            return True
        else:
            print("❌ Resume indices are inconsistent")
            return False
            
    except Exception as e:
        print(f"❌ Resume point calculation failed: {e}")
        return False

def test_processed_products_integrity(state):
    """Test processed products data integrity"""
    try:
        processed_products = state.get("processed_products", {})
        successful_products = state.get("successful_products", 0)
        
        actual_count = len(processed_products)
        
        print(f"📦 Processed Products Analysis:")
        print(f"   - Processed Products Dict: {actual_count} entries")
        print(f"   - Successful Products Count: {successful_products}")
        
        if actual_count == successful_products:
            print("✅ Processed products count matches successful count")
            
            # Sample some processed products
            sample_products = list(processed_products.items())[:3]
            print(f"   - Sample products:")
            for url, data in sample_products:
                status = data.get("status", "unknown")
                timestamp = data.get("timestamp", "unknown")
                print(f"     • {url[:50]}... -> {status} @ {timestamp}")
            
            return True
        else:
            print(f"❌ Count mismatch: {actual_count} != {successful_products}")
            return False
            
    except Exception as e:
        print(f"❌ Processed products integrity check failed: {e}")
        return False

def test_category_progression_state(state):
    """Test category progression state for resume"""
    try:
        supplier_progress = state.get("supplier_extraction_progress", {})
        system_progression = state.get("system_progression", {})
        
        print(f"🏗️ Category Progression Analysis:")
        
        # Check supplier progress
        current_cat_idx = supplier_progress.get("current_category_index", 0)
        total_categories = supplier_progress.get("total_categories", 0)
        current_url = supplier_progress.get("current_category_url", "")
        
        print(f"   - Supplier Progress: {current_cat_idx}/{total_categories}")
        print(f"   - Current Category: {current_url}")
        
        # Check system progression
        sys_cat_idx = system_progression.get("current_category_index", 0)
        sys_url = system_progression.get("current_category_url", "")
        
        print(f"   - System Progress: {sys_cat_idx}")
        print(f"   - System Category: {sys_url}")
        
        # Validate consistency
        if current_cat_idx == sys_cat_idx and current_url == sys_url:
            print("✅ Category progression is consistent")
            return True
        else:
            print("❌ Category progression inconsistency detected")
            return False
            
    except Exception as e:
        print(f"❌ Category progression check failed: {e}")
        return False

def test_gap_processing_state(state):
    """Test gap processing state for resume"""
    try:
        gap_processing = state.get("gap_processing", {})
        
        phase = gap_processing.get("phase", "unknown")
        gap_total = gap_processing.get("gap_products_total", 0)
        gap_processed = gap_processing.get("gap_products_processed", 0)
        startup_completed = gap_processing.get("startup_analysis_completed", False)
        
        print(f"🔄 Gap Processing Analysis:")
        print(f"   - Phase: {phase}")
        print(f"   - Gap Products: {gap_processed}/{gap_total}")
        print(f"   - Startup Analysis: {startup_completed}")
        
        # Gap processing should be in a valid state
        if phase in ["not_started", "gap_processing", "completed"]:
            print("✅ Gap processing state is valid")
            return True
        else:
            print(f"❌ Invalid gap processing phase: {phase}")
            return False
            
    except Exception as e:
        print(f"❌ Gap processing check failed: {e}")
        return False

def run_resume_tests(dry_run=True):
    """Run all resume functionality tests"""
    print("🧪 Resume Functionality Test Suite")
    print("=" * 50)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No state modifications")
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: State Loading
    print("\n1️⃣ Testing State Loading...")
    success, state = test_state_loading()
    if success:
        tests_passed += 1
    
    if not state:
        print("💥 Cannot continue tests without valid state")
        return False
    
    # Test 2: Resume Point Calculation
    print("\n2️⃣ Testing Resume Point Calculation...")
    if test_resume_point_calculation(state):
        tests_passed += 1
    
    # Test 3: Processed Products Integrity
    print("\n3️⃣ Testing Processed Products Integrity...")
    if test_processed_products_integrity(state):
        tests_passed += 1
    
    # Test 4: Category Progression State
    print("\n4️⃣ Testing Category Progression State...")
    if test_category_progression_state(state):
        tests_passed += 1
    
    # Test 5: Gap Processing State
    print("\n5️⃣ Testing Gap Processing State...")
    if test_gap_processing_state(state):
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All resume functionality tests passed!")
        return True
    else:
        print("💥 Some resume functionality tests failed!")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test resume functionality")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run in dry-run mode")
    
    args = parser.parse_args()
    
    success = run_resume_tests(dry_run=args.dry_run)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())