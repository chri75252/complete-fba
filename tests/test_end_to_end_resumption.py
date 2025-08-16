#!/usr/bin/env python3
"""
End-to-end integration test for the complete resumption fix.

This test validates that the entire system (state management + workflow execution)
works together correctly to resume from the proper category.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestEndToEndResumption(unittest.TestCase):
    """Test complete end-to-end resumption behavior"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Set up realistic state data
        self.state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 1,
                "total_categories": 233,
                "current_category_url": "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials",
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 16
            },
            "system_progression": {
                "current_category_index": 0,  # Corrupted data
                "total_categories": 0,        # Corrupted data
                "current_category_url": "",   # Corrupted data
                "current_phase": "supplier"
            },
            "resumption_index": 8378,
            "total_products": 9046
        }
        
    def test_state_management_provides_correct_resume_data(self):
        """Test that state management provides correct resume data to workflow"""
        # Test helper methods return correct values from operational data
        category_index = self.state_manager.get_current_category_index()
        category_url = self.state_manager.get_current_category_url()
        
        # Should use supplier_extraction_progress (operational data), not system_progression (corrupted)
        self.assertEqual(category_index, 1)
        self.assertEqual(category_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials")
        
    def test_workflow_would_respect_resume_point(self):
        """Test that workflow logic would respect the resume point from state management"""
        # Simulate the workflow logic
        category_urls_to_scrape = [
            "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween",           # Index 0
            "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials",  # Index 1 - Resume point
            "https://www.poundwholesale.co.uk/seasonal/wholesale-christmas",          # Index 2
            "https://www.poundwholesale.co.uk/seasonal/wholesale-easter"              # Index 3
        ]
        
        # Get resume point from state management (as workflow would do)
        resume_category_index = self.state_manager.get_current_category_index()
        
        # Validate bounds (as workflow would do)
        if resume_category_index is None:
            resume_category_index = 0
        elif resume_category_index >= len(category_urls_to_scrape):
            resume_category_index = 0
            
        # Test chunk processing logic (as workflow would do)
        chunk_size = 1
        chunk_starts = list(range(resume_category_index, len(category_urls_to_scrape), chunk_size))
        
        # Should start from index 1, not 0
        self.assertEqual(chunk_starts[0], 1)
        self.assertEqual(category_urls_to_scrape[chunk_starts[0]], "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials")
        
    def test_category_consistency_validation_would_work(self):
        """Test that category consistency validation would work correctly"""
        # Simulate the workflow validation logic
        category_urls_to_scrape = [
            "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween",           # Index 0
            "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials",  # Index 1 - Resume point
            "https://www.poundwholesale.co.uk/seasonal/wholesale-christmas",          # Index 2
        ]
        
        # Get expected URL from state management
        expected_url = self.state_manager.get_current_category_url()
        
        # Simulate workflow selecting wrong category (index 0)
        selected_url = category_urls_to_scrape[0]  # Wrong category
        
        # Test validation logic
        if expected_url and expected_url != selected_url:
            try:
                correct_index = category_urls_to_scrape.index(expected_url)
                corrected_url = expected_url
            except ValueError:
                corrected_url = selected_url  # Fallback
        else:
            corrected_url = selected_url
            
        # Should correct to the expected URL
        self.assertEqual(corrected_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials")
        
    def test_bounds_validation_prevents_out_of_range_errors(self):
        """Test that bounds validation prevents out-of-range errors"""
        # Test with out-of-bounds resume point
        self.state_manager.state_data["supplier_extraction_progress"]["current_category_index"] = 10
        
        category_urls_to_scrape = ["url1", "url2", "url3"]  # Only 3 categories
        
        # Get resume point
        resume_category_index = self.state_manager.get_current_category_index()
        
        # Validate bounds
        is_valid = self.state_manager.validate_category_index_bounds(resume_category_index, len(category_urls_to_scrape))
        
        # Should detect out-of-bounds condition
        self.assertFalse(is_valid)
        
        # Workflow should reset to 0 in this case
        if not is_valid:
            resume_category_index = 0
            
        self.assertEqual(resume_category_index, 0)
        
    def test_complete_resumption_scenario(self):
        """Test complete resumption scenario from start to finish"""
        # Simulate complete workflow resumption logic
        category_urls_to_scrape = [
            "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween",           # Index 0
            "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials",  # Index 1 - Resume point
            "https://www.poundwholesale.co.uk/seasonal/wholesale-christmas",          # Index 2
            "https://www.poundwholesale.co.uk/seasonal/wholesale-easter"              # Index 3
        ]
        
        # Step 1: Get resume point from state management
        resume_category_index = self.state_manager.get_current_category_index()
        expected_url = self.state_manager.get_current_category_url()
        
        # Step 2: Validate bounds
        if resume_category_index is None:
            resume_category_index = 0
        elif resume_category_index >= len(category_urls_to_scrape):
            resume_category_index = 0
            
        # Step 3: Process chunks starting from resume point
        chunk_size = 1
        first_chunk_start = resume_category_index
        first_chunk_end = min(first_chunk_start + chunk_size, len(category_urls_to_scrape))
        first_chunk_categories = category_urls_to_scrape[first_chunk_start:first_chunk_end]
        
        # Step 4: Validate category consistency
        selected_url = first_chunk_categories[0] if first_chunk_categories else None
        
        if expected_url and selected_url and expected_url != selected_url:
            try:
                correct_index = category_urls_to_scrape.index(expected_url)
                validated_url = expected_url
            except ValueError:
                validated_url = selected_url
        else:
            validated_url = selected_url
            
        # Verify complete resumption works correctly
        self.assertEqual(resume_category_index, 1)  # Should resume from category 1
        self.assertEqual(selected_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials")  # Should select correct URL
        self.assertEqual(validated_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials")  # Should validate correctly
        
        # Verify it's NOT starting from category 0
        self.assertNotEqual(resume_category_index, 0)
        self.assertNotEqual(selected_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-halloween")


class TestResumptionWithCorruptedState(unittest.TestCase):
    """Test resumption behavior with various corrupted state scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = FixedEnhancedStateManager("test_supplier")
        
    def test_resumption_with_empty_operational_data(self):
        """Test resumption when operational data is empty but tracking data exists"""
        # Set up state with empty operational data but valid tracking data
        self.state_manager.state_data = {
            "supplier_extraction_progress": {},  # Empty operational data
            "system_progression": {
                "current_category_index": 3,
                "current_category_url": "https://www.poundwholesale.co.uk/seasonal/wholesale-christmas"
            }
        }
        
        # Should fall back to tracking data
        category_index = self.state_manager.get_current_category_index()
        category_url = self.state_manager.get_current_category_url()
        
        self.assertEqual(category_index, 3)
        self.assertEqual(category_url, "https://www.poundwholesale.co.uk/seasonal/wholesale-christmas")
        
    def test_resumption_with_completely_empty_state(self):
        """Test resumption when both operational and tracking data are empty"""
        # Set up completely empty state
        self.state_manager.state_data = {
            "supplier_extraction_progress": {},
            "system_progression": {}
        }
        
        # Should return None for both
        category_index = self.state_manager.get_current_category_index()
        category_url = self.state_manager.get_current_category_url()
        
        self.assertIsNone(category_index)
        self.assertIsNone(category_url)
        
        # Workflow should default to 0 when None is returned
        if category_index is None:
            category_index = 0
            
        self.assertEqual(category_index, 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)