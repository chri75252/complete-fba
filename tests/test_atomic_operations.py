#!/usr/bin/env python3
"""
Unit Tests for Atomic Operations
Tests the atomic file operations and state management
"""

import os
import sys
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.atomic_file_operations import AtomicFileOperations, atomic_json_write, atomic_json_read
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

class TestAtomicOperations(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.atomic_ops = AtomicFileOperations()
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_atomic_write_json(self):
        """Test atomic JSON writing."""
        test_file = self.temp_dir / "test.json"
        test_data = {"test": "data", "count": 42}
        
        success = self.atomic_ops.atomic_write_json(test_file, test_data)
        self.assertTrue(success)
        self.assertTrue(test_file.exists())
        
        # Verify content
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)
    
    def test_atomic_read_json(self):
        """Test atomic JSON reading."""
        test_file = self.temp_dir / "test.json"
        test_data = {"read": "test", "value": 123}
        
        # Write test data
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Read atomically
        loaded_data = self.atomic_ops.atomic_read_json(test_file)
        self.assertEqual(loaded_data, test_data)
        
        # Test non-existent file
        non_existent = self.temp_dir / "does_not_exist.json"
        result = self.atomic_ops.atomic_read_json(non_existent)
        self.assertIsNone(result)
    
    def test_concurrent_write_safety(self):
        """Test that concurrent writes are thread-safe."""
        test_file = self.temp_dir / "concurrent.json"
        results = []
        errors = []
        
        def writer_thread(thread_id):
            try:
                data = {"thread": thread_id, "timestamp": time.time()}
                success = self.atomic_ops.atomic_write_json(test_file, data)
                results.append((thread_id, success))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Start multiple writer threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=writer_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
        
        # File should exist and be valid JSON
        self.assertTrue(test_file.exists())
        self.assertTrue(self.atomic_ops.validate_json_integrity(test_file))
    
    def test_json_validation(self):
        """Test JSON file validation."""
        # Valid JSON file
        valid_file = self.temp_dir / "valid.json"
        with open(valid_file, 'w') as f:
            json.dump({"valid": True}, f)
        
        self.assertTrue(self.atomic_ops.validate_json_integrity(valid_file))
        
        # Invalid JSON file
        invalid_file = self.temp_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("invalid json content {")
        
        self.assertFalse(self.atomic_ops.validate_json_integrity(invalid_file))
        
        # Non-existent file
        non_existent = self.temp_dir / "does_not_exist.json"
        self.assertFalse(self.atomic_ops.validate_json_integrity(non_existent))

class TestFixedEnhancedStateManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        # Mock the state file path
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_atomic_commit_methods(self):
        """Test that atomic commit methods work correctly."""
        # Create state manager
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Test supplier progress commit
        state_manager.commit_supplier_progress(
            cat_idx=1,
            prod_idx=5,
            total_cats=10,
            cat_url="https://test.com/category",
            total_prod_in_cat=20
        )
        
        # Verify state was updated
        sp = state_manager.state_data.get("system_progression", {})
        self.assertEqual(sp.get("current_phase"), "supplier")
        self.assertEqual(sp.get("current_category_index"), 1)
        self.assertEqual(sp.get("current_product_index_in_category"), 5)
        
        # Test Amazon progress commit
        state_manager.commit_amazon_progress(
            cat_idx=2,
            queue_idx=10,
            total_cats=10,
            cat_url="https://test.com/category2",
            queue_len=50
        )
        
        # Verify state was updated
        sp = state_manager.state_data.get("system_progression", {})
        self.assertEqual(sp.get("current_phase"), "amazon_analysis")
        self.assertEqual(sp.get("current_category_index"), 2)
        self.assertEqual(sp.get("current_product_index_in_category"), 10)
    
    def test_cross_run_monotonicity(self):
        """Test cross-run monotonicity validation."""
        # Create state manager with initial state
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Set up initial state
        state_manager.state_data["system_progression"] = {
            "current_category_index": 5,
            "current_product_index_in_category": 10
        }
        state_manager.state_data["resumption_index"] = 100
        
        # Simulate saving and loading (cross-run scenario)
        state_manager._validate_cross_run_monotonicity()
        
        # Try to set backward values (should be corrected)
        state_manager.state_data["system_progression"]["current_category_index"] = 3  # Backward
        state_manager.state_data["resumption_index"] = 50  # Backward
        
        # Validation should correct these
        state_manager._validate_cross_run_monotonicity()
        
        # Check that values were corrected
        sp = state_manager.state_data.get("system_progression", {})
        self.assertGreaterEqual(sp.get("current_category_index", 0), 5)
        self.assertGreaterEqual(state_manager.state_data.get("resumption_index", 0), 100)
    
    def test_legacy_method_disabled(self):
        """Test that legacy update_processing_index is disabled."""
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # This should raise NotImplementedError
        with self.assertRaises(NotImplementedError):
            state_manager.update_processing_index(10, 100)
    
    def test_resume_proof_banners(self):
        """Test that resume proof banners are logged."""
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Capture log output
        import logging
        import io
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        try:
            # First call should log "FIRST AFTER-RESUME KEY"
            state_manager.log_resume_proof_after_commit("test_context")
            
            # Second call should log "RESUME HONORED"
            state_manager.log_resume_proof_after_commit("test_context2")
            
            log_output = log_capture.getvalue()
            self.assertIn("FIRST AFTER-RESUME KEY", log_output)
            self.assertIn("RESUME HONORED", log_output)
            
        finally:
            logger.removeHandler(handler)

def run_tests():
    """Run all tests and return results."""
    print("🧪 RUNNING ATOMIC OPERATIONS TESTS...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAtomicOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestFixedEnhancedStateManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Total: {total_tests}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failures}")
    print(f"   Errors: {errors}")
    
    success = failures == 0 and errors == 0
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        
    return success

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
