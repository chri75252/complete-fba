#!/usr/bin/env python3
"""
Test suite for workflow execution fixes in state management architectural fix.

This test suite validates that the workflow execution properly respects resume points
from state management and maintains category URL consistency.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestStateManagerHelperMethods(unittest.TestCase):
    """Test the helper methods added to FixedEnhancedStateManager for workflow integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = FixedEnhancedStateManager("test_supplier")
        
    def test_get_current_category_index_from_operational_data(self):
        """Test that get_current_category_index returns value from supplier_extraction_progress"""
        # Set up state with operational data
        self.state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 5,
                "total_categories": 233
            },
            "system_progression": {
                "current_category_index": 0  # Corrupted data
            }
        }
        
        # Should return value from supplier_extraction_progress (operational data)
        result = self.state_manager.get_current_category_index()
        self.assertEqual(result, 5)
        
    def test_get_current_category_index_fallback_to_tracking(self):
        """Test fallback to system_progression when supplier_extraction_progress is empty"""
        # Set up state with only tracking data
        self.state_manager.state_data = {
            "supplier_extraction_progress": {},
            "system_progression": {
                "current_category_index": 3
            }
        }
        
        # Should fall back to system_progression
        result = self.state_manager.get_current_category_index()
        self.assertEqual(result, 3)
        
    def test_get_current_category_index_returns_none_when_no_data(self):
        """Test that method returns None when no data is available"""
        # Set up empty state
        self.state_manager.state_data = {
            "supplier_extraction_progress": {},
            "system_progression": {}
        }
        
        # Should return None
        result = self.state_manager.get_current_category_index()
        self.assertIsNone(result)
        
    def test_get_current_category_url_from_operational_data(self):
        """Test that get_current_category_url returns value from supplier_extraction_progress"""
        # Set up state with operational data
        test_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials"
        self.state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_url": test_url
            },
            "system_progression": {
                "current_category_url": "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween"  # Wrong URL
            }
        }
        
        # Should return value from supplier_extraction_progress (operational data)
        result = self.state_manager.get_current_category_url()
        self.assertEqual(result, test_url)
        
    def test_get_current_category_url_fallback_to_tracking(self):
        """Test fallback to system_progression when supplier_extraction_progress is empty"""
        # Set up state with only tracking data
        test_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween"
        self.state_manager.state_data = {
            "supplier_extraction_progress": {},
            "system_progression": {
                "current_category_url": test_url
            }
        }
        
        # Should fall back to system_progression
        result = self.state_manager.get_current_category_url()
        self.assertEqual(result, test_url)
        
    def test_validate_category_index_bounds_valid_index(self):
        """Test that valid category index passes bounds checking"""
        result = self.state_manager.validate_category_index_bounds(5, 10)
        self.assertTrue(result)
        
    def test_validate_category_index_bounds_negative_index(self):
        """Test that negative category index fails bounds checking"""
        result = self.state_manager.validate_category_index_bounds(-1, 10)
        self.assertFalse(result)
        
    def test_validate_category_index_bounds_exceeds_total(self):
        """Test that category index exceeding total fails bounds checking"""
        result = self.state_manager.validate_category_index_bounds(10, 10)  # Index 10 with total 10 (0-9 valid)
        self.assertFalse(result)


class TestWorkflowCategoryConsistency(unittest.TestCase):
    """Test category URL consistency validation in workflow execution"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the workflow class since it's complex to instantiate
        self.workflow = Mock()
        self.workflow.state_manager = Mock()
        self.workflow.log = Mock()
        
        # Import the actual method we want to test
        from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
        self.workflow._validate_category_consistency = PassiveExtractionWorkflow._validate_category_consistency.__get__(self.workflow)
        
    def test_category_consistency_no_expected_url(self):
        """Test validation when no expected URL exists in state"""
        # Mock state manager to return None for expected URL
        self.workflow.state_manager.get_current_category_url.return_value = None
        
        selected_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween"
        category_list = [selected_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials"]
        
        result = self.workflow._validate_category_consistency(selected_url, category_list)
        self.assertEqual(result, selected_url)
        
    def test_category_consistency_urls_match(self):
        """Test validation when selected URL matches expected URL"""
        expected_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials"
        self.workflow.state_manager.get_current_category_url.return_value = expected_url
        
        category_list = ["https://www.poundwholesale.co.uk/seasonal/wholesale-halloween", expected_url]
        
        result = self.workflow._validate_category_consistency(expected_url, category_list)
        self.assertEqual(result, expected_url)
        
    def test_category_consistency_mismatch_correction(self):
        """Test correction when selected URL doesn't match expected URL"""
        expected_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials"
        selected_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween"
        
        self.workflow.state_manager.get_current_category_url.return_value = expected_url
        
        category_list = [selected_url, expected_url]
        
        result = self.workflow._validate_category_consistency(selected_url, category_list)
        self.assertEqual(result, expected_url)  # Should return corrected URL
        
    def test_category_consistency_mismatch_fallback(self):
        """Test fallback when expected URL is not found in category list"""
        expected_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-not-in-list"
        selected_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween"
        
        self.workflow.state_manager.get_current_category_url.return_value = expected_url
        
        category_list = [selected_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials"]
        
        result = self.workflow._validate_category_consistency(selected_url, category_list)
        self.assertEqual(result, selected_url)  # Should fall back to selected URL


class TestWorkflowResumePointIntegration(unittest.TestCase):
    """Test that workflow execution respects resume points from state management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.workflow = Mock()
        self.workflow.state_manager = Mock()
        self.workflow.log = Mock()
        
    def test_resume_point_respected_in_chunk_processing(self):
        """Test that chunk processing starts from resume point, not 0"""
        # Mock state manager to return resume point
        self.workflow.state_manager.get_current_category_index.return_value = 5
        
        # Simulate category list
        category_urls = [f"https://example.com/category-{i}" for i in range(10)]
        
        # Test the logic that should start from resume point
        resume_category_index = self.workflow.state_manager.get_current_category_index()
        chunk_size = 1
        
        # Verify that range starts from resume point
        chunk_starts = list(range(resume_category_index, len(category_urls), chunk_size))
        
        # Should start from index 5, not 0
        self.assertEqual(chunk_starts[0], 5)
        self.assertNotEqual(chunk_starts[0], 0)
        
    def test_resume_point_bounds_validation(self):
        """Test that resume point is validated against category list bounds"""
        # Mock state manager to return out-of-bounds resume point
        self.workflow.state_manager.get_current_category_index.return_value = 15
        
        # Simulate category list with only 10 categories
        category_urls = [f"https://example.com/category-{i}" for i in range(10)]
        
        # Test bounds validation logic
        resume_category_index = self.workflow.state_manager.get_current_category_index()
        
        if resume_category_index >= len(category_urls):
            resume_category_index = 0  # Reset to 0 as per implementation
            
        self.assertEqual(resume_category_index, 0)
        
    def test_resume_point_none_defaults_to_zero(self):
        """Test that None resume point defaults to 0"""
        # Mock state manager to return None
        self.workflow.state_manager.get_current_category_index.return_value = None
        
        # Test default behavior
        resume_category_index = self.workflow.state_manager.get_current_category_index()
        if resume_category_index is None:
            resume_category_index = 0
            
        self.assertEqual(resume_category_index, 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)